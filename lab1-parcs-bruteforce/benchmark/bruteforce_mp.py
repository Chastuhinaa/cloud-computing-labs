import argparse
import hashlib
import string
import time
from multiprocessing import Pool

CHARSETS = {
    "lower": string.ascii_lowercase,
    "lower+digits": string.ascii_lowercase + string.digits,
    "alnum": string.ascii_lowercase + string.ascii_uppercase + string.digits,
}


def index_to_candidate(index, charset, maxlen):
    base = len(charset)
    length = 1
    count = base
    offset = 0
    while index >= offset + count and length < maxlen:
        offset += count
        length += 1
        count *= base
    local = index - offset
    chars = []
    for _ in range(length):
        chars.append(charset[local % base])
        local //= base
    return "".join(reversed(chars))


def keyspace_size(charset, maxlen):
    base = len(charset)
    return sum(base ** L for L in range(1, maxlen + 1))


def stretched_hash(word, stretch):
    h = word.encode()
    for _ in range(stretch):
        h = hashlib.sha256(h).digest()
    return hashlib.sha256(h).hexdigest()


_CFG = {}


def init_worker(charset, maxlen, stretch, target):
    _CFG["charset"] = charset
    _CFG["maxlen"] = maxlen
    _CFG["stretch"] = stretch
    _CFG["target"] = target


def scan_range(args):
    start, end = args
    charset = _CFG["charset"]
    maxlen = _CFG["maxlen"]
    stretch = _CFG["stretch"]
    target = _CFG["target"]
    found = None
    for idx in range(start, end):
        cand = index_to_candidate(idx, charset, maxlen)
        if stretched_hash(cand, stretch) == target:
            found = cand
    return found


def split_ranges(total, n):
    step = total // n
    ranges = []
    for i in range(n):
        start = i * step
        end = total if i == n - 1 else (i + 1) * step
        ranges.append((start, end))
    return ranges


def run(n_workers, charset, maxlen, stretch, target):
    total = keyspace_size(charset, maxlen)
    ranges = split_ranges(total, n_workers)
    t0 = time.perf_counter()
    with Pool(processes=n_workers, initializer=init_worker,
              initargs=(charset, maxlen, stretch, target)) as pool:
        results = pool.map(scan_range, ranges)
    elapsed = time.perf_counter() - t0
    found = next((r for r in results if r), None)
    return elapsed, found, total


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--charset", default="lower+digits", choices=list(CHARSETS))
    ap.add_argument("--maxlen", type=int, default=4)
    ap.add_argument("--stretch", type=int, default=60)
    ap.add_argument("--password", default="help")
    ap.add_argument("--workers", type=int, nargs="+", default=[1, 2, 3, 4])
    ap.add_argument("--out", default="results.csv")
    args = ap.parse_args()

    charset = CHARSETS[args.charset]
    target = stretched_hash(args.password, args.stretch)
    total = keyspace_size(charset, args.maxlen)

    print("=" * 60)
    print("PARCS brute-force benchmark (multiprocessing)")
    print("charset=%s (%d chars), maxlen=%d, stretch=%d"
          % (args.charset, len(charset), args.maxlen, args.stretch))
    print("keyspace = %d candidates" % total)
    print("target: password='%s', hash=%s" % (args.password, target[:16] + "..."))
    print("=" * 60)

    rows = [("workers", "time_sec", "speedup", "found")]
    base_time = None
    for n in args.workers:
        elapsed, found, _ = run(n, charset, args.maxlen, args.stretch, target)
        if base_time is None:
            base_time = elapsed
        speedup = base_time / elapsed
        rows.append((n, round(elapsed, 3), round(speedup, 2), found or ""))
        print("workers=%d  time=%6.3f s  speedup=%4.2f  found=%s"
              % (n, elapsed, speedup, found))

    with open(args.out, "w") as f:
        for r in rows:
            f.write(",".join(str(x) for x in r) + "\n")
    print("\nSaved table -> %s" % args.out)


if __name__ == "__main__":
    main()

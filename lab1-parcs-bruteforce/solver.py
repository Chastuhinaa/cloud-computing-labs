from Pyro4 import expose


def keyspace_size(base, maxlen):
    return sum(base ** L for L in range(1, maxlen + 1))


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


class Solver:
    def __init__(self, workers, input_file_name, output_file_name):
        self.input_file_name = input_file_name
        self.output_file_name = output_file_name
        self.workers = workers
        print("Solver inited")

    def solve(self):
        print("Job started")
        print("Workers: %d" % len(self.workers))

        charset, maxlen, stretch, target = self.read_input()
        total = keyspace_size(len(charset), maxlen)
        n = len(self.workers)
        step = total // n

        mapped = []
        for i in xrange(0, n):
            start = i * step
            end = total if i == n - 1 else (i + 1) * step
            print("Worker %d -> range [%d, %d)" % (i, start, end))
            mapped.append(
                self.workers[i].mymap(start, end, charset, maxlen, stretch, target)
            )

        result = self.myreduce(mapped)
        self.write_output(result)
        print("Job finished")

    @staticmethod
    @expose
    def mymap(start, end, charset, maxlen, stretch, target):
        import hashlib

        def stretched_hash(word):
            h = word.encode("utf-8")
            for _ in range(stretch):
                h = hashlib.sha256(h).digest()
            return hashlib.sha256(h).hexdigest()

        print("mymap [%d, %d)" % (start, end))
        found = ""
        for idx in range(start, end):
            cand = index_to_candidate(idx, charset, maxlen)
            if stretched_hash(cand) == target:
                found = cand
                break
        return found

    @staticmethod
    @expose
    def myreduce(mapped):
        for future in mapped:
            res = future.value
            if res:
                return res
        return ""

    def read_input(self):
        with open(self.input_file_name, "r") as f:
            lines = [ln.rstrip("\n") for ln in f.readlines()]
        charset = lines[0]
        maxlen = int(lines[1])
        stretch = int(lines[2])
        target = lines[3].strip()
        return charset, maxlen, stretch, target

    def write_output(self, result):
        with open(self.output_file_name, "w") as f:
            if result:
                f.write("PASSWORD FOUND: %s\n" % result)
            else:
                f.write("NOT FOUND (password not in keyspace)\n")
        print("Result: %s" % (result if result else "NOT FOUND"))

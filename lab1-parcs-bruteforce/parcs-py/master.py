import argparse
import os
import time
import sys

import Pyro4

sys.path.insert(0, "/parcs/job")
import solver as solver_module

Pyro4.config.SERIALIZER = "serpent"
Pyro4.config.SERIALIZERS_ACCEPTED = set(["serpent", "json", "pickle"])


def discover_workers(ns, max_wait=30, expected=0):
    stable, prev = 0, -1
    entries = {}
    for _ in range(max_wait):
        entries = ns.list(prefix="parcs.worker.")
        count = len(entries)
        if expected > 0:
            if count >= expected:
                break
        else:
            stable = stable + 1 if count == prev and count > 0 else 0
            if stable >= 3:
                break
            prev = count
        time.sleep(1)

    workers = []
    for name, uri in entries.items():
        proxy = Pyro4.Proxy(uri)
        proxy._pyroAsync()
        workers.append(proxy)
    return workers


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--nameserver", default="master")
    ap.add_argument("--ns-port", type=int, default=9090)
    ap.add_argument("--solver", default="job/solver.py")
    ap.add_argument("--input", default="job/input.txt")
    ap.add_argument("--output", default="job/output.txt")
    args = ap.parse_args()

    ns = Pyro4.locateNS(args.nameserver, args.ns_port)
    expected = int(os.environ.get("EXPECTED_WORKERS", "0"))
    workers = discover_workers(ns, expected=expected)
    print("[master] found %d worker(s)" % len(workers))
    if not workers:
        print("[master] no workers registered - aborting")
        sys.exit(1)

    t0 = time.time()
    solver = solver_module.Solver(workers, args.input, args.output)
    solver.solve()
    print("[master] elapsed %.3f s" % (time.time() - t0))


if __name__ == "__main__":
    main()

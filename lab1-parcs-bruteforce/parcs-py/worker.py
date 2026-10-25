import argparse
import socket
import sys
import uuid

import Pyro4

sys.path.insert(0, "/parcs/job")
import solver as solver_module

Pyro4.config.SERIALIZER = "serpent"
Pyro4.config.SERIALIZERS_ACCEPTED = set(["serpent", "json", "pickle"])


@Pyro4.expose
class Worker(object):
    def mymap(self, start, end, charset, maxlen, stretch, target):
        return solver_module.Solver.mymap(start, end, charset, maxlen, stretch, target)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--nameserver", default="master")
    ap.add_argument("--ns-port", type=int, default=9090)
    args = ap.parse_args()

    ns = Pyro4.locateNS(args.nameserver, args.ns_port)
    daemon = Pyro4.Daemon(host=socket.gethostname())
    uri = daemon.register(Worker())
    name = "parcs.worker." + uuid.uuid4().hex
    ns.register(name, uri)
    print("[worker] registered as %s -> %s" % (name, uri))
    daemon.requestLoop()


if __name__ == "__main__":
    main()

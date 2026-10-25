#!/usr/bin/env bash
set -e

MASTER_HOST="${MASTER_HOST:-master}"
NS_PORT="${NS_PORT:-9090}"

if [ "$ROLE" = "master" ]; then
  echo "[master] starting Pyro4 nameserver on ${MASTER_HOST}:${NS_PORT}"
  python -m Pyro4.naming -n 0.0.0.0 -p "${NS_PORT}" &
  sleep 3
  echo "[master] launching job (solver.py) with input.txt"
  exec python master.py \
      --nameserver "${MASTER_HOST}" \
      --solver job/solver.py \
      --input job/input.txt \
      --output job/output.txt
elif [ "$ROLE" = "worker" ]; then
  echo "[worker] connecting to nameserver ${MASTER_HOST}:${NS_PORT}"
  until python -c "import Pyro4,sys; Pyro4.locateNS('${MASTER_HOST}', ${NS_PORT})" 2>/dev/null; do
    echo "[worker] waiting for nameserver..."; sleep 2
  done
  exec python worker.py --nameserver "${MASTER_HOST}"
else
  echo "ROLE must be 'master' or 'worker' (got '${ROLE}')" >&2
  exit 1
fi

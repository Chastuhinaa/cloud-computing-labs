#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
docker build -t parcs-bench .
docker run --rm --cpus=4 -v "$(pwd)":/app parcs-bench
echo "Готово: results.csv та results.png у поточній теці."

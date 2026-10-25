FROM python:2.7-slim

RUN pip install --no-cache-dir "serpent==1.28" "Pyro4==4.77"

WORKDIR /parcs
COPY parcs-py/ /parcs/
COPY solver.py input.txt /parcs/job/

ENV PYRO_SERIALIZERS_ACCEPTED=serpent,json,pickle
ENV PYRO_SERIALIZER=serpent

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]

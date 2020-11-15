FROM m.docker-registry.ir/python:3.6.9

COPY requirements.txt /requirements.txt

RUN pip install -r /requirements.txt

COPY . /opt/goldiba/back

WORKDIR /opt/goldiba/back

RUN chmod +x run.sh

ENTRYPOINT ["./run.sh"]
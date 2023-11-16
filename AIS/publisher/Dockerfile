FROM python:3.11-slim-buster

WORKDIR /usr/app/src

RUN pip3 install toml
RUN pip3 install confluent-kafka
RUN pip3 install pyais
RUN pip3 install redis

COPY make_cot.py ./
COPY ais_cot_types.xml ./
COPY publisher.py ./

CMD ["python", "./publisher.py"]
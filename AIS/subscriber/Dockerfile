FROM python:3.11-slim-buster

WORKDIR /usr/app/src

RUN pip3 install toml
RUN pip3 install confluent-kafka
RUN pip3 install cryptography
RUN pip3 install pytak

COPY subscriber.py ./
COPY make_pem.py ./

CMD ["python", "./subscriber.py"]
FROM python:3.5
RUN apt-get update -y 

ENV PYTHONUNBUFFERED 1
RUN mkdir /code

ADD ./config/pip-requirements.txt  /code/
RUN pip install -r /code/pip-requirements.txt

RUN apt-get install netcat -y
 
WORKDIR /cLIMS
ADD scripts/start_django_server.sh /code/

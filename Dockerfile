FROM ubuntu:16.04
RUN apt-get update -y
RUN apt-get install -y python3-pip python-dev build-essential
COPY . /exchange
WORKDIR /exchange
RUN pip3 install -r requirements.txt
ENV PYTHONPATH /exchange
ENTRYPOINT ["python3"]
EXPOSE 5000
CMD ["exchange/rest_api.py"]
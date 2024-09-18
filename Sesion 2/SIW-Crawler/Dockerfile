FROM python:3.10
ADD . .
ENV OPENSSL_CONF=./openssl.cnf
RUN pip install -r requirements.txt
CMD [ "python", "./Crawler.py", "files/seed.txt"]
FROM alpine:latest

RUN apk add --no-cache python3-dev \
	&& apk add py3-pip \
	&& pip install --upgrade pip

WORKDIR /app

COPY . /app

RUN pip3 --no-cache-dir install -r requirements.txt

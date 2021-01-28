FROM python:3.6-alpine

RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apk/repositories

RUN mkdir -p /usr/local/src/tethys

WORKDIR /usr/local/src/tethys

RUN apk add gcc g++ openssl-dev libressl-dev \
	libffi-dev mariadb-dev jpeg-dev zlib-dev build-base bash \
        bash-doc \
        bash-completion 

RUN rm -rf /var/cache/apk/*

COPY server ./

RUN pip install pipenv -i https://mirrors.aliyun.com/pypi/simple

RUN pipenv install --pypi-mirror https://mirrors.aliyun.com/pypi/simple

COPY entrypoint.sh /usr/local/bin/

RUN chmod +x /usr/local/bin/entrypoint.sh

ENTRYPOINT ["entrypoint.sh"]

EXPOSE 9000

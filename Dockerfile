# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster
WORKDIR /project
COPY ./USENIX_AE/VulnerabilityLifetimes_v5/requirements.txt requirements.txt
COPY ./USENIX_AE/VulnerabilityLifetimes_v5/Analysis/requirements.txt requirements2.txt
COPY ./USENIX_AE/VulnerabilityLifetimes_v5/packages_list.txt packages_list.txt
RUN apt update && apt install -y wget && apt install -y gnupg\
    && wget -qO - https://www.mongodb.org/static/pgp/server-5.0.asc | apt-key add - \
    && printf "deb http://repo.mongodb.org/apt/debian buster/mongodb-org/5.0 main" > /etc/apt/sources.list.d/mongodb-org-5.0.list \
    && apt update \
    && xargs -a packages_list.txt apt install -y \
    && rm -rf /var/lib/apt/lists/*
RUN pip3 install -r requirements.txt
RUN pip3 install -r requirements2.txt
COPY ./USENIX_AE/VulnerabilityLifetimes_v5 ./VulnerabilityLifetimes
RUN git clone https://github.com/cve-search/cve-search.git /project/cve-search
RUN service mysql start \
    && service redis-server start \
    && mongod --config /etc/mongod.conf & \
    && pip3 install -r ./cve-search/requirements.txt \
    && mysql -p < ./VulnerabilityLifetimes/Database/Scripts/100_combined.sql \

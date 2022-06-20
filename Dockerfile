# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster
WORKDIR /project
COPY . /project/VulnerabilityLifetimes
RUN apt update && apt install -y wget && apt install -y gnupg\
    && wget -qO - https://www.mongodb.org/static/pgp/server-5.0.asc | apt-key add - \
    && printf "deb http://repo.mongodb.org/apt/debian buster/mongodb-org/5.0 main" > /etc/apt/sources.list.d/mongodb-org-5.0.list \
    && apt update \
    && xargs -a /project/VulnerabilityLifetimes/packages_list.txt apt install -y \
    && rm -rf /var/lib/apt/lists/*
RUN pip3 install -r /project/VulnerabilityLifetimes/requirements.txt
RUN pip3 install -r /project/VulnerabilityLifetimes/Analysis/requirements.txt
RUN git clone https://github.com/cve-search/cve-search.git /project/cve-search
RUN pip3 install -r /project/cve-search/requirements.txt

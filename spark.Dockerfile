FROM ubuntu:22.04

ENV PYTHON_VERSION=3.12
ENV USER_EXEC=wizard
ENV USER_EXEC_ID=oooo
ENV USER_EXEC_GROUP=root
ENV USER_EXEC_GROUP_ID=0
ENV VIRTUAL_ENV=.venv

# Update and upgrade packages
RUN apt-get update && apt-get upgrade -y

# Install necessary software
RUN apt-get install -y software-properties-common python$PYTHON_VERSION python3-pip python${PYTHON_VERSION}-venv git postgresql postgresql-contrib php

# Create user
RUN useradd --uid $USER_EXEC_ID --gid $USER_EXEC_GROUP_ID --create-home $USER_EXEC

# Clone repository
WORKDIR /postgres
RUN git clone https://github.com/teddybee-r/GwentOneDB.git

# Start PostgreSQL service and create user
RUN pg_ctlcluster 12 main start && \
    /usr/lib/postgresql/12/bin/createuser --superuser myuser && \
    /usr/lib/postgresql/12/bin/createextension hstore

EXPOSE 5432

# RUN php postgres/bin/database 1


FROM ubuntu:22.04

# Update and upgrade packages with DEBCONF_NONINTERACTIVE set for automated time zone selection
#RUN DEBIAN_FRONTEND=noninteractive DEBCONF_NONINTERACTIVE=YES env LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8 /usr/bin/debconf-set -t debconf/templets --database templet
#systemchooser=0 Europe,systemchooser=globe/Europe,systemchooser=fixedchoice/European
RUN apt-get update && apt-get upgrade -y
RUN rm -rf /etc/localtime && ln -s /usr/share/zoneinfo/Europe/Amsterdam /etc/localtime 

# Install necessary software (using more general python3 package version)
RUN apt-get install -y software-properties-common git postgresql postgresql-contrib php libapache2-mod-php

# Create user
RUN groupadd --gid 1000 usergroup && useradd --uid 1001 --gid 1000 userexec

# Set environment variables
ENV VIRTUAL_ENV=.venv

# Clone repository
WORKDIR /postgres
RUN git clone https://github.com/teddybee-r/GwentOneDB.git

#RUN su -c "pg_ctlcluster 12 main start" \
#    - postgres \
#&& createuser --superuser wizard && \
#    psql -d gwent -c "CREATE EXTENSION IF NOT EXISTS hstore;"

# Start PostgreSQL service and create database/user
#RUN pg_ctlcluster 12 main start && \
#    /usr/lib/postgresql/12/bin/createuser --superuser wizard && \
#    /usr/lib/postgresql/12/bin/createextension hstore

#EXPOSE 5432

CMD ["sleep", "3600"]

# Run PHP script to insert data into PostgreSQL
#WORKDIR /postgres/GwentOneDB
#RUN php bin/database 

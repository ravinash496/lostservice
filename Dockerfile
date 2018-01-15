FROM ubuntu:xenial

MAINTAINER GeoComm

RUN echo "deb http://archive.ubuntu.com/ubuntu/ xenial main universe" >> /etc/apt/sources.list && apt-get update



RUN apt-get install -y tar \
                   git \
                   curl \
                   nano \
                   wget \
                   dialog \
                   net-tools \
                   build-essential \
                   checkinstall \
                   libreadline-gplv2-dev \
                   libncursesw5-dev \
                   libssl-dev \
                   libsqlite3-dev \
                   tk-dev \
                   libgdbm-dev \
                   libc6-dev \
                   libbz2-dev \
                   software-properties-common \
                   python-software-properties

RUN wget https://www.python.org/ftp/python/3.6.1/Python-3.6.1.tgz

RUN tar -xvf Python-3.6.1.tgz

WORKDIR /Python-3.6.1
RUN ./configure && make install && python3.6 -m pip install virtualenv

RUN add-apt-repository -y ppa:ubuntugis/ppa && apt-get update
RUN apt-get install -y gdal-bin libgdal-dev
ARG GEMFURY_URL
ARG CPLUS_INCLUDE_PATH=/usr/include/gdal
ARG C_INCLUDE_PATH=/usr/include/gdal

COPY requirements.txt /app/requirements.txt
COPY server.py /app/server.py
COPY build.sh /app/build.sh
COPY /lostservice /app/lostservice

#Run python build requirements.
WORKDIR /app
RUN chmod +x ./build.sh
RUN ./build.sh

#Copy configs after python build is complete.
COPY /deploy/lostservice.ini /app/lostservice/lostservice.ini
COPY /deploy/lostservice.default.ini /app/lostservice/lostservice.default.ini

# Expose ports
EXPOSE 8080

# Set the default directory where CMD will execute
WORKDIR /app

# Set the default command to execute
# when creating a new container
CMD /bin/bash -c "source ./venv/bin/activate && python server.py"

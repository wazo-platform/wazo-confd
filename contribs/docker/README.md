Dockerfile for XiVO confd

## Install Docker

To install docker on Linux :

    curl -sL https://get.docker.io/ | sh
 
 or
 
     wget -qO- https://get.docker.io/ | sh

## Build

To build the image, simply invoke

    docker build -t xivo-confd github.com/xivo-pbx/xivo-confd/tree/contribs/docker

Or directly in the sources in contribs/docker

    docker build -t xivo-confd .
  
## Usage

To run the container, do the following:

    docker run -d -P xivo-confd

On interactive mode :

    docker run -i -t xivo-confd /bin/bash

After launch xivo-confd-service in /root directory.

    cd /root
    ./xivo-confd-service

## Infos

- Using docker version 1.2.0 (from get.docker.io) on ubuntu 14.04.
- The root password is xivo by default.
- If you want to using a simple webi to administrate docker use : https://github.com/crosbymichael/dockerui

To get the IP of your container use :

    docker ps -a
    docker inspect <container_id> | grep IPAddress | awk -F\" '{print $4}'

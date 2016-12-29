Dockerfile for XiVO confd

## Install Docker

To install docker on Linux :

    curl -sL https://get.docker.io/ | sh
 
 or
 
     wget -qO- https://get.docker.io/ | sh

## Build

To build the image, simply invoke

    docker build -t xivo-confd github.com/wazo-pbx/xivo-confd

Or directly in the sources in contribs/docker

    docker build -t xivo-confd .
  
## Usage

To run the container, do the following:

    docker run --name xivo-confd -d -p 9486:9486 -v /config/confd:/etc/xivo-confd -t xivo-confd

On interactive mode :

    docker run -p 9486:9486 -v /config/confd:/etc/xivo-confd -it xivo-confd /bin/bash

After launch xivo-confd-service in /root directory.

    xivo-confd -d -f

## Infos

- Using docker version 1.4.0 (from get.docker.io) on ubuntu 14.04.
- If you want to using a simple webi to administrate docker use : https://github.com/crosbymichael/dockerui
- Using config.yml to configure xivo-confd

To get the IP of your container use :

    docker ps -a
    docker inspect <container_id> | grep IPAddress | awk -F\" '{print $4}'

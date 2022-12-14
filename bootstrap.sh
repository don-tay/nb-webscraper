#!/bin/bash
CONTAINER_NAME=${1:-nb-webscraper-container}

# build and run docker image
docker stop $CONTAINER_NAME
docker rm $CONTAINER_NAME
docker build -t nb-webscraper .
docker run -d --name $CONTAINER_NAME --env-file .env nb-webscraper

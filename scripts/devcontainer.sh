#!/bin/bash

if [ "${1-}" = "up" ]; then
    mkdir -p "${IMAGE_RETRIEVAL_ROOT_DIR:-.}/volumes/vscode-extensions"
    chmod -R 777 "${IMAGE_RETRIEVAL_ROOT_DIR:-.}/volumes"

    docker-compose -f ${IMAGE_RETRIEVAL_ROOT_DIR:-.}/docker-compose-devcontainer.yml up -d
fi

if [ "${1-}" = "down" ]; then
    docker-compose -f ${IMAGE_RETRIEVAL_ROOT_DIR:-.}/docker-compose-devcontainer.yml down
    rm -rf "${IMAGE_RETRIEVAL_ROOT_DIR:-.}/volumes"
fi

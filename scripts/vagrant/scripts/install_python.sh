#!/usr/bin/env bash

# update python 2.7.x
sudo add-apt-repository ppa:fkrull/deadsnakes

sudo apt-get update -y
sudo apt-get install python-dev \
                     python3-dev \
                     python2.7 \
                     -y

# install and update pip
sudo apt-get install python-pip \
                     python3-pip \
                     -y

pip install --upgrade pip

# install package distribution requirements
pip install -U pip \
               setuptools \
               virtualenv



#!/usr/bin/env bash

# install essentials
sudo apt-get install python-software-properties \
                     build-essential \
                     libssl-dev \
                     libffi-dev \
                     git \
                     nano \
                     curl \
                     mc \
                     -y

# install stress to be able to quickly check if the VM can use all the resources of the host CPU
# usage:
  # for 1 core: stress -c 1
  # for 4 cores: stress -c 4
sudo apt-get install stress -y

# update after essentials (especially python-software-properties)
sudo apt-get update -y

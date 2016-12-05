#!/usr/bin/env bash

export _HOME_DIR="/home/ubuntu"

export _VAGRANT_DIR="/vagrant"
export _PROVISION_DIR="$_VAGRANT_DIR/scripts/vagrant"
export _SCRIPTS_DIR="$_PROVISION_DIR/scripts"
export _CONTENT_DIR="$_PROVISION_DIR/content"
export _USER_DIR="$_CONTENT_DIR/user_dir"

# Update before provisioning
sudo apt-get update -y

# Install scripts
"$_SCRIPTS_DIR/install_essentials.sh"
"$_SCRIPTS_DIR/install_git.sh"
"$_SCRIPTS_DIR/install_python.sh"

# Add custom content to .bashrc
cat "$_USER_DIR/.bashrc" >> "$_HOME_DIR/.bashrc"

# Link /vagrant to ~/vagrant
ln -s "$_VAGRANT_DIR" "$_HOME_DIR/vagrant"
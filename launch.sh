#! /bin/bash

sudo systemctl stop apache2
sudo systemctl start mongod
sudo systemctl start nginx
sudo systemctl start istapp

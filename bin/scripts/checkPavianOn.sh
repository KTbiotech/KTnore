#!/bin/bash



On=`netstat -tulpn | grep LISTEN|grep 127.0.0.1:5000|wc -l`


echo $On

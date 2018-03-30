#!/usr/bin/env bash

# copies contents of ./remote_scripts to ~/scripts/rtg on DjangoEurope server.

scp -r remote_scripts/* muden@s17.wservices.ch:/home/muden/scripts/rtg/
#!/bin/bash

source ${HOME}/dev/.pyve/rtg/bin/activate
inv -e deploy-prod  # does a remote git pull and replaces the app on the server
deactivate
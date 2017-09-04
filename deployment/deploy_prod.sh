#!/bin/bash

source ${HOME}/dev/.pyve/rtg/bin/activate
fab -a --abort-on-prompts deploy_prod     ## does a remote git pull and replaces the app on the server
deactivate
#!/bin/bash

source ../.v/rtg/bin/activate
inv -e deploy-demo  # does a remote git pull and replaces the app on the server
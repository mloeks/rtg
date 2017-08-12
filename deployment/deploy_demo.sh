#!/bin/bash

source ${HOME}/dev/.pyve/rtg/bin/activate

#fab svn_commit      ## need only to execute if not already done manually
fab deploy_demo     ## does a remote svn up and replaces the prod app

deactivate
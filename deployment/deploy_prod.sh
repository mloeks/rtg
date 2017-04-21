#!/bin/bash

source ${HOME}/pyve/rtg2016/bin/activate

fab svn_commit      ## need only to execute if not already done manually
fab deploy_prod     ## does a remote svn up and replaces the prod app

deactivate
#!/bin/bash

# version 2021-08-07 15:20

cd ~/dockersolarrs485mqtt

if [ -n "$1" ]; then
  ex=$1
else
  rc=$(git remote show origin |  grep "local out of date" | wc -l)
  if [ $rc -ne "0" ]; then
    ex=true
  else
    ex=false
  fi
fi

if [ $ex == true ]; then
    git pull
    chmod +x build.sh

    docker image build -t revenberg/solarrs485mqtt .

    docker push revenberg/solarrs485mqtt

    # testing: 

    echo "==========================================================="
    echo "=                                                         ="
    echo "=          docker run revenberg/solarrs485mqtt          ="
    echo "=                                                         ="
    echo "==========================================================="
    # docker run revenberg/solarrs485mqtt
fi

cd -


#!/usr/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

if [ -z $ATLAS_LOCAL_ROOT_BASE ]; then
        ATLAS_LOCAL_ROOT_BASE=/cvmfs/atlas.cern.ch/repo/ATLASLocalRootBase
fi
. ${ATLAS_LOCAL_ROOT_BASE}/user/atlasLocalSetup.sh -q

lsetup "views LCG_103 x86_64-centos7-gcc11-opt" -q

python ${SCRIPT_DIR}/python/condor_memory.py -i "$1" -o "$2"


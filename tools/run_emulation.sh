#!/bin/bash
# Copyright European Organization for Nuclear Research (CERN)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Authors:
# - Vincent Garonne, <vincent.garonne@cern.ch>, 2012-2013
# - Ralph Vigne, <ralph.vigne@cern.ch>, 2013


function usage {
  echo "Usage: $0 [OPTION]..."
  echo "Run Rucio's emulation suite(s)"
  echo ""
  exit
}

while getopts hsc: opt
do
  case "$opt" in
    h|help) usage;;
  esac
done

# Cleanup *pyc
echo "cleaning *.pyc files"
find lib -iname '*.pyc' | xargs rm

# Cleanup old token
rm -rf /tmp/.rucio_*/

./tools/reset_database.py
if [ $? != 0 ]; then
    echo 'Failed to reset the database'
    exit
fi

echo 'Sync rse_repository with Rucio core'
./tools/sync_rses.py

echo 'Sync metadata keys'
./tools/sync_meta.py

# Run nosetests
python lib/rucio/tests/emulation/emulator.py 

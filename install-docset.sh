#!/bin/bash

if [[ $# -lt 2 ]]; then
    echo "Usage: $0 [docset.tgz ...] [zeal doc dir]"
    exit -1
fi

dest=${@: -1}

for i in $(seq $(($#-1))); do
    echo "Extracting $1 to $dest"
    tar -xf $1 -C $dest
    shift
done

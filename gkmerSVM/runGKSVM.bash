#!/usr/bin/env bash
if [ -z ${3} ]; then
    echo "3 argumnets: pos file, neg file, output prefix"
else
    echo "Creating kernel matrix.."
    kernMatName="kernmat_"$3".out"
    ./gkmsvm-1.3/gkmsvm_kernel $1 $2 $kernMatName 
    echo "Starting SVM training.."
    $PYTHON ./gkmsvm-1.3/scripts/cksvm_train.py -v 1 $kernMatName $1 $2 $3
fi

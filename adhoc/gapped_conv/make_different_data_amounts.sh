#!/usr/bin/env bash

for data_amt in 100 200 400 800 1600 3200 6400 12800; do
    echo $data_amt
    ./prep_data_and_make_hdf5.sh $data_amt
    mv train_data.hdf5 "train_data_"$data_amt".hdf5"
done

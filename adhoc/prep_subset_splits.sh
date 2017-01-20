#!/usr/bin/env bash

#for splitting training set into subsets of 20%-80%
#intended to be used with make_hdf5 in avutils/scrips
#assumes your inputs and labels lie one directory up in inputs.gz and labels.gz
#and that the original splits lie one directory up in splits/ttrain.gz
for num in 1; do #2 4 6 8; do
    rm -r ${num}0pc #in case it was created in an earlier run
    mkdir ${num}0pc
    cd ${num}0pc
    ln -s ../../inputs.gz . 
    ln -s ../../labels.gz . 
    mkdir splits
    zcat ../../splits/train.gz | perl -lane 'if ($.%10 < '${num}') {print $_}' | gzip -c > splits/train.gz
    echo "" | gzip -c > splits/valid.gz
    echo "" | gzip -c > splits/test.gz
    ln -s ~/avutils/avutils/yaml_data_import/canned_yamls/basic_fasta make_hdf5_yaml
    make_hdf5 --yaml_configs make_hdf5_yaml/*
    #get rid of the empty valid/test hdf5's
    rm valid_data.hdf5
    rm test_data.hdf5
    cd ..
done


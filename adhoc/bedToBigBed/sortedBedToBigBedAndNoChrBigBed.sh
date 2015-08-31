#!/usr/bin/env bash
#start from sorted bed, trim the chromosome to produce nochr
if [ -z "$3" ]; then
    echo "Please provide the chromsizes (with and then without chrom) as the first two arguments and the beds as the remaining";
else
    mm10file=$1
    mm10file_noChr=$2
    echo "mm10 file "$mm10file
    for bed in "${@:3}"; do
        base=`basename $bed .bed`
        bigBedOutput=$base".bb"
        bedToBigBed $bed $mm10file $bigBedOutput
        #noChr bigBed file
        noChrOutputFile="noChr_"$bed
        perl -pe '$_ =~ s/chr//' $bed > $noChrOutputFile
        bedToBigBed $noChrOutputFile $mm10file_noChr "noChr_"$bigBedOutput
        rm $noChrOutputFile
    done
fi

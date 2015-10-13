#start from unsorted bed, sort, get relevant columns, make bigBed
for bed in `ls *.bed`; do
    base=`basename $bed .bed`
    sortedBed="sorted_"$bed
    bedSort $bed $sortedBed
    regionOnlySortedBed="regionOnly_"$sortedBed
    perl -pe '@_=split(/\t/); $"="\t"; $_="@_[0..2]\n"' $sortedBed > $regionOnlySortedBed
    rm $sortedBed
    bigBedOutputName=$base".bb"
    bedToBigBed $regionOnlySortedBed ../mm10.chrom.sizes $bigBedOutputName
done
#start from sorted bed, trim the chromosome to produce nochr
for bed in `ls regionOnly_*.bed`; do
    noChrOutputFile="noChr_"$bed
    perl -pe '$_ =~ s/chr//' $bed > $noChrOutputFile
    base=`basename $bed .bed`
    bigBedOutput=$base".bb"
    bedToBigBed $noChrOutputFile ../../mm10.chromnochr.sizes $bigBedOutput
    rm $noChrOutputFile
done

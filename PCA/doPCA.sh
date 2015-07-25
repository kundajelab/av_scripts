#!/usr/bin/env sh
doPCA.R $1 $2
perl -i -pe '$_ = $. == 1 ? "\t$_" : $_' $2

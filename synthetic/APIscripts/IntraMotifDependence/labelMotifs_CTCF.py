#!/usr/bin/env python
#Will read in every row, look at the actual motif that was
#embedded, and will label the sequence accordingly
from __future__ import division;
from __future__ import print_function;
from __future__ import absolute_import;
import sys;
import os;
scriptsDir = os.environ.get("UTIL_SCRIPTS_DIR");
if (scriptsDir is None):
    raise Exception("Please set environment variable UTIL_SCRIPTS_DIR");
sys.path.insert(0,scriptsDir);
import pathSetter;
import util;
import fileProcessing as fp;
from synthetic import synthetic as sn;
from synthetic import labelAccordingToEmbeddings as late;

def labelMotifsGivenLabelFromEmbeddings(
    options, labelFromEmbeddingsObjects):
    """
        labelFromEmbeddingsObjects is an array of
            late.LabelFromEmbeddings objects.
    """
    simdataFileHandle = fp.getFileHandle(options.simdataFile);
    outputFileHandle = fp.getFileHandle(
                        fp.getFileNameParts(options.simdataFile)\
                            .getFilePathWithTransformation(
                                lambda x: "CTCFlabelled_"+x, extension=".txt")
                        , 'w'); 
    def action(inp, lineNumber):
        if lineNumber==1:
            outputFileHandle.write(
                "seqName\t"
                +"\t".join(x.labelName for x in labelFromEmbeddingsObjects)
                +"\n");
        else:
            seqName = inp[0]
            embeddings = sn.getEmbeddingsFromString(inp[2]);
            outputFileHandle.write(seqName+"\t"
                                    +"\t".join( 
                                        ["1" if x.isPositive(embeddings) else "0" for x in
                                        labelFromEmbeddingsObjects])
                                    +"\n"); 
    fp.performActionOnEachLineOfFile(
        fileHandle=simdataFileHandle 
        ,action=action
        ,transformation=fp.defaultTabSeppd
        ,ignoreInputTitle=False
    );
    outputFileHandle.close();

def labelMotifs(options):
    ctcfDependentLabelRule=late.LabelIfRuleSatisfied(
                                labelName="label1"
                                ,rule=lambda embeddings:\
                                  False if len(embeddings)==0 else
                                  (embeddings[0].what.string[5]=='A'\
                                  and embeddings[0].what.string[15]=='A'));
    anyCtcfLabelRule=late.LabelIfRuleSatisfied(
                            labelName="label2"
                            ,rule=lambda embeddings: len(embeddings)>0);
    labelMotifsGivenLabelFromEmbeddings(
        options
        ,[ctcfDependentLabelRule
          ,anyCtcfLabelRule]);

if __name__ == "__main__":
    import argparse;
    parser = argparse.ArgumentParser(); 
    parser.add_argument("simdataFile");
    options = parser.parse_args();
    labelMotifs(options)

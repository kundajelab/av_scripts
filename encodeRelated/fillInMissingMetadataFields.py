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
import fileProcessing as fp;
import util;
from collections import OrderedDict;

#ad-hoc script
metadataCols = util.enum(fileAccession='File accession', fileFormat='File format', experimentAccession='Experiment accession', biosampleTermName='Biosample term name', experimentTarget='Experiment target', biosampleAge='Biosample Age', outputType='Output type');
metadataColsForExperiment = [metadataCols.biosampleTermName, metadataCols.biosampleAge];

def readMetadataFile(metadataFile, relevantColumns=metadataCols.vals):
    #returns an instance of util.titledMapping
    titledMapping = fp.readTitledMapping(fp.getFileHandle(metadataFile), contentType=str, subsetOfColumnsToUseOptions=fp.SubsetOfColumnsToUseOptions(columnNames=relevantColumns));  
    return titledMapping;

def getMappingFromExperimentAccessionToValuableFields(metadataTitledMapping):
    experimentToDetailsTitledMapping = util.TitledMapping(titleArr=metadataColsForExperiment, flagIfInconsistent=True);
    for metadataTitledArr in metadataTitledMapping:
        dataFilledIn = True;
        for metadataColForExperiment in metadataColsForExperiment:
            if metadataTitledArr.getCol(metadataColForExperiment) == "":
                dataFilledIn = False;
                break;
        if (dataFilledIn):
            experimentToDetailsTitledMapping.addKey(metadataTitledArr.getCol(metadataCols.experimentAccession), [metadataTitledArr.getCol(x) for x in metadataColsForExperiment]);
    return experimentToDetailsTitledMapping;

def fillInMissingFieldsUsingExperimentData(metadataTitledMapping, experimentMetadataTitledMapping):
    for titledArr in metadataTitledMapping:
        for metadataColForExperiment in metadataColsForExperiment:
            if titledArr.getCol(metadataColForExperiment) == "":
                experiment = titledArr.getCol(metadataCols.experimentAccession);
                titledArr.setCol(metadataColForExperiment, experimentMetadataTitledMapping.getTitledArrForKey(experiment).getCol(metadataColForExperiment));

def main():
    inputFile = "mouseExperimentMetadata.tsv";
    metadataTitledMapping = readMetadataFile(inputFile);
    experimentToDetailsTitledMapping = getMappingFromExperimentAccessionToValuableFields(metadataTitledMapping)
    fillInMissingFieldsUsingExperimentData(metadataTitledMapping, experimentToDetailsTitledMapping);
    outputFile = "filledMetadata.txt";
    metadataTitledMapping.printToFile(fp.getFileHandle(outputFile, 'w'));

main();

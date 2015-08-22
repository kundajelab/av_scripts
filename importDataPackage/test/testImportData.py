#!/usr/bin/env python
import yaml;
import importData;
    
def testImportData(options):
    yamlObjects = [yaml.load(open(x)) for x in options.yamls];
    splitNameToInputData = importData.getSplitNameToInputDataFromSeriesOfYamls(yamlObjects);
    firstSplit = splitNameToInputData["train"];
    secondSplit = splitNameToInputData["valid"];
    for split in [firstSplit, secondSplit]:
        print split.ids;
        print split.X;
        print split.Y;
        print split.featureNames;
        print split.labelNames;
      

if __name__ == "__main__":
    import argparse;
    parser = argparse.ArgumentParser();
    parser.add_argument("--yamls", nargs="+", required=True);
    options = parser.parse_args();
    testImportData(options); 

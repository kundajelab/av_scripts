#!/usr/bin/env python
import yaml;
import importData;
    
def testImportData(options):
    yamlObjects = [yaml.load(open(x)) for x in options.yamls];
    splitNameToInputData = importData.getSplitNameToInputDataFromSeriesOfYamls(yamlObjects);
    firstSplit = splitNameToInputData["train"];
    secondSplit = splitNameToInputData["valid"];
    for split,splitName in zip([firstSplit, secondSplit],["train","valid"]):
        print("splitName",splitName)
        print("ids",split.ids);
        print("X",split.X);
        print("Y",split.Y);
        print("labelNames",split.labelNames);
      

if __name__ == "__main__":
    import argparse;
    parser = argparse.ArgumentParser();
    parser.add_argument("--yamls", nargs="+", required=True);
    options = parser.parse_args();
    testImportData(options); 

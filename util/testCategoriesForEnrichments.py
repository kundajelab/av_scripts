#!/usr/bin/env python
import sys, os;
scriptsDir = os.environ.get("UTIL_SCRIPTS_DIR");
if (scriptsDir is None):
    raise Exception("Please set environment variable UTIL_SCRIPTS_DIR");
sys.path.insert(0,scriptsDir);
import pathSetter;
import argparse;
import fileProcessing as fp;
import util;

def getNormalisedRatio(theDict, theTotal):
    theRatios = {};
    for aKey in theDict:
        theRatios[aKey] = float(theDict[aKey])/theTotal;
    return theRatios;

def getClusterEnrichments(clusterDict, categoriesDict):
    clusterCategoryCounts = {};
    clusterTotalCounts = {};
    categoryTotalCounts = {};
    total = 0;
    for aKey in clusterDict:
        cluster = clusterDict[aKey];
        category = categoriesDict[aKey];
        if cluster not in clusterCategoryCounts:
            clusterCategoryCounts[cluster] = {};
            clusterTotalCounts[cluster] = 0;
        if category not in clusterCategoryCounts[cluster]:
            clusterCategoryCounts[cluster][category] = 0;
        if category not in categoryTotalCounts:
            categoryTotalCounts[category] = 0;
        clusterCategoryCounts[cluster][category] += 1;
        clusterTotalCounts[cluster] += 1;
        categoryTotalCounts[category] += 1;
        total += 1;
    clusterCategoryRatios = {};
    for clusterKey in clusterCategoryCounts:
        clusterCategoryRatios[clusterKey] = {};
        for category in clusterCategoryCounts[clusterKey]:
            clusterCategoryRatios[clusterKey][category] = float(clusterCategoryCounts[clusterKey][category])/clusterTotalCounts[clusterKey];
    categoryRatios = getNormalisedRatio(categoryTotalCounts, total);
    clusterRatios = getNormalisedRatio(clusterTotalCounts, total);
    return clusterCategoryRatios, categoryRatios, clusterRatios, total;

def getEnrichments(options):
    clusterDict = fp.simpleDictionaryFromFile(fp.getFileHandle(options.clusterInfoFile), options.clusterInfoFileIdIdx, options.clusterInfoFileClusterIdx, not options.clusterInfoFileTitleAbsent);
    categoriesDict = fp.simpleDictionaryFromFile(fp.getFileHandle(options.categoriesInfoFile), options.categoriesInfoFileIdIdx, options.categoriesInfoFileCategoryIndex, not options.categoriesInfoFileTitleAbsent);
    return getClusterEnrichments(clusterDict, categoriesDict);

if __name__ == "__main__":
    parser = argparse.ArgumentParser();
    parser.add_argument("--clusterInfoFile", required=True);
    parser.add_argument("--clusterInfoFileTitleAbsent", action="store_true");
    parser.add_argument("--clusterInfoFileIdIdx", type=int, default=0);
    parser.add_argument("--clusterInfoFileClusterIdx", type=int, default=1);
    parser.add_argument("--categoriesInfoFile", required=True);
    parser.add_argument("--categoriesInfoFileTitleAbsent", action="store_true");
    parser.add_argument("--categoriesInfoFileIdIdx", type=int, default=0);
    parser.add_argument("--categoriesInfoFileCategoryIndex", type=int, default=1);

    options = parser.parse_args();
    clusterCategoryRatios, categoryRatios, clusterRatios, total = getEnrichments(options);
    clusters = sorted(clusterRatios.keys());
    categories = sorted(categoryRatios.keys());
    print "Total",total;
    for cluster in clusters:
        print "cluster",cluster;
        print "ratio",clusterRatios[cluster];
        enrichments = [];
        for category in categoryRatios:
            enrichments.append((str(category)+":",clusterCategoryRatios[cluster][category] if category in clusterCategoryRatios[cluster] else 0,"vs",categoryRatios[category]));
        enrichments = sorted(enrichments, key=lambda x: -x[1]/x[3]);
        for enrichment in enrichments: #hacky printing...
            print " ".join(str(x) for x in enrichment);

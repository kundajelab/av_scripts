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

def getClusterEnrichment(clusterDict, categoriesDict):
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
    clusterDict = fp.simpleDictionaryFromFile(options.clusterInfoFile, options.clusterInfoFileIdIdx, options.clusterInfoFileClusterIdx, options.clusterInfoFileTitlePresent);
    categoriesDict = fp.simpleDictionaryFromFile(options.categoryInfoFile, options.categoriesInfoFileIdIdx, options.categoriesInfoFileCategoryIndex, options.categoriesInfoFileTitlePresent);
       
if __name__ == "__main__":
    argparse = ArgumentParser();
    argparse.add_argument("--clusterInfoFile", required=True);
    argparse.add_argument("--clusterInfoFileTitlePresent", action="store_true");
    argparse.add_argument("--clusterInfoFileIdIdx", type=int, default=0);
    argparse.add_argument("--clusterInfoFileClusterIdx", type=int, default=1);
    argparse.add_argument("--categoriesInfoFile", required=True);
    argparse.add_argument("--categoriesInfoFileTitlePresent", action="store_true");
    argparse.add_argument("--categoriesInfoFileIdIdx", type=int, default=0);
    argparse.add_argument("--categoriesInfoFileCategoryIndex", type=int, default=1);
    argparse.add_argument("--categoriesInfoFileIdIdx", type=int, default=0);

    options = parser.parse_args();
    clusterCategoryRatios, categoryRatios, cluserRatios, total = getClusterEnrichments(options);
    clusters = sorted(clusterRatios.keys());
    categories = sorted(categoryRatios.keys());
    print "Total",total;
    for cluster in clusters:
        print "cluster",cluster;
        print "ratio",clusterRatios[cluster];
        for category in categoryRatios:
            print str(category)+":",clusterRatios[cluster][category],"vs",categoryRatios[category];

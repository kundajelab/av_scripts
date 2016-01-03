import matplotlib.pyplot as plt;
import sys;
import os;
scriptsDir = os.environ.get("UTIL_SCRIPTS_DIR");
if (scriptsDir is None):
	raise Exception("Please set environment variable UTIL_SCRIPTS_DIR");
sys.path.insert(0,scriptsDir);
import pathSetter;
import util;
import fileProcessing as fp;
import argparse;
import matplotlib.pyplot as plt
import numpy as np;
from collections import defaultdict

class StackedBarChartOptions(object):
    def __init__(self, stackedSeriesNames, colors):
        self.stackedSeriesNames=stackedSeriesNames;
        self.colors=colors;

def stackedBarChart(stackedMeans, stackedBarChartOptions, width=0.35, figSize=(10,10)):
    #stacked data is two-dimensional; first axis is the series, second
    #axis is the means.         
    cumulativePositiveBottom = np.zeros(stackedMeans.shape[1]);
    cumulativeNegativeBottom = np.zeros(stackedMeans.shape[1]);
    ind = np.arange(stackedMeans.shape[1]);
    plottedArrs = []
    plt.figure(figsize=figSize)
    for (seriesMeans,color) in zip(stackedMeans, stackedBarChartOptions.colors):
        p = plt.bar(ind, seriesMeans, width, color=color, bottom=cumulativePositiveBottom*(seriesMeans>0)+cumulativeNegativeBottom*(seriesMeans<0));
        plottedArrs.append(p)
        cumulativePositiveBottom += seriesMeans*(seriesMeans>0);
        cumulativeNegativeBottom += seriesMeans*(seriesMeans<0);
    plt.legend([x[0] for x in plottedArrs], stackedBarChartOptions.stackedSeriesNames);

    return plt;

#an attempt to make matplotlib somewhat as easy as R.
def plotHeatmap(data, logTransform=False, zeroCenter=False, cmap=plt.cm.coolwarm, figsize=(15,15)):
    fig, ax = plt.subplots(figsize=figsize)
    plotHeatmapGivenAx(ax, data , logTransform=logTransform
                                , zeroCenter=zeroCenter
                                , cmap=cmap);
    return plt;

def plotHeatmapGivenAx(ax, data, logTransform=False, zeroCenter=False, cmap=plt.cm.coolwarm):
    if logTransform:
        data = np.log(np.abs(data)+1)*np.sign(data);
    if (zeroCenter):
        data = data*((data<0)/np.abs(np.min(data)) + (data>0)/np.max(data));
    ax.pcolor(data, cmap=cmap);
    return ax;

def plotHeatmapSortedByLabels(arr, labels, *args, **kwargs):
    arrSortedByLabels = util.sortByLabels(arr, labels);
    countsPerLabel = defaultdict(lambda: 0);
    for label in labels:
        countsPerLabel[label] += 1;
    for label in sorted(countsPerLabel.keys(), key=lambda x: -x):
        print(label,":",countsPerLabel[label]);
    plotHeatmap(np.array(arrSortedByLabels), *args, **kwargs);
    
    
def barplot(data):
    plt.bar(np.arange(len(data)), data)
    return plt;

def scatterPlot(xycoords, labels=None, colors=None, figsize=(5,5)):
    """
        If labels is not none, will assign colors using
            points evenly sampled from
            Blue -> Violet -> Red -> Yellow -> Green
    """
    import matplotlib.pyplot as plt
    plt.figure(figsize=figsize)
    if (labels is None):
        plt.scatter(xycoords[:,0], xycoords[:,1])
    else:
        if (colors is None):
            maxLabel = np.max(labels);
            colors = [util.fracToRainbowColour(x/float(maxLabel)) for x in range(maxLabel+1)];
            print("No colors supplied, so autogen'd as:\n"+
                    "\n".join(str(x) for x in list(enumerate(colors))))
        plt.scatter(xycoords[:,0], xycoords[:,1], c=[colors[x] for x in labels]);

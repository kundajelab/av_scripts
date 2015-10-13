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
    plotHeatmapGivenAx(ax, data, logTransform, zeroCenter, cmap);
    return plt;

def plotHeatmapGivenAx(ax, data, logTransform=False, zeroCenter=False, cmap=plt.cm.coolwarm):
    if logTransform:
        data = np.log(np.abs(data)+1)*np.sign(data);
    if (zeroCenter):
        data = data*((data<0)/np.abs(np.min(data)) + (data>0)/np.max(data));
    ax.pcolor(data, cmap=cmap);
    return ax;

def barplot(data):
    plt.bar(np.arange(len(data)), data)
    return plt;


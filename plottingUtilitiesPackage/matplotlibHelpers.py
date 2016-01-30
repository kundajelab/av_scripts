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
    plt.show()
    return plt;

#an attempt to make matplotlib somewhat as easy as R.
def plotHeatmap(data, logTransform=False, zeroCenter=False, cmap=plt.cm.coolwarm, figsize=(15,15)):
    fig, ax = plt.subplots(figsize=figsize)
    plotHeatmapGivenAx(ax, data , logTransform=logTransform
                                , zeroCenter=zeroCenter
                                , cmap=cmap);
    plt.show()
    return plt;

def plotHeatmapGivenAx(ax, data, logTransform=False, zeroCenter=False, cmap=plt.cm.coolwarm):
    if logTransform:
        data = np.log(np.abs(data)+1)*np.sign(data);
    if (zeroCenter):
        data = data*((data<0)/(1 if np.min(data)==0 else np.abs(np.min(data))) + (data>0)/np.max(data));
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
    
def barplot(data, figsize=None, dashedLine=None, title=""):
    plt.figure(figsize=figsize);
    plt.title(title)
    plt.bar(np.arange(len(data)), data)
    if (dashedLine is not None):
        plt.axhline(dashedLine, linestyle='dashed', color='black')
    plt.show()
    return plt;

def plotHist(data, bins=None, figsize=(7,7), title=""):
    if (bins==None):
        bins=len(data)
    plt.figure(figsize=figsize);
    plt.hist(data,bins=bins)
    plt.title(title)
    plt.show()

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
            colors = [util.fracToRainbowColour(x/float(maxLabel))
                        if x > 0 else util.fracToRainbowColour(0)
                        for x in range(maxLabel+1)];
            print("No colors supplied, so autogen'd as:\n"+
                    "\n".join(str(x) for x in list(enumerate(colors))))
        plt.scatter(xycoords[:,0], xycoords[:,1], c=[colors[x] for x in labels]);
    plt.show();

def plotImage(image, dpiMultiplier=1):
    assert len(image.shape)==2 or len(image.shape)==3;
    if (len(image.shape)==3):
        assert image.shape[2]==3;
    dpi = int(20*dpiMultiplier);
    margin = 0.05 # (5% of the width/height of the figure...)
    xpixels, ypixels = image.shape[0], image.shape[1]

    # Make a figure big enough to accomodate an axis of xpixels by ypixels
    # as well as the ticklabels, etc...
    figsize = (1 + margin) * ypixels / dpi, (1 + margin) * xpixels / dpi

    fig = plt.figure(figsize=figsize, dpi=dpi)
    # Make the axis the right size...
    ax = fig.add_axes([margin, margin, 1 - 2*margin, 1 - 2*margin])

    ax.imshow(image, interpolation='none')
    plt.show()

def plotOneHotEncodingsAsImage(oneHotEncodings, *args, **kwargs):
    assert len(oneHotEncodings.shape)==3;
    assert oneHotEncodings.shape[1]==4;
    colors = [(0,1,0), (0,0,1), (1,1,0), (1,0,0)];
    image = np.array([[colors[np.argmax(oneHotEncoding[:,i])]\
                    if np.max(oneHotEncoding[:,i])>0 else (0,0,0)
                    for i in xrange(oneHotEncoding.shape[1])]
                for oneHotEncoding in oneHotEncodings])
    plotImage(image, *args, **kwargs); 
     
    

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

###WTF did I do below this like idk what I was thinking


#PLOT OPTIONS!
class PlotOptions: #try to design this to be compatible with the objects resulting from argparse!
	def __init__(self,title=None, xlabel=None, ylabel=None):
		self.title = title;
		self.xlabel = xlabel;
		self.ylabel = ylabel;

def applyPlotOptions(plotOptions,plot):
	if (plotOptions.title is not None):
		plot.title = plotOptions.title;
	if (plotOptions.xlabel is not None):
		plot.xlabel = plotOptions.xlabel;
	if (plotOptions.ylabel is not None):
		plot.ylabel = plotOptions.ylabel;

def getPlotOptionsArgumentParser(): #note that the resulting parsed object doubles up as a PlotOptions!
	parser = argparse.ArgumentParser(add_help=False);
	parser.add_argument('--title',help="Title of plot");
	parser.add_argument('--xlabel', help="x-label of plot");
	parser.add_argument('--ylabel', help="y-label of plot");
	return parser;

#FILTER OPTIONS!
class FilterOptions: #desiging this to be compatible with the objects resulting from argparse!
	def __init__(self, minVal=None, maxVal=None):
		self.minVal = None;
		self.maxVal = None;

def applyFilterOptions(filterOptions, arr):
	toReturn = [x for x in arr if (
			(filterOptions.minVal == None or filterOptions.minVal < x)
			and (filterOptions.maxVal == None or filterOptions.maxVal > x))];
	lenAfter = len(toReturn);
	lenBefore = len(arr);
	percentRetained = 100*float(lenAfter)/lenBefore;
	print str(len(toReturn))+" retained from "+str(len(arr))+" after filtering - "+str(percentRetained)+"%";
	return toReturn;

def getFilterOptionsArgumentParser():
	parser = argparse.ArgumentParser(add_help=False);
	parser.add_argument('--minVal', help="Minimum value to be considered", type=float);
	parser.add_argument('--maxVal', help="Maximum value to be considered", type=float);
	return parser;

def quickHistogram(arr,outputPath="out.png",plotOptions=PlotOptions(),filterOptions=None):
	if (filterOptions is not None):
		arr = applyFilterOptions(filterOptions,arr);
	plt.hist(arr);
	applyPlotOptions(plotOptions,plt);
	plt.savefig(outputPath);

def fileToHistogram(inputFile
	, outputPath=None
	, plotOptions=PlotOptions()
	, filterOptions=None):
	arr = [float(x) for x in fp.readRowsIntoArr(fp.getFileHandle(inputFile))];
	if (outputPath == None):
		outputPath = fp.getFileNameParts(inputFile).getFilePathWithTransformation(lambda x: "hist_"+x, extension=".png");
	quickHistogram(arr, outputPath, plotOptions, filterOptions);


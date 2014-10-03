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

class PlotOptions: #try to design this to be compatible with the objects resulting from argparse!
	def __init__(self,title=None, xlabel=None, ylabel=None):
		self.title = title;
		self.xlabel = xlabel;
		self.ylabel = ylabel;

def applyPlotOptions(plotOptions,plt):
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

def quickHistogram(arr,outputPath="out.png",plotOptions=PlotOptions()):
	plt.hist(arr);
	applyPlotOptions(plotOptions,plt);
	plt.savefig(outputPath);

def fileToHistogram(inputFile
	, outputPath=None
	, toNumFunction=util.chainFunctions(fp.trimNewline,fp.stringToFloat)
	, plotOptions=PlotOptions()
	, progressUpdates=None):
	arr = fp.transformFileIntoArray(fp.getFileHandle(inputFile),transformation=toNumFunction,progressUpdates=progressUpdates);
	if (outputPath == None):
		outputPath = fp.getFileNameParts(inputFile).getFilePathWithTransformation(lambda x: "hist_"+x, extension=".png");
	quickHistogram(arr, outputPath, plotOptions);


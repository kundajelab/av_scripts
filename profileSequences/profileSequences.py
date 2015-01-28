#!/srv/gs1/software/python/python-2.7/bin/python
import sys;
import os;
scriptsDir = os.environ.get("UTIL_SCRIPTS_DIR");
if (scriptsDir is None):
    raise Exception("Please set environment variable UTIL_SCRIPTS_DIR");
sys.path.insert(0,scriptsDir);
import pathSetter;
import argparse;
import fileProcessing as fp;
import util;
import stats;

def profileSequences(args):
    countProfilerFactories = [];
    if (args.kmer is not None):
        countProfilerFactories.append(KmerCountProfilerFactory(lambda x: x.upper(), args.kmer));
    if (args.lowercase):
        countProfilerFactories.append(getLowercaseCountProfilerFactory());
    if (args.gcContent):
        countProfilerFactories.append(getGcCountProfilerFactory());
    if (args.baseCount):
        countProfilerFactories.append(getBaseCountProfilerFactory());
    
    (profilerNameToCategoryCountsMap,blah) = profileInputFile(
            args.inputFiles
            , countProfilerFactories
            , categoryFromInput=((lambda x: x[args.groupByColIndex]) if (args.groupByColIndex is not None) else (lambda x: "defaultCategory"))
            , sequenceFromInput=(lambda x: x[args.sequencesColIndex])
            , preprocessing = util.chainFunctions(fp.trimNewline,fp.splitByTabs)
            , progressUpdates=args.progressUpdates
            , ignoreInputTitle=(not (args.hasNoTitle))
        );
    significantDifferences = computeSignificantDifferences(
        profilerNameToCategoryCountsMap    
        , args.significanceThreshold);
    
    toPrint = "";
    for category in significantDifferences:
        if (args.tabDelimitedOutput == False):
            toPrint = toPrint + "-----\n" + category + ":\n-----\n";
        if (args.tabDelimitedOutput):
            toPrint += SignificantResults.tabTitle()+"\n";
        toPrint = toPrint + "\n".join([x.tabDelimString() if args.tabDelimitedOutput else str(x) for x in significantDifferences[category]])+"\n";
    
    if (args.outputFile is None):
        args.outputFile = fp.getFileNameParts(args.inputFiles[0]).getFilePathWithTransformation(lambda x: 'profiledDifferences_'+x, '.txt');
        
    fp.writeToFile(args.outputFile, toPrint);
    

def profileInputFile(inputFiles
    , countProfilerFactories
    , categoryFromInput
    , sequenceFromInput
    , preprocessing=None
    , filterFunction=None
    , transformation=lambda x: x
    , progressUpdates=None
    , ignoreInputTitle=False):
    #init map of count profiler name to map of category-->count
    profilerName_to_categoryToCountMaps = {};
    categoryCounts = {};    
    def action(input,i): #the input is the value of the line after preprocess, filter and transformation
        category = categoryFromInput(input);
        sequence = sequenceFromInput(input);
        if (category not in categoryCounts):
            categoryCounts[category] = 0;
        categoryCounts[category] += 1;
        for countProfilerFactory in countProfilerFactories:
            if (countProfilerFactory.profilerName not in profilerName_to_categoryToCountMaps):
                profilerName_to_categoryToCountMaps[countProfilerFactory.profilerName] = {}
            if (category not in profilerName_to_categoryToCountMaps[countProfilerFactory.profilerName]):
                profilerName_to_categoryToCountMaps[countProfilerFactory.profilerName][category] = countProfilerFactory.getCountProfiler();
            profilerName_to_categoryToCountMaps[countProfilerFactory.profilerName][category].process(sequence);
    
    for inputFile in inputFiles:
        print "Processing",inputFile;
        inputFileHandle = fp.getFileHandle(inputFile);
        fp.performActionOnEachLineOfFile(
            inputFileHandle
            ,action
            ,preprocessing=preprocessing
            ,filterFunction=filterFunction
            ,transformation=transformation
            ,ignoreInputTitle=ignoreInputTitle
            ,progressUpdates=progressUpdates
        );
    return profilerName_to_categoryToCountMaps,categoryCounts;        


#to be used in conjunction with output of profileInputFile
def computeSignificantDifferences(
        profilerName_to_categoryToCountMaps
        ,significanceThreshold=0.01
    ):
    significantDifferences = {};
    for profilerName in profilerName_to_categoryToCountMaps:
        print "Profiling: "+profilerName;
        categoryCountMap = profilerName_to_categoryToCountMaps[profilerName];
        significantDifferences[profilerName] = profileCountDifferences(categoryCountMap,significanceThreshold);
    return significantDifferences;    
    

class CountProfiler:
    def __init__(self,keysGenerator,profilerName):
        self.counts = {};
        self.keysGenerator = keysGenerator;
        self.profilerName = profilerName;
        self.sequencesProcessed = 0;
    def process(self,sequence):
        self.sequencesProcessed += 1;
        for key in self.keysGenerator(sequence):
            if (key not in self.counts):
                self.counts[key] = 0;
            self.counts[key] += 1;
    def normalise(self):
        total = 0;
        for aKey in self.counts:
            total += self.counts[aKey];
        self.total = total;
        self.normalisedCounts = {};
        for aKey in self.counts:
            self.normalisedCounts[aKey] = float(self.counts[aKey])/total;
        return self.normalisedCounts;

class CountProfilerFactory(object):
    def __init__(self,keysGenerator,profilerName):
        self.keysGenerator = keysGenerator;
        self.profilerName = profilerName;
    def getCountProfiler(self):
        return CountProfiler(self.keysGenerator,self.profilerName);
    
class LetterByLetterCountProfilerFactory(CountProfilerFactory):
    def __init__(self,letterToKey,profilerName):
        super(self.__class__,self).__init__(getLetterByLetterKeysGenerator(letterToKey),profilerName);

def getLetterByLetterKeysGenerator(letterToKey):
    def keysGenerator(sequence):
        for letter in sequence:
            yield letterToKey(letter);
    return keysGenerator; 

def getLowercaseCountProfilerFactory():
    lowercaseAlphabet = ['a','c','g','t','n']
    uppercaseAlphabet = ['A','C','G','T']
    def letterToKey(x):
        if (x in lowercaseAlphabet):
            return 'acgt';
        if (x in uppercaseAlphabet):
            return 'ACGT';
        if (x == 'N'):
            return 'N';
        raise Exception("Unexpected dna input: "+x);
    return LetterByLetterCountProfilerFactory(letterToKey, 'LowercaseCount');

#!!!if you change this, PLEASE remember to update getGCcontent in perSequence_profile.py 
GCkeys = util.enum(GC='GC', AT='AT', N='N');
def gcLetterToKey(x):
    if (x in ['c','g','C','G']):
        return GCkeys.GC;
    if (x in ['a','t','A','T']):
        return GCkeys.AT;
    if (x == 'N' or x=='n'):
        return GCkeys.N;
    raise Exception("Unexpected dna input: "+x); 

def getGcCountProfilerFactory():
    return LetterByLetterCountProfilerFactory(gcLetterToKey, 'GC-content');

def getBaseCountProfilerFactory():
    return LetterByLetterCountProfilerFactory(lambda x: x.upper(), 'BaseCount');

#TODO: implement more efficient rolling window if perf is issue
class KmerCountProfilerFactory(CountProfilerFactory):
    def __init__(self,stringPreprocess,kmerLength):
        super(KmerCountProfilerFactory,self).__init__(getKmerGenerator(stringPreprocess,kmerLength),str(kmerLength)+"-mer");

def getKmerGenerator(stringPreprocess,kmerLength):
    def keysGenerator(sequence):
        sequence = stringPreprocess(sequence);
        #not the best rolling window but eh:
        for i in range(0,len(sequence)-kmerLength+1):
            yield sequence[i:i+kmerLength];
    return keysGenerator;
    

def profileCountDifferences(mapOfCategoryToCountProfiler,significanceThreshold=0.01):
    significantResults = [];
    keyTotals = {};
    grandTotal = 0;
    for category in mapOfCategoryToCountProfiler:
        mapOfCategoryToCountProfiler[category].normalise();
        counts = mapOfCategoryToCountProfiler[category].counts;
        grandTotal += mapOfCategoryToCountProfiler[category].total;
        for key in counts:
            if key not in keyTotals:
                keyTotals[key] = 0;
            keyTotals[key] += counts[key];
    #performing the hypgeo test:
    for category in mapOfCategoryToCountProfiler:
        print("Profiling differences for "+category);
        counts = mapOfCategoryToCountProfiler[category].counts;
        for key in counts:
            special = keyTotals[key];
            picked = mapOfCategoryToCountProfiler[category].total;
            specialPicked = counts[key];
            testResult = stats.proportionTest(grandTotal,special,picked,specialPicked);
            if (testResult.pval <= significanceThreshold):
                significantResults.append(SignificantResults(grandTotal,special,picked,specialPicked,testResult,key,category));
    return significantResults;

class SignificantResults:
    def __init__(self,total,special,picked,specialPicked,testResult,specialName="special",pickedName="picked"):
        self.total = total;
        self.special = special;
        self.picked = picked;
        self.specialPicked = specialPicked;
        self.testResult = testResult;
        self.specialName = specialName;
        self.pickedName = pickedName;
        self.pickedRatio = 0 if self.picked == 0 else float(self.specialPicked)/self.picked;
        self.specialUnpicked = self.special-self.specialPicked;
        self.unpicked = self.total - self.picked;
        self.unpickedRatio = 0 if self.unpicked == 0 else float(self.specialUnpicked)/self.unpicked;
    def __str__(self):
        pickedRatio = float(self.specialPicked)/self.picked;
        unpickedRatio = 0 if self.total == self.picked else float(self.special-self.specialPicked)/(self.total - self.picked);
        return self.pickedName+" for "+self.specialName+" - "+str(pickedRatio)+" vs. "+str(unpickedRatio)+"; "+(str(self.testResult)
            +", "+self.specialName+": "+str(self.special)
            +", "+self.pickedName+": "+str(self.picked)
            +", both: "+str(self.specialPicked)
            +", total: "+str(self.total)); 
    def tabDelimString(self):
        return self.pickedName+"\t"+self.specialName+"\t"+self.testResult.tabDelimString()+"\t"+str(self.pickedRatio)+"\t"+str(self.unpickedRatio)+"\t"+str(self.specialPicked)+"\t"+str(self.picked)+"\t"+str(self.specialUnpicked)+"\t"+str(self.unpicked);
    @staticmethod
    def tabTitle():
        return "pickedName\tspecialName\t"+stats.TestResult.tabTitle()+"\tpickedRatio\tunpickedRatio\tspecialPicked\tpicked\tspecialUnpicked\tunpicked";

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Profiles the sequences");
    parser.add_argument('inputFiles',nargs='+');
    parser.add_argument('--outputFile',help="If not specified, name will be 'profiledDifferences_inputFile'");
    parser.add_argument('--tabDelimitedOutput', action="store_true");
    parser.add_argument('--significanceThreshold',type=float,default=0.01);
    parser.add_argument('--progressUpdates',type=int);
    parser.add_argument('--hasNoTitle',action="store_true");
    parser.add_argument('--groupByColIndex',type=int);
    parser.add_argument('--sequencesColIndex',type=int,required=True);
    parser.add_argument('--baseCount', action='store_true');
    parser.add_argument('--gcContent', action='store_true');
    parser.add_argument('--lowercase', action='store_true');
    parser.add_argument('--kmer', type=int);
    args = parser.parse_args();
    profileSequences(args);    





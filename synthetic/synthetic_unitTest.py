from __future__ import division;
from __future__ import print_function;
import os, sys;
scriptsDir = os.environ.get("UTIL_SCRIPTS_DIR");
if (scriptsDir is None):
    raise Exception("Please set environment variable UTIL_SCRIPTS_DIR");
sys.path.insert(0,scriptsDir);
import pathSetter;
import util;
from synthetic import synthetic;

def basicInstantiationTests():
    synthetic.GeneratedSequence();
    synthetic.Embedding("what",10);
    synthetic.AdditionalInfo();  

def basicPositionGeneratorUnitTest(positionGeneratorInstance, lenBackground=100, lenSubstring=10):
    additionalInfo = synthetic.AdditionalInfo();
    positionGeneratorInstance.generatePos(lenBackground, lenSubstring, None);
    positionGeneratorInstance.generatePos(lenBackground, lenSubstring, additionalInfo);
    assert additionalInfo.isInTrace(positionGeneratorInstance.name);

def basicPositionGeneratorUnitTests():
    basicPositionGeneratorUnitTest(synthetic.UniformPositionGenerator());
    basicPositionGeneratorUnitTest(synthetic.InsideCentralBp(50));
    basicPositionGeneratorUnitTest(synthetic.OutsideCentralBp(50));
    print("Done basicPositionGeneratorUnitTests");

def basicEmbedderUnitTest(embeddableEmbedder, length=100):
    backgroundStringArr = ["X" for x in xrange(length)];
    priorEmbeddedThings = synthetic.PriorEmbeddedThings_numpyArrayBacked(length);
    additionalInfo = synthetic.AdditionalInfo();  
    embeddableEmbedder.embed(backgroundStringArr, priorEmbeddedThings, None); 
    embeddableEmbedder.embed(backgroundStringArr, priorEmbeddedThings, additionalInfo); 
    assert additionalInfo.isInTrace(embeddableEmbedder.name);

def getEmbeddableEmbedderOfFixedString(aString,name=None):
    return synthetic.EmbeddableEmbedder(embeddableGenerator=synthetic.SubstringEmbeddableGenerator(synthetic.FixedSubstringGenerator(aString)),name=name)   

def basicEmbedderUnitTests():
    basicEmbedderUnitTest(getEmbeddableEmbedderOfFixedString("oink",name="blah"));
    basicEmbedderUnitTest(synthetic.XOREmbedder(embedder1=getEmbeddableEmbedderOfFixedString("ab")
                                                ,embedder2=getEmbeddableEmbedderOfFixedString("cd")
                                                ,probOfFirst=0.3));
    basicEmbedderUnitTest(synthetic.RandomSubsetOfEmbedders(quantityGenerator=synthetic.FixedQuantityGenerator(2)
                            ,embedders=[getEmbeddableEmbedderOfFixedString("ab"), getEmbeddableEmbedderOfFixedString("cd")]));
    basicEmbedderUnitTest(synthetic.RepeatedEmbedder(quantityGenerator=synthetic.FixedQuantityGenerator(2),embedder=getEmbeddableEmbedderOfFixedString("ab"))); 
    print("Done basicEmbedderUnitTests");

def runUnitTests():
    basicPositionGeneratorUnitTests();
    basicEmbedderUnitTests();

runUnitTests();

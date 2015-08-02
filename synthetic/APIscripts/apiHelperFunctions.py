from __future__ import division;
from __future__ import print_function;
from __future__ import absolute_import;
import os;
import sys;
scriptsDir = os.environ.get("UTIL_SCRIPTS_DIR");
if (scriptsDir is None):
    raise Exception("Please set environment variable UTIL_SCRIPTS_DIR");
sys.path.insert(0,scriptsDir);
from synthetic import synthetic;

def getLoadedMotifs(options):
    loadedMotifs = synthetic.LoadedEncodeMotifs(options.pathToMotifs, pseudocountProb=options.pcProb)
    return loadedMotifs;

def getMotifGenerator(motifName, loadedMotifs, options):
    kwargs={'loadedMotifs':loadedMotifs}
    if (options.useBestHitForMotifs):
        theClass=synthetic.BestHitPwmFromLoadedMotifs;
        kwargs['bestHitMode']=bestHitMode=pwm.BEST_HIT_MODE.pwmProb; #prob don't need to twiddle this
    else:
        theClass=synthetic.PwmSamplerFromLoadedMotifs;
    motifGenerator=theClass(motifName=motifName,**kwargs)
    return motifGenerator;




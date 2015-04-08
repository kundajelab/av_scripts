import dlFramework;
enhancerScriptsDir = os.environ.get("ENHANCER_SCRIPTS_DIR");
if (enhancerScriptsDir is None):
    raise Exception("Please set environment variable ENHANCER_SCRIPTS_DIR");
sys.path.insert(0,enhancerScriptsDir);


class NN_yamlBasedInit_commandConstructor(CommandConstructor):
   def __init__(self):
        super(NN_yamlBasedInit, self).__init__(enhancerScriptsDir+"/pylearn2_local/NN_yamlBasedInit.py"); 

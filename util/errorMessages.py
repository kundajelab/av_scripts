
def assertParameterNecessaryForMode(parameterName, parameter, modeName, mode):
    if (parameter is None):
        raise RuntimeError(parameterName+" is necessary when "+modeName+" is "+mode);
    
def assertParameterIrrelevantForMode(parameterName, parameter, modeName, mode):
    if (parameter is not None):
        raise RuntimeError(parameterName+" is irrelevant when "+modeName+" is "+mode);

def unsupportedValueForMode(modeName, mode):
   raise RuntimeError("Unsupported value for "+modeName+": "+str(mode)); 

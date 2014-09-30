import os;

def executeAsSystemCall(commandToExecute):
	print "Executing: "+commandToExecute;
	if (os.system(commandToExecute)):
		raise "Error encountered with command "+commandToExecute;

def enum(**enums):
    return type('Enum', (), enums)

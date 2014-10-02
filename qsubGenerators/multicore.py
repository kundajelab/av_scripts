#!/usr/bin/python
import sys;
sys.path.insert(0,"/home/avanti/av_scripts");
import qsubHelp as qh;

def main():
	if (len(sys.argv) < 4):
		print "arguments: [qsubShellScriptPath] [email] [numCores] command...";
		raise;

	qsubShellScriptPath = sys.argv[1];
	email = sys.argv[2];
	numCores = sys.argv[3];
	command = " ".join(sys.argv[4:]);
	writeQsubFile(qsubShellScriptPath,email,numCores,command);

def writeQsubFile(qsubShellScriptPath, email, numCores, command):
	header = qh.getDefaultHeaderBasedOnFilePath(qsubShellScriptPath, email);
	header.numCores = numCores
	qh.writeQsubFile(qsubShellScriptPath, header, command);

main(); 

#!/usr/bin/python
import sys;
sys.path.insert(0,"/home/avanti/av_scripts");
import qsubHelp as qh;

def writeDefaultQsubFile(qsubShellScriptPath, email, command):
	header = qh.getDefaultHeaderBasedOnFilePath(qsubShellScriptPath, email);
	qh.writeQsubFile(qsubShellScriptPath, header, command);

if (len(sys.argv) < 3):
	print "arguments: [qsubShellScriptPath] [email] command...";
	raise;

qsubShellScriptPath = sys.argv[1];
email = sys.argv[2];
command = " ".join(sys.argv[3:]);
writeDefaultQsubFile(qsubShellScriptPath,email,command);

 

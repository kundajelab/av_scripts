import sys;
sys.path.insert(0, '../');
import handySubroutines as hs;

fh = hs.getFileHandle("oink.txt");
print fh.readline()
fh = hs.getFileHandle("oink.txt.gz");
print fh.readline()

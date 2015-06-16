import sys

SCORESEQFILENAME = sys.argv[1]
OUTPUTFILENAME = sys.argv[2]

def getNumSeqOccurrences():
	# Get the number of occurrences of each sequence in an output file from scoreSeq.py
	seqDict = {}
	scoreSeqFile = open(SCORESEQFILENAME)
	scoreSeqFile.readline() # Remove the header
	for line in scoreSeqFile:
		# Iterate through the lines of the file from score seq, and increment the counts for each sequence
		lineElements = line.split("\t")
		currentSeq = lineElements[2]
		if currentSeq in seqDict.keys():
			# The current sequence is in the dictionary, so add 1 to its count
			seqDict[currentSeq] = seqDict[currentSeq] + 1
		else:
			# Add the current sequence to the dictionary
			seqDict[currentSeq] = 1
	scoreSeqFile.close()
	return seqDict

def outputSeqDict(seqDict):
	# Output the sequence dictionary
	outputFile = open(OUTPUTFILENAME, 'w+')
	for seq in seqDict.keys():
		# Iterate through the sequences and record each and its count
		outputFile.write(seq + "\t" + str(seqDict[seq]) + "\n")
	outputFile.close()

if __name__=="__main__":
	seqDict = getNumSeqOccurrences()
	outputSeqDict(seqDict)
	
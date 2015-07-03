import sys

SEQUENCESFILENAME = sys.argv[1] # ASSUMES THAT ALL SEQUENCES ARE THE SAME LENGTH
SEQ = sys.argv[2]
CENTERNUM = int(sys.argv[3])
OUTPUTFILENAME = sys.argv[4]
INCLUDERCINT = int(sys.argv[5])

def makeSequenceRC():
	# Make the sequence's reverse complement
	rc = ""
	for base in SEQ:
		# Iterate through the bases and get the reverse complement of each
		if base == "A":
			# At A, so convert it to a T
			rc = "T" + rc
		elif base == "C":
			# At C, so convert it to a G
			rc = "G" + rc
		elif base == "G":
			# At G, so convert it to a C
			rc = "C" + rc
		elif base == "T":
			# At T, so convert it to a A
			rc = "A" + rc
		else:
			# At a wild card
			rc = base + rc
	return rc

def evaluateInCenterOutside(currentSequence, centerStart, centerEnd, seqRC):
	# Evaluate whether SEQ is in the center or the outside of the current sequence
	if CENTERNUM == 0:
		# Evaluate whether SEQ is in the sequence
		if SEQ in currentSequence:
			# SEQ is in the sequence
			return [1, 0]
		return [0, 0]
	inCenter = 0
	inOutside = 0
	if SEQ in currentSequence[centerStart:centerEnd]:
		# The sequence is in the center
		inCenter = 1
	elif seqRC != "":
		if seqRC in currentSequence[centerStart:centerEnd]:
			# The sequence is in the center
			inCenter = 1
	if (SEQ in currentSequence[0:centerStart]) or (SEQ in currentSequence[centerEnd:len(currentSequence)]):
		# The sequence is in the outside
		inOutside = 1
	elif seqRC != "":
		if (seqRC in currentSequence[0:centerStart]) or (seqRC in currentSequence[centerEnd:len(currentSequence)]):
			# The sequence is in the center
			inOutside = 1
	return [inCenter, inOutside]

def getNumSpecificSeqOccurrences(seqRC):
	# Get the number of occurrences of each sequence in an output file from scoreSeq.py
	sequencesFile = open(SEQUENCESFILENAME)
	numCenter = 0
	numOutside = 0
	currentSequence = sequencesFile.readline().strip()
	seqLen = len(currentSequence)
	center = int(round(seqLen/2))
	centerStart = center - int(round(CENTERNUM/2))
	centerEnd = center + int(round(CENTERNUM/2))
	outputFile = open(OUTPUTFILENAME, 'w+')
	[inCenter, inOutside] = evaluateInCenterOutside(currentSequence, centerStart, centerEnd, seqRC);
	outputFile.write(str(inCenter) + "\t" + str(inOutside) + "\n")
	numCenter = numCenter + inCenter
	numOutside = numOutside + inOutside
	for line in sequencesFile:
		# Iterate through the lines 
		currentSequence = line.strip()
		[inCenter, inOutside] = evaluateInCenterOutside(currentSequence, centerStart, centerEnd, seqRC);
		outputFile.write(str(inCenter) + "\t" + str(inOutside) + "\n")
		numCenter = numCenter + inCenter
		numOutside = numOutside + inOutside
	sequencesFile.close()
	outputFile.close()
	print numCenter
	print numOutside

if __name__=="__main__":
	seqRC = ""
	if INCLUDERCINT == 1:
		# Include the reverse complement
		seqRC = makeSequenceRC()
	getNumSpecificSeqOccurrences(seqRC)
	
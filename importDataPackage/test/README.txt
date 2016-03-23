#different modes
python testImportData.py --yamls differentModes_features.yaml featuresFastaInColumn.yaml differentModes_labels.yaml splits.yaml
#output looks like this:
Subset of labels to use is specified
Processed 1 lines of featureFile1_fasta.txt
Processed 2 lines of featureFile1_fasta.txt
('WARNING.', 'id3', 'was not found in train/test/valid splits')
This is the only time such a warning will be printed. Remaining such ids will be silently ignored
Processed 3 lines of featureFile1_fasta.txt
(1, 'rows skipped from', 'featureFile1_fasta.txt')
Processed 1 lines of featureFile2_fasta.txt
Processed 2 lines of featureFile2_fasta.txt
(0, 'rows skipped from', 'featureFile2_fasta.txt')
Done loading in fastas
(0, 'rows skipped from', 'featureFile1_part2.txt')
(0, 'rows skipped from', 'featureFile1_part1.txt')
('WARNING.', 'id3', 'was not found in train/test/valid splits')
This is the only time such a warning will be printed. Remaining such ids will be silently ignored
(1, 'rows skipped from', 'featureFile1_fastaInColumn.txt')
(0, 'rows skipped from', 'featureFile2_fastaInColumn.txt')
Returning desired dict
('WARNING.', 1, ' ids in the train/test/valid split files were not found in the input feature file. The first ten are: ', ['idNonExist'])
('splitName', 'train')
('ids', ['id1', 'id2'])
('X', OrderedDict([('inputMode1', [array([[[ 1.,  0.,  0.,  0.,  1.,  0.,  0.,  0.],
        [ 0.,  1.,  0.,  0.,  0.,  1.,  0.,  0.],
        [ 0.,  0.,  1.,  0.,  0.,  0.,  1.,  0.],
        [ 0.,  0.,  0.,  1.,  0.,  0.,  0.,  1.]]]), array([[[ 0.,  0.,  0.,  1.,  0.,  0.,  0.,  1.],
        [ 0.,  1.,  0.,  0.,  0.,  0.,  1.,  0.],
        [ 0.,  0.,  1.,  0.,  0.,  1.,  0.,  0.],
        [ 1.,  0.,  0.,  0.,  1.,  0.,  0.,  0.]]])]), ('inputMode2', [[1, 2], [1, 2]]), ('defaultInputModeName', [array([[[ 1.,  0.,  0.,  0.,  1.,  0.,  0.,  0.],
        [ 0.,  1.,  0.,  0.,  0.,  1.,  0.,  0.],
        [ 0.,  0.,  1.,  0.,  0.,  0.,  1.,  0.],
        [ 0.,  0.,  0.,  1.,  0.,  0.,  0.,  1.]]]), array([[[ 0.,  0.,  0.,  1.,  0.,  0.,  0.,  1.],
        [ 0.,  1.,  0.,  0.,  0.,  0.,  1.,  0.],
        [ 0.,  0.,  1.,  0.,  0.,  1.,  0.,  0.],
        [ 1.,  0.,  0.,  0.,  1.,  0.,  0.,  0.]]])])]))
('Y', OrderedDict([('labelMode1', [[0], [1]]), ('labelMode2', [[0.1, 5.3], [0.0, 1.1]])]))
('labelNames', OrderedDict([('labelMode1', ['lab2']), ('labelMode2', ['lab1', 'lab2'])]))
('splitName', 'valid')
('ids', ['id2'])
('X', OrderedDict([('inputMode1', [array([[[ 0.,  0.,  0.,  1.,  0.,  0.,  0.,  1.],
        [ 0.,  1.,  0.,  0.,  0.,  0.,  1.,  0.],
        [ 0.,  0.,  1.,  0.,  0.,  1.,  0.,  0.],
        [ 1.,  0.,  0.,  0.,  1.,  0.,  0.,  0.]]])]), ('inputMode2', [[1, 2]]), ('defaultInputModeName', [array([[[ 0.,  0.,  0.,  1.,  0.,  0.,  0.,  1.],
        [ 0.,  1.,  0.,  0.,  0.,  0.,  1.,  0.],
        [ 0.,  0.,  1.,  0.,  0.,  1.,  0.,  0.],
        [ 1.,  0.,  0.,  0.,  1.,  0.,  0.,  0.]]])])]))
('Y', OrderedDict([('labelMode1', [[1]]), ('labelMode2', [[0.0, 1.1]])]))
('labelNames', OrderedDict([('labelMode1', ['lab2']), ('labelMode2', ['lab1', 'lab2'])]))

#no modes
python testImportData.py --yamls featuresFasta.yaml labels.yaml splits.yaml
python testImportData.py --yamls featuresFastaInColumn.yaml labels.yaml splits.yaml
#produces:
Subset of labels to use is specified
Processed 1 lines of featureFile1_fasta.txt
Processed 2 lines of featureFile1_fasta.txt
('WARNING.', 'id3', 'was not found in train/test/valid splits')
This is the only time such a warning will be printed. Remaining such ids will be silently ignored
Processed 3 lines of featureFile1_fasta.txt
(1, 'rows skipped from', 'featureFile1_fasta.txt')
Processed 1 lines of featureFile2_fasta.txt
Processed 2 lines of featureFile2_fasta.txt
(0, 'rows skipped from', 'featureFile2_fasta.txt')
Done loading in fastas
Returning desired dict
('WARNING.', 1, ' ids in the train/test/valid split files were not found in the input feature file. The first ten are: ', ['idNonExist'])
('splitName', 'train')
('ids', ['id1', 'id2'])
('X', [array([[[ 1.,  0.,  0.,  0.,  1.,  0.,  0.,  0.],
        [ 0.,  1.,  0.,  0.,  0.,  1.,  0.,  0.],
        [ 0.,  0.,  1.,  0.,  0.,  0.,  1.,  0.],
        [ 0.,  0.,  0.,  1.,  0.,  0.,  0.,  1.]]]), array([[[ 0.,  0.,  0.,  1.,  0.,  0.,  0.,  1.],
        [ 0.,  1.,  0.,  0.,  0.,  0.,  1.,  0.],
        [ 0.,  0.,  1.,  0.,  0.,  1.,  0.,  0.],
        [ 1.,  0.,  0.,  0.,  1.,  0.,  0.,  0.]]])])
('Y', [[0], [1]])
('labelNames', ['lab2'])
('splitName', 'valid')
('ids', ['id2'])
('X', [array([[[ 0.,  0.,  0.,  1.,  0.,  0.,  0.,  1.],
        [ 0.,  1.,  0.,  0.,  0.,  0.,  1.,  0.],
        [ 0.,  0.,  1.,  0.,  0.,  1.,  0.,  0.],
        [ 1.,  0.,  0.,  0.,  1.,  0.,  0.,  0.]]])])
('Y', [[1]])
('labelNames', ['lab2'])

#Chaing duplicatesDisallowed to False
python testImportData.py --yamls features1.yaml features2.yaml labels.yaml splits.yaml 
Subset of labels to use is specified
(0, 'rows skipped from', 'featureFile1_part1.txt')
(0, 'rows skipped from', 'featureFile1_part2.txt')
Subset of labels to use is specified
(0, 'rows skipped from', 'featureFile2.txt')
Returning desired dict
('WARNING.', 1, ' ids in the train/test/valid split files were not found in the input feature file. The first ten are: ', ['idNonExist'])
('splitName', 'train')
('ids', ['id1', 'id2'])
('X', [[1, 2, 3.1], [1, 2, 3.2]]) #there is a subset of features to use going on
('Y', [[0], [1]])
('labelNames', ['lab2'])
('splitName', 'valid')
('ids', ['id2'])
('X', [[1, 2, 3.2]])
('Y', [[1]])
('labelNames', ['lab2'])

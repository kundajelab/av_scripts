from optparse import OptionParser
import os
import math
from time import gmtime, strftime
import re
'''
Author:Oana Ursu
'''

def main():
    parser=OptionParser()

    parser.add_option('--metadata',dest='metadata',help='Metadata file. One line per condition. Should be tab or space-delimited: 1. Individual, 2. sample name (unique),3. fastq1, 4. fastq2, 5. genome_path (for instance for <path>/NA19099 the genome_path=path), 6. gender,7. vcf file for personal genome,alignment directory. If any of these entries is missing, e.g. fastq2 is missing, say NA. Header should start with #')
    opts,args=parser.parse_args()

  
    sample_di={}
    for line in open(opts.metadata).readlines():
        if line[0]=='#':
            continue
        items=line.strip().split()
        individual=items[0]
        fastq1=items[2]
        fastq2=items[3]
        sample_name=items[1]
        genome=items[4]
        gender=items[5]
        vcf_file=items[6]
        align_dir=items[7]
        seqOrImputed=items[8]
        if sample_name in sample_di.keys():
            sys.exit('Sample name '+sample_name+' appears multiple times in the metadata. Please recreate your metadata to have unique sample names')
        else:
            sample_di[sample_name]={}
            sample_di[sample_name]['sample_name']=sample_name
            sample_di[sample_name]['individual']=individual
            sample_di[sample_name]['fastq1']=fastq1
            sample_di[sample_name]['fastq2']=fastq2
            sample_di[sample_name]['genome_path']=genome
            sample_di[sample_name]['gender']=gender
            sample_di[sample_name]['vcf']=vcf_file
            sample_di[sample_name]['alignment_directory']=align_dir
            sample_di[sample_name]['seqOrImputed']=seqOrImputed
            sample_di[sample_name]['aligned_bam']=sample_di[sample_name]['alignment_directory']+'tagAlign/'+sample_di[sample_name]['sample_name']+'_reconcile.dedup.q30.nochrM.bam'
            sample_di[sample_name]['QC_dir']='/srv/gs1/projects/snyder/jzaugg/histoneQTL/ChIPseq_alignment/results/Alignments/tagAlign/QC/'
            sample_di[sample_name]['fragment_length_file']=sample_di[sample_name]['QC_dir']+os.path.basename(sample_di[sample_name]['aligned_bam'])+'SPP_table.txt'
            sample_di[sample_name]['peak_call_directory']='/srv/gs1/projects/snyder/jzaugg/histoneQTL/ChIPseq_alignment/results/peakCalls/'
            sample_di[sample_name]['merge_group']='NA'
            for merge_group in ['H3K4ME1','H3K4ME3','H3K27AC']:
                if merge_group in sample_di[sample_name]['sample_name']:
                    sample_di[sample_name]['merge_group']=merge_group
            #sample_di[sample_name]['merge_dir']=sample_di[sample_name]['peak_call_directory']+'ALL_109_individuals_merged_peaks_'+sample_di[sample_name]['merge_group']+'/'
            sample_di[sample_name]['merge_dir']=sample_di[sample_name]['peak_call_directory']+'Unrelated_75_individuals_merged_peaks_'+sample_di[sample_name]['merge_group']+'/' 
            os.system('mkdir '+sample_di[sample_name]['merge_dir'])

    out=open(opts.metadata+'_for_peakCalling','w')
    

    #Replicate combos. Need to add columns: replicate group, whether it's input, peak output for the group
    replicate_groups={}
    chromo_people=['GM18486','GM19193','GM19238','GM19239','GM19240'] 
    for sample_name in sample_di.keys():
        print sample_name
        simple_sample_name='NA'
        if 'chromoPaper' in sample_di[sample_name]['seqOrImputed']:
            if 'INPUT' in sample_name:
                simple_sample_name=sample_name
            else:
                simple_sample_name=sample_name.split(re.findall(re.compile('_[0-9]'),sample_name)[0])[0]
        else:
            simple_sample_name=re.sub('-1','',re.sub('-2','',sample_name))
        #if simple_sample_name not in replicate_groups.keys():
        #    replicate_groups[simple_sample_name]=set()
        #replicate_groups[simple_sample_name].add(sample_name)
        replicate_groups[sample_name]=simple_sample_name

    print replicate_groups
    out=open(opts.metadata+'_for_peakCalling','w')
    out.write('#Individual\tSampleName\tFQ1\tFQ2\tGenomePath\tGender\tVcfFile\tAlignmentDirectory\tSequencedOrImputed\tAlignedBam\tQCdir\tfragLenFile\tpeakDir\tReplicateGroup\tIsInput\tInputName\tMergeGroup\tMergeDir\n')
    #FOR THIS STUDY WE WILL BE USING JUST 1 UNiVERSAL INPUT
    input_for_all='/srv/gs1/projects/snyder/jzaugg/histoneQTL/ChIPseq_alignment/results/Alignments/chromoVar_done_alignments/tagAlign/merged_replicates/subsampled/INPUT_7YRI_GM19239_GM19238_GM18505_GM19240_GM19099_GM19193_GM18486.subsampleTo77000000.tagAlign.gz'
    for sample_name in sample_di.keys():
        print sample_name
        if 'chromoPaper' in sample_di[sample_name]['seqOrImputed']:
            isYRI=False
            for p in chromo_people:
                if p in sample_name:
                    isYRI=True
            if 'INPUT' in sample_name:
                continue
            if isYRI==False:
                continue
        input_status='INPUT' in sample_name
        out.write(sample_di[sample_name]['individual']+'\t'+sample_di[sample_name]['sample_name']+'\t'+sample_di[sample_name]['fastq1']+'\t'+sample_di[sample_name]['fastq2']+'\t'+sample_di[sample_name]['genome_path']+'\t'+sample_di[sample_name]['gender']+'\t'+sample_di[sample_name]['vcf']+'\t'+sample_di[sample_name]['alignment_directory']+'\t'+sample_di[sample_name]['seqOrImputed']+'\t'+sample_di[sample_name]['aligned_bam']+'\t'+sample_di[sample_name]['QC_dir']+'\t'+sample_di[sample_name]['fragment_length_file']+'\t'+sample_di[sample_name]['peak_call_directory']+'\t'+replicate_groups[sample_name]+'\t'+str(input_status)+'\t'+input_for_all+'\t'+sample_di[sample_name]['merge_group']+'\t'+sample_di[sample_name]['merge_dir']+'\n')
    



main()

#!/bin/bash

#
#
#
#
#
usage='Error >USAGE: my_script <ref_fasta> <gff> <batch_fastq> <log-file> <taxid> <batch>'


if [[ $# < 4 ]]; then
echo $usage
exit;
fi



seq_fasta=$1
seq_gff3=$2
batch_fastq=$3
log_file=$4
taxid=$5
batch=$6


if [[ ! -d $taxid ]]; then mkdir $taxid; fi
cd $taxid
if [[ ! -d taxid_$taxid_$batch ]]; then mkdir taxid_$taxid_$batch ; fi
cd taxid_$taxid_$batch


## tach name tu ten file : https://www.cyberciti.biz/faq/bash-get-basename-of-filename-or-directory-name/
name="$(basename -- $seq_fasta)"
name=`echo $name|cut -d\. -f1`
## minimap $3 to $1

if [ ! -e $name.sam ]; then
minimap2 -ax map-ont $seq_fasta $batch_fastq > $name.sam
fi
echo '<---------minimap2------------>'

if [ ! -e $name.bam ]; then
samtools view -S -b $name.sam > $name.bam
fi
echo '<---------sam to bam------------>'

if [ ! -e $name.sorted.bam ]; then
samtools sort -o $name.sorted.bam $name.bam
fi
echo '<---------sorted bam------------>'

if [ ! -e $name.sorted.bam.bai ]; then
samtools index $name.sorted.bam
fi
echo '<---------index bam------------>'

cat $seq_fasta >$name.fna
if [ ! -e $name.fna.fai ]; then
samtools faidx $name.fna
fi
echo '<---------index fna------------>'




### prepare config Jbrowser

#gff3 process
sort -k1,1 -k4,4n $seq_gff3 > $name.sorted.gff3
(grep ^"#" $seq_gff3; grep -v ^"#" $seq_gff3 | grep -v "^$" | grep "\t" | sort -k1,1 -k4,4n) > $name.sorted.gff3

bgzip --force $name.sorted.gff3
tabix -p gff $name.sorted.gff3.gz

### config Jbrowser

echo '[GENERAL]'					>tracks.conf
echo "refSeqs=$name.fna.fai"				>>tracks.conf
echo ''						>>tracks.conf
echo '[tracks.refseq]'					>>tracks.conf
echo "urlTemplate=$name.fna"				>>tracks.conf
echo 'storeClass=JBrowse/Store/SeqFeature/IndexedFasta' >>tracks.conf
echo 'type=Sequence'					>>tracks.conf
echo "key=refseq-$name"				>>tracks.conf
echo ''						>>tracks.conf
echo '[tracks.genes]'					>>tracks.conf
echo "urlTemplate=$name.sorted.gff3.gz"			>>tracks.conf
echo 'storeClass=JBrowse/Store/SeqFeature/GFF3Tabix'	>>tracks.conf
echo 'type=CanvasFeatures'				>>tracks.conf
echo ''						>>tracks.conf
echo '[tracks.alignments]'				>>tracks.conf
echo "urlTemplate=$name.sorted.bam"			>>tracks.conf
echo 'storeClass=JBrowse/Store/SeqFeature/BAM'		>>tracks.conf
echo 'type=Alignments2'					>>tracks.conf
echo ''						>>tracks.conf
echo '[tracks.my-bam-coverage-track]'			>>tracks.conf
echo 'storeClass = JBrowse/Store/SeqFeature/BAM'	>>tracks.conf
echo "urlTemplate = $name.sorted.bam"			>>tracks.conf
echo 'type = JBrowse/View/Track/SNPCoverage'		>>tracks.conf
echo 'metadata.Description = SNP/Coverage view of volvox-sorted.bam, simulated  resequencing alignments.' >>tracks.conf
echo "key = BAM - $name.sort SNPs/Coverage"		>>tracks.conf
 
cd ../
cd ../

echo "DONE"


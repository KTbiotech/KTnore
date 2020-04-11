#!/bin/bash

#dùng để mapping so song dưới nền từ môt danh sách ref cho trước
USAGE='para_map.sh <fastq> <reflist(csv)> <outdir>'
fastq=$1
ref=$2 # tsv 2 cotchứa đường dẫn đến các file ref: cot1 chua ten, cot2 chua duong dan
out=$3 # thu muc chua file ket qua file bam vâ sam
fname=`basename $fastq .fastq`

cat $ref|while read line
do
    reffa=`cut -d "," -f2 <(echo $line)`
    refname=`cut -d "," -f1 <(echo $line)`
    name=$out"/"$refname"map"$fname
    echo "Created $name.sam"
    echo "----------"
    my_map(){
	reffa=$1
	fastq=$2
	$name=$3
    	minimap2 -ax map-ont $reffa $fastq > $name.sam
    	samtools view -bS $name.sam|samtools sort -O bam -o $name.sorted.bam
    	samtools index $name.sorted.bam $name.sorted.bai
	}
    my_map $reffa $fastq $name 
done
wait

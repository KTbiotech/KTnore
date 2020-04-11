#!/bin/bash

USAGE='myscript <folder_realtime> <projectID> <summary_meta>'

if [[ $# < 2 ]]; then
	echo $USAGE
	exit
fi

projectID=$2

if [ -d ./$2 ]; then
	echo " projectID $projectID exits"
	exit
else
	mkdir $projectID
fi

cd $projectID



##
###------------------------------------
##
summary_meta=$3
main_process(){
	file=$1
	batch=`basename $file`
if [[ ! -d $batch ]]; then mkdir $batch; fi
cd $batch
####################################
echo '|||||||||||||||||header extract'
## Extract header fastq >> $batch.meta-header.txt
grep "@" $file| sed 's/@//g' > $batch.meta-header.temp
## Join with summary_meta >>$batch.meta-sumary.txt

awk '{print $1}' $batch.meta-header.temp > $batch.id-fastq.temp

grep -wFf $batch.id-fastq.temp $summary_meta > $batch.meta-summary.temp

#add header
head -n 1 $summary_meta > header.temp
cat header.temp $batch.meta-summary.temp > $batch.meta-summary.txt


rm header.temp
rm $batch.meta-summary.temp
rm $batch.meta-header.temp
####################################
#OUTPUT for web: $batch.meta-summary.txt
##????
###################################

#cetrifuge

centrifuge_flag="ON"
if [[ $centrifuge_flag == "ON" ]]; then
echo "|||||||||||||||||centrifuge"
centrifuge_indexs='/opt/lampp/htdocs/realtime/gia-data/centrifuge-indexs/p_compressed+h+v/p_compressed+h+v'
thress=8
centrifuge -x $centrifuge_indexs -p $thress \
	-q $file \
	--min-hitlen 22 \
	-S $batch.readtoTaxid.centrifuge.tsv \
	--report-file $batch.centrifuge_report.tsv
echo "|||||||||||||||||centrifuge-kreport"

centrifuge-kreport -x $centrifuge_indexs $batch.readtoTaxid.centrifuge.tsv > $batch.kreport.tsv

sorted_flag="OFF"
if [[ $sorted_flag == "ON" ]]; then
	##
	echo "Somethings";
fi


## Ket noi kreport va $batch.readtoTaxid.centrifuge.tsv > $batch.summary-meta-taxid.tsv
##?
####################################
#OUTPUT for web: $batch.summary-meta-taxid.tsv
##????
###################################
fi

####MAPPING>
ref_flag="OFF"
if [[ $ref_flag == "ON" ]] && [[ $centrifuge_flag == "ON" ]] ; then
centrifuge-inspect --conversion-table $centrifuge_indexs > taxid_indexs_centrifuge.tsv


#check exit from centrigue indexs
ref_list='/opt/lampp/htdocs/realtime/gia-data/data/ref_list'
awk '{print $2}' taxid_indexs_centrifuge.tsv|sort|uniq -c > taxid_indexs_centrifuge.count.tsv
grep -wFf $ref_list taxid_indexs_centrifuge.count.tsv > isExitsRef-centrifuge.temp

join -1 2 -2 1 -a2 -o 1.1,1.2,2.1 <(sort -k2 isExitsRef-centrifuge.temp) <(sort -k1 $ref_list) > isExitsRef-centriguge.txt
fi

#check exit from custom_ref file
custom_ref_flag="OFF"
if [[ $custom_ref_flag == "ON" ]]; then
ref_custom.lst=''

grep -wFf $ref_list ref_custom.lst > isExitsRef.custom.avaible
join -1 1 -2 2 -a1 -o 1.1,2.2 <(sort -k1 isExitsRef.custom.avaible) <(sort -k1 $ref_list) > isExitsRef-custom.txt
fi
###MAPPING ((((
map_flag="ON"
if [[ $map_flag == "ON" ]]; then
isExitsRef="/opt/lampp/htdocs/realtime/gia-data/data/ref_list"
cat "$isExitsRef"|while read line ; do

	taxid=`echo $line |awk '{print $1}'`;
	ref_fasta=`echo $line |awk '{print $2}'`;
	ref_gff=`echo $line |awk '{print $3}'`;

#./my_script_jbrowser.sh	
# my_script <ref_fasta> <gff> <batch_fastq> <log-file> <taxid> <batch>


bash '/opt/lampp/htdocs/realtime/gia-data/my_script_jbrowser.sh' $ref_fasta $ref_gff $file "$batch.$taxid.log" $taxid $batch


done



fi


####)))))MAPPING

#######AMR(((
amg_flag="ON"
if [[ $amg_flag == "ON" ]]; then 
###./my_blast.sh <files_fastq> <title_blastdb> <out_folder_files>

bash '/opt/lampp/htdocs/realtime/gia-data/my_blast.sh' $file B_$batch blast_folder 

fi





#########)))AMR

cd ../	

}; 
## )))main_process

##############
folder_realtime=$1
realtime_flag="ON"

if [[ $realtime_flag == "ON" ]]; then
inotifywait -m -r "$folder_realtime" -e close_write -e moved_to --exclude ".*\.log"|
while read path action file;do

((total_files++))
((new_files++))
filelist=("${filelist[@]}" "$path$file")

# last file is ${filelist[@]}

main_process  ${filelist[@]}
unset filelist
done

else
	cat $folder_realtime/*.fastq > endpoint.fnq
	main_process endpoint.fnq
	echo "DONE"

fi
#/// Do it!!





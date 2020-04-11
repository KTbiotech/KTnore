#!/usr/bin/env python3

#Last update: 10/11/2019
#Author: H-Van-Phuc
#
#

#import modules
import argparse
import os
from os import path
import re
import operator
import shutil
import plotly
import plotly.graph_objects as go
from subprocess import Popen, PIPE
from Bio import SeqIO
from time import time
from datetime import datetime
import json
from termcolor import cprint
import random
import shutil
import plotly.graph_objects as go
import plotly.io as pio
from Bio import SeqIO
import pandas as pd

####
this=os.getcwd()
#

def makedir(container, sample, timepoint): # return True nếu tạo được các thư mục con
    '''
    Tạo ra các thư mục output cho chương trình
    Tham số:
    --------
    container: str ~ jobID
        Thư mục cha cho tất cả các thư mục con bên trong:
        gồm samples>timpoint dict
    sample: (str)
        thư mục sample
    timepoint: (str)
        thực mực timpoint
    
    Returns
    --------
        global subdir
        chứa đường dẫn đến tât cả các thư mục con gồm sample và compare tại 1 thời điểm

    '''
    global subdir  #  biến globals cho subdir
    subdir={"file":"1.Files", # files gốc ( xủ lý giải nén, kiểm tra status) chuẩn bị cho workflow cùng các tham số (.txt) cho workflows,
            "QC":"2.QC", # chứa các tập tin fastqc, multiqc, qualimap
            "trim":"3.Trimming", # chứa files sau khi trimming
            "taxonomy":"4.Taxonomy", # chứa các #folder cho phân loại taxonomy
            "centrifuge":"4.Taxonomy/4.1.Centrifuge", # chứa các output của Centrifuge
            "map":"5.Map"
            }
    container=this + "/" + container
    if os.path.exists ("{}/{}/{}".format(container,sample,timepoint)):
        print ("Thu muc \n {}/{}/{} ton tai".format(container,sample,timepoint))
        rquest=input('Xoa thu muc ton tai va tiep tuc [Y/n]: ' )
        if rquest == 'Y':
            shutil.rmtree(container)
            print ("Xoa thanh cong va tao moi thu muc \n {}".format(container))
        else:
            print ("Thu muc khong the xoa:\n {}".format(container))
            exit()
    for sub in list(subdir.keys()):
            subdir[sub]="{}/{}/{}/{}".format(container,sample,timepoint,subdir[sub] ) #  full path đến thư mục con
            os.makedirs( subdir[sub] ) # tạo ra thư mục và các thư mục trung gian nếu không tồn tại trước đó
            print ("Created: {}".format(subdir[sub]))
    
    compare_container="{}/{}/{}".format(container, "0.compare", timepoint)
    '''
    if not os.path.exists(compare_container):
        os.makedirs(compare_container) # tạo thư mục compare ngang cấp với sample và có thư mục con là timpoint
    return subdir
    '''
def randomid(n): #return một dãy số ngẫu nhiên n
    '''
    Tạo ra một dãy số chứa n số ngãu nhiên
    params:
        n : int
    return:
        global randomid (str)
    '''
    global randomid
    randomid=''
    for i in range(n):
        randomid=randomid + str(random.randint(1, 9))
    return randomid

def writelog(filelog,msg):
    '''
    Chương trình dùng để viết file sgm vào file log cố đinh, con trực
    tieps của thư mục jobid
    '''
    with open (filelog,"a") as log:
        log.write("{}\n".format(msg))


def centrifuge (files,out,args,format='-q',threads='16', name='custom', minhit=0, minscore=300,
                x='/media/kt02/DATA/Phuc_folders/Dev/NGS/db/centrifugeINDEX/p_compressed+h+v/p_compressed+h+v',prefer=False):
    
    '''
    Thực hiện phân loại bằng centrifuge
    params:


        files: (str) đường dẫn đến files
        format: (str) fastq
        threads: (int) (option -p)
        name: (str) prefix của file output
        minhit: (int) chiều dài hit tối thiểu -cutoff
        minscore: (int) điểm phân loaị tối thiểu
        out: (str) thự mục output
        x: (str) đường dẫn ( prefix) đến indecies

    return:
        Không return:
        Trả kết quả về  3 file:
        custom.cf.detail.out,
        custom.cf.report.tsv,
        custom.cf.kraken.tsv,
        custom.cf.sumary : thong ke ve so luong read, so luong read clasifed, so luong read unclassied
            nằm trong thưc mục out=subdir[centrifuge]
    '''
    centrifuge_cmd= "centrifuge" + " -x {} -p {} -S {} --report-file {} {} {}".format (
                x,
                threads,
                subdir['centrifuge'] + "/" + name + ".cf.detail.out",
                subdir['centrifuge'] + "/" + name + ".cf.report.tsv",
                format,
                files
                )
    print (centrifuge_cmd +"\n-----\n")
    proc4=Popen(centrifuge_cmd, stdout=PIPE, stderr=PIPE, shell=True)
    proc4.wait()

    kraken_rp_cmd="centrifuge-kreport" +" -x {} --min-score {} --min-length {} {} > {}".format(
                x,
                300, # --min-score
                35, # --min-length
                subdir['centrifuge'] + "/" + name + ".cf.detail.out",
                subdir['centrifuge'] + "/" + name + ".cf.kraken.tsv"
                )
    print(kraken_rp_cmd +"\n-----\n")
    proc4=Popen(kraken_rp_cmd, stdout=PIPE, stderr=PIPE, shell=True)
    proc4.wait()

    dfkreport=pd.read_csv(subdir['centrifuge'] + "/" + name + ".cf.kraken.tsv", sep="\t", header=None)
    dfkreport.columns=['Percentage','taxonRead', 'cladeRead','Rank','taxID','Name']
    overview, summary, custom=dict(), dict(), dict()
    ##some functions
    def taxonRead(df, taxID):
        '''
        '''
        taxID=int(taxID)
        query=df[df['taxID']== taxID]
        taxonRead=0 if len(query)==0 else query.iloc[0]['taxonRead']
        taxonName='N/A' if len(query)==0 else query.iloc[0]['Name']
        return [taxID,taxonName,taxonRead]

    overview['BACTERIA']=taxonRead(dfkreport,"2")
    overview['EUKARYOTA']=taxonRead(dfkreport,"2759")
    overview['VIRUSES']=taxonRead(dfkreport,"10239")
    overview['ARCHAEA']=taxonRead(dfkreport,"2157")
    summary["read-analysed"]=taxonRead(dfkreport,"1")
    summary["read-unclassified"]=taxonRead(dfkreport,"0")
    summary["read-classified"]=summary["read-analysed"][-1] -  summary["read-unclassified"][-1]

    f=subdir['centrifuge'] + "/summary.txt"
    with open(f,"w") as f:
        f.write("var overview = {} ;\n".format(overview))
        f.write("var summary = {} ;\n".format(summary))
        #nếu có danh sách các taxid quan tâm, cần ghi thêm biến prefer để lưu trữ
        if prefer != False:
            fprefer=open(prefer,"r")
            for line in fprefer:
                custom[line]=taxonRead(dfkreport,line)
            f.write("var custom = {} ;\n".format(custom))

    piec_cmd="{} {} {}".format("python3 piec.py", 
                    subdir['centrifuge'] + "/summary.txt",
                    subdir['centrifuge'] + "/chart.html" ) 
    print (piec_cmd)
    proc4=Popen(piec_cmd, stdout=PIPE, stderr=PIPE, shell=True)
    proc4.wait()

    writelog(args.filelog,"{}\t{}\t{}\t{}\t{}\t{}\t{}".format(
                args.timepoint, # time point
                args.job, # jobID
                args.sample, # sample
                os.getppid,
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'), # parrent pid proccessing
                "CENTRIFUGE",
                "STOP"
    )
           )

    # file f cần cho việc xây dưng html và vẽ plot


def extract_guppyQC(guppy_file,file,outguppy, outhtml,sample): #return dataFrame của gupp_extract_custom.summary.txt
    '''
    Tạo ra bảng con Guppy theo trình từ header cho trước
    params
    ---------
    guppy-file (file): file chứa kết quả summary.txt từ guppy calling
    file (fastq hoặc fasta): dùng để tách header
    outguppy: output của file gupp_extract_custom.summary.txt
    outhtml: output htm cua pycoQC
    sample: sample title pycoQC

    return
    ---------
    return dataFrame của gupp_extract_custom.summary.txt
    '''
    global dfextract
    dfguppy=pd.read_csv(guppy_file, sep='\t') # mặc định dòng 1 là header header=True

    #extract header từ file
    header=[record.id for record in SeqIO.parse(file, "fastq")]
    dfheader=pd.DataFrame(header)
    dfheader.columns=['read_id'] 
    #extract guppy df
    dfextract=dfguppy.merge(dfheader,on="read_id", how='inner')
    exfile="{}/gupp_extract_{}.summary.txt".format(outguppy,file.split("/")[-1].split(".")[0])
    dfextract.to_csv(exfile, sep="\t")


    '''
    pycoQC
    '''
    pycoQCtemplate="/media/kt02/DATA/Phuc_folders/Dev/py/pycoQC-template.html"
    pycoQC_cmd="pycoQC" + "  --summary_file {}  --html_outfile {}  --min_pass_qual {} --min_pass_len {} --report_title {} --template_file {}".format(
                exfile,
                "{}/{}.html".format(outhtml,sample),
                7,
                0,
                sample,
                pycoQCtemplate
                )
    print (pycoQC_cmd +"\n-----\n")
    proc2=Popen(pycoQC_cmd, stdout=PIPE, stderr=PIPE, shell=True)
    proc2.wait()
    return dfextract # guppy summary

def Nanoplot (fastq_rich,out,sample,threads=16):
    '''
    Thông kế bằng nanoPlot, sau này sẽ thay thế bằng NanoStatics
    params
    ---------
    threads:
        threads được sử dungj mặc định là 16
    fastq_rich:
        file fastq chưa thông tin meta
    out:
        thưc mục chưa kết quả
    sample (str)
        tên mẫu được sử dụng như prefix cho các output files
    return
        không return
    ---------
    '''
    nanoplot_cmd="NanoPlot" + " -t {}  --fastq_rich {} --outdir {} --prefix {}_".format(
                threads,
                fastq_rich,
                out,
                sample
                )
    print (nanoplot_cmd +"\n-----\n")
    proc2=Popen(nanoplot_cmd, stdout=PIPE, stderr=PIPE, shell=True)
    proc2.wait()
def pyCoQC_bam(guppy_file,bampath, outhtml,sample):
    '''
    QC file bam từ kết quả mapping
    params:N
    --------
    guppy_file:
        file chứa kết quả summary từ guppy
    bampath (thực mục chứ file các file bam)
        bampath từ kết quả minimap2: eg /*.bam
    outhtml (folder)
        folder chứa kết quả html
    sample: (str)
        tên

    return:
        không return
        kết quả là một file html nằm trong thư mục html
    '''
    pycoQC_cmd="pycoQC" + "  --summary_file {}  --html_outfile {} --bam_file {}  --report_title {}".format(
                guppy_file,
                "{}/{}.map.html".format(outhtml,sample),
                bampath,
                sample
                )
    print (pycoQC_cmd +"\n-----\n")
    proc2=Popen(pycoQC_cmd, stdout=PIPE, stderr=PIPE, shell=True)
    proc2.wait()

def bamcov(bam, out):
    '''
    thống kê về file bam ( sorted)
    params
    ---------
    bam
        file bam
    out (path)
        đường dẫn tuyêt đối đến file ( bao gồm cả tên file)
    
    return
    --------
    Không return
        kết quả là mọt file out
    '''
    bamcov_sh="/media/kt02/DATA/Phuc_folders/Dev/NGS/tools/bamcov/bamcov"
    bamcov_cmd=bamcov_sh + " --output {} {}".format(out,bam)
    proc2=Popen(bamcov_cmd, stdout=PIPE, stderr=PIPE, shell=True)
    proc2.wait()
def bamindex(sam, out): # return đường dân đến file bam sorted tương ứng
    '''
    sam to bam file va index file bam
    params
    ---------
    sam:
        sam file
    out: 
        thưc mục chứa kết quả
    return
    --------
    đường dẫn đến file bam sorted tương ứng
    '''
    name=sam.split("/")[-1].split(".")[0]
    samtools_cmd="samtools view -bS {}|samtools sort  -O bam  -o {}".format(sam, "{}/{}.sort.bam".format(out,name))
    samindex_cmd="samtools index {} {}".format(
        "{}/{}.sort.bam".format(out,name),
        "{}/{}.sort.bai".format(out,name))
    proc2=Popen(samtools_cmd, stdout=PIPE, stderr=PIPE, shell=True)
    proc2.wait()
    proc2=Popen(samindex_cmd, stdout=PIPE, stderr=PIPE, shell=True)
    proc2.wait()

    return "{}/{}.sort.bam".format(out,name)
def extract_seq(file,header,name,out):
    '''
    Extract fastq file từ danh sách các header cho trước
    params:
    file (file)
        file fastq : file nguồn
    header (file)
        file chứa các header
    name (str)
        tên file được tao ra
    out (str)
        folder lưu file name.fastq 
    '''
    seqtk_cmd="seqtk" + " subseq {} {} > {}".format(file,header,"{}/{}.html".format(out,name))
    proc2=Popen(seqtk_cmd, stdout=PIPE, stderr=PIPE, shell=True)
    proc2.wait()
def plotbytime(cf_report,cf_detail,guppy_file,out,cutoff=10):
    '''
    sử dụng in-house script plotbytime.py để vẽ 3 biểu đồ plot theo thời gian, chưa có xét cutoff manh,
    và điều này có thể khác với k-report
    params:
    --------
    plotbytime.py <CENTRIFUGEreport(.tsv)> <CENTRIFUGEdetail (.tsv)> <GUPPYsummary (.tsv)> <seqcount_cutoff (int)> <output(html)>
    cutoff: loài đượ cho tồn tại (+1) khi số lượng read lớn hơn giá trị cutoff
    return:
    -------
    Không return
    '''
    plot_cmd="python3 plotbytime.py {} {} {} {} {}".format(
            cf_report,
            cf_detail,
            guppy_file,
            cutoff,
            out
            )
    print (plot_cmd +"\n-----\n")
    proc4=Popen(plot_cmd, stdout=PIPE, stderr=PIPE, shell=True)
    proc4.wait()

def filecheck(files, out):
    '''
    Kiểm tra file format và giải nén file khi cần
    Tham số:
    --------
    files; list
        Danh sách chứa các đường dẫn file cần kiểm tra
    out: (folder)
        Folder chứa các tập tin giải nén, hoặc di chuyển
    
    Returns
    --------
        No return

    '''
    valid=['fastq', 'fastq.gz'] # valid format files
    for file in files:
        if path.isfile('file') == False: #kiem tra files co ton tai hay khong
            print ("Khong tim thay files {}".format(file))
            flag=False
        if flag != False:
            base=file.split("/")[-1].split(".")[-1]
            if base not in valid:
                print ("Format file khong phai la fastq {}".format(file))
                flag=False
        
        if flag == False:
            exit()

def maptorefs (fastq, ref_csv,out):
    '''
    para_map.sh dùng để mapping và xử lý cá file sam> sortedbam và bai
    params:
    ------------
    USAGE='para_map.sh <fastq> <reflist(csv)> <outdir>'
    fastq: hoặ fasta
        file fastq/fasta dùng để mapping bằng minimap2
    ref_csv:
        file csv chứa cột 1 là cột chứ tên chủng và cột 2 chứ đường dẫn đến file fasta ref
    out:
        thuwcc mục đầu ra

    return
        không return, 
        kết quả là các file sam và sorted.bam, bai
    '''
    para_map_cmd="./para_map.sh {} {} {}".format(fastq,ref_csv,out)
    print (para_map_cmd + "\n------\n")
    proc5=Popen(para_map_cmd, stdout=PIPE, stderr=PIPE, shell=True)
    proc5.wait()

#main()

def main():

    parser = argparse.ArgumentParser(
        prog='pypy.py',
        description="something about KTore"
    )
    parser.add_argument("-t", "--threads", dest="threads", default=16,
        help="something about threads")
    parser.add_argument('-x', '--indexdb', dest='indexdb',default="",
        help="something about index centrifuge")
    parser.add_argument("-f",dest="files", metavar='files',nargs='+',
        help='Something about file')
    parser.add_argument("-id", "--id-user", dest="job",default="123", 
        help="something about id jobs")
    parser.add_argument("-sp", "--sample-id", dest="sample",default="S1", 
        help="something about sample")
    parser.add_argument("-tp", "--time-point", dest="timepoint",default="t1", 
        help="something about timepoint")
    parser.add_argument("--prefer", dest="prefer",default=False, 
        help="something about prefer")
    parser.add_argument("--guppy-summary", dest="guppy_file", 
        help="something about guppy summary")
    parser.add_argument("--ref-csv", dest="ref_csv", default=False,
        help="something about ref-csv")
    parser.add_argument("--file-log", dest="filelog", default=True,
        help="something about filelog")

    args=parser.parse_args()
    if args.filelog: #mặc định là TRUE
        args.filelog="{}/{}/process.log".format(this,args.job)
    #print (args.files)
    #print (parser.print_help())
    writelog(args.filelog,"{}\t{}\t{}\t{}\t{}\t{}\t{}".format(
                args.timepoint, # time point
                args.job, # jobID
                args.sample, # sample
                os.getppid,
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'), # parrent pid proccessing
                "PY",
                "START"
    )
           )
    # bước 1: tạo ra các thư mục kết quả
    # randomid là mã số ID của job submit| global randomid (int)
    makedir(args.job,args.sample,args.timepoint) # tao ra thực mục cho output | global subdir (dict)
    #Chuyển fileinputs vào thực mục 1.files với rquest=True
    '''
    rquest=True
    filecheck(args.files, 'out')
    '''
    #NanoPlot
    files_str=" ".join(args.files) # file từ list to str
    Nanoplot(files_str,'{}/{}'.format(subdir['QC'],args.timepoint),args.sample)
    #pycoQC
    extract_guppyQC(args.guppy_file,args.files[0],subdir["QC"],subdir["QC"],args.sample)
    # Run centrifuge
    for i in range(len(args.files)):
        name=args.files[i].split('/')[-1].split('.')[0]
        centrifuge(args.files[i],subdir['centrifuge'],name=name,prefer=
        args.prefer, args=args)
    #plotbytime.py
        plotbytime(
            subdir['centrifuge'] + "/" + name + ".cf.report.tsv",
            subdir['centrifuge'] + "/" + name + ".cf.detail.out",
            args.guppy_file,
            out="{}/{}".format(subdir['centrifuge'],name),
            cutoff=10
        )
    #mutiple parallel mapping custom list
    '''
    if args.ref_csv != False:
        maptorefs(args.files[0],args.ref_csv,subdir['map'])
        pyCoQC_bam(args.guppy_file,
            "{}/*.sorted.bam".format(subdir['map']),
            subdir['map'],
            args.sample
        )
    '''

####################
#check input argv

####################

if __name__ == "__main__":
    main()

    exit()


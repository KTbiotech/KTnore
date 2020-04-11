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
from time import time, sleep
from datetime import datetime
import json
from termcolor import cprint
import random
import shutil
import plotly.graph_objects as go
import plotly.io as pio
from Bio import SeqIO
import pandas as pd
import ast
from termcolor import colored
import psutil # kiểm tra pid
from shutil import copyfile

####
this=os.getcwd()
########
## đầu tiên chạy chương trình monitor.py trước dưới background
# sig folder cần người dùng cup cấp bỡi
def readPID(pid):
    '''
    Chương trình dùng để kiểm tra PID có tồn tại hay không?
    '''
    if psutil.pid_exists(pid):
        return "RUNNING"
    else:
        return "STOP"

def realtime(jobid,logfile,sig_folder,mon_folder,timeout,tempfolder,summary_file,args):

    '''

    '''
    log=logfile # file chứa thông tin hàng chờ
    monitor_cmd="python3 monitorv2.py -sig {} -mo {} -tsc {} -toff {} -log {}".format(
                sig_folder, # folder làm signal để ghi nhận sự thay đổi
                mon_folder, # folder sẽ dùng để làm việc ! quan trọng
                5, # thời gian giữa các đợt scan
                timeout, # Thời gian timeout, nếu không có kết quả mới sẽ kết thúc chương trình monitor
                log
        )
    print ("{}\n".format(monitor_cmd))
    monitor=Popen(monitor_cmd,shell= True,close_fds=True)

    ##Dùng để kill chương trình khi cần thiết
    this_pid=os.getpid()
    monitor_pid=monitor.pid
    with open ("{}/pid.txt".format(tempfolder),"w") as pidfile:
        pidfile.write("{}|[{},{}]".format(
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    this_pid,
                    monitor_pid
                    ))
    print ("PID của chương trình đã được viết vào tập tin:\n" 
            + "{}/pid.txt".format(tempfolder)  )
    ##

    sleep(5)
    run,signal,mutiples,comparelist=[],'start',0,[]
    while signal != 'end':                                   # trong file supperlist hk có chữ end
        sleep(10)
        f=open(log,"r")                                 # mỗi lần lặp là mỗi lần đọc lại file hàng chờ
        for line in f:
            proc=line.strip().split("|")
            signal=proc[0]                                     # ID của hàng chờ cụ thể
            ####
            if signal not in run and signal != 'end' and signal !='': # id hàng chờ này khác 'end' và chưa xử lý
                run.append(signal)                            # đặt id hàng chờ vào đã xử lý
            
                print(colored(signal+"||Khởi động thực thi chương trình pypy.py với thông số signal", "green") )
                #####??? chạy chương trình chính dưới background#######################################
                samples=proc[1] # danh sách của mẫu sample sẽ xử lý, một dict() {S1: [file1, fil2]. S2: [file3, file 4]}
                samples=ast.literal_eval(samples)# chuyển đổi string to dict
                timepoint=proc[0] # thời điểm được đặt tên lại, t1, t2
                timedate=proc[2] # thời gian tuyệt đối
                #main()
                for sample in list(samples.keys()): # từng sample
                    if samples[sample] != []: # danh sách các file cần xử lý > concatenate  [file1, file2], tránh tập rỗng
                        # cat file
                        outcat="{}/{}_{}.cat.fastq".format(tempfolder,sample,timepoint)
                        strfile=" ".join([i for i in samples[sample]]) # file input cho option của cat
                        cat_cmd="python3 catfile.py -o {} -f {}".format(outcat,strfile)
                        print (cat_cmd)
                        cat=Popen(cat_cmd,
                                    shell=True) # kết nối các file ra file output
                        cat.wait() # catfile hoàn tất
                        print ("cat hoàn tất: {}".format(outcat))
                        
                        # run catfile bằng chương trình pypy.py
                        main_cmd="python3 pypy.py -t {} -id {} -sp {} -tp {} --guppy-summary {} -f {}".format(
                                16,
                                jobid, # JobID
                                sample,
                                timepoint,
                                summary_file,
                                outcat
                                )
                        
                        print ("{}:\n{}".format(" Khởi động chương trình dưới background", main_cmd))
                        #Run it

                        main_proc=Popen(main_cmd,shell= True,close_fds=True)
                        mutiples+=1

                        #### VIẾT PID VÀO FILE THEO DÕI VÀO FILE jobid/process.txt
                        #SIGNAL #PID #START #STATUS
                        with open("{}/process.pid".format(jobid), "a") as process_pid:
                            process_pid.write("{}\t{}\t{}\t{}\t{}\t{}\n".format(
                                signal,
                                jobid,
                                sample,
                                main_proc.pid,
                                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                'START')
                                )
                    
                #################
                
                # số luowngj chương trình đã xảy ra
                check=timepoint # thời điểm phân tích

                '''                                # số chương trình đang thực thi tăng thêm 1
                if mutiples == 3:                             # giới hạn số chương trình A.py thực thi cùng lúc ( nếu xảy ra) là 3
                    print("Phải đợi cho tất cả kết thúc rồi mới chạy tiếp")
                    ##??? Câu lệnh đợi chương trình chạy ẩn kết thúc
                    mutiples=0
                '''
                                                # cài lại mutiples=0
            elif signal == 'end':
                print ("Kết thức theo dõi, các tập đang xử lý sẽ tiếp tục và hoàn tất")
     
        if mutiples > 1 and os.path.isfile("{}/{}/process.log".format(this,jobid)) and check not in comparelist: # có 1 chương trình đã chay, bây h nhờ vòng lăp, kiểm tra trạng thái của nó
            run_proc=pd.read_csv("{}/{}/process.log".format(this,jobid), header=None, sep="\t")
            run_proc.columns=['SIG','JOB','SAMPLE','PID','START','STEP','STATUS']
            # tách cách có chữ STOP vào thời điểm t= check
            dfSTOP=run_proc.loc[(run_proc['STATUS'] == 'STOP') & (run_proc['SIG'] == check) & (run_proc['STEP'] == 'CENTRIFUGE')]
            
            if len(dfSTOP) > 0:
                sampleSTOP=dfSTOP['SAMPLE'].to_list()
                if set(sampleSTOP)==set(list(samples.keys())): # kiểm tra các mẫu đã chạy xong hết chưa
                    print ('OK chuẩn bị compare các kết quả vào thời điểm: ' + check)
                    comparefolder="{}/0.compare/{}".format(args.jobid,check)
                    if not os.path.exists(comparefolder):
                        os.makedirs(comparefolder) # tạo thư mục compare ngang cấp với sample và có thư mục con là timpoin
                    #chuyển các file cần sô sánh vào thưc mục đata
                    datafolder=comparefolder + "/data"
                    os.makedirs(datafolder)
                    for sample in set(sampleSTOP):
                        filetocp="{}/{}/{}/4.Taxonomy/4.1.Centrifuge/{}_{}.cf.detail.out".format(
                            args.jobid,
                            sample,
                            check,
                            sample,
                            check

                        )
                        copyfile(filetocp,"{}/{}_{}.cf.detail.out".format(datafolder,sample,check))
                        compare1_cmd="rcf -n {} -f {} -o {} -e FULL -c {} -y {} -s SHEL".format(
                            "/media/kt02/DATA/Phuc_folders/Dev/py/taxonomy/taxdump", # taxdump
                            datafolder,
                            "{}/{}_{}.html".format(comparefolder,check,"vs".join(list(set(sampleSTOP)))),
                            1, # ncontro;l
                            300
                        )
                        print (compare1_cmd +"\n")
                        compare1=Popen(compare1_cmd, shell=True, close_fds=True)
                        comparelist.append(check)

            
        
    f.close()



#main()


def main():

    parser = argparse.ArgumentParser(
        prog='monitor_supper.py',
        description="The script monitors and links all sub-script files when the realtime process starts."
    )
    parser.add_argument("-id", "--job-id", dest="jobid", required=True,
        help="unique project id")
    parser.add_argument("-log", "--log-file", dest="log_monitor", default=True,
        help="log monitor file output")
    parser.add_argument("-sig", "--sig_folder", dest="sig_folder",required=True,
        help="")
    parser.add_argument("-mon", "--mon-folder", dest="mon_folder", required=True,
        help="mon_folder")
    parser.add_argument("-gpy", "--summary-file", dest="summary_file", required=True,
        help="summary file created by basecalling ")
    parser.add_argument("-temp", "--tempfolder", dest="tempfolder", default=True,
        help="temp folder")
    parser.add_argument("-toff", "--timeout", dest="timeout",default=5000000,
        help="after the timeout (s), there is no change in the signal directory, the realtime process will stop")
    
    args=parser.parse_args()


    if args.tempfolder: # khi yếu tempfoder là default
        args.tempfolder="{}/{}/temp".format(this,args.jobid)
        if not os.path.exists(args.tempfolder):
            os.makedirs(args.tempfolder) # tạo thư mục temp
    if args.log_monitor: # khi yếu tempfoder là default
        args.log_monitor="{}/{}/log.txt".format(this,args.jobid)
    
    #realtime(jobid,logfile,sig_folder,mon_folder,timeout,tempfolder,summary_file)

    realtime(
        jobid = args.jobid,
        logfile = args.log_monitor,
        sig_folder=args.sig_folder,
        mon_folder=args.mon_folder,
        timeout=args.timeout,
        tempfolder=args.tempfolder,
        summary_file=args.summary_file,
        args=args
    )

   



if __name__ == "__main__":
    main()

#!/usr/bin/env python3

#Theo dõi file

#import modules
import glob
from time import sleep
from datetime import datetime
import os
import argparse
def monitor(folder,foldersample, scantime, timeout, log):
    '''
    Theo dõi sự hiện diễn của các tập tin .fastq trong thư mục

    params:
    -----------
    folder: (path)
        folder theo dõi
    scantime: (int)
        thời gian (s) để vòng lặp scan 
    timeout: (int)
        thời gian mà nếu thư mục không thay đổi sẽ cho dừng scan, exit
    
    return:
    ----------
    {"time": "",
    'newfile':[],
    'queue':[]}
    '''
    start=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print ("[{}] Bắt đầu theo dõi thư mục: \n {} \n>>>>>>".format(start,folder))
    empty=0
    old=[[]]
    t=0
    
    while empty < timeout:  # 
        files=glob.glob('{}/*.fastq'.format(folder)) #scan tất cả các file có đuôi là .fastq, kq là list
        old.append(files) # GHI LẠI CÁC KẾT QUẢ CỦA CÁC LẦN SCAN
       
        diff=set(old[-1]) -set (old[-2]) # SỰ KHÁC BIỆT GIỮA 2 LẦN SCAN GẦN NHẤT
        
        if diff != set():
            empty=0 # empty được cài lại là rỗng
            
            #######################
            t+=1
            samplefolder=foldersample
            samples=[]
            for dirs in os.listdir(samplefolder):
                if os.path.isdir("{}/{}".format(samplefolder, dirs)):
                    samples.append(dirs)
            sampledict=dict()
            for sample in samples:
                # tìm kiems các tập tin fastq
                files=glob.glob("{}/{}/*".format(samplefolder,sample))
                sampledict[sample]=files
            print (sampledict)
            timenow=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            f=open(log, "a")
            f.write("t{}|{}|{}\n".format(t,sampledict,timenow))
            f.close()
            sleep(2)
            #######################






        else:
            empty+=scantime # empty tăng lên do scan không có kết quả khác
        sleep(scantime)
    end=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    f=open(log, "a")
    f.write("end|")
    f.close()
    print ('[{}] Hết theo dõi'.format(end))
    

#main

def main():

    parser = argparse.ArgumentParser(
        prog='monitor.py',
        description="something about monitor.py"
    )
    parser.add_argument("-sig","--signal-folder",dest="sigfolder",
        default="/media/kt02/DATA/Phuc_folders/Dev/py/creatSUPPERlst/S1",
        help="something about signal folder")
    parser.add_argument("-mo", "--monitor-folder", dest="monfolder",
        default="/media/kt02/DATA/Phuc_folders/Dev/py/creatSUPPERlst",
        help="something about monitor folder")
    parser.add_argument("-tsc", "--scan-time", dest="scantime", default=5,
        help="something about scantime")
    parser.add_argument("-toff", "--time-out", dest="timeout", default=500,
        help="something about timeout")
    parser.add_argument("-log", "--log-file", dest="log",
        default="supperlist.txt",
        help="something about log file")
    args=parser.parse_args()
    
    if os.path.isfile(args.log): # file log đã tồn tại, xóa nó đi ngay
       os.remove(args.log) # xóa file log trước đó
    # Hey, ghi nhận sự thay đôi ghi vào file log
    monitor(args.sigfolder,args.monfolder,int(args.scantime), int(args.timeout), args.log)
    

if __name__ == "__main__":
    main()








        

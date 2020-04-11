#!/usr/bin/env python3

#Theo dõi file

#import modules
import glob as gb
from time import sleep
from datetime import datetime


def monitor(folder, scantime, timeout):
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
    queue=dict()
    proc=[]
    old=[[]]
    while empty < timeout:  # 
        files=gb.glob('{}/*.fastq'.format(folder)) #scan tất cả các file có đuôi là .fastq, kq là list
      
        old.append(files) # GHI LẠI CÁC KẾT QUẢ CỦA CÁC LẦN SCAN
       
        diff=set(old[-1]) -set (old[-2]) # SỰ KHÁC BIỆT GIỮA 2 LẦN SCAN GẦN NHẤT
        if diff != set():
            empty=0 # empty được cài lại là rỗng
            queue['newfile']=list(diff) # queue được thêm vào diff và mục new file
            proc.append(old[-1])
            queue['queue']=proc # các đợt cần xử lý được thêm vào queue['queue']
            print (queue)
        else:
            empty+=scantime # empty tăng lên do scan không có kết quả khác

        sleep(scantime)
    end=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print ('[{}] Hết theo dõi'.format(end))
    return queue


monitor('/media/kt02/DATA/Phuc_folders/Dev/py/temp',1,25)


        

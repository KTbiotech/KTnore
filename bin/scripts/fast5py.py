#!/urs/bin/env python3 

import sys
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from time import time, sleep
from subprocess import Popen, PIPE
import hashlib
import shutil
import argparse


class EventHandler(FileSystemEventHandler):

    def __init__(self,output,outBC):
        self.output=output
        self.outBC=outBC

    def on_any_event(self, event):
      
        if event.event_type=="created" and event.src_path.split(".")[-1]=="fast5" :
            #newfast5
            this=os.getcwd()
            newfast5=event.src_path

            prefix=newfast5.split("/")[-1].split(".")[0][-3:]
            #### KIỂM TRA QUÁ TRÌNH DI CHUYỂN FILE ĐÃ HOÀN TẤT HAY CHƯA
            output="{}/{}_{}".format(self.output,"call",prefix)
            outBC=self.outBC
            historicalSize = -1
            print ("nhận file")
            print ("đợi file copy xong")
            while (historicalSize != os.path.getsize(newfast5)):
                historicalSize = os.path.getsize(newfast5)
                sleep(1)
            print ("copy hoàn tất")  

            ### run Guppy basecaller:
            guppy_basecaller="python3 guppy.py {} {} {}".format(newfast5, output, outBC)
            g=Popen(guppy_basecaller,shell=True, close_fds=True)
            print (guppy_basecaller +" |chạy ẩn")
        


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='fast5py.py',
        description="Dùng cho realtime"
    )
    parser.add_argument("-f5", "--path-fast5", dest="path", required=True,
        help="Some thing about path fast5")
    parser.add_argument("-fq", "--path-fastq", dest="output", required=True,
        help="Some thing about path fast5")
    parser.add_argument("-bc", "--path-barcode", dest="outBC", required=True,
        help="Some thing about path fast5")

    
    args=parser.parse_args()



    path=args.path
    output=args.output
    outBC=args.outBC

    
    print ("Đang theo dõi thư mục:['{}']\n".format(path))

    event_handler = EventHandler(output=output, outBC=outBC)
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:
        while True:
            sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()



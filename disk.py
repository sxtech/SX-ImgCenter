import wmi 
#import os 
#import sys 
#import time

class DiskState:
    def __init__(self):
        self.c = wmi.WMI()
        self.disk_state = {}
        
    def checkDisk(self):
        for disk in self.c.Win32_LogicalDisk (DriveType=3):
            #print disk
            self.disk_state[disk.Caption[0]] = 100.0*long(disk.FreeSpace)/long(disk.Size)
            #print disk.Caption, "%0.2f%% free"%(100.0*long(disk.FreeSpace)/long(disk.Size)) 
        #return self.disk_state
if __name__ == '__main__':
    ds = DiskState()
    ds.checkDisk()
    print ds.disk_state
    del ds

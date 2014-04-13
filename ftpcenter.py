# -*- coding: cp936 -*-
import ftplib
from mysqldb import ImgMysql
from ftpclient2 import FtpClient
from inicof import FtpIni
import MySQLdb
import time,datetime,os,sys
import logging
import logging.handlers
import threading
from singleinstance import singleinstance3
from disk import DiskState

def getTime():
    return datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")

def version():
    return 'SX-ftpcenter V0.2.3'

def initLogging(logFilename):
    """Init for logging"""
    path = os.path.split(logFilename)
    if os.path.isdir(path[0]):
        pass
    else:
        os.makedirs(path[0])
    logging.basicConfig(
                    level    = logging.DEBUG,
                    format   = '%(asctime)s %(filename)s[line:%(lineno)d] [%(levelname)s] %(message)s',
                    datefmt  = '%Y-%m-%d %H:%M:%S',
                    filename = logFilename,
                    filemode = 'a');

class FtpCenter:
    def __init__(self,trigger = ('',1)):
        self.style_red = 'size=4 face=arial color=red'
        self.style_blue = 'size=4 face=arial color=blue'
        self.style_green = 'size=4 face=arial color=green'
        self.trigger = trigger

        initLogging(r'log\ftpcenter.log')
        self.ftpIni = FtpIni()
        #self.ds = DiskState()
        self.direction = {'0':u'进城','1':u'出城','2':u'由东往西','3':u'由南往北','4':u'由西往东','5':u'由北往南'}
        
        self.mysqlset = self.ftpIni.getMysqlConf()
        diskset = self.ftpIni.getDiskConf()
        self.disk_list  = diskset['disklist'].split(',')
        self.activedisk = diskset['activedisk']
        self.ftpuser = self.ftpIni.getFtpConf()['user']
        self.ftppasswd = self.ftpIni.getFtpConf()['passwd']
        self.imgMysql = ImgMysql(self.mysqlset['host'],self.mysqlset['user'],self.mysqlset['passwd'])

        self.ftphost_dict = {}
        self.ftplosthost_dict = {}
        self.hosts_list = []
        self.ip_state = {}
        self.newip = ()
        self.quitflag = False
        self.loginmysqlflag = True
        self.loginmysqlcount = 0
        self.ftpcount = 0
        self.imgcount = 0

        self.singal = threading.Event()

    def __del__(self):
        del self.imgMysql
        for i in self.ftphost_dict.keys():
            del i
        for j in self.ftplosthost_dict.keys():
            del j

    def loginMysql(self):
        now = getTime()
        try:
            self.trigger.emit("<font %s>%s</font>"%(self.style_green,now+'Start to connect mysql server '),1)
            self.imgMysql.login()
            self.trigger.emit("<font %s>%s</font>"%(self.style_green,now+'Connect mysql success! '),1)
        except MySQLdb.Error,e:
            self.trigger.emit("<font %s>%s</font>"%(self.style_red,now+str(e)),1)
            self.trigger.emit("<font %s>%s</font>"%(self.style_red,now+'Reconn after 15 seconds'),1)
            logging.exception(e)
            self.loginmysqlflag = True
            self.loginmysqlcount = 1
        except Exception,e:
            self.trigger.emit("<font %s>%s</font>"%(self.style_red,now+str(e)),1)
            logging.exception(e)
        else:
            self.loginmysqlflag = False
            self.loginmysqlcount = 0

    def getNewIP(self):
        try:
            self.newip = self.imgMysql.getNewIP(self.hosts_list)
            if len(self.newip)>0:
                for i in self.newip:
                    self.hosts_list.append(i['ip'])
                    self.ftplosthost_dict[i['ip']] = FtpClient(i['ip'],self.ftpuser,self.ftppasswd)
        except MySQLdb.Error,e:
            self.trigger.emit("<font %s>%s</font>"%(self.style_red,getTime()+str(e)),1)
            logging.exception(e)
            self.loginmysqlflag = True
            self.loginmysqlcount = 0
        except Exception,e:
            self.trigger.emit("<font %s>%s</font>"%(self.style_red,getTime()+str(e)),1)
            logging.exception(e)

    def getIPState(self):
        try:
            iplist = self.imgMysql.getIPList()
            now = datetime.datetime.now() - datetime.timedelta(minutes = 1)
            conn_state =0
            ftp_state = 0
            for i in iplist:
                if i['activetime'] > now:
                    conn_state = 4
                else:
                    conn_state = 0
                if i['ip'] in self.ftphost_dict:
                    ftp_state = 2
                else:
                    ftp_state = 0
                self.trigger.emit("%s"%i['ip'],conn_state+ftp_state)
                
        except MySQLdb.Error,e:
            self.trigger.emit("<font %s>%s</font>"%(self.style_red,getTime()+str(e)),1)
            logging.exception(e)
            self.loginmysqlflag = True
            self.loginmysqlcount = 0
        except Exception,e:
            self.trigger.emit("<font %s>%s</font>"%(self.style_red,getTime()+str(e)),1)
            logging.exception(e)

    def checkFtp(self):
        ftp_host = self.ftplosthost_dict.keys()

        if len(ftp_host)>0:
            for i in ftp_host:
                try:
                    self.singal.wait(1)
                    self.trigger.emit("<font %s>%s</font>"%(self.style_green,getTime()+'Start to connect ftp '+i),1)
                    self.ftplosthost_dict[i].login()
                    self.trigger        #print 'self.activedisk',self.activedisk
        #print self.diskstate.disk_state.emit("<font %s>%s</font>"%(self.style_green,getTime()+'Connect ftp success! '+i),1)
                    self.ftphost_dict[i]=self.ftplosthost_dict[i]
                    del(self.ftplosthost_dict[i])
                    self.singal.set()
                except ftplib.all_errors,e:
                    self.trigger.emit("<font %s>%s</font>"%(self.style_red,getTime()+str(e)),1)
                    logging.exception(e)
                except Exception,e:
                    self.trigger.emit("<font %s>%s</font>"%(self.style_red,getTime()+str(e)),1)
                    logging.exception(e)

    def setDisk(self):
        self.imgMysql.setDisk(ip,disk)

    def getDisk(self):
        #print 'self.activedisk',self.activedisk
        #print self.diskstate.disk_state
        self.ds.checkDisk()
        space = self.ds.disk_state[self.activedisk]
        print getTime(),self.activedisk,"%0.2f%% free"%space
        if space<10:
            num = len(self.disk_list)
            idx = self.disk_list.index(self.activedisk)
            if idx+1>=num:
                print getTime(),'Disk space is full!'
                logging.error('Disk space is full!')
                sys.exit()
            else:
                self.activedisk=self.disk_list[idx+1]
                self.ftpIni.setDiskConf(self.activedisk)
                self.checkDisk()
        
    def getImg(self):
        try:
            imgpath = self.imgMysql.getImgInfoByIPList(5,self.ftphost_dict.keys())
            num = len(imgpath)
            i = {}
            if num>0:
                for i in imgpath:
                    remotepath = os.path.splitext(i['inifile'])[0]+'.jpg'
                    ftpclient = self.ftphost_dict.get(i['pcip'],0)
                    if ftpclient != 0:
                        try:
                            if ftpclient.downloadfile(remotepath.encode('gbk'),i['imgpath'].encode('gbk'),i['disk'].encode('gbk')):
                                self.imgMysql.flagImgIndex(i['id'])
                        except IOError,e:
                            self.trigger.emit("<font %s>%s</font>"%(self.style_red,getTime()+str(e)))
                            if e[0] == 2:
                                ftpclient.makedirs()
    ##                        else:
    ##                            self.ftplosthost_dict[i['pcip']]=self.ftphost_dict[i['pcip']]
    ##                            del(self.ftphost_dict[i['pcip']])
                            logging.exception(e)
                        except ftplib.all_errors,e:
                            self.trigger.emit("<font %s>%s</font>"%(self.style_red,getTime()+str(e)))
                            if str(e) == '550 File not found':
                                self.imgMysql.flagImgIndex(i['id'],2)
                            else:
                                self.singal.wait(1)
                                self.ftplosthost_dict[i['pcip']]=self.ftphost_dict[i['pcip']]
                                del(self.ftphost_dict[i['pcip']])
                                self.singal.set()
                            logging.exception(e)
                    carstr =  '%s %s %s | %s | %s | %s车道 | IP:%s'%(getTime(),i['platecode'].encode("gbk"),i['platecolor'].encode("gbk"),i['roadname'].encode("gbk"),self.direction.get(i['directionid'],u'其他').encode("gbk"),i['channelid'].encode("gbk"),i['pcip'].encode("gbk"),0)
                    self.trigger.emit("<font %s>%s</font>"%(self.style_blue,carstr),1)
            else:
                if self.imgcount%120==0:
                    self.imgcount = 1
                    self.getNewIP()
                    self.getIPState()
                    #self.checkDisk()
                time.sleep(0.125)
                
            if self.imgcount%120==0:
                self.imgcount = 1
                self.getNewIP()
                self.getIPState()
                #self.checkDisk()
        except MySQLdb.Error,e:
            self.trigger.emit("<font %s>%s</font>"%(self.style_red,getTime()+str(e)),1)
            self.loginmysqlflag = True
            self.loginmysqlcount = 0
            logging.exception(e)
        except Exception,e:
            self.trigger.emit("<font %s>%s</font>"%(self.style_red,getTime()+str(e)),1)
            #logging.error(ip)
            print e
            logging.exception(e)
            time.sleep(5)


if __name__ == "__main__":
##    myapp = singleinstance3()
##    if myapp.aleradyrunning():
##        print version(),'已经启动!3秒后自动退出...'
##        time.sleep(3)
##        sys.exit(0)
  
    fc = FtpCenter()
    #self.diskstate.checkDisk()
    #print fc.disk_list
    #print fc.activedisk
##    while True:
##        #print '123'
##        fc.checkDisk()
##        time.sleep(5)
    fc.main()

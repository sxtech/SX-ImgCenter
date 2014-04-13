import ftplib
from mysqldb import ImgMysql
import MySQLdb
import socket
import time,datetime,os 

def getTime():
    return datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")

class FtpClient:
    def __init__(self,host='127.0.0.1',username='fire',password='yqlfire'):
        self.host = host
        self.username   = username
        self.password   = password
        self.localpath  = ''
        self.remotepath = ''
        self.port       = 21
        self.dir_path   = ''
        self.ftp        = ftplib.FTP()
        self.bufsize    = 1024
        self.imgpath = ':\SpreadData\ImageFile'
        self.disk = 'F'
        
    def __del__(self):
        #print getTime(),'%s ftp is quit'%self.host
        try:
            self.ftp.quit()
        except:
            pass
        
    def login(self):
        #ftp.set_debuglevel(2)
        self.ftp.set_pasv(True)
        #print getTime(),'start to conn ftp server %s' %(self.host)
        self.ftp.connect(self.host ,self.port)
        #print getTime(),'conn success ! %s' %(self.host)
        #print getTime(),'start to login ftp server %s' %(self.host)
        self.ftp.login(self.username,self.password)
        #print getTime(),'login success ! %s' %(self.host)
        #self.ftp.cwd('ImageFile')

        #self.ftp.retrlines('LIST')
        #return ftp

##    def setupFtp(self):
##        try:
##            self.login()
##        except Exception,e:
##            now = getTime()
##            print now,e
##            #logging.exception(e)
##            print now,'Reconn after 15 seconds'
##            time.sleep(15)
##            self.setupFtp()
##        else:
##            pass
##            #logging.info('Connect mysql success!')

    def downloadfile2(self,remotepath,localpath):
        self.localpath = localpath
        self.remotepath = remotepath
        s=False
        try:
            fp = open(self.imgpath+os.sep+self.localpath,'wb')
            #print self.imgpath+os.sep+self.localpath
            self.ftp.retrbinary('RETR '+self.remotepath, fp.write, self.bufsize)
        except IOError,e:
            print 'IOError',e
            if e[0] == 2:
                self.makedirs()
                self.downloadfile(self.remotepath, self.localpath)
                #time.sleep(1)
            else:
                #print 'test123'
                raise IOError
        except Exception,e:
            #print 'Exception',e
            raise
        else:
        #ftp.set_debuglevel(0)
            s = True
        finally:
            return s
            if 'fp' in dir():
                #print 'fp True'
                fp.close()

    def downloadfile(self,remotepath,localpath,disk='F'):
        self.localpath = localpath
        self.remotepath = remotepath
        self.disk = disk
        fp = open(self.disk+self.imgpath+os.sep+self.localpath,'wb')
        #print self.imgpath+os.sep+self.localpath
        self.ftp.retrbinary('RETR '+self.remotepath, fp.write, self.bufsize)
        if 'fp' in dir():
            fp.close()
        return True
            
##    def uploadfile(self,remotepath,localpath):
##        #print 'upload'
##        self.localpath = localpath
##        self.remotepath = remotepath
##        fp = open(self.dir_path+self.localpath,'rb')
##        try:
##            #fp = open(self.dir_path+self.localpath,'rb')
##            self.ftp.storbinary('STOR '+self.remotepath, fp, self.bufsize)
##        except ftplib.all_errors,e:
##            print 'FTP',e
##            if e[0] == '550 Filename invalid':
##                #print os.path.splitext(remotepath)[0]
##                self.ftp.mkd(os.path.split(remotepath)[0])
##                self.uploadfile(self.remotepath,self.localpath)
##            else:
##                raise
##        except Exception,e:
##            print e
##            print 'uploadfile error'
##            #fp.close()
##            raise
##        else:
##            pass
##        finally:
##            fp.close()
    
    def makedirs(self):
        try:
            file_path = os.path.split(self.disk+self.imgpath+os.sep+self.localpath)
            if os.path.isdir(file_path[0]):
                pass
            else:
                os.makedirs(file_path[0])
        except IOError,e:
            print e
            raise

    def test(self):
        self.ftp.retrlines('LIST')
            
if __name__ == "__main__":
    imgMysql = ImgMysql('localhost','root','')
    imgMysql.login()
    ftpClient = FtpClient('192.168.0.1','fire','yqlfire')
    try:
        ftpClient.login()
    except Exception,e:
        print e
##    #imgMysql.login()
##    while True:
##        #imgpath = imgMysql.getIndexByImgFlag(20)
##        print 'loop',datetime.datetime.now()
##        try:
##            imgpath = imgMysql.getImgInfoByIP(10,'127.0.0.1')
##            for i in imgpath:
##                remotepath = os.path.splitext(i['inifile'])[0]+'.jpg'
##                #print 'remotepath',remotepath
##                #localpath = i['imgpath']
##                #print 'localpath',localpath
##                if ftpClient.downloadfile(remotepath.encode('gbk'),i['imgpath'].encode('gbk')):
##                    imgMysql.flagManyImgIndex(i['id'])
##        except MySQLdb.Error,e:
##            print e
##            time.sleep(15)
##            imgMysql.login()
##        except IOError,e:
##            print 'IOError',e
##            if e[0] == 2:
##                self.makedirs()
##            ftpClient.setupFtp()
##        except ftplib.all_errors,e:
##            print 'ftp',e
##            if str(e) == '550 File not found':
##                print '123'
##            ftpClient.setupFtp()
##        except Exception,e:
##            print 'exception',e
##        finally:
##            #imgMysql.sqlCommit()
##            time.sleep(5)

##    while True:
##        imgpath = imgMysql.getIndexByImgFlag(20)
##        #print 'imgpath',imgpath
##        print 'loop',datetime.datetime.now()
##        try:
##            for i in imgpath:
##                localpath = os.path.splitext(i['inifile'])[0]+'.jpg'
##                remotepath = i['imgpath']
##                print "i['imgpath']",i['imgpath']
##                ftpClient.uploadfile(remotepath.encode('gbk'),localpath.encode('gbk'))
##                imgMysql.flagManyImgIndex(i['id'])
##        except IOError,e:
##            print e
##        except Exception,e:
##            print e
##            del ftpClient
##            ftpClient = FtpClient()
##        finally:
##            imgMysql.endOfCur()
##            time.sleep(10)
    del imgMysql
    #del ftpClient
    #ftpquit(ftp)



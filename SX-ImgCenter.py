# -*- coding: cp936 -*-
from ftpcenter import FtpCenter
from PyQt4 import QtGui, QtCore
import sys,time,datetime,os
import MySQLdb
import logging
import logging.handlers
import threading
from singleinstance import singleinstance3
import gl

def getTime():
    return datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
            
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

def version():
    return 'SX-ImgCenter V0.2.2'

 
class MyThread(QtCore.QThread):
    trigger = QtCore.pyqtSignal(str,int)
 
    def __init__(self, parent=None):
        super(MyThread, self).__init__(parent)
 
    def run(self):
        m = icmain(self.trigger)
        m.mainloop()

class icmain:
    def __init__(self,trigger):
        self.style_red = 'size=4 face=arial color=red'
        self.style_blue = 'size=4 face=arial color=blue'
        self.style_green = 'size=4 face=arial color=green'
        self.trigger = trigger

        initLogging(r'log\ftpcenter.log')
        self.fc = FtpCenter(trigger)
        self.count = 0
        self.loginflag = True
        self.logincount = 0
        self.setupflag = False

        self.trigger.emit("<font %s>%s</font>"%(self.style_green,'Welcome to '+version()),1)


    def __del__(self):
        #print 'quit SX-ImgCenter'
        del self.fc

    def getImgsLoop(self):
        #count = 0
        while True:
            if gl.qtflag == False:
                gl.imgflag = False
                break            
            
            if self.fc.loginmysqlflag:
                if self.fc.loginmysqlcount == 0:
                    self.fc.loginMysql()
                    if self.fc.loginmysqlflag == False:
                        self.fc.getNewIP()
                elif self.fc.loginmysqlcount<=15:
                    self.fc.loginmysqlcount += 1
                    time.sleep(1)
                else:
                    self.fc.loginmysqlcount = 0
            else:
                self.fc.getImg()
            self.fc.imgcount += 1

    def checkFtpLoop(self):
        while True:
            if gl.qtflag == False:
                gl.ftpflag = False
                break 
            
            if self.fc.ftpcount%11 == 0:
                self.fc.checkFtp()
                self.fc.ftpcount = 1
            self.fc.ftpcount += 1
            time.sleep(1)
                   
    def mainloop(self):
        t1 = threading.Thread(target=self.getImgsLoop, args=(),kwargs={})
        t2 = threading.Thread(target=self.checkFtpLoop, args=(),kwargs={})
        t1.start()
        time.sleep(1)
        t2.start()
        t1.join()
        t2.join()

    
class MainWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):  
        super(MainWindow, self).__init__(parent)
        self.resize(850, 450)
        self.setWindowTitle(version())

        self.tree = QtGui.QTreeWidget()
        self.tree.setMinimumWidth(250)
        self.tree.setMaximumWidth(300)
        self.tree.setColumnCount(3)
        self.tree.setHeaderLabels(['IP','Conn','Ftp'])

        self.root = QtGui.QTreeWidgetItem(self.tree)
        self.root.setText(0,'State')

        self.count = 0
        self.ipdict = {}
        self.statelist = [('off',QtGui.QColor(255,0,0)),('on',QtGui.QColor(0,200,50))]
        self.statedict = {0:(self.statelist[0],self.statelist[0]),2:(self.statelist[0],self.statelist[1]),4:(self.statelist[1],self.statelist[0]),6:(self.statelist[1],self.statelist[1])}
        
        self.tree.addTopLevelItem(self.root)

        self.setCentralWidget(self.tree) 
        
        self.text_area = QtGui.QTextBrowser()
        self.text_area.setMinimumWidth(600)
        self.text_area.setMinimumHeight(400)
 
        central_widget = QtGui.QWidget()
        central_layout = QtGui.QHBoxLayout()
        central_layout.addWidget(self.tree)
        central_layout.addWidget(self.text_area)
        central_widget.setLayout(central_layout)
        self.setCentralWidget(central_widget)

        exit = QtGui.QAction(QtGui.QIcon('icons/exit.png'), 'Exit', self)
        exit.setShortcut('Ctrl+Q')
        exit.setStatusTip('Exit application')
        self.connect(exit, QtCore.SIGNAL('triggered()'), QtCore.SLOT('close()'))

        self.statusBar()

        menubar = self.menuBar()
        file = menubar.addMenu('&File')
        file.addAction(exit)
        
        toolbar = self.addToolBar('Exit')
        toolbar.addAction(exit)
        
        #self.setGeometry(300, 300, 250, 150)
        #self.setWindowTitle('Icon')
        self.setWindowIcon(QtGui.QIcon('icons/logo3.png'))
        
        self.start_threads()
        
    def closeEvent(self, event):
        reply = QtGui.QMessageBox.question(self, 'Message',
            "Are you sure to quit?", QtGui.QMessageBox.Yes |
            QtGui.QMessageBox.No, QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            gl.qtflag = False
            while gl.imgflag and gl.ftpflag:
                #print 'gl.imgflag',gl.imgflag
                #print 'gl.ftpflag',gl.ftpflag
                time.sleep(1)
            event.accept()
        else:
            event.ignore()
            
    def start_threads(self):
        self.threads = []              # this will keep a reference to threads
        thread = MyThread(self)    # create a thread
        thread.trigger.connect(self.update_text)  # connect to it's signal
        thread.start()             # start the thread
        self.threads.append(thread) # keep a reference
 
    def update_text(self, message,m_type):
        if m_type == 1:
            self.text_area.append(unicode(message, 'gbk'))
            self.count += 1
            if self.count >1000:
                self.text_area.clear()
                self.count = 0
        else:
            #print 'm_type',m_type,'message',message
            if self.ipdict.get(message,0) == 0:
                self.ipdict[message] = QtGui.QTreeWidgetItem(self.root)
            else:
                pass
            one,two = self.statedict.get(m_type,(self.statelist[0],self.statelist[0]))
            self.ipdict[message].setText(0,message)
            self.ipdict[message].setText(1,one[0])
            self.ipdict[message].setText(2,two[0])
            self.ipdict[message].setTextColor(1,one[1])
            self.ipdict[message].setTextColor(2,two[1])

 
if __name__ == '__main__':
    myapp = singleinstance3()
    if myapp.aleradyrunning():
        print version(),'已经启动!3秒后自动退出...'
        time.sleep(3)
        sys.exit(0)
        
    app = QtGui.QApplication(sys.argv)
 
    mainwindow = MainWindow()
    mainwindow.show()
    #print 'after show'
 
    sys.exit(app.exec_())

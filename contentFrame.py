# coding=utf-8
from os import path,getcwd
from re import sub
from zipfile import ZipFile
import wx
import time
import random
import threading
import queue
from selenium import webdriver
from fake_useragent import UserAgent
import re
import requests
import pymysql
import csv
from selenium.webdriver.support.wait import WebDriverWait
import inforequests as inforeq
import linkrequests as linkreq
#import insertzipfile as izf

class ContentFrame(wx.Frame):

    def __init__(self, parent=None, id=-1, UpdateUI=None):
        wx.Frame.__init__(self, parent, -1, title='luoxinkun', size=(400, 400), pos=(500, 200))

        self.UpdateUI = UpdateUI

        self.InitUI()  # 绘制UI

    def InitUI(self):

        #self.myThread = myThread(1, "Thread-1", 1)
        wx.Frame.__init__(self, None, title='QQ：1154128829', size=(730, 600))
        self.count = 0
        self.ThreadNums = 1	
        self.ProxyList = []	
        self.proxyIp = None
        self.LinkHeaderCountry = 'fr'
        self.pathVerify = path.join(getcwd(),'ca.crt')
        self.InfoQue = queue.Queue()
        self.LinkQue = queue.Queue()
        self.currentInfoFilePath = None
        self.currentLinkFilePath = None
        self.ThreadSwitch = 1
        self.currentTempLinkFilePath = path.join(getcwd(),'Temp.txt')
        self.InfoText = wx.StaticText(self, pos=(5,5),size=(90,25),label='详情文件地址：')
        self.InfoFileName = wx.TextCtrl(self, pos=(95, 5), size=(200, 25))

        self.InfoSelBtn = wx.Button(self, label='选择文件', pos=(305, 5), size=(80, 25))
        self.InfoSelBtn.Bind(wx.EVT_BUTTON, self.OnOpenInfoFile)

        self.InfoOkBtn = wx.Button(self, label='导入', pos=(405, 5), size=(60, 25))
        self.InfoOkBtn.Bind(wx.EVT_BUTTON, self.InfoReadFile)

        self.InfoStartBtn = wx.Button(self, label='开始', pos=(485, 5), size=(60, 25))
        self.InfoStartBtn.Bind(wx.EVT_BUTTON, self.StartInfoFile)

        self.InfoStopBtn = wx.Button(self, label='暂停', pos=(565, 5), size=(60, 25))
        self.InfoStopBtn.Bind(wx.EVT_BUTTON,self.StopBtn)
		
        self.InfoAccountNums = wx.StaticText(self, pos=(635,5),size=(75,25),label='连接：0')
		
		
        self.LinkText = wx.StaticText(self, pos=(5,35),size=(90,25),label='链接文件地址：')
        self.LinkFileName = wx.TextCtrl(self, pos=(95, 35), size=(200, 25))

        self.LinkSelBtn = wx.Button(self, label='选择文件', pos=(305, 35), size=(80, 25))
        self.LinkSelBtn.Bind(wx.EVT_BUTTON, self.OnOpenLinkFile)

        self.LinkOkBtn = wx.Button(self, label='导入', pos=(405, 35), size=(60, 25))
        self.LinkOkBtn.Bind(wx.EVT_BUTTON, self.LinkReadFile)

        self.LinkStartBtn = wx.Button(self, label='开始', pos=(485, 35), size=(60, 25))
        self.LinkStartBtn.Bind(wx.EVT_BUTTON, self.StartLinkFile)

        self.LinkStopBtn = wx.Button(self, label='结束', pos=(565, 35), size=(60, 25))
		
        self.LinkAccountNums = wx.StaticText(self, pos=(635,35),size=(75,25),label='连接：0')

        self.FileContent = wx.TextCtrl(self, pos=(5, 95), size=(660, 450), style=wx.TE_RICH2 | wx.TE_MULTILINE)

        self.LinkText = wx.StaticText(self, pos=(5,65),size=(90,25),label='设置代理：')
        self.ProxyInput = wx.TextCtrl(self, pos=(95, 65), size=(120, 25))
        self.proxyBtn = wx.Button(self, label='确定', pos=(225, 65), size=(60, 25))
        self.proxyBtn.Bind(wx.EVT_BUTTON,self.SetProxy)
		
        self.LinkHeader = wx.StaticText(self,label='替换头部',pos=(315,65),size=(60,25))
        self.LinkHeaderText = wx.TextCtrl(self,pos=(385,65),size=(80,25))
        self.LinkHeaderBtn = wx.Button(self,label='替换',pos=(475,65),size=(50,25))
        self.LinkHeaderBtn.Bind(wx.EVT_BUTTON,self.ReplaceHeader)
		
        self.threadNum = wx.StaticText(self,label='线程数',pos=(535,65),size=(40,25))
        self.threadNumText = wx.TextCtrl(self,pos=(585,65),size=(30,25))
        self.threadNumBtn = wx.Button(self,label='确定',pos=(625,65),size=(40,25))
        self.threadNumBtn.Bind(wx.EVT_BUTTON,self.setThreadNums)
        #self.UpdateCount('Info')
        #self.UpdateCount('Link')
		
    def infoMess(self,msg):
        self.FileContent.AppendText(msg['info'])
		
    def StopBtn(self,event):
        if self.InfoStopBtn.GetLabel() == '暂停':
            self.ThreadSwitch = 2
            self.InfoStopBtn.SetLabel('重新开始')
        elif self.InfoStopBtn.GetLabel() == '重新开始':
            self.ThreadSwitch = 1
            self.InfoStopBtn.SetLabel('暂停')
		
    def setThreadNums(self,event):
        try:
            threadNums = self.threadNumText.GetValue()
            threadNums = threadNums.replace(' ','')
            threadNums = int(threadNums)
            self.ThreadNums = threadNums
            self.FileContent.AppendText('线程设置为：%s成功'%self.ThreadNums)
        except:
            self.FileContent.AppendText('线程设置失败，请检查参数是否正确')
		
    def ReplaceHeader(self,event):
        headerCountry = self.LinkHeaderText.GetValue()
        headerCountry = headerCountry.replace(' ','').lower()
        if len(headerCountry)>0:
            self.LinkHeaderCountry = headerCountry
            self.FileContent.AppendText('头部替换为：%s成功'%headerCountry)
    #设置代理
    def SetProxy(self,event):
        currentProxyIp = self.ProxyInput.GetValue()
        currentProxyIp = currentProxyIp.strip()
        if len(currentProxyIp) >0:
            currentProxyIp = currentProxyIp.replace('：',':')
            self.proxyIp = currentProxyIp
            self.FileContent.AppendText('代理成功设置为：%s\n'%currentProxyIp)
        else:
            self.proxyIp = None
            self.FileContent.AppendText('代理成功设置为：%s\n'%'None')
			
    #打开文件
    def OnOpenInfoFile(self, event):
        wildcard = 'All files(*.*)|*.*'
        dialog = wx.FileDialog(None, 'select', getcwd(), '', wildcard, wx.ID_OPEN)
        if dialog.ShowModal() == wx.ID_OK:
            self.InfoFileName.SetValue(dialog.GetPath())
            dialog.Destroy
			
    def OnOpenLinkFile(self, event):
        wildcard = 'All files(*.*)|*.*'
        dialog = wx.FileDialog(None, 'select', getcwd(), '', wildcard, wx.ID_OPEN)
        if dialog.ShowModal() == wx.ID_OK:
            self.LinkFileName.SetValue(dialog.GetPath())
            dialog.Destroy
			
    #导入
    def InfoReadFile(self, event):
        filePath = self.InfoFileName.GetValue()
        filePath = filePath.strip()
        if len(filePath) == 0:
            self.FileContent.AppendText('请输入详情文件地址\n')
            return 0
        self.FileContent.AppendText('开始导入\n')
        f = open(filePath,'r',encoding='utf-8')
        for line in f:
            line = line.replace('www',self.LinkHeaderCountry).strip()
            if len(line)>0:
                self.InfoQue.put(line.strip())
                self.UpdateCount('Info')
        f.close()
        self.FileContent.AppendText('导入完成\n')
        self.currentInfoFilePath = filePath
		
    def LinkReadFile(self, event):
        try:
            fTemp = open(self.currentTempLinkFilePath,'r',encoding='utf-8')
            for lineTemp in fTemp:
                self.LinkQue.put(lineTemp.strip())
                self.UpdateCount('Link')
            fTemp.close()
        except:
            pass
        filePath = self.LinkFileName.GetValue()
        filePath = filePath.strip()
        if len(filePath) == 0:
            self.FileContent.AppendText('请输入详情文件地址\n')
            return 0
        self.FileContent.AppendText('开始导入\n')
        f = open(filePath,'r',encoding='utf-8')
        for line in f:
            self.LinkQue.put(line.strip())
            self.UpdateCount('Link')
        f.close()
        self.currentLinkFilePath = filePath
        self.FileContent.AppendText('导入完成\n')

		
    #修改数量
    def UpdateCount(self,TypeStatus):
        if TypeStatus == 'Info':
            self.InfoAccountNums.SetLabel('连接: %d' % self.InfoQue.qsize())
        elif TypeStatus == 'Link':
            self.LinkAccountNums.SetLabel('连接: %d' % self.LinkQue.qsize())

    #开始
    def StartInfoFile(self,event):
        for i in range(self.ThreadNums):
            thread = myThread(1, "InfoThread-"+str(i), 1,self,'Info')
            thread.start()
		
    def StartLinkFile(self,event):
        for i in range(self.ThreadNums):
            thread = myThread(1, "LinkThread-"+str(i), 1,self,'Link')
            thread.start()
    
    def InfoAccessLog(self,msg):
        self.FileContent.AppendText('链接：%s--%s\n'%(msg['url'],msg['info']))
        self.UpdateCount('Info')
        self.deleteInfoFileLink(msg['url'])
		
    def LinkAccessLog(self,msg):
        self.FileContent.AppendText('链接：%s--%s\n'%(msg['url'],msg['info']))
        self.UpdateCount('Link')
        self.deleteLinkFileLink(msg['url'])	

    def TempLinkAccessLog(self,msg):
        self.FileContent.AppendText('链接：%s--%s\n'%(msg['url'],msg['info']))
        self.UpdateCount('Link')
        self.deleteTempLinkFileLink(msg['url'])		
    
    #完成		
    def EndOf(self,msg):
        msg = msg+"检索完成\n"
        self.FileContent.AppendText(msg)
        #self.myThread.exm()
		
    def deleteInfoFileLink(self,link):
        try:
            linkId = re.search('\d{4,}',link).group()
        except:
            return -1
        change_data = ""
        with open(self.currentInfoFilePath,'r',encoding='utf-8') as f:
            for line in f:
                if linkId not in line:
                    change_data += line
        with open(self.currentInfoFilePath,'w',encoding='utf-8') as f:
            f.write(change_data)
		
    def deleteLinkFileLink(self,link):
        try:
            linkId = re.search('\d{4,}',link).group()
        except:
            return -1
        change_data = ""
        with open(self.currentLinkFilePath,'r',encoding='utf-8') as f:
            for line in f:
                if linkId not in line:
                    change_data += line
        with open(self.currentLinkFilePath,'w',encoding='utf-8') as f:
            f.write(change_data)
		
    def deleteTempLinkFileLink(self,link):
        try:
            linkId = re.search('\d{4,}',link).group()
        except:
            return -1
        change_data = ""
        with open(self.currentTempLinkFilePath,'r',encoding='utf-8') as f:
            for line in f:
                if link not in line:
                    change_data += line
        with open(self.currentTempLinkFilePath,'w',encoding='utf-8') as f:
            f.write(change_data)
        
lock = threading.Lock()

class myThread(threading.Thread):
    def __init__(self,threadID,name,counter,window,statustype):
        threading.Thread.__init__(self)
        self.window = window
        self.statusType = statustype
        self.threadID = threadID
        self.name = name
        self.data = None
        self.autiZipDir = path.join(getcwd(),'anticaptcha-plugin_v0.48.zip')
        self.counter = counter
        self.Proxy = 'checkip'

    def addQsize(self):
        f = open(self.window.currentTempLinkFilePath,'r',encoding='utf-8')
        for line in f:
            self.window.LinkQue.put(line.strip())
            self.UpdateCount('Link')
        f.close()

    def run(self):
        if self.statusType == 'Info':
            while self.window.InfoQue.qsize():
                #while self.startStatus:
                #    time.sleep(1)
                while True:
                    if self.window.ThreadSwitch == 1:
                        break
                    elif self.window.ThreadSwitch == 2:
                        wx.CallAfter(self.window.infoMess,{'info':'暂停中'})
                        time.sleep(5)
                        continue
                infourl = self.window.InfoQue.get()
                #print(infourl)
                infoResult = inforeq.infostart(infourl,self.window.proxyIp,self.window.pathVerify,self.window.LinkHeaderCountry)
                print(infoResult)
                if infoResult == -1:
                    self.window.InfoQue.put(infourl)
                else:
                    lock.acquire()
                    wx.CallAfter(self.window.InfoAccessLog,{'url':infourl,'info':'完成'})
                    lock.release()
            self.window.EndOf('Info')
        elif self.statusType == 'Link':
            while self.window.LinkQue.qsize():
                while True:
                    if self.window.ThreadSwitch == 1:
                        break
                    elif self.window.ThreadSwitch == 2:
                        wx.CallAfter(self.window.infoMess,{'info':'暂停中'})
                        time.sleep(5)
                        continue
                linkurl = self.window.LinkQue.get()
                #print(linkurl)
                print(self.window.pathVerify)
                linkResult,linkList = linkreq.Linkstatus(linkurl,self.window.proxyIp,self.window.pathVerify,self.window.currentTempLinkFilePath)
                if len(linkList)>0:
                    for listX in linkList:
                        self.window.LinkQue.put(listX)
                print(linkResult)
                if linkResult == -1:
                    self.window.LinkQue.put(linkurl)
                else:
                    if '?page' in linkurl:
                        lock.acquire()
                        wx.CallAfter(self.window.TempLinkAccessLog,{'url':linkurl,'info':'完成'})
                        lock.release()
                    else:
                        lock.acquire()
                        wx.CallAfter(self.window.LinkAccessLog,{'url':linkurl,'info':'完成'})
                        lock.release()
            self.window.EndOf('Link')

app = wx.PySimpleApp()
frm = ContentFrame()
frm.Show()
app.MainLoop()

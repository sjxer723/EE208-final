#2020 FALL EE208
#Copyright: Group5
import jieba
import re
import urllib
import requests
import datetime
import sys, os,threading, time

from bs4 import BeautifulSoup
from urllib.parse import urlparse
from datetime import datetime

class Parser(object):
    def __init__(self,_index,_html_folder):
        '''
            @self.index:存放filename和url对应关系的文件名
            @self.html_folder:存放html文件的文件夹名
            @self.filename_url:储存filename和对应的url
        '''
        self.index=_index
        self.html_folder=_html_folder
        self.filename_url=dict()
        self.pic_count=0

    #######################
    #初始化filename_url字典#
    #######################
    def intial_filename_url(self):
        with open(self.index,"r") as f:
            while True:
                line=f.readline()
                if line=='\n' or line=='':
                    break
                url_filename=line.split('\t')
                url=url_filename[0]
                if not len(url_filename)==2:
                    continue
                filename=url_filename[1][:-1]
                self.filename_url[filename]=url
            print("Reading text finished!")
    
    ##################
    #获取新闻网页的图片#
    ##################
    def get_img(self,url,soup,filename):
        news_img_list=[]
        for i in soup.findAll('div',{'class':'textBody'}):
            for img in i.findAll('img'):
                img_src=img.get('src')
                img_src=urllib.parse.urljoin(url,img_src)
                news_img_list.append(img_src)
        return news_img_list

    #################
    #返回新闻具体信息#
    #################
    def news_detail(self,filename):
        '''
            @filename:html文件名
        '''
        path=os.path.join(self.html_folder,filename)
        f=open(path,encoding='utf-8')
        contents=f.read()
        f.close()
        soup=BeautifulSoup(contents,features="html.parser")
        title=re.findall("<title>(.*)</title>",contents)[0] #标题
        date=re.findall('<time>(.*)</time>',contents)[0] #日期
        #文本内容
        text=""
        for txt in soup.findAll('div',{'class':'textBody'}):
            for t in txt.findAll('p'):
                text+=t.text
        url=self.filename_url.get(filename) #url
        #图片
        new_img_url=""
        if len(self.get_img(url,soup,filename))>0:
            new_img_url=self.get_img(url,soup,filename)[0]
        #tips
        for i in soup.findAll('div',{'class':'tips'}):
            tips=i.select('p')[0].text
        #site
        site=urlparse(url).netloc
        #related
        related=[]
        for div in soup.findAll('div',{'class':'left1 mulu_bg'}):
            for i in div.findAll('li',{'class':'even'}): 
                related_news=dict()
                for a in i.findAll('a'):
                    new_url=a.get('href')
                    related_news['href']=urllib.parse.urljoin('http://www.jhzhx.com/gjzq/xj/3121.html',new_url)
                    for img in a.findAll('img'):
                        related_news['title']=img.get('alt')
                        img_src=img.get('src')
                        related_news['img_src']=urllib.parse.urljoin('http://www.jhzhx.com/gjzq/xj/3121.htmll',img_src)
                related.append(related_news)
                related_news['text']=i.select('p')[0].text
        return title,date,url,site,new_img_url,tips,text,related

    ##########
    #存储图片#
    #########
    def save_all_img(self):
        folder="image"
        if not os.path.exists(folder):  # 如果文件夹不存在则新建
            os.mkdir(folder)
        with open(self.index,"r") as f:
            while True:
                line=f.readline()
                if line=='\n' or line=='':
                    break
                url_filename=line.split('\t')
                filename=url_filename[1][:-1]
                self.save_img(folder,filename)
        
    def save_img(self,folder,filename):
        global count
        path=os.path.join(self.html_folder,filename)
        try:
            f=open(path,encoding='utf-8')
            contents=f.read()
            f.close()
            soup=BeautifulSoup(contents,features="html.parser")
            url=self.filename_url.get(filename)
            img_list=self.get_img(url,soup,filename)
            count=0
            for img in img_list:
                img_filename=filename+"%"+str(count)+'.jpg'
                f=open(os.path.join(folder,img_filename),'wb')
                a=requests.get(img)
                f.write(a.content)  # 将图片存入文件
                f.close()
                count+=1
                self.pic_count+=1
                print(self.pic_count,"pictures")
        except:
            return 

if __name__ == '__main__':
    xinwen_parser=Parser('sports_index.txt','xinwen_html')
    xinwen_parser.intial_filename_url()
    xinwen_parser.save_all_img()
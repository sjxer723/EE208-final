# 2020 FALL EE208
# Copyright Group5
INDEX_DIR = "IndexFiles.index"

import sys, os, lucene,threading, time
from urllib.parse import urlparse
from datetime import datetime

# from java.io import File
from java.nio.file import Paths
from org.apache.lucene.analysis.miscellaneous import LimitTokenCountAnalyzer
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.document import Document, Field, FieldType, StringField
from org.apache.lucene.index import FieldInfo, IndexWriter, IndexWriterConfig, IndexOptions
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.util import Version

from bs4 import BeautifulSoup
import jieba
import re
import urllib
import requests
import datetime
import parser

"""
This class is loosely based on the Lucene (java implementation) demo class 
org.apache.lucene.demo.IndexFiles.  It will take a directory as an argument
and will index all of the files in that directory and downward recursively.
It will index on the file path, the file name and the file contents.  The
resulting Lucene index will be placed in the current directory and called
'index'.
"""
count=0
opt_site=[]
def get_site(url):
    res=urlparse(url)
    return res.netloc

class Ticker(object):
    def __init__(self):
        self.tick = True
    def run(self):
        while self.tick:
            sys.stdout.write('.')
            sys.stdout.flush()
            time.sleep(1.0)

class IndexFiles(object):
    """Usage: python IndexFiles <doc_directory>"""
    def __init__(self,root,index,storeDir):
        if not os.path.exists(storeDir):
            os.mkdir(storeDir)

        #store=SimpleFSDirectory(File(storeDir).toPath())
        store=SimpleFSDirectory(Paths.get(storeDir))
        analyzer=StandardAnalyzer() #analyzer对文档进行词法分析和语言处理
        analyzer=LimitTokenCountAnalyzer(analyzer, 1048576)
        config=IndexWriterConfig(analyzer)
        config.setOpenMode(IndexWriterConfig.OpenMode.CREATE)
        writer=IndexWriter(store, config) #创建一个IndexWriter用来写索引文件

        self.indexDocs(root,index,writer)
        ticker=Ticker()
        print('commit index')
        threading.Thread(target=ticker.run).start()
        writer.commit()
        writer.close()
        ticker.tick=False
        print('done')

    def indexDocs(self,root,index,writer):
        global filename_url,count
        #文档的文件名及路径的FieldType
        t1 = FieldType()
        t1.setStored(True) #表示需要完全储存内容
        t1.setTokenized(False) #表示需要分词
        t1.setIndexOptions(IndexOptions.NONE)  # Not Indexed
        
        #文档内容相关的FieldType
        t2 = FieldType()
        t2.setStored(True) #表示不需要完全储存内容
        t2.setTokenized(True)
        t2.setIndexOptions(IndexOptions.DOCS_AND_FREQS_AND_POSITIONS)  # Indexes documents, frequencies and positions.
    
        xinwen_parser=parser.Parser(index,root)
        xinwen_parser.intial_filename_url()
        for root,dirnames,filenames in os.walk(root):
            #游走遍历目录下的所有文档
            sum=0
            for filename in filenames:
                print("adding", filename)
                try:
                    if not xinwen_parser.filename_url.get(filename):
                        continue
                    title,date,url,site,new_img_url,tips,text,related=xinwen_parser.news_detail(filename)
                    #建立索引
                    doc = Document()
                    doc.add(Field("title",title,t1))
                    doc.add(Field("date", date, t1))
                    doc.add(Field("url",url,t1))
                    doc.add(Field("site",site,t1))
                    doc.add(Field("new_img_url",new_img_url,t1))
                    doc.add(Field("filename",filename, t1))
                    doc.add(Field("tips",tips,t1))
                    if len(text)==0:
                        print("warning: no content in %s" % filename)
                        continue
                    doc.add(Field("contents",text, t2))
                    writer.addDocument(doc)
                    sum+=1
                    print("Finished",sum,"pages")
                except Exception as e:
                    print("Failed in indexDocs:", e)

if __name__ == '__main__':
    lucene.initVM()#vmargs=['-Djava.awt.headless=true'])
    print('lucene', lucene.VERSION)
    # import ipdb; ipdb.set_trace()
    start=time.time()
    try:
        IndexFiles('xinwen_html',"sports_index.txt",'sports_index')
        end=time.time()
        print(end-start)
    except Exception as e:
        print("Failed: ", e)
        raise e
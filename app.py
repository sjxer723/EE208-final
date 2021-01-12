# 2020 sjtu FALL EE208
# Copyright: Group5

INDEX_DIR = "IndexFiles.index"

import sys, os, lucene
from java.io import File
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.index import DirectoryReader
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.search import IndexSearcher
from org.apache.lucene.util import Version
from org.apache.lucene.search.highlight import SimpleFragmenter
from org.apache.lucene.search.highlight import SimpleHTMLFormatter
from org.apache.lucene.search.highlight import Highlighter
from org.apache.lucene.search.highlight import QueryScorer
import datetime
import parser
import web
import jieba
import lsh
import extract_faces
#import extract_features
from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__,static_url_path='/static')
search_result=[] #储存搜索结果
dic1=dict()
dic2=dict()

LSH_1=lsh.lsh('features')
LSH_1.generate_hash()
LSH_2=lsh.lsh('faces_features')
LSH_2.generate_hash()

###############
#基于关键词搜索#
###############
def search(keyword):
    STORE_DIR = "sports_index"
    vm_env.attachCurrentThread()
    directory=SimpleFSDirectory(File(STORE_DIR).toPath())
    searcher=IndexSearcher(DirectoryReader.open(directory))
    analyzer=StandardAnalyzer()

    res_cnt,res_list=get_res(searcher,analyzer,keyword)
    return res_cnt,res_list

###########
#按时间排序#
###########
def get_date(res):
    return datetime.datetime.strptime(res['date'],"%Y-%m-%d %M:%S").timestamp()
def search_by_time(keyword):
    res_cnt,res_list=search(keyword)
    res_list=sorted(res_list,key=lambda res:get_date(res),reverse=True)
    return res_cnt,res_list

##########
#图像搜索#
#########
def img_search(filename):
    #ex.extract_test(filename)
    #LSH=lsh.lsh()
    global LSH_1
    res=LSH_1.match('httpwww.jhzhx.comgjzq27.html%0.jpg.npy')
    return len(res),res

#########
#人脸搜索#
#########
def face_search(filename):
    ex=extract_faces.face_recognition()
    faces_cnt,faces=ex.extract(filename)
    return faces_cnt,faces

def highlighting(analyzer,contents,query):
    formatter=SimpleHTMLFormatter("<b><font color='black'>","</font></b>")
    highlighter=Highlighter(formatter,QueryScorer(query))
    highlighter.setTextFragmenter(SimpleFragmenter(30))
    tokenStream=analyzer.tokenStream('contents',contents)
    light_content=highlighter.getBestFragments(tokenStream,contents,3,'...')
    return light_content 

def face_match(res_list):
    global LSH_2
    res=[]
    res=res+LSH_2.match('httpwww.jhzhx.comgjzq79.html%0%1.npy')
    '''
    for face in res_list:
        res=res++LSH_2.match(face)
    '''
    return len(res),res
##################
#返回关键词搜索结果#
##################
def get_res(searcher,analyzer,keyword):
    query=QueryParser("contents",analyzer).parse(keyword)
    scoreDocs=searcher.search(query, 50).scoreDocs
    res_list=[]
    for i, scoreDoc in enumerate(scoreDocs):
        doc = searcher.doc(scoreDoc.doc)
        res={}
        res['title']=doc.get('title')
        res['url']=doc.get('url')
        res['site']=doc.get('site')
        res['date']=doc.get('date')
        res['tips']=highlighting(analyzer,doc.get('tips'),query)
        res['filename']=doc.get('filename')
        res['new_img_url']=doc.get('new_img_url')
        res_list.append(res)
    return len(scoreDocs),res_list

#################
#返回新闻具体信息#
#################
def get_message(index,root,filename):
    xinwen_parser=parser.Parser(index,root)
    xinwen_parser.intial_filename_url()
    title,date,url,site,new_img_url,tips,text,related=xinwen_parser.news_detail(filename)
    return title,date,url,site,new_img_url,tips,text,related

def init_dict():
    global dic1,dic2
    f=open('dic.txt',encoding='utf-8')
    contents=f.read()
    dic1=eval(contents)
    f_1=open('newdict.txt',encoding='utf-8')
    contents_1=f_1.read()
    dic2=eval(contents_1)

def get_similar(title):
    id=dic1[title]
    similar=dic2[id]
    return similar

@app.route('/')
def form_1():
    return render_template("index.html")

@app.route('/t')
def form_t():
    return render_template("test.html")

@app.route('/word')
def form_2():
    return render_template("word.html")

@app.route('/img')
def form_3():
    return render_template("img.html")

@app.route('/face')
def form_4():
    return render_template("face.html")

@app.route('/wdresult', methods=['GET','POST'])
def wd_result():
    keyword=request.args.get('keyword')
    res_cnt,res_list=search(keyword)
    res_cnt_1,res_list_1=search_by_time(keyword)
    return render_template("result.html", keyword=keyword,res_cnt=res_cnt,res_list=res_list,res_cnt_1=res_cnt_1,res_list_1=res_list_1)

@app.route('/imgresult', methods=['GET','POST'])
def img_result():
    photo=request.files['file'] #获取网页上传的图片
    res_cnt,res_list=img_search(photo)
    return render_template("imgresult.html",res_cnt=res_cnt,res_list=res_list)

@app.route('/faceresult', methods=['GET','POST'])
def face_result():
    #photo=request.files['file'] #获取网页上传的图片
    res_cnt,res_list=face_search('httpwww.jhzhx.comgjzq79.html%0.jpg')
    match_cnt,match_list=face_match(res_list)
    return render_template("faceresult.html",res_cnt=res_cnt,res_list=res_list,match_cnt=match_cnt,match_list=match_list)

@app.route('/message',methods=['GET','POST'])
def book_detail():
    filename=request.args.get('filename')
    title,date,url,site,new_img_url,tips,text,related=get_message("sports_index.txt",'xinwen_html',filename)
    similar=get_similar(title)
    return render_template("message.html", title=title,date=date,url=url,site=site,pic=new_img_url,tips=tips,text=text,related=related,similar=similar)

if __name__ == '__main__':
    init_dict()
    try:
        vm_env = lucene.initVM(vmargs=['-Djava.awt.headless=true'])
    except:
        vm_env = lucene.getVMEnv()
    app.run(debug=True, port=5050)
    '''
    print(face_search('httpwww.jhzhx.comgjzq79.html%0.jpg'))
    '''
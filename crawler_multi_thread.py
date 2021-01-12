# SJTU EE208

import threading
import queue
import time
import os
import string
import sys
import urllib.error
import urllib.parse
import urllib.request
import re

from bs4 import BeautifulSoup

#全局变量，用来控制任务的运行次数
flag=1
count=0

#将网页名转换为合法的文件名
def valid_filename(s):
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    s = ''.join(c for c in s if c in valid_chars)
    return s


#获取page链接对应的网页html文档
def get_page(page):
    content=''
    #提示正在进行页面下载工作
    print('downloading page %s' % page)
    #尝试打开page链接并获取其html文档内容，失败则打印错误提示
    headers={
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36',
        'Cookie':'__permanent_id=20200712202406832115487145286544802; ddscreen=2; dest_area=country_id%3D9000%26province_id%3D111%26city_id%20%3D0%26district_id%3D0%26town_id%3D0; __visit_id=20201101181846655242098865516761669; __out_refer=; permanent_key=202011011819233302793386812c8df6; USERNUM=B9jO62DY5GRvw4bbfdztEA==; login.dangdang.com=.AYH=20201101182030113054848&.ASPXAUTH=KZWL81MqcgeipctXhYn3bIhRIOAsWDbAWZ2Uf3kSgNxPvjHeBOoSIg==; dangdang.com=email=MTU5MDIxNTk1MzYxMTc2MEBkZG1vYmlscGhvbmVfX3VzZXIuY29t&nickname=&display_id=3776740407085&customerid=sSIsotxMDoq7SC0aRDZRuA==&viptype=ZFj1HqZg5SY=&show_name=159%2A%2A%2A%2A9536; ddoy=email=1590215953611760%40ddmobilphone__user.com&nickname=&agree_date=1&validatedflag=0&uname=15902159536&utype=&.ALFG=off&.ALTM=1604226084; sessionID=pc_5fef5a742e91879558c469ce82da4f1fa2852564c9ac246b1f90b233ae7d1084; __dd_token_id=20201101182124446760780380f6bbb9; __rpm=login_page.login_password_div..1604226010995%7Clogin_share_bind_page...1604226084338; order_follow_source=-%7C-O-123%7C%2311%7C%23login_third_qq%7C%230%7C%23; LOGIN_TIME=1604226086003; __trace_id=20201101182126012218704386760888105',
    }
    req = urllib.request.Request(url=page,headers=headers)
    try:
        status=urllib.request.urlopen(req,timeout=100).code
        content=urllib.request.urlopen(req,timeout=100).read()
        
        time.sleep(0.5)
        print('Request %s succeeded.'% page)
        return content
    except:
        print('Request %s Error.'% page)


#获取html文档中的链接地址，并存入列表中
def get_all_links(content,page):
    links = []
    #若content为空则跳过
    if not content:
        pass
    else:
        #将html文档构建为BeautifulSoup对象，使用utf-8编码
        content=BeautifulSoup(content,'html.parser',from_encoding='utf-8')
        #获取链接的绝对地址或相对地址
        for i in content.findAll('a',{'href':re.compile('^http|^/')}):
            link=i.get('href')
            #将相对地址补全为绝对地址
            link=urllib.parse.urljoin(page,link)
            if link is not None:
                #排除伪协议的干扰
                if link.find('javascript')!=-1:
                    pass
                #将链接地址存入列表中
                else:
                    links.append(link) 
    return links


#将网页存到文件夹里，将网址和对应的文件名写入index.txt中
def add_page_to_folder(page, content):
    index_filename = 'sports_index8.txt'  
    #存放网页的文件夹
    folder = 'sports_html8'
    #将网址变成合法的文件名
    filename = valid_filename(page)
    index = open(index_filename, 'a')
    try:
        #index.txt中每行是'网址 对应的文件名'
        search=re.search(r'^http://sports.xinhuanet.com/c/\S+',page)
        if search==None:
            index.close()
            pass
        else:
            index.write(page + '\t' + filename + '\n')
            index.close()
    #如果文件夹不存在则新建
            if not os.path.exists(folder):
                os.mkdir(folder)
            try:
                f = open(os.path.join(folder, filename), 'w')
        #   若页面为空则跳过
                if not content:
                    pass
                else:
                #将网页存入文件
                    f.write(content.decode('utf8','ignore'))  
                    f.close()
            except:
                pass
    except:
        pass

#任务函数
def working():
    #声明全局变量count和flag
    global count
    global flag
    while flag:
        #获取队列中第一个元素
        page = q.get()
        #若该链接未爬过则运行
        if page not in crawled:
            #获取html文档
            content = get_page(page)
            #将网页存入文件夹中
            add_page_to_folder(page,content)
            #获取html文档中的链接地址
            outlinks = get_all_links(content,page)
            for link in outlinks:
                #对链接进行查重
                if link not in crawled:
                    #没有爬过则加入队列
                    q.put(link)
                else:
                    #爬过则从列表中移除
                    outlinks.remove(link)
            #申请锁                
            if varLock.acquire():
                #将当前地址存入已爬列表中
                crawled.append(page)
                #计数器计数
                count+=1
                #提示当前爬取页面数量
                print('%s pages have been crawled.' % count)
                #当爬取页面数量达到设定的最大值时准备结束任务
                if count==max_num:
                    flag=0
                    localflag=1
                    while localflag:
                        try:
                            #将队列逐项清空
                            q.task_done()
                        except:
                            localflag=0
                    break
                varLock.release()
            q.task_done()


if __name__=='__main__':
    #获取种子链接和爬取页面最大数量
    seed=sys.argv[1]
    max_num=int(sys.argv[2])
    #输入线程数量
    NUM=int(input('Please give the quantity of threads:'))

    crawled=[]

    #创建锁对象
    varLock=threading.Lock()

    #创建队列
    q=queue.Queue()

    #将种子放入队列中
    q.put(seed)

    print('started')
    #获取任务开始时间
    start=time.time()

    #创建线程并开始任务，将其设置为守护线程
    for i in range(NUM):
        t=threading.Thread(target=working)
        t.setDaemon(True)
        t.start()
    #等待队列为空再执行后面的操作
    q.join()
    #获取任务结束时间
    end=time.time()
    print('Crawling completed.')
    #输出任务用时
    print(end-start)

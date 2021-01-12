import os
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import HashingVectorizer
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans, MiniBatchKMeans
import jieba,sys
import json

def loadDataset():
    #导入数据
    root='./sports_html'

    for dirpath, dirnames, filenames in os.walk(root):
        dataset=[]
        for filename in filenames:
            path = os.path.join(root, filename)
            file = open(path, encoding='utf-8', errors='ignore')
            contents = file.read()
            file.close()
            soup=BeautifulSoup(contents,'html.parser')
            title=soup.findAll('title')
            if(len(title))==0:
                continue
            title=title[0].string
            title=title.strip('\n')
            #使用jieba分词器进行文本处理
            newtitle=jieba.cut_for_search(title)
            newtitle=''.join(newtitle)
            dataset.append((newtitle,filename,title))
            #为节省时间，将数据保存到文本文件中
            with open('dataset.txt','w') as f:
                data=str(dataset)
                f.write(data)
    return dataset
    

def transform(dataset,n_features=1000):
    vectorizer = TfidfVectorizer(max_df=0.5, max_features=n_features, min_df=2,use_idf=True)
    tmp=[]
    for i in dataset:
        tmp.append(i[0])
    X = vectorizer.fit_transform(tmp)
    return X,vectorizer

def train(X,vectorizer,true_k=13,minibatch = False,showLable = False):
    #使用采样数据还是原始数据训练k-means，    
    if minibatch:
        km = MiniBatchKMeans(n_clusters=true_k, init='k-means++', n_init=1,
                             init_size=1000, batch_size=1000, verbose=False)
    else:
        km = KMeans(n_clusters=true_k, init='k-means++', max_iter=300, n_init=1,
                    verbose=False)
    km.fit(X)    
    if showLable:
        print("Top terms per cluster:")
        order_centroids = km.cluster_centers_.argsort()[:, ::-1]
        terms = vectorizer.get_feature_names()
        print (vectorizer.get_stop_words())
        for i in range(true_k):
            print("Cluster %d:" % i, end='')
            for ind in order_centroids[i, :10]:
                print(' %s' % terms[ind], end='')
            print()
    result = list(km.predict(X))
    print ('Cluster distribution:')
    print (dict([(i, result.count(i)) for i in result]))
    return -km.score(X),result

def test():
    #测试选择最优分类数，并绘制误差与分类数的关系曲线
    dataset = loadDataset()    
    print("%d documents" % len(dataset))
    X,vectorizer = transform(dataset,n_features=500)
    true_ks = []
    scores = []
    for i in range(3,150,1):        
        score,rs = train(X,vectorizer,true_k=i)
        score=score/len(dataset)
        print (i,score)
        true_ks.append(i)
        scores.append(score)
    plt.figure(figsize=(8,4))
    plt.plot(true_ks,scores,label="error",color="red",linewidth=1)
    plt.xlabel("n_features")
    plt.ylabel("error")
    plt.legend()
    plt.savefig('result.jpg')
    plt.show()

def out():
    #在最优参数下输出聚类结果
    dataset = loadDataset()
    X,vectorizer = transform(dataset,n_features=500)
    score = train(X,vectorizer,true_k=13,showLable=True)/len(dataset)
    print (score)






data=open('dataset.txt','r')
dataset=data.read()
data.close()
dataset=eval(dataset)
print(type(dataset))
X,vectorizer = transform(dataset,n_features=500)
score,res = train(X,vectorizer,true_k=11,showLable=True)
dic={}
for i in range(len(res)):
    dic[dataset[i][2]]=res[i]
dic=str(dic)
with open('dic.txt','w') as h:
    h.write(dic)
newdic={}
for i in range(11):
    newdic[i]=[]
#获取分类结果，并保存进dic.txt和newdict.txt文件中
file=open('dic.txt','r')
dic=file.read()
dic=eval(dic)
for j in dic.keys():
    newdic[dic[j]].append(j)
with open('newdict.txt','w') as f:
    newdic=str(newdic)
    f.write(newdic)
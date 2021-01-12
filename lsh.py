# 2020 sjtu FALL EE208
# Copyright: Group5

import numpy as np
import time
import os

class lsh(object):
    def __init__(self,_index,_L=16,_num_dataset=40,):
        self.L=_L
        self.num_dataset=_num_dataset
        self.hashtable=[]
        self.index=_index
    
    #######################
    #计算单张图片的特征信息#
    #######################
    def get_features(self,folder,npy_name):
        try:
            in_vec=np.load(folder+'/'+npy_name).ravel()
            norm=np.linalg.norm(in_vec,ord=2)
            norm_vec=in_vec/norm #归一化处理
            for j in range(2048):
                if norm_vec[j]>=0 and norm_vec[j]<0.015:
                    norm_vec[j]=0
                elif norm_vec[j]>=0.015 and norm_vec[j]<0.02:
                    norm_vec[j]=1
                elif norm_vec[j]>=0.02:
                    norm_vec[j]=2
            return norm_vec
        except:
            pass

    #############
    #生成哈希散列#
    #############
    def generate_hash(self):
        self.init_hashtable()
        self.calc_dataset()
        print("create succssfully!")

    #############
    #初始化哈希表#
    #############
    def init_hashtable(self):
        for j in range (self.L):
            self.hashtable.append({'0':[],'1':[],'2':[],'3':[]})
        return

    ######################
    #计算数据集对应的哈希值#
    ######################
    def calc_dataset(self):
        for root,firname,npynames in os.walk(self.index):
            for npy in npynames:
                vec=self.get_features(self.index,npy)
                #计算L个哈希函数值
                for j in range(self.L):
                    x_1,x_2=0,0
                    if vec[128*j+1]>=1:
                        x_1=1
                    if vec[128*j+65]==2:
                        x_2=1
                    idx=x_1+x_2*2
                    self.hashtable[j][str(idx)].append(npy[:-4])
    ######
    #匹配#
    ######
    def match(self,target_npy):
        data=[]
        target_vec=self.get_features("input_npy",target_npy)
        for j in range(self.L):
            x_1,x_2=0,0
            if target_vec[128*j+1]>=1:
                x_1=1
            if target_vec[128*j+65]==2:
                x_2=1
            idx=x_1+x_2*2
            data.append(str(idx))
        zone=set(self.hashtable[0][data[0]])
        for i in range(1,len(data)):
            zone=set(zone)&set(self.hashtable[i][data[i]])
        result=[]
        for id,res in enumerate(zone):
            result.append(res)
            if id>5:
                break
        return result

                


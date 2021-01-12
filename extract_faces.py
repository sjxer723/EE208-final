# 2020 Fall EE208
# Copyright Group 5
import dlib
import numpy as np
import cv2
import os

class face_recognition(object):
    def __init__(self,_path_read="../static/image/",_path_save="../static/faces_separated/", \
    _path_test_save="static/input_faces/",_path_test="input/",_model='../data/dlib/shape_predictor_68_face_landmarks.dat'):
        '''
            @path_read:读取图像的路径
            @path_save:用来存储生成的单张人脸的路径
            @path_test:用来存储输入图像
            @path_test_save:用来存储输入图像的人脸
            @detector:dlib预测器
        '''
        self.path_read=_path_read
        self.path_save=_path_save
        self.path_test=_path_test
        self.path_test_save=_path_test_save
        self.detector=dlib.get_frontal_face_detector()
    
    # Delete old images
    def clear_images(self):
        imgs=os.listdir(self.path_save)
        for img in imgs:
            os.remove(self.path_save+img)
        print("clean finish",'\n')
    
    # extract the faces in test image
    def extract(self,filename):
        res=[]
        test_image=cv2.imread(self.path_test+filename)
        test_faces=self.detector(test_image,1)
        print(test_faces)
        for num,face in enumerate(test_faces):
            height,width= face.bottom()-face.top(),face.right()-face.left() # 计算矩形框大小
            test_img_blank=np.zeros((height, width,3),np.uint8) # 根据人脸大小生成空的图像
            for i in range(height):
                for j in range(width):
                    test_img_blank[i][j]=test_image[face.top()+i][face.left()+j]
            # save faces
            face_path=self.path_test_save+filename[:-4]+"%"+str(num+1)+".jpg"
            print("Save into:",face_path)
            cv2.imwrite(face_path,test_img_blank)
            res.append(face_path)
        return len(res),res

    # create the face database
    def face_recog(self):
        if not os.path.exists(self.path_save):
            os.mkdir(self.path_save)
        self.clear_images()
        read_imgs=os.listdir(self.path_read)
        for read_img in read_imgs:
            try:
                img=cv2.imread(self.path_read+read_img)
                faces=self.detector(img,1)
                print("人脸数/faces in all:", len(faces), '\n')

                for num,face in enumerate(faces):
                    height,width= face.bottom()-face.top(),face.right()-face.left() # 计算矩形框大小
                    # 根据人脸大小生成空的图像
                    img_blank=np.zeros((height, width, 3), np.uint8)
                    for i in range(height):
                        for j in range(width):
                                img_blank[i][j] = img[face.top()+i][face.left()+j]
                    # save faces
                    print("Save into:",self.path_save+read_img[:-4]+"%"+str(num+1)+".jpg")
                    cv2.imwrite(self.path_save+read_img[:-4]+"%"+str(num+1)+".jpg",img_blank)
            except:
                continue



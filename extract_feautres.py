# SJTU EE208
import numpy as np
import torch
import os
import torchvision.transforms as transforms
from torchvision.datasets.folder import default_loader

print('Load model: ResNet50')
model = torch.hub.load('pytorch/vision', 'resnet50', pretrained=True)

normalize = transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                 std=[0.229, 0.224, 0.225])
trans = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    normalize,
])

def features(x):
    x = model.conv1(x)
    x = model.bn1(x)
    x = model.relu(x)
    x = model.maxpool(x)
    x = model.layer1(x)
    x = model.layer2(x)
    x = model.layer3(x)
    x = model.layer4(x)
    x = model.avgpool(x)

    return x

def extract_database():
    root="image"
    for root,dirname,images in os.walk(root):
        for img in images:
            try:
                test_image = default_loader(os.path.join(root,img))
                input_image = trans(test_image)
                input_image = torch.unsqueeze(input_image, 0)
                image_feature = features(input_image)
                image_feature = image_feature.detach().numpy()
                np.save('./features/%s.npy'%img[:-4], image_feature)
                print('Save features!')
            except:
                continue

def extract_test(photo):
    root_1="input"
    test_image=default_loader(os.path.join(root,img))
    input_image=trans(test_image)
    input_image = torch.unsqueeze(input_image, 0)
    image_feature = features(input_image)
    image_feature = image_feature.detach().numpy()
    np.save('./input_npy/%s.npy'%img[:-4], image_feature)
    print('Save features!')

if __name__ == "__main__":
    extract_database()
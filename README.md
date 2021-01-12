# Search engine based on Flask
This is our final project for 2020 Fall EE208.🙂

## What we have done?
In this project, we have crawled over ten thousands pages and six thousands photos. And we 

# What can it help you achieve?

## The implement of the main files
In `static`, it's our static resource for the front web, which includes the image and faces database and css js files.
Before using it, you should first add the static path to the `app.py`.  
In `templates`,it's our html templates.  
In `genetic-drawing`,it's a ai-drawing achieved by genetic-algorithm. It can imitate the way humans draw and produce a `gif` image of the search result.   However, we didn't write it alone. It's an open source project from GitHub. We improve and adjust it.  
`sports_html` and `sohu_html` are our original data.
`sports_index` is the index created by lucene.
`app.py` is used to create our web.
`extract_face.py` is used to extract all faces in a photo and create the faces database. 

## Python
you would need the following python 3 libraries:
* opencv 3.4.1
* numpy 1.16.2
* matplotlib 3.0.3
* jieba 0.42.1
* Flask 1.1.2
* dlib 19.21.1
* lucene 
The project is runned in docker enviroment.
## How to start?
open the project in docker enviroment, and enter
`python app.py`

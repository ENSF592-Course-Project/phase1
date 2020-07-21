import pymongo
from pymongo import MongoClient
import pandas as pd
import re
import os

cluster= MongoClient("mongodb+srv://cityAlberta:123321Zxc@citypythonproject.ygcbk.mongodb.net/cityData?retryWrites=true&w=majority")
# cluster-- database --collection


def readAndInsertFile(filepath):
    print(filepath)
    index=0
    for year in range(2016,2019):
        if(str(year) in filepath):
            index=filepath.find(str(year))
            break
        else:
            continue    
    typeList=["Volumes","Incidents","Volume*"]
    dbName=""
    for type in typeList:
        if(type.lower() in filepath.lower()):
            dbName=type
            break
    #database Name
    db=cluster[dbName]
    collection=db[dbName+"_"+filepath[index:index+4]]
     # collection Name
    df=pd.read_csv(filepath)
    if(filepath[index:index+4]=='2017' and dbName=="Volumes"):
        df=df.rename(columns={'year':"year_vol", "segment_name":"secname"})
    elif(filepath[index:index+4]=='2018' and dbName=="Volumes"):
        df=df.rename(columns={'YEAR':"year_vol",'SECNAME':"secname", 'Shape_Leng':"shape_leng", 'VOLUME':"volume",'multilinestring':"the_geom"})   
    records_ = df.to_dict(orient = 'records')
    collection.insert_many(records_ )


def readCSVFiles(directory):
    for subdir, dirs, files in os.walk(rootdir):
        for file in files:
            if(file.endswith('.csv')):
                readAndInsertFile("projectFiles/"+file)



# ****************  commands to insert files into mongodb*********************
rootdir= 'C:/Users/15878/Desktop/ENSP 592/python/PythonLab/projectFiles'
readCSVFiles(rootdir)
                

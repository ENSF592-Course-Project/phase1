import pymongo
from pymongo import MongoClient
import pandas as pd
from tabulate import tabulate
import matplotlib.pyplot as plt
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import folium
import webbrowser

class db_operation():
    def __init__(self, dbName, collectionName, year):
        self.cluster= MongoClient("mongodb+srv://group_member_1:pythonpythonpython@cluster0.nvhig.mongodb.net/<cluster0>?retryWrites=true&w=majority")
        self.dbName = dbName
        self.collectionName = collectionName
        self.year = year


    def read_db(self,sort):
        #commands to read data from mongodb and plot in pandas
        db = self.cluster[self.dbName]
        collection = db[self.collectionName]
        year = self.year
        if(self.dbName == 'Volumes'):
            cursor = collection.find()
            entries = list(cursor)
            df = pd.DataFrame(entries, columns= ['secname','year_vol','the_geom','length_m','volume'])
            df = df.set_index('secname')
            if(sort):
                df.sort_values(by = ['volume'], inplace = True, ascending = False)
        elif(self.dbName == 'Incidents'):
            cursor=collection.find({'START_DT': {'$regex':year}})
            entries = list(cursor)
            df = pd.DataFrame(entries)
            # df=df.groupby(['INCIDENT INFO','Longitude','Latitude'])['Count'].sum().reset_index()
            # longitude and latitude slightly varies, so group by those will return inaccurate results
            df = df.groupby('INCIDENT INFO').agg({'Longitude':'mean','Latitude':'mean', 'Count':'sum'}).reset_index()

            if(sort):
                df.sort_values(by=['Count'], inplace=True, ascending=False)
        else:
            return
        return df.head(50)

    
    def analyze_top_volumes(self):
        YearList = [2016, 2017, 2018]
        MaxVolumeList=[]
        db=self.cluster["Volumes"]
        for i in YearList:
            collection = db["Volumes" + "_" + str(i)]
            cursor = collection.find()
            entries = list(cursor)
            df = pd.DataFrame(entries,columns= ['secname', '_id','year_vol','the_geom','length_m','volume'])
            df.sort_values(by = ['volume'], inplace=True, ascending=False)
            MaxVolumeList.append(int(df.iloc[0,-1]))
        return MaxVolumeList
    

    def analyze_top_accidents(self):
        YearList = [2016,2017,2018]
        MaxAccidentCountsList = []
        db = self.cluster[self.dbName]
        collection = db[self.collectionName]
        for i in YearList:
            cursor=collection.find({'START_DT': {'$regex':str(i)}})
            entries = list(cursor)
            df = pd.DataFrame(entries)
            df = df.groupby('INCIDENT INFO').agg({'Longitude':'mean','Latitude':'mean', 'Count':'sum'}).reset_index()
            df.sort_values(by = ['Count'], inplace=True, ascending=False)
            MaxAccidentCountsList.append(int(df.iloc[0,-1]))
        return MaxAccidentCountsList
     
    
    def map_display(self):
        df = self.read_db(True)
        YYC_COORDINATES = [51.05011, -114.08529]

        # create empty map zoomed in on Calgary
        map = folium.Map(location=YYC_COORDINATES, zoom_start=12)

        # add a marker for for highest volumn or incident number
        if self.dbName == 'Incidents':
            folium.Marker([df['Latitude'].iloc[0], df['Longitude'].iloc[0]], popup = 'Highest number of incidents').add_to(map)
        elif self.dbName == 'Volumes':
            s = df['the_geom'].iloc[0].split()
            latitude_start = float(s[2].strip(",)("))
            longitude_start = float(s[1].strip(",)("))
            index_endpoint = len(s)-1
            latitude_end = float(s[index_endpoint].strip(",)("))
            longitude_end = float(s[index_endpoint-1].strip(",)("))
            # add start point marker
            folium.Marker([latitude_start, longitude_start], popup = 'Highest volume start point').add_to(map)
            # add end point marker
            folium.Marker([latitude_end, longitude_end], popup = 'Highest volume end point').add_to(map)
            
            line = [[latitude_start, longitude_start], [latitude_end, longitude_end]]
            folium.PolyLine(line, color="green", weight=2.5, opacity=1).add_to(map)
        map.save("map.html")
        
        filename = 'file:///Users/apple/UofCalgary/ENSF-592/Project/map.html'
        chrome_path = '/Applications/Google Chrome.app'
        webbrowser.get('chrome').open_new_tab(filename)
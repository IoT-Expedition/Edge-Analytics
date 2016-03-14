#!/usr/bin/env python
#
# Knonking scenario GIoTTO.
# Khalid Elgazzar
# 2015/11/7
#
# Copyright 2015 Carnegie Mellon University
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

#http://stackoverflow.com/questions/2835559/parsing-values-from-a-json-file-in-python

import os
import sys

import cv2
import urllib2
import json
import requests

from StringIO import StringIO

import requests
from PIL import Image
from bs4 import BeautifulSoup

from subprocess import call
from subprocess import check_output

from time import time
from time import sleep
import datetime

#import nowCards


fileDir = os.path.dirname(os.path.realpath(__file__)) #~/openface
sys.path.append(fileDir)

#classifierFile = os.path.join(fileDir, '~/openface/data/mydataset/reps/classifier.pkl')
classifierFile = '/root/src/openface/data/mydataset/reps/classifier.pkl')
# Capturing the knocking person's face
para={}

with open("knocking.conf", "r") as f:
    for line in f:
        (key, value)=line.split()
        para[key]=value

headers = {'content-type':'application/json'}
postSensor_uuid = para["postSensor_uuid"] #b3272cdd-0f74-4cb9-92fc-6baf5ee748de
BD_domain = para["BD_domain"]
posturl = BD_domain+":82/service/sensor/{}/timeseries"

#domainName = "http://localhost/" # on mac
domainName = "http://buildingdepot.andrew.cmu.edu/" # on Linux
#documentRoot = "/Library/WebServer/Documents/" # on mac
#documentRoot = "/srv/buildingdepot/Documentation/build/html/" #Bulidingdepot
#documentRoot = "/Users/Elgazzar/" # on mac
documentRoot = "/var/www/html/" # on linux
snapshot_fileName = "knockerface.png"
snapshot_loc = documentRoot + snapshot_fileName
#snapshot_loc = "./openface/images/examples/khalid1.png"
snapshot_url = domainName + snapshot_fileName

#http://buildingdepot.andrew.cmu.edu:82/service/api/v1/data/id=b90cac66-ae49-4e6d-9de5-12aed18e6a64/interval=8h/
knockingSensor_uuid = para["knockingSensor_uuid"] #"b90cac66-ae49-4e6d-9de5-12aed18e6a64"
base_url = BD_domain+":82/service/api/v1/data/id="
res = para["res"]
url = base_url + knockingSensor_uuid + res

def capture_face_local():
    # initialize the camera
    cam = cv2.VideoCapture(0)   # 0 -> index of camera
    sleep(0.3)
    s, img = cam.read()
    if s:    # frame captured without any errors
        #cv2.imwrite("khalid.jpg",img) #save image
        cv2.imwrite(snapshot_loc,img) #save image
        cam.release()
        

def capture_face():
    DCS_IP = para["camera_ip"]
    userauth = ('admin', '')

    snapurl = "http://" + DCS_IP + "/top.htm"

    r = requests.get(snapurl,  auth=userauth)
    soup = BeautifulSoup(r.content, "html.parser")

    # There are several <img> tags in page, so use border=0 attribute of 
    # objective <img> to distinguish it
    imgtag = soup.find_all("img", attrs={'border':0})
    imgsrc = BeautifulSoup(str(imgtag[0])).img['src']
    imgurl = "http://" + DCS_IP + "/" + imgsrc

    img = requests.get(imgurl, auth=userauth)
    knocker = Image.open(StringIO(img.content))
    knocker.save(snapshot_loc)

def postData(dataToPost,timeStr,sensorBD,sensorType):
    payload = { "data":[{"value":dataToPost,"time":timeStr}],"value_type":sensorType}
    r = requests.post(posturl.format(sensorBD),headers = headers,data = json.dumps(payload))


while True:
    response = requests.get(url)
    data = response.json()
    val = [];
    if bool(data["data"]):
        for x,y,z in data["data"]["series"][0]["values"]:
            val.append(z)
        print("List of current values: {}".format(val));
        
        knocktime = data["data"]["series"][0]["values"][0][1]
        timeToPost = datetime.datetime.fromtimestamp(int(knocktime)).strftime('%H:%M:%S')
        #status = data["data"]["series"][0]["values"][0][2] #first reading in the response
        #status = data["data"]["series"][0]["values"][-2][2] # last reading in the resposne
        if "knocking" in val:
            capture_face()
            #capture_face_local()
            #call("./openface/demos/classifier.py", "infer ./openface/data/mydataset/reps/classifier.pkl ./openface/images/examples/khalid1.png")
            #call(["scp", snapshot_loc, "synergy@buildingdepot.andrew.cmu.edu:/srv/buildingdepot/Documentation/build/html"])
            try:
                knocker_name = check_output(["/root/src/openface/demos/classifier.py", "infer", classifierFile, snapshot_loc])[:-1]
                #knocker_name = check_output(["~/openface/demos/classifier.py", "infer", classifierFile, snapshot_loc])[:-1]
                #knocker_name = check_output(["./demos/classifier.py", "infer","/Users/Elgazzar/openface/data/mydataset/reps/classifier.pkl","./images/examples/khalid1.png"])
            except:
                knocker_name = "Unknown"
            print("Knocker name: {}".format(knocker_name));
            
            dataToPost={"knocking_user_name":knocker_name,"knocking_user_email":"cmugiotto@gmail.com","img_url":snapshot_url,"text_content":timeToPost}
            #postData(json.dumps(dataToPost),knocktime,postSensor_uuid,"Location")
            print ("Posted data:{}".format(dataToPost));
            print ('\n')
            #nowCards.check(postSensor_uuid)
    sleep(3) #sleep 3sec
    

#!/usr/bin/env python
#
# Knonking scenario GIoTTO.
# Khalid Elgazzar
# 2015/11/7
# updated 2016/5/23
#
# Copyright 2015-2016 Carnegie Mellon University
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

from BuildingDepotHelper import BuildingDepotHelper
import nowCards

bdHelper = BuildingDepotHelper()

fileDir = os.path.dirname(os.path.realpath(__file__)) #~/openface
sys.path.append(fileDir)

classifierFile = '../openface/data/mydataset/reps/classifier.pkl'
#classifierFile = os.path.join(fileDir, '~/openface/data/mydataset/reps/classifier.pkl')
#classifierFile = '/root/src/openface/data/mydataset/reps/classifier.pkl')

postSensor_uuid = bdHelper.others["postSensor_uuid"] #7906d606-40be-419e-9dfd-6eabe28e475c
BD_domain = bdHelper.bd_rest_api['domain']

#documentRoot = "/Library/WebServer/Documents/" # on mac
documentRoot = bdHelper.bd_rest_api['documentRoot']
snapshot_fileName = bdHelper.others['snapshot_fileName']
snapshot_loc = documentRoot + snapshot_fileName
snapshot_url = BD_domain + '/'+ snapshot_fileName

def capture_face_local():
    # initialize the camera
    cam = cv2.VideoCapture(0)   # 0 -> index of camera
    sleep(0.3)
    s, img = cam.read()
    if s:    # frame captured without any errors
        #cv2.imwrite("khalid.jpg",img) #save image
        cv2.imwrite(snapshot_loc,img) #save image
        cam.release()
    call(["scp", snapshot_loc, "kelgazzar@cmu.buildingdepot.org:/srv/buildingdepot/Documentation/build/html"])

def capture_face():
    DCS_IP = settings['others']['camera_ip']
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

while True:
    end_time = int(time())
    start_time = int(time())- 15

    knockingSensor_uuid = bdHelper.others['knockingSensor_uuid'] #"516b2f6e-ce23-49e6-b56e-b5269c142a74"
    data = bdHelper.get_timeseries_data(knockingSensor_uuid, start_time, end_time)
    #data=["knocking", "silent"]
    if data:
        print("List of current values: {}".format(data));
        #knocktime = data["data"]["series"][0]["values"][0][1]
        timeToPost = datetime.datetime.fromtimestamp(int(time())).strftime('%H:%M:%S')
        #status = data["data"]["series"][0]["values"][0][2] #first reading in the response
        #status = data["data"]["series"][0]["values"][-2][2] # last reading in the resposne
        if "knocking" in data:
            capture_face()
            #capture_face_local()
            try:
                #knocker_name = check_output(["/root/srv/openface/demos/classifier.py", "infer", classifierFile, snapshot_loc])[:-1]
                knocker_name = check_output(["../openface/demos/classifier.py", "infer", classifierFile, snapshot_loc])[:-1]
            except:
                knocker_name = "Unknown"
            print("Knocker name: {}".format(knocker_name));
            
            dataToPost={"knocking_user_name":knocker_name,"knocking_user_email":"cmugiotto@gmail.com","img_url":snapshot_url,"text_content":timeToPost}
            dataToPost = json.dumps(dataToPost) 
            data_array = [
                {
                    "sensor_id":postSensor_uuid,
                    "samples":[{
                        "time":time(),
                        "value":dataToPost
                    }]
                }
            ]
 
            print bdHelper.post_data_array(data_array)
            print ("Posted data:{}".format(dataToPost));
            print ('\n')
            nowCards.check(postSensor_uuid)
    sleep(3) #sleep 3sec
    

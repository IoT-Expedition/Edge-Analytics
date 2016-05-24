import requests
import json
import time
import sys

import triggerCard
from BuildingDepotHelper import BuildingDepotHelper
bdHelper = BuildingDepotHelper()

knockername = knockermail = knockerimage = knockertext = "dummy"

def check(postSensor_uuid):
    end_time = int(time.time())
    start_time = int(time.time())- 2000
    sensor_data = bdHelper.get_timeseries_data(postSensor_uuid, start_time, end_time)
    print sensor_data
    if(sensor_data):
    	data = dict(json.loads(sensor_data[0]))
        knockername  = data['knocking_user_name']
        knockermail  = data['knocking_user_email']
        knockerimage = data['img_url']
        knockertext  = data['text_content']
        triggerCard.triggerCardfunction(data)
        time.sleep(5)
    else:
        print "No knocking singnal ..."

if __name__ == "__main__":
	#check()
	while True:
		check()	

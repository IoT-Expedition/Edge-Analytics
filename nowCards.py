import requests
import json
import time
import sys

import triggerCard

from BuildingDepotHelper import BuildingDepotHelper

bdHelper = BuildingDepotHelper()

knockername = knockermail = knockerimage = knockertext = "dummy"

"""settingFilePath = "./knockingSettings.json"
settings = json.loads(open(settingFilePath,'r').read())

def get_access_token():
    '''Get OAuth access token'''
    headers = {'content-type': 'application/json'}
    url = settings['bd_rest_api']['domain']
    url += ':' + settings['bd_rest_api']['port'] 
    url += '/oauth/access_token/client_id='
    url += settings['oauth']['client_id']
    url += '/client_secret='
    url += settings['oauth']['client_key']
    result = requests.get(url, headers=headers, verify=False)

    if result.status_code == 200:
        dic = result.json()
        return dic['access_token']
    else:
        return ''

access_token = bdHelper.get_oauth_token()
headers = {
            'content-type': 'application/json',
            'Authorization': 'Bearer ' + access_token
            }"""

def check(postSensor_uuid):
	# URL of KNOCKER sensor
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

"""def getknockerdetails(knocker_json):
	knocker_json = json.loads(knocker_json)
	try:
		checkforValues = knocker_json['data']['series']
	except KeyError, e:
		return "no data"

	values = knocker_json['data'] ['series'] [0] ['values']
	length = len(values)
	lastUpdatedValue = values[length-1][2]
	return (dict(json.loads(lastUpdatedValue)))"""


if __name__ == "__main__":
	#check()
	while True:
		check()	

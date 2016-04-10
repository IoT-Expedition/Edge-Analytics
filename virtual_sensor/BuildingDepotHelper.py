import requests

import json
import time
from giottoSetting import giottoSetting 

class BuildingDepotHelper:
    def __init__(self):
        setting = giottoSetting()
        self.buildingDepotUrl = setting.get('building_depot_url')

    def postData(self, sensorId, data, value_type=''):
        headers = {'content-type': 'application/json'}
        url = 'http://' + self.buildingDepotUrl + '/service/sensor/' + sensorId + '/timeseries'
        t = int(time.time())
        data = { "data":[{"value":data,"time":t,"value_type":value_type}]}
        result = requests.post(url, data=json.dumps(data), headers=headers)
        return result.text


if __name__ == "__main__":
    print "BuildingDepotHelper"
    helper = BuildingDepotHelper()
    helper.postData('c9eb7379-1d25-4c72-b444-f50d6fbe87ad',102)
    print 'called'

    for i in range(200):
        time.sleep(0.1)



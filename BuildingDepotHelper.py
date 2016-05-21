"""BuildingDepot helper
Provides helper methods to post data to Building Depot via its REST APIs
"""

import requests
import time
import json
import time
import calendar
from json_setting import JsonSetting

class BuildingDepotHelper:
    '''Building Depot Helpe Class'''
    def __init__(self, settingFilePath="./knockingSettings.json"):
        '''Initialize instance and load settings'''
        setting = JsonSetting(settingFilePath)
        self.bd_rest_api = setting.get('bd_rest_api')
        self.oauth = setting.get('oauth')
        self.others = setting.get('others')
        self.access_token = self.get_oauth_token()

    def get_oauth_token(self):
        '''Get OAuth access token'''
        headers = {'content-type': 'application/json'}
        url = self.bd_rest_api['domain']
        url += ':' + self.bd_rest_api['port'] 
        url += '/oauth/access_token/client_id='
        url += self.oauth['client_id']
        url += '/client_secret='
        url += self.oauth['client_key']
        result = requests.get(url, headers=headers, verify=False)

        if result.status_code == 200:
            dic = result.json()
            return dic['access_token']
        else:
            return ''

    def get_timeseries_data(self, uuid, start_time, end_time):
        '''Gets time series data
        Gets time series data for a sensor with given UUID in BuildingDepot between
        start_time and end_time
        Args:
            uuid: A UUID of a sensor
            start_time: A unix timestamp
            end_tiem: A unix timestamp
        Returns:
            An array consisting of timeseries data 
        '''
        data = []
        headers = {
            'content-type': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
            }
        url = self.bd_rest_api['domain']
        url += ':' + self.bd_rest_api['port'] 
        url += self.bd_rest_api['api_prefix'] + '/sensor/'
        url += uuid + '/timeseries?'
        url += 'start_time=' + str(start_time)
        url += '&end_time=' + str(end_time)

        result = requests.get(url, headers=headers)
        json = result.json()
        if json["data"]:
            readings = json['data']['series'][0]
            columns = readings['columns']
            values = readings['values']
            index = columns.index('value')
            
            for value in values:
                data.append(value[index])
                
        return data

    def post_data_array(self, data_array):
        '''Posts timeseries data to BuildingDepot
        Posts timeseries data to BuildingDepot. The data_array can contain
        timeseries data for multiple sensors. This is to improve data-post performance
        by reducing overheads (such as http connection establishment).
        Args:
            data_array: An object that has timeseris data for multiple sensors.
            [
                {
                    "seonor_id": UUID of a sensor,
                    "value_type": a value type (currently not used),
                    "samples":[
                        {
                            "timestamp": A unix tiemstamp,
                            "value": A sensor reading
                        },
                        { more samples if you have}
                    ]
                },
                { more sensors if you have }
            ]
        Returns:
            A returning object from BuildingDepot. If there is no error, it should
            return {"unauthorized sensor":[], "success":"true"}. Otherwise, an error
            occurred. Check BuildingDepot's document for more details about the 
            return value.
        '''
        headers = {
            'content-type': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
            }
        url = self.bd_rest_api['domain']
        url += ':' + self.bd_rest_api['port'] 
        url += self.bd_rest_api['api_prefix'] + '/sensor/timeseries'

        result = requests.post(url, data=json.dumps(data_array), headers=headers)
        return result.json()

if __name__ == "__main__":
    pass


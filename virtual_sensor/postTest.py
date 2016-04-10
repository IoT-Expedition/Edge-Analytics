import requests
import json
import gevent
import time
from gevent import monkey


headers = {'content-type': 'application/json'}
url = 'http://buildingdepot.andrew.cmu.edu:82/service/sensor/c9eb7379-1d25-4c72-b444-f50d6fbe87ad/timeseries'

data = { "data":[{"value":100,"time":0,"value_type":"something random"}]}

result = requests.post(url, data=json.dumps(data), headers=headers)
print result.text
result = requests.post(url, data=json.dumps(data), headers=headers)
print result.text

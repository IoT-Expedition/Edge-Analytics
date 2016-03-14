import requests
import json

headers = {'content-type': 'application/x-www-form-urlencoded',
			'user-agent' : 'Google NOW API Python Quickstart'}

par_anind = "client_id="
par_knock = "client_id="

def getaccessToken(flag):
	if(flag == 0):
		par = par_anind
	else:
		par = par_knock

	url="https://www.googleapis.com/oauth2/v3/token"
	r=requests.post(url,par,headers=headers)
	token = json.loads(json.dumps(r.json()))

	access_token = token['access_token']
	print access_token, flag
	return access_token
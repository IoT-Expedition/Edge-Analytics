import requests
import json

headers = {'content-type': 'application/x-www-form-urlencoded',
			'user-agent' : 'Google NOW API Python Quickstart'}

par_anind = "client_id=840111498569-hdrkf24lan7lh5r8npcf379jlthqjdjd.apps.googleusercontent.com&client_secret=0lh2Hu49DYJVdb3Y802mAvXo&refresh_token=1/abUx8j-GPJ-5CDlcbKjMPsQH65npmSjwzxnRdzaLYhtIgOrJDtdun6zK6XiATCKT&grant_type=refresh_token"
par_knock = "client_id=581708599250-7ktc40uvqh5msnh8oh5besgbcf31t5di.apps.googleusercontent.com&client_secret=NPZbT9Q_CjlI63bu02pbRTb1&refresh_token=1/4DNRM8nQPu-ZTvZfhi1AHVrDVH-9Cvwk-x5Hd-Ql-GQ&grant_type=refresh_token"

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
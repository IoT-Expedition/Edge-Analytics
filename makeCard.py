import requests
import json
import deleteCard
import refreshtoken
import jsonFormat

url = "https://www.googleapis.com/now/v1/users/me/cards/"
headers = {'Authorization': 'Bearer access_token',
				'Content-Type': 'application/json'}


if(requests.get(url,headers=headers).status_code!=200):
	accessToken = refreshtoken.getaccessToken(0)
	headers['Authorization'] = 'Bearer '+ accessToken
	deleteCard.makeDelete(accessToken)

getNowCardsList = requests.get(url, headers = headers)
print json.dumps(getNowCardsList.json(), indent = 2)

payload = jsonFormat.payload_anind
updateNowCard = requests.post(url,json.dumps(payload),headers = headers)
print json.dumps(updateNowCard.json(), indent = 2)

import requests
import json

def makeDelete(accessToken):

	headershere = {'Authorization': '',
			'Content-Type': 'application/json'}
	urlhere = "https://www.googleapis.com/now/v1/users/me/cards/"

	headershere['Authorization'] = 'Bearer '+ accessToken
	
	# DELETE THE CARD

	getNowCardsList = requests.get(urlhere, headers = headershere)
	getit = json.dumps(getNowCardsList.json(), indent = 2)
	if(getit=='{}'):
		# print "None"
		pass
		
	else:
		getit = json.loads(getit)
	
		id = getit ['cards'] [0] ['cardId']
		urlhere = urlhere+id		
		deleteNowCard = requests.delete(urlhere, headers = headershere)
		print deleteNowCard
		url = "https://www.googleapis.com/now/v1/users/me/cards/"

	return
import requests
import json
import time

import triggerCard

knockername = knockermail = knockerimage = knockertext = "dummy"

def check():
	# URL of KNOCKER sensor
	knockerURL = "http://buildingdepot.andrew.cmu.edu:82/service/api/v1/data/id=b3272cdd-0f74-4cb9-92fc-6baf5ee748de/interval=5s/"

	# Check if the URL is valid
	knockerstatuscode = (requests.head(knockerURL).status_code)

	# Get RESPONSE from BD of KNOCKER
	if(knockerstatuscode==200):
		knocker_response = requests.get(knockerURL)

		# Convert response obtained to a JSON String
		knocker_json = json.dumps(knocker_response.json(),indent=2)

		# from JSON get the details of KNOCKER to be put on the card
		knockerdetails = getknockerdetails(knocker_json)

 		if(not(knockerdetails == "no data")):
	  		knockername  = knockerdetails['knocking_user_name']
			knockermail  = knockerdetails['knocking_user_email']
			knockerimage = knockerdetails['img_url']
			knockertext  = knockerdetails['text_content']

			triggerCard.triggerCardfunction(knockerdetails)
			time.sleep(5)

		else:
			print "Wait for the knocker"

def getknockerdetails(knocker_json):
	knocker_json = json.loads(knocker_json)
	try:
		checkforValues = knocker_json['data']['series']
	except KeyError, e:
		return "no data"

	values = knocker_json['data'] ['series'] [0] ['values']
	length = len(values)
	lastUpdatedValue = values[length-1][2]
	return (dict(json.loads(lastUpdatedValue)))


if __name__ == "__main__":
	#check()
	while True:
		check()	

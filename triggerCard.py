import json
import requests
from datetime import datetime

import jsonFormat
import refreshtoken
import quickstart
import sendEmail
import deleteCard

def triggerCardfunction(knockerdetails):
	
	# Extract Knocker's details
	knockername  = knockerdetails['knocking_user_name']
	knockermail  = knockerdetails['knocking_user_email']
	knockerimage = knockerdetails['img_url']
	knockertext  = knockerdetails['text_content']
	knockerphone = '?phone=4129809143'


	# modify anind's card
	# Load content
	display_text_anind = knockername + " knocked your door at " + knockertext
	jsonFormat.payload_anind['content'] ['genericCard'] ['content'] ['displayString'] = display_text_anind
	
	# Load Image URL
	jsonFormat.payload_anind['content'] ['genericCard'] ['image'] ['url'] = knockerimage



	# Load call button
	callurl = jsonFormat.payload_anind['content'] ['genericCard'] ['buttons'] [0] ['tapAction'] ['urls'] [0]
	callurl = callurl+knockerphone
	jsonFormat.payload_anind['content'] ['genericCard'] ['buttons'] [0] ['tapAction'] ['urls'] [0] = callurl

	# Load sms button
	smsurl = jsonFormat.payload_anind['content'] ['genericCard'] ['buttons'] [1] ['tapAction'] ['urls'] [0]
	smsurl = smsurl+knockerphone
	jsonFormat.payload_anind['content'] ['genericCard'] ['buttons'] [1] ['tapAction'] ['urls'] [0] = smsurl

	# Load email card
	# emailurl = jsonFormat.payload_anind['content'] ['genericCard'] ['tapAction'] ['urls'] [0]
	# emailurl = emailurl+'?mail='+knockermail
	jsonFormat.payload_anind['content'] ['genericCard'] ['tapAction'] ['urls'] [0] = knockerimage


	# Load email button
	# mailurl = jsonFormat.payload_anind['content'] ['genericCard'] ['buttons'] [0] ['tapAction'] ['urls'] [0]
	# mailurl = mailurl+'/mobile/4124992400/'+knockermail
	# jsonFormat.payload_anind['content'] ['genericCard'] ['buttons'] [0] ['tapAction'] ['urls'] [0] = mailurl


	# Load details for the kncoker's card
	make = quickstart.get()
	
	if(not(make == "None")):
		free_start = getTime(make[0])
		free_end   = getTime(make[1])
		display_text_knocker = "Anind is free between " + str(free_start) + " and " + str(free_end) + " to meet."
	else: 
		display_text_knocker = " Anind has No free time "
	jsonFormat.payload_knocker['content'] ['genericCard'] ['content'] ['displayString'] = display_text_knocker
	# print display_text_knocker

	# Load email 
	emailKnockerurl = jsonFormat.payload_knocker['content'] ['genericCard'] ['buttons'] [0] ['tapAction'] ['urls'] [0]
	emailKnockerurl = emailKnockerurl+'?mail=cmuiotexpedition@gmail.com'
	jsonFormat.payload_knocker['content'] ['genericCard'] ['buttons'] [0] ['tapAction'] ['urls'] [0] = emailKnockerurl


	flag = 0
	# Trigger card for Room Owner
	callCardTrigger(flag)

	# Trigger Card for the Knocker and Email for non whitelisted
	if(knockername=="Unknown"):
		accessToken = refreshtoken.getaccessToken(flag+1)
		deleteCard.makeDelete(accessToken)
		pass
		# sendEmail.sendemail(knockermail, display_text_knocker)
	else:
		callCardTrigger(flag+1)

def getTime(timestamp):
	# i = datetime.now()
	# k = i.strftime('%Y-%m-%d')
	# return datetime.strptime(timestamp, k+'T%H:%M:%S-05:00')
	return datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:00-05:00')


def  callCardTrigger(flag):
	# Set the HTTP /1.1 POST/GET/DELETE/PUT URL for the NOW card
	url = "https://www.googleapis.com/now/v1/users/me/cards/"
	headers = {'Authorization': 'Bearer ya29',
				'Content-Type': 'application/json'}

	if(requests.get(url,headers=headers).status_code!=200):
		accessToken = refreshtoken.getaccessToken(flag)
		headers['Authorization'] = 'Bearer '+ accessToken
		deleteCard.makeDelete(accessToken)

	#  HTTP GET request to list the available NOW cards of the USER 
	#  In URL specify a cardId for listic the specific card
	getNowCardsList = requests.get(url, headers = headers)
	# print json.dumps(getNowCardsList.json(), indent = 2)
	
	# Payload define for knocker and Anind
	if(flag==0): 
		payload = jsonFormat.payload_anind
	else:
		payload = jsonFormat.payload_knocker

	# url = url+payload['cardId']

	#  HTTP PUT request to update a specific NOW card of the USER 
	#  specify a cardId in the URL and also add ----> "cardId" : "<card's Id>" in the card content file
	#  uncomment the next line when making an update card request
	updateNowCard = requests.post(url,json.dumps(payload),headers = headers)
	print json.dumps(updateNowCard.json(), indent = 2)

	headers['Authorization'] = 'none'
	return

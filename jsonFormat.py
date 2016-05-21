'''------------------------------------------------------------------------------------------------------------------------------------------------------

# The NOW cards contents go here inside the payload dictionary

------------------------------------------------------------------------------------------------------------------------------------------------------'''

payload_anind = {"content": {
  "genericCard": {
   "title": {
    "displayString": "Door Knocker"
   },
   "content": {
    "displayString": "Successful NOW card"
   },
   "tapAction": {
    "urls": [
     "http://cmu.buildingdepot.org/knockerface.png"
    ]
   },
   "logo": {
    "url": "http://cmu.buildingdepot.org/cmu1.png"
   },
   "buttons": [
        {
          "name": "CALL",
          "icon": "call",
          "tapAction": {
            "urls": [
              "android-app://com.example.deeplinkapp/callschema/myapp.com"
            ]
          }
        },
        {
          "name": "SMS",
          "icon": "sms",
          "tapAction": {
            "urls": [
              "android-app://com.example.deeplinkapp/textschema/myapp.com"
            ]
          }
        }
      ],
    "image": {
        "url": "http://cmu.buildingdepot.org/knockerface.png"
      },
  },
  "locales": [
   "en"
  ],
  "justification": {
   "displayString": "Issued to Andrew Dey since his door was knocked"
  }
 }
}

# payload_anind['content'] ['genericCard'] ['content'] ['displayString'] = "Hello"
# print payload_anind
# https://mail.google.com/mail/?view=cm&fs=1&tf=1&to=abcd@gmail.com&su=Hello

# "url": "http://s22.postimg.org/unc61tizl/KNOCKERIMAGE.jpg"


payload_knocker = {"content": {
  "genericCard": {
   "title": {
    "displayString": "Door Knocker"
   },
   "content": {
    "displayString": "<CARD CONTENT>"
   },
   "tapAction": {
    "urls": [
     "http://google.com/"
    ]
   },
   "logo": {
    "url": "http://cmu.buildingdepot.org/cmu1.png"
   },
   "buttons": [
        {
          "name": "send an email",
          "icon": "sms",
          "tapAction": {
            "urls": [
              "android-app://com.example.deeplinkapp/mailschema/myapp.com"
            ]
          }
        }
      ],
  },
  "locales": [
   "en"
  ],
  "justification": {
   "displayString": "Issued since you knocked Andrew's door"
  }
 }
}

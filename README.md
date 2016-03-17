# Leveraging Edge-Analytics in IoT

*Knocking demo using the Giotto Stack.*

---
This is an open source application built on top of the GIoTTO stack to showcase how an IoT app can leverage the stack functionality to offer advanced features and complex interactions between multiple IoT entities. It also demonstrates how Edge Analytics reduces the end-to-end time required for IoT scenarios. The schematic diagram of the application is shown in Figure 1. 

![Schemaic diagram of the knocking app.](./architecture.jpg)

# Required Devices
+ [TI sensor tag] (http://www.ti.com/tool/cc2541dk-sensor)
+ [Raspberry PI] (https://www.raspberrypi.org/blog/raspberry-pi-3-on-sale/)
+ IP camera
+ Internet connection

# How does it work?
The [knocking.conf] (./knocking.conf) file holds the configurations required for the demo:
+ camera_ip, the IoT camera IP in IPv4 format 0.0.0.0
+ BD_domain, url for buildingdepot
+ base_url, service url @ buildingdepot
+ res, checing resosultion, how frequent to check on the sensor data
+ knockingSensor_uuid, where knocking sensor posts time-series data
+ postSensor_uuid, where google cards information are posted


# Generating Google Now cards
Currently, the Google Now API is not avialable for public. You need to [whitelist your email with Google](https://support.google.com/a/answer/60751?hl=en) to be ble to access their Now API. Then, you need to create an account with Google developer if you don't have one already. Once you register, you will receive a client id and a client secret tokens. Those go into client_id and client_secret parementers in the [client_secret.json file](./client_secret.json). You will need to request and access token and replace any access_token instance in the files: [makeCard.py](./makeCard.py). To get an access token, you just need to put your credentials in [refreshtoken.py](./refreshtoken.py) file.

# Licensing
Unless otherwise stated, the source code and trained Torch and Python
model files are copyright Carnegie Mellon University and licensed
under the [Apache 2.0 License](./LICENSE).
Portions from the following third party sources have
been modified and are included in this repository.
These portions are noted in the source files and are
copyright their respective authors with
the licenses listed.

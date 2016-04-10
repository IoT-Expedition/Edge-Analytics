import json

class giottoSetting:
    def __init__(self, settingFilePath="./giottoSetting.json"):
        self.setting = json.loads(open(settingFilePath,'r').read())

    def get(self, settingName):
        return self.setting[settingName]

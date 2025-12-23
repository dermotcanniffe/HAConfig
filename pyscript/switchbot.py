import json
import time
import hashlib
import hmac
import base64
import uuid
import requests
import pprint
import hass

# Declare empty header dictionary
apiHeader = {}
# open token
token = 'e1872082fe30c96ca2ad418ee55da9d77fb60b4667ff13e24c704521e1c8ce3e254d761a2debbe42cab45e5cf524dd7c' # copy and paste from the SwitchBot app V6.14 or later
# secret key
secret = '4b880cf82d5002fd50618c2d2f0be991' # copy and paste from the SwitchBot app V6.14 or later
nonce = uuid.uuid4()
t = int(round(time.time() * 1000))
string_to_sign = '{}{}{}'.format(token, t, nonce)

string_to_sign = bytes(string_to_sign, 'utf-8')
secret = bytes(secret, 'utf-8')

sign = base64.b64encode(hmac.new(secret, msg=string_to_sign, digestmod=hashlib.sha256).digest())
print ('Authorization: {}'.format(token))
print ('t: {}'.format(t))
print ('sign: {}'.format(str(sign, 'utf-8')))
print ('nonce: {}'.format(nonce))

#Build api header JSON
apiHeader['Authorization']=token
apiHeader['Content-Type']='application/json'
apiHeader['charset']='utf8'
apiHeader['t']=str(t)
apiHeader['sign']=str(sign, 'utf-8')
apiHeader['nonce']=str(nonce)

def getDevices():
    url = "https://api.switch-bot.com/v1.0/devices"
    response = requests.get(url, headers=apiHeader)
    #print(response.text)
    return response.text

def switchOnBot(deviceId):
    url = "https://api.switch-bot.com/v1.0/devices/"+deviceId+"/commands"
    payload = {"command": "turnOn"}
    response = requests.post(url, headers=apiHeader, json=payload)
    #print(response.text)
    return response.text

DeviceList = json.loads(getDevices())
#pprint.pprint(DeviceList, compact=True)
SwitchOn = json.loads(switchOnBot('F2EA2D0C0AA7'))
#pprint.pprint(SwitchOn, compact=True)
if hass.states.set("input_boolean.videolightonoff", "off"):
    hass.states.set("input_boolean.videolightonoff", "on")
if hass.states.set("input_boolean.videolightonoff", "off"):
    hass.states.set("input_boolean.videolightonoff", "on")



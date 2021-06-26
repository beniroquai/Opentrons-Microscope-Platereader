 io.imread( image_filename )#!/usr/bin/env python
# coding: utf-8

# In[20]:


import requests 
import json
import matplotlib.pyplot as plt

# In[22]:

print("Turning on the light..")
# check the state of the light on the light
headers = {'opentrons-version': '*'}
path = 'http://21.3.2.11:31950/robot/lights'
x = requests.get(path, headers=headers)

# turn on the light
headers = {'content-type': 'application/json',
           'opentrons-version': '*'}
payload = {"on": "true"}
x = requests.post(path, data = json.dumps(payload), headers=headers)

print(x.content)


#%% get picture


path='http://21.3.2.11:31950/camera/picture'
headers = {'content-type': 'image/jpg',
           'opentrons-version': '*'}
payload = {"on": "false"}
r = requests.post(path, data = json.dumps(payload), headers=headers)

import shutil
filepath = 'tmp.jpg'
if r.status_code == 200:
    with open(filepath, 'wb') as f:
        for chunk in r:
            f.write(chunk)
plt.imshow(plt.imread(filepath))



#%% homing the pipette
headers = {'content-type': 'application/json',
           'opentrons-version': '*'}
path = 'http://21.3.2.11:31950/robot/home'
payload = {
"target": "pipette",
"mount": "right"
}
x = requests.post(path, data = json.dumps(payload), headers=headers)

print(x.content)

#%% homing the robot
headers = {'content-type': 'application/json',
           'opentrons-version': '*'}
path = 'http://21.3.2.11:31950/robot/home'
payload = {
"target": "robot",
"mount": "right"
}
x = requests.post(path, data = json.dumps(payload), headers=headers)

print(x.content)

#%% Setting protocol to live mode
path = 'http://21.3.2.11:31950/sessions'
payload = {    "data": {
        "sessionType": "liveProtocol"
    } }

x = requests.post(path, data = json.dumps(payload), headers=headers)
session_id = json.loads(x.__dict__['_content'].decode("utf-8").replace("'", '"'))['data']['id']
print(session_id)

#%% Aspirate

path = 'http://21.3.2.11:31950/sessions/'+str(session_id)+'/commands/execute'
payload = {
    "data": {
        "command": "equipment.loadPipette",
        "data": {
            "pipetteName": "p300_single",
            "mount": "right"
        }
    }
}

x = requests.post(path, data = json.dumps(payload), headers=headers)
print(x.content)

#%%
POST /sessions/:sessionId/commands/execute
{
    "data": {
        "command": "equipment.loadLabware",
        "data": {
            "loadName": "opentrons_96_tiprack_300ul",
            "version": 1,
            "namespace": "opentrons",
            "location": { "slot": 5 }
        }
    }
}

Those responses will come back with a `result.pipetteId` and a `result.labwareId`, respectively, which you can use in future commands, like:
POST /sessions/:sessionId/commands/execute
{
    "data": {
        "command": "pipette.pickUpTip",
        "data": {
            "pipetteId": "b1c58fa0-7fea-43c7-b6da-f23525f8f66f",
            "labwareId": "a3d31c93-aeb5-45f5-8503-5a6993e925aa",
            "wellName": "A1"
        }
    }
}

#%% aspirate
headers = {'content-type': 'application/json',
           'opentrons-version': '*'}
path = 'http://21.3.2.11:31950/robot/home'
payload = {
"target": "robot",
"mount": "right"
}
x = requests.post(path, data = json.dumps(payload), headers=headers)

print(x.content)



        'name': command_types.ASPIRATE,
        'payload': {
            'instrument': instrument,
            'volume': volume,
            'location': location,
            'rate': rate,
            'text': text
        }
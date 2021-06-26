#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr  5 18:53:45 2021

@author: bene
"""
import requests
import json

host = 'http://127.0.0.1'
port = 8000
base_uri = f"{host}:{port}"


def get_json(path, payload=None):
    """Perform an HTTP GET request and return the JSON response"""
    if not path.startswith("http"):
        path = base_uri + path
    if payload is not None:
        r = requests.get(path, payload)
    else:
        r = requests.get(path)
        
    r.raise_for_status()
    return r.json()

def post_json(path, payload={}, wait_on_task="auto"):
    """Make an HTTP POST request and return the JSON response"""
    if not path.startswith("http"):
        path = base_uri + path
    r = requests.post(path, json=payload)
    r.raise_for_status()
    r = r.json()
    if wait_on_task == "auto":
        wait_on_task = is_a_task(r)
    if wait_on_task:
        return poll_task(r)
    else:
        return r


#%% HOMING
def protocol_home():
    # do homing of the robot
    path = '/hardware/home'
    return_message = get_json(path)
    print(return_message)

protocol_home()

#%% PIPETTE
def add_pipette(name='p300_single', position='right'):
    payload = {
        "name": "p300_single", 
        "position": 'right'
    }
    path = '/hardware/pipette/add'
    
    x = post_json(path, payload, wait_on_task=False)
    
    return x


return_message = add_pipette(name='p300_single', position='right')


#%% HOME PIPETTE

#%% ADD LABWARE

#%% GET TIP 

#%% ASPIRATE 

#%% DISPENSE

#%% BLOW OUT

#%% MOVE TO


'''
curl -X 'GET' 'http://127.0.0.1:31950/robot/lights'   -H 'accept: application/json'
  '''
  
'''
curl -X 'GET' \
  'http://127.0.0.1:8000/pizzas' \
  -H 'accept: application/json'
  '''
  
headers = {'content-type': 'application/json'}
url = 'http://127.0.0.1:31950/robot/lights'
x = requests.get(path, headers=headers)


headers = {'content-type': 'application/json'}
payload = {"on": 1}
x = requests.post(path, data = payload, headers=headers)
print(x.content)




#%% 
endpoint = '/pizzas' #{'/pizzas': None}
payload = {}
path = url+endpoint
x = requests.get(path, data = payload)

print(x.text)

#%%
data = {
    "name": "string", 
    "toppings": [
    "string"
  ]
}
myobj = {'/pizzas': data}
x = requests.post(url, data = myobj)
print(x.text)

post_json


curl -X 'POST' \
  'http://127.0.0.1:8000/pizzas' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "name": "string",
  "toppings": [
    "string"
  ]
}'
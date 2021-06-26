# Import FastAPI
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

import uvicorn

# organize the imports
import opentrons.execute
import opentrons.simulate
from opentrons import types 


# Connect to the opentrons robot
protocol = opentrons.simulate.get_protocol_api('2.9')

# Initialize the app
app = FastAPI()

@app.get('/hardware/home')
async def home():
    print("Homing the robot")
    protocol.home()
    #TODO: Need a state for "home already?"
    return {"Message" : "Homing the robot"}


class Pipette(BaseModel):
    name: str
    position: str


# add pipette
pipettes = []
#pipette_to_add = Pipette(name='p300_single',position='left')
@app.post('/hardware/pipette/add')
async def pipette_add(pipette_to_add: Pipette):
    try:
        pipette = protocol.load_instrument(pipette_to_add.name, pipette_to_add.position)
        pipettes.append()
        print("Adding pipette: " + pipette.requested_as)
        return_message = "Added pipette."
    except RuntimeError as e:
        print(str(e))
        return_message = str(e)
        
    return return_message

@app.get('/hardware/pipette/list')
async def pipette_list():
    for i_pipette in range(len(pipettes)):
        print(pipettes[i_pipette])



pipette = protocol.load_instrument('p300_single', 'right')
pipette_8 = protocol.load_instrument('p300_multi', 'left')

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8888)

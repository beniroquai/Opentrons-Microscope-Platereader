# Import FastAPI
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

db = [
	{
		'id': 0,
		'name': 'Neapolitan Pizza',
		'toppings': ['Mozzarella cheese', 'Tomatoes', 'Basil']
	},
	{
		'id': 1,
		'name': 'Chicago/Deep-Dish Pizza',
		'toppings': ['Cheese', 'Tomatoes', 'pepperoni', 'Onions', 'Mushrooms']
	},
]

# Initialize the app
app = FastAPI()

# GET operation at route '/'
@app.get('/')
async def index():
	return {"greeting" : "Welcome to Paul's Pizza!"}

# get all pizzas
@app.get('/pizzas')
async def get_pizzas():
	return db

# get a pizza by id
@app.get('/pizzas/{pizza_id}')
async def get_pizzas(pizza_id):
	for pizza in db:
		if(pizza['id'] == int(pizza_id)):
			return pizza
	return {"error": "Pizza not found with id:: " + pizza_id}

# pizza data model
class Pizza(BaseModel):
  name: str
  toppings: List[str]

# add a new pizza
@app.post('/pizzas')
async def post_pizza(pizza: Pizza):
	# convert to dictionary
	new_pizza = pizza.dict()
	# add a new id
	new_pizza['id'] = db[-1]['id'] + 1
	# add to list
	print(new_pizza)
	db.append(new_pizza)
	return new_pizza
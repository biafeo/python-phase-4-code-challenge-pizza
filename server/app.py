#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response, jsonify
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)



@app.route("/")
def index():
    return "<h1>Code challenge</h1>"


class Restaurants(Resource):
    
    def get(self):
        restaurants = [restaurant.to_dict() for restaurant in Restaurant.query.all()]
        return make_response(jsonify(restaurants), 200)
    
api.add_resource(Restaurants, '/restaurants')



class RestaurantByID(Resource):
    def get(self, id):
        restaurant = Restaurant.query.filter_by(id=id).first()
        
        if restaurant is None:
            return make_response(jsonify(error="Restaurant not found"), 404, {'Content-Type': 'application/json'})
        else:
            restaurant_dict = restaurant.to_dict_with_pizzas()
            return make_response(jsonify(restaurant_dict), 200)
        
    def delete(self, id):
        restaurant = Restaurant.query.filter(Restaurant.id == id).first()
        if restaurant is None:
            return make_response(jsonify(error="Restaurant not found"), 404, {'Content-Type': 'application/json'})
        else:
            db.session.delete(restaurant)
            db.session.commit()
            
        response = make_response('', 204)
        
        return response 
    
api.add_resource(RestaurantByID, "/restaurants/<int:id>")



class Pizzas(Resource):
    def get(self):
        pizzas = [pizza.to_dict() for pizza in Pizza.query.all()]
        return make_response(jsonify(pizzas),200)
api.add_resource(Pizzas, '/pizzas')


class RestaurantPizzasClass(Resource):
    def post(self):
       
        try:
            new_restaurant_pizza = RestaurantPizza(
                price=request.get_json()["price"],
                pizza_id=request.get_json()["pizza_id"],
                restaurant_id=request.get_json()["restaurant_id"],
            )
            db.session.add(new_restaurant_pizza)
            db.session.commit()

            return make_response(new_restaurant_pizza.to_dict(), 201)
        except ValueError:
            return make_response({"errors": ["validation errors"]}, 400)




api.add_resource(RestaurantPizzasClass, "/restaurant_pizzas")

if __name__ == "__main__":
    app.run(port=5555, debug=True)

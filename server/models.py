from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData, Column, Integer, String, ForeignKey
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

metadata = MetaData(
    naming_convention={
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    }
)

db = SQLAlchemy(metadata=metadata)


class Restaurant(db.Model, SerializerMixin):
    __tablename__ = "restaurants"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    address = Column(String)

    restaurant_pizzas = db.relationship(
        'RestaurantPizza', back_populates='restaurant', cascade='all, delete-orphan'
    )

    pizzas = association_proxy('restaurant_pizzas', 'pizza',
                              creator=lambda pizza_obj: RestaurantPizza(pizza=pizza_obj))
    serialize_rules = ("-restaurant_pizzas.restaurants",)
    
    def to_dict(self):
        return{
            'id':self.id,
            'name':self.name,
            'address':self.address
        }
        
    def to_dict_with_pizzas(self):
        return {
            'id': self.id,
            'name': self.name,
            'address': self.address,
            'restaurant_pizzas': [rp.to_dict() for rp in self.restaurant_pizzas]
        }
    
    def __repr__(self):
        return f"<Restaurant {self.name}>"


class Pizza(db.Model, SerializerMixin):
    __tablename__ = "pizzas"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    ingredients = Column(String)
    restaurant_pizzas = db.relationship(
        'RestaurantPizza', back_populates='pizza', cascade='all, delete-orphan'
    )

    restaurants = association_proxy('restaurant_pizzas', 'restaurant',
                                    creator=lambda restaurant_obj: RestaurantPizza(restaurant=restaurant_obj))
    serialize_rules = ('-restaurant_pizzas.pizza',)
    def to_dict(self):
        return {
            'id': self.id,
            'name':self.name,
            'ingredients': self.ingredients
        }
    
    
    def __repr__(self):
        return f"<Pizza {self.name}, {self.ingredients}>"


class RestaurantPizza(db.Model, SerializerMixin):
    __tablename__ = "restaurant_pizzas"

    id = Column(Integer, primary_key=True)
    price = Column(Integer, nullable=False)
    pizza_id = Column(Integer, ForeignKey('pizzas.id'))
    restaurant_id = Column(Integer, ForeignKey('restaurants.id'))

    pizza = db.relationship('Pizza', back_populates='restaurant_pizzas')
    restaurant = db.relationship('Restaurant', back_populates='restaurant_pizzas')

    serialize_rules = ('-pizza.restaurant_pizzas', '-restaurant.restaurant_pizzas',)

    @validates('price')
    def validate_price(self, key, price):
        if price < 1:
            raise ValueError("price need to be over $1")
        elif price > 30:
            raise ValueError("select a price less than $30")
        return price

    def __repr__(self):
        return f"<RestaurantPizza ${self.price}>"
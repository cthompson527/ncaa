from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from restaurant_database_setup import Restaurant, Base, MenuItem

engine = create_engine('sqlite:///restaurantmenu.db')

Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

restaurant1 = Restaurant(name='Urban Burger')
session.add(restaurant1)
session.commit()

menuItem1 = MenuItem(name = "French Fries", description = "with garlic and parmesan", price = "$2.99", course = "Appetizer", restaurant = restaurant1)
session.add(menuItem1)
session.commit()

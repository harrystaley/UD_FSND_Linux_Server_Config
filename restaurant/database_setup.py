""" This sets up the restaurant database """
import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()
# END BEGINNING CONFIG CODE
# place class defs between this and the end config code


class User(Base):
    """ Class defines the table for the restraunts in the database """
    # defines the name of the table
    __tablename__ = 'user'
    # mapper variables for each of the atributes of a restraunt
    name = Column(String(80), nullable=False)
    email = Column(String(80), nullable=False)
    picture = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)


class Restaurant(Base):
    """ Class defines the table for the restraunts in the database """
    # defines the name of the table
    __tablename__ = 'restaurant'
    # defines relationships with other tables
    user = relationship(User)

    # mapper variables for each of the atributes of a restraunt
    name = Column(String(80), nullable=False)
    address = Column(String(80), nullable=False)
    city = Column(String(80), nullable=False)
    state = Column(String(2), nullable=False)
    zip_code = Column(String(5), nullable=False)
    phone = Column(String(12), nullable=False)
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))

    @property
    def serialize(self):
        return {
            'name': self.name,
            'id': self.id
        }


class MenuItem(Base):
    """
    This class defines the table for the items that will be on the menu.
    """
    # defines the name of the table
    __tablename__ = 'menu_item'
    # defines relationships with other tables
    restaurant = relationship(Restaurant)
    user = relationship(User)

    # mapper variables for each of the atributes of a menu item
    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    course = Column(String(250))
    picture_url = Column(String(250))
    alt_text = Column(String(250))
    description = Column(String(250))
    price = Column(String(8))
    restaurant_id = Column(Integer, ForeignKey('restaurant.id'))
    user_id = Column(Integer, ForeignKey('user.id'))

    @property
    def serialize(self):
        return {
            'name': self.name,
            'description': self.description,
            'id': self.id,
            'price': self.price,
            'course': self.course,
            'picture_url': self.picture_url,
            'alt_text': self.alt_text,
            'alt_text': self.alt_text
        }


# END CONFIG CODE
engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.create_all(engine)

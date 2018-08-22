import os
import sys
import enum
import logging
from sqlalchemy import Column, ForeignKey, Integer, String, JSON, Enum, update
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, validates, sessionmaker
from sqlalchemy import create_engine
# Local import
from FB_barcode_util import create_product_barcode, fill_digits, LENGTH_ID_BC
from FB_logging import logging_handler

# Logging utilities
logging.basicConfig(format='[%(module)s][%(levelname)s][%(funcName)s]%(asctime)s %(message)s')
db_api_logger = logging.Logger('dba_logger')
db_api_logger.setLevel(logging.INFO)
db_api_logger.addHandler(logging_handler)

def set_logger_level(p_level):
    db_api_logger.setLevel(p_level)

# Enum corresponding to wp order status
class Order_status_enum(enum.Enum):
    pending = 'pending payement' 
    completed = 'completed'
    on_hold = 'on hold'
    processing = 'processing'
    cancelled = 'cancelled'
    refunded = 'refunded'
    failed = 'failed'

# Internal status for the boards
class Board_status_enum(enum.Enum):
    pending = 'pending' 
    waiting_machine = 'waiting machine'
    processing = 'processing'
    waiting_ship = 'waiting ship'
    completed = 'completed'    

Base = declarative_base()
engine = create_engine('mysql://root:12.36EI/ml4@localhost:3306/fingered_works')
Base.metadata.create_all(engine)
Base.metadata.bind = engine
DBSession = sessionmaker()
DBSession.bind = engine
session = DBSession()

example_board_json = {
    "width": 600,
    "height": 200,
    "depth": 50,
    "hole_height": 20,
    "holes": [
        {"type": "x_hole", "x_position": 20, "y_position": 32, "depth": 20, "length" : 80, "angle" : 0, "hole_list" : []},
        {"type": "x_hole", "x_position": 110, "y_position": 32, "depth": 20, "length" : 24, "angle" : 0, "hole_list" : []},
        {"type": "x_hole", "x_position": 144, "y_position": 32, "depth": 20, "length" : 50, "angle" : 0, "hole_list" : []},
        {"type": "x_hole", "x_position": 202, "y_position": 32, "depth": 20, "length" : 140, "angle" : 0, "hole_list" : []},
        {"type": "x_hole", "x_position": 351, "y_position": 32, "depth": 20, "length" : 50, "angle" : 0, "hole_list" : []},
        {"type": "x_hole", "x_position": 411, "y_position": 32, "depth": 20, "length" : 24, "angle" : 0, "hole_list" : []},
        {"type": "x_hole", "x_position": 445, "y_position": 32, "depth": 20, "length" : 80, "angle" : 0, "hole_list" : []},
        {"type": "x_hole", "x_position": 20, "y_position": 64, "depth": 30, "length" : 80, "angle" : 0, "hole_list" : []},
        {"type": "x_hole", "x_position": 110, "y_position": 64, "depth": 30, "length" : 24, "angle" : 0, "hole_list" : []},
        {"type": "x_hole", "x_position": 144, "y_position": 64, "depth": 30, "length" : 50, "angle" : 0, "hole_list" : []},
        {"type": "x_hole", "x_position": 202, "y_position": 64, "depth": 30, "length" : 140, "angle" : 0, "hole_list" : []},
        {"type": "x_hole", "x_position": 351, "y_position": 64, "depth": 30, "length" : 50, "angle" : 0, "hole_list" : []},
        {"type": "x_hole", "x_position": 411, "y_position": 64, "depth": 30, "length" : 24, "angle" : 0, "hole_list" : []},
        {"type": "x_hole", "x_position": 445, "y_position": 64, "depth": 30, "length" : 80, "angle" : 0, "hole_list" : []},
        {"type": "x_hole", "x_position": 20, "y_position": 96, "depth": 40, "length" : 80, "angle" : 0, "hole_list" : []},
        {"type": "x_hole", "x_position": 110, "y_position": 96, "depth": 40, "length" : 24, "angle" : 0, "hole_list" : []},
        {"type": "x_hole", "x_position": 144, "y_position": 96, "depth": 40, "length" : 50, "angle" : 0, "hole_list" : []},
        {"type": "x_hole", "x_position": 202, "y_position": 96, "depth": 40, "length" : 140, "angle" : 0, "hole_list" : []},
        {"type": "x_hole", "x_position": 351, "y_position": 96, "depth": 40, "length" : 50, "angle" : 0, "hole_list" : []},
        {"type": "x_hole", "x_position": 411, "y_position": 96, "depth": 40, "length" : 24, "angle" : 0, "hole_list" : []},
        {"type": "x_hole", "x_position": 445, "y_position": 96, "depth": 40, "length" : 80, "angle" : 0, "hole_list" : []},  
    ]
}

def get_engine():
    return engine

def get_session():
    return session

def add_new_user(p_firstname, p_lastname, p_email):
    new_user = User(firstname=p_firstname, lastname = p_lastname, email=p_email)
    session.add(new_user)
    return new_user

def add_new_address(p_country, p_street, p_house_number,
                    p_city, p_postal_code):
    new_address = Address(country=p_country, street=p_street,
                          house_number = p_house_number, city = p_city,
                          postal_code = p_postal_code)
    session.add(new_address)
    return new_address

def add_new_board(p_width, p_height, p_depth, p_holes, p_barcode, p_status):
    new_board = Board(holes = p_holes, width = p_width,
                      height = p_height, depth = p_depth,
                      barcode = p_barcode, status = p_status)
    return new_board

def add_new_order(p_wc_id, p_status, p_board, p_address, p_user):
    new_order = Order(wc_id = p_wc_id, status = p_status,
                      boards = p_board, address = p_address,
                      user = p_user)
    session.add(new_order)
    return new_order

def is_wc_order_in_db(p_wc_id):
    if session.query(Order).filter(Order.wc_id == p_wc_id).all():
        return True
    return False

def commit_changes():
    session.commit()

def add_order_to_db(p_order):
    # Create new user
    firstname = p_order["shipping"]["first_name"]
    lastname = p_order["shipping"]["last_name"]
    email = p_order["billing"]["email"]
    user = add_new_user(firstname, lastname, email)
    # Create new address
    address = p_order["shipping"]["address_1"] + " " + p_order["shipping"]["address_2"]
    house_number = [int(s) for s in address.split() if s.isdigit()]
    if len(house_number) > 1:
        return 0
    address = ''.join([i for i in address if not i.isdigit()])
    postal_code = p_order["shipping"]["postcode"]
    country = p_order["shipping"]["country"]
    city = p_order["shipping"]["city"]
    address = add_new_address(country, address, house_number[0], city, postal_code)
    # Create new board
    width = int(example_board_json["width"])
    height = int(example_board_json["height"])
    depth = int(example_board_json["depth"])
    holes = example_board_json["holes"]
    product_barcode = create_product_barcode(0, width, height, depth)
    board_status = "pending"
    board = add_new_board(width, height, depth, holes, product_barcode, board_status)
    # Update the barcode after the creation of the board item since it needs the id of the board
    session.query().\
       filter(Board.id == board.id).\
       update({"barcode": update_barcode_from_id(product_barcode, board.id)})
    # Create new order
    order_id = int(p_order["id"])
    order_status = p_order["status"]
    add_new_order(order_id, order_status, [board], address, user)
    # Commit changes
    commit_changes()
    db_api_logger.info('New order added with id %d', order_id)

def add_board_to_queue():
    pass

def update_board_status(p_board_id, p_new_status):
    db_api_logger.info("Updating board %d status to %s", p_board_id, p_new_status)
    session.query(Board).filter(Board.id==p_board_id).\
        update({"status":p_new_status})
    commit_changes()
        
def update_barcode_from_id(p_barcode, p_id):
    id_4digits = fill_digits(int(p_id), 0, LENGTH_ID_BC)
    return (p_barcode[0] + id_4digits + p_barcode[5:])

def read_order():
    return session.query(Order).filter(Order.status == Order_status_enum.completed).first()

def get_pending_board():
    return session.query(Board).filter(Board.status == Board_status_enum.pending).first()

def find_board_from_barcode(p_barcode):
    return session.query(Board).filter(Board.barcode == p_barcode).first()

def refresh_session():
    session.expire_all()

class Address(Base):
    __tablename__ = 'address'
    id = Column(Integer, primary_key=True)
    country = Column(String(20), nullable=False)
    street = Column(String(200), nullable=False)
    house_number = Column(Integer)
    city = Column(String(50), nullable=False)
    postal_code = Column(Integer)


class User(Base):
    __tablename__ = 'user'
    # Each user has an ID
    id = Column(Integer, primary_key=True)
    firstname = Column(String(200), nullable=False)
    lastname = Column(String(200), nullable=False)
    email = Column(String(100))

    @validates('email')
    def validate_email(self, key, address):
        assert '@' in address
        return address


class Order(Base):
    __tablename__ = 'order'
    id = Column(Integer, primary_key=True)
    wc_id = Column(Integer)
    status = Column(Enum(Order_status_enum))
    boards = relationship("Board", back_populates="order")
    address_id = Column(Integer, ForeignKey('address.id'))
    address = relationship(Address)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

class Board(Base):
    __tablename__ = 'board'
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('order.id'))
    order = relationship("Order", back_populates="boards")
    holes = Column(JSON)
    width = Column(Integer)
    height = Column(Integer)
    depth = Column(Integer)
    barcode = Column(String(13))
    status = Column(Enum(Board_status_enum))

def create_example_db():
    Base.metadata.create_all(engine)
    na = add_new_address('France', 'Au sein mouelleu', 10, 'Vergeture', 4555)
    nb = add_new_board(600, 200, 50, {}, 200010602050, 'pending')
    nb2 = add_new_board(600, 200, 50, {}, 200020602050, 'pending')
    nu = add_new_user('Pierre', 'Marie', 's@s.be')
    no = add_new_order(1, Order_status_enum.completed, [nb, nb2], na, nu)
    na2 = add_new_address('Belgium', 'La bite fantastique', 10, 'Au pré des dames', 1000)
    nu2 = add_new_user('Jean', 'Jean', 'jj@s.be')
    no2 = add_new_order(2, Order_status_enum.completed, [nb, nb2], na2, nu2)
    commit_changes()

if __name__ == "__main__":
    create_example_db()
    if(is_wc_order_in_db(2)):
        board = session.query(Board).filter(Board.id == 1).first()
        print('order already in db')
        print(board.barcode)
    else:
        print('order not found in db')
    

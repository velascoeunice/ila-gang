import pymongo
from flask import session

myclient = pymongo.MongoClient("mongodb://localhost:27017/")

products_db = myclient["products"]

order_management_db = myclient["order_management"]


def get_product(code):
    products_coll = products_db["products"]

    product = products_coll.find_one({"code":code}, {"_id":0})

    return product


def get_products():
    product_list = []

    products_coll = products_db["products"]

    for p in products_coll.find({}, {"_id":0}):
        product_list.append(p)

    return product_list


def get_branch(code):
    products_coll = products_db["branches"]

    branches = products_coll.find_one({"code":code})

    return branches[code]

def get_branches():
    branches_list = []

    products_coll = products_db["branches"]

    for product in products_coll.find({}):
        branches_list.append(product)

    return branches_list


def get_user(username):
    customers_coll = order_management_db['customers']
    user=customers_coll.find_one({"username":username})
    return user

def change_pass(username, newpassword):
    order_management_db['customers'].update({"username":username}, {"$set":{"password":newpassword}})
    return True


def get_orders():
    order_list = []

    orders_coll = order_management_db['orders']

    for p in orders_coll.find({"username": session["user"]["username"]}):
        order_list.append(p)

    return order_list

def create_order(order):
    orders_coll = order_management_db['orders']
    orders_coll.insert(order)

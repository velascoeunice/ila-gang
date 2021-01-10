from flask import Flask,redirect
from flask import render_template
from flask import request
from flask import session
from bson.json_util import loads, dumps
from flask import make_response
from flask import flash
import database as db
import authentication
import logging
import ordermanagement as om
import datetime



app = Flask(__name__)

# Set the secret key to some random bytes.
# Keep this really secret!
app.secret_key = b's@g@d@c0ff33!'


logging.basicConfig(level=logging.DEBUG)
app.logger.setLevel(logging.INFO)


@app.route('/')
def index():
    return render_template('index.html', page="Index")

@app.route('/products')
def products():
    product_list = db.get_products()
    return render_template('products.html', page="Products", product_list=product_list)

@app.route('/productdetails')
def productdetails():
    code = request.args.get('code', '')
    product = db.get_product(int(code))
    return render_template('productdetails.html', code=code, product=product)

@app.route('/branches')
def branches():
    branch_list = db.get_branches()
    return render_template('branches.html', page="Branches", branch_list=branch_list)

@app.route('/branchdetails')
def branchdetails():
    code = request.args.get('code', '')
    branch = db.get_branch(code)
    return render_template('branchdetails.html', code=code, branch=branch)

@app.route('/aboutus')
def aboutus():
    return render_template('aboutus.html', page="About Us")

@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')

@app.route('/auth', methods = ['POST'])
def auth():
    username = request.form.get('username')
    password = request.form.get('password')

    is_successful, user = authentication.login(username, password)
    app.logger.info('%s', is_successful)
    if(is_successful):
        session["user"] = user

        return redirect('/')
    else:
        flash("Invalid username or password. Try again.")
        return redirect('/login')


@app.route('/logout')
def logout():
    session.pop("user",None)
    session.pop("cart",None)
    return redirect('/')


@app.route('/addtocart')
def addtocart():
    code = request.args.get('code', '')
    product = db.get_product(int(code))
    item=dict()
    # A click to add a product translates to a
    # quantity of 1 for now

    item["code"] = code
    item["qty"] = 1
    item["name"] = product["name"]
    item["subtotal"] = product["price"]*item["qty"]

    if(session.get("cart") is None):
        session["cart"]={}

    cart = session["cart"]
    cart[code]=item
    session["cart"]=cart
    return redirect('/cart')

@app.route('/cart')
def cart():
    return render_template('cart.html')

@app.route('/formsubmission', methods = ['POST'])
def form_submission():

    code = request.form.getlist("code")
    qty = request.form.getlist("qty")

    cart = session["cart"]

    for i in range(len(code)):
        product = db.get_product(int(code[i]))
        cart[code[i]]["qty"] = int(qty[i])
        cart[code[i]]["subtotal"] = int(qty[i]) * product["price"]

    session["cart"]=cart

    return redirect('/cart')

@app.route('/deleteitem')
def delete_item():
    code = request.args.get('code', '')
    cart = session["cart"]
    cart.pop(code, None)
    session["cart"]=cart

    return redirect('/cart')

@app.route('/checkout')
def checkout():
    # clear cart in session memory upon checkout
    # check if the user has previously checkedout
    om.create_order_from_cart()
    session.pop("cart",None)
    return redirect('/ordercomplete')

@app.route('/ordercomplete')
def ordercomplete():
    return render_template('ordercomplete.html')

@app.route('/pastorders')
def pastorders():
    orders = db.get_orders()
    order_list = []
    for item in orders:
        for order in item['details']:
            order_list.append(order)

    return render_template('pastorders.html', page="Past Orders", orders = order_list)

@app.route('/changepassword')
def changepassrender():
    return render_template('changepass.html')

@app.route('/changepass', methods = ['POST'])
def changepasspost():
    oldpassword = request.form.get('oldpass')
    newpassword = request.form.get('newpass')
    confirmpassword = request.form.get('confirmpass')

    is_successful, is_correct_oldpass, is_same_newpasses = authentication.change_password_verification(oldpassword, newpassword, confirmpassword)
    app.logger.info('%s', is_successful)
    if(is_successful):
        db.change_pass(session['user']['username'], newpassword)
        return redirect('/changepassword')
    else:
        if not is_correct_oldpass:
            flash("Old password is not correct.")
        if not is_same_newpasses:
            flash("Passwords do not match.")

        return redirect('/changepassword')

@app.route('/api/products',methods=['GET'])
def api_get_products():
    resp = make_response( dumps(db.get_products()) )
    resp.mimetype = 'application/json'
    return resp

@app.route('/api/products/<int:code>',methods=['GET'])
def api_get_product(code):
    resp = make_response(dumps(db.get_product(code)))
    resp.mimetype = 'application/json'
    return resp

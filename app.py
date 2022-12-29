from hack import app, create_db, db
from flask import render_template, redirect, abort, url_for, flash
from flask_login import current_user, login_user, logout_user, login_required
from hack.forms import LoginForm, RegForm
from hack.models import User, Product
from werkzeug.security import generate_password_hash, check_password_hash

# create_db(app)

@app.route('/')
def home():
    # for i in range(9):
    #     new_prod = Product(name=f'Sneaker {i+1}', category='Shoes and sneakers',image='/static/products/sneaker.png', price=100)
    #     db.session.add(new_prod)
    #     db.session.commit()
    products = Product.query.all()
    return render_template('index.html', products=products)

@app.route('/reg', methods=['GET', 'POST'])
def reg():
    form = RegForm()
    mess=''
    if form.validate_on_submit():
        email = form.email.data
        username = form.username.data
        password = form.password.data
        user = User.query.filter_by(email=email).first()
        if user:
            mess = 'Account already exists'
        else:
            new_user = User(email=email, username=username, password=generate_password_hash(password))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for('home'))
    if current_user.is_authenticated:
        return abort(404)
    return render_template('reg.html', form=form, mess=mess)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    mess=''
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = User.query.filter_by(email=email).first()
        if not user:
            mess = 'Email not found'
        else:
            if check_password_hash(user.password, password):
                login_user(user, remember=True)
                return redirect(url_for('home'))
            else:
                mess = 'Incorrect password'
    if current_user.is_authenticated:
        return abort(404)
    return render_template('login.html', mess=mess, form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/buy/<id>')
@login_required
def buy(id):
    product = Product.query.filter_by(id=id).first()
    if product:
        current_user.credits -= product.price
        db.session.add(current_user)
        db.session.commit()
        flash('Item purchased successfully.')
    return redirect(url_for('home'))

@app.route('/addtocart/<id>')
@login_required
def addtocart(id):
    product = Product.query.filter_by(id=id).first()
    if product:
        current_user.products.append(product)
        db.session.add(current_user)
        db.session.commit()
        flash('Product added to cart successfully.')
    return redirect(url_for('home'))

@app.route('/remove/<id>')
@login_required
def remove(id):
    product = Product.query.filter_by(id=id).first()
    if product:
        current_user.products.remove(product)
        db.session.add(current_user)
        db.session.commit()
    return redirect(url_for('cart'))

@app.route('/cart')
@login_required
def cart():
    return render_template('cart.html')

if __name__ == '__main__':
    app.run(debug=True)


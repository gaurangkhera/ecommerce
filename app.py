from hack import app, create_db, db, UPLOAD_FOLDER
from flask import render_template, redirect, abort, url_for, flash, request
from flask_login import current_user, login_user, logout_user, login_required
from hack.forms import LoginForm, RegForm, CreditForm, ProfileForm, ReviewForm
from hack.models import User, Product, Review
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import uuid as uuid
import os

# create_db(app)


@app.route('/')
def home():
    # for i in range(9):
    #     new_prod = Product(name=f'Sneaker {i+1}', category='Shoes and sneakers',image='/static/products/sneaker.png', price=i*10)
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
            new_user = User(username=username, email=email, password=generate_password_hash(password))
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
        if current_user.credits > 0:
            if product.price  < current_user.credits:
                current_user.credits -= product.price
                db.session.add(current_user)
                db.session.commit()
                flash('Item purchased successfully.')
            else:
                return redirect(url_for('get_credits'))
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
    total = 0
    for entry in current_user.products:
        total += entry.price
    return render_template('cart.html', total=total)
    
@app.route('/get_credits', methods=['GET', 'POST'])
@login_required
def get_credits():
    form = CreditForm()
    mess=''
    if form.validate_on_submit():
        current_user.credits += form.credits.data
        db.session.add(current_user)
        db.session.commit()
        mess = 'credit balance updated.'
    return render_template('get_credits.html', form=form, mess=mess)

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm()
    if form.validate_on_submit():
        if form.username.data != "":
            current_user.username = form.username.data
        if form.email.data != "":
            current_user.email = form.email.data
        if form.password.data != "":
            current_user.password = generate_password_hash(form.password.data)
        if form.image.data is not None:
                file = form.image.data
                file_name = secure_filename(file.filename)
                pic_name = str(uuid.uuid1()) + '_' + file_name
                current_user.image = pic_name
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], pic_name))
        db.session.add(current_user)
        db.session.commit()
    return render_template('profile.html', form=form)

@app.route('/review/<id>', methods=['GET', 'POST'])
@login_required
def review_product(id):
    form = ReviewForm()
    product = Product.query.filter_by(id=id).first()
    if form.validate_on_submit():
        new_review = Review(text=form.review.data, product_id=product.id)
        db.session.add(new_review)
        db.session.commit()
    return render_template('review.html', form=form, product=product)
        
if __name__ == '__main__':
    app.run(debug=True)
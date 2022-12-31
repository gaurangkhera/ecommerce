from hack import app, create_db, db
from flask import render_template, redirect, abort, url_for, flash, request
from flask_login import current_user, login_user, logout_user, login_required
from hack.forms import LoginForm, RegForm, CreditForm, ProfileForm, ReviewForm, EditProductForm
from hack.models import User, Product, Review, Order
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import uuid as uuid
import os

app.config['UPLOAD_FOLDER'] = 'hack/static/'
create_db(app)


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
            if current_user.is_authenticated:
                return redirect('admin')
            else:
                login_user(new_user)
                return redirect(url_for('home'))
    if current_user.is_authenticated and current_user.username != 'XINO':
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
    if current_user.is_authenticated and current_user.username != 'XINO':
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
                order = Order(image=product.image, name=product.name, qty=1, price=product.price, user_id=current_user.id)
                order.products.append(product)
                db.session.add(current_user)
                db.session.add(order)
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
        product.qty +=1 
        current_user.products.append(product)
        db.session.add(current_user)
        db.session.add(product)
        db.session.commit()
        flash('Product added to cart successfully.')
    return redirect(url_for('home'))

@app.route('/remove/<id>')
@login_required
def remove(id):
    product = Product.query.filter_by(id=id).first()
    if product:
        current_user.products.remove(product)
        product.qty = 0
        db.session.add(current_user)
        db.session.add(product)
        db.session.commit()
    return redirect(url_for('cart'))

@app.route('/cart')
@login_required
def cart():
    total = 0
    for entry in current_user.products:
        total += entry.price * entry.qty
    return render_template('cart.html', total=total)
    
@app.route('/buycart')
@login_required
def buy_cart():
        total = 0
        for entry in current_user.products:
            total += entry.price * entry.qty
            order = Order(image=entry.image, name=entry.name, price=entry.price, qty=entry.qty, user_id=current_user.id)
            order.products.append(entry)
            entry.qty = 0
            db.session.add(order)
            db.session.commit()
        if current_user.credits > total:
            current_user.credits -= total
            current_user.products = []
            db.session.add(current_user)
            db.session.commit()
            return redirect(url_for('thank_you'))   
        flash('You do not have enough credits.', 'error')
        return redirect(url_for('cart'))
        
        

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
        new_review = Review(text=form.review.data, product_id=product.id, reviewer=current_user.username)
        db.session.add(new_review)
        db.session.commit()
    return render_template('review.html', form=form, product=product)

@app.route('/thankyou')
@login_required
def thank_you():
    return render_template('thankyou.html')

@app.route('/admin')
@login_required
def admin():
    if current_user.username == 'XINO':
        products = Product.query.all()
        users = User.query.all()
        reviews = Review.query.all()
        return render_template('admin.html', users=users, products=products, reviews=reviews)
    abort(403)

@app.route('/delete_review/<productid>/<reviewid>')
@login_required
def delete_review(productid, reviewid):
    product = Product.query.filter_by(id=int(productid)).first()
    review =  Review.query.filter_by(id=int(reviewid)).first()
    if current_user.username == 'XINO' or current_user.username == review.reviewer:
        if product and review:
            db.session.delete(review)
            db.session.commit()
            return redirect(url_for('home'))
    return abort(403)

@app.route('/delete_user/<id>')
@login_required
def delete_user(id):
    if current_user.username == 'XINO':
        user = User.query.filter_by(id=id).first()
        db.session.delete(user)
        db.session.commit() 
        return redirect(url_for('admin'))
    return abort(403)

@app.route('/edit_user/<id>', methods=['GET', 'POST'])
@login_required
def edit_user(id):
    if current_user.username == 'XINO':
        form = ProfileForm()
        user = User.query.filter_by(id=id).first()
        if form.validate_on_submit():
            if form.username.data != "":
                user.username = form.username.data
            if form.email.data != "":
                user.email = form.email.data
            if form.password.data != "":
                user.password = generate_password_hash(form.password.data)
            if form.image.data is not None:
                file = form.image.data
                file_name = secure_filename(file.filename)
                print(file_name)
                pic_name = str(uuid.uuid1()) + '_' + file_name
                user.image = pic_name
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], pic_name))
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('admin'))
        return render_template('admin_profile.html', form=form, user=user)
    return abort(403)

@app.route('/edit_product/<id>', methods=['GET', 'POST'])
@login_required
def edit_product(id):
        if current_user.username == 'XINO':
            form = EditProductForm()
            product = Product.query.filter_by(id=id).first()
            if form.validate_on_submit():
                if form.name.data:
                    product.name = form.name.data
                if form.price.data:
                    product.price = form.price.data
                if form.category.data:
                    product.category = form.category.data
                if form.image.data:
                    image = form.image.data
                    image_name = secure_filename(image.filename)
                    pic_name = str(uuid.uuid1()) + '_' + image_name
                    product.image = pic_name
                    image.save(os.path.join(app.config['UPLOAD_FOLDER'], pic_name))
                db.session.add(product)
                db.session.commit()
            return render_template('edit_product.html', form=form, product=product)
        return abort(403)

@app.route('/add_product', methods=['GET', 'POST'])
@login_required
def add_product():
    if current_user.username == 'XINO':
        form = EditProductForm()
        if form.validate_on_submit:
            if form.image.data:
                image = form.image.data
                image_name = secure_filename(image.filename)
                pic_name = str(uuid.uuid1()) + '_' + image_name
                new_product = Product(image=pic_name, name=form.name.data, price=form.price.data, category=form.category.data)
                image.save(os.path.join(app.config['UPLOAD_FOLDER'], pic_name))
                db.session.add(new_product)
                db.session.commit()
                return redirect(url_for('admin'))
        return render_template('add_product.html', form=form)
    return abort(403)

@app.route('/delete_product/<id>')
@login_required
def delete_product(id):
    if current_user.username == 'XINO':
        product = Product.query.filter_by(id=id).first()
        db.session.delete(product)
        db.session.commit()
        return redirect(url_for('admin'))
    return abort(403)

@app.route('/orders')
@login_required
def orders():
    return render_template('order.html')
            

if __name__ == '__main__':
    app.run(debug=True)

from flask import render_template, url_for, redirect, flash, request
from market import app, db
from market.models import Item, User
from market.forms import RegisterForm, LoginForm
from flask_login import login_user, logout_user, current_user, login_required

@app.route('/')
@app.route('/home')
def home_page():
    return render_template('home.html')

@app.route('/about')
def about_page():
    return render_template('about.html')

@app.route('/contact')
def contact_page():
    return render_template('contact.html')

@app.route('/market')
def market_page():
    items = Item.query.all()
    return render_template('market.html', items=items)

@app.route('/register', methods=['GET', 'POST'])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        user_to_create = User(username=form.username.data,
                              email_address=form.email_address.data,
                              password=form.password1.data)
        db.session.add(user_to_create)
        db.session.commit()
        return redirect(url_for('market_page'))
    if form.errors != {}:
        for err_msg in form.errors.values():
            flash(f'There was a problem creating a User {err_msg}', category='danger')
    
    return render_template('register.html', form=form)

@app.route('/login', methods=['POST', 'GET'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
            attempted_user = User.query.filter_by(username=form.username.data).first()
            if attempted_user and attempted_user.check_password(form.password.data):
                login_user(attempted_user)
                flash(f'Success! You are logged in as: {attempted_user.username}', category='success')
                return redirect(url_for('market_page'))
            else:
                flash('Username and password are not match! Please try again', category='danger')        
    if form.errors != {}:
        for err_msg in form.errors.values():
            flash(f'There was a problem logging in {err_msg}', category='danger')
    return render_template('login.html', form=form)

@app.route('/logout')
def logout_page():
    logout_user()
    flash('You have been logged out successfully!', category='info')
    return redirect(url_for('home_page'))

@app.route('/cart')
@login_required
def cart_page():
    # Calculate total price of items in cart
    total_price = sum(item.price for item in current_user.items)
    tax = total_price * 0.1
    total_with_tax = total_price + tax
    remaining_budget = current_user.budget - total_with_tax
    
    return render_template('cart.html', 
                         total_price=total_price, 
                         tax=tax, 
                         total_with_tax=total_with_tax,
                         remaining_budget=remaining_budget)

@app.route('/add_to_cart/<int:item_id>', methods=['POST'])
@login_required
def add_to_cart(item_id):
    item_to_add = Item.query.get_or_404(item_id)
    if item_to_add.stock > 0 and item_to_add.owner != current_user.id:
        # Check if user already owns this item
        if item_to_add not in current_user.items:
            item_to_add.owner = current_user.id
            item_to_add.stock -= 1
            db.session.commit()
            flash(f'{item_to_add.name} has been added to your cart!', category='success')
        else:
            flash(f'{item_to_add.name} is already in your cart!', category='info')
    elif item_to_add.stock == 0:
        flash(f'{item_to_add.name} is out of stock!', category='danger')
    else:
        flash('Cannot add your own item to cart!', category='danger')
    
    return redirect(url_for('market_page'))

@app.route('/remove_from_cart/<int:item_id>', methods=['POST'])
@login_required
def remove_from_cart(item_id):
    item_to_remove = Item.query.get_or_404(item_id)
    if item_to_remove in current_user.items:
        item_to_remove.owner = None
        item_to_remove.stock += 1
        db.session.commit()
        flash(f'{item_to_remove.name} has been removed from your cart!', category='info')
    else:
        flash('Item not found in your cart!', category='danger')
    
    return redirect(url_for('cart_page'))

@app.route('/checkout', methods=['POST'])
@login_required
def checkout():
    total_cost = sum(item.price for item in current_user.items)

    if current_user.budget >= total_cost:
        current_user.budget -= int(total_cost)
        db.session.commit()
        flash(f'Congratulations! You have successfully purchased {len(current_user.items)} items for ${total_cost:.2f}!', category='success')
        return redirect(url_for('market_page'))
    else:
        flash('Insufficient budget to complete this purchase!', category='danger')
        return redirect(url_for('cart_page'))
from flask import render_template
from market import app
from market.models import Item

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

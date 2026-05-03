from flask import Flask, render_template, request, session, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, RadioField, SelectField
from wtforms.validators import DataRequired, Length, Optional, Regexp, ValidationError, Email
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import re

app = Flask(__name__)
app.secret_key = "A_Very_Good_Key"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.sqlite3'
bootstrap = Bootstrap(app)
db = SQLAlchemy(app)

class OrderForm(FlaskForm):
    order = IntegerField('Order Amount: ', validators = [DataRequired()])
    favourite = RadioField(choices=[('yes', 'Favourite Item')], validators=[Optional()])
    submit = SubmitField('Add to Basket')

class SortForm(FlaskForm):
    sort = SelectField('Sort By: ', choices=[('price_high', 'Most Expensive First'),
                                             ('price_low', 'Cheapest First'),
                                             ('name_asc','A-Z'),
                                             ('name_desc','Z-A')])

    submit = SubmitField('Sort')

class CheckoutForm(FlaskForm):
    name     = StringField('Full name',       validators=[DataRequired()])
    email    = StringField('Email address',   validators=[DataRequired(), Email()])
    phone    = StringField('Phone number',    validators=[DataRequired()])
    address1 = StringField('Address line 1',  validators=[DataRequired()])
    address2 = StringField('Address line 2')
    city     = StringField('City',            validators=[DataRequired()])
    postcode = StringField('Postcode',        validators=[DataRequired()])

    card_number = StringField('Card number', validators=[
        DataRequired(),
        Regexp(r'^\d{4} \d{4} \d{4} \d{4}$|^\d{16}$', message='Card number must be 16 digits.')
    ])

    expiry = StringField('Expiry date', validators=[
        DataRequired(),
        Regexp(r'^(0[1-9]|1[0-2])\/\d{2}$', message='Expiry must be in MM/YY format.')
    ])

    cvv = StringField('CVV', validators=[
        DataRequired(),
        Regexp(r'^\d{3}$', message='CVV must be 3 digits.')
    ])

    submit = SubmitField('Place order')

    def validate_expiry(self, field):
        match = re.match(r'^(0[1-9]|1[0-2])\/(\d{2})$', field.data)
        if match:
            exp_month = int(match.group(1))
            exp_year  = int(match.group(2)) + 2000
            now = datetime.now()
            if (exp_year, exp_month) < (now.year, now.month):
                raise ValidationError('Your card has expired.')

class Stock(db.Model):
    __tablename__ = 'stock'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)
    price = db.Column(db.Integer)
    description = db.Column(db.String)
    image = db.Column(db.String)

class Users(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, unique=True)
    passhash = db.Column(db.String)

class Orders(db.Model):
    __tablename__ = 'orders'
    orderId = db.Column(db.Integer, primary_key=True)
    fishId = db.Column(db.Integer, db.ForeignKey('stock.id'))
    quantity = db.Column(db.Integer)
    userId = db.Column(db.Integer, db.ForeignKey('users.id'))

@app.route('/', methods=['GET','POST'])
def galleryPage():
    sorting = SortForm()
    order = OrderForm()

    if 'basket' not in session:
        session['basket'] = {}

    # Handle the order form submission
    if request.method == 'POST' and 'fish_id' in request.form:
        fish_id = request.form.get('fish_id')  # from the hidden input
        fish = db.session.get(Stock, int(fish_id))

        if fish and order.validate_on_submit():
            quantity = order.order.data
            key = str(fish_id)

            if key in session['basket']:
                session['basket'][key]['quantity'] += quantity
            else:
                session['basket'][key] = {
                    'name': fish.name,
                    'price': fish.price,
                    'quantity': quantity
                }

            session.modified = True
            return redirect(url_for('galleryPage'))

    # Handle sorting (separate POST, no fish_id present)
    if sorting.is_submitted() and 'fish_id' not in request.form:
        sortby = sorting.data['sort']
        sort_options = {
            "name_asc": Stock.name.asc(),
            "name_desc": Stock.name.desc(),
            "price_low": Stock.price.asc(),
            "price_high": Stock.price.desc()
        }
        query = Stock.query.order_by(sort_options.get(sortby)).all()
        return render_template('index.html', stock=query, sort=sorting, order=order)

    return render_template('index.html', stock=Stock.query.all(), sort=sorting, order=order)

@app.route('/description/<int:fishId>')
def getDescription(fishId):
    fish = db.session.get(Stock, fishId)
    if fish is None:
        return "Not found", 404
    return fish.description

@app.route('/stock/<int:fishId>', methods=['GET','POST'])
def singleProductPage(fishId):
    form = OrderForm()
    fish = db.session.get(Stock, fishId)

    if fish is None:
        return "Fish not found", 404

    if request.method == 'POST':
        if form.validate_on_submit():
            quantity = form.order.data

            # Initialise basket
            if 'basket' not in session:
                session['basket'] = {}

            key = str(fishId)

            if key in session['basket']:
                # Fish already in basket — add to existing quantity
                session['basket'][key]['quantity'] += quantity
            else:
                # New item — store name, price, and quantity
                session['basket'][key] = {
                    'name': fish.name,
                    'price': fish.price,
                    'quantity': quantity
                }

            session.modified = True

            return render_template('itemdetail.html', fish=fish, form=form)
        else:
            print(form.errors)

    return render_template('itemdetail.html', fish=fish, form=form)

@app.route('/basket', methods=['GET','POST'])
def basketPage():
    basket = session.get('basket', {})

    total = sum(
        item['price'] * item['quantity']
        for item in basket.values()
    )

    return render_template('basket.html', basket=basket, total=total)

@app.route('/basket/remove/<fishId>', methods=['POST'])
def removeFromBasket(fishId):
    basket = session.get('basket', {})
    if fishId in basket:
        del basket[fishId]
        session['basket'] = basket
    return redirect(url_for('basketPage'))

@app.route('/checkout', methods=['GET', 'POST'])
def checkoutPage():
    form = CheckoutForm()
    basket = session.get('basket', {})
    total = sum(item['price'] * item['quantity'] for item in basket.values())

    if form.validate_on_submit():
        name  = form.name.data
        email = form.email.data

        session['basket'] = {}

        return render_template('orderconfirmed.html',
                               name=name,
                               email=email,
                               basket=basket,
                               total=total)

    return render_template('checkout.html', form=form, total=total)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
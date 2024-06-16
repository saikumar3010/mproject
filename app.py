import logging
from flask import Flask, request, render_template, url_for, redirect,flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length
from flask_bcrypt import Bcrypt
import pandas as pd
import pickle
import requests
from bs4 import BeautifulSoup
import os
from sklearn.inspection import permutation_importance
from flask_migrate import Migrate
from wtforms.validators import DataRequired, Length, EqualTo

app = Flask(__name__)
app.config['SECRET_KEY'] = 'thisisasecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login_user'  # Default to user login; modify as needed



@login_manager.user_loader
def load_user(user_id):
    # Try to load the user from the User table
    user = User.query.get(int(user_id))
    if user:
        return user

    # If no User is found, try to load from the Farmer table
    farmer = Farmer.query.get(int(user_id))
    return farmer


from werkzeug.security import generate_password_hash, check_password_hash



class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Farmer(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    kisaan_id = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class FarmerLoginForm(FlaskForm):
    kisaan_id = StringField('KisaanID', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class UserLoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8, max=35),
        EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Confirm Password')
    submit = SubmitField('Register')
class FarmerRegistrationForm(FlaskForm):
    kisaan_id = StringField('Kisaan ID', validators=[DataRequired(), Length(min=4, max=20)])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8),
        EqualTo('confirm_password', message='Passwords must match.')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired()])
    submit = SubmitField('Register')
from flask_login import login_user, logout_user

# Login routes for user
from flask_login import login_user, logout_user

@app.route('/login/user', methods=['GET', 'POST'])
def user_login():
    form = UserLoginForm()  # Instantiate the form
    if form.validate_on_submit():  # Checks if the form has been submitted and is valid
        username = form.username.data
        password = form.password.data   
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('request_loanid'))
        flash('Invalid username or password')
    return render_template('login.html', form=form)  # Pass the form to the template


# Registration route for user
@app.route('/register/user', methods=['GET', 'POST'])
def register_user():
    form = RegistrationForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        existing_user = User.query.filter_by(username=username).first()
        if existing_user is None:
            user = User(username=username)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login_user'))
        else:
            flash('Username already exists.', 'error')
    return render_template('register.html', form=form)


# Login routes for farmer
@app.route('/login/farmer', methods=['GET', 'POST'])
def login_farmer():
    form = FarmerLoginForm()
    if form.validate_on_submit():
        kisaan_id = form.kisaan_id.data
        password = form.password.data
        farmer = Farmer.query.filter_by(kisaan_id=kisaan_id).first()
        if farmer and farmer.check_password(password):
            login_user(farmer)
            return redirect(url_for('farmer_dashboard'))
        flash('Invalid Kisaan ID or password')
    return render_template('farmerlogin.html', form=form)


# Registration route for farmer
@app.route('/register/farmer', methods=['GET', 'POST'])
def register_farmer():
    form = FarmerRegistrationForm()
    if form.validate_on_submit():  # Processes the form only if it is submitted
        kisaan_id = form.kisaan_id.data
        password = form.password.data
        existing_farmer = Farmer.query.filter_by(kisaan_id=kisaan_id).first()
        if existing_farmer is None:
            farmer = Farmer(kisaan_id=kisaan_id)
            farmer.set_password(password)  # Setting the hashed password
            db.session.add(farmer)
            db.session.commit()
            flash('Your account has been created! You can now log in.', 'success')
            return redirect(url_for('login_farmer'))
        else:
            flash('That Kisaan ID is already taken. Please choose a different one.', 'error')
    return render_template('farmerregister.html', form=form)




# Add your routes for farmer login and registration here

@app.route('/farmer_dashboard', methods=['GET', 'POST'])

def farmer_dashboard():
    return render_template('farmerinput.html')

model = pickle.load(open('YieldPrice.pkl', 'rb'))
model1 = pickle.load(open('gradient_boosting_classifier.pkl', 'rb'))







@app.route('/')
def home():
    return render_template('home.html')




@app.route('/request_loanid', methods=['GET', 'POST'])

def request_loanid():
    if request.method == 'POST':
        loanid = request.form.get('loanid')
        if loanid:
            data = pd.read_csv('customer_data.csv')
            row = data[data['Loan ID'].astype(str) == loanid]
            if not row.empty:
                data_dict = row.iloc[0].to_dict()
                # Log the data retrieved based on loanid
                print(f'Data retrieved for loan ID {loanid}: {data_dict}')
                return render_template('details.html', data=data_dict)
            
            else:
            
                return render_template('details.html', data=None, loanid=loanid)
    return render_template('request_loanid.html')

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    return render_template('details.html')

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))



@app.route('/default_calculator', methods=['GET', 'POST'])
def default_calculator():
    if request.method == 'POST':
        return predict()
    return render_template('defaultcalc.html')

def get_rainfall(district_name):
    url = "https://www.tsdps.telangana.gov.in/districtdata.jsp"
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        rows = soup.find_all('tr')
        for row in rows:
            cells = row.find_all('td')
            if len(cells) > 1 and cells[1].text.strip().lower() == district_name.lower():
                return cells[5].text.strip()
    return 0

def calculate_net_profit(profit):
    brackets = [(300000, 0.00), (300000, 0.10), (300000, 0.15), (300000, 0.20), (float('inf'), 0.30)]
    excess = profit
    tax = 0
    for bracket in brackets:
        if excess > bracket[0]:
            tax += bracket[0] * bracket[1]
            excess -= bracket[0]
        else:
            tax += excess * bracket[1]
            break
    return profit - tax

@app.route('/predict', methods=['POST'])

def predict():
    def get_form_data(key, default=None, cast_type=str):
        """ Safely extract and cast form data """
        value = form_data.get(key, default)
        try:
            return cast_type(value)
        except ValueError:
            flash(f"Invalid format for {key}, using default value.", "warning")
            return default
    form_data = request.form
    crop = get_form_data('crop', '').lower()  # Use parentheses to call .get()
    district = get_form_data('district', '')
    area = get_form_data('area', default=1, cast_type=float)

    rainfall = get_rainfall(district)
    max_temp = get_form_data('matemp', default=0, cast_type=float)
    min_temp = get_form_data('mitemp', default=0, cast_type=float)
    loan_amount = get_form_data('loanamount', default=0, cast_type=float)
    has_existing_loan = get_form_data('hasexistingloan', default='no') == 'yes'
    existing_loan_amount = get_form_data('existingloanamount', default=0, cast_type=float) if has_existing_loan else 0
    interest_rate = get_form_data('interestrate', default=0, cast_type=float) / 100  # Convert percentage for calculations
    tenure = get_form_data('tenure', default=0, cast_type=int)
    family_size = get_form_data('familysize', default=1, cast_type=int)
    year = get_form_data('Year', default=2021, cast_type=int)
    amount_to_be_repaid = loan_amount * (1 + interest_rate * tenure / 12)

    input_data = pd.DataFrame({
        'Crop': [crop],
        'Total Rainfall': [rainfall],
        'Max. Temp': [max_temp],
        'Min Temp': [min_temp],
        'District': [district]
    })
    
    # Prediction is assumed to be yield in kg per acre
    yield_per_acre = model.predict(input_data)[0]
    yield1 = round(yield_per_acre * area, 2)
    output = round(yield_per_acre, 2)
    
    # Prices per kg and cost of cultivation per acre
    prices = {'paddy': 11.45, 'chilli': 155.6, 'maize': 26.56, 'bengal gram': 57.5, 'groundnut': 63.5}
    cultivation_costs = {'paddy': 65338, 'maize': 24463, 'bengal gram': 12996, 'groundnut': 40898, 'chilli': 62672}
    
    # Calculate income and profit
    income_per_acre = output * prices.get(crop, 0)
    total_income = income_per_acre * area
    profit_per_acre = income_per_acre - cultivation_costs.get(crop, 0)
    total_profit = total_income - cultivation_costs.get(crop, 0) * area
    net_profit = calculate_net_profit(total_profit)
    act_profit = net_profit - (existing_loan_amount + amount_to_be_repaid)

    # Prepare data for the ML model
    input_data1 = pd.DataFrame({
        'Loan Amount': [loan_amount],
        'Land Area': [area],
        'Crop': [crop],
        'District': [district],
        'Existing Loan Boolean': [has_existing_loan],
        'Loan Tenure': [tenure],
        'Existing Loan Amount': [existing_loan_amount],
        'Interest Rate': [interest_rate],
        'Amount to be Repaid': [amount_to_be_repaid],
        'Year': [year],
        'expected_yield': [yield1],
        'Profit': [total_profit],
        'family size': [family_size],
        'Net_Profit': [net_profit],
        'Act_Profit': [act_profit]
    })

    # Make prediction
    verdict = model1.predict(input_data1)[0]
    probabilities = model1.predict_proba(input_data1)[0]
    yes_prob = probabilities[1]  # Probability for 'Yes'
    no_prob = probabilities[0]
    importances = model1.named_steps['classifier'].feature_importances_
    feature_names = [name for name in input_data1.columns]
    
    # Combine importances with feature names
    feature_importance_dict = dict(zip(feature_names, importances))
    
    # Sort features by importance
    sorted_features = sorted(feature_importance_dict.items(), key=lambda x: x[1], reverse=True)
    
    # Get top reason for the prediction
    top_reason = sorted_features[0][0]
    reason_text = f"The primary reason for the predicted outcome is the high influence of {top_reason}."
    print(district)
    print(rainfall)
    print(verdict)
    return render_template('output.html',
                           crop=crop.capitalize(),
                           district=district,
                           area=area,
                           rainfall=rainfall,
                           max_temp=max_temp,
                           min_temp=min_temp,
                           loan_amount=loan_amount,
                           total_income=total_income,
                           tenure=tenure,
                           existing_loan_amount=existing_loan_amount,
                           interest_rate=interest_rate * 100,  # Convert back to percentage for display
                           year=year,
                           family_size=family_size,
                           yield1=yield1,
                           total_profit=total_profit,
                           verdict=verdict,
                           net_profit=net_profit,
                           act_profit=act_profit,
                           yes_prob=yes_prob * 100,
                           no_prob=no_prob * 100,
                           prediction_text=f' {verdict} with {probabilities.max():.2f}% confidence',
                           top_reason=reason_text)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)

   
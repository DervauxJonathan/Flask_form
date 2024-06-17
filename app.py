from flask import Flask, render_template, request, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, RadioField, BooleanField, SubmitField
from wtforms.validators import InputRequired, Email
from flask_sqlalchemy import SQLAlchemy
import bleach

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # In production, use a secure key from environment variables
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///formdata.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# Class for the form 

class ContactForm(FlaskForm):
    first_name = StringField('First Name', validators=[InputRequired()])
    last_name = StringField('Last Name', validators=[InputRequired()])
    email = StringField('Email', validators=[InputRequired(), Email()])
    country = SelectField('Country', validators=[InputRequired()], choices=[
        ('', 'Select a country'), ('BE', 'Belgium'), ('DE', 'Germany'),('FR', 'France'), ('UK', 'United Kingdom'), ('CA', 'Canada'), ('US', 'United State')
    ])
    message = TextAreaField('Message', validators=[InputRequired()])
    gender = RadioField('Gender', validators=[InputRequired()], choices=[
        ('M', 'Male'), ('F', 'Female')
    ])
    subject_repair = BooleanField('Repair')
    subject_order = BooleanField('Order')
    subject_others = BooleanField('Others', default=True)
    submit = SubmitField('Submit')


# construct of the database

class FormData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    country = db.Column(db.String(50), nullable=False)
    message = db.Column(db.Text, nullable=False)
    gender = db.Column(db.String(1), nullable=False)
    subjects = db.Column(db.String(200), nullable=False)

with app.app_context():
    db.create_all()

@app.route('/', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    if request.method == 'POST' and form.validate():
        first_name = bleach.clean(form.first_name.data)
        last_name = bleach.clean(form.last_name.data)
        email = bleach.clean(form.email.data)
        country = bleach.clean(form.country.data)
        message = bleach.clean(form.message.data)
        gender = bleach.clean(form.gender.data)
        subjects = []
        if form.subject_repair.data:
            subjects.append('Repair')
        if form.subject_order.data:
            subjects.append('Order')
        if form.subject_others.data:
            subjects.append('Others')
        if not subjects:
            subjects = ['Others']
        subjects_str = ', '.join(subjects)
        
        new_entry = FormData(
            first_name=first_name,
            last_name=last_name,
            email=email,
            country=country,
            message=message,
            gender=gender,
            subjects=subjects_str
        )
        
        db.session.add(new_entry)
        db.session.commit()
        
        flash('Form submitted successfully!', 'success')
        return redirect(url_for('contact'))
    return render_template('contact.html', form=form)

if __name__ == '__main__':
    app.run(debug=True)

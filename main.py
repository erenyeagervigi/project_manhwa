from flask import Flask, render_template
from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests

app = Flask(__name__)

class Addform(FlaskForm):
    title = StringField('Manhwa Title', validators=[DataRequired()])
    done = SubmitField(label='Add')

@app.route("/")
def home():
    return render_template("index.html")

@app.route('/edit')
def edit():
    return 'hello'

if __name__ == "__main__":
    app.run(debug=True)
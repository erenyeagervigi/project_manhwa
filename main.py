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
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///manhwa.db"
app.secret_key = 'eren'
Bootstrap5(app)

class Base(DeclarativeBase):
    pass
db = SQLAlchemy(model_class=Base)
db.init_app(app)

with app.app_context():
    db.create_all()

class Addform(FlaskForm):
    title = StringField('Manhwa Title', validators=[DataRequired()])
    done = SubmitField(label='Add')

@app.route("/")
def home():
    return render_template("index.html")

@app.route('/edit')
def edit():
    return 'hello'

def add_manhwa(name):
    url = "https://graphql.anilist.co"

    query = """
    query ($search: String) {
      Media(search: $search, type: MANGA) {
        id
        title {
          english
        }
        description(asHtml: false)
        startDate {
          year
        }
        coverImage {
          extraLarge
          large
          medium
        }
      }
    }
    """

    variables = {"search": name}

    try:
        response = requests.post(url, json={"query": query, "variables": variables})
        response.raise_for_status()  # check for HTTP errors
        json_data = response.json()

        # If Media is None → not found
        media = json_data.get("data", {}).get("Media")
        if not media:
            return None

        return {
            'title': media['title'] or {"english": name},
            'description': (media['description'] or "No description available.").split("<br>")[0],
            'year': media['startDate']['year'] if media['startDate'] else "Unknown",
            'img_url': media['coverImage']['extraLarge'] if media['coverImage'] else ""
        }

    except Exception as e:
        print("AniList error:", e)
        return None

@app.route('/add', methods = ['GET', 'POST'])
def add():
    add_form = Addform()

    if request.method == 'POST':
        manhwa_title = request.form.get('title')
        print(manhwa_title)
        return render_template('index.html')

    return render_template('add.html', form= add_form)

if __name__ == "__main__":
    app.run(debug=True)
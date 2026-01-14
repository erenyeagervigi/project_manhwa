from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests
import os
from dotenv import load_dotenv

load_dotenv('secrets.env')

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DB_URI")
app.secret_key = os.getenv('secret_key')
Bootstrap5(app)

class Base(DeclarativeBase):
    pass
db = SQLAlchemy(model_class=Base)
db.init_app(app)

class Manhwa(db.Model):
    id:Mapped[int] = mapped_column(Integer,primary_key=True)
    title:Mapped[str] = mapped_column(String,nullable=False, unique=True)
    year:Mapped[int] = mapped_column(Integer,nullable=False)
    description:Mapped[str] = mapped_column(String,nullable=False)
    img_url: Mapped[str] = mapped_column(String,nullable=False)

with app.app_context():
    db.create_all()

class Addform(FlaskForm):
    title = StringField('Manhwa Title', validators=[DataRequired()])
    done = SubmitField(label='Add')

@app.route("/")
def home():
    manhwa = db.session.execute(db.select(Manhwa)).scalars().all()
    return render_template("index.html", manhwa = manhwa)

@app.route('/view', methods = ['POST','GET'])
def view():
    id = request.args.get('id')
    selected_manwha =  db.session.execute(db.select(Manhwa). where(Manhwa.id == id)).scalars().first()
    return render_template('view.html', manhwa = selected_manwha)

@app.route("/about")
def about():
    return render_template('about.html')

@app.route('/delete', methods = ['POST','GET'])
def delete():
        id = request.args.get('id')
        delete_manhwa = db.get_or_404(Manhwa, id)
        db.session.delete(delete_manhwa)
        db.session.commit()
        return redirect(url_for('home'))

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
        manhwa = add_manhwa(manhwa_title)
        if not manhwa:
            return "❌ Manhwa not found. Try again.", 404

        title = manhwa['title'].get('english') or manhwa_title
        description = manhwa['description']
        year = manhwa['year']
        img_url = manhwa['img_url']

        new_manwa = Manhwa(
            title=title,
            description=description,
            year=year,
            img_url=img_url,
        )
        db.session.add(new_manwa)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('add.html', form= add_form)

if __name__ == "__main__":
    app.run(debug=False, host = '0.0.0.0')
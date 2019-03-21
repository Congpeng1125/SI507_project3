#__author__ == "Jackie Cohen (jczetta)"

import os
from flask import Flask, render_template, session, redirect, url_for # tools that will make it easier to build on things
from flask_sqlalchemy import SQLAlchemy # handles database stuff for us - need to pip install flask_sqlalchemy in your virtual env, environment, etc to use this and run this

# Application configurations
app = Flask(__name__)
app.debug = True
app.use_reloader = True
app.config['SECRET_KEY'] = 'hard to guess string for app security adgsdfsadfdflsdfsj'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///./sample_songs.db' # TODO: decide what your new database name will be -- that has to go here
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


# Set up Flask debug stuff
db = SQLAlchemy(app) # For database use
session = db.session # to make queries easy





#########
######### Everything above this line is important/useful setup, not problem-solving.
#########


##### Set up Models #####

# Set up association Table between artists and albums
collections = db.Table('collections',db.Column('Release Date_id',db.Integer, db.ForeignKey('Release_Date.id')),db.Column('Major Genre_id',db.Integer, db.ForeignKey('Major_Genre.id')))

class Release_Date(db.Model):
    __tablename__ = "Release_Date"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    major_genres = db.relationship('Major_Genre',secondary=collections,backref=db.backref('Release_Date',lazy='dynamic'),lazy='dynamic')
    movies = db.relationship('Movie',backref='Release_Date')


class Major_Genre(db.Model):
    __tablename__ = "Major_Genre"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    movies = db.relationship('Movie',backref='Major_Genre')

    def __repr__(self):
        return "{} (ID: {})".format(self.name,self.id)


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64),unique=True) # Only unique title songs can exist in this data model
    Release_Date_id = db.Column(db.Integer, db.ForeignKey("Release_Date.id")) #ok to be null for now
    Major_Genre_id = db.Column(db.Integer, db.ForeignKey("Major_Genre.id")) # ok to be null for now
    genre = db.Column(db.String(64)) # ok to be null
    # keeping genre as atomic element here even though in a more complex database it could be its own table and be referenced here

    def __repr__(self):
        return "{} by {} | {}".format(self.title,self.artist_id, self.genre)


##### Helper functions #####

### For database additions
### Relying on global session variable above existing

def get_or_create_genre(genre_name):
    genre_name = Major_Genre.query.filter_by(name=genre_name).first()
    if genre_name:
        return genre_name
    else:
        genre_name = Major_Genre(name=genre_name)
        session.add(genre_name)
        session.commit()
        return genre_name

def get_or_create_date(release_date):
    release_date = Release_Date.query.filter_by(name=release_date).first()
    if release_date:
        return release_date
    else:
        release_date = Release_Date(name=release_date)
        session.add(release_date)
        session.commit()
        return release_date

##### Set up Controllers (route functions) #####

## Main route
@app.route('/')
def index():
    movies = Movie.query.all()
    num_movies = len(movies)
    return render_template('index.html', num_movies=num_movies)

@app.route('/movie/new/<title>/<genre_name>/<release_date>/')
def new_movie(title, genre, release_date):
    if Movie.query.filter_by(title=title).first(): # if there is a song by that title
        return "That movie already exists! Go back to the main app!</h1>"
    else:
        genre_name = get_or_create_genre(genre_name)
        release_date = get_or_create_date(release_date)
        movie = Movie(title=title, Major_Genre_id=Genre_Name.id,Release_Date_id = Release_Date.id)
        session.add(movie)
        session.commit()
        return "You successfully add a new movie: {} to database! The genre is {}.The release date is {}. You can go to check the UPL to see if it is added successfully.".format(movie.title, Major_Genre.name,Release_Date.name)

@app.route('/all_movies')
def see_all():
    all_movies = [] # Will be be tuple list of title, genre
    movies = Movie.query.all()
    for s in movies:
        genre = Major_Genre.query.filter_by(id=s.Major_Genre_id).first() # get just one artist instance
        date = Release_Date.query.filter_by(id=s.Release_Date_id).first()
        all_movies.append((s.title,genre.name, date.name)) # get list of songs with info to easily access [not the only way to do this]
    return render_template('all_movies.html',all_movies=all_movies) # check out template to see what it's doing with what we're sending!

@app.route('/all_genres')
def see_all_genres():
    genres = Major_Genre.query.all()
    names = []
    for a in genres:
        num_movies = len(Movie.query.filter_by(Major_Genre_id=a.id).all())
        newtup = (a.name,num_movies)
        names.append(newtup) # names will be a list of tuples
    return render_template('all_genres.html',artist_names=names)


if __name__ == '__main__':
    db.create_all() # This will create database in current directory, as set up, if it doesn't exist, but won't overwrite if you restart - so no worries about that
    app.run() # run with this: python main_app.py runserver

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restx import Api, Resource

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///music_app.db'  # Replace with your DB URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

api = Api(app, version='1.0', title='Music App API',
          description='A Swagger-enabled API for the music application.')

# Models based on SQL Statements
class Account(db.Model):
    account_id = db.Column(db.String(24), primary_key=True)
    mail = db.Column(db.String(50), nullable=False, unique=True)
    full_name = db.Column(db.String(50))
    is_subscriber = db.Column(db.Boolean, nullable=False, default=False)
    registration_date = db.Column(db.DateTime, default=db.func.now())
    country = db.Column(db.String(50))
    sex = db.Column(db.String(50))
    language = db.Column(db.String(50), nullable=False)
    birth_date = db.Column(db.Date)
    user_id = db.Column(db.String(24), db.ForeignKey('user.user_id'))


class User(db.Model):
    user_id = db.Column(db.String(24), primary_key=True)
    nickname = db.Column(db.String(50), nullable=False)
    favorite_genre = db.Column(db.String(50))
    user_image = db.Column(db.LargeBinary)


class Follower(db.Model):
    user_id_1 = db.Column(db.String(24), db.ForeignKey('user.user_id'), primary_key=True)
    user_id_2 = db.Column(db.String(24), db.ForeignKey('user.user_id'), primary_key=True)


class Playlist(db.Model):
    playlist_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    playlist_name = db.Column(db.String(50), nullable=False)
    playlist_description = db.Column(db.String(300))
    playlist_image = db.Column(db.LargeBinary)
    creator = db.Column(db.String(24), db.ForeignKey('user.user_id'))


class PlaylistUser(db.Model):
    user = db.Column(db.String(24), db.ForeignKey('user.user_id'), primary_key=True)
    follows = db.Column(db.Integer, db.ForeignKey('playlist.playlist_id'), primary_key=True)


class PlaylistSong(db.Model):
    playlist_id = db.Column(db.Integer, db.ForeignKey('playlist.playlist_id'), primary_key=True)
    song_id = db.Column(db.String(16), db.ForeignKey('song.song_id'), primary_key=True)


class Like(db.Model):
    user_id = db.Column(db.String(24), db.ForeignKey('user.user_id'), primary_key=True)
    song_id = db.Column(db.String(16), db.ForeignKey('song.song_id'), primary_key=True)


class Song(db.Model):
    song_id = db.Column(db.String(16), primary_key=True)
    song_name = db.Column(db.String(50), nullable=False)
    song_time = db.Column(db.Interval, nullable=False)
    song_image = db.Column(db.LargeBinary)
    audio = db.Column(db.LargeBinary)


class Genre(db.Model):
    song_id = db.Column(db.String(16), db.ForeignKey('song.song_id'), primary_key=True)
    genre = db.Column(db.String(50))


class Album(db.Model):
    album_id = db.Column(db.String(24), primary_key=True)
    album_name = db.Column(db.String(50), nullable=False, unique=True)
    about = db.Column(db.String(250))
    album_image = db.Column(db.LargeBinary)


class AlbumInfo(db.Model):
    album_id = db.Column(db.String(16), db.ForeignKey('album.album_id'), primary_key=True)
    song_id = db.Column(db.String(16), db.ForeignKey('song.song_id'), primary_key=True)


class Group(db.Model):
    group_id = db.Column(db.String(16), primary_key=True)
    group_name = db.Column(db.String(50), nullable=False, unique=True)
    number_of_members = db.Column(db.Integer)
    creation_date = db.Column(db.Date)
    group_image = db.Column(db.LargeBinary)


class Artist(db.Model):
    group_id = db.Column(db.String(16), db.ForeignKey('group.group_id'), primary_key=True)
    full_name = db.Column(db.String(50), primary_key=True)
    origin_country = db.Column(db.String(50))
    instruments = db.Column(db.String(50))


class AlbumGroup(db.Model):
    album_id = db.Column(db.String(16), db.ForeignKey('album.album_id'), primary_key=True)
    group_id = db.Column(db.String(16), db.ForeignKey('group.group_id'), primary_key=True)


class History(db.Model):
    user_id = db.Column(db.String(24), db.ForeignKey('user.user_id'), primary_key=True)
    start_time = db.Column(db.DateTime, default=db.func.now(), primary_key=True)
    duration = db.Column(db.Interval)
    song = db.Column(db.String(16), db.ForeignKey('song.song_id'))


# Swagger Resource Example
@api.route('/users')
class UserList(Resource):
    def get(self):
        """Get all users"""
        users = User.query.all()
        return [{'user_id': user.user_id, 'nickname': user.nickname} for user in users]

    def post(self):
        """Create a new user"""
        # Example implementation
        return {"message": "User creation not implemented yet"}, 501


if __name__ == '__main__':
    with app.app_context():  # Ensures the app context is set
        db.create_all()  # Create database tables
    app.run(debug=True)

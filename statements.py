statement_1 = """CREATE TABLE Account(
    account_id CHAR(24) PRIMARY KEY,
    mail VARCHAR(50) NOT NULL UNIQUE,
    full_name VARCHAR(50),
    is_subscriber BOOL NOT NULL DEFAULT 0,
    registiration_date DATETIME DEFAULT GetDate(),
    country VARCHAR(50),
    sex VARCHAR(50),
    language VARCHAR(50) NOT NULL,
    birth_date DATE,
    account_id REFERENCES User (user_id)
)"""

statement_2 = """CREATE TABLE User(
    user_id CHAR(24) PRIMARY KEY,
    nickname VARCHAR(50) NOT NULL,
    favorite_genre VARCHAR(50),
    user_image BLOB, 
)""" 

statement_3 = """CREATE TABLE Fallower(
    user_id_1 CHAR(24) PRIMARY KEY,
    user_id_2 CHAR(24) PRIMARY KEY,
    user_id_1 REFERENCES User (user_id),
    user_id_2 REFERENCES User (user_id),
)"""

statement_4 = """CREATE TABLE Playlist (
    playlist_id INT AUTO_INCREMENT PRIMARY KEY,
    playlist_name VARCHAR(50) NOT NULL,
    playlist_description VARCHAR(300),
    playlist_image BLOB,
    creator CHAR(24),
    creator REFERENCES User (user_id),
)"""

statement_5 = """CREATE TABLE Playlist_User (
    user CHAR(24) PRIMARY KEY,
    fallows INT PRIMARY KEY,
    user REFERENCES User (user_id),
    fallows REFERENCES Playlist (playlist_id),
)"""

statement_6 = """CREATE TABLE Playlist_Song (
    playlist_id INT PRIMARY KEY,
    song_id CHAR(16) PRIMARY KEY,
    playlist_id REFERENCES Playlist (playlist_id),
    song_id REFERENCES Song (song_id),
)"""

statement_7 = """CREATE TABLE Like (
    user_id CHAR(24) PRIMARY KEY,
    song_id CHAR(16) PRIMARY KEY,
    user_id REFERENCES User (user_id),
    song_id REFERENCES Song (song_id),
)"""

statement_8 = """CREATE TABLE Song (
    song_id CHAR(16) PRIMARY KEY,
    song_name VARCHAR(50) NOT NULL,
    song_time INTERVAL NOT NULL,
    song_image BLOB,
    audio BLOB,
)"""

statement_9 = """CREATE TABLE Genre (
    song_id CHAR(16) PRIMARY KEY,
    genre VARCHAR(50),
    song_id REFERENCES Song (song_id),
)"""

statement_10 = """CREATE TABLE Album (
    album_id CHAR(24) PRIMARY KEY,
    album_name VARCHAR(50) NOT NULL UNIQUE,
    about VARCHAR(250),
    album_image BLOB,
)"""

statement_11 = """CREATE TABLE Album_Info (
    album_id CHAR(16) PRIMARY KEY,
    song_id CHAR(16) PRIMARY KEY,
    album_id REFERENCES Album (album_id),
    song_id REFERENCES Song (song_id),
)"""

statement_12 = """CREATE TABLE Group (
    group_id CHAR(16) PRIMARY KEY,
    group_name VARCHAR(50) NOT NULL UNIQUE,
    number_of_members INT,
    creation_date DATE,
    group_image BLOB,
)"""

statement_13 = """CREATE TABLE Artist (
    group_id CHAR(16) PRIMARY KEY,
    full_name VARCHAR(50) PRIMARY KEY,
    origin_country VARCHAR(50),
    instruments VARCHAR(50),
    group_id REFERENCES Group (group_id),
)"""

statement_14 = """CREATE TABLE Album_Group (
    album_id CHAR(16) PRIMARY KEY,
    group_id CHAR(16) PRIMARY KEY,
    album_id REFERENCES Album (album_id),
    group_id REFERENCES Group (group_id)
)"""

statement_15 = """CREATE TABLE History (
    user_id CHAR(24) PRIMARY KEY,
    start_time DATETIME DEFAULT GetDate() PRIMARY KEY,
    duration INTERVAL,
    song CHAR(16), 
    user_id REFERENCES User (user_id),
    song REFERENCES Song (song_id)
)"""


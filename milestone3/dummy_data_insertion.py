import sqlite3
from werkzeug.security import generate_password_hash
import uuid

def insert_dummy_data(DATABASE):
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    # Enable foreign key constraints
    cursor.execute("PRAGMA foreign_keys = ON;")

    try:
        # First, verify there are no duplicate nicknames in our data
        nicknames = [
            'Tunceredits', '345math', 'EFCK', 'Batman', 'Charlie', 
            'mgs6', 'infinityedge', 'franxx', 'rockson', '800kmid',
            'musiclover', 'jazzcat', 'rocknroller', 'beatmaker', 'classicfan',
            'rapperfan', 'livemusic', 'vinyladdict', 'concertgoer', 'producer'
        ]
        if len(nicknames) != len(set(nicknames)):
            raise ValueError("Found duplicate nicknames in dummy data! Each nickname must be unique.")
        
        # Print a message about inserting users
        print("Inserting users...")
        
        # Insert dummy data into the User table - Let the database generate user_ids automatically
        # Using executemany with placeholders for proper SQLite insertion
        user_data = [
            ('Tunceredits', 'Pop', None),
            ('345math', 'Rock', None),
            ('EFCK', 'Jazz', None),
            ('Batman', 'Rock', None),
            ('Charlie', 'Pop', None),
            ('mgs6', 'Jazz', None),
            ('infinityedge', 'Rock', None),
            ('franxx', 'Pop', None),
            ('rockson', 'Jazz', None),
            ('800kmid', 'Rap', None),
            ('musiclover', 'Pop', None),
            ('jazzcat', 'Jazz', None),
            ('rocknroller', 'Rock', None),
            ('beatmaker', 'Hip Hop', None),
            ('classicfan', 'Classical', None),
            ('rapperfan', 'Rap', None),
            ('livemusic', 'Folk', None),
            ('vinyladdict', 'Indie', None),
            ('concertgoer', 'Electronic', None),
            ('producer', 'Pop', None)
        ]
        cursor.executemany(
            "INSERT INTO User (nickname, favorite_genre, user_image) VALUES (?, ?, ?)",
            user_data
        )
        connection.commit()
        
        # Get the generated user_ids to use for Account table
        print("Retrieving generated user IDs...")
        cursor.execute("SELECT user_id, nickname FROM User")
        user_data = cursor.fetchall()
        
        # Create a dictionary to map nicknames to user_ids
        user_id_map = {nickname: user_id for user_id, nickname in user_data}
        
        # Print user_id map for debugging
        print(f"User ID map: {user_id_map}")
        
        # Generate password hashes for users
        print("Inserting accounts...")
        
        # Check for existing emails first
        cursor.execute("SELECT mail FROM Account")
        existing_emails = {row[0] for row in cursor.fetchall()}
        print(f"Found {len(existing_emails)} existing email addresses")
        
        for nickname in user_id_map.keys():
            user_id = user_id_map[nickname]
            # Create a simple password (in a real app, these would be properly secured)
            password = f"password_{nickname}"
            
            # For demonstration only: Let werkzeug handle the salt generation automatically
            # werkzeug.security generate_password_hash already includes salt handling
            password_hash = generate_password_hash(password, method='pbkdf2:sha256')
            
            # Store the salt portion separately for this demo as instructed
            parts = password_hash.split('$')
            salt_string = parts[2]
            
            # Verify email length doesn't exceed 50 characters
            email = f"{nickname.lower()}@example.com"
            if len(email) > 50:
                email = f"{nickname.lower()[:40]}@example.com"  # Truncate if too long
                
            # Skip if email already exists
            if email in existing_emails:
                print(f"Account with email {email} already exists, skipping")
                continue
                
            # Current timestamp for last_login using ISO 8601 format
            last_login = '2024-01-01T12:00:00'
            
            try:
                # Insert into Account table with proper user_id and required fields
                print(f"Inserting account for {nickname} with user_id {user_id}")
                cursor.execute("""
                    INSERT INTO Account (user_id, mail, password_hash, password_salt, full_name, is_subscriber, 
                                       registration_date, country, sex, language, birth_date, last_login) VALUES
                    (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    user_id, 
                    email,
                    password_hash, 
                    salt_string,  # Using direct salt extraction as instructed
                    get_full_name(nickname), 
                    is_subscriber(nickname),
                    '2021-05-01',
                    get_country(nickname),
                    get_sex(nickname),
                    get_language(nickname),
                    get_birth_date(nickname),
                    last_login
                ))
                # Add email to existing_emails to avoid trying to insert it again if another user has the same email
                existing_emails.add(email)
            except sqlite3.Error as e:
                print(f"Error inserting account for {nickname}: {str(e)}")
                # Continue with the next account
        connection.commit()
        
        # Insert follower relationships using the user IDs from the map
        print("Inserting follower relationships...")
        try:
            insert_followers(cursor, user_id_map)
            connection.commit()
        except sqlite3.Error as e:
            print(f"Error inserting follower relationships: {str(e)}")
        
        # Insert playlists with auto-generated IDs
        print("Inserting playlists...")
        try:
            insert_playlists(cursor, user_id_map)
            connection.commit()
        except sqlite3.Error as e:
            print(f"Error inserting playlists: {str(e)}")
        
        # Get playlist IDs for later use
        try:
            print("Retrieving playlist IDs...")
            cursor.execute("SELECT playlist_id, playlist_name FROM Playlist")
            playlist_data = cursor.fetchall()
            playlist_id_map = {name: p_id for p_id, name in playlist_data}
        except sqlite3.Error as e:
            print(f"Error retrieving playlist IDs: {str(e)}")
            playlist_id_map = {}
            
        # Insert songs with auto-generated IDs
        print("Inserting songs...")
        try:
            insert_songs(cursor)
            connection.commit()
        except sqlite3.Error as e:
            print(f"Error inserting songs: {str(e)}")
        
        # Get song IDs for later use
        try:
            print("Retrieving song IDs...")
            cursor.execute("SELECT song_id, song_name FROM Song")
            song_data = cursor.fetchall()
            song_id_map = {name: s_id for s_id, name in song_data}
        except sqlite3.Error as e:
            print(f"Error retrieving song IDs: {str(e)}")
            song_id_map = {}
            
        # Associate playlists with users
        if playlist_id_map and user_id_map:
            print("Inserting playlist-user relationships...")
            try:
                insert_playlist_users(cursor, user_id_map, playlist_id_map)
                connection.commit()
            except sqlite3.Error as e:
                print(f"Error inserting playlist-user relationships: {str(e)}")
        
        # Associate songs with playlists
        if playlist_id_map and song_id_map:
            print("Inserting playlist-song relationships...")
            try:
                insert_playlist_songs(cursor, playlist_id_map, song_id_map)
                connection.commit()
            except sqlite3.Error as e:
                print(f"Error inserting playlist-song relationships: {str(e)}")
            
        # Add user likes
        if user_id_map and song_id_map:
            print("Inserting user likes...")
            try:
                insert_user_likes(cursor, user_id_map, song_id_map)
                connection.commit()
            except sqlite3.Error as e:
                print(f"Error inserting user likes: {str(e)}")
            
        # Add song genres
        if song_id_map:
            print("Inserting genres...")
            try:
                insert_genres(cursor, song_id_map)
                connection.commit()
            except sqlite3.Error as e:
                print(f"Error inserting genres: {str(e)}")
            
        # Add albums
        print("Inserting albums...")
        try:
            insert_albums(cursor)
            connection.commit()
        except sqlite3.Error as e:
            print(f"Error inserting albums: {str(e)}")
            
        # Get album IDs for later use
        try:
            print("Retrieving album IDs...")
            cursor.execute("SELECT album_id, album_name FROM Album")
            album_data = cursor.fetchall()
            album_id_map = {name: a_id for a_id, name in album_data}
        except sqlite3.Error as e:
            print(f"Error retrieving album IDs: {str(e)}")
            album_id_map = {}
        
        # Associate songs with albums
        if album_id_map and song_id_map:
            print("Inserting album info (album-song relationships)...")
            try:
                insert_album_info(cursor, album_id_map, song_id_map)
                connection.commit()
            except sqlite3.Error as e:
                print(f"Error inserting album-song relationships: {str(e)}")
            
        # Add music groups
        print("Inserting music groups...")
        try:
            insert_music_groups(cursor)
            connection.commit()
        except sqlite3.Error as e:
            print(f"Error inserting music groups: {str(e)}")
            
        # Get group IDs for later use
        try:
            print("Retrieving group IDs...")
            cursor.execute("SELECT group_id, group_name FROM MusicGroup")
            group_data = cursor.fetchall()
            group_id_map = {name: g_id for g_id, name in group_data}
        except sqlite3.Error as e:
            print(f"Error retrieving group IDs: {str(e)}")
            group_id_map = {}
            
        # Add artists to groups
        if group_id_map:
            print("Inserting artists...")
            try:
                insert_artists(cursor, group_id_map)
                connection.commit()
            except sqlite3.Error as e:
                print(f"Error inserting artists: {str(e)}")
            
        # Associate albums with groups
        if album_id_map and group_id_map:
            print("Inserting album-group relationships...")
            try:
                insert_album_groups(cursor, album_id_map, group_id_map)
                connection.commit()
            except sqlite3.Error as e:
                print(f"Error inserting album-group relationships: {str(e)}")
            
        # Insert listening history
        if user_id_map and song_id_map:
            print("Inserting listening history...")
            try:
                insert_history(cursor, user_id_map, song_id_map)
                connection.commit()
            except sqlite3.Error as e:
                print(f"Error inserting listening history: {str(e)}")
                
        print("Dummy data insertion completed!")
                
    except Exception as e:
        print(f"Error during dummy data insertion: {str(e)}")
        raise
    finally:
        connection.close()

# Helper functions to get appropriate values for each user
def get_full_name(nickname):
    name_map = {
        'Tunceredits': 'Mahmut Tuncer',
        '345math': 'Pisagor Pisagor',
        'EFCK': 'Efe Can Kirbiyik',
        'Batman': 'Bruce Wayne',
        'Charlie': 'Random Person 3',
        'mgs6': 'Hideo Kojima',
        'infinityedge': 'Miss Fortune',
        'franxx': 'Zero Two',
        'rockson': 'Dost Kayaoğlu',
        '800kmid': 'Fatih Ucubeoğlu',
        'musiclover': 'Alex Johnson',
        'jazzcat': 'Ella Fitzgerald',
        'rocknroller': 'Mick Richards',
        'beatmaker': 'DJ Fresh',
        'classicfan': 'Wolfgang Mozart',
        'rapperfan': 'Marshall Matters',
        'livemusic': 'Woody Guthrie',
        'vinyladdict': 'Ian Curtis',
        'concertgoer': 'David Guetta',
        'producer': 'Rick Rubin'
    }
    return name_map.get(nickname, nickname)

def is_subscriber(nickname):
    # Define subscribers list directly in the function
    subscribers = ['Tunceredits', 'EFCK', 'mgs6', 'infinityedge', 'franxx', 'rockson', 
                   'musiclover', 'jazzcat', 'classicfan', 'rapperfan', 'producer']
    return 1 if nickname in subscribers else 0

def get_country(nickname):
    # Define dictionary mapping nicknames to country values
    country_mapping = {
        'Tunceredits': 'Turkey',
        '345math': 'Greece', 
        'EFCK': 'Turkey',
        'Batman': 'USA',
        'Charlie': 'Canada',
        'mgs6': 'Japan',
        'infinityedge': 'USA',
        'franxx': 'Japan',
        'rockson': 'Turkey',
        '800kmid': 'Turkey',
        'musiclover': 'UK',
        'jazzcat': 'USA',
        'rocknroller': 'UK',
        'beatmaker': 'USA',
        'classicfan': 'Austria',
        'rapperfan': 'USA',
        'livemusic': 'USA',
        'vinyladdict': 'UK',
        'concertgoer': 'France',
        'producer': 'USA'
    }
    return country_mapping.get(nickname, 'Unknown')

def get_sex(nickname):
    # Define dictionary mapping nicknames to sex values
    sex_mapping = {
        'Tunceredits': 'Male',
        '345math': 'Male',
        'EFCK': 'Male',
        'Batman': 'Male',
        'Charlie': 'Female',
        'mgs6': 'Male',
        'infinityedge': 'Female',
        'franxx': 'Female',
        'rockson': 'Male',
        '800kmid': 'Male',
        'musiclover': 'Male',
        'jazzcat': 'Female',
        'rocknroller': 'Male',
        'beatmaker': 'Male',
        'classicfan': 'Male',
        'rapperfan': 'Male',
        'livemusic': 'Male',
        'vinyladdict': 'Male',
        'concertgoer': 'Male',
        'producer': 'Male'
    }
    return sex_mapping.get(nickname, 'Prefer not to say')

def get_language(nickname):
    # Define dictionary mapping nicknames to language values
    language_mapping = {
        'Tunceredits': 'Turkish',
        '345math': 'English',
        'EFCK': 'Turkish',
        'Batman': 'English',
        'Charlie': 'English',
        'mgs6': 'Japanese',
        'infinityedge': 'English',
        'franxx': 'Japanese',
        'rockson': 'Turkish',
        '800kmid': 'Turkish',
        'musiclover': 'English',
        'jazzcat': 'English',
        'rocknroller': 'English',
        'beatmaker': 'English',
        'classicfan': 'German',
        'rapperfan': 'English',
        'livemusic': 'English',
        'vinyladdict': 'English',
        'concertgoer': 'French',
        'producer': 'English'
    }
    return language_mapping.get(nickname, 'English')

def get_birth_date(nickname):
    # Define dictionary mapping nicknames to birth dates
    birth_date_mapping = {
        'Tunceredits': '1961-05-05',
        '345math': '1900-01-01',
        'EFCK': '2001-12-12',
        'Batman': '1939-05-05',
        'Charlie': '1990-01-01',
        'mgs6': '1963-08-24',
        'infinityedge': '1996-02-21',
        'franxx': '2000-02-02',
        'rockson': '1999-01-01',
        '800kmid': '2000-01-01',
        'musiclover': '1985-03-15',
        'jazzcat': '1980-06-12',
        'rocknroller': '1978-11-22',
        'beatmaker': '1992-04-18',
        'classicfan': '1970-01-27',
        'rapperfan': '1995-10-17',
        'livemusic': '1983-07-04',
        'vinyladdict': '1975-09-30',
        'concertgoer': '1988-12-05',
        'producer': '1965-08-10'
    }
    return birth_date_mapping.get(nickname, '2000-01-01')

# Helper functions to insert related data
def insert_followers(cursor, user_id_map):
    # Examples of follower relationships
    follower_pairs = [
        ('Tunceredits', '345math'),
        ('Tunceredits', 'EFCK'),
        ('345math', 'Tunceredits'),
        ('Batman', 'Tunceredits'),
        ('Charlie', 'Tunceredits'),
        ('mgs6', 'Tunceredits'),
        ('infinityedge', 'Tunceredits'),
        ('franxx', 'Tunceredits'),
        ('rockson', 'Tunceredits'),
        ('800kmid', 'Tunceredits'),
        ('musiclover', 'rockson'),
        ('jazzcat', 'EFCK'),
        ('rocknroller', 'Batman'),
        ('beatmaker', 'infinityedge'),
        ('classicfan', 'Charlie'),
        ('rapperfan', '800kmid'),
        ('livemusic', 'mgs6'),
        ('vinyladdict', 'franxx'),
        ('concertgoer', '345math'),
        ('producer', 'Tunceredits'),
        ('Tunceredits', 'musiclover'),
        ('345math', 'jazzcat'),
        ('EFCK', 'rocknroller'),
        ('Batman', 'beatmaker'),
        ('Charlie', 'classicfan'),
        ('mgs6', 'rapperfan'),
        ('infinityedge', 'livemusic'),
        ('franxx', 'vinyladdict'),
        ('rockson', 'concertgoer'),
        ('800kmid', 'producer')
    ]
    
    # Prepare data for executemany
    follower_data = [(user_id_map[follower], user_id_map[followee]) for follower, followee in follower_pairs]
    
    # Use executemany for bulk insertion
    cursor.executemany(
        "INSERT INTO Follower (user_id_1, user_id_2) VALUES (?, ?)",
        follower_data
    )

def insert_playlists(cursor, user_id_map):
    # Define list of playlists to insert
    playlists = [
        ('AGLAMA GARANTILI KARISIK', 'A playlist of popular rock songs', 'Tunceredits'),
        ('Lofi', 'Student dying musics', '345math'),
        ('Zam yaparken dinlemelik müzikler', 'Economic boost songs', 'EFCK'),
        ('Jazz Classics', 'The best of jazz music', 'jazzcat'),
        ('Rock Anthems', 'Classic rock hits', 'rocknroller'),
        ('Hip Hop Beats', 'Fresh beats for freestyle', 'beatmaker'),
        ('Classical Masterpieces', 'The greatest classical compositions', 'classicfan'),
        ('Rap Essentials', 'Essential tracks from rap legends', 'rapperfan'),
        ('Folk Collection', 'Acoustic folk classics', 'livemusic'),
        ('Indie Discoveries', 'Underground indie gems', 'vinyladdict'),
        ('Electronic Mix', 'Electronic dance music mix', 'concertgoer'),
        ('Pop Hits 2024', 'Current pop chart toppers', 'producer'),
        ('Workout Mix', 'High energy songs for exercise', 'Batman'),
        ('Chill Vibes', 'Relaxing music for downtime', 'Charlie'),
        ('Gaming Soundtrack', 'Music for gaming sessions', 'mgs6'),
        ('Road Trip Playlist', 'Songs for the open road', 'infinityedge'),
        ('Anime Openings', 'Best anime theme songs', 'franxx'),
        ('Turkish Classics', 'Classic Turkish music collection', 'rockson'),
        ('Rap Battles', 'Best tracks for rap battles', '800kmid'),
        ('All Time Favorites', 'Collection of all-time favorite songs', 'musiclover')
    ]
    
    # Prepare data for executemany
    # For each playlist, get the user_id that corresponds to the creator nickname
    playlist_data = []
    for name, desc, creator in playlists:
        if creator in user_id_map:
            creator_id = user_id_map[creator]
            playlist_data.append((name, desc, creator_id))
        else:
            print(f"Warning: Creator '{creator}' not found in user_id_map, skipping playlist '{name}'")
    
    # Print the SQL statement and data for debugging
    print(f"Executing INSERT INTO Playlist with {len(playlist_data)} playlists")
    print(f"Sample data: {playlist_data[0] if playlist_data else 'No data'}")
    
    # Use executemany for bulk insertion
    cursor.executemany(
        "INSERT INTO Playlist (playlist_name, playlist_description, playlist_image, creator_id) VALUES (?, ?, NULL, ?)",
        playlist_data
    )

def insert_songs(cursor):
    songs = [
        ('Stairway to Heaven', 482),
        ('Bohemian Rhapsody', 355),
        ('Metal Gear Solid 3 Theme', 150),
        ('Bilgewater', 180),
        ('Kiss of Death', 240),
        ('Under the tree', 122),
        ('800kmid', 120),
        ('Tunceredits', 210),
        ('345math', 210),
        ('Take Me Out', 237),
        ('All Along the Watchtower', 240),
        ('Sweet Child O Mine', 356),
        ('Nothing Else Matters', 386),
        ('Piano Sonata No. 14', 840),
        ('99 Problems', 226),
        ('Lose Yourself', 320),
        ('Harvest Moon', 312),
        ('Love Will Tear Us Apart', 218),
        ('One More Time', 320),
        ('Kashmir', 508),
        ('Imagine', 183),
        ('Hotel California', 390),
        ('Thriller', 358),
        ('Smells Like Teen Spirit', 301),
        ('Billie Jean', 293)
    ]
    
    # Use executemany for bulk insertion
    cursor.executemany(
        "INSERT INTO Song (song_name, song_time, song_image, audio) VALUES (?, ?, NULL, NULL)",
        songs
    )

def insert_playlist_users(cursor, user_id_map, playlist_id_map):
    relationships = [
        ('Tunceredits', 'AGLAMA GARANTILI KARISIK'),
        ('Tunceredits', 'Lofi'),
        ('Tunceredits', 'Zam yaparken dinlemelik müzikler'),
        ('345math', 'AGLAMA GARANTILI KARISIK'),
        ('345math', 'Lofi'),
        ('EFCK', 'AGLAMA GARANTILI KARISIK'),
        ('jazzcat', 'Jazz Classics'),
        ('rocknroller', 'Rock Anthems'),
        ('beatmaker', 'Hip Hop Beats'),
        ('musiclover', 'All Time Favorites'),
        ('Tunceredits', 'Pop Hits 2024'),
        ('Batman', 'Rock Anthems'),
        ('Charlie', 'Chill Vibes'),
        ('infinityedge', 'Road Trip Playlist'),
        ('franxx', 'Anime Openings'),
        ('rockson', 'Turkish Classics'),
        ('800kmid', 'Rap Battles'),
        ('musiclover', 'Chill Vibes'),
        ('jazzcat', 'All Time Favorites'),
        ('producer', 'Electronic Mix')
    ]
    
    # Prepare data for executemany
    relationship_data = [(user_id_map[user], playlist_id_map[playlist]) for user, playlist in relationships]
    
    # Use executemany for bulk insertion
    cursor.executemany(
        "INSERT INTO Playlist_User (user_id, playlist_id) VALUES (?, ?)",
        relationship_data
    )

def insert_playlist_songs(cursor, playlist_id_map, song_id_map):
    relationships = [
        ('AGLAMA GARANTILI KARISIK', 'Stairway to Heaven'),
        ('AGLAMA GARANTILI KARISIK', 'Bohemian Rhapsody'),
        ('Lofi', 'Metal Gear Solid 3 Theme'),
        ('Lofi', 'Bilgewater'),
        ('Zam yaparken dinlemelik müzikler', 'Kiss of Death'),
        ('Jazz Classics', 'All Along the Watchtower'),
        ('Rock Anthems', 'Sweet Child O Mine'),
        ('Rock Anthems', 'Nothing Else Matters'),
        ('Classical Masterpieces', 'Piano Sonata No. 14'),
        ('Rap Essentials', '99 Problems'),
        ('Rap Essentials', 'Lose Yourself'),
        ('Folk Collection', 'Harvest Moon'),
        ('Indie Discoveries', 'Love Will Tear Us Apart'),
        ('Electronic Mix', 'One More Time'),
        ('Pop Hits 2024', 'Thriller'),
        ('Pop Hits 2024', 'Billie Jean'),
        ('Workout Mix', 'Sweet Child O Mine'),
        ('Chill Vibes', 'Imagine'),
        ('Gaming Soundtrack', 'Metal Gear Solid 3 Theme'),
        ('Road Trip Playlist', 'Hotel California')
    ]
    
    # Prepare data for executemany
    relationship_data = [(playlist_id_map[playlist], song_id_map[song]) for playlist, song in relationships]
    
    # Use executemany for bulk insertion
    cursor.executemany(
        "INSERT INTO Playlist_Song (playlist_id, song_id) VALUES (?, ?)",
        relationship_data
    )

def insert_user_likes(cursor, user_id_map, song_id_map):
    # Define list of user likes
    likes = [
        ('Tunceredits', 'Stairway to Heaven'),
        ('Tunceredits', 'Bohemian Rhapsody'),
        ('345math', 'Stairway to Heaven'),
        ('EFCK', 'Metal Gear Solid 3 Theme'),
        ('Batman', 'Bilgewater'),
        ('musiclover', 'Imagine'),
        ('jazzcat', 'All Along the Watchtower'),
        ('rocknroller', 'Sweet Child O Mine'),
        ('beatmaker', 'Lose Yourself'),
        ('classicfan', 'Piano Sonata No. 14'),
        ('rapperfan', '99 Problems'),
        ('livemusic', 'Harvest Moon'),
        ('vinyladdict', 'Love Will Tear Us Apart'),
        ('concertgoer', 'One More Time'),
        ('producer', 'Thriller'),
        ('Tunceredits', 'Hotel California'),
        ('345math', 'Nothing Else Matters'),
        ('EFCK', 'Imagine'),
        ('Charlie', 'Billie Jean'),
        ('mgs6', 'Kashmir')
    ]
    
    # Prepare data for executemany
    like_data = [(user_id_map[user], song_id_map[song]) for user, song in likes]
    
    # Use executemany for bulk insertion
    cursor.executemany(
        "INSERT INTO UserLikes (user_id, song_id) VALUES (?, ?)",
        like_data
    )

def insert_genres(cursor, song_id_map):
    # Define unique genres
    unique_genres = [
        'Rock', 'Pop', 'Jazz', 'Classical', 'Rap', 'Folk', 'Indie', 'Electronic', 
        'Metal', 'Country', 'R&B', 'Blues', 'Reggae', 'Hip Hop', 'Alternative'
    ]
    
    # First insert the unique genres and build a mapping
    genre_id_map = {}
    
    for genre_name in unique_genres:
        # Generate a UUID for each genre
        genre_id = str(uuid.uuid4())
        
        # Insert the genre
        cursor.execute(
            "INSERT INTO Genre (genre_id, genre_name) VALUES (?, ?)",
            (genre_id, genre_name)
        )
        
        # Store the genre_id in the map
        genre_id_map[genre_name] = genre_id
    
    # Define song-genre relationships
    song_genres = [
        ('Stairway to Heaven', 'Rock'),
        ('Bohemian Rhapsody', 'Rock'),
        ('Bohemian Rhapsody', 'Pop'),  # Example of multiple genres for one song
        ('Metal Gear Solid 3 Theme', 'Jazz'),
        ('Metal Gear Solid 3 Theme', 'Alternative'),  # Multiple genres
        ('Bilgewater', 'Rock'),
        ('Kiss of Death', 'Pop'),
        ('Under the tree', 'Jazz'),
        ('800kmid', 'Rap'),
        ('Tunceredits', 'Pop'),
        ('345math', 'Rock'),
        ('Take Me Out', 'Rock'),
        ('All Along the Watchtower', 'Rock'),
        ('Sweet Child O Mine', 'Rock'),
        ('Nothing Else Matters', 'Rock'),
        ('Nothing Else Matters', 'Metal'),  # Multiple genres
        ('Piano Sonata No. 14', 'Classical'),
        ('99 Problems', 'Rap'),
        ('99 Problems', 'Hip Hop'),  # Multiple genres
        ('Lose Yourself', 'Rap'),
        ('Harvest Moon', 'Folk'),
        ('Love Will Tear Us Apart', 'Indie'),
        ('One More Time', 'Electronic'),
        ('Kashmir', 'Rock'),
        ('Imagine', 'Pop'),
        ('Imagine', 'Folk'),  # Multiple genres
        ('Hotel California', 'Rock'),
        ('Thriller', 'Pop'),
        ('Smells Like Teen Spirit', 'Rock'),
        ('Smells Like Teen Spirit', 'Alternative'),  # Multiple genres
        ('Billie Jean', 'Pop'),
        ('Billie Jean', 'R&B')  # Multiple genres
    ]
    
    # Prepare data for the SongGenre junction table
    song_genre_data = []
    
    for song_name, genre_name in song_genres:
        if song_name in song_id_map and genre_name in genre_id_map:
            song_genre_data.append((song_id_map[song_name], genre_id_map[genre_name]))
    
    # Use executemany for bulk insertion into the junction table
    cursor.executemany(
        "INSERT INTO SongGenre (song_id, genre_id) VALUES (?, ?)",
        song_genre_data
    )

def insert_albums(cursor):
    albums = [
        ('This Fire', 'An amazing album', '2020-01-01'),
        ('The Wall', 'A classic album', '1979-11-30'),
        ('Evolve', 'Modern rock album', '2017-06-23'),
        ('The Division Bell', 'Pink Floyd album', '1994-03-28'),
        ('Led Zeppelin IV', 'Classic rock album', '1971-11-08'),
        ('A Night at the Opera', 'Queen masterpiece', '1975-11-21'),
        ('Master of Puppets', 'Metallica classic', '1986-03-03'),
        ('Beethoven: Complete Sonatas', 'Classical masterpieces', '1950-01-01'),
        ('The Blueprint', 'Jay-Z classic', '2001-09-11'),
        ('Harvest', 'Neil Young folk album', '1972-02-01'),
        ('Unknown Pleasures', 'Joy Division debut', '1979-06-15'),
        ('Discovery', 'Daft Punk electronic classic', '2001-03-12'),
        ('Physical Graffiti', 'Led Zeppelin double album', '1975-02-24'),
        ('Imagine', 'John Lennon classic', '1971-09-09'),
        ('Hotel California', 'Eagles masterpiece', '1976-12-08'),
        ('Thriller', 'Michael Jackson bestseller', '1982-11-30'),
        ('Nevermind', 'Nirvana breakthrough', '1991-09-24'),
        ('Dangerous', 'Michael Jackson album', '1991-11-26'),
        ('Back in Black', 'AC/DC classic', '1980-07-25'),
        ('Rumours', 'Fleetwood Mac classic', '1977-02-04')
    ]
    
    # Check for existing albums first to avoid unique constraint error
    cursor.execute("SELECT album_name FROM Album")
    existing_albums = {row[0] for row in cursor.fetchall()}
    
    # Filter out albums that already exist in the database
    new_albums = [(name, about, date) for name, about, date in albums if name not in existing_albums]
    
    if not new_albums:
        print("No new albums to insert - all albums already exist")
        return
    
    print(f"Inserting {len(new_albums)} new albums")
    if new_albums:
        print(f"Sample album: {new_albums[0]}")
    
    # Use executemany for bulk insertion
    cursor.executemany(
        "INSERT INTO Album (album_name, about, album_image, release_date) VALUES (?, ?, NULL, ?)",
        new_albums
    )

def insert_album_info(cursor, album_id_map, song_id_map):
    # Define album tracks with unique track numbers per album
    tracks = [
        ('This Fire', 'Stairway to Heaven', 1),
        ('This Fire', 'Kiss of Death', 2),
        ('The Wall', 'Bohemian Rhapsody', 1),
        ('The Wall', 'Take Me Out', 2),
        ('Evolve', 'Metal Gear Solid 3 Theme', 1),
        ('Evolve', '800kmid', 2),
        ('The Division Bell', 'Bilgewater', 1),
        ('The Division Bell', 'Tunceredits', 2),
        ('Led Zeppelin IV', 'Stairway to Heaven', 1),
        ('Led Zeppelin IV', 'Kashmir', 2),
        ('A Night at the Opera', 'Bohemian Rhapsody', 1),
        ('Master of Puppets', 'Nothing Else Matters', 1),
        ('Beethoven: Complete Sonatas', 'Piano Sonata No. 14', 1),
        ('The Blueprint', '99 Problems', 1),
        ('Harvest', 'Harvest Moon', 1),
        ('Unknown Pleasures', 'Love Will Tear Us Apart', 1),
        ('Discovery', 'One More Time', 1),
        ('Physical Graffiti', 'Kashmir', 1),
        ('Imagine', 'Imagine', 1),
        ('Hotel California', 'Hotel California', 1),
        ('Thriller', 'Thriller', 1),
        ('Thriller', 'Billie Jean', 2),
        ('Nevermind', 'Smells Like Teen Spirit', 1),
        ('Dangerous', 'Billie Jean', 1),
        ('Back in Black', 'Sweet Child O Mine', 1),
        ('Rumours', 'Love Will Tear Us Apart', 1)
    ]
    
    # Check for duplicate track numbers within the same album
    album_tracks = {}
    for album, song, track_num in tracks:
        if album not in album_tracks:
            album_tracks[album] = set()
        if track_num in album_tracks[album]:
            print(f"Warning: Duplicate track number {track_num} for album '{album}'")
        album_tracks[album].add(track_num)
    
    # Prepare data for executemany, handling missing albums or songs
    album_info_data = []
    for album, song, track_num in tracks:
        if album in album_id_map and song in song_id_map:
            album_info_data.append((album_id_map[album], song_id_map[song], track_num))
        else:
            if album not in album_id_map:
                print(f"Warning: Album '{album}' not found in album_id_map, skipping")
            if song not in song_id_map:
                print(f"Warning: Song '{song}' not found in song_id_map, skipping")
    
    # Print debugging information
    print(f"Inserting {len(album_info_data)} album-song relationships")
    if album_info_data:
        print(f"Sample data: {album_info_data[0]}")
    
    # Use executemany for bulk insertion
    cursor.executemany(
        "INSERT INTO Album_Info (album_id, song_id, track_number) VALUES (?, ?, ?)",
        album_info_data
    )

def insert_music_groups(cursor):
    groups = [
        ('The Beatles', 4, '1960-08-01'),
        ('Queen', 4, '1970-06-27'),
        ('Pink Floyd', 3, '1965-01-01'),
        ('Metallica', 4, '1981-10-28'),
        ('Led Zeppelin', 4, '1968-09-25'),
        ('Nirvana', 3, '1987-01-01'),
        ('AC/DC', 5, '1973-11-01'),
        ('Eagles', 5, '1971-02-01'),
        ('Fleetwood Mac', 5, '1967-07-01'),
        ('The Rolling Stones', 4, '1962-07-12'),
        ('Guns N Roses', 5, '1985-03-01'),
        ('Black Sabbath', 4, '1968-09-01'),
        ('Joy Division', 4, '1976-01-01'),
        ('Daft Punk', 2, '1993-01-01'),
        ('Red Hot Chili Peppers', 4, '1983-01-01'),
        ('Radiohead', 5, '1985-01-01'),
        ('U2', 4, '1976-09-25'),
        ('Coldplay', 4, '1996-01-01'),
        ('Linkin Park', 6, '1996-01-01'),
        ('Green Day', 3, '1987-01-01')
    ]
    
    # Check for existing groups first to avoid unique constraint error
    cursor.execute("SELECT group_name FROM MusicGroup")
    existing_groups = {row[0] for row in cursor.fetchall()}
    
    # Filter out groups that already exist in the database
    new_groups = [(name, members, date) for name, members, date in groups if name not in existing_groups]
    
    if not new_groups:
        print("No new music groups to insert - all groups already exist")
        return
    
    print(f"Inserting {len(new_groups)} new music groups")
    if new_groups:
        print(f"Sample group: {new_groups[0]}")
    
    # Use executemany for bulk insertion
    cursor.executemany(
        "INSERT INTO MusicGroup (group_name, number_of_members, creation_date, group_image) VALUES (?, ?, ?, NULL)",
        new_groups
    )

def insert_artists(cursor, group_id_map):
    artists = [
        ('The Beatles', 'John Lennon'),
        ('The Beatles', 'Paul McCartney'),
        ('The Beatles', 'George Harrison'),
        ('The Beatles', 'Ringo Starr'),
        ('Queen', 'Freddie Mercury'),
        ('Queen', 'Brian May'),
        ('Queen', 'Roger Taylor'),
        ('Queen', 'John Deacon'),
        ('Pink Floyd', 'David Gilmour'),
        ('Pink Floyd', 'Nick Mason'),
        ('Pink Floyd', 'Richard Wright'),
        ('Metallica', 'James Hetfield'),
        ('Metallica', 'Lars Ulrich'),
        ('Metallica', 'Kirk Hammett'),
        ('Metallica', 'Robert Trujillo'),
        ('Led Zeppelin', 'Robert Plant'),
        ('Led Zeppelin', 'Jimmy Page'),
        ('Led Zeppelin', 'John Paul Jones'),
        ('Led Zeppelin', 'John Bonham'),
        ('Nirvana', 'Kurt Cobain'),
        ('Nirvana', 'Dave Grohl'),
        ('Nirvana', 'Krist Novoselic'),
        ('AC/DC', 'Angus Young'),
        ('Eagles', 'Don Henley'),
        ('Fleetwood Mac', 'Stevie Nicks')
    ]
    
    # Check for existing artists first to avoid unique constraint error
    cursor.execute("SELECT g.group_name, a.full_name FROM Artist a JOIN MusicGroup g ON a.group_id = g.group_id")
    existing_artists = {(row[0], row[1]) for row in cursor.fetchall()}
    
    # Filter the artists to keep only those that don't exist yet
    new_artists = [(group, artist) for group, artist in artists 
                  if (group, artist) not in existing_artists and group in group_id_map]
    
    if not new_artists:
        print("No new artists to insert - all artists already exist")
        return
    
    print(f"Inserting {len(new_artists)} new artists")
    if new_artists:
        print(f"Sample artist: {new_artists[0]}")
    
    # Prepare data for executemany
    artist_data = [(group_id_map[group], artist) for group, artist in new_artists]
    
    # Use executemany for bulk insertion
    cursor.executemany(
        "INSERT INTO Artist (group_id, full_name) VALUES (?, ?)",
        artist_data
    )

def insert_album_groups(cursor, album_id_map, group_id_map):
    relationships = [
        ('This Fire', 'The Beatles'),
        ('This Fire', 'Metallica'),
        ('The Wall', 'Queen'),
        ('The Wall', 'Led Zeppelin'),
        ('Evolve', 'Pink Floyd'),
        ('The Division Bell', 'Pink Floyd'),
        ('Led Zeppelin IV', 'Led Zeppelin'),
        ('A Night at the Opera', 'Queen'),
        ('Master of Puppets', 'Metallica'),
        ('Unknown Pleasures', 'Joy Division'),
        ('Discovery', 'Daft Punk'),
        ('Physical Graffiti', 'Led Zeppelin'),
        ('Imagine', 'The Beatles'),
        ('Hotel California', 'Eagles'),
        ('Thriller', 'The Beatles'),
        ('Nevermind', 'Nirvana'),
        ('Back in Black', 'AC/DC'),
        ('Rumours', 'Fleetwood Mac')
    ]
    
    # Check for valid album and group IDs
    valid_relationships = [(album, group) for album, group in relationships 
                          if album in album_id_map and group in group_id_map]
    
    # Check for existing relationships to avoid unique constraint error
    cursor.execute("SELECT a.album_name, g.group_name FROM Album_Group ag "
                  "JOIN Album a ON ag.album_id = a.album_id "
                  "JOIN MusicGroup g ON ag.group_id = g.group_id")
    existing_relationships = {(row[0], row[1]) for row in cursor.fetchall()}
    
    # Filter out relationships that already exist
    new_relationships = [(album, group) for album, group in valid_relationships 
                        if (album, group) not in existing_relationships]
    
    if not new_relationships:
        print("No new album-group relationships to insert - all relationships already exist")
        return
    
    print(f"Inserting {len(new_relationships)} new album-group relationships")
    if new_relationships:
        print(f"Sample relationship: {new_relationships[0]}")
    
    # Prepare data for executemany
    relationship_data = [(album_id_map[album], group_id_map[group]) for album, group in new_relationships]
    
    # Use executemany for bulk insertion
    cursor.executemany(
        "INSERT INTO Album_Group (album_id, group_id) VALUES (?, ?)",
        relationship_data
    )

def insert_history(cursor, user_id_map, song_id_map):
    history_entries = [
        ('Tunceredits', 'Stairway to Heaven', '2023-01-01T12:00:00', 210),
        ('345math', 'Bohemian Rhapsody', '2024-01-01T12:00:00', 210),
        ('EFCK', 'Metal Gear Solid 3 Theme', '2024-12-01T12:00:00', 210),
        ('Batman', 'Bilgewater', '2024-11-15T12:00:00', 210),
        ('Charlie', 'Kiss of Death', '2024-11-01T12:00:00', 210),
        ('musiclover', 'Imagine', '2024-05-10T14:30:00', 180),
        ('jazzcat', 'All Along the Watchtower', '2024-05-11T09:15:00', 240),
        ('rocknroller', 'Sweet Child O Mine', '2024-05-12T18:45:00', 300),
        ('beatmaker', 'Lose Yourself', '2024-05-13T22:20:00', 320),
        ('classicfan', 'Piano Sonata No. 14', '2024-05-14T16:10:00', 600),
        ('rapperfan', '99 Problems', '2024-05-15T13:40:00', 226),
        ('livemusic', 'Harvest Moon', '2024-05-16T20:30:00', 312),
        ('vinyladdict', 'Love Will Tear Us Apart', '2024-05-17T19:05:00', 218),
        ('concertgoer', 'One More Time', '2024-05-18T23:55:00', 320),
        ('producer', 'Thriller', '2024-05-19T17:25:00', 358),
        ('Tunceredits', 'Hotel California', '2024-05-20T08:30:00', 390),
        ('345math', 'Nothing Else Matters', '2024-05-21T11:45:00', 386),
        ('EFCK', 'Imagine', '2024-05-22T15:15:00', 183),
        ('Charlie', 'Billie Jean', '2024-05-23T21:10:00', 293),
        ('mgs6', 'Kashmir', '2024-05-24T10:05:00', 508)
    ]
    
    # Prepare data for executemany
    history_data = [(user_id_map[user], start_time, duration, song_id_map[song]) 
                   for user, song, start_time, duration in history_entries]
    
    # Use executemany for bulk insertion
    cursor.executemany(
        "INSERT INTO History (user_id, start_time, duration, song_id) VALUES (?, ?, ?, ?)",
        history_data
    )
import sqlite3
from werkzeug.security import generate_password_hash
import uuid
import random

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
        # Manually assign UUIDs for accounts
        account_id_map = {
            'Tunceredits': '11111111-1111-1111-1111-111111111111',
            '345math': '22222222-2222-2222-2222-222222222222',
            'EFCK': '33333333-3333-3333-3333-333333333333',
            'Batman': '44444444-4444-4444-4444-444444444444',
            'Charlie': '55555555-5555-5555-5555-555555555555',
            'mgs6': '66666666-6666-6666-6666-666666666666',
            'infinityedge': '77777777-7777-7777-7777-777777777777',
            'franxx': '88888888-8888-8888-8888-888888888888',
            'rockson': '99999999-9999-9999-9999-999999999999',
            '800kmid': '00000000-0000-0000-0000-000000000000',
            'musiclover': 'aaaaaaaa-aaaa-aaaa-aaaa-1aaaaaaaaaaa',
            'jazzcat': 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbb2bbbbb',
            'rocknroller': 'cccccccc-cccc-cccc-cccc-c3cccccccccc',
            'beatmaker': 'dddddddd-dddd-dddd-dddd-ddd4dddddddd',
            'classicfan': 'eeeeeeee-eeee-eeee-eeee-ee5eeeeeeeee',
            'rapperfan': 'ffffffff-ffff-ffff-ffff-fff6ffffffff',
            'livemusic': '11111111-2222-3333-4444-555575555555',
            'vinyladdict': '22222222-3333-4444-5555-668666666666',
            'concertgoer': '33333333-4444-5555-6666-779777777777',
            'producer': '44444444-5555-6666-7777-888880888888'
        }

        # Define user_id_map using account_id_map
        user_id_map = account_id_map

        playlists = [
            ('AGLAMA GARANTILI KARISIK', 'A playlist of popular rock songs', 'Tunceredits'),
            ('Lofi', 'Student dying musics', '345math'),
            ('Zam yaparken dinlemelik müzikler', 'Economic boost songs', 'EFCK'),
            ('Jazz Classics', 'The best of jazz music', 'jazzcat'),
            ('Rock Anthems', 'Classic rock hits', 'rocknroller')
        ]

        # Ensure all playlists have unique IDs
        playlist_id_map = {
            'AGLAMA GARANTILI KARISIK': '55555555-5555-5555-5555-655555555555',
            'Lofi': '66666666-6666-6666-6666-666656666666',
            'Zam yaparken dinlemelik müzikler': '77777777-7777-7777-7777-776777777777',
            'Jazz Classics': '88888488-8888-8888-8888-888888888888',
            'Rock Anthems': '99919999-9999-9999-9999-999999999999'
        }

        # Example data for songs
        songs = [
            ('Stairway to Heaven', 482),
            ('Bohemian Rhapsody', 355),
            ('Metal Gear Solid 3 Theme', 150),
            ('Kiss of Death', 200),
            ('All Along the Watchtower', 220),
            ('Sweet Child O Mine', 250),
            ('Lose Yourself', 200),
            ('Love Will Tear Us Apart', 220),
            ('One More Time', 250),
            ('Harvest Moon', 200),
            ('Hotel California', 220),
            ('Nothing Else Matters', 250)
        ]

        playlist_user_data = [
            ('Tunceredits', 'AGLAMA GARANTILI KARISIK'),
            ('345math', 'Lofi'), 
            ('EFCK', 'Zam yaparken dinlemelik müzikler'),
            ('jazzcat', 'Jazz Classics'),
            ('rocknroller', 'Rock Anthems'),
            ('musiclover', 'AGLAMA GARANTILI KARISIK'),
            ('vinyladdict', 'Lofi'),
            ('concertgoer', 'Zam yaparken dinlemelik müzikler'),
            ('producer', 'Jazz Classics'),
            ('rapperfan', 'Rock Anthems'),
            ('livemusic', 'AGLAMA GARANTILI KARISIK'),
            ('mgs6', 'Lofi'),
            ('infinityedge', 'Zam yaparken dinlemelik müzikler'),
            ('franxx', 'Jazz Classics'),
            ('rockson', 'Rock Anthems')
        ]
        
        playlist_song_data = [
            ('AGLAMA GARANTILI KARISIK', 'Stairway to Heaven'),
            ('Lofi', 'Bohemian Rhapsody'),
            ('Zam yaparken dinlemelik müzikler', 'Metal Gear Solid 3 Theme'),
            ('Jazz Classics', 'Kiss of Death'),
            ('Rock Anthems', 'All Along the Watchtower'),
            ('AGLAMA GARANTILI KARISIK', 'Sweet Child O Mine'),
            ('Lofi', 'Lose Yourself'),
            ('Zam yaparken dinlemelik müzikler', 'Love Will Tear Us Apart'),
            ('Jazz Classics', 'One More Time'),
            ('Rock Anthems', 'Harvest Moon'),
            ('AGLAMA GARANTILI KARISIK', 'Hotel California'),
        ]

        # Example data for user likes
        User_likes_data = [
            ('Tunceredits', 'Stairway to Heaven'),
            ('345math', 'Bohemian Rhapsody'),
            ('EFCK', 'Metal Gear Solid 3 Theme'),
            ('Batman', 'Kiss of Death'),
            ('jazzcat', 'All Along the Watchtower'), 
            ('rocknroller', 'Sweet Child O Mine'),
            ('musiclover', 'Lose Yourself'),
            ('vinyladdict', 'Love Will Tear Us Apart'),
            ('concertgoer', 'One More Time'),
            ('producer', 'Harvest Moon'),
            ('rapperfan', 'Hotel California'),
            ('livemusic', 'Nothing Else Matters'),
            ('mgs6', 'Stairway to Heaven'),
            ('infinityedge', 'Bohemian Rhapsody'),
            ('franxx', 'Metal Gear Solid 3 Theme'),
            ('rockson', 'Kiss of Death'),
            ('Tunceredits', 'Sweet Child O Mine'),
            ('345math', 'One More Time'),
            ('EFCK', 'Hotel California'),
            ('Batman', 'Nothing Else Matters')
        ]
        # Example data for albums
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

        # Manually assign UUIDs for songs
        song_id_map = {
            'Stairway to Heaven': '88888888-8888-8888-8888-888888888888',
            'Bohemian Rhapsody': '99999999-9999-9999-9999-999999999999',
            'Metal Gear Solid 3 Theme': '00000000-0000-0000-0000-000000000000',
            'Kiss of Death': '11111111-1111-1111-1111-111111111111',
            'All Along the Watchtower': '22222222-2222-2222-2222-222222222222',
            'Sweet Child O Mine': '33333333-3333-3333-3333-333333333333',
            'Lose Yourself': '44444444-4444-4444-4444-444444444444',
            'Love Will Tear Us Apart': '55555555-5555-5555-5555-555555555555',
            'One More Time': '66666666-6666-6666-6666-666666666666',
            'Harvest Moon': '77777777-7777-7777-7777-777777777777',
            'Hotel California': '88888888-88a8-8888-8888-888888855588',
            'Nothing Else Matters': '99999999-b999-9999-9999-669999999999'
        }

        # Manually assign UUIDs for albums
        album_id_map = {
            'This Fire': 'aaaaaaaa-aaaa-aaaa-aaaa-aaaa1aaaaaaa',
            'The Wall': 'bbbbbbbb-bbbb-bbbb-bbbb-bb2bbbbbbbbb',
            'Evolve': 'cccccccc-cccc-cccc-cccc-ccccc3cccccc',
            'The Division Bell': 'dddddddd-dddd-dddd-dd4d-dddddddddddd',
            'Led Zeppelin IV': 'eeeeeeee-eeee-eeee-eeee-eeeee5eeeeee',
            'A Night at the Opera': 'ffffffff-ffff-ffff-ffff-fff6ffffffff',
            'Master of Puppets': '11111111-1111-1111-1111-111141111111',
            'Beethoven: Complete Sonatas': '22222222-2222-2222-2122-222222222222',
            'The Blueprint': '33333333-3333-3333-3333-333433333333',
            'Harvest': '44444444-4444-4444-4444-544444444444',
            'Unknown Pleasures': '55555555-5555-5555-5555-555155555555',
            'Discovery': '66666666-6666-6666-6666-666666666626',
            'Physical Graffiti': '77777777-7777-7777-7777-733777777777',
            'Imagine': '88888888-8888-8888-8888-888858888888',
            'Hotel California': '99999999-9999-9999-9999-999199999999',
            'Thriller': '00000000-0000-0000-0000-000000000900',
            'Nevermind': 'aaaaaaaa-bbbb-bbbb-bbbb-bbbbbbbbbcbb',
            'Dangerous': 'bbbbbbbb-cccc-cccc-cccc-cccccccgcccc',
            'Back in Black': 'cccccccc-dddd-dddd-dddd-ddfddddddddd',
            'Rumours': 'dddddddd-eeee-eeee-eeee-eeeeedeeeeee'
        }

        artists = [
            ('John Lennon', 'UK', 'Vocals'),
            ('Paul McCartney', 'UK', 'Bass'),
            ('George Harrison', 'UK', 'Guitar'),
            ('Ringo Starr', 'UK', 'Drums'),
            ('Freddie Mercury', 'UK', 'Vocals'),
            ('Brian May', 'UK', 'Guitar'),
            ('Roger Taylor', 'UK', 'Drums'),
            ('John Deacon', 'UK', 'Bass'),
            ('Kurt Cobain', 'USA', 'Vocals'),
            ('Axl Rose', 'USA', 'Vocals'),
            ('Slash', 'USA', 'Guitar'),
            ('Robert Plant', 'UK', 'Vocals'),
            ('Jimmy Page', 'UK', 'Guitar'),
            ('Mick Jagger', 'UK', 'Vocals'),
            ('Keith Richards', 'UK', 'Guitar'),
            ('Bono', 'Ireland', 'Vocals'),
            ('The Edge', 'Ireland', 'Guitar'),
            ('Chris Martin', 'UK', 'Vocals'),
            ('Thom Yorke', 'UK', 'Vocals'),
            ('Eddie Vedder', 'USA', 'Vocals'),
            ('John Paul Jones', 'UK', 'Bass'),
            ('John Bonham', 'UK', 'Drums'),
            ('Syd Barrett', 'UK', 'Guitar'),
            ('Roger Waters', 'UK', 'Bass'),
            ('David Gilmour', 'UK', 'Guitar'),
            ('Nick Mason', 'UK', 'Drums'),
            ('Richard Wright', 'UK', 'Keyboard'),
            ('James Hetfield', 'USA', 'Vocals'),
            ('Lars Ulrich', 'Denmark', 'Drums'),
            ('Kirk Hammett', 'USA', 'Guitar'),
            ('Robert Trujillo', 'USA', 'Bass'),
            ('Don Henley', 'USA', 'Vocals'),
            ('Glenn Frey', 'USA', 'Guitar'),
            ('Joe Walsh', 'USA', 'Guitar'),
            ('Randy Meisner', 'USA', 'Bass'),
            ('Don Felder', 'USA', 'Guitar'),
            ('Mick Fleetwood', 'UK', 'Drums'),
            ('John McVie', 'UK', 'Bass'),
            ('Christine McVie', 'UK', 'Keyboard'),
            ('Lindsey Buckingham', 'USA', 'Guitar'),
            ('Stevie Nicks', 'USA', 'Vocals'),
            ('Krist Novoselic', 'USA', 'Bass'),
            ('Dave Grohl', 'USA', 'Drums')
        ]

        # Manually assign UUIDs for artists
        artist_id_map = {
            'John Lennon': '44444444-4444-4444-4444-444444444441',
            'Paul McCartney': '55555555-5555-5555-5555-555555555552',
            'George Harrison': '66666666-6666-6666-6666-666666666663',
            'Ringo Starr': '77777777-7777-7777-7777-777777774777',
            'Freddie Mercury': '88888888-8888-8888-8888-888858888888',
            'Brian May': '99999999-9999-9999-9999-999999997999',
            'Roger Taylor': '00000000-0000-0000-0000-000008000000',
            'John Deacon': 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaa9aaaaa',
            'Kurt Cobain': 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbb4bbbbb',
            'Axl Rose': 'cccccccc-cccc-cccc-cccc-ccccccccc5cc',
            'Slash': 'dddddddd-dddd-dddd-dddd-ddddddd4dddd',
            'Robert Plant': 'eeeeeeee-eeee-eeee-eeee-eee2eeeeeeee',
            'Jimmy Page': 'ffffffff-ffff-ffff-ffff-fffffff1ffff',
            'Mick Jagger': '11111111-1111-1111-1111-111111112111',
            'Keith Richards': '22222222-2222-2222-2222-222221222222',
            'Bono': '33333333-3333-3333-3333-333333333533',
            'The Edge': '44444444-4444-4444-4444-447444444444',
            'Chris Martin': '55555555-5555-5555-5555-585555555555',
            'Thom Yorke': '66666666-6666-6666-6666-666669666666',
            'Eddie Vedder': '77777777-7777-7777-7777-777771777777',
            'John Paul Jones': '88808888-8888-8888-8888-888888888888',
            'John Bonham': '999999a9-9999-9999-9999-999999999999',
            'Syd Barrett': '000000b0-0000-0000-0000-000000000000',
            'Roger Waters': '111111c1-1111-1111-1111-111111111111',
            'David Gilmour': '22222222-2g22-2222-2222-222222222222',
            'Nick Mason': '33333333-3333-3e33-3333-333333333333',
            'Richard Wright': '44444444-4444-44f4-4444-444444444444',
            'James Hetfield': '55555555-5555-1555-5555-555555555555',
            'Lars Ulrich': '66666666-6666-6666-6666-622666666666',
            'Kirk Hammett': '77777777-7777-7777-7777-777777733777',
            'Robert Trujillo': '88888888-8888-8888-8488-888888888888',
            'Don Henley': '99999999-9999-9999-9599-999999999999',
            'Glenn Frey': '00000000-0000-0060-0000-000000000000',
            'Joe Walsh': '11111111-1111-1711-1111-111111111111',
            'Randy Meisner': '22222222-2822-2222-2222-222222222222',
            'Don Felder': '33333333-3333-3933-3333-333333333333',
            'Mick Fleetwood': '44444444-4404-4444-4444-444444444444',
            'John McVie': '55555555-5555-5515-5555-555555555555',
            'Christine McVie': '66666666-6666-6666-6266-666666666666',
            ('Lindsey Buckingham', 'USA', 'Guitar'): '77777777-7377-7777-7777-777777777777',
            ('Stevie Nicks', 'USA', 'Vocals'): '88888888-8888-8a88-8888-888888888888',
            ('Krist Novoselic', 'USA', 'Bass'): '99999999-9999-99c9-9999-999999999999',
            ('Dave Grohl', 'USA', 'Drums'): '00000000-0000-0000-0000-0000d0000000'
        }


        groups = [
            ('The Beatles', 4, '1960-01-01'),
            ('Queen', 4, '1970-01-01'),
            ('Pink Floyd', 5, '1965-01-01'),
            ('Metallica', 4, '1981-01-01'),
            ('Led Zeppelin', 4, '1968-01-01'),
            ('Nirvana', 3, '1987-01-01'),
            ('AC/DC', 5, '1973-01-01'),
            ('Eagles', 5, '1971-01-01'),
            ('Fleetwood Mac', 5, '1967-01-01'),
            ('The Rolling Stones', 5, '1962-01-01'),
            ('Guns N Roses', 6, '1985-01-01'),
            ('Black Sabbath', 4, '1968-01-01'),
            ('Joy Division', 4, '1976-01-01'),
            ('Daft Punk', 2, '1993-01-01'),
            ('Red Hot Chili Peppers', 4, '1983-01-01'),
            ('Radiohead', 5, '1985-01-01'),
            ('U2', 4, '1976-01-01'),
            ('Coldplay', 4, '1996-01-01'),
            ('Linkin Park', 6, '1996-01-01'),
            ('Green Day', 3, '1987-01-01')
        ]
        # Manually assign UUIDs for music groups
        group_id_map = {
            'The Beatles': 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb',
            'Queen': 'cccccccc-cccc-cccc-cccc-cccccccccccc',
            'Pink Floyd': 'dddddddd-dddd-dddd-dddd-dddddddddddd',
            'Metallica': 'eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee',
            'Led Zeppelin': 'ffffffff-ffff-ffff-ffff-ffffffffffff',
            'Nirvana': '11111111-1111-1111-1111-111111111111',
            'AC/DC': '22222222-2222-2222-2222-222222222222',
            'Eagles': '33333333-3333-3333-3333-333333333333',
            'Fleetwood Mac': '44444444-4444-4444-4444-444444444444',
            'The Rolling Stones': '55555555-5555-5555-5555-555555555555',
            'Guns N Roses': '66666666-6666-6666-6666-666666666666',
            'Black Sabbath': '77777777-7777-7777-7777-777777777777',
            'Joy Division': '88888888-8888-8888-8888-888888888888',
            'Daft Punk': '99999999-9999-9999-9999-999999999999',
            'Red Hot Chili Peppers': '00000000-0000-0000-0000-000000000000',
            'Radiohead': 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa1',
            'U2': 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbb2',
            'Coldplay': 'cccccccc-cccc-cccc-cccc-ccccccccccc3',
            'Linkin Park': 'dddddddd-dddd-dddd-dddd-ddddddddddd4',
            'Green Day': 'eeeeeeee-eeee-eeee-eeee-eeeeeeeeeee5'
        }

        # Manually assign UUIDs for genres
        genre_id_map = {
            'Rock': 1,
            'Pop': 2,
            'Jazz': 3,
            'Classical': 4,
            'Hip Hop': 5,
            'Rap': 6,
            'Electronic': 7,
            'Indie': 8,
            'Folk': 9,
            'Metal': 10,
            'Blues': 11,
            'Reggae': 12,
            'Country': 13,
            'Soul': 14,
            'Punk': 15,
            'Disco': 16,
            'Funk': 17,
            'R&B': 18,
            'Latin': 19,
            'Alternative': 20
        }

        followers = [
            ('Tunceredits', '345math'),
            ('Tunceredits', 'EFCK'),
            ('345math', 'Batman'),
            ('345math', 'Charlie'),
            ('EFCK', 'mgs6'),
            ('EFCK', 'infinityedge'),
            ('Batman', 'franxx'),
            ('Batman', 'rockson'),
            ('Charlie', '800kmid'),
            ('Charlie', 'musiclover'),
            ('mgs6', 'jazzcat'),
            ('mgs6', 'rocknroller'),
            ('infinityedge', 'beatmaker'),
            ('infinityedge', 'classicfan'),
            ('franxx', 'rapperfan'),
            ('franxx', 'livemusic'),
            ('rockson', 'vinyladdict'),
            ('rockson', 'concertgoer'),
            ('800kmid', 'producer'),
            ('800kmid', 'Tunceredits')
        ]

        # Define album_info_data with song track numbers
        album_info_data = [
            # Led Zeppelin IV
            (album_id_map['Led Zeppelin IV'], song_id_map['Stairway to Heaven'], 4),
            
            # A Night at the Opera
            (album_id_map['A Night at the Opera'], song_id_map['Bohemian Rhapsody'], 11),
            
            # Hotel California
            (album_id_map['Hotel California'], song_id_map['Hotel California'], 2),
            
            # Master of Puppets
            (album_id_map['Master of Puppets'], song_id_map['Nothing Else Matters'], 8),
            
            # Discovery
            (album_id_map['Discovery'], song_id_map['One More Time'], 1),
            
            # Unknown Pleasures
            (album_id_map['Unknown Pleasures'], song_id_map['Love Will Tear Us Apart'], 5),
            
            # Harvest
            (album_id_map['Harvest'], song_id_map['Harvest Moon'], 3)
        ]

        # Define album_group_data with album and group mappings
        album_group_data = [
            # The Beatles albums
            (album_id_map['Imagine'], group_id_map['The Beatles']),
            
            # Queen albums
            (album_id_map['A Night at the Opera'], group_id_map['Queen']),
            
            # Led Zeppelin albums
            (album_id_map['Led Zeppelin IV'], group_id_map['Led Zeppelin']),
            (album_id_map['Physical Graffiti'], group_id_map['Led Zeppelin']),
            
            # Pink Floyd albums
            (album_id_map['The Wall'], group_id_map['Pink Floyd']),
            (album_id_map['The Division Bell'], group_id_map['Pink Floyd']),
            
            # Metallica albums
            (album_id_map['Master of Puppets'], group_id_map['Metallica']),
            
            # Eagles albums
            (album_id_map['Hotel California'], group_id_map['Eagles']),
            
            # Fleetwood Mac albums
            (album_id_map['Rumours'], group_id_map['Fleetwood Mac']),
            
            # Nirvana albums
            (album_id_map['Nevermind'], group_id_map['Nirvana'])
        ]

        # Define music_group_data with group details
        music_group_data = [
            # Group name, number of members, creation date
            (group_id_map['The Beatles'], 'The Beatles', 4, '1960-08-01'),
            (group_id_map['Queen'], 'Queen', 4, '1970-06-27'),
            (group_id_map['Led Zeppelin'], 'Led Zeppelin', 4, '1968-09-25'),
            (group_id_map['Pink Floyd'], 'Pink Floyd', 5, '1965-01-01'),
            (group_id_map['Metallica'], 'Metallica', 4, '1981-10-28'),
            (group_id_map['Eagles'], 'Eagles', 5, '1971-01-01'),
            (group_id_map['Fleetwood Mac'], 'Fleetwood Mac', 5, '1967-07-01'),
            (group_id_map['Nirvana'], 'Nirvana', 3, '1987-01-01')
        ]

        # Define genre_data with song and genre mappings
        genre_data = [
            (song_id_map['Stairway to Heaven'], 1),  # Rock
            (song_id_map['Bohemian Rhapsody'], 1),  # Rock
            (song_id_map['Metal Gear Solid 3 Theme'], 7),  # Electronic
            (song_id_map['Kiss of Death'], 8),  # Indie
            (song_id_map['All Along the Watchtower'], 1),  # Rock
            (song_id_map['Sweet Child O Mine'], 1),  # Rock
            (song_id_map['Lose Yourself'], 6),  # Rap
            (song_id_map['Love Will Tear Us Apart'], 8),  # Indie
            (song_id_map['One More Time'], 7),  # Electronic
            (song_id_map['Harvest Moon'], 9),  # Folk
            (song_id_map['Hotel California'], 1),  # Rock
            (song_id_map['Nothing Else Matters'], 1)  # Rock
        ]


        # Define history_data with user and song mappings
        history_data = [
            (user_id_map['Tunceredits'], song_id_map['Stairway to Heaven'], '2023-01-01 10:00:00'),
            (user_id_map['345math'], song_id_map['Bohemian Rhapsody'], '2023-01-02 11:00:00'),
            (user_id_map['EFCK'], song_id_map['Metal Gear Solid 3 Theme'], '2023-01-03 12:00:00'),
            (user_id_map['Batman'], song_id_map['Kiss of Death'], '2023-01-04 13:00:00'),
            (user_id_map['Charlie'], song_id_map['All Along the Watchtower'], '2023-01-05 14:00:00'),
            (user_id_map['mgs6'], song_id_map['Sweet Child O Mine'], '2023-01-06 15:00:00'),
            (user_id_map['infinityedge'], song_id_map['Lose Yourself'], '2023-01-07 16:00:00'),
            (user_id_map['franxx'], song_id_map['Love Will Tear Us Apart'], '2023-01-08 17:00:00'),
            (user_id_map['rockson'], song_id_map['One More Time'], '2023-01-09 18:00:00'),
            (user_id_map['800kmid'], song_id_map['Harvest Moon'], '2023-01-10 19:00:00'),
            (user_id_map['musiclover'], song_id_map['Hotel California'], '2023-01-11 20:00:00'),
            (user_id_map['jazzcat'], song_id_map['Nothing Else Matters'], '2023-01-12 21:00:00')
        ]

        # Define group_artist_data with group and artist mappings
        group_artist_data = [
            (group_id_map['The Beatles'], artist_id_map['John Lennon']),
            (group_id_map['The Beatles'], artist_id_map['Paul McCartney']),
            (group_id_map['The Beatles'], artist_id_map['George Harrison']),
            (group_id_map['The Beatles'], artist_id_map['Ringo Starr']),
            (group_id_map['Queen'], artist_id_map['Freddie Mercury']),
            (group_id_map['Queen'], artist_id_map['Brian May']),
            (group_id_map['Queen'], artist_id_map['Roger Taylor']),
            (group_id_map['Queen'], artist_id_map['John Deacon']),
            (group_id_map['Led Zeppelin'], artist_id_map['Robert Plant']),
            (group_id_map['Led Zeppelin'], artist_id_map['Jimmy Page']),
            (group_id_map['Led Zeppelin'], artist_id_map['John Paul Jones']),
            (group_id_map['Led Zeppelin'], artist_id_map['John Bonham']),
            (group_id_map['Pink Floyd'], artist_id_map['Syd Barrett']),
            (group_id_map['Pink Floyd'], artist_id_map['Roger Waters']),
            (group_id_map['Pink Floyd'], artist_id_map['David Gilmour']),
            (group_id_map['Pink Floyd'], artist_id_map['Nick Mason']),
            (group_id_map['Pink Floyd'], artist_id_map['Richard Wright']),
            (group_id_map['Metallica'], artist_id_map['James Hetfield']),
            (group_id_map['Metallica'], artist_id_map['Lars Ulrich']),
            (group_id_map['Metallica'], artist_id_map['Kirk Hammett']),
            (group_id_map['Metallica'], artist_id_map['Robert Trujillo']),
            (group_id_map['Eagles'], artist_id_map['Don Henley']),
            (group_id_map['Eagles'], artist_id_map['Glenn Frey']),
            (group_id_map['Eagles'], artist_id_map['Joe Walsh']),
            (group_id_map['Eagles'], artist_id_map['Randy Meisner']),
            (group_id_map['Eagles'], artist_id_map['Don Felder']),
            (group_id_map['Fleetwood Mac'], artist_id_map['Mick Fleetwood']),
            (group_id_map['Fleetwood Mac'], artist_id_map['John McVie']),
            (group_id_map['Fleetwood Mac'], artist_id_map['Christine McVie'])
        ]

        # Update account data insertion
        account_data = []
        for nickname in nicknames:
            password = f"password_{nickname}"
            password_hash = generate_password_hash(password, method='pbkdf2:sha256')
            parts = password_hash.split('$')
            salt_string = parts[2]
            email = f"{nickname.lower()}@example.com"
            if len(email) > 50:
                email = f"{nickname.lower()[:40]}@example.com"
            account_data.append((account_id_map[nickname], email, password_hash, salt_string, get_full_name(nickname), is_subscriber(nickname), '2021-05-01', get_country(nickname), get_sex(nickname), get_language(nickname), get_birth_date(nickname), '2024-01-01T12:00:00'))
        cursor.executemany(
            """INSERT INTO Account (account_id, mail, password_hash, password_salt, full_name, is_subscriber, 
                                   registration_date, country, sex, language, birth_date, last_login) VALUES
            (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            account_data
        )
        connection.commit()

        # user data insertion
        print("Inserting users...")
        user_data = [
            (account_id_map[nickname], nickname, 'Pop', None) for nickname in nicknames
        ]
        cursor.executemany(
            "INSERT INTO User (user_id, nickname, favorite_genre, user_image) VALUES (?, ?, ?, ?)",
            user_data
        )
        connection.commit()

        # insert playlists
        print("Inserting playlists...")
        playlist_data = [
            (playlist_id_map[name], name, desc, user_id_map[creator])
            for name, desc, creator in playlists
            if creator in user_id_map and name in playlist_id_map
        ]
        
        cursor.executemany(
            "INSERT INTO Playlist (playlist_id, playlist_name, playlist_description, playlist_image, creator_id) VALUES (?, ?, ?, NULL, ?)",
            playlist_data
        )
        connection.commit()

        # insert songs
        print("Inserting songs...")
        valid_song_data = [
            (song_id_map[name], name, time, None, None)
            for name, time in songs
            if name in song_id_map
        ]
        cursor.executemany(
            "INSERT INTO Song (song_id, song_name, song_time, song_image, audio) VALUES (?, ?, ?, ?, ?)",
            valid_song_data
        )
        connection.commit()

        # Manually filter valid album data
        print("Inserting albums...")
        valid_album_data = [
            (album_id_map[name], name, about, None, date)
            for name, about, date in albums
            if name in album_id_map
        ]
        cursor.executemany(
            "INSERT INTO Album (album_id, album_name, about, album_image, release_date) VALUES (?, ?, ?, ?, ?)",
            valid_album_data
        )
        connection.commit()

        # insert artists
        print("Inserting artists...")
        valid_artist_data = [
            (artist_id_map[name], name, country, role)
            for name, country, role in artists
            if name in artist_id_map
        ]
        cursor.executemany(
            "INSERT INTO Artist (artist_id, full_name, origin_country, instrument) VALUES (?, ?, ?, ?)",
            valid_artist_data
        )
        connection.commit()

        # insert followers
        print("Inserting followers...")
        followers_data = [
            (user_id_map[follower], user_id_map[followee])
            for follower, followee in followers
            if follower in user_id_map and followee in user_id_map
        ]
        cursor.executemany(
            "INSERT INTO Follower (user_id_1, user_id_2) VALUES (?, ?)",
            followers_data
        )
        connection.commit()

        # Insert playlist songs
        print("Inserting playlist songs...")
        print(cursor.execute("SELECT * FROM Playlist").fetchall())
        print(cursor.execute("SELECT * FROM Song").fetchall())
        valid_playlist_song_data = [
            (playlist_id_map[playlist], song_id_map[song])
            for playlist, song in playlist_song_data
            if playlist in playlist_id_map and song in song_id_map
        ]
        cursor.executemany(
            "INSERT INTO Playlist_Song (playlist_id, song_id) VALUES (?, ?)",
            valid_playlist_song_data
        )
        connection.commit()

        # Insert playlist users
        print("Inserting playlist users...")
        valid_playlist_user_data = [
            (user_id_map[user], playlist_id_map[playlist])
            for user, playlist in playlist_user_data
            if user in user_id_map and playlist in playlist_id_map
        ]
        cursor.executemany(
            "INSERT INTO Playlist_User (user_id, playlist_id) VALUES (?, ?)",
            valid_playlist_user_data
        )
        connection.commit()

        # Insert user likes
        print("Inserting user likes...")
        valid_user_likes_data = [
            (user_id_map[user], song_id_map[song])
            for user, song in User_likes_data
            if user in user_id_map and song in song_id_map
        ]
        cursor.executemany(
            "INSERT INTO UserLikes (user_id, song_id) VALUES (?, ?)",
            valid_user_likes_data
        )
        connection.commit()


        # Insert into the GenreFields table
        print("Inserting genres into GenreFields...")
        genres = [
            'Rock', 'Pop', 'Jazz', 'Classical', 'Hip Hop', 'Rap', 'Electronic', 'Indie', 'Folk', 'Metal',
            'Blues', 'Reggae', 'Country', 'Soul', 'Punk', 'Disco', 'Funk', 'R&B', 'Latin', 'Alternative'
        ]
        cursor.executemany(
            "INSERT INTO GenreFields (genre_name) VALUES (?)",
            [(genre,) for genre in genres]
        )
        connection.commit()

        # insert genre_data
        print("Inserting genre data...")
        cursor.executemany(
            "INSERT INTO Genre (song_id, genre_id) VALUES (?, ?)",
            genre_data
        )
        connection.commit()

        # insert album_info_data
        print("Inserting album info data...")
        cursor.executemany(
            "INSERT INTO Album_Info (album_id, song_id, track_number) VALUES (?, ?, ?)",
            album_info_data
        )
        connection.commit()

        # insert album_group_data
        print(cursor.execute("SELECT * FROM Album").fetchall())
        print(cursor.execute("SELECT * FROM Group").fetchall())
        print("Inserting album group data...")
        cursor.executemany(
            "INSERT INTO Album_Group (album_id, group_id) VALUES (?, ?)",
            album_group_data
        )
        connection.commit()

        # insert music_group_data
        print("Inserting music group data...")
        cursor.executemany(
            "INSERT INTO MusicGroup (group_id, group_name, number_of_members, creation_date) VALUES (?, ?, ?, ?)",
            music_group_data
        )
        connection.commit()

        # insert group_artist_data
        print("Inserting group artist data...")
        cursor.executemany(
            "INSERT INTO GroupArtist (group_id, artist_id) VALUES (?, ?)",
            group_artist_data
        )
        connection.commit()

        # insert history_data
        print("Inserting history data...")
        cursor.executemany(
            "INSERT INTO History (user_id, song_id, start_time) VALUES (?, ?, ?)",
            history_data
        )
        connection.commit()

        # Add missing artists to the Artist table
        missing_artists = [
            ('John Paul Jones', 'UK', 'Bass'),
            ('John Bonham', 'UK', 'Drums'),
            ('Syd Barrett', 'UK', 'Guitar'),
            ('Roger Waters', 'UK', 'Bass'),
            ('David Gilmour', 'UK', 'Guitar'),
            ('Nick Mason', 'UK', 'Drums'),
            ('Richard Wright', 'UK', 'Keyboard'),
            ('James Hetfield', 'USA', 'Vocals'),
            ('Lars Ulrich', 'Denmark', 'Drums'),
            ('Kirk Hammett', 'USA', 'Guitar'),
            ('Robert Trujillo', 'USA', 'Bass'),
            ('Don Henley', 'USA', 'Vocals'),
            ('Glenn Frey', 'USA', 'Guitar'),
            ('Randy Meisner', 'USA', 'Bass'),
            ('Don Felder', 'USA', 'Guitar'),
            ('Mick Fleetwood', 'UK', 'Drums'),
            ('John McVie', 'UK', 'Bass'),
            ('Christine McVie', 'UK', 'Keyboard'),
            ('Stevie Nicks', 'USA', 'Vocals'),
            ('Krist Novoselic', 'USA', 'Bass'),
            ('Dave Grohl', 'USA', 'Drums')
        ]

        # Insert missing artists
        print("Inserting missing artists...")
        cursor.executemany(
            "INSERT INTO Artist (full_name, origin_country, instrument) VALUES (?, ?, ?)",
            missing_artists
        )
        connection.commit()

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


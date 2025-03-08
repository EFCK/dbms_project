# SUPERTIFY - Music Streaming Platform

## Overview

SUPERTIFY is a comprehensive music streaming database and API project that allows users to manage and explore music collections, create playlists, follow artists, and track listening history. The platform is designed to provide a robust backend for music streaming applications with a focus on data integrity and performance.

## Key Features

- **User Management**: Create and manage user profiles with personalized preferences
- **Music Library**: Comprehensive database of songs, albums, artists, and genres
- **Playlist Creation**: Build and share custom playlists
- **Social Features**: Follow other users and see their activity
- **Listening History**: Track what users listen to and when
- **Analytics**: Built-in queries for music streaming statistics
- **REST API**: Complete API for accessing all functionality programmatically

## Technology Stack

- **Database**: SQLite with comprehensive schema design
- **API Framework**: Flask with Flask-RESTX for automatic documentation
- **Authentication**: JWT-based authentication system
- **Data Validation**: Type checking and validation using Flask-RESTX models
- **Documentation**: Auto-generated Swagger documentation

## Database Schema

The database is designed with the following key entities:

- **User/Account**: Store user information and authentication details
- **Song/Album/Artist**: Hierarchical music catalog structure
- **Genre**: Categorization of music by style
- **Playlist**: User-created collections of songs
- **History**: Record of user listening activity

## API Endpoints

The API provides endpoints for:

- User registration and authentication
- CRUD operations for all entities (users, songs, albums, etc.)
- Playlist management
- Social features (following users)
- Listening history
- Music statistics and analytics

## Sample Usage

### Authentication

```bash
# Register a new user
curl -X POST "http://localhost:5000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"username": "example_user", "password": "secure_password"}'

# Login to get JWT token
curl -X POST "http://localhost:5000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "example_user", "password": "secure_password"}'
```

### Creating a Playlist

```bash
# With a valid JWT token
curl -X POST "http://localhost:5000/playlists" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "playlist_name": "My Awesome Playlist",
    "playlist_description": "A collection of my favorite tracks",
    "creator_id": "user_id_here"
  }'
```

## Project Structure

- `milestone3/`: Core project implementation
  - `api.py`: Main API implementation
  - `statements.py`: SQL statements for database creation
  - `dummy_data_insertion.py`: Scripts for populating test data

## Contributions

This project was developed as a database management systems educational project, with a focus on database design, SQL query optimization, and RESTful API development.

## Installation

For installation instructions, see the [Installation Guide](how_to_install.md) 
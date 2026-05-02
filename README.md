# Media Tracker Backend

Backend API for Media Tracker, a private platform designed to manage the music and movie backlog of a closed social circle. Built with Django and Django REST Framework (DRF).

## Features

- **JWT Authentication**: Secure user authentication using JSON Web Tokens.
- **Global Catalog**: Centralized database for movies and albums to avoid duplicates.
- **External API Integrations**: Syncs data from Spotify (music) and TMDb (movies) and caches it locally.
- **Group Isolation**: Architecture ready to manage media lists by custom user groups (e.g., family, friends).
- **Domain-Driven Design (DDD)**: Logic resides in the services layer (`services.py`) keeping views and serializers clean.

## Tech Stack

- Python 3.11+
- Django 5.x
- Django REST Framework (DRF)
- PostgreSQL
- SimpleJWT

## Setup Instructions

1. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   # On Windows use: 
   .\venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Variables:**
   Create a `.env` file in the root directory:
   ```env
   SECRET_KEY=your_secret_key
   DEBUG=True
   
   DB_NAME=mediatracker_db
   DB_USER=mediatracker
   DB_PASSWORD=mediatracker_pass
   DB_HOST=127.0.0.1
   DB_PORT=5432
   
   REGISTRATION_SECRET_KEY=your_registration_secret
   
   SPOTIFY_CLIENT_ID=your_spotify_id
   SPOTIFY_CLIENT_SECRET=your_spotify_secret
   
   TMDB_API_KEY=your_tmdb_key
   ```

4. **Run Migrations:**
   ```bash
   python manage.py migrate
   ```

5. **Start Development Server:**
   ```bash
   python manage.py runserver
   ```

import requests
from typing import Tuple, List, Dict, Any
from django.conf import settings
from rest_framework.exceptions import PermissionDenied, APIException
from rest_framework_simplejwt.tokens import RefreshToken
from django.db import transaction
from .models import User, Album, Artist, Movie, CustomGroup

def register_user(validated_data: dict) -> Tuple[User, str, str]:
    """
    Registra un usuario validando el código de invitación.
    Retorna el usuario creado, refresh_token y access_token.
    """
    invitation_code = validated_data.pop('invitation_code', None)
    
    if invitation_code != settings.REGISTRATION_SECRET_KEY:
        raise PermissionDenied("Código de invitación inválido.")
        
    with transaction.atomic():
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        
        # Crear grupo personal automático para el usuario
        personal_group = CustomGroup.objects.create(name=f"Mi Catálogo ({user.username})")
        personal_group.members.add(user)
    
    # Generar JWT para el nuevo usuario
    refresh = RefreshToken.for_user(user)
    
    return user, str(refresh), str(refresh.access_token)

def get_spotify_access_token() -> str:
    """
    Obtiene un access token de Spotify usando las credenciales del cliente.
    """
    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "client_credentials",
        "client_id": settings.SPOTIFY_CLIENT_ID,
        "client_secret": settings.SPOTIFY_CLIENT_SECRET,
    }
    
    response = requests.post(url, headers=headers, data=data)
    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        raise APIException("Error al autenticar con Spotify API.")

def search_spotify_albums(query: str) -> List[Dict[str, Any]]:
    """
    Busca álbumes en Spotify por término de búsqueda.
    """
    token = get_spotify_access_token()
    url = "https://api.spotify.com/v1/search"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    params = {
        "q": query,
        "type": "album",
        "limit": 10
    }
    
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json().get("albums", {}).get("items", [])
    else:
        raise APIException("Error al buscar en Spotify API.")

def search_tmdb_movies(query: str) -> List[Dict[str, Any]]:
    """
    Busca películas en TMDb por término de búsqueda.
    """
    url = "https://api.themoviedb.org/3/search/movie"
    params = {
        "api_key": settings.TMDB_API_KEY,
        "query": query,
        "language": "es-ES",
        "page": 1,
        "include_adult": False
    }
    
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json().get("results", [])
    else:
        raise APIException("Error al buscar en TMDb API.")

def get_or_create_spotify_album(spotify_id: str) -> Album:
    """
    Busca un álbum por su ID en la BD local. Si no existe, lo descarga de Spotify y lo guarda.
    """
    try:
        return Album.objects.get(spotify_id=spotify_id)
    except Album.DoesNotExist:
        pass
        
    token = get_spotify_access_token()
    url = f"https://api.spotify.com/v1/albums/{spotify_id}"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise APIException("Error al obtener detalle del álbum en Spotify API.")
        
    data = response.json()
    
    with transaction.atomic():
        artist_data = data.get('artists', [{}])[0]
        artist_spotify_id = artist_data.get('id')
        artist_name = artist_data.get('name', 'Unknown Artist')
        
        artist, _ = Artist.objects.get_or_create(
            spotify_id=artist_spotify_id,
            defaults={'name': artist_name}
        )
        
        genres = data.get('genres', [])
        
        images = data.get('images', [])
        cover_url = images[0].get('url') if images else None
        
        release_date_str = data.get('release_date')
        release_date = release_date_str if release_date_str and len(release_date_str) == 10 else None
        
        album = Album.objects.create(
            title=data.get('name', 'Unknown Title'),
            artist=artist,
            spotify_id=spotify_id,
            cover_url=cover_url,
            genres=genres,
            release_date=release_date
        )
        return album

def get_or_create_tmdb_movie(tmdb_id: str) -> Movie:
    """
    Busca una película por su ID en la BD local. Si no existe, la descarga de TMDb y la guarda.
    """
    try:
        return Movie.objects.get(tmdb_id=tmdb_id)
    except Movie.DoesNotExist:
        pass
        
    url = f"https://api.themoviedb.org/3/movie/{tmdb_id}"
    params = {
        "api_key": settings.TMDB_API_KEY,
        "language": "es-ES"
    }
    
    response = requests.get(url, params=params)
    if response.status_code != 200:
        raise APIException("Error al obtener detalle de la película en TMDb API.")
        
    data = response.json()
    
    with transaction.atomic():
        genres_data = data.get('genres', [])
        genres = [g.get('name') for g in genres_data]
        
        poster_path = data.get('poster_path')
        poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else None
        
        release_date = data.get('release_date')
        if not release_date:
            release_date = None
            
        movie = Movie.objects.create(
            title=data.get('title', 'Unknown Title'),
            tmdb_id=tmdb_id,
            poster_url=poster_url,
            synopsis=data.get('overview', ''),
            genres=genres,
            release_date=release_date
        )
        return movie

def add_album_to_group(group_id: int, album: Album, user: User) -> 'GroupAlbum':
    from .models import CustomGroup, GroupAlbum
    group = CustomGroup.objects.get(id=group_id)
    group_album, created = GroupAlbum.objects.get_or_create(
        group=group,
        album=album,
        defaults={'added_by': user, 'status': 'pending'}
    )
    return group_album

def add_movie_to_group(group_id: int, movie: Movie, user: User) -> 'GroupMovie':
    from .models import CustomGroup, GroupMovie
    group = CustomGroup.objects.get(id=group_id)
    group_movie, created = GroupMovie.objects.get_or_create(
        group=group,
        movie=movie,
        defaults={'added_by': user, 'status': 'pending'}
    )
    return group_movie

def mark_group_album_completed(group_album_id: int) -> 'GroupAlbum':
    from .models import GroupAlbum
    group_album = GroupAlbum.objects.get(id=group_album_id)
    group_album.mark_as_completed()
    return group_album

def mark_group_movie_completed(group_movie_id: int) -> 'GroupMovie':
    from .models import GroupMovie
    group_movie = GroupMovie.objects.get(id=group_movie_id)
    group_movie.mark_as_completed()
    return group_movie

def create_or_update_review(user: User, rating: int, comment: str, album_id: int = None, movie_id: int = None) -> 'UserReview':
    from .models import UserReview
    if album_id:
        review, created = UserReview.objects.update_or_create(
            user=user, album_id=album_id,
            defaults={'rating': rating, 'comment': comment, 'movie': None}
        )
    elif movie_id:
        review, created = UserReview.objects.update_or_create(
            user=user, movie_id=movie_id,
            defaults={'rating': rating, 'comment': comment, 'album': None}
        )
    else:
        raise ValueError("Debe proporcionar album_id o movie_id")
    return review

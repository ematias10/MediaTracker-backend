from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    # AbstractUser ya incluye username, password, email, first_name, last_name, is_active, etc.
    
    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"

class CustomGroup(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nombre del Grupo")
    members = models.ManyToManyField(User, related_name="custom_groups", verbose_name="Miembros")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")

    class Meta:
        verbose_name = "Grupo Personalizado"
        verbose_name_plural = "Grupos Personalizados"

    def __str__(self):
        return self.name

class Artist(models.Model):
    name = models.CharField(max_length=255, verbose_name="Nombre")
    spotify_id = models.CharField(max_length=255, unique=True, null=True, blank=True, verbose_name="ID de Spotify")
    genres = models.JSONField(default=list, blank=True, verbose_name="Géneros")

    class Meta:
        verbose_name = "Artista"
        verbose_name_plural = "Artistas"

    def __str__(self):
        return self.name

class Album(models.Model):
    title = models.CharField(max_length=255, verbose_name="Título")
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name="albums", verbose_name="Artista")
    spotify_id = models.CharField(max_length=255, unique=True, verbose_name="ID de Spotify")
    cover_url = models.URLField(max_length=500, null=True, blank=True, verbose_name="URL de Portada")
    genres = models.JSONField(default=list, blank=True, verbose_name="Géneros")
    release_date = models.DateField(null=True, blank=True, verbose_name="Fecha de Lanzamiento")

    class Meta:
        verbose_name = "Álbum"
        verbose_name_plural = "Álbumes"

    def __str__(self):
        return f"{self.title} - {self.artist.name}"

class Movie(models.Model):
    title = models.CharField(max_length=255, verbose_name="Título")
    tmdb_id = models.CharField(max_length=255, unique=True, verbose_name="ID de TMDb")
    poster_url = models.URLField(max_length=500, null=True, blank=True, verbose_name="URL de Póster")
    synopsis = models.TextField(blank=True, verbose_name="Sinopsis")
    genres = models.JSONField(default=list, blank=True, verbose_name="Géneros")
    release_date = models.DateField(null=True, blank=True, verbose_name="Fecha de Lanzamiento")

    class Meta:
        verbose_name = "Película"
        verbose_name_plural = "Películas"

    def __str__(self):
        return self.title

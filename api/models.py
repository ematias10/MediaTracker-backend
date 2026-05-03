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

class GroupAlbum(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('completed', 'Completado'),
    ]

    group = models.ForeignKey(CustomGroup, on_delete=models.CASCADE, related_name="albums", verbose_name="Grupo")
    album = models.ForeignKey(Album, on_delete=models.CASCADE, verbose_name="Álbum")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Estado")
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="Agregado por")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")

    class Meta:
        unique_together = ('group', 'album')
        verbose_name = "Álbum de Grupo"
        verbose_name_plural = "Álbumes de Grupos"

    def mark_as_completed(self):
        if self.status == 'completed':
            from django.core.exceptions import ValidationError
            raise ValidationError("Este álbum ya está completado en este grupo.")
        self.status = 'completed'
        self.save(update_fields=['status'])

class GroupMovie(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('completed', 'Completado'),
    ]

    group = models.ForeignKey(CustomGroup, on_delete=models.CASCADE, related_name="movies", verbose_name="Grupo")
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, verbose_name="Película")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Estado")
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="Agregado por")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")

    class Meta:
        unique_together = ('group', 'movie')
        verbose_name = "Película de Grupo"
        verbose_name_plural = "Películas de Grupos"
        
    def mark_as_completed(self):
        if self.status == 'completed':
            from django.core.exceptions import ValidationError
            raise ValidationError("Esta película ya está completada en este grupo.")
        self.status = 'completed'
        self.save(update_fields=['status'])

class UserReview(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews", verbose_name="Usuario")
    album = models.ForeignKey(Album, on_delete=models.CASCADE, null=True, blank=True, related_name="reviews", verbose_name="Álbum")
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, null=True, blank=True, related_name="reviews", verbose_name="Película")
    rating = models.PositiveSmallIntegerField(verbose_name="Calificación")
    comment = models.TextField(blank=True, verbose_name="Comentario")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")

    class Meta:
        verbose_name = "Reseña de Usuario"
        verbose_name_plural = "Reseñas de Usuarios"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(rating__gte=1) & models.Q(rating__lte=5),
                name="rating_range"
            ),
            models.CheckConstraint(
                condition=(models.Q(album__isnull=False) & models.Q(movie__isnull=True)) | 
                          (models.Q(album__isnull=True) & models.Q(movie__isnull=False)),
                name="review_target_exclusive"
            )
        ]

    def __str__(self):
        target = self.album.title if self.album else self.movie.title
        return f"{self.user.username} - {target} ({self.rating}/5)"


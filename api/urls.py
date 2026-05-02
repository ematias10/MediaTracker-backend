from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    RegisterView, SearchMusicView, SearchMoviesView, 
    CatalogMusicView, CatalogMoviesView
)

urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    path('search/music/', SearchMusicView.as_view(), name='search_music'),
    path('search/movies/', SearchMoviesView.as_view(), name='search_movies'),
    
    path('catalog/music/', CatalogMusicView.as_view(), name='catalog_music'),
    path('catalog/movies/', CatalogMoviesView.as_view(), name='catalog_movies'),
]

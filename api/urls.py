from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    RegisterView, SearchMusicView, SearchMoviesView, 
    CatalogMusicView, CatalogMoviesView,
    UserGroupsView, GroupAlbumsView, GroupMoviesView,
    CompleteGroupAlbumView, CompleteGroupMovieView, ReviewView
)

urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    path('search/music/', SearchMusicView.as_view(), name='search_music'),
    path('search/movies/', SearchMoviesView.as_view(), name='search_movies'),
    
    path('catalog/music/', CatalogMusicView.as_view(), name='catalog_music'),
    path('catalog/movies/', CatalogMoviesView.as_view(), name='catalog_movies'),
    
    # Groups & Lists
    path('groups/', UserGroupsView.as_view(), name='user_groups'),
    path('groups/<int:group_id>/albums/', GroupAlbumsView.as_view(), name='group_albums'),
    path('groups/<int:group_id>/movies/', GroupMoviesView.as_view(), name='group_movies'),
    
    # Complete Actions
    path('groups/albums/<int:pk>/complete/', CompleteGroupAlbumView.as_view(), name='complete_group_album'),
    path('groups/movies/<int:pk>/complete/', CompleteGroupMovieView.as_view(), name='complete_group_movie'),
    
    # Reviews
    path('reviews/', ReviewView.as_view(), name='reviews'),
]

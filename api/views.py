from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import CustomGroup, GroupAlbum, GroupMovie, Album, Movie
from .serializers import RegisterSerializer, AlbumSerializer, MovieSerializer, GroupAlbumSerializer, GroupMovieSerializer, CustomGroupSerializer, UserReviewSerializer
from .services import register_user, search_spotify_albums, search_tmdb_movies, get_or_create_spotify_album, get_or_create_tmdb_movie, add_album_to_group, add_movie_to_group, mark_group_album_completed, mark_group_movie_completed, create_or_update_review

class RegisterView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            # register_user raises PermissionDenied (403) if code is invalid
            user, refresh_token, access_token = register_user(serializer.validated_data)
            
            return Response({
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                },
                "refresh": refresh_token,
                "access": access_token
            }, status=status.HTTP_201_CREATED)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SearchMusicView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        query = request.query_params.get('q', '')
        group_id = request.query_params.get('group_id')
        if not query:
            return Response({"error": "Se requiere el parámetro 'q'."}, status=status.HTTP_400_BAD_REQUEST)
        
        results = search_spotify_albums(query)
        
        if group_id:
            existing_ids = GroupAlbum.objects.filter(
                group_id=group_id,
                album__spotify_id__in=[item['id'] for item in results]
            ).values_list('album__spotify_id', flat=True)
            for item in results:
                item['already_in_group'] = item['id'] in existing_ids
                
        return Response(results)

class SearchMoviesView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        query = request.query_params.get('q', '')
        group_id = request.query_params.get('group_id')
        if not query:
            return Response({"error": "Se requiere el parámetro 'q'."}, status=status.HTTP_400_BAD_REQUEST)
            
        results = search_tmdb_movies(query)
        
        if group_id:
            existing_ids = GroupMovie.objects.filter(
                group_id=group_id,
                movie__tmdb_id__in=[str(item['id']) for item in results]
            ).values_list('movie__tmdb_id', flat=True)
            for item in results:
                item['already_in_group'] = str(item['id']) in existing_ids
                
        return Response(results)

class CatalogMusicView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        spotify_id = request.data.get('spotify_id')
        if not spotify_id:
            return Response({"error": "Se requiere 'spotify_id'."}, status=status.HTTP_400_BAD_REQUEST)
        album = get_or_create_spotify_album(spotify_id)
        serializer = AlbumSerializer(album)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class CatalogMoviesView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        tmdb_id = request.data.get('tmdb_id')
        if not tmdb_id:
            return Response({"error": "Se requiere 'tmdb_id'."}, status=status.HTTP_400_BAD_REQUEST)
        movie = get_or_create_tmdb_movie(tmdb_id)
        serializer = MovieSerializer(movie)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class UserGroupsView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        groups = request.user.custom_groups.all()
        serializer = CustomGroupSerializer(groups, many=True)
        return Response(serializer.data)
        
    def post(self, request):
        name = request.data.get('name')
        if not name:
            return Response({"error": "Nombre del grupo requerido."}, status=status.HTTP_400_BAD_REQUEST)
        
        group = CustomGroup.objects.create(name=name)
        group.members.add(request.user)
        serializer = CustomGroupSerializer(group)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class GroupAlbumsView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, group_id):
        group = get_object_or_404(CustomGroup, id=group_id, members=request.user)
        # N+1 optimization
        group_albums = GroupAlbum.objects.filter(group=group).select_related('album', 'album__artist', 'added_by').order_by('-created_at')
        serializer = GroupAlbumSerializer(group_albums, many=True)
        return Response(serializer.data)
        
    def post(self, request, group_id):
        group = get_object_or_404(CustomGroup, id=group_id, members=request.user)
        spotify_id = request.data.get('spotify_id')
        if not spotify_id:
            return Response({"error": "Se requiere 'spotify_id'."}, status=status.HTTP_400_BAD_REQUEST)
        
        album = get_or_create_spotify_album(spotify_id)
        group_album = add_album_to_group(group.id, album, request.user)
        serializer = GroupAlbumSerializer(group_album)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class GroupMoviesView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, group_id):
        group = get_object_or_404(CustomGroup, id=group_id, members=request.user)
        group_movies = GroupMovie.objects.filter(group=group).select_related('movie', 'added_by').order_by('-created_at')
        serializer = GroupMovieSerializer(group_movies, many=True)
        return Response(serializer.data)
        
    def post(self, request, group_id):
        group = get_object_or_404(CustomGroup, id=group_id, members=request.user)
        tmdb_id = request.data.get('tmdb_id')
        if not tmdb_id:
            return Response({"error": "Se requiere 'tmdb_id'."}, status=status.HTTP_400_BAD_REQUEST)
        
        movie = get_or_create_tmdb_movie(tmdb_id)
        group_movie = add_movie_to_group(group.id, movie, request.user)
        serializer = GroupMovieSerializer(group_movie)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class CompleteGroupAlbumView(APIView):
    permission_classes = [IsAuthenticated]
    def patch(self, request, pk):
        group_album = get_object_or_404(GroupAlbum, pk=pk, group__members=request.user)
        try:
            group_album = mark_group_album_completed(pk)
            serializer = GroupAlbumSerializer(group_album)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class CompleteGroupMovieView(APIView):
    permission_classes = [IsAuthenticated]
    def patch(self, request, pk):
        group_movie = get_object_or_404(GroupMovie, pk=pk, group__members=request.user)
        try:
            group_movie = mark_group_movie_completed(pk)
            serializer = GroupMovieSerializer(group_movie)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class ReviewView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        album_id = request.data.get('album_id')
        movie_id = request.data.get('movie_id')
        rating = request.data.get('rating')
        comment = request.data.get('comment', '')
        
        if not rating or not (1 <= int(rating) <= 5):
            return Response({"error": "Calificación válida requerida (1-5)."}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            review = create_or_update_review(request.user, int(rating), comment, album_id, movie_id)
            serializer = UserReviewSerializer(review)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

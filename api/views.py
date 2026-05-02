from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import RegisterSerializer, AlbumSerializer, MovieSerializer
from .services import register_user, search_spotify_albums, search_tmdb_movies, get_or_create_spotify_album, get_or_create_tmdb_movie

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
        if not query:
            return Response({"error": "Se requiere el parámetro 'q'."}, status=status.HTTP_400_BAD_REQUEST)
        results = search_spotify_albums(query)
        return Response(results)

class SearchMoviesView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        query = request.query_params.get('q', '')
        if not query:
            return Response({"error": "Se requiere el parámetro 'q'."}, status=status.HTTP_400_BAD_REQUEST)
        results = search_tmdb_movies(query)
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

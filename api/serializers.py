from rest_framework import serializers
from .models import User, Artist, Album, Movie, GroupAlbum, GroupMovie, UserReview, CustomGroup
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    invitation_code = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'first_name', 'last_name', 'invitation_code')

class ArtistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Artist
        fields = '__all__'

class AlbumSerializer(serializers.ModelSerializer):
    artist = ArtistSerializer(read_only=True)
    class Meta:
        model = Album
        fields = '__all__'

class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = '__all__'

class UserReviewSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    class Meta:
        model = UserReview
        fields = ('id', 'username', 'rating', 'comment', 'created_at')

class GroupAlbumSerializer(serializers.ModelSerializer):
    album = AlbumSerializer(read_only=True)
    added_by_name = serializers.CharField(source='added_by.username', read_only=True)
    class Meta:
        model = GroupAlbum
        fields = ('id', 'album', 'status', 'added_by_name', 'created_at')

class GroupMovieSerializer(serializers.ModelSerializer):
    movie = MovieSerializer(read_only=True)
    added_by_name = serializers.CharField(source='added_by.username', read_only=True)
    class Meta:
        model = GroupMovie
        fields = ('id', 'movie', 'status', 'added_by_name', 'created_at')

class CustomGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomGroup
        fields = ('id', 'name')

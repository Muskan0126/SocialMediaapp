from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from apps.common.validators import validate_image
from apps.post.models import Comment, Follow, Post, Story
import re

class CreatePostSerializer(serializers.ModelSerializer):
    picture = serializers.ImageField(
        validators=[validate_image]
    )
    class Meta:
        model = Post
        fields = [
            "picture",
            "caption",
        ]

    def validate_caption(self, value):

        if len(value) > 2200:
            raise serializers.ValidationError(
                "Caption cannot exceed 2200 characters."
            )

        return value
    
class PostListSerializer(serializers.ModelSerializer):

    username = serializers.CharField(
        source="user.username",
        read_only=True
    )

    profile_photo = serializers.ImageField(
        source="user.profile_photo",
        read_only=True
    )

    likes = serializers.SerializerMethodField()

    comments = serializers.SerializerMethodField()

    class Meta:

        model = Post

        fields = [
            "id",
            "username",
            "profile_photo",
            "picture",
            "caption",
            "likes",
            "comments",
            "posted",
        ]

    def get_likes(self, obj):

        return obj.post_likes.count()

    def get_comments(self, obj):

        return obj.comments.count()
    
class UpdatePostSerializer(serializers.ModelSerializer):

    class Meta:
        model = Post
        fields = [
            "caption",
        ]

    def validate_caption(self, value):

        if len(value) > 2200:
            raise serializers.ValidationError(
                "Caption cannot exceed 2200 characters."
            )
        return value
    
class CreateStorySerializer(serializers.ModelSerializer):
    image = serializers.ImageField(
        validators=[validate_image]
    )
    class Meta:
        model = Story
        fields = [
            "image"
        ]

class CommentSerializer(serializers.ModelSerializer):

    username = serializers.CharField(
        source="User.username",
        read_only=True
    )

    class Meta:
        model = Comment
        fields = [
            "id",
            "comment",
            "parent",
            "username",
            "date_commented",
        ]

        read_only_fields = [
            "id",
            "username",
            "date_commented",
        ]
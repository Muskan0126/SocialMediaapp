
import uuid
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .serializers import CommentSerializer, CreatePostSerializer, CreateStorySerializer, PostListSerializer, UpdatePostSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import get_object_or_404
from apps.post.models import Follow, Likes, Post, Story
from apps.useraccount.models import User

class CreatePostAPIView(APIView):
# /api/posts/create/
    permission_classes = [IsAuthenticated]

    def post(self, request):

        serializer = CreatePostSerializer(
            data=request.data
        )

        if serializer.is_valid():

            serializer.save(
                user=request.user
            )
            post = serializer.save(user=request.user)
            return Response(

                {
                    "message": "Post created successfully.",
                    "data": {
                        "id": post.id,
                        **serializer.data
                    }
                },

                status=status.HTTP_201_CREATED

            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
    
class PostListAPIView(APIView):
    # api/posts/
    def get(self,request):
  
        queryset = (
            Post.objects
            .select_related("user")
            .prefetch_related("post_likes")
            .order_by("-posted")
        )
        serializer_class = PostListSerializer(queryset,many= True)
        return Response(serializer_class.data)
    
class UpdatePostAPIView(APIView):
#/api/posts/post-update/27/
    permission_classes = [IsAuthenticated]

    def patch(self, request,pk):
        post = get_object_or_404(Post, id=pk)
        
        if post.user != request.user:
            return Response(
                {"detail": "You do not have permission to edit this post."}, 
                status=status.HTTP_403_FORBIDDEN
            )
        serializer = UpdatePostSerializer(
            post,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors)
    
class DeletePostAPIView(APIView):
#/api/posts/post-delete/27/
    permission_classes = [IsAuthenticated]

    def delete(self, request,pk):
        post = get_object_or_404(Post, id=pk)
        
        if post.user != request.user:
            return Response(
                {"detail": "You do not have permission to delete this post."}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        post.delete()
        return Response({"detail": "Post deleted successfully."}, 
                status=status.HTTP_200_OK)

class CreateStoryAPIView(APIView):
# /api/posts/story-create/
    permission_classes = [IsAuthenticated]

    def post(self, request):
        
        serializer = CreateStorySerializer(
            data=request.data
        )

        if serializer.is_valid():

            serializer.save(
                user=request.user
            )
            story = serializer.save(user=request.user)
            return Response(

                {
                    "message": "Story created successfully.",
                    "data": {
                        "id": story.id,
                        **serializer.data
                    }
                },

                status=status.HTTP_201_CREATED

            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
    
class LikeAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):

        try:
            post = Post.objects.get(id=post_id)

        except Post.DoesNotExist:

            return Response(
                {
                    "message": "Post not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        like = Likes.objects.filter(
            user=request.user,
            post=post
        )

        if like.exists():

            like.delete()

            return Response(
                {
                    "liked": False,
                    "likes_count": post.post_likes.count(),
                    "message": "Post unliked successfully."
                }
            )

        Likes.objects.create(
            user=request.user,
            post=post
        )

        return Response(
            {
                "liked": True,
                "likes_count": post.post_likes.count(),
                "message": "Post liked successfully."
            }
        )
    

class FollowAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, id):

        user_to_follow = get_object_or_404(
            User,
            id=id
        )

        if request.user == user_to_follow:

            return Response(
                {
                    "message": "You cannot follow yourself."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        follow = Follow.objects.filter(
            follower=request.user,
            following=user_to_follow
        )

        if follow.exists():

            follow.delete()

            return Response(
                {
                    "following": False,
                    "followers": Follow.objects.filter(
                        following=user_to_follow
                    ).count(),
                    "message": "Unfollowed successfully."
                }
            )

        Follow.objects.create(
            follower=request.user,
            following=user_to_follow
        )

        return Response(
            {
                "following": True,
                "followers": Follow.objects.filter(
                    following=user_to_follow
                ).count(),
                "message": "Followed successfully."
            }
        )
    
class DeleteStoryAPIView(APIView):
#/api/posts/story-delete/27/
    permission_classes = [IsAuthenticated]

    def delete(self, request,pk):
        story = get_object_or_404(Story, id=pk)
        
        if story.user != request.user:
            return Response(
                {"detail": "You do not have permission to delete this story."}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        story.delete()
        return Response({"detail": "story deleted successfully."}, 
                status=status.HTTP_200_OK)

class CommentAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):

        post = get_object_or_404(
            Post,
            id=post_id
        )

        serializer = CommentSerializer(
            data=request.data
        )

        if serializer.is_valid():

            serializer.save(
                id = str(uuid.uuid4())[:25],
                author=request.user,
                item=post
            )

            return Response(
                {
                    "message": "Comment added successfully.",
                    "data": serializer.data
                },
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
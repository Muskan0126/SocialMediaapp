from django.urls import path

from apps.post.apis.views import CommentAPIView, CreatePostAPIView, CreateStoryAPIView, DeletePostAPIView, DeleteStoryAPIView, FollowAPIView, LikeAPIView,PostListAPIView, UpdatePostAPIView

urlpatterns = [
 path("create/",CreatePostAPIView.as_view(),name="create-post"),# /api/posts/create/
 path('',PostListAPIView.as_view(),name="post-list"),# /api/posts/
 path("post-update/<int:pk>/",UpdatePostAPIView.as_view(),name="post-update"),# /api/posts/post-update/2/
 path("post-delete/<int:pk>/",DeletePostAPIView.as_view(),name="post-delete"),# /api/posts/post-delete/2/
 path("story-create/",CreateStoryAPIView.as_view(),name="create-story"),# /api/posts/story-create/
 path("<int:post_id>/like/",LikeAPIView.as_view(),name="like"),# /api/posts/28/like/
 path("<int:id>/follow/",FollowAPIView.as_view(),name="follow"),#/api/posts/61/follow/  
 path("<int:post_id>/comment/",CommentAPIView.as_view(),name="follow"),#/ap/posts/28/comment/i    
 path("story-delete/<int:pk>/",DeleteStoryAPIView.as_view(),name="post-delete"),# /api/posts/story-delete/2/
]
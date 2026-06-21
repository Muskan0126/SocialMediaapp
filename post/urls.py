from django.urls import path

from useraccount.views import forgot_password_view

from .views import (
    edit_profile,
    home_view,
    create_post_view,
    create_story_view,
    like_post, my_posts_view, delete_post_view, delete_story_view,
    profile_view,
    delete_account_view,
    follow_user,
    notifications_view,
    add_comment,
    delete_comment_view,
    edit_caption_view,
)

urlpatterns = [

    path("",home_view.as_view(),name="home"),

    path("create-post/",create_post_view.as_view(),name="create_post"),
    path(
        "create-story/",
        create_story_view.as_view(),
        name="create_story"
    ),

    path(
        "my-posts/",
        my_posts_view.as_view(),
        name="my_posts"
    ),

    path(
        "delete-post/<int:post_id>/",
        delete_post_view.as_view(),
        name="delete_post"
    ),

    path(
        "delete-story/<int:story_id>/",
        delete_story_view.as_view(),
        name="delete_story"
    ),
    path(
        "profile-view",
        profile_view.as_view(),
        name = "profile_view"
    ),
    path(
        "edit-profile",
        edit_profile.as_view(),
        name="edit_profile"
    ),
    path(
        "delete-account/",
        delete_account_view.as_view(),
        name="delete_account"
    ),
    path(
        "like/<int:post_id>/",
        like_post.as_view(),
        name="like_post"
    ),
    path(
        "follow/<int:user_id>/",
        follow_user.as_view(),
        name="follow_user"
    ),
    path(
        "notifications/",
        notifications_view.as_view(),
        name="notifications"
    ),
    path(
        "comment/<int:post_id>/",
        add_comment.as_view(),
        name="add_comment"
    ),
    path(
        "comment/delete/<str:comment_id>/",
        delete_comment_view.as_view(),
        name="delete_comment"
    ),
    path(
        "edit-caption/<int:post_id>/",
        edit_caption_view.as_view(),
        name="edit_caption"
    ),
]

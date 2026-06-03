from django.urls import path

from .views import (
    edit_profile,
    home_view,
    create_post_view,
    create_story_view,my_posts_view,delete_post_view,delete_story_view,
    profile_view
)

urlpatterns = [

    path("",home_view,name="home"),

    path("create-post/",create_post_view,name="create_post"),
    path(
        "create-story/",
        create_story_view,
        name="create_story"
    ),

    path(
        "my-posts/",
        my_posts_view,
        name="my_posts"
    ),

    path(
        "delete-post/<int:post_id>/",
        delete_post_view,
        name="delete_post"
    ),

    path(
        "delete-story/<int:story_id>/",
        delete_story_view,
        name="delete_story"
    ),
    path(
        "profile-view",
        profile_view,
        name = "profile_view"
    ),
    path(
        "edit-profile",
        edit_profile,
        name = "edit_profile"
    ),

]
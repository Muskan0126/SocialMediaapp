from django.shortcuts import (
    render,
    redirect,
    get_object_or_404
)

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from .models import (
    Post,
    Story,
    Follow,
)
from .forms import EditProfileForm, PostForm, StoryForm
import pdb

@login_required
def home_view(request):

    stories = Story.objects.select_related("user").all()
    posts = Post.objects.select_related("user").all()
    context = {
        "stories": stories,
        "posts": posts}
    return render(
        request,
        "post/home.html",
        context
    )

@login_required
def create_post_view(request):

    form = PostForm()

    if request.method == "POST":

        form = PostForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            post = form.save(commit=False)
            post.user = request.user
            post.save()

            messages.success(
                request,
                "Post uploaded successfully."
            )
            return redirect(
                "home"
            )
    return render(
        request,
        "post/create_post.html",
        {
            "form": form
        }
    )

@login_required
def create_story_view(request):

    form = StoryForm()

    if request.method == "POST":

        form = StoryForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            story = form.save(
                commit=False
            )

            story.user = request.user

            story.save()

            messages.success(
                request,
                "Story uploaded successfully."
            )

            return redirect(
                "home"
            )

    return render(
        request,
        "post/create_story.html",
        {
            "form": form
        }
    )


@login_required
def my_posts_view(request):

    posts = Post.objects.filter(
        user=request.user
    )

    return render(
        request,
        "post/my_posts.html",
        {
            "posts": posts
        }
    )


@login_required
def delete_post_view(request, post_id):

    post = get_object_or_404(
        Post,
        id=post_id,
        user=request.user
    )

    post.delete()

    messages.success(
        request,
        "Post deleted successfully."
    )

    return redirect(
        "my_posts"
    )


@login_required
def delete_story_view(request, story_id):

    story = get_object_or_404(
        Story,
        id=story_id,
        user=request.user
    )

    story.delete()

    messages.success(
        request,
        "Story deleted successfully."
    )

    return redirect(
        "home"
    )

@login_required
def profile_view(request):

    posts = (
        Post.objects
        .filter(user=request.user)
        .select_related("user")
    )

    paginator = Paginator(
        posts,
        9
    )

    page_number = request.GET.get(
        "page"
    )

    page_obj = paginator.get_page(
        page_number
    )

    followers_count = (
        Follow.objects.filter(
            following=request.user
        ).count()
    )

    following_count = (
        Follow.objects.filter(
            follower=request.user
        ).count()
    )

    posts_count = posts.count()

    context = {

        "page_obj": page_obj,

        "followers_count":
            followers_count,

        "following_count":
            following_count,

        "posts_count":
            posts_count,
    }

    return render(
        request,
        "post/profile_view.html",
        context
    )
    
    
@login_required
def edit_profile(request):
   
    form = EditProfileForm(
        instance=request.user
    )

    if request.method == "POST":

        form = EditProfileForm(
            request.POST,
            request.FILES,
            instance=request.user
        )

        if form.is_valid():

            form.save()

            return redirect(
                "profile_view"
            )

    return render(
        request,
        "post/edit_profile.html",
        {
            "form": form
        }
    )
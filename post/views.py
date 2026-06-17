from django.http import JsonResponse
from django.shortcuts import (
    render,
    redirect,
    get_object_or_404
)

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator

from useraccount.forms import ForgotPasswordForm
from .models import (
    Likes,
    Post,
    Story,
    Follow,
    Notification,
    Comment,
)
from .forms import EditProfileForm, PostForm, StoryForm
import pdb
from django.contrib.auth import (
    authenticate,
    logout,
)
from django.db.models import Case, When, IntegerField
from django.contrib.auth import get_user_model
    
User = get_user_model()
@login_required
def home_view(request):

    stories = Story.objects.select_related("user").annotate(
        is_me=Case(
            When(user=request.user, then=0),
            default=1,
            output_field=IntegerField()
        )
    ).order_by("is_me", "-created_at")
    posts = Post.objects.select_related("user").all()
    liked_posts = Likes.objects.filter(user=request.user).values_list("post_id", flat=True)
    following_ids = Follow.objects.filter(follower=request.user).values_list("following_id", flat=True)
    context = {
        "stories": stories,
        "posts": posts,
        "likes": liked_posts,
        "following_ids": following_ids,
    }
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
        "home"
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

@login_required
def notifications_view(request):
    notifications = Notification.objects.filter(
        receiver=request.user
    ).select_related("sender")
    notifications.update(is_read=True)
    return render(request, "post/notifications.html", {"notifications": notifications})


@login_required
def delete_account_view(request):
    if request.method == "POST":
        user = request.user
        logout(request)
        user.delete()
        messages.success(request, "Your account has been deleted.")
        return redirect("signup")
    return redirect("profile_view")

@login_required
def like_post(request, post_id):

    post = Post.objects.get(
        id=post_id
    )

    like = Likes.objects.filter(
        user=request.user,
        post=post
    )

    if like.exists():

        like.delete()

        liked = False

    else:

        Likes.objects.create(
            user=request.user,
            post=post
        )

        liked = True

    return JsonResponse({

        "liked": liked,

        "likes_count":
        post.post_likes.count()

    })

@login_required
def add_comment(request, post_id):
    if request.method == "POST":
        post = get_object_or_404(Post, id=post_id)
        text = request.POST.get("comment", "").strip()
        if text:
            import uuid
            Comment.objects.create(
                id=str(uuid.uuid4())[:25],
                author=request.user,
                item=post,
                comment=text,
            )
            return JsonResponse({"author": request.user.username, "comment": text})
    return JsonResponse({"error": "invalid"}, status=400)


@login_required
def follow_user(request, user_id):
    
    target = get_object_or_404(User, id=user_id)

    if target == request.user:
        return JsonResponse({"error": "Cannot follow yourself"}, status=400)

    follow = Follow.objects.filter(follower=request.user, following=target)

    if follow.exists():
        follow.delete()
        following = False
    else:
        Follow.objects.create(follower=request.user, following=target)
        following = True

    return JsonResponse({
        "following": following,
        "followers_count": Follow.objects.filter(following=target).count(),
    })
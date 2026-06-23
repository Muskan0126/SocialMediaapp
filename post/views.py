from django.http import JsonResponse
from django.shortcuts import (
    render,
    redirect,
    get_object_or_404
)

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.views import View

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
from django.contrib.auth.mixins import LoginRequiredMixin
User = get_user_model()

class home_view(View, LoginRequiredMixin):

    def get(self, request):
    
        stories = Story.objects.select_related("user").annotate(
            is_me=Case(
                When(user=request.user, then=0),
                default=1,
                output_field=IntegerField()
            )
        ).order_by("is_me", "-created_at")
        posts = Post.objects.select_related("user").order_by("-posted", "-id")
        liked_posts = Likes.objects.filter(user=request.user).values_list("post_id", flat=True)
        following_ids = Follow.objects.filter(follower=request.user).values_list("following_id", flat=True)
        context = {
            "stories": stories,
            "posts": posts,
            "likes": liked_posts,
            "following_ids": following_ids,
            "post_form": PostForm(),
            "story_form": StoryForm(),
        }
        return render(
            request,
            "post/home.html",
            context
        )

class create_post_view(View):
    def get (self,request):
        form = PostForm()
        return render(
            request,
            "post/create_post.html",
            {
                "form": form
            }
        )
    def post(self,request):
        form = PostForm()

        form = PostForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            post = form.save(commit=False)
            post.user = request.user
            post.save()
            
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
class create_story_view(View):
    
    def get(self,request):
        form = StoryForm()
        return render(
            request,
            "post/create_story.html",
            {
                "form": form
            }
        )
    def post(self, request):

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

class my_posts_view(View):
    def get(self,request):
        posts = Post.objects.filter(user=request.user).order_by("-posted", "-id")
        return render(
            request,
            "post/my_posts.html",
            {
                "posts": posts
            })

class delete_post_view(View):
    def post(self, request, post_id):
        if not request.user.is_authenticated:
            return JsonResponse({"error": "not authenticated"}, status=401)
        post = get_object_or_404(Post, id=post_id, user=request.user)
        post.delete()
        return JsonResponse({"success": True})


class edit_caption_view(View):
    def post(self, request, post_id):
        if not request.user.is_authenticated:
            return JsonResponse({"error": "not authenticated"}, status=401)
        post = get_object_or_404(Post, id=post_id, user=request.user)
        caption = request.POST.get("caption", "").strip()
        if not caption:
            return JsonResponse({"error": "Caption cannot be empty."}, status=400)
        post.caption = caption
        post.save()
        return JsonResponse({"success": True, "caption": post.caption})



class delete_story_view(View):
    def get(self,request,story_id):
        story = get_object_or_404(
            Story,
            id=story_id,
            user=request.user
        )

        story.delete()

       

        return redirect("home")


class profile_view(View):
    def get(self,request):
        posts = (
            Post.objects
            .filter(user=request.user)
            .select_related("user")
            .order_by("-posted", "-id")
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
        
    
class edit_profile(View):
    def get(self,request):
        form = EditProfileForm
        form = EditProfileForm(
            instance=request.user
        )
        return render(
                request,
                "post/edit_profile.html",
                {
                    "form": form
                }
            )
    def post(self,request):
        form = EditProfileForm
        form = EditProfileForm(
            instance=request.user
        )

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


class notifications_view(View):
    def get(self,request):
        notifications = Notification.objects.filter(
            receiver=request.user
        ).select_related("sender")
        notifications.update(is_read=True)

        following_ids = (
            Follow.objects
            .filter(follower=request.user)
            .values_list(
                "following_id",
                flat=True
            )
        )

        return render(
            request,
            "post/notifications.html",
            {
                "notifications": notifications,
                "following_ids": following_ids,
            }
        )
    



class delete_account_view(View):
    def post(self,request):
        if request.method == "POST":
            user = request.user
            logout(request)
            user.delete()
            return redirect("signup")
        return redirect("profile_view")


class like_post(View):
    def post(self,request,post_id):

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

class add_comment(View):
    def post(self,request, post_id):
        
            post = get_object_or_404(Post, id=post_id)
            text = request.POST.get("comment", "").strip()
            parent_id = request.POST.get("parent_id", "").strip()
            if text:
                import uuid
                parent = None
                if parent_id:
                    try:
                        parent = Comment.objects.get(id=parent_id, item=post)
                    except Comment.DoesNotExist:
                        pass
                c = Comment.objects.create(
                    id=str(uuid.uuid4())[:25],
                    author=request.user,
                    item=post,
                    comment=text,
                    parent=parent,
                )
                return JsonResponse({
                    "id": c.id,
                    "author": request.user.username,
                    "comment": text,
                    "parent_id": parent_id or None,
                    "comment_count" : post.comments.count()
                })
            return JsonResponse({"error": "invalid"}, status=400)


class delete_comment_view(View):
    def post(self, request, comment_id):
        if not request.user.is_authenticated:
            return JsonResponse({"error": "not authenticated"}, status=401)

        comment = get_object_or_404(Comment, id=comment_id)
        post = comment.item

        if comment.author != request.user and post.user != request.user:
            return JsonResponse({"error": "not allowed"}, status=403)

        comment.delete()

        return JsonResponse({
            "success": True,
            "post_id": post.id,
            "comment_count": post.comments.count(),
        })



class follow_user(View):
    def post(self,request, user_id):
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

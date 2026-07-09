from django import middleware
from rest_framework.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import HttpResponse
from django.test import Client, RequestFactory
from apps.common.validators import validate_image
from apps.post.models import Notification, Post, Story, Likes, Follow, Comment, Stream
from rest_framework_simplejwt.tokens import RefreshToken
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from apps.useraccount.models import  otp 
from apps.post.models import  Follow
from apps.useraccount.apis.views import RegisterAPIView,LoginAPIView
from rest_framework_simplejwt.tokens import RefreshToken
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import SimpleUploadedFile
from apps.useraccount.test_middleware import RequestLoggingMiddleware, SystemInfoMiddleware
User = get_user_model()
class PostAPIViewTestCase(APITestCase):

    def setUp(self):

        self.user = User.objects.create_user(
            username="muskan",
            email="muskan@test.com",
            password="Password123!"
        )

        self.other_user = User.objects.create_user(
            username="other",
            email="other@test.com",
            password="Password123!"
        )

        refresh = RefreshToken.for_user(self.user)

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}"
        )


        self.image = self.get_temporary_image()

        self.post = Post.objects.create(
            user=self.user,
            picture=self.image,
            caption="Test Caption"
        )

        self.story = Story.objects.create(
            user=self.user,
            image=self.image
        )


        self.create_post_url = reverse("create-post")
        self.post_list_url = reverse("post-list")
    def get_temporary_image(self):

        file = BytesIO()

        image = Image.new(
            "RGB",
            (100,100)
        )

        image.save(
            file,
            "JPEG"
        )

        file.seek(0)

        return SimpleUploadedFile(
            "test.jpg",
            file.read(),
            content_type="image/jpeg"
        )
        

    def test_create_post_success(self):

        image = self.get_temporary_image()

        response = self.client.post(
            self.create_post_url,
            {
                "picture": image,
                "caption": "Hello"
            },
            format="multipart"
        )

        print(response.data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response.data["message"],
            "Post created successfully."
        )
    
    def test_create_post_invalid_image(self):

        invalid_file = SimpleUploadedFile(
            "test.txt",
            b"This is not an image",
            content_type="text/plain"
        )

        response = self.client.post(
            self.create_post_url,
            {
                "picture": invalid_file,
                "caption": "Hello"
            },
            format="multipart"
        )
        print("\n Error :", response.data)
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertEqual(
            str(response.data["picture"][0]),
            "Upload a valid image. The file you uploaded was either not an image or a corrupted image."
        )
    def test_create_post_without_caption(self):

        image = self.get_temporary_image()

        response = self.client.post(
            self.create_post_url,
            {
                "picture": image,
                "caption": ""
            },
            format="multipart"
        )
        print("\n Error :", response.data)
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertEqual(
            response.data["caption"][0],
            "This field may not be blank."
        )

    def test_post_list(self):

        response = self.client.get(self.post_list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    def test_update_post(self):

        response = self.client.patch(

            reverse(
                "post-update",
                kwargs={"pk": self.post.id}
            ),

            {
                "caption": "Updated Caption"
            },

            format="json"
        )

        self.post.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            self.post.caption,
            "Updated Caption"
        )

    def test_delete_post(self):

        response = self.client.delete(

            reverse(
                "post-delete",
                kwargs={"pk": self.post.id}
            )

        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertFalse(
            Post.objects.filter(
                id=self.post.id
            ).exists()
        )

    def test_create_story(self):

        image = self.get_temporary_image()

        response = self.client.post(
            reverse("create-story"),
            {
                "image": image
            },
            format="multipart"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )
    def test_create_story_invalid_image(self):

        invalid_file = SimpleUploadedFile(
            "story.txt",
            b"This is not an image",
            content_type="text/plain"
        )

        response = self.client.post(
            reverse("create-story"),
            {
                "image": invalid_file
            },
            format="multipart"
        )
        print("\n Error :", response.data)
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        
    def test_delete_story(self):

        response = self.client.delete(

            reverse(
                "story-delete",
                kwargs={"pk": self.story.id}
            )

        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
    def test_like_post(self):

        response = self.client.post(

            reverse(
                "like",
                kwargs={
                    "post_id": self.post.id
                }
            )

        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["liked"])

    def test_unlike_post(self):

        Likes.objects.create(
            user=self.user,
            post=self.post
        )

        response = self.client.post(

            reverse(
                "like",
                kwargs={
                    "post_id": self.post.id
                }
            )

        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["liked"])

    def test_follow_user(self):

        response = self.client.post(

            reverse(
                "follow",
                kwargs={
                    "id": self.other_user.id
                }
            )

        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["following"])

    def test_unfollow_user(self):

        Follow.objects.create(
            follower=self.user,
            following=self.other_user
        )

        response = self.client.post(

            reverse(
                "follow",
                kwargs={
                    "id": self.other_user.id
                }
            )

        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["following"])

    def test_follow_self(self):

        response = self.client.post(

            reverse(
                "follow",
                kwargs={
                    "id": self.user.id
                }
            )

        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class PostModelTest(APITestCase):

    def setUp(self):

        self.user = User.objects.create_user(
            username="test",
            password="Password123!"
        )
    def test_user_follow_method(self):

        other = User.objects.create_user(
    username="other2",
    email="other2@gmail.com",
    password="Password123!"
)
    

        follow = Follow.objects.create(
            follower=self.user,
            following=other
        )

        Follow.user_follow(
            sender=Follow,
            instance=follow
        )

        self.assertTrue(
            Notification.objects.filter(
                sender=self.user,
                receiver=other,
                notification_type=3
            ).exists()
        )
    def test_stream_add_post(self):

        follower = User.objects.create_user(
            username="follower",
            email="follower@gmail.com",
            password="Password123!"
        )

        Follow.objects.create(
            follower=follower,
            following=self.user
        )

        post = Post.objects.create(
            user=self.user,
            caption="Hello"
        )

        Stream.add_post(
            sender=Post,
            instance=post
        )

        self.assertEqual(
            Stream.objects.count(),
            1
        )

        stream = Stream.objects.first()

        self.assertEqual(stream.user, follower)
        self.assertEqual(stream.post, post)
        self.assertEqual(stream.following, self.user)
    def test_story_string(self):

        story = Story.objects.create(
            user=self.user,
            image="story.jpg"
        )

        self.assertEqual(
            str(story),
            f"{self.user.username} Story"
        )
    def test_user_unfollow_method(self):

        other = User.objects.create_user(
        username="other",
        email="other@gmail.com",
        password="Password123!"
)

        Notification.objects.create(
            id="1",
            sender=self.user,
            receiver=other,
            notification_type=3,
            notification_text="Follow"
        )

        follow = Follow.objects.create(
            follower=self.user,
            following=other
        )

        Follow.user_unfollow(
            sender=Follow,
            instance=follow
        )

        self.assertFalse(
            Notification.objects.filter(
                sender=self.user,
                receiver=other,
                notification_type=3
            ).exists()
        )
    def test_user_liked_post_method(self):
        post = Post.objects.create(
            user=self.user,
            caption="Test"
        )

        like = Likes.objects.create(
            user=self.user,
            post=post
        )

        Likes.user_liked_post(
            sender=Likes,
            instance=like
        )
    def test_user_unliked_post_method(self):
        post = Post.objects.create(
            user=self.user,
            caption="Test"
        )

        like = Likes.objects.create(
            user=self.user,
            post=post
        )

        Likes.user_unliked_post(
            sender=Likes,
            instance=like
        )
    def test_comment_string(self):
        post = Post.objects.create(
            user=self.user,
            caption="Hello"
        )

        comment = Comment.objects.create(
            id="1",
            item=post,
            author=self.user,
            comment="Nice"
        )

        self.assertEqual(
            str(comment),
            str(post)
        )
    def test_notification_string(self):

        post = Post.objects.create(
            user=self.user,
            caption="Hello"
        )

        notification = Notification.objects.create(
            id="1",
            post=post,
            comment=None,
            sender=self.user,
            receiver=self.user,
            notification_type=1,
            notification_text="Liked"
        )

        self.assertEqual(
            str(notification),
            "1"
        )

    def test_notification_string(self):

        post = Post.objects.create(
            user=self.user,
            caption="Hello"
        )

        notification = Notification.objects.create(
            id="1",
            post=post,
            comment=None,
            sender=self.user,
            receiver=self.user,
            notification_type=1,
            notification_text="Liked"
        )

        self.assertEqual(
            str(notification),
            "1"
        )
    def test_post_string(self):

        post = Post.objects.create(
            user=self.user,
            caption="hello"
        )

        self.assertIsNotNone(
            str(post)
        )


    def test_comment_creation(self):

        post = Post.objects.create(
            user=self.user,
            caption="hello"
        )

        comment = Comment.objects.create(
            item=post,
            author=self.user,
            comment="Nice post"
        )

        self.assertEqual(
            comment.comment,
            "Nice post"
        )
    
from apps.post.forms import EditProfileForm, PostForm, ResetPassword, StoryForm


class PostFormTest(APITestCase):


    def test_empty_post_form(self):

        form = PostForm(
            data={}
        )

        self.assertFalse(
            form.is_valid()
        )
class PostAPIViewsTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="muskan",
            password="Password123!"
        )

        self.client = Client()

    def test_post_list_view(self):

        self.client.login(
            username="muskan",
            password="Password123!"
        )

        response = self.client.get(
            reverse("post-list")
        )

        self.assertEqual(
            response.status_code,
            200
        )


    def test_create_post_login_required(self):

        response = self.client.get(
            reverse("create-post")
        )

        self.assertEqual(
            response.status_code,
            302
        )


    def test_create_post_login_required(self):

        response = self.client.get(
            reverse("create-post")
        )

        self.assertEqual(
            response.status_code,
            401
        )


    def test_logout_view(self):

        self.client.login(
            username="muskan",
            password="Password123!"
        )

        response = self.client.get(
            reverse("logout")
        )

        self.assertEqual(
            response.status_code,
            302
        )
    



class PostViewsTestCase(APITestCase):

    def setUp(self):

        self.user = User.objects.create_user(
            username="testuser",
            email="test@test.com",
            password="password123"
        )

        self.user2 = User.objects.create_user(
            username="second",
            email="second@test.com",
            password="password123"
        )

        self.client.login(
            username="testuser",
            password="password123"
        )
    def get_temporary_image(self):

        file = BytesIO()

        image = Image.new(
            "RGB",
            (100,100)
        )

        image.save(
            file,
            "JPEG"
        )

        file.seek(0)

        return SimpleUploadedFile(
            "test.jpg",
            file.read(),
            content_type="image/jpeg"
        )

    # HOME VIEW

    def test_home_view(self):

        response = self.client.get(
            reverse("home")
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertTemplateUsed(
            response,
            "post/home.html"
        )



    # CREATE POST GET

    def test_create_post_get(self):

        response = self.client.get(
            reverse("create_post")
        )

        self.assertEqual(
            response.status_code,
            200
        )


    # CREATE POST SUCCESS

    def test_create_post_success(self):

        response = self.client.post(
            reverse("create_post"),
            {
                "caption":"hello",
                "picture":self.get_temporary_image()
            }
        )
        self.assertEqual(
            response.status_code,
            302
        )




    # CREATE POST INVALID

    def test_create_post_invalid(self):

        response = self.client.post(
            reverse("create_post"),
            {
                "caption":""
            }
        )


        self.assertEqual(
            response.status_code,
            200
        )



    # STORY GET

    def test_create_story_get(self):

        response=self.client.get(
            reverse("create_story")
        )

        self.assertEqual(
            response.status_code,
            200
        )



    # STORY CREATE

    def test_create_story_success(self):

        response=self.client.post(
            reverse("create_story"),
            {
                "image":self.get_temporary_image()
            }
        )

        self.assertEqual(
            response.status_code,
            302
        )



    # DELETE POST

    def test_delete_post(self):

        post=Post.objects.create(
            user=self.user,
            caption="hello",
            picture=self.get_temporary_image()
        )


        response=self.client.post(
            reverse(
                "delete_post",
                args=[post.id]
            )
        )


        self.assertEqual(
            response.status_code,
            200
        )


        self.assertFalse(
            Post.objects.filter(
                id=post.id
            ).exists()
        )



    # EDIT CAPTION

    def test_edit_caption(self):

        post=Post.objects.create(
            user=self.user,
            caption="old",
            picture=self.get_temporary_image()
        )


        response=self.client.post(
            reverse(
                "edit_caption",
                args=[post.id]
            ),
            {
                "caption":"new"
            }
        )


        self.assertEqual(
            response.status_code,
            200
        )


        post.refresh_from_db()

        self.assertEqual(
            post.caption,
            "new"
        )



    # LIKE POST

    def test_like_post(self):

        post=Post.objects.create(
            user=self.user,
            caption="hello",
            picture=self.get_temporary_image()
        )


        response=self.client.post(
            reverse(
                "like_post",
                args=[post.id]
            )
        )


        self.assertEqual(
            response.status_code,
            200
        )

        self.assertTrue(
            Likes.objects.exists()
        )



    # UNLIKE POST

    def test_unlike_post(self):

        post=Post.objects.create(
            user=self.user,
            caption="hello",
            picture=self.get_temporary_image()
        )


        Likes.objects.create(
            user=self.user,
            post=post
        )


        response=self.client.post(
            reverse(
                "like_post",
                args=[post.id]
            )
        )


        self.assertEqual(
            response.status_code,
            200
        )


        self.assertFalse(
            Likes.objects.exists()
        )



    # FOLLOW USER

    def test_follow_user(self):

        response=self.client.post(
            reverse(
                "follow_user",
                args=[self.user2.id]
            )
        )


        self.assertEqual(
            response.status_code,
            200
        )


        self.assertTrue(
            Follow.objects.exists()
        )



    # FOLLOW AGAIN REMOVE

    def test_unfollow_user(self):

        Follow.objects.create(
            follower=self.user,
            following=self.user2
        )


        response=self.client.post(
            reverse(
                "follow_user",
                args=[self.user2.id]
            )
        )


        self.assertEqual(
            response.status_code,
            200
        )



    # FOLLOW SELF

    def test_follow_self(self):

        response=self.client.post(
            reverse(
                "follow_user",
                args=[self.user.id]
            )
        )


        self.assertEqual(
            response.status_code,
            400
        )



    # COMMENT

    def test_add_comment(self):

        post=Post.objects.create(
            user=self.user,
            caption="hello",
            picture=self.get_temporary_image()
        )


        response=self.client.post(
            reverse(
                "add_comment",
                args=[post.id]
            ),
            {
                "comment":"nice"
            }
        )


        self.assertEqual(
            response.status_code,
            200
        )


        self.assertEqual(
            Comment.objects.count(),
            1
        )



    # EMPTY COMMENT

    def test_empty_comment(self):

        post=Post.objects.create(
            user=self.user,
            caption="hello",
            picture=self.get_temporary_image()
        )


        response=self.client.post(
            reverse(
                "add_comment",
                args=[post.id]
            ),
            {
                "comment":""
            }
        )


        self.assertEqual(
            response.status_code,
            400
        )



    # PROFILE VIEW

    def test_profile_view(self):

        response=self.client.get(
            reverse("profile_view")
        )

        self.assertEqual(
            response.status_code,
            200
        )



    # NOTIFICATION VIEW

    def test_notifications(self):

        Notification.objects.create(
            sender=self.user2,
            receiver=self.user,
            notification_type="3"
        )

        response = self.client.get(
            reverse("notifications")
        )

        self.assertEqual(
            response.status_code,
            200
        )
    def test_delete_post_without_login(self):

        self.client.logout()

        post = Post.objects.create(
            user=self.user,
            caption="hello",
            picture=self.get_temporary_image()
        )

        response = self.client.post(
            reverse("delete_post", args=[post.id])
        )

        self.assertEqual(response.status_code, 401)
    def test_edit_caption_empty(self):

        post = Post.objects.create(
            user=self.user,
            caption="hello",
            picture=self.get_temporary_image()
        )

        response = self.client.post(
            reverse("edit_caption", args=[post.id]),
            {"caption": ""}
        )
        self.assertEqual(response.status_code, 400)
    def test_profile_counts(self):

        Follow.objects.create(
            follower=self.user2,
            following=self.user
        )

        for i in range(12):
            Post.objects.create(
                user=self.user,
                caption=f"post{i}",
                picture=self.get_temporary_image()
            )

        response = self.client.get(reverse("profile_view"))

        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            response.context["followers_count"],
            1
        )
        self.assertEqual(
            response.context["posts_count"],
            12
        )
    def test_delete_account_get(self):

        response = self.client.get(
            reverse("delete_account")
        )
        self.assertEqual(response.status_code, 405)
    def test_reply_comment(self):

        post = Post.objects.create(
            user=self.user,
            caption="hello",
            picture=self.get_temporary_image()
        )

        parent = Comment.objects.create(
            id="123",
            author=self.user,
            item=post,
            comment="Parent"
        )

        response = self.client.post(
            reverse("add_comment", args=[post.id]),
            {
                "comment": "Reply",
                "parent_id": parent.id
            }
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            Comment.objects.count(),
            2
        )

        reply = Comment.objects.exclude(id=parent.id).first()

        self.assertEqual(
            reply.parent,
            parent
        )
    def test_like_post_json(self):

        post = Post.objects.create(
            user=self.user,
            caption="hello",
            picture=self.get_temporary_image()
        )

        response = self.client.post(
            reverse("like_post", args=[post.id])
        )

        self.assertTrue(response.json()["liked"])
        self.assertEqual(response.json()["likes_count"], 1)
    def test_unlike_post_json(self):

        post = Post.objects.create(
            user=self.user,
            caption="hello",
            picture=self.get_temporary_image()
        )

        Likes.objects.create(
            user=self.user,
            post=post
        )

        response = self.client.post(
            reverse("like_post", args=[post.id])
        )

        self.assertFalse(response.json()["liked"])
        self.assertEqual(response.json()["likes_count"], 0)
    def test_follow_json(self):

        response = self.client.post(
            reverse("follow_user", args=[self.user2.id])
        )

        self.assertTrue(response.json()["following"])
        self.assertEqual(response.json()["followers_count"], 1)
    def test_unfollow_json(self):

        Follow.objects.create(
            follower=self.user,
            following=self.user2
        )

        response = self.client.post(
            reverse("follow_user", args=[self.user2.id])
        )

        self.assertFalse(response.json()["following"])
        self.assertEqual(response.json()["followers_count"], 0)
class PostFormsTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@test.com",
            password="password123"
        )

        self.user2 = User.objects.create_user(
            username="seconduser",
            email="second@test.com",
            password="password123"
        )

    def get_temporary_image(self):

        file = BytesIO()

        image = Image.new(
            "RGB",
            (100,100)
        )

        image.save(
            file,
            "JPEG"
        )

        file.seek(0)

        return SimpleUploadedFile(
            "test.jpg",
            file.read(),
            content_type="image/jpeg"
        )
        


    # ------------------------
    # PostForm
    # ------------------------

    def test_post_form_valid(self):
        form = PostForm(
            data={
                "caption": "Hello"
            },
            files={
                "picture": self.get_temporary_image()
            }
        )

        self.assertTrue(form.is_valid())

    # ------------------------
    # StoryForm
    # ------------------------

    def test_story_form_valid(self):
        form = StoryForm(
            files={
                "image": self.get_temporary_image()
            }
        )

        self.assertTrue(form.is_valid())

    # ------------------------
    # EditProfileForm
    # ------------------------

    def test_edit_profile_valid(self):

        form = EditProfileForm(
            instance=self.user,
            data={
                "username": "newuser",
                "email": "new@test.com",
                "bio": "bio",
                "first_name": "John",
                "last_name": "Doe",
                "phone_no": "9876543210",
                "gender": "M",
            }
        )

        self.assertTrue(form.is_valid())

    def test_duplicate_username(self):

        form = EditProfileForm(
            instance=self.user,
            data={
                "username": "seconduser",
                "email": "new@test.com",
                "phone_no": "9876543210",
                "gender": "M",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("username", form.errors)

    def test_invalid_username_capital(self):

        form = EditProfileForm(
            instance=self.user,
            data={
                "username": "TestUser",
                "email": "new@test.com",
                "phone_no": "9876543210",
                "gender": "M",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("username", form.errors)

    def test_invalid_username_starts_number(self):

        form = EditProfileForm(
            instance=self.user,
            data={
                "username": "1test",
                "email": "new@test.com",
                "phone_no": "9876543210",
                "gender": "M",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("username", form.errors)

    def test_duplicate_email(self):

        form = EditProfileForm(
            instance=self.user,
            data={
                "username": "newuser",
                "email": "second@test.com",
                "phone_no": "9876543210",
                "gender": "M",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_invalid_phone(self):

        form = EditProfileForm(
            instance=self.user,
            data={
                "username": "newuser",
                "email": "new@test.com",
                "phone_no": "12345",
                "gender": "M",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("phone_no", form.errors)

    def test_invalid_gender(self):

        form = EditProfileForm(
            instance=self.user,
            data={
                "username": "newuser",
                "email": "new@test.com",
                "phone_no": "9876543210",
                "gender": "X",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("gender", form.errors)

    # ------------------------
    # ResetPassword
    # ------------------------

    def test_reset_password_valid(self):

        form = ResetPassword(
            data={
                "old_password": "oldpassword",
                "new_password": "Password123",
                "confirm_password": "Password123",
            }
        )

        self.assertTrue(form.is_valid())

    def test_reset_password_short(self):

        form = ResetPassword(
            data={
                "old_password": "oldpassword",
                "new_password": "123",
                "confirm_password": "123",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("new_password", form.errors)

    def test_reset_password_numeric(self):

        form = ResetPassword(
            data={
                "old_password": "oldpassword",
                "new_password": "12345678",
                "confirm_password": "12345678",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("new_password", form.errors)

    def test_reset_password_mismatch(self):

        form = ResetPassword(
            data={
                "old_password": "oldpassword",
                "new_password": "Password123",
                "confirm_password": "Password321",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("__all__", form.errors)

class RequestLoggingMiddlewareTestCase(APITestCase):

    def setUp(self):

        self.factory = RequestFactory()


    def get_response(self, request):

        return HttpResponse("OK")


    def test_request_logging_middleware(self):

        middleware = RequestLoggingMiddleware(
            self.get_response
        )

        request = self.factory.get(
            "/test-path/"
        )

        response = middleware(request)

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertEqual(
            response.content,
            b"OK"
        )



class SystemInfoMiddlewareTestCase(APITestCase):

    def setUp(self):

        self.factory = RequestFactory()


    def get_response(self, request):

        return HttpResponse("OK")


    def test_system_info_middleware(self):

        middleware = SystemInfoMiddleware(
            self.get_response
        )

        request = self.factory.get(
            "/profile/",
            HTTP_USER_AGENT=(
                "Mozilla/5.0 "
                "(Windows NT 10.0; Win64; x64) "
                "Chrome/120.0.0.0"
            )
        )

        response = middleware(request)

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertEqual(
            response.content,
            b"OK"
        )


    def test_system_info_without_user_agent(self):

        middleware = SystemInfoMiddleware(
            self.get_response
        )

        request = self.factory.get(
            "/test/"
        )

        response = middleware(request)

        self.assertEqual(
            response.status_code,
            200
        )
class ValidatorTestCase(APITestCase):

    def test_invalid_image_extension(self):

        file = SimpleUploadedFile(
            "image.gif",
            b"dummy content",
            content_type="image/gif"
        )

        with self.assertRaises(ValidationError):
            validate_image(file)
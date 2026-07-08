from django.core.files.uploadedfile import SimpleUploadedFile
from apps.post.models import Post, Story, Likes, Follow, Comment
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
    def get_temporary_image():

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
        self.image = get_temporary_image()

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

    def test_create_post_success(self):

        image = get_temporary_image()

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

        image = get_temporary_image()

        response = self.client.post(
            self.create_post_url,
            {
                "picture": image,
                "caption": "Hello"
            },
            format="multipart"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

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

        image = SimpleUploadedFile(
            "story.jpg",
            b"story",
            content_type="image/jpeg"
        )

        response = self.client.post(

            reverse("create-story"),

            {
                "image": image
            },

            format="multipart"
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

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

    
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from apps.useraccount.models import  otp 
from apps.post.models import  Follow
from apps.useraccount.apis.views import RegisterAPIView,LoginAPIView
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

class RegisterAPIViewTestCase(APITestCase):
    def setUp(self):
     
        self.url = reverse('register-api') 
        
        self.valid_payload = {
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "StrongPassword123!",
            "confirm_password" : "StrongPassword123!"
        }
        self.invalid_payload = {
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "StrongPassword123!",
            "confirm_password" : "StrongPassord123!"
        }
    def test_registration_success(self):
    
        response = self.client.post(self.url, self.valid_payload, format='json')
        print("\n", response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["message"], "User registered successfully.")
        self.assertTrue(User.objects.filter(username="testuser").exists())

    def test_registration_invalid_data(self):
       
        response = self.client.post(self.url, self.invalid_payload, format='json')
        print("\n Error :", response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

from apps.useraccount.apis.views import RegisterAPIView

User = get_user_model()

class LoginAPIViewTestCase(APITestCase):
    def setUp(self):
        
        self.url = reverse('login-api')  
        
        self.username = "testloginuser"
        self.password = "StrongPassword123!"
        
        self.user = User.objects.create_user(
            username=self.username,
            email="loginuser@example.com",
            password=self.password
        )
        self.url = reverse('login-api') 
        
        self.valid_payload = {
            "username": "testloginuser",
            "password" : "StrongPassword123!"
        }
        self.invalid_payload = {
            "username": "testuser",
            "password": "StrtongPassword123!"
        }
    def test_login_success(self):
    
        response = self.client.post(self.url, self.valid_payload, format='json')
        print("\n", response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Login Successful")
        self.assertTrue(User.objects.filter(username="testloginuser").exists())

    def test_registration_invalid_data(self):
       
        response = self.client.post(self.url, self.invalid_payload, format='json')
        print("\n Error :", response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class AuthenticatedViewsTestCase(APITestCase):
    def setUp(self):
  
        self.user = User.objects.create_user(
            username="user", 
            email="User@example.com", 
            password="Password123!"
        )
        self.other_user = User.objects.create_user(
            username="otheruser", 
            email="other@example.com", 
            password="Password123!"
        )
        self.refresh = RefreshToken.for_user(self.user)
        self.access_token = str(self.refresh.access_token)

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        self.profile_url = reverse('profile-api') 
        self.update_profile_url = reverse('update-profile-api')
        self.logout_url = reverse('logout-api')
        self.forgot_password_url = reverse('forgot-password')


    def test_get_profile_success_with_following(self):

        Follow.objects.create(follower=self.user, following=self.other_user)
        response = self.client.get(f"{self.profile_url}?id={self.other_user.id}")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["is_following"])

    def test_get_profile_missing_id(self):
        response = self.client.get(self.profile_url)
        print("\n Error :", response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "id is required")

    def test_get_profile_not_found(self):
        response = self.client.get(f"{self.profile_url}?id=99999")
        print("\n Error :", response.data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_profile_patch_success(self):
        payload = {"username": "newusername"} 
        response = self.client.patch(self.update_profile_url, payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, "newusername")

    def test_logout_success(self):
 
        payload = {"refresh": str(self.refresh)}
        response = self.client.post(self.logout_url, payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Logout successful")

    def test_logout_missing_refresh_token(self):

        response = self.client.post(self.logout_url, {}, format='json')
        print("\n Error :", response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "Refresh token is required")


class LoginViewTestCase(APITestCase):

    def setUp(self):

        self.user = User.objects.create_user(
            username="muskan",
            email="muskan@gmail.com",
            password="Password123!"
        )

        self.url = reverse("login")

    def test_login_get(self):

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)

    def test_login_success(self):

        response = self.client.post(
            self.url,
            {
                "username": "muskan",
                "password": "Password123!"
            }
        )

        self.assertEqual(response.status_code, 302)

    def test_login_invalid(self):

        response = self.client.post(
            self.url,
            {
                "username": "muskan",
                "password": "wrongpassword"
            }
        )

        self.assertEqual(response.status_code, 200)

class LogoutViewTestCase(APITestCase):

    def setUp(self):

        self.user = User.objects.create_user(
            username="muskan",
            password="Password123!"
        )

        self.client.login(
            username="muskan",
            password="Password123!"
        )

        self.url = reverse("logout")

    def test_logout(self):

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 302)

class ForgotPasswordViewTestCase(APITestCase):

    def setUp(self):

        self.user = User.objects.create_user(
            username="muskan",
            email="muskan@gmail.com",
            password="Password123!"
        )

        self.url = reverse("forgot_password")

    def test_get(self):

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)

    def test_valid_email(self):

        response = self.client.post(
            self.url,
            {
                "email": "muskan@gmail.com"
            }
        )

        self.assertEqual(response.status_code, 302)

        self.assertTrue(
            otp.objects.filter(email=self.user).exists()
        )

    def test_invalid_email(self):

        response = self.client.post(
            self.url,
            {
                "email": "abc@gmail.com"
            }
        )

        self.assertEqual(response.status_code, 200)
    
class ResetPasswordViewTestCase(APITestCase):

    def setUp(self):

        self.user = User.objects.create_user(
            username="muskan",
            email="muskan@gmail.com",
            password="Password123!"
        )

        self.url = reverse("reset_password")

        session = self.client.session
        session["reset_email"] = "muskan@gmail.com"
        session.save()

        otp.objects.create(
            email=self.user,
            otp="123456"
        )

    def test_get(self):

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)

    def test_reset_success(self):

        response = self.client.post(
            self.url,
            {
                "otp": "123456",
                "new_password": "NewPassword123!",
                "confirm_password": "NewPassword123!"
            }
        )

        self.assertEqual(response.status_code, 302)

    def test_wrong_otp(self):

        response = self.client.post(
            self.url,
            {
                "otp": "999999",
                "new_password": "NewPassword123!",
                "confirm_password": "NewPassword123!"
            }
        )

        self.assertEqual(response.status_code, 200)
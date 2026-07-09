from datetime import timedelta
from django.utils import timezone

from django.test import SimpleTestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.common.validators import validate_image
from apps.useraccount.forms import ForgotPasswordForm, LoginForm, ResetPasswordForm, SignupForm
from apps.useraccount.utils import generate_otp
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

class SignupFormTestCase(APITestCase):

    def setUp(self):

        self.user = User.objects.create_user(
            username="existinguser",
            email="existing@test.com",
            password="Password123",
            phone_no="9876543210",
            gender="M"
        )

    def test_signup_form_invalid_password(self):

        form = SignupForm(data={
            "username": "testuser",
            "email": "test@gmail.com",
            "password": "1234567",      # less than 8 chars and only digits
            "phone_no": "9876543210",
            "gender": "M",
        })

        self.assertFalse(form.is_valid())
        self.assertIn("password", form.errors)
    def test_signup_form_invalid_phone(self):

        form = SignupForm(data={
            "username": "testuser",
            "email": "test@gmail.com",
            "password": "Password123",
            "phone_no": "12345",        # invalid
            "gender": "M",
        })

        self.assertFalse(form.is_valid())
        self.assertIn("phone_no", form.errors)
    def valid_data(self):

        return {
            "username": "testuser",
            "email": "test@test.com",
            "password": "Password123",
            "phone_no": "9876543210",
            "gender": "M",
        }


    # -------------------------
    # Signup valid
    # -------------------------

    def test_signup_valid(self):

        form = SignupForm(
            data=self.valid_data()
        )

        self.assertTrue(form.is_valid())


    # -------------------------
    # Username validation
    # -------------------------

    def test_signup_duplicate_username(self):

        data = self.valid_data()

        data["username"] = "existinguser"

        form = SignupForm(data=data)

        self.assertFalse(form.is_valid())
        self.assertIn(
            "username",
            form.errors
        )


    def test_signup_username_capital(self):

        data = self.valid_data()

        data["username"] = "TestUser"

        form = SignupForm(data=data)

        self.assertFalse(form.is_valid())

        self.assertIn(
            "username",
            form.errors
        )


    def test_signup_username_start_number(self):

        data = self.valid_data()

        data["username"] = "1testuser"

        form = SignupForm(data=data)

        self.assertFalse(form.is_valid())

        self.assertIn(
            "username",
            form.errors
        )


    def test_signup_username_start_symbol(self):

        data = self.valid_data()

        data["username"] = "@testuser"

        form = SignupForm(data=data)

        self.assertFalse(form.is_valid())

        self.assertIn(
            "username",
            form.errors
        )


    # -------------------------
    # Email validation
    # -------------------------

    def test_signup_duplicate_email(self):

        data = self.valid_data()

        data["email"] = "existing@test.com"

        form = SignupForm(data=data)

        self.assertFalse(form.is_valid())

        self.assertIn(
            "email",
            form.errors
        )


    # -------------------------
    # Password validation
    # -------------------------

    def test_signup_short_password(self):

        data = self.valid_data()

        data["password"] = "123"

        form = SignupForm(data=data)

        self.assertFalse(form.is_valid())

        self.assertIn(
            "password",
            form.errors
        )


    def test_signup_only_number_password(self):

        data = self.valid_data()

        data["password"] = "12345678"

        form = SignupForm(data=data)

        self.assertFalse(form.is_valid())

        self.assertIn(
            "password",
            form.errors
        )


    # -------------------------
    # Phone validation
    # -------------------------

    def test_signup_invalid_phone(self):

        data = self.valid_data()

        data["phone_no"] = "12345"

        form = SignupForm(data=data)

        self.assertFalse(form.is_valid())

        self.assertIn(
            "phone_no",
            form.errors
        )


    def test_signup_phone_contains_letters(self):

        data = self.valid_data()

        data["phone_no"] = "98765abc10"

        form = SignupForm(data=data)

        self.assertFalse(form.is_valid())

        self.assertIn(
            "phone_no",
            form.errors
        )
    



class LoginFormTestCase(APITestCase):


    def test_login_form_valid(self):

        form = LoginForm(
            data={
                "username":"testuser",
                "password":"Password123"
            }
        )

        self.assertTrue(
            form.is_valid()
        )


    def test_login_form_empty(self):

        form = LoginForm(
            data={}
        )

        self.assertFalse(
            form.is_valid()
        )



class ForgotPasswordFormTestCase(APITestCase):


    def test_valid_email(self):

        form = ForgotPasswordForm(
            data={
                "email":"test@test.com"
            }
        )

        self.assertTrue(
            form.is_valid()
        )


    def test_invalid_email(self):

        form = ForgotPasswordForm(
            data={
                "email":"invalid"
            }
        )

        self.assertFalse(
            form.is_valid()
        )



class ResetPasswordFormTestCase(APITestCase):


    def test_reset_password_valid(self):

        form = ResetPasswordForm(
            data={
                "otp":"123456",
                "new_password":"Password123"
            }
        )

        self.assertTrue(
            form.is_valid()
        )


    def test_reset_password_invalid_otp_length(self):

        form = ResetPasswordForm(
            data={
                "otp":"1235697",
                "new_password":"Password123"
            }
        )

        self.assertFalse(
            form.is_valid()
        )

        self.assertIn(
            "otp",
            form.errors
        )

class GenerateOTPTestCase(SimpleTestCase):

    def test_generate_otp_default_length(self):
        otp = generate_otp()

        self.assertEqual(len(otp), 6)
        self.assertTrue(otp.isdigit())

    def test_generate_otp_custom_length(self):
        otp = generate_otp(4)

        self.assertEqual(len(otp), 4)
        self.assertTrue(otp.isdigit())

    def test_generate_otp_zero_length(self):
        otp = generate_otp(0)

        self.assertEqual(otp, "")

    def test_generate_otp_random(self):
        otp1 = generate_otp()
        otp2 = generate_otp()

     
        self.assertEqual(len(otp1), 6)
        self.assertEqual(len(otp2), 6)
        self.assertTrue(otp1.isdigit())
        self.assertTrue(otp2.isdigit())
class SerializerValidationTestCase(APITestCase):

    def setUp(self):

        self.user = User.objects.create_user(
            username="existinguser",
            email="existing@gmail.com",
            phone_no="9876543210",
            password="Password123!",
            gender="M"
        )

        self.refresh = RefreshToken.for_user(self.user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.refresh.access_token}"
        )

        self.register_url = reverse("register-api")
        self.update_url = reverse("update-profile-api")
        self.forgot_url = reverse("forgot-password")

    def test_register_username_capital(self):

        response = self.client.post(
            self.register_url,
            {
                "username": "Muskan",
                "email": "abc@gmail.com",
                "password": "Password123!",
                "confirm_password": "Password123!"
            },
            format="json"
        )

        self.assertEqual(response.status_code, 400)

    def test_register_duplicate_username(self):

        response = self.client.post(
            self.register_url,
            {
                "username": "existinguser",
                "email": "new@gmail.com",
                "password": "Password123!",
                "confirm_password": "Password123!"
            },
            format="json"
        )

        self.assertEqual(response.status_code, 400)
    def test_register_duplicate_email(self):

        response = self.client.post(
            self.register_url,
            {
                "username": "newuser",
                "email": "existing@gmail.com",
                "password": "Password123!",
                "confirm_password": "Password123!"
            },
            format="json"
        )

        self.assertEqual(response.status_code, 400)
    def test_register_invalid_phone(self):

        response = self.client.post(
            self.register_url,
            {
                "username": "newuser",
                "email": "abc@gmail.com",
                "password": "Password123!",
                "confirm_password": "Password123!",
                "phone_no": "1234"
            },
            format="json"
        )

        self.assertEqual(response.status_code, 400)
    def test_register_invalid_gender(self):

        response = self.client.post(
            self.register_url,
            {
                "username": "newuser",
                "email": "abc@gmail.com",
                "password": "Password123!",
                "confirm_password": "Password123!",
                "gender": "A"
            },
            format="json"
        )

        self.assertEqual(response.status_code, 400)
    def test_update_duplicate_username(self):

        User.objects.create_user(
            username="anotheruser",
            email="another@gmail.com",
            password="Password123!"
        )

        response = self.client.patch(
            self.update_url,
            {
                "username": "anotheruser"
            },
            format="json"
        )

        self.assertEqual(response.status_code, 400)
    def test_update_duplicate_email(self):

        User.objects.create_user(
            username="abc",
            email="duplicate@gmail.com",
            password="Password123!"
        )

        response = self.client.patch(
            self.update_url,
            {
                "email": "duplicate@gmail.com"
            },
            format="json"
        )

        self.assertEqual(response.status_code, 400)
    def test_update_duplicate_phone(self):

        User.objects.create_user(
            username="abc",
            email="abc@gmail.com",
            phone_no="9999999999",
            password="Password123!"
        )

        response = self.client.patch(
            self.update_url,
            {
                "phone_no": "9999999999"
            },
            format="json"
        )

        self.assertEqual(response.status_code, 400)
    def test_forgot_password_email_not_found(self):

        response = self.client.post(
            self.forgot_url,
            {
                "email": "notfound@gmail.com"
            },
            format="json"
        )

        self.assertEqual(response.status_code, 400)

    def test_profile_upload_path(self):

        path = User.profile_upload_path(
            self.user,
            "profile.jpg"
        )

        self.assertIn(
            "profile/",
            path
        )

        self.assertTrue(
            path.endswith(".jpg")
        )
    def test_user_string(self):

        self.assertEqual(
            str(self.user),
            "existinguser"
        )
    def test_otp_expired(self):

        otp_obj = otp.objects.create(
            email=self.user,
            otp="123456"
        )

        otp_obj.created_at = timezone.now() - timedelta(minutes=6)
        otp_obj.save(update_fields=["created_at"])

        self.assertTrue(
            otp_obj.is_expired()
        )
    def test_otp_not_expired(self):

        otp_obj = otp.objects.create(
            email=self.user,
            otp="123456"
        )

        self.assertFalse(
            otp_obj.is_expired()
        )
    
    def test_reset_password_without_session(self):

        response = self.client.post(
            reverse("reset_password"),
            {
                "otp": "123456",
                "new_password": "Password123!",
                "confirm_password": "Password123!"
            }
        )

        self.assertRedirects(
            response,
            reverse("forgot_password")
        )
    def test_invalid_otp(self):

        session = self.client.session
        session["reset_email"] = self.user.email
        session.save()

        response = self.client.post(
            reverse("reset_password"),
            {
                "otp": "999999",
                "new_password": "Password123!",
                "confirm_password": "Password123!"
            }
        )

        self.assertContains(
            response,
            "Invalid OTP."
        )
    def test_expired_otp(self):

        otp_obj = otp.objects.create(
            email=self.user,
            otp="123456"
        )

        otp_obj.created_at = timezone.now() - timedelta(minutes=6)
        otp_obj.save(update_fields=["created_at"])

        session = self.client.session
        session["reset_email"] = self.user.email
        session.save()

        response = self.client.post(
            reverse("reset_password"),
            {
                "otp": "123456",
                "new_password": "Password123!",
                "confirm_password": "Password123!"
            }
        )

        self.assertRedirects(
            response,
            reverse("forgot_password")
        )
    def test_reset_password_invalid_form(self):

        session = self.client.session
        session["reset_email"] = self.user.email
        session.save()

        response = self.client.post(
            reverse("reset_password"),
            {
                "otp": "123456",
                "new_password": "Password123!",
                "confirm_password": "Password12"
            }
        )

        self.assertEqual(
            response.status_code,
            200
        )

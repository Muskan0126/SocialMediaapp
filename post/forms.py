from django import forms
from .models import Post, Story, User
import pdb
from django.contrib.auth.hashers import check_password

class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ["picture","caption"]


class StoryForm(forms.ModelForm):

    class Meta:
        model = Story
        fields = ["image"]
        
class EditProfileForm(forms.ModelForm):
  
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = [
            "bio", 
            "email",
            "username", 
            "first_name", 
            "last_name", 
            "phone_no", 
            "profile_photo", 
            "gender",
        ]

    def clean_username(self):
        
        username = self.cleaned_data.get("username")
        if not username:
            return username
    
        if User.objects.filter(username=username).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Username already exists.")
            
        if username[0].isdigit() or username[0] in ('@', '/', '-', '+'):
            raise forms.ValidationError("Username should start with an alphabet letter only.")
            
        return username

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email and User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Email already exists.")
        return email



    def clean_phone_no(self):
        phone_no = self.cleaned_data.get("phone_no")
        if not phone_no or len(str(phone_no)) != 10:
            raise forms.ValidationError("Please enter a valid 10-digit phone number.")
        return phone_no

    def clean_gender(self):
        gender = self.cleaned_data.get("gender")
    
        if not gender or gender not in ('M', 'F', 'O'):
            raise forms.ValidationError("Enter Gender. Only 'M', 'F', 'O' allowed.")
        return gender
    

from django import forms


class ResetPassword(forms.Form):

    old_password = forms.CharField(
        widget=forms.PasswordInput
    )

    new_password = forms.CharField(
        widget=forms.PasswordInput
    )

    confirm_password = forms.CharField(
        widget=forms.PasswordInput
    )

    def clean_new_password(self):
        breakpoint()
        password = self.cleaned_data.get(
            "new_password"
        )

        if len(password) < 8:

            raise forms.ValidationError(
                "Password must be at least 8 characters."
            )

        if password.isdigit():

            raise forms.ValidationError(
                "Password cannot contain only numbers."
            )

        return password

    def clean(self):

        cleaned_data = super().clean()

        new_password = cleaned_data.get(
            "new_password"
        )

        confirm_password = cleaned_data.get(
            "confirm_password"
        )

        if (
            new_password
            and
            confirm_password
            and
            new_password != confirm_password
        ):

            raise forms.ValidationError(
                "Passwords do not match."
            )

        return cleaned_data
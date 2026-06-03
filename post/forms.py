from django import forms
from .models import Post, Story, User
import pdb

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
    password = forms.CharField(widget=forms.PasswordInput, required=True)

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

    def clean_password(self):
        password = self.cleaned_data.get("password")
        if password:
            if password.isdigit() or len(password) < 8:
                raise forms.ValidationError("Password must contain both characters and numbers, and be over 8 characters long.")
        return password

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
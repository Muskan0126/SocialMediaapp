from django import forms
from .models import Post, Story


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = [
            "picture",
            "caption"]


class StoryForm(forms.ModelForm):

    class Meta:
        model = Story
        fields = [
            "image"]
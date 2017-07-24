# to make a database driven app we need to make forms
from django import forms
from models import UserModel, PostModel, LikeModel,CommentModel,CategoryModel


# forms are created using classes which consists of fields that are to be displayed in web pages
class SignUpForm(forms.ModelForm):
    class Meta:
        model = UserModel
        fields=['email','username','name','password']

class LoginForm(forms.ModelForm):
    class Meta:
        model = UserModel
        fields = ['username','password']

class PostForm(forms.ModelForm):
    class Meta:
        model = PostModel
        fields = ['image','caption']

class CategoryForm(forms.ModelForm):
    class Meta:
        model = CategoryModel
        fields = ['category']


class LikeForm(forms.ModelForm):
    class Meta:
        model = LikeModel
        fields = ['post']

class CommentForm(forms.ModelForm):
    class Meta:
        model = CommentModel
        fields = ['comment_text','post']
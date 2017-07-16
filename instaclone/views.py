# -*- coding: utf-8 -*-from __future__ import unicode_literals
from django.shortcuts import render, redirect
from forms import SignUpForm, LoginForm, PostForm, LikeForm, CommentForm
from models import UserModel, SessionToken, PostModel, LikeModel, CommentModel
from django.contrib.auth.hashers import make_password, check_password
from datetime import timedelta
from django.utils import timezone
from myapp.settings import BASE_DIR


# from clarifai.rest import ClarifaiApp
# import sendgrid
#
#
from imgurpython import ImgurClient



# client_id_imgur=f7e1fe53d2e71e7
# client_secret_imgur=4f87a455291c79ff1caec48add2c3c4222116ef0
# clarify_api_key=f8ceeb90d41443a1b5691289eaaa0849
# sendgrid_api_key=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
#
#
#
# app = ClarifaiApp(api_key='{f8ceeb90d41443a1b5691289eaaa0849}')
# model = app.models.get("Apparel-v1.3")
# model.predict_by_url(url='')
#
#
#
# from sendgrid.helpers.mail import *
#
# sg = sendgrid.SendGridAPIClient(apikey=('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'))
# from_email = Email("test@example.com")
# to_email = Email("test@example.com")
# subject = "Sending with SendGrid is Fun"
# content = Content("text/plain", "and easy to do anywhere, even with Python")
# mail = Mail(from_email, subject, to_email, content)
# response = sg.client.mail.send.post(request_body=mail.get())
# print(response.status_code)
# print(response.body)
# print(response.headers)
#

def signup_view(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = UserModel(name=name, password=make_password(password), email=email, username=username)
            user.save()
            return render(request,'Login.html')
    else:
        form = SignUpForm()

    return render(request, 'Signup.html', {'form' : form})


def login_view(request):
   # response_data = {}
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = UserModel.objects.filter(username=username).first()

            if user:
                if check_password(password, user.password):
                    token = SessionToken(user=user)
                    token.create_token()
                    token.save()
                    response = redirect('Feeds/')
                    response.set_cookie(key='session_token', value=token.session_token)
                    return response
                else:
                    print "Invalid password or username"
                    #response_data['message'] = 'Incorrect Password! Please try again!'

    elif request.method == 'GET':
        form = LoginForm()

   # response_data['form'] = form
    return render(request, 'Login.html', {'form':form})


def post_view(request):
    user = check_validation(request)

    if user:
        if request.method == 'POST':
            form = PostForm(request.POST, request.FILES)
            if form.is_valid():
                image = form.cleaned_data.get('image')
                caption = form.cleaned_data.get('caption')
                post = PostModel(user=user, image=image)#, caption=caption)
                post.save()

                path = str(BASE_DIR + post.image.url)

                client = ImgurClient('f7e1fe53d2e71e7','4f87a455291c79ff1caec48add2c3c4222116ef0' )
                post.image_url = client.upload_from_path(path,anon=True)['link']
                post.save()

                return redirect('/Feeds/')
        else:
            form=PostForm()
        return render(request, 'Post.html',{'form':form})
    else:
        return redirect('/Login/')

def feed_view(request):
    user = check_validation(request)
    if user:

        posts = PostModel.objects.all().order_by('created_on')

        for post in posts:
            existing_like = LikeModel.objects.filter(post_id=post.id, user=user).first()
            if existing_like:
                post.has_liked = True

        return render(request, 'Feeds.html', {'posts': posts})
    else:

        return redirect('/Login/')


def like_view(request):
    user = check_validation(request)
    if user and request.method == 'POST':

            form = LikeForm(request.POST)
            if form.is_valid():
                post_id = form.cleaned_data.get('post').id
                existing_like = LikeModel.objects.filter(post_id=post_id, user=user).first()
                if not existing_like:
                    LikeModel.objects.create(post_id=post_id, user=user)
                else:
                    existing_like.delete()

                return redirect('/Feeds/')

    else:
        return redirect('/Login/')


def comment_view(request):
    user = check_validation(request)
    if user and request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            post_id = form.cleaned_data.get('post').id
            comment_text = form.cleaned_data.get('comment_text')
            comment = CommentModel.objects.create(user=user, post_id=post_id, comment_text=comment_text)
            comment.save()
            return redirect('/Feeds/')
        else:
            return redirect('/Feeds/')
    else:
        return redirect('/Login/')



def check_validation(request):
    if request.COOKIES.get('session_token'):
        session = SessionToken.objects.filter(session_token=request.COOKIES.get('session_token')).first()
        if session:
            time_to_live = session.created_on + timedelta(days=1)
            if time_to_live > timezone.now():
                return session.user
    else:
        return None




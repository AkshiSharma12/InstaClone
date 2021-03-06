# -*- coding: utf-8 -*-from __future__ import unicode_literals
from django.shortcuts import render, redirect
# from django we import forms that we want
from forms import SignUpForm, LoginForm, PostForm, LikeForm, CommentForm, CategoryForm
# importing models
from models import UserModel, SessionToken, PostModel, LikeModel, CommentModel,CategoryModel
# hashers library converts passwords to hashcode
from django.contrib.auth.hashers import make_password, check_password
# datetime module is used to display / use local time on webpage
from datetime import timedelta
from django.utils import timezone
from myapp.settings import BASE_DIR
#clarify api is used to autodetect and categorise images
from clarifai.rest import ClarifaiApp
from keys import clarify_api_key
# sendgrid api is used to send automated emails to users
import sendgrid
from keys import sendgrid_api_key
from imgurpython import ImgurClient
# imgr api is used to save images on server / cloud which provides us the url required
from sendgrid.helpers.mail import *






def signup_view(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            if set('abcdefghijklmnopqrstuvwxyz').intersection(name) and set('abcdefghijklmnopqrstuvwxyz@_1234567890').intersection(username):
                if len(username) > 4 and len(password) > 5:
                    user = UserModel(name=name, password=make_password(password), email=email, username=username)
                    user.save()
                    sg = sendgrid.SendGridAPIClient(apikey=(sendgrid_api_key))
                    from_email = Email("akshisharma12@gmail.com")
                    to_email = Email(form.cleaned_data['email'])
                    subject = "Welcome to P2P Marketing"
                    content = Content("text/plain", "Welcome onboard. Upload Images up for sale and let us categorise them for you. Have Fun." "Team P2P Marketing")
                    mail = Mail(from_email, subject, to_email, content)
                    response = sg.client.mail.send.post(request_body=mail.get())
                    print(response.status_code)
                    print(response.body)
                    print(response.headers)
                    print ("Sucessfully signed up!")
                    return render(request,'Login.html')
            else:
             print ("Invalid entries!")
             form=SignUpForm
             return render(request, 'Signup.html', {'form': form})

        else:
            print ("Invalid Name/Username")
    else:
        form = SignUpForm()

        return render(request, 'Signup.html', {'form' : form})


def login_view(request):
    response_data = {}
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
                    response_data['message'] = 'Incorrect Password! Please try again!'

    elif request.method == 'GET':
        form = LoginForm()

    response_data['form'] = form
    return render(request, 'Login.html', {'form':form})


def post_view(request):
    user = check_validation(request)

    if user:
        if request.method == 'POST':
            form = PostForm(request.POST, request.FILES)
            if form.is_valid():
                image = form.cleaned_data.get('image')
                caption = form.cleaned_data.get('caption')
                post = PostModel(user=user, image=image, caption=caption)
                post.save()

                path = str(BASE_DIR + post.image.url)

                client = ImgurClient('f7e1fe53d2e71e7','4f87a455291c79ff1caec48add2c3c4222116ef0' )
                post.image_url = client.upload_from_path(path,anon=True)['link']
                #saving to DB
                post.save()

                return redirect('/Feeds/')

        else:
            form=PostForm()
        return render(request, 'Post.html',{'form':form})
    else:
        return redirect('/Login/')

def category_view(post):
                app = ClarifaiApp(api_key=clarify_api_key)
                model = app.models.get("General-v1.3")
                response = model.predict_by_url(url=post.image_url)
                if response["status"]["code"] == 10000:
                    if response["outputs"]:
                        if response["outputs"][0]["data"]:
                            if response["outputs"][0]["data"]["concepts"]:
                                for index in range(0, len(response["outputs"][0]["data"]["concepts"])):
                                    category = CategoryModel(post=post, category=response["outputs"][0]["data"]["concepts"][0]["name"])
                                    category.save()
                            else:
                                print "No concepts List Error"
                        else:
                            print "No Data List Error"
                    else:
                        print "No Outputs List Error"
                else:
                    print "Response Code Error"



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
                    like = LikeModel.objects.create(post_id=post_id, user=user)
                    sg = sendgrid.SendGridAPIClient(apikey=(sendgrid_api_key))
                    from_email = Email("akshisharma12@gmail.com")
                    to_email = Email(like.post.user.email)
                    subject = "Like!"
                    content = Content("text/plain","Your post has a new like.")
                    mail = Mail(from_email, subject, to_email, content)
                    response = sg.client.mail.send.post(request_body=mail.get())
                    print(response.status_code)
                    print(response.body)
                    print(response.headers)
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
            sg = sendgrid.SendGridAPIClient(apikey=(sendgrid_api_key))
            from_email = Email("akshisharma12@gmail.com")
            to_email = Email(comment.post.user.email)
            subject = "Comment!"
            content = Content("text/plain", "Your post has a new comment.")
            mail = Mail(from_email, subject, to_email, content)
            response = sg.client.mail.send.post(request_body=mail.get())
            print(response.status_code)
            print(response.body)
            print(response.headers)
            return redirect('/Feeds/')
        else:
            return redirect('/Feeds/')
    else:
        return redirect('/Login/')

def userpost_view(request,user_name):
    posts=PostModel.objects.all().filter(user_username=user_name)
    return render(request,'UserPost.html',{'posts':posts,'user_name':user_name})


def logout_view(request):
    request.session.modified = True
    response = redirect('/Login/')
    response.delete_cookie(key='session_token')
    return response

#for validating the session
def check_validation(request):
    if request.COOKIES.get('session_token'):
        session = SessionToken.objects.filter(session_token=request.COOKIES.get('session_token')).first()
        if session:
            time_to_live = session.created_on + timedelta(days=1)
            if time_to_live > timezone.now():
                return session.user
    else:
        return None




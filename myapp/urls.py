from django.conf.urls import url
from django.contrib import  admin
from instaclone.views import signup_view, login_view, feed_view, like_view,comment_view,post_view

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url('Post/',post_view),
    url('Feeds/',feed_view),
    url('Like/',like_view),
    url('Comment/',comment_view),
    url('Login/', login_view),
    url('', signup_view)
]

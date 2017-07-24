# to create urls in django we have to import urls from django.conf.url
from django.conf.urls import url
#admin panel is created which has a major control overdatabase
from django.contrib import  admin
#from views we import pages which we are giving url to
from instaclone.views import signup_view, login_view, feed_view, like_view,comment_view,post_view,logout_view,userpost_view
# r is the regular expression
urlpatterns = [
    url(r'^login/feed/(?P<user_name>.+)/$', userpost_view),
    url('/Logout/',logout_view),
    url('Post/',post_view),
    url('Feeds/',feed_view),
    url('Like/',like_view),
    url('Comment/',comment_view),

    url(r'^admin/', admin.site.urls),
    url('Login/', login_view),

    url('', signup_view)
]

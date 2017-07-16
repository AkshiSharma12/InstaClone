# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from models import UserModel,PostModel,LikeModel,CommentModel


admin.site.register(UserModel)
admin.site.register(PostModel)
admin.site.register(LikeModel)
admin.site.register(CommentModel)

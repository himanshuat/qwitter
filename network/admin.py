from django.contrib import admin

from .models import *

# Register your models here.
admin.site.register(User)
admin.site.register(Profile)
admin.site.register(Connection)
admin.site.register(Post)
admin.site.register(Reaction)
admin.site.register(Comment)
admin.site.register(Bookmark)

from django.contrib import admin
from .models import (
    Post,
    PostImage,
    Comment,
    Profile,
    Notification,
    Story,
    SavedPost,
    Reel,
    ReelComment
)

admin.site.register(Post)
admin.site.register(PostImage)
admin.site.register(Comment)
admin.site.register(Profile)
admin.site.register(Notification)
admin.site.register(Story)
admin.site.register(SavedPost)
admin.site.register(Reel)
admin.site.register(ReelComment)



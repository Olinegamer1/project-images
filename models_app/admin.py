from django.contrib import admin
from .models.profile import Profile
from .models.post import Post
from .models.like import Like
from .models.comment import Comment


@admin.register(Profile)
class ProfileModel(admin.ModelAdmin):
    list_display = ['user', 'date_of_birth', 'avatar']
    raw_id_fields = ['user']


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'published_date']
    list_filter = ['published_date', 'user']
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ['user']
    ordering = ['status', 'published_date']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'post', 'created', 'parent_comment']
    list_filter = ['created', 'modified', 'parent_comment']
    raw_id_fields = ['user', 'post', 'parent_comment']
    search_fields = ['post__title', 'body']


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ['user', 'post']
    list_filter = ['post']
    search_fields = ['user_username', 'post__title']

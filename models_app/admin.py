from django.contrib import admin

from .models.comment import Comment
from .models.like import Like
from .models.post import Post, Status
from .models.profile import Profile

admin.site.disable_action('delete_selected')


@admin.register(Profile)
class ProfileModel(admin.ModelAdmin):
    list_display = ['user', 'date_of_birth', 'avatar']
    raw_id_fields = ['user']


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'published_date', 'status']
    list_filter = ['published_date', 'user']
    search_fields = ['title', 'description']
    exclude = ['status', 'slug']
    raw_id_fields = ['user']
    ordering = ['status', 'published_date']
    actions = ['reject_and_delete', 'restore', 'approve']

    @admin.action(description='Reject selected posts')
    def reject_and_delete(self, request, queryset):
        self.perform_action_for_selected_posts(queryset, Status.MODERATION, Post.reject_by_admin)

    @admin.action(description='Restore rejected posts')
    def restore(self, request, queryset):
            self.perform_action_for_selected_posts(queryset, Status.REJECTED, Post.restore_by_admin)

    @admin.action(description='Approve moderation posts')
    def approve(self, request, queryset):
        self.perform_action_for_selected_posts(queryset, Status.MODERATION, Post.approve_by_admin)

    def perform_action_for_selected_posts(self, queryset, target_status, action_process):
        for post in queryset:
            post.custom_post_process(target_status=target_status, process=action_process)


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
    search_fields = ['user__username', 'post__title']

from django.contrib import admin
from django.contrib import messages

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
        for post in queryset:
            if post.status == Status.MODERATION:
                post.reject_by_admin()
                post.save()
                self.message_user(request,
                                  'Selected posts have been rejected and'
                                  ' will be deleted with a delay.',
                                  messages.SUCCESS)
            else:
                self.message_user(request,
                                  'Only posts with moderation status can be'
                                  ' rejected and deleted with delay.',
                                  messages.WARNING)

    @admin.action(description='Restore rejected posts')
    def restore(self, request, queryset):
        for post in queryset:
            if post.status == Status.REJECTED:
                post.restore_by_admin()
                post.save()
                self.message_user(request,
                                  'Selected posts have been restored.',
                                  messages.SUCCESS)
            else:
                self.message_user(request,
                                  'Only posts with rejected status can be restored.',
                                  messages.WARNING)

    @admin.action(description='Approve moderation posts')
    def approve(self, request, queryset):
        for post in queryset:
            if post.status == Status.MODERATION:
                post.approve_by_admin()
                post.save()
                self.message_user(request,
                                  'Selected posts have been approved.',
                                  messages.SUCCESS)
            else:
                self.message_user(request,
                                  'Only posts with moderation status can be approved.',
                                  messages.WARNING)


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

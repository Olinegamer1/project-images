from django.conf import settings
from django.db import models
from django_fsm import FSMField, transition, GET_STATE
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill


def get_restore_target_state(is_published):
    return 'published' if is_published else 'moderation'


class Post(models.Model):
    STATUS_CHOICES = [
        ('moderation', 'Moderation'),
        ('published', 'Published'),
        ('deleted', 'Deleted'),
        ('rejected', 'Rejected')
    ]
    title = models.CharField(max_length=50)
    description = models.CharField(max_length=250)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             related_name='posts',
                             related_query_name='post',
                             on_delete=models.CASCADE)
    slug = models.SlugField(max_length=50, blank=True)
    published_date = models.DateTimeField(blank=True, null=True)
    image = models.ImageField(upload_to='image/%Y/%m/%d')
    image_thumbnails = ImageSpecField(source='image',
                                      processors=[ResizeToFill(400, 400)],
                                      format='JPEG',
                                      options={'quality': 100})

    status = FSMField(default='moderation', choices=STATUS_CHOICES)

    class Meta:
        indexes = [
            models.Index(fields=['-published_date']),
        ]
        ordering = ['-published_date']

    @transition(field=status, source='moderation', target='rejected')
    def reject_by_admin(self):
        ...

    @transition(field=status, source='moderation', target='publish')
    def approve_by_admin(self):
        ...

    @transition(field=status, source=('moderation', 'published'), target='deleted')
    def delete_by_user(self):
        ...

    @transition(field=status, source='published', target='moderation')
    def edit_by_user(self):
        ...

    @transition(field=status, source='rejected', target='moderation')
    def restore_by_admin(self):
        ...

    @transition(field=status,
                source='deleted',
                target=GET_STATE(get_restore_target_state,
                                 states=['moderation', 'published']))
    def restore_by_user(self, is_published):
        ...

    def __str__(self):
        return self.title

from django.conf import settings
from django.db import models
from django.db.models import Manager
from django.utils import timezone
from django.core.validators import FileExtensionValidator
from django_fsm import FSMField, transition, GET_STATE
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill

from project_images.settings import ALLOWED_IMAGE_TYPES
from models_app.validators import validate_image_file_size, validate_image_dimensions


def get_restore_target_state(is_published):
    return Status.PUBLISHED if is_published else Status.MODERATION


class Status(models.TextChoices):
    MODERATION = 'mod', 'Moderation'
    PUBLISHED = 'pub', 'Published'
    DELETED = 'del', 'Deleted'
    REJECTED = 'rej', 'Rejected'


class PublishedPostManager(Manager):
    def get_queryset(self):
        return (super().get_queryset()
                .filter(status=Status.PUBLISHED))


class Post(models.Model):
    title = models.CharField(max_length=50, unique=True)
    description = models.TextField(max_length=250)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             related_name='posts',
                             related_query_name='post',
                             on_delete=models.CASCADE)
    slug = models.SlugField(max_length=50, blank=True)
    published_date = models.DateTimeField(blank=True, null=True)
    image = models.ImageField(upload_to='image/%Y/%m/%d',
                              validators=[
                                  FileExtensionValidator(allowed_extensions=ALLOWED_IMAGE_TYPES),
                                  validate_image_file_size,
                                  validate_image_dimensions,
                              ])
    image_thumbnails = ImageSpecField(source='image',
                                      processors=[ResizeToFill(250, 250)],
                                      format='JPEG',
                                      options={'quality': 100})
    status = FSMField(default=Status.MODERATION,
                      choices=Status.choices,
                      protected=True)
    total_likes = models.PositiveIntegerField(default=0)
    total_comments = models.PositiveIntegerField(default=0)

    objects = models.Manager()
    published_objects = PublishedPostManager()

    class Meta:
        indexes = [
            models.Index(fields=['-published_date']),
            models.Index(fields=['-total_likes']),
            models.Index(fields=['-total_comments'])
        ]
        ordering = ['-published_date']

    @transition(field=status, source=Status.MODERATION, target=Status.REJECTED)
    def reject_by_admin(self):
        ...

    @transition(field=status, source=Status.MODERATION, target=Status.PUBLISHED)
    def approve_by_admin(self):
        self.published_date = timezone.now()

    @transition(field=status,
                source=(Status.MODERATION, Status.PUBLISHED),
                target=Status.DELETED)
    def delete_by_user(self):
        ...

    @transition(field=status, source=Status.PUBLISHED, target=Status.MODERATION)
    def edit_by_user(self):
        ...

    @transition(field=status, source=Status.REJECTED, target=Status.MODERATION)
    def restore_by_admin(self):
        ...

    @transition(field=status,
                source=Status.DELETED,
                target=GET_STATE(get_restore_target_state,
                                 states=[Status.MODERATION, Status.PUBLISHED]))
    def restore_by_user(self, is_published):
        ...

    def __str__(self):
        return self.title

from django.conf import settings
from django.db import models, transaction
from django.utils import timezone
from django_fsm import FSMField, transition, GET_STATE
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill
from decouple import config

from ..tasks import delete_post_delayed, cancel_post_deletion, cache

REMOVAL_DELAY_POST_IN_SECONDS = config('REMOVAL_DELAY_POST_IN_SECONDS',
                                       default=3600,
                                       cast=int)


def get_restore_target_state(is_published):
    return Status.PUBLISHED if is_published else Status.MODERATION


class Status(models.TextChoices):
    MODERATION = 'mod', 'Moderation'
    PUBLISHED = 'pub', 'Published'
    DELETED = 'del', 'Deleted'
    REJECTED = 'rej', 'Rejected'


class Post(models.Model):
    title = models.CharField(max_length=50, unique=True)
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

    status = FSMField(default=Status.MODERATION,
                      choices=Status.choices,
                      protected=True)

    class Meta:
        indexes = [
            models.Index(fields=['-published_date']),
        ]
        ordering = ['-published_date']

    def schedule_deletion(self, delay_seconds):
        task = delete_post_delayed.apply_async(kwargs={'post_id': self.id}, countdown=delay_seconds)
        cache.set(self.id, task.id)

    @transaction.atomic
    def custom_post_process(self, *, target_status, process):
        """
        Processing an object according to the specified process,
        if its status corresponds to the target status.
        """
        if self.status == target_status:
            process()
            self.save()

    @transition(field=status, source=Status.MODERATION, target=Status.REJECTED)
    def reject_by_admin(self):
        self.schedule_deletion(REMOVAL_DELAY_POST_IN_SECONDS)

    @transition(field=status, source=Status.MODERATION, target=Status.PUBLISHED)
    def approve_by_admin(self):
        self.published_date = timezone.now()

    @transition(field=status,
                source=(Status.MODERATION, Status.PUBLISHED),
                target=Status.DELETED)
    def delete_by_user(self):
        self.schedule_deletion(REMOVAL_DELAY_POST_IN_SECONDS)

    @transition(field=status, source=Status.PUBLISHED, target=Status.MODERATION)
    def edit_by_user(self):
        ...

    @transition(field=status, source=Status.REJECTED, target=Status.MODERATION)
    def restore_by_admin(self):
        cancel_post_deletion(self.id)

    @transition(field=status,
                source=Status.DELETED,
                target=GET_STATE(get_restore_target_state,
                                 states=[Status.MODERATION, Status.PUBLISHED]))
    def restore_by_user(self, is_published):
        cancel_post_deletion(self.id)

    def __str__(self):
        return self.title

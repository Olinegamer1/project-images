from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.text import slugify

from .models.post import Post


@receiver(pre_save, sender=Post)
def update_post_slug(sender, instance, **kwargs):
    instance.slug = slugify(instance.title)

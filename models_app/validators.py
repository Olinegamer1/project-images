from django.core.exceptions import ValidationError
from django.template.defaultfilters import filesizeformat
from project_images.settings import (MAX_SIZE_FILE_MB,
                                     MIN_WIDTH_IMAGE,
                                     MIN_HEIGHT_IMAGE)


def validate_image_dimensions(image):
    width, height = image.width, image.height

    if width < MIN_WIDTH_IMAGE or height < MIN_HEIGHT_IMAGE:
        raise ValidationError(f'Image dimension must be at least 400x400 pixels.')


def validate_image_file_size(image):
    if image.size >= MAX_SIZE_FILE_MB:
        raise ValidationError(f'Your file size: {filesizeformat(image.size)}.'
                              f' Max file size: {filesizeformat(MAX_SIZE_FILE_MB)}.')

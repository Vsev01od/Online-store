from django.db import models


class BaseModelIsPublished(models.Model):
    is_published = models.BooleanField(default=False)

    class Meta:
        abstract = True
        verbose_name = "основа публикации"
        verbose_name_plural = "основные публикации"

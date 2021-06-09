from django.db import models


class User(models.Model):
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    external_id = models.BigIntegerField(verbose_name='Telegram id', null=False, primary_key=True)
    name = models.CharField(verbose_name="Telegram name", max_length=60)
    is_moderator = models.BooleanField(verbose_name="Has Moderator rights", default=False)

    def __str__(self):
        return self.name


class MediaContent(models.Model):
    class Meta:
        verbose_name = 'Media Content'
        verbose_name_plural = 'Media Content'

    displayed_name = models.CharField(verbose_name='Displayed name', max_length=60)
    filepath = models.CharField(verbose_name='Path to content file', max_length=1000)
    author = models.ForeignKey(User, null=True, default=None, on_delete=models.CASCADE)

    likers = models.ManyToManyField('User', verbose_name='Users, who hit like', related_name='liked_media_content',
                                    blank=True)

    @property
    def likes(self):
        return self.likers.distinct().count()

    def __str__(self):
        return self.displayed_name

from django.db import models


class CommentQuerySet(models.QuerySet):
    def for_post(self, post):
        return self.filter(post=post)

    def for_user(self, user):
        return self.filter(author=user)


class CommentManager(models.Manager):
    def get_queryset(self):
        return CommentQuerySet(self.model, using=self._db)

    def for_post(self, post):
        return self.get_queryset().for_post(post)

    def for_user(self, user):
        return self.get_queryset().for_user(user)

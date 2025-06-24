from django.db import models


class ReactionQuerySet(models.QuerySet):
    def for_post(self, post):
        return self.filter(post=post)

    def by_user(self, user):
        return self.filter(user=user)

    def has_liked(self, user, post):
        return self.filter(user=user, post=post).exists()


class ReactionManager(models.Manager):
    def get_queryset(self):
        return ReactionQuerySet(self.model, using=self._db)

    def for_post(self, post):
        return self.get_queryset().for_post(post)

    def by_user(self, user):
        return self.get_queryset().by_user(user)

    def has_liked(self, user, post):
        return self.get_queryset().has_liked(user, post)

    def like(self, user, post):
        obj, created = self.get_or_create(user=user, post=post)
        return obj, created

    def unlike(self, user, post):
        return self.filter(user=user, post=post).delete()

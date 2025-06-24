from django.db import models


class FollowQuerySet(models.QuerySet):
    def following(self, user):
        return self.filter(follower=user).select_related('followed')

    def followers(self, user):
        return self.filter(followed=user).select_related('follower')

    def is_following(self, follower, followed):
        return self.filter(follower=follower, followed=followed).exists()


class FollowManager(models.Manager):
    def get_queryset(self):
        return FollowQuerySet(self.model, using=self._db)

    def following(self, user):
        return self.get_queryset().following(user)

    def followers(self, user):
        return self.get_queryset().followers(user)

    def is_following(self, follower, followed):
        return self.get_queryset().is_following(follower, followed)

    def follow(self, follower, followed):
        if follower == followed:
            return None, False
        obj, created = self.get_or_create(follower=follower, followed=followed)
        return obj, created

    def unfollow(self, follower, followed):
        return self.filter(follower=follower, followed=followed).delete()

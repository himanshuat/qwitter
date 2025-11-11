from django.db import models


class FollowQuerySet(models.QuerySet):
    def following(self, user):
        """Get users that the given user is following."""
        return self.filter(follower=user).select_related("followed")

    def followers(self, user):
        """Get users following the given user."""
        return self.filter(followed=user).select_related("follower")

    def is_following(self, follower, followed):
        """Check if follower is following followed."""
        return self.filter(follower=follower, followed=followed).exists()

    def with_follower(self):
        """Prefetch follower user details."""
        return self.select_related("follower")

    def with_followed(self):
        """Prefetch followed user details."""
        return self.select_related("followed")

    def with_both(self):
        """Prefetch both follower and followed user details."""
        return self.select_related("follower", "followed")

    def mutual_follows(self, user):
        """
        Get mutual follows for a user (users who follow each other).
        Returns users where both follow each other.
        """
        following_ids = self.filter(follower=user).values_list("followed", flat=True)
        followers_ids = self.filter(followed=user).values_list("follower", flat=True)
        mutual_ids = set(following_ids) & set(followers_ids)

        return self.filter(follower=user, followed__in=mutual_ids).select_related(
            "followed"
        )


class FollowManager(models.Manager):
    def get_queryset(self):
        return FollowQuerySet(self.model, using=self._db)

    def following(self, user):
        """
        Optimized query to get list of users being followed.
        Returns Follow objects with followed user prefetched.
        """
        return self.get_queryset().following(user).order_by("-created_date")

    def followers(self, user):
        """
        Optimized query to get list of followers.
        Returns Follow objects with follower user prefetched.
        """
        return self.get_queryset().followers(user).order_by("-created_date")

    def is_following(self, follower, followed):
        """
        Check if follower is following followed.
        Note: For checking multiple users, use with_follow_status() instead.
        """
        return self.get_queryset().is_following(follower, followed)

    def follow(self, follower, followed):
        """
        Follow a user. Returns (follow_obj, created).
        Returns (None, False) if trying to follow self.
        """
        if follower == followed:
            return None, False
        obj, created = self.get_or_create(follower=follower, followed=followed)
        return obj, created

    def unfollow(self, follower, followed):
        """
        Unfollow a user. Returns (count, details) from delete().
        """
        return self.filter(follower=follower, followed=followed).delete()

    def toggle(self, follower, followed):
        """
        Toggle follow status. Returns (is_following: bool, follow_obj or None).
        Returns (False, None) if trying to follow self.
        """
        if follower == followed:
            return False, None

        if self.is_following(follower, followed):
            self.unfollow(follower, followed)
            return False, None
        else:
            obj, _ = self.follow(follower, followed)
            return True, obj

    def following_count(self, user):
        """Count how many users the given user is following."""
        return self.filter(follower=user).count()

    def followers_count(self, user):
        """Count how many followers the given user has."""
        return self.filter(followed=user).count()

    def mutual_follows(self, user):
        """Get mutual follows for a user."""
        return self.get_queryset().mutual_follows(user)

    def with_follower(self):
        return self.get_queryset().with_follower()

    def with_followed(self):
        return self.get_queryset().with_followed()

    def with_both(self):
        return self.get_queryset().with_both()

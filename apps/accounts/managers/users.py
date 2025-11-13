from django.contrib.auth.models import UserManager as BaseUserManager
from django.db import models
from django.db.models import Count, Exists, OuterRef


class UserQuerySet(models.QuerySet):
    def with_follow_counts(self):
        """
        Annotate users with follower and following counts.
        """
        return self.annotate(
            followers_count=Count("followers", distinct=True),
            following_count=Count("following", distinct=True),
        )

    def with_post_count(self):
        """Annotate users with their post count."""
        return self.annotate(posts_count=Count("posts", distinct=True))

    def with_all_counts(self):
        """Annotate with all counts: followers, following, posts."""
        return self.annotate(
            followers_count=Count("followers", distinct=True),
            following_count=Count("following", distinct=True),
            posts_count=Count("posts", distinct=True),
        )

    def with_follow_status(self, user):
        """
        Annotate whether user is following each user in queryset.
        Returns: is_following (bool)
        """
        if not user or not user.is_authenticated:
            return self.annotate(
                is_following=models.Value(False, output_field=models.BooleanField())
            )

        from apps.feed.models import Follow

        return self.annotate(
            is_following=Exists(
                Follow.objects.filter(follower=user, followed=OuterRef("pk"))
            )
        )

    def following_of(self, user):
        """Get users that the given user is following, ordered by follow date."""
        return (
            self.filter(following__followed=user)
            .only("username", "name", "image")
            .order_by("-following__created_date")
        )

    def followers_of(self, user):
        """Get users who are following the given user, ordered by follow date."""
        return (
            self.filter(followers__follower=user)
            .only("username", "name", "image")
            .order_by("-followers__created_date")
        )

    def active(self):
        """Get only active users."""
        return self.filter(is_active=True)

    def search(self, query):
        """
        Search users by username, name, or email.
        Case-insensitive search.
        """
        return self.filter(
            models.Q(username__icontains=query)
            | models.Q(name__icontains=query)
            | models.Q(email__icontains=query)
        )


class UserManager(BaseUserManager):
    """
    Custom User Manager extending Django's UserManager.
    Inherits create_user, create_superuser, etc.
    """

    def get_queryset(self):
        return UserQuerySet(self.model, using=self._db)

    def with_follow_counts(self):
        return self.get_queryset().with_follow_counts()

    def with_post_count(self):
        return self.get_queryset().with_post_count()

    def with_all_counts(self):
        return self.get_queryset().with_all_counts()

    def with_follow_status(self, user):
        return self.get_queryset().with_follow_status(user)

    def following_of(self, user):
        return self.get_queryset().following_of(user)

    def followers_of(self, user):
        return self.get_queryset().followers_of(user)

    def active(self):
        return self.get_queryset().active()

    def search(self, query):
        """
        Search for users with counts pre-annotated.
        Useful for user discovery/search pages.
        """
        return self.get_queryset().search(query).with_all_counts()

    def get_profile(self, username, user=None):
        """
        Optimized query for profile page.
        Returns user with counts and follow status.
        """
        qs = (
            self.get_queryset()
            .only(
                "username",
                "name",
                "image",
                "bio",
                "dob",
                "date_joined",
                "is_active",
            )
            .with_all_counts()
        )
        if user:
            qs = qs.with_follow_status(user)
        return qs.get(username__iexact=username)

    def suggested_users(self, user, limit=5):
        """
        Get suggested users to follow.
        Excludes: current user, users already followed, inactive users.
        Orders by: most followers.
        """
        from apps.feed.models import Follow

        following_ids = Follow.objects.filter(follower=user).values_list(
            "followed", flat=True
        )

        return (
            self.get_queryset()
            .active()
            .exclude(pk=user.pk)
            .exclude(pk__in=following_ids)
            .with_follow_counts()
            .order_by("-followers_count")[:limit]
        )

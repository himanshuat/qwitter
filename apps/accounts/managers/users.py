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

    def with_follow_status(self, current_user):
        """
        Annotate whether current_user is following each user in queryset.
        Returns: is_following (bool)
        """
        if not current_user or not current_user.is_authenticated:
            return self.annotate(
                is_following=models.Value(False, output_field=models.BooleanField())
            )

        from apps.feed.models import Follow

        return self.annotate(
            is_following=Exists(
                Follow.objects.filter(follower=current_user, followed=OuterRef("pk"))
            )
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

    def with_follow_status(self, current_user):
        return self.get_queryset().with_follow_status(current_user)

    def active(self):
        return self.get_queryset().active()

    def search(self, query):
        """
        Search for users with counts pre-annotated.
        Useful for user discovery/search pages.
        """
        return self.get_queryset().search(query).with_all_counts()

    def get_profile(self, username, current_user=None):
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
        if current_user:
            qs = qs.with_follow_status(current_user)
        return qs.get(username__iexact=username)

    def suggested_users(self, current_user, limit=5):
        """
        Get suggested users to follow.
        Excludes: current user, users already followed, inactive users.
        Orders by: most followers.
        """
        from apps.feed.models import Follow

        following_ids = Follow.objects.filter(follower=current_user).values_list(
            "followed", flat=True
        )

        return (
            self.get_queryset()
            .active()
            .exclude(pk=current_user.pk)
            .exclude(pk__in=following_ids)
            .with_follow_counts()
            .order_by("-followers_count")[:limit]
        )

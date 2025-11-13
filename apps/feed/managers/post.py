from django.db import models
from django.db.models import Count, Exists, OuterRef, Q, Prefetch

from apps.accounts.models import Follow


class PostQuerySet(models.QuerySet):
    def by_user(self, user):
        """Get posts by a specific user."""
        return self.filter(author=user)

    def with_counts(self):
        """
        Annotate posts with reaction, comment, and repost counts.
        Solves N+1 query problem for count properties.
        """
        return self.annotate(
            reactions_count=Count("reactions", distinct=True),
            comments_count=Count("comments", distinct=True),
            reposts_count=Count(
                "reposts",
                filter=Q(reposts__body="") | Q(reposts__body__isnull=True),
                distinct=True,
            ),
            quotes_count=Count(
                "reposts",
                filter=~Q(reposts__body="") & ~Q(reposts__body__isnull=True),
                distinct=True,
            ),
        )

    def with_user_interactions(self, user):
        """
        Annotate whether the given user has liked or bookmarked each post.
        Returns: is_liked (bool), is_bookmarked (bool)
        """
        if not user or not user.is_authenticated:
            return self.annotate(
                is_liked=models.Value(False, output_field=models.BooleanField()),
                is_reposted=models.Value(False, output_field=models.BooleanField()),
                is_bookmarked=models.Value(False, output_field=models.BooleanField()),
            )

        from apps.feed.models import Bookmark, Post, Reaction

        return self.annotate(
            is_liked=Exists(Reaction.objects.filter(post=OuterRef("pk"), user=user)),
            is_bookmarked=Exists(
                Bookmark.objects.filter(post=OuterRef("pk"), user=user)
            ),
            is_reposted=Exists(
                Post.objects.filter(parent=OuterRef("pk"), author=user, body="")
                | Post.objects.filter(
                    parent=OuterRef("pk"), author=user, body__isnull=True
                )
            ),
        )

    def with_author(self):
        """Prefetch author to avoid additional queries."""
        return self.select_related("author")

    def with_parent(self, user=None):
        """
        Prefetch parent post with counts and user interactions.
        """
        # Build the parent queryset with annotations
        parent_qs = self.model.objects.select_related("author").annotate(
            reactions_count=Count("reactions", distinct=True),
            comments_count=Count("comments", distinct=True),
            reposts_count=Count(
                "reposts",
                filter=Q(reposts__body="") | Q(reposts__body__isnull=True),
                distinct=True,
            ),
            quotes_count=Count(
                "reposts",
                filter=~Q(reposts__body="") & ~Q(reposts__body__isnull=True),
                distinct=True,
            ),
        )

        from apps.feed.models import Bookmark, Post, Reaction

        # Add user interactions if user provided
        if user and user.is_authenticated:

            parent_qs = parent_qs.annotate(
                is_liked=Exists(
                    Reaction.objects.filter(post=OuterRef("pk"), user=user)
                ),
                is_bookmarked=Exists(
                    Bookmark.objects.filter(post=OuterRef("pk"), user=user)
                ),
                is_reposted=Exists(
                    Post.objects.filter(parent=OuterRef("pk"), author=user).filter(
                        Q(body="") | Q(body__isnull=True)
                    )
                ),
                is_quoted=Exists(
                    Post.objects.filter(parent=OuterRef("pk"), author=user).exclude(
                        Q(body="") | Q(body__isnull=True)
                    )
                ),
            )
        else:
            parent_qs = parent_qs.annotate(
                is_liked=models.Value(False, output_field=models.BooleanField()),
                is_bookmarked=models.Value(False, output_field=models.BooleanField()),
                is_reposted=models.Value(False, output_field=models.BooleanField()),
                is_quoted=models.Value(False, output_field=models.BooleanField()),
            )

        # Use Prefetch to replace parent relationship with annotated queryset
        return self.prefetch_related(Prefetch("parent", queryset=parent_qs))

    def with_full_details(self, user=None):
        """
        Full optimization for post detail/feed views.
        Includes: author, parent, counts, user interactions.
        """
        qs = self.with_author().with_counts()

        # Add parent with its own counts/interactions
        if user:
            qs = qs.with_parent(user).with_user_interactions(user)
        else:
            qs = qs.with_parent()

        return qs

    def feed_for_user(self, user):
        """
        Optimized feed query for a specific user's following.
        Use this for the "Following" feed view.
        """

        followed_users = Follow.objects.filter(follower=user).values_list(
            "followed", flat=True
        )

        return (
            self.filter(author__in=followed_users)
            .with_full_details(user)
            .order_by("-created_date")
        )

    def bookmarked_by(self, user):
        """Get posts bookmarked by a specific user, ordered by bookmark date."""
        return self.filter(bookmarks__user=user).order_by("-bookmarks__created_date")

    def liked_by(self, user):
        """Get posts liked by a specific user, ordered by reaction date."""
        return self.filter(reactions__user=user).order_by("-reactions__created_date")


class PostManager(models.Manager):
    def get_queryset(self):
        return PostQuerySet(self.model, using=self._db)

    def by_user(self, user):
        return self.get_queryset().by_user(user)

    def with_counts(self):
        return self.get_queryset().with_counts()

    def with_user_interactions(self, user):
        return self.get_queryset().with_user_interactions(user)

    def with_author(self):
        return self.get_queryset().with_author()

    def with_parent(self, user=None):
        return self.get_queryset().with_parent(user)

    def with_full_details(self, user=None):
        return self.get_queryset().with_full_details(user)

    def feed_for_user(self, user):
        return self.get_queryset().feed_for_user(user)

    def bookmarked_by(self, user):
        return self.get_queryset().bookmarked_by(user)

    def liked_by(self, user):
        return self.get_queryset().liked_by(user)

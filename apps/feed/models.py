from django.core.exceptions import ValidationError
from django.db import models
from apps.core.models import TimeStampedModel
from apps.accounts.models import User

from apps.feed.managers.bookmark import BookmarkManager
from apps.feed.managers.comment import CommentManager
from apps.feed.managers.follow import FollowManager
from apps.feed.managers.post import PostManager
from apps.feed.managers.reaction import ReactionManager


class Follow(TimeStampedModel):
    follower = models.ForeignKey(
        User,
        related_name="following",
        on_delete=models.CASCADE,
        help_text="User who is following another user.",
    )
    followed = models.ForeignKey(
        User,
        related_name="followers",
        on_delete=models.CASCADE,
        help_text="User who is being followed.",
    )

    objects = FollowManager()

    class Meta:
        verbose_name = "Follow"
        verbose_name_plural = "Follows"
        ordering = ["-created_date"]
        constraints = [
            models.UniqueConstraint(
                fields=["follower", "followed"], name="unique_follow"
            )
        ]
        indexes = [
            models.Index(fields=["follower", "-created_date"]),
            models.Index(fields=["followed", "-created_date"]),
        ]

    def __str__(self):
        return f"@{self.follower} follows @{self.followed}"

    def clean(self):
        if self.follower == self.followed:
            raise ValidationError("Users cannot follow themselves.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class Post(TimeStampedModel):
    author = models.ForeignKey(
        User,
        related_name="posts",
        on_delete=models.CASCADE,
        help_text="Author of the post.",
        db_index=True,
    )
    body = models.TextField(
        max_length=280,
        blank=True,
        null=True,
        help_text="Text content of the post (max 280 characters). Leave blank if repost.",
    )
    parent = models.ForeignKey(
        "self",
        related_name="reposts",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="If this is a repost or quote, the original post.",
        db_index=True,
    )
    is_pinned = models.BooleanField(
        default=False,
        help_text="Mark the post as pinned to appear at the top of user's profile.",
    )

    objects = PostManager()

    class Meta:
        verbose_name = "Post"
        verbose_name_plural = "Posts"
        ordering = ["-created_date"]
        indexes = [
            models.Index(fields=["author", "-created_date"]),
            models.Index(fields=["parent", "-created_date"]),
            models.Index(fields=["author", "-is_pinned", "-created_date"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["author", "parent"],
                condition=models.Q(body="") | models.Q(body__isnull=True),
                name="unique_repost_per_user",
            )
        ]

    def __str__(self):
        if self.is_quote:
            return f"@{self.author} quoted: {self.body[:20]}"
        elif self.is_repost:
            return f"@{self.author} reposted"
        return f"@{self.author}: {self.body[:20]}"

    def clean(self):
        # Prevent self-parenting and circular repost chains
        if self.parent:
            if self.parent == self:
                raise ValidationError("Post cannot reference itself as parent.")
            if self._creates_loop():
                raise ValidationError("Post repost/quote chain cannot form a loop.")

        if self.parent.is_repost:
            raise ValidationError(
                "Cannot repost or quote a repost. Only posts and quotes can be reposted/quoted."
            )

        if self.is_pinned and self.is_repost:
            raise ValidationError(
                "Cannot pin a repost. Only posts and quotes can be pinned."
            )

        has_parent = bool(self.parent)
        has_body = bool(self.body and str(self.body).strip())

        if not has_parent and not has_body:
            raise ValidationError("A post must have a body or reference a parent post.")

    def _creates_loop(self):
        """Check if this post indirectly reposts itself through ancestors."""
        ancestor = self.parent
        while ancestor:
            if ancestor == self:
                return True
            ancestor = ancestor.parent
        return False

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def is_original(self):
        return self.parent is None and self.body

    @property
    def is_repost(self):
        return self.parent is not None and not self.body

    @property
    def is_quote(self):
        return self.parent is not None and self.body

    @property
    def reactions_count(self):
        return self.reactions.count()

    @property
    def comments_count(self):
        return self.comments.count()

    @property
    def reposts_count(self):
        return self.reposts.filter(body="").count()

    @property
    def quotes_count(self):
        return self.reposts.exclude(body="").count()

    @property
    def type(self) -> str:
        """
        Return the type of post:
        - 'original' → a standalone post with no parent
        - 'repost'   → a repost (has a parent, no body)
        - 'quote'    → a quote post (has a parent and a body)
        """
        if self.is_quote:
            return "quote"
        if self.is_repost:
            return "repost"
        return "original"


class Comment(TimeStampedModel):
    author = models.ForeignKey(
        User,
        related_name="comments",
        on_delete=models.CASCADE,
        help_text="Author of the comment.",
    )
    post = models.ForeignKey(
        Post,
        related_name="comments",
        on_delete=models.CASCADE,
        help_text="The post this comment belongs to.",
        db_index=True,
    )
    body = models.TextField(
        max_length=280, help_text="Content of the comment (max 280 characters)."
    )

    objects = CommentManager()

    class Meta:
        verbose_name = "Comment"
        verbose_name_plural = "Comments"
        ordering = ["-created_date"]
        indexes = [
            models.Index(fields=["post", "-created_date"]),
        ]

    def __str__(self):
        return f"@{self.author} commented: {self.body[:20]}"

    def clean(self):
        if self.post and self.post.is_repost:
            raise ValidationError(
                "Cannot comment on a repost. Comments are only allowed on posts and quotes."
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class Reaction(TimeStampedModel):
    user = models.ForeignKey(
        User,
        related_name="reactions",
        on_delete=models.CASCADE,
        help_text="User who reacted to the post.",
    )
    post = models.ForeignKey(
        Post,
        related_name="reactions",
        on_delete=models.CASCADE,
        help_text="Post that was reacted to.",
        db_index=True,
    )

    objects = ReactionManager()

    class Meta:
        verbose_name = "Reaction"
        verbose_name_plural = "Reactions"
        ordering = ["-created_date"]
        constraints = [
            models.UniqueConstraint(fields=["user", "post"], name="unique_reaction")
        ]

    def __str__(self):
        return f"@{self.user} liked post #{self.post.id}"

    def clean(self):
        if self.post and self.post.is_repost:
            raise ValidationError(
                "Cannot react to a repost. Reactions are only allowed on posts and quotes."
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class Bookmark(TimeStampedModel):
    user = models.ForeignKey(
        User,
        related_name="bookmarks",
        on_delete=models.CASCADE,
        help_text="User who bookmarked the post.",
    )
    post = models.ForeignKey(
        Post,
        related_name="bookmarks",
        on_delete=models.CASCADE,
        help_text="Bookmarked post.",
        db_index=True,
    )

    objects = BookmarkManager()

    class Meta:
        verbose_name = "Bookmark"
        verbose_name_plural = "Bookmarks"
        ordering = ["-created_date"]
        constraints = [
            models.UniqueConstraint(fields=["user", "post"], name="unique_bookmark")
        ]
        indexes = [
            models.Index(fields=["user", "-created_date"]),
        ]

    def __str__(self):
        return f"@{self.user} bookmarked post #{self.post.id}"

    def clean(self):
        if self.post and self.post.is_repost:
            raise ValidationError(
                "Cannot bookmark a repost. Bookmarks are only allowed on posts and quotes."
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

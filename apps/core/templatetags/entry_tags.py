from django import template

register = template.Library()

@register.filter
def has_liked(user, post):
    return user.is_authenticated and user.reactions.filter(post=post).exists()


@register.filter
def has_bookmarked(user, post):
    return user.is_authenticated and user.bookmarks.filter(post=post).exists()


@register.filter
def is_following(user, target_user):
    """
    Check if the logged-in user follows the given target_user.
    """
    if not user.is_authenticated or user == target_user:
        return False
    return user.following.filter(followed=target_user).exists()
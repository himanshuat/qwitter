"""
Custom throttle classes for Qwitter API rate limiting.

This module provides comprehensive rate limiting for all API endpoints,
with admin/staff exemptions and action-specific throttle rates.
"""

from rest_framework.throttling import UserRateThrottle, AnonRateThrottle


class AdminExemptUserRateThrottle(UserRateThrottle):
    """
    Base throttle class that exempts admin and staff users from rate limiting.
    
    All authenticated user throttles should inherit from this class to ensure
    that administrators and staff members can bypass rate limits for testing
    and administrative purposes.
    """

    def allow_request(self, request, view):
        """
        Check if the request should be allowed.
        
        Admin and staff users bypass all throttling. Regular users are subject
        to the configured rate limits.
        
        Args:
            request: The incoming HTTP request
            view: The view being accessed
            
        Returns:
            bool: True if request is allowed, False if throttled
        """
        # Exempt authenticated staff and superusers from all throttling
        if request.user and request.user.is_authenticated:
            if request.user.is_staff or request.user.is_superuser:
                return True
        
        # Apply normal throttling for non-admin users
        return super().allow_request(request, view)


# ============================================================================
# AUTHENTICATION THROTTLES
# ============================================================================

class AuthLoginThrottle(AdminExemptUserRateThrottle):
    """
    Rate limit for login attempts to prevent brute force attacks.
    Scope: auth_login (5 requests/hour)
    """
    scope = "auth_login"


class AuthRegisterThrottle(AdminExemptUserRateThrottle):
    """
    Rate limit for user registration to prevent spam account creation.
    Scope: auth_register (3 requests/hour)
    """
    scope = "auth_register"


class TokenRefreshThrottle(AdminExemptUserRateThrottle):
    """
    Rate limit for JWT token refresh requests.
    Scope: token_refresh (100 requests/hour)
    """
    scope = "token_refresh"


class TokenVerifyThrottle(AdminExemptUserRateThrottle):
    """
    Rate limit for JWT token verification requests.
    Scope: token_verify (200 requests/hour)
    """
    scope = "token_verify"


# ============================================================================
# ACCOUNT MANAGEMENT THROTTLES
# ============================================================================

class PasswordChangeThrottle(AdminExemptUserRateThrottle):
    """
    Rate limit for password change operations.
    Scope: password_change (3 requests/hour)
    """
    scope = "password_change"


class EmailChangeThrottle(AdminExemptUserRateThrottle):
    """
    Rate limit for email address change operations.
    Scope: email_change (3 requests/hour)
    """
    scope = "email_change"


class UsernameChangeThrottle(AdminExemptUserRateThrottle):
    """
    Rate limit for username change operations.
    Scope: username_change (3 requests/hour)
    """
    scope = "username_change"


class AccountDeactivateThrottle(AdminExemptUserRateThrottle):
    """
    Rate limit for account deactivation requests.
    Scope: account_deactivate (2 requests/hour)
    """
    scope = "account_deactivate"


class ProfileEditThrottle(AdminExemptUserRateThrottle):
    """
    Rate limit for profile editing operations.
    Scope: profile_edit (10 requests/hour)
    """
    scope = "profile_edit"


# ============================================================================
# POST CONTENT THROTTLES
# ============================================================================

class PostCreateThrottle(AdminExemptUserRateThrottle):
    """
    Rate limit for creating new posts.
    Scope: post_create (20 requests/hour)
    """
    scope = "post_create"


class PostQuoteThrottle(AdminExemptUserRateThrottle):
    """
    Rate limit for creating quote posts.
    Scope: post_quote (20 requests/hour)
    """
    scope = "post_quote"


class PostRepostThrottle(AdminExemptUserRateThrottle):
    """
    Rate limit for reposting content.
    Scope: post_repost (30 requests/hour)
    """
    scope = "post_repost"


class PostEditThrottle(AdminExemptUserRateThrottle):
    """
    Rate limit for editing existing posts.
    Scope: post_edit (30 requests/hour)
    """
    scope = "post_edit"


class PostDeleteThrottle(AdminExemptUserRateThrottle):
    """
    Rate limit for deleting posts.
    Scope: post_delete (10 requests/hour)
    """
    scope = "post_delete"


# ============================================================================
# COMMENT THROTTLES
# ============================================================================

class CommentCreateThrottle(AdminExemptUserRateThrottle):
    """
    Rate limit for creating comments.
    Scope: comment_create (30 requests/hour)
    """
    scope = "comment_create"


class CommentEditThrottle(AdminExemptUserRateThrottle):
    """
    Rate limit for editing comments.
    Scope: comment_edit (30 requests/hour)
    """
    scope = "comment_edit"


class CommentDeleteThrottle(AdminExemptUserRateThrottle):
    """
    Rate limit for deleting comments.
    Scope: comment_delete (10 requests/hour)
    """
    scope = "comment_delete"


# ============================================================================
# INTERACTION THROTTLES
# ============================================================================

class FollowActionThrottle(AdminExemptUserRateThrottle):
    """
    Rate limit for follow/unfollow actions.
    Scope: follow_action (30 requests/hour)
    """
    scope = "follow_action"


class LikeActionThrottle(AdminExemptUserRateThrottle):
    """
    Rate limit for like/unlike (reaction) actions.
    Scope: like_action (100 requests/hour)
    """
    scope = "like_action"


class BookmarkActionThrottle(AdminExemptUserRateThrottle):
    """
    Rate limit for bookmark/unbookmark actions.
    Scope: bookmark_action (100 requests/hour)
    """
    scope = "bookmark_action"


class PinActionThrottle(AdminExemptUserRateThrottle):
    """
    Rate limit for pin/unpin post actions.
    Scope: pin_action (10 requests/hour)
    """
    scope = "pin_action"

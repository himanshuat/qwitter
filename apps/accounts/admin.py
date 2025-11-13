from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from apps.accounts.models import Follow, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    model = User
    list_display = ("avatar_tag", "username", "name", "email", "is_active")
    search_fields = ("username", "email", "name")
    readonly_fields = ("avatar_tag", "last_login", "date_joined")

    fieldsets = (
        (_("Credentials"), {"fields": ("username", "password")}),
        (
            _("Personal Info"),
            {"fields": ("name", "email", "image", "dob", "bio", "avatar_tag")},
        ),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "name", "email", "password1", "password2"),
            },
        ),
    )

    def avatar_tag(self, obj):
        return obj.avatar_tag

    avatar_tag.short_description = "Avatar"


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ("follower", "followed", "created_date")
    search_fields = ("follower__username", "followed__username")
    list_filter = ("created_date",)
    ordering = ("-created_date",)

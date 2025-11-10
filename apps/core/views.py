from django.shortcuts import render


def error_400_view(request, exception):
    """Handle 400 Bad Request errors."""
    return render(request, "errors/400.html", status=400)


def error_403_view(request, exception):
    """Handle 403 Forbidden errors."""
    return render(request, "errors/403.html", status=403)


def error_404_view(request, exception):
    """Handle 404 Not Found errors."""

    path = request.path
    context = {
        "path": path,
    }

    if "/post/" in path:
        context["title"] = "Post Not Found"
        context["message"] = "This post may have been deleted or doesn't exist."
    elif path.startswith("/profile/") or "/@" in path:
        context["title"] = "User Not Found"
        context["message"] = (
            "This user doesn't exist or the account has been deactivated."
        )
    else:
        context["title"] = "Page Not Found"
        context["message"] = "The page you're looking for doesn't exist."

    return render(request, "errors/404.html", context, status=404)


def error_500_view(request):
    """Handle 500 Internal Server errors."""
    return render(request, "errors/500.html", status=500)

from django.contrib.auth.models import User

def user_context(request):
    user = request.user
    return {
        'current_user': user.username if user.is_authenticated else None,
        'is_authenticated': user.is_authenticated
    }
from functools import wraps

from django.http import JsonResponse

def staff_required_for_writes(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.method not in ("GET", "HEAD", "OPTIONS"):
            if not request.user.is_authenticated:
                return JsonResponse(
                    {"error": "Authentication required"},
                    status=401
                )

            if not request.user.is_staff:
                return JsonResponse(
                    {"error": "Staff access required"},
                    status=403,
                )

        return view_func(request, *args, **kwargs)

    return wrapper

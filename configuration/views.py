from django.http import JsonResponse


def custom_404_view(request, exception):
    return JsonResponse(
        {
            "status": False,
            "errors": "Error 404: URL not found",
            "data": None,
        },
        status=404,
    )

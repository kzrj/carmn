from django.http import JsonResponse
from django.views.decorators.http import require_GET

from .services import get_health_payload


@require_GET
def health_view(request):
    return JsonResponse(get_health_payload())

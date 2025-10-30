from django.http import JsonResponse
from django.views.decorators.http import require_GET

@require_GET
def handler400(request, exception=None):
    return JsonResponse({'error': 'Bad request'}, status=400)

@require_GET
def handler404(request, exception=None):
    return JsonResponse({'error': 'Endpoint not found'}, status=404)

@require_GET
def handler500(request):
    return JsonResponse({'error': 'Internal server error'}, status=500)
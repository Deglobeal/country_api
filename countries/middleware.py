from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin

class JSONErrorMiddleware(MiddlewareMixin):
    """Middleware that returns JSON errors instead of HTML"""
    def process_response(self, request, response):
        # If it's already a JSON response, leave it as is
        if response.get('Content-Type', '').startswith('application/json'):
            return response
        
        # Convert 404 errors to JSON
        if response.status_code == 404:
            return JsonResponse(
                {'error': 'Endpoint not found'}, 
                status=404,
            )
        
        # Convert 500 errors to JSON
        if response.status_code == 500:
            return JsonResponse(
                {'error': 'Internal server error'}, 
                status=500,
            )
        
        # Convert 400 errors to JSON
        if response.status_code == 400:
            return JsonResponse(
                {'error': 'Bad request'}, 
                status=400,
            )
        
        return response

    def process_exception(self, request, exception):
        """Handle uncaught exceptions and return JSON"""
        return JsonResponse(
            {'error': 'Internal server error'}, 
            status=500,
        )
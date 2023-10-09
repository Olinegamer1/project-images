from django.db.utils import IntegrityError, DataError, DatabaseError
from django.http import JsonResponse


class DataBaseErrorMiddleware:
    def __init__(self, get_response):
        self._get_response = get_response

    def __call__(self, request):
        return self._get_response(request)

    def process_exception(self, request, exception):
        if isinstance(exception, (IntegrityError, DataError, DatabaseError)):
            response_data = {'error': str(exception)}
            return JsonResponse(response_data, status=500)
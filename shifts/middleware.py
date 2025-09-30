from django.utils import translation

class ForceNorwegianMiddleware:
    """
    Forces all users to use Norwegian ('nb') regardless of browser settings.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        translation.activate('nb')
        request.LANGUAGE_CODE = 'nb'
        response = self.get_response(request)
        translation.deactivate()
        return response

"""
Test to reproduce the issue where the first middleware receives a coroutine
instead of an HttpResponse in ASGI mode.
"""
import asyncio
from asgiref.testing import ApplicationCommunicator
from django.core.asgi import get_asgi_application
from django.http import HttpResponse
from django.test import AsyncRequestFactory, SimpleTestCase, override_settings
from django.utils.deprecation import MiddlewareMixin


class TestMiddlewareCoroutineBug(SimpleTestCase):
    """Test that middleware receives HttpResponse, not coroutine."""
    
    async def test_first_middleware_receives_response_not_coroutine(self):
        """
        The first middleware in the chain should receive an HttpResponse object
        in its process_response() method, not a coroutine.
        """
        # Track what types are passed to process_response
        response_types = []
        
        class FirstMiddleware(MiddlewareMixin):
            def process_response(self, request, response):
                response_types.append(type(response).__name__)
                return response
        
        class SecondMiddleware(MiddlewareMixin):
            def process_response(self, request, response):
                response_types.append(type(response).__name__)
                return response
        
        # Create a simple ASGI app with our middleware
        from django.core.handlers.asgi import ASGIHandler
        from django.test.utils import override_settings
        
        with override_settings(
            MIDDLEWARE=[
                'test_middleware_coroutine_bug.FirstMiddleware',
                'test_middleware_coroutine_bug.SecondMiddleware',
            ],
            ROOT_URLCONF='asgi.urls',
        ):
            # We need to manually test the middleware chain
            async def get_response(request):
                return HttpResponse('test')
            
            # Create middleware instances
            second_mw = SecondMiddleware(get_response)
            first_mw = FirstMiddleware(second_mw)
            
            # Create a fake request
            from django.http import HttpRequest
            request = HttpRequest()
            request.method = 'GET'
            request.path = '/'
            
            # Call the first middleware
            response = await first_mw(request)
            
            # Check that both middlewares received HttpResponse, not coroutine
            print(f"Response types received: {response_types}")
            assert response_types[0] == 'HttpResponse', f"First middleware received {response_types[0]}, expected HttpResponse"
            assert response_types[1] == 'HttpResponse', f"Second middleware received {response_types[1]}, expected HttpResponse"


if __name__ == '__main__':
    import django
    from django.conf import settings
    
    if not settings.configured:
        settings.configure(
            DEBUG=True,
            DATABASES={
                'default': {
                    'ENGINE': 'django.db.backends.sqlite3',
                    'NAME': ':memory:',
                }
            },
            INSTALLED_APPS=[
                'django.contrib.contenttypes',
                'django.contrib.auth',
            ],
            MIDDLEWARE=[],
            ROOT_URLCONF='asgi.urls',
        )
        django.setup()
    
    # Run the test
    test = TestMiddlewareCoroutineBug()
    asyncio.run(test.test_first_middleware_receives_response_not_coroutine())
    print("Test passed!")

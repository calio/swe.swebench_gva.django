"""
Test to reproduce the issue where the first middleware receives a coroutine
instead of an HttpResponse in ASGI mode.

The real issue is when the first middleware doesn't have process_response,
but the second one does. In that case, the second middleware's process_response
receives the coroutine from the first middleware's __call__.
"""
import asyncio
from django.http import HttpResponse
from django.test import SimpleTestCase
from django.utils.deprecation import MiddlewareMixin


class TestMiddlewareCoroutineBug(SimpleTestCase):
    """Test that middleware receives HttpResponse, not coroutine."""
    
    async def test_first_middleware_without_process_response(self):
        """
        When the first middleware doesn't have process_response,
        the second middleware's process_response receives a coroutine.
        """
        # Track what types are passed to process_response
        response_types = []
        
        class FirstMiddleware(MiddlewareMixin):
            # No process_response method!
            pass
        
        class SecondMiddleware(MiddlewareMixin):
            def process_response(self, request, response):
                response_types.append(('second', type(response).__name__, asyncio.iscoroutine(response)))
                if asyncio.iscoroutine(response):
                    print("BUG FOUND: Second middleware received a coroutine!")
                return response
        
        # Create a simple async get_response
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
        
        # Call first_mw
        result = first_mw(request)
        print(f"first_mw(request) returned: {type(result).__name__}, is_coroutine={asyncio.iscoroutine(result)}")
        
        # Now we await it
        response = await result
        
        # Check what was received
        print(f"Response types received: {response_types}")
        for mw_name, type_name, is_coro in response_types:
            print(f"  {mw_name}: {type_name}, is_coroutine={is_coro}")


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
    asyncio.run(test.test_first_middleware_without_process_response())

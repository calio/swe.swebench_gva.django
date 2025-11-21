"""
Test to reproduce the issue where the first middleware receives a coroutine
instead of an HttpResponse in ASGI mode.

The key insight: when MiddlewareMixin.__call__ returns self.__acall__(request),
it returns a coroutine. But the middleware chain expects __call__ to return
the response directly (or a coroutine if the middleware is async-capable).

The problem is that __call__ is NOT marked as a coroutine function, so when
it returns a coroutine, the next middleware in the chain receives that coroutine
as the response from get_response.
"""
import asyncio
from django.http import HttpResponse
from django.test import SimpleTestCase
from django.utils.deprecation import MiddlewareMixin


class TestMiddlewareCoroutineBug(SimpleTestCase):
    """Test that middleware receives HttpResponse, not coroutine."""
    
    async def test_middleware_receives_coroutine_from_previous_middleware(self):
        """
        When the first middleware's __call__ returns a coroutine,
        the second middleware's get_response receives that coroutine.
        """
        # Track what types are passed to get_response
        get_response_types = []
        
        class FirstMiddleware(MiddlewareMixin):
            sync_capable = True
            async_capable = True
            
            def process_response(self, request, response):
                return response
        
        class SecondMiddleware(MiddlewareMixin):
            sync_capable = True
            async_capable = True
            
            def __init__(self, get_response):
                super().__init__(get_response)
                self.original_get_response = get_response
            
            def __call__(self, request):
                # Intercept what get_response returns
                result = self.original_get_response(request)
                get_response_types.append(('second_call', type(result).__name__, asyncio.iscoroutine(result)))
                if asyncio.iscoroutine(result):
                    print("BUG FOUND: Second middleware's get_response returned a coroutine!")
                return result
        
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
        print(f"get_response types: {get_response_types}")
        for name, type_name, is_coro in get_response_types:
            print(f"  {name}: {type_name}, is_coroutine={is_coro}")


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
    asyncio.run(test.test_middleware_receives_coroutine_from_previous_middleware())

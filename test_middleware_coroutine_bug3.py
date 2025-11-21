"""
Test to reproduce the issue where the first middleware receives a coroutine
instead of an HttpResponse in ASGI mode.

The issue is that when MiddlewareMixin.__call__() detects an async get_response,
it returns self.__acall__(request) which is a coroutine. This coroutine is then
passed to the next middleware's process_response() method.
"""
import asyncio
from django.http import HttpResponse
from django.test import SimpleTestCase
from django.utils.deprecation import MiddlewareMixin


class TestMiddlewareCoroutineBug(SimpleTestCase):
    """Test that middleware receives HttpResponse, not coroutine."""
    
    async def test_first_middleware_receives_response_not_coroutine(self):
        """
        The first middleware in the chain should receive an HttpResponse object
        in its process_response() method, not a coroutine.
        
        The bug occurs because:
        1. MiddlewareMixin.__call__() is synchronous
        2. When it detects async get_response, it returns self.__acall__(request)
        3. This returns a coroutine, not the actual response
        4. The next middleware receives this coroutine in process_response()
        """
        # Track what types are passed to process_response
        response_types = []
        
        class FirstMiddleware(MiddlewareMixin):
            def process_response(self, request, response):
                response_types.append(('first', type(response).__name__, asyncio.iscoroutine(response)))
                if asyncio.iscoroutine(response):
                    print("BUG FOUND: First middleware received a coroutine!")
                return response
        
        class SecondMiddleware(MiddlewareMixin):
            def process_response(self, request, response):
                response_types.append(('second', type(response).__name__, asyncio.iscoroutine(response)))
                return response
        
        # Create a simple async get_response
        async def get_response(request):
            return HttpResponse('test')
        
        # Create middleware instances - note the order!
        # In the middleware chain, the first middleware wraps the second
        second_mw = SecondMiddleware(get_response)
        first_mw = FirstMiddleware(second_mw)
        
        # Create a fake request
        from django.http import HttpRequest
        request = HttpRequest()
        request.method = 'GET'
        request.path = '/'
        
        # The issue: when we call first_mw(request), it calls __call__()
        # which detects that get_response (second_mw) is async and returns
        # self.__acall__(request) - a coroutine!
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
    asyncio.run(test.test_first_middleware_receives_response_not_coroutine())

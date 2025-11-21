"""
Test to reproduce the issue where the first middleware receives a coroutine
instead of an HttpResponse in ASGI mode.

Looking at the code flow:
1. BaseHandler.load_middleware() builds the middleware chain in reverse
2. Each middleware wraps the next one
3. When the first middleware's __call__ is invoked with an async get_response,
   it returns self.__acall__(request) - a coroutine
4. But the middleware chain expects __call__ to return the response directly

The issue is that __call__ should NOT return a coroutine when get_response is async.
Instead, it should be marked as a coroutine function itself.
"""
import asyncio
from django.http import HttpResponse
from django.test import SimpleTestCase
from django.utils.deprecation import MiddlewareMixin


class TestMiddlewareCoroutineBug(SimpleTestCase):
    """Test that middleware receives HttpResponse, not coroutine."""
    
    async def test_middleware_chain_with_sync_middleware(self):
        """
        When a sync middleware wraps an async middleware,
        the sync middleware's __call__ returns a coroutine.
        """
        # Track what types are passed to process_response
        response_types = []
        
        class FirstMiddleware(MiddlewareMixin):
            sync_capable = True
            async_capable = False
            
            def process_response(self, request, response):
                response_types.append(('first', type(response).__name__, asyncio.iscoroutine(response)))
                if asyncio.iscoroutine(response):
                    print("BUG FOUND: First middleware received a coroutine!")
                return response
        
        class SecondMiddleware(MiddlewareMixin):
            sync_capable = True
            async_capable = True
            
            def process_response(self, request, response):
                response_types.append(('second', type(response).__name__, asyncio.iscoroutine(response)))
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
    asyncio.run(test.test_middleware_chain_with_sync_middleware())

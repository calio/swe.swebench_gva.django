"""
Test to see if the second middleware's __call__ detects that get_response is async.
"""
import asyncio
from django.http import HttpResponse
from django.test import SimpleTestCase
from django.utils.deprecation import MiddlewareMixin


class TestMiddlewareCoroutineBug(SimpleTestCase):
    """Test that middleware receives HttpResponse, not coroutine."""
    
    async def test_middleware_detects_async_get_response(self):
        """
        Check if the second middleware's __call__ detects that get_response is async.
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
            
            def __call__(self, request):
                print(f"SecondMiddleware.__call__: asyncio.iscoroutinefunction(self.get_response) = {asyncio.iscoroutinefunction(self.get_response)}")
                return super().__call__(request)
        
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
    asyncio.run(test.test_middleware_detects_async_get_response())

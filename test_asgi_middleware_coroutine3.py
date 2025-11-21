"""
Test to reproduce the issue where the first middleware receives a coroutine
instead of an HttpResponse in ASGI mode.

The issue might occur when the first middleware doesn't have process_response.
"""
import asyncio
from django.http import HttpResponse
from django.test import SimpleTestCase
from django.utils.deprecation import MiddlewareMixin
from django.core.handlers.exception import convert_exception_to_response


class TestASGIMiddlewareCoroutine(SimpleTestCase):
    """Test that middleware receives HttpResponse, not coroutine in ASGI mode."""
    
    async def test_first_middleware_without_process_response(self):
        """
        When the first middleware doesn't have process_response,
        the second middleware should still receive an HttpResponse.
        """
        # Track what types are passed to process_response
        response_types = []
        
        class FirstMiddleware(MiddlewareMixin):
            sync_capable = True
            async_capable = False  # Sync-only!
            
            # No process_response!
        
        class SecondMiddleware(MiddlewareMixin):
            sync_capable = True
            async_capable = True
            
            def process_response(self, request, response):
                response_types.append(('second', type(response).__name__, asyncio.iscoroutine(response)))
                if asyncio.iscoroutine(response):
                    print("BUG: Second middleware received a coroutine!")
                return response
        
        # Create a simple async get_response (simulating the handler)
        async def get_response(request):
            return HttpResponse('test')
        
        # Build the middleware chain like BaseHandler.load_middleware() does
        handler = convert_exception_to_response(get_response)
        
        # Add second middleware
        second_mw = SecondMiddleware(handler)
        handler = convert_exception_to_response(second_mw)
        
        # Add first middleware (sync-only, no process_response)
        first_mw = FirstMiddleware(handler)
        handler = convert_exception_to_response(first_mw)
        
        # Create a fake request
        from django.http import HttpRequest
        request = HttpRequest()
        request.method = 'GET'
        request.path = '/'
        
        # Call the middleware chain (simulating ASGIHandler.get_response_async)
        response = await handler(request)
        
        # Check that the second middleware received HttpResponse, not coroutine
        print(f"Response types received: {response_types}")
        for mw_name, type_name, is_coro in response_types:
            print(f"  {mw_name}: {type_name}, is_coroutine={is_coro}")
        
        # Assert that no middleware received a coroutine
        for mw_name, type_name, is_coro in response_types:
            assert not is_coro, f"{mw_name} middleware received a coroutine!"


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
    test = TestASGIMiddlewareCoroutine()
    asyncio.run(test.test_first_middleware_without_process_response())
    print("Test passed!")

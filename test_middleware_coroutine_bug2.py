"""
Test to reproduce the issue where the first middleware receives a coroutine
instead of an HttpResponse in ASGI mode.
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
        """
        # Track what types are passed to process_response
        response_types = []
        
        class FirstMiddleware(MiddlewareMixin):
            def process_response(self, request, response):
                response_types.append(('first', type(response).__name__, asyncio.iscoroutine(response)))
                return response
        
        class SecondMiddleware(MiddlewareMixin):
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
        
        # Call the first middleware - this should be awaited
        response = await first_mw(request)
        
        # Check that both middlewares received HttpResponse, not coroutine
        print(f"Response types received: {response_types}")
        for mw_name, type_name, is_coro in response_types:
            print(f"  {mw_name}: {type_name}, is_coroutine={is_coro}")
        
        # The bug: first middleware receives a coroutine
        assert response_types[0][2] == False, f"First middleware received a coroutine!"
        assert response_types[1][2] == False, f"Second middleware received a coroutine!"


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

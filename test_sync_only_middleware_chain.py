"""
Test the middleware chain with a sync-only first middleware.
"""
import asyncio
from django.http import HttpResponse, HttpRequest
from django.utils.deprecation import MiddlewareMixin
from django.core.handlers.exception import convert_exception_to_response
from django.core.handlers.base import BaseHandler


class FirstMiddleware(MiddlewareMixin):
    sync_capable = True
    async_capable = False  # Sync-only!
    
    def process_response(self, request, response):
        print(f"FirstMiddleware.process_response: response type = {type(response).__name__}, is_coroutine = {asyncio.iscoroutine(response)}")
        if asyncio.iscoroutine(response):
            print("BUG: FirstMiddleware received a coroutine!")
        return response


class SecondMiddleware(MiddlewareMixin):
    sync_capable = True
    async_capable = True
    
    def process_response(self, request, response):
        print(f"SecondMiddleware.process_response: response type = {type(response).__name__}, is_coroutine = {asyncio.iscoroutine(response)}")
        return response


async def handler(request):
    return HttpResponse('test')


async def test():
    # Simulate BaseHandler.load_middleware(is_async=True)
    handler_func = convert_exception_to_response(handler)
    handler_is_async = True
    
    # Add second middleware
    second_mw = SecondMiddleware(handler_func)
    handler_func = convert_exception_to_response(second_mw)
    handler_is_async = True
    
    # Add first middleware (sync-only)
    # In BaseHandler.load_middleware(), it would adapt the handler if needed
    # Since the first middleware is sync-only and the handler is async,
    # it would wrap the handler with async_to_sync
    from asgiref.sync import async_to_sync
    handler_func = async_to_sync(handler_func)
    
    first_mw = FirstMiddleware(handler_func)
    handler_func = convert_exception_to_response(first_mw)
    
    # Create a fake request
    request = HttpRequest()
    request.method = 'GET'
    request.path = '/'
    
    # Call the middleware chain
    response = await handler_func(request)
    print(f"Final response type: {type(response).__name__}")


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
    
    asyncio.run(test())

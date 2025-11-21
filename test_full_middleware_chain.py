"""
Test the full middleware chain to see if the first middleware receives a coroutine.
"""
import asyncio
from django.http import HttpResponse, HttpRequest
from django.utils.deprecation import MiddlewareMixin
from django.core.handlers.exception import convert_exception_to_response


class FirstMiddleware(MiddlewareMixin):
    sync_capable = True
    async_capable = True
    
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
    # Build the middleware chain
    get_response = convert_exception_to_response(handler)
    
    # Add second middleware
    second_mw = SecondMiddleware(get_response)
    get_response = convert_exception_to_response(second_mw)
    
    # Add first middleware
    first_mw = FirstMiddleware(get_response)
    get_response = convert_exception_to_response(first_mw)
    
    # Create a fake request
    request = HttpRequest()
    request.method = 'GET'
    request.path = '/'
    
    # Call the middleware chain
    response = await get_response(request)
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

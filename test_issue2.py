import asyncio
from django.conf import settings
from django.http import HttpResponse
from django.utils.deprecation import MiddlewareMixin
from django.core.handlers.base import BaseHandler
from django.core.handlers.exception import convert_exception_to_response
from asgiref.sync import sync_to_async

# Configure Django settings
if not settings.configured:
    settings.configure(
        DEBUG=True,
        MIDDLEWARE=[
            'test_issue2.FirstMiddleware',
            'test_issue2.SecondMiddleware',
        ],
        ROOT_URLCONF='',
    )

class FirstMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        print(f"FirstMiddleware.process_response received: {type(response)}")
        print(f"Is coroutine: {asyncio.iscoroutine(response)}")
        if asyncio.iscoroutine(response):
            print("ERROR: Received a coroutine instead of HttpResponse!")
        return response

class SecondMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        print(f"SecondMiddleware.process_response received: {type(response)}")
        return response

async def test():
    from django.http import HttpRequest
    
    # Simulate what BaseHandler does
    handler = BaseHandler()
    handler.load_middleware(is_async=True)
    
    request = HttpRequest()
    response = await handler._middleware_chain(request)
    print(f"Final response: {type(response)}")

asyncio.run(test())

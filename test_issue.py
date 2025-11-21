import asyncio
from django.conf import settings
from django.http import HttpResponse
from django.utils.deprecation import MiddlewareMixin
from asgiref.sync import async_to_sync

# Configure Django settings
if not settings.configured:
    settings.configure(
        DEBUG=True,
        MIDDLEWARE=[],
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

async def get_response(request):
    return HttpResponse("OK")

# Simulate the middleware chain
async def test():
    from django.http import HttpRequest
    
    # Create middleware chain
    handler = get_response
    handler = SecondMiddleware(handler)
    handler = FirstMiddleware(handler)
    
    request = HttpRequest()
    response = await handler(request)
    print(f"Final response: {type(response)}")

asyncio.run(test())

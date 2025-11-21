"""
Test if the _is_coroutine marker is working.
"""
import asyncio
from django.http import HttpResponse
from django.utils.deprecation import MiddlewareMixin


async def get_response(request):
    return HttpResponse('test')


class TestMiddleware(MiddlewareMixin):
    pass


mw = TestMiddleware(get_response)

print(f"asyncio.iscoroutinefunction(mw): {asyncio.iscoroutinefunction(mw)}")
print(f"asyncio.iscoroutinefunction(mw.__call__): {asyncio.iscoroutinefunction(mw.__call__)}")
print(f"hasattr(mw, '_is_coroutine'): {hasattr(mw, '_is_coroutine')}")
print(f"hasattr(mw.__call__, '_is_coroutine'): {hasattr(mw.__call__, '_is_coroutine')}")

# Check if calling mw returns a coroutine
from django.http import HttpRequest
request = HttpRequest()
request.method = 'GET'
request.path = '/'

result = mw(request)
print(f"type(mw(request)): {type(result).__name__}")
print(f"asyncio.iscoroutine(result): {asyncio.iscoroutine(result)}")

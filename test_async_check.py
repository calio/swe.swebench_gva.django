"""
Test to see if _async_check detects when get_response is a regular function
that returns a coroutine.
"""
import asyncio
from django.http import HttpResponse
from django.utils.deprecation import MiddlewareMixin


# Create a regular function that returns a coroutine
def get_response_wrapper(request):
    async def inner():
        return HttpResponse('test')
    return inner()


class TestMiddleware(MiddlewareMixin):
    pass


mw = TestMiddleware(get_response_wrapper)

print(f"asyncio.iscoroutinefunction(mw.get_response): {asyncio.iscoroutinefunction(mw.get_response)}")
print(f"hasattr(mw, '_is_coroutine'): {hasattr(mw, '_is_coroutine')}")

# Now let's test with an async function
async def async_get_response(request):
    return HttpResponse('test')


mw2 = TestMiddleware(async_get_response)

print(f"asyncio.iscoroutinefunction(mw2.get_response): {asyncio.iscoroutinefunction(mw2.get_response)}")
print(f"hasattr(mw2, '_is_coroutine'): {hasattr(mw2, '_is_coroutine')}")

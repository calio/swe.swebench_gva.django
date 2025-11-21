"""
Trace the issue:

When load_middleware(is_async=True) is called:

1. handler = convert_exception_to_response(_get_response_async)
   - handler is now an async function that wraps _get_response_async

2. For each middleware (in reverse order):
   a. middleware_is_async = determine if middleware can be async
   b. handler = adapt_method_mode(middleware_is_async, handler, handler_is_async)
      - If middleware_is_async=True and handler_is_async=True, handler stays the same
      - If middleware_is_async=True and handler_is_async=False, handler is wrapped with sync_to_async
      - If middleware_is_async=False and handler_is_async=True, handler is wrapped with async_to_sync
   c. mw_instance = middleware(handler)
      - The middleware receives the (possibly adapted) handler
   d. handler = convert_exception_to_response(mw_instance)
      - The middleware instance is wrapped with exception handling
   e. handler_is_async = middleware_is_async

The issue:
- When the first middleware's __call__ is invoked (which is actually __acall__ due to MiddlewareMixin)
- It awaits self.get_response(request)
- But self.get_response is the handler from the second middleware
- If the handler is wrapped with sync_to_async, it returns a coroutine
- But the middleware's __acall__ doesn't properly handle this case

Actually, looking at MiddlewareMixin.__acall__:
```python
async def __acall__(self, request):
    response = None
    if hasattr(self, 'process_request'):
        response = await sync_to_async(self.process_request)(request)
    response = response or await self.get_response(request)  # <-- This should await properly
    if hasattr(self, 'process_response'):
        response = await sync_to_async(self.process_response)(request, response)
    return response
```

The issue is that `await self.get_response(request)` should properly await the coroutine.
But if self.get_response is a SyncToAsync instance, calling it returns a coroutine that needs to be awaited.

Wait, that's not right. SyncToAsync is callable and when called, it returns a coroutine.
So `await self.get_response(request)` should work correctly.

Let me think about this differently...

The issue might be that when the middleware's __call__ is invoked, it checks:
```python
if asyncio.iscoroutinefunction(self.get_response):
    return self.__acall__(request)
```

But __acall__ returns a coroutine, not the result of awaiting it!
So the first middleware returns a coroutine instead of the actual response.

Then when the next middleware tries to call process_response, it receives a coroutine!
"""

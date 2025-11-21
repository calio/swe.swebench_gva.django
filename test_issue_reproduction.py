"""
Reproduce the issue where the first middleware receives a coroutine
instead of an HttpResponse in ASGI mode.
"""
import asyncio
from django.http import HttpResponse
from django.test import AsyncRequestFactory, SimpleTestCase, override_settings
from django.utils.deprecation import MiddlewareMixin
from django.core.asgi import get_asgi_application
from asgiref.testing import ApplicationCommunicator


class DummyMiddleware(MiddlewareMixin):
    """Middleware that prints the types of arguments it receives."""
    
    def process_response(self, request, response):
        print(f"DummyMiddleware.process_response: request={request.__class__}, response={response.__class__}")
        if asyncio.iscoroutine(response):
            print("BUG: DummyMiddleware received a coroutine!")
            raise AssertionError("DummyMiddleware received a coroutine instead of HttpResponse!")
        return response


class TestIssueReproduction(SimpleTestCase):
    """Test to reproduce the issue."""
    
    async def test_first_middleware_receives_response_not_coroutine(self):
        """
        The first middleware should receive an HttpResponse, not a coroutine.
        """
        with override_settings(
            MIDDLEWARE=[
                'test_issue_reproduction.DummyMiddleware',
                'django.middleware.security.SecurityMiddleware',
            ],
            ROOT_URLCONF='asgi.urls',
        ):
            application = get_asgi_application()
            
            # Construct HTTP request
            factory = AsyncRequestFactory()
            scope = factory._base_scope(path='/')
            communicator = ApplicationCommunicator(application, scope)
            await communicator.send_input({'type': 'http.request'})
            
            # Read the response
            response_start = await communicator.receive_output()
            assert response_start['type'] == 'http.response.start'
            assert response_start['status'] == 200
            
            response_body = await communicator.receive_output()
            assert response_body['type'] == 'http.response.body'


if __name__ == '__main__':
    import django
    from django.conf import settings
    
    if not settings.configured:
        settings.configure(
            DEBUG=True,
            SECRET_KEY='test-secret-key',
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
            MIDDLEWARE=[
                'test_issue_reproduction.DummyMiddleware',
                'django.middleware.security.SecurityMiddleware',
            ],
            ROOT_URLCONF='asgi.urls',
        )
        django.setup()
    
    # Run the test
    test = TestIssueReproduction()
    asyncio.run(test.test_first_middleware_receives_response_not_coroutine())
    print("Test passed!")

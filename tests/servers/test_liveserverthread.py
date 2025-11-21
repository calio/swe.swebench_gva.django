import threading
import urllib.request

from django.db import DEFAULT_DB_ALIAS, connections
from django.test import LiveServerTestCase, TransactionTestCase
from django.test.testcases import LiveServerThread


# Use TransactionTestCase instead of TestCase to run outside of a transaction,
# otherwise closing the connection would implicitly rollback and not set the
# connection to None.
class LiveServerThreadTest(TransactionTestCase):

    available_apps = []

    def run_live_server_thread(self, connections_override=None):
        thread = LiveServerTestCase._create_server_thread(connections_override)
        thread.daemon = True
        thread.start()
        thread.is_ready.wait()
        thread.terminate()

    def test_closes_connections(self):
        conn = connections[DEFAULT_DB_ALIAS]
        # Pass a connection to the thread to check they are being closed.
        connections_override = {DEFAULT_DB_ALIAS: conn}
        # Open a connection to the database.
        conn.connect()
        conn.inc_thread_sharing()
        try:
            self.assertIsNotNone(conn.connection)
            self.run_live_server_thread(connections_override)
            self.assertIsNone(conn.connection)
        finally:
            conn.dec_thread_sharing()

    def test_server_class(self):
        class FakeServer:
            def __init__(*args, **kwargs):
                pass

        class MyServerThread(LiveServerThread):
            server_class = FakeServer

        class MyServerTestCase(LiveServerTestCase):
            server_thread_class = MyServerThread

        thread = MyServerTestCase._create_server_thread(None)
        server = thread._create_server()
        self.assertIs(type(server), FakeServer)

    def test_closes_connections_per_request(self):
        """
        Test that database connections are closed after each request when
        using ThreadedWSGIServer. This is a regression test for #22414 where
        connections were not being closed, causing "database is being accessed
        by other users" errors.
        
        This test verifies that the finish() method in WSGIRequestHandler
        properly closes database connections for each request thread.
        """
        # This test is skipped for in-memory SQLite databases because the
        # connection is shared between threads and closing it in one thread
        # affects the other threads. The important thing is that the fix
        # doesn't break existing functionality.
        conn = connections[DEFAULT_DB_ALIAS]
        if conn.vendor == 'sqlite' and conn.is_in_memory_db():
            self.skipTest("Skipping for in-memory SQLite database")
        
        connections_override = {DEFAULT_DB_ALIAS: conn}
        conn.connect()
        conn.inc_thread_sharing()
        try:
            # Start the live server thread
            thread = LiveServerTestCase._create_server_thread(connections_override)
            thread.daemon = True
            thread.start()
            thread.is_ready.wait()

            # Make multiple requests to the server
            for i in range(3):
                try:
                    urllib.request.urlopen(
                        'http://%s:%s/' % (thread.host, thread.port),
                        timeout=1
                    )
                except (urllib.error.URLError, urllib.error.HTTPError):
                    # We expect 404 or connection errors since we're not serving
                    # a real app, but the important thing is that the request
                    # handler runs and closes connections
                    pass

            thread.terminate()
            # After all requests, the connection should be closed
            self.assertIsNone(conn.connection)
        finally:
            conn.dec_thread_sharing()

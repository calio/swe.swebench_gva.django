from django.test import SimpleTestCase
from django.utils.safestring import mark_safe

from ..utils import setup


class EscapeseqTests(SimpleTestCase):
    @setup({"escapeseq01": '{{ a|join:", " }} -- {{ a|escapeseq|join:", " }}'})
    def test_escapeseq01(self):
        """Test that escapeseq escapes each element in a sequence."""
        output = self.engine.render_to_string("escapeseq01", {"a": ["&", "<"]})
        self.assertEqual(output, "&amp;, &lt; -- &amp;, &lt;")

    @setup(
        {
            "escapeseq02": (
                '{% autoescape off %}{{ a|join:", " }} -- {{ a|escapeseq|join:", " }}'
                "{% endautoescape %}"
            )
        }
    )
    def test_escapeseq02(self):
        """Test that escapeseq escapes elements even when autoescape is off."""
        output = self.engine.render_to_string("escapeseq02", {"a": ["&", "<"]})
        self.assertEqual(output, "&, < -- &amp;, &lt;")

    @setup({"escapeseq03": '{{ a|escapeseq|join:", " }}'})
    def test_escapeseq03(self):
        """Test that escapeseq works with HTML special characters."""
        output = self.engine.render_to_string(
            "escapeseq03", {"a": ["<script>", '"quotes"', "'apostrophes'"]}
        )
        self.assertEqual(
            output, "&lt;script&gt;, &quot;quotes&quot;, &#x27;apostrophes&#x27;"
        )

    @setup({"escapeseq04": '{{ a|escapeseq|join:", " }}'})
    def test_escapeseq04(self):
        """Test that escapeseq does not double-escape already safe strings."""
        output = self.engine.render_to_string(
            "escapeseq04", {"a": [mark_safe("&"), mark_safe("<")]}
        )
        self.assertEqual(output, "&, <")

    @setup(
        {
            "escapeseq05": (
                '{% autoescape off %}{{ a|escapeseq|join:", " }}{% endautoescape %}'
            )
        }
    )
    def test_escapeseq05(self):
        """Test that escapeseq returns escaped content even with autoescape off."""
        output = self.engine.render_to_string("escapeseq05", {"a": ["&", "<", ">"]})
        self.assertEqual(output, "&amp;, &lt;, &gt;")

    @setup({"escapeseq06": '{{ a|escapeseq|join:", " }}'})
    def test_escapeseq06(self):
        """Test that escapeseq works with mixed safe and unsafe strings."""
        output = self.engine.render_to_string(
            "escapeseq06", {"a": ["&", mark_safe("<"), ">"]}
        )
        self.assertEqual(output, "&amp;, <, &gt;")

from pathlib import Path
from unittest import mock

from django.template import autoreload
from django.test import SimpleTestCase, override_settings
from django.test.utils import require_jinja2

ROOT = Path(__file__).parent.absolute()
EXTRA_TEMPLATES_DIR = ROOT / "templates_extra"


@override_settings(
    INSTALLED_APPS=["template_tests"],
    TEMPLATES=[
        {
            "BACKEND": "django.template.backends.dummy.TemplateStrings",
            "APP_DIRS": True,
        },
        {
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "DIRS": [EXTRA_TEMPLATES_DIR],
            "OPTIONS": {
                "context_processors": [
                    "django.template.context_processors.request",
                ],
                "loaders": [
                    "django.template.loaders.filesystem.Loader",
                    "django.template.loaders.app_directories.Loader",
                ],
            },
        },
    ],
)
class TemplateReloadTests(SimpleTestCase):
    @mock.patch("django.template.autoreload.reset_loaders")
    def test_template_changed(self, mock_reset):
        template_path = Path(__file__).parent / "templates" / "index.html"
        self.assertTrue(autoreload.template_changed(None, template_path))
        mock_reset.assert_called_once()

    @mock.patch("django.template.autoreload.reset_loaders")
    def test_non_template_changed(self, mock_reset):
        self.assertIsNone(autoreload.template_changed(None, Path(__file__)))
        mock_reset.assert_not_called()

    @override_settings(
        TEMPLATES=[
            {
                "DIRS": [ROOT],
                "BACKEND": "django.template.backends.django.DjangoTemplates",
            }
        ]
    )
    @mock.patch("django.template.autoreload.reset_loaders")
    def test_non_template_changed_in_template_directory(self, mock_reset):
        self.assertIsNone(autoreload.template_changed(None, Path(__file__)))
        mock_reset.assert_not_called()

    def test_watch_for_template_changes(self):
        mock_reloader = mock.MagicMock()
        autoreload.watch_for_template_changes(mock_reloader)
        self.assertSequenceEqual(
            sorted(mock_reloader.watch_dir.call_args_list),
            [
                mock.call(ROOT / "templates", "**/*"),
                mock.call(ROOT / "templates_extra", "**/*"),
            ],
        )

    def test_get_template_directories(self):
        self.assertSetEqual(
            autoreload.get_template_directories(),
            {
                ROOT / "templates_extra",
                ROOT / "templates",
            },
        )

    @mock.patch("django.template.loaders.base.Loader.reset")
    def test_reset_all_loaders(self, mock_reset):
        autoreload.reset_loaders()
        self.assertEqual(mock_reset.call_count, 2)

    @override_settings(
        TEMPLATES=[
            {
                "DIRS": [
                    str(ROOT) + "/absolute_str",
                    "template_tests/relative_str",
                    Path("template_tests/relative_path"),
                ],
                "BACKEND": "django.template.backends.django.DjangoTemplates",
            }
        ]
    )
    def test_template_dirs_normalized_to_paths(self):
        self.assertSetEqual(
            autoreload.get_template_directories(),
            {
                ROOT / "absolute_str",
                Path.cwd() / "template_tests/relative_str",
                Path.cwd() / "template_tests/relative_path",
            },
        )


@require_jinja2
@override_settings(INSTALLED_APPS=["template_tests"])
class Jinja2TemplateReloadTests(SimpleTestCase):
    def test_watch_for_template_changes(self):
        mock_reloader = mock.MagicMock()
        autoreload.watch_for_template_changes(mock_reloader)
        self.assertSequenceEqual(
            sorted(mock_reloader.watch_dir.call_args_list),
            [
                mock.call(ROOT / "templates", "**/*"),
            ],
        )

    def test_get_template_directories(self):
        self.assertSetEqual(
            autoreload.get_template_directories(),
            {
                ROOT / "templates",
            },
        )

    @mock.patch("django.template.loaders.base.Loader.reset")
    def test_reset_all_loaders(self, mock_reset):
        autoreload.reset_loaders()
        self.assertEqual(mock_reset.call_count, 0)


@override_settings(
    TEMPLATES=[
        {
            "DIRS": [""],  # Empty string in DIRS
            "BACKEND": "django.template.backends.django.DjangoTemplates",
        }
    ]
)
class TemplateReloadEmptyDirsTests(SimpleTestCase):
    """Test that empty strings in TEMPLATES DIRS don't break autoreload."""

    def test_empty_string_in_dirs(self):
        """Empty strings should be filtered out from template directories."""
        dirs = autoreload.get_template_directories()
        # Should not include the project root
        self.assertNotIn(Path.cwd(), dirs)
        # Should be empty since we only have an empty string
        self.assertEqual(dirs, set())

    @mock.patch("django.template.autoreload.reset_loaders")
    def test_template_changed_with_empty_dirs(self, mock_reset):
        """template_changed should not always return True with empty dirs."""
        # Create a test file path that's not in any template directory
        test_file = Path(__file__).parent / "test_file.py"
        result = autoreload.template_changed(None, test_file)
        # Should return None (not True) since the file is not in a template directory
        self.assertIsNone(result)
        mock_reset.assert_not_called()

    @override_settings(
        TEMPLATES=[
            {
                "DIRS": ["", EXTRA_TEMPLATES_DIR, ""],  # Mix of empty and valid dirs
                "BACKEND": "django.template.backends.django.DjangoTemplates",
            }
        ]
    )
    def test_mixed_empty_and_valid_dirs(self):
        """Empty strings mixed with valid dirs should be filtered correctly."""
        dirs = autoreload.get_template_directories()
        # Should only include the valid directory
        self.assertEqual(dirs, {EXTRA_TEMPLATES_DIR})
        # Should not include the project root
        self.assertNotIn(Path.cwd(), dirs)

    @override_settings(
        TEMPLATES=[
            {
                "DIRS": [""],  # Empty string from split(",") on empty env var
                "BACKEND": "django.template.backends.django.DjangoTemplates",
            }
        ]
    )
    @mock.patch("django.template.autoreload.reset_loaders")
    def test_autoreload_with_empty_dirs_from_env(self, mock_reset):
        """
        Test the scenario from the issue: TEMPLATES_DIRS from environment variable.
        When TEMPLATES_DIRS env var is empty, split(",") produces [""].
        This should not break autoreload.
        """
        # Simulate a file change in the app code (not in a template directory)
        app_file = Path(__file__).parent / "app_code.py"
        result = autoreload.template_changed(None, app_file)
        # Should return None since the file is not in a template directory
        self.assertIsNone(result)
        mock_reset.assert_not_called()

        # Simulate a template file change (should still work if we had valid dirs)
        template_file = Path(__file__).parent / "templates" / "test.html"
        # With only empty string in DIRS, no template directories are watched
        result = autoreload.template_changed(None, template_file)
        self.assertIsNone(result)
        mock_reset.assert_not_called()

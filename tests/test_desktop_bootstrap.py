"""Unit tests for desktop-only argument and path helpers."""
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from desktop import launcher
from desktop.main import _worker_args_from_process_argv


class DesktopBootstrapTests(unittest.TestCase):
    def test_legacy_frozen_worker_arguments(self):
        self.assertEqual(
            _worker_args_from_process_argv(["-u", "extract.py", "--incremental"]),
            ["extract", "--incremental"],
        )

    def test_explicit_worker_arguments(self):
        self.assertEqual(
            _worker_args_from_process_argv(["--worker", "extract", "--list-conversations"]),
            ["extract", "--list-conversations"],
        )

    def test_normal_gui_arguments_are_not_workers(self):
        self.assertIsNone(_worker_args_from_process_argv([]))
        self.assertIsNone(_worker_args_from_process_argv(["--unknown"]))

    def test_application_dir_uses_local_app_data(self):
        with tempfile.TemporaryDirectory() as tmp, patch.dict(
            os.environ, {"LOCALAPPDATA": tmp}, clear=False
        ):
            self.assertEqual(
                launcher.application_dir(),
                (Path(tmp) / launcher.APP_NAME).resolve(),
            )


if __name__ == "__main__":
    unittest.main()

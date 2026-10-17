import contextlib
import io
from pathlib import Path
import tempfile
import unittest

from build_system import ForgeBuilder
from kimi_forge_unified import ForgeToolCall, ForgeToolRegistry, KimiForgeUnified, KimiK2Model


class DemonstrationIntegrityTests(unittest.TestCase):
    def test_generation_explicitly_has_no_model_or_confidence(self):
        response = KimiK2Model().generate("edit this video")
        self.assertIn("DEMO", response.text)
        self.assertIn("no model loaded", response.text)
        self.assertIsNone(response.confidence)

    def test_every_defined_tool_reports_nonexecution(self):
        registry = ForgeToolRegistry()
        for name in registry.tools:
            with self.subTest(tool=name):
                call = ForgeToolCall(name, {"task": "example"})
                result = registry.execute_tool(call)
                self.assertEqual(result["status"], "not_implemented")
                self.assertIs(result["executed"], False)
                self.assertIs(result["demo"], True)

    def test_stats_distinguish_definitions_from_executable_tools(self):
        stats = KimiForgeUnified().get_stats()
        self.assertEqual(stats["status"], "demonstration")
        self.assertFalse(stats["model_loaded"])
        self.assertEqual(stats["forge_tools_available"], 0)
        self.assertEqual(stats["total_capabilities"], 0)
        self.assertGreater(stats["tool_definitions"], 0)

    def test_user_response_does_not_report_simulated_tool_success(self):
        output = KimiForgeUnified().process("edit this video")
        self.assertIn("DEMO", output)
        self.assertIn("Status: not_implemented", output)
        self.assertNotIn("Status: success", output)

    def test_unimplemented_linux_and_video_builds_fail_explicitly(self):
        builder = ForgeBuilder()
        for method in (builder.build_linux_os, builder.build_video_editor):
            with self.subTest(method=method.__name__):
                with self.assertRaises(NotImplementedError):
                    method()

    def test_full_build_does_not_publish_a_fake_distribution(self):
        with tempfile.TemporaryDirectory() as directory:
            builder = ForgeBuilder()
            builder.project_root = Path(directory)
            builder.build_dir = Path(directory) / "build"
            builder.dist_dir = Path(directory) / "dist"
            for name in ("forge_implementation.py", "forge_server.py", "forge_cli.py", "forge_gui.py"):
                (Path(directory) / name).touch()
            with contextlib.redirect_stdout(io.StringIO()) as output:
                self.assertFalse(builder.build_all())
            self.assertNotIn("BUILD COMPLETE!", output.getvalue())
            self.assertEqual(list(builder.dist_dir.glob("*.zip")), [])


if __name__ == "__main__":
    unittest.main()

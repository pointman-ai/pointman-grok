"""Offline contract checks. These never execute Grok or authenticate."""
import json
from pathlib import Path
import tomllib
import unittest

ROOT = Path(__file__).resolve().parents[1]


class ManifestContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = tomllib.loads((ROOT / "extension.toml").read_text())
        cls.client = cls.manifest["client"]

    def test_install_and_protocol(self):
        self.assertEqual(self.manifest["extension"]["id"], "grok")
        self.assertEqual(self.manifest["extension"]["node"], ">=0.4.2")
        self.assertEqual(self.client["protocol"], "grok-stream")
        self.assertEqual(self.client["install"], {"from": "npm", "package": "@xai-official/grok"})
        self.assertEqual(self.client["binaries"], ["grok"])

    def test_new_and_resume_are_explicit_and_distinct(self):
        run = self.client["run"]
        self.assertEqual(run["new_session"], ["--session-id", "{value}"])
        self.assertEqual(run["resume"], ["--resume", "{value}"])
        self.assertIn("{session}", run["args"])
        self.assertNotIn("--continue", run["args"])
        self.assertEqual(run["prompt"], "arg")
        self.assertEqual(run["args"][:5], ["--no-auto-update", "-p", "{prompt}", "--output-format", "streaming-json"])

    def test_home_and_compatibility_isolation(self):
        self.assertEqual(self.client["home_env"], "HOME")
        self.assertEqual(self.client["run"]["env"], {"GROK_HOME": "{home}/.grok"})
        self.assertEqual(self.client["api_keys"], ["XAI_API_KEY"])
        mcp = self.client["mcp"]
        self.assertEqual((mcp["via"], mcp["file"], mcp["key"]), ("config-file", ".grok/config.toml", "mcp_servers"))
        for vendor in ("claude", "cursor"):
            self.assertEqual(mcp["settings"]["compat"][vendor], dict.fromkeys(("mcps", "hooks", "skills", "rules", "agents"), False))
        self.assertEqual(mcp["drop"], ["type"])
        self.assertFalse(mcp["settings"]["cli"]["auto_update"])

    def test_behaviours_and_permissions(self):
        self.assertEqual(self.client["instructions"], {"via": "flag", "args": ["--rules", "{value}"]})
        self.assertEqual(set(self.client["run"]["permissions"]), {"default", "auto", "acceptEdits", "plan"})
        self.assertEqual(self.client["run"]["permissions"]["default"], ["--permission-mode", "dontAsk", "--allow", "MCPTool"])
        self.assertNotIn("check", self.client["sign_in"])

    def test_native_fixture_is_chunked_and_not_messages_format(self):
        stream = [json.loads(line) for line in (ROOT / "tests/fixtures/native.jsonl").read_text().splitlines()]
        self.assertEqual("".join(e["data"] for e in stream if e["type"] == "text"), "Hello world.\n")
        self.assertEqual(stream[-1]["type"], "end")
        self.assertEqual(stream[-1]["stopReason"], "end_turn")
        self.assertEqual(stream[-1]["sessionId"], "11111111-2222-4333-8444-555555555555")
        self.assertEqual([e["toolCallId"] for e in stream if e["type"].startswith("tool_call")], ["call_1", "call_1"])
        self.assertFalse(any(e["type"] in ("assistant", "result", "system") for e in stream))


if __name__ == "__main__":
    unittest.main()

# Pointman Grok client

A client extension for xAI Grok Build. Intended repository: `pointman-ai/pointman-grok`.
Requires a Pointman node with the `grok-stream` decoder and MCP `settings` merging.
This local repository has not been published or released.

## Installation and sign-in

Pointman installs `@xai-official/grok` through its npm installer when needed.
The [official npm wrapper](https://github.com/xai-org/grok-build/blob/main/crates/codegen/xai-grok-pager/npm/grok/README.md)
lists macOS arm64 and Linux arm64/x64. npm/Node and native binary bootstrap must
work on the machine; installation on NixOS has not been verified here.

Each agent gets its own `HOME`, at `<node-state>/homes/grok/<handle>`.
Sign in manually using that exact absolute HOME and the installed executable:

```sh
HOME=/absolute/node-state/homes/grok/my-agent /absolute/path/to/grok login
# For a machine without a browser:
HOME=/absolute/node-state/homes/grok/my-agent /absolute/path/to/grok login --device-auth
```

Do not run these during automated checks. No existing login or another client's
credentials are copied. Ordinary `grok login` with your usual HOME does not sign
this isolated agent in. The node strips `XAI_API_KEY`; this extension uses login.
There is no documented offline sign-in status check, so the manifest supplies none.
Grok's wrapper may bootstrap a binary under the isolated home on first use.

## Runs and config

A wake uses `--no-auto-update -p <prompt> --output-format streaming-json`.
New sessions use an explicit UUID with `--session-id`; later wakes use that UUID
with `--resume`. Behaviours go through `--rules`; stdin is closed by the keeper.
The default mode uses `dontAsk` with MCP tools allowed; additional tools need an
explicit permission mode. Other modes can deny or prompt; stdin cannot answer.

The node merges servers into `$HOME/.grok/config.toml` under `mcp_servers`, keeps
HTTP `headers`, and drops `type`. Settings disable Claude/Cursor compatibility
scanners and automatic updates. HOME also isolates their usual user config paths.
The child environment must not inherit a pre-existing `GROK_HOME` override.
Project `.grok/config.toml` can still contribute servers and override a user server;
this is not a guarantee that only Pointman's MCP servers exist in a project.
See [MCP configuration](https://docs.x.ai/build/features/mcp-servers) and
[settings](https://docs.x.ai/build/settings/reference).

## Stream contract and checks

`tests/fixtures/native.jsonl` is synthetic schema-derived data, not a captured
account run. It follows xAI's [native reducer source](https://github.com/xai-org/grok-build/blob/main/crates/codegen/xai-grok-pager/src/headless/reducer/acp.rs),
read 2026-10-29 on `main`; no installed binary version was verified.
Text is incremental `text.data`; tool updates have ACP camelCase fields.
The terminal `end` carries `sessionId` and `stopReason`, without final response
text. The decoder returns chunks; the keeper must concatenate them verbatim.
Reasoning is ignored. Only `end_turn` is successful; truncation and cancellation
are failures. Native `error.message` becomes a failed result. Limit detection is
an error-text heuristic, without invented quota windows. Unknown/malformed lines
remain in the raw log; a missing terminal result fails the run.

The decoder lives in the Pointman node at `node/src/clientstream/grok.rs`.
Its tests cover native chunks, tools, session metadata, errors, partial cost,
unknown shapes, cancellation and structured output failure. CI here checks only
the manifest contract and fixture consistency:

```sh
python3 -m unittest discover -s tests -v
```

No real model call, sign-in, account change, npm installation, NixOS runtime,
full-node integration or hosted CI run was performed for this extension.

# CLAUDE.md

Guidance for Claude Code when working in this repository.

## Commands

```bash
uv sync                              # install dependencies
uv run python main.py console        # local-mic dev (no LiveKit server needed)
uv run python main.py dev            # connect to LiveKit (dev)
uv run python main.py start          # production worker
uv run ruff check src/               # lint
uv run mypy src/                     # type check
uv run python -m pytest -q           # tests
```

## Architecture

A minimal LiveKit voice agent (`livekit-agents==1.5.6`). Entry point:
`main.py` -> `src/agent.py`.

- `src/agent.py`: `AgentServer`, prewarm (Silero VAD), and the `@server.rtc_session`
  entrypoint. Explicit dispatch via `agent_name` (`config.AGENT_NAME`).
- `src/agents/assistant.py`: `Assistant(Agent)`, the conversational agent. Extend
  with `@function_tool` methods or `AgentTask` handoffs.
- `src/prompts/instructions.py`: the system prompt.
- `src/core/config.py`: `pydantic-settings` config (`AGENT_NAME`, `ENV`, `SENTRY_DSN`).
- `src/core/events.py`: generic session event handlers plus a usage summary.
- `src/utils/room.py`: `parse_room_metadata`, `identify()` (web vs SIP).

Pipeline: Deepgram `nova-3` STT, OpenAI `gpt-4.1-mini` LLM, Cartesia TTS, with
Silero VAD and the LiveKit multilingual turn detector.

## Conventions

- No em dashes in prompts, code, or docs.
- `uv` over pip, `ruff` over black plus flake8.
- The agent makes no backend HTTP calls. Tokens are minted by the backend.

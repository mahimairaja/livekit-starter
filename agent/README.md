# Voice agent (LiveKit)

A minimal LiveKit voice agent: it joins a room (web or SIP), greets the
participant, and holds a natural conversation. Built on `livekit-agents`, with a
Deepgram, OpenAI, Cartesia pipeline. Pairs with the backend `/token` endpoint and
a LiveKit-based frontend.

## Stack

| Layer | Provider |
| ----- | -------- |
| STT | Deepgram (`nova-3`) |
| LLM | OpenAI (`gpt-4.1-mini`) |
| TTS | Cartesia |
| VAD | Silero (prewarmed) |
| Turn detection | LiveKit multilingual model |

## Quickstart

```bash
cp .env.example .env     # fill in LIVEKIT_*, OPENAI, DEEPGRAM, CARTESIA
uv sync
uv run python main.py download-files   # pre-fetch VAD and turn-detector models

uv run python main.py console          # talk to the agent with your local mic
uv run python main.py dev              # connect to your LiveKit server (dev)
uv run python main.py start            # production worker
```

## Dispatch

The worker registers with `agent_name` equal to `AGENT_NAME` (default `assistant`)
and uses explicit dispatch:

- Web: the frontend requests a token whose `room_config` names this agent. The
  backend `/token` endpoint passes `room_config` through.
- SIP: configure a LiveKit dispatch rule that routes inbound calls to `assistant`.

The agent and the backend must share the same `LIVEKIT_API_KEY` and
`LIVEKIT_API_SECRET`.

## Extending

- Add tools: give `Assistant` (`src/agents/assistant.py`) `@function_tool` methods.
- Add structured flows: hand off to an `AgentTask`.
- Web mic cleanup: `uv add livekit-plugins-noise-cancellation`, then pass
  `room_input_options=RoomInputOptions(noise_cancellation=BVC())` to
  `session.start` in `src/agent.py`.

## Dev commands

```bash
uv run ruff check src/
uv run mypy src/
uv run python -m pytest -q
```

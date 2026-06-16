# Frontend (React + Vite)

A browser voice UI built with React, Vite, Tailwind, and LiveKit's Agents UI
components: audio visualizer, live transcript, and text chat. Fetches a token
from the backend and dispatches the `assistant` agent.

## Quickstart

```bash
cp .env.example .env     # VITE_TOKEN_ENDPOINT, VITE_AGENT_NAME
pnpm install
pnpm dev                 # http://localhost:5173
```

Needs the backend and agent running, all three sharing the same LiveKit project
credentials. `VITE_AGENT_NAME` must match the agent's `AGENT_NAME`.

## Layout

```
src/
  App.tsx                 session + AgentSessionProvider + welcome/session switch
  lib/token-source.ts     TokenSource.endpoint(...) + agent name
  components/app/          welcome screen, session view
  components/agents-ui/    LiveKit Agents UI (shadcn registry, vendored)
```

## Components

Installed from the `@agents-ui` shadcn registry into `src/components/agents-ui/`
as editable source. Swap the visualizer by importing a different
`AgentAudioVisualizer*` (they share the same props).

## Commands

```bash
pnpm dev          # dev server
pnpm build        # production build -> dist/
pnpm run lint     # eslint
pnpm test         # vitest
```

## Deploy

Static build (`dist/`) → Cloudflare Pages. Set `VITE_TOKEN_ENDPOINT` to the prod
backend and the backend `CORS_ORIGINS_STR` to this app's origin.

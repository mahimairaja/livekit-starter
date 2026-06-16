# Voice frontend (React + Vite)

A browser voice agent UI built with React, Vite, and LiveKit Agents UI components.
It requests a token from the backend `/token` endpoint, dispatches the `assistant`
agent, and supports voice, a live transcript, and text chat.

## Quickstart

```bash
cp .env.example .env     # point VITE_TOKEN_ENDPOINT at your backend
pnpm install
pnpm dev                 # http://localhost:5173
```

Requires the backend (token endpoint) and the agent worker running, all three
sharing the same LiveKit project credentials. `VITE_AGENT_NAME` must match the
agent worker's `AGENT_NAME`.

## How it works

- `src/lib/token-source.ts` builds a `TokenSource.endpoint(...)` pointed at the
  backend, plus the agent name.
- `src/App.tsx` creates the session with `useSession(tokenSource, { agentName })`,
  wraps the UI in `AgentSessionProvider`, and switches between the welcome screen
  and the live session view based on `useAgent()` state getters.
- `src/components/app/session-view.tsx` composes the Agents UI components: an
  audio visualizer, the chat transcript, and the control bar (mic, expandable
  text chat, and leave).

## Components

LiveKit Agents UI (Shadcn registry `@agents-ui`) live under
`src/components/agents-ui/` with full source you can edit. Swap the visualizer by
importing a different `AgentAudioVisualizer*` (they share the same props).

## Scripts

```bash
pnpm dev       # dev server
pnpm build     # production build -> dist/
pnpm test      # vitest
```

## Deploy

The static build (`dist/`) deploys to Cloudflare Pages. Set `VITE_TOKEN_ENDPOINT`
to the production backend, and set the backend `CORS_ORIGINS_STR` to this app's
origin.

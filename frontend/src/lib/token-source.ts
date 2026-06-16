import { TokenSource } from "livekit-client";

// Points at the backend's standard LiveKit token endpoint. The backend passes
// room_config through, so naming the agent (below) dispatches it into the room.
export const tokenSource = TokenSource.endpoint(
  import.meta.env.VITE_TOKEN_ENDPOINT ?? "http://localhost:8000/api/v1/token",
);

// Must match the agent worker's agent_name (AGENT_NAME in the agent package).
export const AGENT_NAME = import.meta.env.VITE_AGENT_NAME ?? "assistant";

from pydantic import BaseModel

# Request/response follow the LiveKit standardized token-endpoint schema so any
# LiveKit client SDK (e.g. `TokenSource.endpoint(...)`) works without glue.
# https://docs.livekit.io/frontends/build/authentication/endpoint/


class RoomTokenRequest(BaseModel):
    # All optional: the server fills sensible defaults for room/identity.
    room_name: str | None = None
    participant_identity: str | None = None
    participant_name: str | None = None
    participant_metadata: str | None = None
    participant_attributes: dict[str, str] | None = None
    # Agent dispatch and other room-level config. The client SDKs package agent
    # info (agent_name, agent_metadata) into room_config; we pass it through.
    room_config: dict | None = None


class RoomTokenResponse(BaseModel):
    server_url: str
    participant_token: str

import pytest
from fastapi import HTTPException
from livekit.api import TokenVerifier

from src.core.config import Config
from src.schemas.token_schemas import RoomTokenRequest
from src.services.token_service import TokenService

KEY = "devkey"
SECRET = "devsecret-devsecret-devsecret-1234"
URL = "wss://example.livekit.cloud"


def _service() -> TokenService:
    cfg = Config(
        ENV="dev",
        _env_file=None,
        LIVEKIT_URL=URL,
        LIVEKIT_API_KEY=KEY,
        LIVEKIT_API_SECRET=SECRET,
    )
    return TokenService(cfg)


def _claims(token: str):
    return TokenVerifier(KEY, SECRET).verify(token)


def test_mints_token_with_requested_room_and_identity():
    resp = _service().create_room_token(
        RoomTokenRequest(
            room_name="r1", participant_identity="alice", participant_name="Alice"
        )
    )
    assert resp.server_url == URL
    claims = _claims(resp.participant_token)
    assert claims.identity == "alice"
    assert claims.name == "Alice"
    assert claims.video.room == "r1"
    assert claims.video.room_join is True
    assert claims.video.can_publish is True
    assert claims.video.can_subscribe is True


def test_generates_defaults_when_fields_missing():
    claims = _claims(_service().create_room_token(RoomTokenRequest()).participant_token)
    assert claims.identity.startswith("user-")
    assert claims.video.room.startswith("room-")


def test_metadata_and_attributes_are_encoded():
    resp = _service().create_room_token(
        RoomTokenRequest(
            participant_metadata="hello", participant_attributes={"tier": "pro"}
        )
    )
    claims = _claims(resp.participant_token)
    assert claims.metadata == "hello"
    assert claims.attributes["tier"] == "pro"


def test_room_config_enables_agent_dispatch():
    resp = _service().create_room_token(
        RoomTokenRequest(
            room_name="r", room_config={"agents": [{"agentName": "assistant"}]}
        )
    )
    claims = _claims(resp.participant_token)
    assert claims.room_config is not None
    assert claims.room_config.agents[0].agent_name == "assistant"


def test_unconfigured_livekit_raises_503():
    cfg = Config(
        ENV="dev",
        _env_file=None,
        LIVEKIT_URL=None,
        LIVEKIT_API_KEY=None,
        LIVEKIT_API_SECRET=None,
    )
    with pytest.raises(HTTPException) as exc:
        TokenService(cfg).create_room_token(RoomTokenRequest())
    assert exc.value.status_code == 503

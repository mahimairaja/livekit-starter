"""Tests for room utilities."""

from types import SimpleNamespace

from livekit import rtc

from src.utils.room import Caller, identify, parse_room_metadata


def _participant(
    identity="u1",
    kind=rtc.ParticipantKind.PARTICIPANT_KIND_STANDARD,
    attributes=None,
):
    return SimpleNamespace(identity=identity, kind=kind, attributes=attributes or {})


def test_parse_valid_json():
    assert parse_room_metadata('{"source": "sandbox"}') == {"source": "sandbox"}


def test_parse_empty():
    assert parse_room_metadata(None) == {}
    assert parse_room_metadata("") == {}


def test_parse_invalid_json():
    assert parse_room_metadata("not json") == {}


def test_parse_non_dict_json():
    assert parse_room_metadata("[1,2,3]") == {}


def test_identify_web_participant():
    caller = identify(_participant(identity="web-user"))
    assert caller == Caller(kind="web", identity="web-user", phone=None)


def test_identify_sip_by_attribute():
    caller = identify(_participant(attributes={"sip.phoneNumber": "+14165550000"}))
    assert caller.kind == "sip"
    assert caller.phone == "+14165550000"


def test_identify_sip_by_kind():
    caller = identify(_participant(kind=rtc.ParticipantKind.PARTICIPANT_KIND_SIP))
    assert caller.kind == "sip"

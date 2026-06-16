import json
import logging
from dataclasses import dataclass

from livekit import rtc

logger = logging.getLogger(__name__)


@dataclass
class Caller:
    """A connected participant, classified by transport."""

    kind: str  # "web" or "sip"
    identity: str
    phone: str | None = None


def parse_room_metadata(raw: str | None) -> dict:
    """Safely parse room metadata as JSON; return {} on any failure."""
    if not raw:
        return {}
    try:
        data = json.loads(raw)
        return data if isinstance(data, dict) else {}
    except json.JSONDecodeError:
        logger.warning("Room metadata is not valid JSON: %r", raw)
        return {}


def identify(participant: rtc.Participant) -> Caller:
    """Classify a participant as a web or SIP caller.

    SIP participants report a SIP participant kind and carry the originating
    number in the ``sip.phoneNumber`` attribute.
    """
    attrs = participant.attributes or {}
    phone = attrs.get("sip.phoneNumber") or None
    is_sip = participant.kind == rtc.ParticipantKind.PARTICIPANT_KIND_SIP or bool(phone)
    return Caller(
        kind="sip" if is_sip else "web",
        identity=participant.identity,
        phone=phone if is_sip else None,
    )

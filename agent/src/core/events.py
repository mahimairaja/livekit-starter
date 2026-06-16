import logging

from livekit.agents import AgentSession, metrics
from livekit.agents.llm import ChatMessage

logger = logging.getLogger("agent")


def register_event_handlers(
    session: AgentSession, usage: metrics.UsageCollector
) -> None:
    """Attach generic logging + usage-collection handlers to a session."""

    @session.on("user_state_changed")
    def _on_user_state_changed(ev) -> None:
        logger.info("user_state: %s -> %s", getattr(ev, "old_state", "?"), ev.new_state)

    @session.on("agent_state_changed")
    def _on_agent_state_changed(ev) -> None:
        logger.info(
            "agent_state: %s -> %s", getattr(ev, "old_state", "?"), ev.new_state
        )

    @session.on("conversation_item_added")
    def _on_item_added(ev) -> None:
        item = ev.item
        if isinstance(item, ChatMessage) and item.text_content:
            logger.info("%s: %s", item.role, item.text_content)

    @session.on("metrics_collected")
    def _on_metrics_collected(ev) -> None:
        metrics.log_metrics(ev.metrics)
        usage.collect(ev.metrics)


def log_usage_summary(usage: metrics.UsageCollector) -> None:
    """Log the aggregated usage (tokens, audio duration) for the session."""
    try:
        logger.info("usage summary: %s", usage.get_summary())
    except Exception:
        logger.exception("failed to build usage summary")

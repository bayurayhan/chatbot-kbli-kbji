import logging
from fastapi_events.handlers.local import local_handler
from fastapi_events.typing import Event

logger = logging.getLogger("app")

@local_handler.register(event_name="queryHandled/success")
def handle_query_handled_successfully(event: Event):
    event_name, payload = event

    logger.info(f"{payload['id']} finished successfully!")

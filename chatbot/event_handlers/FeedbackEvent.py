import logging
from fastapi_events.handlers.local import local_handler
from fastapi_events.typing import Event
from ..FeedbackSystem import FeedbackSystem


@local_handler.register(event_name="queryHandled/success")
def handle_query_handled_successfully(event: Event):
    event_name, payload = event

    logging.getLogger("app").info(f"{payload['id']} finished successfully!")

    logging.getLogger("app").debug(event_name + " -> " + str(payload))

    chat_id, message_id = payload.get("id").split("__")

    feedback = FeedbackSystem.get_instance()

    poll_message = feedback.send_feedback_poll(chat_id, message_id)
    poll_message = poll_message.get("result")

    feedback.add_feedback(
        id=payload.get("id"),
        poll_id=poll_message.get("poll_id"),
        response=payload.get("response"),
        user_prompt=payload.get("user_prompt"),
        response_time=None,
        is_relevant=None,
        is_error=False,
    )


@local_handler.register(event_name="feedback/success")
def handle_feedback_successfully(event: Event):
    event_name, payload = event

    logging.getLogger("app").debug(event_name + " -> " + str(payload))

    feedback = FeedbackSystem.get_instance()
    feedback.edit_feedback(poll_id=payload.get("poll_id"), column="is_relevant", new_data=payload.get("is_relevant"))

    logging.getLogger("app").info("Feedback saved successfully!")
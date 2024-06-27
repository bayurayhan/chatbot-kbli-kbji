import logging
import time
from fastapi_events.handlers.local import local_handler
from fastapi_events.typing import Event
from ..FeedbackSystem import FeedbackSystem


@local_handler.register(event_name="queryHandled/success")
def handle_query_handled_successfully(event: Event):
    # end_time = time.time()
    # event_name, payload = event

    # start_time = payload.get("start_time")

    # # Calculate response time
    # response_time = end_time - start_time

    # logging.getLogger("app").debug(f"Handled {payload['id']} with response time: {response_time}")

    # chat_id, message_id = payload.get("id").split("__")

    # feedback = FeedbackSystem.get_instance()

    # if not feedback.config["active"]:
    #     return

    # poll_message = feedback.send_feedback_poll(chat_id, message_id)
    # poll_message = poll_message.get("result")
    # logging.getLogger("app").debug(poll_message)

    # feedback.add_feedback(
    #     id=payload.get("id"),
    #     poll_id=poll_message.get("message_id"),
    #     response=payload.get("response"),
    #     user_prompt=payload.get("user_prompt"),
    #     response_time=response_time,
    #     is_relevant=None,
    #     is_error=False,
    # )
    pass


@local_handler.register(event_name="feedback/success")
def handle_feedback_successfully(event: Event):
    # event_name, payload = event

    # logging.getLogger("app").debug(event_name + " -> " + str(payload))

    # feedback = FeedbackSystem.get_instance()
    # feedback.edit_feedback(poll_id=payload.get("poll_id"), column="is_relevant", new_data=payload.get("is_relevant"))

    # logging.getLogger("app").info("Feedback saved successfully!")
    pass
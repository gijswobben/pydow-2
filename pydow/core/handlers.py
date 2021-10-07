import uuid

from flask import session
from flask_socketio import emit

from blinker import signal
from pydow.signals import signal_navigation_event
from pydow.signals import signal_state_update
from pydow.signals import signal_default_event
from pydow.signals import signal_clear_input_field_event


def handle_connect() -> None:
    """ Generate and store a session ID for every connect.
    """

    session["session_id"] = str(uuid.uuid4())


def handle_requestSession(event):
    emit("STORE_SESSION", {"session_id": session["session_id"]})


def handle_restoreSession(event):
    if "session_id" in event:
        session["session_id"] = event.get("session_id")


def handle_all_json(json):
    json["session_id"] = session["session_id"]
    print(json)
    signal_default_event.send(json)


def handle_dom_event(json: dict) -> None:

    if "DOMEventCategory" in json:

        if json.get("DOMEventCategory", None) == "MouseEvent click":

            target_identifier = json.get("target", "")
            if target_identifier is not "":
                signal(f"ON_CLICK_{target_identifier}").send({"session_id": session["session_id"]})

        elif (
            json.get("DOMEventCategory", None) == "Event input"
            or json.get("DOMEventCategory", None) == "Event change"
        ):
            target_identifier = json.get("target", "")
            if target_identifier is not "":
                signal(f"ON_CHANGE_{target_identifier}").send({"value": json.get("value", ""), "session_id": session["session_id"]})

        elif json.get("DOMEventCategory", None) == "Event submit":
            target_identifier = json.get("target", "")
            if target_identifier is not "":
                signal(f"ON_FORM_SUBMIT_{target_identifier}").send({"session_id": session["session_id"]})

        elif json.get("DOMEventCategory", None) == "UIEvent load":
            signal_navigation_event.send(
                {
                    "link_target": json.get("link_target", "/"),
                    "link_search": json.get("link_search", None),
                    "link_anchor": json.get("link_anchor", None),
                    "session_id": session["session_id"],
                }
            )

        else:
            print(f"Recieved an unhandled event: {json}")
    else:
        print(f"Recieved an unhandled event: {json}")

    # Update the DOM after the event has been handled
    # TODO: Reduce the number of refresh (only when the vdom actually changed)
    signal_state_update.send({"session_id": session["session_id"]})

import os
import sys
import uuid
import configparser

from flask import Flask
from flask import session
from flask import render_template
from flask import send_from_directory

from flask_socketio import emit
from flask_socketio import SocketIO

from typing import Generic
from typing import TypeVar


# Define parameter types (for typing in Python)
VirtualDOM_type = TypeVar("VirtualDOM")


class App(object):
    """ Construct the full app.
    """

    def __init__(
        self: object,
        vdom: Generic[VirtualDOM_type],
        title: str = "",
        extend_head: str = "",
        custom_javascript: str = "",
        public_folder: str = "./public",
        plugin_folder: str = "./plugins",
        template_folder: str = "../public",
        configuration_file: str = "./server.conf",
        *args: list,
        **kwargs: dict,
    ) -> None:
        """ Initialization of the app.
        """

        # Get the configuration
        self.configuration_file = configuration_file
        self.config = configparser.ConfigParser()
        self.config.read(os.path.abspath(self.configuration_file))

        # Store the input parameters
        self.vdom = vdom
        self.title = title
        self.extend_head = extend_head
        self.public_folder = public_folder
        self.plugin_folder = plugin_folder
        self.custom_javascript = custom_javascript
        self.template_folder = os.path.abspath(
            os.path.join(os.path.dirname(__file__), template_folder)
        )

        # Register any plugins in the plugin folder
        self.registerPlugins()

        # Create the app from the provided VDOM object
        self.socketio, self.app = self.createApp()

    def run(self: object, *args: list, **kwargs: dict) -> None:
        """ Wrapper that passes all arguments into the socketio run method.
        """
        self.socketio.run(self.app, *args, **kwargs)

    def registerPlugins(self: object) -> None:
        """ Method that registers plugins from the plugin folder. All plugins
            are automatically initialized.
        """

        # Add the plugin folder to the search path (this is relative to the users app)
        sys.path.insert(0, self.plugin_folder)

        # Start with an empty plugins dict
        plugins = {}

        # Detect plugin files
        plugin_files = [
            f
            for f in os.listdir(self.plugin_folder)
            if os.path.isfile(os.path.join(self.plugin_folder, f))
        ]

        # Loop the plugin files
        for plugin_file in plugin_files:

            # Split the filename and extention and make sure it's Python code
            fname, ext = os.path.splitext(plugin_file)
            if ext == ".py":

                # Import the module
                mod = __import__(fname)
                config = self.config[f"plugins:{fname}"] if f"plugins:{fname}" in self.config else None
                plugins[fname] = mod.Plugin(app=self, vdom=self.vdom, config=config)

        self.plugins = plugins

    def createApp(self: object) -> tuple:
        """ Method that constructs the entire app.
        """

        app = Flask(__name__, template_folder=self.template_folder)
        app.config["SECRET_KEY"] = "secret!"
        socketio = SocketIO(app, manage_session=True, async_mode='threading')

        def sendStateUpdate(event: dict) -> None:
            session_id = event.get("session_id")
            emit("VDOM_UPDATE", self.vdom.toDict(session_id=session_id))

        def sendNavigationUpdate(event: dict) -> None:
            target = event.get("target", "/")
            search = event.get("search", "")

            if search == "" or search is None:
                target = f"{target}"
            elif search.startswith("?"):
                target = f"{target}{search}"
            else:
                target = f"{target}?{search}"

            emit("NAVIGATION_EVENT", {"target": target})

        def sendClearInputField(event: dict) -> None:
            emit("CLEAR_INPUT_FIELD", {"identifier": event.get("identifier", "")})

        def defaultSend(event: dict) -> None:
            print("TRIGGER", event)
            with app.test_request_context('/'):
                socketio.emit(event.get("type", ""), event)

        # Add some event listeners to send updates to the browser
        self.vdom.dispatcher.addEventListener("STATE_UPDATE_EVENT", sendStateUpdate)
        self.vdom.dispatcher.addEventListener("NAVIGATION_EVENT", sendNavigationUpdate)
        self.vdom.dispatcher.addEventListener("CLEAR_INPUT_FIELD", sendClearInputField)
        self.vdom.dispatcher.addEventListener("DEFAULT", defaultSend)

        @socketio.on("connect")
        def handle_connect() -> None:
            """ Generate and store a session ID for every connect.
            """

            session["session_id"] = str(uuid.uuid4())

        @socketio.on("REQUEST_SESSION")
        def handle_requestSession(event):
            emit("STORE_SESSION", {"session_id": session["session_id"]})

        @socketio.on("RESTORE_SESSION")
        def handle_restoreSession(event):
            print("Restoring session:", event)
            session["session_id"] = event.get("session_id")

        @socketio.on("DOM_EVENT")
        def handle_dom_event(json: dict) -> None:

            if "DOMEventCategory" in json:

                if json.get("DOMEventCategory", None) == "MouseEvent click":

                    target_identifier = json.get("target", "")
                    if target_identifier is not "":
                        self.vdom.dispatcher.dispatchEvent(
                            {
                                "type": f"ON_CLICK_{target_identifier}",
                                "session_id": session["session_id"],
                            }
                        )

                elif (
                    json.get("DOMEventCategory", None) == "Event input"
                    or json.get("DOMEventCategory", None) == "Event change"
                ):
                    target_identifier = json.get("target", "")
                    if target_identifier is not "":
                        self.vdom.dispatcher.dispatchEvent(
                            {
                                "type": f"ON_CHANGE_{target_identifier}",
                                "value": json.get("value", ""),
                                "session_id": session["session_id"],
                            }
                        )

                elif json.get("DOMEventCategory", None) == "Event submit":
                    target_identifier = json.get("target", "")
                    if target_identifier is not "":
                        self.vdom.dispatcher.dispatchEvent(
                            {
                                "type": f"ON_FORM_SUBMIT_{target_identifier}",
                                "session_id": session["session_id"],
                            }
                        )

                elif json.get("DOMEventCategory", None) == "UIEvent load":
                    self.vdom.dispatcher.dispatchEvent(
                        {
                            "type": "NAVIGATION_EVENT",
                            "target": json.get("link_target", "/"),
                            "search": json.get("link_search", None),
                            "anchor": json.get("link_anchor", None),
                            "session_id": session["session_id"],
                        }
                    )

                else:
                    print(f"Recieved an unhandled event: {json}")
            else:
                print(f"Recieved an unhandled event: {json}")

            # Update the DOM after the event has been handled
            # TODO: Reduce the number of refresh (only when the vdom actually changed)
            self.vdom.dispatcher.dispatchEvent(
                {"type": "STATE_UPDATE_EVENT", "session_id": session["session_id"]}
            )

        @socketio.on("DEFAULT")
        def handle_all_json(json):
            json["session_id"] = session["session_id"]
            print("Dispatching DEFAULT event")
            self.vdom.dispatcher.dispatchEvent(json)

        @app.route("/", defaults={"path": ""})
        @app.route("/<path:path>")
        def catch_all(path: str) -> str:
            """ Catch all routes and redirect them to the index page
                where the Router takes over the rest of the navigation.
            """
            with app.test_request_context():
                if path == "public/index.js":
                    return send_from_directory(
                        os.path.abspath(
                            os.path.join(os.path.dirname(__file__), "../public")
                        ),
                        "index.js",
                    )

                # Serve from the users public path
                if path.startswith("public/"):
                    return send_from_directory(
                        os.path.abspath(self.public_folder), path[7:]
                    )

                return render_template(
                    "index.html",
                    title=self.title,
                    extend_head=self.extend_head,
                    custom_javascript=self.custom_javascript,
                )

        return socketio, app

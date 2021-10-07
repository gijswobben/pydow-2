import os
import sys
import configparser

from flask import Flask
from flask_socketio import emit
from flask_socketio import SocketIO

from typing import Generic
from typing import TypeVar

from .handlers import (
    handle_connect,
    handle_requestSession,
    handle_restoreSession,
    handle_dom_event,
    handle_all_json,
)

from .routes import catch_all

from pydow.signals import (
    signal_navigation_event,
    signal_state_update,
    signal_clear_input_field_event,
    signal_default_event,
)

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
        middleware_folder: str = "./middleware",
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
        self.public_folder = os.path.abspath(public_folder)
        self.plugin_folder = plugin_folder
        self.middleware_folder = middleware_folder
        self.custom_javascript = custom_javascript
        self.template_folder = os.path.abspath(
            os.path.join(os.path.dirname(__file__), template_folder)
        )

        # Register any plugins in the plugin folder
        self.registerPlugins()

        # Register any middleware in the middleware folder
        self.registerMiddelWare()

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
                config = (
                    self.config[f"plugins:{fname}"]
                    if f"plugins:{fname}" in self.config
                    else None
                )
                plugins[fname] = mod.Plugin(app=self, vdom=self.vdom, config=config)

        self.plugins = plugins

    def registerMiddelWare(self: object) -> None:
        """
        """

        # Add the plugin folder to the search path (this is relative to the users app)
        sys.path.insert(0, self.middleware_folder)

        middleware = {}

        if not os.path.isdir(self.middleware_folder):
            self.middleware = middleware
            return

        # Detect middleware files
        middleware_files = [
            f
            for f in os.listdir(self.middleware_folder)
            if os.path.isfile(os.path.join(self.middleware_folder, f))
        ]

        # Loop the plugin files
        for middleware_file in middleware_files:

            # Split the filename and extention and make sure it's Python code
            fname, ext = os.path.splitext(middleware_file)
            if ext == ".py":

                # Import the module
                mod = __import__(fname)
                config = (
                    self.config[f"middleware:{fname}"]
                    if f"middleware:{fname}" in self.config
                    else None
                )
                if config.getboolean("enabled", fallback=True):
                    middleware[fname] = mod.MiddleWare(
                        app=self, vdom=self.vdom, config=config
                    )

        self.middleware = middleware

    def runMiddleWare(self: object, *args: list, **kwargs: dict) -> None:
        """ Method that triggers the middleware at every request.
        """

        for name, middleware in self.middleware.items():
            print(f"Running middleware {name}")
            middleware.run(*args, **kwargs)

    def _sendStateUpdate(self: object, event: dict, *args, **kwargs) -> None:
        """ Method that emits updates to the VDOM to the browser.
        """
        session_id = event.get("session_id")
        emit("VDOM_UPDATE", self.vdom.toDict(session_id=session_id))

    def _sendNavigationUpdate(self: object, event: dict) -> None:
        """ Helper method that sends navigation update events to the browser.
        """

        # Run any middleware when changing pages
        self.runMiddleWare(session_id=event.get("session_id"))

        # Extract information about where we're going
        target = event.get("link_target", "/")
        search = event.get("link_search", "")

        # Construct the url
        if search == "" or search is None:
            target = f"{target}"
        elif search.startswith("?"):
            target = f"{target}{search}"
        else:
            target = f"{target}?{search}"

        # Emit the navigation change to the browser
        emit("NAVIGATION_EVENT", {"link_target": target})

    def _defaultSend(self: object, event: dict) -> None:
        """ Fallback method for any unknown event that should be send to the browser.
        """
        with self.app.test_request_context("/"):
            self.socketio.emit(event.get("type", ""), event)

    def _sendClearInputField(self: object, event: dict) -> None:
        """ Specific method for emitting an event to clear an input field in the browser.
        """
        emit("CLEAR_INPUT_FIELD", {"identifier": event.get("identifier", "")})

    def createApp(self: object) -> tuple:
        """ Method that constructs the entire app (assembly).
        """

        # Create the Flask app and Socket
        self.app = Flask(__name__, template_folder=self.template_folder)
        self.app.config["SECRET_KEY"] = "secret!"
        self.socketio = SocketIO(self.app, manage_session=True, async_mode="threading")

        # Register callbacks for different event signals
        signal_state_update.connect(self._sendStateUpdate, weak=False)
        signal_navigation_event.connect(self._sendNavigationUpdate, weak=False)
        signal_clear_input_field_event.connect(self._sendClearInputField, weak=False)
        signal_default_event.connect(self._defaultSend, weak=False)

        # Register SocketIO events
        self.socketio.on_event("connect", handle_connect)
        self.socketio.on_event("REQUEST_SESSION", handle_requestSession)
        self.socketio.on_event("RESTORE_SESSION", handle_restoreSession)
        self.socketio.on_event("DEFAULT", handle_all_json)
        self.socketio.on_event("DOM_EVENT", handle_dom_event)

        # Add url routes for the Flask app
        self.app.add_url_rule(
            "/<path:path>",
            "catch_all",
            defaults={
                "app": self.app,
                "public_folder": self.public_folder,
                "title": self.title,
                "extend_head": self.extend_head,
                "custom_javascript": self.custom_javascript,
            },
            view_func=catch_all,
        )
        self.app.add_url_rule(
            "/",
            "catch_all",
            defaults={
                "path": "",
                "app": self.app,
                "public_folder": self.public_folder,
                "title": self.title,
                "extend_head": self.extend_head,
                "custom_javascript": self.custom_javascript,
            },
            view_func=catch_all,
        )

        # Return the socket and app
        return self.socketio, self.app

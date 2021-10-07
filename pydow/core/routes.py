import os

from flask import render_template
from flask import send_from_directory


def catch_all(path: str, app, public_folder, title, extend_head, custom_javascript, *args, **kwargs) -> str:
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
                os.path.abspath(public_folder), path[7:]
            )

        return render_template(
            "index.html",
            title=title,
            extend_head=extend_head,
            custom_javascript=custom_javascript,
        )

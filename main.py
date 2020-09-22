"""Google Cloud Functions frontend to the plucode module."""

import os
try:
    from secrets import choice
except ImportError:
    # secrets was added in Python 3.6
    from random import choice

import flask

from lib import plucode

_USERNAME = os.environ.get('BASIC_AUTH_USERNAME')
"""String expected HTTP basic authentication username."""

_PASSWORD = os.environ.get('BASIC_AUTH_PASSWORD')
"""String expected HTTP basic authentication password."""

_FALLBACKS = [
    "I didn't get that. Can you say it again?",
    "I missed what you said. What was that?",
    "Sorry, could you say that again?",
    "Sorry, can you say that again?",
    "Can you say that again?",
    "Sorry, I didn't get that. Can you rephrase?",
    "Sorry, what was that?",
    "One more time?",
    "What was that?",
    "Say that one more time?",
    "I didn't get that. Can you repeat?",
    "I missed that, say that again?"
]
"""List of string fallback responses to use."""

_NOT_FOUND = [
    "I couldn't find that.",
    "Sorry, I couldn't find that.",
    "I didn't find that.",
    "Sorry, I didn't find that.",
    "No match found.",
    "Sorry, no match found.",
    "No match was found.",
    "Sorry, no match was found."
]
"""List of string responses to use when no match was found."""

_LIMIT = 7
"""Integer maximum number of matches to return."""

_TOO_MANY = [
    "Too many matches. Can you be more specific?",
    "Too many matches. Can you rephrase?"
]
"""List of string responses to use when more than _LIMIT matches were found."""

def _build_google_response(text=None, expect_response=False,
                           choices=_FALLBACKS):
    """Return a flask.Response object in the Dialogflow webhook format.

    Args:
        text: Optional string response text.
        expect_response: Optional boolean flag indicating whether a user
            response is expected.
            Defaults to False which ends the conversation.
        choices: Optional list of string responses from which to choose when
            text is not supplied.
    Returns:
        flask.Response object in the Dialogflow webhook format.
    """
    if not isinstance(text, str):
        text = choice(choices)
    if len(text) <= 0:
        text = choice(choices)

    response = flask.jsonify({
        'payload': {
            'google': {
                'expectUserResponse': expect_response,
                'richResponse': {
                    'items': [
                        {
                            'simpleResponse': {
                                'displayText': text,
                                'textToSpeech': text
                            }
                        }
                    ]
                }
            }
        }
    })
    response.content_type = 'application/json; charset=utf-8'
    return response

def google(request):
    """Look up a PLU code or find a PLU code by description.

    Args:
        request (flask.Request): The request object.
        <https://flask.palletsprojects.com/en/1.0.x/api/#flask.Request>
    Returns:
        The response text, or any set of values that can be turned into a
        Response object using `make_response`.
        <https://flask.palletsprojects.com/en/1.0.x/api/#flask.Flask.make_response>
    """
    if isinstance(_USERNAME, str) and isinstance(_PASSWORD, str):
        # HTTP basic authentication
        if request.authorization is None:
            return flask.abort(401)
        if ((request.authorization.username != _USERNAME) or
            (request.authorization.password != _PASSWORD)):
            return flask.abort(401)

    if request.method != 'POST':
        return flask.abort(405)

    request_json = request.get_json(silent=True)
    if not isinstance(request_json, dict):
        # mimetype does not indicate JSON or parsing failed
        return _build_google_response()
    query_result = request_json.get('queryResult')
    if not isinstance(query_result, dict):
        return _build_google_response()
    parameters = query_result.get('parameters')
    if not isinstance(parameters, dict):
        return _build_google_response()

    number = parameters.get('number')
    description = parameters.get('description')
    if isinstance(number, str):
        return _build_google_response(plucode.get_description(number),
                                      choices=_NOT_FOUND)
    elif isinstance(description, str) and (len(description) > 0):
        keywords = description.strip().lower().split()
        codes = plucode.get_code(keywords)
        count = len(codes)
        if count <= 0:
            return _build_google_response(choices=_NOT_FOUND)
        elif count > _LIMIT:
            return _build_google_response(choices=_TOO_MANY)
        else:
            return _build_google_response(', '.join(codes))
    else:
        return _build_google_response()

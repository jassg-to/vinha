from firebase_functions import https_fn, options
from firebase_functions.params import SecretParam

JWT_SECRET = SecretParam("JWT_SECRET")

_asgi_app = None


def _get_app():
    global _asgi_app
    if _asgi_app is None:
        from evinha.main import app
        _asgi_app = app
    return _asgi_app


@https_fn.on_request(
    region="northamerica-northeast1",
    memory=options.MemoryOption.MB_512,
    max_instances=10,
    secrets=[JWT_SECRET],
)
def api(req: https_fn.Request) -> https_fn.Response:
    import asyncio
    from a2wsgi import ASGIMiddleware

    app = _get_app()
    wsgi = ASGIMiddleware(app)

    # Build WSGI environ from Flask request
    environ = req.environ.copy()
    response_started = []
    response_body = []

    def start_response(status, headers, exc_info=None):
        response_started.append((status, headers))
        return response_body.append

    result = wsgi(environ, start_response)
    try:
        body = b"".join(result)
    finally:
        if hasattr(result, "close"):
            result.close()

    status_code = int(response_started[0][0].split(" ", 1)[0])
    headers = dict(response_started[0][1])

    from flask import Response as FlaskResponse
    return FlaskResponse(body, status=status_code, headers=headers)

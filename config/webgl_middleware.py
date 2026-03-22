# FILE LOCATION:
# D:\Amrutha\AIGLMS\gamified_lms\config\webgl_middleware.py
#
# CREATE this as a new file inside your config/ folder
# (same folder as settings.py and urls.py)

class WebGLHeadersMiddleware:
    """
    Unity WebGL needs special HTTP headers to load in a browser.
    Without this, the .wasm and .js files are blocked and the
    game shows a blank screen or gives a MIME type error.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        path = request.path

        if path.endswith('.js'):
            response['Content-Type'] = 'application/javascript'

        elif path.endswith('.wasm'):
            response['Content-Type'] = 'application/wasm'

        elif path.endswith('.data'):
            response['Content-Type'] = 'application/octet-stream'

        # Required for Unity WebGL threading to work in browser
        response['Cross-Origin-Opener-Policy']  = 'same-origin'
        response['Cross-Origin-Embedder-Policy'] = 'require-corp'

        return response
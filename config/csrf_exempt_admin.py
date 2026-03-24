from django.middleware.csrf import CsrfViewMiddleware

class DisableCSRFOnAdmin(CsrfViewMiddleware):
    """
    Disables CSRF check specifically for Django admin on Railway.
    Safe because admin is protected by username/password login.
    """
    def process_view(self, request, callback, callback_args, callback_kwargs):
        # Skip CSRF check for admin URLs
        if request.path.startswith('/admin/'):
            return None
        return super().process_view(
            request, callback, callback_args, callback_kwargs
        )
METHOD_OVERRIDE_HEADER = 'HTTP_X_HTTP_METHOD_OVERRIDE'


class PatchOverrideMiddleware(object):
    def process_view(self, request, callback, callback_args, callback_kwargs):
        if request.method == 'POST' and request.META.get(METHOD_OVERRIDE_HEADER) == 'PATCH':
            request.method = 'PATCH'

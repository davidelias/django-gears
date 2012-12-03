import os
import mimetypes
import posixpath
import time
import urllib

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.contrib.staticfiles.views import serve as staticfiles_serve
from django.views.static import serve as default_serve
from django.http import HttpResponse
from django.utils.http import http_date

from gears.assets import build_asset
from gears.exceptions import FileNotFound

from .settings import environment


MAX_AGE = 60 * 60 * 24 * 7  # 1 week


def serve(request, path, **kwargs):
    if not settings.DEBUG and not kwargs.get('insecure'):
        raise ImproperlyConfigured(
            "The gears view can only be used in debug mode or if the "
            "--insecure option of 'runserver' is used.")

    mimetype, encoding = mimetypes.guess_type(path)
    should_serve = mimetype in environment.mimetypes.values()

    # It is only required check because we generate
    # version arg for each file
    if should_serve and 'HTTP_IF_MODIFIED_SINCE' in request.META:
        response = HttpResponse()
        response['Expires'] = http_date(time.time() + MAX_AGE)
        response.status_code = 304
        return response

    normalized_path = posixpath.normpath(urllib.unquote(path)).lstrip('/')

    try:
        asset = build_asset(environment, normalized_path)
    except FileNotFound:
        return staticfiles_serve(request, path, **kwargs)

    mimetype, encoding = mimetypes.guess_type(normalized_path)
    if not should_serve:
        document_root, path = os.path.split(asset.absolute_path)
        return default_serve(request, path, document_root=document_root)

    last_modified = asset.mtime
    source = asset.processed_source if 'body' in request.GET else asset.compressed_source
    response = HttpResponse(source, mimetype=mimetype)
    if encoding:
        response['Content-Encoding'] = encoding
    response['Last-Modified'] = http_date(last_modified)
    return response

import os
import mimetypes
import posixpath
import urllib

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.contrib.staticfiles.views import serve as staticfiles_serve
from django.views.static import was_modified_since
from django.http import HttpResponse, HttpResponseNotModified
from django.utils.http import http_date

from gears.assets import build_asset
from gears.exceptions import FileNotFound

from .settings import environment


def serve(request, path, **kwargs):
    if not settings.DEBUG and not kwargs.get('insecure'):
        raise ImproperlyConfigured(
            "The gears view can only be used in debug mode or if the "
            "--insecure option of 'runserver' is used.")

    mimetype, encoding = mimetypes.guess_type(path)
    if not mimetype in environment.mimetypes.values():
        return staticfiles_serve(request, path, **kwargs)

    normalized_path = posixpath.normpath(urllib.unquote(path)).lstrip('/')

    try:
        asset = build_asset(environment, normalized_path)
    except FileNotFound:
        return staticfiles_serve(request, path, **kwargs)

    bundle = not request.GET.get('body')
    source = asset.compressed_source if bundle else asset.processed_source

    # Respect the If-Modified-Since header.
    size = len(source)
    modified_since = request.META.get('HTTP_IF_MODIFIED_SINCE')
    if not was_modified_since(modified_since, asset.mtime, size):
        return HttpResponseNotModified(mimetype=asset.attributes.mimetype)

    response = HttpResponse(source, mimetype=asset.attributes.mimetype)
    response['Last-Modified'] = http_date(asset.mtime)
    response['Content-Length'] = size
    if encoding:
        response['Content-Encoding'] = encoding

    return response

from django.conf import settings

from .engines import get_engine_class
from .environment import Environment
from .finders import get_finder_class
from .processors import get_processor_class


DEFAULT_FINDERS = (
    ('gears.finders.FileSystemFinder', {
        'directories': getattr(settings, 'GEARS_DIRS', ()),
    }),
)

DEFAULT_MIMETYPES = {
    '.css': 'text/css',
    '.js': 'application/javascript',
}

DEFAULT_PREPROCESSORS = {
    'text/css': 'gears.processors.DirectivesProcessor',
    'application/javascript': 'gears.processors.DirectivesProcessor',
}

DEFAULT_PUBLIC_ASSETS = (
    'css/style.css',
    'js/script.js',
)


environment = Environment(getattr(settings, 'GEARS_ROOT'))

for finder_class in getattr(settings, 'GEARS_FINDERS', DEFAULT_FINDERS):
    if isinstance(finder_class, (list, tuple)):
        finder_class, options = finder_class
    else:
        options = {}
    finder_class = get_finder_class(finder_class)
    environment.finders.register(finder_class(**options))

mimetypes = getattr(settings, 'GEARS_MIMETYPES', DEFAULT_MIMETYPES)
for extension, mimetype in mimetypes.items():
    environment.mimetypes.register(extension, mimetype)

for extension, engine_class in getattr(settings, 'GEARS_ENGINES', {}).items():
    if isinstance(engine_class, (list, tuple)):
        engine_class, options = engine_class
    else:
        options = {}
    engine_class = get_engine_class(engine_class)
    environment.engines.register(extension, engine_class(**options))

public_assets = getattr(settings, 'GEARS_PUBLIC_ASSETS', DEFAULT_PUBLIC_ASSETS)
for public_asset in public_assets:
    environment.public_assets.register(public_asset)

preprocessors = getattr(settings, 'GEARS_PREPROCESSORS', DEFAULT_PREPROCESSORS)
for mimetype, preprocessor_classes in preprocessors.items():
    if not isinstance(preprocessor_classes, (list, tuple)):
        preprocessor_classes = [preprocessor_classes]
    for preprocessor_class in preprocessor_classes:
        preprocessor_class = get_processor_class(preprocessor_class)
        environment.preprocessors.register(mimetype, preprocessor_class)

postprocessors = getattr(settings, 'GEARS_POSTPROCESSORS', {})
for mimetype, postprocessor_classes in postprocessors.items():
    if not isinstance(postprocessor_classes, (list, tuple)):
        postprocessor_classes = [postprocessor_classes]
    for postprocessor_class in postprocessor_classes:
        postprocessor_class = get_processor_class(postprocessor_class)
        environment.postprocessors.register(mimetype, postprocessor_class)

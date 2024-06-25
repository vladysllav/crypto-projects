from datetime import timedelta

from .base import *  # noqa: F403

DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

# Additional applications and customizations for development
INSTALLED_APPS += [  # noqa: F405
    "silk",
]

MIDDLEWARE += [  # noqa: F405
    "silk.middleware.SilkyMiddleware",
]

SIMPLE_JWT.update(  # noqa: F405
    {
        "ACCESS_TOKEN_LIFETIME": timedelta(days=7),
        "REFRESH_TOKEN_LIFETIME": timedelta(days=30),
    }
)

INTERNAL_IPS = [
    "127.0.0.1",
]

# Silk settings
SILKY_AUTHENTICATION = True
SILKY_AUTHORISATION = True
SILKY_PYTHON_PROFILER = True

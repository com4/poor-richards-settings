# Poor Richard's Settings Framework
# Version: 0.1.0
# URL: https://github.com/com4/poor-richards-settings/
# Copyright 2020 jason@zzq.org
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
import logging
import os
import sys
import threading
from typing import Dict, get_type_hints, List, Tuple

# Uses the module name for a cleaner logger name
logger = logging.getLogger(__name__.split(".")[0])


class Settings:
    """Define settings for the application."""
    #: All settings are required to be ``not None`` unless in this list
    _optional_settings: Tuple[str] = ()
    #: These settings cannot be set by an environment variable
    _no_environ_set: Tuple[str] = ()

    # Examples: Replace with your settings
    #: Enables debug mode
    debug: bool = False
    #: DSN for Postgres
    database_dsn: str = None


def update_from_env(settings_class, *, prefix):
    """Update a global settings class with environment variables.

    This function pulls environment variables starting with ``prefix``, removes
    ``prefix``, lower cases the remaining suffix and sets the value on the
    class attribute.

    .. note::

       This function is thread-safe.

    Args:
        settings_class: The global settings class to update
        prefix: The prefix of the environment variables to consider.
    """
    type_hints = get_type_hints(settings_class)
    with threading.Lock():
        for k in os.environ:
            if not k.startswith(prefix):
                continue

            attr = k.replace(prefix, "").lower()

            if attr in getattr(settings_class, "_no_environ_set", ()):
                logger.debug(f"Skipping {k}. Disallowed set from environ.")
                continue

            v = os.getenv(k)
            try:
                # Attempt to typecast based on the hint.
                v = type_hints.get(attr)(v)
            except (AttributeError, KeyError, TypeError):
                pass


            logger.debug(
                "Found environment variable: {}. ({}={})".format(
                    k,
                    attr,
                    "****{}".format(v[:4]) if "password" in attr else v))
            setattr(settings_class, attr, v)


def get_missing_settings(settings_class) -> List[str]:
    """Used to validate required settings.

    Verifies that all attributes which don't start with ``_`` and aren't named
    in ``_optional_settings`` are not set to None.

    Args:
        settings_class: The global settings class to validate settings on.

    Returns: List of setting names that should not be ``None``. If the list is
        empty then all required settings are defined.
    """
    missing_settings = []
    for attr in vars(settings_class):
        if attr.startswith("_") or \
           attr in getattr(settings_class, "_optional_settings", ()):
            continue

        if getattr(settings_class, attr) is None:
            missing_settings.append(attr)

    return missing_settings


def test_get_missing_settings():
    class TestSettings:
        _optional_settings = ("optional", )
        setting1: str = None
        setting2: int = 123
        optional: str = None

    missing_settings = get_missing_settings(TestSettings)

    # the only missing setting should be setting1
    missing_settings_len = len(missing_settings)
    assert missing_settings_len == 1, f"{missing_settings_len} != 1"
    assert "setting1" in missing_settings, f"'setting1' not in {missing_settings}"


def test_update_from_env():
    class TestSettings:
        _no_environ_set = ("s5", )
        s1: int = None
        s2: bool = None
        s3: str = None
        s4: str = None
        s5: List[int] = (1, 2, 3)

    os.environ["MYAPP_S1"] = "32"
    os.environ["MYAPP_S2"] = "1"
    os.environ["MYAPP_S3"] = "a test"
    os.environ["MYAPP_S5"] = "should be skipped"
    update_from_env(TestSettings, prefix="MYAPP_")
    del os.environ["MYAPP_S1"]
    del os.environ["MYAPP_S2"]
    del os.environ["MYAPP_S3"]
    del os.environ["MYAPP_S5"]

    # should be typecast to an int
    assert TestSettings.s1 == 32, f"{TestSettings.s1} != 32"
    # should be typecast to a bool
    assert TestSettings.s2 is True, f"{TestSettings.s2} is not True"
    assert TestSettings.s3 == "a test", f"{TestSettings.s3} != 'a test'"
    # Should remain None
    assert TestSettings.s4 is None, f"{TestSettings.s4} is not None"
    # Should have been skipped
    assert TestSettings.s5 == (1, 2, 3), f"{TestSettings.s5} != (1, 2, 3)"

if __name__ == "__main__":
    test_get_missing_settings()
    test_update_from_env()

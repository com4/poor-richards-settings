# Poor Richard's Settings Framework
Defines a simple settings framework targeting values set via environment
variables. PRSF is self contained and should be copy and pasted to other
projects which need global application settings.

## Features:
* Works with IDE auto-complete
* No external dependencies
* Automatically pull values from environment variables and set on your class
* Simple static class (no singletons)
* Typecast primitive types via hints (int, bool, str)
* Thread safe


## Usage
Add fields as class variables to the Settings object. At the entry point
of your app, inject the environment variables and validate there are no missing
settings.

Environment variables are expected to have a prefix (e.g. your app
name). The are parsed, prefix removed, lowercased and set as attributes on the
class. For example if the prefix is ``MYAPP_`` then ``MYAPP_MY_SETTING`` would
correspond to ``Settings.my_setting``.

```python
from . import conf

conf.update_from_env(conf.Settings, "MYAPP_")
missing_settings = conf.get_missing_settings(conf.Settings)
if len(missing_settings) > 0:
    for s in missing_settings:
        logger.error(f"Undefined setting {s}")
    sys.exit(1)

print("All required settings are defined")
```

## Upgrading
You'll have to manually make your changes if you copy/pasted into your
application.  Use `git diff` or Github to diff the version you're currently on
with the target or latest version. The functions should be replaceable and
changes to the Settings class minimal. PSRF uses semantic versioning so
backward incompatible changes will be noted with a new major version number.

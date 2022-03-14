from pathlib import Path

from poetry_publish.publish import poetry_publish  # type: ignore

import cfgcaddy

PACKAGE_ROOT = Path(cfgcaddy.__file__).parent.parent


def publish():
    poetry_publish(
        package_root=PACKAGE_ROOT,
        version=cfgcaddy.__version__,
    )

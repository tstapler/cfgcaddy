from pathlib import Path

import cfgcaddy
from poetry_publish.publish import poetry_publish


def publish():
    poetry_publish(
        package_root=Path(cfgcaddy.__file__).parent.parent,
        version=cfgcaddy.__version__,
    )

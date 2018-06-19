from setuptools import setup

setup(
    name='cfgcaddy',
    version='0.1.1',
    description='Tool for managing configuration files',
    url='https://github.com/tstapler/cfgcaddy',
    author='Tyler Stapler',
    author_email='tystapler@gmail.com',
    license='MIT',
    packages=['cfgcaddy'],
    install_requires=[
        "click",
        "enum34",
        "pathspec",
        "pyyaml",
        "whaaaaat",
    ],
    entry_points={'console_scripts': ['cfgcaddy = cfgcaddy.__main__:main']},
    zip_safe=True)

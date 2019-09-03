from setuptools import setup

setup(
    name='cfgcaddy',
    version='0.1.2',
    description='Tool for managing configuration files',
    url='https://github.com/tstapler/cfgcaddy',
    author='Tyler Stapler',
    author_email='tystapler@gmail.com',
    license='MIT',
    packages=['cfgcaddy'],
    install_requires=[
        "click==6.7",
        "enum34==1.1.6",
        "pathspec==0.5.3",
        "pyyaml==3.12",
        "whaaaaat==0.5.2",
    ],
    entry_points={'console_scripts': ['cfgcaddy = cfgcaddy.__main__:main']},
    zip_safe=True)

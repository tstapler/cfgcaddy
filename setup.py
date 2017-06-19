from setuptools import setup

setup(name='cfgcaddy',
      version='0.1',
      description='Tool for managing configuration files',
      url='https://github.com/tstapler/cfgcaddy',
      author='Tyler Stapler',
      author_email='tystapler at gm@il',
      license='MIT',
      packages=['cfgcaddy'],
      install_requires=[
          "inquirer",
          "yaml"
      ],
      zip_safe=True)

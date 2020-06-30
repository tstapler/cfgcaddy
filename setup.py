from setuptools import setup

setup(name='cfgcaddy',
      version='0.1.3',
      description='Tool for managing configuration files',
      url='https://github.com/tstapler/cfgcaddy',
      author='Tyler Stapler',
      author_email='tystapler@gmail.com',
      license='MIT',
      packages=['cfgcaddy'],
      install_requires=[
          "click==6.7", "enum34==1.1.6", "pathspec==0.5.3",
          "ruamel.yaml==0.16.5", "whaaaaat==0.5.2", "prompt-toolkit<1.0.15"
      ],
      entry_points={'console_scripts': ['cfgcaddy = cfgcaddy.__main__:main']},
      zip_safe=True)

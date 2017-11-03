try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
from glob import glob
import os.path


setup(
    name='datatools',
    # version='0.1.0',
    # author='S. Fenn',
    # author_email='shannon.fenn@gmail.com',
    # # packages=['datatools'],
    scripts=glob(os.path.join('scripts', '*.py')),
    # url='https://github.com/shannonfenn/data-tools',
    # license='LICENSE.txt',
    # description='Tools for data generation and handling.',
    # long_description='',
    # install_requires=[
    #     "numpy >= 1.10.1",
    #     "pandas >= 0.17.0",
    # ],
)

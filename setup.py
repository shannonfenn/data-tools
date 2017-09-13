try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='datatools',
    # version='0.1.0',
    # author='S. Fenn',
    # author_email='shannon.fenn@gmail.com',
    # # packages=['datatools'],
    scripts=['scripts/aggregate_results.py',
             'scripts/collapse_keys.py',
             'scripts/cumulative_scores.py',
             'scripts/filter_keys.py',
             'scripts/join_completed.py',
             'scripts/json2numpy.py',
             'scripts/read_sampling_settings.py',
             'scripts/write_bool_mapping.py',
             'scripts/write_nontrivial_samples.py',
             'scripts/write_samples.py'],
    # url='https://github.com/shannonfenn/data-tools',
    # license='LICENSE.txt',
    # description='Tools for data generation and handling.',
    # long_description='',
    # install_requires=[
    #     "numpy >= 1.10.1",
    #     "pandas >= 0.17.0",
    # ],
)

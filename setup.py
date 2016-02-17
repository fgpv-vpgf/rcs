from distutils.core import setup

setup(
    name="rcs",
    description="RAMP Configuration Service",
    version="2.0.0-1",
    author="Environment Canada",
    author_email="mike.weech@ec.gc.ca",
    url="https://github.com/fgpv-vpgf/rcs",
    py_modules=['run', 'wfastcgi', 'config', 'seed_qa_keys'],
    packages=['services'],
    license='MIT',
)

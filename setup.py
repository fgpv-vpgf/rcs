from distutils.core import setup
import os

# http://bugs.python.org/issue8876#msg208792
del os.link

setup(
    name="rcs",
    description="RAMP Configuration Service",
    version="2.2.1",
    author="Environment and Climate Change Canada",
    author_email="mike.weech@canada.ca",
    url="https://github.com/fgpv-vpgf/rcs",
    py_modules=['run', 'wfastcgi', 'config', 'seed_qa_keys'],
    packages=['services', 'services.db', 'services.regparse'],
    license='MIT',
)

from distutils.core import setup

setup(
    name="rcs",
    description="RAMP Configuration Service",
    version="1.0.0",
    author="Environment Canada",
    author_email="mike.weech@ec.gc.ca",
    url="https://github.com/RAMP-PCAR/RCS",
    py_modules=['rcs','wfastcgi'],
    packages=['db','regparse'],
)

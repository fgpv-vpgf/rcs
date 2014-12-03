from distutils.core import setup

setup(
    name="rcs",
    description="RAMP Configuration Service",
    version="1.5.1",
    author="Environment Canada",
    author_email="mike.weech@ec.gc.ca",
    url="https://github.com/RAMP-PCAR/RCS",
    py_modules=['rcs','wfastcgi','config'],
    packages=['db','regparse'],
    license='MIT',
)

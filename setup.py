from distutils.core import setup

setup(
    name="rcs",
    description="RAMP Configuration Service",
    version="1.10.1",
    author="Environment Canada",
    author_email="mike.weech@ec.gc.ca",
    url="https://github.com/fgpv-vpgf/rcs",
    py_modules=['rcs','wfastcgi','config','seed_qa_keys'],
    packages=['db','regparse'],
    license='MIT',
)

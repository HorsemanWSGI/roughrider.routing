import os
from setuptools import setup, find_packages


version = "0.2"

install_requires = [
    'horseman',
    'autoroutes'
]

test_requires = [
    'WebTest',
    'pyhamcrest',
    'pytest',
]


setup(
    name='roughrider.routing',
    version=version,
    author='Souheil CHELFOUH',
    author_email='trollfot@gmail.com',
    url='',
    download_url='http://pypi.python.org/pypi/roughrider.routing',
    description='Routing utilities for WSGI apps using horseman.',
    long_description=(open("README.rst").read() + "\n" +
                      open(os.path.join("docs", "HISTORY.rst")).read()),
    license='ZPL',
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Internet :: WWW/HTTP :: WSGI',
    ],
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['roughrider',],
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    extras_require={
        'test': test_requires,
    },
)

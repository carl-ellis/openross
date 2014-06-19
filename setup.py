from setuptools import setup

setup(
    name='openross',
    version='0.1.0',
    description='Open BobRoss Image Processor',
    url='http://www.lyst.com',
    license='FreeBSD Licence',
    author='LYST Ltd',
    author_email='data@ly.st',

    # packaging
    packages=['openross', 'openross.endpoint', 'openross.pipeline', 'openross.twisted.plugins'],

    # dependencies
    install_requires=[
        'Twisted>=13.1.0',
        'txJSON-RPC==0.3.1',
        'setuptools_trial==0.5.12',
        'ujson==1.30',
        'txaws==0.2.3',
        'pHash==0.1',
        'zope.interface==4.0.5',
        'pgmagick==0.5.7',
        'boto==2.9.0',
        'raven==3.3.6',
        'pyopenssl==0.13.1',
        'python-statsd==1.6.0',
    ],
    include_package_data=True,
    zip_safe=False,

    # scripts
    entry_points={}
)

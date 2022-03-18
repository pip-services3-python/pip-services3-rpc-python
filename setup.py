"""
Pip.Services Rpc
----------------------

Pip.Services is an open-source library of basic microservices.
pip_services3_rpc provides synchronous and asynchronous communication components.

Links
`````

* `website <http://github.com/pip-services-python/>`_
* `development version <http://github.com/pip-services3-python/pip-services3-rpc-python>`

"""

from setuptools import find_packages
from setuptools import setup

try:
    readme = open('readme.md').read()
except:
    readme = __doc__

setup(
    name='pip_services3_rpc',
    version='3.3.2',
    url='http://github.com/pip-services3-python/pip-services3-rpc-python',
    license='MIT',
    author='Conceptual Vision Consulting LLC',
    author_email='seroukhov@gmail.com',
    description='Communication components for Pip.Services in Python',
    long_description=readme,
    long_description_content_type="text/markdown",
    packages=find_packages(exclude=['config', 'data', 'test']),
    include_package_data=True,
    zip_safe=True,
    platforms='any',
    install_requires=[
        'pytz',
        'bottle >= 0.12.19, < 0.13',
        'requests >= 2.27.1, < 3.0',
        'cheroot >= 8.6.0, < 9.0',
        'beaker >= 1.11.0, < 2.0',
        'psutil >= 5.9.0, < 6.0',
        'pip-services3-commons >= 3.3.13, < 4.0',
        'pip-services3-components >= 3.5.9, < 4.0'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)

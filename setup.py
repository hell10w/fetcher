# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


version = __import__('fetcher').__version__


setup(
    name = 'fetcher',
    version = version,
    description = 'Spiders framework',
    url = 'http://github.com/alexey-grom/fetcher',
    author = 'Gromov Alexey',
    author_email = 'alxgrmv@gmail.com',

    packages = find_packages(),
    include_package_data = True,
)

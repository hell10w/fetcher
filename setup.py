from distutils.core import setup


setup(
    name='fetcher',
    version='0.0.1',
    packages=[
        'fetcher',
        'fetcher.multifetch',
        'fetcher.multifetch.dispatcher',
        'fetcher.tasks',
        'fetcher.tasks.queues',
        'fetcher.test',
        'fetcher.test.utils',
        'fetcher.fetch',
        'fetcher.fetch.transport',
        'fetcher.errors',
        'fetcher.cache'],
    url='http://github.com/alexey-grom/fetcher',
    license='',
    author='Alexey Gromov',
    author_email='',
    description=''
)

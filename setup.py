from distutils.core import setup

setup(
    name='fetcher',
    version='0.0.2',
    packages=['fetcher', 'fetcher.multifetch', 'fetcher.multifetch.dispatcher', 'fetcher.tasks', 'fetcher.tasks.queues',
              'fetcher.test', 'fetcher.test.utils', 'fetcher.fetch', 'fetcher.fetch.transport',
              'fetcher.fetch.extensions', 'fetcher.fetch.extensions.js_aux', 'fetcher.errors', 'fetcher.cache',
              'samples'],
    url='',
    license='',
    author='Alexey Gromov',
    author_email='',
    description=''
)

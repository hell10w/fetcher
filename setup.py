from distutils.core import setup

setup(
    name='fetcher',
    version='0.0.3',
    packages=['samples', 'fetcher', 'fetcher.tasks', 'fetcher.tasks.queues', 'fetcher.test', 'fetcher.test.utils',
              'fetcher.fetch', 'fetcher.fetch.transport', 'fetcher.fetch.extensions', 'fetcher.fetch.extensions.js_aux',
              'fetcher.multifetch', 'fetcher.multifetch.dispatcher', 'fetcher.cache', 'fetcher.errors',
              'fetcher.frontend', 'fetcher.frontend.flask_frontend'],
    url='',
    license='',
    author='Alexey Gromov',
    author_email='',
    description=''
)

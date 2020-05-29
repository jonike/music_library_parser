from setuptools import setup

setup(
    name='music_library_parser',
    version='1.4.9',
    packages=['media_parser', 'media_parser.db',
              'media_parser.lib', 'tests'],
    url='https://github.com/github-pdx/music_library_parser',
    license='MIT',
    author='github.pdx',
    author_email='github.pdx@runbox.com',
    description=f'extract metadata from ['.mp3','.m4a','.flac','.wma'] files'
)

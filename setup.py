import os

from setuptools import setup, find_packages


def get_scripts(path):
    for name in os.listdir(path):
        yield os.path.join(path, name)

setup(
    name='dbooru',
    version='0.1',
    package_dir={'': 'src'},
    packages=find_packages('src'),
    scripts=list(get_scripts('src/bin')),

    author='Allen Li',
    author_email='darkfeline@felesatra.moe',
    description='',
    license='',
    url='',
)

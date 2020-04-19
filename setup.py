from setuptools import setup, find_packages

setup(
    name='netut',
    version='0.0.1',
    url='https://github.com/rtitle/neil-tut.git',
    author='Rob & Neil Title',
    author_email='rtitle@gmail.com',
    description='Neil Tut games',
    packages=find_packages(),    
    install_requires=['pygame >= 1.9.6'],
)

#from distutils.core import setup
from setuptools import setup
setup(
    name='newsonterminal',
    version='1.0.0',
    py_modules=['newsonterminal'],
    license='LICENSE.md',
    author='Amit Kulkarni',
    author_email='kulkarniamit@outlook.com',
    url='https://github.com/kulkarniamit/newsonterminal',
    install_requires=["requests >= 2.13.0","lxml == 3.7.3"],
    description='A simple utility to display the top news on terminal'
)

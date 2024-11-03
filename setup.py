from setuptools import setup, find_packages

setup(
    name="tmk",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'pandas',
        'praw',
        'openai',
        'textblob',
        'pyyaml',
    ],
) 
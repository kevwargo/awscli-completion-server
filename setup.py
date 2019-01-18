from setuptools import setup, find_packages

setup(
    name='aws-comp-srv',
    install_requires=['awscli'],
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'aws-comp-srv = awscli_completion_server:run'
        ]
    }
)

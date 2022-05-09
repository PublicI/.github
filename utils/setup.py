from setuptools import setup
setup(
    name = 'publici_utils',
    version = '0.0.1',
    entry_points = {
        'console_scripts': [
            'publici-acl = acl_utils:main',
        ]
    },
    install_requires = ['pyyaml']
)
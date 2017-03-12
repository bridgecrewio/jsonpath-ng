import io
import setuptools


setuptools.setup(
    name='jsonpath-ng',
    version='1.4.2',
    description=(
        'A robust and significantly extended implementation '
        'of JSONPath for Python, with a clear AST for metaprogramming.'
    ),
    author='Tomas Aparicio',
    author_email='tomas@aparicio.me',
    url='https://github.com/tomas-fp/python-jsonpath-ng',
    license='Apache 2.0',
    long_description=io.open('README.rst', encoding='utf-8').read(),
    packages=['jsonpath_ng', 'jsonpath_ng.bin', 'jsonpath_ng.ext'],
    entry_points={
        'console_scripts': [
            'jsonpath.py=jsonpath_ng.bin.jsonpath:entry_point'
        ],
    },
    test_suite='tests',
    install_requires=[
        'ply', 'decorator', 'six'
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)

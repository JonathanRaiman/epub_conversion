import os
from setuptools import setup, find_packages

def readfile(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='epub-conversion',
    version='1.0.7',
    description='Python package for converting xml and epubs to text files',
    long_description=readfile('README.md'),
    ext_modules=[],
    packages=find_packages(),
    py_modules = [],
    author='Jonathan Raiman',
    author_email='jraiman at mit dot edu',
    url='https://github.com/JonathanRaiman/epub_conversion',
    download_url='https://github.com/JonathanRaiman/epub_conversion',
    keywords='XML, epub, tokenization, NLP',
    license='MIT',
    platforms='any',
    zip_safe=False,
    classifiers=[
        'Intended Audience :: Science/Research',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.3',
        'Topic :: Text Processing :: Linguistic',
    ],
    # test_suite="something.test",
    setup_requires = [],
    install_requires=[
        'bz2file',
        'epub',
        'xml_cleaner'
    ],
    include_package_data=True,
)

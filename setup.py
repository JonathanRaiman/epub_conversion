import os
from setuptools import setup, find_packages


def readfile(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name='epub-conversion',
    version='1.0.8',
    description='Python package for converting xml and epubs to text files',
    long_description=readfile('README.md'),
    long_description_content_type="text/markdown",
    ext_modules=[],
    packages=find_packages(),
    py_modules=[],
    author='Jonathan Raiman',
    author_email='jonathanraiman@gmail.com',
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
    setup_requires=[],
    install_requires=[
        'bz2file',
        'epub',
        'ciseau'
    ],
    include_package_data=True,
)

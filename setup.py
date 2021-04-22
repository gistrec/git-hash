from setuptools import find_packages, setup

LONGDESC = """
Git-Hash can be used to create commit hash by mask.

Website: https://github.com/gistrec/git-hash

Author:  Aleksandr Kovalko <gistrec@mail.ru>
"""

setup(
    name="git-hash",
    version="1.0.2",
    description='Create commit hash by mask',
    license='Apache License 2.0',
    author="Aleksandr Kovalko",
    author_email="gistrec@mail.ru",
    url="https://github.com/gistrec/git-hash",
    platforms='Any',
    install_requires=[
        'optparse-pretty'
    ],
    packages=find_packages(),
    long_description=LONGDESC,
    zip_safe=True,
    entry_points={
        'console_scripts': [
           'git-hash = githash.githash:run',
        ]},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Programming Language :: Python",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Version Control",
        "Topic :: Utilities"],
    keywords='git hash commit'
)

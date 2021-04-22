from setuptools import find_packages, setup

LONGDESC = """
Git-Hash can be used to create commit hash by mask.
Website: https://github.com/gistrec/git-hash
Author:  Aleksandr Kovalko <gistrec@mail.ru>
"""

setup(
    name="git-hash",
    version="1.0.0",
    description='Create commit hash by mask',
    license='Apache License 2.0',
    author="Aleksandr Kovalko",
    author_email="gistrec@mail.ru",
    url="",
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
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Utilities"],
    keywords='git hash commit'
)

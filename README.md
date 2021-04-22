# Git-Hash

[![PyPI](https://img.shields.io/pypi/v/git-hash.svg)](https://pypi.python.org/pypi/git-hash "Package listing on PyPI")
[![Codecov](https://img.shields.io/codecov/c/github/gistrec/git-hash.svg)](https://codecov.io/gh/gistrec/git-hash "Code coverage (via Codecov)")

---

Git-Hash can be used to create commit hash by mask.

## Installation

Git-Hash requires [Python](https://www.python.org) 2.7 or 3.4+. Further, for installation, [pip](https://pip.pypa.io) should be used.

To install the [latest release](https://pypi.python.org/pypi/git-hash) of Git-Hash from PyPI:

```console
pip install git-hash
```

## Usage

To generate a hash that starts with `<hash>`, go to the directory with the git repository and write:

```console
git-hash <hash> --verbose
```

You will see something like this:
```console
> git-hash aaaaaa --verbose
Subhash to find: aaaaaa
Approximate number of permutations 1048576
Iteration 130000, compute 12%, elapsed 0 sec, estimated 1 sec.
Iteration 260000, compute 25%, elapsed 0 sec, estimated 1 sec.
Iteration 390000, compute 37%, elapsed 1 sec.
Commit hash: aaaaaa3ad991376a76b69853969c8414392ba03a
Author date: 1595131373

You can change commit hash by:
GIT_COMMITTER_DATE="Thu Apr 22 13:35:45 2021 +0700" git commit --amend --no-edit --date "1595131373"
```

**Note: it is not recommended to specify more than 8 characters.**
# Git-Hash

[![PyPI](https://img.shields.io/pypi/v/git-hash.svg)](https://pypi.python.org/pypi/git-hash "Package listing on PyPI")
[![Tests](https://github.com/gistrec/git-hash/actions/workflows/tests.yml/badge.svg)](https://github.com/gistrec/git-hash/actions/workflows/tests.yml "GitHub Actions test runs")
[![Codecov](https://img.shields.io/codecov/c/github/gistrec/git-hash.svg)](https://codecov.io/gh/gistrec/git-hash "Code coverage (via Codecov)")
[![License: Apache 2.0](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://www.apache.org/licenses/LICENSE-2.0)

---

`git-hash` finds an author timestamp for `HEAD` such that the resulting commit
SHA-1 starts with a hex prefix you choose. Useful for vanity hashes
(e.g. `deadbeef…`, `c0ffee…`).

## Installation

Requires Python 3.8+ and a working `git` on `PATH`.

```console
pip install git-hash
```

## Usage

Inside a git repository, run:

```console
git-hash <prefix> [--verbose]
```

`<prefix>` must be lowercase hexadecimal (`0-9`, `a-f`).

Example:

```console
> git-hash aaaaaa --verbose
Hash to find: aaaaaa
Approximate number of permutations 1048576
Iteration 130000, compute 12%, elapsed 0 sec, estimated 1 sec.
Iteration 260000, compute 25%, elapsed 0 sec, estimated 1 sec.
Iteration 390000, compute 37%, elapsed 1 sec.
Commit hash: aaaaaa3ad991376a76b69853969c8414392ba03a
Author date: 1595131373

You can change commit hash by:
GIT_COMMITTER_DATE="1595131400 +0700" git commit --amend --no-edit --date "1595131373 +0700"
```

Copy the printed `git commit --amend` line and run it. After the amend, `git rev-parse HEAD` will equal the `Commit hash` printed by the tool — the committer date is preserved via `GIT_COMMITTER_DATE`, and the new author date is passed in git's raw `<unix> <tz>` format.

## How it works

A git commit object is hashed as:

```
sha1("commit " + len(body) + "\0" + body)
```

where `body` is the textual commit (tree, parents, author, committer, message). Changing any byte changes the SHA-1. `git-hash` mutates only the **author timestamp** of `HEAD`'s commit body and re-hashes in a tight loop, decrementing the timestamp by one second each iteration until the digest's prefix matches. The committer line is left untouched, which is why the suggested `git commit --amend` sets `GIT_COMMITTER_DATE` to its original value — together they reproduce the exact body that was hashed.

## Limitations

- Only `HEAD` is rewritten. To re-hash older commits, use an interactive rebase and apply this tool at each step.
- Search cost is `~16^N` SHA-1s for an `N`-character prefix. **More than 8 characters is not recommended** (16⁸ ≈ 4·10⁹ hashes, easily minutes-to-hours on a single core).
- The author timestamp must remain 10 digits (years ~2001–2286). The tool aborts cleanly if it would leave that range.
- Forging vanity hashes is for fun and aesthetics. Don't use it to imitate other authors or backdate commits in contexts where that would mislead anyone.

## Running tests

```console
python -m unittest discover -s tests
```

With coverage:

```console
python -m coverage run --source=githash -m unittest discover -s tests
python -m coverage report -m
```

## License

Apache License 2.0. See [LICENSE](https://www.apache.org/licenses/LICENSE-2.0).

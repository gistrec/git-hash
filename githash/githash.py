#!/usr/bin/env python
# -*- coding: utf-8 -*-


import optparse
import subprocess
import hashlib
import time
import re


HEX_RE = re.compile(r"^[0-9a-f]+$")
AUTHOR_DATE_RE = re.compile(rb"^author .*<[^>]*> (\d{10}) ([+-]\d{4})$", re.MULTILINE)
COMMITTER_DATE_RE = re.compile(rb"^committer .*<[^>]*> (\d{10}) ([+-]\d{4})$", re.MULTILINE)


def is_repository_exists():
    result = subprocess.run(
        ["git", "rev-parse", "--is-inside-work-tree"], capture_output=True
    )
    return result.returncode == 0


def get_commit_info():
    result = subprocess.run(["git", "cat-file", "commit", "HEAD"], capture_output=True)
    return result.stdout


def build_commit_object(commit_body):
    return b"commit " + str(len(commit_body)).encode("ascii") + b"\0" + commit_body


def find_hash(commit_body, subhash, verbose=False, log=print):
    """Find an author timestamp such that SHA-1 of the commit object starts with `subhash`.

    Only the author date is mutated; the committer date is preserved so that the
    printed hash matches what `git commit --amend` produces when the caller also
    sets `GIT_COMMITTER_DATE` to the original committer timestamp.

    Returns (new_commit_body, new_author_date, author_tz, committer_date, committer_tz,
             iterations, elapsed_seconds).
    """
    author = AUTHOR_DATE_RE.search(commit_body)
    if author is None:
        raise ValueError("Cannot locate author date in commit object.")
    committer = COMMITTER_DATE_RE.search(commit_body)
    if committer is None:
        raise ValueError("Cannot locate committer date in commit object.")

    date = author.group(1)
    author_tz = author.group(2)
    committer_date = committer.group(1)
    committer_tz = committer.group(2)
    date_start = author.start(1)

    object_bytes = build_commit_object(commit_body)
    obj_date_start = len(object_bytes) - len(commit_body) + date_start

    target_len = len(subhash)
    start = time.time()
    iterations = 0

    while True:
        iterations += 1
        if hashlib.sha1(object_bytes).hexdigest()[:target_len] == subhash:
            break

        new_date = str(int(date) - 1).encode("ascii")
        if len(new_date) != 10:
            raise RuntimeError(
                "Author timestamp left the 10-digit range; aborting to keep object length stable."
            )
        object_bytes = (
            object_bytes[:obj_date_start]
            + new_date
            + object_bytes[obj_date_start + 10:]
        )
        date = new_date

        if verbose and iterations % (2 ** 17) == 0:
            ratio = iterations / 16 ** target_len
            elapsed = time.time() - start
            estimated = elapsed / ratio if ratio else 0
            log(
                "Iteration %d, compute %d%%, elapsed %d sec, estimated %d sec."
                % (round(iterations, -4), ratio * 100, elapsed, estimated)
            )

    elapsed = time.time() - start
    new_commit_body = object_bytes[len(object_bytes) - len(commit_body):]
    return (
        new_commit_body,
        date,
        author_tz,
        committer_date,
        committer_tz,
        iterations,
        elapsed,
    )


def run():
    options_parser = optparse.OptionParser(
        usage="%prog <hash> [OPTIONS]",
        description="Compute commit date that starts with the <hash>.",
    )
    options_parser.add_option(
        "--verbose",
        action="store_true",
        dest="verbose",
        default=False,
        help="verbose output (statistics, etc.)",
    )
    options, args = options_parser.parse_args()
    if not len(args):
        options_parser.error("The <hash> not set.")
    subhash = args[0].lower()
    if not HEX_RE.match(subhash):
        print("Invalid hash string. Allowed characters: 0-9, a-f.")
        return

    if not is_repository_exists():
        print("Repository not found.")
        return

    commit = get_commit_info()

    print("Hash to find: %s" % subhash)
    print("Approximate number of permutations %d" % 16 ** len(subhash))

    try:
        (
            new_commit,
            date,
            author_tz,
            committer_date,
            committer_tz,
            iterations,
            elapsed,
        ) = find_hash(commit, subhash, verbose=options.verbose)
    except (ValueError, RuntimeError) as exc:
        print(str(exc))
        return

    digest = hashlib.sha1(build_commit_object(new_commit)).hexdigest()
    ratio = iterations / 16 ** len(subhash)
    print(
        "Iteration %d, compute %d%%, elapsed %d sec."
        % (iterations, ratio * 100, elapsed)
    )
    print("Commit hash: %s" % digest)
    print("Author date: %s" % date.decode("ascii"))
    print("")

    print("You can change commit hash by:")
    print(
        'GIT_COMMITTER_DATE="%s %s" git commit --amend --no-edit --date "%s %s"'
        % (
            committer_date.decode("ascii"),
            committer_tz.decode("ascii"),
            date.decode("ascii"),
            author_tz.decode("ascii"),
        )
    )


if __name__ == "__main__":
    run()

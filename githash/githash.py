#!/usr/bin/env python
# -*- coding: utf-8 -*-


import optparse
import subprocess
import hashlib
import time
import re


def is_repository_exists():
    result = subprocess.run(["git", "branch", "--show-current"], capture_output=True)
    return result.returncode == 0


def get_commit_info():
    result = subprocess.run(["git", "cat-file", "commit", "HEAD"], capture_output=True)
    return result.stdout


def run():
    options_parser = optparse.OptionParser(
        usage="%prog <hash> [OPTIONS]",
        description="Compute commit date that starts with the <hash>.")
    options_parser.add_option("--verbose",
                              action="store_true", dest="verbose", default=False,
                              help="verbose output (statistics, etc.)")
    options, args = options_parser.parse_args()
    if not len(args):
        options_parser.error("The <hash> not set.")
    subhash = args[0].lower()
    if not re.match(r"^[a-z0-9]+$", subhash):
        print("Invalid hash string.")
        return

    if not is_repository_exists():
        print("Repository not found.")
        return

    # Create string to be hashed.
    commit = get_commit_info()
    commit = b'commit ' + str(len(commit)).encode("utf-8") + b'\0' + commit

    # Get author date. This date will decrease to get the required hash.
    date = re.search(rb"> (\d{10})", commit).group(1)

    # Print statistic.
    print("Hash to find: %s" % subhash)
    print("Approximate number of permutations %d" % 16 ** len(subhash))

    start = time.time()
    iterations = 0

    while True:
        iterations += 1

        current_hash = hashlib.sha1(commit)

        if current_hash.hexdigest()[0:len(subhash)] == subhash:
            break

        # Get new author date by reducing the previous.
        new_date = str(int(date.decode("utf-8")) - 1).encode("utf-8")

        commit = commit.replace(date, new_date)
        date = new_date

        # Print verbose message every 2^18 iterations.
        if options.verbose and iterations % (2 ** 17) is 0:
            ratio = iterations / 16 ** len(subhash)
            elapsed = time.time() - start
            estimated = elapsed / ratio
            print("Iteration %d, compute %d%%, elapsed %d sec, estimated %d sec." %
                  (round(iterations, -4), ratio * 100, elapsed, estimated))

    ratio = iterations / 16 ** len(subhash)
    elapsed = time.time() - start
    print("Iteration %d, compute %d%%, elapsed %d sec." % (iterations, ratio * 100, elapsed))
    print("Commit hash: %s" % hashlib.sha1(commit).hexdigest())
    print("Author date: %s" % date.decode("utf-8"))
    print("")

    commit_date = subprocess.run(["git", "log", "-1", "--format=%cd"], capture_output=True, encoding="utf-8").stdout.strip()
    print("You can change commit hash by:")
    print('GIT_COMMITTER_DATE="%s" git commit --amend --no-edit --date "%s"' % (commit_date, date.decode("utf-8")))


if __name__ == '__main__':
    run()

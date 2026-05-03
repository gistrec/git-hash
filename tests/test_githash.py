import hashlib
import re
import unittest

from githash.githash import (
    AUTHOR_DATE_RE,
    COMMITTER_DATE_RE,
    HEX_RE,
    build_commit_object,
    find_hash,
)


SAMPLE_COMMIT = (
    b"tree 4b825dc642cb6eb9a060e54bf8d69288fbee4904\n"
    b"author Test User <test@example.com> 1700000000 +0300\n"
    b"committer Other User <other@example.com> 1700000050 -0500\n"
    b"\n"
    b"sample message\n"
)


class HexValidationTests(unittest.TestCase):
    def test_accepts_hex_lowercase(self):
        self.assertIsNotNone(HEX_RE.match("0123456789abcdef"))

    def test_rejects_non_hex_letters(self):
        for s in ("g", "abz", "xyz", "abc!", ""):
            self.assertIsNone(HEX_RE.match(s), "should reject %r" % s)

    def test_rejects_uppercase(self):
        # `run()` lower-cases input first, but HEX_RE itself must be strict.
        self.assertIsNone(HEX_RE.match("ABC"))


class CommitParsingTests(unittest.TestCase):
    def test_author_date_regex_matches(self):
        m = AUTHOR_DATE_RE.search(SAMPLE_COMMIT)
        self.assertIsNotNone(m)
        self.assertEqual(m.group(1), b"1700000000")
        self.assertEqual(m.group(2), b"+0300")

    def test_committer_date_regex_matches(self):
        m = COMMITTER_DATE_RE.search(SAMPLE_COMMIT)
        self.assertIsNotNone(m)
        self.assertEqual(m.group(1), b"1700000050")
        self.assertEqual(m.group(2), b"-0500")

    def test_author_regex_does_not_match_committer_line(self):
        # If author line is missing, AUTHOR_DATE_RE must not fall back to committer.
        commit_no_author = re.sub(rb"^author .*\n", b"", SAMPLE_COMMIT, flags=re.MULTILINE)
        self.assertIsNone(AUTHOR_DATE_RE.search(commit_no_author))


class BuildCommitObjectTests(unittest.TestCase):
    def test_object_format(self):
        obj = build_commit_object(b"hello")
        self.assertEqual(obj, b"commit 5\x00hello")

    def test_sha1_matches_git_blob_format(self):
        # Reproduces git's own object hashing: header + body.
        body = SAMPLE_COMMIT
        expected = hashlib.sha1(
            b"commit " + str(len(body)).encode() + b"\0" + body
        ).hexdigest()
        self.assertEqual(
            hashlib.sha1(build_commit_object(body)).hexdigest(), expected
        )


class FindHashTests(unittest.TestCase):
    def test_finds_single_char_prefix(self):
        new_commit, date, author_tz, c_date, c_tz, iterations, _ = find_hash(
            SAMPLE_COMMIT, "a"
        )
        digest = hashlib.sha1(build_commit_object(new_commit)).hexdigest()
        self.assertTrue(digest.startswith("a"))
        self.assertGreaterEqual(iterations, 1)

    def test_committer_line_unchanged(self):
        # The whole point of the fix: committer date must remain bit-identical,
        # otherwise the printed hash will not match what git produces with
        # GIT_COMMITTER_DATE=<original>.
        new_commit, _, _, c_date, c_tz, _, _ = find_hash(SAMPLE_COMMIT, "0")
        self.assertEqual(c_date, b"1700000050")
        self.assertEqual(c_tz, b"-0500")
        original_committer_line = b"committer Other User <other@example.com> 1700000050 -0500\n"
        self.assertIn(original_committer_line, new_commit)

    def test_author_date_decremented(self):
        new_commit, date, _, _, _, iterations, _ = find_hash(SAMPLE_COMMIT, "0")
        # Author date must equal original (1700000000) minus (iterations - 1):
        # iteration 1 hashes the original commit; each subsequent iteration
        # decrements once before re-hashing.
        self.assertEqual(int(date), 1700000000 - (iterations - 1))
        author_line = b"author Test User <test@example.com> %d +0300\n" % int(date)
        self.assertIn(author_line, new_commit)

    def test_returned_body_matches_returned_digest(self):
        # The hash printed by run() is sha1(build_commit_object(new_commit_body)).
        # If this passes, the user can reproduce the same hash with:
        #   GIT_COMMITTER_DATE="<c_date> <c_tz>" git commit --amend --no-edit \
        #       --date "<date> <author_tz>"
        new_commit, date, author_tz, c_date, c_tz, _, _ = find_hash(
            SAMPLE_COMMIT, "f"
        )
        digest = hashlib.sha1(build_commit_object(new_commit)).hexdigest()
        # Reconstruct the body from the returned fields and verify byte equality.
        rebuilt = re.sub(
            rb"^author (.*)<([^>]*)> \d{10} [+-]\d{4}$",
            lambda m: b"author "
            + m.group(1)
            + b"<"
            + m.group(2)
            + b"> "
            + date
            + b" "
            + author_tz,
            SAMPLE_COMMIT,
            count=1,
            flags=re.MULTILINE,
        )
        self.assertEqual(rebuilt, new_commit)
        self.assertEqual(
            hashlib.sha1(build_commit_object(rebuilt)).hexdigest(), digest
        )
        self.assertTrue(digest.startswith("f"))

    def test_raises_on_missing_author(self):
        broken = b"tree abc\ncommitter X <x@x> 1700000000 +0000\n\nm\n"
        with self.assertRaises(ValueError):
            find_hash(broken, "0")


if __name__ == "__main__":
    unittest.main()

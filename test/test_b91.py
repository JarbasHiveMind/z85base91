import os
import random
import re
import unittest
from pathlib import Path

from z85base91 import B91
from z85base91.b91 import B91 as B91py


class TestB91(unittest.TestCase):
    def test_encode_empty(self):
        """Test encoding an empty byte sequence."""
        self.assertEqual(B91.encode(b''), b'')
        self.assertEqual(B91.encode(''), b'')

    def test_decode_empty(self):
        """Test decoding an empty string."""
        self.assertEqual(B91.decode(''), b'')
        self.assertEqual(B91.decode(b''), b'')

    def test_encode_single_byte(self):
        """Test encoding a single byte."""
        self.assertEqual(b'A', B91.decode(B91.encode(b'A')))
        self.assertEqual(b'B', B91.decode(B91.encode('B')))
        self.assertEqual(b'_~', B91.decode(B91.encode(b'_~')))
        self.assertEqual(b'_~', B91.decode(B91.encode('_~')))

    def test_encode_short_string(self):
        """Test encoding a short string."""
        self.assertEqual(b'hello', B91.decode(B91.encode(b'hello')))
        self.assertEqual(B91.decode('>OwJh>Io0Tv!lE'), b'Hello World')

    def test_encode_decode_round_trip(self):
        """Test encoding and decoding round-trip."""
        data = b'The quick brown fox jumps over the lazy dog.'
        encoded = B91.encode(data)
        decoded = B91.decode(encoded)
        self.assertEqual(decoded, data)

    def test_encode_unicode_string(self):
        """Test encoding a Unicode string."""
        data = 'こんにちは'  # Japanese for "hello"
        encoded = B91.encode(data)
        decoded = B91.decode(encoded)
        self.assertEqual(decoded.decode('utf-8'), data)

    def test_decode_invalid_character(self):
        """Test decoding with invalid Base91 characters."""
        with self.assertRaises(ValueError):
            B91.decode('Invalid🎉Chars')

    def test_3bytes_threshold(self):
        """Test edge cases around the 88 threshold."""
        data = b'\x00\x00\x00'  # Minimal data
        encoded = B91.encode(data)
        self.assertEqual(B91.decode(encoded), data)

    def test_encode_large_data(self):
        """Test encoding a large byte sequence."""
        data = b'\xff' * 1000
        encoded = B91.encode(data)
        decoded = B91.decode(encoded)
        self.assertEqual(decoded, data)


if __name__ == '__main__':
    unittest.main()


class TestShippedLibraries(unittest.TestCase):
    """The committed shared libraries must implement the alphabet in src/b91.c.

    The binaries are committed artifacts built by hand, one per architecture, so
    nothing stops one of them being rebuilt while the others keep an older
    codec. Wire compatibility then depends on which machine a peer happens to
    run on: a client on one architecture encodes text its counterpart cannot
    decode, and the only symptom is the far end rejecting every frame it is
    sent.

    The alphabet survives compilation as a contiguous string constant, so each
    binary can be checked by reading it rather than executing it. That is what
    lets a test on any one machine cover the builds for every architecture.
    """

    @staticmethod
    def _source_alphabet():
        source = Path(__file__).resolve().parents[1] / "src" / "b91.c"
        text = source.read_text(encoding="utf-8")
        match = re.search(r'ALPHABET\[ALPHABET_SIZE\]\s*=\s*"((?:[^"\\]|\\.)*)"', text)
        assert match, "could not find the alphabet in src/b91.c"
        return match.group(1).replace('\\"', '"').replace("\\\\", "\\")

    @staticmethod
    def _embedded_alphabet(path):
        """The 91 distinct printable characters the compiler left in the binary."""
        blob = path.read_bytes()
        for run in re.findall(rb"[\x21-\x7e]{80,120}", blob):
            candidate = run.decode("latin1")
            if len(candidate) == 91 and len(set(candidate)) == 91:
                return candidate
        return None

    def test_alphabet_is_defined_once_in_the_source(self):
        """The expectation every binary is measured against."""
        alphabet = self._source_alphabet()
        self.assertEqual(len(alphabet), 91)
        self.assertEqual(len(set(alphabet)), 91, "the alphabet repeats a character")

    def test_every_shipped_library_matches_the_source(self):
        """A binary built from older source ships a different codec in silence."""
        expected = self._source_alphabet()
        package = Path(__file__).resolve().parents[1] / "z85base91"
        libraries = sorted(package.glob("libbase91-*.so"))
        self.assertTrue(libraries, "no compiled base91 libraries found")

        stale = {}
        for library in libraries:
            found = self._embedded_alphabet(library)
            if found != expected:
                stale[library.name] = found

        self.assertEqual(
            stale, {},
            "these libraries were built from different source than src/b91.c, so "
            "they encode text other architectures cannot decode",
        )


class TestLoadedLibraryEquivalence(unittest.TestCase):
    """The library this machine loads must agree with the pure-Python codec.

    The alphabet check above reads every binary, so it covers architectures
    this machine cannot run. This one exercises the build that actually loaded,
    over every byte value and random inputs, and is the check a user can run in
    place on the architecture they deploy to: it would have shown the drift on
    the board where it happened rather than at the far end of the wire.
    """

    def test_c_and_python_encode_identically(self):
        rng = random.Random(0x5B91)
        samples = [bytes([b]) for b in range(256)]
        samples += [bytes(range(256)), b"", b"\x00" * 64, b"\xff" * 64]
        samples += [os.urandom(rng.randint(1, 2048)) for _ in range(300)]
        for data in samples:
            self.assertEqual(B91.encode(data), B91py.encode(data), data[:16])

    def test_c_and_python_decode_each_other(self):
        rng = random.Random(0x5B92)
        samples = [bytes([b]) for b in range(256)]
        samples += [os.urandom(rng.randint(1, 2048)) for _ in range(300)]
        for data in samples:
            self.assertEqual(B91py.decode(B91.encode(data)), data, data[:16])
            self.assertEqual(B91.decode(B91py.encode(data)), data, data[:16])

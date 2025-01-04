# TODO - package this properly for pypi
# $ gcc -shared -o libz85p.so -fPIC z85p.c
# $ gcc -shared -o libz85b.so -fPIC z85b.c
# $ gcc -shared -o libbase91.so -fPIC b91.c

import ctypes
from ctypes import c_char_p, c_void_p, c_size_t, c_ubyte, byref, POINTER
from typing import Union


class Z85P:
    # Load the shared library
    lib = ctypes.CDLL('./libz85p.so')  # On Windows, use './z85p.dll'

    # Initialize the Z85 map (this needs to be called first)
    lib.initialize_z85_map()

    # Define the encode function prototype
    lib.encode_z85p.argtypes = [ctypes.POINTER(ctypes.c_ubyte), c_size_t, POINTER(c_size_t)]
    lib.encode_z85p.restype = ctypes.POINTER(ctypes.c_ubyte)

    # Define the decode function prototype
    lib.decode_z85p.argtypes = [ctypes.POINTER(ctypes.c_ubyte), c_size_t, POINTER(c_size_t)]
    lib.decode_z85p.restype = ctypes.POINTER(ctypes.c_ubyte)

    @classmethod
    def encode(cls, data: bytes) -> bytes:
        out_len = c_size_t(0)
        raw_data = (ctypes.c_ubyte * len(data))(*data)
        encoded_data = cls.lib.encode_z85p(raw_data, len(data), ctypes.byref(out_len))
        return bytes(ctypes.string_at(encoded_data, out_len.value))

    @classmethod
    def decode(cls, data: bytes) -> bytes:
        out_len = c_size_t(0)
        raw_data = (ctypes.c_ubyte * len(data))(*data)
        decoded_data = cls.lib.decode_z85p(raw_data, len(data), ctypes.byref(out_len))
        return bytes(ctypes.string_at(decoded_data, out_len.value))


class B91:
    # Load the shared library
    lib = ctypes.CDLL('./libbase91.so')  # On Windows, use './base91.dll'

    # Initialize the decode table (this needs to be called first)
    lib.initialize_decode_table()

    # Define the decode function prototype
    lib.decode.argtypes = [c_char_p, ctypes.POINTER(c_size_t)]
    lib.decode.restype = c_void_p

    # Define the encode function prototype
    lib.encode.argtypes = [ctypes.POINTER(ctypes.c_ubyte), c_size_t, ctypes.POINTER(c_size_t)]
    lib.encode.restype = c_char_p

    @classmethod
    def decode(cls, encoded_data: Union[str, bytes]):
        if isinstance(encoded_data, str):
            # Convert the encoded data to bytes
            encoded_data = encoded_data.encode('utf-8')
        output_len = c_size_t(0)

        # Call the C function
        decoded_data = cls.lib.decode(encoded_data, ctypes.byref(output_len))

        if decoded_data:
            return ctypes.string_at(decoded_data, output_len.value)
        else:
            raise ValueError("Invalid Base91 string")

    @classmethod
    def encode(cls, data: Union[str, bytes]):
        if isinstance(data, str):
            # Convert the data to bytes
            data = data.encode('utf-8')
        output_len = c_size_t(0)

        # Call the C function
        encoded_data = cls.lib.encode((ctypes.c_ubyte * len(data))(*data), len(data), ctypes.byref(output_len))

        if encoded_data:
            return ctypes.string_at(encoded_data, output_len.value)
        else:
            raise ValueError("Encoding failed")


class Z85B:
    # Load the shared library dynamically
    lib = ctypes.CDLL('./libz85b.so')  # Update path as needed

    # Define function prototypes
    lib.encode_z85b.argtypes = [POINTER(c_ubyte), c_size_t, POINTER(c_size_t)]
    lib.encode_z85b.restype = POINTER(c_ubyte)

    lib.decode_z85b.argtypes = [POINTER(c_ubyte), c_size_t, POINTER(c_size_t)]
    lib.decode_z85b.restype = POINTER(c_ubyte)

    lib.free.argtypes = [ctypes.c_void_p]  # Add free function for memory cleanup

    @classmethod
    def encode(cls, data: bytes) -> bytes:
        """
        Encode raw bytes into Z85b format.

        Args:
            data (bytes): Input data to encode.

        Returns:
            bytes: Z85b-encoded data.

        Raises:
            ValueError: If encoding fails.
        """
        output_len = c_size_t(0)
        encoded_data = cls.lib.encode_z85b((c_ubyte * len(data))(*data), len(data), byref(output_len))
        if not encoded_data:
            raise ValueError("Encoding failed")

        try:
            return ctypes.string_at(encoded_data, output_len.value)
        finally:
            cls.lib.free(encoded_data)

    @classmethod
    def decode(cls, encoded_data: bytes) -> bytes:
        """
        Decode Z85b-encoded bytes into raw bytes.

        Args:
            encoded_data (bytes): Z85b-encoded input.

        Returns:
            bytes: Decoded raw bytes.

        Raises:
            ValueError: If decoding fails.
        """
        output_len = c_size_t(0)
        decoded_data = cls.lib.decode_z85b((c_ubyte * len(encoded_data))(*encoded_data), len(encoded_data),
                                           byref(output_len))
        if not decoded_data:
            raise ValueError("Decoding failed")

        try:
            return ctypes.string_at(decoded_data, output_len.value)
        finally:
            cls.lib.free(decoded_data)


if __name__ == "__main__":
    from hivemind_bus_client.encodings import Z85B as Z85Bpy, B91 as B91py, Z85P as Z85Ppy


    def test_b91(s=b"Hello, Base91!"):
        # Example usage:
        try:
            encoded = B91py.encode(s)
            print("Encoded py:", encoded)
            decoded = B91py.decode(encoded)
            print("Decoded py:", decoded)

            encoded = B91.encode(s)
            print("Encoded:", encoded)
            decoded = B91.decode(encoded)
            print("Decoded:", decoded)
        except Exception as e:
            print(f"Error: {e}")


    def test_z85b(s=b"Hello, Z85B!"):
        try:
            encoded = Z85Bpy.encode(s)
            print("Encoded py:", encoded)
            decoded = Z85Bpy.decode(encoded)
            print("Decoded py:", decoded)

            encoded = Z85B.encode(s)
            print("Encoded:", encoded)
            decoded = Z85B.decode(encoded)
            print("Decoded:", decoded)
        except Exception as e:
            print(f"Error: {e}")


    def test_z85p(s=b"Hello, Z85P!"):
        try:
            encoded = Z85Ppy.encode(s)
            print(f"Encoded py: {encoded}")
            decoded = Z85Ppy.decode(encoded)
            print(f"Decoded py: {decoded.decode('utf-8')}")

            encoded = Z85P.encode(s)
            print(f"Encoded: {encoded}")
            decoded = Z85P.decode(encoded)
            print(f"Decoded: {decoded.decode('utf-8')}")
        except Exception as e:
            print(f"Error: {e}")


    test_b91()
    test_z85p()
    test_z85b()

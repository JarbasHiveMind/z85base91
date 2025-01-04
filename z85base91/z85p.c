#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

#define Z85CHARS "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ.-:+=^!/*?&<>()[]{}@%$#"

// Z85 character map
static int Z85MAP[256];
static const uint64_t _85s[] = {85 * 85 * 85 * 85, 85 * 85 * 85, 85 * 85, 85, 1};

// Function to initialize the Z85MAP
void initialize_z85_map() {
    for (int i = 0; i < 85; i++) {
        Z85MAP[(unsigned char)Z85CHARS[i]] = i;
    }
}

// Encode function for Z85P
unsigned char* encode_z85p(const unsigned char* rawbytes, size_t raw_len, size_t* out_len) {
    size_t padding = (4 - raw_len % 4) % 4;
    size_t padded_len = raw_len + padding;
    size_t nvalues = padded_len / 4;
    unsigned char* out = (unsigned char*)malloc(nvalues * 5 + 1);
    if (!out) return NULL;

    out[0] = padding;  // Store padding size at the first byte

    uint32_t *values = (uint32_t*)malloc(nvalues * sizeof(uint32_t));
    if (!values) {
        free(out);
        return NULL;
    }

    // Pack raw bytes into 32-bit values
    for (size_t i = 0; i < nvalues; i++) {
        values[i] = 0;
        for (size_t j = 0; j < 4; j++) {
            if (i * 4 + j < raw_len) {
                values[i] |= (rawbytes[i * 4 + j] << (8 * (3 - j)));
            }
        }
    }

    // Encode 32-bit values to Z85
    size_t idx = 1;
    for (size_t i = 0; i < nvalues; i++) {
        uint32_t v = values[i];
        for (size_t j = 0; j < 5; j++) {
            out[idx++] = Z85CHARS[v / _85s[j] % 85];
        }
    }

    free(values);
    *out_len = idx;
    return out;
}

// Decode function for Z85P
unsigned char* decode_z85p(const unsigned char* z85bytes, size_t z85_len, size_t* out_len) {
    if (z85_len == 0 || z85_len % 5 != 1) return NULL;

    size_t padding = z85bytes[0];
    if (padding > 4) return NULL;

    size_t nvalues = (z85_len - 1) / 5;
    unsigned char* out = (unsigned char*)malloc(nvalues * 4);
    if (!out) return NULL;

    uint32_t* values = (uint32_t*)malloc(nvalues * sizeof(uint32_t));
    if (!values) {
        free(out);
        return NULL;
    }

    // Decode Z85 to 32-bit values
    for (size_t i = 0; i < nvalues; i++) {
        uint32_t value = 0;
        for (size_t j = 0; j < 5; j++) {
            value += Z85MAP[z85bytes[1 + i * 5 + j]] * _85s[j];
        }
        values[i] = value;
    }

    // Unpack 32-bit values into raw bytes
    size_t idx = 0;
    for (size_t i = 0; i < nvalues; i++) {
        for (size_t j = 0; j < 4; j++) {
            if (idx < nvalues * 4 - padding) {
                out[idx++] = (values[i] >> (8 * (3 - j))) & 0xFF;
            }
        }
    }

    free(values);
    *out_len = idx;
    return out;
}
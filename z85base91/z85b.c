#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

#define Z85CHARS "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ.-:+=^!/*?&<>()[]{}@%$#"

// Powers of 85 for encoding/decoding
static const uint32_t _85s[5] = {1, 85, 85 * 85, 85 * 85 * 85, 85 * 85 * 85 * 85};

// Encode function
unsigned char* encode_z85b(const unsigned char* data, size_t data_len, size_t* output_len) {
    size_t padding = (4 - data_len % 4) % 4;
    size_t padded_len = data_len + padding;
    size_t nvalues = padded_len / 4;

    // Allocate memory for the encoded output
    unsigned char* encoded = (unsigned char*)malloc(nvalues * 5);
    if (!encoded) return NULL;

    // Copy the data with padding
    unsigned char* padded_data = (unsigned char*)malloc(padded_len);
    memcpy(padded_data, data, data_len);
    memset(padded_data + data_len, 0, padding);

    // Encode the data
    size_t out_idx = 0;
    for (size_t i = 0; i < nvalues; i++) {
        uint32_t value = 0;
        for (size_t j = 0; j < 4; j++) {
            value |= padded_data[i * 4 + j] << (8 * j);
        }

        // Convert the value to base 85
        for (size_t j = 0; j < 5; j++) {
            encoded[out_idx++] = Z85CHARS[value % 85];
            value /= 85;
        }
    }

    free(padded_data);

    // Remove padding characters
    *output_len = out_idx - padding;
    return encoded;
}

// Decode function
unsigned char* decode_z85b(const unsigned char* encoded_data, size_t encoded_len, size_t* output_len) {
    // Allocate memory for the decoded output
    size_t padding = (5 - encoded_len % 5) % 5;
    size_t nvalues = (encoded_len + padding) / 5;
    unsigned char* decoded = (unsigned char*)malloc(nvalues * 4);
    if (!decoded) return NULL;

    // Decode the data
    size_t out_idx = 0;
    for (size_t i = 0; i < nvalues; i++) {
        uint32_t value = 0;
        for (size_t j = 0; j < 5; j++) {
            char* pos = strchr(Z85CHARS, encoded_data[i * 5 + j]);
            if (!pos) {
                free(decoded);
                return NULL; // Invalid character encountered
            }
            value += (pos - Z85CHARS) * _85s[j];
        }

        // Convert the value to raw bytes
        for (size_t j = 0; j < 4; j++) {
            decoded[out_idx++] = (value >> (8 * j)) & 0xFF;
        }
    }

    // Remove padding
    *output_len = out_idx - padding;
    return decoded;
}

int main() {
    // Example encoding and decoding

    const char* input_data = "Hello, Z85b!";
    size_t encoded_len;
    unsigned char* encoded_data = encode_z85b((unsigned char*)input_data, strlen(input_data), &encoded_len);

    if (encoded_data) {
        printf("Encoded: %.*s\n", (int)encoded_len, encoded_data);

        size_t decoded_len;
        unsigned char* decoded_data = decode_z85b(encoded_data, encoded_len, &decoded_len);

        if (decoded_data) {
            printf("Decoded: %.*s\n", (int)decoded_len, decoded_data);
            free(decoded_data);
        } else {
            printf("Decoding failed\n");
        }

        free(encoded_data);
    } else {
        printf("Encoding failed\n");
    }

    return 0;
}

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

#define ALPHABET_SIZE 91

// Base91 Alphabet (same as Python ALPHABET)
const char ALPHABET[ALPHABET_SIZE] = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!#$%&()*+,./:;<=>?@[]^_`{|}~\"";

// Decode table (maps Base91 characters to their indices in the alphabet)
int DECODE_TABLE[256];

// Function to initialize the DECODE_TABLE
void initialize_decode_table() {
    // Set all values to -1 (invalid by default)
    for (int i = 0; i < 256; i++) {
        DECODE_TABLE[i] = -1;
    }

    // Now populate the DECODE_TABLE for valid characters
    for (int i = 0; i < ALPHABET_SIZE; i++) {
        DECODE_TABLE[(unsigned char)ALPHABET[i]] = i;
    }
}

// Base91 decode function
unsigned char* decode(const char* encoded_data, size_t* output_len) {
    size_t length = strlen(encoded_data);
    int v = -1;
    int b = 0;
    int n = 0;
    size_t out_size = length * 13 / 8 + 1; // Rough estimate for output size
    unsigned char* out = (unsigned char*)malloc(out_size);
    if (!out) return NULL;

    size_t out_idx = 0;

    for (size_t i = 0; i < length; i++) {
        char c = encoded_data[i];
        if (DECODE_TABLE[(unsigned char)c] == -1) {
            free(out);
            return NULL;  // Invalid character
        }
        int c_val = DECODE_TABLE[(unsigned char)c];

        if (v < 0) {
            v = c_val;
        } else {
            v += c_val * 91;
            b |= v << n;
            n += (v & 8191) > 88 ? 13 : 14;
            while (n >= 8) {
                out[out_idx++] = b & 255;
                b >>= 8;
                n -= 8;
            }
            v = -1;
        }
    }

    if (v >= 0) {
        out[out_idx++] = (b | v << n) & 255;
    }

    *output_len = out_idx;
    return out;
}

// Base91 encode function
char* encode(const unsigned char* data, size_t data_len, size_t* output_len) {
    size_t out_size = data_len * 2 + 1; // Rough estimate for output size
    char* out = (char*)malloc(out_size);
    if (!out) return NULL;

    int b = 0;
    int n = 0;
    size_t out_idx = 0;

    for (size_t i = 0; i < data_len; i++) {
        b |= data[i] << n;  // Shift the bits
        n += 8;  // Move 8 bits at a time
        if (n > 13) {  // We need to encode multiple characters
            int v = b & 8191;  // Get the first 13 bits (Base91 split)
            if (v > 88) {
                b >>= 13;
                n -= 13;
            } else {
                v = b & 16383;  // Get 14 bits
                b >>= 14;
                n -= 14;
            }
            out[out_idx++] = ALPHABET[v % 91];
            out[out_idx++] = ALPHABET[v / 91];
        }
    }

    // Handle any leftover bits
    if (n) {
        out[out_idx++] = ALPHABET[b % 91];  // Place the final character
        if (n > 7 || b > 90) {
            out[out_idx++] = ALPHABET[b / 91];
        }
    }

    out[out_idx] = '\0';  // Null-terminate the output string
    *output_len = out_idx;
    return out;
}

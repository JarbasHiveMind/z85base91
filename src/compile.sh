#!/bin/bash

# Compile for x86_64
gcc -shared -o libbase91-x86_64.so -fPIC b91.c
gcc -shared -o libz85p-x86_64.so -fPIC z85p.c
gcc -shared -o libz85b-x86_64.so -fPIC z85b.c

# Compile for armhf (32-bit ARM)
arm-linux-gnueabihf-gcc -shared -o libbase91-armhf.so -fPIC b91.c
arm-linux-gnueabihf-gcc -shared -o libz85p-armhf.so -fPIC z85p.c
arm-linux-gnueabihf-gcc -shared -o libz85b-armhf.so -fPIC z85b.c

# Compile for aarch64 (64-bit ARM)
aarch64-linux-gnu-gcc -shared -o libbase91-aarch64.so -fPIC b91.c
aarch64-linux-gnu-gcc -shared -o libz85p-aarch64.so -fPIC z85p.c
aarch64-linux-gnu-gcc -shared -o libz85b-aarch64.so -fPIC z85b.c

# Compile for i386 (32-bit Intel/AMD)
gcc -m32 -shared -o libbase91-i386.so -fPIC b91.c
gcc -m32 -shared -o libz85p-i386.so -fPIC z85p.c
gcc -m32 -shared -o libz85b-i386.so -fPIC z85b.c

# Compile for Windows
x86_64-w64-mingw32-gcc -shared -o libbase91.dll -fPIC b91.c
x86_64-w64-mingw32-gcc -shared -o libz85p.dll -fPIC z85p.c
x86_64-w64-mingw32-gcc -shared -o libz85b.dll -fPIC z85b.c

# Compile for MacOS
osxcross -shared -o libbase91.dylib -fPIC b91.c
osxcross -shared -o libz85p.dylib -fPIC z85p.c
osxcross -shared -o libz85b.dylib -fPIC z85b.c

echo "Compilation completed!"

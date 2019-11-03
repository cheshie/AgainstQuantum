import os

"""
* FrodoKEM: Learning with Errors Key Encapsulation
*
* Abstract: configuration file
"""

# Definition of operating system

# define OS_WIN       1
# define OS_NIX       2

# if defined(WINDOWS)            // Microsoft Windows
# define OS_TARGET OS_WIN
# elif defined(NIX)              // Unix-like operative systems
# define OS_TARGET OS_NIX
# else
# error -- "Unsupported OS"
# endif


# Definition of compiler

# define COMPILER_VC      1
# define COMPILER_GCC     2
# define COMPILER_CLANG   3

# if defined(_MSC_VER)           // Microsoft Visual C compiler
# define COMPILER COMPILER_VC
# elif defined(__GNUC__)         // GNU GCC compiler
# define COMPILER COMPILER_GCC
# elif defined(__clang__)        // Clang compiler
# define COMPILER COMPILER_CLANG
# else
# error -- "Unsupported COMPILER"
# endif


# Definition of the targeted architecture and basic data types

# define TARGET_AMD64        1
# define TARGET_x86          2
# define TARGET_ARM          3

# if defined(_AMD64_)
# define TARGET TARGET_AMD64
# elif defined(_X86_)
# define TARGET TARGET_x86
# elif defined(_ARM_)
# define TARGET TARGET_ARM
# else
# error -- "Unsupported ARCHITECTURE"
# endif


# topic: https://docs.microsoft.com/en-us/cpp/cpp/align-cpp?view=vs-2019
# question: are these __declspec, align and __attribute__ c - specific?
if 'nt' in os.name:
    def ALIGN_HEADER(N):
        return N #__declspec(align(N))
    #
    def ALIGN_FOOTER(N):
        return N
else:
    def ALIGN_HEADER(N):
        return N
    def ALIGN_FOOTER(N):
        return N #__attribute__((aligned(N)))


# Selecting implementation: fast, generic or reference
# if defined(_FAST_)    // The "fast" implementation requires support for AVX2 and AES_NI instructions
# define USE_AVX2
# define AES_ENABLE_NI
# define USE_FAST
# elif defined(_FAST_GENERIC_)
# define USE_FAST_GENERIC
# elif defined(_REFERENCE_)
# define USE_REFERENCE
# else
# error -- unsupported implementation
# endif


# Defining method for generating matrix A
# if defined(_AES128_FOR_A_)
# define USE_AES128_FOR_A
# elif defined(_SHAKE128_FOR_A_)
# define USE_SHAKE128_FOR_A
# else
##error -- missing method for generating matrix A
# endif

# Selecting use of OpenSSL 's AES functions
# if defined(_USE_OPENSSL_)
# define USE_OPENSSL
# endif


# Configuration for endianness

# if defined(__BYTE_ORDER__) && (__BYTE_ORDER__ == __ORDER_BIG_ENDIAN__)
#def LE_TO_UINT16(n):
#    return ushort(n) & 0xFF << ushort(8) | ushort(n) & 0xFF00 >> ushort(8)

#def UINT16_TO_LE(n):
#    return ushort(n) & 0xFF << ushort(8) | ushort(n) & 0xFF00 >> ushort(8)

# elif (TARGET == TARGET_x86 || TARGET == TARGET_AMD64) || (defined(__BYTE_ORDER__) && (__BYTE_ORDER__ == __ORDER_LITTLE_ENDIAN__))
def LE_TO_UINT16(n):
    return n
def UINT16_TO_LE(n):
    return n

# else
# define LE_TO_UINT16(n) (((uint8_t *) &(n))[0] | (((uint8_t *) &(n))[1] << 8))
# static inline uint16_t UINT16_TO_LE(const uint16_t x) { uint16_t y; uint8_t * z = (uint8_t *) & y; z[0] = x & 0xFF; z[1] = x >> 8; return y;}
# endif

# endif

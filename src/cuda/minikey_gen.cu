#include <stdint.h>

__device__ __constant__ char kAlphabet[59] = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz";

extern "C" __global__ void minikey_gen(char* out, size_t count, const uint8_t* start, unsigned long long base){
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if(idx >= count) return;
    uint8_t digits[22];
    unsigned long long carry = base + static_cast<unsigned long long>(idx);
    for(int i=21;i>=0;--i){
        unsigned long long v = static_cast<unsigned long long>(start[i]) + (carry % 58ULL);
        carry /= 58ULL;
        if(v >= 58ULL){
            v -= 58ULL;
            carry++;
        }
        digits[i] = static_cast<uint8_t>(v);
    }
    for(int i=0;i<22;i++){
        out[idx*22 + i] = kAlphabet[digits[i]];
    }
}


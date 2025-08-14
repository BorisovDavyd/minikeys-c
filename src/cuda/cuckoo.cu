#include <stdint.h>
// Placeholder for cuckoo hash index
extern "C" __global__ void cuckoo_lookup(const uint8_t* h160, size_t count, uint8_t* results){
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if(idx<count) results[idx]=0; // no match
}

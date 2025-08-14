#include <stdint.h>

// Linear search index lookup on GPU
extern "C" __global__ void cuckoo_lookup(const uint8_t* h160, size_t count,
                                          const uint8_t* table, size_t table_count,
                                          uint8_t* results){
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if(idx>=count) return;
    const uint8_t* target = h160 + idx*20;
    for(size_t i=0;i<table_count;i++){
        const uint8_t* entry = table + i*20;
        bool match = true;
        #pragma unroll
        for(int j=0;j<20;j++){
            if(entry[j]!=target[j]){ match=false; break; }
        }
        if(match){ results[idx]=1; return; }
    }
    results[idx]=0;
}

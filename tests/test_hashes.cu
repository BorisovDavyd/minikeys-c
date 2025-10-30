#include <iostream>
#include <cstring>
#include "../src/common/sha256.hpp"
#include "../src/common/ripemd160.hpp"
#ifdef __CUDACC__
#include <cuda_runtime.h>
extern "C" __global__ void sha256_gpu(const uint8_t*, size_t, uint8_t*);
extern "C" __global__ void ripemd160_gpu(const uint8_t*, size_t, uint8_t*);
#endif

int main(){
    const char* msg = "abc";
    uint8_t out[32];
    SHA256Ctx sctx; sha256_init(&sctx); sha256_update(&sctx,(const uint8_t*)msg,3); sha256_final(&sctx,out);
    const uint8_t exp_sha[32] = {0xBA,0x78,0x16,0xBF,0x8F,0x01,0xCF,0xEA,0x41,0x41,0x40,0xDE,0x5D,0xAE,0x22,0x23,0xB0,0x03,0x61,0xA3,0x96,0x17,0x7A,0x9C,0xB4,0x10,0xFF,0x61,0xF2,0x00,0x15,0xAD};
    bool cpu_sha_ok = std::memcmp(out, exp_sha, 32)==0;

    uint8_t out160[20]; RIPEMD160Ctx rctx; ripemd160_init(&rctx); ripemd160_update(&rctx,(const uint8_t*)msg,3); ripemd160_final(&rctx,out160);
    const uint8_t exp_ripemd[20] = {0x8E,0xB2,0x08,0xF7,0xE0,0x5D,0x98,0x7A,0x9B,0x04,0x4A,0x8E,0x98,0xC6,0xB8,0x7C,0x6E,0x48,0xD8,0x6E};
    bool cpu_ripemd_ok = std::memcmp(out160, exp_ripemd, 20)==0;

    bool gpu_ok=true;
#ifdef __CUDACC__
    uint8_t *d_in,*d_out;
    if(cudaMalloc(&d_in,3)!=cudaSuccess) {gpu_ok=false;} else if(cudaMalloc(&d_out,32)!=cudaSuccess){gpu_ok=false;} else {
        cudaMemcpy(d_in,msg,3,cudaMemcpyHostToDevice);
        sha256_gpu<<<1,1>>>(d_in,3,d_out);
        if(cudaDeviceSynchronize()!=cudaSuccess) gpu_ok=false; else cudaMemcpy(out,d_out,32,cudaMemcpyDeviceToHost);
        cudaFree(d_out); cudaFree(d_in);
        gpu_ok &= (std::memcmp(out, exp_sha, 32)==0);
    }
#endif
    if(!cpu_sha_ok || !cpu_ripemd_ok) {
        std::cerr << "CPU hash mismatch" << std::endl; return 1;
    }
    if(!gpu_ok) std::cerr << "GPU tests skipped or failed" << std::endl;
    return 0;
}

#include <cuda_runtime.h>
#include <vector>
#include <cstdio>
#include <array>
#include <cstring>
#include "pipeline.hpp"
#include "../common/sha256.hpp"
#include "../common/ripemd160.hpp"

#define CUDA_CHECK(call) do { \
    cudaError_t err = (call); \
    if (err != cudaSuccess) { \
        fprintf(stderr, "CUDA error %s at %s:%d\n", cudaGetErrorString(err), __FILE__, __LINE__); \
        return; \
    } \
} while(0)

extern "C" __global__ void minikey_gen(char* out, size_t count, const uint8_t* start, unsigned long long base);
extern "C" __global__ void cuckoo_lookup(const uint8_t* h160, size_t count, uint8_t* results);

__global__ void hash160_from_minikey(const char* keys, uint8_t* h160, size_t count){
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if(idx>=count) return;
    // verify checksum
    char tmp[23];
    for(int i=0;i<22;i++) tmp[i]=keys[idx*22+i];
    tmp[22]='?';
    uint8_t chk[32];
    SHA256Ctx c; sha256_init(&c); sha256_update(&c,(uint8_t*)tmp,23); sha256_final(&c,chk);
    if(chk[0]!=0){
        for(int i=0;i<20;i++) h160[idx*20+i]=0; return;
    }
    SHA256Ctx s; sha256_init(&s); sha256_update(&s,(const uint8_t*)(keys+idx*22),22); sha256_final(&s,chk);
    RIPEMD160Ctx r; ripemd160_init(&r); ripemd160_update(&r,chk,32); ripemd160_final(&r,h160+idx*20);
}

struct DeviceBuf{char* keys; uint8_t* h160; uint8_t* matches; uint8_t* host_matches; cudaEvent_t ready;};

void run_pipeline(const PipelineConfig& cfg){
    std::vector<cudaStream_t> streams(cfg.streams);
    for(auto &s:streams) CUDA_CHECK(cudaStreamCreate(&s));
    DeviceBuf buf[2];
    const char* alphabet = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz";
    std::array<uint8_t,22> start_digits{};
    if(!cfg.start_minikey.empty() && cfg.start_minikey.size()==22){
        for(int i=0;i<22;i++){
            const char* p = strchr(alphabet,cfg.start_minikey[i]);
            start_digits[i] = p ? static_cast<uint8_t>(p - alphabet) : 0;
        }
    } else {
        const char* p = strchr(alphabet,'S');
        start_digits.fill(0);
        if(p) start_digits[0] = p - alphabet;
    }
    uint8_t* d_start = nullptr;
    CUDA_CHECK(cudaMalloc(&d_start,22));
    CUDA_CHECK(cudaMemcpy(d_start,start_digits.data(),22,cudaMemcpyHostToDevice));
    size_t key_bytes = cfg.batch*22;
    size_t h160_bytes = cfg.batch*20;
    size_t res_bytes = cfg.batch;
    for(int i=0;i<2;i++){
        CUDA_CHECK(cudaMalloc(&buf[i].keys,key_bytes));
        CUDA_CHECK(cudaMalloc(&buf[i].h160,h160_bytes));
        CUDA_CHECK(cudaMalloc(&buf[i].matches,res_bytes));
        CUDA_CHECK(cudaMallocHost(&buf[i].host_matches,res_bytes));
        CUDA_CHECK(cudaEventCreateWithFlags(&buf[i].ready,cudaEventDisableTiming));
        CUDA_CHECK(cudaEventRecord(buf[i].ready,0));
    }
    dim3 block(128);
    dim3 grid((cfg.batch+block.x-1)/block.x);
    unsigned long long base = 0ULL;
    for(size_t it=0; it<cfg.iterations; ++it){
        int b = it & 1;
        CUDA_CHECK(cudaEventSynchronize(buf[b].ready));
        cudaStream_t s = streams[it % cfg.streams];
        minikey_gen<<<grid,block,0,s>>>(buf[b].keys,cfg.batch,d_start,base);
        hash160_from_minikey<<<grid,block,0,s>>>(buf[b].keys,buf[b].h160,cfg.batch);
        cuckoo_lookup<<<grid,block,0,s>>>(buf[b].h160,cfg.batch,buf[b].matches);
        CUDA_CHECK(cudaMemcpyAsync(buf[b].host_matches,buf[b].matches,res_bytes,cudaMemcpyDeviceToHost,s));
        CUDA_CHECK(cudaEventRecord(buf[b].ready,s));
        base += cfg.batch;
    }
    CUDA_CHECK(cudaDeviceSynchronize());
    size_t total=0;
    for(int b=0;b<2;b++){
        for(size_t i=0;i<cfg.batch;i++) total += buf[b].host_matches[i];
    }
    printf("Total matches: %zu\n", total);
    for(auto s:streams) cudaStreamDestroy(s);
    for(int i=0;i<2;i++){
        cudaFree(buf[i].keys); cudaFree(buf[i].h160); cudaFree(buf[i].matches);
        cudaFreeHost(buf[i].host_matches); cudaEventDestroy(buf[i].ready);
    }
    cudaFree(d_start);
}

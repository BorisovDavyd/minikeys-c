#include "../common/sha256.hpp"
extern "C" __global__ void sha256_gpu(const uint8_t* in, size_t len, uint8_t* out){
    SHA256Ctx ctx; sha256_init(&ctx); sha256_update(&ctx,in,len); sha256_final(&ctx,out);
}

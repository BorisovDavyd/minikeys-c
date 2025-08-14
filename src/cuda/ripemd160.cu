#include "../common/ripemd160.hpp"
extern "C" __global__ void ripemd160_gpu(const uint8_t* in, size_t len, uint8_t* out){
    RIPEMD160Ctx ctx; ripemd160_init(&ctx); ripemd160_update(&ctx,in,len); ripemd160_final(&ctx,out);
}

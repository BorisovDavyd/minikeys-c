#pragma once
#include <cstdint>
#include <cstddef>
#include <cstring>

#ifndef HD
#ifdef __CUDACC__
#define HD __host__ __device__
#else
#define HD
#endif
#endif

struct RIPEMD160Ctx {
    uint32_t h[5];
    uint8_t  buf[64];
    uint64_t bitlen;
    uint32_t buflen;
};

static HD uint32_t rol(uint32_t x, uint32_t n){return (x<<n)|(x>>(32-n));}

static HD inline void ripemd160_transform(RIPEMD160Ctx* ctx, const uint8_t block[64]){
    const uint32_t K[5] = {0x00000000,0x5A827999,0x6ED9EBA1,0x8F1BBCDC,0xA953FD4E};
    const uint32_t KK[5]= {0x50A28BE6,0x5C4DD124,0x6D703EF3,0x7A6D76E9,0x00000000};
    const uint32_t r[80] = {
     0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,
     7,4,13,1,10,6,15,3,12,0,9,5,2,14,11,8,
     3,10,14,4,9,15,8,1,2,7,0,6,13,11,5,12,
     1,9,11,10,0,8,12,4,13,3,7,15,14,5,6,2,
     4,0,5,9,7,12,2,10,14,1,3,8,11,6,15,13
    };
    const uint32_t rr[80] = {
     5,14,7,0,9,2,11,4,13,6,15,8,1,10,3,12,
     6,11,3,7,0,13,5,10,14,15,8,12,4,9,1,2,
     15,5,1,3,7,14,6,9,11,8,12,2,10,0,4,13,
     8,6,4,1,3,11,15,0,5,12,2,13,9,7,10,14,
     12,15,10,4,1,5,8,7,6,2,13,14,0,3,9,11
    };
    const uint32_t s[80] = {
     11,14,15,12,5,8,7,9,11,13,14,15,6,7,9,8,
     7,6,8,13,11,9,7,15,7,12,15,9,11,7,13,12,
     11,13,6,7,14,9,13,15,14,8,13,6,5,12,7,5,
     11,12,14,15,14,15,9,8,9,14,5,6,8,6,5,12,
     9,15,5,11,6,8,13,12,5,12,13,14,11,8,5,6
    };
    const uint32_t ss[80] = {
     8,9,9,11,13,15,15,5,7,7,8,11,14,14,12,6,
     9,13,15,7,12,8,9,11,7,7,12,7,6,15,13,11,
     9,7,15,11,8,6,6,14,12,13,5,14,13,13,7,5,
     15,5,8,11,14,14,6,14,6,9,12,9,12,5,15,8,
     8,5,12,9,12,5,14,6,8,13,6,5,15,13,11,11
    };
    uint32_t X[16];
    for(int i=0;i<16;i++){
        X[i] = (uint32_t)block[i*4] | ((uint32_t)block[i*4+1]<<8) | ((uint32_t)block[i*4+2]<<16) | ((uint32_t)block[i*4+3]<<24);
    }
    uint32_t a=ctx->h[0],b=ctx->h[1],c=ctx->h[2],d=ctx->h[3],e=ctx->h[4];
    uint32_t A=ctx->h[0],B=ctx->h[1],C=ctx->h[2],D=ctx->h[3],E=ctx->h[4];
    for(int i=0;i<80;i++){
        uint32_t T = rol(a + (b^c^d) + X[r[i]] + K[i/16], s[i]) + e;
        a=e;e=d;d=rol(c,10);c=b;b=T;
        T = rol(A + (B^(C|~D)) + X[rr[i]] + KK[i/16], ss[i]) + E;
        A=E;E=D;D=rol(C,10);C=B;B=T;
    }
    uint32_t tmp = ctx->h[1] + c + D;
    ctx->h[1] = ctx->h[2] + d + E;
    ctx->h[2] = ctx->h[3] + e + A;
    ctx->h[3] = ctx->h[4] + a + B;
    ctx->h[4] = ctx->h[0] + b + C;
    ctx->h[0] = tmp;
}

static HD inline void ripemd160_init(RIPEMD160Ctx* ctx){
    ctx->h[0]=0x67452301;ctx->h[1]=0xefcdab89;ctx->h[2]=0x98badcfe;ctx->h[3]=0x10325476;ctx->h[4]=0xc3d2e1f0;
    ctx->bitlen=0;ctx->buflen=0;
}

static HD inline void ripemd160_update(RIPEMD160Ctx* ctx, const uint8_t* data, size_t len){
    for(size_t i=0;i<len;i++){
        ctx->buf[ctx->buflen++] = data[i];
        if(ctx->buflen==64){
            ripemd160_transform(ctx, ctx->buf);
            ctx->bitlen += 512;
            ctx->buflen=0;
        }
    }
}

static HD inline void ripemd160_final(RIPEMD160Ctx* ctx, uint8_t hash[20]){
    uint32_t i = ctx->buflen;
    ctx->buf[i++] = 0x80;
    if(i>56){
        while(i<64) ctx->buf[i++]=0;
        ripemd160_transform(ctx, ctx->buf);
        i=0;
    }
    while(i<56) ctx->buf[i++]=0;
    ctx->bitlen += ctx->buflen*8;
    for(int j=0;j<8;j++) ctx->buf[56+j] = (ctx->bitlen >> (8*j)) & 0xff;
    ripemd160_transform(ctx, ctx->buf);
    for(int j=0;j<5;j++){
        hash[j*4+0] = ctx->h[j] & 0xff;
        hash[j*4+1] = (ctx->h[j] >> 8) & 0xff;
        hash[j*4+2] = (ctx->h[j] >> 16) & 0xff;
        hash[j*4+3] = (ctx->h[j] >> 24) & 0xff;
    }
}

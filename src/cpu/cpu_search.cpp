#include <array>
#include <string>
#include <vector>
#include <unordered_set>
#include <cstring>
#include <iostream>
#include "base58check.hpp"
#include "secp256k1_openssl.hpp"
#include "../common/sha256.hpp"
#include "../common/ripemd160.hpp"

static const char* ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz";

static bool valid_minikey(const char* mk){
    uint8_t chk[32];
    char tmp[23];
    std::memcpy(tmp,mk,22); tmp[22]='?';
    SHA256Ctx ctx; sha256_init(&ctx); sha256_update(&ctx,(uint8_t*)tmp,23); sha256_final(&ctx,chk);
    return chk[0]==0;
}

static void increment(std::array<uint8_t,22>& digits){
    for(int i=21;i>=0;--i){
        if(++digits[i]<58) break; digits[i]=0;
    }
}

size_t cpu_search(const std::vector<std::array<uint8_t,20>>& hashes, const std::string& start, size_t count){
    std::unordered_set<std::string> set; set.reserve(hashes.size());
    for(const auto& h:hashes) set.emplace((const char*)h.data(),20);
    std::array<uint8_t,22> digits{};
    if(!start.empty() && start.size()==22){
        for(int i=0;i<22;i++){ const char* p=strchr(ALPHABET,start[i]); digits[i]=p? (uint8_t)(p-ALPHABET):0; }
    } else {
        const char* p=strchr(ALPHABET,'S'); digits.fill(0); if(p) digits[0]=p-ALPHABET;
    }
    std::array<char,23> mk; mk[22]='\0';
    size_t matches=0;
    for(size_t n=0;n<count;n++){
        for(int i=0;i<22;i++) mk[i]=ALPHABET[digits[i]];
        if(valid_minikey(mk.data())){
            uint8_t priv[32]; SHA256Ctx s; sha256_init(&s); sha256_update(&s,(uint8_t*)mk.data(),22); sha256_final(&s,priv);
            uint8_t pub[33]; if(!secp256k1_pubkey(priv,pub)) { increment(digits); continue; }
            uint8_t hash[32]; sha256_init(&s); sha256_update(&s,pub,33); sha256_final(&s,hash);
            uint8_t h160[20]; RIPEMD160Ctx r; ripemd160_init(&r); ripemd160_update(&r,hash,32); ripemd160_final(&r,h160);
            if(set.find(std::string((char*)h160,20))!=set.end()) matches++;
        }
        increment(digits);
    }
    return matches;
}

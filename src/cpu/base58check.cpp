#include <algorithm>
#include <vector>
#include <string>
#include <fstream>
#include <array>
#include <iostream>
#include "../common/sha256.hpp"
#include "../common/ripemd160.hpp"

static const char* ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz";
static int8_t MAP[128];
struct MapInit{MapInit(){std::fill(std::begin(MAP), std::end(MAP), -1);for(int i=0;i<58;i++)MAP[(int)ALPHABET[i]]=i;}};static MapInit init;

std::vector<uint8_t> base58check_decode(const std::string& str){
    std::vector<uint8_t> bytes;
    for(char c: str){
        if(c & 0x80 || MAP[(int)c]==-1) return {};
        int carry = MAP[(int)c];
        for(size_t i=0;i<bytes.size();++i){
            int v = bytes[bytes.size()-1-i]*58 + carry;
            bytes[bytes.size()-1-i] = v & 0xff;
            carry = v >> 8;
        }
        while(carry){
            bytes.insert(bytes.begin(), carry & 0xff);
            carry >>= 8;
        }
    }
    // count leading '1'
    size_t nZeros = 0; for(char c: str){ if(c=='1') nZeros++; else break; }
    bytes.insert(bytes.begin(), nZeros, 0);
    if(bytes.size()<4) return {};
    std::vector<uint8_t> out(bytes.begin(), bytes.end()-4);
    uint8_t chk1[32];
    SHA256Ctx ctx; sha256_init(&ctx); sha256_update(&ctx, out.data(), out.size()); sha256_final(&ctx, chk1);
    sha256_init(&ctx); sha256_update(&ctx, chk1, 32); sha256_final(&ctx, chk1);
    if(!std::equal(chk1, chk1+4, bytes.end()-4)) return {};
    return out;
}

std::vector<std::array<uint8_t,20>> load_hash160(const std::string& path){
    std::ifstream in(path); std::string line; std::vector<std::array<uint8_t,20>> hashes;
    while(std::getline(in,line)){
        if(line.empty()) continue;
        auto decoded = base58check_decode(line);
        if(decoded.size()==21 && decoded[0]==0x00){
            std::array<uint8_t,20> h; std::copy(decoded.begin()+1, decoded.begin()+21, h.begin());
            hashes.push_back(h);
        } else {
            std::cerr << "Invalid address: " << line << "\n";
        }
    }
    return hashes;
}

#include <iostream>
#include <vector>
#include <array>
#include "../src/cpu/base58check.hpp"
#include "../src/cpu/cpu_search.hpp"

int main(){
    // Known mini-key and address from Bitcoin Wiki
    std::string minikey = "SzavMBLoXU6kDrqtUVmffv";
    std::vector<std::array<uint8_t,20>> hashes;
    // Address 19GuvDvMMUZ8vq84wT79fvnvhMd5MnfTkR
    std::array<uint8_t,20> h = {0x5a,0xc3,0x6b,0x4a,0xff,0x94,0x5d,0xa3,0x0c,0x16,0xbf,0x6c,0x25,0xdb,0xac,0x43,0x46,0x64,0xda,0x8c};
    hashes.push_back(h);
    size_t matches = cpu_search(hashes, minikey, 1);
    if(matches!=1){ std::cerr << "minikey search failed" << std::endl; return 1; }
    return 0;
}

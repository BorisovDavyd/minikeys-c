#include <array>
#include <iostream>
#include <string>
#include <vector>

#include "cpu/base58check.hpp"
#include "cpu/preload_index.hpp"

int main(int argc, char** argv) {
    std::cout << "WARNING: mini-key format is deprecated and insecure.\n";
    std::cout << "Use for educational purposes only.\n";

    std::string addr_path;
    for (int i = 1; i < argc; ++i) {
        std::string arg = argv[i];
        if (arg == "--addresses" && i + 1 < argc) {
            addr_path = argv[++i];
        }
    }

    if (addr_path.empty()) {
        std::cerr << "Missing --addresses argument\n";
        return 1;
    }

    auto hashes = load_hash160(addr_path);
    std::cout << "Loaded " << hashes.size() << " addresses\n";
    preload_index(hashes);

    std::cout << "GPU pipeline not yet implemented.\n";
    return 0;
}

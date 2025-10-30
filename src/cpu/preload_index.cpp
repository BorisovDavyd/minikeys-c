#include <vector>
#include <array>
#include <string>
#include <iostream>
#include <cuda_runtime.h>

// Upload HASH160 list to GPU and return device pointer
uint8_t* preload_index(const std::vector<std::array<uint8_t,20>>& hashes) {
    std::cout << "Preloading " << hashes.size() << " HASH160 entries\n";
    if(hashes.empty()) return nullptr;
    uint8_t* d_table = nullptr;
    size_t bytes = hashes.size()*20;
    cudaError_t err = cudaMalloc(&d_table, bytes);
    if(err != cudaSuccess){
        std::cerr << "cudaMalloc failed: " << cudaGetErrorString(err) << "\n";
        return nullptr;
    }
    err = cudaMemcpy(d_table, hashes.data()->data(), bytes, cudaMemcpyHostToDevice);
    if(err != cudaSuccess){
        std::cerr << "cudaMemcpy failed: " << cudaGetErrorString(err) << "\n";
        cudaFree(d_table);
        return nullptr;
    }
    return d_table;
}

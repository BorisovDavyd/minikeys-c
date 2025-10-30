#pragma once
#include <cstddef>
#include <cstdint>
#include <string>
#include <vector>
#include <array>

struct PipelineConfig {
    size_t batch;
    int streams;
    size_t iterations;
    std::string start_minikey;
    const uint8_t* hashes;
    size_t hash_count;
    const std::vector<std::array<uint8_t,20>>* hashes_host;
};

void run_pipeline(const PipelineConfig& cfg);

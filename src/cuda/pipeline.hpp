#pragma once
#include <cstddef>
#include <cstdint>
#include <string>

struct PipelineConfig {
    size_t batch;
    int streams;
    size_t iterations;
    std::string start_minikey;
    const uint8_t* hashes;
    size_t hash_count;
};

void run_pipeline(const PipelineConfig& cfg);

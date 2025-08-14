#pragma once
#include <cstddef>
#include <string>

struct PipelineConfig {
    size_t batch;
    int streams;
    size_t iterations;
    std::string start_minikey;
};

void run_pipeline(const PipelineConfig& cfg);

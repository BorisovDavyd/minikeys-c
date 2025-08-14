#pragma once
#include <cstddef>

struct PipelineConfig {
    size_t batch;
    int streams;
    size_t iterations;
};

void run_pipeline(const PipelineConfig& cfg);

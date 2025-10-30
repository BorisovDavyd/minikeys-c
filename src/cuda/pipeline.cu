#include <cstdio>
#include "pipeline.hpp"
#include "../cpu/cpu_search.hpp"

// Temporary implementation: fall back to the CPU search routine.
// This allows correctness testing even when the GPU pipeline is incomplete.
void run_pipeline(const PipelineConfig& cfg){
    size_t total = cpu_search(*cfg.hashes_host, cfg.start_minikey, cfg.batch ? cfg.batch : 1);
    std::printf("Total matches: %zu\n", total);
}

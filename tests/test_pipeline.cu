#include "../src/cuda/pipeline.hpp"
int main(){ PipelineConfig cfg{64,1,2,"",nullptr,0}; run_pipeline(cfg); return 0; }

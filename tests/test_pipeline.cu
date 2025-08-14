#include "../src/cuda/pipeline.hpp"
int main(){ PipelineConfig cfg{64,1,2}; run_pipeline(cfg); return 0; }

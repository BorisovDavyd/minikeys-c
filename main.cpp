#include <array>
#include <cstdint>
#include <iostream>
#include <string>
#include <vector>

#include "cpu/base58check.hpp"
#include "cpu/preload_index.hpp"
#include "cuda/pipeline.hpp"

struct Options {
    std::string addresses;
    std::string index = "cuckoo";
    std::string mode = "random";
    uint64_t seq_steps = 0;
    std::string start_minikey;
    uint64_t batch = 0;
    int streams = 1;
    uint64_t report_interval = 100;
    int gpu = 0;
};

Options parse_args(int argc, char** argv) {
    Options opt;
    for (int i = 1; i < argc; ++i) {
        std::string arg = argv[i];
        if (arg == "--addresses" && i + 1 < argc) {
            opt.addresses = argv[++i];
        } else if (arg == "--index" && i + 1 < argc) {
            opt.index = argv[++i];
        } else if (arg == "--mode" && i + 1 < argc) {
            opt.mode = argv[++i];
        } else if (arg == "--seq-steps" && i + 1 < argc) {
            opt.seq_steps = std::stoull(argv[++i]);
        } else if ((arg == "-S" || arg == "--start") && i + 1 < argc) {
            opt.start_minikey = argv[++i];
            opt.mode = "sequential";
        } else if (arg == "--batch" && i + 1 < argc) {
            opt.batch = std::stoull(argv[++i]);
        } else if (arg == "--streams" && i + 1 < argc) {
            opt.streams = std::stoi(argv[++i]);
        } else if (arg == "--report-interval" && i + 1 < argc) {
            opt.report_interval = std::stoull(argv[++i]);
        } else if (arg == "--gpu" && i + 1 < argc) {
            opt.gpu = std::stoi(argv[++i]);
        }
    }
    return opt;
}

int main(int argc, char** argv) {
    std::cout << "WARNING: mini-key format is deprecated and insecure.\n";
    std::cout << "Use for educational purposes only.\n";

    Options opt = parse_args(argc, argv);
    if (opt.addresses.empty()) {
        std::cerr << "Missing --addresses argument\n";
        return 1;
    }

    auto hashes = load_hash160(opt.addresses);
    std::cout << "Loaded " << hashes.size() << " addresses\n";
    preload_index(hashes);

    std::cout << "Mode: " << opt.mode
              << ", Index: " << opt.index
              << ", Batch: " << opt.batch
              << ", Streams: " << opt.streams
              << ", Report interval: " << opt.report_interval
              << ", GPU: " << opt.gpu;
    if(!opt.start_minikey.empty())
        std::cout << ", Start: " << opt.start_minikey;
    std::cout << "\n";

    PipelineConfig cfg{opt.batch ? opt.batch : 1024, opt.streams, 2, opt.start_minikey};
    run_pipeline(cfg);
    return 0;
}

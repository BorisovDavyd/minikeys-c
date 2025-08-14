cmake_minimum_required(VERSION 3.18)
project(minikey_research LANGUAGES C CXX CUDA)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CUDA_STANDARD 17)

set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CUDA_STANDARD_REQUIRED ON)

# Enable fast math for CUDA
set(CMAKE_CUDA_FLAGS "${CMAKE_CUDA_FLAGS} -O3 --use_fast_math")

add_library(cpu
    src/cpu/base58check.cpp
    src/cpu/preload_index.cpp
)

add_library(cuda
    src/cuda/sha256.cu
    src/cuda/ripemd160.cu
    src/cuda/minikey_gen.cu
    src/cuda/secp256k1_gpu.cu
    src/cuda/cuckoo.cu
    src/cuda/bloom.cu
    src/cuda/pipeline.cu
)

target_include_directories(cpu PUBLIC src)
target_include_directories(cuda PUBLIC src)

add_executable(minikey-research main.cpp)

target_link_libraries(minikey-research PRIVATE cpu cuda)

enable_testing()
add_executable(test_hashes tests/test_hashes.cu)
target_link_libraries(test_hashes PRIVATE cpu cuda)
add_test(NAME hashes COMMAND test_hashes)

add_executable(test_pipeline tests/test_pipeline.cu)
target_link_libraries(test_pipeline PRIVATE cpu cuda)
add_test(NAME pipeline COMMAND test_pipeline)

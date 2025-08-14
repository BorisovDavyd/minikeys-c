# Simple Makefile for minikey-research (CPU + CUDA)

CUDA_PATH ?= /usr/local/cuda
NVCC      ?= $(CUDA_PATH)/bin/nvcc
CXXFLAGS  := -O3 --use_fast_math
INCLUDES  := -I./src -I./extern/bitcrack -I./extern/cgbn

CUDA_SRCS := src/cuda/sha256.cu src/cuda/ripemd160.cu src/cuda/minikey_gen.cu src/cuda/secp256k1_gpu.cu src/cuda/cuckoo.cu src/cuda/bloom.cu src/cuda/pipeline.cu
CPU_SRCS  := main.cpp src/cpu/base58check.cpp src/cpu/preload_index.cpp

OBJS := $(CUDA_SRCS:.cu=.o) $(CPU_SRCS:.cpp=.o)

TARGET := minikey-research

all: $(TARGET)

$(TARGET): $(OBJS)
	$(NVCC) $(CXXFLAGS) $(OBJS) -o $@

%.o: %.cu
	$(NVCC) $(CXXFLAGS) $(INCLUDES) -c $< -o $@

%.o: %.cpp
	$(NVCC) $(CXXFLAGS) $(INCLUDES) -c $< -o $@

clean:
	rm -f $(OBJS) $(TARGET) tests/test_hashes

# Build and run hash self-tests
.PHONY: test

test: tests/test_hashes
	./tests/test_hashes

tests/test_hashes: tests/test_hashes.cu $(OBJS)
	$(NVCC) $(CXXFLAGS) $(INCLUDES) tests/test_hashes.cu -o $@

.PHONY: all clean

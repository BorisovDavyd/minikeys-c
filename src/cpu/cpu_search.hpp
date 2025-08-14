#pragma once
#include <cstddef>
#include <array>
#include <vector>
#include <string>

size_t cpu_search(const std::vector<std::array<uint8_t,20>>& hashes, const std::string& start, size_t count);

#pragma once
#include <array>
#include <cstdint>
#include <string>
#include <vector>

std::vector<std::array<uint8_t,20>> load_hash160(const std::string& path);

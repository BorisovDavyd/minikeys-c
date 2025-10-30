#pragma once
#include <cstdint>

bool secp256k1_pubkey(const uint8_t priv[32], uint8_t pub[33]);

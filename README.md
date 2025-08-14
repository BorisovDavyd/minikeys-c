# minikey-research

Educational GPU-accelerated utility for exploring Bitcoin mini private keys.

> **Warning:** The mini-key format is obsolete and insecure. This project is
> for educational research only.

## Build

Requires a CUDA 12 toolkit and a C++17 compiler.

```bash
make
```

The default target builds the `minikey-research` binary. To run self-tests:

```bash
make test
```

Clean build artifacts with:

```bash
make clean
```

If the build fails with `nvcc: command not found`, install the CUDA toolkit
and ensure `nvcc` is in your `PATH`.

## Usage

Run `minikey-research` with the path to a file containing newline-separated
P2PKH addresses (each starting with `1`):

```bash
./minikey-research --addresses addresses.txt [options]
```

### Options

| Argument | Description |
|----------|-------------|
| `--addresses <file>` | Path to the input address list. |
| `--index <cuckoo|bloom>` | Select GPU index type (default: `cuckoo`). |
| `--mode <random|mixed>` | Mini-key generation mode (default: `random`). |
| `--seq-steps <N>` | Step size for `mixed` mode sequences. |
| `--batch <N>` | Keys processed per GPU batch. |
| `--streams <N>` | Number of CUDA streams to overlap pipeline stages. |
| `--report-interval <N>` | Print progress every N batches. |
| `--gpu <id>` | GPU device to use (default: 0). |

### Examples

Run in purely random generation mode, reporting progress every 100 batches of
two million keys:

```bash
./minikey-research --addresses addresses.txt --mode random --batch 2000000 \
  --report-interval 100
```

Start from a random seed but walk the keyspace deterministically using a step
size, overlapping stages with two CUDA streams:

```bash
./minikey-research --addresses addresses.txt --mode mixed --seq-steps 12121212 \
  --batch 3000000 --streams 2 --report-interval 1
```

To experiment with an alternative Bloom filter index sized for 64 million
entries with 8 hash functions:

```bash
./minikey-research --addresses addresses.txt --index bloom --batch 500000 \
  --mode random
```

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

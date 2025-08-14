extern "C" __global__ void minikey_gen(char* out, size_t count){
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if(idx < count){
        out[idx*22] = 'S';
        for(int i=1;i<22;i++) out[idx*22+i] = '1';
    }
}

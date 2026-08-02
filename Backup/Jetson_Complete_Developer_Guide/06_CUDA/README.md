# 06. CUDA Programming

## 1. CUDA 개요

CUDA(Compute Unified Device Architecture)는 NVIDIA GPU에서 병렬 컴퓨팅을 가능하게 하는 플랫폼입니다.

| 항목 | 현재 환경 |
|------|----------|
| CUDA 버전 | 10.2 |
| GPU 아키텍처 | Volta (SM 7.2) |
| CUDA 코어 | 384개 |
| 컴파일러 | nvcc |

### CPU vs GPU 병렬 처리

```
CPU (6코어):     │ Task1 │ Task2 │ Task3 │ Task4 │ Task5 │ Task6 │
                 └───────┴───────┴───────┴───────┴───────┴───────┘
                 순차/소수 병렬, 복잡한 제어에 강함

GPU (384코어):    │T1│T2│T3│...│T384│
                  └──┴──┴──┴───┴────┘
                  단순 연산을 대량 병렬로 처리
```

---

## 2. CUDA 프로그래밍 모델

### 기본 구조

```cpp
// 1. Host (CPU) 코드
// 2. Device (GPU) 코드 — __global__ 함수 (커널)
// 3. Host→Device 메모리 복사
// 4. 커널 실행
// 5. Device→Host 메모리 복사
```

### Hello, CUDA!

```cpp
// hello_cuda.cu
#include <stdio.h>

// GPU에서 실행될 커널
__global__ void hello_from_gpu() {
    printf("Hello from GPU block %d, thread %d!\n",
           blockIdx.x, threadIdx.x);
}

int main() {
    printf("Hello from CPU!\n");

    // 1개의 블록, 4개의 스레드로 커널 실행
    hello_from_gpu<<<1, 4>>>();
    cudaDeviceSynchronize();  // GPU 작업 완료 대기

    return 0;
}
```

```bash
# 컴파일 및 실행
nvcc -o hello_cuda hello_cuda.cu
./hello_cuda
# 출력:
# Hello from CPU!
# Hello from GPU block 0, thread 0!
# Hello from GPU block 0, thread 1!
# Hello from GPU block 0, thread 2!
# Hello from GPU block 0, thread 3!
```

---

## 3. 벡터 덧셈 (Vector Add) — 실습

```cpp
// vector_add.cu
#include <stdio.h>
#include <cuda_runtime.h>

#define N 1000000  // 100만 개 요소

// GPU 커널: 두 벡터를 더함
__global__ void vector_add(float *a, float *b, float *c, int n) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;

    if (idx < n) {
        c[idx] = a[idx] + b[idx];
    }
}

int main() {
    float *h_a, *h_b, *h_c;       // Host (CPU) 포인터
    float *d_a, *d_b, *d_c;       // Device (GPU) 포인터

    // 1. Host 메모리 할당
    h_a = (float*)malloc(N * sizeof(float));
    h_b = (float*)malloc(N * sizeof(float));
    h_c = (float*)malloc(N * sizeof(float));

    // 2. 초기화
    for (int i = 0; i < N; i++) {
        h_a[i] = i * 1.0f;
        h_b[i] = i * 2.0f;
    }

    // 3. GPU 메모리 할당
    cudaMalloc(&d_a, N * sizeof(float));
    cudaMalloc(&d_b, N * sizeof(float));
    cudaMalloc(&d_c, N * sizeof(float));

    // 4. Host → GPU 데이터 복사
    cudaMemcpy(d_a, h_a, N * sizeof(float), cudaMemcpyHostToDevice);
    cudaMemcpy(d_b, h_b, N * sizeof(float), cudaMemcpyHostToDevice);

    // 5. 커널 실행
    int threads_per_block = 256;
    int blocks = (N + threads_per_block - 1) / threads_per_block;
    vector_add<<<blocks, threads_per_block>>>(d_a, d_b, d_c, N);

    // 6. 결과를 Host로 복사
    cudaMemcpy(h_c, d_c, N * sizeof(float), cudaMemcpyDeviceToHost);

    // 7. 결과 확인
    printf("h_a[0] = %.1f, h_b[0] = %.1f, h_c[0] = %.1f\n",
           h_a[0], h_b[0], h_c[0]);
    printf("h_a[999999] = %.1f, h_b[999999] = %.1f, h_c[999999] = %.1f\n",
           h_a[N-1], h_b[N-1], h_c[N-1]);

    // 8. 메모리 해제
    free(h_a); free(h_b); free(h_c);
    cudaFree(d_a); cudaFree(d_b); cudaFree(d_c);

    return 0;
}
```

```bash
# 컴파일 및 실행
nvcc -o vector_add vector_add.cu
./vector_add
# h_a[0] = 0.0, h_b[0] = 0.0, h_c[0] = 0.0
# h_a[999999] = 999999.0, h_b[999999] = 1999998.0, h_c[999999] = 2999997.0
```

---

## 4. 이미지 처리: Sobel Edge Detection

```cpp
// sobel_cuda.cu — GPU를 활용한 에지 검출
#include <stdio.h>
#include <cuda_runtime.h>
#include <math.h>

#define WIDTH 1920
#define HEIGHT 1080

// Sobel X 커널 (수직 에지)
__global__ void sobel_x(unsigned char *input, unsigned char *output,
                        int width, int height) {
    int col = blockIdx.x * blockDim.x + threadIdx.x;
    int row = blockIdx.y * blockDim.y + threadIdx.y;

    if (col > 0 && col < width-1 && row > 0 && row < height-1) {
        int idx = row * width + col;
        // Sobel X 마스크 적용
        int gx = -input[(row-1)*width + (col-1)] + input[(row-1)*width + (col+1)]
                 -2*input[row*width + (col-1)] + 2*input[row*width + (col+1)]
                 -input[(row+1)*width + (col-1)] + input[(row+1)*width + (col+1)];
        output[idx] = min(max(abs(gx) / 8, 0), 255);
    }
}

int main() {
    unsigned char *d_input, *d_output;
    cudaMalloc(&d_input, WIDTH * HEIGHT);
    cudaMalloc(&d_output, WIDTH * HEIGHT);

    dim3 block_size(16, 16);
    dim3 grid_size((WIDTH + 15) / 16, (HEIGHT + 15) / 16);

    sobel_x<<<grid_size, block_size>>>(d_input, d_output, WIDTH, HEIGHT);
    cudaDeviceSynchronize();

    printf("Sobel X edge detection completed on GPU.\n");
    printf("Grid: %dx%d, Block: %dx%d\n",
           grid_size.x, grid_size.y, block_size.x, block_size.y);

    cudaFree(d_input);
    cudaFree(d_output);
    return 0;
}
```

### CUDA 성능 프로파일링

```bash
# 커널 실행 시간 측정
nvcc -o sobel sobel_cuda.cu
./sobel

# 상세 프로파일링 (nsight)
nvprof ./sobel
```

---

## 5. CUDA + Python (PyCUDA)

```python
# pycuda_example.py
import pycuda.autoinit
import pycuda.driver as cuda
import numpy as np
from pycuda.compiler import SourceModule

# CUDA 커널 (문자열로 직접 작성)
mod = SourceModule("""
__global__ void multiply_by_2(float *data, int n) {
    int idx = threadIdx.x + blockIdx.x * blockDim.x;
    if (idx < n) {
        data[idx] *= 2.0f;
    }
}
""")

# 데이터 준비
n = 1000
data = np.random.randn(n).astype(np.float32)
data_gpu = cuda.mem_alloc(data.nbytes)
cuda.memcpy_htod(data_gpu, data)

# 커널 실행
func = mod.get_function("multiply_by_2")
func(data_gpu, np.int32(n), block=(256, 1, 1), grid=((n+255)//256, 1))

# 결과 복사
result = np.empty_like(data)
cuda.memcpy_dtoh(result, data_gpu)

# 검증
print(f"Original[0]: {data[0]:.4f}")
print(f"Result[0]:   {result[0]:.4f}")
print(f"Expected:   {data[0]*2:.4f}")
print(f"Pass: {np.allclose(result, data*2)}")
```

---

## 6. Jetson GPU 최적화 팁

| 최적화 방법 | 설명 | 효과 |
|:-----------|------|:----:|
| **통합 메모리 사용** | `cudaMallocManaged` | 메모리 복사 최소화 |
| **적절한 블록 크기** | 128~256 스레드/블록 | SM 점유율 최대화 |
| **공유 메모리 활용** | `__shared__` | 글로벌 메모리 접근 감소 |
| **GPU 클럭 고정** | `sudo jetson_clocks` | 안정적인 성능 |

### jetson_clocks 실행

```bash
# GPU/CPU 최대 클럭 고정 (성능 최대화)
sudo jetson_clocks

# 기본 모드로 복귀
sudo jetson_clocks --restore
```

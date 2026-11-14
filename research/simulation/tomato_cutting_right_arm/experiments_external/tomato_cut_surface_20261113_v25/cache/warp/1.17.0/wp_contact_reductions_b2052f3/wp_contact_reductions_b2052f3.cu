#define WP_NO_BFLOAT16

#define WP_TILE_BLOCK_DIM 256
#define WP_NO_CRT
#include "builtin.h"
#include "deterministic.h"

// Map wp.breakpoint() to a device brkpt at the call site so cuda-gdb attributes the stop to the generated .cu line
#if defined(__CUDACC__) && !defined(_MSC_VER)
#define __debugbreak() __brkpt()
#endif

#define builtin_tid1d() wp::tid(_idx, dim)
#define builtin_tid2d(x, y) wp::tid(x, y, _idx, dim)
#define builtin_tid3d(x, y, z) wp::tid(x, y, z, _idx, dim)
#define builtin_tid4d(x, y, z, w) wp::tid(x, y, z, w, _idx, dim)

#define builtin_block_dim() wp::block_dim()

// CUDA Thread Block Cluster shape declaration. Expands to __cluster_dims__
// only on devices that support clusters (compute capability 9.0+); otherwise
// expands to nothing so the same source compiles cleanly for any target arch.
#if defined(__CUDA_ARCH__) && (__CUDA_ARCH__ >= 900)
#define WP_CLUSTER_DIMS(x, y, z) __cluster_dims__(x, y, z)
#else
#define WP_CLUSTER_DIMS(x, y, z)
#endif

// Maximum registers per thread. __maxnreg__ was added in CUDA Toolkit 12.4;
// older toolkits ignore the opt-in so the same source remains compilable.
#if defined(__CUDACC_VER_MAJOR__) && (__CUDACC_VER_MAJOR__ > 12 || (__CUDACC_VER_MAJOR__ == 12 && __CUDACC_VER_MINOR__ >= 4))
#define WP_MAXNREG(n) __maxnreg__(n)
#else
#define WP_MAXNREG(n)
#endif

// Allow PTXAS to spill registers into shared memory. CUDA Toolkit 13.0
// introduced the pragma, which is unavailable in device-debug compilation.
#if defined(__CUDACC_VER_MAJOR__) && (__CUDACC_VER_MAJOR__ >= 13) && !defined(_DEBUG)
#define WP_ENABLE_SMEM_SPILLING() asm volatile(".pragma \"enable_smem_spilling\";");
#else
#define WP_ENABLE_SMEM_SPILLING()
#endif


// avoid namespacing of float type for casting to float type, this is to avoid wp::float(x), which is not valid in C++
#define float(x) cast_float(x)
#define adj_float(x, adj_x, adj_ret) adj_cast_float(x, adj_x, adj_ret)

#define int(x) cast_int(x)
#define adj_int(x, adj_x, adj_ret) adj_cast_int(x, adj_x, adj_ret)



extern "C" __global__ void force_guard_41cd5126_cuda_kernel_forward(
    wp::launch_bounds_t<1> dim,
    wp::array_t<wp::vec_t<3, wp::float32>> var_sums,
    wp::array_t<wp::float32> var_magnitudes,
    wp::array_t<wp::int32> var_bad,
    wp::array_t<wp::float32> var_peak,
    wp::int32 var_n)
{
    wp::tile_shared_storage_t tile_mem;

    for (size_t _idx = static_cast<size_t>(blockDim.x) * static_cast<size_t>(blockIdx.x) + static_cast<size_t>(threadIdx.x);
         _idx < dim.size;
         _idx += static_cast<size_t>(blockDim.x) * static_cast<size_t>(gridDim.x))
    {
            // reset shared memory allocator
        wp::tile_shared_storage_t::init();

        //---------
        // primal vars
        wp::int32 var_0;
        const wp::int32 var_1 = 0;
        bool var_2;
        const wp::float32 var_3 = 0.0;
        wp::vec_t<3, wp::float32> var_4;
        const wp::float32 var_5 = 0.0;
        wp::float32 var_6;
        wp::range_t var_7;
        wp::int32 var_8;
        wp::vec_t<3, wp::float32>* var_9;
        wp::vec_t<3, wp::float32> var_10;
        wp::vec_t<3, wp::float32> var_11;
        wp::float32* var_12;
        wp::float32 var_13;
        wp::float32 var_14;
        wp::float32 var_15;
        wp::float32 var_16;
        const wp::int32 var_17 = 0;
        wp::float32* var_18;
        wp::float32 var_19;
        wp::float32 var_20;
        const wp::int32 var_21 = 0;
        bool var_22;
        const wp::float32 var_23 = 2.0;
        bool var_24;
        bool var_25;
        bool var_26;
        const wp::int32 var_27 = 0;
        const wp::int32 var_28 = 3;
        wp::int32 var_29;
        //---------
        // forward
        // def force_guard(sums:wp.array(dtype=wp.vec3),magnitudes:wp.array(dtype=float),bad:wp.array(dtype=int),peak:wp.array(dtype=float),n:int):       <L 16>
        // if wp.tid()==0:                                                                        <L 17>
        var_0 = builtin_tid1d();
        var_2 = (var_0 == var_1);
        if (var_2) {
            // f=wp.vec3(0.);m=float(0.)                                                          <L 18>
            var_4 = wp::vec_t<3, wp::float32>(var_3);
            var_6 = wp::float(var_5);
            // for b in range(n):f+=sums[b];m+=magnitudes[b]                                      <L 19>
            var_7 = wp::range(var_n);
            start_for_0:;
                if (iter_cmp(var_7) == 0) goto end_for_0;
                var_8 = wp::iter_next(var_7);
                var_9 = wp::address(var_sums, var_8);
                var_11 = wp::load(var_9);
                var_10 = wp::add(var_4, var_11);
                var_12 = wp::address(var_magnitudes, var_8);
                var_14 = wp::load(var_12);
                var_13 = wp::add(var_6, var_14);
                wp::assign(var_4, var_10);
                wp::assign(var_6, var_13);
                goto start_for_0;
            end_for_0:;
            // value=wp.max(m,wp.length(f));peak[0]=wp.max(peak[0],value)                         <L 20>
            var_15 = wp::length(var_4);
            var_16 = wp::max(var_6, var_15);
            var_18 = wp::address(var_peak, var_17);
            var_20 = wp::load(var_18);
            var_19 = wp::max(var_20, var_16);
            wp::array_store(var_peak, var_21, var_19);
            // if value>2. or not wp.isfinite(value):wp.atomic_max(bad,0,3)                       <L 21>
            var_24 = (var_16 > var_23);
            var_22 = var_24;
            if (!var_22) {
                var_25 = wp::isfinite(var_16);
                var_26 = wp::unot(var_25);
                var_22 = var_22 || var_26;
            }
            if (var_22) {
                var_29 = wp::atomic_max(var_bad, var_27, var_28);
            }
        }
    }
}



extern "C" __global__ void force_parts_6eb50331_cuda_kernel_forward(
    wp::launch_bounds_t<1> dim,
    wp::array_t<wp::vec_t<3, wp::float32>> var_cf,
    wp::array_t<wp::vec_t<3, wp::float32>> var_sums,
    wp::array_t<wp::float32> var_magnitudes,
    wp::int32 var_n)
{
    wp::tile_shared_storage_t tile_mem;

    for (size_t _idx = static_cast<size_t>(blockDim.x) * static_cast<size_t>(blockIdx.x) + static_cast<size_t>(threadIdx.x);
         _idx < dim.size;
         _idx += static_cast<size_t>(blockDim.x) * static_cast<size_t>(gridDim.x))
    {
            // reset shared memory allocator
        wp::tile_shared_storage_t::init();

        //---------
        // primal vars
        wp::int32 var_0;
        const wp::float32 var_1 = 0.0;
        wp::vec_t<3, wp::float32> var_2;
        const wp::float32 var_3 = 0.0;
        wp::float32 var_4;
        const wp::int32 var_5 = 128;
        wp::int32 var_6;
        const wp::int32 var_7 = 1;
        wp::int32 var_8;
        const wp::int32 var_9 = 128;
        wp::int32 var_10;
        wp::int32 var_11;
        wp::range_t var_12;
        wp::int32 var_13;
        wp::vec_t<3, wp::float32>* var_14;
        wp::vec_t<3, wp::float32> var_15;
        wp::vec_t<3, wp::float32> var_16;
        wp::vec_t<3, wp::float32>* var_17;
        wp::float32 var_18;
        wp::vec_t<3, wp::float32> var_19;
        wp::float32 var_20;
        //---------
        // forward
        // def force_parts(cf:wp.array(dtype=wp.vec3),sums:wp.array(dtype=wp.vec3),magnitudes:wp.array(dtype=float),n:int):       <L 11>
        // b=wp.tid();f=wp.vec3(0.);m=float(0.)                                                   <L 12>
        var_0 = builtin_tid1d();
        var_2 = wp::vec_t<3, wp::float32>(var_1);
        var_4 = wp::float(var_3);
        // for i in range(b*128,wp.min((b+1)*128,n)):f+=cf[i];m+=wp.length(cf[i])                 <L 13>
        var_6 = wp::mul(var_0, var_5);
        var_8 = wp::add(var_0, var_7);
        var_10 = wp::mul(var_8, var_9);
        var_11 = wp::min(var_10, var_n);
        var_12 = wp::range(var_6, var_11);
        start_for_0:;
            if (iter_cmp(var_12) == 0) goto end_for_0;
            var_13 = wp::iter_next(var_12);
            var_14 = wp::address(var_cf, var_13);
            var_16 = wp::load(var_14);
            var_15 = wp::add(var_2, var_16);
            var_17 = wp::address(var_cf, var_13);
            var_19 = wp::load(var_17);
            var_18 = wp::length(var_19);
            var_20 = wp::add(var_4, var_18);
            wp::assign(var_2, var_15);
            wp::assign(var_4, var_20);
            goto start_for_0;
        end_for_0:;
        // sums[b]=f;magnitudes[b]=m                                                              <L 14>
        wp::array_store(var_sums, var_0, var_2);
        wp::array_store(var_magnitudes, var_0, var_4);
    }
}


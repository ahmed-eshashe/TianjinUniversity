#define WP_NO_BFLOAT16

#define WP_TILE_BLOCK_DIM 128
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



extern "C" __global__ void pullback_parallel_bea7c15a_cuda_kernel_forward(
    wp::launch_bounds_t<1> dim,
    wp::array_t<wp::int32> var_ptr,
    wp::array_t<wp::int32> var_ids,
    wp::array_t<wp::float32> var_w,
    wp::array_t<wp::vec_t<3, wp::float32>> var_cf,
    wp::array_t<wp::vec_t<3, wp::float32>> var_external,
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
        const wp::int32 var_1 = 32;
        wp::int32 var_2;
        const wp::int32 var_3 = 32;
        wp::int32 var_4;
        const wp::float32 var_5 = 0.0;
        wp::vec_t<3, wp::float32> var_6;
        bool var_7;
        wp::int32* var_8;
        wp::int32 var_9;
        wp::int32 var_10;
        const wp::int32 var_11 = 1;
        wp::int32 var_12;
        wp::int32* var_13;
        const wp::int32 var_14 = 32;
        wp::range_t var_15;
        wp::int32 var_16;
        wp::int32 var_17;
        wp::float32* var_18;
        wp::int32* var_19;
        wp::vec_t<3, wp::float32>* var_20;
        wp::int32 var_21;
        wp::vec_t<3, wp::float32> var_22;
        wp::float32 var_23;
        wp::vec_t<3, wp::float32> var_24;
        wp::vec_t<3, wp::float32> var_25;
        const bool var_26 = true;
        wp::tile_shared_t<wp::vec_t<3, wp::float32>,wp::tile_layout_strided_t<wp::tile_shape_t<128>, wp::tile_stride_t<1>>, true> var_27 = wp::tile_alloc_empty<wp::vec_t<3, wp::float32>,wp::tile_shape_t<128>,wp::tile_stride_t<1>,false>();
        const wp::int32 var_28 = 4;
        const wp::int32 var_29 = 32;
        wp::tuple_t<wp::int32, wp::int32> var_30;
        wp::tile_shared_t<wp::vec_t<3, wp::float32>,wp::tile_layout_strided_t<wp::tile_shape_t<4,32>, wp::tile_stride_t<32,1>>, false> var_31 = nullptr;
        const wp::int32 var_32 = 1;
        wp::tile_register_t<wp::vec_t<3, wp::float32>,wp::tile_layout_register_t<wp::tile_shape_t<4>>> var_33 = wp::tile_register_t<wp::vec_t<3, wp::float32>,wp::tile_layout_register_t<wp::tile_shape_t<4>>>{};
        const wp::int32 var_34 = 128;
        wp::int32 var_35;
        const wp::int32 var_36 = 4;
        wp::int32 var_37;
        //---------
        // forward
        // def pullback_parallel(ptr:wp.array(dtype=int),ids:wp.array(dtype=int),w:wp.array(dtype=float),cf:wp.array(dtype=wp.vec3),external:wp.array(dtype=wp.vec3),n:int):       <L 4>
        // t=wp.tid();i=t//32;lane=t%32;f=wp.vec3(0.)                                             <L 5>
        var_0 = builtin_tid1d();
        var_2 = wp::floordiv(var_0, var_1);
        var_4 = wp::mod(var_0, var_3);
        var_6 = wp::vec_t<3, wp::float32>(var_5);
        // if i<n:                                                                                <L 6>
        var_7 = (var_2 < var_n);
        if (var_7) {
            // for k in range(ptr[i]+lane,ptr[i+1],32):f+=w[k]*cf[ids[k]]                         <L 7>
            var_8 = wp::address(var_ptr, var_2);
            var_10 = wp::load(var_8);
            var_9 = wp::add(var_10, var_4);
            var_12 = wp::add(var_2, var_11);
            var_13 = wp::address(var_ptr, var_12);
            var_16 = wp::load(var_13);
            var_15 = wp::range(var_9, var_16, var_14);
            start_for_0:;
                if (iter_cmp(var_15) == 0) goto end_for_0;
                var_17 = wp::iter_next(var_15);
                var_18 = wp::address(var_w, var_17);
                var_19 = wp::address(var_ids, var_17);
                var_21 = wp::load(var_19);
                var_20 = wp::address(var_cf, var_21);
                var_23 = wp::load(var_18);
                var_24 = wp::load(var_20);
                var_22 = wp::mul(var_23, var_24);
                var_25 = wp::add(var_6, var_22);
                wp::assign(var_6, var_25);
                goto start_for_0;
            end_for_0:;
        }
        // total=wp.tile_sum(wp.tile_reshape(wp.tile(f,preserve_type=True),(4,32)),axis=1)        <L 8>
        var_27 = wp::tile<wp::vec_t<3, wp::float32>>(var_6);
        var_30 = wp::tuple(var_28, var_29);
        var_31 = wp::tile_reshape<wp::tile_shared_t<wp::vec_t<3, wp::float32>,wp::tile_layout_strided_t<wp::tile_shape_t<4,32>, wp::tile_stride_t<32,1>>, false>>(var_27);
        var_33 = wp::tile_sum<1>(var_31);
        // wp.tile_store(external,total,offset=(t//128)*4)                                        <L 9>
        var_35 = wp::floordiv(var_0, var_34);
        var_37 = wp::mul(var_35, var_36);
        wp::tile_store<wp::vec_t<3, wp::float32>, true, false>(var_external, var_37, var_33);
    }
}


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



extern "C" __global__ void gather_edges_21e69691_cuda_kernel_forward(
    wp::launch_bounds_t<1> dim,
    wp::array_t<wp::int32> var_ptr,
    wp::array_t<wp::int32> var_edge,
    wp::array_t<wp::vec_t<3, wp::float32>> var_edgeforce,
    wp::array_t<wp::vec_t<3, wp::float32>> var_external,
    wp::array_t<wp::vec_t<3, wp::float32>> var_force,
    wp::array_t<wp::int32> var_counts)
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
        const wp::int32 var_7 = 0;
        wp::int32* var_8;
        bool var_9;
        wp::int32 var_10;
        wp::int32* var_11;
        wp::int32 var_12;
        wp::int32 var_13;
        const wp::int32 var_14 = 1;
        wp::int32 var_15;
        wp::int32* var_16;
        const wp::int32 var_17 = 32;
        wp::range_t var_18;
        wp::int32 var_19;
        wp::int32 var_20;
        wp::int32* var_21;
        wp::vec_t<3, wp::float32>* var_22;
        wp::int32 var_23;
        wp::vec_t<3, wp::float32> var_24;
        wp::vec_t<3, wp::float32> var_25;
        const wp::int32 var_26 = 0;
        bool var_27;
        wp::vec_t<3, wp::float32>* var_28;
        wp::vec_t<3, wp::float32> var_29;
        wp::vec_t<3, wp::float32> var_30;
        wp::vec_t<3, wp::float32> var_31;
        wp::vec_t<3, wp::float32> var_32;
        const bool var_33 = true;
        wp::tile_shared_t<wp::vec_t<3, wp::float32>,wp::tile_layout_strided_t<wp::tile_shape_t<128>, wp::tile_stride_t<1>>, true> var_34 = wp::tile_alloc_empty<wp::vec_t<3, wp::float32>,wp::tile_shape_t<128>,wp::tile_stride_t<1>,false>();
        const wp::int32 var_35 = 4;
        const wp::int32 var_36 = 32;
        wp::tuple_t<wp::int32, wp::int32> var_37;
        wp::tile_shared_t<wp::vec_t<3, wp::float32>,wp::tile_layout_strided_t<wp::tile_shape_t<4,32>, wp::tile_stride_t<32,1>>, false> var_38 = nullptr;
        const wp::int32 var_39 = 1;
        wp::tile_register_t<wp::vec_t<3, wp::float32>,wp::tile_layout_register_t<wp::tile_shape_t<4>>> var_40 = wp::tile_register_t<wp::vec_t<3, wp::float32>,wp::tile_layout_register_t<wp::tile_shape_t<4>>>{};
        const wp::int32 var_41 = 128;
        wp::int32 var_42;
        const wp::int32 var_43 = 4;
        wp::int32 var_44;
        //---------
        // forward
        // def gather_edges(ptr:wp.array(dtype=int),edge:wp.array(dtype=int),edgeforce:wp.array(dtype=wp.vec3),external:wp.array(dtype=wp.vec3),force:wp.array(dtype=wp.vec3),counts:wp.array(dtype=int)):       <L 24>
        // t=wp.tid();i=t//32;lane=t%32;f=wp.vec3(0.0)                                            <L 25>
        var_0 = builtin_tid1d();
        var_2 = wp::floordiv(var_0, var_1);
        var_4 = wp::mod(var_0, var_3);
        var_6 = wp::vec_t<3, wp::float32>(var_5);
        // if i<counts[0]:                                                                        <L 26>
        var_8 = wp::address(var_counts, var_7);
        var_10 = wp::load(var_8);
        var_9 = (var_2 < var_10);
        if (var_9) {
            // for e in range(ptr[i]+lane,ptr[i+1],32):f-=edgeforce[edge[e]]                      <L 27>
            var_11 = wp::address(var_ptr, var_2);
            var_13 = wp::load(var_11);
            var_12 = wp::add(var_13, var_4);
            var_15 = wp::add(var_2, var_14);
            var_16 = wp::address(var_ptr, var_15);
            var_19 = wp::load(var_16);
            var_18 = wp::range(var_12, var_19, var_17);
            start_for_0:;
                if (iter_cmp(var_18) == 0) goto end_for_0;
                var_20 = wp::iter_next(var_18);
                var_21 = wp::address(var_edge, var_20);
                var_23 = wp::load(var_21);
                var_22 = wp::address(var_edgeforce, var_23);
                var_25 = wp::load(var_22);
                var_24 = wp::sub(var_6, var_25);
                wp::assign(var_6, var_24);
                goto start_for_0;
            end_for_0:;
            // if lane==0:f+=external[i]                                                          <L 28>
            var_27 = (var_4 == var_26);
            if (var_27) {
                var_28 = wp::address(var_external, var_2);
                var_30 = wp::load(var_28);
                var_29 = wp::add(var_6, var_30);
            }
            var_31 = wp::where(var_27, var_29, var_6);
        }
        var_32 = wp::where(var_9, var_31, var_6);
        // total=wp.tile_sum(wp.tile_reshape(wp.tile(f,preserve_type=True),(4,32)),axis=1)        <L 29>
        var_34 = wp::tile<wp::vec_t<3, wp::float32>>(var_32);
        var_37 = wp::tuple(var_35, var_36);
        var_38 = wp::tile_reshape<wp::tile_shared_t<wp::vec_t<3, wp::float32>,wp::tile_layout_strided_t<wp::tile_shape_t<4,32>, wp::tile_stride_t<32,1>>, false>>(var_34);
        var_40 = wp::tile_sum<1>(var_38);
        // wp.tile_store(force,total,offset=(t//128)*4)                                           <L 30>
        var_42 = wp::floordiv(var_0, var_41);
        var_44 = wp::mul(var_42, var_43);
        wp::tile_store<wp::vec_t<3, wp::float32>, true, false>(var_force, var_44, var_40);
    }
}


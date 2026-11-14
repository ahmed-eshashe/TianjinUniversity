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



extern "C" __global__ void estimate_55f3ecb2_cuda_kernel_forward(
    wp::launch_bounds_t<1> dim,
    wp::array_t<wp::int32> var_ptr,
    wp::array_t<wp::int32> var_ids,
    wp::array_t<wp::float32> var_mass_inv,
    wp::array_t<wp::vec_t<3, wp::float32>> var_force,
    wp::array_t<wp::vec_t<3, wp::float32>> var_base,
    wp::array_t<wp::vec_t<3, wp::float32>> var_v,
    wp::array_t<wp::int32> var_fixed,
    wp::float32 var_dt,
    wp::int32 var_n,
    wp::array_t<wp::int32> var_bad)
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
        bool var_1;
        bool var_2;
        const wp::int32 var_3 = 0;
        wp::int32* var_4;
        const wp::int32 var_5 = 0;
        bool var_6;
        wp::int32 var_7;
        wp::int32* var_8;
        const wp::int32 var_9 = 0;
        bool var_10;
        wp::int32 var_11;
        const wp::float32 var_12 = 0.0;
        wp::vec_t<3, wp::float32> var_13;
        const wp::float32 var_14 = 0.0;
        wp::vec_t<3, wp::float32> var_15;
        wp::int32* var_16;
        const wp::int32 var_17 = 1;
        wp::int32 var_18;
        wp::int32* var_19;
        wp::range_t var_20;
        wp::int32 var_21;
        wp::int32 var_22;
        wp::int32 var_23;
        wp::float32* var_24;
        wp::int32* var_25;
        wp::vec_t<3, wp::float32>* var_26;
        wp::int32 var_27;
        wp::vec_t<3, wp::float32> var_28;
        wp::float32 var_29;
        wp::vec_t<3, wp::float32> var_30;
        wp::vec_t<3, wp::float32> var_31;
        wp::vec_t<3, wp::float32>* var_32;
        wp::vec_t<3, wp::float32> var_33;
        wp::vec_t<3, wp::float32> var_34;
        wp::vec_t<3, wp::float32> var_35;
        //---------
        // forward
        // def estimate(ptr:wp.array(dtype=int),ids:wp.array(dtype=int),mass_inv:wp.array(dtype=float),force:wp.array(dtype=wp.vec3),base:wp.array(dtype=wp.vec3),v:wp.array(dtype=wp.vec3),fixed:wp.array(dtype=int),dt:float,n:int,bad:wp.array(dtype=int)):       <L 13>
        // i=wp.tid()                                                                             <L 14>
        var_0 = builtin_tid1d();
        // if i<n and bad[0]==0:                                                                  <L 15>
        var_2 = (var_0 < var_n);
        var_1 = var_2;
        if (var_1) {
            var_4 = wp::address(var_bad, var_3);
            var_7 = wp::load(var_4);
            var_6 = (var_7 == var_5);
            var_1 = var_1 && var_6;
        }
        if (var_1) {
            // if fixed[i]!=0:v[i]=wp.vec3(0.)                                                    <L 16>
            var_8 = wp::address(var_fixed, var_0);
            var_11 = wp::load(var_8);
            var_10 = (var_11 != var_9);
            if (var_10) {
                var_13 = wp::vec_t<3, wp::float32>(var_12);
                wp::array_store(var_v, var_0, var_13);
            }
            if (!var_10) {
                // acc=wp.vec3(0.)                                                                <L 18>
                var_15 = wp::vec_t<3, wp::float32>(var_14);
                // for j in range(ptr[i],ptr[i+1]):acc+=mass_inv[j]*force[ids[j]]                 <L 19>
                var_16 = wp::address(var_ptr, var_0);
                var_18 = wp::add(var_0, var_17);
                var_19 = wp::address(var_ptr, var_18);
                var_21 = wp::load(var_16);
                var_22 = wp::load(var_19);
                var_20 = wp::range(var_21, var_22);
                start_for_0:;
                    if (iter_cmp(var_20) == 0) goto end_for_0;
                    var_23 = wp::iter_next(var_20);
                    var_24 = wp::address(var_mass_inv, var_23);
                    var_25 = wp::address(var_ids, var_23);
                    var_27 = wp::load(var_25);
                    var_26 = wp::address(var_force, var_27);
                    var_29 = wp::load(var_24);
                    var_30 = wp::load(var_26);
                    var_28 = wp::mul(var_29, var_30);
                    var_31 = wp::add(var_15, var_28);
                    wp::assign(var_15, var_31);
                    goto start_for_0;
                end_for_0:;
                // v[i]=base[i]+dt*acc                                                            <L 20>
                var_32 = wp::address(var_base, var_0);
                var_33 = wp::mul(var_dt, var_15);
                var_35 = wp::load(var_32);
                var_34 = wp::add(var_35, var_33);
                wp::array_store(var_v, var_0, var_34);
            }
        }
    }
}


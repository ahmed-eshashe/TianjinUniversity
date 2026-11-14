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



extern "C" __global__ void contact_advance_0a8cad94_cuda_kernel_forward(
    wp::launch_bounds_t<1> dim,
    wp::array_t<wp::vec_t<3, wp::float32>> var_x,
    wp::array_t<wp::vec_t<3, wp::float32>> var_v,
    wp::array_t<wp::int32> var_codes,
    wp::array_t<wp::int32> var_lookup,
    wp::array_t<wp::int32> var_ids,
    wp::array_t<wp::float32> var_w,
    wp::array_t<wp::vec_t<3, wp::float32>> var_v0,
    wp::array_t<wp::vec_t<3, wp::float32>> var_v1,
    wp::array_t<wp::vec_t<3, wp::float32>> var_force,
    wp::float32 var_mass,
    wp::array_t<wp::int32> var_fixed,
    wp::array_t<wp::vec_t<3, wp::float32>> var_support,
    wp::float32 var_dt)
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
        wp::int32* var_1;
        wp::int32* var_2;
        wp::int32 var_3;
        wp::int32 var_4;
        wp::int32 var_5;
        const wp::float32 var_6 = 0.0;
        wp::vec_t<3, wp::float32> var_7;
        const wp::int32 var_8 = 27;
        wp::range_t var_9;
        wp::int32 var_10;
        wp::int32* var_11;
        wp::int32 var_12;
        wp::int32 var_13;
        wp::float32* var_14;
        wp::vec_t<3, wp::float32>* var_15;
        wp::vec_t<3, wp::float32>* var_16;
        wp::vec_t<3, wp::float32> var_17;
        wp::vec_t<3, wp::float32> var_18;
        wp::vec_t<3, wp::float32> var_19;
        wp::vec_t<3, wp::float32> var_20;
        wp::float32 var_21;
        wp::vec_t<3, wp::float32> var_22;
        wp::vec_t<3, wp::float32>* var_23;
        wp::vec_t<3, wp::float32> var_24;
        wp::vec_t<3, wp::float32> var_25;
        wp::vec_t<3, wp::float32>* var_26;
        wp::vec_t<3, wp::float32> var_27;
        wp::vec_t<3, wp::float32> var_28;
        wp::vec_t<3, wp::float32> var_29;
        wp::vec_t<3, wp::float32> var_30;
        const wp::float32 var_31 = 0.0;
        wp::vec_t<3, wp::float32> var_32;
        wp::int32* var_33;
        const wp::int32 var_34 = 0;
        bool var_35;
        wp::int32 var_36;
        wp::float32 var_37;
        wp::vec_t<3, wp::float32> var_38;
        const wp::float32 var_39 = 0.0;
        wp::vec_t<3, wp::float32> var_40;
        wp::vec_t<3, wp::float32> var_41;
        wp::vec_t<3, wp::float32>* var_42;
        wp::vec_t<3, wp::float32> var_43;
        wp::vec_t<3, wp::float32> var_44;
        wp::vec_t<3, wp::float32> var_45;
        //---------
        // forward
        // def contact_advance(x:wp.array(dtype=wp.vec3),v:wp.array(dtype=wp.vec3),codes:wp.array(dtype=int),lookup:wp.array(dtype=int),ids:wp.array2d(dtype=int),w:wp.array2d(dtype=float),v0:wp.array2d(dtype=wp.vec3),v1:wp.array2d(dtype=wp.vec3),force:wp.array(dtype=wp.vec3),mass:float,fixed:wp.array(dtype=int),support:wp.array(dtype=wp.vec3),dt:float):       <L 3>
        // p=wp.tid();a=lookup[codes[p]];dv=wp.vec3(0.0)                                          <L 4>
        var_0 = builtin_tid1d();
        var_1 = wp::address(var_codes, var_0);
        var_3 = wp::load(var_1);
        var_2 = wp::address(var_lookup, var_3);
        var_5 = wp::load(var_2);
        var_4 = wp::copy(var_5);
        var_7 = wp::vec_t<3, wp::float32>(var_6);
        // for s in range(27):                                                                    <L 5>
        var_9 = wp::range(var_8);
        start_for_0:;
            if (iter_cmp(var_9) == 0) goto end_for_0;
            var_10 = wp::iter_next(var_9);
            // i=ids[p,s];dv+=w[p,s]*(v1[a,i]-v0[a,i])                                            <L 6>
            var_11 = wp::address(var_ids, var_0, var_10);
            var_13 = wp::load(var_11);
            var_12 = wp::copy(var_13);
            var_14 = wp::address(var_w, var_0, var_10);
            var_15 = wp::address(var_v1, var_4, var_12);
            var_16 = wp::address(var_v0, var_4, var_12);
            var_18 = wp::load(var_15);
            var_19 = wp::load(var_16);
            var_17 = wp::sub(var_18, var_19);
            var_21 = wp::load(var_14);
            var_20 = wp::mul(var_21, var_17);
            var_22 = wp::add(var_7, var_20);
            wp::assign(var_7, var_22);
            goto start_for_0;
        end_for_0:;
        // vv=v[p]+dv+dt*force[p]/mass;support[p]=wp.vec3(0.0)                                    <L 7>
        var_23 = wp::address(var_v, var_0);
        var_25 = wp::load(var_23);
        var_24 = wp::add(var_25, var_7);
        var_26 = wp::address(var_force, var_0);
        var_28 = wp::load(var_26);
        var_27 = wp::mul(var_dt, var_28);
        var_29 = wp::div(var_27, var_mass);
        var_30 = wp::add(var_24, var_29);
        var_32 = wp::vec_t<3, wp::float32>(var_31);
        wp::array_store(var_support, var_0, var_32);
        // if fixed[p]!=0:support[p]=-mass*vv;vv=wp.vec3(0.0)                                     <L 8>
        var_33 = wp::address(var_fixed, var_0);
        var_36 = wp::load(var_33);
        var_35 = (var_36 != var_34);
        if (var_35) {
            var_37 = wp::neg(var_mass);
            var_38 = wp::mul(var_37, var_30);
            wp::array_store(var_support, var_0, var_38);
            var_40 = wp::vec_t<3, wp::float32>(var_39);
        }
        var_41 = wp::where(var_35, var_40, var_30);
        // v[p]=vv;x[p]=x[p]+dt*vv                                                                <L 9>
        wp::array_store(var_v, var_0, var_41);
        var_42 = wp::address(var_x, var_0);
        var_43 = wp::mul(var_dt, var_41);
        var_45 = wp::load(var_42);
        var_44 = wp::add(var_45, var_43);
        wp::array_store(var_x, var_0, var_44);
    }
}


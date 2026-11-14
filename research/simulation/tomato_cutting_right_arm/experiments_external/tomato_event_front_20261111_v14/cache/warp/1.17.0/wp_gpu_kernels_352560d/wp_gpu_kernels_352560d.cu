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



extern "C" __global__ void force_0540bcbf_cuda_kernel_forward(
    wp::launch_bounds_t<1> dim,
    wp::array_t<wp::int32> var_ptr,
    wp::array_t<wp::int32> var_ids,
    wp::array_t<wp::vec_t<3, wp::float64>> var_grad,
    wp::array_t<wp::mat_t<3, 3, wp::float64>> var_Pvol,
    wp::array_t<wp::vec_t<3, wp::float64>> var_load,
    wp::array_t<wp::int32> var_clock,
    wp::float64 var_dt,
    wp::float64 var_start_time,
    wp::float64 var_duration,
    wp::int32 var_mode,
    wp::int32 var_stage,
    wp::array_t<wp::vec_t<3, wp::float64>> var_out)
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
        wp::float64 var_1;
        wp::vec_t<3, wp::float64> var_2;
        wp::int32* var_3;
        const wp::int32 var_4 = 1;
        wp::int32 var_5;
        wp::int32* var_6;
        wp::range_t var_7;
        wp::int32 var_8;
        wp::int32 var_9;
        wp::int32 var_10;
        wp::int32* var_11;
        wp::mat_t<3, 3, wp::float64>* var_12;
        wp::int32 var_13;
        wp::vec_t<3, wp::float64>* var_14;
        wp::vec_t<3, wp::float64> var_15;
        wp::mat_t<3, 3, wp::float64> var_16;
        wp::vec_t<3, wp::float64> var_17;
        wp::vec_t<3, wp::float64> var_18;
        wp::float64 var_19;
        const wp::int32 var_20 = 1;
        bool var_21;
        const wp::int32 var_22 = 0;
        wp::int32* var_23;
        wp::int32 var_24;
        wp::int32 var_25;
        wp::float64 var_26;
        wp::float64 var_27;
        wp::float64 var_28;
        wp::float64 var_29;
        wp::float64 var_30;
        wp::float64 var_31;
        wp::float64 var_32;
        wp::float64 var_33;
        wp::float64 var_34;
        wp::vec_t<3, wp::float64>* var_35;
        wp::vec_t<3, wp::float64> var_36;
        wp::vec_t<3, wp::float64> var_37;
        wp::vec_t<3, wp::float64> var_38;
        //---------
        // forward
        // def force(ptr: wp.array(dtype=int), ids: wp.array(dtype=int), grad: wp.array(dtype=wp.vec3d),       <L 30>
        // i = wp.tid()                                                                           <L 34>
        var_0 = builtin_tid1d();
        // f = wp.vec3d(wp.float64(0.0))                                                          <L 35>
        var_1 = 0.0;
        var_2 = wp::vec_t<3, wp::float64>(var_1);
        // for e in range(ptr[i], ptr[i+1]):                                                      <L 36>
        var_3 = wp::address(var_ptr, var_0);
        var_5 = wp::add(var_0, var_4);
        var_6 = wp::address(var_ptr, var_5);
        var_8 = wp::load(var_3);
        var_9 = wp::load(var_6);
        var_7 = wp::range(var_8, var_9);
        start_for_0:;
            if (iter_cmp(var_7) == 0) goto end_for_0;
            var_10 = wp::iter_next(var_7);
            // f -= Pvol[ids[e]]*grad[e]                                                          <L 37>
            var_11 = wp::address(var_ids, var_10);
            var_13 = wp::load(var_11);
            var_12 = wp::address(var_Pvol, var_13);
            var_14 = wp::address(var_grad, var_10);
            var_16 = wp::load(var_12);
            var_17 = wp::load(var_14);
            var_15 = wp::mul(var_16, var_17);
            var_18 = wp::sub(var_2, var_15);
            wp::assign(var_2, var_18);
            goto start_for_0;
        end_for_0:;
        // amplitude = wp.float64(1.0)                                                            <L 38>
        var_19 = 1.0;
        // if mode == 1:                                                                          <L 39>
        var_21 = (var_mode == var_20);
        if (var_21) {
            // t = start_time + wp.float64(clock[0]+stage)*dt                                     <L 40>
            var_23 = wp::address(var_clock, var_22);
            var_25 = wp::load(var_23);
            var_24 = wp::add(var_25, var_stage);
            var_26 = wp::float64(var_24);
            var_27 = wp::mul(var_26, var_dt);
            var_28 = wp::add(var_start_time, var_27);
            // value = wp.sin(wp.float64(3.141592653589793)*t/duration)                           <L 41>
            var_29 = 3.141592653589793;
            var_30 = wp::mul(var_29, var_28);
            var_31 = wp::div(var_30, var_duration);
            var_32 = wp::sin(var_31);
            // amplitude = value*value                                                            <L 42>
            var_33 = wp::mul(var_32, var_32);
        }
        var_34 = wp::where(var_21, var_33, var_19);
        // out[i] = f + amplitude*load[i]                                                         <L 43>
        var_35 = wp::address(var_load, var_0);
        var_37 = wp::load(var_35);
        var_36 = wp::mul(var_34, var_37);
        var_38 = wp::add(var_2, var_36);
        wp::array_store(var_out, var_0, var_38);
    }
}



extern "C" __global__ void kick_17a9e9bc_cuda_kernel_forward(
    wp::launch_bounds_t<1> dim,
    wp::array_t<wp::vec_t<3, wp::float64>> var_q,
    wp::array_t<wp::vec_t<3, wp::float64>> var_v,
    wp::array_t<wp::vec_t<3, wp::float64>> var_a,
    wp::array_t<wp::vec_t<3, wp::float64>> var_r,
    wp::array_t<wp::float64> var_translation,
    wp::float64 var_dt,
    wp::array_t<wp::vec_t<3, wp::float64>> var_impulse,
    wp::array_t<wp::vec_t<3, wp::float64>> var_moment,
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
        const wp::int32 var_1 = 0;
        wp::int32* var_2;
        const wp::int32 var_3 = 0;
        bool var_4;
        wp::int32 var_5;
        wp::float64 var_6;
        wp::float64 var_7;
        wp::vec_t<3, wp::float64>* var_8;
        wp::vec_t<3, wp::float64> var_9;
        wp::vec_t<3, wp::float64> var_10;
        wp::vec_t<3, wp::float64> var_11;
        wp::float64 var_12;
        wp::float64 var_13;
        wp::float64* var_14;
        wp::float64 var_15;
        wp::float64 var_16;
        wp::vec_t<3, wp::float64>* var_17;
        wp::vec_t<3, wp::float64> var_18;
        wp::vec_t<3, wp::float64> var_19;
        wp::vec_t<3, wp::float64> var_20;
        wp::float64 var_21;
        wp::float64 var_22;
        wp::vec_t<3, wp::float64>* var_23;
        wp::vec_t<3, wp::float64>* var_24;
        wp::vec_t<3, wp::float64> var_25;
        wp::vec_t<3, wp::float64> var_26;
        wp::vec_t<3, wp::float64> var_27;
        wp::vec_t<3, wp::float64> var_28;
        wp::vec_t<3, wp::float64> var_29;
        const wp::int32 var_30 = 0;
        bool var_31;
        wp::vec_t<3, wp::float64>* var_32;
        wp::float64 var_33;
        wp::vec_t<3, wp::float64> var_34;
        bool var_35;
        bool var_36;
        wp::vec_t<3, wp::float64>* var_37;
        wp::float64 var_38;
        wp::vec_t<3, wp::float64> var_39;
        bool var_40;
        bool var_41;
        const wp::int32 var_42 = 0;
        const wp::int32 var_43 = 3;
        wp::int32 var_44;
        const wp::int32 var_45 = 1;
        bool var_46;
        wp::vec_t<3, wp::float64>* var_47;
        wp::float64 var_48;
        wp::vec_t<3, wp::float64> var_49;
        bool var_50;
        bool var_51;
        wp::vec_t<3, wp::float64>* var_52;
        wp::float64 var_53;
        wp::vec_t<3, wp::float64> var_54;
        bool var_55;
        bool var_56;
        const wp::int32 var_57 = 0;
        const wp::int32 var_58 = 3;
        wp::int32 var_59;
        const wp::int32 var_60 = 2;
        bool var_61;
        wp::vec_t<3, wp::float64>* var_62;
        wp::float64 var_63;
        wp::vec_t<3, wp::float64> var_64;
        bool var_65;
        bool var_66;
        wp::vec_t<3, wp::float64>* var_67;
        wp::float64 var_68;
        wp::vec_t<3, wp::float64> var_69;
        bool var_70;
        bool var_71;
        const wp::int32 var_72 = 0;
        const wp::int32 var_73 = 3;
        wp::int32 var_74;
        //---------
        // forward
        // def kick(q: wp.array(dtype=wp.vec3d), v: wp.array(dtype=wp.vec3d), a: wp.array(dtype=wp.vec3d),       <L 126>
        // i = wp.tid()                                                                           <L 129>
        var_0 = builtin_tid1d();
        // if bad[0] == 0:                                                                        <L 130>
        var_2 = wp::address(var_bad, var_1);
        var_5 = wp::load(var_2);
        var_4 = (var_5 == var_3);
        if (var_4) {
            // v[i] += wp.float64(0.5)*dt*a[i]                                                    <L 131>
            var_6 = 0.5;
            var_7 = wp::mul(var_6, var_dt);
            var_8 = wp::address(var_a, var_0);
            var_10 = wp::load(var_8);
            var_9 = wp::mul(var_7, var_10);
            var_11 = wp::atomic_add(var_v, var_0, var_9);
            // impulse[i] += wp.float64(0.5)*dt*translation[i]*r[i]                               <L 132>
            var_12 = 0.5;
            var_13 = wp::mul(var_12, var_dt);
            var_14 = wp::address(var_translation, var_0);
            var_16 = wp::load(var_14);
            var_15 = wp::mul(var_13, var_16);
            var_17 = wp::address(var_r, var_0);
            var_19 = wp::load(var_17);
            var_18 = wp::mul(var_15, var_19);
            var_20 = wp::atomic_add(var_impulse, var_0, var_18);
            // moment[i] += wp.float64(0.5)*dt*wp.cross(q[i],r[i])                                <L 133>
            var_21 = 0.5;
            var_22 = wp::mul(var_21, var_dt);
            var_23 = wp::address(var_q, var_0);
            var_24 = wp::address(var_r, var_0);
            var_26 = wp::load(var_23);
            var_27 = wp::load(var_24);
            var_25 = wp::cross(var_26, var_27);
            var_28 = wp::mul(var_22, var_25);
            var_29 = wp::atomic_add(var_moment, var_0, var_28);
            // for j in range(3):                                                                 <L 134>
            // if not wp.isfinite(q[i][j]) or not wp.isfinite(v[i][j]):                           <L 135>
            var_32 = wp::address(var_q, var_0);
            var_34 = wp::load(var_32);
            var_33 = wp::extract(var_34, var_30);
            var_35 = wp::isfinite(var_33);
            var_36 = wp::unot(var_35);
            var_31 = var_36;
            if (!var_31) {
                var_37 = wp::address(var_v, var_0);
                var_39 = wp::load(var_37);
                var_38 = wp::extract(var_39, var_30);
                var_40 = wp::isfinite(var_38);
                var_41 = wp::unot(var_40);
                var_31 = var_31 || var_41;
            }
            if (var_31) {
                // wp.atomic_max(bad,0,3)                                                         <L 136>
                var_44 = wp::atomic_max(var_bad, var_42, var_43);
            }
            // if not wp.isfinite(q[i][j]) or not wp.isfinite(v[i][j]):                           <L 135>
            var_47 = wp::address(var_q, var_0);
            var_49 = wp::load(var_47);
            var_48 = wp::extract(var_49, var_45);
            var_50 = wp::isfinite(var_48);
            var_51 = wp::unot(var_50);
            var_46 = var_51;
            if (!var_46) {
                var_52 = wp::address(var_v, var_0);
                var_54 = wp::load(var_52);
                var_53 = wp::extract(var_54, var_45);
                var_55 = wp::isfinite(var_53);
                var_56 = wp::unot(var_55);
                var_46 = var_46 || var_56;
            }
            if (var_46) {
                // wp.atomic_max(bad,0,3)                                                         <L 136>
                var_59 = wp::atomic_max(var_bad, var_57, var_58);
            }
            // if not wp.isfinite(q[i][j]) or not wp.isfinite(v[i][j]):                           <L 135>
            var_62 = wp::address(var_q, var_0);
            var_64 = wp::load(var_62);
            var_63 = wp::extract(var_64, var_60);
            var_65 = wp::isfinite(var_63);
            var_66 = wp::unot(var_65);
            var_61 = var_66;
            if (!var_61) {
                var_67 = wp::address(var_v, var_0);
                var_69 = wp::load(var_67);
                var_68 = wp::extract(var_69, var_60);
                var_70 = wp::isfinite(var_68);
                var_71 = wp::unot(var_70);
                var_61 = var_61 || var_71;
            }
            if (var_61) {
                // wp.atomic_max(bad,0,3)                                                         <L 136>
                var_74 = wp::atomic_max(var_bad, var_72, var_73);
            }
        }
    }
}



extern "C" __global__ void mass_residual_285f6480_cuda_kernel_forward(
    wp::launch_bounds_t<1> dim,
    wp::array_t<wp::int32> var_ptr,
    wp::array_t<wp::int32> var_ids,
    wp::array_t<wp::float64> var_values,
    wp::array_t<wp::vec_t<3, wp::float64>> var_a,
    wp::array_t<wp::vec_t<3, wp::float64>> var_f,
    wp::array_t<wp::vec_t<3, wp::float64>> var_r,
    wp::array_t<wp::float64> var_error2,
    wp::array_t<wp::float64> var_scale2)
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
        wp::float64 var_1;
        wp::vec_t<3, wp::float64> var_2;
        wp::int32* var_3;
        const wp::int32 var_4 = 1;
        wp::int32 var_5;
        wp::int32* var_6;
        wp::range_t var_7;
        wp::int32 var_8;
        wp::int32 var_9;
        wp::int32 var_10;
        wp::float64* var_11;
        wp::int32* var_12;
        wp::vec_t<3, wp::float64>* var_13;
        wp::int32 var_14;
        wp::vec_t<3, wp::float64> var_15;
        wp::float64 var_16;
        wp::vec_t<3, wp::float64> var_17;
        wp::vec_t<3, wp::float64> var_18;
        wp::vec_t<3, wp::float64>* var_19;
        wp::vec_t<3, wp::float64> var_20;
        wp::vec_t<3, wp::float64> var_21;
        wp::vec_t<3, wp::float64>* var_22;
        wp::vec_t<3, wp::float64> var_23;
        wp::vec_t<3, wp::float64> var_24;
        wp::float64 var_25;
        wp::vec_t<3, wp::float64>* var_26;
        wp::vec_t<3, wp::float64>* var_27;
        wp::vec_t<3, wp::float64> var_28;
        wp::vec_t<3, wp::float64> var_29;
        wp::vec_t<3, wp::float64> var_30;
        wp::vec_t<3, wp::float64>* var_31;
        wp::vec_t<3, wp::float64>* var_32;
        wp::vec_t<3, wp::float64> var_33;
        wp::vec_t<3, wp::float64> var_34;
        wp::vec_t<3, wp::float64> var_35;
        wp::float64 var_36;
        //---------
        // forward
        // def mass_residual(ptr: wp.array(dtype=int), ids: wp.array(dtype=int), values: wp.array(dtype=wp.float64),       <L 88>
        // i = wp.tid()                                                                           <L 91>
        var_0 = builtin_tid1d();
        // ma = wp.vec3d(wp.float64(0.0))                                                         <L 92>
        var_1 = 0.0;
        var_2 = wp::vec_t<3, wp::float64>(var_1);
        // for e in range(ptr[i],ptr[i+1]):                                                       <L 93>
        var_3 = wp::address(var_ptr, var_0);
        var_5 = wp::add(var_0, var_4);
        var_6 = wp::address(var_ptr, var_5);
        var_8 = wp::load(var_3);
        var_9 = wp::load(var_6);
        var_7 = wp::range(var_8, var_9);
        start_for_0:;
            if (iter_cmp(var_7) == 0) goto end_for_0;
            var_10 = wp::iter_next(var_7);
            // ma += values[e]*a[ids[e]]                                                          <L 94>
            var_11 = wp::address(var_values, var_10);
            var_12 = wp::address(var_ids, var_10);
            var_14 = wp::load(var_12);
            var_13 = wp::address(var_a, var_14);
            var_16 = wp::load(var_11);
            var_17 = wp::load(var_13);
            var_15 = wp::mul(var_16, var_17);
            var_18 = wp::add(var_2, var_15);
            wp::assign(var_2, var_18);
            goto start_for_0;
        end_for_0:;
        // residual = ma-f[i]-r[i]                                                                <L 95>
        var_19 = wp::address(var_f, var_0);
        var_21 = wp::load(var_19);
        var_20 = wp::sub(var_2, var_21);
        var_22 = wp::address(var_r, var_0);
        var_24 = wp::load(var_22);
        var_23 = wp::sub(var_20, var_24);
        // error2[i] = wp.dot(residual,residual)                                                  <L 96>
        var_25 = wp::dot(var_23, var_23);
        wp::array_store(var_error2, var_0, var_25);
        // scale2[i] = wp.dot(f[i]+r[i],f[i]+r[i])                                                <L 97>
        var_26 = wp::address(var_f, var_0);
        var_27 = wp::address(var_r, var_0);
        var_29 = wp::load(var_26);
        var_30 = wp::load(var_27);
        var_28 = wp::add(var_29, var_30);
        var_31 = wp::address(var_f, var_0);
        var_32 = wp::address(var_r, var_0);
        var_34 = wp::load(var_31);
        var_35 = wp::load(var_32);
        var_33 = wp::add(var_34, var_35);
        var_36 = wp::dot(var_28, var_33);
        wp::array_store(var_scale2, var_0, var_36);
    }
}



extern "C" __global__ void force_partial_5a145249_cuda_kernel_forward(
    wp::launch_bounds_t<2> dim,
    wp::array_t<wp::int32> var_ptr,
    wp::array_t<wp::int32> var_ids,
    wp::array_t<wp::vec_t<3, wp::float64>> var_grad,
    wp::array_t<wp::mat_t<3, 3, wp::float64>> var_Pvol,
    wp::array_t<wp::vec_t<3, wp::float64>> var_partial)
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
        wp::int32 var_1;
        wp::float64 var_2;
        wp::vec_t<3, wp::float64> var_3;
        wp::int32* var_4;
        wp::int32 var_5;
        wp::int32 var_6;
        const wp::int32 var_7 = 1;
        wp::int32 var_8;
        wp::int32* var_9;
        const wp::int32 var_10 = 32;
        wp::range_t var_11;
        wp::int32 var_12;
        wp::int32 var_13;
        wp::int32* var_14;
        wp::mat_t<3, 3, wp::float64>* var_15;
        wp::int32 var_16;
        wp::vec_t<3, wp::float64>* var_17;
        wp::vec_t<3, wp::float64> var_18;
        wp::mat_t<3, 3, wp::float64> var_19;
        wp::vec_t<3, wp::float64> var_20;
        wp::vec_t<3, wp::float64> var_21;
        //---------
        // forward
        // def force_partial(ptr: wp.array(dtype=int), ids: wp.array(dtype=int), grad: wp.array(dtype=wp.vec3d),       <L 47>
        // i, lane = wp.tid()                                                                     <L 49>
        builtin_tid2d(var_0, var_1);
        // f = wp.vec3d(wp.float64(0.0))                                                          <L 50>
        var_2 = 0.0;
        var_3 = wp::vec_t<3, wp::float64>(var_2);
        // for e in range(ptr[i]+lane,ptr[i+1],32):                                               <L 51>
        var_4 = wp::address(var_ptr, var_0);
        var_6 = wp::load(var_4);
        var_5 = wp::add(var_6, var_1);
        var_8 = wp::add(var_0, var_7);
        var_9 = wp::address(var_ptr, var_8);
        var_12 = wp::load(var_9);
        var_11 = wp::range(var_5, var_12, var_10);
        start_for_0:;
            if (iter_cmp(var_11) == 0) goto end_for_0;
            var_13 = wp::iter_next(var_11);
            // f -= Pvol[ids[e]]*grad[e]                                                          <L 52>
            var_14 = wp::address(var_ids, var_13);
            var_16 = wp::load(var_14);
            var_15 = wp::address(var_Pvol, var_16);
            var_17 = wp::address(var_grad, var_13);
            var_19 = wp::load(var_15);
            var_20 = wp::load(var_17);
            var_18 = wp::mul(var_19, var_20);
            var_21 = wp::sub(var_3, var_18);
            wp::assign(var_3, var_21);
            goto start_for_0;
        end_for_0:;
        // partial[i,lane] = f                                                                    <L 53>
        wp::array_store(var_partial, var_0, var_1, var_3);
    }
}



extern "C" __global__ void mass_guard_5c58cec1_cuda_kernel_forward(
    wp::launch_bounds_t<1> dim,
    wp::array_t<wp::int32> var_ptr,
    wp::array_t<wp::float64> var_err,
    wp::array_t<wp::float64> var_scale,
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
        wp::float64 var_1;
        wp::float64 var_2;
        wp::int32* var_3;
        const wp::int32 var_4 = 1;
        wp::int32 var_5;
        wp::int32* var_6;
        wp::range_t var_7;
        wp::int32 var_8;
        wp::int32 var_9;
        wp::int32 var_10;
        wp::float64* var_11;
        wp::float64 var_12;
        wp::float64 var_13;
        wp::float64* var_14;
        wp::float64 var_15;
        wp::float64 var_16;
        bool var_17;
        bool var_18;
        bool var_19;
        bool var_20;
        bool var_21;
        wp::float64 var_22;
        wp::float64 var_23;
        wp::float64 var_24;
        wp::float64 var_25;
        bool var_26;
        const wp::int32 var_27 = 0;
        const wp::int32 var_28 = 2;
        wp::int32 var_29;
        //---------
        // forward
        // def mass_guard(ptr: wp.array(dtype=int), err: wp.array(dtype=wp.float64), scale: wp.array(dtype=wp.float64),       <L 101>
        // piece = wp.tid()                                                                       <L 103>
        var_0 = builtin_tid1d();
        // e = wp.float64(0.0)                                                                    <L 104>
        var_1 = 0.0;
        // s = wp.float64(0.0)                                                                    <L 105>
        var_2 = 0.0;
        // for i in range(ptr[piece],ptr[piece+1]):                                               <L 106>
        var_3 = wp::address(var_ptr, var_0);
        var_5 = wp::add(var_0, var_4);
        var_6 = wp::address(var_ptr, var_5);
        var_8 = wp::load(var_3);
        var_9 = wp::load(var_6);
        var_7 = wp::range(var_8, var_9);
        start_for_0:;
            if (iter_cmp(var_7) == 0) goto end_for_0;
            var_10 = wp::iter_next(var_7);
            // e += err[i]                                                                        <L 107>
            var_11 = wp::address(var_err, var_10);
            var_13 = wp::load(var_11);
            var_12 = wp::add(var_1, var_13);
            // s += scale[i]                                                                      <L 108>
            var_14 = wp::address(var_scale, var_10);
            var_16 = wp::load(var_14);
            var_15 = wp::add(var_2, var_16);
            wp::assign(var_1, var_12);
            wp::assign(var_2, var_15);
            goto start_for_0;
        end_for_0:;
        // if not wp.isfinite(e) or not wp.isfinite(s) or e > wp.float64(1e-14)*wp.max(s,wp.float64(1e-24)):       <L 109>
        var_18 = wp::isfinite(var_1);
        var_19 = wp::unot(var_18);
        var_17 = var_19;
        if (!var_17) {
            var_20 = wp::isfinite(var_2);
            var_21 = wp::unot(var_20);
            var_17 = var_17 || var_21;
        }
        if (!var_17) {
            var_22 = 1e-14;
            var_23 = 1e-24;
            var_24 = wp::max(var_2, var_23);
            var_25 = wp::mul(var_22, var_24);
            var_26 = (var_1 > var_25);
            var_17 = var_17 || var_26;
        }
        if (var_17) {
            // wp.atomic_max(bad,0,2)                                                             <L 110>
            var_29 = wp::atomic_max(var_bad, var_27, var_28);
        }
    }
}



extern "C" __global__ void solve_930130d1_cuda_kernel_forward(
    wp::launch_bounds_t<1> dim,
    wp::array_t<wp::int32> var_ptr,
    wp::array_t<wp::int32> var_ids,
    wp::array_t<wp::float64> var_values,
    wp::array_t<wp::int32> var_rptr,
    wp::array_t<wp::int32> var_rids,
    wp::array_t<wp::float64> var_rvalues,
    wp::array_t<wp::vec_t<3, wp::float64>> var_f,
    wp::array_t<wp::vec_t<3, wp::float64>> var_a,
    wp::array_t<wp::vec_t<3, wp::float64>> var_r)
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
        wp::float64 var_1;
        wp::vec_t<3, wp::float64> var_2;
        wp::float64 var_3;
        wp::vec_t<3, wp::float64> var_4;
        wp::int32* var_5;
        const wp::int32 var_6 = 1;
        wp::int32 var_7;
        wp::int32* var_8;
        wp::range_t var_9;
        wp::int32 var_10;
        wp::int32 var_11;
        wp::int32 var_12;
        wp::float64* var_13;
        wp::int32* var_14;
        wp::vec_t<3, wp::float64>* var_15;
        wp::int32 var_16;
        wp::vec_t<3, wp::float64> var_17;
        wp::float64 var_18;
        wp::vec_t<3, wp::float64> var_19;
        wp::vec_t<3, wp::float64> var_20;
        wp::int32* var_21;
        const wp::int32 var_22 = 1;
        wp::int32 var_23;
        wp::int32* var_24;
        wp::range_t var_25;
        wp::int32 var_26;
        wp::int32 var_27;
        wp::int32 var_28;
        wp::float64* var_29;
        wp::int32* var_30;
        wp::vec_t<3, wp::float64>* var_31;
        wp::int32 var_32;
        wp::vec_t<3, wp::float64> var_33;
        wp::float64 var_34;
        wp::vec_t<3, wp::float64> var_35;
        wp::vec_t<3, wp::float64> var_36;
        //---------
        // forward
        // def solve(ptr: wp.array(dtype=int), ids: wp.array(dtype=int), values: wp.array(dtype=wp.float64),       <L 73>
        // i = wp.tid()                                                                           <L 76>
        var_0 = builtin_tid1d();
        // aa = wp.vec3d(wp.float64(0.0))                                                         <L 77>
        var_1 = 0.0;
        var_2 = wp::vec_t<3, wp::float64>(var_1);
        // rr = wp.vec3d(wp.float64(0.0))                                                         <L 78>
        var_3 = 0.0;
        var_4 = wp::vec_t<3, wp::float64>(var_3);
        // for e in range(ptr[i], ptr[i+1]):                                                      <L 79>
        var_5 = wp::address(var_ptr, var_0);
        var_7 = wp::add(var_0, var_6);
        var_8 = wp::address(var_ptr, var_7);
        var_10 = wp::load(var_5);
        var_11 = wp::load(var_8);
        var_9 = wp::range(var_10, var_11);
        start_for_0:;
            if (iter_cmp(var_9) == 0) goto end_for_0;
            var_12 = wp::iter_next(var_9);
            // aa += values[e]*f[ids[e]]                                                          <L 80>
            var_13 = wp::address(var_values, var_12);
            var_14 = wp::address(var_ids, var_12);
            var_16 = wp::load(var_14);
            var_15 = wp::address(var_f, var_16);
            var_18 = wp::load(var_13);
            var_19 = wp::load(var_15);
            var_17 = wp::mul(var_18, var_19);
            var_20 = wp::add(var_2, var_17);
            wp::assign(var_2, var_20);
            goto start_for_0;
        end_for_0:;
        // for e in range(rptr[i], rptr[i+1]):                                                    <L 81>
        var_21 = wp::address(var_rptr, var_0);
        var_23 = wp::add(var_0, var_22);
        var_24 = wp::address(var_rptr, var_23);
        var_26 = wp::load(var_21);
        var_27 = wp::load(var_24);
        var_25 = wp::range(var_26, var_27);
        start_for_2:;
            if (iter_cmp(var_25) == 0) goto end_for_2;
            var_28 = wp::iter_next(var_25);
            // rr += rvalues[e]*f[rids[e]]                                                        <L 82>
            var_29 = wp::address(var_rvalues, var_28);
            var_30 = wp::address(var_rids, var_28);
            var_32 = wp::load(var_30);
            var_31 = wp::address(var_f, var_32);
            var_34 = wp::load(var_29);
            var_35 = wp::load(var_31);
            var_33 = wp::mul(var_34, var_35);
            var_36 = wp::add(var_4, var_33);
            wp::assign(var_4, var_36);
            goto start_for_2;
        end_for_2:;
        // a[i] = aa                                                                              <L 83>
        wp::array_store(var_a, var_0, var_2);
        // r[i] = rr                                                                              <L 84>
        wp::array_store(var_r, var_0, var_4);
    }
}



extern "C" __global__ void observation_guard_9f125012_cuda_kernel_forward(
    wp::launch_bounds_t<1> dim,
    wp::array_t<wp::int32> var_ptr,
    wp::array_t<wp::int32> var_ids,
    wp::array_t<wp::vec_t<3, wp::float64>> var_grad,
    wp::array_t<wp::float64> var_weights,
    wp::array_t<wp::int32> var_fixed,
    wp::array_t<wp::vec_t<3, wp::float64>> var_q,
    wp::array_t<wp::vec_t<3, wp::float64>> var_a,
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
        wp::float64 var_1;
        wp::mat_t<3, 3, wp::float64> var_2;
        wp::float64 var_3;
        wp::vec_t<3, wp::float64> var_4;
        wp::int32* var_5;
        const wp::int32 var_6 = 1;
        wp::int32 var_7;
        wp::int32* var_8;
        wp::range_t var_9;
        wp::int32 var_10;
        wp::int32 var_11;
        wp::int32 var_12;
        wp::int32* var_13;
        wp::vec_t<3, wp::float64>* var_14;
        wp::int32 var_15;
        wp::vec_t<3, wp::float64>* var_16;
        wp::mat_t<3, 3, wp::float64> var_17;
        wp::vec_t<3, wp::float64> var_18;
        wp::vec_t<3, wp::float64> var_19;
        wp::mat_t<3, 3, wp::float64> var_20;
        wp::float64* var_21;
        wp::int32* var_22;
        wp::vec_t<3, wp::float64>* var_23;
        wp::int32 var_24;
        wp::vec_t<3, wp::float64> var_25;
        wp::float64 var_26;
        wp::vec_t<3, wp::float64> var_27;
        wp::vec_t<3, wp::float64> var_28;
        wp::float64 var_29;
        bool var_30;
        wp::float64 var_31;
        bool var_32;
        wp::float64 var_33;
        bool var_34;
        bool var_35;
        bool var_36;
        const wp::int32 var_37 = 0;
        const wp::int32 var_38 = 4;
        wp::int32 var_39;
        wp::int32* var_40;
        const wp::int32 var_41 = 0;
        bool var_42;
        wp::int32 var_43;
        const wp::int32 var_44 = 0;
        bool var_45;
        wp::float64 var_46;
        wp::float64 var_47;
        wp::float64 var_48;
        bool var_49;
        wp::float64 var_50;
        bool var_51;
        bool var_52;
        const wp::int32 var_53 = 0;
        const wp::int32 var_54 = 5;
        wp::int32 var_55;
        const wp::int32 var_56 = 1;
        bool var_57;
        wp::float64 var_58;
        wp::float64 var_59;
        wp::float64 var_60;
        bool var_61;
        wp::float64 var_62;
        bool var_63;
        bool var_64;
        const wp::int32 var_65 = 0;
        const wp::int32 var_66 = 5;
        wp::int32 var_67;
        const wp::int32 var_68 = 2;
        bool var_69;
        wp::float64 var_70;
        wp::float64 var_71;
        wp::float64 var_72;
        bool var_73;
        wp::float64 var_74;
        bool var_75;
        bool var_76;
        const wp::int32 var_77 = 0;
        const wp::int32 var_78 = 5;
        wp::int32 var_79;
        //---------
        // forward
        // def observation_guard(ptr: wp.array(dtype=int), ids: wp.array(dtype=int), grad: wp.array(dtype=wp.vec3d),       <L 140>
        // p = wp.tid()                                                                           <L 143>
        var_0 = builtin_tid1d();
        // F = wp.mat33d(wp.float64(0.0))                                                         <L 144>
        var_1 = 0.0;
        var_2 = wp::mat_t<3, 3, wp::float64>(var_1);
        // aa = wp.vec3d(wp.float64(0.0))                                                         <L 145>
        var_3 = 0.0;
        var_4 = wp::vec_t<3, wp::float64>(var_3);
        // for e in range(ptr[p],ptr[p+1]):                                                       <L 146>
        var_5 = wp::address(var_ptr, var_0);
        var_7 = wp::add(var_0, var_6);
        var_8 = wp::address(var_ptr, var_7);
        var_10 = wp::load(var_5);
        var_11 = wp::load(var_8);
        var_9 = wp::range(var_10, var_11);
        start_for_0:;
            if (iter_cmp(var_9) == 0) goto end_for_0;
            var_12 = wp::iter_next(var_9);
            // F += wp.outer(q[ids[e]],grad[e])                                                   <L 147>
            var_13 = wp::address(var_ids, var_12);
            var_15 = wp::load(var_13);
            var_14 = wp::address(var_q, var_15);
            var_16 = wp::address(var_grad, var_12);
            var_18 = wp::load(var_14);
            var_19 = wp::load(var_16);
            var_17 = wp::outer(var_18, var_19);
            var_20 = wp::add(var_2, var_17);
            // aa += weights[e]*a[ids[e]]                                                         <L 148>
            var_21 = wp::address(var_weights, var_12);
            var_22 = wp::address(var_ids, var_12);
            var_24 = wp::load(var_22);
            var_23 = wp::address(var_a, var_24);
            var_26 = wp::load(var_21);
            var_27 = wp::load(var_23);
            var_25 = wp::mul(var_26, var_27);
            var_28 = wp::add(var_4, var_25);
            wp::assign(var_2, var_20);
            wp::assign(var_4, var_28);
            goto start_for_0;
        end_for_0:;
        // J = wp.determinant(F)                                                                  <L 149>
        var_29 = wp::determinant(var_2);
        // if J <= wp.float64(0.1) or J >= wp.float64(10.0) or not wp.isfinite(J):                <L 150>
        var_31 = 0.1;
        var_32 = (var_29 <= var_31);
        var_30 = var_32;
        if (!var_30) {
            var_33 = 10.0;
            var_34 = (var_29 >= var_33);
            var_30 = var_30 || var_34;
        }
        if (!var_30) {
            var_35 = wp::isfinite(var_29);
            var_36 = wp::unot(var_35);
            var_30 = var_30 || var_36;
        }
        if (var_30) {
            // wp.atomic_max(bad,0,4)                                                             <L 151>
            var_39 = wp::atomic_max(var_bad, var_37, var_38);
        }
        // if fixed[p] != 0:                                                                      <L 152>
        var_40 = wp::address(var_fixed, var_0);
        var_43 = wp::load(var_40);
        var_42 = (var_43 != var_41);
        if (var_42) {
            // for j in range(3):                                                                 <L 153>
            // if wp.abs(aa[j]) > wp.float64(1e-6) or not wp.isfinite(aa[j]):                     <L 154>
            var_46 = wp::extract(var_4, var_44);
            var_47 = wp::abs(var_46);
            var_48 = 1e-06;
            var_49 = (var_47 > var_48);
            var_45 = var_49;
            if (!var_45) {
                var_50 = wp::extract(var_4, var_44);
                var_51 = wp::isfinite(var_50);
                var_52 = wp::unot(var_51);
                var_45 = var_45 || var_52;
            }
            if (var_45) {
                // wp.atomic_max(bad,0,5)                                                         <L 155>
                var_55 = wp::atomic_max(var_bad, var_53, var_54);
            }
            // if wp.abs(aa[j]) > wp.float64(1e-6) or not wp.isfinite(aa[j]):                     <L 154>
            var_58 = wp::extract(var_4, var_56);
            var_59 = wp::abs(var_58);
            var_60 = 1e-06;
            var_61 = (var_59 > var_60);
            var_57 = var_61;
            if (!var_57) {
                var_62 = wp::extract(var_4, var_56);
                var_63 = wp::isfinite(var_62);
                var_64 = wp::unot(var_63);
                var_57 = var_57 || var_64;
            }
            if (var_57) {
                // wp.atomic_max(bad,0,5)                                                         <L 155>
                var_67 = wp::atomic_max(var_bad, var_65, var_66);
            }
            // if wp.abs(aa[j]) > wp.float64(1e-6) or not wp.isfinite(aa[j]):                     <L 154>
            var_70 = wp::extract(var_4, var_68);
            var_71 = wp::abs(var_70);
            var_72 = 1e-06;
            var_73 = (var_71 > var_72);
            var_69 = var_73;
            if (!var_69) {
                var_74 = wp::extract(var_4, var_68);
                var_75 = wp::isfinite(var_74);
                var_76 = wp::unot(var_75);
                var_69 = var_69 || var_76;
            }
            if (var_69) {
                // wp.atomic_max(bad,0,5)                                                         <L 155>
                var_79 = wp::atomic_max(var_bad, var_77, var_78);
            }
        }
    }
}



extern "C" __global__ void advance_dc64ba9a_cuda_kernel_forward(
    wp::launch_bounds_t<1> dim,
    wp::array_t<wp::int32> var_clock,
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
        const wp::int32 var_0 = 0;
        wp::int32* var_1;
        const wp::int32 var_2 = 0;
        bool var_3;
        wp::int32 var_4;
        const wp::int32 var_5 = 1;
        const wp::int32 var_6 = 0;
        wp::int32 var_7;
        //---------
        // forward
        // def advance(clock: wp.array(dtype=int),bad: wp.array(dtype=int)):                      <L 159>
        // if bad[0] == 0:                                                                        <L 160>
        var_1 = wp::address(var_bad, var_0);
        var_4 = wp::load(var_1);
        var_3 = (var_4 == var_2);
        if (var_3) {
            // clock[0] += 1                                                                      <L 161>
            var_7 = wp::atomic_add(var_clock, var_6, var_5);
        }
    }
}



extern "C" __global__ void stress_e9a9511f_cuda_kernel_forward(
    wp::launch_bounds_t<1> dim,
    wp::array_t<wp::int32> var_ptr,
    wp::array_t<wp::int32> var_ids,
    wp::array_t<wp::vec_t<3, wp::float64>> var_grad,
    wp::array_t<wp::vec_t<3, wp::float64>> var_q,
    wp::array_t<wp::float64> var_vol,
    wp::float64 var_mu,
    wp::float64 var_lam,
    wp::array_t<wp::mat_t<3, 3, wp::float64>> var_Pvol,
    wp::array_t<wp::float64> var_energy,
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
        wp::float64 var_1;
        wp::mat_t<3, 3, wp::float64> var_2;
        wp::int32* var_3;
        const wp::int32 var_4 = 1;
        wp::int32 var_5;
        wp::int32* var_6;
        wp::range_t var_7;
        wp::int32 var_8;
        wp::int32 var_9;
        wp::int32 var_10;
        wp::int32* var_11;
        wp::vec_t<3, wp::float64>* var_12;
        wp::int32 var_13;
        wp::vec_t<3, wp::float64>* var_14;
        wp::mat_t<3, 3, wp::float64> var_15;
        wp::vec_t<3, wp::float64> var_16;
        wp::vec_t<3, wp::float64> var_17;
        wp::mat_t<3, 3, wp::float64> var_18;
        wp::float64 var_19;
        bool var_20;
        wp::float64 var_21;
        bool var_22;
        wp::float64 var_23;
        bool var_24;
        bool var_25;
        bool var_26;
        const wp::int32 var_27 = 0;
        const wp::int32 var_28 = 1;
        wp::int32 var_29;
        wp::float64 var_30;
        wp::mat_t<3, 3, wp::float64> var_31;
        wp::float64 var_32;
        wp::float64 var_33;
        wp::float64* var_34;
        wp::mat_t<3, 3, wp::float64> var_35;
        wp::float64 var_36;
        wp::float64 var_37;
        wp::mat_t<3, 3, wp::float64> var_38;
        wp::mat_t<3, 3, wp::float64> var_39;
        wp::mat_t<3, 3, wp::float64> var_40;
        wp::mat_t<3, 3, wp::float64> var_41;
        wp::mat_t<3, 3, wp::float64> var_42;
        wp::float64 var_43;
        wp::float64 var_44;
        const wp::int32 var_45 = 0;
        const wp::int32 var_46 = 0;
        wp::float64 var_47;
        wp::float64 var_48;
        wp::float64 var_49;
        wp::float64 var_50;
        const wp::int32 var_51 = 1;
        wp::float64 var_52;
        wp::float64 var_53;
        wp::float64 var_54;
        wp::float64 var_55;
        const wp::int32 var_56 = 2;
        wp::float64 var_57;
        wp::float64 var_58;
        wp::float64 var_59;
        wp::float64 var_60;
        const wp::int32 var_61 = 1;
        const wp::int32 var_62 = 0;
        wp::float64 var_63;
        wp::float64 var_64;
        wp::float64 var_65;
        wp::float64 var_66;
        const wp::int32 var_67 = 1;
        wp::float64 var_68;
        wp::float64 var_69;
        wp::float64 var_70;
        wp::float64 var_71;
        const wp::int32 var_72 = 2;
        wp::float64 var_73;
        wp::float64 var_74;
        wp::float64 var_75;
        wp::float64 var_76;
        const wp::int32 var_77 = 2;
        const wp::int32 var_78 = 0;
        wp::float64 var_79;
        wp::float64 var_80;
        wp::float64 var_81;
        wp::float64 var_82;
        const wp::int32 var_83 = 1;
        wp::float64 var_84;
        wp::float64 var_85;
        wp::float64 var_86;
        wp::float64 var_87;
        const wp::int32 var_88 = 2;
        wp::float64 var_89;
        wp::float64 var_90;
        wp::float64 var_91;
        wp::float64 var_92;
        wp::float64* var_93;
        wp::float64 var_94;
        wp::float64 var_95;
        wp::float64 var_96;
        wp::float64 var_97;
        wp::float64 var_98;
        wp::float64 var_99;
        wp::float64 var_100;
        wp::float64 var_101;
        wp::float64 var_102;
        wp::float64 var_103;
        wp::float64 var_104;
        wp::float64 var_105;
        wp::float64 var_106;
        wp::float64 var_107;
        //---------
        // forward
        // def stress(ptr: wp.array(dtype=int), ids: wp.array(dtype=int), grad: wp.array(dtype=wp.vec3d),       <L 6>
        // p = wp.tid()                                                                           <L 10>
        var_0 = builtin_tid1d();
        // F = wp.mat33d(wp.float64(0.0))                                                         <L 11>
        var_1 = 0.0;
        var_2 = wp::mat_t<3, 3, wp::float64>(var_1);
        // for e in range(ptr[p], ptr[p+1]):                                                      <L 12>
        var_3 = wp::address(var_ptr, var_0);
        var_5 = wp::add(var_0, var_4);
        var_6 = wp::address(var_ptr, var_5);
        var_8 = wp::load(var_3);
        var_9 = wp::load(var_6);
        var_7 = wp::range(var_8, var_9);
        start_for_0:;
            if (iter_cmp(var_7) == 0) goto end_for_0;
            var_10 = wp::iter_next(var_7);
            // F += wp.outer(q[ids[e]], grad[e])                                                  <L 13>
            var_11 = wp::address(var_ids, var_10);
            var_13 = wp::load(var_11);
            var_12 = wp::address(var_q, var_13);
            var_14 = wp::address(var_grad, var_10);
            var_16 = wp::load(var_12);
            var_17 = wp::load(var_14);
            var_15 = wp::outer(var_16, var_17);
            var_18 = wp::add(var_2, var_15);
            wp::assign(var_2, var_18);
            goto start_for_0;
        end_for_0:;
        // J = wp.determinant(F)                                                                  <L 14>
        var_19 = wp::determinant(var_2);
        // if J <= wp.float64(0.1) or J >= wp.float64(10.0) or not wp.isfinite(J):                <L 15>
        var_21 = 0.1;
        var_22 = (var_19 <= var_21);
        var_20 = var_22;
        if (!var_20) {
            var_23 = 10.0;
            var_24 = (var_19 >= var_23);
            var_20 = var_20 || var_24;
        }
        if (!var_20) {
            var_25 = wp::isfinite(var_19);
            var_26 = wp::unot(var_25);
            var_20 = var_20 || var_26;
        }
        if (var_20) {
            // wp.atomic_max(bad, 0, 1)                                                           <L 16>
            var_29 = wp::atomic_max(var_bad, var_27, var_28);
            // Pvol[p] = wp.mat33d(wp.float64(0.0))                                               <L 17>
            var_30 = 0.0;
            var_31 = wp::mat_t<3, 3, wp::float64>(var_30);
            wp::array_store(var_Pvol, var_0, var_31);
            // energy[p] = wp.float64(0.0)                                                        <L 18>
            var_32 = 0.0;
            wp::array_store(var_energy, var_0, var_32);
        }
        if (!var_20) {
            // lnJ = wp.log(J)                                                                    <L 20>
            var_33 = wp::log(var_19);
            // Pvol[p] = vol[p] * (mu*F + (lam*lnJ-mu)*wp.transpose(wp.inverse(F)))               <L 21>
            var_34 = wp::address(var_vol, var_0);
            var_35 = wp::mul(var_mu, var_2);
            var_36 = wp::mul(var_lam, var_33);
            var_37 = wp::sub(var_36, var_mu);
            var_38 = wp::inverse(var_2);
            var_39 = wp::transpose(var_38);
            var_40 = wp::mul(var_37, var_39);
            var_41 = wp::add(var_35, var_40);
            var_43 = wp::load(var_34);
            var_42 = wp::mul(var_43, var_41);
            wp::array_store(var_Pvol, var_0, var_42);
            // norm2 = wp.float64(0.0)                                                            <L 22>
            var_44 = 0.0;
            // for i in range(3):                                                                 <L 23>
            // for j in range(3):                                                                 <L 24>
            // norm2 += F[i,j]*F[i,j]                                                             <L 25>
            var_47 = wp::extract(var_2, var_45, var_46);
            var_48 = wp::extract(var_2, var_45, var_46);
            var_49 = wp::mul(var_47, var_48);
            var_50 = wp::add(var_44, var_49);
            var_52 = wp::extract(var_2, var_45, var_51);
            var_53 = wp::extract(var_2, var_45, var_51);
            var_54 = wp::mul(var_52, var_53);
            var_55 = wp::add(var_50, var_54);
            var_57 = wp::extract(var_2, var_45, var_56);
            var_58 = wp::extract(var_2, var_45, var_56);
            var_59 = wp::mul(var_57, var_58);
            var_60 = wp::add(var_55, var_59);
            // for j in range(3):                                                                 <L 24>
            // norm2 += F[i,j]*F[i,j]                                                             <L 25>
            var_63 = wp::extract(var_2, var_61, var_62);
            var_64 = wp::extract(var_2, var_61, var_62);
            var_65 = wp::mul(var_63, var_64);
            var_66 = wp::add(var_60, var_65);
            var_68 = wp::extract(var_2, var_61, var_67);
            var_69 = wp::extract(var_2, var_61, var_67);
            var_70 = wp::mul(var_68, var_69);
            var_71 = wp::add(var_66, var_70);
            var_73 = wp::extract(var_2, var_61, var_72);
            var_74 = wp::extract(var_2, var_61, var_72);
            var_75 = wp::mul(var_73, var_74);
            var_76 = wp::add(var_71, var_75);
            // for j in range(3):                                                                 <L 24>
            // norm2 += F[i,j]*F[i,j]                                                             <L 25>
            var_79 = wp::extract(var_2, var_77, var_78);
            var_80 = wp::extract(var_2, var_77, var_78);
            var_81 = wp::mul(var_79, var_80);
            var_82 = wp::add(var_76, var_81);
            var_84 = wp::extract(var_2, var_77, var_83);
            var_85 = wp::extract(var_2, var_77, var_83);
            var_86 = wp::mul(var_84, var_85);
            var_87 = wp::add(var_82, var_86);
            var_89 = wp::extract(var_2, var_77, var_88);
            var_90 = wp::extract(var_2, var_77, var_88);
            var_91 = wp::mul(var_89, var_90);
            var_92 = wp::add(var_87, var_91);
            // energy[p] = vol[p]*(wp.float64(0.5)*mu*(norm2-wp.float64(3.0))-mu*lnJ+wp.float64(0.5)*lam*lnJ*lnJ)       <L 26>
            var_93 = wp::address(var_vol, var_0);
            var_94 = 0.5;
            var_95 = wp::mul(var_94, var_mu);
            var_96 = 3.0;
            var_97 = wp::sub(var_92, var_96);
            var_98 = wp::mul(var_95, var_97);
            var_99 = wp::mul(var_mu, var_33);
            var_100 = wp::sub(var_98, var_99);
            var_101 = 0.5;
            var_102 = wp::mul(var_101, var_lam);
            var_103 = wp::mul(var_102, var_33);
            var_104 = wp::mul(var_103, var_33);
            var_105 = wp::add(var_100, var_104);
            var_107 = wp::load(var_93);
            var_106 = wp::mul(var_107, var_105);
            wp::array_store(var_energy, var_0, var_106);
        }
    }
}



extern "C" __global__ void drift_fcc07267_cuda_kernel_forward(
    wp::launch_bounds_t<1> dim,
    wp::array_t<wp::vec_t<3, wp::float64>> var_q,
    wp::array_t<wp::vec_t<3, wp::float64>> var_v,
    wp::array_t<wp::vec_t<3, wp::float64>> var_a,
    wp::array_t<wp::vec_t<3, wp::float64>> var_r,
    wp::array_t<wp::float64> var_translation,
    wp::float64 var_dt,
    wp::array_t<wp::vec_t<3, wp::float64>> var_impulse,
    wp::array_t<wp::vec_t<3, wp::float64>> var_moment,
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
        const wp::int32 var_1 = 0;
        wp::int32* var_2;
        const wp::int32 var_3 = 0;
        bool var_4;
        wp::int32 var_5;
        wp::float64 var_6;
        wp::float64 var_7;
        wp::float64* var_8;
        wp::float64 var_9;
        wp::float64 var_10;
        wp::vec_t<3, wp::float64>* var_11;
        wp::vec_t<3, wp::float64> var_12;
        wp::vec_t<3, wp::float64> var_13;
        wp::vec_t<3, wp::float64> var_14;
        wp::float64 var_15;
        wp::float64 var_16;
        wp::vec_t<3, wp::float64>* var_17;
        wp::vec_t<3, wp::float64>* var_18;
        wp::vec_t<3, wp::float64> var_19;
        wp::vec_t<3, wp::float64> var_20;
        wp::vec_t<3, wp::float64> var_21;
        wp::vec_t<3, wp::float64> var_22;
        wp::vec_t<3, wp::float64> var_23;
        wp::float64 var_24;
        wp::float64 var_25;
        wp::vec_t<3, wp::float64>* var_26;
        wp::vec_t<3, wp::float64> var_27;
        wp::vec_t<3, wp::float64> var_28;
        wp::vec_t<3, wp::float64> var_29;
        wp::vec_t<3, wp::float64>* var_30;
        wp::vec_t<3, wp::float64> var_31;
        wp::vec_t<3, wp::float64> var_32;
        wp::vec_t<3, wp::float64> var_33;
        //---------
        // forward
        // def drift(q: wp.array(dtype=wp.vec3d), v: wp.array(dtype=wp.vec3d), a: wp.array(dtype=wp.vec3d),       <L 114>
        // i = wp.tid()                                                                           <L 117>
        var_0 = builtin_tid1d();
        // if bad[0] == 0:                                                                        <L 118>
        var_2 = wp::address(var_bad, var_1);
        var_5 = wp::load(var_2);
        var_4 = (var_5 == var_3);
        if (var_4) {
            // impulse[i] += wp.float64(0.5)*dt*translation[i]*r[i]                               <L 119>
            var_6 = 0.5;
            var_7 = wp::mul(var_6, var_dt);
            var_8 = wp::address(var_translation, var_0);
            var_10 = wp::load(var_8);
            var_9 = wp::mul(var_7, var_10);
            var_11 = wp::address(var_r, var_0);
            var_13 = wp::load(var_11);
            var_12 = wp::mul(var_9, var_13);
            var_14 = wp::atomic_add(var_impulse, var_0, var_12);
            // moment[i] += wp.float64(0.5)*dt*wp.cross(q[i],r[i])                                <L 120>
            var_15 = 0.5;
            var_16 = wp::mul(var_15, var_dt);
            var_17 = wp::address(var_q, var_0);
            var_18 = wp::address(var_r, var_0);
            var_20 = wp::load(var_17);
            var_21 = wp::load(var_18);
            var_19 = wp::cross(var_20, var_21);
            var_22 = wp::mul(var_16, var_19);
            var_23 = wp::atomic_add(var_moment, var_0, var_22);
            // v[i] += wp.float64(0.5)*dt*a[i]                                                    <L 121>
            var_24 = 0.5;
            var_25 = wp::mul(var_24, var_dt);
            var_26 = wp::address(var_a, var_0);
            var_28 = wp::load(var_26);
            var_27 = wp::mul(var_25, var_28);
            var_29 = wp::atomic_add(var_v, var_0, var_27);
            // q[i] += dt*v[i]                                                                    <L 122>
            var_30 = wp::address(var_v, var_0);
            var_32 = wp::load(var_30);
            var_31 = wp::mul(var_dt, var_32);
            var_33 = wp::atomic_add(var_q, var_0, var_31);
        }
    }
}



extern "C" __global__ void force_reduce_fe1a055b_cuda_kernel_forward(
    wp::launch_bounds_t<1> dim,
    wp::array_t<wp::vec_t<3, wp::float64>> var_partial,
    wp::array_t<wp::vec_t<3, wp::float64>> var_load,
    wp::array_t<wp::int32> var_clock,
    wp::float64 var_dt,
    wp::float64 var_start_time,
    wp::float64 var_duration,
    wp::int32 var_mode,
    wp::int32 var_stage,
    wp::array_t<wp::vec_t<3, wp::float64>> var_out)
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
        wp::float64 var_1;
        wp::vec_t<3, wp::float64> var_2;
        const wp::int32 var_3 = 32;
        wp::range_t var_4;
        wp::int32 var_5;
        wp::vec_t<3, wp::float64>* var_6;
        wp::vec_t<3, wp::float64> var_7;
        wp::vec_t<3, wp::float64> var_8;
        wp::float64 var_9;
        const wp::int32 var_10 = 1;
        bool var_11;
        const wp::int32 var_12 = 0;
        wp::int32* var_13;
        wp::int32 var_14;
        wp::int32 var_15;
        wp::float64 var_16;
        wp::float64 var_17;
        wp::float64 var_18;
        wp::float64 var_19;
        wp::float64 var_20;
        wp::float64 var_21;
        wp::float64 var_22;
        wp::float64 var_23;
        wp::float64 var_24;
        wp::vec_t<3, wp::float64>* var_25;
        wp::vec_t<3, wp::float64> var_26;
        wp::vec_t<3, wp::float64> var_27;
        wp::vec_t<3, wp::float64> var_28;
        //---------
        // forward
        // def force_reduce(partial: wp.array2d(dtype=wp.vec3d), load: wp.array(dtype=wp.vec3d),       <L 57>
        // i = wp.tid()                                                                           <L 60>
        var_0 = builtin_tid1d();
        // f = wp.vec3d(wp.float64(0.0))                                                          <L 61>
        var_1 = 0.0;
        var_2 = wp::vec_t<3, wp::float64>(var_1);
        // for lane in range(32):                                                                 <L 62>
        var_4 = wp::range(var_3);
        start_for_0:;
            if (iter_cmp(var_4) == 0) goto end_for_0;
            var_5 = wp::iter_next(var_4);
            // f += partial[i,lane]                                                               <L 63>
            var_6 = wp::address(var_partial, var_0, var_5);
            var_8 = wp::load(var_6);
            var_7 = wp::add(var_2, var_8);
            wp::assign(var_2, var_7);
            goto start_for_0;
        end_for_0:;
        // amplitude = wp.float64(1.0)                                                            <L 64>
        var_9 = 1.0;
        // if mode == 1:                                                                          <L 65>
        var_11 = (var_mode == var_10);
        if (var_11) {
            // t = start_time + wp.float64(clock[0]+stage)*dt                                     <L 66>
            var_13 = wp::address(var_clock, var_12);
            var_15 = wp::load(var_13);
            var_14 = wp::add(var_15, var_stage);
            var_16 = wp::float64(var_14);
            var_17 = wp::mul(var_16, var_dt);
            var_18 = wp::add(var_start_time, var_17);
            // value = wp.sin(wp.float64(3.141592653589793)*t/duration)                           <L 67>
            var_19 = 3.141592653589793;
            var_20 = wp::mul(var_19, var_18);
            var_21 = wp::div(var_20, var_duration);
            var_22 = wp::sin(var_21);
            // amplitude = value*value                                                            <L 68>
            var_23 = wp::mul(var_22, var_22);
        }
        var_24 = wp::where(var_11, var_23, var_9);
        // out[i] = f + amplitude*load[i]                                                         <L 69>
        var_25 = wp::address(var_load, var_0);
        var_27 = wp::load(var_25);
        var_26 = wp::mul(var_24, var_27);
        var_28 = wp::add(var_2, var_26);
        wp::array_store(var_out, var_0, var_28);
    }
}


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



extern "C" __global__ void constrained_stage_77be734b_cuda_kernel_forward(
    wp::launch_bounds_t<1> dim,
    wp::array_t<wp::int32> var_mptr,
    wp::array_t<wp::int32> var_mids,
    wp::array_t<wp::float64> var_mass,
    wp::array_t<wp::vec_t<3, wp::float32>> var_force,
    wp::array_t<wp::vec_t<3, wp::float64>> var_acc,
    wp::array_t<wp::vec_t<3, wp::float32>> var_q0,
    wp::array_t<wp::vec_t<3, wp::float32>> var_v0,
    wp::array_t<wp::vec_t<3, wp::float32>> var_q,
    wp::array_t<wp::vec_t<3, wp::float32>> var_v,
    wp::array_t<wp::vec_t<3, wp::float32>> var_dq,
    wp::array_t<wp::vec_t<3, wp::float32>> var_dv,
    wp::array_t<wp::int32> var_fixed,
    wp::array_t<wp::vec_t<3, wp::float32>> var_support,
    wp::float32 var_dt,
    wp::float32 var_weight,
    wp::float32 var_beta,
    wp::int32 var_last,
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
        wp::int32* var_6;
        const wp::int32 var_7 = 0;
        bool var_8;
        wp::int32 var_9;
        wp::vec_t<3, wp::float32>* var_10;
        wp::vec_t<3, wp::float64> var_11;
        wp::vec_t<3, wp::float32> var_12;
        wp::vec_t<3, wp::float64> var_13;
        wp::int32* var_14;
        const wp::int32 var_15 = 1;
        wp::int32 var_16;
        wp::int32* var_17;
        wp::range_t var_18;
        wp::int32 var_19;
        wp::int32 var_20;
        wp::int32 var_21;
        wp::float64* var_22;
        wp::int32* var_23;
        wp::vec_t<3, wp::float64>* var_24;
        wp::int32 var_25;
        wp::vec_t<3, wp::float64> var_26;
        wp::float64 var_27;
        wp::vec_t<3, wp::float64> var_28;
        wp::vec_t<3, wp::float64> var_29;
        wp::float32 var_30;
        wp::vec_t<3, wp::float32> var_31;
        wp::vec_t<3, wp::float32> var_32;
        wp::vec_t<3, wp::float32> var_33;
        wp::vec_t<3, wp::float32>* var_34;
        wp::vec_t<3, wp::float32> var_35;
        const wp::float32 var_36 = 0.0;
        wp::vec_t<3, wp::float32> var_37;
        wp::vec_t<3, wp::float32>* var_38;
        wp::vec_t<3, wp::float32> var_39;
        wp::vec_t<3, wp::float32> var_40;
        wp::vec_t<3, wp::float64>* var_41;
        wp::vec_t<3, wp::float32> var_42;
        wp::vec_t<3, wp::float64> var_43;
        wp::vec_t<3, wp::float32> var_44;
        wp::vec_t<3, wp::float32> var_45;
        wp::vec_t<3, wp::float32> var_46;
        wp::vec_t<3, wp::float32> var_47;
        const wp::int32 var_48 = 0;
        bool var_49;
        wp::vec_t<3, wp::float32>* var_50;
        wp::vec_t<3, wp::float32>* var_51;
        wp::vec_t<3, wp::float32> var_52;
        wp::vec_t<3, wp::float32> var_53;
        wp::vec_t<3, wp::float32> var_54;
        wp::vec_t<3, wp::float32> var_55;
        wp::vec_t<3, wp::float32>* var_56;
        wp::vec_t<3, wp::float32>* var_57;
        wp::vec_t<3, wp::float32> var_58;
        wp::vec_t<3, wp::float32> var_59;
        wp::vec_t<3, wp::float32> var_60;
        wp::vec_t<3, wp::float32> var_61;
        wp::vec_t<3, wp::float32>* var_62;
        wp::float32 var_63;
        wp::vec_t<3, wp::float32> var_64;
        wp::vec_t<3, wp::float32> var_65;
        wp::vec_t<3, wp::float32> var_66;
        wp::vec_t<3, wp::float32>* var_67;
        wp::float32 var_68;
        wp::vec_t<3, wp::float32> var_69;
        wp::vec_t<3, wp::float32> var_70;
        wp::vec_t<3, wp::float32> var_71;
        //---------
        // forward
        // def constrained_stage(mptr:wp.array(dtype=int),mids:wp.array(dtype=int),mass:wp.array(dtype=wp.float64),force:wp.array(dtype=wp.vec3),acc:wp.array(dtype=wp.vec3d),q0:wp.array(dtype=wp.vec3),v0:wp.array(dtype=wp.vec3),q:wp.array(dtype=wp.vec3),v:wp.array(dtype=wp.vec3),dq:wp.array(dtype=wp.vec3),dv:wp.array(dtype=wp.vec3),fixed:wp.array(dtype=int),support:wp.array(dtype=wp.vec3),dt:float,weight:float,beta:float,last:int,bad:wp.array(dtype=int)):       <L 21>
        // i=wp.tid()                                                                             <L 22>
        var_0 = builtin_tid1d();
        // if bad[0]==0:                                                                          <L 23>
        var_2 = wp::address(var_bad, var_1);
        var_5 = wp::load(var_2);
        var_4 = (var_5 == var_3);
        if (var_4) {
            // if fixed[i]!=0:                                                                    <L 24>
            var_6 = wp::address(var_fixed, var_0);
            var_9 = wp::load(var_6);
            var_8 = (var_9 != var_7);
            if (var_8) {
                // reaction=-wp.vec3d(force[i])                                                   <L 25>
                var_10 = wp::address(var_force, var_0);
                var_12 = wp::load(var_10);
                var_11 = wp::vec_t<3, wp::float64>(var_12);
                var_13 = wp::neg(var_11);
                // for j in range(mptr[i],mptr[i+1]):reaction+=mass[j]*acc[mids[j]]               <L 26>
                var_14 = wp::address(var_mptr, var_0);
                var_16 = wp::add(var_0, var_15);
                var_17 = wp::address(var_mptr, var_16);
                var_19 = wp::load(var_14);
                var_20 = wp::load(var_17);
                var_18 = wp::range(var_19, var_20);
                start_for_0:;
                    if (iter_cmp(var_18) == 0) goto end_for_0;
                    var_21 = wp::iter_next(var_18);
                    var_22 = wp::address(var_mass, var_21);
                    var_23 = wp::address(var_mids, var_21);
                    var_25 = wp::load(var_23);
                    var_24 = wp::address(var_acc, var_25);
                    var_27 = wp::load(var_22);
                    var_28 = wp::load(var_24);
                    var_26 = wp::mul(var_27, var_28);
                    var_29 = wp::add(var_13, var_26);
                    wp::assign(var_13, var_29);
                    goto start_for_0;
                end_for_0:;
                // support[i]+=dt*weight*wp.vec3(reaction);q[i]=q0[i];v[i]=wp.vec3(0.)            <L 27>
                var_30 = wp::mul(var_dt, var_weight);
                var_31 = wp::vec_t<3, wp::float32>(var_13);
                var_32 = wp::mul(var_30, var_31);
                var_33 = wp::atomic_add(var_support, var_0, var_32);
                var_34 = wp::address(var_q0, var_0);
                var_35 = wp::load(var_34);
                wp::array_store(var_q, var_0, var_35);
                var_37 = wp::vec_t<3, wp::float32>(var_36);
                wp::array_store(var_v, var_0, var_37);
            }
            if (!var_8) {
                // vel=v[i];a=wp.vec3(acc[i]);dq[i]+=weight*vel;dv[i]+=weight*a                   <L 29>
                var_38 = wp::address(var_v, var_0);
                var_40 = wp::load(var_38);
                var_39 = wp::copy(var_40);
                var_41 = wp::address(var_acc, var_0);
                var_43 = wp::load(var_41);
                var_42 = wp::vec_t<3, wp::float32>(var_43);
                var_44 = wp::mul(var_weight, var_39);
                var_45 = wp::atomic_add(var_dq, var_0, var_44);
                var_46 = wp::mul(var_weight, var_42);
                var_47 = wp::atomic_add(var_dv, var_0, var_46);
                // if last!=0:q[i]=q0[i]+dt*dq[i];v[i]=v0[i]+dt*dv[i]                             <L 30>
                var_49 = (var_last != var_48);
                if (var_49) {
                    var_50 = wp::address(var_q0, var_0);
                    var_51 = wp::address(var_dq, var_0);
                    var_53 = wp::load(var_51);
                    var_52 = wp::mul(var_dt, var_53);
                    var_55 = wp::load(var_50);
                    var_54 = wp::add(var_55, var_52);
                    wp::array_store(var_q, var_0, var_54);
                    var_56 = wp::address(var_v0, var_0);
                    var_57 = wp::address(var_dv, var_0);
                    var_59 = wp::load(var_57);
                    var_58 = wp::mul(var_dt, var_59);
                    var_61 = wp::load(var_56);
                    var_60 = wp::add(var_61, var_58);
                    wp::array_store(var_v, var_0, var_60);
                }
                if (!var_49) {
                    // else:q[i]=q0[i]+beta*dt*vel;v[i]=v0[i]+beta*dt*a                           <L 31>
                    var_62 = wp::address(var_q0, var_0);
                    var_63 = wp::mul(var_beta, var_dt);
                    var_64 = wp::mul(var_63, var_39);
                    var_66 = wp::load(var_62);
                    var_65 = wp::add(var_66, var_64);
                    wp::array_store(var_q, var_0, var_65);
                    var_67 = wp::address(var_v0, var_0);
                    var_68 = wp::mul(var_beta, var_dt);
                    var_69 = wp::mul(var_68, var_42);
                    var_71 = wp::load(var_67);
                    var_70 = wp::add(var_71, var_69);
                    wp::array_store(var_v, var_0, var_70);
                }
            }
        }
    }
}



extern "C" __global__ void acceleration_d4f6c163_cuda_kernel_forward(
    wp::launch_bounds_t<1> dim,
    wp::array_t<wp::int32> var_ptr,
    wp::array_t<wp::int32> var_ids,
    wp::array_t<wp::float64> var_values,
    wp::array_t<wp::vec_t<3, wp::float32>> var_force,
    wp::array_t<wp::vec_t<3, wp::float64>> var_acc,
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
        wp::vec_t<3, wp::float64> var_2;
        const wp::int32 var_3 = 0;
        wp::int32* var_4;
        const wp::int32 var_5 = 0;
        bool var_6;
        wp::int32 var_7;
        wp::int32* var_8;
        const wp::int32 var_9 = 1;
        wp::int32 var_10;
        wp::int32* var_11;
        wp::range_t var_12;
        wp::int32 var_13;
        wp::int32 var_14;
        wp::int32 var_15;
        wp::float64* var_16;
        wp::int32* var_17;
        wp::vec_t<3, wp::float32>* var_18;
        wp::int32 var_19;
        wp::vec_t<3, wp::float64> var_20;
        wp::vec_t<3, wp::float32> var_21;
        wp::vec_t<3, wp::float64> var_22;
        wp::float64 var_23;
        wp::vec_t<3, wp::float64> var_24;
        //---------
        // forward
        // def acceleration(ptr:wp.array(dtype=int),ids:wp.array(dtype=int),values:wp.array(dtype=wp.float64),force:wp.array(dtype=wp.vec3),acc:wp.array(dtype=wp.vec3d),bad:wp.array(dtype=int)):       <L 14>
        // i=wp.tid();a=wp.vec3d(wp.float64(0.))                                                  <L 15>
        var_0 = builtin_tid1d();
        var_1 = 0.0;
        var_2 = wp::vec_t<3, wp::float64>(var_1);
        // if bad[0]==0:                                                                          <L 16>
        var_4 = wp::address(var_bad, var_3);
        var_7 = wp::load(var_4);
        var_6 = (var_7 == var_5);
        if (var_6) {
            // for j in range(ptr[i],ptr[i+1]):a+=values[j]*wp.vec3d(force[ids[j]])               <L 17>
            var_8 = wp::address(var_ptr, var_0);
            var_10 = wp::add(var_0, var_9);
            var_11 = wp::address(var_ptr, var_10);
            var_13 = wp::load(var_8);
            var_14 = wp::load(var_11);
            var_12 = wp::range(var_13, var_14);
            start_for_0:;
                if (iter_cmp(var_12) == 0) goto end_for_0;
                var_15 = wp::iter_next(var_12);
                var_16 = wp::address(var_values, var_15);
                var_17 = wp::address(var_ids, var_15);
                var_19 = wp::load(var_17);
                var_18 = wp::address(var_force, var_19);
                var_21 = wp::load(var_18);
                var_20 = wp::vec_t<3, wp::float64>(var_21);
                var_23 = wp::load(var_16);
                var_22 = wp::mul(var_23, var_20);
                var_24 = wp::add(var_2, var_22);
                wp::assign(var_2, var_24);
                goto start_for_0;
            end_for_0:;
        }
        // acc[i]=a                                                                               <L 18>
        wp::array_store(var_acc, var_0, var_2);
    }
}


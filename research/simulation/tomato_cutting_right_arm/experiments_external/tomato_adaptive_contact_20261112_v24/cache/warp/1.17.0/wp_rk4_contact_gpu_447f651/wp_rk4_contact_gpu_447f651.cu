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



extern "C" __global__ void stage_550bf238_cuda_kernel_forward(
    wp::launch_bounds_t<1> dim,
    wp::array_t<wp::int32> var_ptr,
    wp::array_t<wp::int32> var_ids,
    wp::array_t<wp::float32> var_mi,
    wp::array_t<wp::vec_t<3, wp::float32>> var_force,
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
    wp::int32 var_n,
    wp::array_t<wp::int32> var_bad,
    wp::array_t<wp::float32> var_maxspeed)
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
        wp::float32 var_12;
        wp::vec_t<3, wp::float32>* var_13;
        wp::vec_t<3, wp::float32> var_14;
        wp::vec_t<3, wp::float32> var_15;
        wp::vec_t<3, wp::float32> var_16;
        wp::vec_t<3, wp::float32>* var_17;
        wp::vec_t<3, wp::float32> var_18;
        const wp::float32 var_19 = 0.0;
        wp::vec_t<3, wp::float32> var_20;
        const wp::float32 var_21 = 0.0;
        wp::vec_t<3, wp::float32> var_22;
        wp::int32* var_23;
        const wp::int32 var_24 = 1;
        wp::int32 var_25;
        wp::int32* var_26;
        wp::range_t var_27;
        wp::int32 var_28;
        wp::int32 var_29;
        wp::int32 var_30;
        wp::float32* var_31;
        wp::int32* var_32;
        wp::vec_t<3, wp::float32>* var_33;
        wp::int32 var_34;
        wp::vec_t<3, wp::float32> var_35;
        wp::float32 var_36;
        wp::vec_t<3, wp::float32> var_37;
        wp::vec_t<3, wp::float32> var_38;
        wp::vec_t<3, wp::float32>* var_39;
        wp::vec_t<3, wp::float32> var_40;
        wp::vec_t<3, wp::float32> var_41;
        const wp::int32 var_42 = 0;
        wp::float32 var_43;
        wp::float32 var_44;
        wp::vec_t<3, wp::float32> var_45;
        wp::vec_t<3, wp::float32> var_46;
        wp::vec_t<3, wp::float32> var_47;
        wp::vec_t<3, wp::float32> var_48;
        const wp::int32 var_49 = 0;
        bool var_50;
        wp::vec_t<3, wp::float32>* var_51;
        wp::vec_t<3, wp::float32>* var_52;
        wp::vec_t<3, wp::float32> var_53;
        wp::vec_t<3, wp::float32> var_54;
        wp::vec_t<3, wp::float32> var_55;
        wp::vec_t<3, wp::float32> var_56;
        wp::vec_t<3, wp::float32>* var_57;
        wp::vec_t<3, wp::float32>* var_58;
        wp::vec_t<3, wp::float32> var_59;
        wp::vec_t<3, wp::float32> var_60;
        wp::vec_t<3, wp::float32> var_61;
        wp::vec_t<3, wp::float32> var_62;
        wp::vec_t<3, wp::float32>* var_63;
        wp::float32 var_64;
        wp::vec_t<3, wp::float32> var_65;
        wp::vec_t<3, wp::float32> var_66;
        wp::vec_t<3, wp::float32> var_67;
        wp::vec_t<3, wp::float32>* var_68;
        wp::float32 var_69;
        wp::vec_t<3, wp::float32> var_70;
        wp::vec_t<3, wp::float32> var_71;
        wp::vec_t<3, wp::float32> var_72;
        //---------
        // forward
        // def stage(ptr:wp.array(dtype=int),ids:wp.array(dtype=int),mi:wp.array(dtype=float),force:wp.array(dtype=wp.vec3),q0:wp.array(dtype=wp.vec3),v0:wp.array(dtype=wp.vec3),q:wp.array(dtype=wp.vec3),v:wp.array(dtype=wp.vec3),dq:wp.array(dtype=wp.vec3),dv:wp.array(dtype=wp.vec3),fixed:wp.array(dtype=int),support:wp.array(dtype=wp.vec3),dt:float,weight:float,beta:float,last:int,n:int,bad:wp.array(dtype=int),maxspeed:wp.array(dtype=float)):       <L 11>
        // i=wp.tid()                                                                             <L 12>
        var_0 = builtin_tid1d();
        // if i<n and bad[0]==0:                                                                  <L 13>
        var_2 = (var_0 < var_n);
        var_1 = var_2;
        if (var_1) {
            var_4 = wp::address(var_bad, var_3);
            var_7 = wp::load(var_4);
            var_6 = (var_7 == var_5);
            var_1 = var_1 && var_6;
        }
        if (var_1) {
            // if fixed[i]!=0:support[i]-=dt*weight*force[i];q[i]=q0[i];v[i]=wp.vec3(0.)          <L 14>
            var_8 = wp::address(var_fixed, var_0);
            var_11 = wp::load(var_8);
            var_10 = (var_11 != var_9);
            if (var_10) {
                var_12 = wp::mul(var_dt, var_weight);
                var_13 = wp::address(var_force, var_0);
                var_15 = wp::load(var_13);
                var_14 = wp::mul(var_12, var_15);
                var_16 = wp::atomic_sub(var_support, var_0, var_14);
                var_17 = wp::address(var_q0, var_0);
                var_18 = wp::load(var_17);
                wp::array_store(var_q, var_0, var_18);
                var_20 = wp::vec_t<3, wp::float32>(var_19);
                wp::array_store(var_v, var_0, var_20);
            }
            if (!var_10) {
                // acc=wp.vec3(0.)                                                                <L 16>
                var_22 = wp::vec_t<3, wp::float32>(var_21);
                // for j in range(ptr[i],ptr[i+1]):acc+=mi[j]*force[ids[j]]                       <L 17>
                var_23 = wp::address(var_ptr, var_0);
                var_25 = wp::add(var_0, var_24);
                var_26 = wp::address(var_ptr, var_25);
                var_28 = wp::load(var_23);
                var_29 = wp::load(var_26);
                var_27 = wp::range(var_28, var_29);
                start_for_0:;
                    if (iter_cmp(var_27) == 0) goto end_for_0;
                    var_30 = wp::iter_next(var_27);
                    var_31 = wp::address(var_mi, var_30);
                    var_32 = wp::address(var_ids, var_30);
                    var_34 = wp::load(var_32);
                    var_33 = wp::address(var_force, var_34);
                    var_36 = wp::load(var_31);
                    var_37 = wp::load(var_33);
                    var_35 = wp::mul(var_36, var_37);
                    var_38 = wp::add(var_22, var_35);
                    wp::assign(var_22, var_38);
                    goto start_for_0;
                end_for_0:;
                // vel=v[i];wp.atomic_max(maxspeed,0,wp.length(vel));dq[i]+=weight*vel;dv[i]+=weight*acc       <L 18>
                var_39 = wp::address(var_v, var_0);
                var_41 = wp::load(var_39);
                var_40 = wp::copy(var_41);
                var_43 = wp::length(var_40);
                var_44 = wp::atomic_max(var_maxspeed, var_42, var_43);
                var_45 = wp::mul(var_weight, var_40);
                var_46 = wp::atomic_add(var_dq, var_0, var_45);
                var_47 = wp::mul(var_weight, var_22);
                var_48 = wp::atomic_add(var_dv, var_0, var_47);
                // if last!=0:q[i]=q0[i]+dt*dq[i];v[i]=v0[i]+dt*dv[i]                             <L 19>
                var_50 = (var_last != var_49);
                if (var_50) {
                    var_51 = wp::address(var_q0, var_0);
                    var_52 = wp::address(var_dq, var_0);
                    var_54 = wp::load(var_52);
                    var_53 = wp::mul(var_dt, var_54);
                    var_56 = wp::load(var_51);
                    var_55 = wp::add(var_56, var_53);
                    wp::array_store(var_q, var_0, var_55);
                    var_57 = wp::address(var_v0, var_0);
                    var_58 = wp::address(var_dv, var_0);
                    var_60 = wp::load(var_58);
                    var_59 = wp::mul(var_dt, var_60);
                    var_62 = wp::load(var_57);
                    var_61 = wp::add(var_62, var_59);
                    wp::array_store(var_v, var_0, var_61);
                }
                if (!var_50) {
                    // else:q[i]=q0[i]+beta*dt*vel;v[i]=v0[i]+beta*dt*acc                         <L 20>
                    var_63 = wp::address(var_q0, var_0);
                    var_64 = wp::mul(var_beta, var_dt);
                    var_65 = wp::mul(var_64, var_40);
                    var_67 = wp::load(var_63);
                    var_66 = wp::add(var_67, var_65);
                    wp::array_store(var_q, var_0, var_66);
                    var_68 = wp::address(var_v0, var_0);
                    var_69 = wp::mul(var_beta, var_dt);
                    var_70 = wp::mul(var_69, var_22);
                    var_72 = wp::load(var_68);
                    var_71 = wp::add(var_72, var_70);
                    wp::array_store(var_v, var_0, var_71);
                }
            }
        }
    }
}



extern "C" __global__ void stage_time_d73c079e_cuda_kernel_forward(
    wp::launch_bounds_t<1> dim,
    wp::array_t<wp::float64> var_clock,
    wp::array_t<wp::float64> var_base,
    wp::float64 var_delta,
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
        const wp::int32 var_5 = 0;
        wp::float64* var_6;
        wp::float64 var_7;
        wp::float64 var_8;
        const wp::int32 var_9 = 0;
        //---------
        // forward
        // def stage_time(clock:wp.array(dtype=wp.float64),base:wp.array(dtype=wp.float64),delta:wp.float64,bad:wp.array(dtype=int)):       <L 23>
        // if bad[0]==0:clock[0]=base[0]+delta                                                    <L 24>
        var_1 = wp::address(var_bad, var_0);
        var_4 = wp::load(var_1);
        var_3 = (var_4 == var_2);
        if (var_3) {
            var_6 = wp::address(var_base, var_5);
            var_8 = wp::load(var_6);
            var_7 = wp::add(var_8, var_delta);
            wp::array_store(var_clock, var_9, var_7);
        }
    }
}


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



extern "C" __global__ void ledger_active_a99e87a3_cuda_kernel_forward(
    wp::launch_bounds_t<1> dim,
    wp::array_t<wp::int32> var_n,
    wp::array_t<wp::int32> var_ids,
    wp::array_t<wp::vec_t<3, wp::float32>> var_cf,
    wp::array_t<wp::float32> var_cp,
    wp::array_t<wp::float32> var_power,
    wp::array_t<wp::vec_t<3, wp::float32>> var_moment,
    wp::array_t<wp::vec_t<3, wp::float32>> var_impulse,
    wp::array_t<wp::vec_t<3, wp::float32>> var_angular,
    wp::array_t<wp::float32> var_work,
    wp::array_t<wp::float32> var_diss,
    wp::float32 var_dt,
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
        const wp::int32 var_2 = 0;
        wp::int32* var_3;
        bool var_4;
        wp::int32 var_5;
        const wp::int32 var_6 = 0;
        wp::int32* var_7;
        const wp::int32 var_8 = 0;
        bool var_9;
        wp::int32 var_10;
        const wp::int32 var_11 = 0;
        const wp::int32 var_12 = 3;
        wp::int32* var_13;
        wp::int32 var_14;
        wp::int32 var_15;
        wp::int32 var_16;
        wp::vec_t<3, wp::float32>* var_17;
        wp::vec_t<3, wp::float32> var_18;
        wp::vec_t<3, wp::float32> var_19;
        wp::vec_t<3, wp::float32> var_20;
        wp::vec_t<3, wp::float32>* var_21;
        wp::vec_t<3, wp::float32> var_22;
        wp::vec_t<3, wp::float32> var_23;
        wp::vec_t<3, wp::float32> var_24;
        wp::float32* var_25;
        wp::float32 var_26;
        wp::float32 var_27;
        wp::float32 var_28;
        wp::float32* var_29;
        wp::float32 var_30;
        wp::float32 var_31;
        wp::float32 var_32;
        const wp::int32 var_33 = 1;
        const wp::int32 var_34 = 3;
        wp::int32* var_35;
        wp::int32 var_36;
        wp::int32 var_37;
        wp::int32 var_38;
        wp::vec_t<3, wp::float32>* var_39;
        wp::vec_t<3, wp::float32> var_40;
        wp::vec_t<3, wp::float32> var_41;
        wp::vec_t<3, wp::float32> var_42;
        wp::vec_t<3, wp::float32>* var_43;
        wp::vec_t<3, wp::float32> var_44;
        wp::vec_t<3, wp::float32> var_45;
        wp::vec_t<3, wp::float32> var_46;
        wp::float32* var_47;
        wp::float32 var_48;
        wp::float32 var_49;
        wp::float32 var_50;
        wp::float32* var_51;
        wp::float32 var_52;
        wp::float32 var_53;
        wp::float32 var_54;
        const wp::int32 var_55 = 2;
        const wp::int32 var_56 = 3;
        wp::int32* var_57;
        wp::int32 var_58;
        wp::int32 var_59;
        wp::int32 var_60;
        wp::vec_t<3, wp::float32>* var_61;
        wp::vec_t<3, wp::float32> var_62;
        wp::vec_t<3, wp::float32> var_63;
        wp::vec_t<3, wp::float32> var_64;
        wp::vec_t<3, wp::float32>* var_65;
        wp::vec_t<3, wp::float32> var_66;
        wp::vec_t<3, wp::float32> var_67;
        wp::vec_t<3, wp::float32> var_68;
        wp::float32* var_69;
        wp::float32 var_70;
        wp::float32 var_71;
        wp::float32 var_72;
        wp::float32* var_73;
        wp::float32 var_74;
        wp::float32 var_75;
        wp::float32 var_76;
        //---------
        // forward
        // def ledger_active(n:wp.array(dtype=int),ids:wp.array(dtype=int),cf:wp.array(dtype=wp.vec3),cp:wp.array(dtype=float),power:wp.array(dtype=float),moment:wp.array(dtype=wp.vec3),impulse:wp.array(dtype=wp.vec3),angular:wp.array(dtype=wp.vec3),work:wp.array(dtype=float),diss:wp.array(dtype=float),dt:float,bad:wp.array(dtype=int)):       <L 38>
        // k=wp.tid()                                                                             <L 39>
        var_0 = builtin_tid1d();
        // if k<n[0] and bad[0]==0:                                                               <L 40>
        var_3 = wp::address(var_n, var_2);
        var_5 = wp::load(var_3);
        var_4 = (var_0 < var_5);
        var_1 = var_4;
        if (var_1) {
            var_7 = wp::address(var_bad, var_6);
            var_10 = wp::load(var_7);
            var_9 = (var_10 == var_8);
            var_1 = var_1 && var_9;
        }
        if (var_1) {
            // for v in range(3):                                                                 <L 41>
            // i=3*ids[k]+v;impulse[i]+=dt*cf[i];angular[i]+=dt*moment[i];work[i]+=dt*power[i];diss[i]+=dt*cp[i]       <L 42>
            var_13 = wp::address(var_ids, var_0);
            var_15 = wp::load(var_13);
            var_14 = wp::mul(var_12, var_15);
            var_16 = wp::add(var_14, var_11);
            var_17 = wp::address(var_cf, var_16);
            var_19 = wp::load(var_17);
            var_18 = wp::mul(var_dt, var_19);
            var_20 = wp::atomic_add(var_impulse, var_16, var_18);
            var_21 = wp::address(var_moment, var_16);
            var_23 = wp::load(var_21);
            var_22 = wp::mul(var_dt, var_23);
            var_24 = wp::atomic_add(var_angular, var_16, var_22);
            var_25 = wp::address(var_power, var_16);
            var_27 = wp::load(var_25);
            var_26 = wp::mul(var_dt, var_27);
            var_28 = wp::atomic_add(var_work, var_16, var_26);
            var_29 = wp::address(var_cp, var_16);
            var_31 = wp::load(var_29);
            var_30 = wp::mul(var_dt, var_31);
            var_32 = wp::atomic_add(var_diss, var_16, var_30);
            var_35 = wp::address(var_ids, var_0);
            var_37 = wp::load(var_35);
            var_36 = wp::mul(var_34, var_37);
            var_38 = wp::add(var_36, var_33);
            var_39 = wp::address(var_cf, var_38);
            var_41 = wp::load(var_39);
            var_40 = wp::mul(var_dt, var_41);
            var_42 = wp::atomic_add(var_impulse, var_38, var_40);
            var_43 = wp::address(var_moment, var_38);
            var_45 = wp::load(var_43);
            var_44 = wp::mul(var_dt, var_45);
            var_46 = wp::atomic_add(var_angular, var_38, var_44);
            var_47 = wp::address(var_power, var_38);
            var_49 = wp::load(var_47);
            var_48 = wp::mul(var_dt, var_49);
            var_50 = wp::atomic_add(var_work, var_38, var_48);
            var_51 = wp::address(var_cp, var_38);
            var_53 = wp::load(var_51);
            var_52 = wp::mul(var_dt, var_53);
            var_54 = wp::atomic_add(var_diss, var_38, var_52);
            var_57 = wp::address(var_ids, var_0);
            var_59 = wp::load(var_57);
            var_58 = wp::mul(var_56, var_59);
            var_60 = wp::add(var_58, var_55);
            var_61 = wp::address(var_cf, var_60);
            var_63 = wp::load(var_61);
            var_62 = wp::mul(var_dt, var_63);
            var_64 = wp::atomic_add(var_impulse, var_60, var_62);
            var_65 = wp::address(var_moment, var_60);
            var_67 = wp::load(var_65);
            var_66 = wp::mul(var_dt, var_67);
            var_68 = wp::atomic_add(var_angular, var_60, var_66);
            var_69 = wp::address(var_power, var_60);
            var_71 = wp::load(var_69);
            var_70 = wp::mul(var_dt, var_71);
            var_72 = wp::atomic_add(var_work, var_60, var_70);
            var_73 = wp::address(var_cp, var_60);
            var_75 = wp::load(var_73);
            var_74 = wp::mul(var_dt, var_75);
            var_76 = wp::atomic_add(var_diss, var_60, var_74);
        }
    }
}



extern "C" __global__ void clear_previous_b2f5914a_cuda_kernel_forward(
    wp::launch_bounds_t<1> dim,
    wp::array_t<wp::int32> var_n,
    wp::array_t<wp::int32> var_ids,
    wp::array_t<wp::vec_t<3, wp::float64>> var_ff,
    wp::array_t<wp::float64> var_uu,
    wp::array_t<wp::float64> var_dd,
    wp::array_t<wp::float64> var_ww,
    wp::array_t<wp::vec_t<3, wp::float64>> var_mm,
    wp::array_t<wp::vec_t<3, wp::float32>> var_cf,
    wp::array_t<wp::float32> var_cu,
    wp::array_t<wp::float32> var_cp,
    wp::array_t<wp::float32> var_power,
    wp::array_t<wp::vec_t<3, wp::float32>> var_moment)
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
        bool var_3;
        wp::int32 var_4;
        wp::int32* var_5;
        wp::int32 var_6;
        wp::int32 var_7;
        wp::float64 var_8;
        wp::float64 var_9;
        wp::float64 var_10;
        wp::float64 var_11;
        wp::vec_t<3, wp::float64> var_12;
        const wp::int32 var_13 = 0;
        const wp::int32 var_14 = 3;
        wp::int32 var_15;
        wp::int32 var_16;
        wp::float64 var_17;
        wp::vec_t<3, wp::float64> var_18;
        const wp::float32 var_19 = 0.0;
        wp::vec_t<3, wp::float32> var_20;
        const wp::float32 var_21 = 0.0;
        const wp::float32 var_22 = 0.0;
        const wp::float32 var_23 = 0.0;
        const wp::float32 var_24 = 0.0;
        wp::vec_t<3, wp::float32> var_25;
        const wp::int32 var_26 = 1;
        const wp::int32 var_27 = 3;
        wp::int32 var_28;
        wp::int32 var_29;
        wp::float64 var_30;
        wp::vec_t<3, wp::float64> var_31;
        const wp::float32 var_32 = 0.0;
        wp::vec_t<3, wp::float32> var_33;
        const wp::float32 var_34 = 0.0;
        const wp::float32 var_35 = 0.0;
        const wp::float32 var_36 = 0.0;
        const wp::float32 var_37 = 0.0;
        wp::vec_t<3, wp::float32> var_38;
        const wp::int32 var_39 = 2;
        const wp::int32 var_40 = 3;
        wp::int32 var_41;
        wp::int32 var_42;
        wp::float64 var_43;
        wp::vec_t<3, wp::float64> var_44;
        const wp::float32 var_45 = 0.0;
        wp::vec_t<3, wp::float32> var_46;
        const wp::float32 var_47 = 0.0;
        const wp::float32 var_48 = 0.0;
        const wp::float32 var_49 = 0.0;
        const wp::float32 var_50 = 0.0;
        wp::vec_t<3, wp::float32> var_51;
        //---------
        // forward
        // def clear_previous(n:wp.array(dtype=int),ids:wp.array(dtype=int),ff:wp.array2d(dtype=wp.vec3d),uu:wp.array(dtype=wp.float64),dd:wp.array(dtype=wp.float64),ww:wp.array(dtype=wp.float64),mm:wp.array(dtype=wp.vec3d),cf:wp.array(dtype=wp.vec3),cu:wp.array(dtype=float),cp:wp.array(dtype=float),power:wp.array(dtype=float),moment:wp.array(dtype=wp.vec3)):       <L 13>
        // k=wp.tid()                                                                             <L 14>
        var_0 = builtin_tid1d();
        // if k<n[0]:                                                                             <L 15>
        var_2 = wp::address(var_n, var_1);
        var_4 = wp::load(var_2);
        var_3 = (var_0 < var_4);
        if (var_3) {
            // face=ids[k];uu[face]=wp.float64(0.);dd[face]=wp.float64(0.);ww[face]=wp.float64(0.);mm[face]=wp.vec3d(wp.float64(0.))       <L 16>
            var_5 = wp::address(var_ids, var_0);
            var_7 = wp::load(var_5);
            var_6 = wp::copy(var_7);
            var_8 = 0.0;
            wp::array_store(var_uu, var_6, var_8);
            var_9 = 0.0;
            wp::array_store(var_dd, var_6, var_9);
            var_10 = 0.0;
            wp::array_store(var_ww, var_6, var_10);
            var_11 = 0.0;
            var_12 = wp::vec_t<3, wp::float64>(var_11);
            wp::array_store(var_mm, var_6, var_12);
            // for v in range(3):                                                                 <L 17>
            // i=face*3+v;ff[face,v]=wp.vec3d(wp.float64(0.));cf[i]=wp.vec3(0.);cu[i]=0.;cp[i]=0.;power[i]=0.;moment[i]=wp.vec3(0.)       <L 18>
            var_15 = wp::mul(var_6, var_14);
            var_16 = wp::add(var_15, var_13);
            var_17 = 0.0;
            var_18 = wp::vec_t<3, wp::float64>(var_17);
            wp::array_store(var_ff, var_6, var_13, var_18);
            var_20 = wp::vec_t<3, wp::float32>(var_19);
            wp::array_store(var_cf, var_16, var_20);
            wp::array_store(var_cu, var_16, var_21);
            wp::array_store(var_cp, var_16, var_22);
            wp::array_store(var_power, var_16, var_23);
            var_25 = wp::vec_t<3, wp::float32>(var_24);
            wp::array_store(var_moment, var_16, var_25);
            var_28 = wp::mul(var_6, var_27);
            var_29 = wp::add(var_28, var_26);
            var_30 = 0.0;
            var_31 = wp::vec_t<3, wp::float64>(var_30);
            wp::array_store(var_ff, var_6, var_26, var_31);
            var_33 = wp::vec_t<3, wp::float32>(var_32);
            wp::array_store(var_cf, var_29, var_33);
            wp::array_store(var_cu, var_29, var_34);
            wp::array_store(var_cp, var_29, var_35);
            wp::array_store(var_power, var_29, var_36);
            var_38 = wp::vec_t<3, wp::float32>(var_37);
            wp::array_store(var_moment, var_29, var_38);
            var_41 = wp::mul(var_6, var_40);
            var_42 = wp::add(var_41, var_39);
            var_43 = 0.0;
            var_44 = wp::vec_t<3, wp::float64>(var_43);
            wp::array_store(var_ff, var_6, var_39, var_44);
            var_46 = wp::vec_t<3, wp::float32>(var_45);
            wp::array_store(var_cf, var_42, var_46);
            wp::array_store(var_cu, var_42, var_47);
            wp::array_store(var_cp, var_42, var_48);
            wp::array_store(var_power, var_42, var_49);
            var_51 = wp::vec_t<3, wp::float32>(var_50);
            wp::array_store(var_moment, var_42, var_51);
        }
    }
}



extern "C" __global__ void collect_active_c71fa598_cuda_kernel_forward(
    wp::launch_bounds_t<1> dim,
    wp::array_t<wp::int32> var_n,
    wp::array_t<wp::int32> var_ids,
    wp::array_t<wp::vec_t<3, wp::float64>> var_ff,
    wp::array_t<wp::float64> var_uu,
    wp::array_t<wp::float64> var_dd,
    wp::array_t<wp::float64> var_ww,
    wp::array_t<wp::vec_t<3, wp::float64>> var_mm,
    wp::array_t<wp::vec_t<3, wp::float32>> var_cf,
    wp::array_t<wp::float32> var_cu,
    wp::array_t<wp::float32> var_cp,
    wp::array_t<wp::float32> var_power,
    wp::array_t<wp::vec_t<3, wp::float32>> var_moment,
    wp::array_t<wp::int32> var_ptr,
    wp::array_t<wp::int32> var_nodes,
    wp::array_t<wp::float64> var_weights,
    wp::array_t<wp::vec_t<3, wp::float32>> var_external)
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
        bool var_3;
        wp::int32 var_4;
        wp::int32* var_5;
        wp::int32 var_6;
        wp::int32 var_7;
        const wp::int32 var_8 = 0;
        const wp::int32 var_9 = 3;
        wp::int32 var_10;
        wp::int32 var_11;
        wp::vec_t<3, wp::float64>* var_12;
        wp::vec_t<3, wp::float32> var_13;
        wp::vec_t<3, wp::float64> var_14;
        wp::float64* var_15;
        wp::float64 var_16;
        wp::float64 var_17;
        wp::float64 var_18;
        wp::float32 var_19;
        wp::float64* var_20;
        wp::float64 var_21;
        wp::float64 var_22;
        wp::float64 var_23;
        wp::float32 var_24;
        wp::float64* var_25;
        wp::float64 var_26;
        wp::float64 var_27;
        wp::float64 var_28;
        wp::float32 var_29;
        wp::vec_t<3, wp::float64>* var_30;
        wp::float64 var_31;
        wp::vec_t<3, wp::float64> var_32;
        wp::vec_t<3, wp::float64> var_33;
        wp::vec_t<3, wp::float32> var_34;
        wp::int32* var_35;
        const wp::int32 var_36 = 1;
        wp::int32 var_37;
        wp::int32* var_38;
        wp::range_t var_39;
        wp::int32 var_40;
        wp::int32 var_41;
        wp::int32 var_42;
        wp::int32* var_43;
        wp::float64* var_44;
        wp::float32 var_45;
        wp::float64 var_46;
        wp::vec_t<3, wp::float32> var_47;
        wp::vec_t<3, wp::float32> var_48;
        wp::int32 var_49;
        const wp::int32 var_50 = 1;
        const wp::int32 var_51 = 3;
        wp::int32 var_52;
        wp::int32 var_53;
        wp::vec_t<3, wp::float64>* var_54;
        wp::vec_t<3, wp::float32> var_55;
        wp::vec_t<3, wp::float64> var_56;
        wp::float64* var_57;
        wp::float64 var_58;
        wp::float64 var_59;
        wp::float64 var_60;
        wp::float32 var_61;
        wp::float64* var_62;
        wp::float64 var_63;
        wp::float64 var_64;
        wp::float64 var_65;
        wp::float32 var_66;
        wp::float64* var_67;
        wp::float64 var_68;
        wp::float64 var_69;
        wp::float64 var_70;
        wp::float32 var_71;
        wp::vec_t<3, wp::float64>* var_72;
        wp::float64 var_73;
        wp::vec_t<3, wp::float64> var_74;
        wp::vec_t<3, wp::float64> var_75;
        wp::vec_t<3, wp::float32> var_76;
        wp::int32* var_77;
        const wp::int32 var_78 = 1;
        wp::int32 var_79;
        wp::int32* var_80;
        wp::range_t var_81;
        wp::int32 var_82;
        wp::int32 var_83;
        wp::int32 var_84;
        wp::int32* var_85;
        wp::float64* var_86;
        wp::float32 var_87;
        wp::float64 var_88;
        wp::vec_t<3, wp::float32> var_89;
        wp::vec_t<3, wp::float32> var_90;
        wp::int32 var_91;
        const wp::int32 var_92 = 2;
        const wp::int32 var_93 = 3;
        wp::int32 var_94;
        wp::int32 var_95;
        wp::vec_t<3, wp::float64>* var_96;
        wp::vec_t<3, wp::float32> var_97;
        wp::vec_t<3, wp::float64> var_98;
        wp::float64* var_99;
        wp::float64 var_100;
        wp::float64 var_101;
        wp::float64 var_102;
        wp::float32 var_103;
        wp::float64* var_104;
        wp::float64 var_105;
        wp::float64 var_106;
        wp::float64 var_107;
        wp::float32 var_108;
        wp::float64* var_109;
        wp::float64 var_110;
        wp::float64 var_111;
        wp::float64 var_112;
        wp::float32 var_113;
        wp::vec_t<3, wp::float64>* var_114;
        wp::float64 var_115;
        wp::vec_t<3, wp::float64> var_116;
        wp::vec_t<3, wp::float64> var_117;
        wp::vec_t<3, wp::float32> var_118;
        wp::int32* var_119;
        const wp::int32 var_120 = 1;
        wp::int32 var_121;
        wp::int32* var_122;
        wp::range_t var_123;
        wp::int32 var_124;
        wp::int32 var_125;
        wp::int32 var_126;
        wp::int32* var_127;
        wp::float64* var_128;
        wp::float32 var_129;
        wp::float64 var_130;
        wp::vec_t<3, wp::float32> var_131;
        wp::vec_t<3, wp::float32> var_132;
        wp::int32 var_133;
        //---------
        // forward
        // def collect_active(n:wp.array(dtype=int),ids:wp.array(dtype=int),ff:wp.array2d(dtype=wp.vec3d),uu:wp.array(dtype=wp.float64),dd:wp.array(dtype=wp.float64),ww:wp.array(dtype=wp.float64),mm:wp.array(dtype=wp.vec3d),cf:wp.array(dtype=wp.vec3),cu:wp.array(dtype=float),cp:wp.array(dtype=float),power:wp.array(dtype=float),moment:wp.array(dtype=wp.vec3),ptr:wp.array(dtype=int),nodes:wp.array(dtype=int),weights:wp.array(dtype=wp.float64),external:wp.array(dtype=wp.vec3)):       <L 21>
        // k=wp.tid()                                                                             <L 22>
        var_0 = builtin_tid1d();
        // if k<n[0]:                                                                             <L 23>
        var_2 = wp::address(var_n, var_1);
        var_4 = wp::load(var_2);
        var_3 = (var_0 < var_4);
        if (var_3) {
            // face=ids[k]                                                                        <L 24>
            var_5 = wp::address(var_ids, var_0);
            var_7 = wp::load(var_5);
            var_6 = wp::copy(var_7);
            // for v in range(3):                                                                 <L 25>
            // i=face*3+v;f=wp.vec3(ff[face,v]);cf[i]=f;cu[i]=float(uu[face]/wp.float64(3.));cp[i]=float(dd[face]/wp.float64(3.));power[i]=float(ww[face]/wp.float64(3.));moment[i]=wp.vec3(mm[face]/wp.float64(3.))       <L 26>
            var_10 = wp::mul(var_6, var_9);
            var_11 = wp::add(var_10, var_8);
            var_12 = wp::address(var_ff, var_6, var_8);
            var_14 = wp::load(var_12);
            var_13 = wp::vec_t<3, wp::float32>(var_14);
            wp::array_store(var_cf, var_11, var_13);
            var_15 = wp::address(var_uu, var_6);
            var_16 = 3.0;
            var_18 = wp::load(var_15);
            var_17 = wp::div(var_18, var_16);
            var_19 = wp::float(var_17);
            wp::array_store(var_cu, var_11, var_19);
            var_20 = wp::address(var_dd, var_6);
            var_21 = 3.0;
            var_23 = wp::load(var_20);
            var_22 = wp::div(var_23, var_21);
            var_24 = wp::float(var_22);
            wp::array_store(var_cp, var_11, var_24);
            var_25 = wp::address(var_ww, var_6);
            var_26 = 3.0;
            var_28 = wp::load(var_25);
            var_27 = wp::div(var_28, var_26);
            var_29 = wp::float(var_27);
            wp::array_store(var_power, var_11, var_29);
            var_30 = wp::address(var_mm, var_6);
            var_31 = 3.0;
            var_33 = wp::load(var_30);
            var_32 = wp::div(var_33, var_31);
            var_34 = wp::vec_t<3, wp::float32>(var_32);
            wp::array_store(var_moment, var_11, var_34);
            // for j in range(ptr[i],ptr[i+1]):wp.atomic_add(external,nodes[j],float(weights[j])*f)       <L 27>
            var_35 = wp::address(var_ptr, var_11);
            var_37 = wp::add(var_11, var_36);
            var_38 = wp::address(var_ptr, var_37);
            var_40 = wp::load(var_35);
            var_41 = wp::load(var_38);
            var_39 = wp::range(var_40, var_41);
            start_for_0:;
                if (iter_cmp(var_39) == 0) goto end_for_0;
                var_42 = wp::iter_next(var_39);
                var_43 = wp::address(var_nodes, var_42);
                var_44 = wp::address(var_weights, var_42);
                var_46 = wp::load(var_44);
                var_45 = wp::float(var_46);
                var_47 = wp::mul(var_45, var_13);
                var_49 = wp::load(var_43);
                var_48 = wp::atomic_add(var_external, var_49, var_47);
                goto start_for_0;
            end_for_0:;
            // i=face*3+v;f=wp.vec3(ff[face,v]);cf[i]=f;cu[i]=float(uu[face]/wp.float64(3.));cp[i]=float(dd[face]/wp.float64(3.));power[i]=float(ww[face]/wp.float64(3.));moment[i]=wp.vec3(mm[face]/wp.float64(3.))       <L 26>
            var_52 = wp::mul(var_6, var_51);
            var_53 = wp::add(var_52, var_50);
            var_54 = wp::address(var_ff, var_6, var_50);
            var_56 = wp::load(var_54);
            var_55 = wp::vec_t<3, wp::float32>(var_56);
            wp::array_store(var_cf, var_53, var_55);
            var_57 = wp::address(var_uu, var_6);
            var_58 = 3.0;
            var_60 = wp::load(var_57);
            var_59 = wp::div(var_60, var_58);
            var_61 = wp::float(var_59);
            wp::array_store(var_cu, var_53, var_61);
            var_62 = wp::address(var_dd, var_6);
            var_63 = 3.0;
            var_65 = wp::load(var_62);
            var_64 = wp::div(var_65, var_63);
            var_66 = wp::float(var_64);
            wp::array_store(var_cp, var_53, var_66);
            var_67 = wp::address(var_ww, var_6);
            var_68 = 3.0;
            var_70 = wp::load(var_67);
            var_69 = wp::div(var_70, var_68);
            var_71 = wp::float(var_69);
            wp::array_store(var_power, var_53, var_71);
            var_72 = wp::address(var_mm, var_6);
            var_73 = 3.0;
            var_75 = wp::load(var_72);
            var_74 = wp::div(var_75, var_73);
            var_76 = wp::vec_t<3, wp::float32>(var_74);
            wp::array_store(var_moment, var_53, var_76);
            // for j in range(ptr[i],ptr[i+1]):wp.atomic_add(external,nodes[j],float(weights[j])*f)       <L 27>
            var_77 = wp::address(var_ptr, var_53);
            var_79 = wp::add(var_53, var_78);
            var_80 = wp::address(var_ptr, var_79);
            var_82 = wp::load(var_77);
            var_83 = wp::load(var_80);
            var_81 = wp::range(var_82, var_83);
            start_for_2:;
                if (iter_cmp(var_81) == 0) goto end_for_2;
                var_84 = wp::iter_next(var_81);
                var_85 = wp::address(var_nodes, var_84);
                var_86 = wp::address(var_weights, var_84);
                var_88 = wp::load(var_86);
                var_87 = wp::float(var_88);
                var_89 = wp::mul(var_87, var_55);
                var_91 = wp::load(var_85);
                var_90 = wp::atomic_add(var_external, var_91, var_89);
                goto start_for_2;
            end_for_2:;
            // i=face*3+v;f=wp.vec3(ff[face,v]);cf[i]=f;cu[i]=float(uu[face]/wp.float64(3.));cp[i]=float(dd[face]/wp.float64(3.));power[i]=float(ww[face]/wp.float64(3.));moment[i]=wp.vec3(mm[face]/wp.float64(3.))       <L 26>
            var_94 = wp::mul(var_6, var_93);
            var_95 = wp::add(var_94, var_92);
            var_96 = wp::address(var_ff, var_6, var_92);
            var_98 = wp::load(var_96);
            var_97 = wp::vec_t<3, wp::float32>(var_98);
            wp::array_store(var_cf, var_95, var_97);
            var_99 = wp::address(var_uu, var_6);
            var_100 = 3.0;
            var_102 = wp::load(var_99);
            var_101 = wp::div(var_102, var_100);
            var_103 = wp::float(var_101);
            wp::array_store(var_cu, var_95, var_103);
            var_104 = wp::address(var_dd, var_6);
            var_105 = 3.0;
            var_107 = wp::load(var_104);
            var_106 = wp::div(var_107, var_105);
            var_108 = wp::float(var_106);
            wp::array_store(var_cp, var_95, var_108);
            var_109 = wp::address(var_ww, var_6);
            var_110 = 3.0;
            var_112 = wp::load(var_109);
            var_111 = wp::div(var_112, var_110);
            var_113 = wp::float(var_111);
            wp::array_store(var_power, var_95, var_113);
            var_114 = wp::address(var_mm, var_6);
            var_115 = 3.0;
            var_117 = wp::load(var_114);
            var_116 = wp::div(var_117, var_115);
            var_118 = wp::vec_t<3, wp::float32>(var_116);
            wp::array_store(var_moment, var_95, var_118);
            // for j in range(ptr[i],ptr[i+1]):wp.atomic_add(external,nodes[j],float(weights[j])*f)       <L 27>
            var_119 = wp::address(var_ptr, var_95);
            var_121 = wp::add(var_95, var_120);
            var_122 = wp::address(var_ptr, var_121);
            var_124 = wp::load(var_119);
            var_125 = wp::load(var_122);
            var_123 = wp::range(var_124, var_125);
            start_for_4:;
                if (iter_cmp(var_123) == 0) goto end_for_4;
                var_126 = wp::iter_next(var_123);
                var_127 = wp::address(var_nodes, var_126);
                var_128 = wp::address(var_weights, var_126);
                var_130 = wp::load(var_128);
                var_129 = wp::float(var_130);
                var_131 = wp::mul(var_129, var_97);
                var_133 = wp::load(var_127);
                var_132 = wp::atomic_add(var_external, var_133, var_131);
                goto start_for_4;
            end_for_4:;
        }
    }
}



extern "C" __global__ void guard_active_f01c8330_cuda_kernel_forward(
    wp::launch_bounds_t<1> dim,
    wp::array_t<wp::int32> var_n,
    wp::array_t<wp::int32> var_ids,
    wp::array_t<wp::vec_t<3, wp::float32>> var_cf,
    wp::array_t<wp::int32> var_bad,
    wp::array_t<wp::float32> var_peak,
    wp::array_t<wp::vec_t<3, wp::float64>> var_cut)
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
        wp::float64 var_0;
        const wp::int32 var_1 = 0;
        wp::int32* var_2;
        wp::range_t var_3;
        wp::int32 var_4;
        wp::int32 var_5;
        const wp::int32 var_6 = 0;
        const wp::int32 var_7 = 3;
        wp::int32* var_8;
        wp::int32 var_9;
        wp::int32 var_10;
        wp::int32 var_11;
        wp::vec_t<3, wp::float32>* var_12;
        wp::vec_t<3, wp::float64> var_13;
        wp::vec_t<3, wp::float32> var_14;
        wp::float64 var_15;
        wp::float64 var_16;
        const wp::int32 var_17 = 1;
        const wp::int32 var_18 = 3;
        wp::int32* var_19;
        wp::int32 var_20;
        wp::int32 var_21;
        wp::int32 var_22;
        wp::vec_t<3, wp::float32>* var_23;
        wp::vec_t<3, wp::float64> var_24;
        wp::vec_t<3, wp::float32> var_25;
        wp::float64 var_26;
        wp::float64 var_27;
        const wp::int32 var_28 = 2;
        const wp::int32 var_29 = 3;
        wp::int32* var_30;
        wp::int32 var_31;
        wp::int32 var_32;
        wp::int32 var_33;
        wp::vec_t<3, wp::float32>* var_34;
        wp::vec_t<3, wp::float64> var_35;
        wp::vec_t<3, wp::float32> var_36;
        wp::float64 var_37;
        wp::float64 var_38;
        const wp::int32 var_39 = 0;
        wp::vec_t<3, wp::float64>* var_40;
        wp::float64 var_41;
        wp::vec_t<3, wp::float64> var_42;
        wp::float64 var_43;
        const wp::int32 var_44 = 0;
        wp::float32 var_45;
        wp::float32 var_46;
        bool var_47;
        wp::float64 var_48;
        bool var_49;
        bool var_50;
        bool var_51;
        const wp::int32 var_52 = 0;
        const wp::int32 var_53 = 3;
        wp::int32 var_54;
        //---------
        // forward
        // def guard_active(n:wp.array(dtype=int),ids:wp.array(dtype=int),cf:wp.array(dtype=wp.vec3),bad:wp.array(dtype=int),peak:wp.array(dtype=float),cut:wp.array(dtype=wp.vec3d)):       <L 30>
        // total=wp.float64(0.)                                                                   <L 31>
        var_0 = 0.0;
        // for k in range(n[0]):                                                                  <L 32>
        var_2 = wp::address(var_n, var_1);
        var_4 = wp::load(var_2);
        var_3 = wp::range(var_4);
        start_for_0:;
            if (iter_cmp(var_3) == 0) goto end_for_0;
            var_5 = wp::iter_next(var_3);
            // for v in range(3):total+=wp.length(wp.vec3d(cf[3*ids[k]+v]))                       <L 33>
            var_8 = wp::address(var_ids, var_5);
            var_10 = wp::load(var_8);
            var_9 = wp::mul(var_7, var_10);
            var_11 = wp::add(var_9, var_6);
            var_12 = wp::address(var_cf, var_11);
            var_14 = wp::load(var_12);
            var_13 = wp::vec_t<3, wp::float64>(var_14);
            var_15 = wp::length(var_13);
            var_16 = wp::add(var_0, var_15);
            var_19 = wp::address(var_ids, var_5);
            var_21 = wp::load(var_19);
            var_20 = wp::mul(var_18, var_21);
            var_22 = wp::add(var_20, var_17);
            var_23 = wp::address(var_cf, var_22);
            var_25 = wp::load(var_23);
            var_24 = wp::vec_t<3, wp::float64>(var_25);
            var_26 = wp::length(var_24);
            var_27 = wp::add(var_16, var_26);
            var_30 = wp::address(var_ids, var_5);
            var_32 = wp::load(var_30);
            var_31 = wp::mul(var_29, var_32);
            var_33 = wp::add(var_31, var_28);
            var_34 = wp::address(var_cf, var_33);
            var_36 = wp::load(var_34);
            var_35 = wp::vec_t<3, wp::float64>(var_36);
            var_37 = wp::length(var_35);
            var_38 = wp::add(var_27, var_37);
            wp::assign(var_0, var_38);
            goto start_for_0;
        end_for_0:;
        // total+=wp.length(cut[0]);wp.atomic_max(peak,0,float(total))                            <L 34>
        var_40 = wp::address(var_cut, var_39);
        var_42 = wp::load(var_40);
        var_41 = wp::length(var_42);
        var_43 = wp::add(var_0, var_41);
        var_45 = wp::float(var_43);
        var_46 = wp::atomic_max(var_peak, var_44, var_45);
        // if total>wp.float64(2.) or not wp.isfinite(total):wp.atomic_max(bad,0,3)               <L 35>
        var_48 = 2.0;
        var_49 = (var_43 > var_48);
        var_47 = var_49;
        if (!var_47) {
            var_50 = wp::isfinite(var_43);
            var_51 = wp::unot(var_50);
            var_47 = var_47 || var_51;
        }
        if (var_47) {
            var_54 = wp::atomic_max(var_bad, var_52, var_53);
        }
    }
}


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



extern "C" __global__ void resistance_04e6bfc8_cuda_kernel_forward(
    wp::launch_bounds_t<1> dim,
    wp::array_t<wp::vec_t<3, wp::float32>> var_v,
    wp::array_t<wp::vec_t<3, wp::float64>> var_B,
    wp::array_t<wp::vec_t<3, wp::float64>> var_c,
    wp::array_t<wp::float64> var_params,
    wp::array_t<wp::vec_t<3, wp::float64>> var_pose,
    wp::float64 var_dt,
    wp::array_t<wp::float64> var_Jout,
    wp::array_t<wp::vec_t<3, wp::float64>> var_force,
    wp::array_t<wp::float64> var_account,
    wp::array_t<wp::vec_t<3, wp::float64>> var_impulse,
    wp::array_t<wp::int32> var_bad,
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
        const wp::int32 var_0 = 0;
        wp::int32* var_1;
        const wp::int32 var_2 = 0;
        bool var_3;
        wp::int32 var_4;
        wp::float64 var_5;
        wp::range_t var_6;
        wp::int32 var_7;
        wp::vec_t<3, wp::float64>* var_8;
        wp::vec_t<3, wp::float32>* var_9;
        wp::vec_t<3, wp::float64> var_10;
        wp::vec_t<3, wp::float32> var_11;
        wp::float64 var_12;
        wp::vec_t<3, wp::float64> var_13;
        wp::float64 var_14;
        const wp::int32 var_15 = 1;
        wp::vec_t<3, wp::float64>* var_16;
        const wp::int32 var_17 = 0;
        wp::vec_t<3, wp::float64>* var_18;
        wp::float64 var_19;
        wp::vec_t<3, wp::float64> var_20;
        wp::vec_t<3, wp::float64> var_21;
        wp::float64 var_22;
        const wp::int32 var_23 = 0;
        wp::float64* var_24;
        wp::float64 var_25;
        wp::float64 var_26;
        wp::float64 var_27;
        wp::float64 var_28;
        wp::float64 var_29;
        bool var_30;
        const wp::int32 var_31 = 2;
        wp::float64* var_32;
        wp::float64 var_33;
        bool var_34;
        wp::float64 var_35;
        const wp::int32 var_36 = 1;
        wp::float64* var_37;
        wp::float64 var_38;
        bool var_39;
        wp::float64 var_40;
        wp::float64 var_41;
        wp::float64 var_42;
        wp::float64 var_43;
        const wp::int32 var_44 = 1;
        wp::float64* var_45;
        wp::float64 var_46;
        wp::float64 var_47;
        wp::float64 var_48;
        wp::float64 var_49;
        const wp::float32 var_50 = 1.0;
        const wp::float32 var_51 = 1e-10;
        wp::float32 var_52;
        wp::float64 var_53;
        wp::float64 var_54;
        bool var_55;
        const wp::int32 var_56 = 1;
        wp::float64* var_57;
        wp::float64 var_58;
        wp::float64 var_59;
        wp::float64 var_60;
        wp::float64 var_61;
        wp::float64 var_62;
        wp::float64 var_63;
        wp::float64 var_64;
        wp::float64 var_65;
        wp::float64 var_66;
        const wp::int32 var_67 = 0;
        wp::float64 var_68;
        const wp::int32 var_69 = 0;
        wp::vec_t<3, wp::float64>* var_70;
        wp::vec_t<3, wp::float64> var_71;
        wp::vec_t<3, wp::float64> var_72;
        const wp::int32 var_73 = 0;
        const wp::int32 var_74 = 0;
        wp::float64* var_75;
        wp::float64 var_76;
        wp::float64 var_77;
        wp::float64 var_78;
        const wp::int32 var_79 = 0;
        wp::float64 var_80;
        wp::float64 var_81;
        wp::float64 var_82;
        wp::float64 var_83;
        const wp::int32 var_84 = 1;
        wp::float64* var_85;
        wp::float64 var_86;
        wp::float64 var_87;
        const wp::int32 var_88 = 1;
        wp::float64 var_89;
        wp::float64 var_90;
        wp::float64 var_91;
        const wp::int32 var_92 = 2;
        wp::float64 var_93;
        const wp::int32 var_94 = 3;
        wp::float64 var_95;
        const wp::int32 var_96 = 0;
        wp::vec_t<3, wp::float64>* var_97;
        wp::vec_t<3, wp::float64> var_98;
        wp::vec_t<3, wp::float64> var_99;
        const wp::int32 var_100 = 0;
        wp::vec_t<3, wp::float64> var_101;
        //---------
        // forward
        // def resistance(v:wp.array(dtype=wp.vec3),B:wp.array(dtype=wp.vec3d),c:wp.array(dtype=wp.vec3d),params:wp.array(dtype=wp.float64),pose:wp.array(dtype=wp.vec3d),dt:wp.float64,Jout:wp.array(dtype=wp.float64),force:wp.array(dtype=wp.vec3d),account:wp.array(dtype=wp.float64),impulse:wp.array(dtype=wp.vec3d),bad:wp.array(dtype=int),n:int):       <L 12>
        // if bad[0]==0:                                                                          <L 13>
        var_1 = wp::address(var_bad, var_0);
        var_4 = wp::load(var_1);
        var_3 = (var_4 == var_2);
        if (var_3) {
            // material=wp.float64(0.)                                                            <L 14>
            var_5 = 0.0;
            // for i in range(n):material+=wp.dot(B[i],wp.vec3d(v[i]))                            <L 15>
            var_6 = wp::range(var_n);
            start_for_0:;
                if (iter_cmp(var_6) == 0) goto end_for_0;
                var_7 = wp::iter_next(var_6);
                var_8 = wp::address(var_B, var_7);
                var_9 = wp::address(var_v, var_7);
                var_11 = wp::load(var_9);
                var_10 = wp::vec_t<3, wp::float64>(var_11);
                var_13 = wp::load(var_8);
                var_12 = wp::dot(var_13, var_10);
                var_14 = wp::add(var_5, var_12);
                wp::assign(var_5, var_14);
                goto start_for_0;
            end_for_0:;
            // tv=wp.dot(pose[1],c[0]);relative=tv-material;Y=params[0]*wp.float64(80.);J=wp.float64(0.);slip=wp.float64(0.)       <L 16>
            var_16 = wp::address(var_pose, var_15);
            var_18 = wp::address(var_c, var_17);
            var_20 = wp::load(var_16);
            var_21 = wp::load(var_18);
            var_19 = wp::dot(var_20, var_21);
            var_22 = wp::sub(var_19, var_5);
            var_24 = wp::address(var_params, var_23);
            var_25 = 80.0;
            var_27 = wp::load(var_24);
            var_26 = wp::mul(var_27, var_25);
            var_28 = 0.0;
            var_29 = 0.0;
            // if params[2]>wp.float64(.5) and params[1]>wp.float64(0.):                          <L 17>
            var_32 = wp::address(var_params, var_31);
            var_33 = 0.5;
            var_35 = wp::load(var_32);
            var_34 = (var_35 > var_33);
            var_30 = var_34;
            if (var_30) {
                var_37 = wp::address(var_params, var_36);
                var_38 = 0.0;
                var_40 = wp::load(var_37);
                var_39 = (var_40 > var_38);
                var_30 = var_30 && var_39;
            }
            if (var_30) {
                // J=wp.min(Y*dt,wp.max(relative,wp.float64(0.))/params[1])                       <L 18>
                var_41 = wp::mul(var_26, var_dt);
                var_42 = 0.0;
                var_43 = wp::max(var_22, var_42);
                var_45 = wp::address(var_params, var_44);
                var_47 = wp::load(var_45);
                var_46 = wp::div(var_43, var_47);
                var_48 = wp::min(var_41, var_46);
                // if J>=Y*dt*wp.float64(1.-1e-10):slip=wp.max(relative-J*params[1],wp.float64(0.))*dt       <L 19>
                var_49 = wp::mul(var_26, var_dt);
                var_52 = wp::sub(var_50, var_51);
                var_53 = wp::float64(var_52);
                var_54 = wp::mul(var_49, var_53);
                var_55 = (var_48 >= var_54);
                if (var_55) {
                    var_57 = wp::address(var_params, var_56);
                    var_59 = wp::load(var_57);
                    var_58 = wp::mul(var_48, var_59);
                    var_60 = wp::sub(var_22, var_58);
                    var_61 = 0.0;
                    var_62 = wp::max(var_60, var_61);
                    var_63 = wp::mul(var_62, var_dt);
                }
                var_64 = wp::where(var_55, var_63, var_29);
            }
            var_65 = wp::where(var_30, var_48, var_28);
            var_66 = wp::where(var_30, var_64, var_29);
            // Jout[0]=J;force[0]=J/dt*c[0];area=params[0]*slip;account[0]+=J*tv;account[1]+=wp.float64(.5)*J*J*params[1];account[2]+=wp.float64(80.)*area;account[3]+=area;impulse[0]+=J*c[0]       <L 20>
            wp::array_store(var_Jout, var_67, var_65);
            var_68 = wp::div(var_65, var_dt);
            var_70 = wp::address(var_c, var_69);
            var_72 = wp::load(var_70);
            var_71 = wp::mul(var_68, var_72);
            wp::array_store(var_force, var_73, var_71);
            var_75 = wp::address(var_params, var_74);
            var_77 = wp::load(var_75);
            var_76 = wp::mul(var_77, var_66);
            var_78 = wp::mul(var_65, var_19);
            var_80 = wp::atomic_add(var_account, var_79, var_78);
            var_81 = 0.5;
            var_82 = wp::mul(var_81, var_65);
            var_83 = wp::mul(var_82, var_65);
            var_85 = wp::address(var_params, var_84);
            var_87 = wp::load(var_85);
            var_86 = wp::mul(var_83, var_87);
            var_89 = wp::atomic_add(var_account, var_88, var_86);
            var_90 = 80.0;
            var_91 = wp::mul(var_90, var_76);
            var_93 = wp::atomic_add(var_account, var_92, var_91);
            var_95 = wp::atomic_add(var_account, var_94, var_76);
            var_97 = wp::address(var_c, var_96);
            var_99 = wp::load(var_97);
            var_98 = wp::mul(var_65, var_99);
            var_101 = wp::atomic_add(var_impulse, var_100, var_98);
        }
    }
}



extern "C" __global__ void apply_impulse_3cfe4d12_cuda_kernel_forward(
    wp::launch_bounds_t<1> dim,
    wp::array_t<wp::vec_t<3, wp::float32>> var_v,
    wp::array_t<wp::vec_t<3, wp::float64>> var_mobility,
    wp::array_t<wp::vec_t<3, wp::float64>> var_reaction,
    wp::array_t<wp::float64> var_J,
    wp::array_t<wp::vec_t<3, wp::float32>> var_support,
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
        const wp::int32 var_6 = 0;
        wp::float64* var_7;
        wp::vec_t<3, wp::float64>* var_8;
        wp::vec_t<3, wp::float64> var_9;
        wp::float64 var_10;
        wp::vec_t<3, wp::float64> var_11;
        wp::vec_t<3, wp::float32> var_12;
        wp::vec_t<3, wp::float32> var_13;
        const wp::int32 var_14 = 0;
        wp::float64* var_15;
        wp::vec_t<3, wp::float64>* var_16;
        wp::vec_t<3, wp::float64> var_17;
        wp::float64 var_18;
        wp::vec_t<3, wp::float64> var_19;
        wp::vec_t<3, wp::float32> var_20;
        wp::vec_t<3, wp::float32> var_21;
        //---------
        // forward
        // def apply_impulse(v:wp.array(dtype=wp.vec3),mobility:wp.array(dtype=wp.vec3d),reaction:wp.array(dtype=wp.vec3d),J:wp.array(dtype=wp.float64),support:wp.array(dtype=wp.vec3),bad:wp.array(dtype=int)):       <L 23>
        // i=wp.tid()                                                                             <L 24>
        var_0 = builtin_tid1d();
        // if bad[0]==0:v[i]+=wp.vec3(J[0]*mobility[i]);support[i]+=wp.vec3(J[0]*reaction[i])       <L 25>
        var_2 = wp::address(var_bad, var_1);
        var_5 = wp::load(var_2);
        var_4 = (var_5 == var_3);
        if (var_4) {
            var_7 = wp::address(var_J, var_6);
            var_8 = wp::address(var_mobility, var_0);
            var_10 = wp::load(var_7);
            var_11 = wp::load(var_8);
            var_9 = wp::mul(var_10, var_11);
            var_12 = wp::vec_t<3, wp::float32>(var_9);
            var_13 = wp::atomic_add(var_v, var_0, var_12);
            var_15 = wp::address(var_J, var_14);
            var_16 = wp::address(var_reaction, var_0);
            var_18 = wp::load(var_15);
            var_19 = wp::load(var_16);
            var_17 = wp::mul(var_18, var_19);
            var_20 = wp::vec_t<3, wp::float32>(var_17);
            var_21 = wp::atomic_add(var_support, var_0, var_20);
        }
    }
}



extern "C" __global__ void combined_guard_59d52164_cuda_kernel_forward(
    wp::launch_bounds_t<1> dim,
    wp::array_t<wp::vec_t<3, wp::float32>> var_cf,
    wp::array_t<wp::vec_t<3, wp::float64>> var_cut,
    wp::array_t<wp::float32> var_peak,
    wp::array_t<wp::int32> var_bad,
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
        const wp::int32 var_0 = 0;
        wp::vec_t<3, wp::float64>* var_1;
        wp::float64 var_2;
        wp::vec_t<3, wp::float64> var_3;
        wp::range_t var_4;
        wp::int32 var_5;
        wp::vec_t<3, wp::float32>* var_6;
        wp::float32 var_7;
        wp::vec_t<3, wp::float32> var_8;
        wp::float64 var_9;
        wp::float64 var_10;
        const wp::int32 var_11 = 0;
        wp::float32 var_12;
        wp::float32 var_13;
        bool var_14;
        wp::float64 var_15;
        bool var_16;
        bool var_17;
        bool var_18;
        const wp::int32 var_19 = 0;
        const wp::int32 var_20 = 3;
        wp::int32 var_21;
        //---------
        // forward
        // def combined_guard(cf:wp.array(dtype=wp.vec3),cut:wp.array(dtype=wp.vec3d),peak:wp.array(dtype=float),bad:wp.array(dtype=int),n:int):       <L 28>
        // value=wp.length(cut[0])                                                                <L 29>
        var_1 = wp::address(var_cut, var_0);
        var_3 = wp::load(var_1);
        var_2 = wp::length(var_3);
        // for i in range(n):value+=wp.float64(wp.length(cf[i]))                                  <L 30>
        var_4 = wp::range(var_n);
        start_for_0:;
            if (iter_cmp(var_4) == 0) goto end_for_0;
            var_5 = wp::iter_next(var_4);
            var_6 = wp::address(var_cf, var_5);
            var_8 = wp::load(var_6);
            var_7 = wp::length(var_8);
            var_9 = wp::float64(var_7);
            var_10 = wp::add(var_2, var_9);
            wp::assign(var_2, var_10);
            goto start_for_0;
        end_for_0:;
        // wp.atomic_max(peak,0,float(value))                                                     <L 31>
        var_12 = wp::float(var_2);
        var_13 = wp::atomic_max(var_peak, var_11, var_12);
        // if value>wp.float64(2.) or not wp.isfinite(value):wp.atomic_max(bad,0,3)               <L 32>
        var_15 = 2.0;
        var_16 = (var_2 > var_15);
        var_14 = var_16;
        if (!var_14) {
            var_17 = wp::isfinite(var_2);
            var_18 = wp::unot(var_17);
            var_14 = var_14 || var_18;
        }
        if (var_14) {
            var_21 = wp::atomic_max(var_bad, var_19, var_20);
        }
    }
}


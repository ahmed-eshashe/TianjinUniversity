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



extern "C" __global__ void stress_26af1b90_cuda_kernel_forward(
    wp::launch_bounds_t<1> dim,
    wp::array_t<wp::int32> var_ptr,
    wp::array_t<wp::int32> var_idx,
    wp::array_t<wp::vec_t<3, wp::float32>> var_grad,
    wp::array_t<wp::vec_t<3, wp::float32>> var_q,
    wp::array_t<wp::float32> var_vol,
    wp::float32 var_mu,
    wp::float32 var_lam,
    wp::array_t<wp::mat_t<3, 3, wp::float32>> var_P,
    wp::array_t<wp::float32> var_energy,
    wp::array_t<wp::int32> var_bad,
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
        const wp::int32 var_1 = 1;
        wp::int32* var_2;
        bool var_3;
        wp::int32 var_4;
        const wp::int32 var_5 = 3;
        wp::mat_t<3, 3, wp::float32> var_6;
        wp::int32* var_7;
        wp::int32* var_8;
        wp::int32 var_9;
        wp::vec_t<3, wp::float32>* var_10;
        wp::int32 var_11;
        wp::vec_t<3, wp::float32> var_12;
        wp::vec_t<3, wp::float32> var_13;
        wp::int32* var_14;
        const wp::int32 var_15 = 1;
        wp::int32 var_16;
        wp::int32 var_17;
        const wp::int32 var_18 = 1;
        wp::int32 var_19;
        wp::int32* var_20;
        wp::range_t var_21;
        wp::int32 var_22;
        wp::int32 var_23;
        wp::int32* var_24;
        wp::vec_t<3, wp::float32>* var_25;
        wp::int32 var_26;
        wp::vec_t<3, wp::float32> var_27;
        wp::vec_t<3, wp::float32> var_28;
        wp::vec_t<3, wp::float32>* var_29;
        wp::mat_t<3, 3, wp::float32> var_30;
        wp::vec_t<3, wp::float32> var_31;
        wp::mat_t<3, 3, wp::float32> var_32;
        wp::float32 var_33;
        bool var_34;
        const wp::float32 var_35 = 0.1;
        bool var_36;
        const wp::float32 var_37 = 10.0;
        bool var_38;
        bool var_39;
        bool var_40;
        const wp::int32 var_41 = 0;
        const wp::int32 var_42 = 1;
        wp::int32 var_43;
        const wp::float32 var_44 = 0.0;
        wp::mat_t<3, 3, wp::float32> var_45;
        const wp::float32 var_46 = 0.0;
        wp::float32 var_47;
        wp::float32* var_48;
        wp::mat_t<3, 3, wp::float32> var_49;
        wp::float32 var_50;
        wp::float32 var_51;
        wp::mat_t<3, 3, wp::float32> var_52;
        wp::mat_t<3, 3, wp::float32> var_53;
        wp::mat_t<3, 3, wp::float32> var_54;
        wp::mat_t<3, 3, wp::float32> var_55;
        wp::mat_t<3, 3, wp::float32> var_56;
        wp::float32 var_57;
        const wp::float32 var_58 = 0.0;
        wp::float32 var_59;
        const wp::int32 var_60 = 0;
        const wp::int32 var_61 = 0;
        wp::float32 var_62;
        wp::float32 var_63;
        wp::float32 var_64;
        wp::float32 var_65;
        const wp::int32 var_66 = 1;
        wp::float32 var_67;
        wp::float32 var_68;
        wp::float32 var_69;
        wp::float32 var_70;
        const wp::int32 var_71 = 2;
        wp::float32 var_72;
        wp::float32 var_73;
        wp::float32 var_74;
        wp::float32 var_75;
        const wp::int32 var_76 = 1;
        const wp::int32 var_77 = 0;
        wp::float32 var_78;
        wp::float32 var_79;
        wp::float32 var_80;
        wp::float32 var_81;
        const wp::int32 var_82 = 1;
        wp::float32 var_83;
        wp::float32 var_84;
        wp::float32 var_85;
        wp::float32 var_86;
        const wp::int32 var_87 = 2;
        wp::float32 var_88;
        wp::float32 var_89;
        wp::float32 var_90;
        wp::float32 var_91;
        const wp::int32 var_92 = 2;
        const wp::int32 var_93 = 0;
        wp::float32 var_94;
        wp::float32 var_95;
        wp::float32 var_96;
        wp::float32 var_97;
        const wp::int32 var_98 = 1;
        wp::float32 var_99;
        wp::float32 var_100;
        wp::float32 var_101;
        wp::float32 var_102;
        const wp::int32 var_103 = 2;
        wp::float32 var_104;
        wp::float32 var_105;
        wp::float32 var_106;
        wp::float32 var_107;
        wp::float32* var_108;
        const wp::float32 var_109 = 0.5;
        wp::float32 var_110;
        const wp::float32 var_111 = 3.0;
        wp::float32 var_112;
        wp::float32 var_113;
        wp::float32 var_114;
        wp::float32 var_115;
        const wp::float32 var_116 = 0.5;
        wp::float32 var_117;
        wp::float32 var_118;
        wp::float32 var_119;
        wp::float32 var_120;
        wp::float32 var_121;
        wp::float32 var_122;
        //---------
        // forward
        // def stress(ptr:wp.array(dtype=int),idx:wp.array(dtype=int),grad:wp.array(dtype=wp.vec3),q:wp.array(dtype=wp.vec3),vol:wp.array(dtype=float),mu:float,lam:float,P:wp.array(dtype=wp.mat33),energy:wp.array(dtype=float),bad:wp.array(dtype=int),counts:wp.array(dtype=int)):       <L 8>
        // p=wp.tid()                                                                             <L 9>
        var_0 = builtin_tid1d();
        // if p<counts[1]:                                                                        <L 10>
        var_2 = wp::address(var_counts, var_1);
        var_4 = wp::load(var_2);
        var_3 = (var_0 < var_4);
        if (var_3) {
            // F=wp.identity(n=3,dtype=float);q0=q[idx[ptr[p]]]                                   <L 11>
            var_6 = wp::identity<3, wp::float32>();
            var_7 = wp::address(var_ptr, var_0);
            var_9 = wp::load(var_7);
            var_8 = wp::address(var_idx, var_9);
            var_11 = wp::load(var_8);
            var_10 = wp::address(var_q, var_11);
            var_13 = wp::load(var_10);
            var_12 = wp::copy(var_13);
            // for e in range(ptr[p]+1,ptr[p+1]):F+=wp.outer(q[idx[e]]-q0,grad[e])                <L 12>
            var_14 = wp::address(var_ptr, var_0);
            var_17 = wp::load(var_14);
            var_16 = wp::add(var_17, var_15);
            var_19 = wp::add(var_0, var_18);
            var_20 = wp::address(var_ptr, var_19);
            var_22 = wp::load(var_20);
            var_21 = wp::range(var_16, var_22);
            start_for_0:;
                if (iter_cmp(var_21) == 0) goto end_for_0;
                var_23 = wp::iter_next(var_21);
                var_24 = wp::address(var_idx, var_23);
                var_26 = wp::load(var_24);
                var_25 = wp::address(var_q, var_26);
                var_28 = wp::load(var_25);
                var_27 = wp::sub(var_28, var_12);
                var_29 = wp::address(var_grad, var_23);
                var_31 = wp::load(var_29);
                var_30 = wp::outer(var_27, var_31);
                var_32 = wp::add(var_6, var_30);
                wp::assign(var_6, var_32);
                goto start_for_0;
            end_for_0:;
            // J=wp.determinant(F)                                                                <L 13>
            var_33 = wp::determinant(var_6);
            // if J<=0.1 or J>=10.0 or not wp.isfinite(J):wp.atomic_max(bad,0,1);P[p]=wp.mat33(0.0);energy[p]=0.0       <L 14>
            var_36 = (var_33 <= var_35);
            var_34 = var_36;
            if (!var_34) {
                var_38 = (var_33 >= var_37);
                var_34 = var_34 || var_38;
            }
            if (!var_34) {
                var_39 = wp::isfinite(var_33);
                var_40 = wp::unot(var_39);
                var_34 = var_34 || var_40;
            }
            if (var_34) {
                var_43 = wp::atomic_max(var_bad, var_41, var_42);
                var_45 = wp::mat_t<3, 3, wp::float32>(var_44);
                wp::array_store(var_P, var_0, var_45);
                wp::array_store(var_energy, var_0, var_46);
            }
            if (!var_34) {
                // lj=wp.log(J);P[p]=vol[p]*(mu*F+(lam*lj-mu)*wp.transpose(wp.inverse(F)));norm=float(0.0)       <L 16>
                var_47 = wp::log(var_33);
                var_48 = wp::address(var_vol, var_0);
                var_49 = wp::mul(var_mu, var_6);
                var_50 = wp::mul(var_lam, var_47);
                var_51 = wp::sub(var_50, var_mu);
                var_52 = wp::inverse(var_6);
                var_53 = wp::transpose(var_52);
                var_54 = wp::mul(var_51, var_53);
                var_55 = wp::add(var_49, var_54);
                var_57 = wp::load(var_48);
                var_56 = wp::mul(var_57, var_55);
                wp::array_store(var_P, var_0, var_56);
                var_59 = wp::float(var_58);
                // for i in range(3):                                                             <L 17>
                // for j in range(3):norm+=F[i,j]*F[i,j]                                          <L 18>
                var_62 = wp::extract(var_6, var_60, var_61);
                var_63 = wp::extract(var_6, var_60, var_61);
                var_64 = wp::mul(var_62, var_63);
                var_65 = wp::add(var_59, var_64);
                var_67 = wp::extract(var_6, var_60, var_66);
                var_68 = wp::extract(var_6, var_60, var_66);
                var_69 = wp::mul(var_67, var_68);
                var_70 = wp::add(var_65, var_69);
                var_72 = wp::extract(var_6, var_60, var_71);
                var_73 = wp::extract(var_6, var_60, var_71);
                var_74 = wp::mul(var_72, var_73);
                var_75 = wp::add(var_70, var_74);
                var_78 = wp::extract(var_6, var_76, var_77);
                var_79 = wp::extract(var_6, var_76, var_77);
                var_80 = wp::mul(var_78, var_79);
                var_81 = wp::add(var_75, var_80);
                var_83 = wp::extract(var_6, var_76, var_82);
                var_84 = wp::extract(var_6, var_76, var_82);
                var_85 = wp::mul(var_83, var_84);
                var_86 = wp::add(var_81, var_85);
                var_88 = wp::extract(var_6, var_76, var_87);
                var_89 = wp::extract(var_6, var_76, var_87);
                var_90 = wp::mul(var_88, var_89);
                var_91 = wp::add(var_86, var_90);
                var_94 = wp::extract(var_6, var_92, var_93);
                var_95 = wp::extract(var_6, var_92, var_93);
                var_96 = wp::mul(var_94, var_95);
                var_97 = wp::add(var_91, var_96);
                var_99 = wp::extract(var_6, var_92, var_98);
                var_100 = wp::extract(var_6, var_92, var_98);
                var_101 = wp::mul(var_99, var_100);
                var_102 = wp::add(var_97, var_101);
                var_104 = wp::extract(var_6, var_92, var_103);
                var_105 = wp::extract(var_6, var_92, var_103);
                var_106 = wp::mul(var_104, var_105);
                var_107 = wp::add(var_102, var_106);
                // energy[p]=vol[p]*(0.5*mu*(norm-3.0)-mu*lj+0.5*lam*lj*lj)                       <L 19>
                var_108 = wp::address(var_vol, var_0);
                var_110 = wp::mul(var_109, var_mu);
                var_112 = wp::sub(var_107, var_111);
                var_113 = wp::mul(var_110, var_112);
                var_114 = wp::mul(var_mu, var_47);
                var_115 = wp::sub(var_113, var_114);
                var_117 = wp::mul(var_116, var_lam);
                var_118 = wp::mul(var_117, var_47);
                var_119 = wp::mul(var_118, var_47);
                var_120 = wp::add(var_115, var_119);
                var_122 = wp::load(var_108);
                var_121 = wp::mul(var_122, var_120);
                wp::array_store(var_energy, var_0, var_121);
            }
        }
    }
}



extern "C" __global__ void advance_f6254ee6_cuda_kernel_forward(
    wp::launch_bounds_t<1> dim,
    wp::array_t<wp::int32> var_mptr,
    wp::array_t<wp::int32> var_midx,
    wp::array_t<wp::float32> var_mi,
    wp::array_t<wp::vec_t<3, wp::float32>> var_force,
    wp::array_t<wp::vec_t<3, wp::float32>> var_q,
    wp::array_t<wp::vec_t<3, wp::float32>> var_v,
    wp::float32 var_kick,
    wp::float32 var_drift,
    wp::array_t<wp::int32> var_bad,
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
        const wp::float32 var_11 = 0.0;
        wp::vec_t<3, wp::float32> var_12;
        wp::int32* var_13;
        const wp::int32 var_14 = 1;
        wp::int32 var_15;
        wp::int32* var_16;
        wp::range_t var_17;
        wp::int32 var_18;
        wp::int32 var_19;
        wp::int32 var_20;
        wp::float32* var_21;
        wp::int32* var_22;
        wp::vec_t<3, wp::float32>* var_23;
        wp::int32 var_24;
        wp::vec_t<3, wp::float32> var_25;
        wp::float32 var_26;
        wp::vec_t<3, wp::float32> var_27;
        wp::vec_t<3, wp::float32> var_28;
        wp::vec_t<3, wp::float32>* var_29;
        wp::vec_t<3, wp::float32> var_30;
        wp::vec_t<3, wp::float32> var_31;
        wp::vec_t<3, wp::float32> var_32;
        const wp::float32 var_33 = 0.0;
        bool var_34;
        wp::vec_t<3, wp::float32> var_35;
        wp::vec_t<3, wp::float32> var_36;
        const wp::int32 var_37 = 0;
        bool var_38;
        wp::float32 var_39;
        bool var_40;
        bool var_41;
        wp::vec_t<3, wp::float32>* var_42;
        wp::float32 var_43;
        wp::vec_t<3, wp::float32> var_44;
        bool var_45;
        bool var_46;
        const wp::int32 var_47 = 0;
        const wp::int32 var_48 = 2;
        wp::int32 var_49;
        const wp::int32 var_50 = 1;
        bool var_51;
        wp::float32 var_52;
        bool var_53;
        bool var_54;
        wp::vec_t<3, wp::float32>* var_55;
        wp::float32 var_56;
        wp::vec_t<3, wp::float32> var_57;
        bool var_58;
        bool var_59;
        const wp::int32 var_60 = 0;
        const wp::int32 var_61 = 2;
        wp::int32 var_62;
        const wp::int32 var_63 = 2;
        bool var_64;
        wp::float32 var_65;
        bool var_66;
        bool var_67;
        wp::vec_t<3, wp::float32>* var_68;
        wp::float32 var_69;
        wp::vec_t<3, wp::float32> var_70;
        bool var_71;
        bool var_72;
        const wp::int32 var_73 = 0;
        const wp::int32 var_74 = 2;
        wp::int32 var_75;
        //---------
        // forward
        // def advance(mptr:wp.array(dtype=int),midx:wp.array(dtype=int),mi:wp.array(dtype=float),force:wp.array(dtype=wp.vec3),q:wp.array(dtype=wp.vec3),v:wp.array(dtype=wp.vec3),kick:float,drift:float,bad:wp.array(dtype=int),counts:wp.array(dtype=int)):       <L 31>
        // i=wp.tid()                                                                             <L 32>
        var_0 = builtin_tid1d();
        // if i<counts[0] and bad[0]==0:                                                          <L 33>
        var_3 = wp::address(var_counts, var_2);
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
            // acc=wp.vec3(0.0)                                                                   <L 34>
            var_12 = wp::vec_t<3, wp::float32>(var_11);
            // for k in range(mptr[i],mptr[i+1]):acc+=mi[k]*force[midx[k]]                        <L 35>
            var_13 = wp::address(var_mptr, var_0);
            var_15 = wp::add(var_0, var_14);
            var_16 = wp::address(var_mptr, var_15);
            var_18 = wp::load(var_13);
            var_19 = wp::load(var_16);
            var_17 = wp::range(var_18, var_19);
            start_for_0:;
                if (iter_cmp(var_17) == 0) goto end_for_0;
                var_20 = wp::iter_next(var_17);
                var_21 = wp::address(var_mi, var_20);
                var_22 = wp::address(var_midx, var_20);
                var_24 = wp::load(var_22);
                var_23 = wp::address(var_force, var_24);
                var_26 = wp::load(var_21);
                var_27 = wp::load(var_23);
                var_25 = wp::mul(var_26, var_27);
                var_28 = wp::add(var_12, var_25);
                wp::assign(var_12, var_28);
                goto start_for_0;
            end_for_0:;
            // vn=v[i]+kick*acc;v[i]=vn                                                           <L 36>
            var_29 = wp::address(var_v, var_0);
            var_30 = wp::mul(var_kick, var_12);
            var_32 = wp::load(var_29);
            var_31 = wp::add(var_32, var_30);
            wp::array_store(var_v, var_0, var_31);
            // if drift>0.:q[i]+=drift*vn                                                         <L 37>
            var_34 = (var_drift > var_33);
            if (var_34) {
                var_35 = wp::mul(var_drift, var_31);
                var_36 = wp::atomic_add(var_q, var_0, var_35);
            }
            // for axis in range(3):                                                              <L 38>
            // if not wp.isfinite(vn[axis]) or not wp.isfinite(q[i][axis]):wp.atomic_max(bad,0,2)       <L 39>
            var_39 = wp::extract(var_31, var_37);
            var_40 = wp::isfinite(var_39);
            var_41 = wp::unot(var_40);
            var_38 = var_41;
            if (!var_38) {
                var_42 = wp::address(var_q, var_0);
                var_44 = wp::load(var_42);
                var_43 = wp::extract(var_44, var_37);
                var_45 = wp::isfinite(var_43);
                var_46 = wp::unot(var_45);
                var_38 = var_38 || var_46;
            }
            if (var_38) {
                var_49 = wp::atomic_max(var_bad, var_47, var_48);
            }
            var_52 = wp::extract(var_31, var_50);
            var_53 = wp::isfinite(var_52);
            var_54 = wp::unot(var_53);
            var_51 = var_54;
            if (!var_51) {
                var_55 = wp::address(var_q, var_0);
                var_57 = wp::load(var_55);
                var_56 = wp::extract(var_57, var_50);
                var_58 = wp::isfinite(var_56);
                var_59 = wp::unot(var_58);
                var_51 = var_51 || var_59;
            }
            if (var_51) {
                var_62 = wp::atomic_max(var_bad, var_60, var_61);
            }
            var_65 = wp::extract(var_31, var_63);
            var_66 = wp::isfinite(var_65);
            var_67 = wp::unot(var_66);
            var_64 = var_67;
            if (!var_64) {
                var_68 = wp::address(var_q, var_0);
                var_70 = wp::load(var_68);
                var_69 = wp::extract(var_70, var_63);
                var_71 = wp::isfinite(var_69);
                var_72 = wp::unot(var_71);
                var_64 = var_64 || var_72;
            }
            if (var_64) {
                var_75 = wp::atomic_max(var_bad, var_73, var_74);
            }
        }
    }
}


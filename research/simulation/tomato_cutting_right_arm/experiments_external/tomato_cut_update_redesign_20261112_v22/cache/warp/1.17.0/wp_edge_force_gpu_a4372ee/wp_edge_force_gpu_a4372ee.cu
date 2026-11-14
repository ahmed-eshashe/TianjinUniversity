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



extern "C" __global__ void stress_edges_166091b7_cuda_kernel_forward(
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
    wp::array_t<wp::vec_t<3, wp::float32>> var_edgeforce,
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
        const wp::float32 var_34 = 0.0;
        wp::mat_t<3, 3, wp::float32> var_35;
        bool var_36;
        const wp::float32 var_37 = 0.1;
        bool var_38;
        const wp::float32 var_39 = 10.0;
        bool var_40;
        bool var_41;
        bool var_42;
        const wp::int32 var_43 = 0;
        const wp::int32 var_44 = 1;
        wp::int32 var_45;
        const wp::float32 var_46 = 0.0;
        wp::mat_t<3, 3, wp::float32> var_47;
        const wp::float32 var_48 = 0.0;
        wp::float32 var_49;
        wp::float32* var_50;
        wp::mat_t<3, 3, wp::float32> var_51;
        wp::float32 var_52;
        wp::float32 var_53;
        wp::mat_t<3, 3, wp::float32> var_54;
        wp::mat_t<3, 3, wp::float32> var_55;
        wp::mat_t<3, 3, wp::float32> var_56;
        wp::mat_t<3, 3, wp::float32> var_57;
        wp::mat_t<3, 3, wp::float32> var_58;
        wp::float32 var_59;
        const wp::float32 var_60 = 0.0;
        wp::float32 var_61;
        const wp::int32 var_62 = 0;
        const wp::int32 var_63 = 0;
        wp::float32 var_64;
        wp::float32 var_65;
        wp::float32 var_66;
        wp::float32 var_67;
        const wp::int32 var_68 = 1;
        wp::float32 var_69;
        wp::float32 var_70;
        wp::float32 var_71;
        wp::float32 var_72;
        const wp::int32 var_73 = 2;
        wp::float32 var_74;
        wp::float32 var_75;
        wp::float32 var_76;
        wp::float32 var_77;
        const wp::int32 var_78 = 1;
        const wp::int32 var_79 = 0;
        wp::float32 var_80;
        wp::float32 var_81;
        wp::float32 var_82;
        wp::float32 var_83;
        const wp::int32 var_84 = 1;
        wp::float32 var_85;
        wp::float32 var_86;
        wp::float32 var_87;
        wp::float32 var_88;
        const wp::int32 var_89 = 2;
        wp::float32 var_90;
        wp::float32 var_91;
        wp::float32 var_92;
        wp::float32 var_93;
        const wp::int32 var_94 = 2;
        const wp::int32 var_95 = 0;
        wp::float32 var_96;
        wp::float32 var_97;
        wp::float32 var_98;
        wp::float32 var_99;
        const wp::int32 var_100 = 1;
        wp::float32 var_101;
        wp::float32 var_102;
        wp::float32 var_103;
        wp::float32 var_104;
        const wp::int32 var_105 = 2;
        wp::float32 var_106;
        wp::float32 var_107;
        wp::float32 var_108;
        wp::float32 var_109;
        wp::float32* var_110;
        const wp::float32 var_111 = 0.5;
        wp::float32 var_112;
        const wp::float32 var_113 = 3.0;
        wp::float32 var_114;
        wp::float32 var_115;
        wp::float32 var_116;
        wp::float32 var_117;
        const wp::float32 var_118 = 0.5;
        wp::float32 var_119;
        wp::float32 var_120;
        wp::float32 var_121;
        wp::float32 var_122;
        wp::float32 var_123;
        wp::float32 var_124;
        wp::mat_t<3, 3, wp::float32> var_125;
        wp::int32* var_126;
        const wp::int32 var_127 = 1;
        wp::int32 var_128;
        wp::int32* var_129;
        wp::range_t var_130;
        wp::int32 var_131;
        wp::int32 var_132;
        wp::int32 var_133;
        wp::vec_t<3, wp::float32>* var_134;
        wp::vec_t<3, wp::float32> var_135;
        wp::vec_t<3, wp::float32> var_136;
        //---------
        // forward
        // def stress_edges(ptr:wp.array(dtype=int),idx:wp.array(dtype=int),grad:wp.array(dtype=wp.vec3),q:wp.array(dtype=wp.vec3),vol:wp.array(dtype=float),mu:float,lam:float,P:wp.array(dtype=wp.mat33),energy:wp.array(dtype=float),edgeforce:wp.array(dtype=wp.vec3),bad:wp.array(dtype=int),counts:wp.array(dtype=int)):       <L 9>
        // p=wp.tid()                                                                             <L 10>
        var_0 = builtin_tid1d();
        // if p<counts[1]:                                                                        <L 11>
        var_2 = wp::address(var_counts, var_1);
        var_4 = wp::load(var_2);
        var_3 = (var_0 < var_4);
        if (var_3) {
            // F=wp.identity(n=3,dtype=float);q0=q[idx[ptr[p]]]                                   <L 12>
            var_6 = wp::identity<3, wp::float32>();
            var_7 = wp::address(var_ptr, var_0);
            var_9 = wp::load(var_7);
            var_8 = wp::address(var_idx, var_9);
            var_11 = wp::load(var_8);
            var_10 = wp::address(var_q, var_11);
            var_13 = wp::load(var_10);
            var_12 = wp::copy(var_13);
            // for e in range(ptr[p]+1,ptr[p+1]):F+=wp.outer(q[idx[e]]-q0,grad[e])                <L 13>
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
            // J=wp.determinant(F);stress=wp.mat33(0.0)                                           <L 14>
            var_33 = wp::determinant(var_6);
            var_35 = wp::mat_t<3, 3, wp::float32>(var_34);
            // if J<=0.1 or J>=10.0 or not wp.isfinite(J):wp.atomic_max(bad,0,1);P[p]=wp.mat33(0.0);energy[p]=0.0       <L 15>
            var_38 = (var_33 <= var_37);
            var_36 = var_38;
            if (!var_36) {
                var_40 = (var_33 >= var_39);
                var_36 = var_36 || var_40;
            }
            if (!var_36) {
                var_41 = wp::isfinite(var_33);
                var_42 = wp::unot(var_41);
                var_36 = var_36 || var_42;
            }
            if (var_36) {
                var_45 = wp::atomic_max(var_bad, var_43, var_44);
                var_47 = wp::mat_t<3, 3, wp::float32>(var_46);
                wp::array_store(var_P, var_0, var_47);
                wp::array_store(var_energy, var_0, var_48);
            }
            if (!var_36) {
                // lj=wp.log(J);stress=vol[p]*(mu*F+(lam*lj-mu)*wp.transpose(wp.inverse(F)));P[p]=stress;norm=float(0.0)       <L 17>
                var_49 = wp::log(var_33);
                var_50 = wp::address(var_vol, var_0);
                var_51 = wp::mul(var_mu, var_6);
                var_52 = wp::mul(var_lam, var_49);
                var_53 = wp::sub(var_52, var_mu);
                var_54 = wp::inverse(var_6);
                var_55 = wp::transpose(var_54);
                var_56 = wp::mul(var_53, var_55);
                var_57 = wp::add(var_51, var_56);
                var_59 = wp::load(var_50);
                var_58 = wp::mul(var_59, var_57);
                wp::array_store(var_P, var_0, var_58);
                var_61 = wp::float(var_60);
                // for i in range(3):                                                             <L 18>
                // for j in range(3):norm+=F[i,j]*F[i,j]                                          <L 19>
                var_64 = wp::extract(var_6, var_62, var_63);
                var_65 = wp::extract(var_6, var_62, var_63);
                var_66 = wp::mul(var_64, var_65);
                var_67 = wp::add(var_61, var_66);
                var_69 = wp::extract(var_6, var_62, var_68);
                var_70 = wp::extract(var_6, var_62, var_68);
                var_71 = wp::mul(var_69, var_70);
                var_72 = wp::add(var_67, var_71);
                var_74 = wp::extract(var_6, var_62, var_73);
                var_75 = wp::extract(var_6, var_62, var_73);
                var_76 = wp::mul(var_74, var_75);
                var_77 = wp::add(var_72, var_76);
                var_80 = wp::extract(var_6, var_78, var_79);
                var_81 = wp::extract(var_6, var_78, var_79);
                var_82 = wp::mul(var_80, var_81);
                var_83 = wp::add(var_77, var_82);
                var_85 = wp::extract(var_6, var_78, var_84);
                var_86 = wp::extract(var_6, var_78, var_84);
                var_87 = wp::mul(var_85, var_86);
                var_88 = wp::add(var_83, var_87);
                var_90 = wp::extract(var_6, var_78, var_89);
                var_91 = wp::extract(var_6, var_78, var_89);
                var_92 = wp::mul(var_90, var_91);
                var_93 = wp::add(var_88, var_92);
                var_96 = wp::extract(var_6, var_94, var_95);
                var_97 = wp::extract(var_6, var_94, var_95);
                var_98 = wp::mul(var_96, var_97);
                var_99 = wp::add(var_93, var_98);
                var_101 = wp::extract(var_6, var_94, var_100);
                var_102 = wp::extract(var_6, var_94, var_100);
                var_103 = wp::mul(var_101, var_102);
                var_104 = wp::add(var_99, var_103);
                var_106 = wp::extract(var_6, var_94, var_105);
                var_107 = wp::extract(var_6, var_94, var_105);
                var_108 = wp::mul(var_106, var_107);
                var_109 = wp::add(var_104, var_108);
                // energy[p]=vol[p]*(0.5*mu*(norm-3.0)-mu*lj+0.5*lam*lj*lj)                       <L 20>
                var_110 = wp::address(var_vol, var_0);
                var_112 = wp::mul(var_111, var_mu);
                var_114 = wp::sub(var_109, var_113);
                var_115 = wp::mul(var_112, var_114);
                var_116 = wp::mul(var_mu, var_49);
                var_117 = wp::sub(var_115, var_116);
                var_119 = wp::mul(var_118, var_lam);
                var_120 = wp::mul(var_119, var_49);
                var_121 = wp::mul(var_120, var_49);
                var_122 = wp::add(var_117, var_121);
                var_124 = wp::load(var_110);
                var_123 = wp::mul(var_124, var_122);
                wp::array_store(var_energy, var_0, var_123);
            }
            var_125 = wp::where(var_36, var_35, var_58);
            // for e in range(ptr[p],ptr[p+1]):edgeforce[e]=stress*grad[e]                        <L 21>
            var_126 = wp::address(var_ptr, var_0);
            var_128 = wp::add(var_0, var_127);
            var_129 = wp::address(var_ptr, var_128);
            var_131 = wp::load(var_126);
            var_132 = wp::load(var_129);
            var_130 = wp::range(var_131, var_132);
            start_for_2:;
                if (iter_cmp(var_130) == 0) goto end_for_2;
                var_133 = wp::iter_next(var_130);
                var_134 = wp::address(var_grad, var_133);
                var_136 = wp::load(var_134);
                var_135 = wp::mul(var_125, var_136);
                wp::array_store(var_edgeforce, var_133, var_135);
                goto start_for_2;
            end_for_2:;
        }
    }
}


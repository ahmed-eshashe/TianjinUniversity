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



extern "C" __global__ void stress_974edbda_cuda_kernel_forward(
    wp::launch_bounds_t<1> dim,
    wp::array_t<wp::int32> var_ids,
    wp::array_t<wp::vec_t<3, wp::float32>> var_grad,
    wp::array_t<wp::vec_t<3, wp::float32>> var_u,
    wp::array_t<wp::float32> var_vol,
    wp::float32 var_mu,
    wp::float32 var_lam,
    wp::array_t<wp::mat_t<3, 3, wp::float32>> var_P,
    wp::array_t<wp::float32> var_energy,
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
        const wp::int32 var_1 = 3;
        wp::mat_t<3, 3, wp::float32> var_2;
        const wp::int32 var_3 = 0;
        wp::int32* var_4;
        wp::vec_t<3, wp::float32>* var_5;
        wp::int32 var_6;
        wp::vec_t<3, wp::float32> var_7;
        wp::vec_t<3, wp::float32> var_8;
        const wp::int32 var_9 = 1;
        wp::int32* var_10;
        wp::vec_t<3, wp::float32>* var_11;
        wp::int32 var_12;
        wp::vec_t<3, wp::float32> var_13;
        wp::vec_t<3, wp::float32> var_14;
        wp::vec_t<3, wp::float32>* var_15;
        wp::mat_t<3, 3, wp::float32> var_16;
        wp::vec_t<3, wp::float32> var_17;
        wp::mat_t<3, 3, wp::float32> var_18;
        const wp::int32 var_19 = 2;
        wp::int32* var_20;
        wp::vec_t<3, wp::float32>* var_21;
        wp::int32 var_22;
        wp::vec_t<3, wp::float32> var_23;
        wp::vec_t<3, wp::float32> var_24;
        wp::vec_t<3, wp::float32>* var_25;
        wp::mat_t<3, 3, wp::float32> var_26;
        wp::vec_t<3, wp::float32> var_27;
        wp::mat_t<3, 3, wp::float32> var_28;
        const wp::int32 var_29 = 3;
        wp::int32* var_30;
        wp::vec_t<3, wp::float32>* var_31;
        wp::int32 var_32;
        wp::vec_t<3, wp::float32> var_33;
        wp::vec_t<3, wp::float32> var_34;
        wp::vec_t<3, wp::float32>* var_35;
        wp::mat_t<3, 3, wp::float32> var_36;
        wp::vec_t<3, wp::float32> var_37;
        wp::mat_t<3, 3, wp::float32> var_38;
        wp::float32 var_39;
        bool var_40;
        const wp::float32 var_41 = 0.1;
        bool var_42;
        const wp::float32 var_43 = 10.0;
        bool var_44;
        bool var_45;
        bool var_46;
        const wp::int32 var_47 = 0;
        const wp::int32 var_48 = 1;
        wp::int32 var_49;
        const wp::float32 var_50 = 0.0;
        wp::mat_t<3, 3, wp::float32> var_51;
        const wp::float32 var_52 = 0.0;
        wp::float32 var_53;
        wp::float32* var_54;
        wp::mat_t<3, 3, wp::float32> var_55;
        wp::float32 var_56;
        wp::float32 var_57;
        wp::mat_t<3, 3, wp::float32> var_58;
        wp::mat_t<3, 3, wp::float32> var_59;
        wp::mat_t<3, 3, wp::float32> var_60;
        wp::mat_t<3, 3, wp::float32> var_61;
        wp::mat_t<3, 3, wp::float32> var_62;
        wp::float32 var_63;
        const wp::float32 var_64 = 0.0;
        wp::float32 var_65;
        const wp::int32 var_66 = 0;
        const wp::int32 var_67 = 0;
        wp::float32 var_68;
        wp::float32 var_69;
        wp::float32 var_70;
        wp::float32 var_71;
        const wp::int32 var_72 = 1;
        wp::float32 var_73;
        wp::float32 var_74;
        wp::float32 var_75;
        wp::float32 var_76;
        const wp::int32 var_77 = 2;
        wp::float32 var_78;
        wp::float32 var_79;
        wp::float32 var_80;
        wp::float32 var_81;
        const wp::int32 var_82 = 1;
        const wp::int32 var_83 = 0;
        wp::float32 var_84;
        wp::float32 var_85;
        wp::float32 var_86;
        wp::float32 var_87;
        const wp::int32 var_88 = 1;
        wp::float32 var_89;
        wp::float32 var_90;
        wp::float32 var_91;
        wp::float32 var_92;
        const wp::int32 var_93 = 2;
        wp::float32 var_94;
        wp::float32 var_95;
        wp::float32 var_96;
        wp::float32 var_97;
        const wp::int32 var_98 = 2;
        const wp::int32 var_99 = 0;
        wp::float32 var_100;
        wp::float32 var_101;
        wp::float32 var_102;
        wp::float32 var_103;
        const wp::int32 var_104 = 1;
        wp::float32 var_105;
        wp::float32 var_106;
        wp::float32 var_107;
        wp::float32 var_108;
        const wp::int32 var_109 = 2;
        wp::float32 var_110;
        wp::float32 var_111;
        wp::float32 var_112;
        wp::float32 var_113;
        wp::float32* var_114;
        const wp::float32 var_115 = 0.5;
        wp::float32 var_116;
        const wp::float32 var_117 = 3.0;
        wp::float32 var_118;
        wp::float32 var_119;
        wp::float32 var_120;
        wp::float32 var_121;
        const wp::float32 var_122 = 0.5;
        wp::float32 var_123;
        wp::float32 var_124;
        wp::float32 var_125;
        wp::float32 var_126;
        wp::float32 var_127;
        wp::float32 var_128;
        wp::int32 var_129;
        //---------
        // forward
        // def stress(ids:wp.array2d(dtype=int),grad:wp.array2d(dtype=wp.vec3),u:wp.array(dtype=wp.vec3),vol:wp.array(dtype=float),mu:float,lam:float,P:wp.array(dtype=wp.mat33),energy:wp.array(dtype=float),bad:wp.array(dtype=int)):       <L 7>
        // p=wp.tid();F=wp.identity(n=3,dtype=float);u0=u[ids[p,0]]                               <L 8>
        var_0 = builtin_tid1d();
        var_2 = wp::identity<3, wp::float32>();
        var_4 = wp::address(var_ids, var_0, var_3);
        var_6 = wp::load(var_4);
        var_5 = wp::address(var_u, var_6);
        var_8 = wp::load(var_5);
        var_7 = wp::copy(var_8);
        // for j in range(1,4):F+=wp.outer(u[ids[p,j]]-u0,grad[p,j])                              <L 9>
        var_10 = wp::address(var_ids, var_0, var_9);
        var_12 = wp::load(var_10);
        var_11 = wp::address(var_u, var_12);
        var_14 = wp::load(var_11);
        var_13 = wp::sub(var_14, var_7);
        var_15 = wp::address(var_grad, var_0, var_9);
        var_17 = wp::load(var_15);
        var_16 = wp::outer(var_13, var_17);
        var_18 = wp::add(var_2, var_16);
        var_20 = wp::address(var_ids, var_0, var_19);
        var_22 = wp::load(var_20);
        var_21 = wp::address(var_u, var_22);
        var_24 = wp::load(var_21);
        var_23 = wp::sub(var_24, var_7);
        var_25 = wp::address(var_grad, var_0, var_19);
        var_27 = wp::load(var_25);
        var_26 = wp::outer(var_23, var_27);
        var_28 = wp::add(var_18, var_26);
        var_30 = wp::address(var_ids, var_0, var_29);
        var_32 = wp::load(var_30);
        var_31 = wp::address(var_u, var_32);
        var_34 = wp::load(var_31);
        var_33 = wp::sub(var_34, var_7);
        var_35 = wp::address(var_grad, var_0, var_29);
        var_37 = wp::load(var_35);
        var_36 = wp::outer(var_33, var_37);
        var_38 = wp::add(var_28, var_36);
        // J=wp.determinant(F)                                                                    <L 10>
        var_39 = wp::determinant(var_38);
        // if J<=0.1 or J>=10.0 or not wp.isfinite(J):wp.atomic_max(bad,0,1);P[p]=wp.mat33(0.0);energy[p]=0.0       <L 11>
        var_42 = (var_39 <= var_41);
        var_40 = var_42;
        if (!var_40) {
            var_44 = (var_39 >= var_43);
            var_40 = var_40 || var_44;
        }
        if (!var_40) {
            var_45 = wp::isfinite(var_39);
            var_46 = wp::unot(var_45);
            var_40 = var_40 || var_46;
        }
        if (var_40) {
            var_49 = wp::atomic_max(var_bad, var_47, var_48);
            var_51 = wp::mat_t<3, 3, wp::float32>(var_50);
            wp::array_store(var_P, var_0, var_51);
            wp::array_store(var_energy, var_0, var_52);
        }
        if (!var_40) {
            // lj=wp.log(J);P[p]=vol[p]*(mu*F+(lam*lj-mu)*wp.transpose(wp.inverse(F)));s=float(0.)       <L 13>
            var_53 = wp::log(var_39);
            var_54 = wp::address(var_vol, var_0);
            var_55 = wp::mul(var_mu, var_38);
            var_56 = wp::mul(var_lam, var_53);
            var_57 = wp::sub(var_56, var_mu);
            var_58 = wp::inverse(var_38);
            var_59 = wp::transpose(var_58);
            var_60 = wp::mul(var_57, var_59);
            var_61 = wp::add(var_55, var_60);
            var_63 = wp::load(var_54);
            var_62 = wp::mul(var_63, var_61);
            wp::array_store(var_P, var_0, var_62);
            var_65 = wp::float(var_64);
            // for i in range(3):                                                                 <L 14>
            // for j in range(3):s+=F[i,j]*F[i,j]                                                 <L 15>
            var_68 = wp::extract(var_38, var_66, var_67);
            var_69 = wp::extract(var_38, var_66, var_67);
            var_70 = wp::mul(var_68, var_69);
            var_71 = wp::add(var_65, var_70);
            var_73 = wp::extract(var_38, var_66, var_72);
            var_74 = wp::extract(var_38, var_66, var_72);
            var_75 = wp::mul(var_73, var_74);
            var_76 = wp::add(var_71, var_75);
            var_78 = wp::extract(var_38, var_66, var_77);
            var_79 = wp::extract(var_38, var_66, var_77);
            var_80 = wp::mul(var_78, var_79);
            var_81 = wp::add(var_76, var_80);
            var_84 = wp::extract(var_38, var_82, var_83);
            var_85 = wp::extract(var_38, var_82, var_83);
            var_86 = wp::mul(var_84, var_85);
            var_87 = wp::add(var_81, var_86);
            var_89 = wp::extract(var_38, var_82, var_88);
            var_90 = wp::extract(var_38, var_82, var_88);
            var_91 = wp::mul(var_89, var_90);
            var_92 = wp::add(var_87, var_91);
            var_94 = wp::extract(var_38, var_82, var_93);
            var_95 = wp::extract(var_38, var_82, var_93);
            var_96 = wp::mul(var_94, var_95);
            var_97 = wp::add(var_92, var_96);
            var_100 = wp::extract(var_38, var_98, var_99);
            var_101 = wp::extract(var_38, var_98, var_99);
            var_102 = wp::mul(var_100, var_101);
            var_103 = wp::add(var_97, var_102);
            var_105 = wp::extract(var_38, var_98, var_104);
            var_106 = wp::extract(var_38, var_98, var_104);
            var_107 = wp::mul(var_105, var_106);
            var_108 = wp::add(var_103, var_107);
            var_110 = wp::extract(var_38, var_98, var_109);
            var_111 = wp::extract(var_38, var_98, var_109);
            var_112 = wp::mul(var_110, var_111);
            var_113 = wp::add(var_108, var_112);
            // energy[p]=vol[p]*(.5*mu*(s-3.)-mu*lj+.5*lam*lj*lj)                                 <L 16>
            var_114 = wp::address(var_vol, var_0);
            var_116 = wp::mul(var_115, var_mu);
            var_118 = wp::sub(var_113, var_117);
            var_119 = wp::mul(var_116, var_118);
            var_120 = wp::mul(var_mu, var_53);
            var_121 = wp::sub(var_119, var_120);
            var_123 = wp::mul(var_122, var_lam);
            var_124 = wp::mul(var_123, var_53);
            var_125 = wp::mul(var_124, var_53);
            var_126 = wp::add(var_121, var_125);
            var_128 = wp::load(var_114);
            var_127 = wp::mul(var_128, var_126);
            wp::array_store(var_energy, var_0, var_127);
        }
        var_129 = wp::where(var_40, var_29, var_109);
    }
}



extern "C" __global__ void update_c031e9a6_cuda_kernel_forward(
    wp::launch_bounds_t<1> dim,
    wp::array_t<wp::int32> var_ptr,
    wp::array_t<wp::int32> var_idx,
    wp::array_t<wp::vec_t<3, wp::float32>> var_grad,
    wp::array_t<wp::mat_t<3, 3, wp::float32>> var_P,
    wp::array_t<wp::float32> var_mass,
    wp::array_t<wp::vec_t<3, wp::float32>> var_external,
    wp::array_t<wp::vec_t<3, wp::float32>> var_u,
    wp::array_t<wp::vec_t<3, wp::float32>> var_v,
    wp::float32 var_dt,
    wp::int32 var_drift,
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
        wp::vec_t<3, wp::float32>* var_1;
        wp::vec_t<3, wp::float32> var_2;
        wp::vec_t<3, wp::float32> var_3;
        wp::int32* var_4;
        const wp::int32 var_5 = 1;
        wp::int32 var_6;
        wp::int32* var_7;
        wp::range_t var_8;
        wp::int32 var_9;
        wp::int32 var_10;
        wp::int32 var_11;
        wp::int32* var_12;
        wp::mat_t<3, 3, wp::float32>* var_13;
        wp::int32 var_14;
        wp::vec_t<3, wp::float32>* var_15;
        wp::vec_t<3, wp::float32> var_16;
        wp::mat_t<3, 3, wp::float32> var_17;
        wp::vec_t<3, wp::float32> var_18;
        wp::vec_t<3, wp::float32> var_19;
        const wp::int32 var_20 = 0;
        wp::int32* var_21;
        const wp::int32 var_22 = 0;
        bool var_23;
        wp::int32 var_24;
        wp::vec_t<3, wp::float32>* var_25;
        const wp::float32 var_26 = 0.5;
        wp::float32 var_27;
        wp::float32* var_28;
        wp::float32 var_29;
        wp::float32 var_30;
        wp::vec_t<3, wp::float32> var_31;
        wp::vec_t<3, wp::float32> var_32;
        wp::vec_t<3, wp::float32> var_33;
        const wp::int32 var_34 = 1;
        bool var_35;
        wp::vec_t<3, wp::float32> var_36;
        wp::vec_t<3, wp::float32> var_37;
        const wp::int32 var_38 = 0;
        bool var_39;
        wp::float32 var_40;
        bool var_41;
        bool var_42;
        wp::vec_t<3, wp::float32>* var_43;
        wp::float32 var_44;
        wp::vec_t<3, wp::float32> var_45;
        bool var_46;
        bool var_47;
        const wp::int32 var_48 = 0;
        const wp::int32 var_49 = 2;
        wp::int32 var_50;
        const wp::int32 var_51 = 1;
        bool var_52;
        wp::float32 var_53;
        bool var_54;
        bool var_55;
        wp::vec_t<3, wp::float32>* var_56;
        wp::float32 var_57;
        wp::vec_t<3, wp::float32> var_58;
        bool var_59;
        bool var_60;
        const wp::int32 var_61 = 0;
        const wp::int32 var_62 = 2;
        wp::int32 var_63;
        const wp::int32 var_64 = 2;
        bool var_65;
        wp::float32 var_66;
        bool var_67;
        bool var_68;
        wp::vec_t<3, wp::float32>* var_69;
        wp::float32 var_70;
        wp::vec_t<3, wp::float32> var_71;
        bool var_72;
        bool var_73;
        const wp::int32 var_74 = 0;
        const wp::int32 var_75 = 2;
        wp::int32 var_76;
        //---------
        // forward
        // def update(ptr:wp.array(dtype=int),idx:wp.array(dtype=int),grad:wp.array(dtype=wp.vec3),P:wp.array(dtype=wp.mat33),mass:wp.array(dtype=float),external:wp.array(dtype=wp.vec3),u:wp.array(dtype=wp.vec3),v:wp.array(dtype=wp.vec3),dt:float,drift:int,bad:wp.array(dtype=int)):       <L 19>
        // i=wp.tid();force=external[i]                                                           <L 20>
        var_0 = builtin_tid1d();
        var_1 = wp::address(var_external, var_0);
        var_3 = wp::load(var_1);
        var_2 = wp::copy(var_3);
        // for e in range(ptr[i],ptr[i+1]):force-=P[idx[e]]*grad[e]                               <L 21>
        var_4 = wp::address(var_ptr, var_0);
        var_6 = wp::add(var_0, var_5);
        var_7 = wp::address(var_ptr, var_6);
        var_9 = wp::load(var_4);
        var_10 = wp::load(var_7);
        var_8 = wp::range(var_9, var_10);
        start_for_0:;
            if (iter_cmp(var_8) == 0) goto end_for_0;
            var_11 = wp::iter_next(var_8);
            var_12 = wp::address(var_idx, var_11);
            var_14 = wp::load(var_12);
            var_13 = wp::address(var_P, var_14);
            var_15 = wp::address(var_grad, var_11);
            var_17 = wp::load(var_13);
            var_18 = wp::load(var_15);
            var_16 = wp::mul(var_17, var_18);
            var_19 = wp::sub(var_2, var_16);
            wp::assign(var_2, var_19);
            goto start_for_0;
        end_for_0:;
        // if bad[0]==0:                                                                          <L 22>
        var_21 = wp::address(var_bad, var_20);
        var_24 = wp::load(var_21);
        var_23 = (var_24 == var_22);
        if (var_23) {
            // vn=v[i]+(.5*dt/mass[i])*force;v[i]=vn                                              <L 23>
            var_25 = wp::address(var_v, var_0);
            var_27 = wp::mul(var_26, var_dt);
            var_28 = wp::address(var_mass, var_0);
            var_30 = wp::load(var_28);
            var_29 = wp::div(var_27, var_30);
            var_31 = wp::mul(var_29, var_2);
            var_33 = wp::load(var_25);
            var_32 = wp::add(var_33, var_31);
            wp::array_store(var_v, var_0, var_32);
            // if drift==1:u[i]+=dt*vn                                                            <L 24>
            var_35 = (var_drift == var_34);
            if (var_35) {
                var_36 = wp::mul(var_dt, var_32);
                var_37 = wp::atomic_add(var_u, var_0, var_36);
            }
            // for j in range(3):                                                                 <L 25>
            // if not wp.isfinite(vn[j]) or not wp.isfinite(u[i][j]):wp.atomic_max(bad,0,2)       <L 26>
            var_40 = wp::extract(var_32, var_38);
            var_41 = wp::isfinite(var_40);
            var_42 = wp::unot(var_41);
            var_39 = var_42;
            if (!var_39) {
                var_43 = wp::address(var_u, var_0);
                var_45 = wp::load(var_43);
                var_44 = wp::extract(var_45, var_38);
                var_46 = wp::isfinite(var_44);
                var_47 = wp::unot(var_46);
                var_39 = var_39 || var_47;
            }
            if (var_39) {
                var_50 = wp::atomic_max(var_bad, var_48, var_49);
            }
            var_53 = wp::extract(var_32, var_51);
            var_54 = wp::isfinite(var_53);
            var_55 = wp::unot(var_54);
            var_52 = var_55;
            if (!var_52) {
                var_56 = wp::address(var_u, var_0);
                var_58 = wp::load(var_56);
                var_57 = wp::extract(var_58, var_51);
                var_59 = wp::isfinite(var_57);
                var_60 = wp::unot(var_59);
                var_52 = var_52 || var_60;
            }
            if (var_52) {
                var_63 = wp::atomic_max(var_bad, var_61, var_62);
            }
            var_66 = wp::extract(var_32, var_64);
            var_67 = wp::isfinite(var_66);
            var_68 = wp::unot(var_67);
            var_65 = var_68;
            if (!var_65) {
                var_69 = wp::address(var_u, var_0);
                var_71 = wp::load(var_69);
                var_70 = wp::extract(var_71, var_64);
                var_72 = wp::isfinite(var_70);
                var_73 = wp::unot(var_72);
                var_65 = var_65 || var_73;
            }
            if (var_65) {
                var_76 = wp::atomic_max(var_bad, var_74, var_75);
            }
        }
    }
}


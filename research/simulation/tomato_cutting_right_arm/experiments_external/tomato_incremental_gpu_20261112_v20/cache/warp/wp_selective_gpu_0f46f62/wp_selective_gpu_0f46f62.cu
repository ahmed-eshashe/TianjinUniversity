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



extern "C" __global__ void advance_07fe24f2_cuda_kernel_forward(
    wp::launch_bounds_t<1> dim,
    wp::array_t<wp::int32> var_iptr,
    wp::array_t<wp::int32> var_iidx,
    wp::array_t<wp::vec_t<3, wp::float32>> var_ig,
    wp::array_t<wp::mat_t<3, 3, wp::float32>> var_P,
    wp::array_t<wp::int32> var_mptr,
    wp::array_t<wp::int32> var_midx,
    wp::array_t<wp::float32> var_mi,
    wp::array_t<wp::vec_t<3, wp::float32>> var_external,
    wp::array_t<wp::vec_t<3, wp::float32>> var_q,
    wp::array_t<wp::vec_t<3, wp::float32>> var_v,
    wp::float32 var_kick,
    wp::float32 var_drift,
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
        const wp::float32 var_1 = 0.0;
        wp::vec_t<3, wp::float32> var_2;
        wp::int32* var_3;
        const wp::int32 var_4 = 1;
        wp::int32 var_5;
        wp::int32* var_6;
        wp::range_t var_7;
        wp::int32 var_8;
        wp::int32 var_9;
        wp::int32 var_10;
        wp::int32* var_11;
        wp::int32 var_12;
        wp::int32 var_13;
        wp::vec_t<3, wp::float32>* var_14;
        wp::vec_t<3, wp::float32> var_15;
        wp::vec_t<3, wp::float32> var_16;
        wp::int32* var_17;
        const wp::int32 var_18 = 1;
        wp::int32 var_19;
        wp::int32* var_20;
        wp::range_t var_21;
        wp::int32 var_22;
        wp::int32 var_23;
        wp::int32 var_24;
        wp::int32* var_25;
        wp::mat_t<3, 3, wp::float32>* var_26;
        wp::int32 var_27;
        wp::vec_t<3, wp::float32>* var_28;
        wp::vec_t<3, wp::float32> var_29;
        wp::mat_t<3, 3, wp::float32> var_30;
        wp::vec_t<3, wp::float32> var_31;
        wp::vec_t<3, wp::float32> var_32;
        wp::float32* var_33;
        wp::vec_t<3, wp::float32> var_34;
        wp::float32 var_35;
        wp::vec_t<3, wp::float32> var_36;
        const wp::int32 var_37 = 0;
        wp::int32* var_38;
        const wp::int32 var_39 = 0;
        bool var_40;
        wp::int32 var_41;
        wp::vec_t<3, wp::float32>* var_42;
        wp::vec_t<3, wp::float32> var_43;
        wp::vec_t<3, wp::float32> var_44;
        wp::vec_t<3, wp::float32> var_45;
        const wp::float32 var_46 = 0.0;
        bool var_47;
        wp::vec_t<3, wp::float32> var_48;
        wp::vec_t<3, wp::float32> var_49;
        const wp::int32 var_50 = 0;
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
        const wp::int32 var_63 = 1;
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
        const wp::int32 var_76 = 2;
        bool var_77;
        wp::float32 var_78;
        bool var_79;
        bool var_80;
        wp::vec_t<3, wp::float32>* var_81;
        wp::float32 var_82;
        wp::vec_t<3, wp::float32> var_83;
        bool var_84;
        bool var_85;
        const wp::int32 var_86 = 0;
        const wp::int32 var_87 = 2;
        wp::int32 var_88;
        //---------
        // forward
        // def advance(iptr:wp.array(dtype=int),iidx:wp.array(dtype=int),ig:wp.array(dtype=wp.vec3),P:wp.array(dtype=wp.mat33),mptr:wp.array(dtype=int),midx:wp.array(dtype=int),mi:wp.array(dtype=float),external:wp.array(dtype=wp.vec3),q:wp.array(dtype=wp.vec3),v:wp.array(dtype=wp.vec3),kick:float,drift:float,bad:wp.array(dtype=int)):       <L 38>
        // i=wp.tid()                                                                             <L 39>
        var_0 = builtin_tid1d();
        // acc=wp.vec3(0.0)                                                                       <L 40>
        var_2 = wp::vec_t<3, wp::float32>(var_1);
        // for k in range(mptr[i],mptr[i+1]):                                                     <L 41>
        var_3 = wp::address(var_mptr, var_0);
        var_5 = wp::add(var_0, var_4);
        var_6 = wp::address(var_mptr, var_5);
        var_8 = wp::load(var_3);
        var_9 = wp::load(var_6);
        var_7 = wp::range(var_8, var_9);
        start_for_0:;
            if (iter_cmp(var_7) == 0) goto end_for_0;
            var_10 = wp::iter_next(var_7);
            // j=midx[k]                                                                          <L 42>
            var_11 = wp::address(var_midx, var_10);
            var_13 = wp::load(var_11);
            var_12 = wp::copy(var_13);
            // force=external[j]                                                                  <L 43>
            var_14 = wp::address(var_external, var_12);
            var_16 = wp::load(var_14);
            var_15 = wp::copy(var_16);
            // for e in range(iptr[j],iptr[j+1]):force-=P[iidx[e]]*ig[e]                          <L 44>
            var_17 = wp::address(var_iptr, var_12);
            var_19 = wp::add(var_12, var_18);
            var_20 = wp::address(var_iptr, var_19);
            var_22 = wp::load(var_17);
            var_23 = wp::load(var_20);
            var_21 = wp::range(var_22, var_23);
            start_for_2:;
                if (iter_cmp(var_21) == 0) goto end_for_2;
                var_24 = wp::iter_next(var_21);
                var_25 = wp::address(var_iidx, var_24);
                var_27 = wp::load(var_25);
                var_26 = wp::address(var_P, var_27);
                var_28 = wp::address(var_ig, var_24);
                var_30 = wp::load(var_26);
                var_31 = wp::load(var_28);
                var_29 = wp::mul(var_30, var_31);
                var_32 = wp::sub(var_15, var_29);
                wp::assign(var_15, var_32);
                goto start_for_2;
            end_for_2:;
            // acc+=mi[k]*force                                                                   <L 45>
            var_33 = wp::address(var_mi, var_10);
            var_35 = wp::load(var_33);
            var_34 = wp::mul(var_35, var_15);
            var_36 = wp::add(var_2, var_34);
            wp::assign(var_2, var_36);
            goto start_for_0;
        end_for_0:;
        // if bad[0]==0:                                                                          <L 46>
        var_38 = wp::address(var_bad, var_37);
        var_41 = wp::load(var_38);
        var_40 = (var_41 == var_39);
        if (var_40) {
            // vn=v[i]+kick*acc                                                                   <L 47>
            var_42 = wp::address(var_v, var_0);
            var_43 = wp::mul(var_kick, var_2);
            var_45 = wp::load(var_42);
            var_44 = wp::add(var_45, var_43);
            // v[i]=vn                                                                            <L 48>
            wp::array_store(var_v, var_0, var_44);
            // if drift>0.0:q[i]+=drift*vn                                                        <L 49>
            var_47 = (var_drift > var_46);
            if (var_47) {
                var_48 = wp::mul(var_drift, var_44);
                var_49 = wp::atomic_add(var_q, var_0, var_48);
            }
            // for axis in range(3):                                                              <L 50>
            // if not wp.isfinite(vn[axis]) or not wp.isfinite(q[i][axis]):wp.atomic_max(bad,0,2)       <L 51>
            var_52 = wp::extract(var_44, var_50);
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
            var_65 = wp::extract(var_44, var_63);
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
            var_78 = wp::extract(var_44, var_76);
            var_79 = wp::isfinite(var_78);
            var_80 = wp::unot(var_79);
            var_77 = var_80;
            if (!var_77) {
                var_81 = wp::address(var_q, var_0);
                var_83 = wp::load(var_81);
                var_82 = wp::extract(var_83, var_76);
                var_84 = wp::isfinite(var_82);
                var_85 = wp::unot(var_84);
                var_77 = var_77 || var_85;
            }
            if (var_77) {
                var_88 = wp::atomic_max(var_bad, var_86, var_87);
            }
        }
    }
}



extern "C" __global__ void stress_0bca625d_cuda_kernel_forward(
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
        wp::int32* var_3;
        wp::int32* var_4;
        wp::int32 var_5;
        wp::vec_t<3, wp::float32>* var_6;
        wp::int32 var_7;
        wp::vec_t<3, wp::float32> var_8;
        wp::vec_t<3, wp::float32> var_9;
        wp::int32* var_10;
        const wp::int32 var_11 = 1;
        wp::int32 var_12;
        wp::int32 var_13;
        const wp::int32 var_14 = 1;
        wp::int32 var_15;
        wp::int32* var_16;
        wp::range_t var_17;
        wp::int32 var_18;
        wp::int32 var_19;
        wp::int32* var_20;
        wp::vec_t<3, wp::float32>* var_21;
        wp::int32 var_22;
        wp::vec_t<3, wp::float32> var_23;
        wp::vec_t<3, wp::float32> var_24;
        wp::vec_t<3, wp::float32>* var_25;
        wp::mat_t<3, 3, wp::float32> var_26;
        wp::vec_t<3, wp::float32> var_27;
        wp::mat_t<3, 3, wp::float32> var_28;
        wp::float32 var_29;
        bool var_30;
        const wp::float32 var_31 = 0.1;
        bool var_32;
        const wp::float32 var_33 = 10.0;
        bool var_34;
        bool var_35;
        bool var_36;
        const wp::int32 var_37 = 0;
        const wp::int32 var_38 = 1;
        wp::int32 var_39;
        const wp::float32 var_40 = 0.0;
        wp::mat_t<3, 3, wp::float32> var_41;
        const wp::float32 var_42 = 0.0;
        wp::float32 var_43;
        wp::float32* var_44;
        wp::mat_t<3, 3, wp::float32> var_45;
        wp::float32 var_46;
        wp::float32 var_47;
        wp::mat_t<3, 3, wp::float32> var_48;
        wp::mat_t<3, 3, wp::float32> var_49;
        wp::mat_t<3, 3, wp::float32> var_50;
        wp::mat_t<3, 3, wp::float32> var_51;
        wp::mat_t<3, 3, wp::float32> var_52;
        wp::float32 var_53;
        const wp::float32 var_54 = 0.0;
        wp::float32 var_55;
        const wp::int32 var_56 = 0;
        const wp::int32 var_57 = 0;
        wp::float32 var_58;
        wp::float32 var_59;
        wp::float32 var_60;
        wp::float32 var_61;
        const wp::int32 var_62 = 1;
        wp::float32 var_63;
        wp::float32 var_64;
        wp::float32 var_65;
        wp::float32 var_66;
        const wp::int32 var_67 = 2;
        wp::float32 var_68;
        wp::float32 var_69;
        wp::float32 var_70;
        wp::float32 var_71;
        const wp::int32 var_72 = 1;
        const wp::int32 var_73 = 0;
        wp::float32 var_74;
        wp::float32 var_75;
        wp::float32 var_76;
        wp::float32 var_77;
        const wp::int32 var_78 = 1;
        wp::float32 var_79;
        wp::float32 var_80;
        wp::float32 var_81;
        wp::float32 var_82;
        const wp::int32 var_83 = 2;
        wp::float32 var_84;
        wp::float32 var_85;
        wp::float32 var_86;
        wp::float32 var_87;
        const wp::int32 var_88 = 2;
        const wp::int32 var_89 = 0;
        wp::float32 var_90;
        wp::float32 var_91;
        wp::float32 var_92;
        wp::float32 var_93;
        const wp::int32 var_94 = 1;
        wp::float32 var_95;
        wp::float32 var_96;
        wp::float32 var_97;
        wp::float32 var_98;
        const wp::int32 var_99 = 2;
        wp::float32 var_100;
        wp::float32 var_101;
        wp::float32 var_102;
        wp::float32 var_103;
        wp::float32* var_104;
        const wp::float32 var_105 = 0.5;
        wp::float32 var_106;
        const wp::float32 var_107 = 3.0;
        wp::float32 var_108;
        wp::float32 var_109;
        wp::float32 var_110;
        wp::float32 var_111;
        const wp::float32 var_112 = 0.5;
        wp::float32 var_113;
        wp::float32 var_114;
        wp::float32 var_115;
        wp::float32 var_116;
        wp::float32 var_117;
        wp::float32 var_118;
        //---------
        // forward
        // def stress(ptr:wp.array(dtype=int),idx:wp.array(dtype=int),grad:wp.array(dtype=wp.vec3),q:wp.array(dtype=wp.vec3),vol:wp.array(dtype=float),mu:float,lam:float,P:wp.array(dtype=wp.mat33),energy:wp.array(dtype=float),bad:wp.array(dtype=int)):       <L 18>
        // p=wp.tid()                                                                             <L 19>
        var_0 = builtin_tid1d();
        // F=wp.identity(n=3,dtype=float)                                                         <L 20>
        var_2 = wp::identity<3, wp::float32>();
        // q0=q[idx[ptr[p]]]                                                                      <L 21>
        var_3 = wp::address(var_ptr, var_0);
        var_5 = wp::load(var_3);
        var_4 = wp::address(var_idx, var_5);
        var_7 = wp::load(var_4);
        var_6 = wp::address(var_q, var_7);
        var_9 = wp::load(var_6);
        var_8 = wp::copy(var_9);
        // for e in range(ptr[p]+1,ptr[p+1]):                                                     <L 22>
        var_10 = wp::address(var_ptr, var_0);
        var_13 = wp::load(var_10);
        var_12 = wp::add(var_13, var_11);
        var_15 = wp::add(var_0, var_14);
        var_16 = wp::address(var_ptr, var_15);
        var_18 = wp::load(var_16);
        var_17 = wp::range(var_12, var_18);
        start_for_0:;
            if (iter_cmp(var_17) == 0) goto end_for_0;
            var_19 = wp::iter_next(var_17);
            // F+=wp.outer(q[idx[e]]-q0,grad[e])                                                  <L 23>
            var_20 = wp::address(var_idx, var_19);
            var_22 = wp::load(var_20);
            var_21 = wp::address(var_q, var_22);
            var_24 = wp::load(var_21);
            var_23 = wp::sub(var_24, var_8);
            var_25 = wp::address(var_grad, var_19);
            var_27 = wp::load(var_25);
            var_26 = wp::outer(var_23, var_27);
            var_28 = wp::add(var_2, var_26);
            wp::assign(var_2, var_28);
            goto start_for_0;
        end_for_0:;
        // J=wp.determinant(F)                                                                    <L 24>
        var_29 = wp::determinant(var_2);
        // if J<=0.1 or J>=10.0 or not wp.isfinite(J):                                            <L 25>
        var_32 = (var_29 <= var_31);
        var_30 = var_32;
        if (!var_30) {
            var_34 = (var_29 >= var_33);
            var_30 = var_30 || var_34;
        }
        if (!var_30) {
            var_35 = wp::isfinite(var_29);
            var_36 = wp::unot(var_35);
            var_30 = var_30 || var_36;
        }
        if (var_30) {
            // wp.atomic_max(bad,0,1)                                                             <L 26>
            var_39 = wp::atomic_max(var_bad, var_37, var_38);
            // P[p]=wp.mat33(0.0)                                                                 <L 27>
            var_41 = wp::mat_t<3, 3, wp::float32>(var_40);
            wp::array_store(var_P, var_0, var_41);
            // energy[p]=0.0                                                                      <L 28>
            wp::array_store(var_energy, var_0, var_42);
        }
        if (!var_30) {
            // lj=wp.log(J)                                                                       <L 30>
            var_43 = wp::log(var_29);
            // P[p]=vol[p]*(mu*F+(lam*lj-mu)*wp.transpose(wp.inverse(F)))                         <L 31>
            var_44 = wp::address(var_vol, var_0);
            var_45 = wp::mul(var_mu, var_2);
            var_46 = wp::mul(var_lam, var_43);
            var_47 = wp::sub(var_46, var_mu);
            var_48 = wp::inverse(var_2);
            var_49 = wp::transpose(var_48);
            var_50 = wp::mul(var_47, var_49);
            var_51 = wp::add(var_45, var_50);
            var_53 = wp::load(var_44);
            var_52 = wp::mul(var_53, var_51);
            wp::array_store(var_P, var_0, var_52);
            // norm=float(0.0)                                                                    <L 32>
            var_55 = wp::float(var_54);
            // for i in range(3):                                                                 <L 33>
            // for j in range(3):norm+=F[i,j]*F[i,j]                                              <L 34>
            var_58 = wp::extract(var_2, var_56, var_57);
            var_59 = wp::extract(var_2, var_56, var_57);
            var_60 = wp::mul(var_58, var_59);
            var_61 = wp::add(var_55, var_60);
            var_63 = wp::extract(var_2, var_56, var_62);
            var_64 = wp::extract(var_2, var_56, var_62);
            var_65 = wp::mul(var_63, var_64);
            var_66 = wp::add(var_61, var_65);
            var_68 = wp::extract(var_2, var_56, var_67);
            var_69 = wp::extract(var_2, var_56, var_67);
            var_70 = wp::mul(var_68, var_69);
            var_71 = wp::add(var_66, var_70);
            var_74 = wp::extract(var_2, var_72, var_73);
            var_75 = wp::extract(var_2, var_72, var_73);
            var_76 = wp::mul(var_74, var_75);
            var_77 = wp::add(var_71, var_76);
            var_79 = wp::extract(var_2, var_72, var_78);
            var_80 = wp::extract(var_2, var_72, var_78);
            var_81 = wp::mul(var_79, var_80);
            var_82 = wp::add(var_77, var_81);
            var_84 = wp::extract(var_2, var_72, var_83);
            var_85 = wp::extract(var_2, var_72, var_83);
            var_86 = wp::mul(var_84, var_85);
            var_87 = wp::add(var_82, var_86);
            var_90 = wp::extract(var_2, var_88, var_89);
            var_91 = wp::extract(var_2, var_88, var_89);
            var_92 = wp::mul(var_90, var_91);
            var_93 = wp::add(var_87, var_92);
            var_95 = wp::extract(var_2, var_88, var_94);
            var_96 = wp::extract(var_2, var_88, var_94);
            var_97 = wp::mul(var_95, var_96);
            var_98 = wp::add(var_93, var_97);
            var_100 = wp::extract(var_2, var_88, var_99);
            var_101 = wp::extract(var_2, var_88, var_99);
            var_102 = wp::mul(var_100, var_101);
            var_103 = wp::add(var_98, var_102);
            // energy[p]=vol[p]*(0.5*mu*(norm-3.0)-mu*lj+0.5*lam*lj*lj)                           <L 35>
            var_104 = wp::address(var_vol, var_0);
            var_106 = wp::mul(var_105, var_mu);
            var_108 = wp::sub(var_103, var_107);
            var_109 = wp::mul(var_106, var_108);
            var_110 = wp::mul(var_mu, var_43);
            var_111 = wp::sub(var_109, var_110);
            var_113 = wp::mul(var_112, var_lam);
            var_114 = wp::mul(var_113, var_43);
            var_115 = wp::mul(var_114, var_43);
            var_116 = wp::add(var_111, var_115);
            var_118 = wp::load(var_104);
            var_117 = wp::mul(var_118, var_116);
            wp::array_store(var_energy, var_0, var_117);
        }
    }
}



extern "C" __global__ void cache_force_9bbc6475_cuda_kernel_forward(
    wp::launch_bounds_t<1> dim,
    wp::array_t<wp::int32> var_iptr,
    wp::array_t<wp::int32> var_iidx,
    wp::array_t<wp::vec_t<3, wp::float32>> var_ig,
    wp::array_t<wp::mat_t<3, 3, wp::float32>> var_P,
    wp::array_t<wp::vec_t<3, wp::float32>> var_external,
    wp::array_t<wp::vec_t<3, wp::float32>> var_force)
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
        //---------
        // forward
        // def cache_force(iptr:wp.array(dtype=int),iidx:wp.array(dtype=int),ig:wp.array(dtype=wp.vec3),P:wp.array(dtype=wp.mat33),external:wp.array(dtype=wp.vec3),force:wp.array(dtype=wp.vec3)):       <L 54>
        // i=wp.tid()                                                                             <L 55>
        var_0 = builtin_tid1d();
        // f=external[i]                                                                          <L 56>
        var_1 = wp::address(var_external, var_0);
        var_3 = wp::load(var_1);
        var_2 = wp::copy(var_3);
        // for e in range(iptr[i],iptr[i+1]):f-=P[iidx[e]]*ig[e]                                  <L 57>
        var_4 = wp::address(var_iptr, var_0);
        var_6 = wp::add(var_0, var_5);
        var_7 = wp::address(var_iptr, var_6);
        var_9 = wp::load(var_4);
        var_10 = wp::load(var_7);
        var_8 = wp::range(var_9, var_10);
        start_for_0:;
            if (iter_cmp(var_8) == 0) goto end_for_0;
            var_11 = wp::iter_next(var_8);
            var_12 = wp::address(var_iidx, var_11);
            var_14 = wp::load(var_12);
            var_13 = wp::address(var_P, var_14);
            var_15 = wp::address(var_ig, var_11);
            var_17 = wp::load(var_13);
            var_18 = wp::load(var_15);
            var_16 = wp::mul(var_17, var_18);
            var_19 = wp::sub(var_2, var_16);
            wp::assign(var_2, var_19);
            goto start_for_0;
        end_for_0:;
        // force[i]=f                                                                             <L 58>
        wp::array_store(var_force, var_0, var_2);
    }
}



extern "C" __global__ void advance_cached_e3987e6f_cuda_kernel_forward(
    wp::launch_bounds_t<1> dim,
    wp::array_t<wp::int32> var_mptr,
    wp::array_t<wp::int32> var_midx,
    wp::array_t<wp::float32> var_mi,
    wp::array_t<wp::vec_t<3, wp::float32>> var_force,
    wp::array_t<wp::vec_t<3, wp::float32>> var_q,
    wp::array_t<wp::vec_t<3, wp::float32>> var_v,
    wp::float32 var_kick,
    wp::float32 var_drift,
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
        const wp::float32 var_1 = 0.0;
        wp::vec_t<3, wp::float32> var_2;
        wp::int32* var_3;
        const wp::int32 var_4 = 1;
        wp::int32 var_5;
        wp::int32* var_6;
        wp::range_t var_7;
        wp::int32 var_8;
        wp::int32 var_9;
        wp::int32 var_10;
        wp::float32* var_11;
        wp::int32* var_12;
        wp::vec_t<3, wp::float32>* var_13;
        wp::int32 var_14;
        wp::vec_t<3, wp::float32> var_15;
        wp::float32 var_16;
        wp::vec_t<3, wp::float32> var_17;
        wp::vec_t<3, wp::float32> var_18;
        const wp::int32 var_19 = 0;
        wp::int32* var_20;
        const wp::int32 var_21 = 0;
        bool var_22;
        wp::int32 var_23;
        wp::vec_t<3, wp::float32>* var_24;
        wp::vec_t<3, wp::float32> var_25;
        wp::vec_t<3, wp::float32> var_26;
        wp::vec_t<3, wp::float32> var_27;
        const wp::float32 var_28 = 0.0;
        bool var_29;
        wp::vec_t<3, wp::float32> var_30;
        wp::vec_t<3, wp::float32> var_31;
        const wp::int32 var_32 = 0;
        bool var_33;
        wp::float32 var_34;
        bool var_35;
        bool var_36;
        wp::vec_t<3, wp::float32>* var_37;
        wp::float32 var_38;
        wp::vec_t<3, wp::float32> var_39;
        bool var_40;
        bool var_41;
        const wp::int32 var_42 = 0;
        const wp::int32 var_43 = 2;
        wp::int32 var_44;
        const wp::int32 var_45 = 1;
        bool var_46;
        wp::float32 var_47;
        bool var_48;
        bool var_49;
        wp::vec_t<3, wp::float32>* var_50;
        wp::float32 var_51;
        wp::vec_t<3, wp::float32> var_52;
        bool var_53;
        bool var_54;
        const wp::int32 var_55 = 0;
        const wp::int32 var_56 = 2;
        wp::int32 var_57;
        const wp::int32 var_58 = 2;
        bool var_59;
        wp::float32 var_60;
        bool var_61;
        bool var_62;
        wp::vec_t<3, wp::float32>* var_63;
        wp::float32 var_64;
        wp::vec_t<3, wp::float32> var_65;
        bool var_66;
        bool var_67;
        const wp::int32 var_68 = 0;
        const wp::int32 var_69 = 2;
        wp::int32 var_70;
        //---------
        // forward
        // def advance_cached(mptr:wp.array(dtype=int),midx:wp.array(dtype=int),mi:wp.array(dtype=float),force:wp.array(dtype=wp.vec3),q:wp.array(dtype=wp.vec3),v:wp.array(dtype=wp.vec3),kick:float,drift:float,bad:wp.array(dtype=int)):       <L 61>
        // i=wp.tid()                                                                             <L 62>
        var_0 = builtin_tid1d();
        // acc=wp.vec3(0.0)                                                                       <L 63>
        var_2 = wp::vec_t<3, wp::float32>(var_1);
        // for k in range(mptr[i],mptr[i+1]):acc+=mi[k]*force[midx[k]]                            <L 64>
        var_3 = wp::address(var_mptr, var_0);
        var_5 = wp::add(var_0, var_4);
        var_6 = wp::address(var_mptr, var_5);
        var_8 = wp::load(var_3);
        var_9 = wp::load(var_6);
        var_7 = wp::range(var_8, var_9);
        start_for_0:;
            if (iter_cmp(var_7) == 0) goto end_for_0;
            var_10 = wp::iter_next(var_7);
            var_11 = wp::address(var_mi, var_10);
            var_12 = wp::address(var_midx, var_10);
            var_14 = wp::load(var_12);
            var_13 = wp::address(var_force, var_14);
            var_16 = wp::load(var_11);
            var_17 = wp::load(var_13);
            var_15 = wp::mul(var_16, var_17);
            var_18 = wp::add(var_2, var_15);
            wp::assign(var_2, var_18);
            goto start_for_0;
        end_for_0:;
        // if bad[0]==0:                                                                          <L 65>
        var_20 = wp::address(var_bad, var_19);
        var_23 = wp::load(var_20);
        var_22 = (var_23 == var_21);
        if (var_22) {
            // vn=v[i]+kick*acc                                                                   <L 66>
            var_24 = wp::address(var_v, var_0);
            var_25 = wp::mul(var_kick, var_2);
            var_27 = wp::load(var_24);
            var_26 = wp::add(var_27, var_25);
            // v[i]=vn                                                                            <L 67>
            wp::array_store(var_v, var_0, var_26);
            // if drift>0.0:q[i]+=drift*vn                                                        <L 68>
            var_29 = (var_drift > var_28);
            if (var_29) {
                var_30 = wp::mul(var_drift, var_26);
                var_31 = wp::atomic_add(var_q, var_0, var_30);
            }
            // for axis in range(3):                                                              <L 69>
            // if not wp.isfinite(vn[axis]) or not wp.isfinite(q[i][axis]):wp.atomic_max(bad,0,2)       <L 70>
            var_34 = wp::extract(var_26, var_32);
            var_35 = wp::isfinite(var_34);
            var_36 = wp::unot(var_35);
            var_33 = var_36;
            if (!var_33) {
                var_37 = wp::address(var_q, var_0);
                var_39 = wp::load(var_37);
                var_38 = wp::extract(var_39, var_32);
                var_40 = wp::isfinite(var_38);
                var_41 = wp::unot(var_40);
                var_33 = var_33 || var_41;
            }
            if (var_33) {
                var_44 = wp::atomic_max(var_bad, var_42, var_43);
            }
            var_47 = wp::extract(var_26, var_45);
            var_48 = wp::isfinite(var_47);
            var_49 = wp::unot(var_48);
            var_46 = var_49;
            if (!var_46) {
                var_50 = wp::address(var_q, var_0);
                var_52 = wp::load(var_50);
                var_51 = wp::extract(var_52, var_45);
                var_53 = wp::isfinite(var_51);
                var_54 = wp::unot(var_53);
                var_46 = var_46 || var_54;
            }
            if (var_46) {
                var_57 = wp::atomic_max(var_bad, var_55, var_56);
            }
            var_60 = wp::extract(var_26, var_58);
            var_61 = wp::isfinite(var_60);
            var_62 = wp::unot(var_61);
            var_59 = var_62;
            if (!var_59) {
                var_63 = wp::address(var_q, var_0);
                var_65 = wp::load(var_63);
                var_64 = wp::extract(var_65, var_58);
                var_66 = wp::isfinite(var_64);
                var_67 = wp::unot(var_66);
                var_59 = var_59 || var_67;
            }
            if (var_59) {
                var_70 = wp::atomic_max(var_bad, var_68, var_69);
            }
        }
    }
}


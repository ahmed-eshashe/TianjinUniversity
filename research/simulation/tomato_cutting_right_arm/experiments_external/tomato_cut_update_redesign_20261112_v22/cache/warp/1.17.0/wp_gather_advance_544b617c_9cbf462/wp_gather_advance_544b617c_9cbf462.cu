#define WP_NO_BFLOAT16

#define WP_TILE_BLOCK_DIM 32
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



extern "C" __global__ void gather_advance_a277ee7a_cuda_kernel_forward(
    wp::launch_bounds_t<1> dim,
    wp::array_t<wp::int32> var_iptr,
    wp::array_t<wp::int32> var_iidx,
    wp::array_t<wp::vec_t<3, wp::float32>> var_ig,
    wp::array_t<wp::mat_t<3, 3, wp::float32>> var_P,
    wp::array_t<wp::vec_t<3, wp::float32>> var_external,
    wp::array_t<wp::int32> var_mptr,
    wp::array_t<wp::int32> var_midx,
    wp::array_t<wp::float32> var_mi,
    wp::array_t<wp::vec_t<3, wp::float32>> var_q,
    wp::array_t<wp::vec_t<3, wp::float32>> var_velocity,
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
        const wp::int32 var_1 = 32;
        wp::int32 var_2;
        const wp::int32 var_3 = 32;
        wp::int32 var_4;
        const wp::float32 var_5 = 0.0;
        wp::vec_t<3, wp::float32> var_6;
        const wp::int32 var_7 = 0;
        wp::int32* var_8;
        bool var_9;
        wp::int32 var_10;
        wp::int32* var_11;
        const wp::int32 var_12 = 1;
        wp::int32 var_13;
        wp::int32* var_14;
        wp::range_t var_15;
        wp::int32 var_16;
        wp::int32 var_17;
        wp::int32 var_18;
        const wp::float32 var_19 = 0.0;
        wp::vec_t<3, wp::float32> var_20;
        wp::int32* var_21;
        wp::int32 var_22;
        wp::int32 var_23;
        wp::int32* var_24;
        wp::int32 var_25;
        wp::int32 var_26;
        const wp::int32 var_27 = 1;
        wp::int32 var_28;
        wp::int32* var_29;
        const wp::int32 var_30 = 32;
        wp::range_t var_31;
        wp::int32 var_32;
        wp::int32 var_33;
        wp::int32* var_34;
        wp::mat_t<3, 3, wp::float32>* var_35;
        wp::int32 var_36;
        wp::vec_t<3, wp::float32>* var_37;
        wp::vec_t<3, wp::float32> var_38;
        wp::mat_t<3, 3, wp::float32> var_39;
        wp::vec_t<3, wp::float32> var_40;
        wp::vec_t<3, wp::float32> var_41;
        const wp::int32 var_42 = 0;
        bool var_43;
        wp::vec_t<3, wp::float32>* var_44;
        wp::vec_t<3, wp::float32> var_45;
        wp::vec_t<3, wp::float32> var_46;
        wp::vec_t<3, wp::float32> var_47;
        const bool var_48 = true;
        wp::tile_register_t<wp::vec_t<3, wp::float32>,wp::tile_layout_register_t<wp::tile_shape_t<32>>> var_49 = wp::tile_register_t<wp::vec_t<3, wp::float32>,wp::tile_layout_register_t<wp::tile_shape_t<32>>>{};
        wp::tile_shared_t<wp::vec_t<3, wp::float32>,wp::tile_layout_strided_t<wp::tile_shape_t<1>, wp::tile_stride_t<1>>, true> var_50 = wp::tile_alloc_empty<wp::vec_t<3, wp::float32>,wp::tile_shape_t<1>,wp::tile_stride_t<1>,false>();
        const wp::int32 var_51 = 0;
        wp::vec_t<3, wp::float32> var_52;
        wp::float32* var_53;
        wp::vec_t<3, wp::float32> var_54;
        wp::float32 var_55;
        wp::vec_t<3, wp::float32> var_56;
        bool var_57;
        const wp::int32 var_58 = 0;
        bool var_59;
        const wp::int32 var_60 = 0;
        wp::int32* var_61;
        const wp::int32 var_62 = 0;
        bool var_63;
        wp::int32 var_64;
        wp::vec_t<3, wp::float32>* var_65;
        wp::vec_t<3, wp::float32> var_66;
        wp::vec_t<3, wp::float32> var_67;
        wp::vec_t<3, wp::float32> var_68;
        const wp::float32 var_69 = 0.0;
        bool var_70;
        wp::vec_t<3, wp::float32> var_71;
        wp::vec_t<3, wp::float32> var_72;
        const wp::int32 var_73 = 0;
        bool var_74;
        wp::float32 var_75;
        bool var_76;
        bool var_77;
        wp::vec_t<3, wp::float32>* var_78;
        wp::float32 var_79;
        wp::vec_t<3, wp::float32> var_80;
        bool var_81;
        bool var_82;
        const wp::int32 var_83 = 0;
        const wp::int32 var_84 = 2;
        wp::int32 var_85;
        const wp::int32 var_86 = 1;
        bool var_87;
        wp::float32 var_88;
        bool var_89;
        bool var_90;
        wp::vec_t<3, wp::float32>* var_91;
        wp::float32 var_92;
        wp::vec_t<3, wp::float32> var_93;
        bool var_94;
        bool var_95;
        const wp::int32 var_96 = 0;
        const wp::int32 var_97 = 2;
        wp::int32 var_98;
        const wp::int32 var_99 = 2;
        bool var_100;
        wp::float32 var_101;
        bool var_102;
        bool var_103;
        wp::vec_t<3, wp::float32>* var_104;
        wp::float32 var_105;
        wp::vec_t<3, wp::float32> var_106;
        bool var_107;
        bool var_108;
        const wp::int32 var_109 = 0;
        const wp::int32 var_110 = 2;
        wp::int32 var_111;
        //---------
        // forward
        // def gather_advance(iptr:wp.array(dtype=int),iidx:wp.array(dtype=int),ig:wp.array(dtype=wp.vec3),P:wp.array(dtype=wp.mat33),external:wp.array(dtype=wp.vec3),mptr:wp.array(dtype=int),midx:wp.array(dtype=int),mi:wp.array(dtype=float),q:wp.array(dtype=wp.vec3),velocity:wp.array(dtype=wp.vec3),kick:float,drift:float,bad:wp.array(dtype=int),counts:wp.array(dtype=int)):       <L 6>
        // t=wp.tid();i=t//32;lane=t%32;acc=wp.vec3(0.0)                                          <L 7>
        var_0 = builtin_tid1d();
        var_2 = wp::floordiv(var_0, var_1);
        var_4 = wp::mod(var_0, var_3);
        var_6 = wp::vec_t<3, wp::float32>(var_5);
        // if i<counts[0]:                                                                        <L 8>
        var_8 = wp::address(var_counts, var_7);
        var_10 = wp::load(var_8);
        var_9 = (var_2 < var_10);
        if (var_9) {
            // for m in range(mptr[i],mptr[i+1]):                                                 <L 9>
            var_11 = wp::address(var_mptr, var_2);
            var_13 = wp::add(var_2, var_12);
            var_14 = wp::address(var_mptr, var_13);
            var_16 = wp::load(var_11);
            var_17 = wp::load(var_14);
            var_15 = wp::range(var_16, var_17);
            start_for_0:;
                if (iter_cmp(var_15) == 0) goto end_for_0;
                var_18 = wp::iter_next(var_15);
                // f=wp.vec3(0.0);j=midx[m]                                                       <L 10>
                var_20 = wp::vec_t<3, wp::float32>(var_19);
                var_21 = wp::address(var_midx, var_18);
                var_23 = wp::load(var_21);
                var_22 = wp::copy(var_23);
                // for e in range(iptr[j]+lane,iptr[j+1],32):f-=P[iidx[e]]*ig[e]                  <L 11>
                var_24 = wp::address(var_iptr, var_22);
                var_26 = wp::load(var_24);
                var_25 = wp::add(var_26, var_4);
                var_28 = wp::add(var_22, var_27);
                var_29 = wp::address(var_iptr, var_28);
                var_32 = wp::load(var_29);
                var_31 = wp::range(var_25, var_32, var_30);
                start_for_2:;
                    if (iter_cmp(var_31) == 0) goto end_for_2;
                    var_33 = wp::iter_next(var_31);
                    var_34 = wp::address(var_iidx, var_33);
                    var_36 = wp::load(var_34);
                    var_35 = wp::address(var_P, var_36);
                    var_37 = wp::address(var_ig, var_33);
                    var_39 = wp::load(var_35);
                    var_40 = wp::load(var_37);
                    var_38 = wp::mul(var_39, var_40);
                    var_41 = wp::sub(var_20, var_38);
                    wp::assign(var_20, var_41);
                    goto start_for_2;
                end_for_2:;
                // if lane==0:f+=external[j]                                                      <L 12>
                var_43 = (var_4 == var_42);
                if (var_43) {
                    var_44 = wp::address(var_external, var_22);
                    var_46 = wp::load(var_44);
                    var_45 = wp::add(var_20, var_46);
                }
                var_47 = wp::where(var_43, var_45, var_20);
                // total=wp.tile_sum(wp.tile(f,preserve_type=True))                               <L 13>
                var_49 = wp::tile<wp::vec_t<3, wp::float32>>(var_47);
                var_50 = wp::tile_sum(var_49);
                // force=wp.tile_extract(total,0)                                                 <L 14>
                var_52 = wp::tile_extract(var_50, var_51);
                // acc+=mi[m]*force                                                               <L 15>
                var_53 = wp::address(var_mi, var_18);
                var_55 = wp::load(var_53);
                var_54 = wp::mul(var_55, var_52);
                var_56 = wp::add(var_6, var_54);
                wp::assign(var_6, var_56);
                goto start_for_0;
            end_for_0:;
            // if lane==0 and bad[0]==0:                                                          <L 16>
            var_59 = (var_4 == var_58);
            var_57 = var_59;
            if (var_57) {
                var_61 = wp::address(var_bad, var_60);
                var_64 = wp::load(var_61);
                var_63 = (var_64 == var_62);
                var_57 = var_57 && var_63;
            }
            if (var_57) {
                // vn=velocity[i]+kick*acc;velocity[i]=vn                                         <L 17>
                var_65 = wp::address(var_velocity, var_2);
                var_66 = wp::mul(var_kick, var_6);
                var_68 = wp::load(var_65);
                var_67 = wp::add(var_68, var_66);
                wp::array_store(var_velocity, var_2, var_67);
                // if drift>0.:q[i]+=drift*vn                                                     <L 18>
                var_70 = (var_drift > var_69);
                if (var_70) {
                    var_71 = wp::mul(var_drift, var_67);
                    var_72 = wp::atomic_add(var_q, var_2, var_71);
                }
                // for axis in range(3):                                                          <L 19>
                // if not wp.isfinite(vn[axis]) or not wp.isfinite(q[i][axis]):wp.atomic_max(bad,0,2)       <L 20>
                var_75 = wp::extract(var_67, var_73);
                var_76 = wp::isfinite(var_75);
                var_77 = wp::unot(var_76);
                var_74 = var_77;
                if (!var_74) {
                    var_78 = wp::address(var_q, var_2);
                    var_80 = wp::load(var_78);
                    var_79 = wp::extract(var_80, var_73);
                    var_81 = wp::isfinite(var_79);
                    var_82 = wp::unot(var_81);
                    var_74 = var_74 || var_82;
                }
                if (var_74) {
                    var_85 = wp::atomic_max(var_bad, var_83, var_84);
                }
                var_88 = wp::extract(var_67, var_86);
                var_89 = wp::isfinite(var_88);
                var_90 = wp::unot(var_89);
                var_87 = var_90;
                if (!var_87) {
                    var_91 = wp::address(var_q, var_2);
                    var_93 = wp::load(var_91);
                    var_92 = wp::extract(var_93, var_86);
                    var_94 = wp::isfinite(var_92);
                    var_95 = wp::unot(var_94);
                    var_87 = var_87 || var_95;
                }
                if (var_87) {
                    var_98 = wp::atomic_max(var_bad, var_96, var_97);
                }
                var_101 = wp::extract(var_67, var_99);
                var_102 = wp::isfinite(var_101);
                var_103 = wp::unot(var_102);
                var_100 = var_103;
                if (!var_100) {
                    var_104 = wp::address(var_q, var_2);
                    var_106 = wp::load(var_104);
                    var_105 = wp::extract(var_106, var_99);
                    var_107 = wp::isfinite(var_105);
                    var_108 = wp::unot(var_107);
                    var_100 = var_100 || var_108;
                }
                if (var_100) {
                    var_111 = wp::atomic_max(var_bad, var_109, var_110);
                }
            }
        }
    }
}


#define WP_NO_BFLOAT16

#define WP_TILE_BLOCK_DIM 128
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



extern "C" __global__ void gather_advance_4b4a1ea9_cuda_kernel_forward(
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
        wp::int32 var_8;
        const wp::int32 var_9 = 0;
        wp::int32* var_10;
        bool var_11;
        wp::int32 var_12;
        const wp::int32 var_13 = 1;
        wp::int32 var_14;
        wp::int32* var_15;
        wp::int32* var_16;
        wp::int32 var_17;
        wp::int32 var_18;
        wp::int32 var_19;
        wp::int32 var_20;
        const bool var_21 = true;
        wp::tile_register_t<wp::int32,wp::tile_layout_register_t<wp::tile_shape_t<128>>> var_22 = wp::tile_register_t<wp::int32,wp::tile_layout_register_t<wp::tile_shape_t<128>>>{};
        wp::tile_shared_t<wp::int32,wp::tile_layout_strided_t<wp::tile_shape_t<1>, wp::tile_stride_t<1>>, true> var_23 = wp::tile_alloc_empty<wp::int32,wp::tile_shape_t<1>,wp::tile_stride_t<1>,false>();
        const wp::int32 var_24 = 128;
        wp::tuple_t<wp::int32> var_25;
        wp::tile_shared_t<wp::int32,wp::tile_layout_strided_t<wp::tile_shape_t<128>, wp::tile_stride_t<0>>, false> var_26 = nullptr;
        wp::int32 var_27;
        wp::range_t var_28;
        wp::int32 var_29;
        const wp::float32 var_30 = 0.0;
        wp::vec_t<3, wp::float32> var_31;
        const wp::float32 var_32 = 0.0;
        wp::float32 var_33;
        bool var_34;
        wp::int32* var_35;
        wp::int32 var_36;
        wp::int32 var_37;
        wp::int32* var_38;
        wp::int32 var_39;
        wp::int32 var_40;
        wp::float32* var_41;
        wp::float32 var_42;
        wp::float32 var_43;
        wp::int32* var_44;
        wp::int32 var_45;
        wp::int32 var_46;
        const wp::int32 var_47 = 1;
        wp::int32 var_48;
        wp::int32* var_49;
        const wp::int32 var_50 = 32;
        wp::range_t var_51;
        wp::int32 var_52;
        wp::int32 var_53;
        wp::int32* var_54;
        wp::mat_t<3, 3, wp::float32>* var_55;
        wp::int32 var_56;
        wp::vec_t<3, wp::float32>* var_57;
        wp::vec_t<3, wp::float32> var_58;
        wp::mat_t<3, 3, wp::float32> var_59;
        wp::vec_t<3, wp::float32> var_60;
        wp::vec_t<3, wp::float32> var_61;
        const wp::int32 var_62 = 0;
        bool var_63;
        wp::vec_t<3, wp::float32>* var_64;
        wp::vec_t<3, wp::float32> var_65;
        wp::vec_t<3, wp::float32> var_66;
        wp::vec_t<3, wp::float32> var_67;
        wp::vec_t<3, wp::float32> var_68;
        wp::float32 var_69;
        const bool var_70 = true;
        wp::tile_shared_t<wp::vec_t<3, wp::float32>,wp::tile_layout_strided_t<wp::tile_shape_t<128>, wp::tile_stride_t<1>>, true> var_71 = wp::tile_alloc_empty<wp::vec_t<3, wp::float32>,wp::tile_shape_t<128>,wp::tile_stride_t<1>,false>();
        const wp::int32 var_72 = 4;
        const wp::int32 var_73 = 32;
        wp::tuple_t<wp::int32, wp::int32> var_74;
        wp::tile_shared_t<wp::vec_t<3, wp::float32>,wp::tile_layout_strided_t<wp::tile_shape_t<4,32>, wp::tile_stride_t<32,1>>, false> var_75 = nullptr;
        const wp::int32 var_76 = 1;
        wp::tile_shared_t<wp::vec_t<3, wp::float32>,wp::tile_layout_strided_t<wp::tile_shape_t<4>, wp::tile_stride_t<1>>, true> var_77 = wp::tile_alloc_empty<wp::vec_t<3, wp::float32>,wp::tile_shape_t<4>,wp::tile_stride_t<1>,false>();
        const wp::int32 var_78 = 4;
        const wp::int32 var_79 = 1;
        wp::tuple_t<wp::int32, wp::int32> var_80;
        wp::tile_shared_t<wp::vec_t<3, wp::float32>,wp::tile_layout_strided_t<wp::tile_shape_t<4,1>, wp::tile_stride_t<1,1>>, false> var_81 = nullptr;
        const wp::int32 var_82 = 4;
        const wp::int32 var_83 = 32;
        wp::tuple_t<wp::int32, wp::int32> var_84;
        wp::tile_shared_t<wp::vec_t<3, wp::float32>,wp::tile_layout_strided_t<wp::tile_shape_t<4,32>, wp::tile_stride_t<1,0>>, false> var_85 = nullptr;
        const wp::int32 var_86 = 4;
        const wp::int32 var_87 = 32;
        wp::tuple_t<wp::int32, wp::int32> var_88;
        wp::tile_shared_t<wp::vec_t<3, wp::float32>,wp::tile_layout_strided_t<wp::tile_shape_t<4,32>, wp::tile_stride_t<32,1>>, true> var_89 = wp::tile_alloc_empty<wp::vec_t<3, wp::float32>,wp::tile_shape_t<4,32>,wp::tile_stride_t<32,1>,false>();
        const wp::int32 var_90 = 0;
        const wp::int32 var_91 = 0;
        const wp::int32 var_92 = 128;
        wp::tuple_t<wp::int32> var_93;
        wp::tile_shared_t<wp::vec_t<3, wp::float32>,wp::tile_layout_strided_t<wp::tile_shape_t<128>, wp::tile_stride_t<1>>, false> var_94 = nullptr;
        wp::vec_t<3, wp::float32> var_95;
        wp::vec_t<3, wp::float32> var_96;
        wp::vec_t<3, wp::float32> var_97;
        bool var_98;
        const wp::int32 var_99 = 0;
        bool var_100;
        const wp::int32 var_101 = 0;
        wp::int32* var_102;
        bool var_103;
        wp::int32 var_104;
        const wp::int32 var_105 = 0;
        wp::int32* var_106;
        const wp::int32 var_107 = 0;
        bool var_108;
        wp::int32 var_109;
        wp::vec_t<3, wp::float32>* var_110;
        wp::vec_t<3, wp::float32> var_111;
        wp::vec_t<3, wp::float32> var_112;
        wp::vec_t<3, wp::float32> var_113;
        const wp::float32 var_114 = 0.0;
        bool var_115;
        wp::vec_t<3, wp::float32> var_116;
        wp::vec_t<3, wp::float32> var_117;
        const wp::int32 var_118 = 0;
        bool var_119;
        wp::float32 var_120;
        bool var_121;
        bool var_122;
        wp::vec_t<3, wp::float32>* var_123;
        wp::float32 var_124;
        wp::vec_t<3, wp::float32> var_125;
        bool var_126;
        bool var_127;
        const wp::int32 var_128 = 0;
        const wp::int32 var_129 = 2;
        wp::int32 var_130;
        const wp::int32 var_131 = 1;
        bool var_132;
        wp::float32 var_133;
        bool var_134;
        bool var_135;
        wp::vec_t<3, wp::float32>* var_136;
        wp::float32 var_137;
        wp::vec_t<3, wp::float32> var_138;
        bool var_139;
        bool var_140;
        const wp::int32 var_141 = 0;
        const wp::int32 var_142 = 2;
        wp::int32 var_143;
        const wp::int32 var_144 = 2;
        bool var_145;
        wp::float32 var_146;
        bool var_147;
        bool var_148;
        wp::vec_t<3, wp::float32>* var_149;
        wp::float32 var_150;
        wp::vec_t<3, wp::float32> var_151;
        bool var_152;
        bool var_153;
        const wp::int32 var_154 = 0;
        const wp::int32 var_155 = 2;
        wp::int32 var_156;
        //---------
        // forward
        // def gather_advance(iptr:wp.array(dtype=int),iidx:wp.array(dtype=int),ig:wp.array(dtype=wp.vec3),P:wp.array(dtype=wp.mat33),external:wp.array(dtype=wp.vec3),mptr:wp.array(dtype=int),midx:wp.array(dtype=int),mi:wp.array(dtype=float),q:wp.array(dtype=wp.vec3),velocity:wp.array(dtype=wp.vec3),kick:float,drift:float,bad:wp.array(dtype=int),counts:wp.array(dtype=int)):       <L 10>
        // t=wp.tid();i=t//32;lane=t%32;acc=wp.vec3(0.0)                                          <L 11>
        var_0 = builtin_tid1d();
        var_2 = wp::floordiv(var_0, var_1);
        var_4 = wp::mod(var_0, var_3);
        var_6 = wp::vec_t<3, wp::float32>(var_5);
        // width=int(0)                                                                           <L 14>
        var_8 = wp::int(var_7);
        // if i<counts[0]:width=mptr[i+1]-mptr[i]                                                 <L 15>
        var_10 = wp::address(var_counts, var_9);
        var_12 = wp::load(var_10);
        var_11 = (var_2 < var_12);
        if (var_11) {
            var_14 = wp::add(var_2, var_13);
            var_15 = wp::address(var_mptr, var_14);
            var_16 = wp::address(var_mptr, var_2);
            var_18 = wp::load(var_15);
            var_19 = wp::load(var_16);
            var_17 = wp::sub(var_18, var_19);
        }
        var_20 = wp::where(var_11, var_17, var_8);
        // widths=wp.tile(width,preserve_type=True)                                               <L 16>
        var_22 = wp::tile<wp::int32>(var_20);
        // widthmax=wp.tile_max(widths)                                                           <L 17>
        var_23 = wp::tile_max(var_22);
        // steps=wp.untile(wp.tile_broadcast(widthmax,shape=(128,)))                              <L 18>
        var_25 = wp::tuple(var_24);
        var_26 = wp::tile_broadcast<128, 0>(var_23);
        var_27 = wp::untile(var_26);
        // for m in range(steps):                                                                 <L 19>
        var_28 = wp::range(var_27);
        start_for_0:;
            if (iter_cmp(var_28) == 0) goto end_for_0;
            var_29 = wp::iter_next(var_28);
            // f=wp.vec3(0.0);weight=float(0.0)                                                   <L 20>
            var_31 = wp::vec_t<3, wp::float32>(var_30);
            var_33 = wp::float(var_32);
            // if m<width:                                                                        <L 21>
            var_34 = (var_29 < var_20);
            if (var_34) {
                // e=mptr[i]+m;j=midx[e];weight=mi[e]                                             <L 22>
                var_35 = wp::address(var_mptr, var_2);
                var_37 = wp::load(var_35);
                var_36 = wp::add(var_37, var_29);
                var_38 = wp::address(var_midx, var_36);
                var_40 = wp::load(var_38);
                var_39 = wp::copy(var_40);
                var_41 = wp::address(var_mi, var_36);
                var_43 = wp::load(var_41);
                var_42 = wp::copy(var_43);
                // for e2 in range(iptr[j]+lane,iptr[j+1],32):f-=P[iidx[e2]]*ig[e2]               <L 23>
                var_44 = wp::address(var_iptr, var_39);
                var_46 = wp::load(var_44);
                var_45 = wp::add(var_46, var_4);
                var_48 = wp::add(var_39, var_47);
                var_49 = wp::address(var_iptr, var_48);
                var_52 = wp::load(var_49);
                var_51 = wp::range(var_45, var_52, var_50);
                start_for_2:;
                    if (iter_cmp(var_51) == 0) goto end_for_2;
                    var_53 = wp::iter_next(var_51);
                    var_54 = wp::address(var_iidx, var_53);
                    var_56 = wp::load(var_54);
                    var_55 = wp::address(var_P, var_56);
                    var_57 = wp::address(var_ig, var_53);
                    var_59 = wp::load(var_55);
                    var_60 = wp::load(var_57);
                    var_58 = wp::mul(var_59, var_60);
                    var_61 = wp::sub(var_31, var_58);
                    wp::assign(var_31, var_61);
                    goto start_for_2;
                end_for_2:;
                // if lane==0:f+=external[j]                                                      <L 24>
                var_63 = (var_4 == var_62);
                if (var_63) {
                    var_64 = wp::address(var_external, var_39);
                    var_66 = wp::load(var_64);
                    var_65 = wp::add(var_31, var_66);
                }
                var_67 = wp::where(var_63, var_65, var_31);
            }
            var_68 = wp::where(var_34, var_67, var_31);
            var_69 = wp::where(var_34, var_42, var_33);
            // total=wp.tile_sum(wp.tile_reshape(wp.tile(f,preserve_type=True),(4,32)),axis=1)       <L 25>
            var_71 = wp::tile<wp::vec_t<3, wp::float32>>(var_68);
            var_74 = wp::tuple(var_72, var_73);
            var_75 = wp::tile_reshape<wp::tile_shared_t<wp::vec_t<3, wp::float32>,wp::tile_layout_strided_t<wp::tile_shape_t<4,32>, wp::tile_stride_t<32,1>>, false>>(var_71);
            var_77 = wp::tile_sum<1>(var_75);
            // ff=wp.tile_broadcast(wp.tile_reshape(total,(4,1)),shape=(4,32))                    <L 27>
            var_80 = wp::tuple(var_78, var_79);
            var_81 = wp::tile_reshape<wp::tile_shared_t<wp::vec_t<3, wp::float32>,wp::tile_layout_strided_t<wp::tile_shape_t<4,1>, wp::tile_stride_t<1,1>>, false>>(var_77);
            var_84 = wp::tuple(var_82, var_83);
            var_85 = wp::tile_broadcast<4, 32, 1, 0>(var_81);
            // copied=wp.tile_zeros(shape=(4,32),dtype=wp.vec3)                                   <L 28>
            var_88 = wp::tuple(var_86, var_87);
            var_89 = wp::tile_zeros<wp::vec_t<3, wp::float32>, 4, 32>();
            // wp.tile_assign(copied,ff)                                                          <L 29>
            wp::tile_assign(var_89, var_85, var_90, var_91);
            // force=wp.untile(wp.tile_reshape(copied,(128,)))                                    <L 30>
            var_93 = wp::tuple(var_92);
            var_94 = wp::tile_reshape<wp::tile_shared_t<wp::vec_t<3, wp::float32>,wp::tile_layout_strided_t<wp::tile_shape_t<128>, wp::tile_stride_t<1>>, false>>(var_89);
            var_95 = wp::untile(var_94);
            // acc+=weight*force                                                                  <L 31>
            var_96 = wp::mul(var_69, var_95);
            var_97 = wp::add(var_6, var_96);
            wp::assign(var_6, var_97);
            goto start_for_0;
        end_for_0:;
        // if lane==0 and i<counts[0] and bad[0]==0:                                              <L 32>
        var_100 = (var_4 == var_99);
        var_98 = var_100;
        if (var_98) {
            var_102 = wp::address(var_counts, var_101);
            var_104 = wp::load(var_102);
            var_103 = (var_2 < var_104);
            var_98 = var_98 && var_103;
        }
        if (var_98) {
            var_106 = wp::address(var_bad, var_105);
            var_109 = wp::load(var_106);
            var_108 = (var_109 == var_107);
            var_98 = var_98 && var_108;
        }
        if (var_98) {
            // vn=velocity[i]+kick*acc;velocity[i]=vn                                             <L 33>
            var_110 = wp::address(var_velocity, var_2);
            var_111 = wp::mul(var_kick, var_6);
            var_113 = wp::load(var_110);
            var_112 = wp::add(var_113, var_111);
            wp::array_store(var_velocity, var_2, var_112);
            // if drift>0.:q[i]+=drift*vn                                                         <L 34>
            var_115 = (var_drift > var_114);
            if (var_115) {
                var_116 = wp::mul(var_drift, var_112);
                var_117 = wp::atomic_add(var_q, var_2, var_116);
            }
            // for axis in range(3):                                                              <L 35>
            // if not wp.isfinite(vn[axis]) or not wp.isfinite(q[i][axis]):wp.atomic_max(bad,0,2)       <L 36>
            var_120 = wp::extract(var_112, var_118);
            var_121 = wp::isfinite(var_120);
            var_122 = wp::unot(var_121);
            var_119 = var_122;
            if (!var_119) {
                var_123 = wp::address(var_q, var_2);
                var_125 = wp::load(var_123);
                var_124 = wp::extract(var_125, var_118);
                var_126 = wp::isfinite(var_124);
                var_127 = wp::unot(var_126);
                var_119 = var_119 || var_127;
            }
            if (var_119) {
                var_130 = wp::atomic_max(var_bad, var_128, var_129);
            }
            var_133 = wp::extract(var_112, var_131);
            var_134 = wp::isfinite(var_133);
            var_135 = wp::unot(var_134);
            var_132 = var_135;
            if (!var_132) {
                var_136 = wp::address(var_q, var_2);
                var_138 = wp::load(var_136);
                var_137 = wp::extract(var_138, var_131);
                var_139 = wp::isfinite(var_137);
                var_140 = wp::unot(var_139);
                var_132 = var_132 || var_140;
            }
            if (var_132) {
                var_143 = wp::atomic_max(var_bad, var_141, var_142);
            }
            var_146 = wp::extract(var_112, var_144);
            var_147 = wp::isfinite(var_146);
            var_148 = wp::unot(var_147);
            var_145 = var_148;
            if (!var_145) {
                var_149 = wp::address(var_q, var_2);
                var_151 = wp::load(var_149);
                var_150 = wp::extract(var_151, var_144);
                var_152 = wp::isfinite(var_150);
                var_153 = wp::unot(var_152);
                var_145 = var_145 || var_153;
            }
            if (var_145) {
                var_156 = wp::atomic_max(var_bad, var_154, var_155);
            }
        }
    }
}


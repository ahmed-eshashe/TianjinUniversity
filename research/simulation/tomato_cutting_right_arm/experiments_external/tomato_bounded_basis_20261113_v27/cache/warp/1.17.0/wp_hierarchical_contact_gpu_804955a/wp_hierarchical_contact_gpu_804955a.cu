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



extern "C" __global__ void corner_frame_b877d902_cuda_kernel_forward(
    wp::launch_bounds_t<1> dim,
    wp::mat_t<3, 3, wp::float64> var_R,
    wp::vec_t<3, wp::float64> var_T0,
    wp::vec_t<3, wp::float64> var_travel,
    wp::float64 var_load,
    wp::float64 var_hold,
    wp::array_t<wp::float64> var_clock,
    wp::array_t<wp::int32> var_ptr,
    wp::array_t<wp::int32> var_ids,
    wp::array_t<wp::float64> var_weights,
    wp::array_t<wp::vec_t<3, wp::float64>> var_ref,
    wp::array_t<wp::vec_t<3, wp::float32>> var_q,
    wp::array_t<wp::vec_t<3, wp::float64>> var_corners,
    wp::array_t<wp::vec_t<3, wp::float64>> var_pose)
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
        wp::float64* var_2;
        wp::float64 var_3;
        wp::float64 var_4;
        wp::float64 var_5;
        wp::float64 var_6;
        wp::float64 var_7;
        bool var_8;
        wp::float64 var_9;
        wp::float64 var_10;
        wp::float64 var_11;
        wp::float64 var_12;
        wp::float64 var_13;
        wp::float64 var_14;
        wp::float64 var_15;
        wp::float64 var_16;
        wp::float64 var_17;
        wp::float64 var_18;
        wp::float64 var_19;
        wp::float64 var_20;
        wp::float64 var_21;
        wp::float64 var_22;
        wp::float64 var_23;
        bool var_24;
        wp::float64 var_25;
        wp::float64 var_26;
        wp::float64 var_27;
        wp::float64 var_28;
        bool var_29;
        wp::float64 var_30;
        wp::float64 var_31;
        wp::float64 var_32;
        wp::float64 var_33;
        wp::float64 var_34;
        wp::float64 var_35;
        wp::float64 var_36;
        wp::float64 var_37;
        wp::float64 var_38;
        wp::float64 var_39;
        wp::float64 var_40;
        wp::float64 var_41;
        wp::float64 var_42;
        wp::float64 var_43;
        wp::float64 var_44;
        wp::float64 var_45;
        wp::float64 var_46;
        wp::float64 var_47;
        wp::float64 var_48;
        wp::float64 var_49;
        wp::float64 var_50;
        wp::float64 var_51;
        wp::vec_t<3, wp::float64> var_52;
        wp::vec_t<3, wp::float64> var_53;
        wp::vec_t<3, wp::float64> var_54;
        wp::vec_t<3, wp::float64>* var_55;
        wp::vec_t<3, wp::float64> var_56;
        wp::vec_t<3, wp::float64> var_57;
        wp::int32* var_58;
        const wp::int32 var_59 = 1;
        wp::int32 var_60;
        wp::int32* var_61;
        wp::range_t var_62;
        wp::int32 var_63;
        wp::int32 var_64;
        wp::int32 var_65;
        wp::float64* var_66;
        wp::int32* var_67;
        wp::vec_t<3, wp::float32>* var_68;
        wp::int32 var_69;
        wp::vec_t<3, wp::float64> var_70;
        wp::vec_t<3, wp::float32> var_71;
        wp::vec_t<3, wp::float64> var_72;
        wp::float64 var_73;
        wp::vec_t<3, wp::float64> var_74;
        wp::mat_t<3, 3, wp::float64> var_75;
        wp::vec_t<3, wp::float64> var_76;
        wp::vec_t<3, wp::float64> var_77;
        const wp::int32 var_78 = 0;
        bool var_79;
        const wp::int32 var_80 = 0;
        const wp::int32 var_81 = 1;
        //---------
        // forward
        // def corner_frame(R:wp.mat33d,T0:wp.vec3d,travel:wp.vec3d,load:wp.float64,hold:wp.float64,clock:wp.array(dtype=wp.float64),ptr:wp.array(dtype=int),ids:wp.array(dtype=int),weights:wp.array(dtype=wp.float64),ref:wp.array(dtype=wp.vec3d),q:wp.array(dtype=wp.vec3),corners:wp.array(dtype=wp.vec3d),pose:wp.array(dtype=wp.vec3d)):       <L 15>
        // i=wp.tid();t=clock[0];shape=wp.float64(0.);speed=wp.float64(0.);pi=wp.float64(3.141592653589793)       <L 16>
        var_0 = builtin_tid1d();
        var_2 = wp::address(var_clock, var_1);
        var_4 = wp::load(var_2);
        var_3 = wp::copy(var_4);
        var_5 = 0.0;
        var_6 = 0.0;
        var_7 = 3.141592653589793;
        // if t<load:shape=wp.float64(.5)*(wp.float64(1.)-wp.cos(pi*t/load));speed=wp.float64(.5)*pi/load*wp.sin(pi*t/load)       <L 17>
        var_8 = (var_3 < var_load);
        if (var_8) {
            var_9 = 0.5;
            var_10 = 1.0;
            var_11 = wp::mul(var_7, var_3);
            var_12 = wp::div(var_11, var_load);
            var_13 = wp::cos(var_12);
            var_14 = wp::sub(var_10, var_13);
            var_15 = wp::mul(var_9, var_14);
            var_16 = 0.5;
            var_17 = wp::mul(var_16, var_7);
            var_18 = wp::div(var_17, var_load);
            var_19 = wp::mul(var_7, var_3);
            var_20 = wp::div(var_19, var_load);
            var_21 = wp::sin(var_20);
            var_22 = wp::mul(var_18, var_21);
        }
        if (!var_8) {
            // elif t<load+hold:shape=wp.float64(1.)                                              <L 18>
            var_23 = wp::add(var_load, var_hold);
            var_24 = (var_3 < var_23);
            if (var_24) {
                var_25 = 1.0;
            }
            if (!var_24) {
                // elif t<wp.float64(2.)*load+hold:                                               <L 19>
                var_26 = 2.0;
                var_27 = wp::mul(var_26, var_load);
                var_28 = wp::add(var_27, var_hold);
                var_29 = (var_3 < var_28);
                if (var_29) {
                    // z=(t-load-hold)/load;shape=wp.float64(.5)*(wp.float64(1.)+wp.cos(pi*z));speed=-wp.float64(.5)*pi/load*wp.sin(pi*z)       <L 20>
                    var_30 = wp::sub(var_3, var_load);
                    var_31 = wp::sub(var_30, var_hold);
                    var_32 = wp::div(var_31, var_load);
                    var_33 = 0.5;
                    var_34 = 1.0;
                    var_35 = wp::mul(var_7, var_32);
                    var_36 = wp::cos(var_35);
                    var_37 = wp::add(var_34, var_36);
                    var_38 = wp::mul(var_33, var_37);
                    var_39 = 0.5;
                    var_40 = wp::neg(var_39);
                    var_41 = wp::mul(var_40, var_7);
                    var_42 = wp::div(var_41, var_load);
                    var_43 = wp::mul(var_7, var_32);
                    var_44 = wp::sin(var_43);
                    var_45 = wp::mul(var_42, var_44);
                }
                var_46 = wp::where(var_29, var_38, var_5);
                var_47 = wp::where(var_29, var_45, var_6);
            }
            var_48 = wp::where(var_24, var_25, var_46);
            var_49 = wp::where(var_24, var_6, var_47);
        }
        var_50 = wp::where(var_8, var_15, var_48);
        var_51 = wp::where(var_8, var_22, var_49);
        // T=T0+travel*shape;tv=travel*speed;x=ref[i]                                             <L 21>
        var_52 = wp::mul(var_travel, var_50);
        var_53 = wp::add(var_T0, var_52);
        var_54 = wp::mul(var_travel, var_51);
        var_55 = wp::address(var_ref, var_0);
        var_57 = wp::load(var_55);
        var_56 = wp::copy(var_57);
        // for k in range(ptr[i],ptr[i+1]):x+=weights[k]*wp.vec3d(q[ids[k]])                      <L 22>
        var_58 = wp::address(var_ptr, var_0);
        var_60 = wp::add(var_0, var_59);
        var_61 = wp::address(var_ptr, var_60);
        var_63 = wp::load(var_58);
        var_64 = wp::load(var_61);
        var_62 = wp::range(var_63, var_64);
        start_for_0:;
            if (iter_cmp(var_62) == 0) goto end_for_0;
            var_65 = wp::iter_next(var_62);
            var_66 = wp::address(var_weights, var_65);
            var_67 = wp::address(var_ids, var_65);
            var_69 = wp::load(var_67);
            var_68 = wp::address(var_q, var_69);
            var_71 = wp::load(var_68);
            var_70 = wp::vec_t<3, wp::float64>(var_71);
            var_73 = wp::load(var_66);
            var_72 = wp::mul(var_73, var_70);
            var_74 = wp::add(var_56, var_72);
            wp::assign(var_56, var_74);
            goto start_for_0;
        end_for_0:;
        // corners[i]=wp.transpose(R)*(x-T)                                                       <L 23>
        var_75 = wp::transpose(var_R);
        var_76 = wp::sub(var_56, var_53);
        var_77 = wp::mul(var_75, var_76);
        wp::array_store(var_corners, var_0, var_77);
        // if i==0:pose[0]=T;pose[1]=tv                                                           <L 24>
        var_79 = (var_0 == var_78);
        if (var_79) {
            wp::array_store(var_pose, var_80, var_53);
            wp::array_store(var_pose, var_81, var_54);
        }
    }
}



extern "C" __global__ void exact_active_frame_e4922d1c_cuda_kernel_forward(
    wp::launch_bounds_t<1> dim,
    wp::mat_t<3, 3, wp::float64> var_R,
    wp::array_t<wp::vec_t<3, wp::float64>> var_pose,
    wp::array_t<wp::int32> var_ptr,
    wp::array_t<wp::int32> var_ids,
    wp::array_t<wp::float64> var_w,
    wp::array_t<wp::vec_t<3, wp::float64>> var_ref,
    wp::array_t<wp::vec_t<3, wp::float32>> var_q,
    wp::array_t<wp::vec_t<3, wp::float32>> var_v,
    wp::array_t<wp::mat_t<3, 3, wp::float64>> var_X,
    wp::array_t<wp::mat_t<3, 3, wp::float64>> var_V,
    wp::array_t<wp::mat_t<3, 3, wp::float64>> var_local,
    wp::array_t<wp::int32> var_bcount,
    wp::array_t<wp::int32> var_bids,
    wp::vec_t<3, wp::float64> var_lo,
    wp::vec_t<3, wp::float64> var_hi,
    wp::array_t<wp::int32> var_count,
    wp::array_t<wp::int32> var_faces,
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
        wp::int32* var_11;
        wp::int32 var_12;
        wp::int32 var_13;
        const wp::int32 var_14 = 0;
        wp::vec_t<3, wp::float64>* var_15;
        wp::vec_t<3, wp::float64> var_16;
        wp::vec_t<3, wp::float64> var_17;
        wp::float64 var_18;
        wp::mat_t<3, 3, wp::float64> var_19;
        wp::float64 var_20;
        wp::mat_t<3, 3, wp::float64> var_21;
        wp::float64 var_22;
        wp::mat_t<3, 3, wp::float64> var_23;
        const wp::int32 var_24 = 0;
        const wp::int32 var_25 = 3;
        wp::int32 var_26;
        wp::int32 var_27;
        wp::vec_t<3, wp::float64>* var_28;
        wp::vec_t<3, wp::float64> var_29;
        wp::vec_t<3, wp::float64> var_30;
        wp::float64 var_31;
        wp::vec_t<3, wp::float64> var_32;
        wp::int32* var_33;
        const wp::int32 var_34 = 1;
        wp::int32 var_35;
        wp::int32* var_36;
        wp::range_t var_37;
        wp::int32 var_38;
        wp::int32 var_39;
        wp::int32 var_40;
        wp::float64* var_41;
        wp::int32* var_42;
        wp::vec_t<3, wp::float32>* var_43;
        wp::int32 var_44;
        wp::vec_t<3, wp::float64> var_45;
        wp::vec_t<3, wp::float32> var_46;
        wp::vec_t<3, wp::float64> var_47;
        wp::float64 var_48;
        wp::vec_t<3, wp::float64> var_49;
        wp::float64* var_50;
        wp::int32* var_51;
        wp::vec_t<3, wp::float32>* var_52;
        wp::int32 var_53;
        wp::vec_t<3, wp::float64> var_54;
        wp::vec_t<3, wp::float32> var_55;
        wp::vec_t<3, wp::float64> var_56;
        wp::float64 var_57;
        wp::vec_t<3, wp::float64> var_58;
        wp::mat_t<3, 3, wp::float64> var_59;
        wp::vec_t<3, wp::float64> var_60;
        wp::vec_t<3, wp::float64> var_61;
        const wp::int32 var_62 = 0;
        wp::float64 var_63;
        wp::float64 var_64;
        wp::float64 var_65;
        const wp::int32 var_66 = 1;
        wp::float64 var_67;
        wp::float64 var_68;
        wp::float64 var_69;
        const wp::int32 var_70 = 2;
        wp::float64 var_71;
        wp::float64 var_72;
        wp::float64 var_73;
        const wp::int32 var_74 = 1;
        const wp::int32 var_75 = 3;
        wp::int32 var_76;
        wp::int32 var_77;
        wp::vec_t<3, wp::float64>* var_78;
        wp::vec_t<3, wp::float64> var_79;
        wp::vec_t<3, wp::float64> var_80;
        wp::float64 var_81;
        wp::vec_t<3, wp::float64> var_82;
        wp::int32* var_83;
        const wp::int32 var_84 = 1;
        wp::int32 var_85;
        wp::int32* var_86;
        wp::range_t var_87;
        wp::int32 var_88;
        wp::int32 var_89;
        wp::int32 var_90;
        wp::float64* var_91;
        wp::int32* var_92;
        wp::vec_t<3, wp::float32>* var_93;
        wp::int32 var_94;
        wp::vec_t<3, wp::float64> var_95;
        wp::vec_t<3, wp::float32> var_96;
        wp::vec_t<3, wp::float64> var_97;
        wp::float64 var_98;
        wp::vec_t<3, wp::float64> var_99;
        wp::float64* var_100;
        wp::int32* var_101;
        wp::vec_t<3, wp::float32>* var_102;
        wp::int32 var_103;
        wp::vec_t<3, wp::float64> var_104;
        wp::vec_t<3, wp::float32> var_105;
        wp::vec_t<3, wp::float64> var_106;
        wp::float64 var_107;
        wp::vec_t<3, wp::float64> var_108;
        wp::mat_t<3, 3, wp::float64> var_109;
        wp::vec_t<3, wp::float64> var_110;
        wp::vec_t<3, wp::float64> var_111;
        const wp::int32 var_112 = 0;
        wp::float64 var_113;
        wp::float64 var_114;
        wp::float64 var_115;
        const wp::int32 var_116 = 1;
        wp::float64 var_117;
        wp::float64 var_118;
        wp::float64 var_119;
        const wp::int32 var_120 = 2;
        wp::float64 var_121;
        wp::float64 var_122;
        wp::float64 var_123;
        const wp::int32 var_124 = 2;
        const wp::int32 var_125 = 3;
        wp::int32 var_126;
        wp::int32 var_127;
        wp::vec_t<3, wp::float64>* var_128;
        wp::vec_t<3, wp::float64> var_129;
        wp::vec_t<3, wp::float64> var_130;
        wp::float64 var_131;
        wp::vec_t<3, wp::float64> var_132;
        wp::int32* var_133;
        const wp::int32 var_134 = 1;
        wp::int32 var_135;
        wp::int32* var_136;
        wp::range_t var_137;
        wp::int32 var_138;
        wp::int32 var_139;
        wp::int32 var_140;
        wp::float64* var_141;
        wp::int32* var_142;
        wp::vec_t<3, wp::float32>* var_143;
        wp::int32 var_144;
        wp::vec_t<3, wp::float64> var_145;
        wp::vec_t<3, wp::float32> var_146;
        wp::vec_t<3, wp::float64> var_147;
        wp::float64 var_148;
        wp::vec_t<3, wp::float64> var_149;
        wp::float64* var_150;
        wp::int32* var_151;
        wp::vec_t<3, wp::float32>* var_152;
        wp::int32 var_153;
        wp::vec_t<3, wp::float64> var_154;
        wp::vec_t<3, wp::float32> var_155;
        wp::vec_t<3, wp::float64> var_156;
        wp::float64 var_157;
        wp::vec_t<3, wp::float64> var_158;
        wp::mat_t<3, 3, wp::float64> var_159;
        wp::vec_t<3, wp::float64> var_160;
        wp::vec_t<3, wp::float64> var_161;
        const wp::int32 var_162 = 0;
        wp::float64 var_163;
        wp::float64 var_164;
        wp::float64 var_165;
        const wp::int32 var_166 = 1;
        wp::float64 var_167;
        wp::float64 var_168;
        wp::float64 var_169;
        const wp::int32 var_170 = 2;
        wp::float64 var_171;
        wp::float64 var_172;
        wp::float64 var_173;
        const bool var_174 = true;
        const wp::int32 var_175 = 0;
        const wp::int32 var_176 = 0;
        wp::float64 var_177;
        const wp::int32 var_178 = 1;
        wp::float64 var_179;
        const wp::int32 var_180 = 2;
        wp::float64 var_181;
        wp::float64 var_182;
        wp::float64 var_183;
        const wp::int32 var_184 = 0;
        wp::float64 var_185;
        const wp::int32 var_186 = 1;
        wp::float64 var_187;
        const wp::int32 var_188 = 2;
        wp::float64 var_189;
        wp::float64 var_190;
        wp::float64 var_191;
        bool var_192;
        wp::float64 var_193;
        bool var_194;
        wp::float64 var_195;
        bool var_196;
        const bool var_197 = false;
        bool var_198;
        const wp::int32 var_199 = 1;
        const wp::int32 var_200 = 0;
        wp::float64 var_201;
        const wp::int32 var_202 = 1;
        wp::float64 var_203;
        const wp::int32 var_204 = 2;
        wp::float64 var_205;
        wp::float64 var_206;
        wp::float64 var_207;
        const wp::int32 var_208 = 0;
        wp::float64 var_209;
        const wp::int32 var_210 = 1;
        wp::float64 var_211;
        const wp::int32 var_212 = 2;
        wp::float64 var_213;
        wp::float64 var_214;
        wp::float64 var_215;
        bool var_216;
        wp::float64 var_217;
        bool var_218;
        wp::float64 var_219;
        bool var_220;
        const bool var_221 = false;
        bool var_222;
        const wp::int32 var_223 = 2;
        const wp::int32 var_224 = 0;
        wp::float64 var_225;
        const wp::int32 var_226 = 1;
        wp::float64 var_227;
        const wp::int32 var_228 = 2;
        wp::float64 var_229;
        wp::float64 var_230;
        wp::float64 var_231;
        const wp::int32 var_232 = 0;
        wp::float64 var_233;
        const wp::int32 var_234 = 1;
        wp::float64 var_235;
        const wp::int32 var_236 = 2;
        wp::float64 var_237;
        wp::float64 var_238;
        wp::float64 var_239;
        bool var_240;
        wp::float64 var_241;
        bool var_242;
        wp::float64 var_243;
        bool var_244;
        const bool var_245 = false;
        bool var_246;
        const wp::int32 var_247 = 0;
        const wp::int32 var_248 = 1;
        wp::int32 var_249;
        wp::shape_t* var_250;
        const wp::int32 var_251 = 0;
        wp::int32 var_252;
        wp::shape_t var_253;
        bool var_254;
        const wp::int32 var_255 = 0;
        const wp::int32 var_256 = 5;
        wp::int32 var_257;
        //---------
        // forward
        // def exact_active_frame(R:wp.mat33d,pose:wp.array(dtype=wp.vec3d),ptr:wp.array(dtype=int),ids:wp.array(dtype=int),w:wp.array(dtype=wp.float64),ref:wp.array(dtype=wp.vec3d),q:wp.array(dtype=wp.vec3),v:wp.array(dtype=wp.vec3),X:wp.array(dtype=wp.mat33d),V:wp.array(dtype=wp.mat33d),local:wp.array(dtype=wp.mat33d),bcount:wp.array(dtype=int),bids:wp.array(dtype=int),lo:wp.vec3d,hi:wp.vec3d,count:wp.array(dtype=int),faces:wp.array(dtype=int),bad:wp.array(dtype=int)):       <L 40>
        // slot=wp.tid()                                                                          <L 41>
        var_0 = builtin_tid1d();
        // if slot>=bcount[0] or bad[0]!=0:return                                                 <L 42>
        var_3 = wp::address(var_bcount, var_2);
        var_5 = wp::load(var_3);
        var_4 = (var_0 >= var_5);
        var_1 = var_4;
        if (!var_1) {
            var_7 = wp::address(var_bad, var_6);
            var_10 = wp::load(var_7);
            var_9 = (var_10 != var_8);
            var_1 = var_1 || var_9;
        }
        if (var_1) {
            continue;
        }
        // face=bids[slot];T=pose[0];xx=wp.mat33d(wp.float64(0.));vv=wp.mat33d(wp.float64(0.));ll=wp.mat33d(wp.float64(0.))       <L 43>
        var_11 = wp::address(var_bids, var_0);
        var_13 = wp::load(var_11);
        var_12 = wp::copy(var_13);
        var_15 = wp::address(var_pose, var_14);
        var_17 = wp::load(var_15);
        var_16 = wp::copy(var_17);
        var_18 = 0.0;
        var_19 = wp::mat_t<3, 3, wp::float64>(var_18);
        var_20 = 0.0;
        var_21 = wp::mat_t<3, 3, wp::float64>(var_20);
        var_22 = 0.0;
        var_23 = wp::mat_t<3, 3, wp::float64>(var_22);
        // for u in range(3):                                                                     <L 44>
        // i=3*face+u;x=ref[i];vel=wp.vec3d(wp.float64(0.))                                       <L 45>
        var_26 = wp::mul(var_25, var_12);
        var_27 = wp::add(var_26, var_24);
        var_28 = wp::address(var_ref, var_27);
        var_30 = wp::load(var_28);
        var_29 = wp::copy(var_30);
        var_31 = 0.0;
        var_32 = wp::vec_t<3, wp::float64>(var_31);
        // for j in range(ptr[i],ptr[i+1]):x+=w[j]*wp.vec3d(q[ids[j]]);vel+=w[j]*wp.vec3d(v[ids[j]])       <L 46>
        var_33 = wp::address(var_ptr, var_27);
        var_35 = wp::add(var_27, var_34);
        var_36 = wp::address(var_ptr, var_35);
        var_38 = wp::load(var_33);
        var_39 = wp::load(var_36);
        var_37 = wp::range(var_38, var_39);
        start_for_1:;
            if (iter_cmp(var_37) == 0) goto end_for_1;
            var_40 = wp::iter_next(var_37);
            var_41 = wp::address(var_w, var_40);
            var_42 = wp::address(var_ids, var_40);
            var_44 = wp::load(var_42);
            var_43 = wp::address(var_q, var_44);
            var_46 = wp::load(var_43);
            var_45 = wp::vec_t<3, wp::float64>(var_46);
            var_48 = wp::load(var_41);
            var_47 = wp::mul(var_48, var_45);
            var_49 = wp::add(var_29, var_47);
            var_50 = wp::address(var_w, var_40);
            var_51 = wp::address(var_ids, var_40);
            var_53 = wp::load(var_51);
            var_52 = wp::address(var_v, var_53);
            var_55 = wp::load(var_52);
            var_54 = wp::vec_t<3, wp::float64>(var_55);
            var_57 = wp::load(var_50);
            var_56 = wp::mul(var_57, var_54);
            var_58 = wp::add(var_32, var_56);
            wp::assign(var_29, var_49);
            wp::assign(var_32, var_58);
            goto start_for_1;
        end_for_1:;
        // p=wp.transpose(R)*(x-T)                                                                <L 47>
        var_59 = wp::transpose(var_R);
        var_60 = wp::sub(var_29, var_16);
        var_61 = wp::mul(var_59, var_60);
        // for k in range(3):xx[u,k]=x[k];vv[u,k]=vel[k];ll[u,k]=p[k]                             <L 48>
        var_63 = wp::extract(var_29, var_62);
        wp::assign_inplace(var_19, var_24, var_62, var_63);
        var_64 = wp::extract(var_32, var_62);
        wp::assign_inplace(var_21, var_24, var_62, var_64);
        var_65 = wp::extract(var_61, var_62);
        wp::assign_inplace(var_23, var_24, var_62, var_65);
        var_67 = wp::extract(var_29, var_66);
        wp::assign_inplace(var_19, var_24, var_66, var_67);
        var_68 = wp::extract(var_32, var_66);
        wp::assign_inplace(var_21, var_24, var_66, var_68);
        var_69 = wp::extract(var_61, var_66);
        wp::assign_inplace(var_23, var_24, var_66, var_69);
        var_71 = wp::extract(var_29, var_70);
        wp::assign_inplace(var_19, var_24, var_70, var_71);
        var_72 = wp::extract(var_32, var_70);
        wp::assign_inplace(var_21, var_24, var_70, var_72);
        var_73 = wp::extract(var_61, var_70);
        wp::assign_inplace(var_23, var_24, var_70, var_73);
        // i=3*face+u;x=ref[i];vel=wp.vec3d(wp.float64(0.))                                       <L 45>
        var_76 = wp::mul(var_75, var_12);
        var_77 = wp::add(var_76, var_74);
        var_78 = wp::address(var_ref, var_77);
        var_80 = wp::load(var_78);
        var_79 = wp::copy(var_80);
        var_81 = 0.0;
        var_82 = wp::vec_t<3, wp::float64>(var_81);
        // for j in range(ptr[i],ptr[i+1]):x+=w[j]*wp.vec3d(q[ids[j]]);vel+=w[j]*wp.vec3d(v[ids[j]])       <L 46>
        var_83 = wp::address(var_ptr, var_77);
        var_85 = wp::add(var_77, var_84);
        var_86 = wp::address(var_ptr, var_85);
        var_88 = wp::load(var_83);
        var_89 = wp::load(var_86);
        var_87 = wp::range(var_88, var_89);
        start_for_3:;
            if (iter_cmp(var_87) == 0) goto end_for_3;
            var_90 = wp::iter_next(var_87);
            var_91 = wp::address(var_w, var_90);
            var_92 = wp::address(var_ids, var_90);
            var_94 = wp::load(var_92);
            var_93 = wp::address(var_q, var_94);
            var_96 = wp::load(var_93);
            var_95 = wp::vec_t<3, wp::float64>(var_96);
            var_98 = wp::load(var_91);
            var_97 = wp::mul(var_98, var_95);
            var_99 = wp::add(var_79, var_97);
            var_100 = wp::address(var_w, var_90);
            var_101 = wp::address(var_ids, var_90);
            var_103 = wp::load(var_101);
            var_102 = wp::address(var_v, var_103);
            var_105 = wp::load(var_102);
            var_104 = wp::vec_t<3, wp::float64>(var_105);
            var_107 = wp::load(var_100);
            var_106 = wp::mul(var_107, var_104);
            var_108 = wp::add(var_82, var_106);
            wp::assign(var_79, var_99);
            wp::assign(var_82, var_108);
            goto start_for_3;
        end_for_3:;
        // p=wp.transpose(R)*(x-T)                                                                <L 47>
        var_109 = wp::transpose(var_R);
        var_110 = wp::sub(var_79, var_16);
        var_111 = wp::mul(var_109, var_110);
        // for k in range(3):xx[u,k]=x[k];vv[u,k]=vel[k];ll[u,k]=p[k]                             <L 48>
        var_113 = wp::extract(var_79, var_112);
        wp::assign_inplace(var_19, var_74, var_112, var_113);
        var_114 = wp::extract(var_82, var_112);
        wp::assign_inplace(var_21, var_74, var_112, var_114);
        var_115 = wp::extract(var_111, var_112);
        wp::assign_inplace(var_23, var_74, var_112, var_115);
        var_117 = wp::extract(var_79, var_116);
        wp::assign_inplace(var_19, var_74, var_116, var_117);
        var_118 = wp::extract(var_82, var_116);
        wp::assign_inplace(var_21, var_74, var_116, var_118);
        var_119 = wp::extract(var_111, var_116);
        wp::assign_inplace(var_23, var_74, var_116, var_119);
        var_121 = wp::extract(var_79, var_120);
        wp::assign_inplace(var_19, var_74, var_120, var_121);
        var_122 = wp::extract(var_82, var_120);
        wp::assign_inplace(var_21, var_74, var_120, var_122);
        var_123 = wp::extract(var_111, var_120);
        wp::assign_inplace(var_23, var_74, var_120, var_123);
        // i=3*face+u;x=ref[i];vel=wp.vec3d(wp.float64(0.))                                       <L 45>
        var_126 = wp::mul(var_125, var_12);
        var_127 = wp::add(var_126, var_124);
        var_128 = wp::address(var_ref, var_127);
        var_130 = wp::load(var_128);
        var_129 = wp::copy(var_130);
        var_131 = 0.0;
        var_132 = wp::vec_t<3, wp::float64>(var_131);
        // for j in range(ptr[i],ptr[i+1]):x+=w[j]*wp.vec3d(q[ids[j]]);vel+=w[j]*wp.vec3d(v[ids[j]])       <L 46>
        var_133 = wp::address(var_ptr, var_127);
        var_135 = wp::add(var_127, var_134);
        var_136 = wp::address(var_ptr, var_135);
        var_138 = wp::load(var_133);
        var_139 = wp::load(var_136);
        var_137 = wp::range(var_138, var_139);
        start_for_5:;
            if (iter_cmp(var_137) == 0) goto end_for_5;
            var_140 = wp::iter_next(var_137);
            var_141 = wp::address(var_w, var_140);
            var_142 = wp::address(var_ids, var_140);
            var_144 = wp::load(var_142);
            var_143 = wp::address(var_q, var_144);
            var_146 = wp::load(var_143);
            var_145 = wp::vec_t<3, wp::float64>(var_146);
            var_148 = wp::load(var_141);
            var_147 = wp::mul(var_148, var_145);
            var_149 = wp::add(var_129, var_147);
            var_150 = wp::address(var_w, var_140);
            var_151 = wp::address(var_ids, var_140);
            var_153 = wp::load(var_151);
            var_152 = wp::address(var_v, var_153);
            var_155 = wp::load(var_152);
            var_154 = wp::vec_t<3, wp::float64>(var_155);
            var_157 = wp::load(var_150);
            var_156 = wp::mul(var_157, var_154);
            var_158 = wp::add(var_132, var_156);
            wp::assign(var_129, var_149);
            wp::assign(var_132, var_158);
            goto start_for_5;
        end_for_5:;
        // p=wp.transpose(R)*(x-T)                                                                <L 47>
        var_159 = wp::transpose(var_R);
        var_160 = wp::sub(var_129, var_16);
        var_161 = wp::mul(var_159, var_160);
        // for k in range(3):xx[u,k]=x[k];vv[u,k]=vel[k];ll[u,k]=p[k]                             <L 48>
        var_163 = wp::extract(var_129, var_162);
        wp::assign_inplace(var_19, var_124, var_162, var_163);
        var_164 = wp::extract(var_132, var_162);
        wp::assign_inplace(var_21, var_124, var_162, var_164);
        var_165 = wp::extract(var_161, var_162);
        wp::assign_inplace(var_23, var_124, var_162, var_165);
        var_167 = wp::extract(var_129, var_166);
        wp::assign_inplace(var_19, var_124, var_166, var_167);
        var_168 = wp::extract(var_132, var_166);
        wp::assign_inplace(var_21, var_124, var_166, var_168);
        var_169 = wp::extract(var_161, var_166);
        wp::assign_inplace(var_23, var_124, var_166, var_169);
        var_171 = wp::extract(var_129, var_170);
        wp::assign_inplace(var_19, var_124, var_170, var_171);
        var_172 = wp::extract(var_132, var_170);
        wp::assign_inplace(var_21, var_124, var_170, var_172);
        var_173 = wp::extract(var_161, var_170);
        wp::assign_inplace(var_23, var_124, var_170, var_173);
        // overlap=True                                                                           <L 49>
        // for k in range(3):                                                                     <L 50>
        // amin=wp.min(ll[0,k],wp.min(ll[1,k],ll[2,k]));amax=wp.max(ll[0,k],wp.max(ll[1,k],ll[2,k]))       <L 51>
        var_177 = wp::extract(var_23, var_176, var_175);
        var_179 = wp::extract(var_23, var_178, var_175);
        var_181 = wp::extract(var_23, var_180, var_175);
        var_182 = wp::min(var_179, var_181);
        var_183 = wp::min(var_177, var_182);
        var_185 = wp::extract(var_23, var_184, var_175);
        var_187 = wp::extract(var_23, var_186, var_175);
        var_189 = wp::extract(var_23, var_188, var_175);
        var_190 = wp::max(var_187, var_189);
        var_191 = wp::max(var_185, var_190);
        // if amax<lo[k] or amin>hi[k]:overlap=False                                              <L 52>
        var_193 = wp::extract(var_lo, var_175);
        var_194 = (var_191 < var_193);
        var_192 = var_194;
        if (!var_192) {
            var_195 = wp::extract(var_hi, var_175);
            var_196 = (var_183 > var_195);
            var_192 = var_192 || var_196;
        }
        if (var_192) {
        }
        var_198 = wp::where(var_192, var_197, var_174);
        // amin=wp.min(ll[0,k],wp.min(ll[1,k],ll[2,k]));amax=wp.max(ll[0,k],wp.max(ll[1,k],ll[2,k]))       <L 51>
        var_201 = wp::extract(var_23, var_200, var_199);
        var_203 = wp::extract(var_23, var_202, var_199);
        var_205 = wp::extract(var_23, var_204, var_199);
        var_206 = wp::min(var_203, var_205);
        var_207 = wp::min(var_201, var_206);
        var_209 = wp::extract(var_23, var_208, var_199);
        var_211 = wp::extract(var_23, var_210, var_199);
        var_213 = wp::extract(var_23, var_212, var_199);
        var_214 = wp::max(var_211, var_213);
        var_215 = wp::max(var_209, var_214);
        // if amax<lo[k] or amin>hi[k]:overlap=False                                              <L 52>
        var_217 = wp::extract(var_lo, var_199);
        var_218 = (var_215 < var_217);
        var_216 = var_218;
        if (!var_216) {
            var_219 = wp::extract(var_hi, var_199);
            var_220 = (var_207 > var_219);
            var_216 = var_216 || var_220;
        }
        if (var_216) {
        }
        var_222 = wp::where(var_216, var_221, var_198);
        // amin=wp.min(ll[0,k],wp.min(ll[1,k],ll[2,k]));amax=wp.max(ll[0,k],wp.max(ll[1,k],ll[2,k]))       <L 51>
        var_225 = wp::extract(var_23, var_224, var_223);
        var_227 = wp::extract(var_23, var_226, var_223);
        var_229 = wp::extract(var_23, var_228, var_223);
        var_230 = wp::min(var_227, var_229);
        var_231 = wp::min(var_225, var_230);
        var_233 = wp::extract(var_23, var_232, var_223);
        var_235 = wp::extract(var_23, var_234, var_223);
        var_237 = wp::extract(var_23, var_236, var_223);
        var_238 = wp::max(var_235, var_237);
        var_239 = wp::max(var_233, var_238);
        // if amax<lo[k] or amin>hi[k]:overlap=False                                              <L 52>
        var_241 = wp::extract(var_lo, var_223);
        var_242 = (var_239 < var_241);
        var_240 = var_242;
        if (!var_240) {
            var_243 = wp::extract(var_hi, var_223);
            var_244 = (var_231 > var_243);
            var_240 = var_240 || var_244;
        }
        if (var_240) {
        }
        var_246 = wp::where(var_240, var_245, var_222);
        // if overlap:                                                                            <L 53>
        if (var_246) {
            // X[face]=xx;V[face]=vv;local[face]=ll;index=wp.atomic_add(count,0,1)                <L 54>
            wp::array_store(var_X, var_12, var_19);
            wp::array_store(var_V, var_12, var_21);
            wp::array_store(var_local, var_12, var_23);
            var_249 = wp::atomic_add(var_count, var_247, var_248);
            // if index>=faces.shape[0]:wp.atomic_max(bad,0,5)                                    <L 55>
            var_250 = &(var_faces.shape);
            var_253 = wp::load(var_250);
            var_252 = wp::extract(var_253, var_251);
            var_254 = (var_249 >= var_252);
            if (var_254) {
                var_257 = wp::atomic_max(var_bad, var_255, var_256);
            }
            if (!var_254) {
                // else:faces[index]=face                                                         <L 56>
                wp::array_store(var_faces, var_249, var_12);
            }
        }
    }
}



extern "C" __global__ void parent_faces_eae1e357_cuda_kernel_forward(
    wp::launch_bounds_t<1> dim,
    wp::array_t<wp::int32> var_parent,
    wp::array_t<wp::int32> var_owner,
    wp::array_t<wp::vec_t<3, wp::float64>> var_corners,
    wp::array_t<wp::vec_t<3, wp::float64>> var_roundoff,
    wp::vec_t<3, wp::float64> var_lo,
    wp::vec_t<3, wp::float64> var_hi,
    wp::array_t<wp::int32> var_count,
    wp::array_t<wp::int32> var_ids,
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
        wp::int32* var_1;
        wp::int32 var_2;
        wp::int32 var_3;
        const bool var_4 = true;
        const wp::int32 var_5 = 0;
        wp::float64 var_6;
        wp::float64 var_7;
        const wp::int32 var_8 = 0;
        wp::int32* var_9;
        wp::vec_t<3, wp::float64>* var_10;
        wp::int32 var_11;
        wp::float64 var_12;
        wp::vec_t<3, wp::float64> var_13;
        wp::float64 var_14;
        wp::int32* var_15;
        wp::vec_t<3, wp::float64>* var_16;
        wp::int32 var_17;
        wp::float64 var_18;
        wp::vec_t<3, wp::float64> var_19;
        wp::float64 var_20;
        const wp::int32 var_21 = 1;
        wp::int32* var_22;
        wp::vec_t<3, wp::float64>* var_23;
        wp::int32 var_24;
        wp::float64 var_25;
        wp::vec_t<3, wp::float64> var_26;
        wp::float64 var_27;
        wp::int32* var_28;
        wp::vec_t<3, wp::float64>* var_29;
        wp::int32 var_30;
        wp::float64 var_31;
        wp::vec_t<3, wp::float64> var_32;
        wp::float64 var_33;
        const wp::int32 var_34 = 2;
        wp::int32* var_35;
        wp::vec_t<3, wp::float64>* var_36;
        wp::int32 var_37;
        wp::float64 var_38;
        wp::vec_t<3, wp::float64> var_39;
        wp::float64 var_40;
        wp::int32* var_41;
        wp::vec_t<3, wp::float64>* var_42;
        wp::int32 var_43;
        wp::float64 var_44;
        wp::vec_t<3, wp::float64> var_45;
        wp::float64 var_46;
        const wp::int32 var_47 = 3;
        wp::int32* var_48;
        wp::vec_t<3, wp::float64>* var_49;
        wp::int32 var_50;
        wp::float64 var_51;
        wp::vec_t<3, wp::float64> var_52;
        wp::float64 var_53;
        wp::int32* var_54;
        wp::vec_t<3, wp::float64>* var_55;
        wp::int32 var_56;
        wp::float64 var_57;
        wp::vec_t<3, wp::float64> var_58;
        wp::float64 var_59;
        wp::float64 var_60;
        wp::float64 var_61;
        wp::float64 var_62;
        wp::vec_t<3, wp::float64>* var_63;
        const wp::int32 var_64 = 0;
        wp::float64 var_65;
        wp::vec_t<3, wp::float64> var_66;
        wp::float64 var_67;
        wp::float64 var_68;
        wp::vec_t<3, wp::float64>* var_69;
        const wp::int32 var_70 = 1;
        wp::float64 var_71;
        wp::vec_t<3, wp::float64> var_72;
        wp::float64 var_73;
        wp::float64 var_74;
        wp::vec_t<3, wp::float64>* var_75;
        const wp::int32 var_76 = 2;
        wp::float64 var_77;
        wp::vec_t<3, wp::float64> var_78;
        wp::float64 var_79;
        wp::float64 var_80;
        wp::float64 var_81;
        wp::float64 var_82;
        wp::float64 var_83;
        wp::float64 var_84;
        bool var_85;
        wp::float64 var_86;
        wp::float64 var_87;
        bool var_88;
        wp::float64 var_89;
        wp::float64 var_90;
        bool var_91;
        const bool var_92 = false;
        bool var_93;
        const wp::int32 var_94 = 1;
        wp::float64 var_95;
        wp::float64 var_96;
        const wp::int32 var_97 = 0;
        wp::int32* var_98;
        wp::vec_t<3, wp::float64>* var_99;
        wp::int32 var_100;
        wp::float64 var_101;
        wp::vec_t<3, wp::float64> var_102;
        wp::float64 var_103;
        wp::int32* var_104;
        wp::vec_t<3, wp::float64>* var_105;
        wp::int32 var_106;
        wp::float64 var_107;
        wp::vec_t<3, wp::float64> var_108;
        wp::float64 var_109;
        const wp::int32 var_110 = 1;
        wp::int32* var_111;
        wp::vec_t<3, wp::float64>* var_112;
        wp::int32 var_113;
        wp::float64 var_114;
        wp::vec_t<3, wp::float64> var_115;
        wp::float64 var_116;
        wp::int32* var_117;
        wp::vec_t<3, wp::float64>* var_118;
        wp::int32 var_119;
        wp::float64 var_120;
        wp::vec_t<3, wp::float64> var_121;
        wp::float64 var_122;
        const wp::int32 var_123 = 2;
        wp::int32* var_124;
        wp::vec_t<3, wp::float64>* var_125;
        wp::int32 var_126;
        wp::float64 var_127;
        wp::vec_t<3, wp::float64> var_128;
        wp::float64 var_129;
        wp::int32* var_130;
        wp::vec_t<3, wp::float64>* var_131;
        wp::int32 var_132;
        wp::float64 var_133;
        wp::vec_t<3, wp::float64> var_134;
        wp::float64 var_135;
        const wp::int32 var_136 = 3;
        wp::int32* var_137;
        wp::vec_t<3, wp::float64>* var_138;
        wp::int32 var_139;
        wp::float64 var_140;
        wp::vec_t<3, wp::float64> var_141;
        wp::float64 var_142;
        wp::int32* var_143;
        wp::vec_t<3, wp::float64>* var_144;
        wp::int32 var_145;
        wp::float64 var_146;
        wp::vec_t<3, wp::float64> var_147;
        wp::float64 var_148;
        wp::float64 var_149;
        wp::float64 var_150;
        wp::float64 var_151;
        wp::vec_t<3, wp::float64>* var_152;
        const wp::int32 var_153 = 0;
        wp::float64 var_154;
        wp::vec_t<3, wp::float64> var_155;
        wp::float64 var_156;
        wp::float64 var_157;
        wp::vec_t<3, wp::float64>* var_158;
        const wp::int32 var_159 = 1;
        wp::float64 var_160;
        wp::vec_t<3, wp::float64> var_161;
        wp::float64 var_162;
        wp::float64 var_163;
        wp::vec_t<3, wp::float64>* var_164;
        const wp::int32 var_165 = 2;
        wp::float64 var_166;
        wp::vec_t<3, wp::float64> var_167;
        wp::float64 var_168;
        wp::float64 var_169;
        wp::float64 var_170;
        wp::float64 var_171;
        wp::float64 var_172;
        wp::float64 var_173;
        bool var_174;
        wp::float64 var_175;
        wp::float64 var_176;
        bool var_177;
        wp::float64 var_178;
        wp::float64 var_179;
        bool var_180;
        const bool var_181 = false;
        bool var_182;
        const wp::int32 var_183 = 2;
        wp::float64 var_184;
        wp::float64 var_185;
        const wp::int32 var_186 = 0;
        wp::int32* var_187;
        wp::vec_t<3, wp::float64>* var_188;
        wp::int32 var_189;
        wp::float64 var_190;
        wp::vec_t<3, wp::float64> var_191;
        wp::float64 var_192;
        wp::int32* var_193;
        wp::vec_t<3, wp::float64>* var_194;
        wp::int32 var_195;
        wp::float64 var_196;
        wp::vec_t<3, wp::float64> var_197;
        wp::float64 var_198;
        const wp::int32 var_199 = 1;
        wp::int32* var_200;
        wp::vec_t<3, wp::float64>* var_201;
        wp::int32 var_202;
        wp::float64 var_203;
        wp::vec_t<3, wp::float64> var_204;
        wp::float64 var_205;
        wp::int32* var_206;
        wp::vec_t<3, wp::float64>* var_207;
        wp::int32 var_208;
        wp::float64 var_209;
        wp::vec_t<3, wp::float64> var_210;
        wp::float64 var_211;
        const wp::int32 var_212 = 2;
        wp::int32* var_213;
        wp::vec_t<3, wp::float64>* var_214;
        wp::int32 var_215;
        wp::float64 var_216;
        wp::vec_t<3, wp::float64> var_217;
        wp::float64 var_218;
        wp::int32* var_219;
        wp::vec_t<3, wp::float64>* var_220;
        wp::int32 var_221;
        wp::float64 var_222;
        wp::vec_t<3, wp::float64> var_223;
        wp::float64 var_224;
        const wp::int32 var_225 = 3;
        wp::int32* var_226;
        wp::vec_t<3, wp::float64>* var_227;
        wp::int32 var_228;
        wp::float64 var_229;
        wp::vec_t<3, wp::float64> var_230;
        wp::float64 var_231;
        wp::int32* var_232;
        wp::vec_t<3, wp::float64>* var_233;
        wp::int32 var_234;
        wp::float64 var_235;
        wp::vec_t<3, wp::float64> var_236;
        wp::float64 var_237;
        wp::float64 var_238;
        wp::float64 var_239;
        wp::float64 var_240;
        wp::vec_t<3, wp::float64>* var_241;
        const wp::int32 var_242 = 0;
        wp::float64 var_243;
        wp::vec_t<3, wp::float64> var_244;
        wp::float64 var_245;
        wp::float64 var_246;
        wp::vec_t<3, wp::float64>* var_247;
        const wp::int32 var_248 = 1;
        wp::float64 var_249;
        wp::vec_t<3, wp::float64> var_250;
        wp::float64 var_251;
        wp::float64 var_252;
        wp::vec_t<3, wp::float64>* var_253;
        const wp::int32 var_254 = 2;
        wp::float64 var_255;
        wp::vec_t<3, wp::float64> var_256;
        wp::float64 var_257;
        wp::float64 var_258;
        wp::float64 var_259;
        wp::float64 var_260;
        wp::float64 var_261;
        wp::float64 var_262;
        bool var_263;
        wp::float64 var_264;
        wp::float64 var_265;
        bool var_266;
        wp::float64 var_267;
        wp::float64 var_268;
        bool var_269;
        const bool var_270 = false;
        bool var_271;
        bool var_272;
        const wp::int32 var_273 = 0;
        wp::int32* var_274;
        const wp::int32 var_275 = 0;
        bool var_276;
        wp::int32 var_277;
        const wp::int32 var_278 = 0;
        const wp::int32 var_279 = 1;
        wp::int32 var_280;
        wp::shape_t* var_281;
        const wp::int32 var_282 = 0;
        wp::int32 var_283;
        wp::shape_t var_284;
        bool var_285;
        const wp::int32 var_286 = 0;
        const wp::int32 var_287 = 5;
        wp::int32 var_288;
        //---------
        // forward
        // def parent_faces(parent:wp.array2d(dtype=int),owner:wp.array(dtype=int),corners:wp.array(dtype=wp.vec3d),roundoff:wp.array(dtype=wp.vec3d),lo:wp.vec3d,hi:wp.vec3d,count:wp.array(dtype=int),ids:wp.array(dtype=int),bad:wp.array(dtype=int)):       <L 27>
        // face=wp.tid();r=owner[face];overlap=True                                               <L 28>
        var_0 = builtin_tid1d();
        var_1 = wp::address(var_owner, var_0);
        var_3 = wp::load(var_1);
        var_2 = wp::copy(var_3);
        // for k in range(3):                                                                     <L 29>
        // low=wp.float64(1e30);high=wp.float64(-1e30)                                            <L 30>
        var_6 = 1e+30;
        var_7 = -1e+30;
        // for j in range(4):low=wp.min(low,corners[parent[r,j]][k]);high=wp.max(high,corners[parent[r,j]][k])       <L 31>
        var_9 = wp::address(var_parent, var_2, var_8);
        var_11 = wp::load(var_9);
        var_10 = wp::address(var_corners, var_11);
        var_13 = wp::load(var_10);
        var_12 = wp::extract(var_13, var_5);
        var_14 = wp::min(var_6, var_12);
        var_15 = wp::address(var_parent, var_2, var_8);
        var_17 = wp::load(var_15);
        var_16 = wp::address(var_corners, var_17);
        var_19 = wp::load(var_16);
        var_18 = wp::extract(var_19, var_5);
        var_20 = wp::max(var_7, var_18);
        var_22 = wp::address(var_parent, var_2, var_21);
        var_24 = wp::load(var_22);
        var_23 = wp::address(var_corners, var_24);
        var_26 = wp::load(var_23);
        var_25 = wp::extract(var_26, var_5);
        var_27 = wp::min(var_14, var_25);
        var_28 = wp::address(var_parent, var_2, var_21);
        var_30 = wp::load(var_28);
        var_29 = wp::address(var_corners, var_30);
        var_32 = wp::load(var_29);
        var_31 = wp::extract(var_32, var_5);
        var_33 = wp::max(var_20, var_31);
        var_35 = wp::address(var_parent, var_2, var_34);
        var_37 = wp::load(var_35);
        var_36 = wp::address(var_corners, var_37);
        var_39 = wp::load(var_36);
        var_38 = wp::extract(var_39, var_5);
        var_40 = wp::min(var_27, var_38);
        var_41 = wp::address(var_parent, var_2, var_34);
        var_43 = wp::load(var_41);
        var_42 = wp::address(var_corners, var_43);
        var_45 = wp::load(var_42);
        var_44 = wp::extract(var_45, var_5);
        var_46 = wp::max(var_33, var_44);
        var_48 = wp::address(var_parent, var_2, var_47);
        var_50 = wp::load(var_48);
        var_49 = wp::address(var_corners, var_50);
        var_52 = wp::load(var_49);
        var_51 = wp::extract(var_52, var_5);
        var_53 = wp::min(var_40, var_51);
        var_54 = wp::address(var_parent, var_2, var_47);
        var_56 = wp::load(var_54);
        var_55 = wp::address(var_corners, var_56);
        var_58 = wp::load(var_55);
        var_57 = wp::extract(var_58, var_5);
        var_59 = wp::max(var_46, var_57);
        // mag=wp.max(wp.abs(low),wp.abs(high));error=roundoff[face][0]*(high-low)+roundoff[face][1]*mag+roundoff[face][2]+wp.float64(1e-10)*(wp.float64(1.)+mag)       <L 32>
        var_60 = wp::abs(var_53);
        var_61 = wp::abs(var_59);
        var_62 = wp::max(var_60, var_61);
        var_63 = wp::address(var_roundoff, var_0);
        var_66 = wp::load(var_63);
        var_65 = wp::extract(var_66, var_64);
        var_67 = wp::sub(var_59, var_53);
        var_68 = wp::mul(var_65, var_67);
        var_69 = wp::address(var_roundoff, var_0);
        var_72 = wp::load(var_69);
        var_71 = wp::extract(var_72, var_70);
        var_73 = wp::mul(var_71, var_62);
        var_74 = wp::add(var_68, var_73);
        var_75 = wp::address(var_roundoff, var_0);
        var_78 = wp::load(var_75);
        var_77 = wp::extract(var_78, var_76);
        var_79 = wp::add(var_74, var_77);
        var_80 = 1e-10;
        var_81 = 1.0;
        var_82 = wp::add(var_81, var_62);
        var_83 = wp::mul(var_80, var_82);
        var_84 = wp::add(var_79, var_83);
        // if high+error<lo[k] or low-error>hi[k]:overlap=False                                   <L 33>
        var_86 = wp::add(var_59, var_84);
        var_87 = wp::extract(var_lo, var_5);
        var_88 = (var_86 < var_87);
        var_85 = var_88;
        if (!var_85) {
            var_89 = wp::sub(var_53, var_84);
            var_90 = wp::extract(var_hi, var_5);
            var_91 = (var_89 > var_90);
            var_85 = var_85 || var_91;
        }
        if (var_85) {
        }
        var_93 = wp::where(var_85, var_92, var_4);
        // low=wp.float64(1e30);high=wp.float64(-1e30)                                            <L 30>
        var_95 = 1e+30;
        var_96 = -1e+30;
        // for j in range(4):low=wp.min(low,corners[parent[r,j]][k]);high=wp.max(high,corners[parent[r,j]][k])       <L 31>
        var_98 = wp::address(var_parent, var_2, var_97);
        var_100 = wp::load(var_98);
        var_99 = wp::address(var_corners, var_100);
        var_102 = wp::load(var_99);
        var_101 = wp::extract(var_102, var_94);
        var_103 = wp::min(var_95, var_101);
        var_104 = wp::address(var_parent, var_2, var_97);
        var_106 = wp::load(var_104);
        var_105 = wp::address(var_corners, var_106);
        var_108 = wp::load(var_105);
        var_107 = wp::extract(var_108, var_94);
        var_109 = wp::max(var_96, var_107);
        var_111 = wp::address(var_parent, var_2, var_110);
        var_113 = wp::load(var_111);
        var_112 = wp::address(var_corners, var_113);
        var_115 = wp::load(var_112);
        var_114 = wp::extract(var_115, var_94);
        var_116 = wp::min(var_103, var_114);
        var_117 = wp::address(var_parent, var_2, var_110);
        var_119 = wp::load(var_117);
        var_118 = wp::address(var_corners, var_119);
        var_121 = wp::load(var_118);
        var_120 = wp::extract(var_121, var_94);
        var_122 = wp::max(var_109, var_120);
        var_124 = wp::address(var_parent, var_2, var_123);
        var_126 = wp::load(var_124);
        var_125 = wp::address(var_corners, var_126);
        var_128 = wp::load(var_125);
        var_127 = wp::extract(var_128, var_94);
        var_129 = wp::min(var_116, var_127);
        var_130 = wp::address(var_parent, var_2, var_123);
        var_132 = wp::load(var_130);
        var_131 = wp::address(var_corners, var_132);
        var_134 = wp::load(var_131);
        var_133 = wp::extract(var_134, var_94);
        var_135 = wp::max(var_122, var_133);
        var_137 = wp::address(var_parent, var_2, var_136);
        var_139 = wp::load(var_137);
        var_138 = wp::address(var_corners, var_139);
        var_141 = wp::load(var_138);
        var_140 = wp::extract(var_141, var_94);
        var_142 = wp::min(var_129, var_140);
        var_143 = wp::address(var_parent, var_2, var_136);
        var_145 = wp::load(var_143);
        var_144 = wp::address(var_corners, var_145);
        var_147 = wp::load(var_144);
        var_146 = wp::extract(var_147, var_94);
        var_148 = wp::max(var_135, var_146);
        // mag=wp.max(wp.abs(low),wp.abs(high));error=roundoff[face][0]*(high-low)+roundoff[face][1]*mag+roundoff[face][2]+wp.float64(1e-10)*(wp.float64(1.)+mag)       <L 32>
        var_149 = wp::abs(var_142);
        var_150 = wp::abs(var_148);
        var_151 = wp::max(var_149, var_150);
        var_152 = wp::address(var_roundoff, var_0);
        var_155 = wp::load(var_152);
        var_154 = wp::extract(var_155, var_153);
        var_156 = wp::sub(var_148, var_142);
        var_157 = wp::mul(var_154, var_156);
        var_158 = wp::address(var_roundoff, var_0);
        var_161 = wp::load(var_158);
        var_160 = wp::extract(var_161, var_159);
        var_162 = wp::mul(var_160, var_151);
        var_163 = wp::add(var_157, var_162);
        var_164 = wp::address(var_roundoff, var_0);
        var_167 = wp::load(var_164);
        var_166 = wp::extract(var_167, var_165);
        var_168 = wp::add(var_163, var_166);
        var_169 = 1e-10;
        var_170 = 1.0;
        var_171 = wp::add(var_170, var_151);
        var_172 = wp::mul(var_169, var_171);
        var_173 = wp::add(var_168, var_172);
        // if high+error<lo[k] or low-error>hi[k]:overlap=False                                   <L 33>
        var_175 = wp::add(var_148, var_173);
        var_176 = wp::extract(var_lo, var_94);
        var_177 = (var_175 < var_176);
        var_174 = var_177;
        if (!var_174) {
            var_178 = wp::sub(var_142, var_173);
            var_179 = wp::extract(var_hi, var_94);
            var_180 = (var_178 > var_179);
            var_174 = var_174 || var_180;
        }
        if (var_174) {
        }
        var_182 = wp::where(var_174, var_181, var_93);
        // low=wp.float64(1e30);high=wp.float64(-1e30)                                            <L 30>
        var_184 = 1e+30;
        var_185 = -1e+30;
        // for j in range(4):low=wp.min(low,corners[parent[r,j]][k]);high=wp.max(high,corners[parent[r,j]][k])       <L 31>
        var_187 = wp::address(var_parent, var_2, var_186);
        var_189 = wp::load(var_187);
        var_188 = wp::address(var_corners, var_189);
        var_191 = wp::load(var_188);
        var_190 = wp::extract(var_191, var_183);
        var_192 = wp::min(var_184, var_190);
        var_193 = wp::address(var_parent, var_2, var_186);
        var_195 = wp::load(var_193);
        var_194 = wp::address(var_corners, var_195);
        var_197 = wp::load(var_194);
        var_196 = wp::extract(var_197, var_183);
        var_198 = wp::max(var_185, var_196);
        var_200 = wp::address(var_parent, var_2, var_199);
        var_202 = wp::load(var_200);
        var_201 = wp::address(var_corners, var_202);
        var_204 = wp::load(var_201);
        var_203 = wp::extract(var_204, var_183);
        var_205 = wp::min(var_192, var_203);
        var_206 = wp::address(var_parent, var_2, var_199);
        var_208 = wp::load(var_206);
        var_207 = wp::address(var_corners, var_208);
        var_210 = wp::load(var_207);
        var_209 = wp::extract(var_210, var_183);
        var_211 = wp::max(var_198, var_209);
        var_213 = wp::address(var_parent, var_2, var_212);
        var_215 = wp::load(var_213);
        var_214 = wp::address(var_corners, var_215);
        var_217 = wp::load(var_214);
        var_216 = wp::extract(var_217, var_183);
        var_218 = wp::min(var_205, var_216);
        var_219 = wp::address(var_parent, var_2, var_212);
        var_221 = wp::load(var_219);
        var_220 = wp::address(var_corners, var_221);
        var_223 = wp::load(var_220);
        var_222 = wp::extract(var_223, var_183);
        var_224 = wp::max(var_211, var_222);
        var_226 = wp::address(var_parent, var_2, var_225);
        var_228 = wp::load(var_226);
        var_227 = wp::address(var_corners, var_228);
        var_230 = wp::load(var_227);
        var_229 = wp::extract(var_230, var_183);
        var_231 = wp::min(var_218, var_229);
        var_232 = wp::address(var_parent, var_2, var_225);
        var_234 = wp::load(var_232);
        var_233 = wp::address(var_corners, var_234);
        var_236 = wp::load(var_233);
        var_235 = wp::extract(var_236, var_183);
        var_237 = wp::max(var_224, var_235);
        // mag=wp.max(wp.abs(low),wp.abs(high));error=roundoff[face][0]*(high-low)+roundoff[face][1]*mag+roundoff[face][2]+wp.float64(1e-10)*(wp.float64(1.)+mag)       <L 32>
        var_238 = wp::abs(var_231);
        var_239 = wp::abs(var_237);
        var_240 = wp::max(var_238, var_239);
        var_241 = wp::address(var_roundoff, var_0);
        var_244 = wp::load(var_241);
        var_243 = wp::extract(var_244, var_242);
        var_245 = wp::sub(var_237, var_231);
        var_246 = wp::mul(var_243, var_245);
        var_247 = wp::address(var_roundoff, var_0);
        var_250 = wp::load(var_247);
        var_249 = wp::extract(var_250, var_248);
        var_251 = wp::mul(var_249, var_240);
        var_252 = wp::add(var_246, var_251);
        var_253 = wp::address(var_roundoff, var_0);
        var_256 = wp::load(var_253);
        var_255 = wp::extract(var_256, var_254);
        var_257 = wp::add(var_252, var_255);
        var_258 = 1e-10;
        var_259 = 1.0;
        var_260 = wp::add(var_259, var_240);
        var_261 = wp::mul(var_258, var_260);
        var_262 = wp::add(var_257, var_261);
        // if high+error<lo[k] or low-error>hi[k]:overlap=False                                   <L 33>
        var_264 = wp::add(var_237, var_262);
        var_265 = wp::extract(var_lo, var_183);
        var_266 = (var_264 < var_265);
        var_263 = var_266;
        if (!var_263) {
            var_267 = wp::sub(var_231, var_262);
            var_268 = wp::extract(var_hi, var_183);
            var_269 = (var_267 > var_268);
            var_263 = var_263 || var_269;
        }
        if (var_263) {
        }
        var_271 = wp::where(var_263, var_270, var_182);
        // if overlap and bad[0]==0:                                                              <L 34>
        var_272 = var_271;
        if (var_272) {
            var_274 = wp::address(var_bad, var_273);
            var_277 = wp::load(var_274);
            var_276 = (var_277 == var_275);
            var_272 = var_272 && var_276;
        }
        if (var_272) {
            // index=wp.atomic_add(count,0,1)                                                     <L 35>
            var_280 = wp::atomic_add(var_count, var_278, var_279);
            // if index>=ids.shape[0]:wp.atomic_max(bad,0,5)                                      <L 36>
            var_281 = &(var_ids.shape);
            var_284 = wp::load(var_281);
            var_283 = wp::extract(var_284, var_282);
            var_285 = (var_280 >= var_283);
            if (var_285) {
                var_288 = wp::atomic_max(var_bad, var_286, var_287);
            }
            if (!var_285) {
                // else:ids[index]=face                                                           <L 37>
                wp::array_store(var_ids, var_280, var_0);
            }
        }
    }
}


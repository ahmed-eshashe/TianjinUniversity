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


// /home/omen/Documents/Codex/experiments/tomato_approx_rl_20261113_v28/src/solver.py:38
static CUDA_CALLABLE void box_normal_0(
    wp::vec_t<3, wp::float32> var_p,
    wp::vec_t<3, wp::float32> var_half,
    wp::vec_t<3, wp::float32> & ret_0,
    wp::float32 & ret_1)
{
    //---------
    // primal vars
    const wp::int32 var_0 = 0;
    wp::float32 var_1;
    wp::float32 var_2;
    const wp::int32 var_3 = 1;
    wp::float32 var_4;
    wp::float32 var_5;
    const wp::int32 var_6 = 2;
    wp::float32 var_7;
    wp::float32 var_8;
    wp::vec_t<3, wp::float32> var_9;
    wp::vec_t<3, wp::float32> var_10;
    const wp::int32 var_11 = 0;
    wp::float32 var_12;
    const wp::float32 var_13 = 0.0;
    wp::float32 var_14;
    const wp::int32 var_15 = 1;
    wp::float32 var_16;
    const wp::float32 var_17 = 0.0;
    wp::float32 var_18;
    const wp::int32 var_19 = 2;
    wp::float32 var_20;
    const wp::float32 var_21 = 0.0;
    wp::float32 var_22;
    wp::vec_t<3, wp::float32> var_23;
    wp::float32 var_24;
    const wp::float32 var_25 = 0.0;
    wp::vec_t<3, wp::float32> var_26;
    const wp::float32 var_27 = 1e-12;
    bool var_28;
    const wp::int32 var_29 = 0;
    wp::float32 var_30;
    wp::float32 var_31;
    const wp::int32 var_32 = 0;
    wp::float32 var_33;
    wp::float32 var_34;
    const wp::int32 var_35 = 1;
    wp::float32 var_36;
    wp::float32 var_37;
    const wp::int32 var_38 = 1;
    wp::float32 var_39;
    wp::float32 var_40;
    const wp::int32 var_41 = 2;
    wp::float32 var_42;
    wp::float32 var_43;
    const wp::int32 var_44 = 2;
    wp::float32 var_45;
    wp::float32 var_46;
    wp::vec_t<3, wp::float32> var_47;
    wp::vec_t<3, wp::float32> var_48;
    const wp::int32 var_49 = 0;
    wp::int32 var_50;
    const wp::int32 var_51 = 1;
    wp::float32 var_52;
    wp::float32 var_53;
    bool var_54;
    const wp::int32 var_55 = 1;
    wp::int32 var_56;
    const wp::int32 var_57 = 2;
    wp::float32 var_58;
    wp::float32 var_59;
    bool var_60;
    const wp::int32 var_61 = 2;
    wp::int32 var_62;
    wp::float32 var_63;
    const wp::float32 var_64 = 0.0;
    bool var_65;
    const wp::float32 var_66 = 1.0;
    const wp::float32 var_67 = -1.0;
    wp::float32 var_68;
    wp::float32 var_69;
    wp::float32 var_70;
    wp::vec_t<3, wp::float32> var_71;
    //---------
    // forward
    // def box_normal(p:wp.vec3,half:wp.vec3):                                                <L 39>
    // q=wp.vec3(wp.abs(p[0]),wp.abs(p[1]),wp.abs(p[2]))-half;outside=wp.vec3(wp.max(q[0],0.),wp.max(q[1],0.),wp.max(q[2],0.));distance=wp.length(outside);normal=wp.vec3(0.)       <L 40>
    var_1 = wp::extract(var_p, var_0);
    var_2 = wp::abs(var_1);
    var_4 = wp::extract(var_p, var_3);
    var_5 = wp::abs(var_4);
    var_7 = wp::extract(var_p, var_6);
    var_8 = wp::abs(var_7);
    var_9 = wp::vec_t<3, wp::float32>(var_2, var_5, var_8);
    var_10 = wp::sub(var_9, var_half);
    var_12 = wp::extract(var_10, var_11);
    var_14 = wp::max(var_12, var_13);
    var_16 = wp::extract(var_10, var_15);
    var_18 = wp::max(var_16, var_17);
    var_20 = wp::extract(var_10, var_19);
    var_22 = wp::max(var_20, var_21);
    var_23 = wp::vec_t<3, wp::float32>(var_14, var_18, var_22);
    var_24 = wp::length(var_23);
    var_26 = wp::vec_t<3, wp::float32>(var_25);
    // if distance>1e-12:                                                                     <L 41>
    var_28 = (var_24 > var_27);
    if (var_28) {
        // normal=wp.vec3(wp.sign(p[0])*outside[0],wp.sign(p[1])*outside[1],wp.sign(p[2])*outside[2])/distance       <L 42>
        var_30 = wp::extract(var_p, var_29);
        var_31 = wp::sign(var_30);
        var_33 = wp::extract(var_23, var_32);
        var_34 = wp::mul(var_31, var_33);
        var_36 = wp::extract(var_p, var_35);
        var_37 = wp::sign(var_36);
        var_39 = wp::extract(var_23, var_38);
        var_40 = wp::mul(var_37, var_39);
        var_42 = wp::extract(var_p, var_41);
        var_43 = wp::sign(var_42);
        var_45 = wp::extract(var_23, var_44);
        var_46 = wp::mul(var_43, var_45);
        var_47 = wp::vec_t<3, wp::float32>(var_34, var_40, var_46);
        var_48 = wp::div(var_47, var_24);
    }
    if (!var_28) {
        // axis=int(0)                                                                        <L 44>
        var_50 = wp::int(var_49);
        // if q[1]>q[axis]:axis=1                                                             <L 45>
        var_52 = wp::extract(var_10, var_51);
        var_53 = wp::extract(var_10, var_50);
        var_54 = (var_52 > var_53);
        if (var_54) {
        }
        var_56 = wp::where(var_54, var_55, var_50);
        // if q[2]>q[axis]:axis=2                                                             <L 46>
        var_58 = wp::extract(var_10, var_57);
        var_59 = wp::extract(var_10, var_56);
        var_60 = (var_58 > var_59);
        if (var_60) {
        }
        var_62 = wp::where(var_60, var_61, var_56);
        // normal[axis]=1. if p[axis]>=0. else -1.;distance=q[axis]                           <L 47>
        var_63 = wp::extract(var_p, var_62);
        var_65 = (var_63 >= var_64);
        if (var_65) {
        }
        if (!var_65) {
        }
        var_68 = wp::where(var_65, var_66, var_67);
        wp::assign_inplace(var_26, var_62, var_68);
        var_69 = wp::extract(var_10, var_62);
    }
    var_70 = wp::where(var_28, var_24, var_69);
    var_71 = wp::where(var_28, var_48, var_26);
    // return normal,distance                                                                 <L 48>
    ret_0 = var_71;
    ret_1 = var_70;
    return;
}


// /home/omen/Documents/Codex/experiments/tomato_approx_rl_20261113_v28/src/solver.py:38
static CUDA_CALLABLE void adj_box_normal_0(
    wp::vec_t<3, wp::float32> var_p,
    wp::vec_t<3, wp::float32> var_half,
    wp::vec_t<3, wp::float32> & ret_0,
    wp::float32 & ret_1,
    wp::vec_t<3, wp::float32> & adj_p,
    wp::vec_t<3, wp::float32> & adj_half,
    wp::vec_t<3, wp::float32> & adj_ret_0,
    wp::float32 & adj_ret_1)
{
	// reverse mode disabled (module option "enable_backward" is False or no dependent kernel found with "enable_backward")
}



extern "C" __global__ void bonds_0502009f_cuda_kernel_forward(
    wp::launch_bounds_t<1> dim,
    wp::array_t<wp::vec_t<3, wp::float32>> var_x,
    wp::array_t<wp::vec_t<3, wp::float32>> var_v,
    wp::array_t<wp::vec_t<3, wp::float32>> var_force,
    wp::array_t<wp::vec_t<2, wp::int32>> var_edge,
    wp::array_t<wp::float32> var_rest,
    wp::array_t<wp::float32> var_stiffness,
    wp::array_t<wp::float32> var_mass,
    wp::array_t<wp::float32> var_area,
    wp::array_t<wp::int32> var_alive,
    wp::array_t<wp::float32> var_paid,
    wp::array_t<wp::vec_t<3, wp::float32>> var_tool,
    wp::array_t<wp::vec_t<3, wp::float32>> var_velocity,
    wp::array_t<wp::quat_t<wp::float32>> var_rotation,
    wp::array_t<wp::vec_t<3, wp::float32>> var_reaction,
    wp::array_t<wp::float32> var_load,
    wp::array_t<wp::float32> var_ledger,
    wp::array_t<wp::int32> var_bad,
    wp::float32 var_h,
    wp::float32 var_dt,
    wp::int32 var_n,
    wp::int32 var_nb,
    wp::float32 var_half_length,
    wp::int32 var_cut_enabled)
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
        wp::int32 var_1;
        wp::int32 var_2;
        bool var_3;
        wp::int32* var_4;
        const wp::int32 var_5 = 0;
        bool var_6;
        wp::int32 var_7;
        wp::int32* var_8;
        const wp::int32 var_9 = 0;
        bool var_10;
        wp::int32 var_11;
        wp::vec_t<2, wp::int32>* var_12;
        wp::vec_t<2, wp::int32> var_13;
        wp::vec_t<2, wp::int32> var_14;
        wp::int32 var_15;
        const wp::int32 var_16 = 0;
        wp::int32 var_17;
        wp::int32 var_18;
        wp::int32 var_19;
        const wp::int32 var_20 = 1;
        wp::int32 var_21;
        wp::int32 var_22;
        wp::vec_t<3, wp::float32>* var_23;
        wp::vec_t<3, wp::float32>* var_24;
        wp::vec_t<3, wp::float32> var_25;
        wp::vec_t<3, wp::float32> var_26;
        wp::vec_t<3, wp::float32> var_27;
        wp::float32 var_28;
        const wp::float32 var_29 = 1e-08;
        bool var_30;
        const wp::int32 var_31 = 2;
        wp::int32 var_32;
        wp::vec_t<3, wp::float32> var_33;
        wp::float32* var_34;
        wp::float32 var_35;
        wp::float32 var_36;
        wp::vec_t<3, wp::float32>* var_37;
        wp::vec_t<3, wp::float32>* var_38;
        wp::vec_t<3, wp::float32> var_39;
        wp::vec_t<3, wp::float32> var_40;
        wp::vec_t<3, wp::float32> var_41;
        wp::float32 var_42;
        const wp::int32 var_43 = 0;
        wp::int32 var_44;
        wp::float32* var_45;
        const wp::int32 var_46 = 1;
        wp::int32 var_47;
        wp::float32* var_48;
        wp::float32 var_49;
        wp::float32 var_50;
        wp::float32 var_51;
        const wp::int32 var_52 = 0;
        wp::int32 var_53;
        wp::float32* var_54;
        const wp::int32 var_55 = 1;
        wp::int32 var_56;
        wp::float32* var_57;
        wp::float32 var_58;
        wp::float32 var_59;
        wp::float32 var_60;
        wp::float32 var_61;
        const wp::float32 var_62 = 2.0;
        const wp::float32 var_63 = 0.02;
        wp::float32 var_64;
        wp::float32* var_65;
        wp::float32 var_66;
        wp::float32 var_67;
        wp::float32 var_68;
        wp::float32 var_69;
        wp::float32* var_70;
        wp::float32 var_71;
        wp::float32 var_72;
        wp::float32 var_73;
        wp::float32 var_74;
        wp::vec_t<3, wp::float32> var_75;
        wp::vec_t<3, wp::float32> var_76;
        wp::vec_t<3, wp::float32> var_77;
        const wp::int32 var_78 = 0;
        wp::float32 var_79;
        wp::float32 var_80;
        wp::float32 var_81;
        wp::float32 var_82;
        const wp::int32 var_83 = 0;
        bool var_84;
        wp::quat_t<wp::float32>* var_85;
        wp::vec_t<3, wp::float32>* var_86;
        wp::vec_t<3, wp::float32>* var_87;
        wp::vec_t<3, wp::float32> var_88;
        wp::vec_t<3, wp::float32> var_89;
        wp::vec_t<3, wp::float32> var_90;
        wp::vec_t<3, wp::float32> var_91;
        wp::quat_t<wp::float32> var_92;
        wp::quat_t<wp::float32>* var_93;
        wp::vec_t<3, wp::float32>* var_94;
        wp::vec_t<3, wp::float32>* var_95;
        wp::vec_t<3, wp::float32> var_96;
        wp::vec_t<3, wp::float32> var_97;
        wp::vec_t<3, wp::float32> var_98;
        wp::vec_t<3, wp::float32> var_99;
        wp::quat_t<wp::float32> var_100;
        const wp::int32 var_101 = 0;
        wp::float32 var_102;
        const wp::int32 var_103 = 0;
        wp::float32 var_104;
        wp::float32 var_105;
        const wp::float32 var_106 = 0.0;
        bool var_107;
        const wp::int32 var_108 = 0;
        wp::float32 var_109;
        const wp::int32 var_110 = 0;
        wp::float32 var_111;
        const wp::int32 var_112 = 0;
        wp::float32 var_113;
        wp::float32 var_114;
        wp::float32 var_115;
        wp::vec_t<3, wp::float32> var_116;
        wp::vec_t<3, wp::float32> var_117;
        wp::vec_t<3, wp::float32> var_118;
        bool var_119;
        const wp::int32 var_120 = 2;
        wp::float32 var_121;
        wp::float32 var_122;
        bool var_123;
        const wp::int32 var_124 = 1;
        wp::float32 var_125;
        const wp::float32 var_126 = -0.5;
        wp::float32 var_127;
        bool var_128;
        const wp::int32 var_129 = 1;
        wp::float32 var_130;
        const wp::float32 var_131 = 0.03;
        bool var_132;
        const wp::float32 var_133 = 1.0;
        wp::float32 var_134;
        wp::vec_t<3, wp::float32>* var_135;
        wp::vec_t<3, wp::float32> var_136;
        wp::vec_t<3, wp::float32> var_137;
        wp::vec_t<3, wp::float32>* var_138;
        wp::vec_t<3, wp::float32> var_139;
        wp::vec_t<3, wp::float32> var_140;
        wp::vec_t<3, wp::float32> var_141;
        wp::vec_t<3, wp::float32>* var_142;
        wp::vec_t<3, wp::float32> var_143;
        wp::vec_t<3, wp::float32> var_144;
        wp::quat_t<wp::float32>* var_145;
        wp::vec_t<3, wp::float32> var_146;
        wp::quat_t<wp::float32> var_147;
        const wp::int32 var_148 = 1;
        wp::float32 var_149;
        wp::float32 var_150;
        const wp::float32 var_151 = 0.0;
        wp::float32 var_152;
        const wp::float32 var_153 = 0.25;
        const wp::int32 var_154 = 2;
        wp::float32 var_155;
        wp::float32 var_156;
        wp::float32 var_157;
        wp::float32 var_158;
        wp::float32 var_159;
        const wp::float32 var_160 = 80.0;
        wp::float32* var_161;
        wp::float32 var_162;
        wp::float32 var_163;
        wp::float32* var_164;
        wp::float32 var_165;
        wp::float32 var_166;
        const wp::float32 var_167 = 0.0;
        wp::float32 var_168;
        bool var_169;
        const wp::float32 var_170 = 0.0;
        bool var_171;
        const wp::float32 var_172 = 1e-08;
        bool var_173;
        const wp::float32 var_174 = 0.0;
        bool var_175;
        wp::float32 var_176;
        wp::float32 var_177;
        wp::float32 var_178;
        wp::float32 var_179;
        wp::float32 var_180;
        wp::float32 var_181;
        wp::vec_t<3, wp::float32> var_182;
        wp::vec_t<3, wp::float32> var_183;
        const wp::float32 var_184 = 1.0;
        wp::float32 var_185;
        wp::vec_t<3, wp::float32> var_186;
        wp::vec_t<3, wp::float32> var_187;
        wp::vec_t<3, wp::float32> var_188;
        wp::vec_t<3, wp::float32> var_189;
        wp::vec_t<3, wp::float32> var_190;
        wp::float32 var_191;
        wp::float32 var_192;
        const wp::int32 var_193 = 1;
        wp::float32 var_194;
        const wp::int32 var_195 = 2;
        wp::vec_t<3, wp::float32>* var_196;
        wp::float32 var_197;
        wp::vec_t<3, wp::float32> var_198;
        wp::float32 var_199;
        wp::float32 var_200;
        wp::float32 var_201;
        wp::float32* var_202;
        const wp::float32 var_203 = 1.0;
        const wp::float32 var_204 = 1e-05;
        wp::float32 var_205;
        wp::float32 var_206;
        bool var_207;
        wp::float32 var_208;
        const wp::int32 var_209 = 0;
        const wp::int32 var_210 = 3;
        const wp::float32 var_211 = 0.5;
        wp::float32* var_212;
        wp::float32 var_213;
        wp::float32 var_214;
        wp::float32 var_215;
        wp::float32 var_216;
        wp::float32 var_217;
        //---------
        // forward
        // def bonds(x:wp.array(dtype=wp.vec3),v:wp.array(dtype=wp.vec3),force:wp.array(dtype=wp.vec3),edge:wp.array(dtype=wp.vec2i),rest:wp.array(dtype=float),stiffness:wp.array(dtype=float),mass:wp.array(dtype=float),area:wp.array(dtype=float),alive:wp.array(dtype=int),paid:wp.array(dtype=float),tool:wp.array(dtype=wp.vec3),velocity:wp.array(dtype=wp.vec3),rotation:wp.array(dtype=wp.quat),reaction:wp.array(dtype=wp.vec3),load:wp.array(dtype=float),ledger:wp.array2d(dtype=float),bad:wp.array(dtype=int),h:float,dt:float,n:int,nb:int,half_length:float,cut_enabled:int):       <L 17>
        // idx=wp.tid();e=idx//nb;b=idx%nb                                                        <L 18>
        var_0 = builtin_tid1d();
        var_1 = wp::floordiv(var_0, var_nb);
        var_2 = wp::mod(var_0, var_nb);
        // if bad[e]!=0 or alive[idx]==0:return                                                   <L 19>
        var_4 = wp::address(var_bad, var_1);
        var_7 = wp::load(var_4);
        var_6 = (var_7 != var_5);
        var_3 = var_6;
        if (!var_3) {
            var_8 = wp::address(var_alive, var_0);
            var_11 = wp::load(var_8);
            var_10 = (var_11 == var_9);
            var_3 = var_3 || var_10;
        }
        if (var_3) {
            continue;
        }
        // ends=edge[b];i=e*n+ends[0];j=e*n+ends[1];delta=x[j]-x[i];length=wp.length(delta)       <L 20>
        var_12 = wp::address(var_edge, var_2);
        var_14 = wp::load(var_12);
        var_13 = wp::copy(var_14);
        var_15 = wp::mul(var_1, var_n);
        var_17 = wp::extract(var_13, var_16);
        var_18 = wp::add(var_15, var_17);
        var_19 = wp::mul(var_1, var_n);
        var_21 = wp::extract(var_13, var_20);
        var_22 = wp::add(var_19, var_21);
        var_23 = wp::address(var_x, var_22);
        var_24 = wp::address(var_x, var_18);
        var_26 = wp::load(var_23);
        var_27 = wp::load(var_24);
        var_25 = wp::sub(var_26, var_27);
        var_28 = wp::length(var_25);
        // if length<1e-8:wp.atomic_max(bad,e,2);return                                           <L 21>
        var_30 = (var_28 < var_29);
        if (var_30) {
            var_32 = wp::atomic_max(var_bad, var_1, var_31);
            continue;
        }
        // direction=delta/length;strain=length-rest[b];relative=wp.dot(v[j]-v[i],direction);reduced=mass[ends[0]]*mass[ends[1]]/(mass[ends[0]]+mass[ends[1]]);damping=2.*.02*wp.sqrt(stiffness[b]*reduced);f=(stiffness[b]*strain+damping*relative)*direction       <L 22>
        var_33 = wp::div(var_25, var_28);
        var_34 = wp::address(var_rest, var_2);
        var_36 = wp::load(var_34);
        var_35 = wp::sub(var_28, var_36);
        var_37 = wp::address(var_v, var_22);
        var_38 = wp::address(var_v, var_18);
        var_40 = wp::load(var_37);
        var_41 = wp::load(var_38);
        var_39 = wp::sub(var_40, var_41);
        var_42 = wp::dot(var_39, var_33);
        var_44 = wp::extract(var_13, var_43);
        var_45 = wp::address(var_mass, var_44);
        var_47 = wp::extract(var_13, var_46);
        var_48 = wp::address(var_mass, var_47);
        var_50 = wp::load(var_45);
        var_51 = wp::load(var_48);
        var_49 = wp::mul(var_50, var_51);
        var_53 = wp::extract(var_13, var_52);
        var_54 = wp::address(var_mass, var_53);
        var_56 = wp::extract(var_13, var_55);
        var_57 = wp::address(var_mass, var_56);
        var_59 = wp::load(var_54);
        var_60 = wp::load(var_57);
        var_58 = wp::add(var_59, var_60);
        var_61 = wp::div(var_49, var_58);
        var_64 = wp::mul(var_62, var_63);
        var_65 = wp::address(var_stiffness, var_2);
        var_67 = wp::load(var_65);
        var_66 = wp::mul(var_67, var_61);
        var_68 = wp::sqrt(var_66);
        var_69 = wp::mul(var_64, var_68);
        var_70 = wp::address(var_stiffness, var_2);
        var_72 = wp::load(var_70);
        var_71 = wp::mul(var_72, var_35);
        var_73 = wp::mul(var_69, var_42);
        var_74 = wp::add(var_71, var_73);
        var_75 = wp::mul(var_74, var_33);
        // wp.atomic_add(force,i,f);wp.atomic_sub(force,j,f);wp.atomic_add(ledger,e,0,damping*relative*relative*dt)       <L 23>
        var_76 = wp::atomic_add(var_force, var_18, var_75);
        var_77 = wp::atomic_sub(var_force, var_22, var_75);
        var_79 = wp::mul(var_69, var_42);
        var_80 = wp::mul(var_79, var_42);
        var_81 = wp::mul(var_80, var_dt);
        var_82 = wp::atomic_add(var_ledger, var_1, var_78, var_81);
        // if cut_enabled==0:return                                                               <L 24>
        var_84 = (var_cut_enabled == var_83);
        if (var_84) {
            continue;
        }
        // a=wp.quat_rotate_inv(rotation[e],x[i]-tool[e]);c=wp.quat_rotate_inv(rotation[e],x[j]-tool[e])       <L 25>
        var_85 = wp::address(var_rotation, var_1);
        var_86 = wp::address(var_x, var_18);
        var_87 = wp::address(var_tool, var_1);
        var_89 = wp::load(var_86);
        var_90 = wp::load(var_87);
        var_88 = wp::sub(var_89, var_90);
        var_92 = wp::load(var_85);
        var_91 = wp::quat_rotate_inv(var_92, var_88);
        var_93 = wp::address(var_rotation, var_1);
        var_94 = wp::address(var_x, var_22);
        var_95 = wp::address(var_tool, var_1);
        var_97 = wp::load(var_94);
        var_98 = wp::load(var_95);
        var_96 = wp::sub(var_97, var_98);
        var_100 = wp::load(var_93);
        var_99 = wp::quat_rotate_inv(var_100, var_96);
        // if a[0]*c[0]>=0.:return                                                                <L 26>
        var_102 = wp::extract(var_91, var_101);
        var_104 = wp::extract(var_99, var_103);
        var_105 = wp::mul(var_102, var_104);
        var_107 = (var_105 >= var_106);
        if (var_107) {
            continue;
        }
        // t=a[0]/(a[0]-c[0]);p=a+t*(c-a)                                                         <L 27>
        var_109 = wp::extract(var_91, var_108);
        var_111 = wp::extract(var_91, var_110);
        var_113 = wp::extract(var_99, var_112);
        var_114 = wp::sub(var_111, var_113);
        var_115 = wp::div(var_109, var_114);
        var_116 = wp::sub(var_99, var_91);
        var_117 = wp::mul(var_115, var_116);
        var_118 = wp::add(var_91, var_117);
        // if wp.abs(p[2])>half_length or p[1]<-.5*h or p[1]>.03:return                           <L 28>
        var_121 = wp::extract(var_118, var_120);
        var_122 = wp::abs(var_121);
        var_123 = (var_122 > var_half_length);
        var_119 = var_123;
        if (!var_119) {
            var_125 = wp::extract(var_118, var_124);
            var_127 = wp::mul(var_126, var_h);
            var_128 = (var_125 < var_127);
            var_119 = var_119 || var_128;
        }
        if (!var_119) {
            var_130 = wp::extract(var_118, var_129);
            var_132 = (var_130 > var_131);
            var_119 = var_119 || var_132;
        }
        if (var_119) {
            continue;
        }
        // midpoint_v=(1.-t)*v[i]+t*v[j];rel=velocity[e]-midpoint_v;local=wp.quat_rotate_inv(rotation[e],rel);advance=wp.max(-local[1],0.)+.25*wp.abs(local[2]);speed=wp.length(rel);budget=80.*area[b];remaining=wp.max(budget-paid[idx],0.)       <L 29>
        var_134 = wp::sub(var_133, var_115);
        var_135 = wp::address(var_v, var_18);
        var_137 = wp::load(var_135);
        var_136 = wp::mul(var_134, var_137);
        var_138 = wp::address(var_v, var_22);
        var_140 = wp::load(var_138);
        var_139 = wp::mul(var_115, var_140);
        var_141 = wp::add(var_136, var_139);
        var_142 = wp::address(var_velocity, var_1);
        var_144 = wp::load(var_142);
        var_143 = wp::sub(var_144, var_141);
        var_145 = wp::address(var_rotation, var_1);
        var_147 = wp::load(var_145);
        var_146 = wp::quat_rotate_inv(var_147, var_143);
        var_149 = wp::extract(var_146, var_148);
        var_150 = wp::neg(var_149);
        var_152 = wp::max(var_150, var_151);
        var_155 = wp::extract(var_146, var_154);
        var_156 = wp::abs(var_155);
        var_157 = wp::mul(var_153, var_156);
        var_158 = wp::add(var_152, var_157);
        var_159 = wp::length(var_143);
        var_161 = wp::address(var_area, var_2);
        var_163 = wp::load(var_161);
        var_162 = wp::mul(var_160, var_163);
        var_164 = wp::address(var_paid, var_0);
        var_166 = wp::load(var_164);
        var_165 = wp::sub(var_162, var_166);
        var_168 = wp::max(var_165, var_167);
        // if advance<=0. or speed<=1e-8 or remaining<=0.:return                                  <L 30>
        var_171 = (var_158 <= var_170);
        var_169 = var_171;
        if (!var_169) {
            var_173 = (var_159 <= var_172);
            var_169 = var_169 || var_173;
        }
        if (!var_169) {
            var_175 = (var_168 <= var_174);
            var_169 = var_169 || var_175;
        }
        if (var_169) {
            continue;
        }
        // dwork=wp.min(remaining,budget/h*advance*dt);resistance=dwork/(speed*dt)*rel/speed       <L 33>
        var_176 = wp::div(var_162, var_h);
        var_177 = wp::mul(var_176, var_158);
        var_178 = wp::mul(var_177, var_dt);
        var_179 = wp::min(var_168, var_178);
        var_180 = wp::mul(var_159, var_dt);
        var_181 = wp::div(var_179, var_180);
        var_182 = wp::mul(var_181, var_143);
        var_183 = wp::div(var_182, var_159);
        // wp.atomic_add(force,i,(1.-t)*resistance);wp.atomic_add(force,j,t*resistance);wp.atomic_sub(reaction,e,resistance);wp.atomic_add(load,e,wp.length(resistance));wp.atomic_add(ledger,e,1,dwork);wp.atomic_add(ledger,e,2,wp.dot(resistance,velocity[e])*dt);paid[idx]+=dwork       <L 34>
        var_185 = wp::sub(var_184, var_115);
        var_186 = wp::mul(var_185, var_183);
        var_187 = wp::atomic_add(var_force, var_18, var_186);
        var_188 = wp::mul(var_115, var_183);
        var_189 = wp::atomic_add(var_force, var_22, var_188);
        var_190 = wp::atomic_sub(var_reaction, var_1, var_183);
        var_191 = wp::length(var_183);
        var_192 = wp::atomic_add(var_load, var_1, var_191);
        var_194 = wp::atomic_add(var_ledger, var_1, var_193, var_179);
        var_196 = wp::address(var_velocity, var_1);
        var_198 = wp::load(var_196);
        var_197 = wp::dot(var_183, var_198);
        var_199 = wp::mul(var_197, var_dt);
        var_200 = wp::atomic_add(var_ledger, var_1, var_195, var_199);
        var_201 = wp::atomic_add(var_paid, var_0, var_179);
        // if paid[idx]>=budget*(1.-1e-5):                                                        <L 35>
        var_202 = wp::address(var_paid, var_0);
        var_205 = wp::sub(var_203, var_204);
        var_206 = wp::mul(var_162, var_205);
        var_208 = wp::load(var_202);
        var_207 = (var_208 >= var_206);
        if (var_207) {
            // alive[idx]=0;wp.atomic_add(ledger,e,3,.5*stiffness[b]*strain*strain)               <L 36>
            wp::array_store(var_alive, var_0, var_209);
            var_212 = wp::address(var_stiffness, var_2);
            var_214 = wp::load(var_212);
            var_213 = wp::mul(var_211, var_214);
            var_215 = wp::mul(var_213, var_35);
            var_216 = wp::mul(var_215, var_35);
            var_217 = wp::atomic_add(var_ledger, var_1, var_210, var_216);
        }
    }
}



extern "C" __global__ void clear_step_1c989fed_cuda_kernel_forward(
    wp::launch_bounds_t<1> dim,
    wp::array_t<wp::vec_t<3, wp::float32>> var_x,
    wp::array_t<wp::vec_t<3, wp::float32>> var_force,
    wp::array_t<wp::float32> var_mass,
    wp::array_t<wp::vec_t<3, wp::float32>> var_reaction,
    wp::array_t<wp::float32> var_normal_load,
    wp::array_t<wp::vec_t<3, wp::float32>> var_drive,
    wp::array_t<wp::vec_t<3, wp::float32>> var_tool,
    wp::array_t<wp::vec_t<3, wp::float32>> var_action,
    wp::array_t<wp::int32> var_bad,
    wp::float32 var_dt,
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
        wp::int32 var_0;
        wp::int32 var_1;
        const wp::float32 var_2 = 0.0;
        const wp::float32 var_3 = -9.81;
        wp::int32 var_4;
        wp::float32* var_5;
        wp::float32 var_6;
        wp::float32 var_7;
        const wp::float32 var_8 = 0.0;
        wp::vec_t<3, wp::float32> var_9;
        wp::int32 var_10;
        const wp::int32 var_11 = 0;
        bool var_12;
        const wp::float32 var_13 = 0.0;
        wp::vec_t<3, wp::float32> var_14;
        const wp::float32 var_15 = 0.0;
        wp::vec_t<3, wp::float32>* var_16;
        wp::vec_t<3, wp::float32> var_17;
        wp::int32* var_18;
        const wp::int32 var_19 = 0;
        bool var_20;
        wp::int32 var_21;
        wp::vec_t<3, wp::float32>* var_22;
        wp::vec_t<3, wp::float32> var_23;
        wp::vec_t<3, wp::float32> var_24;
        wp::vec_t<3, wp::float32> var_25;
        //---------
        // forward
        // def clear_step(x:wp.array(dtype=wp.vec3),force:wp.array(dtype=wp.vec3),mass:wp.array(dtype=float),reaction:wp.array(dtype=wp.vec3),normal_load:wp.array(dtype=float),drive:wp.array(dtype=wp.vec3),tool:wp.array(dtype=wp.vec3),action:wp.array(dtype=wp.vec3),bad:wp.array(dtype=int),dt:float,n:int):       <L 10>
        // i=wp.tid();e=i//n;force[i]=wp.vec3(0.,-9.81*mass[i%n],0.)                              <L 11>
        var_0 = builtin_tid1d();
        var_1 = wp::floordiv(var_0, var_n);
        var_4 = wp::mod(var_0, var_n);
        var_5 = wp::address(var_mass, var_4);
        var_7 = wp::load(var_5);
        var_6 = wp::mul(var_3, var_7);
        var_9 = wp::vec_t<3, wp::float32>(var_2, var_6, var_8);
        wp::array_store(var_force, var_0, var_9);
        // if i%n==0:                                                                             <L 12>
        var_10 = wp::mod(var_0, var_n);
        var_12 = (var_10 == var_11);
        if (var_12) {
            // reaction[e]=wp.vec3(0.);normal_load[e]=0.;drive[e]=action[e]                       <L 13>
            var_14 = wp::vec_t<3, wp::float32>(var_13);
            wp::array_store(var_reaction, var_1, var_14);
            wp::array_store(var_normal_load, var_1, var_15);
            var_16 = wp::address(var_action, var_1);
            var_17 = wp::load(var_16);
            wp::array_store(var_drive, var_1, var_17);
            // if bad[e]==0:tool[e]+=dt*action[e]                                                 <L 14>
            var_18 = wp::address(var_bad, var_1);
            var_21 = wp::load(var_18);
            var_20 = (var_21 == var_19);
            if (var_20) {
                var_22 = wp::address(var_action, var_1);
                var_24 = wp::load(var_22);
                var_23 = wp::mul(var_dt, var_24);
                var_25 = wp::atomic_add(var_tool, var_1, var_23);
            }
        }
    }
}



extern "C" __global__ void finish_step_29b9af99_cuda_kernel_forward(
    wp::launch_bounds_t<1> dim,
    wp::array_t<wp::vec_t<3, wp::float32>> var_reaction,
    wp::array_t<wp::float32> var_load,
    wp::array_t<wp::float32> var_peak,
    wp::array_t<wp::int32> var_bad,
    wp::float32 var_stop_force)
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
        wp::float32* var_1;
        wp::float32* var_2;
        wp::float32 var_3;
        wp::float32 var_4;
        wp::float32 var_5;
        bool var_6;
        wp::float32* var_7;
        bool var_8;
        wp::float32 var_9;
        wp::float32* var_10;
        bool var_11;
        wp::float32 var_12;
        bool var_13;
        const wp::int32 var_14 = 3;
        wp::int32 var_15;
        //---------
        // forward
        // def finish_step(reaction:wp.array(dtype=wp.vec3),load:wp.array(dtype=float),peak:wp.array(dtype=float),bad:wp.array(dtype=int),stop_force:float):       <L 72>
        // e=wp.tid();peak[e]=wp.max(peak[e],load[e])                                             <L 73>
        var_0 = builtin_tid1d();
        var_1 = wp::address(var_peak, var_0);
        var_2 = wp::address(var_load, var_0);
        var_4 = wp::load(var_1);
        var_5 = wp::load(var_2);
        var_3 = wp::max(var_4, var_5);
        wp::array_store(var_peak, var_0, var_3);
        // if load[e]>stop_force or not wp.isfinite(load[e]):wp.atomic_max(bad,e,3)               <L 74>
        var_7 = wp::address(var_load, var_0);
        var_9 = wp::load(var_7);
        var_8 = (var_9 > var_stop_force);
        var_6 = var_8;
        if (!var_6) {
            var_10 = wp::address(var_load, var_0);
            var_12 = wp::load(var_10);
            var_11 = wp::isfinite(var_12);
            var_13 = wp::unot(var_11);
            var_6 = var_6 || var_13;
        }
        if (var_6) {
            var_15 = wp::atomic_max(var_bad, var_0, var_14);
        }
    }
}



extern "C" __global__ void integrate_318633da_cuda_kernel_forward(
    wp::launch_bounds_t<1> dim,
    wp::array_t<wp::vec_t<3, wp::float32>> var_x,
    wp::array_t<wp::int32> var_fixed,
    wp::array_t<wp::vec_t<3, wp::float32>> var_v,
    wp::array_t<wp::vec_t<3, wp::float32>> var_force,
    wp::array_t<wp::float32> var_mass,
    wp::array_t<wp::vec_t<3, wp::float32>> var_tool,
    wp::array_t<wp::vec_t<3, wp::float32>> var_velocity,
    wp::array_t<wp::quat_t<wp::float32>> var_rotation,
    wp::array_t<wp::vec_t<3, wp::float32>> var_reaction,
    wp::array_t<wp::float32> var_load,
    wp::array_t<wp::float32> var_ledger,
    wp::array_t<wp::int32> var_bad,
    wp::float32 var_dt,
    wp::float32 var_radius,
    wp::int32 var_n,
    wp::float32 var_half_length,
    wp::int32 var_knife_enabled)
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
        wp::int32 var_1;
        wp::int32* var_2;
        const wp::int32 var_3 = 0;
        bool var_4;
        wp::int32 var_5;
        wp::int32* var_6;
        const wp::int32 var_7 = 0;
        bool var_8;
        wp::int32 var_9;
        wp::int32 var_10;
        wp::float32* var_11;
        wp::float32 var_12;
        wp::float32 var_13;
        wp::vec_t<3, wp::float32>* var_14;
        wp::vec_t<3, wp::float32>* var_15;
        wp::vec_t<3, wp::float32> var_16;
        wp::vec_t<3, wp::float32> var_17;
        wp::vec_t<3, wp::float32> var_18;
        wp::vec_t<3, wp::float32> var_19;
        wp::vec_t<3, wp::float32> var_20;
        wp::vec_t<3, wp::float32>* var_21;
        wp::vec_t<3, wp::float32> var_22;
        wp::vec_t<3, wp::float32> var_23;
        wp::vec_t<3, wp::float32> var_24;
        const wp::int32 var_25 = 0;
        bool var_26;
        wp::quat_t<wp::float32>* var_27;
        wp::vec_t<3, wp::float32>* var_28;
        wp::vec_t<3, wp::float32> var_29;
        wp::vec_t<3, wp::float32> var_30;
        wp::vec_t<3, wp::float32> var_31;
        wp::quat_t<wp::float32> var_32;
        const wp::float32 var_33 = 0.0;
        const wp::float32 var_34 = 0.015;
        const wp::float32 var_35 = 0.0;
        wp::vec_t<3, wp::float32> var_36;
        wp::vec_t<3, wp::float32> var_37;
        const wp::float32 var_38 = 0.0005;
        const wp::float32 var_39 = 0.015;
        wp::vec_t<3, wp::float32> var_40;
        wp::vec_t<3, wp::float32> var_41;
        wp::float32 var_42;
        wp::float32 var_43;
        const wp::float32 var_44 = 0.0;
        bool var_45;
        wp::quat_t<wp::float32>* var_46;
        wp::vec_t<3, wp::float32> var_47;
        wp::quat_t<wp::float32> var_48;
        wp::vec_t<3, wp::float32> var_49;
        wp::float32 var_50;
        wp::vec_t<3, wp::float32> var_51;
        wp::vec_t<3, wp::float32> var_52;
        wp::vec_t<3, wp::float32> var_53;
        wp::vec_t<3, wp::float32> var_54;
        wp::vec_t<3, wp::float32>* var_55;
        wp::vec_t<3, wp::float32> var_56;
        wp::vec_t<3, wp::float32> var_57;
        wp::float32 var_58;
        wp::vec_t<3, wp::float32> var_59;
        wp::vec_t<3, wp::float32> var_60;
        wp::float32 var_61;
        const wp::float32 var_62 = 0.0;
        wp::vec_t<3, wp::float32> var_63;
        const wp::float32 var_64 = 1e-12;
        bool var_65;
        const wp::float32 var_66 = 0.2;
        wp::float32 var_67;
        wp::float32 var_68;
        wp::float32 var_69;
        wp::float32 var_70;
        wp::float32 var_71;
        wp::vec_t<3, wp::float32> var_72;
        wp::vec_t<3, wp::float32> var_73;
        wp::vec_t<3, wp::float32> var_74;
        wp::vec_t<3, wp::float32> var_75;
        wp::vec_t<3, wp::float32> var_76;
        wp::vec_t<3, wp::float32> var_77;
        wp::vec_t<3, wp::float32> var_78;
        wp::vec_t<3, wp::float32> var_79;
        wp::vec_t<3, wp::float32> var_80;
        wp::float32 var_81;
        wp::float32 var_82;
        wp::float32 var_83;
        const wp::int32 var_84 = 2;
        wp::vec_t<3, wp::float32>* var_85;
        wp::float32 var_86;
        wp::vec_t<3, wp::float32> var_87;
        wp::float32 var_88;
        const wp::int32 var_89 = 4;
        wp::float32 var_90;
        wp::float32 var_91;
        wp::float32 var_92;
        wp::vec_t<3, wp::float32> var_93;
        wp::vec_t<3, wp::float32> var_94;
        wp::vec_t<3, wp::float32> var_95;
        wp::vec_t<3, wp::float32> var_96;
        wp::vec_t<3, wp::float32> var_97;
        const wp::int32 var_98 = 1;
        wp::float32 var_99;
        bool var_100;
        const wp::int32 var_101 = 1;
        const wp::int32 var_102 = 1;
        wp::float32 var_103;
        const wp::float32 var_104 = 0.0;
        bool var_105;
        const wp::int32 var_106 = 1;
        wp::float32 var_107;
        wp::float32 var_108;
        const wp::float32 var_109 = 0.0;
        const wp::int32 var_110 = 1;
        const wp::int32 var_111 = 0;
        wp::float32 var_112;
        const wp::float32 var_113 = 0.0;
        const wp::int32 var_114 = 2;
        wp::float32 var_115;
        wp::vec_t<3, wp::float32> var_116;
        wp::float32 var_117;
        const wp::float32 var_118 = 1e-12;
        bool var_119;
        const wp::float32 var_120 = 0.4;
        wp::float32 var_121;
        wp::float32 var_122;
        wp::vec_t<3, wp::float32> var_123;
        wp::vec_t<3, wp::float32> var_124;
        wp::vec_t<3, wp::float32> var_125;
        wp::vec_t<3, wp::float32> var_126;
        wp::vec_t<3, wp::float32> var_127;
        wp::vec_t<3, wp::float32> var_128;
        bool var_129;
        const wp::int32 var_130 = 0;
        wp::float32 var_131;
        bool var_132;
        bool var_133;
        const wp::int32 var_134 = 1;
        wp::float32 var_135;
        bool var_136;
        bool var_137;
        const wp::int32 var_138 = 2;
        wp::float32 var_139;
        bool var_140;
        bool var_141;
        wp::float32 var_142;
        const wp::float32 var_143 = 10.0;
        bool var_144;
        const wp::int32 var_145 = 2;
        wp::int32 var_146;
        //---------
        // forward
        // def integrate(x:wp.array(dtype=wp.vec3),fixed:wp.array(dtype=int),v:wp.array(dtype=wp.vec3),force:wp.array(dtype=wp.vec3),mass:wp.array(dtype=float),tool:wp.array(dtype=wp.vec3),velocity:wp.array(dtype=wp.vec3),rotation:wp.array(dtype=wp.quat),reaction:wp.array(dtype=wp.vec3),load:wp.array(dtype=float),ledger:wp.array2d(dtype=float),bad:wp.array(dtype=int),dt:float,radius:float,n:int,half_length:float,knife_enabled:int):       <L 51>
        // i=wp.tid();e=i//n                                                                      <L 52>
        var_0 = builtin_tid1d();
        var_1 = wp::floordiv(var_0, var_n);
        // if bad[e]!=0:return                                                                    <L 53>
        var_2 = wp::address(var_bad, var_1);
        var_5 = wp::load(var_2);
        var_4 = (var_5 != var_3);
        if (var_4) {
            continue;
        }
        // if fixed[i]!=0:return                                                                  <L 54>
        var_6 = wp::address(var_fixed, var_0);
        var_9 = wp::load(var_6);
        var_8 = (var_9 != var_7);
        if (var_8) {
            continue;
        }
        // m=mass[i%n];newv=v[i]+dt*force[i]/m;newx=x[i]+dt*newv                                  <L 55>
        var_10 = wp::mod(var_0, var_n);
        var_11 = wp::address(var_mass, var_10);
        var_13 = wp::load(var_11);
        var_12 = wp::copy(var_13);
        var_14 = wp::address(var_v, var_0);
        var_15 = wp::address(var_force, var_0);
        var_17 = wp::load(var_15);
        var_16 = wp::mul(var_dt, var_17);
        var_18 = wp::div(var_16, var_12);
        var_20 = wp::load(var_14);
        var_19 = wp::add(var_20, var_18);
        var_21 = wp::address(var_x, var_0);
        var_22 = wp::mul(var_dt, var_19);
        var_24 = wp::load(var_21);
        var_23 = wp::add(var_24, var_22);
        // if knife_enabled!=0:                                                                   <L 56>
        var_26 = (var_knife_enabled != var_25);
        if (var_26) {
            // p=wp.quat_rotate_inv(rotation[e],newx-tool[e])-wp.vec3(0.,.015,0.);normal,distance=box_normal(p,wp.vec3(.0005,.015,half_length));penetration=radius-distance       <L 57>
            var_27 = wp::address(var_rotation, var_1);
            var_28 = wp::address(var_tool, var_1);
            var_30 = wp::load(var_28);
            var_29 = wp::sub(var_23, var_30);
            var_32 = wp::load(var_27);
            var_31 = wp::quat_rotate_inv(var_32, var_29);
            var_36 = wp::vec_t<3, wp::float32>(var_33, var_34, var_35);
            var_37 = wp::sub(var_31, var_36);
            var_40 = wp::vec_t<3, wp::float32>(var_38, var_39, var_half_length);
            box_normal_0(var_37, var_40, var_41, var_42);
            var_43 = wp::sub(var_radius, var_42);
            // if penetration>0.:                                                                 <L 58>
            var_45 = (var_43 > var_44);
            if (var_45) {
                // normal=wp.quat_rotate(rotation[e],normal);correction=penetration*normal;impulse=m/dt*correction;newx+=correction;newv+=impulse/m       <L 59>
                var_46 = wp::address(var_rotation, var_1);
                var_48 = wp::load(var_46);
                var_47 = wp::quat_rotate(var_48, var_41);
                var_49 = wp::mul(var_43, var_47);
                var_50 = wp::div(var_12, var_dt);
                var_51 = wp::mul(var_50, var_49);
                var_52 = wp::add(var_23, var_49);
                var_53 = wp::div(var_51, var_12);
                var_54 = wp::add(var_19, var_53);
                // rel=newv-velocity[e];tangent=rel-wp.dot(rel,normal)*normal;length=wp.length(tangent);friction=wp.vec3(0.)       <L 60>
                var_55 = wp::address(var_velocity, var_1);
                var_57 = wp::load(var_55);
                var_56 = wp::sub(var_54, var_57);
                var_58 = wp::dot(var_56, var_47);
                var_59 = wp::mul(var_58, var_47);
                var_60 = wp::sub(var_56, var_59);
                var_61 = wp::length(var_60);
                var_63 = wp::vec_t<3, wp::float32>(var_62);
                // if length>1e-12:friction=-wp.min(.2*wp.length(impulse),m*length)*tangent/length;newv+=friction/m       <L 61>
                var_65 = (var_61 > var_64);
                if (var_65) {
                    var_67 = wp::length(var_51);
                    var_68 = wp::mul(var_66, var_67);
                    var_69 = wp::mul(var_12, var_61);
                    var_70 = wp::min(var_68, var_69);
                    var_71 = wp::neg(var_70);
                    var_72 = wp::mul(var_71, var_60);
                    var_73 = wp::div(var_72, var_61);
                    var_74 = wp::div(var_73, var_12);
                    var_75 = wp::add(var_54, var_74);
                }
                var_76 = wp::where(var_65, var_75, var_54);
                var_77 = wp::where(var_65, var_73, var_63);
                // total=impulse+friction;wp.atomic_sub(reaction,e,total/dt);wp.atomic_add(load,e,wp.length(total)/dt);wp.atomic_add(ledger,e,2,wp.dot(total,velocity[e]));wp.atomic_add(ledger,e,4,-wp.dot(friction,rel))       <L 62>
                var_78 = wp::add(var_51, var_77);
                var_79 = wp::div(var_78, var_dt);
                var_80 = wp::atomic_sub(var_reaction, var_1, var_79);
                var_81 = wp::length(var_78);
                var_82 = wp::div(var_81, var_dt);
                var_83 = wp::atomic_add(var_load, var_1, var_82);
                var_85 = wp::address(var_velocity, var_1);
                var_87 = wp::load(var_85);
                var_86 = wp::dot(var_78, var_87);
                var_88 = wp::atomic_add(var_ledger, var_1, var_84, var_86);
                var_90 = wp::dot(var_77, var_56);
                var_91 = wp::neg(var_90);
                var_92 = wp::atomic_add(var_ledger, var_1, var_89, var_91);
            }
            var_93 = wp::where(var_45, var_76, var_19);
            var_94 = wp::where(var_45, var_52, var_23);
            var_95 = wp::where(var_45, var_47, var_41);
        }
        var_96 = wp::where(var_26, var_93, var_19);
        var_97 = wp::where(var_26, var_94, var_23);
        // if newx[1]<radius:                                                                     <L 63>
        var_99 = wp::extract(var_97, var_98);
        var_100 = (var_99 < var_radius);
        if (var_100) {
            // newx[1]=radius                                                                     <L 64>
            wp::assign_inplace(var_97, var_101, var_radius);
            // if newv[1]<0.:                                                                     <L 65>
            var_103 = wp::extract(var_96, var_102);
            var_105 = (var_103 < var_104);
            if (var_105) {
                // normal_speed=-newv[1];newv[1]=0.;horizontal=wp.vec3(newv[0],0.,newv[2]);speed=wp.length(horizontal)       <L 66>
                var_107 = wp::extract(var_96, var_106);
                var_108 = wp::neg(var_107);
                wp::assign_inplace(var_96, var_110, var_109);
                var_112 = wp::extract(var_96, var_111);
                var_115 = wp::extract(var_96, var_114);
                var_116 = wp::vec_t<3, wp::float32>(var_112, var_113, var_115);
                var_117 = wp::length(var_116);
                // if speed>1e-12:newv-=wp.min(.4*normal_speed,speed)*horizontal/speed            <L 67>
                var_119 = (var_117 > var_118);
                if (var_119) {
                    var_121 = wp::mul(var_120, var_108);
                    var_122 = wp::min(var_121, var_117);
                    var_123 = wp::mul(var_122, var_116);
                    var_124 = wp::div(var_123, var_117);
                    var_125 = wp::sub(var_96, var_124);
                }
                var_126 = wp::where(var_119, var_125, var_96);
            }
            var_127 = wp::where(var_105, var_126, var_96);
        }
        var_128 = wp::where(var_100, var_127, var_96);
        // if not wp.isfinite(newx[0]) or not wp.isfinite(newx[1]) or not wp.isfinite(newx[2]) or wp.length(newv)>10.:wp.atomic_max(bad,e,2)       <L 68>
        var_131 = wp::extract(var_97, var_130);
        var_132 = wp::isfinite(var_131);
        var_133 = wp::unot(var_132);
        var_129 = var_133;
        if (!var_129) {
            var_135 = wp::extract(var_97, var_134);
            var_136 = wp::isfinite(var_135);
            var_137 = wp::unot(var_136);
            var_129 = var_129 || var_137;
        }
        if (!var_129) {
            var_139 = wp::extract(var_97, var_138);
            var_140 = wp::isfinite(var_139);
            var_141 = wp::unot(var_140);
            var_129 = var_129 || var_141;
        }
        if (!var_129) {
            var_142 = wp::length(var_128);
            var_144 = (var_142 > var_143);
            var_129 = var_129 || var_144;
        }
        if (var_129) {
            var_146 = wp::atomic_max(var_bad, var_1, var_145);
        }
        // x[i]=newx;v[i]=newv                                                                    <L 69>
        wp::array_store(var_x, var_0, var_97);
        wp::array_store(var_v, var_0, var_128);
    }
}


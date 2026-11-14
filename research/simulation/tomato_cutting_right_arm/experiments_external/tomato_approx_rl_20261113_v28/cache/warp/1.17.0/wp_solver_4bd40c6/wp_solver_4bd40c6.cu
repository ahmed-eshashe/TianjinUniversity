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


// /home/omen/Documents/Codex/experiments/tomato_approx_rl_20261113_v28/src/solver.py:52
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
    // def box_normal(p:wp.vec3,half:wp.vec3):                                                <L 53>
    // q=wp.vec3(wp.abs(p[0]),wp.abs(p[1]),wp.abs(p[2]))-half;outside=wp.vec3(wp.max(q[0],0.),wp.max(q[1],0.),wp.max(q[2],0.));distance=wp.length(outside);normal=wp.vec3(0.)       <L 54>
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
    // if distance>1e-12:                                                                     <L 55>
    var_28 = (var_24 > var_27);
    if (var_28) {
        // normal=wp.vec3(wp.sign(p[0])*outside[0],wp.sign(p[1])*outside[1],wp.sign(p[2])*outside[2])/distance       <L 56>
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
        // axis=int(0)                                                                        <L 58>
        var_50 = wp::int(var_49);
        // if q[1]>q[axis]:axis=1                                                             <L 59>
        var_52 = wp::extract(var_10, var_51);
        var_53 = wp::extract(var_10, var_50);
        var_54 = (var_52 > var_53);
        if (var_54) {
        }
        var_56 = wp::where(var_54, var_55, var_50);
        // if q[2]>q[axis]:axis=2                                                             <L 60>
        var_58 = wp::extract(var_10, var_57);
        var_59 = wp::extract(var_10, var_56);
        var_60 = (var_58 > var_59);
        if (var_60) {
        }
        var_62 = wp::where(var_60, var_61, var_56);
        // normal[axis]=1. if p[axis]>=0. else -1.;distance=q[axis]                           <L 61>
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
    // return normal,distance                                                                 <L 62>
    ret_0 = var_71;
    ret_1 = var_70;
    return;
}


// /home/omen/Documents/Codex/experiments/tomato_approx_rl_20261113_v28/src/solver.py:52
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
        // def bonds(x:wp.array(dtype=wp.vec3),v:wp.array(dtype=wp.vec3),force:wp.array(dtype=wp.vec3),edge:wp.array(dtype=wp.vec2i),rest:wp.array(dtype=float),stiffness:wp.array(dtype=float),mass:wp.array(dtype=float),area:wp.array(dtype=float),alive:wp.array(dtype=int),paid:wp.array(dtype=float),tool:wp.array(dtype=wp.vec3),velocity:wp.array(dtype=wp.vec3),rotation:wp.array(dtype=wp.quat),reaction:wp.array(dtype=wp.vec3),load:wp.array(dtype=float),ledger:wp.array2d(dtype=float),bad:wp.array(dtype=int),h:float,dt:float,n:int,nb:int,half_length:float,cut_enabled:int):       <L 31>
        // idx=wp.tid();e=idx//nb;b=idx%nb                                                        <L 32>
        var_0 = builtin_tid1d();
        var_1 = wp::floordiv(var_0, var_nb);
        var_2 = wp::mod(var_0, var_nb);
        // if bad[e]!=0 or alive[idx]==0:return                                                   <L 33>
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
        // ends=edge[b];i=e*n+ends[0];j=e*n+ends[1];delta=x[j]-x[i];length=wp.length(delta)       <L 34>
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
        // if length<1e-8:wp.atomic_max(bad,e,2);return                                           <L 35>
        var_30 = (var_28 < var_29);
        if (var_30) {
            var_32 = wp::atomic_max(var_bad, var_1, var_31);
            continue;
        }
        // direction=delta/length;strain=length-rest[b];relative=wp.dot(v[j]-v[i],direction);reduced=mass[ends[0]]*mass[ends[1]]/(mass[ends[0]]+mass[ends[1]]);damping=2.*.02*wp.sqrt(stiffness[b]*reduced);f=(stiffness[b]*strain+damping*relative)*direction       <L 36>
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
        // wp.atomic_add(force,i,f);wp.atomic_sub(force,j,f);wp.atomic_add(ledger,e,0,damping*relative*relative*dt)       <L 37>
        var_76 = wp::atomic_add(var_force, var_18, var_75);
        var_77 = wp::atomic_sub(var_force, var_22, var_75);
        var_79 = wp::mul(var_69, var_42);
        var_80 = wp::mul(var_79, var_42);
        var_81 = wp::mul(var_80, var_dt);
        var_82 = wp::atomic_add(var_ledger, var_1, var_78, var_81);
        // if cut_enabled==0:return                                                               <L 38>
        var_84 = (var_cut_enabled == var_83);
        if (var_84) {
            continue;
        }
        // a=wp.quat_rotate_inv(rotation[e],x[i]-tool[e]);c=wp.quat_rotate_inv(rotation[e],x[j]-tool[e])       <L 39>
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
        // if a[0]*c[0]>=0.:return                                                                <L 40>
        var_102 = wp::extract(var_91, var_101);
        var_104 = wp::extract(var_99, var_103);
        var_105 = wp::mul(var_102, var_104);
        var_107 = (var_105 >= var_106);
        if (var_107) {
            continue;
        }
        // t=a[0]/(a[0]-c[0]);p=a+t*(c-a)                                                         <L 41>
        var_109 = wp::extract(var_91, var_108);
        var_111 = wp::extract(var_91, var_110);
        var_113 = wp::extract(var_99, var_112);
        var_114 = wp::sub(var_111, var_113);
        var_115 = wp::div(var_109, var_114);
        var_116 = wp::sub(var_99, var_91);
        var_117 = wp::mul(var_115, var_116);
        var_118 = wp::add(var_91, var_117);
        // if wp.abs(p[2])>half_length or p[1]<-.5*h or p[1]>.03:return                           <L 42>
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
        // midpoint_v=(1.-t)*v[i]+t*v[j];rel=velocity[e]-midpoint_v;local=wp.quat_rotate_inv(rotation[e],rel);advance=wp.max(-local[1],0.)+.25*wp.abs(local[2]);speed=wp.length(rel);budget=80.*area[b];remaining=wp.max(budget-paid[idx],0.)       <L 43>
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
        // if advance<=0. or speed<=1e-8 or remaining<=0.:return                                  <L 44>
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
        // dwork=wp.min(remaining,budget/h*advance*dt);resistance=dwork/(speed*dt)*rel/speed       <L 47>
        var_176 = wp::div(var_162, var_h);
        var_177 = wp::mul(var_176, var_158);
        var_178 = wp::mul(var_177, var_dt);
        var_179 = wp::min(var_168, var_178);
        var_180 = wp::mul(var_159, var_dt);
        var_181 = wp::div(var_179, var_180);
        var_182 = wp::mul(var_181, var_143);
        var_183 = wp::div(var_182, var_159);
        // wp.atomic_add(force,i,(1.-t)*resistance);wp.atomic_add(force,j,t*resistance);wp.atomic_sub(reaction,e,resistance);wp.atomic_add(load,e,wp.length(resistance));wp.atomic_add(ledger,e,1,dwork);wp.atomic_add(ledger,e,2,wp.dot(resistance,velocity[e])*dt);paid[idx]+=dwork       <L 48>
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
        // if paid[idx]>=budget*(1.-1e-5):                                                        <L 49>
        var_202 = wp::address(var_paid, var_0);
        var_205 = wp::sub(var_203, var_204);
        var_206 = wp::mul(var_162, var_205);
        var_208 = wp::load(var_202);
        var_207 = (var_208 >= var_206);
        if (var_207) {
            // alive[idx]=0;wp.atomic_add(ledger,e,3,.5*stiffness[b]*strain*strain)               <L 50>
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
        // def clear_step(x:wp.array(dtype=wp.vec3),force:wp.array(dtype=wp.vec3),mass:wp.array(dtype=float),reaction:wp.array(dtype=wp.vec3),normal_load:wp.array(dtype=float),drive:wp.array(dtype=wp.vec3),tool:wp.array(dtype=wp.vec3),action:wp.array(dtype=wp.vec3),bad:wp.array(dtype=int),dt:float,n:int):       <L 24>
        // i=wp.tid();e=i//n;force[i]=wp.vec3(0.,-9.81*mass[i%n],0.)                              <L 25>
        var_0 = builtin_tid1d();
        var_1 = wp::floordiv(var_0, var_n);
        var_4 = wp::mod(var_0, var_n);
        var_5 = wp::address(var_mass, var_4);
        var_7 = wp::load(var_5);
        var_6 = wp::mul(var_3, var_7);
        var_9 = wp::vec_t<3, wp::float32>(var_2, var_6, var_8);
        wp::array_store(var_force, var_0, var_9);
        // if i%n==0:                                                                             <L 26>
        var_10 = wp::mod(var_0, var_n);
        var_12 = (var_10 == var_11);
        if (var_12) {
            // reaction[e]=wp.vec3(0.);normal_load[e]=0.;drive[e]=action[e]                       <L 27>
            var_14 = wp::vec_t<3, wp::float32>(var_13);
            wp::array_store(var_reaction, var_1, var_14);
            wp::array_store(var_normal_load, var_1, var_15);
            var_16 = wp::address(var_action, var_1);
            var_17 = wp::load(var_16);
            wp::array_store(var_drive, var_1, var_17);
            // if bad[e]==0:tool[e]+=dt*action[e]                                                 <L 28>
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
        // def finish_step(reaction:wp.array(dtype=wp.vec3),load:wp.array(dtype=float),peak:wp.array(dtype=float),bad:wp.array(dtype=int),stop_force:float):       <L 98>
        // e=wp.tid();peak[e]=wp.max(peak[e],load[e])                                             <L 99>
        var_0 = builtin_tid1d();
        var_1 = wp::address(var_peak, var_0);
        var_2 = wp::address(var_load, var_0);
        var_4 = wp::load(var_1);
        var_5 = wp::load(var_2);
        var_3 = wp::max(var_4, var_5);
        wp::array_store(var_peak, var_0, var_3);
        // if load[e]>stop_force or not wp.isfinite(load[e]):wp.atomic_max(bad,e,3)               <L 100>
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



extern "C" __global__ void integrate_8f00c980_cuda_kernel_forward(
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
    wp::array_t<wp::float32> var_penetration_peak,
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
        const wp::int32 var_10 = 0;
        bool var_11;
        wp::quat_t<wp::float32>* var_12;
        wp::vec_t<3, wp::float32>* var_13;
        wp::vec_t<3, wp::float32>* var_14;
        wp::vec_t<3, wp::float32> var_15;
        wp::vec_t<3, wp::float32> var_16;
        wp::vec_t<3, wp::float32> var_17;
        wp::vec_t<3, wp::float32> var_18;
        wp::quat_t<wp::float32> var_19;
        const wp::float32 var_20 = 0.0;
        const wp::float32 var_21 = 0.015;
        const wp::float32 var_22 = 0.0;
        wp::vec_t<3, wp::float32> var_23;
        wp::vec_t<3, wp::float32> var_24;
        const wp::float32 var_25 = 0.0005;
        const wp::float32 var_26 = 0.015;
        wp::vec_t<3, wp::float32> var_27;
        wp::vec_t<3, wp::float32> var_28;
        wp::float32 var_29;
        wp::float32 var_30;
        const wp::float32 var_31 = 0.0;
        wp::float32 var_32;
        wp::float32 var_33;
        const wp::float32 var_34 = 0.0001;
        bool var_35;
        const wp::int32 var_36 = 4;
        wp::int32 var_37;
        wp::int32 var_38;
        wp::float32* var_39;
        wp::float32 var_40;
        wp::float32 var_41;
        wp::vec_t<3, wp::float32>* var_42;
        wp::vec_t<3, wp::float32>* var_43;
        wp::vec_t<3, wp::float32> var_44;
        wp::vec_t<3, wp::float32> var_45;
        wp::vec_t<3, wp::float32> var_46;
        wp::vec_t<3, wp::float32> var_47;
        wp::vec_t<3, wp::float32> var_48;
        wp::vec_t<3, wp::float32>* var_49;
        wp::vec_t<3, wp::float32> var_50;
        wp::vec_t<3, wp::float32> var_51;
        wp::vec_t<3, wp::float32> var_52;
        const wp::int32 var_53 = 0;
        bool var_54;
        wp::quat_t<wp::float32>* var_55;
        wp::vec_t<3, wp::float32>* var_56;
        wp::vec_t<3, wp::float32> var_57;
        wp::vec_t<3, wp::float32> var_58;
        wp::vec_t<3, wp::float32> var_59;
        wp::quat_t<wp::float32> var_60;
        const wp::float32 var_61 = 0.0;
        const wp::float32 var_62 = 0.015;
        const wp::float32 var_63 = 0.0;
        wp::vec_t<3, wp::float32> var_64;
        wp::vec_t<3, wp::float32> var_65;
        const wp::float32 var_66 = 0.0005;
        const wp::float32 var_67 = 0.015;
        wp::vec_t<3, wp::float32> var_68;
        wp::vec_t<3, wp::float32> var_69;
        wp::float32 var_70;
        wp::float32 var_71;
        const wp::float32 var_72 = 0.0;
        wp::float32 var_73;
        wp::float32 var_74;
        const wp::float32 var_75 = 0.0001;
        bool var_76;
        const wp::int32 var_77 = 4;
        wp::int32 var_78;
        const wp::float32 var_79 = 0.0;
        bool var_80;
        wp::quat_t<wp::float32>* var_81;
        wp::vec_t<3, wp::float32> var_82;
        wp::quat_t<wp::float32> var_83;
        wp::vec_t<3, wp::float32> var_84;
        wp::float32 var_85;
        wp::vec_t<3, wp::float32> var_86;
        wp::vec_t<3, wp::float32> var_87;
        wp::vec_t<3, wp::float32> var_88;
        wp::vec_t<3, wp::float32> var_89;
        wp::vec_t<3, wp::float32>* var_90;
        wp::vec_t<3, wp::float32> var_91;
        wp::vec_t<3, wp::float32> var_92;
        wp::float32 var_93;
        wp::vec_t<3, wp::float32> var_94;
        wp::vec_t<3, wp::float32> var_95;
        wp::float32 var_96;
        const wp::float32 var_97 = 0.0;
        wp::vec_t<3, wp::float32> var_98;
        const wp::float32 var_99 = 1e-12;
        bool var_100;
        const wp::float32 var_101 = 0.2;
        wp::float32 var_102;
        wp::float32 var_103;
        wp::float32 var_104;
        wp::float32 var_105;
        wp::float32 var_106;
        wp::vec_t<3, wp::float32> var_107;
        wp::vec_t<3, wp::float32> var_108;
        wp::vec_t<3, wp::float32> var_109;
        wp::vec_t<3, wp::float32> var_110;
        wp::vec_t<3, wp::float32> var_111;
        wp::vec_t<3, wp::float32> var_112;
        wp::vec_t<3, wp::float32> var_113;
        wp::vec_t<3, wp::float32> var_114;
        wp::vec_t<3, wp::float32> var_115;
        wp::float32 var_116;
        wp::float32 var_117;
        wp::float32 var_118;
        const wp::int32 var_119 = 2;
        wp::vec_t<3, wp::float32>* var_120;
        wp::float32 var_121;
        wp::vec_t<3, wp::float32> var_122;
        wp::float32 var_123;
        const wp::int32 var_124 = 4;
        wp::float32 var_125;
        wp::float32 var_126;
        wp::float32 var_127;
        wp::vec_t<3, wp::float32> var_128;
        wp::vec_t<3, wp::float32> var_129;
        wp::vec_t<3, wp::float32> var_130;
        wp::vec_t<3, wp::float32> var_131;
        wp::vec_t<3, wp::float32> var_132;
        wp::float32 var_133;
        wp::float32 var_134;
        wp::vec_t<3, wp::float32> var_135;
        wp::vec_t<3, wp::float32> var_136;
        const wp::int32 var_137 = 1;
        wp::float32 var_138;
        bool var_139;
        const wp::float32 var_140 = 0.5;
        wp::float32 var_141;
        wp::float32 var_142;
        wp::float32 var_143;
        const wp::int32 var_144 = 1;
        const wp::int32 var_145 = 1;
        wp::float32 var_146;
        const wp::float32 var_147 = 0.0;
        bool var_148;
        const wp::int32 var_149 = 1;
        wp::float32 var_150;
        wp::float32 var_151;
        const wp::float32 var_152 = 0.0;
        const wp::int32 var_153 = 1;
        const wp::int32 var_154 = 0;
        wp::float32 var_155;
        const wp::float32 var_156 = 0.0;
        const wp::int32 var_157 = 2;
        wp::float32 var_158;
        wp::vec_t<3, wp::float32> var_159;
        wp::float32 var_160;
        const wp::float32 var_161 = 1e-12;
        bool var_162;
        const wp::float32 var_163 = 0.4;
        wp::float32 var_164;
        wp::float32 var_165;
        wp::vec_t<3, wp::float32> var_166;
        wp::vec_t<3, wp::float32> var_167;
        wp::vec_t<3, wp::float32> var_168;
        wp::vec_t<3, wp::float32> var_169;
        wp::vec_t<3, wp::float32> var_170;
        const wp::int32 var_171 = 6;
        const wp::float32 var_172 = 0.5;
        wp::float32 var_173;
        wp::float32 var_174;
        wp::float32 var_175;
        wp::float32 var_176;
        const wp::float32 var_177 = 0.0;
        wp::float32 var_178;
        wp::float32 var_179;
        wp::vec_t<3, wp::float32> var_180;
        const wp::int32 var_181 = 0;
        bool var_182;
        wp::quat_t<wp::float32>* var_183;
        wp::vec_t<3, wp::float32>* var_184;
        wp::vec_t<3, wp::float32> var_185;
        wp::vec_t<3, wp::float32> var_186;
        wp::vec_t<3, wp::float32> var_187;
        wp::quat_t<wp::float32> var_188;
        const wp::float32 var_189 = 0.0;
        const wp::float32 var_190 = 0.015;
        const wp::float32 var_191 = 0.0;
        wp::vec_t<3, wp::float32> var_192;
        wp::vec_t<3, wp::float32> var_193;
        const wp::float32 var_194 = 0.0005;
        const wp::float32 var_195 = 0.015;
        wp::vec_t<3, wp::float32> var_196;
        wp::vec_t<3, wp::float32> var_197;
        wp::float32 var_198;
        wp::float32 var_199;
        const wp::float32 var_200 = 0.0001;
        bool var_201;
        const wp::int32 var_202 = 4;
        wp::int32 var_203;
        wp::vec_t<3, wp::float32> var_204;
        wp::vec_t<3, wp::float32> var_205;
        wp::float32 var_206;
        bool var_207;
        const wp::int32 var_208 = 0;
        wp::float32 var_209;
        bool var_210;
        bool var_211;
        const wp::int32 var_212 = 1;
        wp::float32 var_213;
        bool var_214;
        bool var_215;
        const wp::int32 var_216 = 2;
        wp::float32 var_217;
        bool var_218;
        bool var_219;
        wp::float32 var_220;
        const wp::float32 var_221 = 10.0;
        bool var_222;
        const wp::int32 var_223 = 2;
        wp::int32 var_224;
        //---------
        // forward
        // def integrate(x:wp.array(dtype=wp.vec3),fixed:wp.array(dtype=int),v:wp.array(dtype=wp.vec3),force:wp.array(dtype=wp.vec3),mass:wp.array(dtype=float),tool:wp.array(dtype=wp.vec3),velocity:wp.array(dtype=wp.vec3),rotation:wp.array(dtype=wp.quat),reaction:wp.array(dtype=wp.vec3),load:wp.array(dtype=float),ledger:wp.array2d(dtype=float),penetration_peak:wp.array(dtype=float),bad:wp.array(dtype=int),dt:float,radius:float,n:int,half_length:float,knife_enabled:int):       <L 65>
        // i=wp.tid();e=i//n                                                                      <L 66>
        var_0 = builtin_tid1d();
        var_1 = wp::floordiv(var_0, var_n);
        // if bad[e]!=0:return                                                                    <L 67>
        var_2 = wp::address(var_bad, var_1);
        var_5 = wp::load(var_2);
        var_4 = (var_5 != var_3);
        if (var_4) {
            continue;
        }
        // if fixed[i]!=0:                                                                        <L 68>
        var_6 = wp::address(var_fixed, var_0);
        var_9 = wp::load(var_6);
        var_8 = (var_9 != var_7);
        if (var_8) {
            // if knife_enabled!=0:                                                               <L 69>
            var_11 = (var_knife_enabled != var_10);
            if (var_11) {
                // p=wp.quat_rotate_inv(rotation[e],x[i]-tool[e])-wp.vec3(0.,.015,0.);normal,distance=box_normal(p,wp.vec3(.0005,.015,half_length));penetration=radius-distance       <L 70>
                var_12 = wp::address(var_rotation, var_1);
                var_13 = wp::address(var_x, var_0);
                var_14 = wp::address(var_tool, var_1);
                var_16 = wp::load(var_13);
                var_17 = wp::load(var_14);
                var_15 = wp::sub(var_16, var_17);
                var_19 = wp::load(var_12);
                var_18 = wp::quat_rotate_inv(var_19, var_15);
                var_23 = wp::vec_t<3, wp::float32>(var_20, var_21, var_22);
                var_24 = wp::sub(var_18, var_23);
                var_27 = wp::vec_t<3, wp::float32>(var_25, var_26, var_half_length);
                box_normal_0(var_24, var_27, var_28, var_29);
                var_30 = wp::sub(var_radius, var_29);
                // wp.atomic_max(penetration_peak,e,wp.max(penetration,0.))                       <L 71>
                var_32 = wp::max(var_30, var_31);
                var_33 = wp::atomic_max(var_penetration_peak, var_1, var_32);
                // if penetration>.0001:wp.atomic_max(bad,e,4)                                    <L 72>
                var_35 = (var_30 > var_34);
                if (var_35) {
                    var_37 = wp::atomic_max(var_bad, var_1, var_36);
                }
            }
            // return                                                                             <L 73>
            continue;
        }
        // m=mass[i%n];newv=v[i]+dt*force[i]/m;newx=x[i]+dt*newv                                  <L 74>
        var_38 = wp::mod(var_0, var_n);
        var_39 = wp::address(var_mass, var_38);
        var_41 = wp::load(var_39);
        var_40 = wp::copy(var_41);
        var_42 = wp::address(var_v, var_0);
        var_43 = wp::address(var_force, var_0);
        var_45 = wp::load(var_43);
        var_44 = wp::mul(var_dt, var_45);
        var_46 = wp::div(var_44, var_40);
        var_48 = wp::load(var_42);
        var_47 = wp::add(var_48, var_46);
        var_49 = wp::address(var_x, var_0);
        var_50 = wp::mul(var_dt, var_47);
        var_52 = wp::load(var_49);
        var_51 = wp::add(var_52, var_50);
        // if knife_enabled!=0:                                                                   <L 75>
        var_54 = (var_knife_enabled != var_53);
        if (var_54) {
            // p=wp.quat_rotate_inv(rotation[e],newx-tool[e])-wp.vec3(0.,.015,0.);normal,distance=box_normal(p,wp.vec3(.0005,.015,half_length));penetration=radius-distance       <L 76>
            var_55 = wp::address(var_rotation, var_1);
            var_56 = wp::address(var_tool, var_1);
            var_58 = wp::load(var_56);
            var_57 = wp::sub(var_51, var_58);
            var_60 = wp::load(var_55);
            var_59 = wp::quat_rotate_inv(var_60, var_57);
            var_64 = wp::vec_t<3, wp::float32>(var_61, var_62, var_63);
            var_65 = wp::sub(var_59, var_64);
            var_68 = wp::vec_t<3, wp::float32>(var_66, var_67, var_half_length);
            box_normal_0(var_65, var_68, var_69, var_70);
            var_71 = wp::sub(var_radius, var_70);
            // wp.atomic_max(penetration_peak,e,wp.max(penetration,0.))                           <L 77>
            var_73 = wp::max(var_71, var_72);
            var_74 = wp::atomic_max(var_penetration_peak, var_1, var_73);
            // if penetration>.0001:wp.atomic_max(bad,e,4);return                                 <L 78>
            var_76 = (var_71 > var_75);
            if (var_76) {
                var_78 = wp::atomic_max(var_bad, var_1, var_77);
                continue;
            }
            // if penetration>0.:                                                                 <L 79>
            var_80 = (var_71 > var_79);
            if (var_80) {
                // normal=wp.quat_rotate(rotation[e],normal);correction=penetration*normal;impulse=m/dt*correction;newx+=correction;newv+=impulse/m       <L 80>
                var_81 = wp::address(var_rotation, var_1);
                var_83 = wp::load(var_81);
                var_82 = wp::quat_rotate(var_83, var_69);
                var_84 = wp::mul(var_71, var_82);
                var_85 = wp::div(var_40, var_dt);
                var_86 = wp::mul(var_85, var_84);
                var_87 = wp::add(var_51, var_84);
                var_88 = wp::div(var_86, var_40);
                var_89 = wp::add(var_47, var_88);
                // rel=newv-velocity[e];tangent=rel-wp.dot(rel,normal)*normal;length=wp.length(tangent);friction=wp.vec3(0.)       <L 81>
                var_90 = wp::address(var_velocity, var_1);
                var_92 = wp::load(var_90);
                var_91 = wp::sub(var_89, var_92);
                var_93 = wp::dot(var_91, var_82);
                var_94 = wp::mul(var_93, var_82);
                var_95 = wp::sub(var_91, var_94);
                var_96 = wp::length(var_95);
                var_98 = wp::vec_t<3, wp::float32>(var_97);
                // if length>1e-12:friction=-wp.min(.2*wp.length(impulse),m*length)*tangent/length;newv+=friction/m       <L 82>
                var_100 = (var_96 > var_99);
                if (var_100) {
                    var_102 = wp::length(var_86);
                    var_103 = wp::mul(var_101, var_102);
                    var_104 = wp::mul(var_40, var_96);
                    var_105 = wp::min(var_103, var_104);
                    var_106 = wp::neg(var_105);
                    var_107 = wp::mul(var_106, var_95);
                    var_108 = wp::div(var_107, var_96);
                    var_109 = wp::div(var_108, var_40);
                    var_110 = wp::add(var_89, var_109);
                }
                var_111 = wp::where(var_100, var_110, var_89);
                var_112 = wp::where(var_100, var_108, var_98);
                // total=impulse+friction;wp.atomic_sub(reaction,e,total/dt);wp.atomic_add(load,e,wp.length(total)/dt);wp.atomic_add(ledger,e,2,wp.dot(total,velocity[e]));wp.atomic_add(ledger,e,4,-wp.dot(friction,rel))       <L 83>
                var_113 = wp::add(var_86, var_112);
                var_114 = wp::div(var_113, var_dt);
                var_115 = wp::atomic_sub(var_reaction, var_1, var_114);
                var_116 = wp::length(var_113);
                var_117 = wp::div(var_116, var_dt);
                var_118 = wp::atomic_add(var_load, var_1, var_117);
                var_120 = wp::address(var_velocity, var_1);
                var_122 = wp::load(var_120);
                var_121 = wp::dot(var_113, var_122);
                var_123 = wp::atomic_add(var_ledger, var_1, var_119, var_121);
                var_125 = wp::dot(var_112, var_91);
                var_126 = wp::neg(var_125);
                var_127 = wp::atomic_add(var_ledger, var_1, var_124, var_126);
            }
            var_128 = wp::where(var_80, var_82, var_69);
            var_129 = wp::where(var_80, var_111, var_47);
            var_130 = wp::where(var_80, var_87, var_51);
        }
        var_131 = wp::where(var_54, var_65, var_24);
        var_132 = wp::where(var_54, var_128, var_28);
        var_133 = wp::where(var_54, var_70, var_29);
        var_134 = wp::where(var_54, var_71, var_30);
        var_135 = wp::where(var_54, var_129, var_47);
        var_136 = wp::where(var_54, var_130, var_51);
        // if newx[1]<radius:                                                                     <L 84>
        var_138 = wp::extract(var_136, var_137);
        var_139 = (var_138 < var_radius);
        if (var_139) {
            // old_ke=.5*m*wp.dot(newv,newv)                                                      <L 85>
            var_141 = wp::mul(var_140, var_40);
            var_142 = wp::dot(var_135, var_135);
            var_143 = wp::mul(var_141, var_142);
            // newx[1]=radius                                                                     <L 86>
            wp::assign_inplace(var_136, var_144, var_radius);
            // if newv[1]<0.:                                                                     <L 87>
            var_146 = wp::extract(var_135, var_145);
            var_148 = (var_146 < var_147);
            if (var_148) {
                // normal_speed=-newv[1];newv[1]=0.;horizontal=wp.vec3(newv[0],0.,newv[2]);speed=wp.length(horizontal)       <L 88>
                var_150 = wp::extract(var_135, var_149);
                var_151 = wp::neg(var_150);
                wp::assign_inplace(var_135, var_153, var_152);
                var_155 = wp::extract(var_135, var_154);
                var_158 = wp::extract(var_135, var_157);
                var_159 = wp::vec_t<3, wp::float32>(var_155, var_156, var_158);
                var_160 = wp::length(var_159);
                // if speed>1e-12:newv-=wp.min(.4*normal_speed,speed)*horizontal/speed            <L 89>
                var_162 = (var_160 > var_161);
                if (var_162) {
                    var_164 = wp::mul(var_163, var_151);
                    var_165 = wp::min(var_164, var_160);
                    var_166 = wp::mul(var_165, var_159);
                    var_167 = wp::div(var_166, var_160);
                    var_168 = wp::sub(var_135, var_167);
                }
                var_169 = wp::where(var_162, var_168, var_135);
            }
            var_170 = wp::where(var_148, var_169, var_135);
            // wp.atomic_add(ledger,e,6,wp.max(old_ke-.5*m*wp.dot(newv,newv),0.))                 <L 90>
            var_173 = wp::mul(var_172, var_40);
            var_174 = wp::dot(var_170, var_170);
            var_175 = wp::mul(var_173, var_174);
            var_176 = wp::sub(var_143, var_175);
            var_178 = wp::max(var_176, var_177);
            var_179 = wp::atomic_add(var_ledger, var_1, var_171, var_178);
        }
        var_180 = wp::where(var_139, var_170, var_135);
        // if knife_enabled!=0:                                                                   <L 91>
        var_182 = (var_knife_enabled != var_181);
        if (var_182) {
            // p=wp.quat_rotate_inv(rotation[e],newx-tool[e])-wp.vec3(0.,.015,0.);normal,distance=box_normal(p,wp.vec3(.0005,.015,half_length))       <L 92>
            var_183 = wp::address(var_rotation, var_1);
            var_184 = wp::address(var_tool, var_1);
            var_186 = wp::load(var_184);
            var_185 = wp::sub(var_136, var_186);
            var_188 = wp::load(var_183);
            var_187 = wp::quat_rotate_inv(var_188, var_185);
            var_192 = wp::vec_t<3, wp::float32>(var_189, var_190, var_191);
            var_193 = wp::sub(var_187, var_192);
            var_196 = wp::vec_t<3, wp::float32>(var_194, var_195, var_half_length);
            box_normal_0(var_193, var_196, var_197, var_198);
            // if radius-distance>.0001:wp.atomic_max(bad,e,4)                                    <L 93>
            var_199 = wp::sub(var_radius, var_198);
            var_201 = (var_199 > var_200);
            if (var_201) {
                var_203 = wp::atomic_max(var_bad, var_1, var_202);
            }
        }
        var_204 = wp::where(var_182, var_193, var_131);
        var_205 = wp::where(var_182, var_197, var_132);
        var_206 = wp::where(var_182, var_198, var_133);
        // if not wp.isfinite(newx[0]) or not wp.isfinite(newx[1]) or not wp.isfinite(newx[2]) or wp.length(newv)>10.:wp.atomic_max(bad,e,2)       <L 94>
        var_209 = wp::extract(var_136, var_208);
        var_210 = wp::isfinite(var_209);
        var_211 = wp::unot(var_210);
        var_207 = var_211;
        if (!var_207) {
            var_213 = wp::extract(var_136, var_212);
            var_214 = wp::isfinite(var_213);
            var_215 = wp::unot(var_214);
            var_207 = var_207 || var_215;
        }
        if (!var_207) {
            var_217 = wp::extract(var_136, var_216);
            var_218 = wp::isfinite(var_217);
            var_219 = wp::unot(var_218);
            var_207 = var_207 || var_219;
        }
        if (!var_207) {
            var_220 = wp::length(var_180);
            var_222 = (var_220 > var_221);
            var_207 = var_207 || var_222;
        }
        if (var_207) {
            var_224 = wp::atomic_max(var_bad, var_1, var_223);
        }
        // x[i]=newx;v[i]=newv                                                                    <L 95>
        wp::array_store(var_x, var_0, var_136);
        wp::array_store(var_v, var_0, var_180);
    }
}



extern "C" __global__ void particle_contacts_d18fc9fc_cuda_kernel_forward(
    wp::launch_bounds_t<1> dim,
    wp::uint64 var_grid,
    wp::array_t<wp::vec_t<3, wp::float32>> var_x,
    wp::array_t<wp::vec_t<3, wp::float32>> var_v,
    wp::array_t<wp::vec_t<3, wp::float32>> var_force,
    wp::array_t<wp::float32> var_mass,
    wp::array_t<wp::float32> var_ledger,
    wp::array_t<wp::int32> var_bad,
    wp::float32 var_radius,
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
        wp::int32* var_2;
        const wp::int32 var_3 = 0;
        bool var_4;
        wp::int32 var_5;
        wp::vec_t<3, wp::float32>* var_6;
        const wp::float32 var_7 = 2.0;
        wp::float32 var_8;
        wp::hash_grid_query_f var_9;
        wp::vec_t<3, wp::float32> var_10;
        wp::int32 var_11;
        bool var_12;
        bool var_13;
        wp::int32 var_14;
        bool var_15;
        wp::vec_t<3, wp::float32>* var_16;
        wp::vec_t<3, wp::float32>* var_17;
        wp::vec_t<3, wp::float32> var_18;
        wp::vec_t<3, wp::float32> var_19;
        wp::vec_t<3, wp::float32> var_20;
        wp::float32 var_21;
        bool var_22;
        const wp::float32 var_23 = 2.0;
        wp::float32 var_24;
        bool var_25;
        const wp::float32 var_26 = 1e-08;
        bool var_27;
        wp::vec_t<3, wp::float32> var_28;
        wp::vec_t<3, wp::float32>* var_29;
        wp::vec_t<3, wp::float32>* var_30;
        wp::vec_t<3, wp::float32> var_31;
        wp::vec_t<3, wp::float32> var_32;
        wp::vec_t<3, wp::float32> var_33;
        wp::float32 var_34;
        wp::int32 var_35;
        wp::float32* var_36;
        wp::int32 var_37;
        wp::float32* var_38;
        wp::float32 var_39;
        wp::float32 var_40;
        wp::float32 var_41;
        wp::int32 var_42;
        wp::float32* var_43;
        wp::int32 var_44;
        wp::float32* var_45;
        wp::float32 var_46;
        wp::float32 var_47;
        wp::float32 var_48;
        wp::float32 var_49;
        const wp::float32 var_50 = 0.4;
        const wp::float32 var_51 = 1000.0;
        wp::float32 var_52;
        wp::float32 var_53;
        wp::float32 var_54;
        const wp::float32 var_55 = 1000.0;
        const wp::float32 var_56 = 2.0;
        wp::float32 var_57;
        wp::float32 var_58;
        wp::float32 var_59;
        wp::float32 var_60;
        wp::float32 var_61;
        const wp::float32 var_62 = 0.0;
        wp::float32 var_63;
        wp::vec_t<3, wp::float32> var_64;
        wp::vec_t<3, wp::float32> var_65;
        wp::float32 var_66;
        const wp::float32 var_67 = 0.0;
        wp::vec_t<3, wp::float32> var_68;
        const wp::float32 var_69 = 1e-10;
        bool var_70;
        const wp::float32 var_71 = 0.2;
        wp::float32 var_72;
        wp::float32 var_73;
        wp::float32 var_74;
        wp::float32 var_75;
        wp::float32 var_76;
        wp::vec_t<3, wp::float32> var_77;
        wp::vec_t<3, wp::float32> var_78;
        wp::vec_t<3, wp::float32> var_79;
        wp::vec_t<3, wp::float32> var_80;
        wp::vec_t<3, wp::float32> var_81;
        wp::vec_t<3, wp::float32> var_82;
        wp::vec_t<3, wp::float32> var_83;
        const wp::int32 var_84 = 5;
        wp::float32 var_85;
        wp::float32 var_86;
        wp::float32 var_87;
        wp::float32 var_88;
        const wp::float32 var_89 = 0.0;
        wp::float32 var_90;
        wp::float32 var_91;
        wp::float32 var_92;
        //---------
        // forward
        // def particle_contacts(grid:wp.uint64,x:wp.array(dtype=wp.vec3),v:wp.array(dtype=wp.vec3),force:wp.array(dtype=wp.vec3),mass:wp.array(dtype=float),ledger:wp.array2d(dtype=float),bad:wp.array(dtype=int),radius:float,dt:float,n:int):       <L 10>
        // i=wp.tid();e=i//n                                                                      <L 11>
        var_0 = builtin_tid1d();
        var_1 = wp::floordiv(var_0, var_n);
        // if bad[e]!=0:return                                                                    <L 12>
        var_2 = wp::address(var_bad, var_1);
        var_5 = wp::load(var_2);
        var_4 = (var_5 != var_3);
        if (var_4) {
            continue;
        }
        // neighbors=wp.hash_grid_query(grid,x[i],2.*radius)                                      <L 13>
        var_6 = wp::address(var_x, var_0);
        var_8 = wp::mul(var_7, var_radius);
        var_10 = wp::load(var_6);
        var_9 = wp::hash_grid_query(var_grid, var_10, var_8);
        // for j in neighbors:                                                                    <L 14>
        start_for_1:;
            if (iter_cmp(var_9) == 0) goto end_for_1;
            var_11 = wp::iter_next(var_9);
            // if j>i and j//n==e:                                                                <L 15>
            var_13 = (var_11 > var_0);
            var_12 = var_13;
            if (var_12) {
                var_14 = wp::floordiv(var_11, var_n);
                var_15 = (var_14 == var_1);
                var_12 = var_12 && var_15;
            }
            if (var_12) {
                // delta=x[j]-x[i];distance=wp.length(delta)                                      <L 16>
                var_16 = wp::address(var_x, var_11);
                var_17 = wp::address(var_x, var_0);
                var_19 = wp::load(var_16);
                var_20 = wp::load(var_17);
                var_18 = wp::sub(var_19, var_20);
                var_21 = wp::length(var_18);
                // if distance<2.*radius and distance>1e-8:                                       <L 17>
                var_24 = wp::mul(var_23, var_radius);
                var_25 = (var_21 < var_24);
                var_22 = var_25;
                if (var_22) {
                    var_27 = (var_21 > var_26);
                    var_22 = var_22 && var_27;
                }
                if (var_22) {
                    // normal=delta/distance;rel=v[j]-v[i];speed=wp.dot(rel,normal);reduced=mass[i%n]*mass[j%n]/(mass[i%n]+mass[j%n]);damping=.4*wp.sqrt(1000.*reduced)       <L 18>
                    var_28 = wp::div(var_18, var_21);
                    var_29 = wp::address(var_v, var_11);
                    var_30 = wp::address(var_v, var_0);
                    var_32 = wp::load(var_29);
                    var_33 = wp::load(var_30);
                    var_31 = wp::sub(var_32, var_33);
                    var_34 = wp::dot(var_31, var_28);
                    var_35 = wp::mod(var_0, var_n);
                    var_36 = wp::address(var_mass, var_35);
                    var_37 = wp::mod(var_11, var_n);
                    var_38 = wp::address(var_mass, var_37);
                    var_40 = wp::load(var_36);
                    var_41 = wp::load(var_38);
                    var_39 = wp::mul(var_40, var_41);
                    var_42 = wp::mod(var_0, var_n);
                    var_43 = wp::address(var_mass, var_42);
                    var_44 = wp::mod(var_11, var_n);
                    var_45 = wp::address(var_mass, var_44);
                    var_47 = wp::load(var_43);
                    var_48 = wp::load(var_45);
                    var_46 = wp::add(var_47, var_48);
                    var_49 = wp::div(var_39, var_46);
                    var_52 = wp::mul(var_51, var_49);
                    var_53 = wp::sqrt(var_52);
                    var_54 = wp::mul(var_50, var_53);
                    // magnitude=wp.max(1000.*(2.*radius-distance)-damping*speed,0.);tangent=rel-speed*normal;slip=wp.length(tangent);friction=wp.vec3(0.)       <L 19>
                    var_57 = wp::mul(var_56, var_radius);
                    var_58 = wp::sub(var_57, var_21);
                    var_59 = wp::mul(var_55, var_58);
                    var_60 = wp::mul(var_54, var_34);
                    var_61 = wp::sub(var_59, var_60);
                    var_63 = wp::max(var_61, var_62);
                    var_64 = wp::mul(var_34, var_28);
                    var_65 = wp::sub(var_31, var_64);
                    var_66 = wp::length(var_65);
                    var_68 = wp::vec_t<3, wp::float32>(var_67);
                    // if slip>1e-10:friction=-wp.min(.2*magnitude,reduced*slip/dt)*tangent/slip       <L 20>
                    var_70 = (var_66 > var_69);
                    if (var_70) {
                        var_72 = wp::mul(var_71, var_63);
                        var_73 = wp::mul(var_49, var_66);
                        var_74 = wp::div(var_73, var_dt);
                        var_75 = wp::min(var_72, var_74);
                        var_76 = wp::neg(var_75);
                        var_77 = wp::mul(var_76, var_65);
                        var_78 = wp::div(var_77, var_66);
                    }
                    var_79 = wp::where(var_70, var_78, var_68);
                    // f=magnitude*normal+friction;wp.atomic_sub(force,i,f);wp.atomic_add(force,j,f);wp.atomic_add(ledger,e,5,wp.max(damping*speed*speed-wp.dot(friction,rel),0.)*dt)       <L 21>
                    var_80 = wp::mul(var_63, var_28);
                    var_81 = wp::add(var_80, var_79);
                    var_82 = wp::atomic_sub(var_force, var_0, var_81);
                    var_83 = wp::atomic_add(var_force, var_11, var_81);
                    var_85 = wp::mul(var_54, var_34);
                    var_86 = wp::mul(var_85, var_34);
                    var_87 = wp::dot(var_79, var_31);
                    var_88 = wp::sub(var_86, var_87);
                    var_90 = wp::max(var_88, var_89);
                    var_91 = wp::mul(var_90, var_dt);
                    var_92 = wp::atomic_add(var_ledger, var_1, var_84, var_91);
                }
            }
            goto start_for_1;
        end_for_1:;
    }
}


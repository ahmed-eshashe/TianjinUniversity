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


// /home/omen/Documents/Codex/experiments/tomato_bounded_basis_20261113_v27/src/convex_guard_gpu.py:13
static CUDA_CALLABLE wp::float64 plane_value_0(
    wp::vec_t<3, wp::float64> var_p,
    wp::vec_t<4, wp::float64> var_plane)
{
    //---------
    // primal vars
    const wp::int32 var_0 = 0;
    wp::float64 var_1;
    const wp::int32 var_2 = 0;
    wp::float64 var_3;
    wp::float64 var_4;
    const wp::int32 var_5 = 1;
    wp::float64 var_6;
    const wp::int32 var_7 = 1;
    wp::float64 var_8;
    wp::float64 var_9;
    wp::float64 var_10;
    const wp::int32 var_11 = 2;
    wp::float64 var_12;
    const wp::int32 var_13 = 2;
    wp::float64 var_14;
    wp::float64 var_15;
    wp::float64 var_16;
    const wp::int32 var_17 = 3;
    wp::float64 var_18;
    wp::float64 var_19;
    //---------
    // forward
    // def plane_value(p:wp.vec3d,plane:wp.vec4d):                                            <L 14>
    // return p[0]*plane[0]+p[1]*plane[1]+p[2]*plane[2]+plane[3]                              <L 15>
    var_1 = wp::extract(var_p, var_0);
    var_3 = wp::extract(var_plane, var_2);
    var_4 = wp::mul(var_1, var_3);
    var_6 = wp::extract(var_p, var_5);
    var_8 = wp::extract(var_plane, var_7);
    var_9 = wp::mul(var_6, var_8);
    var_10 = wp::add(var_4, var_9);
    var_12 = wp::extract(var_p, var_11);
    var_14 = wp::extract(var_plane, var_13);
    var_15 = wp::mul(var_12, var_14);
    var_16 = wp::add(var_10, var_15);
    var_18 = wp::extract(var_plane, var_17);
    var_19 = wp::add(var_16, var_18);
    return var_19;
}


// /home/omen/Documents/Codex/experiments/tomato_bounded_basis_20261113_v27/src/convex_guard_gpu.py:17
static CUDA_CALLABLE bool inside_0(
    wp::vec_t<3, wp::float64> var_p,
    wp::mat_t<4, 4, wp::float64> var_planes)
{
    //---------
    // primal vars
    const bool var_0 = true;
    const wp::int32 var_1 = 0;
    wp::vec_t<4, wp::float64> var_2;
    wp::float64 var_3;
    wp::float64 var_4;
    bool var_5;
    const bool var_6 = false;
    bool var_7;
    const wp::int32 var_8 = 1;
    wp::vec_t<4, wp::float64> var_9;
    wp::float64 var_10;
    wp::float64 var_11;
    bool var_12;
    const bool var_13 = false;
    bool var_14;
    const wp::int32 var_15 = 2;
    wp::vec_t<4, wp::float64> var_16;
    wp::float64 var_17;
    wp::float64 var_18;
    bool var_19;
    const bool var_20 = false;
    bool var_21;
    const wp::int32 var_22 = 3;
    wp::vec_t<4, wp::float64> var_23;
    wp::float64 var_24;
    wp::float64 var_25;
    bool var_26;
    const bool var_27 = false;
    bool var_28;
    //---------
    // forward
    // def inside(p:wp.vec3d,planes:wp.mat44d):                                               <L 18>
    // good=True                                                                              <L 19>
    // for i in range(4):                                                                     <L 20>
    // if plane_value(p,planes[i])>wp.float64(1e-12):good=False                               <L 21>
    var_2 = wp::extract(var_planes, var_1);
    var_3 = plane_value_0(var_p, var_2);
    var_4 = 1e-12;
    var_5 = (var_3 > var_4);
    if (var_5) {
    }
    var_7 = wp::where(var_5, var_6, var_0);
    var_9 = wp::extract(var_planes, var_8);
    var_10 = plane_value_0(var_p, var_9);
    var_11 = 1e-12;
    var_12 = (var_10 > var_11);
    if (var_12) {
    }
    var_14 = wp::where(var_12, var_13, var_7);
    var_16 = wp::extract(var_planes, var_15);
    var_17 = plane_value_0(var_p, var_16);
    var_18 = 1e-12;
    var_19 = (var_17 > var_18);
    if (var_19) {
    }
    var_21 = wp::where(var_19, var_20, var_14);
    var_23 = wp::extract(var_planes, var_22);
    var_24 = plane_value_0(var_p, var_23);
    var_25 = 1e-12;
    var_26 = (var_24 > var_25);
    if (var_26) {
    }
    var_28 = wp::where(var_26, var_27, var_21);
    // return good                                                                            <L 22>
    return var_28;
}


// /home/omen/Documents/Codex/experiments/tomato_bounded_basis_20261113_v27/src/contact_gpu_precise.py:12
static CUDA_CALLABLE wp::vec_t<3, wp::float64> closest_0(
    wp::vec_t<3, wp::float64> var_p,
    wp::vec_t<3, wp::float64> var_a,
    wp::vec_t<3, wp::float64> var_b,
    wp::vec_t<3, wp::float64> var_c)
{
    //---------
    // primal vars
    wp::vec_t<3, wp::float64> var_0;
    wp::vec_t<3, wp::float64> var_1;
    wp::vec_t<3, wp::float64> var_2;
    wp::float64 var_3;
    wp::float64 var_4;
    wp::float64 var_5;
    wp::float64 var_6;
    wp::float64 var_7;
    wp::float64 var_8;
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
    wp::vec_t<3, wp::float64> var_21;
    wp::vec_t<3, wp::float64> var_22;
    wp::vec_t<3, wp::float64> var_23;
    wp::vec_t<3, wp::float64> var_24;
    wp::vec_t<3, wp::float64> var_25;
    wp::vec_t<3, wp::float64> var_26;
    wp::float64 var_27;
    bool var_28;
    wp::float64 var_29;
    bool var_30;
    wp::float64 var_31;
    bool var_32;
    wp::float64 var_33;
    wp::float64 var_34;
    bool var_35;
    wp::float64 var_36;
    wp::float64 var_37;
    const wp::int32 var_38 = 0;
    wp::vec_t<3, wp::float64> var_39;
    wp::vec_t<3, wp::float64> var_40;
    const wp::int32 var_41 = 1;
    bool var_42;
    wp::vec_t<3, wp::float64> var_43;
    wp::vec_t<3, wp::float64> var_44;
    const wp::int32 var_45 = 2;
    bool var_46;
    wp::vec_t<3, wp::float64> var_47;
    wp::vec_t<3, wp::float64> var_48;
    wp::vec_t<3, wp::float64> var_49;
    wp::vec_t<3, wp::float64> var_50;
    wp::vec_t<3, wp::float64> var_51;
    wp::vec_t<3, wp::float64> var_52;
    wp::vec_t<3, wp::float64> var_53;
    wp::vec_t<3, wp::float64> var_54;
    wp::float64 var_55;
    wp::float64 var_56;
    wp::float64 var_57;
    wp::float64 var_58;
    wp::float64 var_59;
    wp::float64 var_60;
    wp::vec_t<3, wp::float64> var_61;
    wp::vec_t<3, wp::float64> var_62;
    wp::vec_t<3, wp::float64> var_63;
    wp::vec_t<3, wp::float64> var_64;
    wp::float64 var_65;
    bool var_66;
    wp::float64 var_67;
    wp::vec_t<3, wp::float64> var_68;
    wp::vec_t<3, wp::float64> var_69;
    wp::float64 var_70;
    const wp::int32 var_71 = 1;
    wp::vec_t<3, wp::float64> var_72;
    wp::vec_t<3, wp::float64> var_73;
    const wp::int32 var_74 = 1;
    bool var_75;
    wp::vec_t<3, wp::float64> var_76;
    wp::vec_t<3, wp::float64> var_77;
    const wp::int32 var_78 = 2;
    bool var_79;
    wp::vec_t<3, wp::float64> var_80;
    wp::vec_t<3, wp::float64> var_81;
    wp::vec_t<3, wp::float64> var_82;
    wp::vec_t<3, wp::float64> var_83;
    wp::vec_t<3, wp::float64> var_84;
    wp::vec_t<3, wp::float64> var_85;
    wp::vec_t<3, wp::float64> var_86;
    wp::vec_t<3, wp::float64> var_87;
    wp::float64 var_88;
    wp::float64 var_89;
    wp::float64 var_90;
    wp::float64 var_91;
    wp::float64 var_92;
    wp::float64 var_93;
    wp::vec_t<3, wp::float64> var_94;
    wp::vec_t<3, wp::float64> var_95;
    wp::vec_t<3, wp::float64> var_96;
    wp::vec_t<3, wp::float64> var_97;
    wp::float64 var_98;
    bool var_99;
    wp::float64 var_100;
    wp::vec_t<3, wp::float64> var_101;
    wp::vec_t<3, wp::float64> var_102;
    wp::float64 var_103;
    const wp::int32 var_104 = 2;
    wp::vec_t<3, wp::float64> var_105;
    wp::vec_t<3, wp::float64> var_106;
    const wp::int32 var_107 = 1;
    bool var_108;
    wp::vec_t<3, wp::float64> var_109;
    wp::vec_t<3, wp::float64> var_110;
    const wp::int32 var_111 = 2;
    bool var_112;
    wp::vec_t<3, wp::float64> var_113;
    wp::vec_t<3, wp::float64> var_114;
    wp::vec_t<3, wp::float64> var_115;
    wp::vec_t<3, wp::float64> var_116;
    wp::vec_t<3, wp::float64> var_117;
    wp::vec_t<3, wp::float64> var_118;
    wp::vec_t<3, wp::float64> var_119;
    wp::vec_t<3, wp::float64> var_120;
    wp::float64 var_121;
    wp::float64 var_122;
    wp::float64 var_123;
    wp::float64 var_124;
    wp::float64 var_125;
    wp::float64 var_126;
    wp::vec_t<3, wp::float64> var_127;
    wp::vec_t<3, wp::float64> var_128;
    wp::vec_t<3, wp::float64> var_129;
    wp::vec_t<3, wp::float64> var_130;
    wp::float64 var_131;
    bool var_132;
    wp::float64 var_133;
    wp::vec_t<3, wp::float64> var_134;
    wp::vec_t<3, wp::float64> var_135;
    wp::float64 var_136;
    //---------
    // forward
    // def closest(p:wp.vec3d,a:wp.vec3d,b:wp.vec3d,c:wp.vec3d):                              <L 13>
    // e=b-a;f=c-a;r=p-a;aa=wp.dot(e,e);ab=wp.dot(e,f);bb=wp.dot(f,f);den=aa*bb-ab*ab;u=(wp.dot(r,e)*bb-wp.dot(r,f)*ab)/den;v=(wp.dot(r,f)*aa-wp.dot(r,e)*ab)/den       <L 14>
    var_0 = wp::sub(var_b, var_a);
    var_1 = wp::sub(var_c, var_a);
    var_2 = wp::sub(var_p, var_a);
    var_3 = wp::dot(var_0, var_0);
    var_4 = wp::dot(var_0, var_1);
    var_5 = wp::dot(var_1, var_1);
    var_6 = wp::mul(var_3, var_5);
    var_7 = wp::mul(var_4, var_4);
    var_8 = wp::sub(var_6, var_7);
    var_9 = wp::dot(var_2, var_0);
    var_10 = wp::mul(var_9, var_5);
    var_11 = wp::dot(var_2, var_1);
    var_12 = wp::mul(var_11, var_4);
    var_13 = wp::sub(var_10, var_12);
    var_14 = wp::div(var_13, var_8);
    var_15 = wp::dot(var_2, var_1);
    var_16 = wp::mul(var_15, var_3);
    var_17 = wp::dot(var_2, var_0);
    var_18 = wp::mul(var_17, var_4);
    var_19 = wp::sub(var_16, var_18);
    var_20 = wp::div(var_19, var_8);
    // q=a+u*e+v*f;best=wp.dot(p-q,p-q)                                                       <L 15>
    var_21 = wp::mul(var_14, var_0);
    var_22 = wp::add(var_a, var_21);
    var_23 = wp::mul(var_20, var_1);
    var_24 = wp::add(var_22, var_23);
    var_25 = wp::sub(var_p, var_24);
    var_26 = wp::sub(var_p, var_24);
    var_27 = wp::dot(var_25, var_26);
    // if u<wp.float64(0.) or v<wp.float64(0.) or u+v>wp.float64(1.):best=wp.float64(1.e20)       <L 16>
    var_29 = 0.0;
    var_30 = (var_14 < var_29);
    var_28 = var_30;
    if (!var_28) {
        var_31 = 0.0;
        var_32 = (var_20 < var_31);
        var_28 = var_28 || var_32;
    }
    if (!var_28) {
        var_33 = wp::add(var_14, var_20);
        var_34 = 1.0;
        var_35 = (var_33 > var_34);
        var_28 = var_28 || var_35;
    }
    if (var_28) {
        var_36 = 1e+20;
    }
    var_37 = wp::where(var_28, var_36, var_27);
    // for k in range(3):                                                                     <L 17>
    // x=a;y=b                                                                                <L 18>
    var_39 = wp::copy(var_a);
    var_40 = wp::copy(var_b);
    // if k==1:x=b;y=c                                                                        <L 19>
    var_42 = (var_38 == var_41);
    if (var_42) {
        var_43 = wp::copy(var_b);
        var_44 = wp::copy(var_c);
    }
    if (!var_42) {
        // elif k==2:x=c;y=a                                                                  <L 20>
        var_46 = (var_38 == var_45);
        if (var_46) {
            var_47 = wp::copy(var_c);
            var_48 = wp::copy(var_a);
        }
        var_49 = wp::where(var_46, var_47, var_39);
        var_50 = wp::where(var_46, var_48, var_40);
    }
    var_51 = wp::where(var_42, var_43, var_49);
    var_52 = wp::where(var_42, var_44, var_50);
    // edge=y-x;t=wp.clamp(wp.dot(p-x,edge)/wp.dot(edge,edge),wp.float64(0.),wp.float64(1.));z=x+t*edge;dd=wp.dot(p-z,p-z)       <L 21>
    var_53 = wp::sub(var_52, var_51);
    var_54 = wp::sub(var_p, var_51);
    var_55 = wp::dot(var_54, var_53);
    var_56 = wp::dot(var_53, var_53);
    var_57 = wp::div(var_55, var_56);
    var_58 = 0.0;
    var_59 = 1.0;
    var_60 = wp::clamp(var_57, var_58, var_59);
    var_61 = wp::mul(var_60, var_53);
    var_62 = wp::add(var_51, var_61);
    var_63 = wp::sub(var_p, var_62);
    var_64 = wp::sub(var_p, var_62);
    var_65 = wp::dot(var_63, var_64);
    // if dd<best:best=dd;q=z                                                                 <L 22>
    var_66 = (var_65 < var_37);
    if (var_66) {
        var_67 = wp::copy(var_65);
        var_68 = wp::copy(var_62);
    }
    var_69 = wp::where(var_66, var_68, var_24);
    var_70 = wp::where(var_66, var_67, var_37);
    // x=a;y=b                                                                                <L 18>
    var_72 = wp::copy(var_a);
    var_73 = wp::copy(var_b);
    // if k==1:x=b;y=c                                                                        <L 19>
    var_75 = (var_71 == var_74);
    if (var_75) {
        var_76 = wp::copy(var_b);
        var_77 = wp::copy(var_c);
    }
    if (!var_75) {
        // elif k==2:x=c;y=a                                                                  <L 20>
        var_79 = (var_71 == var_78);
        if (var_79) {
            var_80 = wp::copy(var_c);
            var_81 = wp::copy(var_a);
        }
        var_82 = wp::where(var_79, var_80, var_72);
        var_83 = wp::where(var_79, var_81, var_73);
    }
    var_84 = wp::where(var_75, var_76, var_82);
    var_85 = wp::where(var_75, var_77, var_83);
    // edge=y-x;t=wp.clamp(wp.dot(p-x,edge)/wp.dot(edge,edge),wp.float64(0.),wp.float64(1.));z=x+t*edge;dd=wp.dot(p-z,p-z)       <L 21>
    var_86 = wp::sub(var_85, var_84);
    var_87 = wp::sub(var_p, var_84);
    var_88 = wp::dot(var_87, var_86);
    var_89 = wp::dot(var_86, var_86);
    var_90 = wp::div(var_88, var_89);
    var_91 = 0.0;
    var_92 = 1.0;
    var_93 = wp::clamp(var_90, var_91, var_92);
    var_94 = wp::mul(var_93, var_86);
    var_95 = wp::add(var_84, var_94);
    var_96 = wp::sub(var_p, var_95);
    var_97 = wp::sub(var_p, var_95);
    var_98 = wp::dot(var_96, var_97);
    // if dd<best:best=dd;q=z                                                                 <L 22>
    var_99 = (var_98 < var_70);
    if (var_99) {
        var_100 = wp::copy(var_98);
        var_101 = wp::copy(var_95);
    }
    var_102 = wp::where(var_99, var_101, var_69);
    var_103 = wp::where(var_99, var_100, var_70);
    // x=a;y=b                                                                                <L 18>
    var_105 = wp::copy(var_a);
    var_106 = wp::copy(var_b);
    // if k==1:x=b;y=c                                                                        <L 19>
    var_108 = (var_104 == var_107);
    if (var_108) {
        var_109 = wp::copy(var_b);
        var_110 = wp::copy(var_c);
    }
    if (!var_108) {
        // elif k==2:x=c;y=a                                                                  <L 20>
        var_112 = (var_104 == var_111);
        if (var_112) {
            var_113 = wp::copy(var_c);
            var_114 = wp::copy(var_a);
        }
        var_115 = wp::where(var_112, var_113, var_105);
        var_116 = wp::where(var_112, var_114, var_106);
    }
    var_117 = wp::where(var_108, var_109, var_115);
    var_118 = wp::where(var_108, var_110, var_116);
    // edge=y-x;t=wp.clamp(wp.dot(p-x,edge)/wp.dot(edge,edge),wp.float64(0.),wp.float64(1.));z=x+t*edge;dd=wp.dot(p-z,p-z)       <L 21>
    var_119 = wp::sub(var_118, var_117);
    var_120 = wp::sub(var_p, var_117);
    var_121 = wp::dot(var_120, var_119);
    var_122 = wp::dot(var_119, var_119);
    var_123 = wp::div(var_121, var_122);
    var_124 = 0.0;
    var_125 = 1.0;
    var_126 = wp::clamp(var_123, var_124, var_125);
    var_127 = wp::mul(var_126, var_119);
    var_128 = wp::add(var_117, var_127);
    var_129 = wp::sub(var_p, var_128);
    var_130 = wp::sub(var_p, var_128);
    var_131 = wp::dot(var_129, var_130);
    // if dd<best:best=dd;q=z                                                                 <L 22>
    var_132 = (var_131 < var_103);
    if (var_132) {
        var_133 = wp::copy(var_131);
        var_134 = wp::copy(var_128);
    }
    var_135 = wp::where(var_132, var_134, var_102);
    var_136 = wp::where(var_132, var_133, var_103);
    // return q                                                                               <L 23>
    return var_135;
}


// /home/omen/Documents/Codex/experiments/tomato_bounded_basis_20261113_v27/src/convex_guard_gpu.py:13
static CUDA_CALLABLE void adj_plane_value_0(
    wp::vec_t<3, wp::float64> var_p,
    wp::vec_t<4, wp::float64> var_plane,
    wp::vec_t<3, wp::float64> & adj_p,
    wp::vec_t<4, wp::float64> & adj_plane,
    wp::float64 & adj_ret)
{
	// reverse mode disabled (module option "enable_backward" is False or no dependent kernel found with "enable_backward")
}


// /home/omen/Documents/Codex/experiments/tomato_bounded_basis_20261113_v27/src/convex_guard_gpu.py:17
static CUDA_CALLABLE void adj_inside_0(
    wp::vec_t<3, wp::float64> var_p,
    wp::mat_t<4, 4, wp::float64> var_planes,
    wp::vec_t<3, wp::float64> & adj_p,
    wp::mat_t<4, 4, wp::float64> & adj_planes,
    bool & adj_ret)
{
	// reverse mode disabled (module option "enable_backward" is False or no dependent kernel found with "enable_backward")
}


// /home/omen/Documents/Codex/experiments/tomato_bounded_basis_20261113_v27/src/contact_gpu_precise.py:12
static CUDA_CALLABLE void adj_closest_0(
    wp::vec_t<3, wp::float64> var_p,
    wp::vec_t<3, wp::float64> var_a,
    wp::vec_t<3, wp::float64> var_b,
    wp::vec_t<3, wp::float64> var_c,
    wp::vec_t<3, wp::float64> & adj_p,
    wp::vec_t<3, wp::float64> & adj_a,
    wp::vec_t<3, wp::float64> & adj_b,
    wp::vec_t<3, wp::float64> & adj_c,
    wp::vec_t<3, wp::float64> & adj_ret)
{
	// reverse mode disabled (module option "enable_backward" is False or no dependent kernel found with "enable_backward")
}



extern "C" __global__ void prove_7b366fcc_cuda_kernel_forward(
    wp::launch_bounds_t<2> dim,
    wp::array_t<wp::mat_t<4, 3, wp::float64>> var_tets,
    wp::array_t<wp::mat_t<4, 3, wp::float64>> var_cells,
    wp::array_t<wp::mat_t<4, 4, wp::float64>> var_planes,
    wp::array_t<wp::int32> var_valid,
    wp::array_t<wp::vec_t<3, wp::float64>> var_lo,
    wp::array_t<wp::vec_t<3, wp::float64>> var_hi,
    wp::array_t<wp::vec_t<3, wp::float64>> var_tri,
    wp::array_t<wp::int32> var_ptr,
    wp::array_t<wp::int32> var_ids,
    wp::float64 var_target,
    wp::array_t<wp::int32> var_unresolved,
    wp::array_t<wp::float64> var_upper)
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
        wp::mat_t<4, 3, wp::float64>* var_2;
        wp::mat_t<4, 3, wp::float64> var_3;
        wp::mat_t<4, 3, wp::float64> var_4;
        wp::mat_t<4, 3, wp::float64>* var_5;
        wp::mat_t<4, 3, wp::float64> var_6;
        wp::mat_t<4, 3, wp::float64> var_7;
        const bool var_8 = true;
        const wp::int32 var_9 = 0;
        const wp::int32 var_10 = 0;
        wp::float64 var_11;
        const wp::int32 var_12 = 1;
        wp::float64 var_13;
        wp::float64 var_14;
        const wp::int32 var_15 = 2;
        wp::float64 var_16;
        const wp::int32 var_17 = 3;
        wp::float64 var_18;
        wp::float64 var_19;
        wp::float64 var_20;
        const wp::int32 var_21 = 0;
        wp::float64 var_22;
        const wp::int32 var_23 = 1;
        wp::float64 var_24;
        wp::float64 var_25;
        const wp::int32 var_26 = 2;
        wp::float64 var_27;
        const wp::int32 var_28 = 3;
        wp::float64 var_29;
        wp::float64 var_30;
        wp::float64 var_31;
        bool var_32;
        wp::float64 var_33;
        wp::float64 var_34;
        wp::vec_t<3, wp::float64>* var_35;
        wp::float64 var_36;
        wp::vec_t<3, wp::float64> var_37;
        bool var_38;
        wp::vec_t<3, wp::float64>* var_39;
        wp::float64 var_40;
        wp::vec_t<3, wp::float64> var_41;
        wp::float64 var_42;
        wp::float64 var_43;
        bool var_44;
        const bool var_45 = false;
        bool var_46;
        const wp::int32 var_47 = 1;
        const wp::int32 var_48 = 0;
        wp::float64 var_49;
        const wp::int32 var_50 = 1;
        wp::float64 var_51;
        wp::float64 var_52;
        const wp::int32 var_53 = 2;
        wp::float64 var_54;
        const wp::int32 var_55 = 3;
        wp::float64 var_56;
        wp::float64 var_57;
        wp::float64 var_58;
        const wp::int32 var_59 = 0;
        wp::float64 var_60;
        const wp::int32 var_61 = 1;
        wp::float64 var_62;
        wp::float64 var_63;
        const wp::int32 var_64 = 2;
        wp::float64 var_65;
        const wp::int32 var_66 = 3;
        wp::float64 var_67;
        wp::float64 var_68;
        wp::float64 var_69;
        bool var_70;
        wp::float64 var_71;
        wp::float64 var_72;
        wp::vec_t<3, wp::float64>* var_73;
        wp::float64 var_74;
        wp::vec_t<3, wp::float64> var_75;
        bool var_76;
        wp::vec_t<3, wp::float64>* var_77;
        wp::float64 var_78;
        wp::vec_t<3, wp::float64> var_79;
        wp::float64 var_80;
        wp::float64 var_81;
        bool var_82;
        const bool var_83 = false;
        bool var_84;
        const wp::int32 var_85 = 2;
        const wp::int32 var_86 = 0;
        wp::float64 var_87;
        const wp::int32 var_88 = 1;
        wp::float64 var_89;
        wp::float64 var_90;
        const wp::int32 var_91 = 2;
        wp::float64 var_92;
        const wp::int32 var_93 = 3;
        wp::float64 var_94;
        wp::float64 var_95;
        wp::float64 var_96;
        const wp::int32 var_97 = 0;
        wp::float64 var_98;
        const wp::int32 var_99 = 1;
        wp::float64 var_100;
        wp::float64 var_101;
        const wp::int32 var_102 = 2;
        wp::float64 var_103;
        const wp::int32 var_104 = 3;
        wp::float64 var_105;
        wp::float64 var_106;
        wp::float64 var_107;
        bool var_108;
        wp::float64 var_109;
        wp::float64 var_110;
        wp::vec_t<3, wp::float64>* var_111;
        wp::float64 var_112;
        wp::vec_t<3, wp::float64> var_113;
        bool var_114;
        wp::vec_t<3, wp::float64>* var_115;
        wp::float64 var_116;
        wp::vec_t<3, wp::float64> var_117;
        wp::float64 var_118;
        wp::float64 var_119;
        bool var_120;
        const bool var_121 = false;
        bool var_122;
        bool var_123;
        wp::float64 var_124;
        wp::mat_t<4, 4, wp::float64> var_125;
        wp::int32* var_126;
        const wp::int32 var_127 = 0;
        bool var_128;
        wp::int32 var_129;
        wp::float64 var_130;
        const wp::int32 var_131 = 0;
        const wp::int32 var_132 = 1;
        const wp::int32 var_133 = 0;
        wp::vec_t<3, wp::float64> var_134;
        wp::vec_t<3, wp::float64> var_135;
        wp::vec_t<3, wp::float64> var_136;
        wp::float64 var_137;
        wp::float64 var_138;
        const wp::int32 var_139 = 2;
        const wp::int32 var_140 = 0;
        wp::vec_t<3, wp::float64> var_141;
        wp::vec_t<3, wp::float64> var_142;
        wp::vec_t<3, wp::float64> var_143;
        wp::float64 var_144;
        wp::float64 var_145;
        const wp::int32 var_146 = 1;
        wp::vec_t<3, wp::float64> var_147;
        wp::vec_t<3, wp::float64> var_148;
        wp::vec_t<3, wp::float64> var_149;
        wp::float64 var_150;
        wp::float64 var_151;
        const wp::int32 var_152 = 3;
        const wp::int32 var_153 = 0;
        wp::vec_t<3, wp::float64> var_154;
        wp::vec_t<3, wp::float64> var_155;
        wp::vec_t<3, wp::float64> var_156;
        wp::float64 var_157;
        wp::float64 var_158;
        const wp::int32 var_159 = 1;
        wp::vec_t<3, wp::float64> var_160;
        wp::vec_t<3, wp::float64> var_161;
        wp::vec_t<3, wp::float64> var_162;
        wp::float64 var_163;
        wp::float64 var_164;
        const wp::int32 var_165 = 2;
        wp::vec_t<3, wp::float64> var_166;
        wp::vec_t<3, wp::float64> var_167;
        wp::vec_t<3, wp::float64> var_168;
        wp::float64 var_169;
        wp::float64 var_170;
        const wp::int32 var_171 = 0;
        const wp::int32 var_172 = 1;
        wp::int32 var_173;
        const wp::int32 var_174 = 4;
        wp::int32 var_175;
        wp::vec_t<3, wp::float64> var_176;
        const wp::int32 var_177 = 2;
        wp::int32 var_178;
        const wp::int32 var_179 = 4;
        wp::int32 var_180;
        wp::vec_t<3, wp::float64> var_181;
        const wp::int32 var_182 = 3;
        wp::int32 var_183;
        const wp::int32 var_184 = 4;
        wp::int32 var_185;
        wp::vec_t<3, wp::float64> var_186;
        wp::vec_t<3, wp::float64> var_187;
        wp::vec_t<3, wp::float64> var_188;
        wp::vec_t<3, wp::float64> var_189;
        wp::float64 var_190;
        wp::float64 var_191;
        bool var_192;
        const bool var_193 = false;
        wp::vec_t<3, wp::float64> var_194;
        wp::vec_t<3, wp::float64> var_195;
        wp::vec_t<3, wp::float64> var_196;
        wp::float64 var_197;
        wp::float64 var_198;
        bool var_199;
        wp::vec_t<3, wp::float64> var_200;
        wp::vec_t<3, wp::float64> var_201;
        wp::float64 var_202;
        wp::float64 var_203;
        const wp::int32 var_204 = 0;
        wp::float64 var_205;
        const wp::int32 var_206 = 1;
        wp::float64 var_207;
        const wp::int32 var_208 = 2;
        wp::float64 var_209;
        wp::vec_t<4, wp::float64> var_210;
        wp::vec_t<3, wp::float64> var_211;
        wp::float64 var_212;
        wp::float64 var_213;
        wp::float64 var_214;
        wp::float64 var_215;
        wp::float64 var_216;
        bool var_217;
        const bool var_218 = false;
        bool var_219;
        bool var_220;
        wp::vec_t<3, wp::float64> var_221;
        const wp::int32 var_222 = 1;
        const wp::int32 var_223 = 1;
        wp::int32 var_224;
        const wp::int32 var_225 = 4;
        wp::int32 var_226;
        wp::vec_t<3, wp::float64> var_227;
        const wp::int32 var_228 = 2;
        wp::int32 var_229;
        const wp::int32 var_230 = 4;
        wp::int32 var_231;
        wp::vec_t<3, wp::float64> var_232;
        const wp::int32 var_233 = 3;
        wp::int32 var_234;
        const wp::int32 var_235 = 4;
        wp::int32 var_236;
        wp::vec_t<3, wp::float64> var_237;
        wp::vec_t<3, wp::float64> var_238;
        wp::vec_t<3, wp::float64> var_239;
        wp::vec_t<3, wp::float64> var_240;
        wp::float64 var_241;
        wp::float64 var_242;
        bool var_243;
        const bool var_244 = false;
        wp::vec_t<3, wp::float64> var_245;
        wp::vec_t<3, wp::float64> var_246;
        wp::vec_t<3, wp::float64> var_247;
        wp::float64 var_248;
        wp::float64 var_249;
        bool var_250;
        wp::vec_t<3, wp::float64> var_251;
        wp::vec_t<3, wp::float64> var_252;
        wp::float64 var_253;
        wp::float64 var_254;
        const wp::int32 var_255 = 0;
        wp::float64 var_256;
        const wp::int32 var_257 = 1;
        wp::float64 var_258;
        const wp::int32 var_259 = 2;
        wp::float64 var_260;
        wp::vec_t<4, wp::float64> var_261;
        wp::vec_t<3, wp::float64> var_262;
        wp::float64 var_263;
        wp::float64 var_264;
        wp::float64 var_265;
        wp::float64 var_266;
        wp::float64 var_267;
        bool var_268;
        const bool var_269 = false;
        bool var_270;
        bool var_271;
        wp::vec_t<3, wp::float64> var_272;
        wp::float64 var_273;
        const wp::int32 var_274 = 2;
        const wp::int32 var_275 = 1;
        wp::int32 var_276;
        const wp::int32 var_277 = 4;
        wp::int32 var_278;
        wp::vec_t<3, wp::float64> var_279;
        const wp::int32 var_280 = 2;
        wp::int32 var_281;
        const wp::int32 var_282 = 4;
        wp::int32 var_283;
        wp::vec_t<3, wp::float64> var_284;
        const wp::int32 var_285 = 3;
        wp::int32 var_286;
        const wp::int32 var_287 = 4;
        wp::int32 var_288;
        wp::vec_t<3, wp::float64> var_289;
        wp::vec_t<3, wp::float64> var_290;
        wp::vec_t<3, wp::float64> var_291;
        wp::vec_t<3, wp::float64> var_292;
        wp::float64 var_293;
        wp::float64 var_294;
        bool var_295;
        const bool var_296 = false;
        wp::vec_t<3, wp::float64> var_297;
        wp::vec_t<3, wp::float64> var_298;
        wp::vec_t<3, wp::float64> var_299;
        wp::float64 var_300;
        wp::float64 var_301;
        bool var_302;
        wp::vec_t<3, wp::float64> var_303;
        wp::vec_t<3, wp::float64> var_304;
        wp::float64 var_305;
        wp::float64 var_306;
        const wp::int32 var_307 = 0;
        wp::float64 var_308;
        const wp::int32 var_309 = 1;
        wp::float64 var_310;
        const wp::int32 var_311 = 2;
        wp::float64 var_312;
        wp::vec_t<4, wp::float64> var_313;
        wp::vec_t<3, wp::float64> var_314;
        wp::float64 var_315;
        wp::float64 var_316;
        wp::float64 var_317;
        wp::float64 var_318;
        wp::float64 var_319;
        bool var_320;
        const bool var_321 = false;
        bool var_322;
        bool var_323;
        wp::vec_t<3, wp::float64> var_324;
        wp::float64 var_325;
        const wp::int32 var_326 = 3;
        const wp::int32 var_327 = 1;
        wp::int32 var_328;
        const wp::int32 var_329 = 4;
        wp::int32 var_330;
        wp::vec_t<3, wp::float64> var_331;
        const wp::int32 var_332 = 2;
        wp::int32 var_333;
        const wp::int32 var_334 = 4;
        wp::int32 var_335;
        wp::vec_t<3, wp::float64> var_336;
        const wp::int32 var_337 = 3;
        wp::int32 var_338;
        const wp::int32 var_339 = 4;
        wp::int32 var_340;
        wp::vec_t<3, wp::float64> var_341;
        wp::vec_t<3, wp::float64> var_342;
        wp::vec_t<3, wp::float64> var_343;
        wp::vec_t<3, wp::float64> var_344;
        wp::float64 var_345;
        wp::float64 var_346;
        bool var_347;
        const bool var_348 = false;
        wp::vec_t<3, wp::float64> var_349;
        wp::vec_t<3, wp::float64> var_350;
        wp::vec_t<3, wp::float64> var_351;
        wp::float64 var_352;
        wp::float64 var_353;
        bool var_354;
        wp::vec_t<3, wp::float64> var_355;
        wp::vec_t<3, wp::float64> var_356;
        wp::float64 var_357;
        wp::float64 var_358;
        const wp::int32 var_359 = 0;
        wp::float64 var_360;
        const wp::int32 var_361 = 1;
        wp::float64 var_362;
        const wp::int32 var_363 = 2;
        wp::float64 var_364;
        wp::vec_t<4, wp::float64> var_365;
        wp::vec_t<3, wp::float64> var_366;
        wp::float64 var_367;
        wp::float64 var_368;
        wp::float64 var_369;
        wp::float64 var_370;
        wp::float64 var_371;
        bool var_372;
        const bool var_373 = false;
        bool var_374;
        bool var_375;
        wp::vec_t<3, wp::float64> var_376;
        wp::float64 var_377;
        bool var_378;
        const wp::int32 var_379 = 1;
        wp::int32 var_380;
        wp::mat_t<4, 4, wp::float64>* var_381;
        wp::mat_t<4, 4, wp::float64> var_382;
        wp::mat_t<4, 4, wp::float64> var_383;
        wp::float64 var_384;
        wp::mat_t<56, 3, wp::float64> var_385;
        const wp::int32 var_386 = 0;
        wp::int32 var_387;
        const wp::int32 var_388 = 0;
        wp::vec_t<3, wp::float64> var_389;
        bool var_390;
        wp::vec_t<3, wp::float64> var_391;
        const wp::int32 var_392 = 1;
        wp::int32 var_393;
        wp::int32 var_394;
        wp::vec_t<3, wp::float64> var_395;
        bool var_396;
        wp::vec_t<3, wp::float64> var_397;
        const wp::int32 var_398 = 1;
        wp::int32 var_399;
        wp::int32 var_400;
        const wp::int32 var_401 = 1;
        wp::vec_t<3, wp::float64> var_402;
        bool var_403;
        wp::vec_t<3, wp::float64> var_404;
        const wp::int32 var_405 = 1;
        wp::int32 var_406;
        wp::int32 var_407;
        wp::vec_t<3, wp::float64> var_408;
        bool var_409;
        wp::vec_t<3, wp::float64> var_410;
        const wp::int32 var_411 = 1;
        wp::int32 var_412;
        wp::int32 var_413;
        const wp::int32 var_414 = 2;
        wp::vec_t<3, wp::float64> var_415;
        bool var_416;
        wp::vec_t<3, wp::float64> var_417;
        const wp::int32 var_418 = 1;
        wp::int32 var_419;
        wp::int32 var_420;
        wp::vec_t<3, wp::float64> var_421;
        bool var_422;
        wp::vec_t<3, wp::float64> var_423;
        const wp::int32 var_424 = 1;
        wp::int32 var_425;
        wp::int32 var_426;
        const wp::int32 var_427 = 3;
        wp::vec_t<3, wp::float64> var_428;
        bool var_429;
        wp::vec_t<3, wp::float64> var_430;
        const wp::int32 var_431 = 1;
        wp::int32 var_432;
        wp::int32 var_433;
        wp::vec_t<3, wp::float64> var_434;
        bool var_435;
        wp::vec_t<3, wp::float64> var_436;
        const wp::int32 var_437 = 1;
        wp::int32 var_438;
        wp::int32 var_439;
        const wp::int32 var_440 = 0;
        wp::mat_t<4, 3, wp::float64> var_441;
        wp::mat_t<4, 4, wp::float64> var_442;
        wp::mat_t<4, 4, wp::float64> var_443;
        const wp::int32 var_444 = 1;
        bool var_445;
        wp::mat_t<4, 3, wp::float64> var_446;
        wp::mat_t<4, 4, wp::float64> var_447;
        wp::mat_t<4, 4, wp::float64> var_448;
        wp::mat_t<4, 3, wp::float64> var_449;
        wp::mat_t<4, 4, wp::float64> var_450;
        wp::mat_t<4, 4, wp::float64> var_451;
        const wp::int32 var_452 = 0;
        const wp::int32 var_453 = 1;
        const wp::int32 var_454 = 0;
        const wp::int32 var_455 = 0;
        wp::vec_t<3, wp::float64> var_456;
        wp::vec_t<4, wp::float64> var_457;
        wp::float64 var_458;
        wp::vec_t<3, wp::float64> var_459;
        wp::vec_t<4, wp::float64> var_460;
        wp::float64 var_461;
        bool var_462;
        bool var_463;
        wp::float64 var_464;
        bool var_465;
        wp::float64 var_466;
        bool var_467;
        bool var_468;
        wp::float64 var_469;
        bool var_470;
        wp::float64 var_471;
        bool var_472;
        wp::vec_t<3, wp::float64> var_473;
        wp::float64 var_474;
        wp::float64 var_475;
        wp::vec_t<3, wp::float64> var_476;
        wp::vec_t<3, wp::float64> var_477;
        wp::vec_t<3, wp::float64> var_478;
        wp::vec_t<3, wp::float64> var_479;
        wp::vec_t<3, wp::float64> var_480;
        bool var_481;
        bool var_482;
        bool var_483;
        const wp::int32 var_484 = 1;
        wp::int32 var_485;
        wp::int32 var_486;
        wp::int32 var_487;
        const wp::int32 var_488 = 1;
        wp::vec_t<3, wp::float64> var_489;
        wp::vec_t<4, wp::float64> var_490;
        wp::float64 var_491;
        wp::vec_t<3, wp::float64> var_492;
        wp::vec_t<4, wp::float64> var_493;
        wp::float64 var_494;
        bool var_495;
        bool var_496;
        wp::float64 var_497;
        bool var_498;
        wp::float64 var_499;
        bool var_500;
        bool var_501;
        wp::float64 var_502;
        bool var_503;
        wp::float64 var_504;
        bool var_505;
        wp::vec_t<3, wp::float64> var_506;
        wp::float64 var_507;
        wp::float64 var_508;
        wp::vec_t<3, wp::float64> var_509;
        wp::vec_t<3, wp::float64> var_510;
        wp::vec_t<3, wp::float64> var_511;
        wp::vec_t<3, wp::float64> var_512;
        wp::vec_t<3, wp::float64> var_513;
        bool var_514;
        bool var_515;
        bool var_516;
        const wp::int32 var_517 = 1;
        wp::int32 var_518;
        wp::int32 var_519;
        wp::int32 var_520;
        wp::vec_t<3, wp::float64> var_521;
        const wp::int32 var_522 = 2;
        wp::vec_t<3, wp::float64> var_523;
        wp::vec_t<4, wp::float64> var_524;
        wp::float64 var_525;
        wp::vec_t<3, wp::float64> var_526;
        wp::vec_t<4, wp::float64> var_527;
        wp::float64 var_528;
        bool var_529;
        bool var_530;
        wp::float64 var_531;
        bool var_532;
        wp::float64 var_533;
        bool var_534;
        bool var_535;
        wp::float64 var_536;
        bool var_537;
        wp::float64 var_538;
        bool var_539;
        wp::vec_t<3, wp::float64> var_540;
        wp::float64 var_541;
        wp::float64 var_542;
        wp::vec_t<3, wp::float64> var_543;
        wp::vec_t<3, wp::float64> var_544;
        wp::vec_t<3, wp::float64> var_545;
        wp::vec_t<3, wp::float64> var_546;
        wp::vec_t<3, wp::float64> var_547;
        bool var_548;
        bool var_549;
        bool var_550;
        const wp::int32 var_551 = 1;
        wp::int32 var_552;
        wp::int32 var_553;
        wp::int32 var_554;
        wp::vec_t<3, wp::float64> var_555;
        const wp::int32 var_556 = 3;
        wp::vec_t<3, wp::float64> var_557;
        wp::vec_t<4, wp::float64> var_558;
        wp::float64 var_559;
        wp::vec_t<3, wp::float64> var_560;
        wp::vec_t<4, wp::float64> var_561;
        wp::float64 var_562;
        bool var_563;
        bool var_564;
        wp::float64 var_565;
        bool var_566;
        wp::float64 var_567;
        bool var_568;
        bool var_569;
        wp::float64 var_570;
        bool var_571;
        wp::float64 var_572;
        bool var_573;
        wp::vec_t<3, wp::float64> var_574;
        wp::float64 var_575;
        wp::float64 var_576;
        wp::vec_t<3, wp::float64> var_577;
        wp::vec_t<3, wp::float64> var_578;
        wp::vec_t<3, wp::float64> var_579;
        wp::vec_t<3, wp::float64> var_580;
        wp::vec_t<3, wp::float64> var_581;
        bool var_582;
        bool var_583;
        bool var_584;
        const wp::int32 var_585 = 1;
        wp::int32 var_586;
        wp::int32 var_587;
        wp::int32 var_588;
        wp::vec_t<3, wp::float64> var_589;
        const wp::int32 var_590 = 2;
        const wp::int32 var_591 = 0;
        const wp::int32 var_592 = 0;
        wp::vec_t<3, wp::float64> var_593;
        wp::vec_t<4, wp::float64> var_594;
        wp::float64 var_595;
        wp::vec_t<3, wp::float64> var_596;
        wp::vec_t<4, wp::float64> var_597;
        wp::float64 var_598;
        bool var_599;
        bool var_600;
        wp::float64 var_601;
        bool var_602;
        wp::float64 var_603;
        bool var_604;
        bool var_605;
        wp::float64 var_606;
        bool var_607;
        wp::float64 var_608;
        bool var_609;
        wp::vec_t<3, wp::float64> var_610;
        wp::float64 var_611;
        wp::float64 var_612;
        wp::vec_t<3, wp::float64> var_613;
        wp::vec_t<3, wp::float64> var_614;
        wp::vec_t<3, wp::float64> var_615;
        wp::vec_t<3, wp::float64> var_616;
        wp::vec_t<3, wp::float64> var_617;
        bool var_618;
        bool var_619;
        bool var_620;
        const wp::int32 var_621 = 1;
        wp::int32 var_622;
        wp::int32 var_623;
        wp::int32 var_624;
        wp::vec_t<3, wp::float64> var_625;
        const wp::int32 var_626 = 1;
        wp::vec_t<3, wp::float64> var_627;
        wp::vec_t<4, wp::float64> var_628;
        wp::float64 var_629;
        wp::vec_t<3, wp::float64> var_630;
        wp::vec_t<4, wp::float64> var_631;
        wp::float64 var_632;
        bool var_633;
        bool var_634;
        wp::float64 var_635;
        bool var_636;
        wp::float64 var_637;
        bool var_638;
        bool var_639;
        wp::float64 var_640;
        bool var_641;
        wp::float64 var_642;
        bool var_643;
        wp::vec_t<3, wp::float64> var_644;
        wp::float64 var_645;
        wp::float64 var_646;
        wp::vec_t<3, wp::float64> var_647;
        wp::vec_t<3, wp::float64> var_648;
        wp::vec_t<3, wp::float64> var_649;
        wp::vec_t<3, wp::float64> var_650;
        wp::vec_t<3, wp::float64> var_651;
        bool var_652;
        bool var_653;
        bool var_654;
        const wp::int32 var_655 = 1;
        wp::int32 var_656;
        wp::int32 var_657;
        wp::int32 var_658;
        wp::vec_t<3, wp::float64> var_659;
        const wp::int32 var_660 = 2;
        wp::vec_t<3, wp::float64> var_661;
        wp::vec_t<4, wp::float64> var_662;
        wp::float64 var_663;
        wp::vec_t<3, wp::float64> var_664;
        wp::vec_t<4, wp::float64> var_665;
        wp::float64 var_666;
        bool var_667;
        bool var_668;
        wp::float64 var_669;
        bool var_670;
        wp::float64 var_671;
        bool var_672;
        bool var_673;
        wp::float64 var_674;
        bool var_675;
        wp::float64 var_676;
        bool var_677;
        wp::vec_t<3, wp::float64> var_678;
        wp::float64 var_679;
        wp::float64 var_680;
        wp::vec_t<3, wp::float64> var_681;
        wp::vec_t<3, wp::float64> var_682;
        wp::vec_t<3, wp::float64> var_683;
        wp::vec_t<3, wp::float64> var_684;
        wp::vec_t<3, wp::float64> var_685;
        bool var_686;
        bool var_687;
        bool var_688;
        const wp::int32 var_689 = 1;
        wp::int32 var_690;
        wp::int32 var_691;
        wp::int32 var_692;
        wp::vec_t<3, wp::float64> var_693;
        const wp::int32 var_694 = 3;
        wp::vec_t<3, wp::float64> var_695;
        wp::vec_t<4, wp::float64> var_696;
        wp::float64 var_697;
        wp::vec_t<3, wp::float64> var_698;
        wp::vec_t<4, wp::float64> var_699;
        wp::float64 var_700;
        bool var_701;
        bool var_702;
        wp::float64 var_703;
        bool var_704;
        wp::float64 var_705;
        bool var_706;
        bool var_707;
        wp::float64 var_708;
        bool var_709;
        wp::float64 var_710;
        bool var_711;
        wp::vec_t<3, wp::float64> var_712;
        wp::float64 var_713;
        wp::float64 var_714;
        wp::vec_t<3, wp::float64> var_715;
        wp::vec_t<3, wp::float64> var_716;
        wp::vec_t<3, wp::float64> var_717;
        wp::vec_t<3, wp::float64> var_718;
        wp::vec_t<3, wp::float64> var_719;
        bool var_720;
        bool var_721;
        bool var_722;
        const wp::int32 var_723 = 1;
        wp::int32 var_724;
        wp::int32 var_725;
        wp::int32 var_726;
        wp::vec_t<3, wp::float64> var_727;
        const wp::int32 var_728 = 1;
        const wp::int32 var_729 = 0;
        wp::vec_t<3, wp::float64> var_730;
        wp::vec_t<4, wp::float64> var_731;
        wp::float64 var_732;
        wp::vec_t<3, wp::float64> var_733;
        wp::vec_t<4, wp::float64> var_734;
        wp::float64 var_735;
        bool var_736;
        bool var_737;
        wp::float64 var_738;
        bool var_739;
        wp::float64 var_740;
        bool var_741;
        bool var_742;
        wp::float64 var_743;
        bool var_744;
        wp::float64 var_745;
        bool var_746;
        wp::vec_t<3, wp::float64> var_747;
        wp::float64 var_748;
        wp::float64 var_749;
        wp::vec_t<3, wp::float64> var_750;
        wp::vec_t<3, wp::float64> var_751;
        wp::vec_t<3, wp::float64> var_752;
        wp::vec_t<3, wp::float64> var_753;
        wp::vec_t<3, wp::float64> var_754;
        bool var_755;
        bool var_756;
        bool var_757;
        const wp::int32 var_758 = 1;
        wp::int32 var_759;
        wp::int32 var_760;
        wp::int32 var_761;
        wp::vec_t<3, wp::float64> var_762;
        const wp::int32 var_763 = 1;
        wp::vec_t<3, wp::float64> var_764;
        wp::vec_t<4, wp::float64> var_765;
        wp::float64 var_766;
        wp::vec_t<3, wp::float64> var_767;
        wp::vec_t<4, wp::float64> var_768;
        wp::float64 var_769;
        bool var_770;
        bool var_771;
        wp::float64 var_772;
        bool var_773;
        wp::float64 var_774;
        bool var_775;
        bool var_776;
        wp::float64 var_777;
        bool var_778;
        wp::float64 var_779;
        bool var_780;
        wp::vec_t<3, wp::float64> var_781;
        wp::float64 var_782;
        wp::float64 var_783;
        wp::vec_t<3, wp::float64> var_784;
        wp::vec_t<3, wp::float64> var_785;
        wp::vec_t<3, wp::float64> var_786;
        wp::vec_t<3, wp::float64> var_787;
        wp::vec_t<3, wp::float64> var_788;
        bool var_789;
        bool var_790;
        bool var_791;
        const wp::int32 var_792 = 1;
        wp::int32 var_793;
        wp::int32 var_794;
        wp::int32 var_795;
        wp::vec_t<3, wp::float64> var_796;
        const wp::int32 var_797 = 2;
        wp::vec_t<3, wp::float64> var_798;
        wp::vec_t<4, wp::float64> var_799;
        wp::float64 var_800;
        wp::vec_t<3, wp::float64> var_801;
        wp::vec_t<4, wp::float64> var_802;
        wp::float64 var_803;
        bool var_804;
        bool var_805;
        wp::float64 var_806;
        bool var_807;
        wp::float64 var_808;
        bool var_809;
        bool var_810;
        wp::float64 var_811;
        bool var_812;
        wp::float64 var_813;
        bool var_814;
        wp::vec_t<3, wp::float64> var_815;
        wp::float64 var_816;
        wp::float64 var_817;
        wp::vec_t<3, wp::float64> var_818;
        wp::vec_t<3, wp::float64> var_819;
        wp::vec_t<3, wp::float64> var_820;
        wp::vec_t<3, wp::float64> var_821;
        wp::vec_t<3, wp::float64> var_822;
        bool var_823;
        bool var_824;
        bool var_825;
        const wp::int32 var_826 = 1;
        wp::int32 var_827;
        wp::int32 var_828;
        wp::int32 var_829;
        wp::vec_t<3, wp::float64> var_830;
        const wp::int32 var_831 = 3;
        wp::vec_t<3, wp::float64> var_832;
        wp::vec_t<4, wp::float64> var_833;
        wp::float64 var_834;
        wp::vec_t<3, wp::float64> var_835;
        wp::vec_t<4, wp::float64> var_836;
        wp::float64 var_837;
        bool var_838;
        bool var_839;
        wp::float64 var_840;
        bool var_841;
        wp::float64 var_842;
        bool var_843;
        bool var_844;
        wp::float64 var_845;
        bool var_846;
        wp::float64 var_847;
        bool var_848;
        wp::vec_t<3, wp::float64> var_849;
        wp::float64 var_850;
        wp::float64 var_851;
        wp::vec_t<3, wp::float64> var_852;
        wp::vec_t<3, wp::float64> var_853;
        wp::vec_t<3, wp::float64> var_854;
        wp::vec_t<3, wp::float64> var_855;
        wp::vec_t<3, wp::float64> var_856;
        bool var_857;
        bool var_858;
        bool var_859;
        const wp::int32 var_860 = 1;
        wp::int32 var_861;
        wp::int32 var_862;
        wp::int32 var_863;
        wp::vec_t<3, wp::float64> var_864;
        const wp::int32 var_865 = 3;
        const wp::int32 var_866 = 0;
        const wp::int32 var_867 = 0;
        wp::vec_t<3, wp::float64> var_868;
        wp::vec_t<4, wp::float64> var_869;
        wp::float64 var_870;
        wp::vec_t<3, wp::float64> var_871;
        wp::vec_t<4, wp::float64> var_872;
        wp::float64 var_873;
        bool var_874;
        bool var_875;
        wp::float64 var_876;
        bool var_877;
        wp::float64 var_878;
        bool var_879;
        bool var_880;
        wp::float64 var_881;
        bool var_882;
        wp::float64 var_883;
        bool var_884;
        wp::vec_t<3, wp::float64> var_885;
        wp::float64 var_886;
        wp::float64 var_887;
        wp::vec_t<3, wp::float64> var_888;
        wp::vec_t<3, wp::float64> var_889;
        wp::vec_t<3, wp::float64> var_890;
        wp::vec_t<3, wp::float64> var_891;
        wp::vec_t<3, wp::float64> var_892;
        bool var_893;
        bool var_894;
        bool var_895;
        const wp::int32 var_896 = 1;
        wp::int32 var_897;
        wp::int32 var_898;
        wp::int32 var_899;
        wp::vec_t<3, wp::float64> var_900;
        const wp::int32 var_901 = 1;
        wp::vec_t<3, wp::float64> var_902;
        wp::vec_t<4, wp::float64> var_903;
        wp::float64 var_904;
        wp::vec_t<3, wp::float64> var_905;
        wp::vec_t<4, wp::float64> var_906;
        wp::float64 var_907;
        bool var_908;
        bool var_909;
        wp::float64 var_910;
        bool var_911;
        wp::float64 var_912;
        bool var_913;
        bool var_914;
        wp::float64 var_915;
        bool var_916;
        wp::float64 var_917;
        bool var_918;
        wp::vec_t<3, wp::float64> var_919;
        wp::float64 var_920;
        wp::float64 var_921;
        wp::vec_t<3, wp::float64> var_922;
        wp::vec_t<3, wp::float64> var_923;
        wp::vec_t<3, wp::float64> var_924;
        wp::vec_t<3, wp::float64> var_925;
        wp::vec_t<3, wp::float64> var_926;
        bool var_927;
        bool var_928;
        bool var_929;
        const wp::int32 var_930 = 1;
        wp::int32 var_931;
        wp::int32 var_932;
        wp::int32 var_933;
        wp::vec_t<3, wp::float64> var_934;
        const wp::int32 var_935 = 2;
        wp::vec_t<3, wp::float64> var_936;
        wp::vec_t<4, wp::float64> var_937;
        wp::float64 var_938;
        wp::vec_t<3, wp::float64> var_939;
        wp::vec_t<4, wp::float64> var_940;
        wp::float64 var_941;
        bool var_942;
        bool var_943;
        wp::float64 var_944;
        bool var_945;
        wp::float64 var_946;
        bool var_947;
        bool var_948;
        wp::float64 var_949;
        bool var_950;
        wp::float64 var_951;
        bool var_952;
        wp::vec_t<3, wp::float64> var_953;
        wp::float64 var_954;
        wp::float64 var_955;
        wp::vec_t<3, wp::float64> var_956;
        wp::vec_t<3, wp::float64> var_957;
        wp::vec_t<3, wp::float64> var_958;
        wp::vec_t<3, wp::float64> var_959;
        wp::vec_t<3, wp::float64> var_960;
        bool var_961;
        bool var_962;
        bool var_963;
        const wp::int32 var_964 = 1;
        wp::int32 var_965;
        wp::int32 var_966;
        wp::int32 var_967;
        wp::vec_t<3, wp::float64> var_968;
        const wp::int32 var_969 = 3;
        wp::vec_t<3, wp::float64> var_970;
        wp::vec_t<4, wp::float64> var_971;
        wp::float64 var_972;
        wp::vec_t<3, wp::float64> var_973;
        wp::vec_t<4, wp::float64> var_974;
        wp::float64 var_975;
        bool var_976;
        bool var_977;
        wp::float64 var_978;
        bool var_979;
        wp::float64 var_980;
        bool var_981;
        bool var_982;
        wp::float64 var_983;
        bool var_984;
        wp::float64 var_985;
        bool var_986;
        wp::vec_t<3, wp::float64> var_987;
        wp::float64 var_988;
        wp::float64 var_989;
        wp::vec_t<3, wp::float64> var_990;
        wp::vec_t<3, wp::float64> var_991;
        wp::vec_t<3, wp::float64> var_992;
        wp::vec_t<3, wp::float64> var_993;
        wp::vec_t<3, wp::float64> var_994;
        bool var_995;
        bool var_996;
        bool var_997;
        const wp::int32 var_998 = 1;
        wp::int32 var_999;
        wp::int32 var_1000;
        wp::int32 var_1001;
        wp::vec_t<3, wp::float64> var_1002;
        const wp::int32 var_1003 = 1;
        const wp::int32 var_1004 = 0;
        wp::vec_t<3, wp::float64> var_1005;
        wp::vec_t<4, wp::float64> var_1006;
        wp::float64 var_1007;
        wp::vec_t<3, wp::float64> var_1008;
        wp::vec_t<4, wp::float64> var_1009;
        wp::float64 var_1010;
        bool var_1011;
        bool var_1012;
        wp::float64 var_1013;
        bool var_1014;
        wp::float64 var_1015;
        bool var_1016;
        bool var_1017;
        wp::float64 var_1018;
        bool var_1019;
        wp::float64 var_1020;
        bool var_1021;
        wp::vec_t<3, wp::float64> var_1022;
        wp::float64 var_1023;
        wp::float64 var_1024;
        wp::vec_t<3, wp::float64> var_1025;
        wp::vec_t<3, wp::float64> var_1026;
        wp::vec_t<3, wp::float64> var_1027;
        wp::vec_t<3, wp::float64> var_1028;
        wp::vec_t<3, wp::float64> var_1029;
        bool var_1030;
        bool var_1031;
        bool var_1032;
        const wp::int32 var_1033 = 1;
        wp::int32 var_1034;
        wp::int32 var_1035;
        wp::int32 var_1036;
        wp::vec_t<3, wp::float64> var_1037;
        const wp::int32 var_1038 = 1;
        wp::vec_t<3, wp::float64> var_1039;
        wp::vec_t<4, wp::float64> var_1040;
        wp::float64 var_1041;
        wp::vec_t<3, wp::float64> var_1042;
        wp::vec_t<4, wp::float64> var_1043;
        wp::float64 var_1044;
        bool var_1045;
        bool var_1046;
        wp::float64 var_1047;
        bool var_1048;
        wp::float64 var_1049;
        bool var_1050;
        bool var_1051;
        wp::float64 var_1052;
        bool var_1053;
        wp::float64 var_1054;
        bool var_1055;
        wp::vec_t<3, wp::float64> var_1056;
        wp::float64 var_1057;
        wp::float64 var_1058;
        wp::vec_t<3, wp::float64> var_1059;
        wp::vec_t<3, wp::float64> var_1060;
        wp::vec_t<3, wp::float64> var_1061;
        wp::vec_t<3, wp::float64> var_1062;
        wp::vec_t<3, wp::float64> var_1063;
        bool var_1064;
        bool var_1065;
        bool var_1066;
        const wp::int32 var_1067 = 1;
        wp::int32 var_1068;
        wp::int32 var_1069;
        wp::int32 var_1070;
        wp::vec_t<3, wp::float64> var_1071;
        const wp::int32 var_1072 = 2;
        wp::vec_t<3, wp::float64> var_1073;
        wp::vec_t<4, wp::float64> var_1074;
        wp::float64 var_1075;
        wp::vec_t<3, wp::float64> var_1076;
        wp::vec_t<4, wp::float64> var_1077;
        wp::float64 var_1078;
        bool var_1079;
        bool var_1080;
        wp::float64 var_1081;
        bool var_1082;
        wp::float64 var_1083;
        bool var_1084;
        bool var_1085;
        wp::float64 var_1086;
        bool var_1087;
        wp::float64 var_1088;
        bool var_1089;
        wp::vec_t<3, wp::float64> var_1090;
        wp::float64 var_1091;
        wp::float64 var_1092;
        wp::vec_t<3, wp::float64> var_1093;
        wp::vec_t<3, wp::float64> var_1094;
        wp::vec_t<3, wp::float64> var_1095;
        wp::vec_t<3, wp::float64> var_1096;
        wp::vec_t<3, wp::float64> var_1097;
        bool var_1098;
        bool var_1099;
        bool var_1100;
        const wp::int32 var_1101 = 1;
        wp::int32 var_1102;
        wp::int32 var_1103;
        wp::int32 var_1104;
        wp::vec_t<3, wp::float64> var_1105;
        const wp::int32 var_1106 = 3;
        wp::vec_t<3, wp::float64> var_1107;
        wp::vec_t<4, wp::float64> var_1108;
        wp::float64 var_1109;
        wp::vec_t<3, wp::float64> var_1110;
        wp::vec_t<4, wp::float64> var_1111;
        wp::float64 var_1112;
        bool var_1113;
        bool var_1114;
        wp::float64 var_1115;
        bool var_1116;
        wp::float64 var_1117;
        bool var_1118;
        bool var_1119;
        wp::float64 var_1120;
        bool var_1121;
        wp::float64 var_1122;
        bool var_1123;
        wp::vec_t<3, wp::float64> var_1124;
        wp::float64 var_1125;
        wp::float64 var_1126;
        wp::vec_t<3, wp::float64> var_1127;
        wp::vec_t<3, wp::float64> var_1128;
        wp::vec_t<3, wp::float64> var_1129;
        wp::vec_t<3, wp::float64> var_1130;
        wp::vec_t<3, wp::float64> var_1131;
        bool var_1132;
        bool var_1133;
        bool var_1134;
        const wp::int32 var_1135 = 1;
        wp::int32 var_1136;
        wp::int32 var_1137;
        wp::int32 var_1138;
        wp::vec_t<3, wp::float64> var_1139;
        const wp::int32 var_1140 = 2;
        const wp::int32 var_1141 = 0;
        wp::vec_t<3, wp::float64> var_1142;
        wp::vec_t<4, wp::float64> var_1143;
        wp::float64 var_1144;
        wp::vec_t<3, wp::float64> var_1145;
        wp::vec_t<4, wp::float64> var_1146;
        wp::float64 var_1147;
        bool var_1148;
        bool var_1149;
        wp::float64 var_1150;
        bool var_1151;
        wp::float64 var_1152;
        bool var_1153;
        bool var_1154;
        wp::float64 var_1155;
        bool var_1156;
        wp::float64 var_1157;
        bool var_1158;
        wp::vec_t<3, wp::float64> var_1159;
        wp::float64 var_1160;
        wp::float64 var_1161;
        wp::vec_t<3, wp::float64> var_1162;
        wp::vec_t<3, wp::float64> var_1163;
        wp::vec_t<3, wp::float64> var_1164;
        wp::vec_t<3, wp::float64> var_1165;
        wp::vec_t<3, wp::float64> var_1166;
        bool var_1167;
        bool var_1168;
        bool var_1169;
        const wp::int32 var_1170 = 1;
        wp::int32 var_1171;
        wp::int32 var_1172;
        wp::int32 var_1173;
        wp::vec_t<3, wp::float64> var_1174;
        const wp::int32 var_1175 = 1;
        wp::vec_t<3, wp::float64> var_1176;
        wp::vec_t<4, wp::float64> var_1177;
        wp::float64 var_1178;
        wp::vec_t<3, wp::float64> var_1179;
        wp::vec_t<4, wp::float64> var_1180;
        wp::float64 var_1181;
        bool var_1182;
        bool var_1183;
        wp::float64 var_1184;
        bool var_1185;
        wp::float64 var_1186;
        bool var_1187;
        bool var_1188;
        wp::float64 var_1189;
        bool var_1190;
        wp::float64 var_1191;
        bool var_1192;
        wp::vec_t<3, wp::float64> var_1193;
        wp::float64 var_1194;
        wp::float64 var_1195;
        wp::vec_t<3, wp::float64> var_1196;
        wp::vec_t<3, wp::float64> var_1197;
        wp::vec_t<3, wp::float64> var_1198;
        wp::vec_t<3, wp::float64> var_1199;
        wp::vec_t<3, wp::float64> var_1200;
        bool var_1201;
        bool var_1202;
        bool var_1203;
        const wp::int32 var_1204 = 1;
        wp::int32 var_1205;
        wp::int32 var_1206;
        wp::int32 var_1207;
        wp::vec_t<3, wp::float64> var_1208;
        const wp::int32 var_1209 = 2;
        wp::vec_t<3, wp::float64> var_1210;
        wp::vec_t<4, wp::float64> var_1211;
        wp::float64 var_1212;
        wp::vec_t<3, wp::float64> var_1213;
        wp::vec_t<4, wp::float64> var_1214;
        wp::float64 var_1215;
        bool var_1216;
        bool var_1217;
        wp::float64 var_1218;
        bool var_1219;
        wp::float64 var_1220;
        bool var_1221;
        bool var_1222;
        wp::float64 var_1223;
        bool var_1224;
        wp::float64 var_1225;
        bool var_1226;
        wp::vec_t<3, wp::float64> var_1227;
        wp::float64 var_1228;
        wp::float64 var_1229;
        wp::vec_t<3, wp::float64> var_1230;
        wp::vec_t<3, wp::float64> var_1231;
        wp::vec_t<3, wp::float64> var_1232;
        wp::vec_t<3, wp::float64> var_1233;
        wp::vec_t<3, wp::float64> var_1234;
        bool var_1235;
        bool var_1236;
        bool var_1237;
        const wp::int32 var_1238 = 1;
        wp::int32 var_1239;
        wp::int32 var_1240;
        wp::int32 var_1241;
        wp::vec_t<3, wp::float64> var_1242;
        const wp::int32 var_1243 = 3;
        wp::vec_t<3, wp::float64> var_1244;
        wp::vec_t<4, wp::float64> var_1245;
        wp::float64 var_1246;
        wp::vec_t<3, wp::float64> var_1247;
        wp::vec_t<4, wp::float64> var_1248;
        wp::float64 var_1249;
        bool var_1250;
        bool var_1251;
        wp::float64 var_1252;
        bool var_1253;
        wp::float64 var_1254;
        bool var_1255;
        bool var_1256;
        wp::float64 var_1257;
        bool var_1258;
        wp::float64 var_1259;
        bool var_1260;
        wp::vec_t<3, wp::float64> var_1261;
        wp::float64 var_1262;
        wp::float64 var_1263;
        wp::vec_t<3, wp::float64> var_1264;
        wp::vec_t<3, wp::float64> var_1265;
        wp::vec_t<3, wp::float64> var_1266;
        wp::vec_t<3, wp::float64> var_1267;
        wp::vec_t<3, wp::float64> var_1268;
        bool var_1269;
        bool var_1270;
        bool var_1271;
        const wp::int32 var_1272 = 1;
        wp::int32 var_1273;
        wp::int32 var_1274;
        wp::int32 var_1275;
        wp::vec_t<3, wp::float64> var_1276;
        const wp::int32 var_1277 = 1;
        wp::mat_t<4, 3, wp::float64> var_1278;
        wp::mat_t<4, 4, wp::float64> var_1279;
        wp::mat_t<4, 4, wp::float64> var_1280;
        const wp::int32 var_1281 = 1;
        bool var_1282;
        wp::mat_t<4, 3, wp::float64> var_1283;
        wp::mat_t<4, 4, wp::float64> var_1284;
        wp::mat_t<4, 4, wp::float64> var_1285;
        wp::mat_t<4, 3, wp::float64> var_1286;
        wp::mat_t<4, 4, wp::float64> var_1287;
        wp::mat_t<4, 4, wp::float64> var_1288;
        const wp::int32 var_1289 = 0;
        const wp::int32 var_1290 = 1;
        const wp::int32 var_1291 = 0;
        const wp::int32 var_1292 = 0;
        wp::vec_t<3, wp::float64> var_1293;
        wp::vec_t<4, wp::float64> var_1294;
        wp::float64 var_1295;
        wp::vec_t<3, wp::float64> var_1296;
        wp::vec_t<4, wp::float64> var_1297;
        wp::float64 var_1298;
        bool var_1299;
        bool var_1300;
        wp::float64 var_1301;
        bool var_1302;
        wp::float64 var_1303;
        bool var_1304;
        bool var_1305;
        wp::float64 var_1306;
        bool var_1307;
        wp::float64 var_1308;
        bool var_1309;
        wp::vec_t<3, wp::float64> var_1310;
        wp::float64 var_1311;
        wp::float64 var_1312;
        wp::vec_t<3, wp::float64> var_1313;
        wp::vec_t<3, wp::float64> var_1314;
        wp::vec_t<3, wp::float64> var_1315;
        wp::vec_t<3, wp::float64> var_1316;
        wp::vec_t<3, wp::float64> var_1317;
        bool var_1318;
        bool var_1319;
        bool var_1320;
        const wp::int32 var_1321 = 1;
        wp::int32 var_1322;
        wp::int32 var_1323;
        wp::int32 var_1324;
        wp::vec_t<3, wp::float64> var_1325;
        const wp::int32 var_1326 = 1;
        wp::vec_t<3, wp::float64> var_1327;
        wp::vec_t<4, wp::float64> var_1328;
        wp::float64 var_1329;
        wp::vec_t<3, wp::float64> var_1330;
        wp::vec_t<4, wp::float64> var_1331;
        wp::float64 var_1332;
        bool var_1333;
        bool var_1334;
        wp::float64 var_1335;
        bool var_1336;
        wp::float64 var_1337;
        bool var_1338;
        bool var_1339;
        wp::float64 var_1340;
        bool var_1341;
        wp::float64 var_1342;
        bool var_1343;
        wp::vec_t<3, wp::float64> var_1344;
        wp::float64 var_1345;
        wp::float64 var_1346;
        wp::vec_t<3, wp::float64> var_1347;
        wp::vec_t<3, wp::float64> var_1348;
        wp::vec_t<3, wp::float64> var_1349;
        wp::vec_t<3, wp::float64> var_1350;
        wp::vec_t<3, wp::float64> var_1351;
        bool var_1352;
        bool var_1353;
        bool var_1354;
        const wp::int32 var_1355 = 1;
        wp::int32 var_1356;
        wp::int32 var_1357;
        wp::int32 var_1358;
        wp::vec_t<3, wp::float64> var_1359;
        const wp::int32 var_1360 = 2;
        wp::vec_t<3, wp::float64> var_1361;
        wp::vec_t<4, wp::float64> var_1362;
        wp::float64 var_1363;
        wp::vec_t<3, wp::float64> var_1364;
        wp::vec_t<4, wp::float64> var_1365;
        wp::float64 var_1366;
        bool var_1367;
        bool var_1368;
        wp::float64 var_1369;
        bool var_1370;
        wp::float64 var_1371;
        bool var_1372;
        bool var_1373;
        wp::float64 var_1374;
        bool var_1375;
        wp::float64 var_1376;
        bool var_1377;
        wp::vec_t<3, wp::float64> var_1378;
        wp::float64 var_1379;
        wp::float64 var_1380;
        wp::vec_t<3, wp::float64> var_1381;
        wp::vec_t<3, wp::float64> var_1382;
        wp::vec_t<3, wp::float64> var_1383;
        wp::vec_t<3, wp::float64> var_1384;
        wp::vec_t<3, wp::float64> var_1385;
        bool var_1386;
        bool var_1387;
        bool var_1388;
        const wp::int32 var_1389 = 1;
        wp::int32 var_1390;
        wp::int32 var_1391;
        wp::int32 var_1392;
        wp::vec_t<3, wp::float64> var_1393;
        const wp::int32 var_1394 = 3;
        wp::vec_t<3, wp::float64> var_1395;
        wp::vec_t<4, wp::float64> var_1396;
        wp::float64 var_1397;
        wp::vec_t<3, wp::float64> var_1398;
        wp::vec_t<4, wp::float64> var_1399;
        wp::float64 var_1400;
        bool var_1401;
        bool var_1402;
        wp::float64 var_1403;
        bool var_1404;
        wp::float64 var_1405;
        bool var_1406;
        bool var_1407;
        wp::float64 var_1408;
        bool var_1409;
        wp::float64 var_1410;
        bool var_1411;
        wp::vec_t<3, wp::float64> var_1412;
        wp::float64 var_1413;
        wp::float64 var_1414;
        wp::vec_t<3, wp::float64> var_1415;
        wp::vec_t<3, wp::float64> var_1416;
        wp::vec_t<3, wp::float64> var_1417;
        wp::vec_t<3, wp::float64> var_1418;
        wp::vec_t<3, wp::float64> var_1419;
        bool var_1420;
        bool var_1421;
        bool var_1422;
        const wp::int32 var_1423 = 1;
        wp::int32 var_1424;
        wp::int32 var_1425;
        wp::int32 var_1426;
        wp::vec_t<3, wp::float64> var_1427;
        const wp::int32 var_1428 = 2;
        const wp::int32 var_1429 = 0;
        const wp::int32 var_1430 = 0;
        wp::vec_t<3, wp::float64> var_1431;
        wp::vec_t<4, wp::float64> var_1432;
        wp::float64 var_1433;
        wp::vec_t<3, wp::float64> var_1434;
        wp::vec_t<4, wp::float64> var_1435;
        wp::float64 var_1436;
        bool var_1437;
        bool var_1438;
        wp::float64 var_1439;
        bool var_1440;
        wp::float64 var_1441;
        bool var_1442;
        bool var_1443;
        wp::float64 var_1444;
        bool var_1445;
        wp::float64 var_1446;
        bool var_1447;
        wp::vec_t<3, wp::float64> var_1448;
        wp::float64 var_1449;
        wp::float64 var_1450;
        wp::vec_t<3, wp::float64> var_1451;
        wp::vec_t<3, wp::float64> var_1452;
        wp::vec_t<3, wp::float64> var_1453;
        wp::vec_t<3, wp::float64> var_1454;
        wp::vec_t<3, wp::float64> var_1455;
        bool var_1456;
        bool var_1457;
        bool var_1458;
        const wp::int32 var_1459 = 1;
        wp::int32 var_1460;
        wp::int32 var_1461;
        wp::int32 var_1462;
        wp::vec_t<3, wp::float64> var_1463;
        const wp::int32 var_1464 = 1;
        wp::vec_t<3, wp::float64> var_1465;
        wp::vec_t<4, wp::float64> var_1466;
        wp::float64 var_1467;
        wp::vec_t<3, wp::float64> var_1468;
        wp::vec_t<4, wp::float64> var_1469;
        wp::float64 var_1470;
        bool var_1471;
        bool var_1472;
        wp::float64 var_1473;
        bool var_1474;
        wp::float64 var_1475;
        bool var_1476;
        bool var_1477;
        wp::float64 var_1478;
        bool var_1479;
        wp::float64 var_1480;
        bool var_1481;
        wp::vec_t<3, wp::float64> var_1482;
        wp::float64 var_1483;
        wp::float64 var_1484;
        wp::vec_t<3, wp::float64> var_1485;
        wp::vec_t<3, wp::float64> var_1486;
        wp::vec_t<3, wp::float64> var_1487;
        wp::vec_t<3, wp::float64> var_1488;
        wp::vec_t<3, wp::float64> var_1489;
        bool var_1490;
        bool var_1491;
        bool var_1492;
        const wp::int32 var_1493 = 1;
        wp::int32 var_1494;
        wp::int32 var_1495;
        wp::int32 var_1496;
        wp::vec_t<3, wp::float64> var_1497;
        const wp::int32 var_1498 = 2;
        wp::vec_t<3, wp::float64> var_1499;
        wp::vec_t<4, wp::float64> var_1500;
        wp::float64 var_1501;
        wp::vec_t<3, wp::float64> var_1502;
        wp::vec_t<4, wp::float64> var_1503;
        wp::float64 var_1504;
        bool var_1505;
        bool var_1506;
        wp::float64 var_1507;
        bool var_1508;
        wp::float64 var_1509;
        bool var_1510;
        bool var_1511;
        wp::float64 var_1512;
        bool var_1513;
        wp::float64 var_1514;
        bool var_1515;
        wp::vec_t<3, wp::float64> var_1516;
        wp::float64 var_1517;
        wp::float64 var_1518;
        wp::vec_t<3, wp::float64> var_1519;
        wp::vec_t<3, wp::float64> var_1520;
        wp::vec_t<3, wp::float64> var_1521;
        wp::vec_t<3, wp::float64> var_1522;
        wp::vec_t<3, wp::float64> var_1523;
        bool var_1524;
        bool var_1525;
        bool var_1526;
        const wp::int32 var_1527 = 1;
        wp::int32 var_1528;
        wp::int32 var_1529;
        wp::int32 var_1530;
        wp::vec_t<3, wp::float64> var_1531;
        const wp::int32 var_1532 = 3;
        wp::vec_t<3, wp::float64> var_1533;
        wp::vec_t<4, wp::float64> var_1534;
        wp::float64 var_1535;
        wp::vec_t<3, wp::float64> var_1536;
        wp::vec_t<4, wp::float64> var_1537;
        wp::float64 var_1538;
        bool var_1539;
        bool var_1540;
        wp::float64 var_1541;
        bool var_1542;
        wp::float64 var_1543;
        bool var_1544;
        bool var_1545;
        wp::float64 var_1546;
        bool var_1547;
        wp::float64 var_1548;
        bool var_1549;
        wp::vec_t<3, wp::float64> var_1550;
        wp::float64 var_1551;
        wp::float64 var_1552;
        wp::vec_t<3, wp::float64> var_1553;
        wp::vec_t<3, wp::float64> var_1554;
        wp::vec_t<3, wp::float64> var_1555;
        wp::vec_t<3, wp::float64> var_1556;
        wp::vec_t<3, wp::float64> var_1557;
        bool var_1558;
        bool var_1559;
        bool var_1560;
        const wp::int32 var_1561 = 1;
        wp::int32 var_1562;
        wp::int32 var_1563;
        wp::int32 var_1564;
        wp::vec_t<3, wp::float64> var_1565;
        const wp::int32 var_1566 = 1;
        const wp::int32 var_1567 = 0;
        wp::vec_t<3, wp::float64> var_1568;
        wp::vec_t<4, wp::float64> var_1569;
        wp::float64 var_1570;
        wp::vec_t<3, wp::float64> var_1571;
        wp::vec_t<4, wp::float64> var_1572;
        wp::float64 var_1573;
        bool var_1574;
        bool var_1575;
        wp::float64 var_1576;
        bool var_1577;
        wp::float64 var_1578;
        bool var_1579;
        bool var_1580;
        wp::float64 var_1581;
        bool var_1582;
        wp::float64 var_1583;
        bool var_1584;
        wp::vec_t<3, wp::float64> var_1585;
        wp::float64 var_1586;
        wp::float64 var_1587;
        wp::vec_t<3, wp::float64> var_1588;
        wp::vec_t<3, wp::float64> var_1589;
        wp::vec_t<3, wp::float64> var_1590;
        wp::vec_t<3, wp::float64> var_1591;
        wp::vec_t<3, wp::float64> var_1592;
        bool var_1593;
        bool var_1594;
        bool var_1595;
        const wp::int32 var_1596 = 1;
        wp::int32 var_1597;
        wp::int32 var_1598;
        wp::int32 var_1599;
        wp::vec_t<3, wp::float64> var_1600;
        const wp::int32 var_1601 = 1;
        wp::vec_t<3, wp::float64> var_1602;
        wp::vec_t<4, wp::float64> var_1603;
        wp::float64 var_1604;
        wp::vec_t<3, wp::float64> var_1605;
        wp::vec_t<4, wp::float64> var_1606;
        wp::float64 var_1607;
        bool var_1608;
        bool var_1609;
        wp::float64 var_1610;
        bool var_1611;
        wp::float64 var_1612;
        bool var_1613;
        bool var_1614;
        wp::float64 var_1615;
        bool var_1616;
        wp::float64 var_1617;
        bool var_1618;
        wp::vec_t<3, wp::float64> var_1619;
        wp::float64 var_1620;
        wp::float64 var_1621;
        wp::vec_t<3, wp::float64> var_1622;
        wp::vec_t<3, wp::float64> var_1623;
        wp::vec_t<3, wp::float64> var_1624;
        wp::vec_t<3, wp::float64> var_1625;
        wp::vec_t<3, wp::float64> var_1626;
        bool var_1627;
        bool var_1628;
        bool var_1629;
        const wp::int32 var_1630 = 1;
        wp::int32 var_1631;
        wp::int32 var_1632;
        wp::int32 var_1633;
        wp::vec_t<3, wp::float64> var_1634;
        const wp::int32 var_1635 = 2;
        wp::vec_t<3, wp::float64> var_1636;
        wp::vec_t<4, wp::float64> var_1637;
        wp::float64 var_1638;
        wp::vec_t<3, wp::float64> var_1639;
        wp::vec_t<4, wp::float64> var_1640;
        wp::float64 var_1641;
        bool var_1642;
        bool var_1643;
        wp::float64 var_1644;
        bool var_1645;
        wp::float64 var_1646;
        bool var_1647;
        bool var_1648;
        wp::float64 var_1649;
        bool var_1650;
        wp::float64 var_1651;
        bool var_1652;
        wp::vec_t<3, wp::float64> var_1653;
        wp::float64 var_1654;
        wp::float64 var_1655;
        wp::vec_t<3, wp::float64> var_1656;
        wp::vec_t<3, wp::float64> var_1657;
        wp::vec_t<3, wp::float64> var_1658;
        wp::vec_t<3, wp::float64> var_1659;
        wp::vec_t<3, wp::float64> var_1660;
        bool var_1661;
        bool var_1662;
        bool var_1663;
        const wp::int32 var_1664 = 1;
        wp::int32 var_1665;
        wp::int32 var_1666;
        wp::int32 var_1667;
        wp::vec_t<3, wp::float64> var_1668;
        const wp::int32 var_1669 = 3;
        wp::vec_t<3, wp::float64> var_1670;
        wp::vec_t<4, wp::float64> var_1671;
        wp::float64 var_1672;
        wp::vec_t<3, wp::float64> var_1673;
        wp::vec_t<4, wp::float64> var_1674;
        wp::float64 var_1675;
        bool var_1676;
        bool var_1677;
        wp::float64 var_1678;
        bool var_1679;
        wp::float64 var_1680;
        bool var_1681;
        bool var_1682;
        wp::float64 var_1683;
        bool var_1684;
        wp::float64 var_1685;
        bool var_1686;
        wp::vec_t<3, wp::float64> var_1687;
        wp::float64 var_1688;
        wp::float64 var_1689;
        wp::vec_t<3, wp::float64> var_1690;
        wp::vec_t<3, wp::float64> var_1691;
        wp::vec_t<3, wp::float64> var_1692;
        wp::vec_t<3, wp::float64> var_1693;
        wp::vec_t<3, wp::float64> var_1694;
        bool var_1695;
        bool var_1696;
        bool var_1697;
        const wp::int32 var_1698 = 1;
        wp::int32 var_1699;
        wp::int32 var_1700;
        wp::int32 var_1701;
        wp::vec_t<3, wp::float64> var_1702;
        const wp::int32 var_1703 = 3;
        const wp::int32 var_1704 = 0;
        const wp::int32 var_1705 = 0;
        wp::vec_t<3, wp::float64> var_1706;
        wp::vec_t<4, wp::float64> var_1707;
        wp::float64 var_1708;
        wp::vec_t<3, wp::float64> var_1709;
        wp::vec_t<4, wp::float64> var_1710;
        wp::float64 var_1711;
        bool var_1712;
        bool var_1713;
        wp::float64 var_1714;
        bool var_1715;
        wp::float64 var_1716;
        bool var_1717;
        bool var_1718;
        wp::float64 var_1719;
        bool var_1720;
        wp::float64 var_1721;
        bool var_1722;
        wp::vec_t<3, wp::float64> var_1723;
        wp::float64 var_1724;
        wp::float64 var_1725;
        wp::vec_t<3, wp::float64> var_1726;
        wp::vec_t<3, wp::float64> var_1727;
        wp::vec_t<3, wp::float64> var_1728;
        wp::vec_t<3, wp::float64> var_1729;
        wp::vec_t<3, wp::float64> var_1730;
        bool var_1731;
        bool var_1732;
        bool var_1733;
        const wp::int32 var_1734 = 1;
        wp::int32 var_1735;
        wp::int32 var_1736;
        wp::int32 var_1737;
        wp::vec_t<3, wp::float64> var_1738;
        const wp::int32 var_1739 = 1;
        wp::vec_t<3, wp::float64> var_1740;
        wp::vec_t<4, wp::float64> var_1741;
        wp::float64 var_1742;
        wp::vec_t<3, wp::float64> var_1743;
        wp::vec_t<4, wp::float64> var_1744;
        wp::float64 var_1745;
        bool var_1746;
        bool var_1747;
        wp::float64 var_1748;
        bool var_1749;
        wp::float64 var_1750;
        bool var_1751;
        bool var_1752;
        wp::float64 var_1753;
        bool var_1754;
        wp::float64 var_1755;
        bool var_1756;
        wp::vec_t<3, wp::float64> var_1757;
        wp::float64 var_1758;
        wp::float64 var_1759;
        wp::vec_t<3, wp::float64> var_1760;
        wp::vec_t<3, wp::float64> var_1761;
        wp::vec_t<3, wp::float64> var_1762;
        wp::vec_t<3, wp::float64> var_1763;
        wp::vec_t<3, wp::float64> var_1764;
        bool var_1765;
        bool var_1766;
        bool var_1767;
        const wp::int32 var_1768 = 1;
        wp::int32 var_1769;
        wp::int32 var_1770;
        wp::int32 var_1771;
        wp::vec_t<3, wp::float64> var_1772;
        const wp::int32 var_1773 = 2;
        wp::vec_t<3, wp::float64> var_1774;
        wp::vec_t<4, wp::float64> var_1775;
        wp::float64 var_1776;
        wp::vec_t<3, wp::float64> var_1777;
        wp::vec_t<4, wp::float64> var_1778;
        wp::float64 var_1779;
        bool var_1780;
        bool var_1781;
        wp::float64 var_1782;
        bool var_1783;
        wp::float64 var_1784;
        bool var_1785;
        bool var_1786;
        wp::float64 var_1787;
        bool var_1788;
        wp::float64 var_1789;
        bool var_1790;
        wp::vec_t<3, wp::float64> var_1791;
        wp::float64 var_1792;
        wp::float64 var_1793;
        wp::vec_t<3, wp::float64> var_1794;
        wp::vec_t<3, wp::float64> var_1795;
        wp::vec_t<3, wp::float64> var_1796;
        wp::vec_t<3, wp::float64> var_1797;
        wp::vec_t<3, wp::float64> var_1798;
        bool var_1799;
        bool var_1800;
        bool var_1801;
        const wp::int32 var_1802 = 1;
        wp::int32 var_1803;
        wp::int32 var_1804;
        wp::int32 var_1805;
        wp::vec_t<3, wp::float64> var_1806;
        const wp::int32 var_1807 = 3;
        wp::vec_t<3, wp::float64> var_1808;
        wp::vec_t<4, wp::float64> var_1809;
        wp::float64 var_1810;
        wp::vec_t<3, wp::float64> var_1811;
        wp::vec_t<4, wp::float64> var_1812;
        wp::float64 var_1813;
        bool var_1814;
        bool var_1815;
        wp::float64 var_1816;
        bool var_1817;
        wp::float64 var_1818;
        bool var_1819;
        bool var_1820;
        wp::float64 var_1821;
        bool var_1822;
        wp::float64 var_1823;
        bool var_1824;
        wp::vec_t<3, wp::float64> var_1825;
        wp::float64 var_1826;
        wp::float64 var_1827;
        wp::vec_t<3, wp::float64> var_1828;
        wp::vec_t<3, wp::float64> var_1829;
        wp::vec_t<3, wp::float64> var_1830;
        wp::vec_t<3, wp::float64> var_1831;
        wp::vec_t<3, wp::float64> var_1832;
        bool var_1833;
        bool var_1834;
        bool var_1835;
        const wp::int32 var_1836 = 1;
        wp::int32 var_1837;
        wp::int32 var_1838;
        wp::int32 var_1839;
        wp::vec_t<3, wp::float64> var_1840;
        const wp::int32 var_1841 = 1;
        const wp::int32 var_1842 = 0;
        wp::vec_t<3, wp::float64> var_1843;
        wp::vec_t<4, wp::float64> var_1844;
        wp::float64 var_1845;
        wp::vec_t<3, wp::float64> var_1846;
        wp::vec_t<4, wp::float64> var_1847;
        wp::float64 var_1848;
        bool var_1849;
        bool var_1850;
        wp::float64 var_1851;
        bool var_1852;
        wp::float64 var_1853;
        bool var_1854;
        bool var_1855;
        wp::float64 var_1856;
        bool var_1857;
        wp::float64 var_1858;
        bool var_1859;
        wp::vec_t<3, wp::float64> var_1860;
        wp::float64 var_1861;
        wp::float64 var_1862;
        wp::vec_t<3, wp::float64> var_1863;
        wp::vec_t<3, wp::float64> var_1864;
        wp::vec_t<3, wp::float64> var_1865;
        wp::vec_t<3, wp::float64> var_1866;
        wp::vec_t<3, wp::float64> var_1867;
        bool var_1868;
        bool var_1869;
        bool var_1870;
        const wp::int32 var_1871 = 1;
        wp::int32 var_1872;
        wp::int32 var_1873;
        wp::int32 var_1874;
        wp::vec_t<3, wp::float64> var_1875;
        const wp::int32 var_1876 = 1;
        wp::vec_t<3, wp::float64> var_1877;
        wp::vec_t<4, wp::float64> var_1878;
        wp::float64 var_1879;
        wp::vec_t<3, wp::float64> var_1880;
        wp::vec_t<4, wp::float64> var_1881;
        wp::float64 var_1882;
        bool var_1883;
        bool var_1884;
        wp::float64 var_1885;
        bool var_1886;
        wp::float64 var_1887;
        bool var_1888;
        bool var_1889;
        wp::float64 var_1890;
        bool var_1891;
        wp::float64 var_1892;
        bool var_1893;
        wp::vec_t<3, wp::float64> var_1894;
        wp::float64 var_1895;
        wp::float64 var_1896;
        wp::vec_t<3, wp::float64> var_1897;
        wp::vec_t<3, wp::float64> var_1898;
        wp::vec_t<3, wp::float64> var_1899;
        wp::vec_t<3, wp::float64> var_1900;
        wp::vec_t<3, wp::float64> var_1901;
        bool var_1902;
        bool var_1903;
        bool var_1904;
        const wp::int32 var_1905 = 1;
        wp::int32 var_1906;
        wp::int32 var_1907;
        wp::int32 var_1908;
        wp::vec_t<3, wp::float64> var_1909;
        const wp::int32 var_1910 = 2;
        wp::vec_t<3, wp::float64> var_1911;
        wp::vec_t<4, wp::float64> var_1912;
        wp::float64 var_1913;
        wp::vec_t<3, wp::float64> var_1914;
        wp::vec_t<4, wp::float64> var_1915;
        wp::float64 var_1916;
        bool var_1917;
        bool var_1918;
        wp::float64 var_1919;
        bool var_1920;
        wp::float64 var_1921;
        bool var_1922;
        bool var_1923;
        wp::float64 var_1924;
        bool var_1925;
        wp::float64 var_1926;
        bool var_1927;
        wp::vec_t<3, wp::float64> var_1928;
        wp::float64 var_1929;
        wp::float64 var_1930;
        wp::vec_t<3, wp::float64> var_1931;
        wp::vec_t<3, wp::float64> var_1932;
        wp::vec_t<3, wp::float64> var_1933;
        wp::vec_t<3, wp::float64> var_1934;
        wp::vec_t<3, wp::float64> var_1935;
        bool var_1936;
        bool var_1937;
        bool var_1938;
        const wp::int32 var_1939 = 1;
        wp::int32 var_1940;
        wp::int32 var_1941;
        wp::int32 var_1942;
        wp::vec_t<3, wp::float64> var_1943;
        const wp::int32 var_1944 = 3;
        wp::vec_t<3, wp::float64> var_1945;
        wp::vec_t<4, wp::float64> var_1946;
        wp::float64 var_1947;
        wp::vec_t<3, wp::float64> var_1948;
        wp::vec_t<4, wp::float64> var_1949;
        wp::float64 var_1950;
        bool var_1951;
        bool var_1952;
        wp::float64 var_1953;
        bool var_1954;
        wp::float64 var_1955;
        bool var_1956;
        bool var_1957;
        wp::float64 var_1958;
        bool var_1959;
        wp::float64 var_1960;
        bool var_1961;
        wp::vec_t<3, wp::float64> var_1962;
        wp::float64 var_1963;
        wp::float64 var_1964;
        wp::vec_t<3, wp::float64> var_1965;
        wp::vec_t<3, wp::float64> var_1966;
        wp::vec_t<3, wp::float64> var_1967;
        wp::vec_t<3, wp::float64> var_1968;
        wp::vec_t<3, wp::float64> var_1969;
        bool var_1970;
        bool var_1971;
        bool var_1972;
        const wp::int32 var_1973 = 1;
        wp::int32 var_1974;
        wp::int32 var_1975;
        wp::int32 var_1976;
        wp::vec_t<3, wp::float64> var_1977;
        const wp::int32 var_1978 = 2;
        const wp::int32 var_1979 = 0;
        wp::vec_t<3, wp::float64> var_1980;
        wp::vec_t<4, wp::float64> var_1981;
        wp::float64 var_1982;
        wp::vec_t<3, wp::float64> var_1983;
        wp::vec_t<4, wp::float64> var_1984;
        wp::float64 var_1985;
        bool var_1986;
        bool var_1987;
        wp::float64 var_1988;
        bool var_1989;
        wp::float64 var_1990;
        bool var_1991;
        bool var_1992;
        wp::float64 var_1993;
        bool var_1994;
        wp::float64 var_1995;
        bool var_1996;
        wp::vec_t<3, wp::float64> var_1997;
        wp::float64 var_1998;
        wp::float64 var_1999;
        wp::vec_t<3, wp::float64> var_2000;
        wp::vec_t<3, wp::float64> var_2001;
        wp::vec_t<3, wp::float64> var_2002;
        wp::vec_t<3, wp::float64> var_2003;
        wp::vec_t<3, wp::float64> var_2004;
        bool var_2005;
        bool var_2006;
        bool var_2007;
        const wp::int32 var_2008 = 1;
        wp::int32 var_2009;
        wp::int32 var_2010;
        wp::int32 var_2011;
        wp::vec_t<3, wp::float64> var_2012;
        const wp::int32 var_2013 = 1;
        wp::vec_t<3, wp::float64> var_2014;
        wp::vec_t<4, wp::float64> var_2015;
        wp::float64 var_2016;
        wp::vec_t<3, wp::float64> var_2017;
        wp::vec_t<4, wp::float64> var_2018;
        wp::float64 var_2019;
        bool var_2020;
        bool var_2021;
        wp::float64 var_2022;
        bool var_2023;
        wp::float64 var_2024;
        bool var_2025;
        bool var_2026;
        wp::float64 var_2027;
        bool var_2028;
        wp::float64 var_2029;
        bool var_2030;
        wp::vec_t<3, wp::float64> var_2031;
        wp::float64 var_2032;
        wp::float64 var_2033;
        wp::vec_t<3, wp::float64> var_2034;
        wp::vec_t<3, wp::float64> var_2035;
        wp::vec_t<3, wp::float64> var_2036;
        wp::vec_t<3, wp::float64> var_2037;
        wp::vec_t<3, wp::float64> var_2038;
        bool var_2039;
        bool var_2040;
        bool var_2041;
        const wp::int32 var_2042 = 1;
        wp::int32 var_2043;
        wp::int32 var_2044;
        wp::int32 var_2045;
        wp::vec_t<3, wp::float64> var_2046;
        const wp::int32 var_2047 = 2;
        wp::vec_t<3, wp::float64> var_2048;
        wp::vec_t<4, wp::float64> var_2049;
        wp::float64 var_2050;
        wp::vec_t<3, wp::float64> var_2051;
        wp::vec_t<4, wp::float64> var_2052;
        wp::float64 var_2053;
        bool var_2054;
        bool var_2055;
        wp::float64 var_2056;
        bool var_2057;
        wp::float64 var_2058;
        bool var_2059;
        bool var_2060;
        wp::float64 var_2061;
        bool var_2062;
        wp::float64 var_2063;
        bool var_2064;
        wp::vec_t<3, wp::float64> var_2065;
        wp::float64 var_2066;
        wp::float64 var_2067;
        wp::vec_t<3, wp::float64> var_2068;
        wp::vec_t<3, wp::float64> var_2069;
        wp::vec_t<3, wp::float64> var_2070;
        wp::vec_t<3, wp::float64> var_2071;
        wp::vec_t<3, wp::float64> var_2072;
        bool var_2073;
        bool var_2074;
        bool var_2075;
        const wp::int32 var_2076 = 1;
        wp::int32 var_2077;
        wp::int32 var_2078;
        wp::int32 var_2079;
        wp::vec_t<3, wp::float64> var_2080;
        const wp::int32 var_2081 = 3;
        wp::vec_t<3, wp::float64> var_2082;
        wp::vec_t<4, wp::float64> var_2083;
        wp::float64 var_2084;
        wp::vec_t<3, wp::float64> var_2085;
        wp::vec_t<4, wp::float64> var_2086;
        wp::float64 var_2087;
        bool var_2088;
        bool var_2089;
        wp::float64 var_2090;
        bool var_2091;
        wp::float64 var_2092;
        bool var_2093;
        bool var_2094;
        wp::float64 var_2095;
        bool var_2096;
        wp::float64 var_2097;
        bool var_2098;
        wp::vec_t<3, wp::float64> var_2099;
        wp::float64 var_2100;
        wp::float64 var_2101;
        wp::vec_t<3, wp::float64> var_2102;
        wp::vec_t<3, wp::float64> var_2103;
        wp::vec_t<3, wp::float64> var_2104;
        wp::vec_t<3, wp::float64> var_2105;
        wp::vec_t<3, wp::float64> var_2106;
        bool var_2107;
        bool var_2108;
        bool var_2109;
        const wp::int32 var_2110 = 1;
        wp::int32 var_2111;
        wp::int32 var_2112;
        wp::int32 var_2113;
        wp::vec_t<3, wp::float64> var_2114;
        const wp::int32 var_2115 = 0;
        bool var_2116;
        wp::float64 var_2117;
        wp::vec_t<3, wp::float64> var_2118;
        wp::range_t var_2119;
        wp::int32 var_2120;
        wp::vec_t<3, wp::float64> var_2121;
        wp::vec_t<3, wp::float64> var_2122;
        wp::float64 var_2123;
        wp::vec_t<3, wp::float64> var_2124;
        const wp::int32 var_2125 = -1;
        wp::int32 var_2126;
        wp::float64 var_2127;
        wp::int32* var_2128;
        const wp::int32 var_2129 = 1;
        wp::int32 var_2130;
        wp::int32* var_2131;
        wp::range_t var_2132;
        wp::int32 var_2133;
        wp::int32 var_2134;
        wp::int32 var_2135;
        wp::int32* var_2136;
        wp::int32 var_2137;
        wp::int32 var_2138;
        const wp::int32 var_2139 = 0;
        wp::vec_t<3, wp::float64>* var_2140;
        const wp::int32 var_2141 = 1;
        wp::vec_t<3, wp::float64>* var_2142;
        const wp::int32 var_2143 = 2;
        wp::vec_t<3, wp::float64>* var_2144;
        wp::vec_t<3, wp::float64> var_2145;
        wp::vec_t<3, wp::float64> var_2146;
        wp::vec_t<3, wp::float64> var_2147;
        wp::vec_t<3, wp::float64> var_2148;
        wp::vec_t<3, wp::float64> var_2149;
        wp::float64 var_2150;
        bool var_2151;
        wp::float64 var_2152;
        wp::int32 var_2153;
        wp::int32 var_2154;
        wp::float64 var_2155;
        wp::float64 var_2156;
        wp::range_t var_2157;
        wp::int32 var_2158;
        wp::vec_t<3, wp::float64> var_2159;
        wp::vec_t<3, wp::float64> var_2160;
        const wp::int32 var_2161 = 0;
        wp::vec_t<3, wp::float64>* var_2162;
        const wp::int32 var_2163 = 1;
        wp::vec_t<3, wp::float64>* var_2164;
        const wp::int32 var_2165 = 2;
        wp::vec_t<3, wp::float64>* var_2166;
        wp::vec_t<3, wp::float64> var_2167;
        wp::vec_t<3, wp::float64> var_2168;
        wp::vec_t<3, wp::float64> var_2169;
        wp::vec_t<3, wp::float64> var_2170;
        wp::vec_t<3, wp::float64> var_2171;
        wp::float64 var_2172;
        wp::float64 var_2173;
        bool var_2174;
        wp::int32* var_2175;
        const wp::int32 var_2176 = 1;
        wp::int32 var_2177;
        wp::int32* var_2178;
        wp::range_t var_2179;
        wp::int32 var_2180;
        wp::int32 var_2181;
        wp::int32 var_2182;
        wp::int32 var_2183;
        wp::int32* var_2184;
        wp::int32 var_2185;
        wp::int32 var_2186;
        wp::float64 var_2187;
        wp::range_t var_2188;
        wp::int32 var_2189;
        wp::vec_t<3, wp::float64> var_2190;
        wp::vec_t<3, wp::float64> var_2191;
        const wp::int32 var_2192 = 0;
        wp::vec_t<3, wp::float64>* var_2193;
        const wp::int32 var_2194 = 1;
        wp::vec_t<3, wp::float64>* var_2195;
        const wp::int32 var_2196 = 2;
        wp::vec_t<3, wp::float64>* var_2197;
        wp::vec_t<3, wp::float64> var_2198;
        wp::vec_t<3, wp::float64> var_2199;
        wp::vec_t<3, wp::float64> var_2200;
        wp::vec_t<3, wp::float64> var_2201;
        wp::vec_t<3, wp::float64> var_2202;
        wp::float64 var_2203;
        wp::float64 var_2204;
        wp::float64 var_2205;
        bool var_2206;
        wp::int32 var_2207;
        wp::int32 var_2208;
        wp::float64 var_2209;
        wp::int32 var_2210;
        wp::int32 var_2211;
        const wp::int32 var_2212 = 0;
        wp::float64 var_2213;
        bool var_2214;
        const wp::int32 var_2215 = 1;
        wp::int32 var_2216;
        //---------
        // forward
        // def prove(tets:wp.array(dtype=M43),cells:wp.array(dtype=M43),planes:wp.array(dtype=wp.mat44d),valid:wp.array(dtype=int),lo:wp.array(dtype=wp.vec3d),hi:wp.array(dtype=wp.vec3d),tri:wp.array2d(dtype=wp.vec3d),ptr:wp.array(dtype=int),ids:wp.array(dtype=int),target:wp.float64,unresolved:wp.array(dtype=int),upper:wp.array(dtype=wp.float64)):       <L 25>
        // i,c=wp.tid();a=tets[i];b=cells[c];overlap=True                                         <L 26>
        builtin_tid2d(var_0, var_1);
        var_2 = wp::address(var_tets, var_0);
        var_4 = wp::load(var_2);
        var_3 = wp::copy(var_4);
        var_5 = wp::address(var_cells, var_1);
        var_7 = wp::load(var_5);
        var_6 = wp::copy(var_7);
        // for k in range(3):                                                                     <L 27>
        // amin=wp.min(wp.min(a[0,k],a[1,k]),wp.min(a[2,k],a[3,k]));amax=wp.max(wp.max(a[0,k],a[1,k]),wp.max(a[2,k],a[3,k]))       <L 28>
        var_11 = wp::extract(var_3, var_10, var_9);
        var_13 = wp::extract(var_3, var_12, var_9);
        var_14 = wp::min(var_11, var_13);
        var_16 = wp::extract(var_3, var_15, var_9);
        var_18 = wp::extract(var_3, var_17, var_9);
        var_19 = wp::min(var_16, var_18);
        var_20 = wp::min(var_14, var_19);
        var_22 = wp::extract(var_3, var_21, var_9);
        var_24 = wp::extract(var_3, var_23, var_9);
        var_25 = wp::max(var_22, var_24);
        var_27 = wp::extract(var_3, var_26, var_9);
        var_29 = wp::extract(var_3, var_28, var_9);
        var_30 = wp::max(var_27, var_29);
        var_31 = wp::max(var_25, var_30);
        // if amax+wp.float64(1e-12)<lo[c][k] or hi[c][k]+wp.float64(1e-12)<amin:overlap=False       <L 29>
        var_33 = 1e-12;
        var_34 = wp::add(var_31, var_33);
        var_35 = wp::address(var_lo, var_1);
        var_37 = wp::load(var_35);
        var_36 = wp::extract(var_37, var_9);
        var_38 = (var_34 < var_36);
        var_32 = var_38;
        if (!var_32) {
            var_39 = wp::address(var_hi, var_1);
            var_41 = wp::load(var_39);
            var_40 = wp::extract(var_41, var_9);
            var_42 = 1e-12;
            var_43 = wp::add(var_40, var_42);
            var_44 = (var_43 < var_20);
            var_32 = var_32 || var_44;
        }
        if (var_32) {
        }
        var_46 = wp::where(var_32, var_45, var_8);
        // amin=wp.min(wp.min(a[0,k],a[1,k]),wp.min(a[2,k],a[3,k]));amax=wp.max(wp.max(a[0,k],a[1,k]),wp.max(a[2,k],a[3,k]))       <L 28>
        var_49 = wp::extract(var_3, var_48, var_47);
        var_51 = wp::extract(var_3, var_50, var_47);
        var_52 = wp::min(var_49, var_51);
        var_54 = wp::extract(var_3, var_53, var_47);
        var_56 = wp::extract(var_3, var_55, var_47);
        var_57 = wp::min(var_54, var_56);
        var_58 = wp::min(var_52, var_57);
        var_60 = wp::extract(var_3, var_59, var_47);
        var_62 = wp::extract(var_3, var_61, var_47);
        var_63 = wp::max(var_60, var_62);
        var_65 = wp::extract(var_3, var_64, var_47);
        var_67 = wp::extract(var_3, var_66, var_47);
        var_68 = wp::max(var_65, var_67);
        var_69 = wp::max(var_63, var_68);
        // if amax+wp.float64(1e-12)<lo[c][k] or hi[c][k]+wp.float64(1e-12)<amin:overlap=False       <L 29>
        var_71 = 1e-12;
        var_72 = wp::add(var_69, var_71);
        var_73 = wp::address(var_lo, var_1);
        var_75 = wp::load(var_73);
        var_74 = wp::extract(var_75, var_47);
        var_76 = (var_72 < var_74);
        var_70 = var_76;
        if (!var_70) {
            var_77 = wp::address(var_hi, var_1);
            var_79 = wp::load(var_77);
            var_78 = wp::extract(var_79, var_47);
            var_80 = 1e-12;
            var_81 = wp::add(var_78, var_80);
            var_82 = (var_81 < var_58);
            var_70 = var_70 || var_82;
        }
        if (var_70) {
        }
        var_84 = wp::where(var_70, var_83, var_46);
        // amin=wp.min(wp.min(a[0,k],a[1,k]),wp.min(a[2,k],a[3,k]));amax=wp.max(wp.max(a[0,k],a[1,k]),wp.max(a[2,k],a[3,k]))       <L 28>
        var_87 = wp::extract(var_3, var_86, var_85);
        var_89 = wp::extract(var_3, var_88, var_85);
        var_90 = wp::min(var_87, var_89);
        var_92 = wp::extract(var_3, var_91, var_85);
        var_94 = wp::extract(var_3, var_93, var_85);
        var_95 = wp::min(var_92, var_94);
        var_96 = wp::min(var_90, var_95);
        var_98 = wp::extract(var_3, var_97, var_85);
        var_100 = wp::extract(var_3, var_99, var_85);
        var_101 = wp::max(var_98, var_100);
        var_103 = wp::extract(var_3, var_102, var_85);
        var_105 = wp::extract(var_3, var_104, var_85);
        var_106 = wp::max(var_103, var_105);
        var_107 = wp::max(var_101, var_106);
        // if amax+wp.float64(1e-12)<lo[c][k] or hi[c][k]+wp.float64(1e-12)<amin:overlap=False       <L 29>
        var_109 = 1e-12;
        var_110 = wp::add(var_107, var_109);
        var_111 = wp::address(var_lo, var_1);
        var_113 = wp::load(var_111);
        var_112 = wp::extract(var_113, var_85);
        var_114 = (var_110 < var_112);
        var_108 = var_114;
        if (!var_108) {
            var_115 = wp::address(var_hi, var_1);
            var_117 = wp::load(var_115);
            var_116 = wp::extract(var_117, var_85);
            var_118 = 1e-12;
            var_119 = wp::add(var_116, var_118);
            var_120 = (var_119 < var_96);
            var_108 = var_108 || var_120;
        }
        if (var_108) {
        }
        var_122 = wp::where(var_108, var_121, var_84);
        // if not overlap:return                                                                  <L 30>
        var_123 = wp::unot(var_122);
        if (var_123) {
            continue;
        }
        // pa=wp.mat44d(wp.float64(0.));ok=valid[c]!=0;h=wp.float64(0.)                           <L 31>
        var_124 = 0.0;
        var_125 = wp::mat_t<4, 4, wp::float64>(var_124);
        var_126 = wp::address(var_valid, var_1);
        var_129 = wp::load(var_126);
        var_128 = (var_129 != var_127);
        var_130 = 0.0;
        // for u in range(4):                                                                     <L 32>
        // for v in range(u):h=wp.max(h,wp.length(a[u]-a[v]))                                     <L 33>
        var_134 = wp::extract(var_3, var_132);
        var_135 = wp::extract(var_3, var_133);
        var_136 = wp::sub(var_134, var_135);
        var_137 = wp::length(var_136);
        var_138 = wp::max(var_130, var_137);
        var_141 = wp::extract(var_3, var_139);
        var_142 = wp::extract(var_3, var_140);
        var_143 = wp::sub(var_141, var_142);
        var_144 = wp::length(var_143);
        var_145 = wp::max(var_138, var_144);
        var_147 = wp::extract(var_3, var_139);
        var_148 = wp::extract(var_3, var_146);
        var_149 = wp::sub(var_147, var_148);
        var_150 = wp::length(var_149);
        var_151 = wp::max(var_145, var_150);
        var_154 = wp::extract(var_3, var_152);
        var_155 = wp::extract(var_3, var_153);
        var_156 = wp::sub(var_154, var_155);
        var_157 = wp::length(var_156);
        var_158 = wp::max(var_151, var_157);
        var_160 = wp::extract(var_3, var_152);
        var_161 = wp::extract(var_3, var_159);
        var_162 = wp::sub(var_160, var_161);
        var_163 = wp::length(var_162);
        var_164 = wp::max(var_158, var_163);
        var_166 = wp::extract(var_3, var_152);
        var_167 = wp::extract(var_3, var_165);
        var_168 = wp::sub(var_166, var_167);
        var_169 = wp::length(var_168);
        var_170 = wp::max(var_164, var_169);
        // for u in range(4):                                                                     <L 34>
        // p0=a[(u+1)%4];p1=a[(u+2)%4];p2=a[(u+3)%4];n=wp.cross(p1-p0,p2-p0);size=wp.length(n)       <L 35>
        var_173 = wp::add(var_171, var_172);
        var_175 = wp::mod(var_173, var_174);
        var_176 = wp::extract(var_3, var_175);
        var_178 = wp::add(var_171, var_177);
        var_180 = wp::mod(var_178, var_179);
        var_181 = wp::extract(var_3, var_180);
        var_183 = wp::add(var_171, var_182);
        var_185 = wp::mod(var_183, var_184);
        var_186 = wp::extract(var_3, var_185);
        var_187 = wp::sub(var_181, var_176);
        var_188 = wp::sub(var_186, var_176);
        var_189 = wp::cross(var_187, var_188);
        var_190 = wp::length(var_189);
        // if size==wp.float64(0.):ok=False                                                       <L 36>
        var_191 = 0.0;
        var_192 = (var_190 == var_191);
        if (var_192) {
        }
        if (!var_192) {
            // n=n/size                                                                           <L 38>
            var_194 = wp::div(var_189, var_190);
            // if wp.dot(n,a[u]-p0)>wp.float64(0.):n=-n                                           <L 39>
            var_195 = wp::extract(var_3, var_171);
            var_196 = wp::sub(var_195, var_176);
            var_197 = wp::dot(var_194, var_196);
            var_198 = 0.0;
            var_199 = (var_197 > var_198);
            if (var_199) {
                var_200 = wp::neg(var_194);
            }
            var_201 = wp::where(var_199, var_200, var_194);
            // d=-wp.dot(n,p0);pa[u]=wp.vec4d(n[0],n[1],n[2],d)                                   <L 40>
            var_202 = wp::dot(var_201, var_176);
            var_203 = wp::neg(var_202);
            var_205 = wp::extract(var_201, var_204);
            var_207 = wp::extract(var_201, var_206);
            var_209 = wp::extract(var_201, var_208);
            var_210 = wp::vec_t<4, wp::float64>(var_205, var_207, var_209, var_203);
            wp::assign_inplace(var_125, var_171, var_210);
            // if wp.abs(wp.dot(n,a[u])+d)<wp.float64(1e-8)*h:ok=False                            <L 41>
            var_211 = wp::extract(var_3, var_171);
            var_212 = wp::dot(var_201, var_211);
            var_213 = wp::add(var_212, var_203);
            var_214 = wp::abs(var_213);
            var_215 = 1e-08;
            var_216 = wp::mul(var_215, var_170);
            var_217 = (var_214 < var_216);
            if (var_217) {
            }
            var_219 = wp::where(var_217, var_218, var_128);
        }
        var_220 = wp::where(var_192, var_193, var_219);
        var_221 = wp::where(var_192, var_189, var_201);
        // p0=a[(u+1)%4];p1=a[(u+2)%4];p2=a[(u+3)%4];n=wp.cross(p1-p0,p2-p0);size=wp.length(n)       <L 35>
        var_224 = wp::add(var_222, var_223);
        var_226 = wp::mod(var_224, var_225);
        var_227 = wp::extract(var_3, var_226);
        var_229 = wp::add(var_222, var_228);
        var_231 = wp::mod(var_229, var_230);
        var_232 = wp::extract(var_3, var_231);
        var_234 = wp::add(var_222, var_233);
        var_236 = wp::mod(var_234, var_235);
        var_237 = wp::extract(var_3, var_236);
        var_238 = wp::sub(var_232, var_227);
        var_239 = wp::sub(var_237, var_227);
        var_240 = wp::cross(var_238, var_239);
        var_241 = wp::length(var_240);
        // if size==wp.float64(0.):ok=False                                                       <L 36>
        var_242 = 0.0;
        var_243 = (var_241 == var_242);
        if (var_243) {
        }
        if (!var_243) {
            // n=n/size                                                                           <L 38>
            var_245 = wp::div(var_240, var_241);
            // if wp.dot(n,a[u]-p0)>wp.float64(0.):n=-n                                           <L 39>
            var_246 = wp::extract(var_3, var_222);
            var_247 = wp::sub(var_246, var_227);
            var_248 = wp::dot(var_245, var_247);
            var_249 = 0.0;
            var_250 = (var_248 > var_249);
            if (var_250) {
                var_251 = wp::neg(var_245);
            }
            var_252 = wp::where(var_250, var_251, var_245);
            // d=-wp.dot(n,p0);pa[u]=wp.vec4d(n[0],n[1],n[2],d)                                   <L 40>
            var_253 = wp::dot(var_252, var_227);
            var_254 = wp::neg(var_253);
            var_256 = wp::extract(var_252, var_255);
            var_258 = wp::extract(var_252, var_257);
            var_260 = wp::extract(var_252, var_259);
            var_261 = wp::vec_t<4, wp::float64>(var_256, var_258, var_260, var_254);
            wp::assign_inplace(var_125, var_222, var_261);
            // if wp.abs(wp.dot(n,a[u])+d)<wp.float64(1e-8)*h:ok=False                            <L 41>
            var_262 = wp::extract(var_3, var_222);
            var_263 = wp::dot(var_252, var_262);
            var_264 = wp::add(var_263, var_254);
            var_265 = wp::abs(var_264);
            var_266 = 1e-08;
            var_267 = wp::mul(var_266, var_170);
            var_268 = (var_265 < var_267);
            if (var_268) {
            }
            var_270 = wp::where(var_268, var_269, var_220);
        }
        var_271 = wp::where(var_243, var_244, var_270);
        var_272 = wp::where(var_243, var_240, var_252);
        var_273 = wp::where(var_243, var_203, var_254);
        // p0=a[(u+1)%4];p1=a[(u+2)%4];p2=a[(u+3)%4];n=wp.cross(p1-p0,p2-p0);size=wp.length(n)       <L 35>
        var_276 = wp::add(var_274, var_275);
        var_278 = wp::mod(var_276, var_277);
        var_279 = wp::extract(var_3, var_278);
        var_281 = wp::add(var_274, var_280);
        var_283 = wp::mod(var_281, var_282);
        var_284 = wp::extract(var_3, var_283);
        var_286 = wp::add(var_274, var_285);
        var_288 = wp::mod(var_286, var_287);
        var_289 = wp::extract(var_3, var_288);
        var_290 = wp::sub(var_284, var_279);
        var_291 = wp::sub(var_289, var_279);
        var_292 = wp::cross(var_290, var_291);
        var_293 = wp::length(var_292);
        // if size==wp.float64(0.):ok=False                                                       <L 36>
        var_294 = 0.0;
        var_295 = (var_293 == var_294);
        if (var_295) {
        }
        if (!var_295) {
            // n=n/size                                                                           <L 38>
            var_297 = wp::div(var_292, var_293);
            // if wp.dot(n,a[u]-p0)>wp.float64(0.):n=-n                                           <L 39>
            var_298 = wp::extract(var_3, var_274);
            var_299 = wp::sub(var_298, var_279);
            var_300 = wp::dot(var_297, var_299);
            var_301 = 0.0;
            var_302 = (var_300 > var_301);
            if (var_302) {
                var_303 = wp::neg(var_297);
            }
            var_304 = wp::where(var_302, var_303, var_297);
            // d=-wp.dot(n,p0);pa[u]=wp.vec4d(n[0],n[1],n[2],d)                                   <L 40>
            var_305 = wp::dot(var_304, var_279);
            var_306 = wp::neg(var_305);
            var_308 = wp::extract(var_304, var_307);
            var_310 = wp::extract(var_304, var_309);
            var_312 = wp::extract(var_304, var_311);
            var_313 = wp::vec_t<4, wp::float64>(var_308, var_310, var_312, var_306);
            wp::assign_inplace(var_125, var_274, var_313);
            // if wp.abs(wp.dot(n,a[u])+d)<wp.float64(1e-8)*h:ok=False                            <L 41>
            var_314 = wp::extract(var_3, var_274);
            var_315 = wp::dot(var_304, var_314);
            var_316 = wp::add(var_315, var_306);
            var_317 = wp::abs(var_316);
            var_318 = 1e-08;
            var_319 = wp::mul(var_318, var_170);
            var_320 = (var_317 < var_319);
            if (var_320) {
            }
            var_322 = wp::where(var_320, var_321, var_271);
        }
        var_323 = wp::where(var_295, var_296, var_322);
        var_324 = wp::where(var_295, var_292, var_304);
        var_325 = wp::where(var_295, var_273, var_306);
        // p0=a[(u+1)%4];p1=a[(u+2)%4];p2=a[(u+3)%4];n=wp.cross(p1-p0,p2-p0);size=wp.length(n)       <L 35>
        var_328 = wp::add(var_326, var_327);
        var_330 = wp::mod(var_328, var_329);
        var_331 = wp::extract(var_3, var_330);
        var_333 = wp::add(var_326, var_332);
        var_335 = wp::mod(var_333, var_334);
        var_336 = wp::extract(var_3, var_335);
        var_338 = wp::add(var_326, var_337);
        var_340 = wp::mod(var_338, var_339);
        var_341 = wp::extract(var_3, var_340);
        var_342 = wp::sub(var_336, var_331);
        var_343 = wp::sub(var_341, var_331);
        var_344 = wp::cross(var_342, var_343);
        var_345 = wp::length(var_344);
        // if size==wp.float64(0.):ok=False                                                       <L 36>
        var_346 = 0.0;
        var_347 = (var_345 == var_346);
        if (var_347) {
        }
        if (!var_347) {
            // n=n/size                                                                           <L 38>
            var_349 = wp::div(var_344, var_345);
            // if wp.dot(n,a[u]-p0)>wp.float64(0.):n=-n                                           <L 39>
            var_350 = wp::extract(var_3, var_326);
            var_351 = wp::sub(var_350, var_331);
            var_352 = wp::dot(var_349, var_351);
            var_353 = 0.0;
            var_354 = (var_352 > var_353);
            if (var_354) {
                var_355 = wp::neg(var_349);
            }
            var_356 = wp::where(var_354, var_355, var_349);
            // d=-wp.dot(n,p0);pa[u]=wp.vec4d(n[0],n[1],n[2],d)                                   <L 40>
            var_357 = wp::dot(var_356, var_331);
            var_358 = wp::neg(var_357);
            var_360 = wp::extract(var_356, var_359);
            var_362 = wp::extract(var_356, var_361);
            var_364 = wp::extract(var_356, var_363);
            var_365 = wp::vec_t<4, wp::float64>(var_360, var_362, var_364, var_358);
            wp::assign_inplace(var_125, var_326, var_365);
            // if wp.abs(wp.dot(n,a[u])+d)<wp.float64(1e-8)*h:ok=False                            <L 41>
            var_366 = wp::extract(var_3, var_326);
            var_367 = wp::dot(var_356, var_366);
            var_368 = wp::add(var_367, var_358);
            var_369 = wp::abs(var_368);
            var_370 = 1e-08;
            var_371 = wp::mul(var_370, var_170);
            var_372 = (var_369 < var_371);
            if (var_372) {
            }
            var_374 = wp::where(var_372, var_373, var_323);
        }
        var_375 = wp::where(var_347, var_348, var_374);
        var_376 = wp::where(var_347, var_344, var_356);
        var_377 = wp::where(var_347, var_325, var_358);
        // if not ok:wp.atomic_max(unresolved,i,1);return                                         <L 42>
        var_378 = wp::unot(var_375);
        if (var_378) {
            var_380 = wp::atomic_max(var_unresolved, var_0, var_379);
            continue;
        }
        // pb=planes[c];points=M56(wp.float64(0.));count=int(0)                                   <L 43>
        var_381 = wp::address(var_planes, var_1);
        var_383 = wp::load(var_381);
        var_382 = wp::copy(var_383);
        var_384 = 0.0;
        var_385 = wp::mat_t<56, 3, wp::float64>(var_384);
        var_387 = wp::int(var_386);
        // for u in range(4):                                                                     <L 44>
        // if inside(a[u],pb):points[count]=a[u];count+=1                                         <L 45>
        var_389 = wp::extract(var_3, var_388);
        var_390 = inside_0(var_389, var_382);
        if (var_390) {
            var_391 = wp::extract(var_3, var_388);
            wp::assign_inplace(var_385, var_387, var_391);
            var_393 = wp::add(var_387, var_392);
        }
        var_394 = wp::where(var_390, var_393, var_387);
        // if inside(b[u],pa):points[count]=b[u];count+=1                                         <L 46>
        var_395 = wp::extract(var_6, var_388);
        var_396 = inside_0(var_395, var_125);
        if (var_396) {
            var_397 = wp::extract(var_6, var_388);
            wp::assign_inplace(var_385, var_394, var_397);
            var_399 = wp::add(var_394, var_398);
        }
        var_400 = wp::where(var_396, var_399, var_394);
        // if inside(a[u],pb):points[count]=a[u];count+=1                                         <L 45>
        var_402 = wp::extract(var_3, var_401);
        var_403 = inside_0(var_402, var_382);
        if (var_403) {
            var_404 = wp::extract(var_3, var_401);
            wp::assign_inplace(var_385, var_400, var_404);
            var_406 = wp::add(var_400, var_405);
        }
        var_407 = wp::where(var_403, var_406, var_400);
        // if inside(b[u],pa):points[count]=b[u];count+=1                                         <L 46>
        var_408 = wp::extract(var_6, var_401);
        var_409 = inside_0(var_408, var_125);
        if (var_409) {
            var_410 = wp::extract(var_6, var_401);
            wp::assign_inplace(var_385, var_407, var_410);
            var_412 = wp::add(var_407, var_411);
        }
        var_413 = wp::where(var_409, var_412, var_407);
        // if inside(a[u],pb):points[count]=a[u];count+=1                                         <L 45>
        var_415 = wp::extract(var_3, var_414);
        var_416 = inside_0(var_415, var_382);
        if (var_416) {
            var_417 = wp::extract(var_3, var_414);
            wp::assign_inplace(var_385, var_413, var_417);
            var_419 = wp::add(var_413, var_418);
        }
        var_420 = wp::where(var_416, var_419, var_413);
        // if inside(b[u],pa):points[count]=b[u];count+=1                                         <L 46>
        var_421 = wp::extract(var_6, var_414);
        var_422 = inside_0(var_421, var_125);
        if (var_422) {
            var_423 = wp::extract(var_6, var_414);
            wp::assign_inplace(var_385, var_420, var_423);
            var_425 = wp::add(var_420, var_424);
        }
        var_426 = wp::where(var_422, var_425, var_420);
        // if inside(a[u],pb):points[count]=a[u];count+=1                                         <L 45>
        var_428 = wp::extract(var_3, var_427);
        var_429 = inside_0(var_428, var_382);
        if (var_429) {
            var_430 = wp::extract(var_3, var_427);
            wp::assign_inplace(var_385, var_426, var_430);
            var_432 = wp::add(var_426, var_431);
        }
        var_433 = wp::where(var_429, var_432, var_426);
        // if inside(b[u],pa):points[count]=b[u];count+=1                                         <L 46>
        var_434 = wp::extract(var_6, var_427);
        var_435 = inside_0(var_434, var_125);
        if (var_435) {
            var_436 = wp::extract(var_6, var_427);
            wp::assign_inplace(var_385, var_433, var_436);
            var_438 = wp::add(var_433, var_437);
        }
        var_439 = wp::where(var_435, var_438, var_433);
        // for side in range(2):                                                                  <L 47>
        // vertices=a;other=pb;own=pa                                                             <L 48>
        var_441 = wp::copy(var_3);
        var_442 = wp::copy(var_382);
        var_443 = wp::copy(var_125);
        // if side==1:vertices=b;other=pa;own=pb                                                  <L 49>
        var_445 = (var_440 == var_444);
        if (var_445) {
            var_446 = wp::copy(var_6);
            var_447 = wp::copy(var_125);
            var_448 = wp::copy(var_382);
        }
        var_449 = wp::where(var_445, var_446, var_441);
        var_450 = wp::where(var_445, var_447, var_442);
        var_451 = wp::where(var_445, var_448, var_443);
        // for u in range(4):                                                                     <L 50>
        // for v in range(u):                                                                     <L 51>
        // for k in range(4):                                                                     <L 52>
        // d0=plane_value(vertices[u],other[k]);d1=plane_value(vertices[v],other[k])              <L 53>
        var_456 = wp::extract(var_449, var_453);
        var_457 = wp::extract(var_450, var_455);
        var_458 = plane_value_0(var_456, var_457);
        var_459 = wp::extract(var_449, var_454);
        var_460 = wp::extract(var_450, var_455);
        var_461 = plane_value_0(var_459, var_460);
        // if (d0<wp.float64(0.) and d1>wp.float64(0.)) or (d1<wp.float64(0.) and d0>wp.float64(0.)):       <L 54>
        var_464 = 0.0;
        var_465 = (var_458 < var_464);
        var_463 = var_465;
        if (var_463) {
            var_466 = 0.0;
            var_467 = (var_461 > var_466);
            var_463 = var_463 && var_467;
        }
        var_462 = var_463;
        if (!var_462) {
            var_469 = 0.0;
            var_470 = (var_461 < var_469);
            var_468 = var_470;
            if (var_468) {
                var_471 = 0.0;
                var_472 = (var_458 > var_471);
                var_468 = var_468 && var_472;
            }
            var_462 = var_462 || var_468;
        }
        if (var_462) {
            // point=vertices[u]+d0/(d0-d1)*(vertices[v]-vertices[u])                             <L 55>
            var_473 = wp::extract(var_449, var_453);
            var_474 = wp::sub(var_458, var_461);
            var_475 = wp::div(var_458, var_474);
            var_476 = wp::extract(var_449, var_454);
            var_477 = wp::extract(var_449, var_453);
            var_478 = wp::sub(var_476, var_477);
            var_479 = wp::mul(var_475, var_478);
            var_480 = wp::add(var_473, var_479);
            // if inside(point,other) and inside(point,own):points[count]=point;count+=1          <L 56>
            var_482 = inside_0(var_480, var_450);
            var_481 = var_482;
            if (var_481) {
                var_483 = inside_0(var_480, var_451);
                var_481 = var_481 && var_483;
            }
            if (var_481) {
                wp::assign_inplace(var_385, var_439, var_480);
                var_485 = wp::add(var_439, var_484);
            }
            var_486 = wp::where(var_481, var_485, var_439);
        }
        var_487 = wp::where(var_462, var_486, var_439);
        // d0=plane_value(vertices[u],other[k]);d1=plane_value(vertices[v],other[k])              <L 53>
        var_489 = wp::extract(var_449, var_453);
        var_490 = wp::extract(var_450, var_488);
        var_491 = plane_value_0(var_489, var_490);
        var_492 = wp::extract(var_449, var_454);
        var_493 = wp::extract(var_450, var_488);
        var_494 = plane_value_0(var_492, var_493);
        // if (d0<wp.float64(0.) and d1>wp.float64(0.)) or (d1<wp.float64(0.) and d0>wp.float64(0.)):       <L 54>
        var_497 = 0.0;
        var_498 = (var_491 < var_497);
        var_496 = var_498;
        if (var_496) {
            var_499 = 0.0;
            var_500 = (var_494 > var_499);
            var_496 = var_496 && var_500;
        }
        var_495 = var_496;
        if (!var_495) {
            var_502 = 0.0;
            var_503 = (var_494 < var_502);
            var_501 = var_503;
            if (var_501) {
                var_504 = 0.0;
                var_505 = (var_491 > var_504);
                var_501 = var_501 && var_505;
            }
            var_495 = var_495 || var_501;
        }
        if (var_495) {
            // point=vertices[u]+d0/(d0-d1)*(vertices[v]-vertices[u])                             <L 55>
            var_506 = wp::extract(var_449, var_453);
            var_507 = wp::sub(var_491, var_494);
            var_508 = wp::div(var_491, var_507);
            var_509 = wp::extract(var_449, var_454);
            var_510 = wp::extract(var_449, var_453);
            var_511 = wp::sub(var_509, var_510);
            var_512 = wp::mul(var_508, var_511);
            var_513 = wp::add(var_506, var_512);
            // if inside(point,other) and inside(point,own):points[count]=point;count+=1          <L 56>
            var_515 = inside_0(var_513, var_450);
            var_514 = var_515;
            if (var_514) {
                var_516 = inside_0(var_513, var_451);
                var_514 = var_514 && var_516;
            }
            if (var_514) {
                wp::assign_inplace(var_385, var_487, var_513);
                var_518 = wp::add(var_487, var_517);
            }
            var_519 = wp::where(var_514, var_518, var_487);
        }
        var_520 = wp::where(var_495, var_519, var_487);
        var_521 = wp::where(var_495, var_513, var_480);
        // d0=plane_value(vertices[u],other[k]);d1=plane_value(vertices[v],other[k])              <L 53>
        var_523 = wp::extract(var_449, var_453);
        var_524 = wp::extract(var_450, var_522);
        var_525 = plane_value_0(var_523, var_524);
        var_526 = wp::extract(var_449, var_454);
        var_527 = wp::extract(var_450, var_522);
        var_528 = plane_value_0(var_526, var_527);
        // if (d0<wp.float64(0.) and d1>wp.float64(0.)) or (d1<wp.float64(0.) and d0>wp.float64(0.)):       <L 54>
        var_531 = 0.0;
        var_532 = (var_525 < var_531);
        var_530 = var_532;
        if (var_530) {
            var_533 = 0.0;
            var_534 = (var_528 > var_533);
            var_530 = var_530 && var_534;
        }
        var_529 = var_530;
        if (!var_529) {
            var_536 = 0.0;
            var_537 = (var_528 < var_536);
            var_535 = var_537;
            if (var_535) {
                var_538 = 0.0;
                var_539 = (var_525 > var_538);
                var_535 = var_535 && var_539;
            }
            var_529 = var_529 || var_535;
        }
        if (var_529) {
            // point=vertices[u]+d0/(d0-d1)*(vertices[v]-vertices[u])                             <L 55>
            var_540 = wp::extract(var_449, var_453);
            var_541 = wp::sub(var_525, var_528);
            var_542 = wp::div(var_525, var_541);
            var_543 = wp::extract(var_449, var_454);
            var_544 = wp::extract(var_449, var_453);
            var_545 = wp::sub(var_543, var_544);
            var_546 = wp::mul(var_542, var_545);
            var_547 = wp::add(var_540, var_546);
            // if inside(point,other) and inside(point,own):points[count]=point;count+=1          <L 56>
            var_549 = inside_0(var_547, var_450);
            var_548 = var_549;
            if (var_548) {
                var_550 = inside_0(var_547, var_451);
                var_548 = var_548 && var_550;
            }
            if (var_548) {
                wp::assign_inplace(var_385, var_520, var_547);
                var_552 = wp::add(var_520, var_551);
            }
            var_553 = wp::where(var_548, var_552, var_520);
        }
        var_554 = wp::where(var_529, var_553, var_520);
        var_555 = wp::where(var_529, var_547, var_521);
        // d0=plane_value(vertices[u],other[k]);d1=plane_value(vertices[v],other[k])              <L 53>
        var_557 = wp::extract(var_449, var_453);
        var_558 = wp::extract(var_450, var_556);
        var_559 = plane_value_0(var_557, var_558);
        var_560 = wp::extract(var_449, var_454);
        var_561 = wp::extract(var_450, var_556);
        var_562 = plane_value_0(var_560, var_561);
        // if (d0<wp.float64(0.) and d1>wp.float64(0.)) or (d1<wp.float64(0.) and d0>wp.float64(0.)):       <L 54>
        var_565 = 0.0;
        var_566 = (var_559 < var_565);
        var_564 = var_566;
        if (var_564) {
            var_567 = 0.0;
            var_568 = (var_562 > var_567);
            var_564 = var_564 && var_568;
        }
        var_563 = var_564;
        if (!var_563) {
            var_570 = 0.0;
            var_571 = (var_562 < var_570);
            var_569 = var_571;
            if (var_569) {
                var_572 = 0.0;
                var_573 = (var_559 > var_572);
                var_569 = var_569 && var_573;
            }
            var_563 = var_563 || var_569;
        }
        if (var_563) {
            // point=vertices[u]+d0/(d0-d1)*(vertices[v]-vertices[u])                             <L 55>
            var_574 = wp::extract(var_449, var_453);
            var_575 = wp::sub(var_559, var_562);
            var_576 = wp::div(var_559, var_575);
            var_577 = wp::extract(var_449, var_454);
            var_578 = wp::extract(var_449, var_453);
            var_579 = wp::sub(var_577, var_578);
            var_580 = wp::mul(var_576, var_579);
            var_581 = wp::add(var_574, var_580);
            // if inside(point,other) and inside(point,own):points[count]=point;count+=1          <L 56>
            var_583 = inside_0(var_581, var_450);
            var_582 = var_583;
            if (var_582) {
                var_584 = inside_0(var_581, var_451);
                var_582 = var_582 && var_584;
            }
            if (var_582) {
                wp::assign_inplace(var_385, var_554, var_581);
                var_586 = wp::add(var_554, var_585);
            }
            var_587 = wp::where(var_582, var_586, var_554);
        }
        var_588 = wp::where(var_563, var_587, var_554);
        var_589 = wp::where(var_563, var_581, var_555);
        // for v in range(u):                                                                     <L 51>
        // for k in range(4):                                                                     <L 52>
        // d0=plane_value(vertices[u],other[k]);d1=plane_value(vertices[v],other[k])              <L 53>
        var_593 = wp::extract(var_449, var_590);
        var_594 = wp::extract(var_450, var_592);
        var_595 = plane_value_0(var_593, var_594);
        var_596 = wp::extract(var_449, var_591);
        var_597 = wp::extract(var_450, var_592);
        var_598 = plane_value_0(var_596, var_597);
        // if (d0<wp.float64(0.) and d1>wp.float64(0.)) or (d1<wp.float64(0.) and d0>wp.float64(0.)):       <L 54>
        var_601 = 0.0;
        var_602 = (var_595 < var_601);
        var_600 = var_602;
        if (var_600) {
            var_603 = 0.0;
            var_604 = (var_598 > var_603);
            var_600 = var_600 && var_604;
        }
        var_599 = var_600;
        if (!var_599) {
            var_606 = 0.0;
            var_607 = (var_598 < var_606);
            var_605 = var_607;
            if (var_605) {
                var_608 = 0.0;
                var_609 = (var_595 > var_608);
                var_605 = var_605 && var_609;
            }
            var_599 = var_599 || var_605;
        }
        if (var_599) {
            // point=vertices[u]+d0/(d0-d1)*(vertices[v]-vertices[u])                             <L 55>
            var_610 = wp::extract(var_449, var_590);
            var_611 = wp::sub(var_595, var_598);
            var_612 = wp::div(var_595, var_611);
            var_613 = wp::extract(var_449, var_591);
            var_614 = wp::extract(var_449, var_590);
            var_615 = wp::sub(var_613, var_614);
            var_616 = wp::mul(var_612, var_615);
            var_617 = wp::add(var_610, var_616);
            // if inside(point,other) and inside(point,own):points[count]=point;count+=1          <L 56>
            var_619 = inside_0(var_617, var_450);
            var_618 = var_619;
            if (var_618) {
                var_620 = inside_0(var_617, var_451);
                var_618 = var_618 && var_620;
            }
            if (var_618) {
                wp::assign_inplace(var_385, var_588, var_617);
                var_622 = wp::add(var_588, var_621);
            }
            var_623 = wp::where(var_618, var_622, var_588);
        }
        var_624 = wp::where(var_599, var_623, var_588);
        var_625 = wp::where(var_599, var_617, var_589);
        // d0=plane_value(vertices[u],other[k]);d1=plane_value(vertices[v],other[k])              <L 53>
        var_627 = wp::extract(var_449, var_590);
        var_628 = wp::extract(var_450, var_626);
        var_629 = plane_value_0(var_627, var_628);
        var_630 = wp::extract(var_449, var_591);
        var_631 = wp::extract(var_450, var_626);
        var_632 = plane_value_0(var_630, var_631);
        // if (d0<wp.float64(0.) and d1>wp.float64(0.)) or (d1<wp.float64(0.) and d0>wp.float64(0.)):       <L 54>
        var_635 = 0.0;
        var_636 = (var_629 < var_635);
        var_634 = var_636;
        if (var_634) {
            var_637 = 0.0;
            var_638 = (var_632 > var_637);
            var_634 = var_634 && var_638;
        }
        var_633 = var_634;
        if (!var_633) {
            var_640 = 0.0;
            var_641 = (var_632 < var_640);
            var_639 = var_641;
            if (var_639) {
                var_642 = 0.0;
                var_643 = (var_629 > var_642);
                var_639 = var_639 && var_643;
            }
            var_633 = var_633 || var_639;
        }
        if (var_633) {
            // point=vertices[u]+d0/(d0-d1)*(vertices[v]-vertices[u])                             <L 55>
            var_644 = wp::extract(var_449, var_590);
            var_645 = wp::sub(var_629, var_632);
            var_646 = wp::div(var_629, var_645);
            var_647 = wp::extract(var_449, var_591);
            var_648 = wp::extract(var_449, var_590);
            var_649 = wp::sub(var_647, var_648);
            var_650 = wp::mul(var_646, var_649);
            var_651 = wp::add(var_644, var_650);
            // if inside(point,other) and inside(point,own):points[count]=point;count+=1          <L 56>
            var_653 = inside_0(var_651, var_450);
            var_652 = var_653;
            if (var_652) {
                var_654 = inside_0(var_651, var_451);
                var_652 = var_652 && var_654;
            }
            if (var_652) {
                wp::assign_inplace(var_385, var_624, var_651);
                var_656 = wp::add(var_624, var_655);
            }
            var_657 = wp::where(var_652, var_656, var_624);
        }
        var_658 = wp::where(var_633, var_657, var_624);
        var_659 = wp::where(var_633, var_651, var_625);
        // d0=plane_value(vertices[u],other[k]);d1=plane_value(vertices[v],other[k])              <L 53>
        var_661 = wp::extract(var_449, var_590);
        var_662 = wp::extract(var_450, var_660);
        var_663 = plane_value_0(var_661, var_662);
        var_664 = wp::extract(var_449, var_591);
        var_665 = wp::extract(var_450, var_660);
        var_666 = plane_value_0(var_664, var_665);
        // if (d0<wp.float64(0.) and d1>wp.float64(0.)) or (d1<wp.float64(0.) and d0>wp.float64(0.)):       <L 54>
        var_669 = 0.0;
        var_670 = (var_663 < var_669);
        var_668 = var_670;
        if (var_668) {
            var_671 = 0.0;
            var_672 = (var_666 > var_671);
            var_668 = var_668 && var_672;
        }
        var_667 = var_668;
        if (!var_667) {
            var_674 = 0.0;
            var_675 = (var_666 < var_674);
            var_673 = var_675;
            if (var_673) {
                var_676 = 0.0;
                var_677 = (var_663 > var_676);
                var_673 = var_673 && var_677;
            }
            var_667 = var_667 || var_673;
        }
        if (var_667) {
            // point=vertices[u]+d0/(d0-d1)*(vertices[v]-vertices[u])                             <L 55>
            var_678 = wp::extract(var_449, var_590);
            var_679 = wp::sub(var_663, var_666);
            var_680 = wp::div(var_663, var_679);
            var_681 = wp::extract(var_449, var_591);
            var_682 = wp::extract(var_449, var_590);
            var_683 = wp::sub(var_681, var_682);
            var_684 = wp::mul(var_680, var_683);
            var_685 = wp::add(var_678, var_684);
            // if inside(point,other) and inside(point,own):points[count]=point;count+=1          <L 56>
            var_687 = inside_0(var_685, var_450);
            var_686 = var_687;
            if (var_686) {
                var_688 = inside_0(var_685, var_451);
                var_686 = var_686 && var_688;
            }
            if (var_686) {
                wp::assign_inplace(var_385, var_658, var_685);
                var_690 = wp::add(var_658, var_689);
            }
            var_691 = wp::where(var_686, var_690, var_658);
        }
        var_692 = wp::where(var_667, var_691, var_658);
        var_693 = wp::where(var_667, var_685, var_659);
        // d0=plane_value(vertices[u],other[k]);d1=plane_value(vertices[v],other[k])              <L 53>
        var_695 = wp::extract(var_449, var_590);
        var_696 = wp::extract(var_450, var_694);
        var_697 = plane_value_0(var_695, var_696);
        var_698 = wp::extract(var_449, var_591);
        var_699 = wp::extract(var_450, var_694);
        var_700 = plane_value_0(var_698, var_699);
        // if (d0<wp.float64(0.) and d1>wp.float64(0.)) or (d1<wp.float64(0.) and d0>wp.float64(0.)):       <L 54>
        var_703 = 0.0;
        var_704 = (var_697 < var_703);
        var_702 = var_704;
        if (var_702) {
            var_705 = 0.0;
            var_706 = (var_700 > var_705);
            var_702 = var_702 && var_706;
        }
        var_701 = var_702;
        if (!var_701) {
            var_708 = 0.0;
            var_709 = (var_700 < var_708);
            var_707 = var_709;
            if (var_707) {
                var_710 = 0.0;
                var_711 = (var_697 > var_710);
                var_707 = var_707 && var_711;
            }
            var_701 = var_701 || var_707;
        }
        if (var_701) {
            // point=vertices[u]+d0/(d0-d1)*(vertices[v]-vertices[u])                             <L 55>
            var_712 = wp::extract(var_449, var_590);
            var_713 = wp::sub(var_697, var_700);
            var_714 = wp::div(var_697, var_713);
            var_715 = wp::extract(var_449, var_591);
            var_716 = wp::extract(var_449, var_590);
            var_717 = wp::sub(var_715, var_716);
            var_718 = wp::mul(var_714, var_717);
            var_719 = wp::add(var_712, var_718);
            // if inside(point,other) and inside(point,own):points[count]=point;count+=1          <L 56>
            var_721 = inside_0(var_719, var_450);
            var_720 = var_721;
            if (var_720) {
                var_722 = inside_0(var_719, var_451);
                var_720 = var_720 && var_722;
            }
            if (var_720) {
                wp::assign_inplace(var_385, var_692, var_719);
                var_724 = wp::add(var_692, var_723);
            }
            var_725 = wp::where(var_720, var_724, var_692);
        }
        var_726 = wp::where(var_701, var_725, var_692);
        var_727 = wp::where(var_701, var_719, var_693);
        // for k in range(4):                                                                     <L 52>
        // d0=plane_value(vertices[u],other[k]);d1=plane_value(vertices[v],other[k])              <L 53>
        var_730 = wp::extract(var_449, var_590);
        var_731 = wp::extract(var_450, var_729);
        var_732 = plane_value_0(var_730, var_731);
        var_733 = wp::extract(var_449, var_728);
        var_734 = wp::extract(var_450, var_729);
        var_735 = plane_value_0(var_733, var_734);
        // if (d0<wp.float64(0.) and d1>wp.float64(0.)) or (d1<wp.float64(0.) and d0>wp.float64(0.)):       <L 54>
        var_738 = 0.0;
        var_739 = (var_732 < var_738);
        var_737 = var_739;
        if (var_737) {
            var_740 = 0.0;
            var_741 = (var_735 > var_740);
            var_737 = var_737 && var_741;
        }
        var_736 = var_737;
        if (!var_736) {
            var_743 = 0.0;
            var_744 = (var_735 < var_743);
            var_742 = var_744;
            if (var_742) {
                var_745 = 0.0;
                var_746 = (var_732 > var_745);
                var_742 = var_742 && var_746;
            }
            var_736 = var_736 || var_742;
        }
        if (var_736) {
            // point=vertices[u]+d0/(d0-d1)*(vertices[v]-vertices[u])                             <L 55>
            var_747 = wp::extract(var_449, var_590);
            var_748 = wp::sub(var_732, var_735);
            var_749 = wp::div(var_732, var_748);
            var_750 = wp::extract(var_449, var_728);
            var_751 = wp::extract(var_449, var_590);
            var_752 = wp::sub(var_750, var_751);
            var_753 = wp::mul(var_749, var_752);
            var_754 = wp::add(var_747, var_753);
            // if inside(point,other) and inside(point,own):points[count]=point;count+=1          <L 56>
            var_756 = inside_0(var_754, var_450);
            var_755 = var_756;
            if (var_755) {
                var_757 = inside_0(var_754, var_451);
                var_755 = var_755 && var_757;
            }
            if (var_755) {
                wp::assign_inplace(var_385, var_726, var_754);
                var_759 = wp::add(var_726, var_758);
            }
            var_760 = wp::where(var_755, var_759, var_726);
        }
        var_761 = wp::where(var_736, var_760, var_726);
        var_762 = wp::where(var_736, var_754, var_727);
        // d0=plane_value(vertices[u],other[k]);d1=plane_value(vertices[v],other[k])              <L 53>
        var_764 = wp::extract(var_449, var_590);
        var_765 = wp::extract(var_450, var_763);
        var_766 = plane_value_0(var_764, var_765);
        var_767 = wp::extract(var_449, var_728);
        var_768 = wp::extract(var_450, var_763);
        var_769 = plane_value_0(var_767, var_768);
        // if (d0<wp.float64(0.) and d1>wp.float64(0.)) or (d1<wp.float64(0.) and d0>wp.float64(0.)):       <L 54>
        var_772 = 0.0;
        var_773 = (var_766 < var_772);
        var_771 = var_773;
        if (var_771) {
            var_774 = 0.0;
            var_775 = (var_769 > var_774);
            var_771 = var_771 && var_775;
        }
        var_770 = var_771;
        if (!var_770) {
            var_777 = 0.0;
            var_778 = (var_769 < var_777);
            var_776 = var_778;
            if (var_776) {
                var_779 = 0.0;
                var_780 = (var_766 > var_779);
                var_776 = var_776 && var_780;
            }
            var_770 = var_770 || var_776;
        }
        if (var_770) {
            // point=vertices[u]+d0/(d0-d1)*(vertices[v]-vertices[u])                             <L 55>
            var_781 = wp::extract(var_449, var_590);
            var_782 = wp::sub(var_766, var_769);
            var_783 = wp::div(var_766, var_782);
            var_784 = wp::extract(var_449, var_728);
            var_785 = wp::extract(var_449, var_590);
            var_786 = wp::sub(var_784, var_785);
            var_787 = wp::mul(var_783, var_786);
            var_788 = wp::add(var_781, var_787);
            // if inside(point,other) and inside(point,own):points[count]=point;count+=1          <L 56>
            var_790 = inside_0(var_788, var_450);
            var_789 = var_790;
            if (var_789) {
                var_791 = inside_0(var_788, var_451);
                var_789 = var_789 && var_791;
            }
            if (var_789) {
                wp::assign_inplace(var_385, var_761, var_788);
                var_793 = wp::add(var_761, var_792);
            }
            var_794 = wp::where(var_789, var_793, var_761);
        }
        var_795 = wp::where(var_770, var_794, var_761);
        var_796 = wp::where(var_770, var_788, var_762);
        // d0=plane_value(vertices[u],other[k]);d1=plane_value(vertices[v],other[k])              <L 53>
        var_798 = wp::extract(var_449, var_590);
        var_799 = wp::extract(var_450, var_797);
        var_800 = plane_value_0(var_798, var_799);
        var_801 = wp::extract(var_449, var_728);
        var_802 = wp::extract(var_450, var_797);
        var_803 = plane_value_0(var_801, var_802);
        // if (d0<wp.float64(0.) and d1>wp.float64(0.)) or (d1<wp.float64(0.) and d0>wp.float64(0.)):       <L 54>
        var_806 = 0.0;
        var_807 = (var_800 < var_806);
        var_805 = var_807;
        if (var_805) {
            var_808 = 0.0;
            var_809 = (var_803 > var_808);
            var_805 = var_805 && var_809;
        }
        var_804 = var_805;
        if (!var_804) {
            var_811 = 0.0;
            var_812 = (var_803 < var_811);
            var_810 = var_812;
            if (var_810) {
                var_813 = 0.0;
                var_814 = (var_800 > var_813);
                var_810 = var_810 && var_814;
            }
            var_804 = var_804 || var_810;
        }
        if (var_804) {
            // point=vertices[u]+d0/(d0-d1)*(vertices[v]-vertices[u])                             <L 55>
            var_815 = wp::extract(var_449, var_590);
            var_816 = wp::sub(var_800, var_803);
            var_817 = wp::div(var_800, var_816);
            var_818 = wp::extract(var_449, var_728);
            var_819 = wp::extract(var_449, var_590);
            var_820 = wp::sub(var_818, var_819);
            var_821 = wp::mul(var_817, var_820);
            var_822 = wp::add(var_815, var_821);
            // if inside(point,other) and inside(point,own):points[count]=point;count+=1          <L 56>
            var_824 = inside_0(var_822, var_450);
            var_823 = var_824;
            if (var_823) {
                var_825 = inside_0(var_822, var_451);
                var_823 = var_823 && var_825;
            }
            if (var_823) {
                wp::assign_inplace(var_385, var_795, var_822);
                var_827 = wp::add(var_795, var_826);
            }
            var_828 = wp::where(var_823, var_827, var_795);
        }
        var_829 = wp::where(var_804, var_828, var_795);
        var_830 = wp::where(var_804, var_822, var_796);
        // d0=plane_value(vertices[u],other[k]);d1=plane_value(vertices[v],other[k])              <L 53>
        var_832 = wp::extract(var_449, var_590);
        var_833 = wp::extract(var_450, var_831);
        var_834 = plane_value_0(var_832, var_833);
        var_835 = wp::extract(var_449, var_728);
        var_836 = wp::extract(var_450, var_831);
        var_837 = plane_value_0(var_835, var_836);
        // if (d0<wp.float64(0.) and d1>wp.float64(0.)) or (d1<wp.float64(0.) and d0>wp.float64(0.)):       <L 54>
        var_840 = 0.0;
        var_841 = (var_834 < var_840);
        var_839 = var_841;
        if (var_839) {
            var_842 = 0.0;
            var_843 = (var_837 > var_842);
            var_839 = var_839 && var_843;
        }
        var_838 = var_839;
        if (!var_838) {
            var_845 = 0.0;
            var_846 = (var_837 < var_845);
            var_844 = var_846;
            if (var_844) {
                var_847 = 0.0;
                var_848 = (var_834 > var_847);
                var_844 = var_844 && var_848;
            }
            var_838 = var_838 || var_844;
        }
        if (var_838) {
            // point=vertices[u]+d0/(d0-d1)*(vertices[v]-vertices[u])                             <L 55>
            var_849 = wp::extract(var_449, var_590);
            var_850 = wp::sub(var_834, var_837);
            var_851 = wp::div(var_834, var_850);
            var_852 = wp::extract(var_449, var_728);
            var_853 = wp::extract(var_449, var_590);
            var_854 = wp::sub(var_852, var_853);
            var_855 = wp::mul(var_851, var_854);
            var_856 = wp::add(var_849, var_855);
            // if inside(point,other) and inside(point,own):points[count]=point;count+=1          <L 56>
            var_858 = inside_0(var_856, var_450);
            var_857 = var_858;
            if (var_857) {
                var_859 = inside_0(var_856, var_451);
                var_857 = var_857 && var_859;
            }
            if (var_857) {
                wp::assign_inplace(var_385, var_829, var_856);
                var_861 = wp::add(var_829, var_860);
            }
            var_862 = wp::where(var_857, var_861, var_829);
        }
        var_863 = wp::where(var_838, var_862, var_829);
        var_864 = wp::where(var_838, var_856, var_830);
        // for v in range(u):                                                                     <L 51>
        // for k in range(4):                                                                     <L 52>
        // d0=plane_value(vertices[u],other[k]);d1=plane_value(vertices[v],other[k])              <L 53>
        var_868 = wp::extract(var_449, var_865);
        var_869 = wp::extract(var_450, var_867);
        var_870 = plane_value_0(var_868, var_869);
        var_871 = wp::extract(var_449, var_866);
        var_872 = wp::extract(var_450, var_867);
        var_873 = plane_value_0(var_871, var_872);
        // if (d0<wp.float64(0.) and d1>wp.float64(0.)) or (d1<wp.float64(0.) and d0>wp.float64(0.)):       <L 54>
        var_876 = 0.0;
        var_877 = (var_870 < var_876);
        var_875 = var_877;
        if (var_875) {
            var_878 = 0.0;
            var_879 = (var_873 > var_878);
            var_875 = var_875 && var_879;
        }
        var_874 = var_875;
        if (!var_874) {
            var_881 = 0.0;
            var_882 = (var_873 < var_881);
            var_880 = var_882;
            if (var_880) {
                var_883 = 0.0;
                var_884 = (var_870 > var_883);
                var_880 = var_880 && var_884;
            }
            var_874 = var_874 || var_880;
        }
        if (var_874) {
            // point=vertices[u]+d0/(d0-d1)*(vertices[v]-vertices[u])                             <L 55>
            var_885 = wp::extract(var_449, var_865);
            var_886 = wp::sub(var_870, var_873);
            var_887 = wp::div(var_870, var_886);
            var_888 = wp::extract(var_449, var_866);
            var_889 = wp::extract(var_449, var_865);
            var_890 = wp::sub(var_888, var_889);
            var_891 = wp::mul(var_887, var_890);
            var_892 = wp::add(var_885, var_891);
            // if inside(point,other) and inside(point,own):points[count]=point;count+=1          <L 56>
            var_894 = inside_0(var_892, var_450);
            var_893 = var_894;
            if (var_893) {
                var_895 = inside_0(var_892, var_451);
                var_893 = var_893 && var_895;
            }
            if (var_893) {
                wp::assign_inplace(var_385, var_863, var_892);
                var_897 = wp::add(var_863, var_896);
            }
            var_898 = wp::where(var_893, var_897, var_863);
        }
        var_899 = wp::where(var_874, var_898, var_863);
        var_900 = wp::where(var_874, var_892, var_864);
        // d0=plane_value(vertices[u],other[k]);d1=plane_value(vertices[v],other[k])              <L 53>
        var_902 = wp::extract(var_449, var_865);
        var_903 = wp::extract(var_450, var_901);
        var_904 = plane_value_0(var_902, var_903);
        var_905 = wp::extract(var_449, var_866);
        var_906 = wp::extract(var_450, var_901);
        var_907 = plane_value_0(var_905, var_906);
        // if (d0<wp.float64(0.) and d1>wp.float64(0.)) or (d1<wp.float64(0.) and d0>wp.float64(0.)):       <L 54>
        var_910 = 0.0;
        var_911 = (var_904 < var_910);
        var_909 = var_911;
        if (var_909) {
            var_912 = 0.0;
            var_913 = (var_907 > var_912);
            var_909 = var_909 && var_913;
        }
        var_908 = var_909;
        if (!var_908) {
            var_915 = 0.0;
            var_916 = (var_907 < var_915);
            var_914 = var_916;
            if (var_914) {
                var_917 = 0.0;
                var_918 = (var_904 > var_917);
                var_914 = var_914 && var_918;
            }
            var_908 = var_908 || var_914;
        }
        if (var_908) {
            // point=vertices[u]+d0/(d0-d1)*(vertices[v]-vertices[u])                             <L 55>
            var_919 = wp::extract(var_449, var_865);
            var_920 = wp::sub(var_904, var_907);
            var_921 = wp::div(var_904, var_920);
            var_922 = wp::extract(var_449, var_866);
            var_923 = wp::extract(var_449, var_865);
            var_924 = wp::sub(var_922, var_923);
            var_925 = wp::mul(var_921, var_924);
            var_926 = wp::add(var_919, var_925);
            // if inside(point,other) and inside(point,own):points[count]=point;count+=1          <L 56>
            var_928 = inside_0(var_926, var_450);
            var_927 = var_928;
            if (var_927) {
                var_929 = inside_0(var_926, var_451);
                var_927 = var_927 && var_929;
            }
            if (var_927) {
                wp::assign_inplace(var_385, var_899, var_926);
                var_931 = wp::add(var_899, var_930);
            }
            var_932 = wp::where(var_927, var_931, var_899);
        }
        var_933 = wp::where(var_908, var_932, var_899);
        var_934 = wp::where(var_908, var_926, var_900);
        // d0=plane_value(vertices[u],other[k]);d1=plane_value(vertices[v],other[k])              <L 53>
        var_936 = wp::extract(var_449, var_865);
        var_937 = wp::extract(var_450, var_935);
        var_938 = plane_value_0(var_936, var_937);
        var_939 = wp::extract(var_449, var_866);
        var_940 = wp::extract(var_450, var_935);
        var_941 = plane_value_0(var_939, var_940);
        // if (d0<wp.float64(0.) and d1>wp.float64(0.)) or (d1<wp.float64(0.) and d0>wp.float64(0.)):       <L 54>
        var_944 = 0.0;
        var_945 = (var_938 < var_944);
        var_943 = var_945;
        if (var_943) {
            var_946 = 0.0;
            var_947 = (var_941 > var_946);
            var_943 = var_943 && var_947;
        }
        var_942 = var_943;
        if (!var_942) {
            var_949 = 0.0;
            var_950 = (var_941 < var_949);
            var_948 = var_950;
            if (var_948) {
                var_951 = 0.0;
                var_952 = (var_938 > var_951);
                var_948 = var_948 && var_952;
            }
            var_942 = var_942 || var_948;
        }
        if (var_942) {
            // point=vertices[u]+d0/(d0-d1)*(vertices[v]-vertices[u])                             <L 55>
            var_953 = wp::extract(var_449, var_865);
            var_954 = wp::sub(var_938, var_941);
            var_955 = wp::div(var_938, var_954);
            var_956 = wp::extract(var_449, var_866);
            var_957 = wp::extract(var_449, var_865);
            var_958 = wp::sub(var_956, var_957);
            var_959 = wp::mul(var_955, var_958);
            var_960 = wp::add(var_953, var_959);
            // if inside(point,other) and inside(point,own):points[count]=point;count+=1          <L 56>
            var_962 = inside_0(var_960, var_450);
            var_961 = var_962;
            if (var_961) {
                var_963 = inside_0(var_960, var_451);
                var_961 = var_961 && var_963;
            }
            if (var_961) {
                wp::assign_inplace(var_385, var_933, var_960);
                var_965 = wp::add(var_933, var_964);
            }
            var_966 = wp::where(var_961, var_965, var_933);
        }
        var_967 = wp::where(var_942, var_966, var_933);
        var_968 = wp::where(var_942, var_960, var_934);
        // d0=plane_value(vertices[u],other[k]);d1=plane_value(vertices[v],other[k])              <L 53>
        var_970 = wp::extract(var_449, var_865);
        var_971 = wp::extract(var_450, var_969);
        var_972 = plane_value_0(var_970, var_971);
        var_973 = wp::extract(var_449, var_866);
        var_974 = wp::extract(var_450, var_969);
        var_975 = plane_value_0(var_973, var_974);
        // if (d0<wp.float64(0.) and d1>wp.float64(0.)) or (d1<wp.float64(0.) and d0>wp.float64(0.)):       <L 54>
        var_978 = 0.0;
        var_979 = (var_972 < var_978);
        var_977 = var_979;
        if (var_977) {
            var_980 = 0.0;
            var_981 = (var_975 > var_980);
            var_977 = var_977 && var_981;
        }
        var_976 = var_977;
        if (!var_976) {
            var_983 = 0.0;
            var_984 = (var_975 < var_983);
            var_982 = var_984;
            if (var_982) {
                var_985 = 0.0;
                var_986 = (var_972 > var_985);
                var_982 = var_982 && var_986;
            }
            var_976 = var_976 || var_982;
        }
        if (var_976) {
            // point=vertices[u]+d0/(d0-d1)*(vertices[v]-vertices[u])                             <L 55>
            var_987 = wp::extract(var_449, var_865);
            var_988 = wp::sub(var_972, var_975);
            var_989 = wp::div(var_972, var_988);
            var_990 = wp::extract(var_449, var_866);
            var_991 = wp::extract(var_449, var_865);
            var_992 = wp::sub(var_990, var_991);
            var_993 = wp::mul(var_989, var_992);
            var_994 = wp::add(var_987, var_993);
            // if inside(point,other) and inside(point,own):points[count]=point;count+=1          <L 56>
            var_996 = inside_0(var_994, var_450);
            var_995 = var_996;
            if (var_995) {
                var_997 = inside_0(var_994, var_451);
                var_995 = var_995 && var_997;
            }
            if (var_995) {
                wp::assign_inplace(var_385, var_967, var_994);
                var_999 = wp::add(var_967, var_998);
            }
            var_1000 = wp::where(var_995, var_999, var_967);
        }
        var_1001 = wp::where(var_976, var_1000, var_967);
        var_1002 = wp::where(var_976, var_994, var_968);
        // for k in range(4):                                                                     <L 52>
        // d0=plane_value(vertices[u],other[k]);d1=plane_value(vertices[v],other[k])              <L 53>
        var_1005 = wp::extract(var_449, var_865);
        var_1006 = wp::extract(var_450, var_1004);
        var_1007 = plane_value_0(var_1005, var_1006);
        var_1008 = wp::extract(var_449, var_1003);
        var_1009 = wp::extract(var_450, var_1004);
        var_1010 = plane_value_0(var_1008, var_1009);
        // if (d0<wp.float64(0.) and d1>wp.float64(0.)) or (d1<wp.float64(0.) and d0>wp.float64(0.)):       <L 54>
        var_1013 = 0.0;
        var_1014 = (var_1007 < var_1013);
        var_1012 = var_1014;
        if (var_1012) {
            var_1015 = 0.0;
            var_1016 = (var_1010 > var_1015);
            var_1012 = var_1012 && var_1016;
        }
        var_1011 = var_1012;
        if (!var_1011) {
            var_1018 = 0.0;
            var_1019 = (var_1010 < var_1018);
            var_1017 = var_1019;
            if (var_1017) {
                var_1020 = 0.0;
                var_1021 = (var_1007 > var_1020);
                var_1017 = var_1017 && var_1021;
            }
            var_1011 = var_1011 || var_1017;
        }
        if (var_1011) {
            // point=vertices[u]+d0/(d0-d1)*(vertices[v]-vertices[u])                             <L 55>
            var_1022 = wp::extract(var_449, var_865);
            var_1023 = wp::sub(var_1007, var_1010);
            var_1024 = wp::div(var_1007, var_1023);
            var_1025 = wp::extract(var_449, var_1003);
            var_1026 = wp::extract(var_449, var_865);
            var_1027 = wp::sub(var_1025, var_1026);
            var_1028 = wp::mul(var_1024, var_1027);
            var_1029 = wp::add(var_1022, var_1028);
            // if inside(point,other) and inside(point,own):points[count]=point;count+=1          <L 56>
            var_1031 = inside_0(var_1029, var_450);
            var_1030 = var_1031;
            if (var_1030) {
                var_1032 = inside_0(var_1029, var_451);
                var_1030 = var_1030 && var_1032;
            }
            if (var_1030) {
                wp::assign_inplace(var_385, var_1001, var_1029);
                var_1034 = wp::add(var_1001, var_1033);
            }
            var_1035 = wp::where(var_1030, var_1034, var_1001);
        }
        var_1036 = wp::where(var_1011, var_1035, var_1001);
        var_1037 = wp::where(var_1011, var_1029, var_1002);
        // d0=plane_value(vertices[u],other[k]);d1=plane_value(vertices[v],other[k])              <L 53>
        var_1039 = wp::extract(var_449, var_865);
        var_1040 = wp::extract(var_450, var_1038);
        var_1041 = plane_value_0(var_1039, var_1040);
        var_1042 = wp::extract(var_449, var_1003);
        var_1043 = wp::extract(var_450, var_1038);
        var_1044 = plane_value_0(var_1042, var_1043);
        // if (d0<wp.float64(0.) and d1>wp.float64(0.)) or (d1<wp.float64(0.) and d0>wp.float64(0.)):       <L 54>
        var_1047 = 0.0;
        var_1048 = (var_1041 < var_1047);
        var_1046 = var_1048;
        if (var_1046) {
            var_1049 = 0.0;
            var_1050 = (var_1044 > var_1049);
            var_1046 = var_1046 && var_1050;
        }
        var_1045 = var_1046;
        if (!var_1045) {
            var_1052 = 0.0;
            var_1053 = (var_1044 < var_1052);
            var_1051 = var_1053;
            if (var_1051) {
                var_1054 = 0.0;
                var_1055 = (var_1041 > var_1054);
                var_1051 = var_1051 && var_1055;
            }
            var_1045 = var_1045 || var_1051;
        }
        if (var_1045) {
            // point=vertices[u]+d0/(d0-d1)*(vertices[v]-vertices[u])                             <L 55>
            var_1056 = wp::extract(var_449, var_865);
            var_1057 = wp::sub(var_1041, var_1044);
            var_1058 = wp::div(var_1041, var_1057);
            var_1059 = wp::extract(var_449, var_1003);
            var_1060 = wp::extract(var_449, var_865);
            var_1061 = wp::sub(var_1059, var_1060);
            var_1062 = wp::mul(var_1058, var_1061);
            var_1063 = wp::add(var_1056, var_1062);
            // if inside(point,other) and inside(point,own):points[count]=point;count+=1          <L 56>
            var_1065 = inside_0(var_1063, var_450);
            var_1064 = var_1065;
            if (var_1064) {
                var_1066 = inside_0(var_1063, var_451);
                var_1064 = var_1064 && var_1066;
            }
            if (var_1064) {
                wp::assign_inplace(var_385, var_1036, var_1063);
                var_1068 = wp::add(var_1036, var_1067);
            }
            var_1069 = wp::where(var_1064, var_1068, var_1036);
        }
        var_1070 = wp::where(var_1045, var_1069, var_1036);
        var_1071 = wp::where(var_1045, var_1063, var_1037);
        // d0=plane_value(vertices[u],other[k]);d1=plane_value(vertices[v],other[k])              <L 53>
        var_1073 = wp::extract(var_449, var_865);
        var_1074 = wp::extract(var_450, var_1072);
        var_1075 = plane_value_0(var_1073, var_1074);
        var_1076 = wp::extract(var_449, var_1003);
        var_1077 = wp::extract(var_450, var_1072);
        var_1078 = plane_value_0(var_1076, var_1077);
        // if (d0<wp.float64(0.) and d1>wp.float64(0.)) or (d1<wp.float64(0.) and d0>wp.float64(0.)):       <L 54>
        var_1081 = 0.0;
        var_1082 = (var_1075 < var_1081);
        var_1080 = var_1082;
        if (var_1080) {
            var_1083 = 0.0;
            var_1084 = (var_1078 > var_1083);
            var_1080 = var_1080 && var_1084;
        }
        var_1079 = var_1080;
        if (!var_1079) {
            var_1086 = 0.0;
            var_1087 = (var_1078 < var_1086);
            var_1085 = var_1087;
            if (var_1085) {
                var_1088 = 0.0;
                var_1089 = (var_1075 > var_1088);
                var_1085 = var_1085 && var_1089;
            }
            var_1079 = var_1079 || var_1085;
        }
        if (var_1079) {
            // point=vertices[u]+d0/(d0-d1)*(vertices[v]-vertices[u])                             <L 55>
            var_1090 = wp::extract(var_449, var_865);
            var_1091 = wp::sub(var_1075, var_1078);
            var_1092 = wp::div(var_1075, var_1091);
            var_1093 = wp::extract(var_449, var_1003);
            var_1094 = wp::extract(var_449, var_865);
            var_1095 = wp::sub(var_1093, var_1094);
            var_1096 = wp::mul(var_1092, var_1095);
            var_1097 = wp::add(var_1090, var_1096);
            // if inside(point,other) and inside(point,own):points[count]=point;count+=1          <L 56>
            var_1099 = inside_0(var_1097, var_450);
            var_1098 = var_1099;
            if (var_1098) {
                var_1100 = inside_0(var_1097, var_451);
                var_1098 = var_1098 && var_1100;
            }
            if (var_1098) {
                wp::assign_inplace(var_385, var_1070, var_1097);
                var_1102 = wp::add(var_1070, var_1101);
            }
            var_1103 = wp::where(var_1098, var_1102, var_1070);
        }
        var_1104 = wp::where(var_1079, var_1103, var_1070);
        var_1105 = wp::where(var_1079, var_1097, var_1071);
        // d0=plane_value(vertices[u],other[k]);d1=plane_value(vertices[v],other[k])              <L 53>
        var_1107 = wp::extract(var_449, var_865);
        var_1108 = wp::extract(var_450, var_1106);
        var_1109 = plane_value_0(var_1107, var_1108);
        var_1110 = wp::extract(var_449, var_1003);
        var_1111 = wp::extract(var_450, var_1106);
        var_1112 = plane_value_0(var_1110, var_1111);
        // if (d0<wp.float64(0.) and d1>wp.float64(0.)) or (d1<wp.float64(0.) and d0>wp.float64(0.)):       <L 54>
        var_1115 = 0.0;
        var_1116 = (var_1109 < var_1115);
        var_1114 = var_1116;
        if (var_1114) {
            var_1117 = 0.0;
            var_1118 = (var_1112 > var_1117);
            var_1114 = var_1114 && var_1118;
        }
        var_1113 = var_1114;
        if (!var_1113) {
            var_1120 = 0.0;
            var_1121 = (var_1112 < var_1120);
            var_1119 = var_1121;
            if (var_1119) {
                var_1122 = 0.0;
                var_1123 = (var_1109 > var_1122);
                var_1119 = var_1119 && var_1123;
            }
            var_1113 = var_1113 || var_1119;
        }
        if (var_1113) {
            // point=vertices[u]+d0/(d0-d1)*(vertices[v]-vertices[u])                             <L 55>
            var_1124 = wp::extract(var_449, var_865);
            var_1125 = wp::sub(var_1109, var_1112);
            var_1126 = wp::div(var_1109, var_1125);
            var_1127 = wp::extract(var_449, var_1003);
            var_1128 = wp::extract(var_449, var_865);
            var_1129 = wp::sub(var_1127, var_1128);
            var_1130 = wp::mul(var_1126, var_1129);
            var_1131 = wp::add(var_1124, var_1130);
            // if inside(point,other) and inside(point,own):points[count]=point;count+=1          <L 56>
            var_1133 = inside_0(var_1131, var_450);
            var_1132 = var_1133;
            if (var_1132) {
                var_1134 = inside_0(var_1131, var_451);
                var_1132 = var_1132 && var_1134;
            }
            if (var_1132) {
                wp::assign_inplace(var_385, var_1104, var_1131);
                var_1136 = wp::add(var_1104, var_1135);
            }
            var_1137 = wp::where(var_1132, var_1136, var_1104);
        }
        var_1138 = wp::where(var_1113, var_1137, var_1104);
        var_1139 = wp::where(var_1113, var_1131, var_1105);
        // for k in range(4):                                                                     <L 52>
        // d0=plane_value(vertices[u],other[k]);d1=plane_value(vertices[v],other[k])              <L 53>
        var_1142 = wp::extract(var_449, var_865);
        var_1143 = wp::extract(var_450, var_1141);
        var_1144 = plane_value_0(var_1142, var_1143);
        var_1145 = wp::extract(var_449, var_1140);
        var_1146 = wp::extract(var_450, var_1141);
        var_1147 = plane_value_0(var_1145, var_1146);
        // if (d0<wp.float64(0.) and d1>wp.float64(0.)) or (d1<wp.float64(0.) and d0>wp.float64(0.)):       <L 54>
        var_1150 = 0.0;
        var_1151 = (var_1144 < var_1150);
        var_1149 = var_1151;
        if (var_1149) {
            var_1152 = 0.0;
            var_1153 = (var_1147 > var_1152);
            var_1149 = var_1149 && var_1153;
        }
        var_1148 = var_1149;
        if (!var_1148) {
            var_1155 = 0.0;
            var_1156 = (var_1147 < var_1155);
            var_1154 = var_1156;
            if (var_1154) {
                var_1157 = 0.0;
                var_1158 = (var_1144 > var_1157);
                var_1154 = var_1154 && var_1158;
            }
            var_1148 = var_1148 || var_1154;
        }
        if (var_1148) {
            // point=vertices[u]+d0/(d0-d1)*(vertices[v]-vertices[u])                             <L 55>
            var_1159 = wp::extract(var_449, var_865);
            var_1160 = wp::sub(var_1144, var_1147);
            var_1161 = wp::div(var_1144, var_1160);
            var_1162 = wp::extract(var_449, var_1140);
            var_1163 = wp::extract(var_449, var_865);
            var_1164 = wp::sub(var_1162, var_1163);
            var_1165 = wp::mul(var_1161, var_1164);
            var_1166 = wp::add(var_1159, var_1165);
            // if inside(point,other) and inside(point,own):points[count]=point;count+=1          <L 56>
            var_1168 = inside_0(var_1166, var_450);
            var_1167 = var_1168;
            if (var_1167) {
                var_1169 = inside_0(var_1166, var_451);
                var_1167 = var_1167 && var_1169;
            }
            if (var_1167) {
                wp::assign_inplace(var_385, var_1138, var_1166);
                var_1171 = wp::add(var_1138, var_1170);
            }
            var_1172 = wp::where(var_1167, var_1171, var_1138);
        }
        var_1173 = wp::where(var_1148, var_1172, var_1138);
        var_1174 = wp::where(var_1148, var_1166, var_1139);
        // d0=plane_value(vertices[u],other[k]);d1=plane_value(vertices[v],other[k])              <L 53>
        var_1176 = wp::extract(var_449, var_865);
        var_1177 = wp::extract(var_450, var_1175);
        var_1178 = plane_value_0(var_1176, var_1177);
        var_1179 = wp::extract(var_449, var_1140);
        var_1180 = wp::extract(var_450, var_1175);
        var_1181 = plane_value_0(var_1179, var_1180);
        // if (d0<wp.float64(0.) and d1>wp.float64(0.)) or (d1<wp.float64(0.) and d0>wp.float64(0.)):       <L 54>
        var_1184 = 0.0;
        var_1185 = (var_1178 < var_1184);
        var_1183 = var_1185;
        if (var_1183) {
            var_1186 = 0.0;
            var_1187 = (var_1181 > var_1186);
            var_1183 = var_1183 && var_1187;
        }
        var_1182 = var_1183;
        if (!var_1182) {
            var_1189 = 0.0;
            var_1190 = (var_1181 < var_1189);
            var_1188 = var_1190;
            if (var_1188) {
                var_1191 = 0.0;
                var_1192 = (var_1178 > var_1191);
                var_1188 = var_1188 && var_1192;
            }
            var_1182 = var_1182 || var_1188;
        }
        if (var_1182) {
            // point=vertices[u]+d0/(d0-d1)*(vertices[v]-vertices[u])                             <L 55>
            var_1193 = wp::extract(var_449, var_865);
            var_1194 = wp::sub(var_1178, var_1181);
            var_1195 = wp::div(var_1178, var_1194);
            var_1196 = wp::extract(var_449, var_1140);
            var_1197 = wp::extract(var_449, var_865);
            var_1198 = wp::sub(var_1196, var_1197);
            var_1199 = wp::mul(var_1195, var_1198);
            var_1200 = wp::add(var_1193, var_1199);
            // if inside(point,other) and inside(point,own):points[count]=point;count+=1          <L 56>
            var_1202 = inside_0(var_1200, var_450);
            var_1201 = var_1202;
            if (var_1201) {
                var_1203 = inside_0(var_1200, var_451);
                var_1201 = var_1201 && var_1203;
            }
            if (var_1201) {
                wp::assign_inplace(var_385, var_1173, var_1200);
                var_1205 = wp::add(var_1173, var_1204);
            }
            var_1206 = wp::where(var_1201, var_1205, var_1173);
        }
        var_1207 = wp::where(var_1182, var_1206, var_1173);
        var_1208 = wp::where(var_1182, var_1200, var_1174);
        // d0=plane_value(vertices[u],other[k]);d1=plane_value(vertices[v],other[k])              <L 53>
        var_1210 = wp::extract(var_449, var_865);
        var_1211 = wp::extract(var_450, var_1209);
        var_1212 = plane_value_0(var_1210, var_1211);
        var_1213 = wp::extract(var_449, var_1140);
        var_1214 = wp::extract(var_450, var_1209);
        var_1215 = plane_value_0(var_1213, var_1214);
        // if (d0<wp.float64(0.) and d1>wp.float64(0.)) or (d1<wp.float64(0.) and d0>wp.float64(0.)):       <L 54>
        var_1218 = 0.0;
        var_1219 = (var_1212 < var_1218);
        var_1217 = var_1219;
        if (var_1217) {
            var_1220 = 0.0;
            var_1221 = (var_1215 > var_1220);
            var_1217 = var_1217 && var_1221;
        }
        var_1216 = var_1217;
        if (!var_1216) {
            var_1223 = 0.0;
            var_1224 = (var_1215 < var_1223);
            var_1222 = var_1224;
            if (var_1222) {
                var_1225 = 0.0;
                var_1226 = (var_1212 > var_1225);
                var_1222 = var_1222 && var_1226;
            }
            var_1216 = var_1216 || var_1222;
        }
        if (var_1216) {
            // point=vertices[u]+d0/(d0-d1)*(vertices[v]-vertices[u])                             <L 55>
            var_1227 = wp::extract(var_449, var_865);
            var_1228 = wp::sub(var_1212, var_1215);
            var_1229 = wp::div(var_1212, var_1228);
            var_1230 = wp::extract(var_449, var_1140);
            var_1231 = wp::extract(var_449, var_865);
            var_1232 = wp::sub(var_1230, var_1231);
            var_1233 = wp::mul(var_1229, var_1232);
            var_1234 = wp::add(var_1227, var_1233);
            // if inside(point,other) and inside(point,own):points[count]=point;count+=1          <L 56>
            var_1236 = inside_0(var_1234, var_450);
            var_1235 = var_1236;
            if (var_1235) {
                var_1237 = inside_0(var_1234, var_451);
                var_1235 = var_1235 && var_1237;
            }
            if (var_1235) {
                wp::assign_inplace(var_385, var_1207, var_1234);
                var_1239 = wp::add(var_1207, var_1238);
            }
            var_1240 = wp::where(var_1235, var_1239, var_1207);
        }
        var_1241 = wp::where(var_1216, var_1240, var_1207);
        var_1242 = wp::where(var_1216, var_1234, var_1208);
        // d0=plane_value(vertices[u],other[k]);d1=plane_value(vertices[v],other[k])              <L 53>
        var_1244 = wp::extract(var_449, var_865);
        var_1245 = wp::extract(var_450, var_1243);
        var_1246 = plane_value_0(var_1244, var_1245);
        var_1247 = wp::extract(var_449, var_1140);
        var_1248 = wp::extract(var_450, var_1243);
        var_1249 = plane_value_0(var_1247, var_1248);
        // if (d0<wp.float64(0.) and d1>wp.float64(0.)) or (d1<wp.float64(0.) and d0>wp.float64(0.)):       <L 54>
        var_1252 = 0.0;
        var_1253 = (var_1246 < var_1252);
        var_1251 = var_1253;
        if (var_1251) {
            var_1254 = 0.0;
            var_1255 = (var_1249 > var_1254);
            var_1251 = var_1251 && var_1255;
        }
        var_1250 = var_1251;
        if (!var_1250) {
            var_1257 = 0.0;
            var_1258 = (var_1249 < var_1257);
            var_1256 = var_1258;
            if (var_1256) {
                var_1259 = 0.0;
                var_1260 = (var_1246 > var_1259);
                var_1256 = var_1256 && var_1260;
            }
            var_1250 = var_1250 || var_1256;
        }
        if (var_1250) {
            // point=vertices[u]+d0/(d0-d1)*(vertices[v]-vertices[u])                             <L 55>
            var_1261 = wp::extract(var_449, var_865);
            var_1262 = wp::sub(var_1246, var_1249);
            var_1263 = wp::div(var_1246, var_1262);
            var_1264 = wp::extract(var_449, var_1140);
            var_1265 = wp::extract(var_449, var_865);
            var_1266 = wp::sub(var_1264, var_1265);
            var_1267 = wp::mul(var_1263, var_1266);
            var_1268 = wp::add(var_1261, var_1267);
            // if inside(point,other) and inside(point,own):points[count]=point;count+=1          <L 56>
            var_1270 = inside_0(var_1268, var_450);
            var_1269 = var_1270;
            if (var_1269) {
                var_1271 = inside_0(var_1268, var_451);
                var_1269 = var_1269 && var_1271;
            }
            if (var_1269) {
                wp::assign_inplace(var_385, var_1241, var_1268);
                var_1273 = wp::add(var_1241, var_1272);
            }
            var_1274 = wp::where(var_1269, var_1273, var_1241);
        }
        var_1275 = wp::where(var_1250, var_1274, var_1241);
        var_1276 = wp::where(var_1250, var_1268, var_1242);
        // vertices=a;other=pb;own=pa                                                             <L 48>
        var_1278 = wp::copy(var_3);
        var_1279 = wp::copy(var_382);
        var_1280 = wp::copy(var_125);
        // if side==1:vertices=b;other=pa;own=pb                                                  <L 49>
        var_1282 = (var_1277 == var_1281);
        if (var_1282) {
            var_1283 = wp::copy(var_6);
            var_1284 = wp::copy(var_125);
            var_1285 = wp::copy(var_382);
        }
        var_1286 = wp::where(var_1282, var_1283, var_1278);
        var_1287 = wp::where(var_1282, var_1284, var_1279);
        var_1288 = wp::where(var_1282, var_1285, var_1280);
        // for u in range(4):                                                                     <L 50>
        // for v in range(u):                                                                     <L 51>
        // for k in range(4):                                                                     <L 52>
        // d0=plane_value(vertices[u],other[k]);d1=plane_value(vertices[v],other[k])              <L 53>
        var_1293 = wp::extract(var_1286, var_1290);
        var_1294 = wp::extract(var_1287, var_1292);
        var_1295 = plane_value_0(var_1293, var_1294);
        var_1296 = wp::extract(var_1286, var_1291);
        var_1297 = wp::extract(var_1287, var_1292);
        var_1298 = plane_value_0(var_1296, var_1297);
        // if (d0<wp.float64(0.) and d1>wp.float64(0.)) or (d1<wp.float64(0.) and d0>wp.float64(0.)):       <L 54>
        var_1301 = 0.0;
        var_1302 = (var_1295 < var_1301);
        var_1300 = var_1302;
        if (var_1300) {
            var_1303 = 0.0;
            var_1304 = (var_1298 > var_1303);
            var_1300 = var_1300 && var_1304;
        }
        var_1299 = var_1300;
        if (!var_1299) {
            var_1306 = 0.0;
            var_1307 = (var_1298 < var_1306);
            var_1305 = var_1307;
            if (var_1305) {
                var_1308 = 0.0;
                var_1309 = (var_1295 > var_1308);
                var_1305 = var_1305 && var_1309;
            }
            var_1299 = var_1299 || var_1305;
        }
        if (var_1299) {
            // point=vertices[u]+d0/(d0-d1)*(vertices[v]-vertices[u])                             <L 55>
            var_1310 = wp::extract(var_1286, var_1290);
            var_1311 = wp::sub(var_1295, var_1298);
            var_1312 = wp::div(var_1295, var_1311);
            var_1313 = wp::extract(var_1286, var_1291);
            var_1314 = wp::extract(var_1286, var_1290);
            var_1315 = wp::sub(var_1313, var_1314);
            var_1316 = wp::mul(var_1312, var_1315);
            var_1317 = wp::add(var_1310, var_1316);
            // if inside(point,other) and inside(point,own):points[count]=point;count+=1          <L 56>
            var_1319 = inside_0(var_1317, var_1287);
            var_1318 = var_1319;
            if (var_1318) {
                var_1320 = inside_0(var_1317, var_1288);
                var_1318 = var_1318 && var_1320;
            }
            if (var_1318) {
                wp::assign_inplace(var_385, var_1275, var_1317);
                var_1322 = wp::add(var_1275, var_1321);
            }
            var_1323 = wp::where(var_1318, var_1322, var_1275);
        }
        var_1324 = wp::where(var_1299, var_1323, var_1275);
        var_1325 = wp::where(var_1299, var_1317, var_1276);
        // d0=plane_value(vertices[u],other[k]);d1=plane_value(vertices[v],other[k])              <L 53>
        var_1327 = wp::extract(var_1286, var_1290);
        var_1328 = wp::extract(var_1287, var_1326);
        var_1329 = plane_value_0(var_1327, var_1328);
        var_1330 = wp::extract(var_1286, var_1291);
        var_1331 = wp::extract(var_1287, var_1326);
        var_1332 = plane_value_0(var_1330, var_1331);
        // if (d0<wp.float64(0.) and d1>wp.float64(0.)) or (d1<wp.float64(0.) and d0>wp.float64(0.)):       <L 54>
        var_1335 = 0.0;
        var_1336 = (var_1329 < var_1335);
        var_1334 = var_1336;
        if (var_1334) {
            var_1337 = 0.0;
            var_1338 = (var_1332 > var_1337);
            var_1334 = var_1334 && var_1338;
        }
        var_1333 = var_1334;
        if (!var_1333) {
            var_1340 = 0.0;
            var_1341 = (var_1332 < var_1340);
            var_1339 = var_1341;
            if (var_1339) {
                var_1342 = 0.0;
                var_1343 = (var_1329 > var_1342);
                var_1339 = var_1339 && var_1343;
            }
            var_1333 = var_1333 || var_1339;
        }
        if (var_1333) {
            // point=vertices[u]+d0/(d0-d1)*(vertices[v]-vertices[u])                             <L 55>
            var_1344 = wp::extract(var_1286, var_1290);
            var_1345 = wp::sub(var_1329, var_1332);
            var_1346 = wp::div(var_1329, var_1345);
            var_1347 = wp::extract(var_1286, var_1291);
            var_1348 = wp::extract(var_1286, var_1290);
            var_1349 = wp::sub(var_1347, var_1348);
            var_1350 = wp::mul(var_1346, var_1349);
            var_1351 = wp::add(var_1344, var_1350);
            // if inside(point,other) and inside(point,own):points[count]=point;count+=1          <L 56>
            var_1353 = inside_0(var_1351, var_1287);
            var_1352 = var_1353;
            if (var_1352) {
                var_1354 = inside_0(var_1351, var_1288);
                var_1352 = var_1352 && var_1354;
            }
            if (var_1352) {
                wp::assign_inplace(var_385, var_1324, var_1351);
                var_1356 = wp::add(var_1324, var_1355);
            }
            var_1357 = wp::where(var_1352, var_1356, var_1324);
        }
        var_1358 = wp::where(var_1333, var_1357, var_1324);
        var_1359 = wp::where(var_1333, var_1351, var_1325);
        // d0=plane_value(vertices[u],other[k]);d1=plane_value(vertices[v],other[k])              <L 53>
        var_1361 = wp::extract(var_1286, var_1290);
        var_1362 = wp::extract(var_1287, var_1360);
        var_1363 = plane_value_0(var_1361, var_1362);
        var_1364 = wp::extract(var_1286, var_1291);
        var_1365 = wp::extract(var_1287, var_1360);
        var_1366 = plane_value_0(var_1364, var_1365);
        // if (d0<wp.float64(0.) and d1>wp.float64(0.)) or (d1<wp.float64(0.) and d0>wp.float64(0.)):       <L 54>
        var_1369 = 0.0;
        var_1370 = (var_1363 < var_1369);
        var_1368 = var_1370;
        if (var_1368) {
            var_1371 = 0.0;
            var_1372 = (var_1366 > var_1371);
            var_1368 = var_1368 && var_1372;
        }
        var_1367 = var_1368;
        if (!var_1367) {
            var_1374 = 0.0;
            var_1375 = (var_1366 < var_1374);
            var_1373 = var_1375;
            if (var_1373) {
                var_1376 = 0.0;
                var_1377 = (var_1363 > var_1376);
                var_1373 = var_1373 && var_1377;
            }
            var_1367 = var_1367 || var_1373;
        }
        if (var_1367) {
            // point=vertices[u]+d0/(d0-d1)*(vertices[v]-vertices[u])                             <L 55>
            var_1378 = wp::extract(var_1286, var_1290);
            var_1379 = wp::sub(var_1363, var_1366);
            var_1380 = wp::div(var_1363, var_1379);
            var_1381 = wp::extract(var_1286, var_1291);
            var_1382 = wp::extract(var_1286, var_1290);
            var_1383 = wp::sub(var_1381, var_1382);
            var_1384 = wp::mul(var_1380, var_1383);
            var_1385 = wp::add(var_1378, var_1384);
            // if inside(point,other) and inside(point,own):points[count]=point;count+=1          <L 56>
            var_1387 = inside_0(var_1385, var_1287);
            var_1386 = var_1387;
            if (var_1386) {
                var_1388 = inside_0(var_1385, var_1288);
                var_1386 = var_1386 && var_1388;
            }
            if (var_1386) {
                wp::assign_inplace(var_385, var_1358, var_1385);
                var_1390 = wp::add(var_1358, var_1389);
            }
            var_1391 = wp::where(var_1386, var_1390, var_1358);
        }
        var_1392 = wp::where(var_1367, var_1391, var_1358);
        var_1393 = wp::where(var_1367, var_1385, var_1359);
        // d0=plane_value(vertices[u],other[k]);d1=plane_value(vertices[v],other[k])              <L 53>
        var_1395 = wp::extract(var_1286, var_1290);
        var_1396 = wp::extract(var_1287, var_1394);
        var_1397 = plane_value_0(var_1395, var_1396);
        var_1398 = wp::extract(var_1286, var_1291);
        var_1399 = wp::extract(var_1287, var_1394);
        var_1400 = plane_value_0(var_1398, var_1399);
        // if (d0<wp.float64(0.) and d1>wp.float64(0.)) or (d1<wp.float64(0.) and d0>wp.float64(0.)):       <L 54>
        var_1403 = 0.0;
        var_1404 = (var_1397 < var_1403);
        var_1402 = var_1404;
        if (var_1402) {
            var_1405 = 0.0;
            var_1406 = (var_1400 > var_1405);
            var_1402 = var_1402 && var_1406;
        }
        var_1401 = var_1402;
        if (!var_1401) {
            var_1408 = 0.0;
            var_1409 = (var_1400 < var_1408);
            var_1407 = var_1409;
            if (var_1407) {
                var_1410 = 0.0;
                var_1411 = (var_1397 > var_1410);
                var_1407 = var_1407 && var_1411;
            }
            var_1401 = var_1401 || var_1407;
        }
        if (var_1401) {
            // point=vertices[u]+d0/(d0-d1)*(vertices[v]-vertices[u])                             <L 55>
            var_1412 = wp::extract(var_1286, var_1290);
            var_1413 = wp::sub(var_1397, var_1400);
            var_1414 = wp::div(var_1397, var_1413);
            var_1415 = wp::extract(var_1286, var_1291);
            var_1416 = wp::extract(var_1286, var_1290);
            var_1417 = wp::sub(var_1415, var_1416);
            var_1418 = wp::mul(var_1414, var_1417);
            var_1419 = wp::add(var_1412, var_1418);
            // if inside(point,other) and inside(point,own):points[count]=point;count+=1          <L 56>
            var_1421 = inside_0(var_1419, var_1287);
            var_1420 = var_1421;
            if (var_1420) {
                var_1422 = inside_0(var_1419, var_1288);
                var_1420 = var_1420 && var_1422;
            }
            if (var_1420) {
                wp::assign_inplace(var_385, var_1392, var_1419);
                var_1424 = wp::add(var_1392, var_1423);
            }
            var_1425 = wp::where(var_1420, var_1424, var_1392);
        }
        var_1426 = wp::where(var_1401, var_1425, var_1392);
        var_1427 = wp::where(var_1401, var_1419, var_1393);
        // for v in range(u):                                                                     <L 51>
        // for k in range(4):                                                                     <L 52>
        // d0=plane_value(vertices[u],other[k]);d1=plane_value(vertices[v],other[k])              <L 53>
        var_1431 = wp::extract(var_1286, var_1428);
        var_1432 = wp::extract(var_1287, var_1430);
        var_1433 = plane_value_0(var_1431, var_1432);
        var_1434 = wp::extract(var_1286, var_1429);
        var_1435 = wp::extract(var_1287, var_1430);
        var_1436 = plane_value_0(var_1434, var_1435);
        // if (d0<wp.float64(0.) and d1>wp.float64(0.)) or (d1<wp.float64(0.) and d0>wp.float64(0.)):       <L 54>
        var_1439 = 0.0;
        var_1440 = (var_1433 < var_1439);
        var_1438 = var_1440;
        if (var_1438) {
            var_1441 = 0.0;
            var_1442 = (var_1436 > var_1441);
            var_1438 = var_1438 && var_1442;
        }
        var_1437 = var_1438;
        if (!var_1437) {
            var_1444 = 0.0;
            var_1445 = (var_1436 < var_1444);
            var_1443 = var_1445;
            if (var_1443) {
                var_1446 = 0.0;
                var_1447 = (var_1433 > var_1446);
                var_1443 = var_1443 && var_1447;
            }
            var_1437 = var_1437 || var_1443;
        }
        if (var_1437) {
            // point=vertices[u]+d0/(d0-d1)*(vertices[v]-vertices[u])                             <L 55>
            var_1448 = wp::extract(var_1286, var_1428);
            var_1449 = wp::sub(var_1433, var_1436);
            var_1450 = wp::div(var_1433, var_1449);
            var_1451 = wp::extract(var_1286, var_1429);
            var_1452 = wp::extract(var_1286, var_1428);
            var_1453 = wp::sub(var_1451, var_1452);
            var_1454 = wp::mul(var_1450, var_1453);
            var_1455 = wp::add(var_1448, var_1454);
            // if inside(point,other) and inside(point,own):points[count]=point;count+=1          <L 56>
            var_1457 = inside_0(var_1455, var_1287);
            var_1456 = var_1457;
            if (var_1456) {
                var_1458 = inside_0(var_1455, var_1288);
                var_1456 = var_1456 && var_1458;
            }
            if (var_1456) {
                wp::assign_inplace(var_385, var_1426, var_1455);
                var_1460 = wp::add(var_1426, var_1459);
            }
            var_1461 = wp::where(var_1456, var_1460, var_1426);
        }
        var_1462 = wp::where(var_1437, var_1461, var_1426);
        var_1463 = wp::where(var_1437, var_1455, var_1427);
        // d0=plane_value(vertices[u],other[k]);d1=plane_value(vertices[v],other[k])              <L 53>
        var_1465 = wp::extract(var_1286, var_1428);
        var_1466 = wp::extract(var_1287, var_1464);
        var_1467 = plane_value_0(var_1465, var_1466);
        var_1468 = wp::extract(var_1286, var_1429);
        var_1469 = wp::extract(var_1287, var_1464);
        var_1470 = plane_value_0(var_1468, var_1469);
        // if (d0<wp.float64(0.) and d1>wp.float64(0.)) or (d1<wp.float64(0.) and d0>wp.float64(0.)):       <L 54>
        var_1473 = 0.0;
        var_1474 = (var_1467 < var_1473);
        var_1472 = var_1474;
        if (var_1472) {
            var_1475 = 0.0;
            var_1476 = (var_1470 > var_1475);
            var_1472 = var_1472 && var_1476;
        }
        var_1471 = var_1472;
        if (!var_1471) {
            var_1478 = 0.0;
            var_1479 = (var_1470 < var_1478);
            var_1477 = var_1479;
            if (var_1477) {
                var_1480 = 0.0;
                var_1481 = (var_1467 > var_1480);
                var_1477 = var_1477 && var_1481;
            }
            var_1471 = var_1471 || var_1477;
        }
        if (var_1471) {
            // point=vertices[u]+d0/(d0-d1)*(vertices[v]-vertices[u])                             <L 55>
            var_1482 = wp::extract(var_1286, var_1428);
            var_1483 = wp::sub(var_1467, var_1470);
            var_1484 = wp::div(var_1467, var_1483);
            var_1485 = wp::extract(var_1286, var_1429);
            var_1486 = wp::extract(var_1286, var_1428);
            var_1487 = wp::sub(var_1485, var_1486);
            var_1488 = wp::mul(var_1484, var_1487);
            var_1489 = wp::add(var_1482, var_1488);
            // if inside(point,other) and inside(point,own):points[count]=point;count+=1          <L 56>
            var_1491 = inside_0(var_1489, var_1287);
            var_1490 = var_1491;
            if (var_1490) {
                var_1492 = inside_0(var_1489, var_1288);
                var_1490 = var_1490 && var_1492;
            }
            if (var_1490) {
                wp::assign_inplace(var_385, var_1462, var_1489);
                var_1494 = wp::add(var_1462, var_1493);
            }
            var_1495 = wp::where(var_1490, var_1494, var_1462);
        }
        var_1496 = wp::where(var_1471, var_1495, var_1462);
        var_1497 = wp::where(var_1471, var_1489, var_1463);
        // d0=plane_value(vertices[u],other[k]);d1=plane_value(vertices[v],other[k])              <L 53>
        var_1499 = wp::extract(var_1286, var_1428);
        var_1500 = wp::extract(var_1287, var_1498);
        var_1501 = plane_value_0(var_1499, var_1500);
        var_1502 = wp::extract(var_1286, var_1429);
        var_1503 = wp::extract(var_1287, var_1498);
        var_1504 = plane_value_0(var_1502, var_1503);
        // if (d0<wp.float64(0.) and d1>wp.float64(0.)) or (d1<wp.float64(0.) and d0>wp.float64(0.)):       <L 54>
        var_1507 = 0.0;
        var_1508 = (var_1501 < var_1507);
        var_1506 = var_1508;
        if (var_1506) {
            var_1509 = 0.0;
            var_1510 = (var_1504 > var_1509);
            var_1506 = var_1506 && var_1510;
        }
        var_1505 = var_1506;
        if (!var_1505) {
            var_1512 = 0.0;
            var_1513 = (var_1504 < var_1512);
            var_1511 = var_1513;
            if (var_1511) {
                var_1514 = 0.0;
                var_1515 = (var_1501 > var_1514);
                var_1511 = var_1511 && var_1515;
            }
            var_1505 = var_1505 || var_1511;
        }
        if (var_1505) {
            // point=vertices[u]+d0/(d0-d1)*(vertices[v]-vertices[u])                             <L 55>
            var_1516 = wp::extract(var_1286, var_1428);
            var_1517 = wp::sub(var_1501, var_1504);
            var_1518 = wp::div(var_1501, var_1517);
            var_1519 = wp::extract(var_1286, var_1429);
            var_1520 = wp::extract(var_1286, var_1428);
            var_1521 = wp::sub(var_1519, var_1520);
            var_1522 = wp::mul(var_1518, var_1521);
            var_1523 = wp::add(var_1516, var_1522);
            // if inside(point,other) and inside(point,own):points[count]=point;count+=1          <L 56>
            var_1525 = inside_0(var_1523, var_1287);
            var_1524 = var_1525;
            if (var_1524) {
                var_1526 = inside_0(var_1523, var_1288);
                var_1524 = var_1524 && var_1526;
            }
            if (var_1524) {
                wp::assign_inplace(var_385, var_1496, var_1523);
                var_1528 = wp::add(var_1496, var_1527);
            }
            var_1529 = wp::where(var_1524, var_1528, var_1496);
        }
        var_1530 = wp::where(var_1505, var_1529, var_1496);
        var_1531 = wp::where(var_1505, var_1523, var_1497);
        // d0=plane_value(vertices[u],other[k]);d1=plane_value(vertices[v],other[k])              <L 53>
        var_1533 = wp::extract(var_1286, var_1428);
        var_1534 = wp::extract(var_1287, var_1532);
        var_1535 = plane_value_0(var_1533, var_1534);
        var_1536 = wp::extract(var_1286, var_1429);
        var_1537 = wp::extract(var_1287, var_1532);
        var_1538 = plane_value_0(var_1536, var_1537);
        // if (d0<wp.float64(0.) and d1>wp.float64(0.)) or (d1<wp.float64(0.) and d0>wp.float64(0.)):       <L 54>
        var_1541 = 0.0;
        var_1542 = (var_1535 < var_1541);
        var_1540 = var_1542;
        if (var_1540) {
            var_1543 = 0.0;
            var_1544 = (var_1538 > var_1543);
            var_1540 = var_1540 && var_1544;
        }
        var_1539 = var_1540;
        if (!var_1539) {
            var_1546 = 0.0;
            var_1547 = (var_1538 < var_1546);
            var_1545 = var_1547;
            if (var_1545) {
                var_1548 = 0.0;
                var_1549 = (var_1535 > var_1548);
                var_1545 = var_1545 && var_1549;
            }
            var_1539 = var_1539 || var_1545;
        }
        if (var_1539) {
            // point=vertices[u]+d0/(d0-d1)*(vertices[v]-vertices[u])                             <L 55>
            var_1550 = wp::extract(var_1286, var_1428);
            var_1551 = wp::sub(var_1535, var_1538);
            var_1552 = wp::div(var_1535, var_1551);
            var_1553 = wp::extract(var_1286, var_1429);
            var_1554 = wp::extract(var_1286, var_1428);
            var_1555 = wp::sub(var_1553, var_1554);
            var_1556 = wp::mul(var_1552, var_1555);
            var_1557 = wp::add(var_1550, var_1556);
            // if inside(point,other) and inside(point,own):points[count]=point;count+=1          <L 56>
            var_1559 = inside_0(var_1557, var_1287);
            var_1558 = var_1559;
            if (var_1558) {
                var_1560 = inside_0(var_1557, var_1288);
                var_1558 = var_1558 && var_1560;
            }
            if (var_1558) {
                wp::assign_inplace(var_385, var_1530, var_1557);
                var_1562 = wp::add(var_1530, var_1561);
            }
            var_1563 = wp::where(var_1558, var_1562, var_1530);
        }
        var_1564 = wp::where(var_1539, var_1563, var_1530);
        var_1565 = wp::where(var_1539, var_1557, var_1531);
        // for k in range(4):                                                                     <L 52>
        // d0=plane_value(vertices[u],other[k]);d1=plane_value(vertices[v],other[k])              <L 53>
        var_1568 = wp::extract(var_1286, var_1428);
        var_1569 = wp::extract(var_1287, var_1567);
        var_1570 = plane_value_0(var_1568, var_1569);
        var_1571 = wp::extract(var_1286, var_1566);
        var_1572 = wp::extract(var_1287, var_1567);
        var_1573 = plane_value_0(var_1571, var_1572);
        // if (d0<wp.float64(0.) and d1>wp.float64(0.)) or (d1<wp.float64(0.) and d0>wp.float64(0.)):       <L 54>
        var_1576 = 0.0;
        var_1577 = (var_1570 < var_1576);
        var_1575 = var_1577;
        if (var_1575) {
            var_1578 = 0.0;
            var_1579 = (var_1573 > var_1578);
            var_1575 = var_1575 && var_1579;
        }
        var_1574 = var_1575;
        if (!var_1574) {
            var_1581 = 0.0;
            var_1582 = (var_1573 < var_1581);
            var_1580 = var_1582;
            if (var_1580) {
                var_1583 = 0.0;
                var_1584 = (var_1570 > var_1583);
                var_1580 = var_1580 && var_1584;
            }
            var_1574 = var_1574 || var_1580;
        }
        if (var_1574) {
            // point=vertices[u]+d0/(d0-d1)*(vertices[v]-vertices[u])                             <L 55>
            var_1585 = wp::extract(var_1286, var_1428);
            var_1586 = wp::sub(var_1570, var_1573);
            var_1587 = wp::div(var_1570, var_1586);
            var_1588 = wp::extract(var_1286, var_1566);
            var_1589 = wp::extract(var_1286, var_1428);
            var_1590 = wp::sub(var_1588, var_1589);
            var_1591 = wp::mul(var_1587, var_1590);
            var_1592 = wp::add(var_1585, var_1591);
            // if inside(point,other) and inside(point,own):points[count]=point;count+=1          <L 56>
            var_1594 = inside_0(var_1592, var_1287);
            var_1593 = var_1594;
            if (var_1593) {
                var_1595 = inside_0(var_1592, var_1288);
                var_1593 = var_1593 && var_1595;
            }
            if (var_1593) {
                wp::assign_inplace(var_385, var_1564, var_1592);
                var_1597 = wp::add(var_1564, var_1596);
            }
            var_1598 = wp::where(var_1593, var_1597, var_1564);
        }
        var_1599 = wp::where(var_1574, var_1598, var_1564);
        var_1600 = wp::where(var_1574, var_1592, var_1565);
        // d0=plane_value(vertices[u],other[k]);d1=plane_value(vertices[v],other[k])              <L 53>
        var_1602 = wp::extract(var_1286, var_1428);
        var_1603 = wp::extract(var_1287, var_1601);
        var_1604 = plane_value_0(var_1602, var_1603);
        var_1605 = wp::extract(var_1286, var_1566);
        var_1606 = wp::extract(var_1287, var_1601);
        var_1607 = plane_value_0(var_1605, var_1606);
        // if (d0<wp.float64(0.) and d1>wp.float64(0.)) or (d1<wp.float64(0.) and d0>wp.float64(0.)):       <L 54>
        var_1610 = 0.0;
        var_1611 = (var_1604 < var_1610);
        var_1609 = var_1611;
        if (var_1609) {
            var_1612 = 0.0;
            var_1613 = (var_1607 > var_1612);
            var_1609 = var_1609 && var_1613;
        }
        var_1608 = var_1609;
        if (!var_1608) {
            var_1615 = 0.0;
            var_1616 = (var_1607 < var_1615);
            var_1614 = var_1616;
            if (var_1614) {
                var_1617 = 0.0;
                var_1618 = (var_1604 > var_1617);
                var_1614 = var_1614 && var_1618;
            }
            var_1608 = var_1608 || var_1614;
        }
        if (var_1608) {
            // point=vertices[u]+d0/(d0-d1)*(vertices[v]-vertices[u])                             <L 55>
            var_1619 = wp::extract(var_1286, var_1428);
            var_1620 = wp::sub(var_1604, var_1607);
            var_1621 = wp::div(var_1604, var_1620);
            var_1622 = wp::extract(var_1286, var_1566);
            var_1623 = wp::extract(var_1286, var_1428);
            var_1624 = wp::sub(var_1622, var_1623);
            var_1625 = wp::mul(var_1621, var_1624);
            var_1626 = wp::add(var_1619, var_1625);
            // if inside(point,other) and inside(point,own):points[count]=point;count+=1          <L 56>
            var_1628 = inside_0(var_1626, var_1287);
            var_1627 = var_1628;
            if (var_1627) {
                var_1629 = inside_0(var_1626, var_1288);
                var_1627 = var_1627 && var_1629;
            }
            if (var_1627) {
                wp::assign_inplace(var_385, var_1599, var_1626);
                var_1631 = wp::add(var_1599, var_1630);
            }
            var_1632 = wp::where(var_1627, var_1631, var_1599);
        }
        var_1633 = wp::where(var_1608, var_1632, var_1599);
        var_1634 = wp::where(var_1608, var_1626, var_1600);
        // d0=plane_value(vertices[u],other[k]);d1=plane_value(vertices[v],other[k])              <L 53>
        var_1636 = wp::extract(var_1286, var_1428);
        var_1637 = wp::extract(var_1287, var_1635);
        var_1638 = plane_value_0(var_1636, var_1637);
        var_1639 = wp::extract(var_1286, var_1566);
        var_1640 = wp::extract(var_1287, var_1635);
        var_1641 = plane_value_0(var_1639, var_1640);
        // if (d0<wp.float64(0.) and d1>wp.float64(0.)) or (d1<wp.float64(0.) and d0>wp.float64(0.)):       <L 54>
        var_1644 = 0.0;
        var_1645 = (var_1638 < var_1644);
        var_1643 = var_1645;
        if (var_1643) {
            var_1646 = 0.0;
            var_1647 = (var_1641 > var_1646);
            var_1643 = var_1643 && var_1647;
        }
        var_1642 = var_1643;
        if (!var_1642) {
            var_1649 = 0.0;
            var_1650 = (var_1641 < var_1649);
            var_1648 = var_1650;
            if (var_1648) {
                var_1651 = 0.0;
                var_1652 = (var_1638 > var_1651);
                var_1648 = var_1648 && var_1652;
            }
            var_1642 = var_1642 || var_1648;
        }
        if (var_1642) {
            // point=vertices[u]+d0/(d0-d1)*(vertices[v]-vertices[u])                             <L 55>
            var_1653 = wp::extract(var_1286, var_1428);
            var_1654 = wp::sub(var_1638, var_1641);
            var_1655 = wp::div(var_1638, var_1654);
            var_1656 = wp::extract(var_1286, var_1566);
            var_1657 = wp::extract(var_1286, var_1428);
            var_1658 = wp::sub(var_1656, var_1657);
            var_1659 = wp::mul(var_1655, var_1658);
            var_1660 = wp::add(var_1653, var_1659);
            // if inside(point,other) and inside(point,own):points[count]=point;count+=1          <L 56>
            var_1662 = inside_0(var_1660, var_1287);
            var_1661 = var_1662;
            if (var_1661) {
                var_1663 = inside_0(var_1660, var_1288);
                var_1661 = var_1661 && var_1663;
            }
            if (var_1661) {
                wp::assign_inplace(var_385, var_1633, var_1660);
                var_1665 = wp::add(var_1633, var_1664);
            }
            var_1666 = wp::where(var_1661, var_1665, var_1633);
        }
        var_1667 = wp::where(var_1642, var_1666, var_1633);
        var_1668 = wp::where(var_1642, var_1660, var_1634);
        // d0=plane_value(vertices[u],other[k]);d1=plane_value(vertices[v],other[k])              <L 53>
        var_1670 = wp::extract(var_1286, var_1428);
        var_1671 = wp::extract(var_1287, var_1669);
        var_1672 = plane_value_0(var_1670, var_1671);
        var_1673 = wp::extract(var_1286, var_1566);
        var_1674 = wp::extract(var_1287, var_1669);
        var_1675 = plane_value_0(var_1673, var_1674);
        // if (d0<wp.float64(0.) and d1>wp.float64(0.)) or (d1<wp.float64(0.) and d0>wp.float64(0.)):       <L 54>
        var_1678 = 0.0;
        var_1679 = (var_1672 < var_1678);
        var_1677 = var_1679;
        if (var_1677) {
            var_1680 = 0.0;
            var_1681 = (var_1675 > var_1680);
            var_1677 = var_1677 && var_1681;
        }
        var_1676 = var_1677;
        if (!var_1676) {
            var_1683 = 0.0;
            var_1684 = (var_1675 < var_1683);
            var_1682 = var_1684;
            if (var_1682) {
                var_1685 = 0.0;
                var_1686 = (var_1672 > var_1685);
                var_1682 = var_1682 && var_1686;
            }
            var_1676 = var_1676 || var_1682;
        }
        if (var_1676) {
            // point=vertices[u]+d0/(d0-d1)*(vertices[v]-vertices[u])                             <L 55>
            var_1687 = wp::extract(var_1286, var_1428);
            var_1688 = wp::sub(var_1672, var_1675);
            var_1689 = wp::div(var_1672, var_1688);
            var_1690 = wp::extract(var_1286, var_1566);
            var_1691 = wp::extract(var_1286, var_1428);
            var_1692 = wp::sub(var_1690, var_1691);
            var_1693 = wp::mul(var_1689, var_1692);
            var_1694 = wp::add(var_1687, var_1693);
            // if inside(point,other) and inside(point,own):points[count]=point;count+=1          <L 56>
            var_1696 = inside_0(var_1694, var_1287);
            var_1695 = var_1696;
            if (var_1695) {
                var_1697 = inside_0(var_1694, var_1288);
                var_1695 = var_1695 && var_1697;
            }
            if (var_1695) {
                wp::assign_inplace(var_385, var_1667, var_1694);
                var_1699 = wp::add(var_1667, var_1698);
            }
            var_1700 = wp::where(var_1695, var_1699, var_1667);
        }
        var_1701 = wp::where(var_1676, var_1700, var_1667);
        var_1702 = wp::where(var_1676, var_1694, var_1668);
        // for v in range(u):                                                                     <L 51>
        // for k in range(4):                                                                     <L 52>
        // d0=plane_value(vertices[u],other[k]);d1=plane_value(vertices[v],other[k])              <L 53>
        var_1706 = wp::extract(var_1286, var_1703);
        var_1707 = wp::extract(var_1287, var_1705);
        var_1708 = plane_value_0(var_1706, var_1707);
        var_1709 = wp::extract(var_1286, var_1704);
        var_1710 = wp::extract(var_1287, var_1705);
        var_1711 = plane_value_0(var_1709, var_1710);
        // if (d0<wp.float64(0.) and d1>wp.float64(0.)) or (d1<wp.float64(0.) and d0>wp.float64(0.)):       <L 54>
        var_1714 = 0.0;
        var_1715 = (var_1708 < var_1714);
        var_1713 = var_1715;
        if (var_1713) {
            var_1716 = 0.0;
            var_1717 = (var_1711 > var_1716);
            var_1713 = var_1713 && var_1717;
        }
        var_1712 = var_1713;
        if (!var_1712) {
            var_1719 = 0.0;
            var_1720 = (var_1711 < var_1719);
            var_1718 = var_1720;
            if (var_1718) {
                var_1721 = 0.0;
                var_1722 = (var_1708 > var_1721);
                var_1718 = var_1718 && var_1722;
            }
            var_1712 = var_1712 || var_1718;
        }
        if (var_1712) {
            // point=vertices[u]+d0/(d0-d1)*(vertices[v]-vertices[u])                             <L 55>
            var_1723 = wp::extract(var_1286, var_1703);
            var_1724 = wp::sub(var_1708, var_1711);
            var_1725 = wp::div(var_1708, var_1724);
            var_1726 = wp::extract(var_1286, var_1704);
            var_1727 = wp::extract(var_1286, var_1703);
            var_1728 = wp::sub(var_1726, var_1727);
            var_1729 = wp::mul(var_1725, var_1728);
            var_1730 = wp::add(var_1723, var_1729);
            // if inside(point,other) and inside(point,own):points[count]=point;count+=1          <L 56>
            var_1732 = inside_0(var_1730, var_1287);
            var_1731 = var_1732;
            if (var_1731) {
                var_1733 = inside_0(var_1730, var_1288);
                var_1731 = var_1731 && var_1733;
            }
            if (var_1731) {
                wp::assign_inplace(var_385, var_1701, var_1730);
                var_1735 = wp::add(var_1701, var_1734);
            }
            var_1736 = wp::where(var_1731, var_1735, var_1701);
        }
        var_1737 = wp::where(var_1712, var_1736, var_1701);
        var_1738 = wp::where(var_1712, var_1730, var_1702);
        // d0=plane_value(vertices[u],other[k]);d1=plane_value(vertices[v],other[k])              <L 53>
        var_1740 = wp::extract(var_1286, var_1703);
        var_1741 = wp::extract(var_1287, var_1739);
        var_1742 = plane_value_0(var_1740, var_1741);
        var_1743 = wp::extract(var_1286, var_1704);
        var_1744 = wp::extract(var_1287, var_1739);
        var_1745 = plane_value_0(var_1743, var_1744);
        // if (d0<wp.float64(0.) and d1>wp.float64(0.)) or (d1<wp.float64(0.) and d0>wp.float64(0.)):       <L 54>
        var_1748 = 0.0;
        var_1749 = (var_1742 < var_1748);
        var_1747 = var_1749;
        if (var_1747) {
            var_1750 = 0.0;
            var_1751 = (var_1745 > var_1750);
            var_1747 = var_1747 && var_1751;
        }
        var_1746 = var_1747;
        if (!var_1746) {
            var_1753 = 0.0;
            var_1754 = (var_1745 < var_1753);
            var_1752 = var_1754;
            if (var_1752) {
                var_1755 = 0.0;
                var_1756 = (var_1742 > var_1755);
                var_1752 = var_1752 && var_1756;
            }
            var_1746 = var_1746 || var_1752;
        }
        if (var_1746) {
            // point=vertices[u]+d0/(d0-d1)*(vertices[v]-vertices[u])                             <L 55>
            var_1757 = wp::extract(var_1286, var_1703);
            var_1758 = wp::sub(var_1742, var_1745);
            var_1759 = wp::div(var_1742, var_1758);
            var_1760 = wp::extract(var_1286, var_1704);
            var_1761 = wp::extract(var_1286, var_1703);
            var_1762 = wp::sub(var_1760, var_1761);
            var_1763 = wp::mul(var_1759, var_1762);
            var_1764 = wp::add(var_1757, var_1763);
            // if inside(point,other) and inside(point,own):points[count]=point;count+=1          <L 56>
            var_1766 = inside_0(var_1764, var_1287);
            var_1765 = var_1766;
            if (var_1765) {
                var_1767 = inside_0(var_1764, var_1288);
                var_1765 = var_1765 && var_1767;
            }
            if (var_1765) {
                wp::assign_inplace(var_385, var_1737, var_1764);
                var_1769 = wp::add(var_1737, var_1768);
            }
            var_1770 = wp::where(var_1765, var_1769, var_1737);
        }
        var_1771 = wp::where(var_1746, var_1770, var_1737);
        var_1772 = wp::where(var_1746, var_1764, var_1738);
        // d0=plane_value(vertices[u],other[k]);d1=plane_value(vertices[v],other[k])              <L 53>
        var_1774 = wp::extract(var_1286, var_1703);
        var_1775 = wp::extract(var_1287, var_1773);
        var_1776 = plane_value_0(var_1774, var_1775);
        var_1777 = wp::extract(var_1286, var_1704);
        var_1778 = wp::extract(var_1287, var_1773);
        var_1779 = plane_value_0(var_1777, var_1778);
        // if (d0<wp.float64(0.) and d1>wp.float64(0.)) or (d1<wp.float64(0.) and d0>wp.float64(0.)):       <L 54>
        var_1782 = 0.0;
        var_1783 = (var_1776 < var_1782);
        var_1781 = var_1783;
        if (var_1781) {
            var_1784 = 0.0;
            var_1785 = (var_1779 > var_1784);
            var_1781 = var_1781 && var_1785;
        }
        var_1780 = var_1781;
        if (!var_1780) {
            var_1787 = 0.0;
            var_1788 = (var_1779 < var_1787);
            var_1786 = var_1788;
            if (var_1786) {
                var_1789 = 0.0;
                var_1790 = (var_1776 > var_1789);
                var_1786 = var_1786 && var_1790;
            }
            var_1780 = var_1780 || var_1786;
        }
        if (var_1780) {
            // point=vertices[u]+d0/(d0-d1)*(vertices[v]-vertices[u])                             <L 55>
            var_1791 = wp::extract(var_1286, var_1703);
            var_1792 = wp::sub(var_1776, var_1779);
            var_1793 = wp::div(var_1776, var_1792);
            var_1794 = wp::extract(var_1286, var_1704);
            var_1795 = wp::extract(var_1286, var_1703);
            var_1796 = wp::sub(var_1794, var_1795);
            var_1797 = wp::mul(var_1793, var_1796);
            var_1798 = wp::add(var_1791, var_1797);
            // if inside(point,other) and inside(point,own):points[count]=point;count+=1          <L 56>
            var_1800 = inside_0(var_1798, var_1287);
            var_1799 = var_1800;
            if (var_1799) {
                var_1801 = inside_0(var_1798, var_1288);
                var_1799 = var_1799 && var_1801;
            }
            if (var_1799) {
                wp::assign_inplace(var_385, var_1771, var_1798);
                var_1803 = wp::add(var_1771, var_1802);
            }
            var_1804 = wp::where(var_1799, var_1803, var_1771);
        }
        var_1805 = wp::where(var_1780, var_1804, var_1771);
        var_1806 = wp::where(var_1780, var_1798, var_1772);
        // d0=plane_value(vertices[u],other[k]);d1=plane_value(vertices[v],other[k])              <L 53>
        var_1808 = wp::extract(var_1286, var_1703);
        var_1809 = wp::extract(var_1287, var_1807);
        var_1810 = plane_value_0(var_1808, var_1809);
        var_1811 = wp::extract(var_1286, var_1704);
        var_1812 = wp::extract(var_1287, var_1807);
        var_1813 = plane_value_0(var_1811, var_1812);
        // if (d0<wp.float64(0.) and d1>wp.float64(0.)) or (d1<wp.float64(0.) and d0>wp.float64(0.)):       <L 54>
        var_1816 = 0.0;
        var_1817 = (var_1810 < var_1816);
        var_1815 = var_1817;
        if (var_1815) {
            var_1818 = 0.0;
            var_1819 = (var_1813 > var_1818);
            var_1815 = var_1815 && var_1819;
        }
        var_1814 = var_1815;
        if (!var_1814) {
            var_1821 = 0.0;
            var_1822 = (var_1813 < var_1821);
            var_1820 = var_1822;
            if (var_1820) {
                var_1823 = 0.0;
                var_1824 = (var_1810 > var_1823);
                var_1820 = var_1820 && var_1824;
            }
            var_1814 = var_1814 || var_1820;
        }
        if (var_1814) {
            // point=vertices[u]+d0/(d0-d1)*(vertices[v]-vertices[u])                             <L 55>
            var_1825 = wp::extract(var_1286, var_1703);
            var_1826 = wp::sub(var_1810, var_1813);
            var_1827 = wp::div(var_1810, var_1826);
            var_1828 = wp::extract(var_1286, var_1704);
            var_1829 = wp::extract(var_1286, var_1703);
            var_1830 = wp::sub(var_1828, var_1829);
            var_1831 = wp::mul(var_1827, var_1830);
            var_1832 = wp::add(var_1825, var_1831);
            // if inside(point,other) and inside(point,own):points[count]=point;count+=1          <L 56>
            var_1834 = inside_0(var_1832, var_1287);
            var_1833 = var_1834;
            if (var_1833) {
                var_1835 = inside_0(var_1832, var_1288);
                var_1833 = var_1833 && var_1835;
            }
            if (var_1833) {
                wp::assign_inplace(var_385, var_1805, var_1832);
                var_1837 = wp::add(var_1805, var_1836);
            }
            var_1838 = wp::where(var_1833, var_1837, var_1805);
        }
        var_1839 = wp::where(var_1814, var_1838, var_1805);
        var_1840 = wp::where(var_1814, var_1832, var_1806);
        // for k in range(4):                                                                     <L 52>
        // d0=plane_value(vertices[u],other[k]);d1=plane_value(vertices[v],other[k])              <L 53>
        var_1843 = wp::extract(var_1286, var_1703);
        var_1844 = wp::extract(var_1287, var_1842);
        var_1845 = plane_value_0(var_1843, var_1844);
        var_1846 = wp::extract(var_1286, var_1841);
        var_1847 = wp::extract(var_1287, var_1842);
        var_1848 = plane_value_0(var_1846, var_1847);
        // if (d0<wp.float64(0.) and d1>wp.float64(0.)) or (d1<wp.float64(0.) and d0>wp.float64(0.)):       <L 54>
        var_1851 = 0.0;
        var_1852 = (var_1845 < var_1851);
        var_1850 = var_1852;
        if (var_1850) {
            var_1853 = 0.0;
            var_1854 = (var_1848 > var_1853);
            var_1850 = var_1850 && var_1854;
        }
        var_1849 = var_1850;
        if (!var_1849) {
            var_1856 = 0.0;
            var_1857 = (var_1848 < var_1856);
            var_1855 = var_1857;
            if (var_1855) {
                var_1858 = 0.0;
                var_1859 = (var_1845 > var_1858);
                var_1855 = var_1855 && var_1859;
            }
            var_1849 = var_1849 || var_1855;
        }
        if (var_1849) {
            // point=vertices[u]+d0/(d0-d1)*(vertices[v]-vertices[u])                             <L 55>
            var_1860 = wp::extract(var_1286, var_1703);
            var_1861 = wp::sub(var_1845, var_1848);
            var_1862 = wp::div(var_1845, var_1861);
            var_1863 = wp::extract(var_1286, var_1841);
            var_1864 = wp::extract(var_1286, var_1703);
            var_1865 = wp::sub(var_1863, var_1864);
            var_1866 = wp::mul(var_1862, var_1865);
            var_1867 = wp::add(var_1860, var_1866);
            // if inside(point,other) and inside(point,own):points[count]=point;count+=1          <L 56>
            var_1869 = inside_0(var_1867, var_1287);
            var_1868 = var_1869;
            if (var_1868) {
                var_1870 = inside_0(var_1867, var_1288);
                var_1868 = var_1868 && var_1870;
            }
            if (var_1868) {
                wp::assign_inplace(var_385, var_1839, var_1867);
                var_1872 = wp::add(var_1839, var_1871);
            }
            var_1873 = wp::where(var_1868, var_1872, var_1839);
        }
        var_1874 = wp::where(var_1849, var_1873, var_1839);
        var_1875 = wp::where(var_1849, var_1867, var_1840);
        // d0=plane_value(vertices[u],other[k]);d1=plane_value(vertices[v],other[k])              <L 53>
        var_1877 = wp::extract(var_1286, var_1703);
        var_1878 = wp::extract(var_1287, var_1876);
        var_1879 = plane_value_0(var_1877, var_1878);
        var_1880 = wp::extract(var_1286, var_1841);
        var_1881 = wp::extract(var_1287, var_1876);
        var_1882 = plane_value_0(var_1880, var_1881);
        // if (d0<wp.float64(0.) and d1>wp.float64(0.)) or (d1<wp.float64(0.) and d0>wp.float64(0.)):       <L 54>
        var_1885 = 0.0;
        var_1886 = (var_1879 < var_1885);
        var_1884 = var_1886;
        if (var_1884) {
            var_1887 = 0.0;
            var_1888 = (var_1882 > var_1887);
            var_1884 = var_1884 && var_1888;
        }
        var_1883 = var_1884;
        if (!var_1883) {
            var_1890 = 0.0;
            var_1891 = (var_1882 < var_1890);
            var_1889 = var_1891;
            if (var_1889) {
                var_1892 = 0.0;
                var_1893 = (var_1879 > var_1892);
                var_1889 = var_1889 && var_1893;
            }
            var_1883 = var_1883 || var_1889;
        }
        if (var_1883) {
            // point=vertices[u]+d0/(d0-d1)*(vertices[v]-vertices[u])                             <L 55>
            var_1894 = wp::extract(var_1286, var_1703);
            var_1895 = wp::sub(var_1879, var_1882);
            var_1896 = wp::div(var_1879, var_1895);
            var_1897 = wp::extract(var_1286, var_1841);
            var_1898 = wp::extract(var_1286, var_1703);
            var_1899 = wp::sub(var_1897, var_1898);
            var_1900 = wp::mul(var_1896, var_1899);
            var_1901 = wp::add(var_1894, var_1900);
            // if inside(point,other) and inside(point,own):points[count]=point;count+=1          <L 56>
            var_1903 = inside_0(var_1901, var_1287);
            var_1902 = var_1903;
            if (var_1902) {
                var_1904 = inside_0(var_1901, var_1288);
                var_1902 = var_1902 && var_1904;
            }
            if (var_1902) {
                wp::assign_inplace(var_385, var_1874, var_1901);
                var_1906 = wp::add(var_1874, var_1905);
            }
            var_1907 = wp::where(var_1902, var_1906, var_1874);
        }
        var_1908 = wp::where(var_1883, var_1907, var_1874);
        var_1909 = wp::where(var_1883, var_1901, var_1875);
        // d0=plane_value(vertices[u],other[k]);d1=plane_value(vertices[v],other[k])              <L 53>
        var_1911 = wp::extract(var_1286, var_1703);
        var_1912 = wp::extract(var_1287, var_1910);
        var_1913 = plane_value_0(var_1911, var_1912);
        var_1914 = wp::extract(var_1286, var_1841);
        var_1915 = wp::extract(var_1287, var_1910);
        var_1916 = plane_value_0(var_1914, var_1915);
        // if (d0<wp.float64(0.) and d1>wp.float64(0.)) or (d1<wp.float64(0.) and d0>wp.float64(0.)):       <L 54>
        var_1919 = 0.0;
        var_1920 = (var_1913 < var_1919);
        var_1918 = var_1920;
        if (var_1918) {
            var_1921 = 0.0;
            var_1922 = (var_1916 > var_1921);
            var_1918 = var_1918 && var_1922;
        }
        var_1917 = var_1918;
        if (!var_1917) {
            var_1924 = 0.0;
            var_1925 = (var_1916 < var_1924);
            var_1923 = var_1925;
            if (var_1923) {
                var_1926 = 0.0;
                var_1927 = (var_1913 > var_1926);
                var_1923 = var_1923 && var_1927;
            }
            var_1917 = var_1917 || var_1923;
        }
        if (var_1917) {
            // point=vertices[u]+d0/(d0-d1)*(vertices[v]-vertices[u])                             <L 55>
            var_1928 = wp::extract(var_1286, var_1703);
            var_1929 = wp::sub(var_1913, var_1916);
            var_1930 = wp::div(var_1913, var_1929);
            var_1931 = wp::extract(var_1286, var_1841);
            var_1932 = wp::extract(var_1286, var_1703);
            var_1933 = wp::sub(var_1931, var_1932);
            var_1934 = wp::mul(var_1930, var_1933);
            var_1935 = wp::add(var_1928, var_1934);
            // if inside(point,other) and inside(point,own):points[count]=point;count+=1          <L 56>
            var_1937 = inside_0(var_1935, var_1287);
            var_1936 = var_1937;
            if (var_1936) {
                var_1938 = inside_0(var_1935, var_1288);
                var_1936 = var_1936 && var_1938;
            }
            if (var_1936) {
                wp::assign_inplace(var_385, var_1908, var_1935);
                var_1940 = wp::add(var_1908, var_1939);
            }
            var_1941 = wp::where(var_1936, var_1940, var_1908);
        }
        var_1942 = wp::where(var_1917, var_1941, var_1908);
        var_1943 = wp::where(var_1917, var_1935, var_1909);
        // d0=plane_value(vertices[u],other[k]);d1=plane_value(vertices[v],other[k])              <L 53>
        var_1945 = wp::extract(var_1286, var_1703);
        var_1946 = wp::extract(var_1287, var_1944);
        var_1947 = plane_value_0(var_1945, var_1946);
        var_1948 = wp::extract(var_1286, var_1841);
        var_1949 = wp::extract(var_1287, var_1944);
        var_1950 = plane_value_0(var_1948, var_1949);
        // if (d0<wp.float64(0.) and d1>wp.float64(0.)) or (d1<wp.float64(0.) and d0>wp.float64(0.)):       <L 54>
        var_1953 = 0.0;
        var_1954 = (var_1947 < var_1953);
        var_1952 = var_1954;
        if (var_1952) {
            var_1955 = 0.0;
            var_1956 = (var_1950 > var_1955);
            var_1952 = var_1952 && var_1956;
        }
        var_1951 = var_1952;
        if (!var_1951) {
            var_1958 = 0.0;
            var_1959 = (var_1950 < var_1958);
            var_1957 = var_1959;
            if (var_1957) {
                var_1960 = 0.0;
                var_1961 = (var_1947 > var_1960);
                var_1957 = var_1957 && var_1961;
            }
            var_1951 = var_1951 || var_1957;
        }
        if (var_1951) {
            // point=vertices[u]+d0/(d0-d1)*(vertices[v]-vertices[u])                             <L 55>
            var_1962 = wp::extract(var_1286, var_1703);
            var_1963 = wp::sub(var_1947, var_1950);
            var_1964 = wp::div(var_1947, var_1963);
            var_1965 = wp::extract(var_1286, var_1841);
            var_1966 = wp::extract(var_1286, var_1703);
            var_1967 = wp::sub(var_1965, var_1966);
            var_1968 = wp::mul(var_1964, var_1967);
            var_1969 = wp::add(var_1962, var_1968);
            // if inside(point,other) and inside(point,own):points[count]=point;count+=1          <L 56>
            var_1971 = inside_0(var_1969, var_1287);
            var_1970 = var_1971;
            if (var_1970) {
                var_1972 = inside_0(var_1969, var_1288);
                var_1970 = var_1970 && var_1972;
            }
            if (var_1970) {
                wp::assign_inplace(var_385, var_1942, var_1969);
                var_1974 = wp::add(var_1942, var_1973);
            }
            var_1975 = wp::where(var_1970, var_1974, var_1942);
        }
        var_1976 = wp::where(var_1951, var_1975, var_1942);
        var_1977 = wp::where(var_1951, var_1969, var_1943);
        // for k in range(4):                                                                     <L 52>
        // d0=plane_value(vertices[u],other[k]);d1=plane_value(vertices[v],other[k])              <L 53>
        var_1980 = wp::extract(var_1286, var_1703);
        var_1981 = wp::extract(var_1287, var_1979);
        var_1982 = plane_value_0(var_1980, var_1981);
        var_1983 = wp::extract(var_1286, var_1978);
        var_1984 = wp::extract(var_1287, var_1979);
        var_1985 = plane_value_0(var_1983, var_1984);
        // if (d0<wp.float64(0.) and d1>wp.float64(0.)) or (d1<wp.float64(0.) and d0>wp.float64(0.)):       <L 54>
        var_1988 = 0.0;
        var_1989 = (var_1982 < var_1988);
        var_1987 = var_1989;
        if (var_1987) {
            var_1990 = 0.0;
            var_1991 = (var_1985 > var_1990);
            var_1987 = var_1987 && var_1991;
        }
        var_1986 = var_1987;
        if (!var_1986) {
            var_1993 = 0.0;
            var_1994 = (var_1985 < var_1993);
            var_1992 = var_1994;
            if (var_1992) {
                var_1995 = 0.0;
                var_1996 = (var_1982 > var_1995);
                var_1992 = var_1992 && var_1996;
            }
            var_1986 = var_1986 || var_1992;
        }
        if (var_1986) {
            // point=vertices[u]+d0/(d0-d1)*(vertices[v]-vertices[u])                             <L 55>
            var_1997 = wp::extract(var_1286, var_1703);
            var_1998 = wp::sub(var_1982, var_1985);
            var_1999 = wp::div(var_1982, var_1998);
            var_2000 = wp::extract(var_1286, var_1978);
            var_2001 = wp::extract(var_1286, var_1703);
            var_2002 = wp::sub(var_2000, var_2001);
            var_2003 = wp::mul(var_1999, var_2002);
            var_2004 = wp::add(var_1997, var_2003);
            // if inside(point,other) and inside(point,own):points[count]=point;count+=1          <L 56>
            var_2006 = inside_0(var_2004, var_1287);
            var_2005 = var_2006;
            if (var_2005) {
                var_2007 = inside_0(var_2004, var_1288);
                var_2005 = var_2005 && var_2007;
            }
            if (var_2005) {
                wp::assign_inplace(var_385, var_1976, var_2004);
                var_2009 = wp::add(var_1976, var_2008);
            }
            var_2010 = wp::where(var_2005, var_2009, var_1976);
        }
        var_2011 = wp::where(var_1986, var_2010, var_1976);
        var_2012 = wp::where(var_1986, var_2004, var_1977);
        // d0=plane_value(vertices[u],other[k]);d1=plane_value(vertices[v],other[k])              <L 53>
        var_2014 = wp::extract(var_1286, var_1703);
        var_2015 = wp::extract(var_1287, var_2013);
        var_2016 = plane_value_0(var_2014, var_2015);
        var_2017 = wp::extract(var_1286, var_1978);
        var_2018 = wp::extract(var_1287, var_2013);
        var_2019 = plane_value_0(var_2017, var_2018);
        // if (d0<wp.float64(0.) and d1>wp.float64(0.)) or (d1<wp.float64(0.) and d0>wp.float64(0.)):       <L 54>
        var_2022 = 0.0;
        var_2023 = (var_2016 < var_2022);
        var_2021 = var_2023;
        if (var_2021) {
            var_2024 = 0.0;
            var_2025 = (var_2019 > var_2024);
            var_2021 = var_2021 && var_2025;
        }
        var_2020 = var_2021;
        if (!var_2020) {
            var_2027 = 0.0;
            var_2028 = (var_2019 < var_2027);
            var_2026 = var_2028;
            if (var_2026) {
                var_2029 = 0.0;
                var_2030 = (var_2016 > var_2029);
                var_2026 = var_2026 && var_2030;
            }
            var_2020 = var_2020 || var_2026;
        }
        if (var_2020) {
            // point=vertices[u]+d0/(d0-d1)*(vertices[v]-vertices[u])                             <L 55>
            var_2031 = wp::extract(var_1286, var_1703);
            var_2032 = wp::sub(var_2016, var_2019);
            var_2033 = wp::div(var_2016, var_2032);
            var_2034 = wp::extract(var_1286, var_1978);
            var_2035 = wp::extract(var_1286, var_1703);
            var_2036 = wp::sub(var_2034, var_2035);
            var_2037 = wp::mul(var_2033, var_2036);
            var_2038 = wp::add(var_2031, var_2037);
            // if inside(point,other) and inside(point,own):points[count]=point;count+=1          <L 56>
            var_2040 = inside_0(var_2038, var_1287);
            var_2039 = var_2040;
            if (var_2039) {
                var_2041 = inside_0(var_2038, var_1288);
                var_2039 = var_2039 && var_2041;
            }
            if (var_2039) {
                wp::assign_inplace(var_385, var_2011, var_2038);
                var_2043 = wp::add(var_2011, var_2042);
            }
            var_2044 = wp::where(var_2039, var_2043, var_2011);
        }
        var_2045 = wp::where(var_2020, var_2044, var_2011);
        var_2046 = wp::where(var_2020, var_2038, var_2012);
        // d0=plane_value(vertices[u],other[k]);d1=plane_value(vertices[v],other[k])              <L 53>
        var_2048 = wp::extract(var_1286, var_1703);
        var_2049 = wp::extract(var_1287, var_2047);
        var_2050 = plane_value_0(var_2048, var_2049);
        var_2051 = wp::extract(var_1286, var_1978);
        var_2052 = wp::extract(var_1287, var_2047);
        var_2053 = plane_value_0(var_2051, var_2052);
        // if (d0<wp.float64(0.) and d1>wp.float64(0.)) or (d1<wp.float64(0.) and d0>wp.float64(0.)):       <L 54>
        var_2056 = 0.0;
        var_2057 = (var_2050 < var_2056);
        var_2055 = var_2057;
        if (var_2055) {
            var_2058 = 0.0;
            var_2059 = (var_2053 > var_2058);
            var_2055 = var_2055 && var_2059;
        }
        var_2054 = var_2055;
        if (!var_2054) {
            var_2061 = 0.0;
            var_2062 = (var_2053 < var_2061);
            var_2060 = var_2062;
            if (var_2060) {
                var_2063 = 0.0;
                var_2064 = (var_2050 > var_2063);
                var_2060 = var_2060 && var_2064;
            }
            var_2054 = var_2054 || var_2060;
        }
        if (var_2054) {
            // point=vertices[u]+d0/(d0-d1)*(vertices[v]-vertices[u])                             <L 55>
            var_2065 = wp::extract(var_1286, var_1703);
            var_2066 = wp::sub(var_2050, var_2053);
            var_2067 = wp::div(var_2050, var_2066);
            var_2068 = wp::extract(var_1286, var_1978);
            var_2069 = wp::extract(var_1286, var_1703);
            var_2070 = wp::sub(var_2068, var_2069);
            var_2071 = wp::mul(var_2067, var_2070);
            var_2072 = wp::add(var_2065, var_2071);
            // if inside(point,other) and inside(point,own):points[count]=point;count+=1          <L 56>
            var_2074 = inside_0(var_2072, var_1287);
            var_2073 = var_2074;
            if (var_2073) {
                var_2075 = inside_0(var_2072, var_1288);
                var_2073 = var_2073 && var_2075;
            }
            if (var_2073) {
                wp::assign_inplace(var_385, var_2045, var_2072);
                var_2077 = wp::add(var_2045, var_2076);
            }
            var_2078 = wp::where(var_2073, var_2077, var_2045);
        }
        var_2079 = wp::where(var_2054, var_2078, var_2045);
        var_2080 = wp::where(var_2054, var_2072, var_2046);
        // d0=plane_value(vertices[u],other[k]);d1=plane_value(vertices[v],other[k])              <L 53>
        var_2082 = wp::extract(var_1286, var_1703);
        var_2083 = wp::extract(var_1287, var_2081);
        var_2084 = plane_value_0(var_2082, var_2083);
        var_2085 = wp::extract(var_1286, var_1978);
        var_2086 = wp::extract(var_1287, var_2081);
        var_2087 = plane_value_0(var_2085, var_2086);
        // if (d0<wp.float64(0.) and d1>wp.float64(0.)) or (d1<wp.float64(0.) and d0>wp.float64(0.)):       <L 54>
        var_2090 = 0.0;
        var_2091 = (var_2084 < var_2090);
        var_2089 = var_2091;
        if (var_2089) {
            var_2092 = 0.0;
            var_2093 = (var_2087 > var_2092);
            var_2089 = var_2089 && var_2093;
        }
        var_2088 = var_2089;
        if (!var_2088) {
            var_2095 = 0.0;
            var_2096 = (var_2087 < var_2095);
            var_2094 = var_2096;
            if (var_2094) {
                var_2097 = 0.0;
                var_2098 = (var_2084 > var_2097);
                var_2094 = var_2094 && var_2098;
            }
            var_2088 = var_2088 || var_2094;
        }
        if (var_2088) {
            // point=vertices[u]+d0/(d0-d1)*(vertices[v]-vertices[u])                             <L 55>
            var_2099 = wp::extract(var_1286, var_1703);
            var_2100 = wp::sub(var_2084, var_2087);
            var_2101 = wp::div(var_2084, var_2100);
            var_2102 = wp::extract(var_1286, var_1978);
            var_2103 = wp::extract(var_1286, var_1703);
            var_2104 = wp::sub(var_2102, var_2103);
            var_2105 = wp::mul(var_2101, var_2104);
            var_2106 = wp::add(var_2099, var_2105);
            // if inside(point,other) and inside(point,own):points[count]=point;count+=1          <L 56>
            var_2108 = inside_0(var_2106, var_1287);
            var_2107 = var_2108;
            if (var_2107) {
                var_2109 = inside_0(var_2106, var_1288);
                var_2107 = var_2107 && var_2109;
            }
            if (var_2107) {
                wp::assign_inplace(var_385, var_2079, var_2106);
                var_2111 = wp::add(var_2079, var_2110);
            }
            var_2112 = wp::where(var_2107, var_2111, var_2079);
        }
        var_2113 = wp::where(var_2088, var_2112, var_2079);
        var_2114 = wp::where(var_2088, var_2106, var_2080);
        // if count==0:return                                                                     <L 57>
        var_2116 = (var_2113 == var_2115);
        if (var_2116) {
            continue;
        }
        // center=wp.vec3d(wp.float64(0.))                                                        <L 58>
        var_2117 = 0.0;
        var_2118 = wp::vec_t<3, wp::float64>(var_2117);
        // for k in range(count):center+=points[k]                                                <L 59>
        var_2119 = wp::range(var_2113);
        start_for_3:;
            if (iter_cmp(var_2119) == 0) goto end_for_3;
            var_2120 = wp::iter_next(var_2119);
            var_2121 = wp::extract(var_385, var_2120);
            var_2122 = wp::add(var_2118, var_2121);
            wp::assign(var_2118, var_2122);
            goto start_for_3;
        end_for_3:;
        // center/=wp.float64(count);face=int(-1);best=wp.float64(1e30)                           <L 60>
        var_2123 = wp::float64(var_2113);
        var_2124 = wp::div(var_2118, var_2123);
        var_2126 = wp::int(var_2125);
        var_2127 = 1e+30;
        // for k in range(ptr[c],ptr[c+1]):                                                       <L 61>
        var_2128 = wp::address(var_ptr, var_1);
        var_2130 = wp::add(var_1, var_2129);
        var_2131 = wp::address(var_ptr, var_2130);
        var_2133 = wp::load(var_2128);
        var_2134 = wp::load(var_2131);
        var_2132 = wp::range(var_2133, var_2134);
        start_for_5:;
            if (iter_cmp(var_2132) == 0) goto end_for_5;
            var_2135 = wp::iter_next(var_2132);
            // j=ids[k];d=wp.length(center-closest(center,tri[j,0],tri[j,1],tri[j,2]))            <L 62>
            var_2136 = wp::address(var_ids, var_2135);
            var_2138 = wp::load(var_2136);
            var_2137 = wp::copy(var_2138);
            var_2140 = wp::address(var_tri, var_2137, var_2139);
            var_2142 = wp::address(var_tri, var_2137, var_2141);
            var_2144 = wp::address(var_tri, var_2137, var_2143);
            var_2146 = wp::load(var_2140);
            var_2147 = wp::load(var_2142);
            var_2148 = wp::load(var_2144);
            var_2145 = closest_0(var_2124, var_2146, var_2147, var_2148);
            var_2149 = wp::sub(var_2124, var_2145);
            var_2150 = wp::length(var_2149);
            // if d<best:best=d;face=j                                                            <L 63>
            var_2151 = (var_2150 < var_2127);
            if (var_2151) {
                var_2152 = wp::copy(var_2150);
                var_2153 = wp::copy(var_2137);
            }
            var_2154 = wp::where(var_2151, var_2153, var_2126);
            var_2155 = wp::where(var_2151, var_2152, var_2127);
            wp::assign(var_377, var_2150);
            wp::assign(var_2126, var_2154);
            wp::assign(var_2127, var_2155);
            goto start_for_5;
        end_for_5:;
        // bound=wp.float64(0.)                                                                   <L 64>
        var_2156 = 0.0;
        // for k in range(count):bound=wp.max(bound,wp.length(points[k]-closest(points[k],tri[face,0],tri[face,1],tri[face,2])))       <L 65>
        var_2157 = wp::range(var_2113);
        start_for_7:;
            if (iter_cmp(var_2157) == 0) goto end_for_7;
            var_2158 = wp::iter_next(var_2157);
            var_2159 = wp::extract(var_385, var_2158);
            var_2160 = wp::extract(var_385, var_2158);
            var_2162 = wp::address(var_tri, var_2126, var_2161);
            var_2164 = wp::address(var_tri, var_2126, var_2163);
            var_2166 = wp::address(var_tri, var_2126, var_2165);
            var_2168 = wp::load(var_2162);
            var_2169 = wp::load(var_2164);
            var_2170 = wp::load(var_2166);
            var_2167 = closest_0(var_2160, var_2168, var_2169, var_2170);
            var_2171 = wp::sub(var_2159, var_2167);
            var_2172 = wp::length(var_2171);
            var_2173 = wp::max(var_2156, var_2172);
            wp::assign(var_2156, var_2173);
            goto start_for_7;
        end_for_7:;
        // if bound>target:                                                                       <L 66>
        var_2174 = (var_2156 > var_target);
        if (var_2174) {
            // for k in range(ptr[c],ptr[c+1]):                                                   <L 67>
            var_2175 = wp::address(var_ptr, var_1);
            var_2177 = wp::add(var_1, var_2176);
            var_2178 = wp::address(var_ptr, var_2177);
            var_2180 = wp::load(var_2175);
            var_2181 = wp::load(var_2178);
            var_2179 = wp::range(var_2180, var_2181);
            var_2182 = wp::copy(var_1703);
            start_for_9:;
                if (iter_cmp(var_2179) == 0) goto end_for_9;
                var_2183 = wp::iter_next(var_2179);
                // j=ids[k];candidate=wp.float64(0.)                                              <L 68>
                var_2184 = wp::address(var_ids, var_2183);
                var_2186 = wp::load(var_2184);
                var_2185 = wp::copy(var_2186);
                var_2187 = 0.0;
                // for u in range(count):candidate=wp.max(candidate,wp.length(points[u]-closest(points[u],tri[j,0],tri[j,1],tri[j,2])))       <L 69>
                var_2188 = wp::range(var_2113);
                start_for_11:;
                    if (iter_cmp(var_2188) == 0) goto end_for_11;
                    var_2189 = wp::iter_next(var_2188);
                    var_2190 = wp::extract(var_385, var_2189);
                    var_2191 = wp::extract(var_385, var_2189);
                    var_2193 = wp::address(var_tri, var_2185, var_2192);
                    var_2195 = wp::address(var_tri, var_2185, var_2194);
                    var_2197 = wp::address(var_tri, var_2185, var_2196);
                    var_2199 = wp::load(var_2193);
                    var_2200 = wp::load(var_2195);
                    var_2201 = wp::load(var_2197);
                    var_2198 = closest_0(var_2191, var_2199, var_2200, var_2201);
                    var_2202 = wp::sub(var_2190, var_2198);
                    var_2203 = wp::length(var_2202);
                    var_2204 = wp::max(var_2187, var_2203);
                    wp::assign(var_2187, var_2204);
                    goto start_for_11;
                end_for_11:;
                // bound=wp.min(bound,candidate)                                                  <L 70>
                var_2205 = wp::min(var_2156, var_2187);
                // if bound<=target:break                                                         <L 71>
                var_2206 = (var_2205 <= var_target);
                if (var_2206) {
                    wp::assign(var_2182, var_2189);
                    wp::assign(var_2137, var_2185);
                    wp::assign(var_2156, var_2205);
                    goto end_for_9;
                }
                var_2207 = wp::where(var_2206, var_2182, var_2189);
                var_2208 = wp::where(var_2206, var_2137, var_2185);
                var_2209 = wp::where(var_2206, var_2156, var_2205);
                wp::assign(var_2182, var_2207);
                wp::assign(var_2137, var_2208);
                wp::assign(var_2156, var_2209);
                goto start_for_9;
            end_for_9:;
        }
        var_2210 = wp::where(var_2174, var_2183, var_2158);
        var_2211 = wp::where(var_2174, var_2182, var_1703);
        // wp.atomic_max(upper,0,bound)                                                           <L 72>
        var_2213 = wp::atomic_max(var_upper, var_2212, var_2156);
        // if bound>target:wp.atomic_max(unresolved,i,1)                                          <L 73>
        var_2214 = (var_2156 > var_target);
        if (var_2214) {
            var_2216 = wp::atomic_max(var_unresolved, var_0, var_2215);
        }
    }
}


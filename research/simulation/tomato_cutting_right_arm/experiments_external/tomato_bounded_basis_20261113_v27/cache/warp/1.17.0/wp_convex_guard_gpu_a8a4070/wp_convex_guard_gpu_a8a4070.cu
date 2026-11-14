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



extern "C" __global__ void prove_97607774_cuda_kernel_forward(
    wp::launch_bounds_t<2> dim,
    wp::array_t<wp::mat_t<4, 3, wp::float64>> var_tets,
    wp::array_t<wp::int32> var_active_count,
    wp::array_t<wp::int32> var_active_ids,
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
        const wp::int32 var_2 = 0;
        wp::int32* var_3;
        const wp::int32 var_4 = 64;
        wp::range_t var_5;
        wp::int32 var_6;
        wp::int32 var_7;
        wp::int32* var_8;
        wp::int32 var_9;
        wp::int32 var_10;
        wp::mat_t<4, 3, wp::float64>* var_11;
        wp::mat_t<4, 3, wp::float64> var_12;
        wp::mat_t<4, 3, wp::float64> var_13;
        wp::mat_t<4, 3, wp::float64>* var_14;
        wp::mat_t<4, 3, wp::float64> var_15;
        wp::mat_t<4, 3, wp::float64> var_16;
        const bool var_17 = true;
        const wp::int32 var_18 = 0;
        const wp::int32 var_19 = 0;
        wp::float64 var_20;
        const wp::int32 var_21 = 1;
        wp::float64 var_22;
        wp::float64 var_23;
        const wp::int32 var_24 = 2;
        wp::float64 var_25;
        const wp::int32 var_26 = 3;
        wp::float64 var_27;
        wp::float64 var_28;
        wp::float64 var_29;
        const wp::int32 var_30 = 0;
        wp::float64 var_31;
        const wp::int32 var_32 = 1;
        wp::float64 var_33;
        wp::float64 var_34;
        const wp::int32 var_35 = 2;
        wp::float64 var_36;
        const wp::int32 var_37 = 3;
        wp::float64 var_38;
        wp::float64 var_39;
        wp::float64 var_40;
        bool var_41;
        wp::float64 var_42;
        wp::float64 var_43;
        wp::vec_t<3, wp::float64>* var_44;
        wp::float64 var_45;
        wp::vec_t<3, wp::float64> var_46;
        bool var_47;
        wp::vec_t<3, wp::float64>* var_48;
        wp::float64 var_49;
        wp::vec_t<3, wp::float64> var_50;
        wp::float64 var_51;
        wp::float64 var_52;
        bool var_53;
        const bool var_54 = false;
        bool var_55;
        const wp::int32 var_56 = 1;
        const wp::int32 var_57 = 0;
        wp::float64 var_58;
        const wp::int32 var_59 = 1;
        wp::float64 var_60;
        wp::float64 var_61;
        const wp::int32 var_62 = 2;
        wp::float64 var_63;
        const wp::int32 var_64 = 3;
        wp::float64 var_65;
        wp::float64 var_66;
        wp::float64 var_67;
        const wp::int32 var_68 = 0;
        wp::float64 var_69;
        const wp::int32 var_70 = 1;
        wp::float64 var_71;
        wp::float64 var_72;
        const wp::int32 var_73 = 2;
        wp::float64 var_74;
        const wp::int32 var_75 = 3;
        wp::float64 var_76;
        wp::float64 var_77;
        wp::float64 var_78;
        bool var_79;
        wp::float64 var_80;
        wp::float64 var_81;
        wp::vec_t<3, wp::float64>* var_82;
        wp::float64 var_83;
        wp::vec_t<3, wp::float64> var_84;
        bool var_85;
        wp::vec_t<3, wp::float64>* var_86;
        wp::float64 var_87;
        wp::vec_t<3, wp::float64> var_88;
        wp::float64 var_89;
        wp::float64 var_90;
        bool var_91;
        const bool var_92 = false;
        bool var_93;
        const wp::int32 var_94 = 2;
        const wp::int32 var_95 = 0;
        wp::float64 var_96;
        const wp::int32 var_97 = 1;
        wp::float64 var_98;
        wp::float64 var_99;
        const wp::int32 var_100 = 2;
        wp::float64 var_101;
        const wp::int32 var_102 = 3;
        wp::float64 var_103;
        wp::float64 var_104;
        wp::float64 var_105;
        const wp::int32 var_106 = 0;
        wp::float64 var_107;
        const wp::int32 var_108 = 1;
        wp::float64 var_109;
        wp::float64 var_110;
        const wp::int32 var_111 = 2;
        wp::float64 var_112;
        const wp::int32 var_113 = 3;
        wp::float64 var_114;
        wp::float64 var_115;
        wp::float64 var_116;
        bool var_117;
        wp::float64 var_118;
        wp::float64 var_119;
        wp::vec_t<3, wp::float64>* var_120;
        wp::float64 var_121;
        wp::vec_t<3, wp::float64> var_122;
        bool var_123;
        wp::vec_t<3, wp::float64>* var_124;
        wp::float64 var_125;
        wp::vec_t<3, wp::float64> var_126;
        wp::float64 var_127;
        wp::float64 var_128;
        bool var_129;
        const bool var_130 = false;
        bool var_131;
        bool var_132;
        wp::float64 var_133;
        wp::mat_t<4, 4, wp::float64> var_134;
        wp::int32* var_135;
        const wp::int32 var_136 = 0;
        bool var_137;
        wp::int32 var_138;
        wp::float64 var_139;
        const wp::int32 var_140 = 0;
        const wp::int32 var_141 = 1;
        const wp::int32 var_142 = 0;
        wp::vec_t<3, wp::float64> var_143;
        wp::vec_t<3, wp::float64> var_144;
        wp::vec_t<3, wp::float64> var_145;
        wp::float64 var_146;
        wp::float64 var_147;
        const wp::int32 var_148 = 2;
        const wp::int32 var_149 = 0;
        wp::vec_t<3, wp::float64> var_150;
        wp::vec_t<3, wp::float64> var_151;
        wp::vec_t<3, wp::float64> var_152;
        wp::float64 var_153;
        wp::float64 var_154;
        const wp::int32 var_155 = 1;
        wp::vec_t<3, wp::float64> var_156;
        wp::vec_t<3, wp::float64> var_157;
        wp::vec_t<3, wp::float64> var_158;
        wp::float64 var_159;
        wp::float64 var_160;
        const wp::int32 var_161 = 3;
        const wp::int32 var_162 = 0;
        wp::vec_t<3, wp::float64> var_163;
        wp::vec_t<3, wp::float64> var_164;
        wp::vec_t<3, wp::float64> var_165;
        wp::float64 var_166;
        wp::float64 var_167;
        const wp::int32 var_168 = 1;
        wp::vec_t<3, wp::float64> var_169;
        wp::vec_t<3, wp::float64> var_170;
        wp::vec_t<3, wp::float64> var_171;
        wp::float64 var_172;
        wp::float64 var_173;
        const wp::int32 var_174 = 2;
        wp::vec_t<3, wp::float64> var_175;
        wp::vec_t<3, wp::float64> var_176;
        wp::vec_t<3, wp::float64> var_177;
        wp::float64 var_178;
        wp::float64 var_179;
        const wp::int32 var_180 = 0;
        const wp::int32 var_181 = 1;
        wp::int32 var_182;
        const wp::int32 var_183 = 4;
        wp::int32 var_184;
        wp::vec_t<3, wp::float64> var_185;
        const wp::int32 var_186 = 2;
        wp::int32 var_187;
        const wp::int32 var_188 = 4;
        wp::int32 var_189;
        wp::vec_t<3, wp::float64> var_190;
        const wp::int32 var_191 = 3;
        wp::int32 var_192;
        const wp::int32 var_193 = 4;
        wp::int32 var_194;
        wp::vec_t<3, wp::float64> var_195;
        wp::vec_t<3, wp::float64> var_196;
        wp::vec_t<3, wp::float64> var_197;
        wp::vec_t<3, wp::float64> var_198;
        wp::float64 var_199;
        wp::float64 var_200;
        bool var_201;
        const bool var_202 = false;
        wp::vec_t<3, wp::float64> var_203;
        wp::vec_t<3, wp::float64> var_204;
        wp::vec_t<3, wp::float64> var_205;
        wp::float64 var_206;
        wp::float64 var_207;
        bool var_208;
        wp::vec_t<3, wp::float64> var_209;
        wp::vec_t<3, wp::float64> var_210;
        wp::float64 var_211;
        wp::float64 var_212;
        const wp::int32 var_213 = 0;
        wp::float64 var_214;
        const wp::int32 var_215 = 1;
        wp::float64 var_216;
        const wp::int32 var_217 = 2;
        wp::float64 var_218;
        wp::vec_t<4, wp::float64> var_219;
        wp::vec_t<3, wp::float64> var_220;
        wp::float64 var_221;
        wp::float64 var_222;
        wp::float64 var_223;
        wp::float64 var_224;
        wp::float64 var_225;
        bool var_226;
        const bool var_227 = false;
        bool var_228;
        bool var_229;
        wp::vec_t<3, wp::float64> var_230;
        const wp::int32 var_231 = 1;
        const wp::int32 var_232 = 1;
        wp::int32 var_233;
        const wp::int32 var_234 = 4;
        wp::int32 var_235;
        wp::vec_t<3, wp::float64> var_236;
        const wp::int32 var_237 = 2;
        wp::int32 var_238;
        const wp::int32 var_239 = 4;
        wp::int32 var_240;
        wp::vec_t<3, wp::float64> var_241;
        const wp::int32 var_242 = 3;
        wp::int32 var_243;
        const wp::int32 var_244 = 4;
        wp::int32 var_245;
        wp::vec_t<3, wp::float64> var_246;
        wp::vec_t<3, wp::float64> var_247;
        wp::vec_t<3, wp::float64> var_248;
        wp::vec_t<3, wp::float64> var_249;
        wp::float64 var_250;
        wp::float64 var_251;
        bool var_252;
        const bool var_253 = false;
        wp::vec_t<3, wp::float64> var_254;
        wp::vec_t<3, wp::float64> var_255;
        wp::vec_t<3, wp::float64> var_256;
        wp::float64 var_257;
        wp::float64 var_258;
        bool var_259;
        wp::vec_t<3, wp::float64> var_260;
        wp::vec_t<3, wp::float64> var_261;
        wp::float64 var_262;
        wp::float64 var_263;
        const wp::int32 var_264 = 0;
        wp::float64 var_265;
        const wp::int32 var_266 = 1;
        wp::float64 var_267;
        const wp::int32 var_268 = 2;
        wp::float64 var_269;
        wp::vec_t<4, wp::float64> var_270;
        wp::vec_t<3, wp::float64> var_271;
        wp::float64 var_272;
        wp::float64 var_273;
        wp::float64 var_274;
        wp::float64 var_275;
        wp::float64 var_276;
        bool var_277;
        const bool var_278 = false;
        bool var_279;
        bool var_280;
        wp::vec_t<3, wp::float64> var_281;
        wp::float64 var_282;
        const wp::int32 var_283 = 2;
        const wp::int32 var_284 = 1;
        wp::int32 var_285;
        const wp::int32 var_286 = 4;
        wp::int32 var_287;
        wp::vec_t<3, wp::float64> var_288;
        const wp::int32 var_289 = 2;
        wp::int32 var_290;
        const wp::int32 var_291 = 4;
        wp::int32 var_292;
        wp::vec_t<3, wp::float64> var_293;
        const wp::int32 var_294 = 3;
        wp::int32 var_295;
        const wp::int32 var_296 = 4;
        wp::int32 var_297;
        wp::vec_t<3, wp::float64> var_298;
        wp::vec_t<3, wp::float64> var_299;
        wp::vec_t<3, wp::float64> var_300;
        wp::vec_t<3, wp::float64> var_301;
        wp::float64 var_302;
        wp::float64 var_303;
        bool var_304;
        const bool var_305 = false;
        wp::vec_t<3, wp::float64> var_306;
        wp::vec_t<3, wp::float64> var_307;
        wp::vec_t<3, wp::float64> var_308;
        wp::float64 var_309;
        wp::float64 var_310;
        bool var_311;
        wp::vec_t<3, wp::float64> var_312;
        wp::vec_t<3, wp::float64> var_313;
        wp::float64 var_314;
        wp::float64 var_315;
        const wp::int32 var_316 = 0;
        wp::float64 var_317;
        const wp::int32 var_318 = 1;
        wp::float64 var_319;
        const wp::int32 var_320 = 2;
        wp::float64 var_321;
        wp::vec_t<4, wp::float64> var_322;
        wp::vec_t<3, wp::float64> var_323;
        wp::float64 var_324;
        wp::float64 var_325;
        wp::float64 var_326;
        wp::float64 var_327;
        wp::float64 var_328;
        bool var_329;
        const bool var_330 = false;
        bool var_331;
        bool var_332;
        wp::vec_t<3, wp::float64> var_333;
        wp::float64 var_334;
        const wp::int32 var_335 = 3;
        const wp::int32 var_336 = 1;
        wp::int32 var_337;
        const wp::int32 var_338 = 4;
        wp::int32 var_339;
        wp::vec_t<3, wp::float64> var_340;
        const wp::int32 var_341 = 2;
        wp::int32 var_342;
        const wp::int32 var_343 = 4;
        wp::int32 var_344;
        wp::vec_t<3, wp::float64> var_345;
        const wp::int32 var_346 = 3;
        wp::int32 var_347;
        const wp::int32 var_348 = 4;
        wp::int32 var_349;
        wp::vec_t<3, wp::float64> var_350;
        wp::vec_t<3, wp::float64> var_351;
        wp::vec_t<3, wp::float64> var_352;
        wp::vec_t<3, wp::float64> var_353;
        wp::float64 var_354;
        wp::float64 var_355;
        bool var_356;
        const bool var_357 = false;
        wp::vec_t<3, wp::float64> var_358;
        wp::vec_t<3, wp::float64> var_359;
        wp::vec_t<3, wp::float64> var_360;
        wp::float64 var_361;
        wp::float64 var_362;
        bool var_363;
        wp::vec_t<3, wp::float64> var_364;
        wp::vec_t<3, wp::float64> var_365;
        wp::float64 var_366;
        wp::float64 var_367;
        const wp::int32 var_368 = 0;
        wp::float64 var_369;
        const wp::int32 var_370 = 1;
        wp::float64 var_371;
        const wp::int32 var_372 = 2;
        wp::float64 var_373;
        wp::vec_t<4, wp::float64> var_374;
        wp::vec_t<3, wp::float64> var_375;
        wp::float64 var_376;
        wp::float64 var_377;
        wp::float64 var_378;
        wp::float64 var_379;
        wp::float64 var_380;
        bool var_381;
        const bool var_382 = false;
        bool var_383;
        bool var_384;
        wp::vec_t<3, wp::float64> var_385;
        wp::float64 var_386;
        bool var_387;
        const wp::int32 var_388 = 1;
        wp::int32 var_389;
        wp::mat_t<4, 4, wp::float64>* var_390;
        wp::mat_t<4, 4, wp::float64> var_391;
        wp::mat_t<4, 4, wp::float64> var_392;
        wp::float64 var_393;
        wp::mat_t<56, 3, wp::float64> var_394;
        const wp::int32 var_395 = 0;
        wp::int32 var_396;
        const wp::int32 var_397 = 0;
        wp::vec_t<3, wp::float64> var_398;
        bool var_399;
        wp::vec_t<3, wp::float64> var_400;
        const wp::int32 var_401 = 1;
        wp::int32 var_402;
        wp::int32 var_403;
        wp::vec_t<3, wp::float64> var_404;
        bool var_405;
        wp::vec_t<3, wp::float64> var_406;
        const wp::int32 var_407 = 1;
        wp::int32 var_408;
        wp::int32 var_409;
        const wp::int32 var_410 = 1;
        wp::vec_t<3, wp::float64> var_411;
        bool var_412;
        wp::vec_t<3, wp::float64> var_413;
        const wp::int32 var_414 = 1;
        wp::int32 var_415;
        wp::int32 var_416;
        wp::vec_t<3, wp::float64> var_417;
        bool var_418;
        wp::vec_t<3, wp::float64> var_419;
        const wp::int32 var_420 = 1;
        wp::int32 var_421;
        wp::int32 var_422;
        const wp::int32 var_423 = 2;
        wp::vec_t<3, wp::float64> var_424;
        bool var_425;
        wp::vec_t<3, wp::float64> var_426;
        const wp::int32 var_427 = 1;
        wp::int32 var_428;
        wp::int32 var_429;
        wp::vec_t<3, wp::float64> var_430;
        bool var_431;
        wp::vec_t<3, wp::float64> var_432;
        const wp::int32 var_433 = 1;
        wp::int32 var_434;
        wp::int32 var_435;
        const wp::int32 var_436 = 3;
        wp::vec_t<3, wp::float64> var_437;
        bool var_438;
        wp::vec_t<3, wp::float64> var_439;
        const wp::int32 var_440 = 1;
        wp::int32 var_441;
        wp::int32 var_442;
        wp::vec_t<3, wp::float64> var_443;
        bool var_444;
        wp::vec_t<3, wp::float64> var_445;
        const wp::int32 var_446 = 1;
        wp::int32 var_447;
        wp::int32 var_448;
        const wp::int32 var_449 = 0;
        wp::mat_t<4, 3, wp::float64> var_450;
        wp::mat_t<4, 4, wp::float64> var_451;
        wp::mat_t<4, 4, wp::float64> var_452;
        const wp::int32 var_453 = 1;
        bool var_454;
        wp::mat_t<4, 3, wp::float64> var_455;
        wp::mat_t<4, 4, wp::float64> var_456;
        wp::mat_t<4, 4, wp::float64> var_457;
        wp::mat_t<4, 3, wp::float64> var_458;
        wp::mat_t<4, 4, wp::float64> var_459;
        wp::mat_t<4, 4, wp::float64> var_460;
        const wp::int32 var_461 = 0;
        const wp::int32 var_462 = 1;
        const wp::int32 var_463 = 0;
        const wp::int32 var_464 = 0;
        wp::vec_t<3, wp::float64> var_465;
        wp::vec_t<4, wp::float64> var_466;
        wp::float64 var_467;
        wp::vec_t<3, wp::float64> var_468;
        wp::vec_t<4, wp::float64> var_469;
        wp::float64 var_470;
        bool var_471;
        bool var_472;
        wp::float64 var_473;
        bool var_474;
        wp::float64 var_475;
        bool var_476;
        bool var_477;
        wp::float64 var_478;
        bool var_479;
        wp::float64 var_480;
        bool var_481;
        wp::vec_t<3, wp::float64> var_482;
        wp::float64 var_483;
        wp::float64 var_484;
        wp::vec_t<3, wp::float64> var_485;
        wp::vec_t<3, wp::float64> var_486;
        wp::vec_t<3, wp::float64> var_487;
        wp::vec_t<3, wp::float64> var_488;
        wp::vec_t<3, wp::float64> var_489;
        bool var_490;
        bool var_491;
        bool var_492;
        const wp::int32 var_493 = 1;
        wp::int32 var_494;
        wp::int32 var_495;
        wp::int32 var_496;
        const wp::int32 var_497 = 1;
        wp::vec_t<3, wp::float64> var_498;
        wp::vec_t<4, wp::float64> var_499;
        wp::float64 var_500;
        wp::vec_t<3, wp::float64> var_501;
        wp::vec_t<4, wp::float64> var_502;
        wp::float64 var_503;
        bool var_504;
        bool var_505;
        wp::float64 var_506;
        bool var_507;
        wp::float64 var_508;
        bool var_509;
        bool var_510;
        wp::float64 var_511;
        bool var_512;
        wp::float64 var_513;
        bool var_514;
        wp::vec_t<3, wp::float64> var_515;
        wp::float64 var_516;
        wp::float64 var_517;
        wp::vec_t<3, wp::float64> var_518;
        wp::vec_t<3, wp::float64> var_519;
        wp::vec_t<3, wp::float64> var_520;
        wp::vec_t<3, wp::float64> var_521;
        wp::vec_t<3, wp::float64> var_522;
        bool var_523;
        bool var_524;
        bool var_525;
        const wp::int32 var_526 = 1;
        wp::int32 var_527;
        wp::int32 var_528;
        wp::int32 var_529;
        wp::vec_t<3, wp::float64> var_530;
        const wp::int32 var_531 = 2;
        wp::vec_t<3, wp::float64> var_532;
        wp::vec_t<4, wp::float64> var_533;
        wp::float64 var_534;
        wp::vec_t<3, wp::float64> var_535;
        wp::vec_t<4, wp::float64> var_536;
        wp::float64 var_537;
        bool var_538;
        bool var_539;
        wp::float64 var_540;
        bool var_541;
        wp::float64 var_542;
        bool var_543;
        bool var_544;
        wp::float64 var_545;
        bool var_546;
        wp::float64 var_547;
        bool var_548;
        wp::vec_t<3, wp::float64> var_549;
        wp::float64 var_550;
        wp::float64 var_551;
        wp::vec_t<3, wp::float64> var_552;
        wp::vec_t<3, wp::float64> var_553;
        wp::vec_t<3, wp::float64> var_554;
        wp::vec_t<3, wp::float64> var_555;
        wp::vec_t<3, wp::float64> var_556;
        bool var_557;
        bool var_558;
        bool var_559;
        const wp::int32 var_560 = 1;
        wp::int32 var_561;
        wp::int32 var_562;
        wp::int32 var_563;
        wp::vec_t<3, wp::float64> var_564;
        const wp::int32 var_565 = 3;
        wp::vec_t<3, wp::float64> var_566;
        wp::vec_t<4, wp::float64> var_567;
        wp::float64 var_568;
        wp::vec_t<3, wp::float64> var_569;
        wp::vec_t<4, wp::float64> var_570;
        wp::float64 var_571;
        bool var_572;
        bool var_573;
        wp::float64 var_574;
        bool var_575;
        wp::float64 var_576;
        bool var_577;
        bool var_578;
        wp::float64 var_579;
        bool var_580;
        wp::float64 var_581;
        bool var_582;
        wp::vec_t<3, wp::float64> var_583;
        wp::float64 var_584;
        wp::float64 var_585;
        wp::vec_t<3, wp::float64> var_586;
        wp::vec_t<3, wp::float64> var_587;
        wp::vec_t<3, wp::float64> var_588;
        wp::vec_t<3, wp::float64> var_589;
        wp::vec_t<3, wp::float64> var_590;
        bool var_591;
        bool var_592;
        bool var_593;
        const wp::int32 var_594 = 1;
        wp::int32 var_595;
        wp::int32 var_596;
        wp::int32 var_597;
        wp::vec_t<3, wp::float64> var_598;
        const wp::int32 var_599 = 2;
        const wp::int32 var_600 = 0;
        const wp::int32 var_601 = 0;
        wp::vec_t<3, wp::float64> var_602;
        wp::vec_t<4, wp::float64> var_603;
        wp::float64 var_604;
        wp::vec_t<3, wp::float64> var_605;
        wp::vec_t<4, wp::float64> var_606;
        wp::float64 var_607;
        bool var_608;
        bool var_609;
        wp::float64 var_610;
        bool var_611;
        wp::float64 var_612;
        bool var_613;
        bool var_614;
        wp::float64 var_615;
        bool var_616;
        wp::float64 var_617;
        bool var_618;
        wp::vec_t<3, wp::float64> var_619;
        wp::float64 var_620;
        wp::float64 var_621;
        wp::vec_t<3, wp::float64> var_622;
        wp::vec_t<3, wp::float64> var_623;
        wp::vec_t<3, wp::float64> var_624;
        wp::vec_t<3, wp::float64> var_625;
        wp::vec_t<3, wp::float64> var_626;
        bool var_627;
        bool var_628;
        bool var_629;
        const wp::int32 var_630 = 1;
        wp::int32 var_631;
        wp::int32 var_632;
        wp::int32 var_633;
        wp::vec_t<3, wp::float64> var_634;
        const wp::int32 var_635 = 1;
        wp::vec_t<3, wp::float64> var_636;
        wp::vec_t<4, wp::float64> var_637;
        wp::float64 var_638;
        wp::vec_t<3, wp::float64> var_639;
        wp::vec_t<4, wp::float64> var_640;
        wp::float64 var_641;
        bool var_642;
        bool var_643;
        wp::float64 var_644;
        bool var_645;
        wp::float64 var_646;
        bool var_647;
        bool var_648;
        wp::float64 var_649;
        bool var_650;
        wp::float64 var_651;
        bool var_652;
        wp::vec_t<3, wp::float64> var_653;
        wp::float64 var_654;
        wp::float64 var_655;
        wp::vec_t<3, wp::float64> var_656;
        wp::vec_t<3, wp::float64> var_657;
        wp::vec_t<3, wp::float64> var_658;
        wp::vec_t<3, wp::float64> var_659;
        wp::vec_t<3, wp::float64> var_660;
        bool var_661;
        bool var_662;
        bool var_663;
        const wp::int32 var_664 = 1;
        wp::int32 var_665;
        wp::int32 var_666;
        wp::int32 var_667;
        wp::vec_t<3, wp::float64> var_668;
        const wp::int32 var_669 = 2;
        wp::vec_t<3, wp::float64> var_670;
        wp::vec_t<4, wp::float64> var_671;
        wp::float64 var_672;
        wp::vec_t<3, wp::float64> var_673;
        wp::vec_t<4, wp::float64> var_674;
        wp::float64 var_675;
        bool var_676;
        bool var_677;
        wp::float64 var_678;
        bool var_679;
        wp::float64 var_680;
        bool var_681;
        bool var_682;
        wp::float64 var_683;
        bool var_684;
        wp::float64 var_685;
        bool var_686;
        wp::vec_t<3, wp::float64> var_687;
        wp::float64 var_688;
        wp::float64 var_689;
        wp::vec_t<3, wp::float64> var_690;
        wp::vec_t<3, wp::float64> var_691;
        wp::vec_t<3, wp::float64> var_692;
        wp::vec_t<3, wp::float64> var_693;
        wp::vec_t<3, wp::float64> var_694;
        bool var_695;
        bool var_696;
        bool var_697;
        const wp::int32 var_698 = 1;
        wp::int32 var_699;
        wp::int32 var_700;
        wp::int32 var_701;
        wp::vec_t<3, wp::float64> var_702;
        const wp::int32 var_703 = 3;
        wp::vec_t<3, wp::float64> var_704;
        wp::vec_t<4, wp::float64> var_705;
        wp::float64 var_706;
        wp::vec_t<3, wp::float64> var_707;
        wp::vec_t<4, wp::float64> var_708;
        wp::float64 var_709;
        bool var_710;
        bool var_711;
        wp::float64 var_712;
        bool var_713;
        wp::float64 var_714;
        bool var_715;
        bool var_716;
        wp::float64 var_717;
        bool var_718;
        wp::float64 var_719;
        bool var_720;
        wp::vec_t<3, wp::float64> var_721;
        wp::float64 var_722;
        wp::float64 var_723;
        wp::vec_t<3, wp::float64> var_724;
        wp::vec_t<3, wp::float64> var_725;
        wp::vec_t<3, wp::float64> var_726;
        wp::vec_t<3, wp::float64> var_727;
        wp::vec_t<3, wp::float64> var_728;
        bool var_729;
        bool var_730;
        bool var_731;
        const wp::int32 var_732 = 1;
        wp::int32 var_733;
        wp::int32 var_734;
        wp::int32 var_735;
        wp::vec_t<3, wp::float64> var_736;
        const wp::int32 var_737 = 1;
        const wp::int32 var_738 = 0;
        wp::vec_t<3, wp::float64> var_739;
        wp::vec_t<4, wp::float64> var_740;
        wp::float64 var_741;
        wp::vec_t<3, wp::float64> var_742;
        wp::vec_t<4, wp::float64> var_743;
        wp::float64 var_744;
        bool var_745;
        bool var_746;
        wp::float64 var_747;
        bool var_748;
        wp::float64 var_749;
        bool var_750;
        bool var_751;
        wp::float64 var_752;
        bool var_753;
        wp::float64 var_754;
        bool var_755;
        wp::vec_t<3, wp::float64> var_756;
        wp::float64 var_757;
        wp::float64 var_758;
        wp::vec_t<3, wp::float64> var_759;
        wp::vec_t<3, wp::float64> var_760;
        wp::vec_t<3, wp::float64> var_761;
        wp::vec_t<3, wp::float64> var_762;
        wp::vec_t<3, wp::float64> var_763;
        bool var_764;
        bool var_765;
        bool var_766;
        const wp::int32 var_767 = 1;
        wp::int32 var_768;
        wp::int32 var_769;
        wp::int32 var_770;
        wp::vec_t<3, wp::float64> var_771;
        const wp::int32 var_772 = 1;
        wp::vec_t<3, wp::float64> var_773;
        wp::vec_t<4, wp::float64> var_774;
        wp::float64 var_775;
        wp::vec_t<3, wp::float64> var_776;
        wp::vec_t<4, wp::float64> var_777;
        wp::float64 var_778;
        bool var_779;
        bool var_780;
        wp::float64 var_781;
        bool var_782;
        wp::float64 var_783;
        bool var_784;
        bool var_785;
        wp::float64 var_786;
        bool var_787;
        wp::float64 var_788;
        bool var_789;
        wp::vec_t<3, wp::float64> var_790;
        wp::float64 var_791;
        wp::float64 var_792;
        wp::vec_t<3, wp::float64> var_793;
        wp::vec_t<3, wp::float64> var_794;
        wp::vec_t<3, wp::float64> var_795;
        wp::vec_t<3, wp::float64> var_796;
        wp::vec_t<3, wp::float64> var_797;
        bool var_798;
        bool var_799;
        bool var_800;
        const wp::int32 var_801 = 1;
        wp::int32 var_802;
        wp::int32 var_803;
        wp::int32 var_804;
        wp::vec_t<3, wp::float64> var_805;
        const wp::int32 var_806 = 2;
        wp::vec_t<3, wp::float64> var_807;
        wp::vec_t<4, wp::float64> var_808;
        wp::float64 var_809;
        wp::vec_t<3, wp::float64> var_810;
        wp::vec_t<4, wp::float64> var_811;
        wp::float64 var_812;
        bool var_813;
        bool var_814;
        wp::float64 var_815;
        bool var_816;
        wp::float64 var_817;
        bool var_818;
        bool var_819;
        wp::float64 var_820;
        bool var_821;
        wp::float64 var_822;
        bool var_823;
        wp::vec_t<3, wp::float64> var_824;
        wp::float64 var_825;
        wp::float64 var_826;
        wp::vec_t<3, wp::float64> var_827;
        wp::vec_t<3, wp::float64> var_828;
        wp::vec_t<3, wp::float64> var_829;
        wp::vec_t<3, wp::float64> var_830;
        wp::vec_t<3, wp::float64> var_831;
        bool var_832;
        bool var_833;
        bool var_834;
        const wp::int32 var_835 = 1;
        wp::int32 var_836;
        wp::int32 var_837;
        wp::int32 var_838;
        wp::vec_t<3, wp::float64> var_839;
        const wp::int32 var_840 = 3;
        wp::vec_t<3, wp::float64> var_841;
        wp::vec_t<4, wp::float64> var_842;
        wp::float64 var_843;
        wp::vec_t<3, wp::float64> var_844;
        wp::vec_t<4, wp::float64> var_845;
        wp::float64 var_846;
        bool var_847;
        bool var_848;
        wp::float64 var_849;
        bool var_850;
        wp::float64 var_851;
        bool var_852;
        bool var_853;
        wp::float64 var_854;
        bool var_855;
        wp::float64 var_856;
        bool var_857;
        wp::vec_t<3, wp::float64> var_858;
        wp::float64 var_859;
        wp::float64 var_860;
        wp::vec_t<3, wp::float64> var_861;
        wp::vec_t<3, wp::float64> var_862;
        wp::vec_t<3, wp::float64> var_863;
        wp::vec_t<3, wp::float64> var_864;
        wp::vec_t<3, wp::float64> var_865;
        bool var_866;
        bool var_867;
        bool var_868;
        const wp::int32 var_869 = 1;
        wp::int32 var_870;
        wp::int32 var_871;
        wp::int32 var_872;
        wp::vec_t<3, wp::float64> var_873;
        const wp::int32 var_874 = 3;
        const wp::int32 var_875 = 0;
        const wp::int32 var_876 = 0;
        wp::vec_t<3, wp::float64> var_877;
        wp::vec_t<4, wp::float64> var_878;
        wp::float64 var_879;
        wp::vec_t<3, wp::float64> var_880;
        wp::vec_t<4, wp::float64> var_881;
        wp::float64 var_882;
        bool var_883;
        bool var_884;
        wp::float64 var_885;
        bool var_886;
        wp::float64 var_887;
        bool var_888;
        bool var_889;
        wp::float64 var_890;
        bool var_891;
        wp::float64 var_892;
        bool var_893;
        wp::vec_t<3, wp::float64> var_894;
        wp::float64 var_895;
        wp::float64 var_896;
        wp::vec_t<3, wp::float64> var_897;
        wp::vec_t<3, wp::float64> var_898;
        wp::vec_t<3, wp::float64> var_899;
        wp::vec_t<3, wp::float64> var_900;
        wp::vec_t<3, wp::float64> var_901;
        bool var_902;
        bool var_903;
        bool var_904;
        const wp::int32 var_905 = 1;
        wp::int32 var_906;
        wp::int32 var_907;
        wp::int32 var_908;
        wp::vec_t<3, wp::float64> var_909;
        const wp::int32 var_910 = 1;
        wp::vec_t<3, wp::float64> var_911;
        wp::vec_t<4, wp::float64> var_912;
        wp::float64 var_913;
        wp::vec_t<3, wp::float64> var_914;
        wp::vec_t<4, wp::float64> var_915;
        wp::float64 var_916;
        bool var_917;
        bool var_918;
        wp::float64 var_919;
        bool var_920;
        wp::float64 var_921;
        bool var_922;
        bool var_923;
        wp::float64 var_924;
        bool var_925;
        wp::float64 var_926;
        bool var_927;
        wp::vec_t<3, wp::float64> var_928;
        wp::float64 var_929;
        wp::float64 var_930;
        wp::vec_t<3, wp::float64> var_931;
        wp::vec_t<3, wp::float64> var_932;
        wp::vec_t<3, wp::float64> var_933;
        wp::vec_t<3, wp::float64> var_934;
        wp::vec_t<3, wp::float64> var_935;
        bool var_936;
        bool var_937;
        bool var_938;
        const wp::int32 var_939 = 1;
        wp::int32 var_940;
        wp::int32 var_941;
        wp::int32 var_942;
        wp::vec_t<3, wp::float64> var_943;
        const wp::int32 var_944 = 2;
        wp::vec_t<3, wp::float64> var_945;
        wp::vec_t<4, wp::float64> var_946;
        wp::float64 var_947;
        wp::vec_t<3, wp::float64> var_948;
        wp::vec_t<4, wp::float64> var_949;
        wp::float64 var_950;
        bool var_951;
        bool var_952;
        wp::float64 var_953;
        bool var_954;
        wp::float64 var_955;
        bool var_956;
        bool var_957;
        wp::float64 var_958;
        bool var_959;
        wp::float64 var_960;
        bool var_961;
        wp::vec_t<3, wp::float64> var_962;
        wp::float64 var_963;
        wp::float64 var_964;
        wp::vec_t<3, wp::float64> var_965;
        wp::vec_t<3, wp::float64> var_966;
        wp::vec_t<3, wp::float64> var_967;
        wp::vec_t<3, wp::float64> var_968;
        wp::vec_t<3, wp::float64> var_969;
        bool var_970;
        bool var_971;
        bool var_972;
        const wp::int32 var_973 = 1;
        wp::int32 var_974;
        wp::int32 var_975;
        wp::int32 var_976;
        wp::vec_t<3, wp::float64> var_977;
        const wp::int32 var_978 = 3;
        wp::vec_t<3, wp::float64> var_979;
        wp::vec_t<4, wp::float64> var_980;
        wp::float64 var_981;
        wp::vec_t<3, wp::float64> var_982;
        wp::vec_t<4, wp::float64> var_983;
        wp::float64 var_984;
        bool var_985;
        bool var_986;
        wp::float64 var_987;
        bool var_988;
        wp::float64 var_989;
        bool var_990;
        bool var_991;
        wp::float64 var_992;
        bool var_993;
        wp::float64 var_994;
        bool var_995;
        wp::vec_t<3, wp::float64> var_996;
        wp::float64 var_997;
        wp::float64 var_998;
        wp::vec_t<3, wp::float64> var_999;
        wp::vec_t<3, wp::float64> var_1000;
        wp::vec_t<3, wp::float64> var_1001;
        wp::vec_t<3, wp::float64> var_1002;
        wp::vec_t<3, wp::float64> var_1003;
        bool var_1004;
        bool var_1005;
        bool var_1006;
        const wp::int32 var_1007 = 1;
        wp::int32 var_1008;
        wp::int32 var_1009;
        wp::int32 var_1010;
        wp::vec_t<3, wp::float64> var_1011;
        const wp::int32 var_1012 = 1;
        const wp::int32 var_1013 = 0;
        wp::vec_t<3, wp::float64> var_1014;
        wp::vec_t<4, wp::float64> var_1015;
        wp::float64 var_1016;
        wp::vec_t<3, wp::float64> var_1017;
        wp::vec_t<4, wp::float64> var_1018;
        wp::float64 var_1019;
        bool var_1020;
        bool var_1021;
        wp::float64 var_1022;
        bool var_1023;
        wp::float64 var_1024;
        bool var_1025;
        bool var_1026;
        wp::float64 var_1027;
        bool var_1028;
        wp::float64 var_1029;
        bool var_1030;
        wp::vec_t<3, wp::float64> var_1031;
        wp::float64 var_1032;
        wp::float64 var_1033;
        wp::vec_t<3, wp::float64> var_1034;
        wp::vec_t<3, wp::float64> var_1035;
        wp::vec_t<3, wp::float64> var_1036;
        wp::vec_t<3, wp::float64> var_1037;
        wp::vec_t<3, wp::float64> var_1038;
        bool var_1039;
        bool var_1040;
        bool var_1041;
        const wp::int32 var_1042 = 1;
        wp::int32 var_1043;
        wp::int32 var_1044;
        wp::int32 var_1045;
        wp::vec_t<3, wp::float64> var_1046;
        const wp::int32 var_1047 = 1;
        wp::vec_t<3, wp::float64> var_1048;
        wp::vec_t<4, wp::float64> var_1049;
        wp::float64 var_1050;
        wp::vec_t<3, wp::float64> var_1051;
        wp::vec_t<4, wp::float64> var_1052;
        wp::float64 var_1053;
        bool var_1054;
        bool var_1055;
        wp::float64 var_1056;
        bool var_1057;
        wp::float64 var_1058;
        bool var_1059;
        bool var_1060;
        wp::float64 var_1061;
        bool var_1062;
        wp::float64 var_1063;
        bool var_1064;
        wp::vec_t<3, wp::float64> var_1065;
        wp::float64 var_1066;
        wp::float64 var_1067;
        wp::vec_t<3, wp::float64> var_1068;
        wp::vec_t<3, wp::float64> var_1069;
        wp::vec_t<3, wp::float64> var_1070;
        wp::vec_t<3, wp::float64> var_1071;
        wp::vec_t<3, wp::float64> var_1072;
        bool var_1073;
        bool var_1074;
        bool var_1075;
        const wp::int32 var_1076 = 1;
        wp::int32 var_1077;
        wp::int32 var_1078;
        wp::int32 var_1079;
        wp::vec_t<3, wp::float64> var_1080;
        const wp::int32 var_1081 = 2;
        wp::vec_t<3, wp::float64> var_1082;
        wp::vec_t<4, wp::float64> var_1083;
        wp::float64 var_1084;
        wp::vec_t<3, wp::float64> var_1085;
        wp::vec_t<4, wp::float64> var_1086;
        wp::float64 var_1087;
        bool var_1088;
        bool var_1089;
        wp::float64 var_1090;
        bool var_1091;
        wp::float64 var_1092;
        bool var_1093;
        bool var_1094;
        wp::float64 var_1095;
        bool var_1096;
        wp::float64 var_1097;
        bool var_1098;
        wp::vec_t<3, wp::float64> var_1099;
        wp::float64 var_1100;
        wp::float64 var_1101;
        wp::vec_t<3, wp::float64> var_1102;
        wp::vec_t<3, wp::float64> var_1103;
        wp::vec_t<3, wp::float64> var_1104;
        wp::vec_t<3, wp::float64> var_1105;
        wp::vec_t<3, wp::float64> var_1106;
        bool var_1107;
        bool var_1108;
        bool var_1109;
        const wp::int32 var_1110 = 1;
        wp::int32 var_1111;
        wp::int32 var_1112;
        wp::int32 var_1113;
        wp::vec_t<3, wp::float64> var_1114;
        const wp::int32 var_1115 = 3;
        wp::vec_t<3, wp::float64> var_1116;
        wp::vec_t<4, wp::float64> var_1117;
        wp::float64 var_1118;
        wp::vec_t<3, wp::float64> var_1119;
        wp::vec_t<4, wp::float64> var_1120;
        wp::float64 var_1121;
        bool var_1122;
        bool var_1123;
        wp::float64 var_1124;
        bool var_1125;
        wp::float64 var_1126;
        bool var_1127;
        bool var_1128;
        wp::float64 var_1129;
        bool var_1130;
        wp::float64 var_1131;
        bool var_1132;
        wp::vec_t<3, wp::float64> var_1133;
        wp::float64 var_1134;
        wp::float64 var_1135;
        wp::vec_t<3, wp::float64> var_1136;
        wp::vec_t<3, wp::float64> var_1137;
        wp::vec_t<3, wp::float64> var_1138;
        wp::vec_t<3, wp::float64> var_1139;
        wp::vec_t<3, wp::float64> var_1140;
        bool var_1141;
        bool var_1142;
        bool var_1143;
        const wp::int32 var_1144 = 1;
        wp::int32 var_1145;
        wp::int32 var_1146;
        wp::int32 var_1147;
        wp::vec_t<3, wp::float64> var_1148;
        const wp::int32 var_1149 = 2;
        const wp::int32 var_1150 = 0;
        wp::vec_t<3, wp::float64> var_1151;
        wp::vec_t<4, wp::float64> var_1152;
        wp::float64 var_1153;
        wp::vec_t<3, wp::float64> var_1154;
        wp::vec_t<4, wp::float64> var_1155;
        wp::float64 var_1156;
        bool var_1157;
        bool var_1158;
        wp::float64 var_1159;
        bool var_1160;
        wp::float64 var_1161;
        bool var_1162;
        bool var_1163;
        wp::float64 var_1164;
        bool var_1165;
        wp::float64 var_1166;
        bool var_1167;
        wp::vec_t<3, wp::float64> var_1168;
        wp::float64 var_1169;
        wp::float64 var_1170;
        wp::vec_t<3, wp::float64> var_1171;
        wp::vec_t<3, wp::float64> var_1172;
        wp::vec_t<3, wp::float64> var_1173;
        wp::vec_t<3, wp::float64> var_1174;
        wp::vec_t<3, wp::float64> var_1175;
        bool var_1176;
        bool var_1177;
        bool var_1178;
        const wp::int32 var_1179 = 1;
        wp::int32 var_1180;
        wp::int32 var_1181;
        wp::int32 var_1182;
        wp::vec_t<3, wp::float64> var_1183;
        const wp::int32 var_1184 = 1;
        wp::vec_t<3, wp::float64> var_1185;
        wp::vec_t<4, wp::float64> var_1186;
        wp::float64 var_1187;
        wp::vec_t<3, wp::float64> var_1188;
        wp::vec_t<4, wp::float64> var_1189;
        wp::float64 var_1190;
        bool var_1191;
        bool var_1192;
        wp::float64 var_1193;
        bool var_1194;
        wp::float64 var_1195;
        bool var_1196;
        bool var_1197;
        wp::float64 var_1198;
        bool var_1199;
        wp::float64 var_1200;
        bool var_1201;
        wp::vec_t<3, wp::float64> var_1202;
        wp::float64 var_1203;
        wp::float64 var_1204;
        wp::vec_t<3, wp::float64> var_1205;
        wp::vec_t<3, wp::float64> var_1206;
        wp::vec_t<3, wp::float64> var_1207;
        wp::vec_t<3, wp::float64> var_1208;
        wp::vec_t<3, wp::float64> var_1209;
        bool var_1210;
        bool var_1211;
        bool var_1212;
        const wp::int32 var_1213 = 1;
        wp::int32 var_1214;
        wp::int32 var_1215;
        wp::int32 var_1216;
        wp::vec_t<3, wp::float64> var_1217;
        const wp::int32 var_1218 = 2;
        wp::vec_t<3, wp::float64> var_1219;
        wp::vec_t<4, wp::float64> var_1220;
        wp::float64 var_1221;
        wp::vec_t<3, wp::float64> var_1222;
        wp::vec_t<4, wp::float64> var_1223;
        wp::float64 var_1224;
        bool var_1225;
        bool var_1226;
        wp::float64 var_1227;
        bool var_1228;
        wp::float64 var_1229;
        bool var_1230;
        bool var_1231;
        wp::float64 var_1232;
        bool var_1233;
        wp::float64 var_1234;
        bool var_1235;
        wp::vec_t<3, wp::float64> var_1236;
        wp::float64 var_1237;
        wp::float64 var_1238;
        wp::vec_t<3, wp::float64> var_1239;
        wp::vec_t<3, wp::float64> var_1240;
        wp::vec_t<3, wp::float64> var_1241;
        wp::vec_t<3, wp::float64> var_1242;
        wp::vec_t<3, wp::float64> var_1243;
        bool var_1244;
        bool var_1245;
        bool var_1246;
        const wp::int32 var_1247 = 1;
        wp::int32 var_1248;
        wp::int32 var_1249;
        wp::int32 var_1250;
        wp::vec_t<3, wp::float64> var_1251;
        const wp::int32 var_1252 = 3;
        wp::vec_t<3, wp::float64> var_1253;
        wp::vec_t<4, wp::float64> var_1254;
        wp::float64 var_1255;
        wp::vec_t<3, wp::float64> var_1256;
        wp::vec_t<4, wp::float64> var_1257;
        wp::float64 var_1258;
        bool var_1259;
        bool var_1260;
        wp::float64 var_1261;
        bool var_1262;
        wp::float64 var_1263;
        bool var_1264;
        bool var_1265;
        wp::float64 var_1266;
        bool var_1267;
        wp::float64 var_1268;
        bool var_1269;
        wp::vec_t<3, wp::float64> var_1270;
        wp::float64 var_1271;
        wp::float64 var_1272;
        wp::vec_t<3, wp::float64> var_1273;
        wp::vec_t<3, wp::float64> var_1274;
        wp::vec_t<3, wp::float64> var_1275;
        wp::vec_t<3, wp::float64> var_1276;
        wp::vec_t<3, wp::float64> var_1277;
        bool var_1278;
        bool var_1279;
        bool var_1280;
        const wp::int32 var_1281 = 1;
        wp::int32 var_1282;
        wp::int32 var_1283;
        wp::int32 var_1284;
        wp::vec_t<3, wp::float64> var_1285;
        const wp::int32 var_1286 = 1;
        wp::mat_t<4, 3, wp::float64> var_1287;
        wp::mat_t<4, 4, wp::float64> var_1288;
        wp::mat_t<4, 4, wp::float64> var_1289;
        const wp::int32 var_1290 = 1;
        bool var_1291;
        wp::mat_t<4, 3, wp::float64> var_1292;
        wp::mat_t<4, 4, wp::float64> var_1293;
        wp::mat_t<4, 4, wp::float64> var_1294;
        wp::mat_t<4, 3, wp::float64> var_1295;
        wp::mat_t<4, 4, wp::float64> var_1296;
        wp::mat_t<4, 4, wp::float64> var_1297;
        const wp::int32 var_1298 = 0;
        const wp::int32 var_1299 = 1;
        const wp::int32 var_1300 = 0;
        const wp::int32 var_1301 = 0;
        wp::vec_t<3, wp::float64> var_1302;
        wp::vec_t<4, wp::float64> var_1303;
        wp::float64 var_1304;
        wp::vec_t<3, wp::float64> var_1305;
        wp::vec_t<4, wp::float64> var_1306;
        wp::float64 var_1307;
        bool var_1308;
        bool var_1309;
        wp::float64 var_1310;
        bool var_1311;
        wp::float64 var_1312;
        bool var_1313;
        bool var_1314;
        wp::float64 var_1315;
        bool var_1316;
        wp::float64 var_1317;
        bool var_1318;
        wp::vec_t<3, wp::float64> var_1319;
        wp::float64 var_1320;
        wp::float64 var_1321;
        wp::vec_t<3, wp::float64> var_1322;
        wp::vec_t<3, wp::float64> var_1323;
        wp::vec_t<3, wp::float64> var_1324;
        wp::vec_t<3, wp::float64> var_1325;
        wp::vec_t<3, wp::float64> var_1326;
        bool var_1327;
        bool var_1328;
        bool var_1329;
        const wp::int32 var_1330 = 1;
        wp::int32 var_1331;
        wp::int32 var_1332;
        wp::int32 var_1333;
        wp::vec_t<3, wp::float64> var_1334;
        const wp::int32 var_1335 = 1;
        wp::vec_t<3, wp::float64> var_1336;
        wp::vec_t<4, wp::float64> var_1337;
        wp::float64 var_1338;
        wp::vec_t<3, wp::float64> var_1339;
        wp::vec_t<4, wp::float64> var_1340;
        wp::float64 var_1341;
        bool var_1342;
        bool var_1343;
        wp::float64 var_1344;
        bool var_1345;
        wp::float64 var_1346;
        bool var_1347;
        bool var_1348;
        wp::float64 var_1349;
        bool var_1350;
        wp::float64 var_1351;
        bool var_1352;
        wp::vec_t<3, wp::float64> var_1353;
        wp::float64 var_1354;
        wp::float64 var_1355;
        wp::vec_t<3, wp::float64> var_1356;
        wp::vec_t<3, wp::float64> var_1357;
        wp::vec_t<3, wp::float64> var_1358;
        wp::vec_t<3, wp::float64> var_1359;
        wp::vec_t<3, wp::float64> var_1360;
        bool var_1361;
        bool var_1362;
        bool var_1363;
        const wp::int32 var_1364 = 1;
        wp::int32 var_1365;
        wp::int32 var_1366;
        wp::int32 var_1367;
        wp::vec_t<3, wp::float64> var_1368;
        const wp::int32 var_1369 = 2;
        wp::vec_t<3, wp::float64> var_1370;
        wp::vec_t<4, wp::float64> var_1371;
        wp::float64 var_1372;
        wp::vec_t<3, wp::float64> var_1373;
        wp::vec_t<4, wp::float64> var_1374;
        wp::float64 var_1375;
        bool var_1376;
        bool var_1377;
        wp::float64 var_1378;
        bool var_1379;
        wp::float64 var_1380;
        bool var_1381;
        bool var_1382;
        wp::float64 var_1383;
        bool var_1384;
        wp::float64 var_1385;
        bool var_1386;
        wp::vec_t<3, wp::float64> var_1387;
        wp::float64 var_1388;
        wp::float64 var_1389;
        wp::vec_t<3, wp::float64> var_1390;
        wp::vec_t<3, wp::float64> var_1391;
        wp::vec_t<3, wp::float64> var_1392;
        wp::vec_t<3, wp::float64> var_1393;
        wp::vec_t<3, wp::float64> var_1394;
        bool var_1395;
        bool var_1396;
        bool var_1397;
        const wp::int32 var_1398 = 1;
        wp::int32 var_1399;
        wp::int32 var_1400;
        wp::int32 var_1401;
        wp::vec_t<3, wp::float64> var_1402;
        const wp::int32 var_1403 = 3;
        wp::vec_t<3, wp::float64> var_1404;
        wp::vec_t<4, wp::float64> var_1405;
        wp::float64 var_1406;
        wp::vec_t<3, wp::float64> var_1407;
        wp::vec_t<4, wp::float64> var_1408;
        wp::float64 var_1409;
        bool var_1410;
        bool var_1411;
        wp::float64 var_1412;
        bool var_1413;
        wp::float64 var_1414;
        bool var_1415;
        bool var_1416;
        wp::float64 var_1417;
        bool var_1418;
        wp::float64 var_1419;
        bool var_1420;
        wp::vec_t<3, wp::float64> var_1421;
        wp::float64 var_1422;
        wp::float64 var_1423;
        wp::vec_t<3, wp::float64> var_1424;
        wp::vec_t<3, wp::float64> var_1425;
        wp::vec_t<3, wp::float64> var_1426;
        wp::vec_t<3, wp::float64> var_1427;
        wp::vec_t<3, wp::float64> var_1428;
        bool var_1429;
        bool var_1430;
        bool var_1431;
        const wp::int32 var_1432 = 1;
        wp::int32 var_1433;
        wp::int32 var_1434;
        wp::int32 var_1435;
        wp::vec_t<3, wp::float64> var_1436;
        const wp::int32 var_1437 = 2;
        const wp::int32 var_1438 = 0;
        const wp::int32 var_1439 = 0;
        wp::vec_t<3, wp::float64> var_1440;
        wp::vec_t<4, wp::float64> var_1441;
        wp::float64 var_1442;
        wp::vec_t<3, wp::float64> var_1443;
        wp::vec_t<4, wp::float64> var_1444;
        wp::float64 var_1445;
        bool var_1446;
        bool var_1447;
        wp::float64 var_1448;
        bool var_1449;
        wp::float64 var_1450;
        bool var_1451;
        bool var_1452;
        wp::float64 var_1453;
        bool var_1454;
        wp::float64 var_1455;
        bool var_1456;
        wp::vec_t<3, wp::float64> var_1457;
        wp::float64 var_1458;
        wp::float64 var_1459;
        wp::vec_t<3, wp::float64> var_1460;
        wp::vec_t<3, wp::float64> var_1461;
        wp::vec_t<3, wp::float64> var_1462;
        wp::vec_t<3, wp::float64> var_1463;
        wp::vec_t<3, wp::float64> var_1464;
        bool var_1465;
        bool var_1466;
        bool var_1467;
        const wp::int32 var_1468 = 1;
        wp::int32 var_1469;
        wp::int32 var_1470;
        wp::int32 var_1471;
        wp::vec_t<3, wp::float64> var_1472;
        const wp::int32 var_1473 = 1;
        wp::vec_t<3, wp::float64> var_1474;
        wp::vec_t<4, wp::float64> var_1475;
        wp::float64 var_1476;
        wp::vec_t<3, wp::float64> var_1477;
        wp::vec_t<4, wp::float64> var_1478;
        wp::float64 var_1479;
        bool var_1480;
        bool var_1481;
        wp::float64 var_1482;
        bool var_1483;
        wp::float64 var_1484;
        bool var_1485;
        bool var_1486;
        wp::float64 var_1487;
        bool var_1488;
        wp::float64 var_1489;
        bool var_1490;
        wp::vec_t<3, wp::float64> var_1491;
        wp::float64 var_1492;
        wp::float64 var_1493;
        wp::vec_t<3, wp::float64> var_1494;
        wp::vec_t<3, wp::float64> var_1495;
        wp::vec_t<3, wp::float64> var_1496;
        wp::vec_t<3, wp::float64> var_1497;
        wp::vec_t<3, wp::float64> var_1498;
        bool var_1499;
        bool var_1500;
        bool var_1501;
        const wp::int32 var_1502 = 1;
        wp::int32 var_1503;
        wp::int32 var_1504;
        wp::int32 var_1505;
        wp::vec_t<3, wp::float64> var_1506;
        const wp::int32 var_1507 = 2;
        wp::vec_t<3, wp::float64> var_1508;
        wp::vec_t<4, wp::float64> var_1509;
        wp::float64 var_1510;
        wp::vec_t<3, wp::float64> var_1511;
        wp::vec_t<4, wp::float64> var_1512;
        wp::float64 var_1513;
        bool var_1514;
        bool var_1515;
        wp::float64 var_1516;
        bool var_1517;
        wp::float64 var_1518;
        bool var_1519;
        bool var_1520;
        wp::float64 var_1521;
        bool var_1522;
        wp::float64 var_1523;
        bool var_1524;
        wp::vec_t<3, wp::float64> var_1525;
        wp::float64 var_1526;
        wp::float64 var_1527;
        wp::vec_t<3, wp::float64> var_1528;
        wp::vec_t<3, wp::float64> var_1529;
        wp::vec_t<3, wp::float64> var_1530;
        wp::vec_t<3, wp::float64> var_1531;
        wp::vec_t<3, wp::float64> var_1532;
        bool var_1533;
        bool var_1534;
        bool var_1535;
        const wp::int32 var_1536 = 1;
        wp::int32 var_1537;
        wp::int32 var_1538;
        wp::int32 var_1539;
        wp::vec_t<3, wp::float64> var_1540;
        const wp::int32 var_1541 = 3;
        wp::vec_t<3, wp::float64> var_1542;
        wp::vec_t<4, wp::float64> var_1543;
        wp::float64 var_1544;
        wp::vec_t<3, wp::float64> var_1545;
        wp::vec_t<4, wp::float64> var_1546;
        wp::float64 var_1547;
        bool var_1548;
        bool var_1549;
        wp::float64 var_1550;
        bool var_1551;
        wp::float64 var_1552;
        bool var_1553;
        bool var_1554;
        wp::float64 var_1555;
        bool var_1556;
        wp::float64 var_1557;
        bool var_1558;
        wp::vec_t<3, wp::float64> var_1559;
        wp::float64 var_1560;
        wp::float64 var_1561;
        wp::vec_t<3, wp::float64> var_1562;
        wp::vec_t<3, wp::float64> var_1563;
        wp::vec_t<3, wp::float64> var_1564;
        wp::vec_t<3, wp::float64> var_1565;
        wp::vec_t<3, wp::float64> var_1566;
        bool var_1567;
        bool var_1568;
        bool var_1569;
        const wp::int32 var_1570 = 1;
        wp::int32 var_1571;
        wp::int32 var_1572;
        wp::int32 var_1573;
        wp::vec_t<3, wp::float64> var_1574;
        const wp::int32 var_1575 = 1;
        const wp::int32 var_1576 = 0;
        wp::vec_t<3, wp::float64> var_1577;
        wp::vec_t<4, wp::float64> var_1578;
        wp::float64 var_1579;
        wp::vec_t<3, wp::float64> var_1580;
        wp::vec_t<4, wp::float64> var_1581;
        wp::float64 var_1582;
        bool var_1583;
        bool var_1584;
        wp::float64 var_1585;
        bool var_1586;
        wp::float64 var_1587;
        bool var_1588;
        bool var_1589;
        wp::float64 var_1590;
        bool var_1591;
        wp::float64 var_1592;
        bool var_1593;
        wp::vec_t<3, wp::float64> var_1594;
        wp::float64 var_1595;
        wp::float64 var_1596;
        wp::vec_t<3, wp::float64> var_1597;
        wp::vec_t<3, wp::float64> var_1598;
        wp::vec_t<3, wp::float64> var_1599;
        wp::vec_t<3, wp::float64> var_1600;
        wp::vec_t<3, wp::float64> var_1601;
        bool var_1602;
        bool var_1603;
        bool var_1604;
        const wp::int32 var_1605 = 1;
        wp::int32 var_1606;
        wp::int32 var_1607;
        wp::int32 var_1608;
        wp::vec_t<3, wp::float64> var_1609;
        const wp::int32 var_1610 = 1;
        wp::vec_t<3, wp::float64> var_1611;
        wp::vec_t<4, wp::float64> var_1612;
        wp::float64 var_1613;
        wp::vec_t<3, wp::float64> var_1614;
        wp::vec_t<4, wp::float64> var_1615;
        wp::float64 var_1616;
        bool var_1617;
        bool var_1618;
        wp::float64 var_1619;
        bool var_1620;
        wp::float64 var_1621;
        bool var_1622;
        bool var_1623;
        wp::float64 var_1624;
        bool var_1625;
        wp::float64 var_1626;
        bool var_1627;
        wp::vec_t<3, wp::float64> var_1628;
        wp::float64 var_1629;
        wp::float64 var_1630;
        wp::vec_t<3, wp::float64> var_1631;
        wp::vec_t<3, wp::float64> var_1632;
        wp::vec_t<3, wp::float64> var_1633;
        wp::vec_t<3, wp::float64> var_1634;
        wp::vec_t<3, wp::float64> var_1635;
        bool var_1636;
        bool var_1637;
        bool var_1638;
        const wp::int32 var_1639 = 1;
        wp::int32 var_1640;
        wp::int32 var_1641;
        wp::int32 var_1642;
        wp::vec_t<3, wp::float64> var_1643;
        const wp::int32 var_1644 = 2;
        wp::vec_t<3, wp::float64> var_1645;
        wp::vec_t<4, wp::float64> var_1646;
        wp::float64 var_1647;
        wp::vec_t<3, wp::float64> var_1648;
        wp::vec_t<4, wp::float64> var_1649;
        wp::float64 var_1650;
        bool var_1651;
        bool var_1652;
        wp::float64 var_1653;
        bool var_1654;
        wp::float64 var_1655;
        bool var_1656;
        bool var_1657;
        wp::float64 var_1658;
        bool var_1659;
        wp::float64 var_1660;
        bool var_1661;
        wp::vec_t<3, wp::float64> var_1662;
        wp::float64 var_1663;
        wp::float64 var_1664;
        wp::vec_t<3, wp::float64> var_1665;
        wp::vec_t<3, wp::float64> var_1666;
        wp::vec_t<3, wp::float64> var_1667;
        wp::vec_t<3, wp::float64> var_1668;
        wp::vec_t<3, wp::float64> var_1669;
        bool var_1670;
        bool var_1671;
        bool var_1672;
        const wp::int32 var_1673 = 1;
        wp::int32 var_1674;
        wp::int32 var_1675;
        wp::int32 var_1676;
        wp::vec_t<3, wp::float64> var_1677;
        const wp::int32 var_1678 = 3;
        wp::vec_t<3, wp::float64> var_1679;
        wp::vec_t<4, wp::float64> var_1680;
        wp::float64 var_1681;
        wp::vec_t<3, wp::float64> var_1682;
        wp::vec_t<4, wp::float64> var_1683;
        wp::float64 var_1684;
        bool var_1685;
        bool var_1686;
        wp::float64 var_1687;
        bool var_1688;
        wp::float64 var_1689;
        bool var_1690;
        bool var_1691;
        wp::float64 var_1692;
        bool var_1693;
        wp::float64 var_1694;
        bool var_1695;
        wp::vec_t<3, wp::float64> var_1696;
        wp::float64 var_1697;
        wp::float64 var_1698;
        wp::vec_t<3, wp::float64> var_1699;
        wp::vec_t<3, wp::float64> var_1700;
        wp::vec_t<3, wp::float64> var_1701;
        wp::vec_t<3, wp::float64> var_1702;
        wp::vec_t<3, wp::float64> var_1703;
        bool var_1704;
        bool var_1705;
        bool var_1706;
        const wp::int32 var_1707 = 1;
        wp::int32 var_1708;
        wp::int32 var_1709;
        wp::int32 var_1710;
        wp::vec_t<3, wp::float64> var_1711;
        const wp::int32 var_1712 = 3;
        const wp::int32 var_1713 = 0;
        const wp::int32 var_1714 = 0;
        wp::vec_t<3, wp::float64> var_1715;
        wp::vec_t<4, wp::float64> var_1716;
        wp::float64 var_1717;
        wp::vec_t<3, wp::float64> var_1718;
        wp::vec_t<4, wp::float64> var_1719;
        wp::float64 var_1720;
        bool var_1721;
        bool var_1722;
        wp::float64 var_1723;
        bool var_1724;
        wp::float64 var_1725;
        bool var_1726;
        bool var_1727;
        wp::float64 var_1728;
        bool var_1729;
        wp::float64 var_1730;
        bool var_1731;
        wp::vec_t<3, wp::float64> var_1732;
        wp::float64 var_1733;
        wp::float64 var_1734;
        wp::vec_t<3, wp::float64> var_1735;
        wp::vec_t<3, wp::float64> var_1736;
        wp::vec_t<3, wp::float64> var_1737;
        wp::vec_t<3, wp::float64> var_1738;
        wp::vec_t<3, wp::float64> var_1739;
        bool var_1740;
        bool var_1741;
        bool var_1742;
        const wp::int32 var_1743 = 1;
        wp::int32 var_1744;
        wp::int32 var_1745;
        wp::int32 var_1746;
        wp::vec_t<3, wp::float64> var_1747;
        const wp::int32 var_1748 = 1;
        wp::vec_t<3, wp::float64> var_1749;
        wp::vec_t<4, wp::float64> var_1750;
        wp::float64 var_1751;
        wp::vec_t<3, wp::float64> var_1752;
        wp::vec_t<4, wp::float64> var_1753;
        wp::float64 var_1754;
        bool var_1755;
        bool var_1756;
        wp::float64 var_1757;
        bool var_1758;
        wp::float64 var_1759;
        bool var_1760;
        bool var_1761;
        wp::float64 var_1762;
        bool var_1763;
        wp::float64 var_1764;
        bool var_1765;
        wp::vec_t<3, wp::float64> var_1766;
        wp::float64 var_1767;
        wp::float64 var_1768;
        wp::vec_t<3, wp::float64> var_1769;
        wp::vec_t<3, wp::float64> var_1770;
        wp::vec_t<3, wp::float64> var_1771;
        wp::vec_t<3, wp::float64> var_1772;
        wp::vec_t<3, wp::float64> var_1773;
        bool var_1774;
        bool var_1775;
        bool var_1776;
        const wp::int32 var_1777 = 1;
        wp::int32 var_1778;
        wp::int32 var_1779;
        wp::int32 var_1780;
        wp::vec_t<3, wp::float64> var_1781;
        const wp::int32 var_1782 = 2;
        wp::vec_t<3, wp::float64> var_1783;
        wp::vec_t<4, wp::float64> var_1784;
        wp::float64 var_1785;
        wp::vec_t<3, wp::float64> var_1786;
        wp::vec_t<4, wp::float64> var_1787;
        wp::float64 var_1788;
        bool var_1789;
        bool var_1790;
        wp::float64 var_1791;
        bool var_1792;
        wp::float64 var_1793;
        bool var_1794;
        bool var_1795;
        wp::float64 var_1796;
        bool var_1797;
        wp::float64 var_1798;
        bool var_1799;
        wp::vec_t<3, wp::float64> var_1800;
        wp::float64 var_1801;
        wp::float64 var_1802;
        wp::vec_t<3, wp::float64> var_1803;
        wp::vec_t<3, wp::float64> var_1804;
        wp::vec_t<3, wp::float64> var_1805;
        wp::vec_t<3, wp::float64> var_1806;
        wp::vec_t<3, wp::float64> var_1807;
        bool var_1808;
        bool var_1809;
        bool var_1810;
        const wp::int32 var_1811 = 1;
        wp::int32 var_1812;
        wp::int32 var_1813;
        wp::int32 var_1814;
        wp::vec_t<3, wp::float64> var_1815;
        const wp::int32 var_1816 = 3;
        wp::vec_t<3, wp::float64> var_1817;
        wp::vec_t<4, wp::float64> var_1818;
        wp::float64 var_1819;
        wp::vec_t<3, wp::float64> var_1820;
        wp::vec_t<4, wp::float64> var_1821;
        wp::float64 var_1822;
        bool var_1823;
        bool var_1824;
        wp::float64 var_1825;
        bool var_1826;
        wp::float64 var_1827;
        bool var_1828;
        bool var_1829;
        wp::float64 var_1830;
        bool var_1831;
        wp::float64 var_1832;
        bool var_1833;
        wp::vec_t<3, wp::float64> var_1834;
        wp::float64 var_1835;
        wp::float64 var_1836;
        wp::vec_t<3, wp::float64> var_1837;
        wp::vec_t<3, wp::float64> var_1838;
        wp::vec_t<3, wp::float64> var_1839;
        wp::vec_t<3, wp::float64> var_1840;
        wp::vec_t<3, wp::float64> var_1841;
        bool var_1842;
        bool var_1843;
        bool var_1844;
        const wp::int32 var_1845 = 1;
        wp::int32 var_1846;
        wp::int32 var_1847;
        wp::int32 var_1848;
        wp::vec_t<3, wp::float64> var_1849;
        const wp::int32 var_1850 = 1;
        const wp::int32 var_1851 = 0;
        wp::vec_t<3, wp::float64> var_1852;
        wp::vec_t<4, wp::float64> var_1853;
        wp::float64 var_1854;
        wp::vec_t<3, wp::float64> var_1855;
        wp::vec_t<4, wp::float64> var_1856;
        wp::float64 var_1857;
        bool var_1858;
        bool var_1859;
        wp::float64 var_1860;
        bool var_1861;
        wp::float64 var_1862;
        bool var_1863;
        bool var_1864;
        wp::float64 var_1865;
        bool var_1866;
        wp::float64 var_1867;
        bool var_1868;
        wp::vec_t<3, wp::float64> var_1869;
        wp::float64 var_1870;
        wp::float64 var_1871;
        wp::vec_t<3, wp::float64> var_1872;
        wp::vec_t<3, wp::float64> var_1873;
        wp::vec_t<3, wp::float64> var_1874;
        wp::vec_t<3, wp::float64> var_1875;
        wp::vec_t<3, wp::float64> var_1876;
        bool var_1877;
        bool var_1878;
        bool var_1879;
        const wp::int32 var_1880 = 1;
        wp::int32 var_1881;
        wp::int32 var_1882;
        wp::int32 var_1883;
        wp::vec_t<3, wp::float64> var_1884;
        const wp::int32 var_1885 = 1;
        wp::vec_t<3, wp::float64> var_1886;
        wp::vec_t<4, wp::float64> var_1887;
        wp::float64 var_1888;
        wp::vec_t<3, wp::float64> var_1889;
        wp::vec_t<4, wp::float64> var_1890;
        wp::float64 var_1891;
        bool var_1892;
        bool var_1893;
        wp::float64 var_1894;
        bool var_1895;
        wp::float64 var_1896;
        bool var_1897;
        bool var_1898;
        wp::float64 var_1899;
        bool var_1900;
        wp::float64 var_1901;
        bool var_1902;
        wp::vec_t<3, wp::float64> var_1903;
        wp::float64 var_1904;
        wp::float64 var_1905;
        wp::vec_t<3, wp::float64> var_1906;
        wp::vec_t<3, wp::float64> var_1907;
        wp::vec_t<3, wp::float64> var_1908;
        wp::vec_t<3, wp::float64> var_1909;
        wp::vec_t<3, wp::float64> var_1910;
        bool var_1911;
        bool var_1912;
        bool var_1913;
        const wp::int32 var_1914 = 1;
        wp::int32 var_1915;
        wp::int32 var_1916;
        wp::int32 var_1917;
        wp::vec_t<3, wp::float64> var_1918;
        const wp::int32 var_1919 = 2;
        wp::vec_t<3, wp::float64> var_1920;
        wp::vec_t<4, wp::float64> var_1921;
        wp::float64 var_1922;
        wp::vec_t<3, wp::float64> var_1923;
        wp::vec_t<4, wp::float64> var_1924;
        wp::float64 var_1925;
        bool var_1926;
        bool var_1927;
        wp::float64 var_1928;
        bool var_1929;
        wp::float64 var_1930;
        bool var_1931;
        bool var_1932;
        wp::float64 var_1933;
        bool var_1934;
        wp::float64 var_1935;
        bool var_1936;
        wp::vec_t<3, wp::float64> var_1937;
        wp::float64 var_1938;
        wp::float64 var_1939;
        wp::vec_t<3, wp::float64> var_1940;
        wp::vec_t<3, wp::float64> var_1941;
        wp::vec_t<3, wp::float64> var_1942;
        wp::vec_t<3, wp::float64> var_1943;
        wp::vec_t<3, wp::float64> var_1944;
        bool var_1945;
        bool var_1946;
        bool var_1947;
        const wp::int32 var_1948 = 1;
        wp::int32 var_1949;
        wp::int32 var_1950;
        wp::int32 var_1951;
        wp::vec_t<3, wp::float64> var_1952;
        const wp::int32 var_1953 = 3;
        wp::vec_t<3, wp::float64> var_1954;
        wp::vec_t<4, wp::float64> var_1955;
        wp::float64 var_1956;
        wp::vec_t<3, wp::float64> var_1957;
        wp::vec_t<4, wp::float64> var_1958;
        wp::float64 var_1959;
        bool var_1960;
        bool var_1961;
        wp::float64 var_1962;
        bool var_1963;
        wp::float64 var_1964;
        bool var_1965;
        bool var_1966;
        wp::float64 var_1967;
        bool var_1968;
        wp::float64 var_1969;
        bool var_1970;
        wp::vec_t<3, wp::float64> var_1971;
        wp::float64 var_1972;
        wp::float64 var_1973;
        wp::vec_t<3, wp::float64> var_1974;
        wp::vec_t<3, wp::float64> var_1975;
        wp::vec_t<3, wp::float64> var_1976;
        wp::vec_t<3, wp::float64> var_1977;
        wp::vec_t<3, wp::float64> var_1978;
        bool var_1979;
        bool var_1980;
        bool var_1981;
        const wp::int32 var_1982 = 1;
        wp::int32 var_1983;
        wp::int32 var_1984;
        wp::int32 var_1985;
        wp::vec_t<3, wp::float64> var_1986;
        const wp::int32 var_1987 = 2;
        const wp::int32 var_1988 = 0;
        wp::vec_t<3, wp::float64> var_1989;
        wp::vec_t<4, wp::float64> var_1990;
        wp::float64 var_1991;
        wp::vec_t<3, wp::float64> var_1992;
        wp::vec_t<4, wp::float64> var_1993;
        wp::float64 var_1994;
        bool var_1995;
        bool var_1996;
        wp::float64 var_1997;
        bool var_1998;
        wp::float64 var_1999;
        bool var_2000;
        bool var_2001;
        wp::float64 var_2002;
        bool var_2003;
        wp::float64 var_2004;
        bool var_2005;
        wp::vec_t<3, wp::float64> var_2006;
        wp::float64 var_2007;
        wp::float64 var_2008;
        wp::vec_t<3, wp::float64> var_2009;
        wp::vec_t<3, wp::float64> var_2010;
        wp::vec_t<3, wp::float64> var_2011;
        wp::vec_t<3, wp::float64> var_2012;
        wp::vec_t<3, wp::float64> var_2013;
        bool var_2014;
        bool var_2015;
        bool var_2016;
        const wp::int32 var_2017 = 1;
        wp::int32 var_2018;
        wp::int32 var_2019;
        wp::int32 var_2020;
        wp::vec_t<3, wp::float64> var_2021;
        const wp::int32 var_2022 = 1;
        wp::vec_t<3, wp::float64> var_2023;
        wp::vec_t<4, wp::float64> var_2024;
        wp::float64 var_2025;
        wp::vec_t<3, wp::float64> var_2026;
        wp::vec_t<4, wp::float64> var_2027;
        wp::float64 var_2028;
        bool var_2029;
        bool var_2030;
        wp::float64 var_2031;
        bool var_2032;
        wp::float64 var_2033;
        bool var_2034;
        bool var_2035;
        wp::float64 var_2036;
        bool var_2037;
        wp::float64 var_2038;
        bool var_2039;
        wp::vec_t<3, wp::float64> var_2040;
        wp::float64 var_2041;
        wp::float64 var_2042;
        wp::vec_t<3, wp::float64> var_2043;
        wp::vec_t<3, wp::float64> var_2044;
        wp::vec_t<3, wp::float64> var_2045;
        wp::vec_t<3, wp::float64> var_2046;
        wp::vec_t<3, wp::float64> var_2047;
        bool var_2048;
        bool var_2049;
        bool var_2050;
        const wp::int32 var_2051 = 1;
        wp::int32 var_2052;
        wp::int32 var_2053;
        wp::int32 var_2054;
        wp::vec_t<3, wp::float64> var_2055;
        const wp::int32 var_2056 = 2;
        wp::vec_t<3, wp::float64> var_2057;
        wp::vec_t<4, wp::float64> var_2058;
        wp::float64 var_2059;
        wp::vec_t<3, wp::float64> var_2060;
        wp::vec_t<4, wp::float64> var_2061;
        wp::float64 var_2062;
        bool var_2063;
        bool var_2064;
        wp::float64 var_2065;
        bool var_2066;
        wp::float64 var_2067;
        bool var_2068;
        bool var_2069;
        wp::float64 var_2070;
        bool var_2071;
        wp::float64 var_2072;
        bool var_2073;
        wp::vec_t<3, wp::float64> var_2074;
        wp::float64 var_2075;
        wp::float64 var_2076;
        wp::vec_t<3, wp::float64> var_2077;
        wp::vec_t<3, wp::float64> var_2078;
        wp::vec_t<3, wp::float64> var_2079;
        wp::vec_t<3, wp::float64> var_2080;
        wp::vec_t<3, wp::float64> var_2081;
        bool var_2082;
        bool var_2083;
        bool var_2084;
        const wp::int32 var_2085 = 1;
        wp::int32 var_2086;
        wp::int32 var_2087;
        wp::int32 var_2088;
        wp::vec_t<3, wp::float64> var_2089;
        const wp::int32 var_2090 = 3;
        wp::vec_t<3, wp::float64> var_2091;
        wp::vec_t<4, wp::float64> var_2092;
        wp::float64 var_2093;
        wp::vec_t<3, wp::float64> var_2094;
        wp::vec_t<4, wp::float64> var_2095;
        wp::float64 var_2096;
        bool var_2097;
        bool var_2098;
        wp::float64 var_2099;
        bool var_2100;
        wp::float64 var_2101;
        bool var_2102;
        bool var_2103;
        wp::float64 var_2104;
        bool var_2105;
        wp::float64 var_2106;
        bool var_2107;
        wp::vec_t<3, wp::float64> var_2108;
        wp::float64 var_2109;
        wp::float64 var_2110;
        wp::vec_t<3, wp::float64> var_2111;
        wp::vec_t<3, wp::float64> var_2112;
        wp::vec_t<3, wp::float64> var_2113;
        wp::vec_t<3, wp::float64> var_2114;
        wp::vec_t<3, wp::float64> var_2115;
        bool var_2116;
        bool var_2117;
        bool var_2118;
        const wp::int32 var_2119 = 1;
        wp::int32 var_2120;
        wp::int32 var_2121;
        wp::int32 var_2122;
        wp::vec_t<3, wp::float64> var_2123;
        const wp::int32 var_2124 = 0;
        bool var_2125;
        wp::float64 var_2126;
        wp::vec_t<3, wp::float64> var_2127;
        wp::range_t var_2128;
        wp::int32 var_2129;
        wp::vec_t<3, wp::float64> var_2130;
        wp::vec_t<3, wp::float64> var_2131;
        wp::float64 var_2132;
        wp::vec_t<3, wp::float64> var_2133;
        const wp::int32 var_2134 = -1;
        wp::int32 var_2135;
        wp::float64 var_2136;
        wp::int32* var_2137;
        const wp::int32 var_2138 = 1;
        wp::int32 var_2139;
        wp::int32* var_2140;
        wp::range_t var_2141;
        wp::int32 var_2142;
        wp::int32 var_2143;
        wp::int32 var_2144;
        wp::int32* var_2145;
        wp::int32 var_2146;
        wp::int32 var_2147;
        const wp::int32 var_2148 = 0;
        wp::vec_t<3, wp::float64>* var_2149;
        const wp::int32 var_2150 = 1;
        wp::vec_t<3, wp::float64>* var_2151;
        const wp::int32 var_2152 = 2;
        wp::vec_t<3, wp::float64>* var_2153;
        wp::vec_t<3, wp::float64> var_2154;
        wp::vec_t<3, wp::float64> var_2155;
        wp::vec_t<3, wp::float64> var_2156;
        wp::vec_t<3, wp::float64> var_2157;
        wp::vec_t<3, wp::float64> var_2158;
        wp::float64 var_2159;
        bool var_2160;
        wp::float64 var_2161;
        wp::int32 var_2162;
        wp::int32 var_2163;
        wp::float64 var_2164;
        wp::float64 var_2165;
        wp::range_t var_2166;
        wp::int32 var_2167;
        wp::vec_t<3, wp::float64> var_2168;
        wp::vec_t<3, wp::float64> var_2169;
        const wp::int32 var_2170 = 0;
        wp::vec_t<3, wp::float64>* var_2171;
        const wp::int32 var_2172 = 1;
        wp::vec_t<3, wp::float64>* var_2173;
        const wp::int32 var_2174 = 2;
        wp::vec_t<3, wp::float64>* var_2175;
        wp::vec_t<3, wp::float64> var_2176;
        wp::vec_t<3, wp::float64> var_2177;
        wp::vec_t<3, wp::float64> var_2178;
        wp::vec_t<3, wp::float64> var_2179;
        wp::vec_t<3, wp::float64> var_2180;
        wp::float64 var_2181;
        wp::float64 var_2182;
        bool var_2183;
        wp::int32* var_2184;
        const wp::int32 var_2185 = 1;
        wp::int32 var_2186;
        wp::int32* var_2187;
        wp::range_t var_2188;
        wp::int32 var_2189;
        wp::int32 var_2190;
        wp::int32 var_2191;
        wp::int32 var_2192;
        wp::int32* var_2193;
        wp::int32 var_2194;
        wp::int32 var_2195;
        wp::float64 var_2196;
        wp::range_t var_2197;
        wp::int32 var_2198;
        wp::vec_t<3, wp::float64> var_2199;
        wp::vec_t<3, wp::float64> var_2200;
        const wp::int32 var_2201 = 0;
        wp::vec_t<3, wp::float64>* var_2202;
        const wp::int32 var_2203 = 1;
        wp::vec_t<3, wp::float64>* var_2204;
        const wp::int32 var_2205 = 2;
        wp::vec_t<3, wp::float64>* var_2206;
        wp::vec_t<3, wp::float64> var_2207;
        wp::vec_t<3, wp::float64> var_2208;
        wp::vec_t<3, wp::float64> var_2209;
        wp::vec_t<3, wp::float64> var_2210;
        wp::vec_t<3, wp::float64> var_2211;
        wp::float64 var_2212;
        wp::float64 var_2213;
        wp::float64 var_2214;
        bool var_2215;
        wp::int32 var_2216;
        wp::int32 var_2217;
        wp::float64 var_2218;
        wp::int32 var_2219;
        wp::int32 var_2220;
        const wp::int32 var_2221 = 0;
        wp::float64 var_2222;
        bool var_2223;
        const wp::int32 var_2224 = 1;
        wp::int32 var_2225;
        //---------
        // forward
        // def prove(tets:wp.array(dtype=M43),active_count:wp.array(dtype=int),active_ids:wp.array(dtype=int),cells:wp.array(dtype=M43),planes:wp.array(dtype=wp.mat44d),valid:wp.array(dtype=int),lo:wp.array(dtype=wp.vec3d),hi:wp.array(dtype=wp.vec3d),tri:wp.array2d(dtype=wp.vec3d),ptr:wp.array(dtype=int),ids:wp.array(dtype=int),target:wp.float64,unresolved:wp.array(dtype=int),upper:wp.array(dtype=wp.float64)):       <L 33>
        // lane,c=wp.tid()                                                                        <L 34>
        builtin_tid2d(var_0, var_1);
        // for slot in range(lane,active_count[0],64):                                            <L 35>
        var_3 = wp::address(var_active_count, var_2);
        var_6 = wp::load(var_3);
        var_5 = wp::range(var_0, var_6, var_4);
        start_for_0:;
            if (iter_cmp(var_5) == 0) goto end_for_0;
            var_7 = wp::iter_next(var_5);
            // i=active_ids[slot];a=tets[i];b=cells[c];overlap=True                               <L 36>
            var_8 = wp::address(var_active_ids, var_7);
            var_10 = wp::load(var_8);
            var_9 = wp::copy(var_10);
            var_11 = wp::address(var_tets, var_9);
            var_13 = wp::load(var_11);
            var_12 = wp::copy(var_13);
            var_14 = wp::address(var_cells, var_1);
            var_16 = wp::load(var_14);
            var_15 = wp::copy(var_16);
            // for k in range(3):                                                                 <L 37>
            // amin=wp.min(wp.min(a[0,k],a[1,k]),wp.min(a[2,k],a[3,k]));amax=wp.max(wp.max(a[0,k],a[1,k]),wp.max(a[2,k],a[3,k]))       <L 38>
            var_20 = wp::extract(var_12, var_19, var_18);
            var_22 = wp::extract(var_12, var_21, var_18);
            var_23 = wp::min(var_20, var_22);
            var_25 = wp::extract(var_12, var_24, var_18);
            var_27 = wp::extract(var_12, var_26, var_18);
            var_28 = wp::min(var_25, var_27);
            var_29 = wp::min(var_23, var_28);
            var_31 = wp::extract(var_12, var_30, var_18);
            var_33 = wp::extract(var_12, var_32, var_18);
            var_34 = wp::max(var_31, var_33);
            var_36 = wp::extract(var_12, var_35, var_18);
            var_38 = wp::extract(var_12, var_37, var_18);
            var_39 = wp::max(var_36, var_38);
            var_40 = wp::max(var_34, var_39);
            // if amax+wp.float64(1e-12)<lo[c][k] or hi[c][k]+wp.float64(1e-12)<amin:overlap=False       <L 39>
            var_42 = 1e-12;
            var_43 = wp::add(var_40, var_42);
            var_44 = wp::address(var_lo, var_1);
            var_46 = wp::load(var_44);
            var_45 = wp::extract(var_46, var_18);
            var_47 = (var_43 < var_45);
            var_41 = var_47;
            if (!var_41) {
                var_48 = wp::address(var_hi, var_1);
                var_50 = wp::load(var_48);
                var_49 = wp::extract(var_50, var_18);
                var_51 = 1e-12;
                var_52 = wp::add(var_49, var_51);
                var_53 = (var_52 < var_29);
                var_41 = var_41 || var_53;
            }
            if (var_41) {
            }
            var_55 = wp::where(var_41, var_54, var_17);
            // amin=wp.min(wp.min(a[0,k],a[1,k]),wp.min(a[2,k],a[3,k]));amax=wp.max(wp.max(a[0,k],a[1,k]),wp.max(a[2,k],a[3,k]))       <L 38>
            var_58 = wp::extract(var_12, var_57, var_56);
            var_60 = wp::extract(var_12, var_59, var_56);
            var_61 = wp::min(var_58, var_60);
            var_63 = wp::extract(var_12, var_62, var_56);
            var_65 = wp::extract(var_12, var_64, var_56);
            var_66 = wp::min(var_63, var_65);
            var_67 = wp::min(var_61, var_66);
            var_69 = wp::extract(var_12, var_68, var_56);
            var_71 = wp::extract(var_12, var_70, var_56);
            var_72 = wp::max(var_69, var_71);
            var_74 = wp::extract(var_12, var_73, var_56);
            var_76 = wp::extract(var_12, var_75, var_56);
            var_77 = wp::max(var_74, var_76);
            var_78 = wp::max(var_72, var_77);
            // if amax+wp.float64(1e-12)<lo[c][k] or hi[c][k]+wp.float64(1e-12)<amin:overlap=False       <L 39>
            var_80 = 1e-12;
            var_81 = wp::add(var_78, var_80);
            var_82 = wp::address(var_lo, var_1);
            var_84 = wp::load(var_82);
            var_83 = wp::extract(var_84, var_56);
            var_85 = (var_81 < var_83);
            var_79 = var_85;
            if (!var_79) {
                var_86 = wp::address(var_hi, var_1);
                var_88 = wp::load(var_86);
                var_87 = wp::extract(var_88, var_56);
                var_89 = 1e-12;
                var_90 = wp::add(var_87, var_89);
                var_91 = (var_90 < var_67);
                var_79 = var_79 || var_91;
            }
            if (var_79) {
            }
            var_93 = wp::where(var_79, var_92, var_55);
            // amin=wp.min(wp.min(a[0,k],a[1,k]),wp.min(a[2,k],a[3,k]));amax=wp.max(wp.max(a[0,k],a[1,k]),wp.max(a[2,k],a[3,k]))       <L 38>
            var_96 = wp::extract(var_12, var_95, var_94);
            var_98 = wp::extract(var_12, var_97, var_94);
            var_99 = wp::min(var_96, var_98);
            var_101 = wp::extract(var_12, var_100, var_94);
            var_103 = wp::extract(var_12, var_102, var_94);
            var_104 = wp::min(var_101, var_103);
            var_105 = wp::min(var_99, var_104);
            var_107 = wp::extract(var_12, var_106, var_94);
            var_109 = wp::extract(var_12, var_108, var_94);
            var_110 = wp::max(var_107, var_109);
            var_112 = wp::extract(var_12, var_111, var_94);
            var_114 = wp::extract(var_12, var_113, var_94);
            var_115 = wp::max(var_112, var_114);
            var_116 = wp::max(var_110, var_115);
            // if amax+wp.float64(1e-12)<lo[c][k] or hi[c][k]+wp.float64(1e-12)<amin:overlap=False       <L 39>
            var_118 = 1e-12;
            var_119 = wp::add(var_116, var_118);
            var_120 = wp::address(var_lo, var_1);
            var_122 = wp::load(var_120);
            var_121 = wp::extract(var_122, var_94);
            var_123 = (var_119 < var_121);
            var_117 = var_123;
            if (!var_117) {
                var_124 = wp::address(var_hi, var_1);
                var_126 = wp::load(var_124);
                var_125 = wp::extract(var_126, var_94);
                var_127 = 1e-12;
                var_128 = wp::add(var_125, var_127);
                var_129 = (var_128 < var_105);
                var_117 = var_117 || var_129;
            }
            if (var_117) {
            }
            var_131 = wp::where(var_117, var_130, var_93);
            // if not overlap:continue                                                            <L 40>
            var_132 = wp::unot(var_131);
            if (var_132) {
                goto start_for_0;
            }
            // pa=wp.mat44d(wp.float64(0.));ok=valid[c]!=0;h=wp.float64(0.)                       <L 41>
            var_133 = 0.0;
            var_134 = wp::mat_t<4, 4, wp::float64>(var_133);
            var_135 = wp::address(var_valid, var_1);
            var_138 = wp::load(var_135);
            var_137 = (var_138 != var_136);
            var_139 = 0.0;
            // for u in range(4):                                                                 <L 42>
            // for v in range(u):h=wp.max(h,wp.length(a[u]-a[v]))                                 <L 43>
            var_143 = wp::extract(var_12, var_141);
            var_144 = wp::extract(var_12, var_142);
            var_145 = wp::sub(var_143, var_144);
            var_146 = wp::length(var_145);
            var_147 = wp::max(var_139, var_146);
            var_150 = wp::extract(var_12, var_148);
            var_151 = wp::extract(var_12, var_149);
            var_152 = wp::sub(var_150, var_151);
            var_153 = wp::length(var_152);
            var_154 = wp::max(var_147, var_153);
            var_156 = wp::extract(var_12, var_148);
            var_157 = wp::extract(var_12, var_155);
            var_158 = wp::sub(var_156, var_157);
            var_159 = wp::length(var_158);
            var_160 = wp::max(var_154, var_159);
            var_163 = wp::extract(var_12, var_161);
            var_164 = wp::extract(var_12, var_162);
            var_165 = wp::sub(var_163, var_164);
            var_166 = wp::length(var_165);
            var_167 = wp::max(var_160, var_166);
            var_169 = wp::extract(var_12, var_161);
            var_170 = wp::extract(var_12, var_168);
            var_171 = wp::sub(var_169, var_170);
            var_172 = wp::length(var_171);
            var_173 = wp::max(var_167, var_172);
            var_175 = wp::extract(var_12, var_161);
            var_176 = wp::extract(var_12, var_174);
            var_177 = wp::sub(var_175, var_176);
            var_178 = wp::length(var_177);
            var_179 = wp::max(var_173, var_178);
            // for u in range(4):                                                                 <L 44>
            // p0=a[(u+1)%4];p1=a[(u+2)%4];p2=a[(u+3)%4];n=wp.cross(p1-p0,p2-p0);size=wp.length(n)       <L 45>
            var_182 = wp::add(var_180, var_181);
            var_184 = wp::mod(var_182, var_183);
            var_185 = wp::extract(var_12, var_184);
            var_187 = wp::add(var_180, var_186);
            var_189 = wp::mod(var_187, var_188);
            var_190 = wp::extract(var_12, var_189);
            var_192 = wp::add(var_180, var_191);
            var_194 = wp::mod(var_192, var_193);
            var_195 = wp::extract(var_12, var_194);
            var_196 = wp::sub(var_190, var_185);
            var_197 = wp::sub(var_195, var_185);
            var_198 = wp::cross(var_196, var_197);
            var_199 = wp::length(var_198);
            // if size==wp.float64(0.):ok=False                                                   <L 46>
            var_200 = 0.0;
            var_201 = (var_199 == var_200);
            if (var_201) {
            }
            if (!var_201) {
                // n=n/size                                                                       <L 48>
                var_203 = wp::div(var_198, var_199);
                // if wp.dot(n,a[u]-p0)>wp.float64(0.):n=-n                                       <L 49>
                var_204 = wp::extract(var_12, var_180);
                var_205 = wp::sub(var_204, var_185);
                var_206 = wp::dot(var_203, var_205);
                var_207 = 0.0;
                var_208 = (var_206 > var_207);
                if (var_208) {
                    var_209 = wp::neg(var_203);
                }
                var_210 = wp::where(var_208, var_209, var_203);
                // d=-wp.dot(n,p0);pa[u]=wp.vec4d(n[0],n[1],n[2],d)                               <L 50>
                var_211 = wp::dot(var_210, var_185);
                var_212 = wp::neg(var_211);
                var_214 = wp::extract(var_210, var_213);
                var_216 = wp::extract(var_210, var_215);
                var_218 = wp::extract(var_210, var_217);
                var_219 = wp::vec_t<4, wp::float64>(var_214, var_216, var_218, var_212);
                wp::assign_inplace(var_134, var_180, var_219);
                // if wp.abs(wp.dot(n,a[u])+d)<wp.float64(1e-8)*h:ok=False                        <L 51>
                var_220 = wp::extract(var_12, var_180);
                var_221 = wp::dot(var_210, var_220);
                var_222 = wp::add(var_221, var_212);
                var_223 = wp::abs(var_222);
                var_224 = 1e-08;
                var_225 = wp::mul(var_224, var_179);
                var_226 = (var_223 < var_225);
                if (var_226) {
                }
                var_228 = wp::where(var_226, var_227, var_137);
            }
            var_229 = wp::where(var_201, var_202, var_228);
            var_230 = wp::where(var_201, var_198, var_210);
            // p0=a[(u+1)%4];p1=a[(u+2)%4];p2=a[(u+3)%4];n=wp.cross(p1-p0,p2-p0);size=wp.length(n)       <L 45>
            var_233 = wp::add(var_231, var_232);
            var_235 = wp::mod(var_233, var_234);
            var_236 = wp::extract(var_12, var_235);
            var_238 = wp::add(var_231, var_237);
            var_240 = wp::mod(var_238, var_239);
            var_241 = wp::extract(var_12, var_240);
            var_243 = wp::add(var_231, var_242);
            var_245 = wp::mod(var_243, var_244);
            var_246 = wp::extract(var_12, var_245);
            var_247 = wp::sub(var_241, var_236);
            var_248 = wp::sub(var_246, var_236);
            var_249 = wp::cross(var_247, var_248);
            var_250 = wp::length(var_249);
            // if size==wp.float64(0.):ok=False                                                   <L 46>
            var_251 = 0.0;
            var_252 = (var_250 == var_251);
            if (var_252) {
            }
            if (!var_252) {
                // n=n/size                                                                       <L 48>
                var_254 = wp::div(var_249, var_250);
                // if wp.dot(n,a[u]-p0)>wp.float64(0.):n=-n                                       <L 49>
                var_255 = wp::extract(var_12, var_231);
                var_256 = wp::sub(var_255, var_236);
                var_257 = wp::dot(var_254, var_256);
                var_258 = 0.0;
                var_259 = (var_257 > var_258);
                if (var_259) {
                    var_260 = wp::neg(var_254);
                }
                var_261 = wp::where(var_259, var_260, var_254);
                // d=-wp.dot(n,p0);pa[u]=wp.vec4d(n[0],n[1],n[2],d)                               <L 50>
                var_262 = wp::dot(var_261, var_236);
                var_263 = wp::neg(var_262);
                var_265 = wp::extract(var_261, var_264);
                var_267 = wp::extract(var_261, var_266);
                var_269 = wp::extract(var_261, var_268);
                var_270 = wp::vec_t<4, wp::float64>(var_265, var_267, var_269, var_263);
                wp::assign_inplace(var_134, var_231, var_270);
                // if wp.abs(wp.dot(n,a[u])+d)<wp.float64(1e-8)*h:ok=False                        <L 51>
                var_271 = wp::extract(var_12, var_231);
                var_272 = wp::dot(var_261, var_271);
                var_273 = wp::add(var_272, var_263);
                var_274 = wp::abs(var_273);
                var_275 = 1e-08;
                var_276 = wp::mul(var_275, var_179);
                var_277 = (var_274 < var_276);
                if (var_277) {
                }
                var_279 = wp::where(var_277, var_278, var_229);
            }
            var_280 = wp::where(var_252, var_253, var_279);
            var_281 = wp::where(var_252, var_249, var_261);
            var_282 = wp::where(var_252, var_212, var_263);
            // p0=a[(u+1)%4];p1=a[(u+2)%4];p2=a[(u+3)%4];n=wp.cross(p1-p0,p2-p0);size=wp.length(n)       <L 45>
            var_285 = wp::add(var_283, var_284);
            var_287 = wp::mod(var_285, var_286);
            var_288 = wp::extract(var_12, var_287);
            var_290 = wp::add(var_283, var_289);
            var_292 = wp::mod(var_290, var_291);
            var_293 = wp::extract(var_12, var_292);
            var_295 = wp::add(var_283, var_294);
            var_297 = wp::mod(var_295, var_296);
            var_298 = wp::extract(var_12, var_297);
            var_299 = wp::sub(var_293, var_288);
            var_300 = wp::sub(var_298, var_288);
            var_301 = wp::cross(var_299, var_300);
            var_302 = wp::length(var_301);
            // if size==wp.float64(0.):ok=False                                                   <L 46>
            var_303 = 0.0;
            var_304 = (var_302 == var_303);
            if (var_304) {
            }
            if (!var_304) {
                // n=n/size                                                                       <L 48>
                var_306 = wp::div(var_301, var_302);
                // if wp.dot(n,a[u]-p0)>wp.float64(0.):n=-n                                       <L 49>
                var_307 = wp::extract(var_12, var_283);
                var_308 = wp::sub(var_307, var_288);
                var_309 = wp::dot(var_306, var_308);
                var_310 = 0.0;
                var_311 = (var_309 > var_310);
                if (var_311) {
                    var_312 = wp::neg(var_306);
                }
                var_313 = wp::where(var_311, var_312, var_306);
                // d=-wp.dot(n,p0);pa[u]=wp.vec4d(n[0],n[1],n[2],d)                               <L 50>
                var_314 = wp::dot(var_313, var_288);
                var_315 = wp::neg(var_314);
                var_317 = wp::extract(var_313, var_316);
                var_319 = wp::extract(var_313, var_318);
                var_321 = wp::extract(var_313, var_320);
                var_322 = wp::vec_t<4, wp::float64>(var_317, var_319, var_321, var_315);
                wp::assign_inplace(var_134, var_283, var_322);
                // if wp.abs(wp.dot(n,a[u])+d)<wp.float64(1e-8)*h:ok=False                        <L 51>
                var_323 = wp::extract(var_12, var_283);
                var_324 = wp::dot(var_313, var_323);
                var_325 = wp::add(var_324, var_315);
                var_326 = wp::abs(var_325);
                var_327 = 1e-08;
                var_328 = wp::mul(var_327, var_179);
                var_329 = (var_326 < var_328);
                if (var_329) {
                }
                var_331 = wp::where(var_329, var_330, var_280);
            }
            var_332 = wp::where(var_304, var_305, var_331);
            var_333 = wp::where(var_304, var_301, var_313);
            var_334 = wp::where(var_304, var_282, var_315);
            // p0=a[(u+1)%4];p1=a[(u+2)%4];p2=a[(u+3)%4];n=wp.cross(p1-p0,p2-p0);size=wp.length(n)       <L 45>
            var_337 = wp::add(var_335, var_336);
            var_339 = wp::mod(var_337, var_338);
            var_340 = wp::extract(var_12, var_339);
            var_342 = wp::add(var_335, var_341);
            var_344 = wp::mod(var_342, var_343);
            var_345 = wp::extract(var_12, var_344);
            var_347 = wp::add(var_335, var_346);
            var_349 = wp::mod(var_347, var_348);
            var_350 = wp::extract(var_12, var_349);
            var_351 = wp::sub(var_345, var_340);
            var_352 = wp::sub(var_350, var_340);
            var_353 = wp::cross(var_351, var_352);
            var_354 = wp::length(var_353);
            // if size==wp.float64(0.):ok=False                                                   <L 46>
            var_355 = 0.0;
            var_356 = (var_354 == var_355);
            if (var_356) {
            }
            if (!var_356) {
                // n=n/size                                                                       <L 48>
                var_358 = wp::div(var_353, var_354);
                // if wp.dot(n,a[u]-p0)>wp.float64(0.):n=-n                                       <L 49>
                var_359 = wp::extract(var_12, var_335);
                var_360 = wp::sub(var_359, var_340);
                var_361 = wp::dot(var_358, var_360);
                var_362 = 0.0;
                var_363 = (var_361 > var_362);
                if (var_363) {
                    var_364 = wp::neg(var_358);
                }
                var_365 = wp::where(var_363, var_364, var_358);
                // d=-wp.dot(n,p0);pa[u]=wp.vec4d(n[0],n[1],n[2],d)                               <L 50>
                var_366 = wp::dot(var_365, var_340);
                var_367 = wp::neg(var_366);
                var_369 = wp::extract(var_365, var_368);
                var_371 = wp::extract(var_365, var_370);
                var_373 = wp::extract(var_365, var_372);
                var_374 = wp::vec_t<4, wp::float64>(var_369, var_371, var_373, var_367);
                wp::assign_inplace(var_134, var_335, var_374);
                // if wp.abs(wp.dot(n,a[u])+d)<wp.float64(1e-8)*h:ok=False                        <L 51>
                var_375 = wp::extract(var_12, var_335);
                var_376 = wp::dot(var_365, var_375);
                var_377 = wp::add(var_376, var_367);
                var_378 = wp::abs(var_377);
                var_379 = 1e-08;
                var_380 = wp::mul(var_379, var_179);
                var_381 = (var_378 < var_380);
                if (var_381) {
                }
                var_383 = wp::where(var_381, var_382, var_332);
            }
            var_384 = wp::where(var_356, var_357, var_383);
            var_385 = wp::where(var_356, var_353, var_365);
            var_386 = wp::where(var_356, var_334, var_367);
            // if not ok:wp.atomic_max(unresolved,i,1);continue                                   <L 52>
            var_387 = wp::unot(var_384);
            if (var_387) {
                var_389 = wp::atomic_max(var_unresolved, var_9, var_388);
                goto start_for_0;
            }
            // pb=planes[c];points=M56(wp.float64(0.));count=int(0)                               <L 53>
            var_390 = wp::address(var_planes, var_1);
            var_392 = wp::load(var_390);
            var_391 = wp::copy(var_392);
            var_393 = 0.0;
            var_394 = wp::mat_t<56, 3, wp::float64>(var_393);
            var_396 = wp::int(var_395);
            // for u in range(4):                                                                 <L 54>
            // if inside(a[u],pb):points[count]=a[u];count+=1                                     <L 55>
            var_398 = wp::extract(var_12, var_397);
            var_399 = inside_0(var_398, var_391);
            if (var_399) {
                var_400 = wp::extract(var_12, var_397);
                wp::assign_inplace(var_394, var_396, var_400);
                var_402 = wp::add(var_396, var_401);
            }
            var_403 = wp::where(var_399, var_402, var_396);
            // if inside(b[u],pa):points[count]=b[u];count+=1                                     <L 56>
            var_404 = wp::extract(var_15, var_397);
            var_405 = inside_0(var_404, var_134);
            if (var_405) {
                var_406 = wp::extract(var_15, var_397);
                wp::assign_inplace(var_394, var_403, var_406);
                var_408 = wp::add(var_403, var_407);
            }
            var_409 = wp::where(var_405, var_408, var_403);
            // if inside(a[u],pb):points[count]=a[u];count+=1                                     <L 55>
            var_411 = wp::extract(var_12, var_410);
            var_412 = inside_0(var_411, var_391);
            if (var_412) {
                var_413 = wp::extract(var_12, var_410);
                wp::assign_inplace(var_394, var_409, var_413);
                var_415 = wp::add(var_409, var_414);
            }
            var_416 = wp::where(var_412, var_415, var_409);
            // if inside(b[u],pa):points[count]=b[u];count+=1                                     <L 56>
            var_417 = wp::extract(var_15, var_410);
            var_418 = inside_0(var_417, var_134);
            if (var_418) {
                var_419 = wp::extract(var_15, var_410);
                wp::assign_inplace(var_394, var_416, var_419);
                var_421 = wp::add(var_416, var_420);
            }
            var_422 = wp::where(var_418, var_421, var_416);
            // if inside(a[u],pb):points[count]=a[u];count+=1                                     <L 55>
            var_424 = wp::extract(var_12, var_423);
            var_425 = inside_0(var_424, var_391);
            if (var_425) {
                var_426 = wp::extract(var_12, var_423);
                wp::assign_inplace(var_394, var_422, var_426);
                var_428 = wp::add(var_422, var_427);
            }
            var_429 = wp::where(var_425, var_428, var_422);
            // if inside(b[u],pa):points[count]=b[u];count+=1                                     <L 56>
            var_430 = wp::extract(var_15, var_423);
            var_431 = inside_0(var_430, var_134);
            if (var_431) {
                var_432 = wp::extract(var_15, var_423);
                wp::assign_inplace(var_394, var_429, var_432);
                var_434 = wp::add(var_429, var_433);
            }
            var_435 = wp::where(var_431, var_434, var_429);
            // if inside(a[u],pb):points[count]=a[u];count+=1                                     <L 55>
            var_437 = wp::extract(var_12, var_436);
            var_438 = inside_0(var_437, var_391);
            if (var_438) {
                var_439 = wp::extract(var_12, var_436);
                wp::assign_inplace(var_394, var_435, var_439);
                var_441 = wp::add(var_435, var_440);
            }
            var_442 = wp::where(var_438, var_441, var_435);
            // if inside(b[u],pa):points[count]=b[u];count+=1                                     <L 56>
            var_443 = wp::extract(var_15, var_436);
            var_444 = inside_0(var_443, var_134);
            if (var_444) {
                var_445 = wp::extract(var_15, var_436);
                wp::assign_inplace(var_394, var_442, var_445);
                var_447 = wp::add(var_442, var_446);
            }
            var_448 = wp::where(var_444, var_447, var_442);
            // for side in range(2):                                                              <L 57>
            // vertices=a;other=pb;own=pa                                                         <L 58>
            var_450 = wp::copy(var_12);
            var_451 = wp::copy(var_391);
            var_452 = wp::copy(var_134);
            // if side==1:vertices=b;other=pa;own=pb                                              <L 59>
            var_454 = (var_449 == var_453);
            if (var_454) {
                var_455 = wp::copy(var_15);
                var_456 = wp::copy(var_134);
                var_457 = wp::copy(var_391);
            }
            var_458 = wp::where(var_454, var_455, var_450);
            var_459 = wp::where(var_454, var_456, var_451);
            var_460 = wp::where(var_454, var_457, var_452);
            // for u in range(4):                                                                 <L 60>
            // for v in range(u):                                                                 <L 61>
            // for k in range(4):                                                                 <L 62>
            // d0=plane_value(vertices[u],other[k]);d1=plane_value(vertices[v],other[k])          <L 63>
            var_465 = wp::extract(var_458, var_462);
            var_466 = wp::extract(var_459, var_464);
            var_467 = plane_value_0(var_465, var_466);
            var_468 = wp::extract(var_458, var_463);
            var_469 = wp::extract(var_459, var_464);
            var_470 = plane_value_0(var_468, var_469);
            // if (d0<wp.float64(0.) and d1>wp.float64(0.)) or (d1<wp.float64(0.) and d0>wp.float64(0.)):       <L 64>
            var_473 = 0.0;
            var_474 = (var_467 < var_473);
            var_472 = var_474;
            if (var_472) {
                var_475 = 0.0;
                var_476 = (var_470 > var_475);
                var_472 = var_472 && var_476;
            }
            var_471 = var_472;
            if (!var_471) {
                var_478 = 0.0;
                var_479 = (var_470 < var_478);
                var_477 = var_479;
                if (var_477) {
                    var_480 = 0.0;
                    var_481 = (var_467 > var_480);
                    var_477 = var_477 && var_481;
                }
                var_471 = var_471 || var_477;
            }
            if (var_471) {
                // point=vertices[u]+d0/(d0-d1)*(vertices[v]-vertices[u])                         <L 65>
                var_482 = wp::extract(var_458, var_462);
                var_483 = wp::sub(var_467, var_470);
                var_484 = wp::div(var_467, var_483);
                var_485 = wp::extract(var_458, var_463);
                var_486 = wp::extract(var_458, var_462);
                var_487 = wp::sub(var_485, var_486);
                var_488 = wp::mul(var_484, var_487);
                var_489 = wp::add(var_482, var_488);
                // if inside(point,other) and inside(point,own):points[count]=point;count+=1       <L 66>
                var_491 = inside_0(var_489, var_459);
                var_490 = var_491;
                if (var_490) {
                    var_492 = inside_0(var_489, var_460);
                    var_490 = var_490 && var_492;
                }
                if (var_490) {
                    wp::assign_inplace(var_394, var_448, var_489);
                    var_494 = wp::add(var_448, var_493);
                }
                var_495 = wp::where(var_490, var_494, var_448);
            }
            var_496 = wp::where(var_471, var_495, var_448);
            // d0=plane_value(vertices[u],other[k]);d1=plane_value(vertices[v],other[k])          <L 63>
            var_498 = wp::extract(var_458, var_462);
            var_499 = wp::extract(var_459, var_497);
            var_500 = plane_value_0(var_498, var_499);
            var_501 = wp::extract(var_458, var_463);
            var_502 = wp::extract(var_459, var_497);
            var_503 = plane_value_0(var_501, var_502);
            // if (d0<wp.float64(0.) and d1>wp.float64(0.)) or (d1<wp.float64(0.) and d0>wp.float64(0.)):       <L 64>
            var_506 = 0.0;
            var_507 = (var_500 < var_506);
            var_505 = var_507;
            if (var_505) {
                var_508 = 0.0;
                var_509 = (var_503 > var_508);
                var_505 = var_505 && var_509;
            }
            var_504 = var_505;
            if (!var_504) {
                var_511 = 0.0;
                var_512 = (var_503 < var_511);
                var_510 = var_512;
                if (var_510) {
                    var_513 = 0.0;
                    var_514 = (var_500 > var_513);
                    var_510 = var_510 && var_514;
                }
                var_504 = var_504 || var_510;
            }
            if (var_504) {
                // point=vertices[u]+d0/(d0-d1)*(vertices[v]-vertices[u])                         <L 65>
                var_515 = wp::extract(var_458, var_462);
                var_516 = wp::sub(var_500, var_503);
                var_517 = wp::div(var_500, var_516);
                var_518 = wp::extract(var_458, var_463);
                var_519 = wp::extract(var_458, var_462);
                var_520 = wp::sub(var_518, var_519);
                var_521 = wp::mul(var_517, var_520);
                var_522 = wp::add(var_515, var_521);
                // if inside(point,other) and inside(point,own):points[count]=point;count+=1       <L 66>
                var_524 = inside_0(var_522, var_459);
                var_523 = var_524;
                if (var_523) {
                    var_525 = inside_0(var_522, var_460);
                    var_523 = var_523 && var_525;
                }
                if (var_523) {
                    wp::assign_inplace(var_394, var_496, var_522);
                    var_527 = wp::add(var_496, var_526);
                }
                var_528 = wp::where(var_523, var_527, var_496);
            }
            var_529 = wp::where(var_504, var_528, var_496);
            var_530 = wp::where(var_504, var_522, var_489);
            // d0=plane_value(vertices[u],other[k]);d1=plane_value(vertices[v],other[k])          <L 63>
            var_532 = wp::extract(var_458, var_462);
            var_533 = wp::extract(var_459, var_531);
            var_534 = plane_value_0(var_532, var_533);
            var_535 = wp::extract(var_458, var_463);
            var_536 = wp::extract(var_459, var_531);
            var_537 = plane_value_0(var_535, var_536);
            // if (d0<wp.float64(0.) and d1>wp.float64(0.)) or (d1<wp.float64(0.) and d0>wp.float64(0.)):       <L 64>
            var_540 = 0.0;
            var_541 = (var_534 < var_540);
            var_539 = var_541;
            if (var_539) {
                var_542 = 0.0;
                var_543 = (var_537 > var_542);
                var_539 = var_539 && var_543;
            }
            var_538 = var_539;
            if (!var_538) {
                var_545 = 0.0;
                var_546 = (var_537 < var_545);
                var_544 = var_546;
                if (var_544) {
                    var_547 = 0.0;
                    var_548 = (var_534 > var_547);
                    var_544 = var_544 && var_548;
                }
                var_538 = var_538 || var_544;
            }
            if (var_538) {
                // point=vertices[u]+d0/(d0-d1)*(vertices[v]-vertices[u])                         <L 65>
                var_549 = wp::extract(var_458, var_462);
                var_550 = wp::sub(var_534, var_537);
                var_551 = wp::div(var_534, var_550);
                var_552 = wp::extract(var_458, var_463);
                var_553 = wp::extract(var_458, var_462);
                var_554 = wp::sub(var_552, var_553);
                var_555 = wp::mul(var_551, var_554);
                var_556 = wp::add(var_549, var_555);
                // if inside(point,other) and inside(point,own):points[count]=point;count+=1       <L 66>
                var_558 = inside_0(var_556, var_459);
                var_557 = var_558;
                if (var_557) {
                    var_559 = inside_0(var_556, var_460);
                    var_557 = var_557 && var_559;
                }
                if (var_557) {
                    wp::assign_inplace(var_394, var_529, var_556);
                    var_561 = wp::add(var_529, var_560);
                }
                var_562 = wp::where(var_557, var_561, var_529);
            }
            var_563 = wp::where(var_538, var_562, var_529);
            var_564 = wp::where(var_538, var_556, var_530);
            // d0=plane_value(vertices[u],other[k]);d1=plane_value(vertices[v],other[k])          <L 63>
            var_566 = wp::extract(var_458, var_462);
            var_567 = wp::extract(var_459, var_565);
            var_568 = plane_value_0(var_566, var_567);
            var_569 = wp::extract(var_458, var_463);
            var_570 = wp::extract(var_459, var_565);
            var_571 = plane_value_0(var_569, var_570);
            // if (d0<wp.float64(0.) and d1>wp.float64(0.)) or (d1<wp.float64(0.) and d0>wp.float64(0.)):       <L 64>
            var_574 = 0.0;
            var_575 = (var_568 < var_574);
            var_573 = var_575;
            if (var_573) {
                var_576 = 0.0;
                var_577 = (var_571 > var_576);
                var_573 = var_573 && var_577;
            }
            var_572 = var_573;
            if (!var_572) {
                var_579 = 0.0;
                var_580 = (var_571 < var_579);
                var_578 = var_580;
                if (var_578) {
                    var_581 = 0.0;
                    var_582 = (var_568 > var_581);
                    var_578 = var_578 && var_582;
                }
                var_572 = var_572 || var_578;
            }
            if (var_572) {
                // point=vertices[u]+d0/(d0-d1)*(vertices[v]-vertices[u])                         <L 65>
                var_583 = wp::extract(var_458, var_462);
                var_584 = wp::sub(var_568, var_571);
                var_585 = wp::div(var_568, var_584);
                var_586 = wp::extract(var_458, var_463);
                var_587 = wp::extract(var_458, var_462);
                var_588 = wp::sub(var_586, var_587);
                var_589 = wp::mul(var_585, var_588);
                var_590 = wp::add(var_583, var_589);
                // if inside(point,other) and inside(point,own):points[count]=point;count+=1       <L 66>
                var_592 = inside_0(var_590, var_459);
                var_591 = var_592;
                if (var_591) {
                    var_593 = inside_0(var_590, var_460);
                    var_591 = var_591 && var_593;
                }
                if (var_591) {
                    wp::assign_inplace(var_394, var_563, var_590);
                    var_595 = wp::add(var_563, var_594);
                }
                var_596 = wp::where(var_591, var_595, var_563);
            }
            var_597 = wp::where(var_572, var_596, var_563);
            var_598 = wp::where(var_572, var_590, var_564);
            // for v in range(u):                                                                 <L 61>
            // for k in range(4):                                                                 <L 62>
            // d0=plane_value(vertices[u],other[k]);d1=plane_value(vertices[v],other[k])          <L 63>
            var_602 = wp::extract(var_458, var_599);
            var_603 = wp::extract(var_459, var_601);
            var_604 = plane_value_0(var_602, var_603);
            var_605 = wp::extract(var_458, var_600);
            var_606 = wp::extract(var_459, var_601);
            var_607 = plane_value_0(var_605, var_606);
            // if (d0<wp.float64(0.) and d1>wp.float64(0.)) or (d1<wp.float64(0.) and d0>wp.float64(0.)):       <L 64>
            var_610 = 0.0;
            var_611 = (var_604 < var_610);
            var_609 = var_611;
            if (var_609) {
                var_612 = 0.0;
                var_613 = (var_607 > var_612);
                var_609 = var_609 && var_613;
            }
            var_608 = var_609;
            if (!var_608) {
                var_615 = 0.0;
                var_616 = (var_607 < var_615);
                var_614 = var_616;
                if (var_614) {
                    var_617 = 0.0;
                    var_618 = (var_604 > var_617);
                    var_614 = var_614 && var_618;
                }
                var_608 = var_608 || var_614;
            }
            if (var_608) {
                // point=vertices[u]+d0/(d0-d1)*(vertices[v]-vertices[u])                         <L 65>
                var_619 = wp::extract(var_458, var_599);
                var_620 = wp::sub(var_604, var_607);
                var_621 = wp::div(var_604, var_620);
                var_622 = wp::extract(var_458, var_600);
                var_623 = wp::extract(var_458, var_599);
                var_624 = wp::sub(var_622, var_623);
                var_625 = wp::mul(var_621, var_624);
                var_626 = wp::add(var_619, var_625);
                // if inside(point,other) and inside(point,own):points[count]=point;count+=1       <L 66>
                var_628 = inside_0(var_626, var_459);
                var_627 = var_628;
                if (var_627) {
                    var_629 = inside_0(var_626, var_460);
                    var_627 = var_627 && var_629;
                }
                if (var_627) {
                    wp::assign_inplace(var_394, var_597, var_626);
                    var_631 = wp::add(var_597, var_630);
                }
                var_632 = wp::where(var_627, var_631, var_597);
            }
            var_633 = wp::where(var_608, var_632, var_597);
            var_634 = wp::where(var_608, var_626, var_598);
            // d0=plane_value(vertices[u],other[k]);d1=plane_value(vertices[v],other[k])          <L 63>
            var_636 = wp::extract(var_458, var_599);
            var_637 = wp::extract(var_459, var_635);
            var_638 = plane_value_0(var_636, var_637);
            var_639 = wp::extract(var_458, var_600);
            var_640 = wp::extract(var_459, var_635);
            var_641 = plane_value_0(var_639, var_640);
            // if (d0<wp.float64(0.) and d1>wp.float64(0.)) or (d1<wp.float64(0.) and d0>wp.float64(0.)):       <L 64>
            var_644 = 0.0;
            var_645 = (var_638 < var_644);
            var_643 = var_645;
            if (var_643) {
                var_646 = 0.0;
                var_647 = (var_641 > var_646);
                var_643 = var_643 && var_647;
            }
            var_642 = var_643;
            if (!var_642) {
                var_649 = 0.0;
                var_650 = (var_641 < var_649);
                var_648 = var_650;
                if (var_648) {
                    var_651 = 0.0;
                    var_652 = (var_638 > var_651);
                    var_648 = var_648 && var_652;
                }
                var_642 = var_642 || var_648;
            }
            if (var_642) {
                // point=vertices[u]+d0/(d0-d1)*(vertices[v]-vertices[u])                         <L 65>
                var_653 = wp::extract(var_458, var_599);
                var_654 = wp::sub(var_638, var_641);
                var_655 = wp::div(var_638, var_654);
                var_656 = wp::extract(var_458, var_600);
                var_657 = wp::extract(var_458, var_599);
                var_658 = wp::sub(var_656, var_657);
                var_659 = wp::mul(var_655, var_658);
                var_660 = wp::add(var_653, var_659);
                // if inside(point,other) and inside(point,own):points[count]=point;count+=1       <L 66>
                var_662 = inside_0(var_660, var_459);
                var_661 = var_662;
                if (var_661) {
                    var_663 = inside_0(var_660, var_460);
                    var_661 = var_661 && var_663;
                }
                if (var_661) {
                    wp::assign_inplace(var_394, var_633, var_660);
                    var_665 = wp::add(var_633, var_664);
                }
                var_666 = wp::where(var_661, var_665, var_633);
            }
            var_667 = wp::where(var_642, var_666, var_633);
            var_668 = wp::where(var_642, var_660, var_634);
            // d0=plane_value(vertices[u],other[k]);d1=plane_value(vertices[v],other[k])          <L 63>
            var_670 = wp::extract(var_458, var_599);
            var_671 = wp::extract(var_459, var_669);
            var_672 = plane_value_0(var_670, var_671);
            var_673 = wp::extract(var_458, var_600);
            var_674 = wp::extract(var_459, var_669);
            var_675 = plane_value_0(var_673, var_674);
            // if (d0<wp.float64(0.) and d1>wp.float64(0.)) or (d1<wp.float64(0.) and d0>wp.float64(0.)):       <L 64>
            var_678 = 0.0;
            var_679 = (var_672 < var_678);
            var_677 = var_679;
            if (var_677) {
                var_680 = 0.0;
                var_681 = (var_675 > var_680);
                var_677 = var_677 && var_681;
            }
            var_676 = var_677;
            if (!var_676) {
                var_683 = 0.0;
                var_684 = (var_675 < var_683);
                var_682 = var_684;
                if (var_682) {
                    var_685 = 0.0;
                    var_686 = (var_672 > var_685);
                    var_682 = var_682 && var_686;
                }
                var_676 = var_676 || var_682;
            }
            if (var_676) {
                // point=vertices[u]+d0/(d0-d1)*(vertices[v]-vertices[u])                         <L 65>
                var_687 = wp::extract(var_458, var_599);
                var_688 = wp::sub(var_672, var_675);
                var_689 = wp::div(var_672, var_688);
                var_690 = wp::extract(var_458, var_600);
                var_691 = wp::extract(var_458, var_599);
                var_692 = wp::sub(var_690, var_691);
                var_693 = wp::mul(var_689, var_692);
                var_694 = wp::add(var_687, var_693);
                // if inside(point,other) and inside(point,own):points[count]=point;count+=1       <L 66>
                var_696 = inside_0(var_694, var_459);
                var_695 = var_696;
                if (var_695) {
                    var_697 = inside_0(var_694, var_460);
                    var_695 = var_695 && var_697;
                }
                if (var_695) {
                    wp::assign_inplace(var_394, var_667, var_694);
                    var_699 = wp::add(var_667, var_698);
                }
                var_700 = wp::where(var_695, var_699, var_667);
            }
            var_701 = wp::where(var_676, var_700, var_667);
            var_702 = wp::where(var_676, var_694, var_668);
            // d0=plane_value(vertices[u],other[k]);d1=plane_value(vertices[v],other[k])          <L 63>
            var_704 = wp::extract(var_458, var_599);
            var_705 = wp::extract(var_459, var_703);
            var_706 = plane_value_0(var_704, var_705);
            var_707 = wp::extract(var_458, var_600);
            var_708 = wp::extract(var_459, var_703);
            var_709 = plane_value_0(var_707, var_708);
            // if (d0<wp.float64(0.) and d1>wp.float64(0.)) or (d1<wp.float64(0.) and d0>wp.float64(0.)):       <L 64>
            var_712 = 0.0;
            var_713 = (var_706 < var_712);
            var_711 = var_713;
            if (var_711) {
                var_714 = 0.0;
                var_715 = (var_709 > var_714);
                var_711 = var_711 && var_715;
            }
            var_710 = var_711;
            if (!var_710) {
                var_717 = 0.0;
                var_718 = (var_709 < var_717);
                var_716 = var_718;
                if (var_716) {
                    var_719 = 0.0;
                    var_720 = (var_706 > var_719);
                    var_716 = var_716 && var_720;
                }
                var_710 = var_710 || var_716;
            }
            if (var_710) {
                // point=vertices[u]+d0/(d0-d1)*(vertices[v]-vertices[u])                         <L 65>
                var_721 = wp::extract(var_458, var_599);
                var_722 = wp::sub(var_706, var_709);
                var_723 = wp::div(var_706, var_722);
                var_724 = wp::extract(var_458, var_600);
                var_725 = wp::extract(var_458, var_599);
                var_726 = wp::sub(var_724, var_725);
                var_727 = wp::mul(var_723, var_726);
                var_728 = wp::add(var_721, var_727);
                // if inside(point,other) and inside(point,own):points[count]=point;count+=1       <L 66>
                var_730 = inside_0(var_728, var_459);
                var_729 = var_730;
                if (var_729) {
                    var_731 = inside_0(var_728, var_460);
                    var_729 = var_729 && var_731;
                }
                if (var_729) {
                    wp::assign_inplace(var_394, var_701, var_728);
                    var_733 = wp::add(var_701, var_732);
                }
                var_734 = wp::where(var_729, var_733, var_701);
            }
            var_735 = wp::where(var_710, var_734, var_701);
            var_736 = wp::where(var_710, var_728, var_702);
            // for k in range(4):                                                                 <L 62>
            // d0=plane_value(vertices[u],other[k]);d1=plane_value(vertices[v],other[k])          <L 63>
            var_739 = wp::extract(var_458, var_599);
            var_740 = wp::extract(var_459, var_738);
            var_741 = plane_value_0(var_739, var_740);
            var_742 = wp::extract(var_458, var_737);
            var_743 = wp::extract(var_459, var_738);
            var_744 = plane_value_0(var_742, var_743);
            // if (d0<wp.float64(0.) and d1>wp.float64(0.)) or (d1<wp.float64(0.) and d0>wp.float64(0.)):       <L 64>
            var_747 = 0.0;
            var_748 = (var_741 < var_747);
            var_746 = var_748;
            if (var_746) {
                var_749 = 0.0;
                var_750 = (var_744 > var_749);
                var_746 = var_746 && var_750;
            }
            var_745 = var_746;
            if (!var_745) {
                var_752 = 0.0;
                var_753 = (var_744 < var_752);
                var_751 = var_753;
                if (var_751) {
                    var_754 = 0.0;
                    var_755 = (var_741 > var_754);
                    var_751 = var_751 && var_755;
                }
                var_745 = var_745 || var_751;
            }
            if (var_745) {
                // point=vertices[u]+d0/(d0-d1)*(vertices[v]-vertices[u])                         <L 65>
                var_756 = wp::extract(var_458, var_599);
                var_757 = wp::sub(var_741, var_744);
                var_758 = wp::div(var_741, var_757);
                var_759 = wp::extract(var_458, var_737);
                var_760 = wp::extract(var_458, var_599);
                var_761 = wp::sub(var_759, var_760);
                var_762 = wp::mul(var_758, var_761);
                var_763 = wp::add(var_756, var_762);
                // if inside(point,other) and inside(point,own):points[count]=point;count+=1       <L 66>
                var_765 = inside_0(var_763, var_459);
                var_764 = var_765;
                if (var_764) {
                    var_766 = inside_0(var_763, var_460);
                    var_764 = var_764 && var_766;
                }
                if (var_764) {
                    wp::assign_inplace(var_394, var_735, var_763);
                    var_768 = wp::add(var_735, var_767);
                }
                var_769 = wp::where(var_764, var_768, var_735);
            }
            var_770 = wp::where(var_745, var_769, var_735);
            var_771 = wp::where(var_745, var_763, var_736);
            // d0=plane_value(vertices[u],other[k]);d1=plane_value(vertices[v],other[k])          <L 63>
            var_773 = wp::extract(var_458, var_599);
            var_774 = wp::extract(var_459, var_772);
            var_775 = plane_value_0(var_773, var_774);
            var_776 = wp::extract(var_458, var_737);
            var_777 = wp::extract(var_459, var_772);
            var_778 = plane_value_0(var_776, var_777);
            // if (d0<wp.float64(0.) and d1>wp.float64(0.)) or (d1<wp.float64(0.) and d0>wp.float64(0.)):       <L 64>
            var_781 = 0.0;
            var_782 = (var_775 < var_781);
            var_780 = var_782;
            if (var_780) {
                var_783 = 0.0;
                var_784 = (var_778 > var_783);
                var_780 = var_780 && var_784;
            }
            var_779 = var_780;
            if (!var_779) {
                var_786 = 0.0;
                var_787 = (var_778 < var_786);
                var_785 = var_787;
                if (var_785) {
                    var_788 = 0.0;
                    var_789 = (var_775 > var_788);
                    var_785 = var_785 && var_789;
                }
                var_779 = var_779 || var_785;
            }
            if (var_779) {
                // point=vertices[u]+d0/(d0-d1)*(vertices[v]-vertices[u])                         <L 65>
                var_790 = wp::extract(var_458, var_599);
                var_791 = wp::sub(var_775, var_778);
                var_792 = wp::div(var_775, var_791);
                var_793 = wp::extract(var_458, var_737);
                var_794 = wp::extract(var_458, var_599);
                var_795 = wp::sub(var_793, var_794);
                var_796 = wp::mul(var_792, var_795);
                var_797 = wp::add(var_790, var_796);
                // if inside(point,other) and inside(point,own):points[count]=point;count+=1       <L 66>
                var_799 = inside_0(var_797, var_459);
                var_798 = var_799;
                if (var_798) {
                    var_800 = inside_0(var_797, var_460);
                    var_798 = var_798 && var_800;
                }
                if (var_798) {
                    wp::assign_inplace(var_394, var_770, var_797);
                    var_802 = wp::add(var_770, var_801);
                }
                var_803 = wp::where(var_798, var_802, var_770);
            }
            var_804 = wp::where(var_779, var_803, var_770);
            var_805 = wp::where(var_779, var_797, var_771);
            // d0=plane_value(vertices[u],other[k]);d1=plane_value(vertices[v],other[k])          <L 63>
            var_807 = wp::extract(var_458, var_599);
            var_808 = wp::extract(var_459, var_806);
            var_809 = plane_value_0(var_807, var_808);
            var_810 = wp::extract(var_458, var_737);
            var_811 = wp::extract(var_459, var_806);
            var_812 = plane_value_0(var_810, var_811);
            // if (d0<wp.float64(0.) and d1>wp.float64(0.)) or (d1<wp.float64(0.) and d0>wp.float64(0.)):       <L 64>
            var_815 = 0.0;
            var_816 = (var_809 < var_815);
            var_814 = var_816;
            if (var_814) {
                var_817 = 0.0;
                var_818 = (var_812 > var_817);
                var_814 = var_814 && var_818;
            }
            var_813 = var_814;
            if (!var_813) {
                var_820 = 0.0;
                var_821 = (var_812 < var_820);
                var_819 = var_821;
                if (var_819) {
                    var_822 = 0.0;
                    var_823 = (var_809 > var_822);
                    var_819 = var_819 && var_823;
                }
                var_813 = var_813 || var_819;
            }
            if (var_813) {
                // point=vertices[u]+d0/(d0-d1)*(vertices[v]-vertices[u])                         <L 65>
                var_824 = wp::extract(var_458, var_599);
                var_825 = wp::sub(var_809, var_812);
                var_826 = wp::div(var_809, var_825);
                var_827 = wp::extract(var_458, var_737);
                var_828 = wp::extract(var_458, var_599);
                var_829 = wp::sub(var_827, var_828);
                var_830 = wp::mul(var_826, var_829);
                var_831 = wp::add(var_824, var_830);
                // if inside(point,other) and inside(point,own):points[count]=point;count+=1       <L 66>
                var_833 = inside_0(var_831, var_459);
                var_832 = var_833;
                if (var_832) {
                    var_834 = inside_0(var_831, var_460);
                    var_832 = var_832 && var_834;
                }
                if (var_832) {
                    wp::assign_inplace(var_394, var_804, var_831);
                    var_836 = wp::add(var_804, var_835);
                }
                var_837 = wp::where(var_832, var_836, var_804);
            }
            var_838 = wp::where(var_813, var_837, var_804);
            var_839 = wp::where(var_813, var_831, var_805);
            // d0=plane_value(vertices[u],other[k]);d1=plane_value(vertices[v],other[k])          <L 63>
            var_841 = wp::extract(var_458, var_599);
            var_842 = wp::extract(var_459, var_840);
            var_843 = plane_value_0(var_841, var_842);
            var_844 = wp::extract(var_458, var_737);
            var_845 = wp::extract(var_459, var_840);
            var_846 = plane_value_0(var_844, var_845);
            // if (d0<wp.float64(0.) and d1>wp.float64(0.)) or (d1<wp.float64(0.) and d0>wp.float64(0.)):       <L 64>
            var_849 = 0.0;
            var_850 = (var_843 < var_849);
            var_848 = var_850;
            if (var_848) {
                var_851 = 0.0;
                var_852 = (var_846 > var_851);
                var_848 = var_848 && var_852;
            }
            var_847 = var_848;
            if (!var_847) {
                var_854 = 0.0;
                var_855 = (var_846 < var_854);
                var_853 = var_855;
                if (var_853) {
                    var_856 = 0.0;
                    var_857 = (var_843 > var_856);
                    var_853 = var_853 && var_857;
                }
                var_847 = var_847 || var_853;
            }
            if (var_847) {
                // point=vertices[u]+d0/(d0-d1)*(vertices[v]-vertices[u])                         <L 65>
                var_858 = wp::extract(var_458, var_599);
                var_859 = wp::sub(var_843, var_846);
                var_860 = wp::div(var_843, var_859);
                var_861 = wp::extract(var_458, var_737);
                var_862 = wp::extract(var_458, var_599);
                var_863 = wp::sub(var_861, var_862);
                var_864 = wp::mul(var_860, var_863);
                var_865 = wp::add(var_858, var_864);
                // if inside(point,other) and inside(point,own):points[count]=point;count+=1       <L 66>
                var_867 = inside_0(var_865, var_459);
                var_866 = var_867;
                if (var_866) {
                    var_868 = inside_0(var_865, var_460);
                    var_866 = var_866 && var_868;
                }
                if (var_866) {
                    wp::assign_inplace(var_394, var_838, var_865);
                    var_870 = wp::add(var_838, var_869);
                }
                var_871 = wp::where(var_866, var_870, var_838);
            }
            var_872 = wp::where(var_847, var_871, var_838);
            var_873 = wp::where(var_847, var_865, var_839);
            // for v in range(u):                                                                 <L 61>
            // for k in range(4):                                                                 <L 62>
            // d0=plane_value(vertices[u],other[k]);d1=plane_value(vertices[v],other[k])          <L 63>
            var_877 = wp::extract(var_458, var_874);
            var_878 = wp::extract(var_459, var_876);
            var_879 = plane_value_0(var_877, var_878);
            var_880 = wp::extract(var_458, var_875);
            var_881 = wp::extract(var_459, var_876);
            var_882 = plane_value_0(var_880, var_881);
            // if (d0<wp.float64(0.) and d1>wp.float64(0.)) or (d1<wp.float64(0.) and d0>wp.float64(0.)):       <L 64>
            var_885 = 0.0;
            var_886 = (var_879 < var_885);
            var_884 = var_886;
            if (var_884) {
                var_887 = 0.0;
                var_888 = (var_882 > var_887);
                var_884 = var_884 && var_888;
            }
            var_883 = var_884;
            if (!var_883) {
                var_890 = 0.0;
                var_891 = (var_882 < var_890);
                var_889 = var_891;
                if (var_889) {
                    var_892 = 0.0;
                    var_893 = (var_879 > var_892);
                    var_889 = var_889 && var_893;
                }
                var_883 = var_883 || var_889;
            }
            if (var_883) {
                // point=vertices[u]+d0/(d0-d1)*(vertices[v]-vertices[u])                         <L 65>
                var_894 = wp::extract(var_458, var_874);
                var_895 = wp::sub(var_879, var_882);
                var_896 = wp::div(var_879, var_895);
                var_897 = wp::extract(var_458, var_875);
                var_898 = wp::extract(var_458, var_874);
                var_899 = wp::sub(var_897, var_898);
                var_900 = wp::mul(var_896, var_899);
                var_901 = wp::add(var_894, var_900);
                // if inside(point,other) and inside(point,own):points[count]=point;count+=1       <L 66>
                var_903 = inside_0(var_901, var_459);
                var_902 = var_903;
                if (var_902) {
                    var_904 = inside_0(var_901, var_460);
                    var_902 = var_902 && var_904;
                }
                if (var_902) {
                    wp::assign_inplace(var_394, var_872, var_901);
                    var_906 = wp::add(var_872, var_905);
                }
                var_907 = wp::where(var_902, var_906, var_872);
            }
            var_908 = wp::where(var_883, var_907, var_872);
            var_909 = wp::where(var_883, var_901, var_873);
            // d0=plane_value(vertices[u],other[k]);d1=plane_value(vertices[v],other[k])          <L 63>
            var_911 = wp::extract(var_458, var_874);
            var_912 = wp::extract(var_459, var_910);
            var_913 = plane_value_0(var_911, var_912);
            var_914 = wp::extract(var_458, var_875);
            var_915 = wp::extract(var_459, var_910);
            var_916 = plane_value_0(var_914, var_915);
            // if (d0<wp.float64(0.) and d1>wp.float64(0.)) or (d1<wp.float64(0.) and d0>wp.float64(0.)):       <L 64>
            var_919 = 0.0;
            var_920 = (var_913 < var_919);
            var_918 = var_920;
            if (var_918) {
                var_921 = 0.0;
                var_922 = (var_916 > var_921);
                var_918 = var_918 && var_922;
            }
            var_917 = var_918;
            if (!var_917) {
                var_924 = 0.0;
                var_925 = (var_916 < var_924);
                var_923 = var_925;
                if (var_923) {
                    var_926 = 0.0;
                    var_927 = (var_913 > var_926);
                    var_923 = var_923 && var_927;
                }
                var_917 = var_917 || var_923;
            }
            if (var_917) {
                // point=vertices[u]+d0/(d0-d1)*(vertices[v]-vertices[u])                         <L 65>
                var_928 = wp::extract(var_458, var_874);
                var_929 = wp::sub(var_913, var_916);
                var_930 = wp::div(var_913, var_929);
                var_931 = wp::extract(var_458, var_875);
                var_932 = wp::extract(var_458, var_874);
                var_933 = wp::sub(var_931, var_932);
                var_934 = wp::mul(var_930, var_933);
                var_935 = wp::add(var_928, var_934);
                // if inside(point,other) and inside(point,own):points[count]=point;count+=1       <L 66>
                var_937 = inside_0(var_935, var_459);
                var_936 = var_937;
                if (var_936) {
                    var_938 = inside_0(var_935, var_460);
                    var_936 = var_936 && var_938;
                }
                if (var_936) {
                    wp::assign_inplace(var_394, var_908, var_935);
                    var_940 = wp::add(var_908, var_939);
                }
                var_941 = wp::where(var_936, var_940, var_908);
            }
            var_942 = wp::where(var_917, var_941, var_908);
            var_943 = wp::where(var_917, var_935, var_909);
            // d0=plane_value(vertices[u],other[k]);d1=plane_value(vertices[v],other[k])          <L 63>
            var_945 = wp::extract(var_458, var_874);
            var_946 = wp::extract(var_459, var_944);
            var_947 = plane_value_0(var_945, var_946);
            var_948 = wp::extract(var_458, var_875);
            var_949 = wp::extract(var_459, var_944);
            var_950 = plane_value_0(var_948, var_949);
            // if (d0<wp.float64(0.) and d1>wp.float64(0.)) or (d1<wp.float64(0.) and d0>wp.float64(0.)):       <L 64>
            var_953 = 0.0;
            var_954 = (var_947 < var_953);
            var_952 = var_954;
            if (var_952) {
                var_955 = 0.0;
                var_956 = (var_950 > var_955);
                var_952 = var_952 && var_956;
            }
            var_951 = var_952;
            if (!var_951) {
                var_958 = 0.0;
                var_959 = (var_950 < var_958);
                var_957 = var_959;
                if (var_957) {
                    var_960 = 0.0;
                    var_961 = (var_947 > var_960);
                    var_957 = var_957 && var_961;
                }
                var_951 = var_951 || var_957;
            }
            if (var_951) {
                // point=vertices[u]+d0/(d0-d1)*(vertices[v]-vertices[u])                         <L 65>
                var_962 = wp::extract(var_458, var_874);
                var_963 = wp::sub(var_947, var_950);
                var_964 = wp::div(var_947, var_963);
                var_965 = wp::extract(var_458, var_875);
                var_966 = wp::extract(var_458, var_874);
                var_967 = wp::sub(var_965, var_966);
                var_968 = wp::mul(var_964, var_967);
                var_969 = wp::add(var_962, var_968);
                // if inside(point,other) and inside(point,own):points[count]=point;count+=1       <L 66>
                var_971 = inside_0(var_969, var_459);
                var_970 = var_971;
                if (var_970) {
                    var_972 = inside_0(var_969, var_460);
                    var_970 = var_970 && var_972;
                }
                if (var_970) {
                    wp::assign_inplace(var_394, var_942, var_969);
                    var_974 = wp::add(var_942, var_973);
                }
                var_975 = wp::where(var_970, var_974, var_942);
            }
            var_976 = wp::where(var_951, var_975, var_942);
            var_977 = wp::where(var_951, var_969, var_943);
            // d0=plane_value(vertices[u],other[k]);d1=plane_value(vertices[v],other[k])          <L 63>
            var_979 = wp::extract(var_458, var_874);
            var_980 = wp::extract(var_459, var_978);
            var_981 = plane_value_0(var_979, var_980);
            var_982 = wp::extract(var_458, var_875);
            var_983 = wp::extract(var_459, var_978);
            var_984 = plane_value_0(var_982, var_983);
            // if (d0<wp.float64(0.) and d1>wp.float64(0.)) or (d1<wp.float64(0.) and d0>wp.float64(0.)):       <L 64>
            var_987 = 0.0;
            var_988 = (var_981 < var_987);
            var_986 = var_988;
            if (var_986) {
                var_989 = 0.0;
                var_990 = (var_984 > var_989);
                var_986 = var_986 && var_990;
            }
            var_985 = var_986;
            if (!var_985) {
                var_992 = 0.0;
                var_993 = (var_984 < var_992);
                var_991 = var_993;
                if (var_991) {
                    var_994 = 0.0;
                    var_995 = (var_981 > var_994);
                    var_991 = var_991 && var_995;
                }
                var_985 = var_985 || var_991;
            }
            if (var_985) {
                // point=vertices[u]+d0/(d0-d1)*(vertices[v]-vertices[u])                         <L 65>
                var_996 = wp::extract(var_458, var_874);
                var_997 = wp::sub(var_981, var_984);
                var_998 = wp::div(var_981, var_997);
                var_999 = wp::extract(var_458, var_875);
                var_1000 = wp::extract(var_458, var_874);
                var_1001 = wp::sub(var_999, var_1000);
                var_1002 = wp::mul(var_998, var_1001);
                var_1003 = wp::add(var_996, var_1002);
                // if inside(point,other) and inside(point,own):points[count]=point;count+=1       <L 66>
                var_1005 = inside_0(var_1003, var_459);
                var_1004 = var_1005;
                if (var_1004) {
                    var_1006 = inside_0(var_1003, var_460);
                    var_1004 = var_1004 && var_1006;
                }
                if (var_1004) {
                    wp::assign_inplace(var_394, var_976, var_1003);
                    var_1008 = wp::add(var_976, var_1007);
                }
                var_1009 = wp::where(var_1004, var_1008, var_976);
            }
            var_1010 = wp::where(var_985, var_1009, var_976);
            var_1011 = wp::where(var_985, var_1003, var_977);
            // for k in range(4):                                                                 <L 62>
            // d0=plane_value(vertices[u],other[k]);d1=plane_value(vertices[v],other[k])          <L 63>
            var_1014 = wp::extract(var_458, var_874);
            var_1015 = wp::extract(var_459, var_1013);
            var_1016 = plane_value_0(var_1014, var_1015);
            var_1017 = wp::extract(var_458, var_1012);
            var_1018 = wp::extract(var_459, var_1013);
            var_1019 = plane_value_0(var_1017, var_1018);
            // if (d0<wp.float64(0.) and d1>wp.float64(0.)) or (d1<wp.float64(0.) and d0>wp.float64(0.)):       <L 64>
            var_1022 = 0.0;
            var_1023 = (var_1016 < var_1022);
            var_1021 = var_1023;
            if (var_1021) {
                var_1024 = 0.0;
                var_1025 = (var_1019 > var_1024);
                var_1021 = var_1021 && var_1025;
            }
            var_1020 = var_1021;
            if (!var_1020) {
                var_1027 = 0.0;
                var_1028 = (var_1019 < var_1027);
                var_1026 = var_1028;
                if (var_1026) {
                    var_1029 = 0.0;
                    var_1030 = (var_1016 > var_1029);
                    var_1026 = var_1026 && var_1030;
                }
                var_1020 = var_1020 || var_1026;
            }
            if (var_1020) {
                // point=vertices[u]+d0/(d0-d1)*(vertices[v]-vertices[u])                         <L 65>
                var_1031 = wp::extract(var_458, var_874);
                var_1032 = wp::sub(var_1016, var_1019);
                var_1033 = wp::div(var_1016, var_1032);
                var_1034 = wp::extract(var_458, var_1012);
                var_1035 = wp::extract(var_458, var_874);
                var_1036 = wp::sub(var_1034, var_1035);
                var_1037 = wp::mul(var_1033, var_1036);
                var_1038 = wp::add(var_1031, var_1037);
                // if inside(point,other) and inside(point,own):points[count]=point;count+=1       <L 66>
                var_1040 = inside_0(var_1038, var_459);
                var_1039 = var_1040;
                if (var_1039) {
                    var_1041 = inside_0(var_1038, var_460);
                    var_1039 = var_1039 && var_1041;
                }
                if (var_1039) {
                    wp::assign_inplace(var_394, var_1010, var_1038);
                    var_1043 = wp::add(var_1010, var_1042);
                }
                var_1044 = wp::where(var_1039, var_1043, var_1010);
            }
            var_1045 = wp::where(var_1020, var_1044, var_1010);
            var_1046 = wp::where(var_1020, var_1038, var_1011);
            // d0=plane_value(vertices[u],other[k]);d1=plane_value(vertices[v],other[k])          <L 63>
            var_1048 = wp::extract(var_458, var_874);
            var_1049 = wp::extract(var_459, var_1047);
            var_1050 = plane_value_0(var_1048, var_1049);
            var_1051 = wp::extract(var_458, var_1012);
            var_1052 = wp::extract(var_459, var_1047);
            var_1053 = plane_value_0(var_1051, var_1052);
            // if (d0<wp.float64(0.) and d1>wp.float64(0.)) or (d1<wp.float64(0.) and d0>wp.float64(0.)):       <L 64>
            var_1056 = 0.0;
            var_1057 = (var_1050 < var_1056);
            var_1055 = var_1057;
            if (var_1055) {
                var_1058 = 0.0;
                var_1059 = (var_1053 > var_1058);
                var_1055 = var_1055 && var_1059;
            }
            var_1054 = var_1055;
            if (!var_1054) {
                var_1061 = 0.0;
                var_1062 = (var_1053 < var_1061);
                var_1060 = var_1062;
                if (var_1060) {
                    var_1063 = 0.0;
                    var_1064 = (var_1050 > var_1063);
                    var_1060 = var_1060 && var_1064;
                }
                var_1054 = var_1054 || var_1060;
            }
            if (var_1054) {
                // point=vertices[u]+d0/(d0-d1)*(vertices[v]-vertices[u])                         <L 65>
                var_1065 = wp::extract(var_458, var_874);
                var_1066 = wp::sub(var_1050, var_1053);
                var_1067 = wp::div(var_1050, var_1066);
                var_1068 = wp::extract(var_458, var_1012);
                var_1069 = wp::extract(var_458, var_874);
                var_1070 = wp::sub(var_1068, var_1069);
                var_1071 = wp::mul(var_1067, var_1070);
                var_1072 = wp::add(var_1065, var_1071);
                // if inside(point,other) and inside(point,own):points[count]=point;count+=1       <L 66>
                var_1074 = inside_0(var_1072, var_459);
                var_1073 = var_1074;
                if (var_1073) {
                    var_1075 = inside_0(var_1072, var_460);
                    var_1073 = var_1073 && var_1075;
                }
                if (var_1073) {
                    wp::assign_inplace(var_394, var_1045, var_1072);
                    var_1077 = wp::add(var_1045, var_1076);
                }
                var_1078 = wp::where(var_1073, var_1077, var_1045);
            }
            var_1079 = wp::where(var_1054, var_1078, var_1045);
            var_1080 = wp::where(var_1054, var_1072, var_1046);
            // d0=plane_value(vertices[u],other[k]);d1=plane_value(vertices[v],other[k])          <L 63>
            var_1082 = wp::extract(var_458, var_874);
            var_1083 = wp::extract(var_459, var_1081);
            var_1084 = plane_value_0(var_1082, var_1083);
            var_1085 = wp::extract(var_458, var_1012);
            var_1086 = wp::extract(var_459, var_1081);
            var_1087 = plane_value_0(var_1085, var_1086);
            // if (d0<wp.float64(0.) and d1>wp.float64(0.)) or (d1<wp.float64(0.) and d0>wp.float64(0.)):       <L 64>
            var_1090 = 0.0;
            var_1091 = (var_1084 < var_1090);
            var_1089 = var_1091;
            if (var_1089) {
                var_1092 = 0.0;
                var_1093 = (var_1087 > var_1092);
                var_1089 = var_1089 && var_1093;
            }
            var_1088 = var_1089;
            if (!var_1088) {
                var_1095 = 0.0;
                var_1096 = (var_1087 < var_1095);
                var_1094 = var_1096;
                if (var_1094) {
                    var_1097 = 0.0;
                    var_1098 = (var_1084 > var_1097);
                    var_1094 = var_1094 && var_1098;
                }
                var_1088 = var_1088 || var_1094;
            }
            if (var_1088) {
                // point=vertices[u]+d0/(d0-d1)*(vertices[v]-vertices[u])                         <L 65>
                var_1099 = wp::extract(var_458, var_874);
                var_1100 = wp::sub(var_1084, var_1087);
                var_1101 = wp::div(var_1084, var_1100);
                var_1102 = wp::extract(var_458, var_1012);
                var_1103 = wp::extract(var_458, var_874);
                var_1104 = wp::sub(var_1102, var_1103);
                var_1105 = wp::mul(var_1101, var_1104);
                var_1106 = wp::add(var_1099, var_1105);
                // if inside(point,other) and inside(point,own):points[count]=point;count+=1       <L 66>
                var_1108 = inside_0(var_1106, var_459);
                var_1107 = var_1108;
                if (var_1107) {
                    var_1109 = inside_0(var_1106, var_460);
                    var_1107 = var_1107 && var_1109;
                }
                if (var_1107) {
                    wp::assign_inplace(var_394, var_1079, var_1106);
                    var_1111 = wp::add(var_1079, var_1110);
                }
                var_1112 = wp::where(var_1107, var_1111, var_1079);
            }
            var_1113 = wp::where(var_1088, var_1112, var_1079);
            var_1114 = wp::where(var_1088, var_1106, var_1080);
            // d0=plane_value(vertices[u],other[k]);d1=plane_value(vertices[v],other[k])          <L 63>
            var_1116 = wp::extract(var_458, var_874);
            var_1117 = wp::extract(var_459, var_1115);
            var_1118 = plane_value_0(var_1116, var_1117);
            var_1119 = wp::extract(var_458, var_1012);
            var_1120 = wp::extract(var_459, var_1115);
            var_1121 = plane_value_0(var_1119, var_1120);
            // if (d0<wp.float64(0.) and d1>wp.float64(0.)) or (d1<wp.float64(0.) and d0>wp.float64(0.)):       <L 64>
            var_1124 = 0.0;
            var_1125 = (var_1118 < var_1124);
            var_1123 = var_1125;
            if (var_1123) {
                var_1126 = 0.0;
                var_1127 = (var_1121 > var_1126);
                var_1123 = var_1123 && var_1127;
            }
            var_1122 = var_1123;
            if (!var_1122) {
                var_1129 = 0.0;
                var_1130 = (var_1121 < var_1129);
                var_1128 = var_1130;
                if (var_1128) {
                    var_1131 = 0.0;
                    var_1132 = (var_1118 > var_1131);
                    var_1128 = var_1128 && var_1132;
                }
                var_1122 = var_1122 || var_1128;
            }
            if (var_1122) {
                // point=vertices[u]+d0/(d0-d1)*(vertices[v]-vertices[u])                         <L 65>
                var_1133 = wp::extract(var_458, var_874);
                var_1134 = wp::sub(var_1118, var_1121);
                var_1135 = wp::div(var_1118, var_1134);
                var_1136 = wp::extract(var_458, var_1012);
                var_1137 = wp::extract(var_458, var_874);
                var_1138 = wp::sub(var_1136, var_1137);
                var_1139 = wp::mul(var_1135, var_1138);
                var_1140 = wp::add(var_1133, var_1139);
                // if inside(point,other) and inside(point,own):points[count]=point;count+=1       <L 66>
                var_1142 = inside_0(var_1140, var_459);
                var_1141 = var_1142;
                if (var_1141) {
                    var_1143 = inside_0(var_1140, var_460);
                    var_1141 = var_1141 && var_1143;
                }
                if (var_1141) {
                    wp::assign_inplace(var_394, var_1113, var_1140);
                    var_1145 = wp::add(var_1113, var_1144);
                }
                var_1146 = wp::where(var_1141, var_1145, var_1113);
            }
            var_1147 = wp::where(var_1122, var_1146, var_1113);
            var_1148 = wp::where(var_1122, var_1140, var_1114);
            // for k in range(4):                                                                 <L 62>
            // d0=plane_value(vertices[u],other[k]);d1=plane_value(vertices[v],other[k])          <L 63>
            var_1151 = wp::extract(var_458, var_874);
            var_1152 = wp::extract(var_459, var_1150);
            var_1153 = plane_value_0(var_1151, var_1152);
            var_1154 = wp::extract(var_458, var_1149);
            var_1155 = wp::extract(var_459, var_1150);
            var_1156 = plane_value_0(var_1154, var_1155);
            // if (d0<wp.float64(0.) and d1>wp.float64(0.)) or (d1<wp.float64(0.) and d0>wp.float64(0.)):       <L 64>
            var_1159 = 0.0;
            var_1160 = (var_1153 < var_1159);
            var_1158 = var_1160;
            if (var_1158) {
                var_1161 = 0.0;
                var_1162 = (var_1156 > var_1161);
                var_1158 = var_1158 && var_1162;
            }
            var_1157 = var_1158;
            if (!var_1157) {
                var_1164 = 0.0;
                var_1165 = (var_1156 < var_1164);
                var_1163 = var_1165;
                if (var_1163) {
                    var_1166 = 0.0;
                    var_1167 = (var_1153 > var_1166);
                    var_1163 = var_1163 && var_1167;
                }
                var_1157 = var_1157 || var_1163;
            }
            if (var_1157) {
                // point=vertices[u]+d0/(d0-d1)*(vertices[v]-vertices[u])                         <L 65>
                var_1168 = wp::extract(var_458, var_874);
                var_1169 = wp::sub(var_1153, var_1156);
                var_1170 = wp::div(var_1153, var_1169);
                var_1171 = wp::extract(var_458, var_1149);
                var_1172 = wp::extract(var_458, var_874);
                var_1173 = wp::sub(var_1171, var_1172);
                var_1174 = wp::mul(var_1170, var_1173);
                var_1175 = wp::add(var_1168, var_1174);
                // if inside(point,other) and inside(point,own):points[count]=point;count+=1       <L 66>
                var_1177 = inside_0(var_1175, var_459);
                var_1176 = var_1177;
                if (var_1176) {
                    var_1178 = inside_0(var_1175, var_460);
                    var_1176 = var_1176 && var_1178;
                }
                if (var_1176) {
                    wp::assign_inplace(var_394, var_1147, var_1175);
                    var_1180 = wp::add(var_1147, var_1179);
                }
                var_1181 = wp::where(var_1176, var_1180, var_1147);
            }
            var_1182 = wp::where(var_1157, var_1181, var_1147);
            var_1183 = wp::where(var_1157, var_1175, var_1148);
            // d0=plane_value(vertices[u],other[k]);d1=plane_value(vertices[v],other[k])          <L 63>
            var_1185 = wp::extract(var_458, var_874);
            var_1186 = wp::extract(var_459, var_1184);
            var_1187 = plane_value_0(var_1185, var_1186);
            var_1188 = wp::extract(var_458, var_1149);
            var_1189 = wp::extract(var_459, var_1184);
            var_1190 = plane_value_0(var_1188, var_1189);
            // if (d0<wp.float64(0.) and d1>wp.float64(0.)) or (d1<wp.float64(0.) and d0>wp.float64(0.)):       <L 64>
            var_1193 = 0.0;
            var_1194 = (var_1187 < var_1193);
            var_1192 = var_1194;
            if (var_1192) {
                var_1195 = 0.0;
                var_1196 = (var_1190 > var_1195);
                var_1192 = var_1192 && var_1196;
            }
            var_1191 = var_1192;
            if (!var_1191) {
                var_1198 = 0.0;
                var_1199 = (var_1190 < var_1198);
                var_1197 = var_1199;
                if (var_1197) {
                    var_1200 = 0.0;
                    var_1201 = (var_1187 > var_1200);
                    var_1197 = var_1197 && var_1201;
                }
                var_1191 = var_1191 || var_1197;
            }
            if (var_1191) {
                // point=vertices[u]+d0/(d0-d1)*(vertices[v]-vertices[u])                         <L 65>
                var_1202 = wp::extract(var_458, var_874);
                var_1203 = wp::sub(var_1187, var_1190);
                var_1204 = wp::div(var_1187, var_1203);
                var_1205 = wp::extract(var_458, var_1149);
                var_1206 = wp::extract(var_458, var_874);
                var_1207 = wp::sub(var_1205, var_1206);
                var_1208 = wp::mul(var_1204, var_1207);
                var_1209 = wp::add(var_1202, var_1208);
                // if inside(point,other) and inside(point,own):points[count]=point;count+=1       <L 66>
                var_1211 = inside_0(var_1209, var_459);
                var_1210 = var_1211;
                if (var_1210) {
                    var_1212 = inside_0(var_1209, var_460);
                    var_1210 = var_1210 && var_1212;
                }
                if (var_1210) {
                    wp::assign_inplace(var_394, var_1182, var_1209);
                    var_1214 = wp::add(var_1182, var_1213);
                }
                var_1215 = wp::where(var_1210, var_1214, var_1182);
            }
            var_1216 = wp::where(var_1191, var_1215, var_1182);
            var_1217 = wp::where(var_1191, var_1209, var_1183);
            // d0=plane_value(vertices[u],other[k]);d1=plane_value(vertices[v],other[k])          <L 63>
            var_1219 = wp::extract(var_458, var_874);
            var_1220 = wp::extract(var_459, var_1218);
            var_1221 = plane_value_0(var_1219, var_1220);
            var_1222 = wp::extract(var_458, var_1149);
            var_1223 = wp::extract(var_459, var_1218);
            var_1224 = plane_value_0(var_1222, var_1223);
            // if (d0<wp.float64(0.) and d1>wp.float64(0.)) or (d1<wp.float64(0.) and d0>wp.float64(0.)):       <L 64>
            var_1227 = 0.0;
            var_1228 = (var_1221 < var_1227);
            var_1226 = var_1228;
            if (var_1226) {
                var_1229 = 0.0;
                var_1230 = (var_1224 > var_1229);
                var_1226 = var_1226 && var_1230;
            }
            var_1225 = var_1226;
            if (!var_1225) {
                var_1232 = 0.0;
                var_1233 = (var_1224 < var_1232);
                var_1231 = var_1233;
                if (var_1231) {
                    var_1234 = 0.0;
                    var_1235 = (var_1221 > var_1234);
                    var_1231 = var_1231 && var_1235;
                }
                var_1225 = var_1225 || var_1231;
            }
            if (var_1225) {
                // point=vertices[u]+d0/(d0-d1)*(vertices[v]-vertices[u])                         <L 65>
                var_1236 = wp::extract(var_458, var_874);
                var_1237 = wp::sub(var_1221, var_1224);
                var_1238 = wp::div(var_1221, var_1237);
                var_1239 = wp::extract(var_458, var_1149);
                var_1240 = wp::extract(var_458, var_874);
                var_1241 = wp::sub(var_1239, var_1240);
                var_1242 = wp::mul(var_1238, var_1241);
                var_1243 = wp::add(var_1236, var_1242);
                // if inside(point,other) and inside(point,own):points[count]=point;count+=1       <L 66>
                var_1245 = inside_0(var_1243, var_459);
                var_1244 = var_1245;
                if (var_1244) {
                    var_1246 = inside_0(var_1243, var_460);
                    var_1244 = var_1244 && var_1246;
                }
                if (var_1244) {
                    wp::assign_inplace(var_394, var_1216, var_1243);
                    var_1248 = wp::add(var_1216, var_1247);
                }
                var_1249 = wp::where(var_1244, var_1248, var_1216);
            }
            var_1250 = wp::where(var_1225, var_1249, var_1216);
            var_1251 = wp::where(var_1225, var_1243, var_1217);
            // d0=plane_value(vertices[u],other[k]);d1=plane_value(vertices[v],other[k])          <L 63>
            var_1253 = wp::extract(var_458, var_874);
            var_1254 = wp::extract(var_459, var_1252);
            var_1255 = plane_value_0(var_1253, var_1254);
            var_1256 = wp::extract(var_458, var_1149);
            var_1257 = wp::extract(var_459, var_1252);
            var_1258 = plane_value_0(var_1256, var_1257);
            // if (d0<wp.float64(0.) and d1>wp.float64(0.)) or (d1<wp.float64(0.) and d0>wp.float64(0.)):       <L 64>
            var_1261 = 0.0;
            var_1262 = (var_1255 < var_1261);
            var_1260 = var_1262;
            if (var_1260) {
                var_1263 = 0.0;
                var_1264 = (var_1258 > var_1263);
                var_1260 = var_1260 && var_1264;
            }
            var_1259 = var_1260;
            if (!var_1259) {
                var_1266 = 0.0;
                var_1267 = (var_1258 < var_1266);
                var_1265 = var_1267;
                if (var_1265) {
                    var_1268 = 0.0;
                    var_1269 = (var_1255 > var_1268);
                    var_1265 = var_1265 && var_1269;
                }
                var_1259 = var_1259 || var_1265;
            }
            if (var_1259) {
                // point=vertices[u]+d0/(d0-d1)*(vertices[v]-vertices[u])                         <L 65>
                var_1270 = wp::extract(var_458, var_874);
                var_1271 = wp::sub(var_1255, var_1258);
                var_1272 = wp::div(var_1255, var_1271);
                var_1273 = wp::extract(var_458, var_1149);
                var_1274 = wp::extract(var_458, var_874);
                var_1275 = wp::sub(var_1273, var_1274);
                var_1276 = wp::mul(var_1272, var_1275);
                var_1277 = wp::add(var_1270, var_1276);
                // if inside(point,other) and inside(point,own):points[count]=point;count+=1       <L 66>
                var_1279 = inside_0(var_1277, var_459);
                var_1278 = var_1279;
                if (var_1278) {
                    var_1280 = inside_0(var_1277, var_460);
                    var_1278 = var_1278 && var_1280;
                }
                if (var_1278) {
                    wp::assign_inplace(var_394, var_1250, var_1277);
                    var_1282 = wp::add(var_1250, var_1281);
                }
                var_1283 = wp::where(var_1278, var_1282, var_1250);
            }
            var_1284 = wp::where(var_1259, var_1283, var_1250);
            var_1285 = wp::where(var_1259, var_1277, var_1251);
            // vertices=a;other=pb;own=pa                                                         <L 58>
            var_1287 = wp::copy(var_12);
            var_1288 = wp::copy(var_391);
            var_1289 = wp::copy(var_134);
            // if side==1:vertices=b;other=pa;own=pb                                              <L 59>
            var_1291 = (var_1286 == var_1290);
            if (var_1291) {
                var_1292 = wp::copy(var_15);
                var_1293 = wp::copy(var_134);
                var_1294 = wp::copy(var_391);
            }
            var_1295 = wp::where(var_1291, var_1292, var_1287);
            var_1296 = wp::where(var_1291, var_1293, var_1288);
            var_1297 = wp::where(var_1291, var_1294, var_1289);
            // for u in range(4):                                                                 <L 60>
            // for v in range(u):                                                                 <L 61>
            // for k in range(4):                                                                 <L 62>
            // d0=plane_value(vertices[u],other[k]);d1=plane_value(vertices[v],other[k])          <L 63>
            var_1302 = wp::extract(var_1295, var_1299);
            var_1303 = wp::extract(var_1296, var_1301);
            var_1304 = plane_value_0(var_1302, var_1303);
            var_1305 = wp::extract(var_1295, var_1300);
            var_1306 = wp::extract(var_1296, var_1301);
            var_1307 = plane_value_0(var_1305, var_1306);
            // if (d0<wp.float64(0.) and d1>wp.float64(0.)) or (d1<wp.float64(0.) and d0>wp.float64(0.)):       <L 64>
            var_1310 = 0.0;
            var_1311 = (var_1304 < var_1310);
            var_1309 = var_1311;
            if (var_1309) {
                var_1312 = 0.0;
                var_1313 = (var_1307 > var_1312);
                var_1309 = var_1309 && var_1313;
            }
            var_1308 = var_1309;
            if (!var_1308) {
                var_1315 = 0.0;
                var_1316 = (var_1307 < var_1315);
                var_1314 = var_1316;
                if (var_1314) {
                    var_1317 = 0.0;
                    var_1318 = (var_1304 > var_1317);
                    var_1314 = var_1314 && var_1318;
                }
                var_1308 = var_1308 || var_1314;
            }
            if (var_1308) {
                // point=vertices[u]+d0/(d0-d1)*(vertices[v]-vertices[u])                         <L 65>
                var_1319 = wp::extract(var_1295, var_1299);
                var_1320 = wp::sub(var_1304, var_1307);
                var_1321 = wp::div(var_1304, var_1320);
                var_1322 = wp::extract(var_1295, var_1300);
                var_1323 = wp::extract(var_1295, var_1299);
                var_1324 = wp::sub(var_1322, var_1323);
                var_1325 = wp::mul(var_1321, var_1324);
                var_1326 = wp::add(var_1319, var_1325);
                // if inside(point,other) and inside(point,own):points[count]=point;count+=1       <L 66>
                var_1328 = inside_0(var_1326, var_1296);
                var_1327 = var_1328;
                if (var_1327) {
                    var_1329 = inside_0(var_1326, var_1297);
                    var_1327 = var_1327 && var_1329;
                }
                if (var_1327) {
                    wp::assign_inplace(var_394, var_1284, var_1326);
                    var_1331 = wp::add(var_1284, var_1330);
                }
                var_1332 = wp::where(var_1327, var_1331, var_1284);
            }
            var_1333 = wp::where(var_1308, var_1332, var_1284);
            var_1334 = wp::where(var_1308, var_1326, var_1285);
            // d0=plane_value(vertices[u],other[k]);d1=plane_value(vertices[v],other[k])          <L 63>
            var_1336 = wp::extract(var_1295, var_1299);
            var_1337 = wp::extract(var_1296, var_1335);
            var_1338 = plane_value_0(var_1336, var_1337);
            var_1339 = wp::extract(var_1295, var_1300);
            var_1340 = wp::extract(var_1296, var_1335);
            var_1341 = plane_value_0(var_1339, var_1340);
            // if (d0<wp.float64(0.) and d1>wp.float64(0.)) or (d1<wp.float64(0.) and d0>wp.float64(0.)):       <L 64>
            var_1344 = 0.0;
            var_1345 = (var_1338 < var_1344);
            var_1343 = var_1345;
            if (var_1343) {
                var_1346 = 0.0;
                var_1347 = (var_1341 > var_1346);
                var_1343 = var_1343 && var_1347;
            }
            var_1342 = var_1343;
            if (!var_1342) {
                var_1349 = 0.0;
                var_1350 = (var_1341 < var_1349);
                var_1348 = var_1350;
                if (var_1348) {
                    var_1351 = 0.0;
                    var_1352 = (var_1338 > var_1351);
                    var_1348 = var_1348 && var_1352;
                }
                var_1342 = var_1342 || var_1348;
            }
            if (var_1342) {
                // point=vertices[u]+d0/(d0-d1)*(vertices[v]-vertices[u])                         <L 65>
                var_1353 = wp::extract(var_1295, var_1299);
                var_1354 = wp::sub(var_1338, var_1341);
                var_1355 = wp::div(var_1338, var_1354);
                var_1356 = wp::extract(var_1295, var_1300);
                var_1357 = wp::extract(var_1295, var_1299);
                var_1358 = wp::sub(var_1356, var_1357);
                var_1359 = wp::mul(var_1355, var_1358);
                var_1360 = wp::add(var_1353, var_1359);
                // if inside(point,other) and inside(point,own):points[count]=point;count+=1       <L 66>
                var_1362 = inside_0(var_1360, var_1296);
                var_1361 = var_1362;
                if (var_1361) {
                    var_1363 = inside_0(var_1360, var_1297);
                    var_1361 = var_1361 && var_1363;
                }
                if (var_1361) {
                    wp::assign_inplace(var_394, var_1333, var_1360);
                    var_1365 = wp::add(var_1333, var_1364);
                }
                var_1366 = wp::where(var_1361, var_1365, var_1333);
            }
            var_1367 = wp::where(var_1342, var_1366, var_1333);
            var_1368 = wp::where(var_1342, var_1360, var_1334);
            // d0=plane_value(vertices[u],other[k]);d1=plane_value(vertices[v],other[k])          <L 63>
            var_1370 = wp::extract(var_1295, var_1299);
            var_1371 = wp::extract(var_1296, var_1369);
            var_1372 = plane_value_0(var_1370, var_1371);
            var_1373 = wp::extract(var_1295, var_1300);
            var_1374 = wp::extract(var_1296, var_1369);
            var_1375 = plane_value_0(var_1373, var_1374);
            // if (d0<wp.float64(0.) and d1>wp.float64(0.)) or (d1<wp.float64(0.) and d0>wp.float64(0.)):       <L 64>
            var_1378 = 0.0;
            var_1379 = (var_1372 < var_1378);
            var_1377 = var_1379;
            if (var_1377) {
                var_1380 = 0.0;
                var_1381 = (var_1375 > var_1380);
                var_1377 = var_1377 && var_1381;
            }
            var_1376 = var_1377;
            if (!var_1376) {
                var_1383 = 0.0;
                var_1384 = (var_1375 < var_1383);
                var_1382 = var_1384;
                if (var_1382) {
                    var_1385 = 0.0;
                    var_1386 = (var_1372 > var_1385);
                    var_1382 = var_1382 && var_1386;
                }
                var_1376 = var_1376 || var_1382;
            }
            if (var_1376) {
                // point=vertices[u]+d0/(d0-d1)*(vertices[v]-vertices[u])                         <L 65>
                var_1387 = wp::extract(var_1295, var_1299);
                var_1388 = wp::sub(var_1372, var_1375);
                var_1389 = wp::div(var_1372, var_1388);
                var_1390 = wp::extract(var_1295, var_1300);
                var_1391 = wp::extract(var_1295, var_1299);
                var_1392 = wp::sub(var_1390, var_1391);
                var_1393 = wp::mul(var_1389, var_1392);
                var_1394 = wp::add(var_1387, var_1393);
                // if inside(point,other) and inside(point,own):points[count]=point;count+=1       <L 66>
                var_1396 = inside_0(var_1394, var_1296);
                var_1395 = var_1396;
                if (var_1395) {
                    var_1397 = inside_0(var_1394, var_1297);
                    var_1395 = var_1395 && var_1397;
                }
                if (var_1395) {
                    wp::assign_inplace(var_394, var_1367, var_1394);
                    var_1399 = wp::add(var_1367, var_1398);
                }
                var_1400 = wp::where(var_1395, var_1399, var_1367);
            }
            var_1401 = wp::where(var_1376, var_1400, var_1367);
            var_1402 = wp::where(var_1376, var_1394, var_1368);
            // d0=plane_value(vertices[u],other[k]);d1=plane_value(vertices[v],other[k])          <L 63>
            var_1404 = wp::extract(var_1295, var_1299);
            var_1405 = wp::extract(var_1296, var_1403);
            var_1406 = plane_value_0(var_1404, var_1405);
            var_1407 = wp::extract(var_1295, var_1300);
            var_1408 = wp::extract(var_1296, var_1403);
            var_1409 = plane_value_0(var_1407, var_1408);
            // if (d0<wp.float64(0.) and d1>wp.float64(0.)) or (d1<wp.float64(0.) and d0>wp.float64(0.)):       <L 64>
            var_1412 = 0.0;
            var_1413 = (var_1406 < var_1412);
            var_1411 = var_1413;
            if (var_1411) {
                var_1414 = 0.0;
                var_1415 = (var_1409 > var_1414);
                var_1411 = var_1411 && var_1415;
            }
            var_1410 = var_1411;
            if (!var_1410) {
                var_1417 = 0.0;
                var_1418 = (var_1409 < var_1417);
                var_1416 = var_1418;
                if (var_1416) {
                    var_1419 = 0.0;
                    var_1420 = (var_1406 > var_1419);
                    var_1416 = var_1416 && var_1420;
                }
                var_1410 = var_1410 || var_1416;
            }
            if (var_1410) {
                // point=vertices[u]+d0/(d0-d1)*(vertices[v]-vertices[u])                         <L 65>
                var_1421 = wp::extract(var_1295, var_1299);
                var_1422 = wp::sub(var_1406, var_1409);
                var_1423 = wp::div(var_1406, var_1422);
                var_1424 = wp::extract(var_1295, var_1300);
                var_1425 = wp::extract(var_1295, var_1299);
                var_1426 = wp::sub(var_1424, var_1425);
                var_1427 = wp::mul(var_1423, var_1426);
                var_1428 = wp::add(var_1421, var_1427);
                // if inside(point,other) and inside(point,own):points[count]=point;count+=1       <L 66>
                var_1430 = inside_0(var_1428, var_1296);
                var_1429 = var_1430;
                if (var_1429) {
                    var_1431 = inside_0(var_1428, var_1297);
                    var_1429 = var_1429 && var_1431;
                }
                if (var_1429) {
                    wp::assign_inplace(var_394, var_1401, var_1428);
                    var_1433 = wp::add(var_1401, var_1432);
                }
                var_1434 = wp::where(var_1429, var_1433, var_1401);
            }
            var_1435 = wp::where(var_1410, var_1434, var_1401);
            var_1436 = wp::where(var_1410, var_1428, var_1402);
            // for v in range(u):                                                                 <L 61>
            // for k in range(4):                                                                 <L 62>
            // d0=plane_value(vertices[u],other[k]);d1=plane_value(vertices[v],other[k])          <L 63>
            var_1440 = wp::extract(var_1295, var_1437);
            var_1441 = wp::extract(var_1296, var_1439);
            var_1442 = plane_value_0(var_1440, var_1441);
            var_1443 = wp::extract(var_1295, var_1438);
            var_1444 = wp::extract(var_1296, var_1439);
            var_1445 = plane_value_0(var_1443, var_1444);
            // if (d0<wp.float64(0.) and d1>wp.float64(0.)) or (d1<wp.float64(0.) and d0>wp.float64(0.)):       <L 64>
            var_1448 = 0.0;
            var_1449 = (var_1442 < var_1448);
            var_1447 = var_1449;
            if (var_1447) {
                var_1450 = 0.0;
                var_1451 = (var_1445 > var_1450);
                var_1447 = var_1447 && var_1451;
            }
            var_1446 = var_1447;
            if (!var_1446) {
                var_1453 = 0.0;
                var_1454 = (var_1445 < var_1453);
                var_1452 = var_1454;
                if (var_1452) {
                    var_1455 = 0.0;
                    var_1456 = (var_1442 > var_1455);
                    var_1452 = var_1452 && var_1456;
                }
                var_1446 = var_1446 || var_1452;
            }
            if (var_1446) {
                // point=vertices[u]+d0/(d0-d1)*(vertices[v]-vertices[u])                         <L 65>
                var_1457 = wp::extract(var_1295, var_1437);
                var_1458 = wp::sub(var_1442, var_1445);
                var_1459 = wp::div(var_1442, var_1458);
                var_1460 = wp::extract(var_1295, var_1438);
                var_1461 = wp::extract(var_1295, var_1437);
                var_1462 = wp::sub(var_1460, var_1461);
                var_1463 = wp::mul(var_1459, var_1462);
                var_1464 = wp::add(var_1457, var_1463);
                // if inside(point,other) and inside(point,own):points[count]=point;count+=1       <L 66>
                var_1466 = inside_0(var_1464, var_1296);
                var_1465 = var_1466;
                if (var_1465) {
                    var_1467 = inside_0(var_1464, var_1297);
                    var_1465 = var_1465 && var_1467;
                }
                if (var_1465) {
                    wp::assign_inplace(var_394, var_1435, var_1464);
                    var_1469 = wp::add(var_1435, var_1468);
                }
                var_1470 = wp::where(var_1465, var_1469, var_1435);
            }
            var_1471 = wp::where(var_1446, var_1470, var_1435);
            var_1472 = wp::where(var_1446, var_1464, var_1436);
            // d0=plane_value(vertices[u],other[k]);d1=plane_value(vertices[v],other[k])          <L 63>
            var_1474 = wp::extract(var_1295, var_1437);
            var_1475 = wp::extract(var_1296, var_1473);
            var_1476 = plane_value_0(var_1474, var_1475);
            var_1477 = wp::extract(var_1295, var_1438);
            var_1478 = wp::extract(var_1296, var_1473);
            var_1479 = plane_value_0(var_1477, var_1478);
            // if (d0<wp.float64(0.) and d1>wp.float64(0.)) or (d1<wp.float64(0.) and d0>wp.float64(0.)):       <L 64>
            var_1482 = 0.0;
            var_1483 = (var_1476 < var_1482);
            var_1481 = var_1483;
            if (var_1481) {
                var_1484 = 0.0;
                var_1485 = (var_1479 > var_1484);
                var_1481 = var_1481 && var_1485;
            }
            var_1480 = var_1481;
            if (!var_1480) {
                var_1487 = 0.0;
                var_1488 = (var_1479 < var_1487);
                var_1486 = var_1488;
                if (var_1486) {
                    var_1489 = 0.0;
                    var_1490 = (var_1476 > var_1489);
                    var_1486 = var_1486 && var_1490;
                }
                var_1480 = var_1480 || var_1486;
            }
            if (var_1480) {
                // point=vertices[u]+d0/(d0-d1)*(vertices[v]-vertices[u])                         <L 65>
                var_1491 = wp::extract(var_1295, var_1437);
                var_1492 = wp::sub(var_1476, var_1479);
                var_1493 = wp::div(var_1476, var_1492);
                var_1494 = wp::extract(var_1295, var_1438);
                var_1495 = wp::extract(var_1295, var_1437);
                var_1496 = wp::sub(var_1494, var_1495);
                var_1497 = wp::mul(var_1493, var_1496);
                var_1498 = wp::add(var_1491, var_1497);
                // if inside(point,other) and inside(point,own):points[count]=point;count+=1       <L 66>
                var_1500 = inside_0(var_1498, var_1296);
                var_1499 = var_1500;
                if (var_1499) {
                    var_1501 = inside_0(var_1498, var_1297);
                    var_1499 = var_1499 && var_1501;
                }
                if (var_1499) {
                    wp::assign_inplace(var_394, var_1471, var_1498);
                    var_1503 = wp::add(var_1471, var_1502);
                }
                var_1504 = wp::where(var_1499, var_1503, var_1471);
            }
            var_1505 = wp::where(var_1480, var_1504, var_1471);
            var_1506 = wp::where(var_1480, var_1498, var_1472);
            // d0=plane_value(vertices[u],other[k]);d1=plane_value(vertices[v],other[k])          <L 63>
            var_1508 = wp::extract(var_1295, var_1437);
            var_1509 = wp::extract(var_1296, var_1507);
            var_1510 = plane_value_0(var_1508, var_1509);
            var_1511 = wp::extract(var_1295, var_1438);
            var_1512 = wp::extract(var_1296, var_1507);
            var_1513 = plane_value_0(var_1511, var_1512);
            // if (d0<wp.float64(0.) and d1>wp.float64(0.)) or (d1<wp.float64(0.) and d0>wp.float64(0.)):       <L 64>
            var_1516 = 0.0;
            var_1517 = (var_1510 < var_1516);
            var_1515 = var_1517;
            if (var_1515) {
                var_1518 = 0.0;
                var_1519 = (var_1513 > var_1518);
                var_1515 = var_1515 && var_1519;
            }
            var_1514 = var_1515;
            if (!var_1514) {
                var_1521 = 0.0;
                var_1522 = (var_1513 < var_1521);
                var_1520 = var_1522;
                if (var_1520) {
                    var_1523 = 0.0;
                    var_1524 = (var_1510 > var_1523);
                    var_1520 = var_1520 && var_1524;
                }
                var_1514 = var_1514 || var_1520;
            }
            if (var_1514) {
                // point=vertices[u]+d0/(d0-d1)*(vertices[v]-vertices[u])                         <L 65>
                var_1525 = wp::extract(var_1295, var_1437);
                var_1526 = wp::sub(var_1510, var_1513);
                var_1527 = wp::div(var_1510, var_1526);
                var_1528 = wp::extract(var_1295, var_1438);
                var_1529 = wp::extract(var_1295, var_1437);
                var_1530 = wp::sub(var_1528, var_1529);
                var_1531 = wp::mul(var_1527, var_1530);
                var_1532 = wp::add(var_1525, var_1531);
                // if inside(point,other) and inside(point,own):points[count]=point;count+=1       <L 66>
                var_1534 = inside_0(var_1532, var_1296);
                var_1533 = var_1534;
                if (var_1533) {
                    var_1535 = inside_0(var_1532, var_1297);
                    var_1533 = var_1533 && var_1535;
                }
                if (var_1533) {
                    wp::assign_inplace(var_394, var_1505, var_1532);
                    var_1537 = wp::add(var_1505, var_1536);
                }
                var_1538 = wp::where(var_1533, var_1537, var_1505);
            }
            var_1539 = wp::where(var_1514, var_1538, var_1505);
            var_1540 = wp::where(var_1514, var_1532, var_1506);
            // d0=plane_value(vertices[u],other[k]);d1=plane_value(vertices[v],other[k])          <L 63>
            var_1542 = wp::extract(var_1295, var_1437);
            var_1543 = wp::extract(var_1296, var_1541);
            var_1544 = plane_value_0(var_1542, var_1543);
            var_1545 = wp::extract(var_1295, var_1438);
            var_1546 = wp::extract(var_1296, var_1541);
            var_1547 = plane_value_0(var_1545, var_1546);
            // if (d0<wp.float64(0.) and d1>wp.float64(0.)) or (d1<wp.float64(0.) and d0>wp.float64(0.)):       <L 64>
            var_1550 = 0.0;
            var_1551 = (var_1544 < var_1550);
            var_1549 = var_1551;
            if (var_1549) {
                var_1552 = 0.0;
                var_1553 = (var_1547 > var_1552);
                var_1549 = var_1549 && var_1553;
            }
            var_1548 = var_1549;
            if (!var_1548) {
                var_1555 = 0.0;
                var_1556 = (var_1547 < var_1555);
                var_1554 = var_1556;
                if (var_1554) {
                    var_1557 = 0.0;
                    var_1558 = (var_1544 > var_1557);
                    var_1554 = var_1554 && var_1558;
                }
                var_1548 = var_1548 || var_1554;
            }
            if (var_1548) {
                // point=vertices[u]+d0/(d0-d1)*(vertices[v]-vertices[u])                         <L 65>
                var_1559 = wp::extract(var_1295, var_1437);
                var_1560 = wp::sub(var_1544, var_1547);
                var_1561 = wp::div(var_1544, var_1560);
                var_1562 = wp::extract(var_1295, var_1438);
                var_1563 = wp::extract(var_1295, var_1437);
                var_1564 = wp::sub(var_1562, var_1563);
                var_1565 = wp::mul(var_1561, var_1564);
                var_1566 = wp::add(var_1559, var_1565);
                // if inside(point,other) and inside(point,own):points[count]=point;count+=1       <L 66>
                var_1568 = inside_0(var_1566, var_1296);
                var_1567 = var_1568;
                if (var_1567) {
                    var_1569 = inside_0(var_1566, var_1297);
                    var_1567 = var_1567 && var_1569;
                }
                if (var_1567) {
                    wp::assign_inplace(var_394, var_1539, var_1566);
                    var_1571 = wp::add(var_1539, var_1570);
                }
                var_1572 = wp::where(var_1567, var_1571, var_1539);
            }
            var_1573 = wp::where(var_1548, var_1572, var_1539);
            var_1574 = wp::where(var_1548, var_1566, var_1540);
            // for k in range(4):                                                                 <L 62>
            // d0=plane_value(vertices[u],other[k]);d1=plane_value(vertices[v],other[k])          <L 63>
            var_1577 = wp::extract(var_1295, var_1437);
            var_1578 = wp::extract(var_1296, var_1576);
            var_1579 = plane_value_0(var_1577, var_1578);
            var_1580 = wp::extract(var_1295, var_1575);
            var_1581 = wp::extract(var_1296, var_1576);
            var_1582 = plane_value_0(var_1580, var_1581);
            // if (d0<wp.float64(0.) and d1>wp.float64(0.)) or (d1<wp.float64(0.) and d0>wp.float64(0.)):       <L 64>
            var_1585 = 0.0;
            var_1586 = (var_1579 < var_1585);
            var_1584 = var_1586;
            if (var_1584) {
                var_1587 = 0.0;
                var_1588 = (var_1582 > var_1587);
                var_1584 = var_1584 && var_1588;
            }
            var_1583 = var_1584;
            if (!var_1583) {
                var_1590 = 0.0;
                var_1591 = (var_1582 < var_1590);
                var_1589 = var_1591;
                if (var_1589) {
                    var_1592 = 0.0;
                    var_1593 = (var_1579 > var_1592);
                    var_1589 = var_1589 && var_1593;
                }
                var_1583 = var_1583 || var_1589;
            }
            if (var_1583) {
                // point=vertices[u]+d0/(d0-d1)*(vertices[v]-vertices[u])                         <L 65>
                var_1594 = wp::extract(var_1295, var_1437);
                var_1595 = wp::sub(var_1579, var_1582);
                var_1596 = wp::div(var_1579, var_1595);
                var_1597 = wp::extract(var_1295, var_1575);
                var_1598 = wp::extract(var_1295, var_1437);
                var_1599 = wp::sub(var_1597, var_1598);
                var_1600 = wp::mul(var_1596, var_1599);
                var_1601 = wp::add(var_1594, var_1600);
                // if inside(point,other) and inside(point,own):points[count]=point;count+=1       <L 66>
                var_1603 = inside_0(var_1601, var_1296);
                var_1602 = var_1603;
                if (var_1602) {
                    var_1604 = inside_0(var_1601, var_1297);
                    var_1602 = var_1602 && var_1604;
                }
                if (var_1602) {
                    wp::assign_inplace(var_394, var_1573, var_1601);
                    var_1606 = wp::add(var_1573, var_1605);
                }
                var_1607 = wp::where(var_1602, var_1606, var_1573);
            }
            var_1608 = wp::where(var_1583, var_1607, var_1573);
            var_1609 = wp::where(var_1583, var_1601, var_1574);
            // d0=plane_value(vertices[u],other[k]);d1=plane_value(vertices[v],other[k])          <L 63>
            var_1611 = wp::extract(var_1295, var_1437);
            var_1612 = wp::extract(var_1296, var_1610);
            var_1613 = plane_value_0(var_1611, var_1612);
            var_1614 = wp::extract(var_1295, var_1575);
            var_1615 = wp::extract(var_1296, var_1610);
            var_1616 = plane_value_0(var_1614, var_1615);
            // if (d0<wp.float64(0.) and d1>wp.float64(0.)) or (d1<wp.float64(0.) and d0>wp.float64(0.)):       <L 64>
            var_1619 = 0.0;
            var_1620 = (var_1613 < var_1619);
            var_1618 = var_1620;
            if (var_1618) {
                var_1621 = 0.0;
                var_1622 = (var_1616 > var_1621);
                var_1618 = var_1618 && var_1622;
            }
            var_1617 = var_1618;
            if (!var_1617) {
                var_1624 = 0.0;
                var_1625 = (var_1616 < var_1624);
                var_1623 = var_1625;
                if (var_1623) {
                    var_1626 = 0.0;
                    var_1627 = (var_1613 > var_1626);
                    var_1623 = var_1623 && var_1627;
                }
                var_1617 = var_1617 || var_1623;
            }
            if (var_1617) {
                // point=vertices[u]+d0/(d0-d1)*(vertices[v]-vertices[u])                         <L 65>
                var_1628 = wp::extract(var_1295, var_1437);
                var_1629 = wp::sub(var_1613, var_1616);
                var_1630 = wp::div(var_1613, var_1629);
                var_1631 = wp::extract(var_1295, var_1575);
                var_1632 = wp::extract(var_1295, var_1437);
                var_1633 = wp::sub(var_1631, var_1632);
                var_1634 = wp::mul(var_1630, var_1633);
                var_1635 = wp::add(var_1628, var_1634);
                // if inside(point,other) and inside(point,own):points[count]=point;count+=1       <L 66>
                var_1637 = inside_0(var_1635, var_1296);
                var_1636 = var_1637;
                if (var_1636) {
                    var_1638 = inside_0(var_1635, var_1297);
                    var_1636 = var_1636 && var_1638;
                }
                if (var_1636) {
                    wp::assign_inplace(var_394, var_1608, var_1635);
                    var_1640 = wp::add(var_1608, var_1639);
                }
                var_1641 = wp::where(var_1636, var_1640, var_1608);
            }
            var_1642 = wp::where(var_1617, var_1641, var_1608);
            var_1643 = wp::where(var_1617, var_1635, var_1609);
            // d0=plane_value(vertices[u],other[k]);d1=plane_value(vertices[v],other[k])          <L 63>
            var_1645 = wp::extract(var_1295, var_1437);
            var_1646 = wp::extract(var_1296, var_1644);
            var_1647 = plane_value_0(var_1645, var_1646);
            var_1648 = wp::extract(var_1295, var_1575);
            var_1649 = wp::extract(var_1296, var_1644);
            var_1650 = plane_value_0(var_1648, var_1649);
            // if (d0<wp.float64(0.) and d1>wp.float64(0.)) or (d1<wp.float64(0.) and d0>wp.float64(0.)):       <L 64>
            var_1653 = 0.0;
            var_1654 = (var_1647 < var_1653);
            var_1652 = var_1654;
            if (var_1652) {
                var_1655 = 0.0;
                var_1656 = (var_1650 > var_1655);
                var_1652 = var_1652 && var_1656;
            }
            var_1651 = var_1652;
            if (!var_1651) {
                var_1658 = 0.0;
                var_1659 = (var_1650 < var_1658);
                var_1657 = var_1659;
                if (var_1657) {
                    var_1660 = 0.0;
                    var_1661 = (var_1647 > var_1660);
                    var_1657 = var_1657 && var_1661;
                }
                var_1651 = var_1651 || var_1657;
            }
            if (var_1651) {
                // point=vertices[u]+d0/(d0-d1)*(vertices[v]-vertices[u])                         <L 65>
                var_1662 = wp::extract(var_1295, var_1437);
                var_1663 = wp::sub(var_1647, var_1650);
                var_1664 = wp::div(var_1647, var_1663);
                var_1665 = wp::extract(var_1295, var_1575);
                var_1666 = wp::extract(var_1295, var_1437);
                var_1667 = wp::sub(var_1665, var_1666);
                var_1668 = wp::mul(var_1664, var_1667);
                var_1669 = wp::add(var_1662, var_1668);
                // if inside(point,other) and inside(point,own):points[count]=point;count+=1       <L 66>
                var_1671 = inside_0(var_1669, var_1296);
                var_1670 = var_1671;
                if (var_1670) {
                    var_1672 = inside_0(var_1669, var_1297);
                    var_1670 = var_1670 && var_1672;
                }
                if (var_1670) {
                    wp::assign_inplace(var_394, var_1642, var_1669);
                    var_1674 = wp::add(var_1642, var_1673);
                }
                var_1675 = wp::where(var_1670, var_1674, var_1642);
            }
            var_1676 = wp::where(var_1651, var_1675, var_1642);
            var_1677 = wp::where(var_1651, var_1669, var_1643);
            // d0=plane_value(vertices[u],other[k]);d1=plane_value(vertices[v],other[k])          <L 63>
            var_1679 = wp::extract(var_1295, var_1437);
            var_1680 = wp::extract(var_1296, var_1678);
            var_1681 = plane_value_0(var_1679, var_1680);
            var_1682 = wp::extract(var_1295, var_1575);
            var_1683 = wp::extract(var_1296, var_1678);
            var_1684 = plane_value_0(var_1682, var_1683);
            // if (d0<wp.float64(0.) and d1>wp.float64(0.)) or (d1<wp.float64(0.) and d0>wp.float64(0.)):       <L 64>
            var_1687 = 0.0;
            var_1688 = (var_1681 < var_1687);
            var_1686 = var_1688;
            if (var_1686) {
                var_1689 = 0.0;
                var_1690 = (var_1684 > var_1689);
                var_1686 = var_1686 && var_1690;
            }
            var_1685 = var_1686;
            if (!var_1685) {
                var_1692 = 0.0;
                var_1693 = (var_1684 < var_1692);
                var_1691 = var_1693;
                if (var_1691) {
                    var_1694 = 0.0;
                    var_1695 = (var_1681 > var_1694);
                    var_1691 = var_1691 && var_1695;
                }
                var_1685 = var_1685 || var_1691;
            }
            if (var_1685) {
                // point=vertices[u]+d0/(d0-d1)*(vertices[v]-vertices[u])                         <L 65>
                var_1696 = wp::extract(var_1295, var_1437);
                var_1697 = wp::sub(var_1681, var_1684);
                var_1698 = wp::div(var_1681, var_1697);
                var_1699 = wp::extract(var_1295, var_1575);
                var_1700 = wp::extract(var_1295, var_1437);
                var_1701 = wp::sub(var_1699, var_1700);
                var_1702 = wp::mul(var_1698, var_1701);
                var_1703 = wp::add(var_1696, var_1702);
                // if inside(point,other) and inside(point,own):points[count]=point;count+=1       <L 66>
                var_1705 = inside_0(var_1703, var_1296);
                var_1704 = var_1705;
                if (var_1704) {
                    var_1706 = inside_0(var_1703, var_1297);
                    var_1704 = var_1704 && var_1706;
                }
                if (var_1704) {
                    wp::assign_inplace(var_394, var_1676, var_1703);
                    var_1708 = wp::add(var_1676, var_1707);
                }
                var_1709 = wp::where(var_1704, var_1708, var_1676);
            }
            var_1710 = wp::where(var_1685, var_1709, var_1676);
            var_1711 = wp::where(var_1685, var_1703, var_1677);
            // for v in range(u):                                                                 <L 61>
            // for k in range(4):                                                                 <L 62>
            // d0=plane_value(vertices[u],other[k]);d1=plane_value(vertices[v],other[k])          <L 63>
            var_1715 = wp::extract(var_1295, var_1712);
            var_1716 = wp::extract(var_1296, var_1714);
            var_1717 = plane_value_0(var_1715, var_1716);
            var_1718 = wp::extract(var_1295, var_1713);
            var_1719 = wp::extract(var_1296, var_1714);
            var_1720 = plane_value_0(var_1718, var_1719);
            // if (d0<wp.float64(0.) and d1>wp.float64(0.)) or (d1<wp.float64(0.) and d0>wp.float64(0.)):       <L 64>
            var_1723 = 0.0;
            var_1724 = (var_1717 < var_1723);
            var_1722 = var_1724;
            if (var_1722) {
                var_1725 = 0.0;
                var_1726 = (var_1720 > var_1725);
                var_1722 = var_1722 && var_1726;
            }
            var_1721 = var_1722;
            if (!var_1721) {
                var_1728 = 0.0;
                var_1729 = (var_1720 < var_1728);
                var_1727 = var_1729;
                if (var_1727) {
                    var_1730 = 0.0;
                    var_1731 = (var_1717 > var_1730);
                    var_1727 = var_1727 && var_1731;
                }
                var_1721 = var_1721 || var_1727;
            }
            if (var_1721) {
                // point=vertices[u]+d0/(d0-d1)*(vertices[v]-vertices[u])                         <L 65>
                var_1732 = wp::extract(var_1295, var_1712);
                var_1733 = wp::sub(var_1717, var_1720);
                var_1734 = wp::div(var_1717, var_1733);
                var_1735 = wp::extract(var_1295, var_1713);
                var_1736 = wp::extract(var_1295, var_1712);
                var_1737 = wp::sub(var_1735, var_1736);
                var_1738 = wp::mul(var_1734, var_1737);
                var_1739 = wp::add(var_1732, var_1738);
                // if inside(point,other) and inside(point,own):points[count]=point;count+=1       <L 66>
                var_1741 = inside_0(var_1739, var_1296);
                var_1740 = var_1741;
                if (var_1740) {
                    var_1742 = inside_0(var_1739, var_1297);
                    var_1740 = var_1740 && var_1742;
                }
                if (var_1740) {
                    wp::assign_inplace(var_394, var_1710, var_1739);
                    var_1744 = wp::add(var_1710, var_1743);
                }
                var_1745 = wp::where(var_1740, var_1744, var_1710);
            }
            var_1746 = wp::where(var_1721, var_1745, var_1710);
            var_1747 = wp::where(var_1721, var_1739, var_1711);
            // d0=plane_value(vertices[u],other[k]);d1=plane_value(vertices[v],other[k])          <L 63>
            var_1749 = wp::extract(var_1295, var_1712);
            var_1750 = wp::extract(var_1296, var_1748);
            var_1751 = plane_value_0(var_1749, var_1750);
            var_1752 = wp::extract(var_1295, var_1713);
            var_1753 = wp::extract(var_1296, var_1748);
            var_1754 = plane_value_0(var_1752, var_1753);
            // if (d0<wp.float64(0.) and d1>wp.float64(0.)) or (d1<wp.float64(0.) and d0>wp.float64(0.)):       <L 64>
            var_1757 = 0.0;
            var_1758 = (var_1751 < var_1757);
            var_1756 = var_1758;
            if (var_1756) {
                var_1759 = 0.0;
                var_1760 = (var_1754 > var_1759);
                var_1756 = var_1756 && var_1760;
            }
            var_1755 = var_1756;
            if (!var_1755) {
                var_1762 = 0.0;
                var_1763 = (var_1754 < var_1762);
                var_1761 = var_1763;
                if (var_1761) {
                    var_1764 = 0.0;
                    var_1765 = (var_1751 > var_1764);
                    var_1761 = var_1761 && var_1765;
                }
                var_1755 = var_1755 || var_1761;
            }
            if (var_1755) {
                // point=vertices[u]+d0/(d0-d1)*(vertices[v]-vertices[u])                         <L 65>
                var_1766 = wp::extract(var_1295, var_1712);
                var_1767 = wp::sub(var_1751, var_1754);
                var_1768 = wp::div(var_1751, var_1767);
                var_1769 = wp::extract(var_1295, var_1713);
                var_1770 = wp::extract(var_1295, var_1712);
                var_1771 = wp::sub(var_1769, var_1770);
                var_1772 = wp::mul(var_1768, var_1771);
                var_1773 = wp::add(var_1766, var_1772);
                // if inside(point,other) and inside(point,own):points[count]=point;count+=1       <L 66>
                var_1775 = inside_0(var_1773, var_1296);
                var_1774 = var_1775;
                if (var_1774) {
                    var_1776 = inside_0(var_1773, var_1297);
                    var_1774 = var_1774 && var_1776;
                }
                if (var_1774) {
                    wp::assign_inplace(var_394, var_1746, var_1773);
                    var_1778 = wp::add(var_1746, var_1777);
                }
                var_1779 = wp::where(var_1774, var_1778, var_1746);
            }
            var_1780 = wp::where(var_1755, var_1779, var_1746);
            var_1781 = wp::where(var_1755, var_1773, var_1747);
            // d0=plane_value(vertices[u],other[k]);d1=plane_value(vertices[v],other[k])          <L 63>
            var_1783 = wp::extract(var_1295, var_1712);
            var_1784 = wp::extract(var_1296, var_1782);
            var_1785 = plane_value_0(var_1783, var_1784);
            var_1786 = wp::extract(var_1295, var_1713);
            var_1787 = wp::extract(var_1296, var_1782);
            var_1788 = plane_value_0(var_1786, var_1787);
            // if (d0<wp.float64(0.) and d1>wp.float64(0.)) or (d1<wp.float64(0.) and d0>wp.float64(0.)):       <L 64>
            var_1791 = 0.0;
            var_1792 = (var_1785 < var_1791);
            var_1790 = var_1792;
            if (var_1790) {
                var_1793 = 0.0;
                var_1794 = (var_1788 > var_1793);
                var_1790 = var_1790 && var_1794;
            }
            var_1789 = var_1790;
            if (!var_1789) {
                var_1796 = 0.0;
                var_1797 = (var_1788 < var_1796);
                var_1795 = var_1797;
                if (var_1795) {
                    var_1798 = 0.0;
                    var_1799 = (var_1785 > var_1798);
                    var_1795 = var_1795 && var_1799;
                }
                var_1789 = var_1789 || var_1795;
            }
            if (var_1789) {
                // point=vertices[u]+d0/(d0-d1)*(vertices[v]-vertices[u])                         <L 65>
                var_1800 = wp::extract(var_1295, var_1712);
                var_1801 = wp::sub(var_1785, var_1788);
                var_1802 = wp::div(var_1785, var_1801);
                var_1803 = wp::extract(var_1295, var_1713);
                var_1804 = wp::extract(var_1295, var_1712);
                var_1805 = wp::sub(var_1803, var_1804);
                var_1806 = wp::mul(var_1802, var_1805);
                var_1807 = wp::add(var_1800, var_1806);
                // if inside(point,other) and inside(point,own):points[count]=point;count+=1       <L 66>
                var_1809 = inside_0(var_1807, var_1296);
                var_1808 = var_1809;
                if (var_1808) {
                    var_1810 = inside_0(var_1807, var_1297);
                    var_1808 = var_1808 && var_1810;
                }
                if (var_1808) {
                    wp::assign_inplace(var_394, var_1780, var_1807);
                    var_1812 = wp::add(var_1780, var_1811);
                }
                var_1813 = wp::where(var_1808, var_1812, var_1780);
            }
            var_1814 = wp::where(var_1789, var_1813, var_1780);
            var_1815 = wp::where(var_1789, var_1807, var_1781);
            // d0=plane_value(vertices[u],other[k]);d1=plane_value(vertices[v],other[k])          <L 63>
            var_1817 = wp::extract(var_1295, var_1712);
            var_1818 = wp::extract(var_1296, var_1816);
            var_1819 = plane_value_0(var_1817, var_1818);
            var_1820 = wp::extract(var_1295, var_1713);
            var_1821 = wp::extract(var_1296, var_1816);
            var_1822 = plane_value_0(var_1820, var_1821);
            // if (d0<wp.float64(0.) and d1>wp.float64(0.)) or (d1<wp.float64(0.) and d0>wp.float64(0.)):       <L 64>
            var_1825 = 0.0;
            var_1826 = (var_1819 < var_1825);
            var_1824 = var_1826;
            if (var_1824) {
                var_1827 = 0.0;
                var_1828 = (var_1822 > var_1827);
                var_1824 = var_1824 && var_1828;
            }
            var_1823 = var_1824;
            if (!var_1823) {
                var_1830 = 0.0;
                var_1831 = (var_1822 < var_1830);
                var_1829 = var_1831;
                if (var_1829) {
                    var_1832 = 0.0;
                    var_1833 = (var_1819 > var_1832);
                    var_1829 = var_1829 && var_1833;
                }
                var_1823 = var_1823 || var_1829;
            }
            if (var_1823) {
                // point=vertices[u]+d0/(d0-d1)*(vertices[v]-vertices[u])                         <L 65>
                var_1834 = wp::extract(var_1295, var_1712);
                var_1835 = wp::sub(var_1819, var_1822);
                var_1836 = wp::div(var_1819, var_1835);
                var_1837 = wp::extract(var_1295, var_1713);
                var_1838 = wp::extract(var_1295, var_1712);
                var_1839 = wp::sub(var_1837, var_1838);
                var_1840 = wp::mul(var_1836, var_1839);
                var_1841 = wp::add(var_1834, var_1840);
                // if inside(point,other) and inside(point,own):points[count]=point;count+=1       <L 66>
                var_1843 = inside_0(var_1841, var_1296);
                var_1842 = var_1843;
                if (var_1842) {
                    var_1844 = inside_0(var_1841, var_1297);
                    var_1842 = var_1842 && var_1844;
                }
                if (var_1842) {
                    wp::assign_inplace(var_394, var_1814, var_1841);
                    var_1846 = wp::add(var_1814, var_1845);
                }
                var_1847 = wp::where(var_1842, var_1846, var_1814);
            }
            var_1848 = wp::where(var_1823, var_1847, var_1814);
            var_1849 = wp::where(var_1823, var_1841, var_1815);
            // for k in range(4):                                                                 <L 62>
            // d0=plane_value(vertices[u],other[k]);d1=plane_value(vertices[v],other[k])          <L 63>
            var_1852 = wp::extract(var_1295, var_1712);
            var_1853 = wp::extract(var_1296, var_1851);
            var_1854 = plane_value_0(var_1852, var_1853);
            var_1855 = wp::extract(var_1295, var_1850);
            var_1856 = wp::extract(var_1296, var_1851);
            var_1857 = plane_value_0(var_1855, var_1856);
            // if (d0<wp.float64(0.) and d1>wp.float64(0.)) or (d1<wp.float64(0.) and d0>wp.float64(0.)):       <L 64>
            var_1860 = 0.0;
            var_1861 = (var_1854 < var_1860);
            var_1859 = var_1861;
            if (var_1859) {
                var_1862 = 0.0;
                var_1863 = (var_1857 > var_1862);
                var_1859 = var_1859 && var_1863;
            }
            var_1858 = var_1859;
            if (!var_1858) {
                var_1865 = 0.0;
                var_1866 = (var_1857 < var_1865);
                var_1864 = var_1866;
                if (var_1864) {
                    var_1867 = 0.0;
                    var_1868 = (var_1854 > var_1867);
                    var_1864 = var_1864 && var_1868;
                }
                var_1858 = var_1858 || var_1864;
            }
            if (var_1858) {
                // point=vertices[u]+d0/(d0-d1)*(vertices[v]-vertices[u])                         <L 65>
                var_1869 = wp::extract(var_1295, var_1712);
                var_1870 = wp::sub(var_1854, var_1857);
                var_1871 = wp::div(var_1854, var_1870);
                var_1872 = wp::extract(var_1295, var_1850);
                var_1873 = wp::extract(var_1295, var_1712);
                var_1874 = wp::sub(var_1872, var_1873);
                var_1875 = wp::mul(var_1871, var_1874);
                var_1876 = wp::add(var_1869, var_1875);
                // if inside(point,other) and inside(point,own):points[count]=point;count+=1       <L 66>
                var_1878 = inside_0(var_1876, var_1296);
                var_1877 = var_1878;
                if (var_1877) {
                    var_1879 = inside_0(var_1876, var_1297);
                    var_1877 = var_1877 && var_1879;
                }
                if (var_1877) {
                    wp::assign_inplace(var_394, var_1848, var_1876);
                    var_1881 = wp::add(var_1848, var_1880);
                }
                var_1882 = wp::where(var_1877, var_1881, var_1848);
            }
            var_1883 = wp::where(var_1858, var_1882, var_1848);
            var_1884 = wp::where(var_1858, var_1876, var_1849);
            // d0=plane_value(vertices[u],other[k]);d1=plane_value(vertices[v],other[k])          <L 63>
            var_1886 = wp::extract(var_1295, var_1712);
            var_1887 = wp::extract(var_1296, var_1885);
            var_1888 = plane_value_0(var_1886, var_1887);
            var_1889 = wp::extract(var_1295, var_1850);
            var_1890 = wp::extract(var_1296, var_1885);
            var_1891 = plane_value_0(var_1889, var_1890);
            // if (d0<wp.float64(0.) and d1>wp.float64(0.)) or (d1<wp.float64(0.) and d0>wp.float64(0.)):       <L 64>
            var_1894 = 0.0;
            var_1895 = (var_1888 < var_1894);
            var_1893 = var_1895;
            if (var_1893) {
                var_1896 = 0.0;
                var_1897 = (var_1891 > var_1896);
                var_1893 = var_1893 && var_1897;
            }
            var_1892 = var_1893;
            if (!var_1892) {
                var_1899 = 0.0;
                var_1900 = (var_1891 < var_1899);
                var_1898 = var_1900;
                if (var_1898) {
                    var_1901 = 0.0;
                    var_1902 = (var_1888 > var_1901);
                    var_1898 = var_1898 && var_1902;
                }
                var_1892 = var_1892 || var_1898;
            }
            if (var_1892) {
                // point=vertices[u]+d0/(d0-d1)*(vertices[v]-vertices[u])                         <L 65>
                var_1903 = wp::extract(var_1295, var_1712);
                var_1904 = wp::sub(var_1888, var_1891);
                var_1905 = wp::div(var_1888, var_1904);
                var_1906 = wp::extract(var_1295, var_1850);
                var_1907 = wp::extract(var_1295, var_1712);
                var_1908 = wp::sub(var_1906, var_1907);
                var_1909 = wp::mul(var_1905, var_1908);
                var_1910 = wp::add(var_1903, var_1909);
                // if inside(point,other) and inside(point,own):points[count]=point;count+=1       <L 66>
                var_1912 = inside_0(var_1910, var_1296);
                var_1911 = var_1912;
                if (var_1911) {
                    var_1913 = inside_0(var_1910, var_1297);
                    var_1911 = var_1911 && var_1913;
                }
                if (var_1911) {
                    wp::assign_inplace(var_394, var_1883, var_1910);
                    var_1915 = wp::add(var_1883, var_1914);
                }
                var_1916 = wp::where(var_1911, var_1915, var_1883);
            }
            var_1917 = wp::where(var_1892, var_1916, var_1883);
            var_1918 = wp::where(var_1892, var_1910, var_1884);
            // d0=plane_value(vertices[u],other[k]);d1=plane_value(vertices[v],other[k])          <L 63>
            var_1920 = wp::extract(var_1295, var_1712);
            var_1921 = wp::extract(var_1296, var_1919);
            var_1922 = plane_value_0(var_1920, var_1921);
            var_1923 = wp::extract(var_1295, var_1850);
            var_1924 = wp::extract(var_1296, var_1919);
            var_1925 = plane_value_0(var_1923, var_1924);
            // if (d0<wp.float64(0.) and d1>wp.float64(0.)) or (d1<wp.float64(0.) and d0>wp.float64(0.)):       <L 64>
            var_1928 = 0.0;
            var_1929 = (var_1922 < var_1928);
            var_1927 = var_1929;
            if (var_1927) {
                var_1930 = 0.0;
                var_1931 = (var_1925 > var_1930);
                var_1927 = var_1927 && var_1931;
            }
            var_1926 = var_1927;
            if (!var_1926) {
                var_1933 = 0.0;
                var_1934 = (var_1925 < var_1933);
                var_1932 = var_1934;
                if (var_1932) {
                    var_1935 = 0.0;
                    var_1936 = (var_1922 > var_1935);
                    var_1932 = var_1932 && var_1936;
                }
                var_1926 = var_1926 || var_1932;
            }
            if (var_1926) {
                // point=vertices[u]+d0/(d0-d1)*(vertices[v]-vertices[u])                         <L 65>
                var_1937 = wp::extract(var_1295, var_1712);
                var_1938 = wp::sub(var_1922, var_1925);
                var_1939 = wp::div(var_1922, var_1938);
                var_1940 = wp::extract(var_1295, var_1850);
                var_1941 = wp::extract(var_1295, var_1712);
                var_1942 = wp::sub(var_1940, var_1941);
                var_1943 = wp::mul(var_1939, var_1942);
                var_1944 = wp::add(var_1937, var_1943);
                // if inside(point,other) and inside(point,own):points[count]=point;count+=1       <L 66>
                var_1946 = inside_0(var_1944, var_1296);
                var_1945 = var_1946;
                if (var_1945) {
                    var_1947 = inside_0(var_1944, var_1297);
                    var_1945 = var_1945 && var_1947;
                }
                if (var_1945) {
                    wp::assign_inplace(var_394, var_1917, var_1944);
                    var_1949 = wp::add(var_1917, var_1948);
                }
                var_1950 = wp::where(var_1945, var_1949, var_1917);
            }
            var_1951 = wp::where(var_1926, var_1950, var_1917);
            var_1952 = wp::where(var_1926, var_1944, var_1918);
            // d0=plane_value(vertices[u],other[k]);d1=plane_value(vertices[v],other[k])          <L 63>
            var_1954 = wp::extract(var_1295, var_1712);
            var_1955 = wp::extract(var_1296, var_1953);
            var_1956 = plane_value_0(var_1954, var_1955);
            var_1957 = wp::extract(var_1295, var_1850);
            var_1958 = wp::extract(var_1296, var_1953);
            var_1959 = plane_value_0(var_1957, var_1958);
            // if (d0<wp.float64(0.) and d1>wp.float64(0.)) or (d1<wp.float64(0.) and d0>wp.float64(0.)):       <L 64>
            var_1962 = 0.0;
            var_1963 = (var_1956 < var_1962);
            var_1961 = var_1963;
            if (var_1961) {
                var_1964 = 0.0;
                var_1965 = (var_1959 > var_1964);
                var_1961 = var_1961 && var_1965;
            }
            var_1960 = var_1961;
            if (!var_1960) {
                var_1967 = 0.0;
                var_1968 = (var_1959 < var_1967);
                var_1966 = var_1968;
                if (var_1966) {
                    var_1969 = 0.0;
                    var_1970 = (var_1956 > var_1969);
                    var_1966 = var_1966 && var_1970;
                }
                var_1960 = var_1960 || var_1966;
            }
            if (var_1960) {
                // point=vertices[u]+d0/(d0-d1)*(vertices[v]-vertices[u])                         <L 65>
                var_1971 = wp::extract(var_1295, var_1712);
                var_1972 = wp::sub(var_1956, var_1959);
                var_1973 = wp::div(var_1956, var_1972);
                var_1974 = wp::extract(var_1295, var_1850);
                var_1975 = wp::extract(var_1295, var_1712);
                var_1976 = wp::sub(var_1974, var_1975);
                var_1977 = wp::mul(var_1973, var_1976);
                var_1978 = wp::add(var_1971, var_1977);
                // if inside(point,other) and inside(point,own):points[count]=point;count+=1       <L 66>
                var_1980 = inside_0(var_1978, var_1296);
                var_1979 = var_1980;
                if (var_1979) {
                    var_1981 = inside_0(var_1978, var_1297);
                    var_1979 = var_1979 && var_1981;
                }
                if (var_1979) {
                    wp::assign_inplace(var_394, var_1951, var_1978);
                    var_1983 = wp::add(var_1951, var_1982);
                }
                var_1984 = wp::where(var_1979, var_1983, var_1951);
            }
            var_1985 = wp::where(var_1960, var_1984, var_1951);
            var_1986 = wp::where(var_1960, var_1978, var_1952);
            // for k in range(4):                                                                 <L 62>
            // d0=plane_value(vertices[u],other[k]);d1=plane_value(vertices[v],other[k])          <L 63>
            var_1989 = wp::extract(var_1295, var_1712);
            var_1990 = wp::extract(var_1296, var_1988);
            var_1991 = plane_value_0(var_1989, var_1990);
            var_1992 = wp::extract(var_1295, var_1987);
            var_1993 = wp::extract(var_1296, var_1988);
            var_1994 = plane_value_0(var_1992, var_1993);
            // if (d0<wp.float64(0.) and d1>wp.float64(0.)) or (d1<wp.float64(0.) and d0>wp.float64(0.)):       <L 64>
            var_1997 = 0.0;
            var_1998 = (var_1991 < var_1997);
            var_1996 = var_1998;
            if (var_1996) {
                var_1999 = 0.0;
                var_2000 = (var_1994 > var_1999);
                var_1996 = var_1996 && var_2000;
            }
            var_1995 = var_1996;
            if (!var_1995) {
                var_2002 = 0.0;
                var_2003 = (var_1994 < var_2002);
                var_2001 = var_2003;
                if (var_2001) {
                    var_2004 = 0.0;
                    var_2005 = (var_1991 > var_2004);
                    var_2001 = var_2001 && var_2005;
                }
                var_1995 = var_1995 || var_2001;
            }
            if (var_1995) {
                // point=vertices[u]+d0/(d0-d1)*(vertices[v]-vertices[u])                         <L 65>
                var_2006 = wp::extract(var_1295, var_1712);
                var_2007 = wp::sub(var_1991, var_1994);
                var_2008 = wp::div(var_1991, var_2007);
                var_2009 = wp::extract(var_1295, var_1987);
                var_2010 = wp::extract(var_1295, var_1712);
                var_2011 = wp::sub(var_2009, var_2010);
                var_2012 = wp::mul(var_2008, var_2011);
                var_2013 = wp::add(var_2006, var_2012);
                // if inside(point,other) and inside(point,own):points[count]=point;count+=1       <L 66>
                var_2015 = inside_0(var_2013, var_1296);
                var_2014 = var_2015;
                if (var_2014) {
                    var_2016 = inside_0(var_2013, var_1297);
                    var_2014 = var_2014 && var_2016;
                }
                if (var_2014) {
                    wp::assign_inplace(var_394, var_1985, var_2013);
                    var_2018 = wp::add(var_1985, var_2017);
                }
                var_2019 = wp::where(var_2014, var_2018, var_1985);
            }
            var_2020 = wp::where(var_1995, var_2019, var_1985);
            var_2021 = wp::where(var_1995, var_2013, var_1986);
            // d0=plane_value(vertices[u],other[k]);d1=plane_value(vertices[v],other[k])          <L 63>
            var_2023 = wp::extract(var_1295, var_1712);
            var_2024 = wp::extract(var_1296, var_2022);
            var_2025 = plane_value_0(var_2023, var_2024);
            var_2026 = wp::extract(var_1295, var_1987);
            var_2027 = wp::extract(var_1296, var_2022);
            var_2028 = plane_value_0(var_2026, var_2027);
            // if (d0<wp.float64(0.) and d1>wp.float64(0.)) or (d1<wp.float64(0.) and d0>wp.float64(0.)):       <L 64>
            var_2031 = 0.0;
            var_2032 = (var_2025 < var_2031);
            var_2030 = var_2032;
            if (var_2030) {
                var_2033 = 0.0;
                var_2034 = (var_2028 > var_2033);
                var_2030 = var_2030 && var_2034;
            }
            var_2029 = var_2030;
            if (!var_2029) {
                var_2036 = 0.0;
                var_2037 = (var_2028 < var_2036);
                var_2035 = var_2037;
                if (var_2035) {
                    var_2038 = 0.0;
                    var_2039 = (var_2025 > var_2038);
                    var_2035 = var_2035 && var_2039;
                }
                var_2029 = var_2029 || var_2035;
            }
            if (var_2029) {
                // point=vertices[u]+d0/(d0-d1)*(vertices[v]-vertices[u])                         <L 65>
                var_2040 = wp::extract(var_1295, var_1712);
                var_2041 = wp::sub(var_2025, var_2028);
                var_2042 = wp::div(var_2025, var_2041);
                var_2043 = wp::extract(var_1295, var_1987);
                var_2044 = wp::extract(var_1295, var_1712);
                var_2045 = wp::sub(var_2043, var_2044);
                var_2046 = wp::mul(var_2042, var_2045);
                var_2047 = wp::add(var_2040, var_2046);
                // if inside(point,other) and inside(point,own):points[count]=point;count+=1       <L 66>
                var_2049 = inside_0(var_2047, var_1296);
                var_2048 = var_2049;
                if (var_2048) {
                    var_2050 = inside_0(var_2047, var_1297);
                    var_2048 = var_2048 && var_2050;
                }
                if (var_2048) {
                    wp::assign_inplace(var_394, var_2020, var_2047);
                    var_2052 = wp::add(var_2020, var_2051);
                }
                var_2053 = wp::where(var_2048, var_2052, var_2020);
            }
            var_2054 = wp::where(var_2029, var_2053, var_2020);
            var_2055 = wp::where(var_2029, var_2047, var_2021);
            // d0=plane_value(vertices[u],other[k]);d1=plane_value(vertices[v],other[k])          <L 63>
            var_2057 = wp::extract(var_1295, var_1712);
            var_2058 = wp::extract(var_1296, var_2056);
            var_2059 = plane_value_0(var_2057, var_2058);
            var_2060 = wp::extract(var_1295, var_1987);
            var_2061 = wp::extract(var_1296, var_2056);
            var_2062 = plane_value_0(var_2060, var_2061);
            // if (d0<wp.float64(0.) and d1>wp.float64(0.)) or (d1<wp.float64(0.) and d0>wp.float64(0.)):       <L 64>
            var_2065 = 0.0;
            var_2066 = (var_2059 < var_2065);
            var_2064 = var_2066;
            if (var_2064) {
                var_2067 = 0.0;
                var_2068 = (var_2062 > var_2067);
                var_2064 = var_2064 && var_2068;
            }
            var_2063 = var_2064;
            if (!var_2063) {
                var_2070 = 0.0;
                var_2071 = (var_2062 < var_2070);
                var_2069 = var_2071;
                if (var_2069) {
                    var_2072 = 0.0;
                    var_2073 = (var_2059 > var_2072);
                    var_2069 = var_2069 && var_2073;
                }
                var_2063 = var_2063 || var_2069;
            }
            if (var_2063) {
                // point=vertices[u]+d0/(d0-d1)*(vertices[v]-vertices[u])                         <L 65>
                var_2074 = wp::extract(var_1295, var_1712);
                var_2075 = wp::sub(var_2059, var_2062);
                var_2076 = wp::div(var_2059, var_2075);
                var_2077 = wp::extract(var_1295, var_1987);
                var_2078 = wp::extract(var_1295, var_1712);
                var_2079 = wp::sub(var_2077, var_2078);
                var_2080 = wp::mul(var_2076, var_2079);
                var_2081 = wp::add(var_2074, var_2080);
                // if inside(point,other) and inside(point,own):points[count]=point;count+=1       <L 66>
                var_2083 = inside_0(var_2081, var_1296);
                var_2082 = var_2083;
                if (var_2082) {
                    var_2084 = inside_0(var_2081, var_1297);
                    var_2082 = var_2082 && var_2084;
                }
                if (var_2082) {
                    wp::assign_inplace(var_394, var_2054, var_2081);
                    var_2086 = wp::add(var_2054, var_2085);
                }
                var_2087 = wp::where(var_2082, var_2086, var_2054);
            }
            var_2088 = wp::where(var_2063, var_2087, var_2054);
            var_2089 = wp::where(var_2063, var_2081, var_2055);
            // d0=plane_value(vertices[u],other[k]);d1=plane_value(vertices[v],other[k])          <L 63>
            var_2091 = wp::extract(var_1295, var_1712);
            var_2092 = wp::extract(var_1296, var_2090);
            var_2093 = plane_value_0(var_2091, var_2092);
            var_2094 = wp::extract(var_1295, var_1987);
            var_2095 = wp::extract(var_1296, var_2090);
            var_2096 = plane_value_0(var_2094, var_2095);
            // if (d0<wp.float64(0.) and d1>wp.float64(0.)) or (d1<wp.float64(0.) and d0>wp.float64(0.)):       <L 64>
            var_2099 = 0.0;
            var_2100 = (var_2093 < var_2099);
            var_2098 = var_2100;
            if (var_2098) {
                var_2101 = 0.0;
                var_2102 = (var_2096 > var_2101);
                var_2098 = var_2098 && var_2102;
            }
            var_2097 = var_2098;
            if (!var_2097) {
                var_2104 = 0.0;
                var_2105 = (var_2096 < var_2104);
                var_2103 = var_2105;
                if (var_2103) {
                    var_2106 = 0.0;
                    var_2107 = (var_2093 > var_2106);
                    var_2103 = var_2103 && var_2107;
                }
                var_2097 = var_2097 || var_2103;
            }
            if (var_2097) {
                // point=vertices[u]+d0/(d0-d1)*(vertices[v]-vertices[u])                         <L 65>
                var_2108 = wp::extract(var_1295, var_1712);
                var_2109 = wp::sub(var_2093, var_2096);
                var_2110 = wp::div(var_2093, var_2109);
                var_2111 = wp::extract(var_1295, var_1987);
                var_2112 = wp::extract(var_1295, var_1712);
                var_2113 = wp::sub(var_2111, var_2112);
                var_2114 = wp::mul(var_2110, var_2113);
                var_2115 = wp::add(var_2108, var_2114);
                // if inside(point,other) and inside(point,own):points[count]=point;count+=1       <L 66>
                var_2117 = inside_0(var_2115, var_1296);
                var_2116 = var_2117;
                if (var_2116) {
                    var_2118 = inside_0(var_2115, var_1297);
                    var_2116 = var_2116 && var_2118;
                }
                if (var_2116) {
                    wp::assign_inplace(var_394, var_2088, var_2115);
                    var_2120 = wp::add(var_2088, var_2119);
                }
                var_2121 = wp::where(var_2116, var_2120, var_2088);
            }
            var_2122 = wp::where(var_2097, var_2121, var_2088);
            var_2123 = wp::where(var_2097, var_2115, var_2089);
            // if count==0:continue                                                               <L 67>
            var_2125 = (var_2122 == var_2124);
            if (var_2125) {
                goto start_for_0;
            }
            // center=wp.vec3d(wp.float64(0.))                                                    <L 68>
            var_2126 = 0.0;
            var_2127 = wp::vec_t<3, wp::float64>(var_2126);
            // for k in range(count):center+=points[k]                                            <L 69>
            var_2128 = wp::range(var_2122);
            start_for_2:;
                if (iter_cmp(var_2128) == 0) goto end_for_2;
                var_2129 = wp::iter_next(var_2128);
                var_2130 = wp::extract(var_394, var_2129);
                var_2131 = wp::add(var_2127, var_2130);
                wp::assign(var_2127, var_2131);
                goto start_for_2;
            end_for_2:;
            // center/=wp.float64(count);face=int(-1);best=wp.float64(1e30)                       <L 70>
            var_2132 = wp::float64(var_2122);
            var_2133 = wp::div(var_2127, var_2132);
            var_2135 = wp::int(var_2134);
            var_2136 = 1e+30;
            // for k in range(ptr[c],ptr[c+1]):                                                   <L 71>
            var_2137 = wp::address(var_ptr, var_1);
            var_2139 = wp::add(var_1, var_2138);
            var_2140 = wp::address(var_ptr, var_2139);
            var_2142 = wp::load(var_2137);
            var_2143 = wp::load(var_2140);
            var_2141 = wp::range(var_2142, var_2143);
            start_for_4:;
                if (iter_cmp(var_2141) == 0) goto end_for_4;
                var_2144 = wp::iter_next(var_2141);
                // j=ids[k];d=wp.length(center-closest(center,tri[j,0],tri[j,1],tri[j,2]))        <L 72>
                var_2145 = wp::address(var_ids, var_2144);
                var_2147 = wp::load(var_2145);
                var_2146 = wp::copy(var_2147);
                var_2149 = wp::address(var_tri, var_2146, var_2148);
                var_2151 = wp::address(var_tri, var_2146, var_2150);
                var_2153 = wp::address(var_tri, var_2146, var_2152);
                var_2155 = wp::load(var_2149);
                var_2156 = wp::load(var_2151);
                var_2157 = wp::load(var_2153);
                var_2154 = closest_0(var_2133, var_2155, var_2156, var_2157);
                var_2158 = wp::sub(var_2133, var_2154);
                var_2159 = wp::length(var_2158);
                // if d<best:best=d;face=j                                                        <L 73>
                var_2160 = (var_2159 < var_2136);
                if (var_2160) {
                    var_2161 = wp::copy(var_2159);
                    var_2162 = wp::copy(var_2146);
                }
                var_2163 = wp::where(var_2160, var_2162, var_2135);
                var_2164 = wp::where(var_2160, var_2161, var_2136);
                wp::assign(var_386, var_2159);
                wp::assign(var_2135, var_2163);
                wp::assign(var_2136, var_2164);
                goto start_for_4;
            end_for_4:;
            // bound=wp.float64(0.)                                                               <L 74>
            var_2165 = 0.0;
            // for k in range(count):bound=wp.max(bound,wp.length(points[k]-closest(points[k],tri[face,0],tri[face,1],tri[face,2])))       <L 75>
            var_2166 = wp::range(var_2122);
            start_for_6:;
                if (iter_cmp(var_2166) == 0) goto end_for_6;
                var_2167 = wp::iter_next(var_2166);
                var_2168 = wp::extract(var_394, var_2167);
                var_2169 = wp::extract(var_394, var_2167);
                var_2171 = wp::address(var_tri, var_2135, var_2170);
                var_2173 = wp::address(var_tri, var_2135, var_2172);
                var_2175 = wp::address(var_tri, var_2135, var_2174);
                var_2177 = wp::load(var_2171);
                var_2178 = wp::load(var_2173);
                var_2179 = wp::load(var_2175);
                var_2176 = closest_0(var_2169, var_2177, var_2178, var_2179);
                var_2180 = wp::sub(var_2168, var_2176);
                var_2181 = wp::length(var_2180);
                var_2182 = wp::max(var_2165, var_2181);
                wp::assign(var_2165, var_2182);
                goto start_for_6;
            end_for_6:;
            // if bound>target:                                                                   <L 76>
            var_2183 = (var_2165 > var_target);
            if (var_2183) {
                // for k in range(ptr[c],ptr[c+1]):                                               <L 77>
                var_2184 = wp::address(var_ptr, var_1);
                var_2186 = wp::add(var_1, var_2185);
                var_2187 = wp::address(var_ptr, var_2186);
                var_2189 = wp::load(var_2184);
                var_2190 = wp::load(var_2187);
                var_2188 = wp::range(var_2189, var_2190);
                var_2191 = wp::copy(var_1712);
                start_for_8:;
                    if (iter_cmp(var_2188) == 0) goto end_for_8;
                    var_2192 = wp::iter_next(var_2188);
                    // j=ids[k];candidate=wp.float64(0.)                                          <L 78>
                    var_2193 = wp::address(var_ids, var_2192);
                    var_2195 = wp::load(var_2193);
                    var_2194 = wp::copy(var_2195);
                    var_2196 = 0.0;
                    // for u in range(count):candidate=wp.max(candidate,wp.length(points[u]-closest(points[u],tri[j,0],tri[j,1],tri[j,2])))       <L 79>
                    var_2197 = wp::range(var_2122);
                    start_for_10:;
                        if (iter_cmp(var_2197) == 0) goto end_for_10;
                        var_2198 = wp::iter_next(var_2197);
                        var_2199 = wp::extract(var_394, var_2198);
                        var_2200 = wp::extract(var_394, var_2198);
                        var_2202 = wp::address(var_tri, var_2194, var_2201);
                        var_2204 = wp::address(var_tri, var_2194, var_2203);
                        var_2206 = wp::address(var_tri, var_2194, var_2205);
                        var_2208 = wp::load(var_2202);
                        var_2209 = wp::load(var_2204);
                        var_2210 = wp::load(var_2206);
                        var_2207 = closest_0(var_2200, var_2208, var_2209, var_2210);
                        var_2211 = wp::sub(var_2199, var_2207);
                        var_2212 = wp::length(var_2211);
                        var_2213 = wp::max(var_2196, var_2212);
                        wp::assign(var_2196, var_2213);
                        goto start_for_10;
                    end_for_10:;
                    // bound=wp.min(bound,candidate)                                              <L 80>
                    var_2214 = wp::min(var_2165, var_2196);
                    // if bound<=target:break                                                     <L 81>
                    var_2215 = (var_2214 <= var_target);
                    if (var_2215) {
                        wp::assign(var_2191, var_2198);
                        wp::assign(var_2146, var_2194);
                        wp::assign(var_2165, var_2214);
                        goto end_for_8;
                    }
                    var_2216 = wp::where(var_2215, var_2191, var_2198);
                    var_2217 = wp::where(var_2215, var_2146, var_2194);
                    var_2218 = wp::where(var_2215, var_2165, var_2214);
                    wp::assign(var_2191, var_2216);
                    wp::assign(var_2146, var_2217);
                    wp::assign(var_2165, var_2218);
                    goto start_for_8;
                end_for_8:;
            }
            var_2219 = wp::where(var_2183, var_2192, var_2167);
            var_2220 = wp::where(var_2183, var_2191, var_1712);
            // wp.atomic_max(upper,0,bound)                                                       <L 82>
            var_2222 = wp::atomic_max(var_upper, var_2221, var_2165);
            // if bound>target:wp.atomic_max(unresolved,i,1)                                      <L 83>
            var_2223 = (var_2165 > var_target);
            if (var_2223) {
                var_2225 = wp::atomic_max(var_unresolved, var_9, var_2224);
            }
            goto start_for_0;
        end_for_0:;
    }
}



extern "C" __global__ void select_volume_b38c8631_cuda_kernel_forward(
    wp::launch_bounds_t<1> dim,
    wp::array_t<wp::mat_t<4, 3, wp::float64>> var_tets,
    wp::vec_t<3, wp::float64> var_lo,
    wp::vec_t<3, wp::float64> var_hi,
    wp::array_t<wp::int32> var_count,
    wp::array_t<wp::int32> var_ids)
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
        wp::mat_t<4, 3, wp::float64>* var_1;
        wp::mat_t<4, 3, wp::float64> var_2;
        wp::mat_t<4, 3, wp::float64> var_3;
        const bool var_4 = true;
        const wp::int32 var_5 = 0;
        const wp::int32 var_6 = 0;
        wp::float64 var_7;
        const wp::int32 var_8 = 1;
        wp::float64 var_9;
        wp::float64 var_10;
        const wp::int32 var_11 = 2;
        wp::float64 var_12;
        const wp::int32 var_13 = 3;
        wp::float64 var_14;
        wp::float64 var_15;
        wp::float64 var_16;
        const wp::int32 var_17 = 0;
        wp::float64 var_18;
        const wp::int32 var_19 = 1;
        wp::float64 var_20;
        wp::float64 var_21;
        const wp::int32 var_22 = 2;
        wp::float64 var_23;
        const wp::int32 var_24 = 3;
        wp::float64 var_25;
        wp::float64 var_26;
        wp::float64 var_27;
        bool var_28;
        wp::float64 var_29;
        wp::float64 var_30;
        wp::float64 var_31;
        bool var_32;
        wp::float64 var_33;
        wp::float64 var_34;
        wp::float64 var_35;
        bool var_36;
        const bool var_37 = false;
        bool var_38;
        const wp::int32 var_39 = 1;
        const wp::int32 var_40 = 0;
        wp::float64 var_41;
        const wp::int32 var_42 = 1;
        wp::float64 var_43;
        wp::float64 var_44;
        const wp::int32 var_45 = 2;
        wp::float64 var_46;
        const wp::int32 var_47 = 3;
        wp::float64 var_48;
        wp::float64 var_49;
        wp::float64 var_50;
        const wp::int32 var_51 = 0;
        wp::float64 var_52;
        const wp::int32 var_53 = 1;
        wp::float64 var_54;
        wp::float64 var_55;
        const wp::int32 var_56 = 2;
        wp::float64 var_57;
        const wp::int32 var_58 = 3;
        wp::float64 var_59;
        wp::float64 var_60;
        wp::float64 var_61;
        bool var_62;
        wp::float64 var_63;
        wp::float64 var_64;
        wp::float64 var_65;
        bool var_66;
        wp::float64 var_67;
        wp::float64 var_68;
        wp::float64 var_69;
        bool var_70;
        const bool var_71 = false;
        bool var_72;
        const wp::int32 var_73 = 2;
        const wp::int32 var_74 = 0;
        wp::float64 var_75;
        const wp::int32 var_76 = 1;
        wp::float64 var_77;
        wp::float64 var_78;
        const wp::int32 var_79 = 2;
        wp::float64 var_80;
        const wp::int32 var_81 = 3;
        wp::float64 var_82;
        wp::float64 var_83;
        wp::float64 var_84;
        const wp::int32 var_85 = 0;
        wp::float64 var_86;
        const wp::int32 var_87 = 1;
        wp::float64 var_88;
        wp::float64 var_89;
        const wp::int32 var_90 = 2;
        wp::float64 var_91;
        const wp::int32 var_92 = 3;
        wp::float64 var_93;
        wp::float64 var_94;
        wp::float64 var_95;
        bool var_96;
        wp::float64 var_97;
        wp::float64 var_98;
        wp::float64 var_99;
        bool var_100;
        wp::float64 var_101;
        wp::float64 var_102;
        wp::float64 var_103;
        bool var_104;
        const bool var_105 = false;
        bool var_106;
        const wp::int32 var_107 = 0;
        const wp::int32 var_108 = 1;
        wp::int32 var_109;
        //---------
        // forward
        // def select_volume(tets:wp.array(dtype=M43),lo:wp.vec3d,hi:wp.vec3d,count:wp.array(dtype=int),ids:wp.array(dtype=int)):       <L 25>
        // i=wp.tid();a=tets[i];overlap=True                                                      <L 26>
        var_0 = builtin_tid1d();
        var_1 = wp::address(var_tets, var_0);
        var_3 = wp::load(var_1);
        var_2 = wp::copy(var_3);
        // for k in range(3):                                                                     <L 27>
        // amin=wp.min(wp.min(a[0,k],a[1,k]),wp.min(a[2,k],a[3,k]));amax=wp.max(wp.max(a[0,k],a[1,k]),wp.max(a[2,k],a[3,k]))       <L 28>
        var_7 = wp::extract(var_2, var_6, var_5);
        var_9 = wp::extract(var_2, var_8, var_5);
        var_10 = wp::min(var_7, var_9);
        var_12 = wp::extract(var_2, var_11, var_5);
        var_14 = wp::extract(var_2, var_13, var_5);
        var_15 = wp::min(var_12, var_14);
        var_16 = wp::min(var_10, var_15);
        var_18 = wp::extract(var_2, var_17, var_5);
        var_20 = wp::extract(var_2, var_19, var_5);
        var_21 = wp::max(var_18, var_20);
        var_23 = wp::extract(var_2, var_22, var_5);
        var_25 = wp::extract(var_2, var_24, var_5);
        var_26 = wp::max(var_23, var_25);
        var_27 = wp::max(var_21, var_26);
        // if amax+wp.float64(1e-12)<lo[k] or hi[k]+wp.float64(1e-12)<amin:overlap=False          <L 29>
        var_29 = 1e-12;
        var_30 = wp::add(var_27, var_29);
        var_31 = wp::extract(var_lo, var_5);
        var_32 = (var_30 < var_31);
        var_28 = var_32;
        if (!var_28) {
            var_33 = wp::extract(var_hi, var_5);
            var_34 = 1e-12;
            var_35 = wp::add(var_33, var_34);
            var_36 = (var_35 < var_16);
            var_28 = var_28 || var_36;
        }
        if (var_28) {
        }
        var_38 = wp::where(var_28, var_37, var_4);
        // amin=wp.min(wp.min(a[0,k],a[1,k]),wp.min(a[2,k],a[3,k]));amax=wp.max(wp.max(a[0,k],a[1,k]),wp.max(a[2,k],a[3,k]))       <L 28>
        var_41 = wp::extract(var_2, var_40, var_39);
        var_43 = wp::extract(var_2, var_42, var_39);
        var_44 = wp::min(var_41, var_43);
        var_46 = wp::extract(var_2, var_45, var_39);
        var_48 = wp::extract(var_2, var_47, var_39);
        var_49 = wp::min(var_46, var_48);
        var_50 = wp::min(var_44, var_49);
        var_52 = wp::extract(var_2, var_51, var_39);
        var_54 = wp::extract(var_2, var_53, var_39);
        var_55 = wp::max(var_52, var_54);
        var_57 = wp::extract(var_2, var_56, var_39);
        var_59 = wp::extract(var_2, var_58, var_39);
        var_60 = wp::max(var_57, var_59);
        var_61 = wp::max(var_55, var_60);
        // if amax+wp.float64(1e-12)<lo[k] or hi[k]+wp.float64(1e-12)<amin:overlap=False          <L 29>
        var_63 = 1e-12;
        var_64 = wp::add(var_61, var_63);
        var_65 = wp::extract(var_lo, var_39);
        var_66 = (var_64 < var_65);
        var_62 = var_66;
        if (!var_62) {
            var_67 = wp::extract(var_hi, var_39);
            var_68 = 1e-12;
            var_69 = wp::add(var_67, var_68);
            var_70 = (var_69 < var_50);
            var_62 = var_62 || var_70;
        }
        if (var_62) {
        }
        var_72 = wp::where(var_62, var_71, var_38);
        // amin=wp.min(wp.min(a[0,k],a[1,k]),wp.min(a[2,k],a[3,k]));amax=wp.max(wp.max(a[0,k],a[1,k]),wp.max(a[2,k],a[3,k]))       <L 28>
        var_75 = wp::extract(var_2, var_74, var_73);
        var_77 = wp::extract(var_2, var_76, var_73);
        var_78 = wp::min(var_75, var_77);
        var_80 = wp::extract(var_2, var_79, var_73);
        var_82 = wp::extract(var_2, var_81, var_73);
        var_83 = wp::min(var_80, var_82);
        var_84 = wp::min(var_78, var_83);
        var_86 = wp::extract(var_2, var_85, var_73);
        var_88 = wp::extract(var_2, var_87, var_73);
        var_89 = wp::max(var_86, var_88);
        var_91 = wp::extract(var_2, var_90, var_73);
        var_93 = wp::extract(var_2, var_92, var_73);
        var_94 = wp::max(var_91, var_93);
        var_95 = wp::max(var_89, var_94);
        // if amax+wp.float64(1e-12)<lo[k] or hi[k]+wp.float64(1e-12)<amin:overlap=False          <L 29>
        var_97 = 1e-12;
        var_98 = wp::add(var_95, var_97);
        var_99 = wp::extract(var_lo, var_73);
        var_100 = (var_98 < var_99);
        var_96 = var_100;
        if (!var_96) {
            var_101 = wp::extract(var_hi, var_73);
            var_102 = 1e-12;
            var_103 = wp::add(var_101, var_102);
            var_104 = (var_103 < var_84);
            var_96 = var_96 || var_104;
        }
        if (var_96) {
        }
        var_106 = wp::where(var_96, var_105, var_72);
        // if overlap:slot=wp.atomic_add(count,0,1);ids[slot]=i                                   <L 30>
        if (var_106) {
            var_109 = wp::atomic_add(var_count, var_107, var_108);
            wp::array_store(var_ids, var_109, var_0);
        }
    }
}


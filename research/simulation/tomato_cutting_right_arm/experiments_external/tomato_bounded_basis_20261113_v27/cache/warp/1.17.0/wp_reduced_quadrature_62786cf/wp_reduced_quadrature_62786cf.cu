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


struct Signed_7e3cff60
{
    wp::float64 phi;
    wp::vec_t<3, wp::float64> normal;


    Signed_7e3cff60() = default;
    CUDA_CALLABLE Signed_7e3cff60(wp::float64 const& phi,
    wp::vec_t<3, wp::float64> const& normal = {})
        : phi{phi}
        , normal{normal}

    {
    }

    CUDA_CALLABLE Signed_7e3cff60& operator += (const Signed_7e3cff60& rhs)
    {    phi += rhs.phi;
    normal += rhs.normal;

        return *this;}

};

static CUDA_CALLABLE void adj_Signed_7e3cff60(wp::float64 const&,
    wp::vec_t<3, wp::float64> const&,
    wp::float64 & adj_phi,
    wp::vec_t<3, wp::float64> & adj_normal,
    Signed_7e3cff60 & adj_ret)
{
    adj_phi += adj_ret.phi;
    adj_normal += adj_ret.normal;
}

// Required when compiling adjoints.
CUDA_CALLABLE Signed_7e3cff60 add(const Signed_7e3cff60& a, const Signed_7e3cff60& b)
{
    return Signed_7e3cff60();
}

CUDA_CALLABLE void adj_atomic_add(Signed_7e3cff60* p, Signed_7e3cff60 t)
{
    wp::adj_atomic_add(&p->phi, t.phi);
    wp::adj_atomic_add(&p->normal, t.normal);
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


// /home/omen/Documents/Codex/experiments/tomato_bounded_basis_20261113_v27/src/inside_cad_gpu.py:9
static CUDA_CALLABLE Signed_7e3cff60 signed_inside_0(
    wp::array_t<wp::vec_t<3, wp::float64>> var_tri,
    wp::array_t<wp::int32> var_ptr,
    wp::array_t<wp::int32> var_ids,
    wp::int32 var_cell,
    wp::vec_t<3, wp::float64> var_p)
{
    //---------
    // primal vars
    wp::float64 var_0;
    const wp::int32 var_1 = -1;
    wp::int32 var_2;
    wp::float64 var_3;
    wp::vec_t<3, wp::float64> var_4;
    wp::int32* var_5;
    const wp::int32 var_6 = 1;
    wp::int32 var_7;
    wp::int32* var_8;
    wp::range_t var_9;
    wp::int32 var_10;
    wp::int32 var_11;
    wp::int32 var_12;
    wp::int32* var_13;
    wp::int32 var_14;
    wp::int32 var_15;
    const wp::int32 var_16 = 0;
    wp::vec_t<3, wp::float64>* var_17;
    const wp::int32 var_18 = 1;
    wp::vec_t<3, wp::float64>* var_19;
    const wp::int32 var_20 = 2;
    wp::vec_t<3, wp::float64>* var_21;
    wp::vec_t<3, wp::float64> var_22;
    wp::vec_t<3, wp::float64> var_23;
    wp::vec_t<3, wp::float64> var_24;
    wp::vec_t<3, wp::float64> var_25;
    wp::vec_t<3, wp::float64> var_26;
    wp::float64 var_27;
    bool var_28;
    wp::float64 var_29;
    wp::int32 var_30;
    wp::vec_t<3, wp::float64> var_31;
    wp::float64 var_32;
    wp::int32 var_33;
    wp::vec_t<3, wp::float64> var_34;
    Signed_7e3cff60 var_35;
    wp::float64 var_36;
    wp::float64 var_37;
    wp::float64 var_38;
    bool var_39;
    wp::vec_t<3, wp::float64> var_40;
    wp::vec_t<3, wp::float64> var_41;
    wp::vec_t<3, wp::float64> var_42;
    const wp::int32 var_43 = 1;
    wp::vec_t<3, wp::float64>* var_44;
    const wp::int32 var_45 = 0;
    wp::vec_t<3, wp::float64>* var_46;
    wp::vec_t<3, wp::float64> var_47;
    wp::vec_t<3, wp::float64> var_48;
    wp::vec_t<3, wp::float64> var_49;
    const wp::int32 var_50 = 2;
    wp::vec_t<3, wp::float64>* var_51;
    const wp::int32 var_52 = 0;
    wp::vec_t<3, wp::float64>* var_53;
    wp::vec_t<3, wp::float64> var_54;
    wp::vec_t<3, wp::float64> var_55;
    wp::vec_t<3, wp::float64> var_56;
    wp::vec_t<3, wp::float64> var_57;
    wp::vec_t<3, wp::float64> var_58;
    //---------
    // forward
    // def signed_inside(tri:wp.array2d(dtype=wp.vec3d),ptr:wp.array(dtype=int),ids:wp.array(dtype=int),cell:int,p:wp.vec3d):       <L 10>
    // best=wp.float64(1e30);face=int(-1);q=wp.vec3d(wp.float64(0.))                          <L 11>
    var_0 = 1e+30;
    var_2 = wp::int(var_1);
    var_3 = 0.0;
    var_4 = wp::vec_t<3, wp::float64>(var_3);
    // for j in range(ptr[cell],ptr[cell+1]):                                                 <L 12>
    var_5 = wp::address(var_ptr, var_cell);
    var_7 = wp::add(var_cell, var_6);
    var_8 = wp::address(var_ptr, var_7);
    var_10 = wp::load(var_5);
    var_11 = wp::load(var_8);
    var_9 = wp::range(var_10, var_11);
    start_for_0:;
        if (iter_cmp(var_9) == 0) goto end_for_0;
        var_12 = wp::iter_next(var_9);
        // k=ids[j];c=closest(p,tri[k,0],tri[k,1],tri[k,2]);d=wp.length_sq(p-c)               <L 13>
        var_13 = wp::address(var_ids, var_12);
        var_15 = wp::load(var_13);
        var_14 = wp::copy(var_15);
        var_17 = wp::address(var_tri, var_14, var_16);
        var_19 = wp::address(var_tri, var_14, var_18);
        var_21 = wp::address(var_tri, var_14, var_20);
        var_23 = wp::load(var_17);
        var_24 = wp::load(var_19);
        var_25 = wp::load(var_21);
        var_22 = closest_0(var_p, var_23, var_24, var_25);
        var_26 = wp::sub(var_p, var_22);
        var_27 = wp::length_sq(var_26);
        // if d<best:best=d;face=k;q=c                                                        <L 14>
        var_28 = (var_27 < var_0);
        if (var_28) {
            var_29 = wp::copy(var_27);
            var_30 = wp::copy(var_14);
            var_31 = wp::copy(var_22);
        }
        var_32 = wp::where(var_28, var_29, var_0);
        var_33 = wp::where(var_28, var_30, var_2);
        var_34 = wp::where(var_28, var_31, var_4);
        wp::assign(var_0, var_32);
        wp::assign(var_2, var_33);
        wp::assign(var_4, var_34);
        goto start_for_0;
    end_for_0:;
    // r=Signed();length=wp.sqrt(best);r.phi=-length                                          <L 15>
    var_35 = Signed_7e3cff60();
    var_36 = wp::sqrt(var_0);
    var_37 = wp::neg(var_36);
    var_35.phi = var_37;
    // if length>wp.float64(1e-15):r.normal=-(p-q)/length                                     <L 16>
    var_38 = 1e-15;
    var_39 = (var_36 > var_38);
    if (var_39) {
        var_40 = wp::sub(var_p, var_4);
        var_41 = wp::neg(var_40);
        var_42 = wp::div(var_41, var_36);
        var_35.normal = var_42;
    }
    if (!var_39) {
        // else:r.normal=wp.normalize(wp.cross(tri[face,1]-tri[face,0],tri[face,2]-tri[face,0]))       <L 17>
        var_44 = wp::address(var_tri, var_2, var_43);
        var_46 = wp::address(var_tri, var_2, var_45);
        var_48 = wp::load(var_44);
        var_49 = wp::load(var_46);
        var_47 = wp::sub(var_48, var_49);
        var_51 = wp::address(var_tri, var_2, var_50);
        var_53 = wp::address(var_tri, var_2, var_52);
        var_55 = wp::load(var_51);
        var_56 = wp::load(var_53);
        var_54 = wp::sub(var_55, var_56);
        var_57 = wp::cross(var_47, var_54);
        var_58 = wp::normalize(var_57);
        var_35.normal = var_58;
    }
    // return r                                                                               <L 18>
    return var_35;
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


// /home/omen/Documents/Codex/experiments/tomato_bounded_basis_20261113_v27/src/inside_cad_gpu.py:9
static CUDA_CALLABLE void adj_signed_inside_0(
    wp::array_t<wp::vec_t<3, wp::float64>> var_tri,
    wp::array_t<wp::int32> var_ptr,
    wp::array_t<wp::int32> var_ids,
    wp::int32 var_cell,
    wp::vec_t<3, wp::float64> var_p,
    wp::array_t<wp::vec_t<3, wp::float64>> & adj_tri,
    wp::array_t<wp::int32> & adj_ptr,
    wp::array_t<wp::int32> & adj_ids,
    wp::int32 & adj_cell,
    wp::vec_t<3, wp::float64> & adj_p,
    Signed_7e3cff60 & adj_ret)
{
	// reverse mode disabled (module option "enable_backward" is False or no dependent kernel found with "enable_backward")
}



extern "C" __global__ void integrate_reduced_8c94dd27_cuda_kernel_forward(
    wp::launch_bounds_t<1> dim,
    wp::uint64 var_mesh,
    wp::array_t<wp::vec_t<3, wp::float64>> var_tri,
    wp::array_t<wp::int32> var_iptr,
    wp::array_t<wp::int32> var_iids,
    wp::array_t<wp::int32> var_cells,
    wp::mat_t<3, 3, wp::float64> var_R,
    wp::array_t<wp::vec_t<3, wp::float64>> var_pose,
    wp::array_t<wp::mat_t<3, 3, wp::float64>> var_X,
    wp::array_t<wp::mat_t<3, 3, wp::float64>> var_V,
    wp::array_t<wp::float64> var_areas,
    wp::array_t<wp::mat_t<3, 3, wp::float64>> var_masters,
    wp::array_t<wp::vec_t<3, wp::float64>> var_polygon,
    wp::array_t<wp::int32> var_counts,
    wp::array_t<wp::int32> var_faces,
    wp::array_t<wp::int32> var_active,
    wp::array_t<wp::int32> var_bad,
    wp::array_t<wp::vec_t<3, wp::float64>> var_ff,
    wp::array_t<wp::float64> var_uu,
    wp::array_t<wp::float64> var_dd,
    wp::array_t<wp::float64> var_ww,
    wp::array_t<wp::vec_t<3, wp::float64>> var_mm)
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
        wp::shape_t* var_1;
        const wp::int32 var_2 = 0;
        wp::int32 var_3;
        wp::shape_t var_4;
        const wp::int32 var_5 = 128;
        wp::int32 var_6;
        const wp::int32 var_7 = 128;
        wp::int32 var_8;
        wp::int32 var_9;
        wp::int32 var_10;
        const wp::int32 var_11 = 0;
        wp::int32* var_12;
        const wp::int32 var_13 = 64;
        wp::range_t var_14;
        wp::int32 var_15;
        wp::int32 var_16;
        const wp::int32 var_17 = 0;
        wp::int32* var_18;
        const wp::int32 var_19 = 0;
        bool var_20;
        wp::int32 var_21;
        wp::int32* var_22;
        wp::int32 var_23;
        wp::int32 var_24;
        wp::int32* var_25;
        wp::int32 var_26;
        wp::int32 var_27;
        wp::float64 var_28;
        wp::mat_t<3, 3, wp::float64> var_29;
        wp::float64 var_30;
        wp::float64 var_31;
        wp::float64 var_32;
        wp::float64 var_33;
        wp::vec_t<3, wp::float64> var_34;
        const wp::int32 var_35 = 2;
        wp::int32 var_36;
        bool var_37;
        const wp::int32 var_38 = 0;
        wp::vec_t<3, wp::float64>* var_39;
        const wp::int32 var_40 = 1;
        wp::int32 var_41;
        wp::vec_t<3, wp::float64>* var_42;
        const wp::int32 var_43 = 2;
        wp::int32 var_44;
        wp::vec_t<3, wp::float64>* var_45;
        wp::mat_t<3, 3, wp::float64> var_46;
        wp::vec_t<3, wp::float64> var_47;
        wp::vec_t<3, wp::float64> var_48;
        wp::vec_t<3, wp::float64> var_49;
        wp::float64* var_50;
        wp::float64 var_51;
        wp::float64 var_52;
        wp::float64 var_53;
        wp::float64 var_54;
        wp::float64 var_55;
        wp::float64 var_56;
        wp::mat_t<3, 3, wp::float64>* var_57;
        wp::mat_t<3, 3, wp::float64> var_58;
        wp::mat_t<3, 3, wp::float64> var_59;
        wp::mat_t<3, 3, wp::float64>* var_60;
        wp::mat_t<3, 3, wp::float64> var_61;
        wp::mat_t<3, 3, wp::float64> var_62;
        wp::mat_t<3, 3, wp::float64>* var_63;
        wp::mat_t<3, 3, wp::float64> var_64;
        wp::mat_t<3, 3, wp::float64> var_65;
        const wp::int32 var_66 = 0;
        wp::vec_t<3, wp::float64>* var_67;
        wp::vec_t<3, wp::float64> var_68;
        wp::vec_t<3, wp::float64> var_69;
        const wp::int32 var_70 = 1;
        wp::vec_t<3, wp::float64>* var_71;
        wp::vec_t<3, wp::float64> var_72;
        wp::vec_t<3, wp::float64> var_73;
        wp::float64 var_74;
        wp::mat_t<3, 3, wp::float64> var_75;
        wp::float64 var_76;
        wp::float64 var_77;
        wp::float64 var_78;
        wp::float64 var_79;
        wp::vec_t<3, wp::float64> var_80;
        const wp::int32 var_81 = 0;
        const wp::float32 var_82 = 1.0;
        const wp::float32 var_83 = 6.0;
        wp::float32 var_84;
        wp::float64 var_85;
        wp::vec_t<3, wp::float64> var_86;
        const wp::float32 var_87 = 2.0;
        const wp::float32 var_88 = 3.0;
        wp::float32 var_89;
        wp::float64 var_90;
        wp::mat_t<3, 3, wp::float64> var_91;
        wp::vec_t<3, wp::float64> var_92;
        wp::mat_t<3, 3, wp::float64> var_93;
        wp::vec_t<3, wp::float64> var_94;
        wp::mat_t<3, 3, wp::float64> var_95;
        wp::vec_t<3, wp::float64> var_96;
        wp::int32* var_97;
        wp::mat_t<3, 3, wp::float64> var_98;
        wp::vec_t<3, wp::float64> var_99;
        wp::vec_t<3, wp::float64> var_100;
        Signed_7e3cff60 var_101;
        wp::int32 var_102;
        wp::float64* var_103;
        wp::float64 var_104;
        wp::float64 var_105;
        wp::float64 var_106;
        wp::float64 var_107;
        wp::vec_t<3, wp::float64>* var_108;
        wp::vec_t<3, wp::float64> var_109;
        wp::vec_t<3, wp::float64> var_110;
        wp::float64 var_111;
        wp::float64 var_112;
        wp::float64 var_113;
        wp::float64 var_114;
        wp::float64 var_115;
        wp::vec_t<3, wp::float64> var_116;
        wp::float64 var_117;
        wp::vec_t<3, wp::float64> var_118;
        wp::vec_t<3, wp::float64> var_119;
        wp::float64 var_120;
        wp::float64 var_121;
        wp::vec_t<3, wp::float64> var_122;
        wp::float64 var_123;
        bool var_124;
        wp::float64 var_125;
        wp::float64 var_126;
        wp::float64 var_127;
        wp::float64 var_128;
        wp::float64 var_129;
        wp::float64 var_130;
        wp::float64 var_131;
        wp::vec_t<3, wp::float64> var_132;
        wp::vec_t<3, wp::float64> var_133;
        wp::vec_t<3, wp::float64> var_134;
        wp::vec_t<3, wp::float64> var_135;
        wp::vec_t<3, wp::float64> var_136;
        const wp::int32 var_137 = 0;
        const wp::int32 var_138 = 0;
        wp::float64 var_139;
        wp::float64 var_140;
        wp::float64 var_141;
        const wp::int32 var_142 = 1;
        wp::float64 var_143;
        wp::float64 var_144;
        wp::float64 var_145;
        const wp::int32 var_146 = 2;
        wp::float64 var_147;
        wp::float64 var_148;
        wp::float64 var_149;
        const wp::int32 var_150 = 1;
        const wp::int32 var_151 = 0;
        wp::float64 var_152;
        wp::float64 var_153;
        wp::float64 var_154;
        const wp::int32 var_155 = 1;
        wp::float64 var_156;
        wp::float64 var_157;
        wp::float64 var_158;
        const wp::int32 var_159 = 2;
        wp::float64 var_160;
        wp::float64 var_161;
        wp::float64 var_162;
        const wp::int32 var_163 = 2;
        const wp::int32 var_164 = 0;
        wp::float64 var_165;
        wp::float64 var_166;
        wp::float64 var_167;
        const wp::int32 var_168 = 1;
        wp::float64 var_169;
        wp::float64 var_170;
        wp::float64 var_171;
        const wp::int32 var_172 = 2;
        wp::float64 var_173;
        wp::float64 var_174;
        wp::float64 var_175;
        wp::float64 var_176;
        wp::float64 var_177;
        wp::float64 var_178;
        wp::float64 var_179;
        wp::float64 var_180;
        wp::float64 var_181;
        wp::float64 var_182;
        wp::float64 var_183;
        wp::vec_t<3, wp::float64> var_184;
        wp::vec_t<3, wp::float64> var_185;
        wp::vec_t<3, wp::float64> var_186;
        const wp::int32 var_187 = 1;
        const wp::float32 var_188 = 1.0;
        const wp::float32 var_189 = 6.0;
        wp::float32 var_190;
        wp::float64 var_191;
        wp::vec_t<3, wp::float64> var_192;
        const wp::float32 var_193 = 2.0;
        const wp::float32 var_194 = 3.0;
        wp::float32 var_195;
        wp::float64 var_196;
        wp::mat_t<3, 3, wp::float64> var_197;
        wp::vec_t<3, wp::float64> var_198;
        wp::mat_t<3, 3, wp::float64> var_199;
        wp::vec_t<3, wp::float64> var_200;
        wp::mat_t<3, 3, wp::float64> var_201;
        wp::vec_t<3, wp::float64> var_202;
        wp::int32* var_203;
        wp::mat_t<3, 3, wp::float64> var_204;
        wp::vec_t<3, wp::float64> var_205;
        wp::vec_t<3, wp::float64> var_206;
        Signed_7e3cff60 var_207;
        wp::int32 var_208;
        wp::float64* var_209;
        wp::float64 var_210;
        wp::float64 var_211;
        wp::float64 var_212;
        wp::float64 var_213;
        wp::vec_t<3, wp::float64>* var_214;
        wp::vec_t<3, wp::float64> var_215;
        wp::vec_t<3, wp::float64> var_216;
        wp::float64 var_217;
        wp::float64 var_218;
        wp::float64 var_219;
        wp::float64 var_220;
        wp::float64 var_221;
        wp::vec_t<3, wp::float64> var_222;
        wp::float64 var_223;
        wp::vec_t<3, wp::float64> var_224;
        wp::vec_t<3, wp::float64> var_225;
        wp::float64 var_226;
        wp::float64 var_227;
        wp::vec_t<3, wp::float64> var_228;
        wp::float64 var_229;
        bool var_230;
        wp::float64 var_231;
        wp::float64 var_232;
        wp::float64 var_233;
        wp::float64 var_234;
        wp::float64 var_235;
        wp::float64 var_236;
        wp::float64 var_237;
        wp::vec_t<3, wp::float64> var_238;
        wp::vec_t<3, wp::float64> var_239;
        wp::vec_t<3, wp::float64> var_240;
        wp::vec_t<3, wp::float64> var_241;
        wp::vec_t<3, wp::float64> var_242;
        const wp::int32 var_243 = 0;
        const wp::int32 var_244 = 0;
        wp::float64 var_245;
        wp::float64 var_246;
        wp::float64 var_247;
        const wp::int32 var_248 = 1;
        wp::float64 var_249;
        wp::float64 var_250;
        wp::float64 var_251;
        const wp::int32 var_252 = 2;
        wp::float64 var_253;
        wp::float64 var_254;
        wp::float64 var_255;
        const wp::int32 var_256 = 1;
        const wp::int32 var_257 = 0;
        wp::float64 var_258;
        wp::float64 var_259;
        wp::float64 var_260;
        const wp::int32 var_261 = 1;
        wp::float64 var_262;
        wp::float64 var_263;
        wp::float64 var_264;
        const wp::int32 var_265 = 2;
        wp::float64 var_266;
        wp::float64 var_267;
        wp::float64 var_268;
        const wp::int32 var_269 = 2;
        const wp::int32 var_270 = 0;
        wp::float64 var_271;
        wp::float64 var_272;
        wp::float64 var_273;
        const wp::int32 var_274 = 1;
        wp::float64 var_275;
        wp::float64 var_276;
        wp::float64 var_277;
        const wp::int32 var_278 = 2;
        wp::float64 var_279;
        wp::float64 var_280;
        wp::float64 var_281;
        wp::float64 var_282;
        wp::float64 var_283;
        wp::float64 var_284;
        wp::float64 var_285;
        wp::float64 var_286;
        wp::float64 var_287;
        wp::float64 var_288;
        wp::float64 var_289;
        wp::vec_t<3, wp::float64> var_290;
        wp::vec_t<3, wp::float64> var_291;
        wp::vec_t<3, wp::float64> var_292;
        const wp::int32 var_293 = 2;
        const wp::float32 var_294 = 1.0;
        const wp::float32 var_295 = 6.0;
        wp::float32 var_296;
        wp::float64 var_297;
        wp::vec_t<3, wp::float64> var_298;
        const wp::float32 var_299 = 2.0;
        const wp::float32 var_300 = 3.0;
        wp::float32 var_301;
        wp::float64 var_302;
        wp::mat_t<3, 3, wp::float64> var_303;
        wp::vec_t<3, wp::float64> var_304;
        wp::mat_t<3, 3, wp::float64> var_305;
        wp::vec_t<3, wp::float64> var_306;
        wp::mat_t<3, 3, wp::float64> var_307;
        wp::vec_t<3, wp::float64> var_308;
        wp::int32* var_309;
        wp::mat_t<3, 3, wp::float64> var_310;
        wp::vec_t<3, wp::float64> var_311;
        wp::vec_t<3, wp::float64> var_312;
        Signed_7e3cff60 var_313;
        wp::int32 var_314;
        wp::float64* var_315;
        wp::float64 var_316;
        wp::float64 var_317;
        wp::float64 var_318;
        wp::float64 var_319;
        wp::vec_t<3, wp::float64>* var_320;
        wp::vec_t<3, wp::float64> var_321;
        wp::vec_t<3, wp::float64> var_322;
        wp::float64 var_323;
        wp::float64 var_324;
        wp::float64 var_325;
        wp::float64 var_326;
        wp::float64 var_327;
        wp::vec_t<3, wp::float64> var_328;
        wp::float64 var_329;
        wp::vec_t<3, wp::float64> var_330;
        wp::vec_t<3, wp::float64> var_331;
        wp::float64 var_332;
        wp::float64 var_333;
        wp::vec_t<3, wp::float64> var_334;
        wp::float64 var_335;
        bool var_336;
        wp::float64 var_337;
        wp::float64 var_338;
        wp::float64 var_339;
        wp::float64 var_340;
        wp::float64 var_341;
        wp::float64 var_342;
        wp::float64 var_343;
        wp::vec_t<3, wp::float64> var_344;
        wp::vec_t<3, wp::float64> var_345;
        wp::vec_t<3, wp::float64> var_346;
        wp::vec_t<3, wp::float64> var_347;
        wp::vec_t<3, wp::float64> var_348;
        const wp::int32 var_349 = 0;
        const wp::int32 var_350 = 0;
        wp::float64 var_351;
        wp::float64 var_352;
        wp::float64 var_353;
        const wp::int32 var_354 = 1;
        wp::float64 var_355;
        wp::float64 var_356;
        wp::float64 var_357;
        const wp::int32 var_358 = 2;
        wp::float64 var_359;
        wp::float64 var_360;
        wp::float64 var_361;
        const wp::int32 var_362 = 1;
        const wp::int32 var_363 = 0;
        wp::float64 var_364;
        wp::float64 var_365;
        wp::float64 var_366;
        const wp::int32 var_367 = 1;
        wp::float64 var_368;
        wp::float64 var_369;
        wp::float64 var_370;
        const wp::int32 var_371 = 2;
        wp::float64 var_372;
        wp::float64 var_373;
        wp::float64 var_374;
        const wp::int32 var_375 = 2;
        const wp::int32 var_376 = 0;
        wp::float64 var_377;
        wp::float64 var_378;
        wp::float64 var_379;
        const wp::int32 var_380 = 1;
        wp::float64 var_381;
        wp::float64 var_382;
        wp::float64 var_383;
        const wp::int32 var_384 = 2;
        wp::float64 var_385;
        wp::float64 var_386;
        wp::float64 var_387;
        wp::float64 var_388;
        wp::float64 var_389;
        wp::float64 var_390;
        wp::float64 var_391;
        wp::float64 var_392;
        wp::float64 var_393;
        wp::float64 var_394;
        wp::float64 var_395;
        wp::vec_t<3, wp::float64> var_396;
        wp::vec_t<3, wp::float64> var_397;
        wp::vec_t<3, wp::float64> var_398;
        wp::mat_t<3, 3, wp::float64> var_399;
        wp::float64 var_400;
        wp::float64 var_401;
        wp::float64 var_402;
        wp::vec_t<3, wp::float64> var_403;
        const wp::int32 var_404 = 0;
        wp::vec_t<3, wp::float64> var_405;
        const bool var_406 = true;
        wp::tile_register_t<wp::vec_t<3, wp::float64>,wp::tile_layout_register_t<wp::tile_shape_t<128>>> var_407 = wp::tile_register_t<wp::vec_t<3, wp::float64>,wp::tile_layout_register_t<wp::tile_shape_t<128>>>{};
        wp::tile_shared_t<wp::vec_t<3, wp::float64>,wp::tile_layout_strided_t<wp::tile_shape_t<1>, wp::tile_stride_t<1>>, true> var_408 = wp::tile_alloc_empty<wp::vec_t<3, wp::float64>,wp::tile_shape_t<1>,wp::tile_stride_t<1>,false>();
        const wp::int32 var_409 = 1;
        wp::vec_t<3, wp::float64> var_410;
        const bool var_411 = true;
        wp::tile_register_t<wp::vec_t<3, wp::float64>,wp::tile_layout_register_t<wp::tile_shape_t<128>>> var_412 = wp::tile_register_t<wp::vec_t<3, wp::float64>,wp::tile_layout_register_t<wp::tile_shape_t<128>>>{};
        wp::tile_shared_t<wp::vec_t<3, wp::float64>,wp::tile_layout_strided_t<wp::tile_shape_t<1>, wp::tile_stride_t<1>>, true> var_413 = wp::tile_alloc_empty<wp::vec_t<3, wp::float64>,wp::tile_shape_t<1>,wp::tile_stride_t<1>,false>();
        const wp::int32 var_414 = 2;
        wp::vec_t<3, wp::float64> var_415;
        const bool var_416 = true;
        wp::tile_register_t<wp::vec_t<3, wp::float64>,wp::tile_layout_register_t<wp::tile_shape_t<128>>> var_417 = wp::tile_register_t<wp::vec_t<3, wp::float64>,wp::tile_layout_register_t<wp::tile_shape_t<128>>>{};
        wp::tile_shared_t<wp::vec_t<3, wp::float64>,wp::tile_layout_strided_t<wp::tile_shape_t<1>, wp::tile_stride_t<1>>, true> var_418 = wp::tile_alloc_empty<wp::vec_t<3, wp::float64>,wp::tile_shape_t<1>,wp::tile_stride_t<1>,false>();
        wp::tile_register_t<wp::float64,wp::tile_layout_register_t<wp::tile_shape_t<128>>> var_419 = wp::tile_register_t<wp::float64,wp::tile_layout_register_t<wp::tile_shape_t<128>>>{};
        wp::tile_shared_t<wp::float64,wp::tile_layout_strided_t<wp::tile_shape_t<1>, wp::tile_stride_t<1>>, true> var_420 = wp::tile_alloc_empty<wp::float64,wp::tile_shape_t<1>,wp::tile_stride_t<1>,false>();
        wp::tile_register_t<wp::float64,wp::tile_layout_register_t<wp::tile_shape_t<128>>> var_421 = wp::tile_register_t<wp::float64,wp::tile_layout_register_t<wp::tile_shape_t<128>>>{};
        wp::tile_shared_t<wp::float64,wp::tile_layout_strided_t<wp::tile_shape_t<1>, wp::tile_stride_t<1>>, true> var_422 = wp::tile_alloc_empty<wp::float64,wp::tile_shape_t<1>,wp::tile_stride_t<1>,false>();
        wp::tile_register_t<wp::float64,wp::tile_layout_register_t<wp::tile_shape_t<128>>> var_423 = wp::tile_register_t<wp::float64,wp::tile_layout_register_t<wp::tile_shape_t<128>>>{};
        wp::tile_shared_t<wp::float64,wp::tile_layout_strided_t<wp::tile_shape_t<1>, wp::tile_stride_t<1>>, true> var_424 = wp::tile_alloc_empty<wp::float64,wp::tile_shape_t<1>,wp::tile_stride_t<1>,false>();
        const bool var_425 = true;
        wp::tile_register_t<wp::vec_t<3, wp::float64>,wp::tile_layout_register_t<wp::tile_shape_t<128>>> var_426 = wp::tile_register_t<wp::vec_t<3, wp::float64>,wp::tile_layout_register_t<wp::tile_shape_t<128>>>{};
        wp::tile_shared_t<wp::vec_t<3, wp::float64>,wp::tile_layout_strided_t<wp::tile_shape_t<1>, wp::tile_stride_t<1>>, true> var_427 = wp::tile_alloc_empty<wp::vec_t<3, wp::float64>,wp::tile_shape_t<1>,wp::tile_stride_t<1>,false>();
        const wp::int32 var_428 = 0;
        bool var_429;
        const wp::int32 var_430 = 0;
        const wp::int32 var_431 = 0;
        wp::vec_t<3, wp::float64> var_432;
        wp::vec_t<3, wp::float64> var_433;
        const wp::int32 var_434 = 1;
        const wp::int32 var_435 = 0;
        wp::vec_t<3, wp::float64> var_436;
        wp::vec_t<3, wp::float64> var_437;
        const wp::int32 var_438 = 2;
        const wp::int32 var_439 = 0;
        wp::vec_t<3, wp::float64> var_440;
        wp::vec_t<3, wp::float64> var_441;
        const wp::int32 var_442 = 0;
        wp::float64 var_443;
        wp::float64 var_444;
        const wp::int32 var_445 = 0;
        wp::float64 var_446;
        wp::float64 var_447;
        const wp::int32 var_448 = 0;
        wp::float64 var_449;
        wp::float64 var_450;
        const wp::int32 var_451 = 0;
        wp::vec_t<3, wp::float64> var_452;
        wp::vec_t<3, wp::float64> var_453;
        //---------
        // forward
        // def integrate_reduced(mesh:wp.uint64,tri:wp.array2d(dtype=wp.vec3d),iptr:wp.array(dtype=int),iids:wp.array(dtype=int),cells:wp.array(dtype=int),R:wp.mat33d,pose:wp.array(dtype=wp.vec3d),X:wp.array(dtype=wp.mat33d),V:wp.array(dtype=wp.mat33d),areas:wp.array(dtype=wp.float64),masters:wp.array(dtype=wp.mat33d),polygon:wp.array2d(dtype=wp.vec3d),counts:wp.array(dtype=int),faces:wp.array(dtype=int),active:wp.array(dtype=int),bad:wp.array(dtype=int),ff:wp.array2d(dtype=wp.vec3d),uu:wp.array(dtype=wp.float64),dd:wp.array(dtype=wp.float64),ww:wp.array(dtype=wp.float64),mm:wp.array(dtype=wp.vec3d)):       <L 5>
        // thread=wp.tid();nm=masters.shape[0];first=thread//128;lane=thread%128;root=lane//nm;leaf=lane%nm       <L 6>
        var_0 = builtin_tid1d();
        var_1 = &(var_masters.shape);
        var_4 = wp::load(var_1);
        var_3 = wp::extract(var_4, var_2);
        var_6 = wp::floordiv(var_0, var_5);
        var_8 = wp::mod(var_0, var_7);
        var_9 = wp::floordiv(var_8, var_3);
        var_10 = wp::mod(var_8, var_3);
        // for slot in range(first,active[0],64):                                                 <L 7>
        var_12 = wp::address(var_active, var_11);
        var_15 = wp::load(var_12);
        var_14 = wp::range(var_6, var_15, var_13);
        start_for_0:;
            if (iter_cmp(var_14) == 0) goto end_for_0;
            var_16 = wp::iter_next(var_14);
            // if bad[0]!=0:break                                                                 <L 8>
            var_18 = wp::address(var_bad, var_17);
            var_21 = wp::load(var_18);
            var_20 = (var_21 != var_19);
            if (var_20) {
                goto end_for_0;
            }
            // face=faces[slot];n=counts[slot];forces=wp.mat33d(wp.float64(0.));U=wp.float64(0.);D=wp.float64(0.);W=wp.float64(0.);M=wp.vec3d(wp.float64(0.))       <L 9>
            var_22 = wp::address(var_faces, var_16);
            var_24 = wp::load(var_22);
            var_23 = wp::copy(var_24);
            var_25 = wp::address(var_counts, var_16);
            var_27 = wp::load(var_25);
            var_26 = wp::copy(var_27);
            var_28 = 0.0;
            var_29 = wp::mat_t<3, 3, wp::float64>(var_28);
            var_30 = 0.0;
            var_31 = 0.0;
            var_32 = 0.0;
            var_33 = 0.0;
            var_34 = wp::vec_t<3, wp::float64>(var_33);
            // if root<n-2:                                                                       <L 10>
            var_36 = wp::sub(var_26, var_35);
            var_37 = (var_9 < var_36);
            if (var_37) {
                // B=wp.matrix_from_rows(polygon[slot,0],polygon[slot,root+1],polygon[slot,root+2]);area=areas[face]*wp.abs(wp.determinant(B))/wp.float64(nm);B=masters[leaf]*B;x=X[face];v=V[face];T=pose[0];tv=pose[1];forces=wp.mat33d(wp.float64(0.));U=wp.float64(0.);D=wp.float64(0.);W=wp.float64(0.);M=wp.vec3d(wp.float64(0.))       <L 11>
                var_39 = wp::address(var_polygon, var_16, var_38);
                var_41 = wp::add(var_9, var_40);
                var_42 = wp::address(var_polygon, var_16, var_41);
                var_44 = wp::add(var_9, var_43);
                var_45 = wp::address(var_polygon, var_16, var_44);
                var_47 = wp::load(var_39);
                var_48 = wp::load(var_42);
                var_49 = wp::load(var_45);
                var_46 = wp::matrix_from_rows<wp::float64>(var_47, var_48, var_49);
                var_50 = wp::address(var_areas, var_23);
                var_51 = wp::determinant(var_46);
                var_52 = wp::abs(var_51);
                var_54 = wp::load(var_50);
                var_53 = wp::mul(var_54, var_52);
                var_55 = wp::float64(var_3);
                var_56 = wp::div(var_53, var_55);
                var_57 = wp::address(var_masters, var_10);
                var_59 = wp::load(var_57);
                var_58 = wp::mul(var_59, var_46);
                var_60 = wp::address(var_X, var_23);
                var_62 = wp::load(var_60);
                var_61 = wp::copy(var_62);
                var_63 = wp::address(var_V, var_23);
                var_65 = wp::load(var_63);
                var_64 = wp::copy(var_65);
                var_67 = wp::address(var_pose, var_66);
                var_69 = wp::load(var_67);
                var_68 = wp::copy(var_69);
                var_71 = wp::address(var_pose, var_70);
                var_73 = wp::load(var_71);
                var_72 = wp::copy(var_73);
                var_74 = 0.0;
                var_75 = wp::mat_t<3, 3, wp::float64>(var_74);
                var_76 = 0.0;
                var_77 = 0.0;
                var_78 = 0.0;
                var_79 = 0.0;
                var_80 = wp::vec_t<3, wp::float64>(var_79);
                // for k in range(3):                                                             <L 12>
                // rule=wp.vec3d(wp.float64(1./6.));rule[k]=wp.float64(2./3.);bary=wp.transpose(B)*rule;p=wp.transpose(x)*bary;vel=wp.transpose(v)*bary;s=signed_inside(tri,iptr,iids,cells[slot],wp.transpose(R)*(p-T));depth=wp.max(-s.phi,wp.float64(0.));normal=R*s.normal;fn=wp.float64(1e9)*area/wp.float64(3.)*depth;rel=vel-tv;tan=rel-wp.dot(rel,normal)*normal;speed=wp.length(tan);fr=wp.vec3d(wp.float64(0.))       <L 13>
                var_84 = wp::div(var_82, var_83);
                var_85 = wp::float64(var_84);
                var_86 = wp::vec_t<3, wp::float64>(var_85);
                var_89 = wp::div(var_87, var_88);
                var_90 = wp::float64(var_89);
                wp::assign_inplace(var_86, var_81, var_90);
                var_91 = wp::transpose(var_58);
                var_92 = wp::mul(var_91, var_86);
                var_93 = wp::transpose(var_61);
                var_94 = wp::mul(var_93, var_92);
                var_95 = wp::transpose(var_64);
                var_96 = wp::mul(var_95, var_92);
                var_97 = wp::address(var_cells, var_16);
                var_98 = wp::transpose(var_R);
                var_99 = wp::sub(var_94, var_68);
                var_100 = wp::mul(var_98, var_99);
                var_102 = wp::load(var_97);
                var_101 = signed_inside_0(var_tri, var_iptr, var_iids, var_102, var_100);
                var_103 = &((var_101).phi);
                var_105 = wp::load(var_103);
                var_104 = wp::neg(var_105);
                var_106 = 0.0;
                var_107 = wp::max(var_104, var_106);
                var_108 = &((var_101).normal);
                var_110 = wp::load(var_108);
                var_109 = wp::mul(var_R, var_110);
                var_111 = 1000000000.0;
                var_112 = wp::mul(var_111, var_56);
                var_113 = 3.0;
                var_114 = wp::div(var_112, var_113);
                var_115 = wp::mul(var_114, var_107);
                var_116 = wp::sub(var_96, var_72);
                var_117 = wp::dot(var_116, var_109);
                var_118 = wp::mul(var_117, var_109);
                var_119 = wp::sub(var_116, var_118);
                var_120 = wp::length(var_119);
                var_121 = 0.0;
                var_122 = wp::vec_t<3, wp::float64>(var_121);
                // if speed>wp.float64(1e-30):fr=-wp.float64(.2)*fn*wp.tanh(speed/wp.float64(.001))*tan/speed       <L 14>
                var_123 = 1e-30;
                var_124 = (var_120 > var_123);
                if (var_124) {
                    var_125 = 0.2;
                    var_126 = wp::neg(var_125);
                    var_127 = wp::mul(var_126, var_115);
                    var_128 = 0.001;
                    var_129 = wp::div(var_120, var_128);
                    var_130 = wp::tanh(var_129);
                    var_131 = wp::mul(var_127, var_130);
                    var_132 = wp::mul(var_131, var_119);
                    var_133 = wp::div(var_132, var_120);
                }
                var_134 = wp::where(var_124, var_133, var_122);
                // f=fn*normal+fr                                                                 <L 15>
                var_135 = wp::mul(var_115, var_109);
                var_136 = wp::add(var_135, var_134);
                // for u in range(3):                                                             <L 16>
                // for a in range(3):forces[u,a]+=bary[u]*f[a]                                    <L 17>
                var_139 = wp::extract(var_92, var_137);
                var_140 = wp::extract(var_136, var_138);
                var_141 = wp::mul(var_139, var_140);
                wp::add_inplace(var_75, var_137, var_138, var_141);
                var_143 = wp::extract(var_92, var_137);
                var_144 = wp::extract(var_136, var_142);
                var_145 = wp::mul(var_143, var_144);
                wp::add_inplace(var_75, var_137, var_142, var_145);
                var_147 = wp::extract(var_92, var_137);
                var_148 = wp::extract(var_136, var_146);
                var_149 = wp::mul(var_147, var_148);
                wp::add_inplace(var_75, var_137, var_146, var_149);
                var_152 = wp::extract(var_92, var_150);
                var_153 = wp::extract(var_136, var_151);
                var_154 = wp::mul(var_152, var_153);
                wp::add_inplace(var_75, var_150, var_151, var_154);
                var_156 = wp::extract(var_92, var_150);
                var_157 = wp::extract(var_136, var_155);
                var_158 = wp::mul(var_156, var_157);
                wp::add_inplace(var_75, var_150, var_155, var_158);
                var_160 = wp::extract(var_92, var_150);
                var_161 = wp::extract(var_136, var_159);
                var_162 = wp::mul(var_160, var_161);
                wp::add_inplace(var_75, var_150, var_159, var_162);
                var_165 = wp::extract(var_92, var_163);
                var_166 = wp::extract(var_136, var_164);
                var_167 = wp::mul(var_165, var_166);
                wp::add_inplace(var_75, var_163, var_164, var_167);
                var_169 = wp::extract(var_92, var_163);
                var_170 = wp::extract(var_136, var_168);
                var_171 = wp::mul(var_169, var_170);
                wp::add_inplace(var_75, var_163, var_168, var_171);
                var_173 = wp::extract(var_92, var_163);
                var_174 = wp::extract(var_136, var_172);
                var_175 = wp::mul(var_173, var_174);
                wp::add_inplace(var_75, var_163, var_172, var_175);
                // U+=wp.float64(.5)*fn*depth;D-=wp.dot(fr,rel);W+=wp.dot(f,tv);M+=wp.cross(p-T,f)       <L 18>
                var_176 = 0.5;
                var_177 = wp::mul(var_176, var_115);
                var_178 = wp::mul(var_177, var_107);
                var_179 = wp::add(var_76, var_178);
                var_180 = wp::dot(var_134, var_116);
                var_181 = wp::sub(var_77, var_180);
                var_182 = wp::dot(var_136, var_72);
                var_183 = wp::add(var_78, var_182);
                var_184 = wp::sub(var_94, var_68);
                var_185 = wp::cross(var_184, var_136);
                var_186 = wp::add(var_80, var_185);
                // rule=wp.vec3d(wp.float64(1./6.));rule[k]=wp.float64(2./3.);bary=wp.transpose(B)*rule;p=wp.transpose(x)*bary;vel=wp.transpose(v)*bary;s=signed_inside(tri,iptr,iids,cells[slot],wp.transpose(R)*(p-T));depth=wp.max(-s.phi,wp.float64(0.));normal=R*s.normal;fn=wp.float64(1e9)*area/wp.float64(3.)*depth;rel=vel-tv;tan=rel-wp.dot(rel,normal)*normal;speed=wp.length(tan);fr=wp.vec3d(wp.float64(0.))       <L 13>
                var_190 = wp::div(var_188, var_189);
                var_191 = wp::float64(var_190);
                var_192 = wp::vec_t<3, wp::float64>(var_191);
                var_195 = wp::div(var_193, var_194);
                var_196 = wp::float64(var_195);
                wp::assign_inplace(var_192, var_187, var_196);
                var_197 = wp::transpose(var_58);
                var_198 = wp::mul(var_197, var_192);
                var_199 = wp::transpose(var_61);
                var_200 = wp::mul(var_199, var_198);
                var_201 = wp::transpose(var_64);
                var_202 = wp::mul(var_201, var_198);
                var_203 = wp::address(var_cells, var_16);
                var_204 = wp::transpose(var_R);
                var_205 = wp::sub(var_200, var_68);
                var_206 = wp::mul(var_204, var_205);
                var_208 = wp::load(var_203);
                var_207 = signed_inside_0(var_tri, var_iptr, var_iids, var_208, var_206);
                var_209 = &((var_207).phi);
                var_211 = wp::load(var_209);
                var_210 = wp::neg(var_211);
                var_212 = 0.0;
                var_213 = wp::max(var_210, var_212);
                var_214 = &((var_207).normal);
                var_216 = wp::load(var_214);
                var_215 = wp::mul(var_R, var_216);
                var_217 = 1000000000.0;
                var_218 = wp::mul(var_217, var_56);
                var_219 = 3.0;
                var_220 = wp::div(var_218, var_219);
                var_221 = wp::mul(var_220, var_213);
                var_222 = wp::sub(var_202, var_72);
                var_223 = wp::dot(var_222, var_215);
                var_224 = wp::mul(var_223, var_215);
                var_225 = wp::sub(var_222, var_224);
                var_226 = wp::length(var_225);
                var_227 = 0.0;
                var_228 = wp::vec_t<3, wp::float64>(var_227);
                // if speed>wp.float64(1e-30):fr=-wp.float64(.2)*fn*wp.tanh(speed/wp.float64(.001))*tan/speed       <L 14>
                var_229 = 1e-30;
                var_230 = (var_226 > var_229);
                if (var_230) {
                    var_231 = 0.2;
                    var_232 = wp::neg(var_231);
                    var_233 = wp::mul(var_232, var_221);
                    var_234 = 0.001;
                    var_235 = wp::div(var_226, var_234);
                    var_236 = wp::tanh(var_235);
                    var_237 = wp::mul(var_233, var_236);
                    var_238 = wp::mul(var_237, var_225);
                    var_239 = wp::div(var_238, var_226);
                }
                var_240 = wp::where(var_230, var_239, var_228);
                // f=fn*normal+fr                                                                 <L 15>
                var_241 = wp::mul(var_221, var_215);
                var_242 = wp::add(var_241, var_240);
                // for u in range(3):                                                             <L 16>
                // for a in range(3):forces[u,a]+=bary[u]*f[a]                                    <L 17>
                var_245 = wp::extract(var_198, var_243);
                var_246 = wp::extract(var_242, var_244);
                var_247 = wp::mul(var_245, var_246);
                wp::add_inplace(var_75, var_243, var_244, var_247);
                var_249 = wp::extract(var_198, var_243);
                var_250 = wp::extract(var_242, var_248);
                var_251 = wp::mul(var_249, var_250);
                wp::add_inplace(var_75, var_243, var_248, var_251);
                var_253 = wp::extract(var_198, var_243);
                var_254 = wp::extract(var_242, var_252);
                var_255 = wp::mul(var_253, var_254);
                wp::add_inplace(var_75, var_243, var_252, var_255);
                var_258 = wp::extract(var_198, var_256);
                var_259 = wp::extract(var_242, var_257);
                var_260 = wp::mul(var_258, var_259);
                wp::add_inplace(var_75, var_256, var_257, var_260);
                var_262 = wp::extract(var_198, var_256);
                var_263 = wp::extract(var_242, var_261);
                var_264 = wp::mul(var_262, var_263);
                wp::add_inplace(var_75, var_256, var_261, var_264);
                var_266 = wp::extract(var_198, var_256);
                var_267 = wp::extract(var_242, var_265);
                var_268 = wp::mul(var_266, var_267);
                wp::add_inplace(var_75, var_256, var_265, var_268);
                var_271 = wp::extract(var_198, var_269);
                var_272 = wp::extract(var_242, var_270);
                var_273 = wp::mul(var_271, var_272);
                wp::add_inplace(var_75, var_269, var_270, var_273);
                var_275 = wp::extract(var_198, var_269);
                var_276 = wp::extract(var_242, var_274);
                var_277 = wp::mul(var_275, var_276);
                wp::add_inplace(var_75, var_269, var_274, var_277);
                var_279 = wp::extract(var_198, var_269);
                var_280 = wp::extract(var_242, var_278);
                var_281 = wp::mul(var_279, var_280);
                wp::add_inplace(var_75, var_269, var_278, var_281);
                // U+=wp.float64(.5)*fn*depth;D-=wp.dot(fr,rel);W+=wp.dot(f,tv);M+=wp.cross(p-T,f)       <L 18>
                var_282 = 0.5;
                var_283 = wp::mul(var_282, var_221);
                var_284 = wp::mul(var_283, var_213);
                var_285 = wp::add(var_179, var_284);
                var_286 = wp::dot(var_240, var_222);
                var_287 = wp::sub(var_181, var_286);
                var_288 = wp::dot(var_242, var_72);
                var_289 = wp::add(var_183, var_288);
                var_290 = wp::sub(var_200, var_68);
                var_291 = wp::cross(var_290, var_242);
                var_292 = wp::add(var_186, var_291);
                // rule=wp.vec3d(wp.float64(1./6.));rule[k]=wp.float64(2./3.);bary=wp.transpose(B)*rule;p=wp.transpose(x)*bary;vel=wp.transpose(v)*bary;s=signed_inside(tri,iptr,iids,cells[slot],wp.transpose(R)*(p-T));depth=wp.max(-s.phi,wp.float64(0.));normal=R*s.normal;fn=wp.float64(1e9)*area/wp.float64(3.)*depth;rel=vel-tv;tan=rel-wp.dot(rel,normal)*normal;speed=wp.length(tan);fr=wp.vec3d(wp.float64(0.))       <L 13>
                var_296 = wp::div(var_294, var_295);
                var_297 = wp::float64(var_296);
                var_298 = wp::vec_t<3, wp::float64>(var_297);
                var_301 = wp::div(var_299, var_300);
                var_302 = wp::float64(var_301);
                wp::assign_inplace(var_298, var_293, var_302);
                var_303 = wp::transpose(var_58);
                var_304 = wp::mul(var_303, var_298);
                var_305 = wp::transpose(var_61);
                var_306 = wp::mul(var_305, var_304);
                var_307 = wp::transpose(var_64);
                var_308 = wp::mul(var_307, var_304);
                var_309 = wp::address(var_cells, var_16);
                var_310 = wp::transpose(var_R);
                var_311 = wp::sub(var_306, var_68);
                var_312 = wp::mul(var_310, var_311);
                var_314 = wp::load(var_309);
                var_313 = signed_inside_0(var_tri, var_iptr, var_iids, var_314, var_312);
                var_315 = &((var_313).phi);
                var_317 = wp::load(var_315);
                var_316 = wp::neg(var_317);
                var_318 = 0.0;
                var_319 = wp::max(var_316, var_318);
                var_320 = &((var_313).normal);
                var_322 = wp::load(var_320);
                var_321 = wp::mul(var_R, var_322);
                var_323 = 1000000000.0;
                var_324 = wp::mul(var_323, var_56);
                var_325 = 3.0;
                var_326 = wp::div(var_324, var_325);
                var_327 = wp::mul(var_326, var_319);
                var_328 = wp::sub(var_308, var_72);
                var_329 = wp::dot(var_328, var_321);
                var_330 = wp::mul(var_329, var_321);
                var_331 = wp::sub(var_328, var_330);
                var_332 = wp::length(var_331);
                var_333 = 0.0;
                var_334 = wp::vec_t<3, wp::float64>(var_333);
                // if speed>wp.float64(1e-30):fr=-wp.float64(.2)*fn*wp.tanh(speed/wp.float64(.001))*tan/speed       <L 14>
                var_335 = 1e-30;
                var_336 = (var_332 > var_335);
                if (var_336) {
                    var_337 = 0.2;
                    var_338 = wp::neg(var_337);
                    var_339 = wp::mul(var_338, var_327);
                    var_340 = 0.001;
                    var_341 = wp::div(var_332, var_340);
                    var_342 = wp::tanh(var_341);
                    var_343 = wp::mul(var_339, var_342);
                    var_344 = wp::mul(var_343, var_331);
                    var_345 = wp::div(var_344, var_332);
                }
                var_346 = wp::where(var_336, var_345, var_334);
                // f=fn*normal+fr                                                                 <L 15>
                var_347 = wp::mul(var_327, var_321);
                var_348 = wp::add(var_347, var_346);
                // for u in range(3):                                                             <L 16>
                // for a in range(3):forces[u,a]+=bary[u]*f[a]                                    <L 17>
                var_351 = wp::extract(var_304, var_349);
                var_352 = wp::extract(var_348, var_350);
                var_353 = wp::mul(var_351, var_352);
                wp::add_inplace(var_75, var_349, var_350, var_353);
                var_355 = wp::extract(var_304, var_349);
                var_356 = wp::extract(var_348, var_354);
                var_357 = wp::mul(var_355, var_356);
                wp::add_inplace(var_75, var_349, var_354, var_357);
                var_359 = wp::extract(var_304, var_349);
                var_360 = wp::extract(var_348, var_358);
                var_361 = wp::mul(var_359, var_360);
                wp::add_inplace(var_75, var_349, var_358, var_361);
                var_364 = wp::extract(var_304, var_362);
                var_365 = wp::extract(var_348, var_363);
                var_366 = wp::mul(var_364, var_365);
                wp::add_inplace(var_75, var_362, var_363, var_366);
                var_368 = wp::extract(var_304, var_362);
                var_369 = wp::extract(var_348, var_367);
                var_370 = wp::mul(var_368, var_369);
                wp::add_inplace(var_75, var_362, var_367, var_370);
                var_372 = wp::extract(var_304, var_362);
                var_373 = wp::extract(var_348, var_371);
                var_374 = wp::mul(var_372, var_373);
                wp::add_inplace(var_75, var_362, var_371, var_374);
                var_377 = wp::extract(var_304, var_375);
                var_378 = wp::extract(var_348, var_376);
                var_379 = wp::mul(var_377, var_378);
                wp::add_inplace(var_75, var_375, var_376, var_379);
                var_381 = wp::extract(var_304, var_375);
                var_382 = wp::extract(var_348, var_380);
                var_383 = wp::mul(var_381, var_382);
                wp::add_inplace(var_75, var_375, var_380, var_383);
                var_385 = wp::extract(var_304, var_375);
                var_386 = wp::extract(var_348, var_384);
                var_387 = wp::mul(var_385, var_386);
                wp::add_inplace(var_75, var_375, var_384, var_387);
                // U+=wp.float64(.5)*fn*depth;D-=wp.dot(fr,rel);W+=wp.dot(f,tv);M+=wp.cross(p-T,f)       <L 18>
                var_388 = 0.5;
                var_389 = wp::mul(var_388, var_327);
                var_390 = wp::mul(var_389, var_319);
                var_391 = wp::add(var_285, var_390);
                var_392 = wp::dot(var_346, var_328);
                var_393 = wp::sub(var_287, var_392);
                var_394 = wp::dot(var_348, var_72);
                var_395 = wp::add(var_289, var_394);
                var_396 = wp::sub(var_306, var_68);
                var_397 = wp::cross(var_396, var_348);
                var_398 = wp::add(var_292, var_397);
            }
            var_399 = wp::where(var_37, var_75, var_29);
            var_400 = wp::where(var_37, var_391, var_30);
            var_401 = wp::where(var_37, var_393, var_31);
            var_402 = wp::where(var_37, var_395, var_32);
            var_403 = wp::where(var_37, var_398, var_34);
            // f0=wp.tile_sum(wp.tile(forces[0],preserve_type=True));f1=wp.tile_sum(wp.tile(forces[1],preserve_type=True));f2=wp.tile_sum(wp.tile(forces[2],preserve_type=True))       <L 19>
            var_405 = wp::extract(var_399, var_404);
            var_407 = wp::tile<wp::vec_t<3, wp::float64>>(var_405);
            var_408 = wp::tile_sum(var_407);
            var_410 = wp::extract(var_399, var_409);
            var_412 = wp::tile<wp::vec_t<3, wp::float64>>(var_410);
            var_413 = wp::tile_sum(var_412);
            var_415 = wp::extract(var_399, var_414);
            var_417 = wp::tile<wp::vec_t<3, wp::float64>>(var_415);
            var_418 = wp::tile_sum(var_417);
            // su=wp.tile_sum(wp.tile(U));sd=wp.tile_sum(wp.tile(D));sw=wp.tile_sum(wp.tile(W));sm=wp.tile_sum(wp.tile(M,preserve_type=True))       <L 20>
            var_419 = wp::tile<wp::float64>(var_400);
            var_420 = wp::tile_sum(var_419);
            var_421 = wp::tile<wp::float64>(var_401);
            var_422 = wp::tile_sum(var_421);
            var_423 = wp::tile<wp::float64>(var_402);
            var_424 = wp::tile_sum(var_423);
            var_426 = wp::tile<wp::vec_t<3, wp::float64>>(var_403);
            var_427 = wp::tile_sum(var_426);
            // if lane==0:                                                                        <L 21>
            var_429 = (var_8 == var_428);
            if (var_429) {
                // wp.atomic_add(ff,face,0,f0[0]);wp.atomic_add(ff,face,1,f1[0]);wp.atomic_add(ff,face,2,f2[0]);wp.atomic_add(uu,face,su[0]);wp.atomic_add(dd,face,sd[0]);wp.atomic_add(ww,face,sw[0]);wp.atomic_add(mm,face,sm[0])       <L 22>
                var_432 = wp::tile_extract(var_408, var_431);
                var_433 = wp::atomic_add(var_ff, var_23, var_430, var_432);
                var_436 = wp::tile_extract(var_413, var_435);
                var_437 = wp::atomic_add(var_ff, var_23, var_434, var_436);
                var_440 = wp::tile_extract(var_418, var_439);
                var_441 = wp::atomic_add(var_ff, var_23, var_438, var_440);
                var_443 = wp::tile_extract(var_420, var_442);
                var_444 = wp::atomic_add(var_uu, var_23, var_443);
                var_446 = wp::tile_extract(var_422, var_445);
                var_447 = wp::atomic_add(var_dd, var_23, var_446);
                var_449 = wp::tile_extract(var_424, var_448);
                var_450 = wp::atomic_add(var_ww, var_23, var_449);
                var_452 = wp::tile_extract(var_427, var_451);
                var_453 = wp::atomic_add(var_mm, var_23, var_452);
            }
            goto start_for_0;
        end_for_0:;
    }
}


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


// /home/omen/Documents/Codex/experiments/tomato_bounded_basis_20261113_v27/src/grid_cad_candidates.py:26
static CUDA_CALLABLE Signed_7e3cff60 signed_grid_0(
    wp::array_t<wp::vec_t<3, wp::float64>> var_tri,
    wp::array_t<wp::int32> var_ptr,
    wp::array_t<wp::int32> var_ids,
    wp::vec_t<3, wp::float64> var_origin,
    wp::vec_t<3, wp::int32> var_shape,
    wp::float64 var_h,
    wp::vec_t<3, wp::float64> var_p)
{
    //---------
    // primal vars
    const wp::int32 var_0 = 0;
    wp::float64 var_1;
    const wp::int32 var_2 = 0;
    wp::float64 var_3;
    wp::float64 var_4;
    wp::float64 var_5;
    wp::float64 var_6;
    wp::int32 var_7;
    const wp::int32 var_8 = 1;
    wp::float64 var_9;
    const wp::int32 var_10 = 1;
    wp::float64 var_11;
    wp::float64 var_12;
    wp::float64 var_13;
    wp::float64 var_14;
    wp::int32 var_15;
    const wp::int32 var_16 = 2;
    wp::float64 var_17;
    const wp::int32 var_18 = 2;
    wp::float64 var_19;
    wp::float64 var_20;
    wp::float64 var_21;
    wp::float64 var_22;
    wp::int32 var_23;
    wp::vec_t<3, wp::int32> var_24;
    const bool var_25 = true;
    const wp::int32 var_26 = 0;
    bool var_27;
    wp::int32 var_28;
    const wp::int32 var_29 = 0;
    bool var_30;
    wp::int32 var_31;
    wp::int32 var_32;
    bool var_33;
    const bool var_34 = false;
    bool var_35;
    const wp::int32 var_36 = 1;
    bool var_37;
    wp::int32 var_38;
    const wp::int32 var_39 = 0;
    bool var_40;
    wp::int32 var_41;
    wp::int32 var_42;
    bool var_43;
    const bool var_44 = false;
    bool var_45;
    const wp::int32 var_46 = 2;
    bool var_47;
    wp::int32 var_48;
    const wp::int32 var_49 = 0;
    bool var_50;
    wp::int32 var_51;
    wp::int32 var_52;
    bool var_53;
    const bool var_54 = false;
    bool var_55;
    const wp::int32 var_56 = 0;
    wp::int32 var_57;
    wp::shape_t* var_58;
    const wp::int32 var_59 = 0;
    wp::int32 var_60;
    wp::shape_t var_61;
    const wp::int32 var_62 = 0;
    wp::int32 var_63;
    const wp::int32 var_64 = 1;
    wp::int32 var_65;
    wp::int32 var_66;
    const wp::int32 var_67 = 1;
    wp::int32 var_68;
    wp::int32 var_69;
    const wp::int32 var_70 = 2;
    wp::int32 var_71;
    wp::int32 var_72;
    const wp::int32 var_73 = 2;
    wp::int32 var_74;
    wp::int32 var_75;
    wp::int32* var_76;
    wp::int32 var_77;
    wp::int32 var_78;
    const wp::int32 var_79 = 1;
    wp::int32 var_80;
    wp::int32* var_81;
    wp::int32 var_82;
    wp::int32 var_83;
    wp::int32 var_84;
    wp::int32 var_85;
    wp::float64 var_86;
    const wp::int32 var_87 = -1;
    wp::int32 var_88;
    wp::float64 var_89;
    wp::vec_t<3, wp::float64> var_90;
    wp::range_t var_91;
    wp::int32 var_92;
    wp::int32 var_93;
    wp::int32* var_94;
    wp::int32 var_95;
    wp::int32 var_96;
    wp::int32 var_97;
    const wp::int32 var_98 = 0;
    wp::vec_t<3, wp::float64>* var_99;
    const wp::int32 var_100 = 1;
    wp::vec_t<3, wp::float64>* var_101;
    const wp::int32 var_102 = 2;
    wp::vec_t<3, wp::float64>* var_103;
    wp::vec_t<3, wp::float64> var_104;
    wp::vec_t<3, wp::float64> var_105;
    wp::vec_t<3, wp::float64> var_106;
    wp::vec_t<3, wp::float64> var_107;
    wp::vec_t<3, wp::float64> var_108;
    wp::float64 var_109;
    bool var_110;
    wp::float64 var_111;
    wp::int32 var_112;
    wp::vec_t<3, wp::float64> var_113;
    wp::float64 var_114;
    wp::int32 var_115;
    wp::vec_t<3, wp::float64> var_116;
    Signed_7e3cff60 var_117;
    wp::float64 var_118;
    wp::float64 var_119;
    wp::float64 var_120;
    bool var_121;
    wp::vec_t<3, wp::float64> var_122;
    wp::vec_t<3, wp::float64> var_123;
    wp::vec_t<3, wp::float64> var_124;
    const wp::int32 var_125 = 1;
    wp::vec_t<3, wp::float64>* var_126;
    const wp::int32 var_127 = 0;
    wp::vec_t<3, wp::float64>* var_128;
    wp::vec_t<3, wp::float64> var_129;
    wp::vec_t<3, wp::float64> var_130;
    wp::vec_t<3, wp::float64> var_131;
    const wp::int32 var_132 = 2;
    wp::vec_t<3, wp::float64>* var_133;
    const wp::int32 var_134 = 0;
    wp::vec_t<3, wp::float64>* var_135;
    wp::vec_t<3, wp::float64> var_136;
    wp::vec_t<3, wp::float64> var_137;
    wp::vec_t<3, wp::float64> var_138;
    wp::vec_t<3, wp::float64> var_139;
    wp::vec_t<3, wp::float64> var_140;
    //---------
    // forward
    // def signed_grid(tri:wp.array2d(dtype=wp.vec3d),ptr:wp.array(dtype=int),ids:wp.array(dtype=int),origin:wp.vec3d,shape:wp.vec3i,h:wp.float64,p:wp.vec3d):       <L 27>
    // index=wp.vec3i(int(wp.floor((p[0]-origin[0])/h)),int(wp.floor((p[1]-origin[1])/h)),int(wp.floor((p[2]-origin[2])/h)));within=True       <L 28>
    var_1 = wp::extract(var_p, var_0);
    var_3 = wp::extract(var_origin, var_2);
    var_4 = wp::sub(var_1, var_3);
    var_5 = wp::div(var_4, var_h);
    var_6 = wp::floor(var_5);
    var_7 = wp::int(var_6);
    var_9 = wp::extract(var_p, var_8);
    var_11 = wp::extract(var_origin, var_10);
    var_12 = wp::sub(var_9, var_11);
    var_13 = wp::div(var_12, var_h);
    var_14 = wp::floor(var_13);
    var_15 = wp::int(var_14);
    var_17 = wp::extract(var_p, var_16);
    var_19 = wp::extract(var_origin, var_18);
    var_20 = wp::sub(var_17, var_19);
    var_21 = wp::div(var_20, var_h);
    var_22 = wp::floor(var_21);
    var_23 = wp::int(var_22);
    var_24 = wp::vec_t<3, wp::int32>(var_7, var_15, var_23);
    // for a in range(3):                                                                     <L 29>
    // if index[a]<0 or index[a]>=shape[a]:within=False                                       <L 30>
    var_28 = wp::extract(var_24, var_26);
    var_30 = (var_28 < var_29);
    var_27 = var_30;
    if (!var_27) {
        var_31 = wp::extract(var_24, var_26);
        var_32 = wp::extract(var_shape, var_26);
        var_33 = (var_31 >= var_32);
        var_27 = var_27 || var_33;
    }
    if (var_27) {
    }
    var_35 = wp::where(var_27, var_34, var_25);
    var_38 = wp::extract(var_24, var_36);
    var_40 = (var_38 < var_39);
    var_37 = var_40;
    if (!var_37) {
        var_41 = wp::extract(var_24, var_36);
        var_42 = wp::extract(var_shape, var_36);
        var_43 = (var_41 >= var_42);
        var_37 = var_37 || var_43;
    }
    if (var_37) {
    }
    var_45 = wp::where(var_37, var_44, var_35);
    var_48 = wp::extract(var_24, var_46);
    var_50 = (var_48 < var_49);
    var_47 = var_50;
    if (!var_47) {
        var_51 = wp::extract(var_24, var_46);
        var_52 = wp::extract(var_shape, var_46);
        var_53 = (var_51 >= var_52);
        var_47 = var_47 || var_53;
    }
    if (var_47) {
    }
    var_55 = wp::where(var_47, var_54, var_45);
    // lo=int(0);hi=tri.shape[0]                                                              <L 31>
    var_57 = wp::int(var_56);
    var_58 = &(var_tri.shape);
    var_61 = wp::load(var_58);
    var_60 = wp::extract(var_61, var_59);
    // if within:                                                                             <L 32>
    if (var_55) {
        // cell=(index[0]*shape[1]+index[1])*shape[2]+index[2];lo=ptr[cell];hi=ptr[cell+1]       <L 33>
        var_63 = wp::extract(var_24, var_62);
        var_65 = wp::extract(var_shape, var_64);
        var_66 = wp::mul(var_63, var_65);
        var_68 = wp::extract(var_24, var_67);
        var_69 = wp::add(var_66, var_68);
        var_71 = wp::extract(var_shape, var_70);
        var_72 = wp::mul(var_69, var_71);
        var_74 = wp::extract(var_24, var_73);
        var_75 = wp::add(var_72, var_74);
        var_76 = wp::address(var_ptr, var_75);
        var_78 = wp::load(var_76);
        var_77 = wp::copy(var_78);
        var_80 = wp::add(var_75, var_79);
        var_81 = wp::address(var_ptr, var_80);
        var_83 = wp::load(var_81);
        var_82 = wp::copy(var_83);
    }
    var_84 = wp::where(var_55, var_77, var_57);
    var_85 = wp::where(var_55, var_82, var_60);
    // best=wp.float64(1e30);face=int(-1);q=wp.vec3d(wp.float64(0.))                          <L 34>
    var_86 = 1e+30;
    var_88 = wp::int(var_87);
    var_89 = 0.0;
    var_90 = wp::vec_t<3, wp::float64>(var_89);
    // for z in range(lo,hi):                                                                 <L 35>
    var_91 = wp::range(var_84, var_85);
    start_for_0:;
        if (iter_cmp(var_91) == 0) goto end_for_0;
        var_92 = wp::iter_next(var_91);
        // f=z                                                                                <L 36>
        var_93 = wp::copy(var_92);
        // if within:f=ids[z]                                                                 <L 37>
        if (var_55) {
            var_94 = wp::address(var_ids, var_92);
            var_96 = wp::load(var_94);
            var_95 = wp::copy(var_96);
        }
        var_97 = wp::where(var_55, var_95, var_93);
        // c=closest(p,tri[f,0],tri[f,1],tri[f,2]);d=wp.length_sq(p-c)                        <L 38>
        var_99 = wp::address(var_tri, var_97, var_98);
        var_101 = wp::address(var_tri, var_97, var_100);
        var_103 = wp::address(var_tri, var_97, var_102);
        var_105 = wp::load(var_99);
        var_106 = wp::load(var_101);
        var_107 = wp::load(var_103);
        var_104 = closest_0(var_p, var_105, var_106, var_107);
        var_108 = wp::sub(var_p, var_104);
        var_109 = wp::length_sq(var_108);
        // if d<best:best=d;face=f;q=c                                                        <L 39>
        var_110 = (var_109 < var_86);
        if (var_110) {
            var_111 = wp::copy(var_109);
            var_112 = wp::copy(var_97);
            var_113 = wp::copy(var_104);
        }
        var_114 = wp::where(var_110, var_111, var_86);
        var_115 = wp::where(var_110, var_112, var_88);
        var_116 = wp::where(var_110, var_113, var_90);
        wp::assign(var_86, var_114);
        wp::assign(var_88, var_115);
        wp::assign(var_90, var_116);
        goto start_for_0;
    end_for_0:;
    // r=Signed();length=wp.sqrt(best);r.phi=-length                                          <L 40>
    var_117 = Signed_7e3cff60();
    var_118 = wp::sqrt(var_86);
    var_119 = wp::neg(var_118);
    var_117.phi = var_119;
    // if length>wp.float64(1e-15):r.normal=-(p-q)/length                                     <L 41>
    var_120 = 1e-15;
    var_121 = (var_118 > var_120);
    if (var_121) {
        var_122 = wp::sub(var_p, var_90);
        var_123 = wp::neg(var_122);
        var_124 = wp::div(var_123, var_118);
        var_117.normal = var_124;
    }
    if (!var_121) {
        // else:r.normal=wp.normalize(wp.cross(tri[face,1]-tri[face,0],tri[face,2]-tri[face,0]))       <L 42>
        var_126 = wp::address(var_tri, var_88, var_125);
        var_128 = wp::address(var_tri, var_88, var_127);
        var_130 = wp::load(var_126);
        var_131 = wp::load(var_128);
        var_129 = wp::sub(var_130, var_131);
        var_133 = wp::address(var_tri, var_88, var_132);
        var_135 = wp::address(var_tri, var_88, var_134);
        var_137 = wp::load(var_133);
        var_138 = wp::load(var_135);
        var_136 = wp::sub(var_137, var_138);
        var_139 = wp::cross(var_129, var_136);
        var_140 = wp::normalize(var_139);
        var_117.normal = var_140;
    }
    // return r                                                                               <L 43>
    return var_117;
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


// /home/omen/Documents/Codex/experiments/tomato_bounded_basis_20261113_v27/src/grid_cad_candidates.py:26
static CUDA_CALLABLE void adj_signed_grid_0(
    wp::array_t<wp::vec_t<3, wp::float64>> var_tri,
    wp::array_t<wp::int32> var_ptr,
    wp::array_t<wp::int32> var_ids,
    wp::vec_t<3, wp::float64> var_origin,
    wp::vec_t<3, wp::int32> var_shape,
    wp::float64 var_h,
    wp::vec_t<3, wp::float64> var_p,
    wp::array_t<wp::vec_t<3, wp::float64>> & adj_tri,
    wp::array_t<wp::int32> & adj_ptr,
    wp::array_t<wp::int32> & adj_ids,
    wp::vec_t<3, wp::float64> & adj_origin,
    wp::vec_t<3, wp::int32> & adj_shape,
    wp::float64 & adj_h,
    wp::vec_t<3, wp::float64> & adj_p,
    Signed_7e3cff60 & adj_ret)
{
	// reverse mode disabled (module option "enable_backward" is False or no dependent kernel found with "enable_backward")
}



extern "C" __global__ void build_candidates_4d8313c3_cuda_kernel_forward(
    wp::launch_bounds_t<1> dim,
    wp::array_t<wp::vec_t<3, wp::float64>> var_tri,
    wp::vec_t<3, wp::float64> var_origin,
    wp::vec_t<3, wp::int32> var_shape,
    wp::float64 var_h,
    wp::array_t<wp::int32> var_counts,
    wp::array_t<wp::int32> var_ids,
    wp::array_t<wp::int32> var_overflow)
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
        const wp::int32 var_1 = 1;
        wp::int32 var_2;
        const wp::int32 var_3 = 2;
        wp::int32 var_4;
        wp::int32 var_5;
        wp::int32 var_6;
        const wp::int32 var_7 = 2;
        wp::int32 var_8;
        wp::int32 var_9;
        const wp::int32 var_10 = 1;
        wp::int32 var_11;
        wp::int32 var_12;
        const wp::int32 var_13 = 2;
        wp::int32 var_14;
        wp::int32 var_15;
        wp::float64 var_16;
        wp::float64 var_17;
        wp::float64 var_18;
        wp::vec_t<3, wp::float64> var_19;
        wp::float64 var_20;
        wp::vec_t<3, wp::float64> var_21;
        wp::vec_t<3, wp::float64> var_22;
        wp::vec_t<3, wp::float64> var_23;
        wp::vec_t<3, wp::float64> var_24;
        wp::float64 var_25;
        wp::shape_t* var_26;
        const wp::int32 var_27 = 0;
        wp::int32 var_28;
        wp::shape_t var_29;
        wp::range_t var_30;
        wp::int32 var_31;
        const wp::int32 var_32 = 0;
        wp::vec_t<3, wp::float64>* var_33;
        const wp::int32 var_34 = 1;
        wp::vec_t<3, wp::float64>* var_35;
        const wp::int32 var_36 = 2;
        wp::vec_t<3, wp::float64>* var_37;
        wp::vec_t<3, wp::float64> var_38;
        wp::vec_t<3, wp::float64> var_39;
        wp::vec_t<3, wp::float64> var_40;
        wp::vec_t<3, wp::float64> var_41;
        wp::vec_t<3, wp::float64> var_42;
        wp::float64 var_43;
        wp::float64 var_44;
        wp::float64 var_45;
        wp::float64 var_46;
        wp::float64 var_47;
        wp::float64 var_48;
        wp::float64 var_49;
        wp::float64 var_50;
        const wp::int32 var_51 = 0;
        wp::int32 var_52;
        wp::shape_t* var_53;
        const wp::int32 var_54 = 0;
        wp::int32 var_55;
        wp::shape_t var_56;
        wp::range_t var_57;
        wp::int32 var_58;
        const wp::int32 var_59 = 0;
        wp::vec_t<3, wp::float64>* var_60;
        const wp::int32 var_61 = 1;
        wp::vec_t<3, wp::float64>* var_62;
        const wp::int32 var_63 = 2;
        wp::vec_t<3, wp::float64>* var_64;
        wp::vec_t<3, wp::float64> var_65;
        wp::vec_t<3, wp::float64> var_66;
        wp::vec_t<3, wp::float64> var_67;
        wp::vec_t<3, wp::float64> var_68;
        wp::vec_t<3, wp::float64> var_69;
        wp::float64 var_70;
        bool var_71;
        wp::shape_t* var_72;
        const wp::int32 var_73 = 1;
        wp::int32 var_74;
        wp::shape_t var_75;
        bool var_76;
        const wp::int32 var_77 = 0;
        const wp::int32 var_78 = 1;
        wp::int32 var_79;
        const wp::int32 var_80 = 1;
        wp::int32 var_81;
        wp::int32 var_82;
        //---------
        // forward
        // def build_candidates(tri:wp.array2d(dtype=wp.vec3d),origin:wp.vec3d,shape:wp.vec3i,h:wp.float64,counts:wp.array(dtype=int),ids:wp.array2d(dtype=int),overflow:wp.array(dtype=int)):       <L 15>
        // index=wp.tid();i=index//(shape[1]*shape[2]);j=(index//shape[2])%shape[1];k=index%shape[2];center=origin+h*(wp.vec3d(wp.float64(i),wp.float64(j),wp.float64(k))+wp.vec3d(wp.float64(.5)));best=wp.float64(1e30)       <L 16>
        var_0 = builtin_tid1d();
        var_2 = wp::extract(var_shape, var_1);
        var_4 = wp::extract(var_shape, var_3);
        var_5 = wp::mul(var_2, var_4);
        var_6 = wp::floordiv(var_0, var_5);
        var_8 = wp::extract(var_shape, var_7);
        var_9 = wp::floordiv(var_0, var_8);
        var_11 = wp::extract(var_shape, var_10);
        var_12 = wp::mod(var_9, var_11);
        var_14 = wp::extract(var_shape, var_13);
        var_15 = wp::mod(var_0, var_14);
        var_16 = wp::float64(var_6);
        var_17 = wp::float64(var_12);
        var_18 = wp::float64(var_15);
        var_19 = wp::vec_t<3, wp::float64>(var_16, var_17, var_18);
        var_20 = 0.5;
        var_21 = wp::vec_t<3, wp::float64>(var_20);
        var_22 = wp::add(var_19, var_21);
        var_23 = wp::mul(var_h, var_22);
        var_24 = wp::add(var_origin, var_23);
        var_25 = 1e+30;
        // for f in range(tri.shape[0]):best=wp.min(best,wp.length(center-closest(center,tri[f,0],tri[f,1],tri[f,2])))       <L 17>
        var_26 = &(var_tri.shape);
        var_29 = wp::load(var_26);
        var_28 = wp::extract(var_29, var_27);
        var_30 = wp::range(var_28);
        start_for_0:;
            if (iter_cmp(var_30) == 0) goto end_for_0;
            var_31 = wp::iter_next(var_30);
            var_33 = wp::address(var_tri, var_31, var_32);
            var_35 = wp::address(var_tri, var_31, var_34);
            var_37 = wp::address(var_tri, var_31, var_36);
            var_39 = wp::load(var_33);
            var_40 = wp::load(var_35);
            var_41 = wp::load(var_37);
            var_38 = closest_0(var_24, var_39, var_40, var_41);
            var_42 = wp::sub(var_24, var_38);
            var_43 = wp::length(var_42);
            var_44 = wp::min(var_25, var_43);
            wp::assign(var_25, var_44);
            goto start_for_0;
        end_for_0:;
        // threshold=best+wp.sqrt(wp.float64(3.))*h+wp.float64(2e-10);n=int(0)                    <L 18>
        var_45 = 3.0;
        var_46 = wp::sqrt(var_45);
        var_47 = wp::mul(var_46, var_h);
        var_48 = wp::add(var_25, var_47);
        var_49 = 2e-10;
        var_50 = wp::add(var_48, var_49);
        var_52 = wp::int(var_51);
        // for f in range(tri.shape[0]):                                                          <L 19>
        var_53 = &(var_tri.shape);
        var_56 = wp::load(var_53);
        var_55 = wp::extract(var_56, var_54);
        var_57 = wp::range(var_55);
        start_for_2:;
            if (iter_cmp(var_57) == 0) goto end_for_2;
            var_58 = wp::iter_next(var_57);
            // if wp.length(center-closest(center,tri[f,0],tri[f,1],tri[f,2]))<=threshold:        <L 20>
            var_60 = wp::address(var_tri, var_58, var_59);
            var_62 = wp::address(var_tri, var_58, var_61);
            var_64 = wp::address(var_tri, var_58, var_63);
            var_66 = wp::load(var_60);
            var_67 = wp::load(var_62);
            var_68 = wp::load(var_64);
            var_65 = closest_0(var_24, var_66, var_67, var_68);
            var_69 = wp::sub(var_24, var_65);
            var_70 = wp::length(var_69);
            var_71 = (var_70 <= var_50);
            if (var_71) {
                // if n<ids.shape[1]:ids[index,n]=f                                               <L 21>
                var_72 = &(var_ids.shape);
                var_75 = wp::load(var_72);
                var_74 = wp::extract(var_75, var_73);
                var_76 = (var_52 < var_74);
                if (var_76) {
                    wp::array_store(var_ids, var_0, var_52, var_58);
                }
                if (!var_76) {
                    // else:wp.atomic_max(overflow,0,1)                                           <L 22>
                    var_79 = wp::atomic_max(var_overflow, var_77, var_78);
                }
                // n+=1                                                                           <L 23>
                var_81 = wp::add(var_52, var_80);
            }
            var_82 = wp::where(var_71, var_81, var_52);
            wp::assign(var_52, var_82);
            goto start_for_2;
        end_for_2:;
        // counts[index]=n                                                                        <L 24>
        wp::array_store(var_counts, var_0, var_52);
    }
}



extern "C" __global__ void query_grid_adb42030_cuda_kernel_forward(
    wp::launch_bounds_t<1> dim,
    wp::array_t<wp::vec_t<3, wp::float64>> var_tri,
    wp::array_t<wp::int32> var_ptr,
    wp::array_t<wp::int32> var_ids,
    wp::vec_t<3, wp::float64> var_origin,
    wp::vec_t<3, wp::int32> var_shape,
    wp::float64 var_h,
    wp::array_t<wp::vec_t<3, wp::float64>> var_points,
    wp::array_t<wp::float64> var_phi,
    wp::array_t<wp::vec_t<3, wp::float64>> var_normal)
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
        wp::vec_t<3, wp::float64>* var_1;
        Signed_7e3cff60 var_2;
        wp::vec_t<3, wp::float64> var_3;
        wp::float64* var_4;
        wp::float64 var_5;
        wp::vec_t<3, wp::float64>* var_6;
        wp::vec_t<3, wp::float64> var_7;
        //---------
        // forward
        // def query_grid(tri:wp.array2d(dtype=wp.vec3d),ptr:wp.array(dtype=int),ids:wp.array(dtype=int),origin:wp.vec3d,shape:wp.vec3i,h:wp.float64,points:wp.array(dtype=wp.vec3d),phi:wp.array(dtype=wp.float64),normal:wp.array(dtype=wp.vec3d)):       <L 46>
        // i=wp.tid();r=signed_grid(tri,ptr,ids,origin,shape,h,points[i]);phi[i]=r.phi;normal[i]=r.normal       <L 47>
        var_0 = builtin_tid1d();
        var_1 = wp::address(var_points, var_0);
        var_3 = wp::load(var_1);
        var_2 = signed_grid_0(var_tri, var_ptr, var_ids, var_origin, var_shape, var_h, var_3);
        var_4 = &((var_2).phi);
        var_5 = wp::load(var_4);
        wp::array_store(var_phi, var_0, var_5);
        var_6 = &((var_2).normal);
        var_7 = wp::load(var_6);
        wp::array_store(var_normal, var_0, var_7);
    }
}


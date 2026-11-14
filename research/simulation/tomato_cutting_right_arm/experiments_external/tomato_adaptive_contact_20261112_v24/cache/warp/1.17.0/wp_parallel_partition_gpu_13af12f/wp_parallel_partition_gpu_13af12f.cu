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




// /home/omen/Documents/Codex/experiments/tomato_adaptive_contact_20261112_v24/src/contact_gpu_precise.py:12
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


// /home/omen/Documents/Codex/experiments/tomato_adaptive_contact_20261112_v24/src/exact_cad_gpu.py:9
static CUDA_CALLABLE Signed_7e3cff60 signed_0(
    wp::uint64 var_mesh,
    wp::array_t<wp::vec_t<3, wp::float64>> var_tri,
    wp::vec_t<3, wp::float64> var_p)
{
    //---------
    // primal vars
    Signed_7e3cff60 var_0;
    wp::float64 var_1;
    wp::float64 var_2;
    wp::vec_t<3, wp::float64> var_3;
    wp::vec_t<3, wp::float32> var_4;
    const wp::float32 var_5 = 10.0;
    wp::mesh_query_point_t var_6;
    const wp::float32 var_7 = 2.0;
    const wp::float32 var_8 = 0.5;
    bool* var_9;
    bool var_10;
    wp::int32* var_11;
    const wp::int32 var_12 = 0;
    wp::vec_t<3, wp::float64>* var_13;
    wp::int32 var_14;
    wp::int32* var_15;
    const wp::int32 var_16 = 1;
    wp::vec_t<3, wp::float64>* var_17;
    wp::int32 var_18;
    wp::int32* var_19;
    const wp::int32 var_20 = 2;
    wp::vec_t<3, wp::float64>* var_21;
    wp::int32 var_22;
    wp::vec_t<3, wp::float64> var_23;
    wp::vec_t<3, wp::float64> var_24;
    wp::vec_t<3, wp::float64> var_25;
    wp::vec_t<3, wp::float64> var_26;
    wp::vec_t<3, wp::float64> var_27;
    wp::float64 var_28;
    wp::int32* var_29;
    wp::int32 var_30;
    wp::int32 var_31;
    wp::float64 var_32;
    wp::float64 var_33;
    wp::float64 var_34;
    wp::vec_t<3, wp::float64> var_35;
    wp::vec_t<3, wp::float64> var_36;
    wp::vec_t<3, wp::float32> var_37;
    wp::vec_t<3, wp::float64> var_38;
    wp::vec_t<3, wp::float64> var_39;
    wp::vec_t<3, wp::float32> var_40;
    wp::mesh_query_aabb_t var_41;
    wp::int32 var_42;
    const wp::int32 var_43 = 0;
    wp::vec_t<3, wp::float64>* var_44;
    const wp::int32 var_45 = 1;
    wp::vec_t<3, wp::float64>* var_46;
    const wp::int32 var_47 = 2;
    wp::vec_t<3, wp::float64>* var_48;
    wp::vec_t<3, wp::float64> var_49;
    wp::vec_t<3, wp::float64> var_50;
    wp::vec_t<3, wp::float64> var_51;
    wp::vec_t<3, wp::float64> var_52;
    wp::vec_t<3, wp::float64> var_53;
    wp::float64 var_54;
    bool var_55;
    bool var_56;
    bool var_57;
    bool var_58;
    bool var_59;
    wp::float64 var_60;
    wp::vec_t<3, wp::float64> var_61;
    wp::int32 var_62;
    wp::vec_t<3, wp::float64> var_63;
    wp::float64 var_64;
    wp::int32 var_65;
    wp::vec_t<3, wp::float64> var_66;
    wp::float64 var_67;
    wp::float32* var_68;
    wp::float64 var_69;
    wp::float32 var_70;
    wp::float64 var_71;
    wp::float64 var_72;
    bool var_73;
    wp::float32* var_74;
    wp::float64 var_75;
    wp::float32 var_76;
    wp::vec_t<3, wp::float64> var_77;
    wp::vec_t<3, wp::float64> var_78;
    const wp::int32 var_79 = 1;
    wp::vec_t<3, wp::float64>* var_80;
    const wp::int32 var_81 = 0;
    wp::vec_t<3, wp::float64>* var_82;
    wp::vec_t<3, wp::float64> var_83;
    wp::vec_t<3, wp::float64> var_84;
    wp::vec_t<3, wp::float64> var_85;
    const wp::int32 var_86 = 2;
    wp::vec_t<3, wp::float64>* var_87;
    const wp::int32 var_88 = 0;
    wp::vec_t<3, wp::float64>* var_89;
    wp::vec_t<3, wp::float64> var_90;
    wp::vec_t<3, wp::float64> var_91;
    wp::vec_t<3, wp::float64> var_92;
    wp::vec_t<3, wp::float64> var_93;
    wp::vec_t<3, wp::float64> var_94;
    bool var_95;
    //---------
    // forward
    // def signed(mesh:wp.uint64,tri:wp.array2d(dtype=wp.vec3d),p:wp.vec3d):                  <L 10>
    // r=Signed();r.phi=wp.float64(100.);r.normal=wp.vec3d(wp.float64(0.));q=wp.mesh_query_point_sign_winding_number(mesh,wp.vec3(p),10.)       <L 11>
    var_0 = Signed_7e3cff60();
    var_1 = 100.0;
    var_0.phi = var_1;
    var_2 = 0.0;
    var_3 = wp::vec_t<3, wp::float64>(var_2);
    var_0.normal = var_3;
    var_4 = wp::vec_t<3, wp::float32>(var_p);
    var_6 = wp::mesh_query_point_sign_winding_number(var_mesh, var_4, var_5, var_7, var_8);
    // if q.result:                                                                           <L 12>
    var_9 = &((var_6).result);
    var_10 = wp::load(var_9);
    if (var_10) {
        // c=closest(p,tri[q.face,0],tri[q.face,1],tri[q.face,2]);best=wp.length_sq(p-c);bestface=q.face       <L 13>
        var_11 = &((var_6).face);
        var_14 = wp::load(var_11);
        var_13 = wp::address(var_tri, var_14, var_12);
        var_15 = &((var_6).face);
        var_18 = wp::load(var_15);
        var_17 = wp::address(var_tri, var_18, var_16);
        var_19 = &((var_6).face);
        var_22 = wp::load(var_19);
        var_21 = wp::address(var_tri, var_22, var_20);
        var_24 = wp::load(var_13);
        var_25 = wp::load(var_17);
        var_26 = wp::load(var_21);
        var_23 = closest_0(var_p, var_24, var_25, var_26);
        var_27 = wp::sub(var_p, var_23);
        var_28 = wp::length_sq(var_27);
        var_29 = &((var_6).face);
        var_31 = wp::load(var_29);
        var_30 = wp::copy(var_31);
        // radius=wp.sqrt(best)+wp.float64(2e-7)                                              <L 17>
        var_32 = wp::sqrt(var_28);
        var_33 = 2e-07;
        var_34 = wp::add(var_32, var_33);
        // candidates=wp.mesh_query_aabb(mesh,wp.vec3(p-wp.vec3d(radius)),wp.vec3(p+wp.vec3d(radius)))       <L 18>
        var_35 = wp::vec_t<3, wp::float64>(var_34);
        var_36 = wp::sub(var_p, var_35);
        var_37 = wp::vec_t<3, wp::float32>(var_36);
        var_38 = wp::vec_t<3, wp::float64>(var_34);
        var_39 = wp::add(var_p, var_38);
        var_40 = wp::vec_t<3, wp::float32>(var_39);
        var_41 = wp::mesh_query_aabb(var_mesh, var_37, var_40);
        // for face in candidates:                                                            <L 19>
        start_for_0:;
            if (iter_cmp(var_41) == 0) goto end_for_0;
            var_42 = wp::iter_next(var_41);
            // candidate=closest(p,tri[face,0],tri[face,1],tri[face,2]);dist=wp.length_sq(p-candidate)       <L 20>
            var_44 = wp::address(var_tri, var_42, var_43);
            var_46 = wp::address(var_tri, var_42, var_45);
            var_48 = wp::address(var_tri, var_42, var_47);
            var_50 = wp::load(var_44);
            var_51 = wp::load(var_46);
            var_52 = wp::load(var_48);
            var_49 = closest_0(var_p, var_50, var_51, var_52);
            var_53 = wp::sub(var_p, var_49);
            var_54 = wp::length_sq(var_53);
            // if dist<best or (dist==best and face<bestface):best=dist;c=candidate;bestface=face       <L 21>
            var_56 = (var_54 < var_28);
            var_55 = var_56;
            if (!var_55) {
                var_58 = (var_54 == var_28);
                var_57 = var_58;
                if (var_57) {
                    var_59 = (var_42 < var_30);
                    var_57 = var_57 && var_59;
                }
                var_55 = var_55 || var_57;
            }
            if (var_55) {
                var_60 = wp::copy(var_54);
                var_61 = wp::copy(var_49);
                var_62 = wp::copy(var_42);
            }
            var_63 = wp::where(var_55, var_61, var_23);
            var_64 = wp::where(var_55, var_60, var_28);
            var_65 = wp::where(var_55, var_62, var_30);
            wp::assign(var_23, var_63);
            wp::assign(var_28, var_64);
            wp::assign(var_30, var_65);
            goto start_for_0;
        end_for_0:;
        // d=p-c;l=wp.sqrt(best);r.phi=wp.float64(q.sign)*l                                   <L 22>
        var_66 = wp::sub(var_p, var_23);
        var_67 = wp::sqrt(var_28);
        var_68 = &((var_6).sign);
        var_70 = wp::load(var_68);
        var_69 = wp::float64(var_70);
        var_71 = wp::mul(var_69, var_67);
        var_0.phi = var_71;
        // if l>wp.float64(1e-15):r.normal=wp.float64(q.sign)*d/l                             <L 23>
        var_72 = 1e-15;
        var_73 = (var_67 > var_72);
        if (var_73) {
            var_74 = &((var_6).sign);
            var_76 = wp::load(var_74);
            var_75 = wp::float64(var_76);
            var_77 = wp::mul(var_75, var_66);
            var_78 = wp::div(var_77, var_67);
            var_0.normal = var_78;
        }
        if (!var_73) {
            // else:r.normal=wp.normalize(wp.cross(tri[bestface,1]-tri[bestface,0],tri[bestface,2]-tri[bestface,0]))       <L 24>
            var_80 = wp::address(var_tri, var_30, var_79);
            var_82 = wp::address(var_tri, var_30, var_81);
            var_84 = wp::load(var_80);
            var_85 = wp::load(var_82);
            var_83 = wp::sub(var_84, var_85);
            var_87 = wp::address(var_tri, var_30, var_86);
            var_89 = wp::address(var_tri, var_30, var_88);
            var_91 = wp::load(var_87);
            var_92 = wp::load(var_89);
            var_90 = wp::sub(var_91, var_92);
            var_93 = wp::cross(var_83, var_90);
            var_94 = wp::normalize(var_93);
            var_0.normal = var_94;
        }
    }
    var_95 = wp::load(var_9);
    // return r                                                                               <L 25>
    return var_0;
}


// /home/omen/Documents/Codex/experiments/tomato_adaptive_contact_20261112_v24/src/contact_gpu_precise.py:12
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


// /home/omen/Documents/Codex/experiments/tomato_adaptive_contact_20261112_v24/src/exact_cad_gpu.py:9
static CUDA_CALLABLE void adj_signed_0(
    wp::uint64 var_mesh,
    wp::array_t<wp::vec_t<3, wp::float64>> var_tri,
    wp::vec_t<3, wp::float64> var_p,
    wp::uint64 & adj_mesh,
    wp::array_t<wp::vec_t<3, wp::float64>> & adj_tri,
    wp::vec_t<3, wp::float64> & adj_p,
    Signed_7e3cff60 & adj_ret)
{
	// reverse mode disabled (module option "enable_backward" is False or no dependent kernel found with "enable_backward")
}



extern "C" __global__ void collect_15c6759a_cuda_kernel_forward(
    wp::launch_bounds_t<1> dim,
    wp::array_t<wp::vec_t<3, wp::float64>> var_ff,
    wp::array_t<wp::float64> var_uu,
    wp::array_t<wp::float64> var_dd,
    wp::array_t<wp::float64> var_ww,
    wp::array_t<wp::vec_t<3, wp::float64>> var_mm,
    wp::array_t<wp::vec_t<3, wp::float32>> var_cf,
    wp::array_t<wp::float32> var_cu,
    wp::array_t<wp::float32> var_cp,
    wp::array_t<wp::float32> var_power,
    wp::array_t<wp::vec_t<3, wp::float32>> var_moment)
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
        wp::int32 var_2;
        const wp::int32 var_3 = 3;
        wp::int32 var_4;
        wp::vec_t<3, wp::float64>* var_5;
        wp::vec_t<3, wp::float32> var_6;
        wp::vec_t<3, wp::float64> var_7;
        wp::float64* var_8;
        wp::float64 var_9;
        wp::float64 var_10;
        wp::float64 var_11;
        wp::float32 var_12;
        wp::float64* var_13;
        wp::float64 var_14;
        wp::float64 var_15;
        wp::float64 var_16;
        wp::float32 var_17;
        wp::float64* var_18;
        wp::float64 var_19;
        wp::float64 var_20;
        wp::float64 var_21;
        wp::float32 var_22;
        wp::vec_t<3, wp::float64>* var_23;
        wp::float64 var_24;
        wp::vec_t<3, wp::float64> var_25;
        wp::vec_t<3, wp::float64> var_26;
        wp::vec_t<3, wp::float32> var_27;
        //---------
        // forward
        // def collect(ff:wp.array2d(dtype=wp.vec3d),uu:wp.array(dtype=wp.float64),dd:wp.array(dtype=wp.float64),ww:wp.array(dtype=wp.float64),mm:wp.array(dtype=wp.vec3d),cf:wp.array(dtype=wp.vec3),cu:wp.array(dtype=float),cp:wp.array(dtype=float),power:wp.array(dtype=float),moment:wp.array(dtype=wp.vec3)):       <L 78>
        // k=wp.tid();face=k//3;vertex=k%3;cf[k]=wp.vec3(ff[face,vertex]);cu[k]=float(uu[face]/wp.float64(3.));cp[k]=float(dd[face]/wp.float64(3.));power[k]=float(ww[face]/wp.float64(3.));moment[k]=wp.vec3(mm[face]/wp.float64(3.))       <L 79>
        var_0 = builtin_tid1d();
        var_2 = wp::floordiv(var_0, var_1);
        var_4 = wp::mod(var_0, var_3);
        var_5 = wp::address(var_ff, var_2, var_4);
        var_7 = wp::load(var_5);
        var_6 = wp::vec_t<3, wp::float32>(var_7);
        wp::array_store(var_cf, var_0, var_6);
        var_8 = wp::address(var_uu, var_2);
        var_9 = 3.0;
        var_11 = wp::load(var_8);
        var_10 = wp::div(var_11, var_9);
        var_12 = wp::float(var_10);
        wp::array_store(var_cu, var_0, var_12);
        var_13 = wp::address(var_dd, var_2);
        var_14 = 3.0;
        var_16 = wp::load(var_13);
        var_15 = wp::div(var_16, var_14);
        var_17 = wp::float(var_15);
        wp::array_store(var_cp, var_0, var_17);
        var_18 = wp::address(var_ww, var_2);
        var_19 = 3.0;
        var_21 = wp::load(var_18);
        var_20 = wp::div(var_21, var_19);
        var_22 = wp::float(var_20);
        wp::array_store(var_power, var_0, var_22);
        var_23 = wp::address(var_mm, var_2);
        var_24 = 3.0;
        var_26 = wp::load(var_23);
        var_25 = wp::div(var_26, var_24);
        var_27 = wp::vec_t<3, wp::float32>(var_25);
        wp::array_store(var_moment, var_0, var_27);
    }
}



extern "C" __global__ void frame_9ea4241c_cuda_kernel_forward(
    wp::launch_bounds_t<1> dim,
    wp::mat_t<3, 3, wp::float64> var_R,
    wp::vec_t<3, wp::float64> var_T0,
    wp::vec_t<3, wp::float64> var_travel,
    wp::float64 var_load,
    wp::float64 var_hold,
    wp::array_t<wp::float64> var_clock,
    wp::array_t<wp::int32> var_ptr,
    wp::array_t<wp::int32> var_ids,
    wp::array_t<wp::float64> var_w,
    wp::array_t<wp::vec_t<3, wp::float64>> var_ref,
    wp::array_t<wp::vec_t<3, wp::float32>> var_q,
    wp::array_t<wp::vec_t<3, wp::float32>> var_v,
    wp::array_t<wp::mat_t<3, 3, wp::float64>> var_X,
    wp::array_t<wp::mat_t<3, 3, wp::float64>> var_V,
    wp::array_t<wp::mat_t<3, 3, wp::float64>> var_local,
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
        const wp::int32 var_55 = 0;
        bool var_56;
        const wp::int32 var_57 = 0;
        const wp::int32 var_58 = 1;
        wp::float64 var_59;
        wp::mat_t<3, 3, wp::float64> var_60;
        wp::float64 var_61;
        wp::mat_t<3, 3, wp::float64> var_62;
        wp::float64 var_63;
        wp::mat_t<3, 3, wp::float64> var_64;
        const wp::int32 var_65 = 0;
        const wp::int32 var_66 = 3;
        wp::int32 var_67;
        wp::int32 var_68;
        wp::vec_t<3, wp::float64>* var_69;
        wp::vec_t<3, wp::float64> var_70;
        wp::vec_t<3, wp::float64> var_71;
        wp::float64 var_72;
        wp::vec_t<3, wp::float64> var_73;
        wp::int32* var_74;
        const wp::int32 var_75 = 1;
        wp::int32 var_76;
        wp::int32* var_77;
        wp::range_t var_78;
        wp::int32 var_79;
        wp::int32 var_80;
        wp::int32 var_81;
        wp::float64* var_82;
        wp::int32* var_83;
        wp::vec_t<3, wp::float32>* var_84;
        wp::int32 var_85;
        wp::vec_t<3, wp::float64> var_86;
        wp::vec_t<3, wp::float32> var_87;
        wp::vec_t<3, wp::float64> var_88;
        wp::float64 var_89;
        wp::vec_t<3, wp::float64> var_90;
        wp::float64* var_91;
        wp::int32* var_92;
        wp::vec_t<3, wp::float32>* var_93;
        wp::int32 var_94;
        wp::vec_t<3, wp::float64> var_95;
        wp::vec_t<3, wp::float32> var_96;
        wp::vec_t<3, wp::float64> var_97;
        wp::float64 var_98;
        wp::vec_t<3, wp::float64> var_99;
        wp::mat_t<3, 3, wp::float64> var_100;
        wp::vec_t<3, wp::float64> var_101;
        wp::vec_t<3, wp::float64> var_102;
        const wp::int32 var_103 = 0;
        wp::float64 var_104;
        wp::float64 var_105;
        wp::float64 var_106;
        const wp::int32 var_107 = 1;
        wp::float64 var_108;
        wp::float64 var_109;
        wp::float64 var_110;
        const wp::int32 var_111 = 2;
        wp::float64 var_112;
        wp::float64 var_113;
        wp::float64 var_114;
        const wp::int32 var_115 = 1;
        const wp::int32 var_116 = 3;
        wp::int32 var_117;
        wp::int32 var_118;
        wp::vec_t<3, wp::float64>* var_119;
        wp::vec_t<3, wp::float64> var_120;
        wp::vec_t<3, wp::float64> var_121;
        wp::float64 var_122;
        wp::vec_t<3, wp::float64> var_123;
        wp::int32* var_124;
        const wp::int32 var_125 = 1;
        wp::int32 var_126;
        wp::int32* var_127;
        wp::range_t var_128;
        wp::int32 var_129;
        wp::int32 var_130;
        wp::int32 var_131;
        wp::float64* var_132;
        wp::int32* var_133;
        wp::vec_t<3, wp::float32>* var_134;
        wp::int32 var_135;
        wp::vec_t<3, wp::float64> var_136;
        wp::vec_t<3, wp::float32> var_137;
        wp::vec_t<3, wp::float64> var_138;
        wp::float64 var_139;
        wp::vec_t<3, wp::float64> var_140;
        wp::float64* var_141;
        wp::int32* var_142;
        wp::vec_t<3, wp::float32>* var_143;
        wp::int32 var_144;
        wp::vec_t<3, wp::float64> var_145;
        wp::vec_t<3, wp::float32> var_146;
        wp::vec_t<3, wp::float64> var_147;
        wp::float64 var_148;
        wp::vec_t<3, wp::float64> var_149;
        wp::mat_t<3, 3, wp::float64> var_150;
        wp::vec_t<3, wp::float64> var_151;
        wp::vec_t<3, wp::float64> var_152;
        const wp::int32 var_153 = 0;
        wp::float64 var_154;
        wp::float64 var_155;
        wp::float64 var_156;
        const wp::int32 var_157 = 1;
        wp::float64 var_158;
        wp::float64 var_159;
        wp::float64 var_160;
        const wp::int32 var_161 = 2;
        wp::float64 var_162;
        wp::float64 var_163;
        wp::float64 var_164;
        const wp::int32 var_165 = 2;
        const wp::int32 var_166 = 3;
        wp::int32 var_167;
        wp::int32 var_168;
        wp::vec_t<3, wp::float64>* var_169;
        wp::vec_t<3, wp::float64> var_170;
        wp::vec_t<3, wp::float64> var_171;
        wp::float64 var_172;
        wp::vec_t<3, wp::float64> var_173;
        wp::int32* var_174;
        const wp::int32 var_175 = 1;
        wp::int32 var_176;
        wp::int32* var_177;
        wp::range_t var_178;
        wp::int32 var_179;
        wp::int32 var_180;
        wp::int32 var_181;
        wp::float64* var_182;
        wp::int32* var_183;
        wp::vec_t<3, wp::float32>* var_184;
        wp::int32 var_185;
        wp::vec_t<3, wp::float64> var_186;
        wp::vec_t<3, wp::float32> var_187;
        wp::vec_t<3, wp::float64> var_188;
        wp::float64 var_189;
        wp::vec_t<3, wp::float64> var_190;
        wp::float64* var_191;
        wp::int32* var_192;
        wp::vec_t<3, wp::float32>* var_193;
        wp::int32 var_194;
        wp::vec_t<3, wp::float64> var_195;
        wp::vec_t<3, wp::float32> var_196;
        wp::vec_t<3, wp::float64> var_197;
        wp::float64 var_198;
        wp::vec_t<3, wp::float64> var_199;
        wp::mat_t<3, 3, wp::float64> var_200;
        wp::vec_t<3, wp::float64> var_201;
        wp::vec_t<3, wp::float64> var_202;
        const wp::int32 var_203 = 0;
        wp::float64 var_204;
        wp::float64 var_205;
        wp::float64 var_206;
        const wp::int32 var_207 = 1;
        wp::float64 var_208;
        wp::float64 var_209;
        wp::float64 var_210;
        const wp::int32 var_211 = 2;
        wp::float64 var_212;
        wp::float64 var_213;
        wp::float64 var_214;
        //---------
        // forward
        // def frame(R:wp.mat33d,T0:wp.vec3d,travel:wp.vec3d,load:wp.float64,hold:wp.float64,clock:wp.array(dtype=wp.float64),ptr:wp.array(dtype=int),ids:wp.array(dtype=int),w:wp.array(dtype=wp.float64),ref:wp.array(dtype=wp.vec3d),q:wp.array(dtype=wp.vec3),v:wp.array(dtype=wp.vec3),X:wp.array(dtype=wp.mat33d),V:wp.array(dtype=wp.mat33d),local:wp.array(dtype=wp.mat33d),pose:wp.array(dtype=wp.vec3d)):       <L 15>
        // face=wp.tid();t=clock[0];shape=wp.float64(0.);speed=wp.float64(0.);pi=wp.float64(3.141592653589793)       <L 16>
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
        // T=T0+travel*shape;tv=travel*speed                                                      <L 21>
        var_52 = wp::mul(var_travel, var_50);
        var_53 = wp::add(var_T0, var_52);
        var_54 = wp::mul(var_travel, var_51);
        // if face==0:pose[0]=T;pose[1]=tv                                                        <L 22>
        var_56 = (var_0 == var_55);
        if (var_56) {
            wp::array_store(var_pose, var_57, var_53);
            wp::array_store(var_pose, var_58, var_54);
        }
        // xx=wp.mat33d(wp.float64(0.));vv=wp.mat33d(wp.float64(0.));ll=wp.mat33d(wp.float64(0.))       <L 23>
        var_59 = 0.0;
        var_60 = wp::mat_t<3, 3, wp::float64>(var_59);
        var_61 = 0.0;
        var_62 = wp::mat_t<3, 3, wp::float64>(var_61);
        var_63 = 0.0;
        var_64 = wp::mat_t<3, 3, wp::float64>(var_63);
        // for u in range(3):                                                                     <L 24>
        // i=3*face+u;x=ref[i];vel=wp.vec3d(wp.float64(0.))                                       <L 25>
        var_67 = wp::mul(var_66, var_0);
        var_68 = wp::add(var_67, var_65);
        var_69 = wp::address(var_ref, var_68);
        var_71 = wp::load(var_69);
        var_70 = wp::copy(var_71);
        var_72 = 0.0;
        var_73 = wp::vec_t<3, wp::float64>(var_72);
        // for j in range(ptr[i],ptr[i+1]):x+=w[j]*wp.vec3d(q[ids[j]]);vel+=w[j]*wp.vec3d(v[ids[j]])       <L 26>
        var_74 = wp::address(var_ptr, var_68);
        var_76 = wp::add(var_68, var_75);
        var_77 = wp::address(var_ptr, var_76);
        var_79 = wp::load(var_74);
        var_80 = wp::load(var_77);
        var_78 = wp::range(var_79, var_80);
        start_for_0:;
            if (iter_cmp(var_78) == 0) goto end_for_0;
            var_81 = wp::iter_next(var_78);
            var_82 = wp::address(var_w, var_81);
            var_83 = wp::address(var_ids, var_81);
            var_85 = wp::load(var_83);
            var_84 = wp::address(var_q, var_85);
            var_87 = wp::load(var_84);
            var_86 = wp::vec_t<3, wp::float64>(var_87);
            var_89 = wp::load(var_82);
            var_88 = wp::mul(var_89, var_86);
            var_90 = wp::add(var_70, var_88);
            var_91 = wp::address(var_w, var_81);
            var_92 = wp::address(var_ids, var_81);
            var_94 = wp::load(var_92);
            var_93 = wp::address(var_v, var_94);
            var_96 = wp::load(var_93);
            var_95 = wp::vec_t<3, wp::float64>(var_96);
            var_98 = wp::load(var_91);
            var_97 = wp::mul(var_98, var_95);
            var_99 = wp::add(var_73, var_97);
            wp::assign(var_70, var_90);
            wp::assign(var_73, var_99);
            goto start_for_0;
        end_for_0:;
        // p=wp.transpose(R)*(x-T)                                                                <L 27>
        var_100 = wp::transpose(var_R);
        var_101 = wp::sub(var_70, var_53);
        var_102 = wp::mul(var_100, var_101);
        // for k in range(3):xx[u,k]=x[k];vv[u,k]=vel[k];ll[u,k]=p[k]                             <L 28>
        var_104 = wp::extract(var_70, var_103);
        wp::assign_inplace(var_60, var_65, var_103, var_104);
        var_105 = wp::extract(var_73, var_103);
        wp::assign_inplace(var_62, var_65, var_103, var_105);
        var_106 = wp::extract(var_102, var_103);
        wp::assign_inplace(var_64, var_65, var_103, var_106);
        var_108 = wp::extract(var_70, var_107);
        wp::assign_inplace(var_60, var_65, var_107, var_108);
        var_109 = wp::extract(var_73, var_107);
        wp::assign_inplace(var_62, var_65, var_107, var_109);
        var_110 = wp::extract(var_102, var_107);
        wp::assign_inplace(var_64, var_65, var_107, var_110);
        var_112 = wp::extract(var_70, var_111);
        wp::assign_inplace(var_60, var_65, var_111, var_112);
        var_113 = wp::extract(var_73, var_111);
        wp::assign_inplace(var_62, var_65, var_111, var_113);
        var_114 = wp::extract(var_102, var_111);
        wp::assign_inplace(var_64, var_65, var_111, var_114);
        // i=3*face+u;x=ref[i];vel=wp.vec3d(wp.float64(0.))                                       <L 25>
        var_117 = wp::mul(var_116, var_0);
        var_118 = wp::add(var_117, var_115);
        var_119 = wp::address(var_ref, var_118);
        var_121 = wp::load(var_119);
        var_120 = wp::copy(var_121);
        var_122 = 0.0;
        var_123 = wp::vec_t<3, wp::float64>(var_122);
        // for j in range(ptr[i],ptr[i+1]):x+=w[j]*wp.vec3d(q[ids[j]]);vel+=w[j]*wp.vec3d(v[ids[j]])       <L 26>
        var_124 = wp::address(var_ptr, var_118);
        var_126 = wp::add(var_118, var_125);
        var_127 = wp::address(var_ptr, var_126);
        var_129 = wp::load(var_124);
        var_130 = wp::load(var_127);
        var_128 = wp::range(var_129, var_130);
        start_for_2:;
            if (iter_cmp(var_128) == 0) goto end_for_2;
            var_131 = wp::iter_next(var_128);
            var_132 = wp::address(var_w, var_131);
            var_133 = wp::address(var_ids, var_131);
            var_135 = wp::load(var_133);
            var_134 = wp::address(var_q, var_135);
            var_137 = wp::load(var_134);
            var_136 = wp::vec_t<3, wp::float64>(var_137);
            var_139 = wp::load(var_132);
            var_138 = wp::mul(var_139, var_136);
            var_140 = wp::add(var_120, var_138);
            var_141 = wp::address(var_w, var_131);
            var_142 = wp::address(var_ids, var_131);
            var_144 = wp::load(var_142);
            var_143 = wp::address(var_v, var_144);
            var_146 = wp::load(var_143);
            var_145 = wp::vec_t<3, wp::float64>(var_146);
            var_148 = wp::load(var_141);
            var_147 = wp::mul(var_148, var_145);
            var_149 = wp::add(var_123, var_147);
            wp::assign(var_120, var_140);
            wp::assign(var_123, var_149);
            goto start_for_2;
        end_for_2:;
        // p=wp.transpose(R)*(x-T)                                                                <L 27>
        var_150 = wp::transpose(var_R);
        var_151 = wp::sub(var_120, var_53);
        var_152 = wp::mul(var_150, var_151);
        // for k in range(3):xx[u,k]=x[k];vv[u,k]=vel[k];ll[u,k]=p[k]                             <L 28>
        var_154 = wp::extract(var_120, var_153);
        wp::assign_inplace(var_60, var_115, var_153, var_154);
        var_155 = wp::extract(var_123, var_153);
        wp::assign_inplace(var_62, var_115, var_153, var_155);
        var_156 = wp::extract(var_152, var_153);
        wp::assign_inplace(var_64, var_115, var_153, var_156);
        var_158 = wp::extract(var_120, var_157);
        wp::assign_inplace(var_60, var_115, var_157, var_158);
        var_159 = wp::extract(var_123, var_157);
        wp::assign_inplace(var_62, var_115, var_157, var_159);
        var_160 = wp::extract(var_152, var_157);
        wp::assign_inplace(var_64, var_115, var_157, var_160);
        var_162 = wp::extract(var_120, var_161);
        wp::assign_inplace(var_60, var_115, var_161, var_162);
        var_163 = wp::extract(var_123, var_161);
        wp::assign_inplace(var_62, var_115, var_161, var_163);
        var_164 = wp::extract(var_152, var_161);
        wp::assign_inplace(var_64, var_115, var_161, var_164);
        // i=3*face+u;x=ref[i];vel=wp.vec3d(wp.float64(0.))                                       <L 25>
        var_167 = wp::mul(var_166, var_0);
        var_168 = wp::add(var_167, var_165);
        var_169 = wp::address(var_ref, var_168);
        var_171 = wp::load(var_169);
        var_170 = wp::copy(var_171);
        var_172 = 0.0;
        var_173 = wp::vec_t<3, wp::float64>(var_172);
        // for j in range(ptr[i],ptr[i+1]):x+=w[j]*wp.vec3d(q[ids[j]]);vel+=w[j]*wp.vec3d(v[ids[j]])       <L 26>
        var_174 = wp::address(var_ptr, var_168);
        var_176 = wp::add(var_168, var_175);
        var_177 = wp::address(var_ptr, var_176);
        var_179 = wp::load(var_174);
        var_180 = wp::load(var_177);
        var_178 = wp::range(var_179, var_180);
        start_for_4:;
            if (iter_cmp(var_178) == 0) goto end_for_4;
            var_181 = wp::iter_next(var_178);
            var_182 = wp::address(var_w, var_181);
            var_183 = wp::address(var_ids, var_181);
            var_185 = wp::load(var_183);
            var_184 = wp::address(var_q, var_185);
            var_187 = wp::load(var_184);
            var_186 = wp::vec_t<3, wp::float64>(var_187);
            var_189 = wp::load(var_182);
            var_188 = wp::mul(var_189, var_186);
            var_190 = wp::add(var_170, var_188);
            var_191 = wp::address(var_w, var_181);
            var_192 = wp::address(var_ids, var_181);
            var_194 = wp::load(var_192);
            var_193 = wp::address(var_v, var_194);
            var_196 = wp::load(var_193);
            var_195 = wp::vec_t<3, wp::float64>(var_196);
            var_198 = wp::load(var_191);
            var_197 = wp::mul(var_198, var_195);
            var_199 = wp::add(var_173, var_197);
            wp::assign(var_170, var_190);
            wp::assign(var_173, var_199);
            goto start_for_4;
        end_for_4:;
        // p=wp.transpose(R)*(x-T)                                                                <L 27>
        var_200 = wp::transpose(var_R);
        var_201 = wp::sub(var_170, var_53);
        var_202 = wp::mul(var_200, var_201);
        // for k in range(3):xx[u,k]=x[k];vv[u,k]=vel[k];ll[u,k]=p[k]                             <L 28>
        var_204 = wp::extract(var_170, var_203);
        wp::assign_inplace(var_60, var_165, var_203, var_204);
        var_205 = wp::extract(var_173, var_203);
        wp::assign_inplace(var_62, var_165, var_203, var_205);
        var_206 = wp::extract(var_202, var_203);
        wp::assign_inplace(var_64, var_165, var_203, var_206);
        var_208 = wp::extract(var_170, var_207);
        wp::assign_inplace(var_60, var_165, var_207, var_208);
        var_209 = wp::extract(var_173, var_207);
        wp::assign_inplace(var_62, var_165, var_207, var_209);
        var_210 = wp::extract(var_202, var_207);
        wp::assign_inplace(var_64, var_165, var_207, var_210);
        var_212 = wp::extract(var_170, var_211);
        wp::assign_inplace(var_60, var_165, var_211, var_212);
        var_213 = wp::extract(var_173, var_211);
        wp::assign_inplace(var_62, var_165, var_211, var_213);
        var_214 = wp::extract(var_202, var_211);
        wp::assign_inplace(var_64, var_165, var_211, var_214);
        // X[face]=xx;V[face]=vv;local[face]=ll                                                   <L 29>
        wp::array_store(var_X, var_0, var_60);
        wp::array_store(var_V, var_0, var_62);
        wp::array_store(var_local, var_0, var_64);
    }
}



extern "C" __global__ void quadrature_c3cc88aa_cuda_kernel_forward(
    wp::launch_bounds_t<1> dim,
    wp::uint64 var_mesh,
    wp::array_t<wp::vec_t<3, wp::float64>> var_tri,
    wp::mat_t<3, 3, wp::float64> var_R,
    wp::array_t<wp::vec_t<3, wp::float64>> var_pose,
    wp::array_t<wp::mat_t<3, 3, wp::float64>> var_X,
    wp::array_t<wp::mat_t<3, 3, wp::float64>> var_V,
    wp::array_t<wp::float64> var_areas,
    wp::int32 var_ncells,
    wp::array_t<wp::mat_t<3, 3, wp::float64>> var_masters,
    wp::array_t<wp::vec_t<3, wp::float64>> var_polygon,
    wp::array_t<wp::int32> var_polycounts,
    wp::array_t<wp::int32> var_sources,
    wp::array_t<wp::int32> var_active,
    wp::array_t<wp::int32> var_active_ids,
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
        const wp::int32 var_5 = 8;
        wp::int32 var_6;
        wp::int32 var_7;
        wp::int32 var_8;
        const wp::int32 var_9 = 8;
        wp::int32 var_10;
        wp::int32 var_11;
        bool var_12;
        const wp::int32 var_13 = 0;
        wp::int32* var_14;
        bool var_15;
        wp::int32 var_16;
        const wp::int32 var_17 = 0;
        wp::int32* var_18;
        const wp::int32 var_19 = 0;
        bool var_20;
        wp::int32 var_21;
        wp::int32* var_22;
        wp::int32 var_23;
        wp::int32 var_24;
        wp::int32 var_25;
        wp::int32* var_26;
        wp::int32 var_27;
        wp::int32 var_28;
        wp::int32* var_29;
        wp::int32 var_30;
        wp::int32 var_31;
        const wp::int32 var_32 = 2;
        wp::int32 var_33;
        bool var_34;
        const wp::int32 var_35 = 0;
        wp::vec_t<3, wp::float64>* var_36;
        const wp::int32 var_37 = 1;
        wp::int32 var_38;
        wp::vec_t<3, wp::float64>* var_39;
        const wp::int32 var_40 = 2;
        wp::int32 var_41;
        wp::vec_t<3, wp::float64>* var_42;
        wp::mat_t<3, 3, wp::float64> var_43;
        wp::vec_t<3, wp::float64> var_44;
        wp::vec_t<3, wp::float64> var_45;
        wp::vec_t<3, wp::float64> var_46;
        wp::float64* var_47;
        wp::float64 var_48;
        wp::float64 var_49;
        wp::float64 var_50;
        wp::float64 var_51;
        wp::float64 var_52;
        wp::float64 var_53;
        wp::mat_t<3, 3, wp::float64>* var_54;
        wp::mat_t<3, 3, wp::float64> var_55;
        wp::mat_t<3, 3, wp::float64> var_56;
        wp::mat_t<3, 3, wp::float64>* var_57;
        wp::mat_t<3, 3, wp::float64> var_58;
        wp::mat_t<3, 3, wp::float64> var_59;
        wp::mat_t<3, 3, wp::float64>* var_60;
        wp::mat_t<3, 3, wp::float64> var_61;
        wp::mat_t<3, 3, wp::float64> var_62;
        const wp::int32 var_63 = 0;
        wp::vec_t<3, wp::float64>* var_64;
        wp::vec_t<3, wp::float64> var_65;
        wp::vec_t<3, wp::float64> var_66;
        const wp::int32 var_67 = 1;
        wp::vec_t<3, wp::float64>* var_68;
        wp::vec_t<3, wp::float64> var_69;
        wp::vec_t<3, wp::float64> var_70;
        wp::float64 var_71;
        wp::mat_t<3, 3, wp::float64> var_72;
        wp::float64 var_73;
        wp::float64 var_74;
        wp::float64 var_75;
        wp::float64 var_76;
        wp::vec_t<3, wp::float64> var_77;
        const wp::int32 var_78 = 0;
        const wp::float32 var_79 = 1.0;
        const wp::float32 var_80 = 6.0;
        wp::float32 var_81;
        wp::float64 var_82;
        wp::vec_t<3, wp::float64> var_83;
        const wp::float32 var_84 = 2.0;
        const wp::float32 var_85 = 3.0;
        wp::float32 var_86;
        wp::float64 var_87;
        wp::mat_t<3, 3, wp::float64> var_88;
        wp::vec_t<3, wp::float64> var_89;
        wp::mat_t<3, 3, wp::float64> var_90;
        wp::vec_t<3, wp::float64> var_91;
        wp::mat_t<3, 3, wp::float64> var_92;
        wp::vec_t<3, wp::float64> var_93;
        wp::mat_t<3, 3, wp::float64> var_94;
        wp::vec_t<3, wp::float64> var_95;
        wp::vec_t<3, wp::float64> var_96;
        Signed_7e3cff60 var_97;
        wp::float64* var_98;
        wp::float64 var_99;
        wp::float64 var_100;
        wp::float64 var_101;
        wp::float64 var_102;
        wp::vec_t<3, wp::float64>* var_103;
        wp::vec_t<3, wp::float64> var_104;
        wp::vec_t<3, wp::float64> var_105;
        wp::float64 var_106;
        wp::float64 var_107;
        wp::float64 var_108;
        wp::float64 var_109;
        wp::float64 var_110;
        wp::vec_t<3, wp::float64> var_111;
        wp::float64 var_112;
        wp::vec_t<3, wp::float64> var_113;
        wp::vec_t<3, wp::float64> var_114;
        wp::float64 var_115;
        wp::float64 var_116;
        wp::vec_t<3, wp::float64> var_117;
        wp::float64 var_118;
        bool var_119;
        wp::float64 var_120;
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
        wp::vec_t<3, wp::float64> var_131;
        const wp::int32 var_132 = 0;
        const wp::int32 var_133 = 0;
        wp::float64 var_134;
        wp::float64 var_135;
        wp::float64 var_136;
        const wp::int32 var_137 = 1;
        wp::float64 var_138;
        wp::float64 var_139;
        wp::float64 var_140;
        const wp::int32 var_141 = 2;
        wp::float64 var_142;
        wp::float64 var_143;
        wp::float64 var_144;
        const wp::int32 var_145 = 1;
        const wp::int32 var_146 = 0;
        wp::float64 var_147;
        wp::float64 var_148;
        wp::float64 var_149;
        const wp::int32 var_150 = 1;
        wp::float64 var_151;
        wp::float64 var_152;
        wp::float64 var_153;
        const wp::int32 var_154 = 2;
        wp::float64 var_155;
        wp::float64 var_156;
        wp::float64 var_157;
        const wp::int32 var_158 = 2;
        const wp::int32 var_159 = 0;
        wp::float64 var_160;
        wp::float64 var_161;
        wp::float64 var_162;
        const wp::int32 var_163 = 1;
        wp::float64 var_164;
        wp::float64 var_165;
        wp::float64 var_166;
        const wp::int32 var_167 = 2;
        wp::float64 var_168;
        wp::float64 var_169;
        wp::float64 var_170;
        wp::float64 var_171;
        wp::float64 var_172;
        wp::float64 var_173;
        wp::float64 var_174;
        wp::float64 var_175;
        wp::float64 var_176;
        wp::float64 var_177;
        wp::float64 var_178;
        wp::vec_t<3, wp::float64> var_179;
        wp::vec_t<3, wp::float64> var_180;
        wp::vec_t<3, wp::float64> var_181;
        const wp::int32 var_182 = 1;
        const wp::float32 var_183 = 1.0;
        const wp::float32 var_184 = 6.0;
        wp::float32 var_185;
        wp::float64 var_186;
        wp::vec_t<3, wp::float64> var_187;
        const wp::float32 var_188 = 2.0;
        const wp::float32 var_189 = 3.0;
        wp::float32 var_190;
        wp::float64 var_191;
        wp::mat_t<3, 3, wp::float64> var_192;
        wp::vec_t<3, wp::float64> var_193;
        wp::mat_t<3, 3, wp::float64> var_194;
        wp::vec_t<3, wp::float64> var_195;
        wp::mat_t<3, 3, wp::float64> var_196;
        wp::vec_t<3, wp::float64> var_197;
        wp::mat_t<3, 3, wp::float64> var_198;
        wp::vec_t<3, wp::float64> var_199;
        wp::vec_t<3, wp::float64> var_200;
        Signed_7e3cff60 var_201;
        wp::float64* var_202;
        wp::float64 var_203;
        wp::float64 var_204;
        wp::float64 var_205;
        wp::float64 var_206;
        wp::vec_t<3, wp::float64>* var_207;
        wp::vec_t<3, wp::float64> var_208;
        wp::vec_t<3, wp::float64> var_209;
        wp::float64 var_210;
        wp::float64 var_211;
        wp::float64 var_212;
        wp::float64 var_213;
        wp::float64 var_214;
        wp::vec_t<3, wp::float64> var_215;
        wp::float64 var_216;
        wp::vec_t<3, wp::float64> var_217;
        wp::vec_t<3, wp::float64> var_218;
        wp::float64 var_219;
        wp::float64 var_220;
        wp::vec_t<3, wp::float64> var_221;
        wp::float64 var_222;
        bool var_223;
        wp::float64 var_224;
        wp::float64 var_225;
        wp::float64 var_226;
        wp::float64 var_227;
        wp::float64 var_228;
        wp::float64 var_229;
        wp::float64 var_230;
        wp::vec_t<3, wp::float64> var_231;
        wp::vec_t<3, wp::float64> var_232;
        wp::vec_t<3, wp::float64> var_233;
        wp::vec_t<3, wp::float64> var_234;
        wp::vec_t<3, wp::float64> var_235;
        const wp::int32 var_236 = 0;
        const wp::int32 var_237 = 0;
        wp::float64 var_238;
        wp::float64 var_239;
        wp::float64 var_240;
        const wp::int32 var_241 = 1;
        wp::float64 var_242;
        wp::float64 var_243;
        wp::float64 var_244;
        const wp::int32 var_245 = 2;
        wp::float64 var_246;
        wp::float64 var_247;
        wp::float64 var_248;
        const wp::int32 var_249 = 1;
        const wp::int32 var_250 = 0;
        wp::float64 var_251;
        wp::float64 var_252;
        wp::float64 var_253;
        const wp::int32 var_254 = 1;
        wp::float64 var_255;
        wp::float64 var_256;
        wp::float64 var_257;
        const wp::int32 var_258 = 2;
        wp::float64 var_259;
        wp::float64 var_260;
        wp::float64 var_261;
        const wp::int32 var_262 = 2;
        const wp::int32 var_263 = 0;
        wp::float64 var_264;
        wp::float64 var_265;
        wp::float64 var_266;
        const wp::int32 var_267 = 1;
        wp::float64 var_268;
        wp::float64 var_269;
        wp::float64 var_270;
        const wp::int32 var_271 = 2;
        wp::float64 var_272;
        wp::float64 var_273;
        wp::float64 var_274;
        wp::float64 var_275;
        wp::float64 var_276;
        wp::float64 var_277;
        wp::float64 var_278;
        wp::float64 var_279;
        wp::float64 var_280;
        wp::float64 var_281;
        wp::float64 var_282;
        wp::vec_t<3, wp::float64> var_283;
        wp::vec_t<3, wp::float64> var_284;
        wp::vec_t<3, wp::float64> var_285;
        const wp::int32 var_286 = 2;
        const wp::float32 var_287 = 1.0;
        const wp::float32 var_288 = 6.0;
        wp::float32 var_289;
        wp::float64 var_290;
        wp::vec_t<3, wp::float64> var_291;
        const wp::float32 var_292 = 2.0;
        const wp::float32 var_293 = 3.0;
        wp::float32 var_294;
        wp::float64 var_295;
        wp::mat_t<3, 3, wp::float64> var_296;
        wp::vec_t<3, wp::float64> var_297;
        wp::mat_t<3, 3, wp::float64> var_298;
        wp::vec_t<3, wp::float64> var_299;
        wp::mat_t<3, 3, wp::float64> var_300;
        wp::vec_t<3, wp::float64> var_301;
        wp::mat_t<3, 3, wp::float64> var_302;
        wp::vec_t<3, wp::float64> var_303;
        wp::vec_t<3, wp::float64> var_304;
        Signed_7e3cff60 var_305;
        wp::float64* var_306;
        wp::float64 var_307;
        wp::float64 var_308;
        wp::float64 var_309;
        wp::float64 var_310;
        wp::vec_t<3, wp::float64>* var_311;
        wp::vec_t<3, wp::float64> var_312;
        wp::vec_t<3, wp::float64> var_313;
        wp::float64 var_314;
        wp::float64 var_315;
        wp::float64 var_316;
        wp::float64 var_317;
        wp::float64 var_318;
        wp::vec_t<3, wp::float64> var_319;
        wp::float64 var_320;
        wp::vec_t<3, wp::float64> var_321;
        wp::vec_t<3, wp::float64> var_322;
        wp::float64 var_323;
        wp::float64 var_324;
        wp::vec_t<3, wp::float64> var_325;
        wp::float64 var_326;
        bool var_327;
        wp::float64 var_328;
        wp::float64 var_329;
        wp::float64 var_330;
        wp::float64 var_331;
        wp::float64 var_332;
        wp::float64 var_333;
        wp::float64 var_334;
        wp::vec_t<3, wp::float64> var_335;
        wp::vec_t<3, wp::float64> var_336;
        wp::vec_t<3, wp::float64> var_337;
        wp::vec_t<3, wp::float64> var_338;
        wp::vec_t<3, wp::float64> var_339;
        const wp::int32 var_340 = 0;
        const wp::int32 var_341 = 0;
        wp::float64 var_342;
        wp::float64 var_343;
        wp::float64 var_344;
        const wp::int32 var_345 = 1;
        wp::float64 var_346;
        wp::float64 var_347;
        wp::float64 var_348;
        const wp::int32 var_349 = 2;
        wp::float64 var_350;
        wp::float64 var_351;
        wp::float64 var_352;
        const wp::int32 var_353 = 1;
        const wp::int32 var_354 = 0;
        wp::float64 var_355;
        wp::float64 var_356;
        wp::float64 var_357;
        const wp::int32 var_358 = 1;
        wp::float64 var_359;
        wp::float64 var_360;
        wp::float64 var_361;
        const wp::int32 var_362 = 2;
        wp::float64 var_363;
        wp::float64 var_364;
        wp::float64 var_365;
        const wp::int32 var_366 = 2;
        const wp::int32 var_367 = 0;
        wp::float64 var_368;
        wp::float64 var_369;
        wp::float64 var_370;
        const wp::int32 var_371 = 1;
        wp::float64 var_372;
        wp::float64 var_373;
        wp::float64 var_374;
        const wp::int32 var_375 = 2;
        wp::float64 var_376;
        wp::float64 var_377;
        wp::float64 var_378;
        wp::float64 var_379;
        wp::float64 var_380;
        wp::float64 var_381;
        wp::float64 var_382;
        wp::float64 var_383;
        wp::float64 var_384;
        wp::float64 var_385;
        wp::float64 var_386;
        wp::vec_t<3, wp::float64> var_387;
        wp::vec_t<3, wp::float64> var_388;
        wp::vec_t<3, wp::float64> var_389;
        const wp::int32 var_390 = 0;
        wp::vec_t<3, wp::float64> var_391;
        wp::vec_t<3, wp::float64> var_392;
        const wp::int32 var_393 = 1;
        wp::vec_t<3, wp::float64> var_394;
        wp::vec_t<3, wp::float64> var_395;
        const wp::int32 var_396 = 2;
        wp::vec_t<3, wp::float64> var_397;
        wp::vec_t<3, wp::float64> var_398;
        wp::float64 var_399;
        wp::float64 var_400;
        wp::float64 var_401;
        wp::vec_t<3, wp::float64> var_402;
        //---------
        // forward
        // def quadrature(mesh:wp.uint64,tri:wp.array2d(dtype=wp.vec3d),R:wp.mat33d,pose:wp.array(dtype=wp.vec3d),X:wp.array(dtype=wp.mat33d),V:wp.array(dtype=wp.mat33d),areas:wp.array(dtype=wp.float64),ncells:int,masters:wp.array(dtype=wp.mat33d),polygon:wp.array3d(dtype=wp.vec3d),polycounts:wp.array(dtype=int),sources:wp.array(dtype=int),active:wp.array(dtype=int),active_ids:wp.array(dtype=int),bad:wp.array(dtype=int),ff:wp.array2d(dtype=wp.vec3d),uu:wp.array(dtype=wp.float64),dd:wp.array(dtype=wp.float64),ww:wp.array(dtype=wp.float64),mm:wp.array(dtype=wp.vec3d)):       <L 61>
        // thread=wp.tid();nmaster=masters.shape[0];slot=thread//(8*nmaster);root=(thread//nmaster)%8;leaf=thread%nmaster       <L 62>
        var_0 = builtin_tid1d();
        var_1 = &(var_masters.shape);
        var_4 = wp::load(var_1);
        var_3 = wp::extract(var_4, var_2);
        var_6 = wp::mul(var_5, var_3);
        var_7 = wp::floordiv(var_0, var_6);
        var_8 = wp::floordiv(var_0, var_3);
        var_10 = wp::mod(var_8, var_9);
        var_11 = wp::mod(var_0, var_3);
        // if slot<active[0] and bad[0]==0:                                                       <L 63>
        var_14 = wp::address(var_active, var_13);
        var_16 = wp::load(var_14);
        var_15 = (var_7 < var_16);
        var_12 = var_15;
        if (var_12) {
            var_18 = wp::address(var_bad, var_17);
            var_21 = wp::load(var_18);
            var_20 = (var_21 == var_19);
            var_12 = var_12 && var_20;
        }
        if (var_12) {
            // pair=active_ids[slot];face=pair//ncells;n=polycounts[pair];src=sources[pair]       <L 64>
            var_22 = wp::address(var_active_ids, var_7);
            var_24 = wp::load(var_22);
            var_23 = wp::copy(var_24);
            var_25 = wp::floordiv(var_23, var_ncells);
            var_26 = wp::address(var_polycounts, var_23);
            var_28 = wp::load(var_26);
            var_27 = wp::copy(var_28);
            var_29 = wp::address(var_sources, var_23);
            var_31 = wp::load(var_29);
            var_30 = wp::copy(var_31);
            // if root<n-2:                                                                       <L 65>
            var_33 = wp::sub(var_27, var_32);
            var_34 = (var_10 < var_33);
            if (var_34) {
                // B=wp.matrix_from_rows(polygon[pair,src,0],polygon[pair,src,root+1],polygon[pair,src,root+2]);area=areas[face]*wp.abs(wp.determinant(B))/wp.float64(nmaster);B=masters[leaf]*B;x=X[face];v=V[face];T=pose[0];tv=pose[1];forces=wp.mat33d(wp.float64(0.));U=wp.float64(0.);D=wp.float64(0.);W=wp.float64(0.);M=wp.vec3d(wp.float64(0.))       <L 66>
                var_36 = wp::address(var_polygon, var_23, var_30, var_35);
                var_38 = wp::add(var_10, var_37);
                var_39 = wp::address(var_polygon, var_23, var_30, var_38);
                var_41 = wp::add(var_10, var_40);
                var_42 = wp::address(var_polygon, var_23, var_30, var_41);
                var_44 = wp::load(var_36);
                var_45 = wp::load(var_39);
                var_46 = wp::load(var_42);
                var_43 = wp::matrix_from_rows<wp::float64>(var_44, var_45, var_46);
                var_47 = wp::address(var_areas, var_25);
                var_48 = wp::determinant(var_43);
                var_49 = wp::abs(var_48);
                var_51 = wp::load(var_47);
                var_50 = wp::mul(var_51, var_49);
                var_52 = wp::float64(var_3);
                var_53 = wp::div(var_50, var_52);
                var_54 = wp::address(var_masters, var_11);
                var_56 = wp::load(var_54);
                var_55 = wp::mul(var_56, var_43);
                var_57 = wp::address(var_X, var_25);
                var_59 = wp::load(var_57);
                var_58 = wp::copy(var_59);
                var_60 = wp::address(var_V, var_25);
                var_62 = wp::load(var_60);
                var_61 = wp::copy(var_62);
                var_64 = wp::address(var_pose, var_63);
                var_66 = wp::load(var_64);
                var_65 = wp::copy(var_66);
                var_68 = wp::address(var_pose, var_67);
                var_70 = wp::load(var_68);
                var_69 = wp::copy(var_70);
                var_71 = 0.0;
                var_72 = wp::mat_t<3, 3, wp::float64>(var_71);
                var_73 = 0.0;
                var_74 = 0.0;
                var_75 = 0.0;
                var_76 = 0.0;
                var_77 = wp::vec_t<3, wp::float64>(var_76);
                // for k in range(3):                                                             <L 67>
                // rule=wp.vec3d(wp.float64(1./6.));rule[k]=wp.float64(2./3.);bary=wp.transpose(B)*rule;p=wp.transpose(x)*bary;vel=wp.transpose(v)*bary;s=signed(mesh,tri,wp.transpose(R)*(p-T));depth=wp.max(-s.phi,wp.float64(0.));normal=R*s.normal;fn=wp.float64(1e9)*area/wp.float64(3.)*depth;rel=vel-tv;tan=rel-wp.dot(rel,normal)*normal;speed=wp.length(tan);fr=wp.vec3d(wp.float64(0.))       <L 68>
                var_81 = wp::div(var_79, var_80);
                var_82 = wp::float64(var_81);
                var_83 = wp::vec_t<3, wp::float64>(var_82);
                var_86 = wp::div(var_84, var_85);
                var_87 = wp::float64(var_86);
                wp::assign_inplace(var_83, var_78, var_87);
                var_88 = wp::transpose(var_55);
                var_89 = wp::mul(var_88, var_83);
                var_90 = wp::transpose(var_58);
                var_91 = wp::mul(var_90, var_89);
                var_92 = wp::transpose(var_61);
                var_93 = wp::mul(var_92, var_89);
                var_94 = wp::transpose(var_R);
                var_95 = wp::sub(var_91, var_65);
                var_96 = wp::mul(var_94, var_95);
                var_97 = signed_0(var_mesh, var_tri, var_96);
                var_98 = &((var_97).phi);
                var_100 = wp::load(var_98);
                var_99 = wp::neg(var_100);
                var_101 = 0.0;
                var_102 = wp::max(var_99, var_101);
                var_103 = &((var_97).normal);
                var_105 = wp::load(var_103);
                var_104 = wp::mul(var_R, var_105);
                var_106 = 1000000000.0;
                var_107 = wp::mul(var_106, var_53);
                var_108 = 3.0;
                var_109 = wp::div(var_107, var_108);
                var_110 = wp::mul(var_109, var_102);
                var_111 = wp::sub(var_93, var_69);
                var_112 = wp::dot(var_111, var_104);
                var_113 = wp::mul(var_112, var_104);
                var_114 = wp::sub(var_111, var_113);
                var_115 = wp::length(var_114);
                var_116 = 0.0;
                var_117 = wp::vec_t<3, wp::float64>(var_116);
                // if speed>wp.float64(1e-30):fr=-wp.float64(.2)*fn*wp.tanh(speed/wp.float64(.001))*tan/speed       <L 69>
                var_118 = 1e-30;
                var_119 = (var_115 > var_118);
                if (var_119) {
                    var_120 = 0.2;
                    var_121 = wp::neg(var_120);
                    var_122 = wp::mul(var_121, var_110);
                    var_123 = 0.001;
                    var_124 = wp::div(var_115, var_123);
                    var_125 = wp::tanh(var_124);
                    var_126 = wp::mul(var_122, var_125);
                    var_127 = wp::mul(var_126, var_114);
                    var_128 = wp::div(var_127, var_115);
                }
                var_129 = wp::where(var_119, var_128, var_117);
                // f=fn*normal+fr                                                                 <L 70>
                var_130 = wp::mul(var_110, var_104);
                var_131 = wp::add(var_130, var_129);
                // for u in range(3):                                                             <L 71>
                // for a in range(3):forces[u,a]+=bary[u]*f[a]                                    <L 72>
                var_134 = wp::extract(var_89, var_132);
                var_135 = wp::extract(var_131, var_133);
                var_136 = wp::mul(var_134, var_135);
                wp::add_inplace(var_72, var_132, var_133, var_136);
                var_138 = wp::extract(var_89, var_132);
                var_139 = wp::extract(var_131, var_137);
                var_140 = wp::mul(var_138, var_139);
                wp::add_inplace(var_72, var_132, var_137, var_140);
                var_142 = wp::extract(var_89, var_132);
                var_143 = wp::extract(var_131, var_141);
                var_144 = wp::mul(var_142, var_143);
                wp::add_inplace(var_72, var_132, var_141, var_144);
                var_147 = wp::extract(var_89, var_145);
                var_148 = wp::extract(var_131, var_146);
                var_149 = wp::mul(var_147, var_148);
                wp::add_inplace(var_72, var_145, var_146, var_149);
                var_151 = wp::extract(var_89, var_145);
                var_152 = wp::extract(var_131, var_150);
                var_153 = wp::mul(var_151, var_152);
                wp::add_inplace(var_72, var_145, var_150, var_153);
                var_155 = wp::extract(var_89, var_145);
                var_156 = wp::extract(var_131, var_154);
                var_157 = wp::mul(var_155, var_156);
                wp::add_inplace(var_72, var_145, var_154, var_157);
                var_160 = wp::extract(var_89, var_158);
                var_161 = wp::extract(var_131, var_159);
                var_162 = wp::mul(var_160, var_161);
                wp::add_inplace(var_72, var_158, var_159, var_162);
                var_164 = wp::extract(var_89, var_158);
                var_165 = wp::extract(var_131, var_163);
                var_166 = wp::mul(var_164, var_165);
                wp::add_inplace(var_72, var_158, var_163, var_166);
                var_168 = wp::extract(var_89, var_158);
                var_169 = wp::extract(var_131, var_167);
                var_170 = wp::mul(var_168, var_169);
                wp::add_inplace(var_72, var_158, var_167, var_170);
                // U+=wp.float64(.5)*fn*depth;D-=wp.dot(fr,rel);W+=wp.dot(f,tv);M+=wp.cross(p-T,f)       <L 73>
                var_171 = 0.5;
                var_172 = wp::mul(var_171, var_110);
                var_173 = wp::mul(var_172, var_102);
                var_174 = wp::add(var_73, var_173);
                var_175 = wp::dot(var_129, var_111);
                var_176 = wp::sub(var_74, var_175);
                var_177 = wp::dot(var_131, var_69);
                var_178 = wp::add(var_75, var_177);
                var_179 = wp::sub(var_91, var_65);
                var_180 = wp::cross(var_179, var_131);
                var_181 = wp::add(var_77, var_180);
                // rule=wp.vec3d(wp.float64(1./6.));rule[k]=wp.float64(2./3.);bary=wp.transpose(B)*rule;p=wp.transpose(x)*bary;vel=wp.transpose(v)*bary;s=signed(mesh,tri,wp.transpose(R)*(p-T));depth=wp.max(-s.phi,wp.float64(0.));normal=R*s.normal;fn=wp.float64(1e9)*area/wp.float64(3.)*depth;rel=vel-tv;tan=rel-wp.dot(rel,normal)*normal;speed=wp.length(tan);fr=wp.vec3d(wp.float64(0.))       <L 68>
                var_185 = wp::div(var_183, var_184);
                var_186 = wp::float64(var_185);
                var_187 = wp::vec_t<3, wp::float64>(var_186);
                var_190 = wp::div(var_188, var_189);
                var_191 = wp::float64(var_190);
                wp::assign_inplace(var_187, var_182, var_191);
                var_192 = wp::transpose(var_55);
                var_193 = wp::mul(var_192, var_187);
                var_194 = wp::transpose(var_58);
                var_195 = wp::mul(var_194, var_193);
                var_196 = wp::transpose(var_61);
                var_197 = wp::mul(var_196, var_193);
                var_198 = wp::transpose(var_R);
                var_199 = wp::sub(var_195, var_65);
                var_200 = wp::mul(var_198, var_199);
                var_201 = signed_0(var_mesh, var_tri, var_200);
                var_202 = &((var_201).phi);
                var_204 = wp::load(var_202);
                var_203 = wp::neg(var_204);
                var_205 = 0.0;
                var_206 = wp::max(var_203, var_205);
                var_207 = &((var_201).normal);
                var_209 = wp::load(var_207);
                var_208 = wp::mul(var_R, var_209);
                var_210 = 1000000000.0;
                var_211 = wp::mul(var_210, var_53);
                var_212 = 3.0;
                var_213 = wp::div(var_211, var_212);
                var_214 = wp::mul(var_213, var_206);
                var_215 = wp::sub(var_197, var_69);
                var_216 = wp::dot(var_215, var_208);
                var_217 = wp::mul(var_216, var_208);
                var_218 = wp::sub(var_215, var_217);
                var_219 = wp::length(var_218);
                var_220 = 0.0;
                var_221 = wp::vec_t<3, wp::float64>(var_220);
                // if speed>wp.float64(1e-30):fr=-wp.float64(.2)*fn*wp.tanh(speed/wp.float64(.001))*tan/speed       <L 69>
                var_222 = 1e-30;
                var_223 = (var_219 > var_222);
                if (var_223) {
                    var_224 = 0.2;
                    var_225 = wp::neg(var_224);
                    var_226 = wp::mul(var_225, var_214);
                    var_227 = 0.001;
                    var_228 = wp::div(var_219, var_227);
                    var_229 = wp::tanh(var_228);
                    var_230 = wp::mul(var_226, var_229);
                    var_231 = wp::mul(var_230, var_218);
                    var_232 = wp::div(var_231, var_219);
                }
                var_233 = wp::where(var_223, var_232, var_221);
                // f=fn*normal+fr                                                                 <L 70>
                var_234 = wp::mul(var_214, var_208);
                var_235 = wp::add(var_234, var_233);
                // for u in range(3):                                                             <L 71>
                // for a in range(3):forces[u,a]+=bary[u]*f[a]                                    <L 72>
                var_238 = wp::extract(var_193, var_236);
                var_239 = wp::extract(var_235, var_237);
                var_240 = wp::mul(var_238, var_239);
                wp::add_inplace(var_72, var_236, var_237, var_240);
                var_242 = wp::extract(var_193, var_236);
                var_243 = wp::extract(var_235, var_241);
                var_244 = wp::mul(var_242, var_243);
                wp::add_inplace(var_72, var_236, var_241, var_244);
                var_246 = wp::extract(var_193, var_236);
                var_247 = wp::extract(var_235, var_245);
                var_248 = wp::mul(var_246, var_247);
                wp::add_inplace(var_72, var_236, var_245, var_248);
                var_251 = wp::extract(var_193, var_249);
                var_252 = wp::extract(var_235, var_250);
                var_253 = wp::mul(var_251, var_252);
                wp::add_inplace(var_72, var_249, var_250, var_253);
                var_255 = wp::extract(var_193, var_249);
                var_256 = wp::extract(var_235, var_254);
                var_257 = wp::mul(var_255, var_256);
                wp::add_inplace(var_72, var_249, var_254, var_257);
                var_259 = wp::extract(var_193, var_249);
                var_260 = wp::extract(var_235, var_258);
                var_261 = wp::mul(var_259, var_260);
                wp::add_inplace(var_72, var_249, var_258, var_261);
                var_264 = wp::extract(var_193, var_262);
                var_265 = wp::extract(var_235, var_263);
                var_266 = wp::mul(var_264, var_265);
                wp::add_inplace(var_72, var_262, var_263, var_266);
                var_268 = wp::extract(var_193, var_262);
                var_269 = wp::extract(var_235, var_267);
                var_270 = wp::mul(var_268, var_269);
                wp::add_inplace(var_72, var_262, var_267, var_270);
                var_272 = wp::extract(var_193, var_262);
                var_273 = wp::extract(var_235, var_271);
                var_274 = wp::mul(var_272, var_273);
                wp::add_inplace(var_72, var_262, var_271, var_274);
                // U+=wp.float64(.5)*fn*depth;D-=wp.dot(fr,rel);W+=wp.dot(f,tv);M+=wp.cross(p-T,f)       <L 73>
                var_275 = 0.5;
                var_276 = wp::mul(var_275, var_214);
                var_277 = wp::mul(var_276, var_206);
                var_278 = wp::add(var_174, var_277);
                var_279 = wp::dot(var_233, var_215);
                var_280 = wp::sub(var_176, var_279);
                var_281 = wp::dot(var_235, var_69);
                var_282 = wp::add(var_178, var_281);
                var_283 = wp::sub(var_195, var_65);
                var_284 = wp::cross(var_283, var_235);
                var_285 = wp::add(var_181, var_284);
                // rule=wp.vec3d(wp.float64(1./6.));rule[k]=wp.float64(2./3.);bary=wp.transpose(B)*rule;p=wp.transpose(x)*bary;vel=wp.transpose(v)*bary;s=signed(mesh,tri,wp.transpose(R)*(p-T));depth=wp.max(-s.phi,wp.float64(0.));normal=R*s.normal;fn=wp.float64(1e9)*area/wp.float64(3.)*depth;rel=vel-tv;tan=rel-wp.dot(rel,normal)*normal;speed=wp.length(tan);fr=wp.vec3d(wp.float64(0.))       <L 68>
                var_289 = wp::div(var_287, var_288);
                var_290 = wp::float64(var_289);
                var_291 = wp::vec_t<3, wp::float64>(var_290);
                var_294 = wp::div(var_292, var_293);
                var_295 = wp::float64(var_294);
                wp::assign_inplace(var_291, var_286, var_295);
                var_296 = wp::transpose(var_55);
                var_297 = wp::mul(var_296, var_291);
                var_298 = wp::transpose(var_58);
                var_299 = wp::mul(var_298, var_297);
                var_300 = wp::transpose(var_61);
                var_301 = wp::mul(var_300, var_297);
                var_302 = wp::transpose(var_R);
                var_303 = wp::sub(var_299, var_65);
                var_304 = wp::mul(var_302, var_303);
                var_305 = signed_0(var_mesh, var_tri, var_304);
                var_306 = &((var_305).phi);
                var_308 = wp::load(var_306);
                var_307 = wp::neg(var_308);
                var_309 = 0.0;
                var_310 = wp::max(var_307, var_309);
                var_311 = &((var_305).normal);
                var_313 = wp::load(var_311);
                var_312 = wp::mul(var_R, var_313);
                var_314 = 1000000000.0;
                var_315 = wp::mul(var_314, var_53);
                var_316 = 3.0;
                var_317 = wp::div(var_315, var_316);
                var_318 = wp::mul(var_317, var_310);
                var_319 = wp::sub(var_301, var_69);
                var_320 = wp::dot(var_319, var_312);
                var_321 = wp::mul(var_320, var_312);
                var_322 = wp::sub(var_319, var_321);
                var_323 = wp::length(var_322);
                var_324 = 0.0;
                var_325 = wp::vec_t<3, wp::float64>(var_324);
                // if speed>wp.float64(1e-30):fr=-wp.float64(.2)*fn*wp.tanh(speed/wp.float64(.001))*tan/speed       <L 69>
                var_326 = 1e-30;
                var_327 = (var_323 > var_326);
                if (var_327) {
                    var_328 = 0.2;
                    var_329 = wp::neg(var_328);
                    var_330 = wp::mul(var_329, var_318);
                    var_331 = 0.001;
                    var_332 = wp::div(var_323, var_331);
                    var_333 = wp::tanh(var_332);
                    var_334 = wp::mul(var_330, var_333);
                    var_335 = wp::mul(var_334, var_322);
                    var_336 = wp::div(var_335, var_323);
                }
                var_337 = wp::where(var_327, var_336, var_325);
                // f=fn*normal+fr                                                                 <L 70>
                var_338 = wp::mul(var_318, var_312);
                var_339 = wp::add(var_338, var_337);
                // for u in range(3):                                                             <L 71>
                // for a in range(3):forces[u,a]+=bary[u]*f[a]                                    <L 72>
                var_342 = wp::extract(var_297, var_340);
                var_343 = wp::extract(var_339, var_341);
                var_344 = wp::mul(var_342, var_343);
                wp::add_inplace(var_72, var_340, var_341, var_344);
                var_346 = wp::extract(var_297, var_340);
                var_347 = wp::extract(var_339, var_345);
                var_348 = wp::mul(var_346, var_347);
                wp::add_inplace(var_72, var_340, var_345, var_348);
                var_350 = wp::extract(var_297, var_340);
                var_351 = wp::extract(var_339, var_349);
                var_352 = wp::mul(var_350, var_351);
                wp::add_inplace(var_72, var_340, var_349, var_352);
                var_355 = wp::extract(var_297, var_353);
                var_356 = wp::extract(var_339, var_354);
                var_357 = wp::mul(var_355, var_356);
                wp::add_inplace(var_72, var_353, var_354, var_357);
                var_359 = wp::extract(var_297, var_353);
                var_360 = wp::extract(var_339, var_358);
                var_361 = wp::mul(var_359, var_360);
                wp::add_inplace(var_72, var_353, var_358, var_361);
                var_363 = wp::extract(var_297, var_353);
                var_364 = wp::extract(var_339, var_362);
                var_365 = wp::mul(var_363, var_364);
                wp::add_inplace(var_72, var_353, var_362, var_365);
                var_368 = wp::extract(var_297, var_366);
                var_369 = wp::extract(var_339, var_367);
                var_370 = wp::mul(var_368, var_369);
                wp::add_inplace(var_72, var_366, var_367, var_370);
                var_372 = wp::extract(var_297, var_366);
                var_373 = wp::extract(var_339, var_371);
                var_374 = wp::mul(var_372, var_373);
                wp::add_inplace(var_72, var_366, var_371, var_374);
                var_376 = wp::extract(var_297, var_366);
                var_377 = wp::extract(var_339, var_375);
                var_378 = wp::mul(var_376, var_377);
                wp::add_inplace(var_72, var_366, var_375, var_378);
                // U+=wp.float64(.5)*fn*depth;D-=wp.dot(fr,rel);W+=wp.dot(f,tv);M+=wp.cross(p-T,f)       <L 73>
                var_379 = 0.5;
                var_380 = wp::mul(var_379, var_318);
                var_381 = wp::mul(var_380, var_310);
                var_382 = wp::add(var_278, var_381);
                var_383 = wp::dot(var_337, var_319);
                var_384 = wp::sub(var_280, var_383);
                var_385 = wp::dot(var_339, var_69);
                var_386 = wp::add(var_282, var_385);
                var_387 = wp::sub(var_299, var_65);
                var_388 = wp::cross(var_387, var_339);
                var_389 = wp::add(var_285, var_388);
                // for u in range(3):wp.atomic_add(ff,face,u,forces[u])                           <L 74>
                var_391 = wp::extract(var_72, var_390);
                var_392 = wp::atomic_add(var_ff, var_25, var_390, var_391);
                var_394 = wp::extract(var_72, var_393);
                var_395 = wp::atomic_add(var_ff, var_25, var_393, var_394);
                var_397 = wp::extract(var_72, var_396);
                var_398 = wp::atomic_add(var_ff, var_25, var_396, var_397);
                // wp.atomic_add(uu,face,U);wp.atomic_add(dd,face,D);wp.atomic_add(ww,face,W);wp.atomic_add(mm,face,M)       <L 75>
                var_399 = wp::atomic_add(var_uu, var_25, var_382);
                var_400 = wp::atomic_add(var_dd, var_25, var_384);
                var_401 = wp::atomic_add(var_ww, var_25, var_386);
                var_402 = wp::atomic_add(var_mm, var_25, var_389);
            }
        }
    }
}



extern "C" __global__ void domains_cafd0a4c_cuda_kernel_forward(
    wp::launch_bounds_t<1> dim,
    wp::array_t<wp::mat_t<3, 3, wp::float64>> var_local,
    wp::array_t<wp::vec_t<4, wp::float64>> var_planes,
    wp::array_t<wp::vec_t<3, wp::float64>> var_bounds,
    wp::int32 var_ncells,
    wp::array_t<wp::vec_t<3, wp::float64>> var_polygon,
    wp::array_t<wp::int32> var_polycounts,
    wp::array_t<wp::int32> var_sources,
    wp::array_t<wp::int32> var_active,
    wp::array_t<wp::int32> var_active_ids,
    wp::int32 var_capacity,
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
        wp::int32 var_1;
        wp::int32 var_2;
        wp::mat_t<3, 3, wp::float64>* var_3;
        wp::mat_t<3, 3, wp::float64> var_4;
        wp::mat_t<3, 3, wp::float64> var_5;
        const bool var_6 = true;
        const wp::int32 var_7 = 0;
        const wp::int32 var_8 = 0;
        const wp::int32 var_9 = 0;
        wp::float64 var_10;
        const wp::int32 var_11 = 1;
        wp::float64 var_12;
        const wp::int32 var_13 = 2;
        wp::float64 var_14;
        wp::float64 var_15;
        wp::float64 var_16;
        const wp::int32 var_17 = 0;
        wp::float64 var_18;
        const wp::int32 var_19 = 1;
        wp::float64 var_20;
        const wp::int32 var_21 = 2;
        wp::float64 var_22;
        wp::float64 var_23;
        wp::float64 var_24;
        bool var_25;
        const wp::int32 var_26 = 0;
        wp::vec_t<3, wp::float64>* var_27;
        wp::float64 var_28;
        wp::vec_t<3, wp::float64> var_29;
        bool var_30;
        const wp::int32 var_31 = 1;
        wp::vec_t<3, wp::float64>* var_32;
        wp::float64 var_33;
        wp::vec_t<3, wp::float64> var_34;
        bool var_35;
        const bool var_36 = false;
        bool var_37;
        const wp::int32 var_38 = 1;
        const wp::int32 var_39 = 0;
        wp::float64 var_40;
        const wp::int32 var_41 = 1;
        wp::float64 var_42;
        const wp::int32 var_43 = 2;
        wp::float64 var_44;
        wp::float64 var_45;
        wp::float64 var_46;
        const wp::int32 var_47 = 0;
        wp::float64 var_48;
        const wp::int32 var_49 = 1;
        wp::float64 var_50;
        const wp::int32 var_51 = 2;
        wp::float64 var_52;
        wp::float64 var_53;
        wp::float64 var_54;
        bool var_55;
        const wp::int32 var_56 = 0;
        wp::vec_t<3, wp::float64>* var_57;
        wp::float64 var_58;
        wp::vec_t<3, wp::float64> var_59;
        bool var_60;
        const wp::int32 var_61 = 1;
        wp::vec_t<3, wp::float64>* var_62;
        wp::float64 var_63;
        wp::vec_t<3, wp::float64> var_64;
        bool var_65;
        const bool var_66 = false;
        bool var_67;
        const wp::int32 var_68 = 2;
        const wp::int32 var_69 = 0;
        wp::float64 var_70;
        const wp::int32 var_71 = 1;
        wp::float64 var_72;
        const wp::int32 var_73 = 2;
        wp::float64 var_74;
        wp::float64 var_75;
        wp::float64 var_76;
        const wp::int32 var_77 = 0;
        wp::float64 var_78;
        const wp::int32 var_79 = 1;
        wp::float64 var_80;
        const wp::int32 var_81 = 2;
        wp::float64 var_82;
        wp::float64 var_83;
        wp::float64 var_84;
        bool var_85;
        const wp::int32 var_86 = 0;
        wp::vec_t<3, wp::float64>* var_87;
        wp::float64 var_88;
        wp::vec_t<3, wp::float64> var_89;
        bool var_90;
        const wp::int32 var_91 = 1;
        wp::vec_t<3, wp::float64>* var_92;
        wp::float64 var_93;
        wp::vec_t<3, wp::float64> var_94;
        bool var_95;
        const bool var_96 = false;
        bool var_97;
        bool var_98;
        const wp::int32 var_99 = 0;
        wp::int32* var_100;
        const wp::int32 var_101 = 0;
        bool var_102;
        wp::int32 var_103;
        const wp::int32 var_104 = 0;
        wp::float64 var_105;
        wp::vec_t<3, wp::float64> var_106;
        wp::float64 var_107;
        const wp::int32 var_108 = 0;
        const wp::int32 var_109 = 1;
        wp::float64 var_110;
        wp::vec_t<3, wp::float64> var_111;
        wp::float64 var_112;
        const wp::int32 var_113 = 0;
        const wp::int32 var_114 = 2;
        wp::float64 var_115;
        wp::vec_t<3, wp::float64> var_116;
        wp::float64 var_117;
        const wp::int32 var_118 = 0;
        const wp::int32 var_119 = 3;
        wp::int32 var_120;
        const wp::int32 var_121 = 0;
        wp::int32 var_122;
        const wp::int32 var_123 = 1;
        wp::int32 var_124;
        const wp::int32 var_125 = 4;
        wp::range_t var_126;
        wp::int32 var_127;
        wp::int32 var_128;
        wp::vec_t<4, wp::float64>* var_129;
        wp::vec_t<4, wp::float64> var_130;
        wp::vec_t<4, wp::float64> var_131;
        const wp::int32 var_132 = 0;
        wp::float64 var_133;
        const wp::int32 var_134 = 1;
        wp::float64 var_135;
        const wp::int32 var_136 = 2;
        wp::float64 var_137;
        wp::vec_t<3, wp::float64> var_138;
        wp::vec_t<3, wp::float64> var_139;
        const wp::int32 var_140 = 3;
        wp::float64 var_141;
        wp::vec_t<3, wp::float64> var_142;
        wp::vec_t<3, wp::float64> var_143;
        const wp::int32 var_144 = 0;
        wp::int32 var_145;
        wp::range_t var_146;
        wp::int32 var_147;
        wp::vec_t<3, wp::float64>* var_148;
        wp::vec_t<3, wp::float64> var_149;
        wp::vec_t<3, wp::float64> var_150;
        const wp::int32 var_151 = 1;
        wp::int32 var_152;
        wp::int32 var_153;
        wp::vec_t<3, wp::float64>* var_154;
        wp::vec_t<3, wp::float64> var_155;
        wp::vec_t<3, wp::float64> var_156;
        wp::float64 var_157;
        wp::float64 var_158;
        wp::float64 var_159;
        bool var_160;
        const wp::int32 var_161 = 10;
        bool var_162;
        const wp::int32 var_163 = 0;
        const wp::int32 var_164 = 6;
        wp::int32 var_165;
        const wp::int32 var_166 = 1;
        wp::int32 var_167;
        wp::int32 var_168;
        wp::int32 var_169;
        bool var_170;
        bool var_171;
        wp::float64 var_172;
        bool var_173;
        wp::float64 var_174;
        bool var_175;
        bool var_176;
        wp::float64 var_177;
        bool var_178;
        wp::float64 var_179;
        bool var_180;
        const wp::int32 var_181 = 10;
        bool var_182;
        const wp::int32 var_183 = 0;
        const wp::int32 var_184 = 6;
        wp::int32 var_185;
        wp::float64 var_186;
        wp::float64 var_187;
        wp::vec_t<3, wp::float64> var_188;
        wp::vec_t<3, wp::float64> var_189;
        wp::vec_t<3, wp::float64> var_190;
        const wp::int32 var_191 = 1;
        wp::int32 var_192;
        wp::int32 var_193;
        wp::int32 var_194;
        wp::int32 var_195;
        wp::int32 var_196;
        wp::int32 var_197;
        wp::int32 var_198;
        const wp::int32 var_199 = 3;
        bool var_200;
        wp::int32 var_201;
        wp::int32 var_202;
        wp::int32 var_203;
        wp::int32 var_204;
        bool var_205;
        const wp::int32 var_206 = 3;
        bool var_207;
        const wp::int32 var_208 = 0;
        wp::int32* var_209;
        const wp::int32 var_210 = 0;
        bool var_211;
        wp::int32 var_212;
        wp::float64 var_213;
        const wp::int32 var_214 = 1;
        wp::int32 var_215;
        const wp::int32 var_216 = 1;
        wp::range_t var_217;
        wp::int32 var_218;
        const wp::int32 var_219 = 0;
        wp::vec_t<3, wp::float64>* var_220;
        wp::vec_t<3, wp::float64>* var_221;
        const wp::int32 var_222 = 1;
        wp::int32 var_223;
        wp::vec_t<3, wp::float64>* var_224;
        wp::mat_t<3, 3, wp::float64> var_225;
        wp::vec_t<3, wp::float64> var_226;
        wp::vec_t<3, wp::float64> var_227;
        wp::vec_t<3, wp::float64> var_228;
        wp::float64 var_229;
        wp::float64 var_230;
        wp::float64 var_231;
        wp::float64 var_232;
        bool var_233;
        const wp::int32 var_234 = 0;
        const wp::int32 var_235 = 1;
        wp::int32 var_236;
        bool var_237;
        const wp::int32 var_238 = 0;
        const wp::int32 var_239 = 5;
        wp::int32 var_240;
        wp::int32 var_241;
        //---------
        // forward
        // def domains(local:wp.array(dtype=wp.mat33d),planes:wp.array2d(dtype=wp.vec4d),bounds:wp.array2d(dtype=wp.vec3d),ncells:int,polygon:wp.array3d(dtype=wp.vec3d),polycounts:wp.array(dtype=int),sources:wp.array(dtype=int),active:wp.array(dtype=int),active_ids:wp.array(dtype=int),capacity:int,bad:wp.array(dtype=int)):       <L 32>
        // pair=wp.tid();face=pair//ncells;cell=pair%ncells;x=local[face];inside=True;polycounts[pair]=0       <L 33>
        var_0 = builtin_tid1d();
        var_1 = wp::floordiv(var_0, var_ncells);
        var_2 = wp::mod(var_0, var_ncells);
        var_3 = wp::address(var_local, var_1);
        var_5 = wp::load(var_3);
        var_4 = wp::copy(var_5);
        wp::array_store(var_polycounts, var_0, var_7);
        // for axis in range(3):                                                                  <L 34>
        // lo=wp.min(x[0,axis],wp.min(x[1,axis],x[2,axis]));hi=wp.max(x[0,axis],wp.max(x[1,axis],x[2,axis]))       <L 35>
        var_10 = wp::extract(var_4, var_9, var_8);
        var_12 = wp::extract(var_4, var_11, var_8);
        var_14 = wp::extract(var_4, var_13, var_8);
        var_15 = wp::min(var_12, var_14);
        var_16 = wp::min(var_10, var_15);
        var_18 = wp::extract(var_4, var_17, var_8);
        var_20 = wp::extract(var_4, var_19, var_8);
        var_22 = wp::extract(var_4, var_21, var_8);
        var_23 = wp::max(var_20, var_22);
        var_24 = wp::max(var_18, var_23);
        // if hi<bounds[cell,0][axis] or lo>bounds[cell,1][axis]:inside=False                     <L 36>
        var_27 = wp::address(var_bounds, var_2, var_26);
        var_29 = wp::load(var_27);
        var_28 = wp::extract(var_29, var_8);
        var_30 = (var_24 < var_28);
        var_25 = var_30;
        if (!var_25) {
            var_32 = wp::address(var_bounds, var_2, var_31);
            var_34 = wp::load(var_32);
            var_33 = wp::extract(var_34, var_8);
            var_35 = (var_16 > var_33);
            var_25 = var_25 || var_35;
        }
        if (var_25) {
        }
        var_37 = wp::where(var_25, var_36, var_6);
        // lo=wp.min(x[0,axis],wp.min(x[1,axis],x[2,axis]));hi=wp.max(x[0,axis],wp.max(x[1,axis],x[2,axis]))       <L 35>
        var_40 = wp::extract(var_4, var_39, var_38);
        var_42 = wp::extract(var_4, var_41, var_38);
        var_44 = wp::extract(var_4, var_43, var_38);
        var_45 = wp::min(var_42, var_44);
        var_46 = wp::min(var_40, var_45);
        var_48 = wp::extract(var_4, var_47, var_38);
        var_50 = wp::extract(var_4, var_49, var_38);
        var_52 = wp::extract(var_4, var_51, var_38);
        var_53 = wp::max(var_50, var_52);
        var_54 = wp::max(var_48, var_53);
        // if hi<bounds[cell,0][axis] or lo>bounds[cell,1][axis]:inside=False                     <L 36>
        var_57 = wp::address(var_bounds, var_2, var_56);
        var_59 = wp::load(var_57);
        var_58 = wp::extract(var_59, var_38);
        var_60 = (var_54 < var_58);
        var_55 = var_60;
        if (!var_55) {
            var_62 = wp::address(var_bounds, var_2, var_61);
            var_64 = wp::load(var_62);
            var_63 = wp::extract(var_64, var_38);
            var_65 = (var_46 > var_63);
            var_55 = var_55 || var_65;
        }
        if (var_55) {
        }
        var_67 = wp::where(var_55, var_66, var_37);
        // lo=wp.min(x[0,axis],wp.min(x[1,axis],x[2,axis]));hi=wp.max(x[0,axis],wp.max(x[1,axis],x[2,axis]))       <L 35>
        var_70 = wp::extract(var_4, var_69, var_68);
        var_72 = wp::extract(var_4, var_71, var_68);
        var_74 = wp::extract(var_4, var_73, var_68);
        var_75 = wp::min(var_72, var_74);
        var_76 = wp::min(var_70, var_75);
        var_78 = wp::extract(var_4, var_77, var_68);
        var_80 = wp::extract(var_4, var_79, var_68);
        var_82 = wp::extract(var_4, var_81, var_68);
        var_83 = wp::max(var_80, var_82);
        var_84 = wp::max(var_78, var_83);
        // if hi<bounds[cell,0][axis] or lo>bounds[cell,1][axis]:inside=False                     <L 36>
        var_87 = wp::address(var_bounds, var_2, var_86);
        var_89 = wp::load(var_87);
        var_88 = wp::extract(var_89, var_68);
        var_90 = (var_84 < var_88);
        var_85 = var_90;
        if (!var_85) {
            var_92 = wp::address(var_bounds, var_2, var_91);
            var_94 = wp::load(var_92);
            var_93 = wp::extract(var_94, var_68);
            var_95 = (var_76 > var_93);
            var_85 = var_85 || var_95;
        }
        if (var_85) {
        }
        var_97 = wp::where(var_85, var_96, var_67);
        // if inside and bad[0]==0:                                                               <L 37>
        var_98 = var_97;
        if (var_98) {
            var_100 = wp::address(var_bad, var_99);
            var_103 = wp::load(var_100);
            var_102 = (var_103 == var_101);
            var_98 = var_98 && var_102;
        }
        if (var_98) {
            // for k in range(3):unit=wp.vec3d(wp.float64(0.));unit[k]=wp.float64(1.);polygon[pair,0,k]=unit       <L 38>
            var_105 = 0.0;
            var_106 = wp::vec_t<3, wp::float64>(var_105);
            var_107 = 1.0;
            wp::assign_inplace(var_106, var_104, var_107);
            wp::array_store(var_polygon, var_0, var_108, var_104, var_106);
            var_110 = 0.0;
            var_111 = wp::vec_t<3, wp::float64>(var_110);
            var_112 = 1.0;
            wp::assign_inplace(var_111, var_109, var_112);
            wp::array_store(var_polygon, var_0, var_113, var_109, var_111);
            var_115 = 0.0;
            var_116 = wp::vec_t<3, wp::float64>(var_115);
            var_117 = 1.0;
            wp::assign_inplace(var_116, var_114, var_117);
            wp::array_store(var_polygon, var_0, var_118, var_114, var_116);
            // n=int(3);src=int(0);dst=int(1)                                                     <L 39>
            var_120 = wp::int(var_119);
            var_122 = wp::int(var_121);
            var_124 = wp::int(var_123);
            // for h in range(4):                                                                 <L 40>
            var_126 = wp::range(var_125);
            var_127 = wp::copy(var_114);
            start_for_0:;
                if (iter_cmp(var_126) == 0) goto end_for_0;
                var_128 = wp::iter_next(var_126);
                // plane=planes[cell,h];normal=wp.vec3d(plane[0],plane[1],plane[2]);distance=x*normal+wp.vec3d(plane[3]);new=int(0)       <L 41>
                var_129 = wp::address(var_planes, var_2, var_128);
                var_131 = wp::load(var_129);
                var_130 = wp::copy(var_131);
                var_133 = wp::extract(var_130, var_132);
                var_135 = wp::extract(var_130, var_134);
                var_137 = wp::extract(var_130, var_136);
                var_138 = wp::vec_t<3, wp::float64>(var_133, var_135, var_137);
                var_139 = wp::mul(var_4, var_138);
                var_141 = wp::extract(var_130, var_140);
                var_142 = wp::vec_t<3, wp::float64>(var_141);
                var_143 = wp::add(var_139, var_142);
                var_145 = wp::int(var_144);
                // for k in range(n):                                                             <L 42>
                var_146 = wp::range(var_120);
                start_for_2:;
                    if (iter_cmp(var_146) == 0) goto end_for_2;
                    var_147 = wp::iter_next(var_146);
                    // p0=polygon[pair,src,k];p1=polygon[pair,src,(k+1)%n];d0=wp.dot(p0,distance);d1=wp.dot(p1,distance)       <L 43>
                    var_148 = wp::address(var_polygon, var_0, var_122, var_147);
                    var_150 = wp::load(var_148);
                    var_149 = wp::copy(var_150);
                    var_152 = wp::add(var_147, var_151);
                    var_153 = wp::mod(var_152, var_120);
                    var_154 = wp::address(var_polygon, var_0, var_122, var_153);
                    var_156 = wp::load(var_154);
                    var_155 = wp::copy(var_156);
                    var_157 = wp::dot(var_149, var_143);
                    var_158 = wp::dot(var_155, var_143);
                    // if d0<=wp.float64(0.):                                                     <L 44>
                    var_159 = 0.0;
                    var_160 = (var_157 <= var_159);
                    if (var_160) {
                        // if new>=10:wp.atomic_max(bad,0,6)                                      <L 45>
                        var_162 = (var_145 >= var_161);
                        if (var_162) {
                            var_165 = wp::atomic_max(var_bad, var_163, var_164);
                        }
                        if (!var_162) {
                            // else:polygon[pair,dst,new]=p0;new+=1                               <L 46>
                            wp::array_store(var_polygon, var_0, var_124, var_145, var_149);
                            var_167 = wp::add(var_145, var_166);
                        }
                        var_168 = wp::where(var_162, var_145, var_167);
                    }
                    var_169 = wp::where(var_160, var_168, var_145);
                    // if (d0<wp.float64(0.) and d1>wp.float64(0.)) or (d1<wp.float64(0.) and d0>wp.float64(0.)):       <L 47>
                    var_172 = 0.0;
                    var_173 = (var_157 < var_172);
                    var_171 = var_173;
                    if (var_171) {
                        var_174 = 0.0;
                        var_175 = (var_158 > var_174);
                        var_171 = var_171 && var_175;
                    }
                    var_170 = var_171;
                    if (!var_170) {
                        var_177 = 0.0;
                        var_178 = (var_158 < var_177);
                        var_176 = var_178;
                        if (var_176) {
                            var_179 = 0.0;
                            var_180 = (var_157 > var_179);
                            var_176 = var_176 && var_180;
                        }
                        var_170 = var_170 || var_176;
                    }
                    if (var_170) {
                        // if new>=10:wp.atomic_max(bad,0,6)                                      <L 48>
                        var_182 = (var_169 >= var_181);
                        if (var_182) {
                            var_185 = wp::atomic_max(var_bad, var_183, var_184);
                        }
                        if (!var_182) {
                            // else:polygon[pair,dst,new]=p0+d0/(d0-d1)*(p1-p0);new+=1            <L 49>
                            var_186 = wp::sub(var_157, var_158);
                            var_187 = wp::div(var_157, var_186);
                            var_188 = wp::sub(var_155, var_149);
                            var_189 = wp::mul(var_187, var_188);
                            var_190 = wp::add(var_149, var_189);
                            wp::array_store(var_polygon, var_0, var_124, var_169, var_190);
                            var_192 = wp::add(var_169, var_191);
                        }
                        var_193 = wp::where(var_182, var_169, var_192);
                    }
                    var_194 = wp::where(var_170, var_193, var_169);
                    wp::assign(var_145, var_194);
                    goto start_for_2;
                end_for_2:;
                // n=new;tmp=src;src=dst;dst=tmp                                                  <L 50>
                var_195 = wp::copy(var_145);
                var_196 = wp::copy(var_122);
                var_197 = wp::copy(var_124);
                var_198 = wp::copy(var_196);
                // if n<3:break                                                                   <L 51>
                var_200 = (var_195 < var_199);
                if (var_200) {
                    wp::assign(var_127, var_147);
                    wp::assign(var_120, var_195);
                    wp::assign(var_122, var_197);
                    wp::assign(var_124, var_198);
                    goto end_for_0;
                }
                var_201 = wp::where(var_200, var_127, var_147);
                var_202 = wp::where(var_200, var_120, var_195);
                var_203 = wp::where(var_200, var_122, var_197);
                var_204 = wp::where(var_200, var_124, var_198);
                wp::assign(var_127, var_201);
                wp::assign(var_120, var_202);
                wp::assign(var_122, var_203);
                wp::assign(var_124, var_204);
                goto start_for_0;
            end_for_0:;
            // if n>=3 and bad[0]==0:                                                             <L 52>
            var_207 = (var_120 >= var_206);
            var_205 = var_207;
            if (var_205) {
                var_209 = wp::address(var_bad, var_208);
                var_212 = wp::load(var_209);
                var_211 = (var_212 == var_210);
                var_205 = var_205 && var_211;
            }
            if (var_205) {
                // area=wp.float64(0.)                                                            <L 53>
                var_213 = 0.0;
                // for k in range(1,n-1):area+=wp.abs(wp.determinant(wp.matrix_from_rows(polygon[pair,src,0],polygon[pair,src,k],polygon[pair,src,k+1])))       <L 54>
                var_215 = wp::sub(var_120, var_214);
                var_217 = wp::range(var_216, var_215);
                start_for_4:;
                    if (iter_cmp(var_217) == 0) goto end_for_4;
                    var_218 = wp::iter_next(var_217);
                    var_220 = wp::address(var_polygon, var_0, var_122, var_219);
                    var_221 = wp::address(var_polygon, var_0, var_122, var_218);
                    var_223 = wp::add(var_218, var_222);
                    var_224 = wp::address(var_polygon, var_0, var_122, var_223);
                    var_226 = wp::load(var_220);
                    var_227 = wp::load(var_221);
                    var_228 = wp::load(var_224);
                    var_225 = wp::matrix_from_rows<wp::float64>(var_226, var_227, var_228);
                    var_229 = wp::determinant(var_225);
                    var_230 = wp::abs(var_229);
                    var_231 = wp::add(var_213, var_230);
                    wp::assign(var_213, var_231);
                    goto start_for_4;
                end_for_4:;
                // if area>wp.float64(1e-30):                                                     <L 55>
                var_232 = 1e-30;
                var_233 = (var_213 > var_232);
                if (var_233) {
                    // index=wp.atomic_add(active,0,1)                                            <L 56>
                    var_236 = wp::atomic_add(var_active, var_234, var_235);
                    // if index>=capacity:wp.atomic_max(bad,0,5)                                  <L 57>
                    var_237 = (var_236 >= var_capacity);
                    if (var_237) {
                        var_240 = wp::atomic_max(var_bad, var_238, var_239);
                    }
                    if (!var_237) {
                        // else:active_ids[index]=pair;polycounts[pair]=n;sources[pair]=src       <L 58>
                        wp::array_store(var_active_ids, var_236, var_0);
                        wp::array_store(var_polycounts, var_0, var_120);
                        wp::array_store(var_sources, var_0, var_122);
                    }
                }
            }
            var_241 = wp::where(var_205, var_218, var_127);
        }
    }
}


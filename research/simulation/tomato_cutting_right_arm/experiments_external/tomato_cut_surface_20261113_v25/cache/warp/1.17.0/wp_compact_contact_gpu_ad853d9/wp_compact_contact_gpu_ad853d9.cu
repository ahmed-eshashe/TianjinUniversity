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




// /home/omen/Documents/Codex/experiments/tomato_cut_surface_20261113_v25/src/contact_gpu_precise.py:12
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


// /home/omen/Documents/Codex/experiments/tomato_cut_surface_20261113_v25/src/exact_cad_gpu.py:9
static CUDA_CALLABLE Signed_7e3cff60 signed_1(
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


// /home/omen/Documents/Codex/experiments/tomato_cut_surface_20261113_v25/src/contact_gpu_precise.py:12
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


// /home/omen/Documents/Codex/experiments/tomato_cut_surface_20261113_v25/src/exact_cad_gpu.py:9
static CUDA_CALLABLE void adj_signed_1(
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



extern "C" __global__ void candidate_pairs_8fe052b6_cuda_kernel_forward(
    wp::launch_bounds_t<1> dim,
    wp::array_t<wp::mat_t<3, 3, wp::float64>> var_local,
    wp::array_t<wp::vec_t<3, wp::float64>> var_bounds,
    wp::int32 var_ncells,
    wp::array_t<wp::int32> var_face_count,
    wp::array_t<wp::int32> var_face_ids,
    wp::array_t<wp::int32> var_count,
    wp::array_t<wp::int32> var_pairs,
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
        bool var_3;
        const wp::int32 var_4 = 0;
        wp::int32* var_5;
        bool var_6;
        wp::int32 var_7;
        const wp::int32 var_8 = 0;
        wp::int32* var_9;
        const wp::int32 var_10 = 0;
        bool var_11;
        wp::int32 var_12;
        wp::int32* var_13;
        wp::int32 var_14;
        wp::int32 var_15;
        wp::int32 var_16;
        wp::int32 var_17;
        wp::mat_t<3, 3, wp::float64>* var_18;
        wp::mat_t<3, 3, wp::float64> var_19;
        wp::mat_t<3, 3, wp::float64> var_20;
        const bool var_21 = true;
        const wp::int32 var_22 = 0;
        const wp::int32 var_23 = 0;
        wp::float64 var_24;
        const wp::int32 var_25 = 1;
        wp::float64 var_26;
        const wp::int32 var_27 = 2;
        wp::float64 var_28;
        wp::float64 var_29;
        wp::float64 var_30;
        const wp::int32 var_31 = 0;
        wp::float64 var_32;
        const wp::int32 var_33 = 1;
        wp::float64 var_34;
        const wp::int32 var_35 = 2;
        wp::float64 var_36;
        wp::float64 var_37;
        wp::float64 var_38;
        bool var_39;
        const wp::int32 var_40 = 0;
        wp::vec_t<3, wp::float64>* var_41;
        wp::float64 var_42;
        wp::vec_t<3, wp::float64> var_43;
        bool var_44;
        const wp::int32 var_45 = 1;
        wp::vec_t<3, wp::float64>* var_46;
        wp::float64 var_47;
        wp::vec_t<3, wp::float64> var_48;
        bool var_49;
        const bool var_50 = false;
        bool var_51;
        const wp::int32 var_52 = 1;
        const wp::int32 var_53 = 0;
        wp::float64 var_54;
        const wp::int32 var_55 = 1;
        wp::float64 var_56;
        const wp::int32 var_57 = 2;
        wp::float64 var_58;
        wp::float64 var_59;
        wp::float64 var_60;
        const wp::int32 var_61 = 0;
        wp::float64 var_62;
        const wp::int32 var_63 = 1;
        wp::float64 var_64;
        const wp::int32 var_65 = 2;
        wp::float64 var_66;
        wp::float64 var_67;
        wp::float64 var_68;
        bool var_69;
        const wp::int32 var_70 = 0;
        wp::vec_t<3, wp::float64>* var_71;
        wp::float64 var_72;
        wp::vec_t<3, wp::float64> var_73;
        bool var_74;
        const wp::int32 var_75 = 1;
        wp::vec_t<3, wp::float64>* var_76;
        wp::float64 var_77;
        wp::vec_t<3, wp::float64> var_78;
        bool var_79;
        const bool var_80 = false;
        bool var_81;
        const wp::int32 var_82 = 2;
        const wp::int32 var_83 = 0;
        wp::float64 var_84;
        const wp::int32 var_85 = 1;
        wp::float64 var_86;
        const wp::int32 var_87 = 2;
        wp::float64 var_88;
        wp::float64 var_89;
        wp::float64 var_90;
        const wp::int32 var_91 = 0;
        wp::float64 var_92;
        const wp::int32 var_93 = 1;
        wp::float64 var_94;
        const wp::int32 var_95 = 2;
        wp::float64 var_96;
        wp::float64 var_97;
        wp::float64 var_98;
        bool var_99;
        const wp::int32 var_100 = 0;
        wp::vec_t<3, wp::float64>* var_101;
        wp::float64 var_102;
        wp::vec_t<3, wp::float64> var_103;
        bool var_104;
        const wp::int32 var_105 = 1;
        wp::vec_t<3, wp::float64>* var_106;
        wp::float64 var_107;
        wp::vec_t<3, wp::float64> var_108;
        bool var_109;
        const bool var_110 = false;
        bool var_111;
        bool var_112;
        const wp::int32 var_113 = 0;
        wp::int32* var_114;
        const wp::int32 var_115 = 0;
        bool var_116;
        wp::int32 var_117;
        const wp::int32 var_118 = 0;
        const wp::int32 var_119 = 1;
        wp::int32 var_120;
        wp::shape_t* var_121;
        const wp::int32 var_122 = 0;
        wp::int32 var_123;
        wp::shape_t var_124;
        bool var_125;
        const wp::int32 var_126 = 0;
        const wp::int32 var_127 = 5;
        wp::int32 var_128;
        //---------
        // forward
        // def candidate_pairs(local:wp.array(dtype=wp.mat33d),bounds:wp.array2d(dtype=wp.vec3d),ncells:int,face_count:wp.array(dtype=int),face_ids:wp.array(dtype=int),count:wp.array(dtype=int),pairs:wp.array(dtype=int),bad:wp.array(dtype=int)):       <L 26>
        // thread=wp.tid();slot=thread//ncells;cell=thread%ncells                                 <L 27>
        var_0 = builtin_tid1d();
        var_1 = wp::floordiv(var_0, var_ncells);
        var_2 = wp::mod(var_0, var_ncells);
        // if slot>=face_count[0] or bad[0]!=0:return                                             <L 28>
        var_5 = wp::address(var_face_count, var_4);
        var_7 = wp::load(var_5);
        var_6 = (var_1 >= var_7);
        var_3 = var_6;
        if (!var_3) {
            var_9 = wp::address(var_bad, var_8);
            var_12 = wp::load(var_9);
            var_11 = (var_12 != var_10);
            var_3 = var_3 || var_11;
        }
        if (var_3) {
            continue;
        }
        // face=face_ids[slot];pair=face*ncells+cell;x=local[face];overlap=True                   <L 29>
        var_13 = wp::address(var_face_ids, var_1);
        var_15 = wp::load(var_13);
        var_14 = wp::copy(var_15);
        var_16 = wp::mul(var_14, var_ncells);
        var_17 = wp::add(var_16, var_2);
        var_18 = wp::address(var_local, var_14);
        var_20 = wp::load(var_18);
        var_19 = wp::copy(var_20);
        // for axis in range(3):                                                                  <L 30>
        // lo=wp.min(x[0,axis],wp.min(x[1,axis],x[2,axis]));hi=wp.max(x[0,axis],wp.max(x[1,axis],x[2,axis]))       <L 31>
        var_24 = wp::extract(var_19, var_23, var_22);
        var_26 = wp::extract(var_19, var_25, var_22);
        var_28 = wp::extract(var_19, var_27, var_22);
        var_29 = wp::min(var_26, var_28);
        var_30 = wp::min(var_24, var_29);
        var_32 = wp::extract(var_19, var_31, var_22);
        var_34 = wp::extract(var_19, var_33, var_22);
        var_36 = wp::extract(var_19, var_35, var_22);
        var_37 = wp::max(var_34, var_36);
        var_38 = wp::max(var_32, var_37);
        // if hi<bounds[cell,0][axis] or lo>bounds[cell,1][axis]:overlap=False                    <L 32>
        var_41 = wp::address(var_bounds, var_2, var_40);
        var_43 = wp::load(var_41);
        var_42 = wp::extract(var_43, var_22);
        var_44 = (var_38 < var_42);
        var_39 = var_44;
        if (!var_39) {
            var_46 = wp::address(var_bounds, var_2, var_45);
            var_48 = wp::load(var_46);
            var_47 = wp::extract(var_48, var_22);
            var_49 = (var_30 > var_47);
            var_39 = var_39 || var_49;
        }
        if (var_39) {
        }
        var_51 = wp::where(var_39, var_50, var_21);
        // lo=wp.min(x[0,axis],wp.min(x[1,axis],x[2,axis]));hi=wp.max(x[0,axis],wp.max(x[1,axis],x[2,axis]))       <L 31>
        var_54 = wp::extract(var_19, var_53, var_52);
        var_56 = wp::extract(var_19, var_55, var_52);
        var_58 = wp::extract(var_19, var_57, var_52);
        var_59 = wp::min(var_56, var_58);
        var_60 = wp::min(var_54, var_59);
        var_62 = wp::extract(var_19, var_61, var_52);
        var_64 = wp::extract(var_19, var_63, var_52);
        var_66 = wp::extract(var_19, var_65, var_52);
        var_67 = wp::max(var_64, var_66);
        var_68 = wp::max(var_62, var_67);
        // if hi<bounds[cell,0][axis] or lo>bounds[cell,1][axis]:overlap=False                    <L 32>
        var_71 = wp::address(var_bounds, var_2, var_70);
        var_73 = wp::load(var_71);
        var_72 = wp::extract(var_73, var_52);
        var_74 = (var_68 < var_72);
        var_69 = var_74;
        if (!var_69) {
            var_76 = wp::address(var_bounds, var_2, var_75);
            var_78 = wp::load(var_76);
            var_77 = wp::extract(var_78, var_52);
            var_79 = (var_60 > var_77);
            var_69 = var_69 || var_79;
        }
        if (var_69) {
        }
        var_81 = wp::where(var_69, var_80, var_51);
        // lo=wp.min(x[0,axis],wp.min(x[1,axis],x[2,axis]));hi=wp.max(x[0,axis],wp.max(x[1,axis],x[2,axis]))       <L 31>
        var_84 = wp::extract(var_19, var_83, var_82);
        var_86 = wp::extract(var_19, var_85, var_82);
        var_88 = wp::extract(var_19, var_87, var_82);
        var_89 = wp::min(var_86, var_88);
        var_90 = wp::min(var_84, var_89);
        var_92 = wp::extract(var_19, var_91, var_82);
        var_94 = wp::extract(var_19, var_93, var_82);
        var_96 = wp::extract(var_19, var_95, var_82);
        var_97 = wp::max(var_94, var_96);
        var_98 = wp::max(var_92, var_97);
        // if hi<bounds[cell,0][axis] or lo>bounds[cell,1][axis]:overlap=False                    <L 32>
        var_101 = wp::address(var_bounds, var_2, var_100);
        var_103 = wp::load(var_101);
        var_102 = wp::extract(var_103, var_82);
        var_104 = (var_98 < var_102);
        var_99 = var_104;
        if (!var_99) {
            var_106 = wp::address(var_bounds, var_2, var_105);
            var_108 = wp::load(var_106);
            var_107 = wp::extract(var_108, var_82);
            var_109 = (var_90 > var_107);
            var_99 = var_99 || var_109;
        }
        if (var_99) {
        }
        var_111 = wp::where(var_99, var_110, var_81);
        // if overlap and bad[0]==0:                                                              <L 33>
        var_112 = var_111;
        if (var_112) {
            var_114 = wp::address(var_bad, var_113);
            var_117 = wp::load(var_114);
            var_116 = (var_117 == var_115);
            var_112 = var_112 && var_116;
        }
        if (var_112) {
            // index=wp.atomic_add(count,0,1)                                                     <L 34>
            var_120 = wp::atomic_add(var_count, var_118, var_119);
            // if index>=pairs.shape[0]:wp.atomic_max(bad,0,5)                                    <L 35>
            var_121 = &(var_pairs.shape);
            var_124 = wp::load(var_121);
            var_123 = wp::extract(var_124, var_122);
            var_125 = (var_120 >= var_123);
            if (var_125) {
                var_128 = wp::atomic_max(var_bad, var_126, var_127);
            }
            if (!var_125) {
                // else:pairs[index]=pair                                                         <L 36>
                wp::array_store(var_pairs, var_120, var_17);
            }
        }
    }
}



extern "C" __global__ void integrate_a907d8d6_cuda_kernel_forward(
    wp::launch_bounds_t<1> dim,
    wp::uint64 var_mesh,
    wp::array_t<wp::vec_t<3, wp::float64>> var_tri,
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
        wp::int32* var_25;
        wp::int32 var_26;
        wp::int32 var_27;
        const wp::int32 var_28 = 2;
        wp::int32 var_29;
        bool var_30;
        const wp::int32 var_31 = 0;
        wp::vec_t<3, wp::float64>* var_32;
        const wp::int32 var_33 = 1;
        wp::int32 var_34;
        wp::vec_t<3, wp::float64>* var_35;
        const wp::int32 var_36 = 2;
        wp::int32 var_37;
        wp::vec_t<3, wp::float64>* var_38;
        wp::mat_t<3, 3, wp::float64> var_39;
        wp::vec_t<3, wp::float64> var_40;
        wp::vec_t<3, wp::float64> var_41;
        wp::vec_t<3, wp::float64> var_42;
        wp::float64* var_43;
        wp::float64 var_44;
        wp::float64 var_45;
        wp::float64 var_46;
        wp::float64 var_47;
        wp::float64 var_48;
        wp::float64 var_49;
        wp::mat_t<3, 3, wp::float64>* var_50;
        wp::mat_t<3, 3, wp::float64> var_51;
        wp::mat_t<3, 3, wp::float64> var_52;
        wp::mat_t<3, 3, wp::float64>* var_53;
        wp::mat_t<3, 3, wp::float64> var_54;
        wp::mat_t<3, 3, wp::float64> var_55;
        wp::mat_t<3, 3, wp::float64>* var_56;
        wp::mat_t<3, 3, wp::float64> var_57;
        wp::mat_t<3, 3, wp::float64> var_58;
        const wp::int32 var_59 = 0;
        wp::vec_t<3, wp::float64>* var_60;
        wp::vec_t<3, wp::float64> var_61;
        wp::vec_t<3, wp::float64> var_62;
        const wp::int32 var_63 = 1;
        wp::vec_t<3, wp::float64>* var_64;
        wp::vec_t<3, wp::float64> var_65;
        wp::vec_t<3, wp::float64> var_66;
        wp::float64 var_67;
        wp::mat_t<3, 3, wp::float64> var_68;
        wp::float64 var_69;
        wp::float64 var_70;
        wp::float64 var_71;
        wp::float64 var_72;
        wp::vec_t<3, wp::float64> var_73;
        const wp::int32 var_74 = 0;
        const wp::float32 var_75 = 1.0;
        const wp::float32 var_76 = 6.0;
        wp::float32 var_77;
        wp::float64 var_78;
        wp::vec_t<3, wp::float64> var_79;
        const wp::float32 var_80 = 2.0;
        const wp::float32 var_81 = 3.0;
        wp::float32 var_82;
        wp::float64 var_83;
        wp::mat_t<3, 3, wp::float64> var_84;
        wp::vec_t<3, wp::float64> var_85;
        wp::mat_t<3, 3, wp::float64> var_86;
        wp::vec_t<3, wp::float64> var_87;
        wp::mat_t<3, 3, wp::float64> var_88;
        wp::vec_t<3, wp::float64> var_89;
        wp::mat_t<3, 3, wp::float64> var_90;
        wp::vec_t<3, wp::float64> var_91;
        wp::vec_t<3, wp::float64> var_92;
        Signed_7e3cff60 var_93;
        wp::float64* var_94;
        wp::float64 var_95;
        wp::float64 var_96;
        wp::float64 var_97;
        wp::float64 var_98;
        wp::vec_t<3, wp::float64>* var_99;
        wp::vec_t<3, wp::float64> var_100;
        wp::vec_t<3, wp::float64> var_101;
        wp::float64 var_102;
        wp::float64 var_103;
        wp::float64 var_104;
        wp::float64 var_105;
        wp::float64 var_106;
        wp::vec_t<3, wp::float64> var_107;
        wp::float64 var_108;
        wp::vec_t<3, wp::float64> var_109;
        wp::vec_t<3, wp::float64> var_110;
        wp::float64 var_111;
        wp::float64 var_112;
        wp::vec_t<3, wp::float64> var_113;
        wp::float64 var_114;
        bool var_115;
        wp::float64 var_116;
        wp::float64 var_117;
        wp::float64 var_118;
        wp::float64 var_119;
        wp::float64 var_120;
        wp::float64 var_121;
        wp::float64 var_122;
        wp::vec_t<3, wp::float64> var_123;
        wp::vec_t<3, wp::float64> var_124;
        wp::vec_t<3, wp::float64> var_125;
        wp::vec_t<3, wp::float64> var_126;
        wp::vec_t<3, wp::float64> var_127;
        const wp::int32 var_128 = 0;
        const wp::int32 var_129 = 0;
        wp::float64 var_130;
        wp::float64 var_131;
        wp::float64 var_132;
        const wp::int32 var_133 = 1;
        wp::float64 var_134;
        wp::float64 var_135;
        wp::float64 var_136;
        const wp::int32 var_137 = 2;
        wp::float64 var_138;
        wp::float64 var_139;
        wp::float64 var_140;
        const wp::int32 var_141 = 1;
        const wp::int32 var_142 = 0;
        wp::float64 var_143;
        wp::float64 var_144;
        wp::float64 var_145;
        const wp::int32 var_146 = 1;
        wp::float64 var_147;
        wp::float64 var_148;
        wp::float64 var_149;
        const wp::int32 var_150 = 2;
        wp::float64 var_151;
        wp::float64 var_152;
        wp::float64 var_153;
        const wp::int32 var_154 = 2;
        const wp::int32 var_155 = 0;
        wp::float64 var_156;
        wp::float64 var_157;
        wp::float64 var_158;
        const wp::int32 var_159 = 1;
        wp::float64 var_160;
        wp::float64 var_161;
        wp::float64 var_162;
        const wp::int32 var_163 = 2;
        wp::float64 var_164;
        wp::float64 var_165;
        wp::float64 var_166;
        wp::float64 var_167;
        wp::float64 var_168;
        wp::float64 var_169;
        wp::float64 var_170;
        wp::float64 var_171;
        wp::float64 var_172;
        wp::float64 var_173;
        wp::float64 var_174;
        wp::vec_t<3, wp::float64> var_175;
        wp::vec_t<3, wp::float64> var_176;
        wp::vec_t<3, wp::float64> var_177;
        const wp::int32 var_178 = 1;
        const wp::float32 var_179 = 1.0;
        const wp::float32 var_180 = 6.0;
        wp::float32 var_181;
        wp::float64 var_182;
        wp::vec_t<3, wp::float64> var_183;
        const wp::float32 var_184 = 2.0;
        const wp::float32 var_185 = 3.0;
        wp::float32 var_186;
        wp::float64 var_187;
        wp::mat_t<3, 3, wp::float64> var_188;
        wp::vec_t<3, wp::float64> var_189;
        wp::mat_t<3, 3, wp::float64> var_190;
        wp::vec_t<3, wp::float64> var_191;
        wp::mat_t<3, 3, wp::float64> var_192;
        wp::vec_t<3, wp::float64> var_193;
        wp::mat_t<3, 3, wp::float64> var_194;
        wp::vec_t<3, wp::float64> var_195;
        wp::vec_t<3, wp::float64> var_196;
        Signed_7e3cff60 var_197;
        wp::float64* var_198;
        wp::float64 var_199;
        wp::float64 var_200;
        wp::float64 var_201;
        wp::float64 var_202;
        wp::vec_t<3, wp::float64>* var_203;
        wp::vec_t<3, wp::float64> var_204;
        wp::vec_t<3, wp::float64> var_205;
        wp::float64 var_206;
        wp::float64 var_207;
        wp::float64 var_208;
        wp::float64 var_209;
        wp::float64 var_210;
        wp::vec_t<3, wp::float64> var_211;
        wp::float64 var_212;
        wp::vec_t<3, wp::float64> var_213;
        wp::vec_t<3, wp::float64> var_214;
        wp::float64 var_215;
        wp::float64 var_216;
        wp::vec_t<3, wp::float64> var_217;
        wp::float64 var_218;
        bool var_219;
        wp::float64 var_220;
        wp::float64 var_221;
        wp::float64 var_222;
        wp::float64 var_223;
        wp::float64 var_224;
        wp::float64 var_225;
        wp::float64 var_226;
        wp::vec_t<3, wp::float64> var_227;
        wp::vec_t<3, wp::float64> var_228;
        wp::vec_t<3, wp::float64> var_229;
        wp::vec_t<3, wp::float64> var_230;
        wp::vec_t<3, wp::float64> var_231;
        const wp::int32 var_232 = 0;
        const wp::int32 var_233 = 0;
        wp::float64 var_234;
        wp::float64 var_235;
        wp::float64 var_236;
        const wp::int32 var_237 = 1;
        wp::float64 var_238;
        wp::float64 var_239;
        wp::float64 var_240;
        const wp::int32 var_241 = 2;
        wp::float64 var_242;
        wp::float64 var_243;
        wp::float64 var_244;
        const wp::int32 var_245 = 1;
        const wp::int32 var_246 = 0;
        wp::float64 var_247;
        wp::float64 var_248;
        wp::float64 var_249;
        const wp::int32 var_250 = 1;
        wp::float64 var_251;
        wp::float64 var_252;
        wp::float64 var_253;
        const wp::int32 var_254 = 2;
        wp::float64 var_255;
        wp::float64 var_256;
        wp::float64 var_257;
        const wp::int32 var_258 = 2;
        const wp::int32 var_259 = 0;
        wp::float64 var_260;
        wp::float64 var_261;
        wp::float64 var_262;
        const wp::int32 var_263 = 1;
        wp::float64 var_264;
        wp::float64 var_265;
        wp::float64 var_266;
        const wp::int32 var_267 = 2;
        wp::float64 var_268;
        wp::float64 var_269;
        wp::float64 var_270;
        wp::float64 var_271;
        wp::float64 var_272;
        wp::float64 var_273;
        wp::float64 var_274;
        wp::float64 var_275;
        wp::float64 var_276;
        wp::float64 var_277;
        wp::float64 var_278;
        wp::vec_t<3, wp::float64> var_279;
        wp::vec_t<3, wp::float64> var_280;
        wp::vec_t<3, wp::float64> var_281;
        const wp::int32 var_282 = 2;
        const wp::float32 var_283 = 1.0;
        const wp::float32 var_284 = 6.0;
        wp::float32 var_285;
        wp::float64 var_286;
        wp::vec_t<3, wp::float64> var_287;
        const wp::float32 var_288 = 2.0;
        const wp::float32 var_289 = 3.0;
        wp::float32 var_290;
        wp::float64 var_291;
        wp::mat_t<3, 3, wp::float64> var_292;
        wp::vec_t<3, wp::float64> var_293;
        wp::mat_t<3, 3, wp::float64> var_294;
        wp::vec_t<3, wp::float64> var_295;
        wp::mat_t<3, 3, wp::float64> var_296;
        wp::vec_t<3, wp::float64> var_297;
        wp::mat_t<3, 3, wp::float64> var_298;
        wp::vec_t<3, wp::float64> var_299;
        wp::vec_t<3, wp::float64> var_300;
        Signed_7e3cff60 var_301;
        wp::float64* var_302;
        wp::float64 var_303;
        wp::float64 var_304;
        wp::float64 var_305;
        wp::float64 var_306;
        wp::vec_t<3, wp::float64>* var_307;
        wp::vec_t<3, wp::float64> var_308;
        wp::vec_t<3, wp::float64> var_309;
        wp::float64 var_310;
        wp::float64 var_311;
        wp::float64 var_312;
        wp::float64 var_313;
        wp::float64 var_314;
        wp::vec_t<3, wp::float64> var_315;
        wp::float64 var_316;
        wp::vec_t<3, wp::float64> var_317;
        wp::vec_t<3, wp::float64> var_318;
        wp::float64 var_319;
        wp::float64 var_320;
        wp::vec_t<3, wp::float64> var_321;
        wp::float64 var_322;
        bool var_323;
        wp::float64 var_324;
        wp::float64 var_325;
        wp::float64 var_326;
        wp::float64 var_327;
        wp::float64 var_328;
        wp::float64 var_329;
        wp::float64 var_330;
        wp::vec_t<3, wp::float64> var_331;
        wp::vec_t<3, wp::float64> var_332;
        wp::vec_t<3, wp::float64> var_333;
        wp::vec_t<3, wp::float64> var_334;
        wp::vec_t<3, wp::float64> var_335;
        const wp::int32 var_336 = 0;
        const wp::int32 var_337 = 0;
        wp::float64 var_338;
        wp::float64 var_339;
        wp::float64 var_340;
        const wp::int32 var_341 = 1;
        wp::float64 var_342;
        wp::float64 var_343;
        wp::float64 var_344;
        const wp::int32 var_345 = 2;
        wp::float64 var_346;
        wp::float64 var_347;
        wp::float64 var_348;
        const wp::int32 var_349 = 1;
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
        const wp::int32 var_362 = 2;
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
        wp::float64 var_375;
        wp::float64 var_376;
        wp::float64 var_377;
        wp::float64 var_378;
        wp::float64 var_379;
        wp::float64 var_380;
        wp::float64 var_381;
        wp::float64 var_382;
        wp::vec_t<3, wp::float64> var_383;
        wp::vec_t<3, wp::float64> var_384;
        wp::vec_t<3, wp::float64> var_385;
        const wp::int32 var_386 = 0;
        wp::vec_t<3, wp::float64> var_387;
        wp::vec_t<3, wp::float64> var_388;
        const wp::int32 var_389 = 1;
        wp::vec_t<3, wp::float64> var_390;
        wp::vec_t<3, wp::float64> var_391;
        const wp::int32 var_392 = 2;
        wp::vec_t<3, wp::float64> var_393;
        wp::vec_t<3, wp::float64> var_394;
        wp::float64 var_395;
        wp::float64 var_396;
        wp::float64 var_397;
        wp::vec_t<3, wp::float64> var_398;
        //---------
        // forward
        // def integrate(mesh:wp.uint64,tri:wp.array2d(dtype=wp.vec3d),R:wp.mat33d,pose:wp.array(dtype=wp.vec3d),X:wp.array(dtype=wp.mat33d),V:wp.array(dtype=wp.mat33d),areas:wp.array(dtype=wp.float64),masters:wp.array(dtype=wp.mat33d),polygon:wp.array2d(dtype=wp.vec3d),counts:wp.array(dtype=int),faces:wp.array(dtype=int),active:wp.array(dtype=int),bad:wp.array(dtype=int),ff:wp.array2d(dtype=wp.vec3d),uu:wp.array(dtype=wp.float64),dd:wp.array(dtype=wp.float64),ww:wp.array(dtype=wp.float64),mm:wp.array(dtype=wp.vec3d)):       <L 66>
        // thread=wp.tid();nm=masters.shape[0];slot=thread//(8*nm);root=(thread//nm)%8;leaf=thread%nm       <L 67>
        var_0 = builtin_tid1d();
        var_1 = &(var_masters.shape);
        var_4 = wp::load(var_1);
        var_3 = wp::extract(var_4, var_2);
        var_6 = wp::mul(var_5, var_3);
        var_7 = wp::floordiv(var_0, var_6);
        var_8 = wp::floordiv(var_0, var_3);
        var_10 = wp::mod(var_8, var_9);
        var_11 = wp::mod(var_0, var_3);
        // if slot<active[0] and bad[0]==0:                                                       <L 68>
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
            // face=faces[slot];n=counts[slot]                                                    <L 69>
            var_22 = wp::address(var_faces, var_7);
            var_24 = wp::load(var_22);
            var_23 = wp::copy(var_24);
            var_25 = wp::address(var_counts, var_7);
            var_27 = wp::load(var_25);
            var_26 = wp::copy(var_27);
            // if root<n-2:                                                                       <L 70>
            var_29 = wp::sub(var_26, var_28);
            var_30 = (var_10 < var_29);
            if (var_30) {
                // B=wp.matrix_from_rows(polygon[slot,0],polygon[slot,root+1],polygon[slot,root+2]);area=areas[face]*wp.abs(wp.determinant(B))/wp.float64(nm);B=masters[leaf]*B;x=X[face];v=V[face];T=pose[0];tv=pose[1];forces=wp.mat33d(wp.float64(0.));U=wp.float64(0.);D=wp.float64(0.);W=wp.float64(0.);M=wp.vec3d(wp.float64(0.))       <L 71>
                var_32 = wp::address(var_polygon, var_7, var_31);
                var_34 = wp::add(var_10, var_33);
                var_35 = wp::address(var_polygon, var_7, var_34);
                var_37 = wp::add(var_10, var_36);
                var_38 = wp::address(var_polygon, var_7, var_37);
                var_40 = wp::load(var_32);
                var_41 = wp::load(var_35);
                var_42 = wp::load(var_38);
                var_39 = wp::matrix_from_rows<wp::float64>(var_40, var_41, var_42);
                var_43 = wp::address(var_areas, var_23);
                var_44 = wp::determinant(var_39);
                var_45 = wp::abs(var_44);
                var_47 = wp::load(var_43);
                var_46 = wp::mul(var_47, var_45);
                var_48 = wp::float64(var_3);
                var_49 = wp::div(var_46, var_48);
                var_50 = wp::address(var_masters, var_11);
                var_52 = wp::load(var_50);
                var_51 = wp::mul(var_52, var_39);
                var_53 = wp::address(var_X, var_23);
                var_55 = wp::load(var_53);
                var_54 = wp::copy(var_55);
                var_56 = wp::address(var_V, var_23);
                var_58 = wp::load(var_56);
                var_57 = wp::copy(var_58);
                var_60 = wp::address(var_pose, var_59);
                var_62 = wp::load(var_60);
                var_61 = wp::copy(var_62);
                var_64 = wp::address(var_pose, var_63);
                var_66 = wp::load(var_64);
                var_65 = wp::copy(var_66);
                var_67 = 0.0;
                var_68 = wp::mat_t<3, 3, wp::float64>(var_67);
                var_69 = 0.0;
                var_70 = 0.0;
                var_71 = 0.0;
                var_72 = 0.0;
                var_73 = wp::vec_t<3, wp::float64>(var_72);
                // for k in range(3):                                                             <L 72>
                // rule=wp.vec3d(wp.float64(1./6.));rule[k]=wp.float64(2./3.);bary=wp.transpose(B)*rule;p=wp.transpose(x)*bary;vel=wp.transpose(v)*bary;s=signed(mesh,tri,wp.transpose(R)*(p-T));depth=wp.max(-s.phi,wp.float64(0.));normal=R*s.normal;fn=wp.float64(1e9)*area/wp.float64(3.)*depth;rel=vel-tv;tan=rel-wp.dot(rel,normal)*normal;speed=wp.length(tan);fr=wp.vec3d(wp.float64(0.))       <L 73>
                var_77 = wp::div(var_75, var_76);
                var_78 = wp::float64(var_77);
                var_79 = wp::vec_t<3, wp::float64>(var_78);
                var_82 = wp::div(var_80, var_81);
                var_83 = wp::float64(var_82);
                wp::assign_inplace(var_79, var_74, var_83);
                var_84 = wp::transpose(var_51);
                var_85 = wp::mul(var_84, var_79);
                var_86 = wp::transpose(var_54);
                var_87 = wp::mul(var_86, var_85);
                var_88 = wp::transpose(var_57);
                var_89 = wp::mul(var_88, var_85);
                var_90 = wp::transpose(var_R);
                var_91 = wp::sub(var_87, var_61);
                var_92 = wp::mul(var_90, var_91);
                var_93 = signed_1(var_mesh, var_tri, var_92);
                var_94 = &((var_93).phi);
                var_96 = wp::load(var_94);
                var_95 = wp::neg(var_96);
                var_97 = 0.0;
                var_98 = wp::max(var_95, var_97);
                var_99 = &((var_93).normal);
                var_101 = wp::load(var_99);
                var_100 = wp::mul(var_R, var_101);
                var_102 = 1000000000.0;
                var_103 = wp::mul(var_102, var_49);
                var_104 = 3.0;
                var_105 = wp::div(var_103, var_104);
                var_106 = wp::mul(var_105, var_98);
                var_107 = wp::sub(var_89, var_65);
                var_108 = wp::dot(var_107, var_100);
                var_109 = wp::mul(var_108, var_100);
                var_110 = wp::sub(var_107, var_109);
                var_111 = wp::length(var_110);
                var_112 = 0.0;
                var_113 = wp::vec_t<3, wp::float64>(var_112);
                // if speed>wp.float64(1e-30):fr=-wp.float64(.2)*fn*wp.tanh(speed/wp.float64(.001))*tan/speed       <L 74>
                var_114 = 1e-30;
                var_115 = (var_111 > var_114);
                if (var_115) {
                    var_116 = 0.2;
                    var_117 = wp::neg(var_116);
                    var_118 = wp::mul(var_117, var_106);
                    var_119 = 0.001;
                    var_120 = wp::div(var_111, var_119);
                    var_121 = wp::tanh(var_120);
                    var_122 = wp::mul(var_118, var_121);
                    var_123 = wp::mul(var_122, var_110);
                    var_124 = wp::div(var_123, var_111);
                }
                var_125 = wp::where(var_115, var_124, var_113);
                // f=fn*normal+fr                                                                 <L 75>
                var_126 = wp::mul(var_106, var_100);
                var_127 = wp::add(var_126, var_125);
                // for u in range(3):                                                             <L 76>
                // for a in range(3):forces[u,a]+=bary[u]*f[a]                                    <L 77>
                var_130 = wp::extract(var_85, var_128);
                var_131 = wp::extract(var_127, var_129);
                var_132 = wp::mul(var_130, var_131);
                wp::add_inplace(var_68, var_128, var_129, var_132);
                var_134 = wp::extract(var_85, var_128);
                var_135 = wp::extract(var_127, var_133);
                var_136 = wp::mul(var_134, var_135);
                wp::add_inplace(var_68, var_128, var_133, var_136);
                var_138 = wp::extract(var_85, var_128);
                var_139 = wp::extract(var_127, var_137);
                var_140 = wp::mul(var_138, var_139);
                wp::add_inplace(var_68, var_128, var_137, var_140);
                var_143 = wp::extract(var_85, var_141);
                var_144 = wp::extract(var_127, var_142);
                var_145 = wp::mul(var_143, var_144);
                wp::add_inplace(var_68, var_141, var_142, var_145);
                var_147 = wp::extract(var_85, var_141);
                var_148 = wp::extract(var_127, var_146);
                var_149 = wp::mul(var_147, var_148);
                wp::add_inplace(var_68, var_141, var_146, var_149);
                var_151 = wp::extract(var_85, var_141);
                var_152 = wp::extract(var_127, var_150);
                var_153 = wp::mul(var_151, var_152);
                wp::add_inplace(var_68, var_141, var_150, var_153);
                var_156 = wp::extract(var_85, var_154);
                var_157 = wp::extract(var_127, var_155);
                var_158 = wp::mul(var_156, var_157);
                wp::add_inplace(var_68, var_154, var_155, var_158);
                var_160 = wp::extract(var_85, var_154);
                var_161 = wp::extract(var_127, var_159);
                var_162 = wp::mul(var_160, var_161);
                wp::add_inplace(var_68, var_154, var_159, var_162);
                var_164 = wp::extract(var_85, var_154);
                var_165 = wp::extract(var_127, var_163);
                var_166 = wp::mul(var_164, var_165);
                wp::add_inplace(var_68, var_154, var_163, var_166);
                // U+=wp.float64(.5)*fn*depth;D-=wp.dot(fr,rel);W+=wp.dot(f,tv);M+=wp.cross(p-T,f)       <L 78>
                var_167 = 0.5;
                var_168 = wp::mul(var_167, var_106);
                var_169 = wp::mul(var_168, var_98);
                var_170 = wp::add(var_69, var_169);
                var_171 = wp::dot(var_125, var_107);
                var_172 = wp::sub(var_70, var_171);
                var_173 = wp::dot(var_127, var_65);
                var_174 = wp::add(var_71, var_173);
                var_175 = wp::sub(var_87, var_61);
                var_176 = wp::cross(var_175, var_127);
                var_177 = wp::add(var_73, var_176);
                // rule=wp.vec3d(wp.float64(1./6.));rule[k]=wp.float64(2./3.);bary=wp.transpose(B)*rule;p=wp.transpose(x)*bary;vel=wp.transpose(v)*bary;s=signed(mesh,tri,wp.transpose(R)*(p-T));depth=wp.max(-s.phi,wp.float64(0.));normal=R*s.normal;fn=wp.float64(1e9)*area/wp.float64(3.)*depth;rel=vel-tv;tan=rel-wp.dot(rel,normal)*normal;speed=wp.length(tan);fr=wp.vec3d(wp.float64(0.))       <L 73>
                var_181 = wp::div(var_179, var_180);
                var_182 = wp::float64(var_181);
                var_183 = wp::vec_t<3, wp::float64>(var_182);
                var_186 = wp::div(var_184, var_185);
                var_187 = wp::float64(var_186);
                wp::assign_inplace(var_183, var_178, var_187);
                var_188 = wp::transpose(var_51);
                var_189 = wp::mul(var_188, var_183);
                var_190 = wp::transpose(var_54);
                var_191 = wp::mul(var_190, var_189);
                var_192 = wp::transpose(var_57);
                var_193 = wp::mul(var_192, var_189);
                var_194 = wp::transpose(var_R);
                var_195 = wp::sub(var_191, var_61);
                var_196 = wp::mul(var_194, var_195);
                var_197 = signed_1(var_mesh, var_tri, var_196);
                var_198 = &((var_197).phi);
                var_200 = wp::load(var_198);
                var_199 = wp::neg(var_200);
                var_201 = 0.0;
                var_202 = wp::max(var_199, var_201);
                var_203 = &((var_197).normal);
                var_205 = wp::load(var_203);
                var_204 = wp::mul(var_R, var_205);
                var_206 = 1000000000.0;
                var_207 = wp::mul(var_206, var_49);
                var_208 = 3.0;
                var_209 = wp::div(var_207, var_208);
                var_210 = wp::mul(var_209, var_202);
                var_211 = wp::sub(var_193, var_65);
                var_212 = wp::dot(var_211, var_204);
                var_213 = wp::mul(var_212, var_204);
                var_214 = wp::sub(var_211, var_213);
                var_215 = wp::length(var_214);
                var_216 = 0.0;
                var_217 = wp::vec_t<3, wp::float64>(var_216);
                // if speed>wp.float64(1e-30):fr=-wp.float64(.2)*fn*wp.tanh(speed/wp.float64(.001))*tan/speed       <L 74>
                var_218 = 1e-30;
                var_219 = (var_215 > var_218);
                if (var_219) {
                    var_220 = 0.2;
                    var_221 = wp::neg(var_220);
                    var_222 = wp::mul(var_221, var_210);
                    var_223 = 0.001;
                    var_224 = wp::div(var_215, var_223);
                    var_225 = wp::tanh(var_224);
                    var_226 = wp::mul(var_222, var_225);
                    var_227 = wp::mul(var_226, var_214);
                    var_228 = wp::div(var_227, var_215);
                }
                var_229 = wp::where(var_219, var_228, var_217);
                // f=fn*normal+fr                                                                 <L 75>
                var_230 = wp::mul(var_210, var_204);
                var_231 = wp::add(var_230, var_229);
                // for u in range(3):                                                             <L 76>
                // for a in range(3):forces[u,a]+=bary[u]*f[a]                                    <L 77>
                var_234 = wp::extract(var_189, var_232);
                var_235 = wp::extract(var_231, var_233);
                var_236 = wp::mul(var_234, var_235);
                wp::add_inplace(var_68, var_232, var_233, var_236);
                var_238 = wp::extract(var_189, var_232);
                var_239 = wp::extract(var_231, var_237);
                var_240 = wp::mul(var_238, var_239);
                wp::add_inplace(var_68, var_232, var_237, var_240);
                var_242 = wp::extract(var_189, var_232);
                var_243 = wp::extract(var_231, var_241);
                var_244 = wp::mul(var_242, var_243);
                wp::add_inplace(var_68, var_232, var_241, var_244);
                var_247 = wp::extract(var_189, var_245);
                var_248 = wp::extract(var_231, var_246);
                var_249 = wp::mul(var_247, var_248);
                wp::add_inplace(var_68, var_245, var_246, var_249);
                var_251 = wp::extract(var_189, var_245);
                var_252 = wp::extract(var_231, var_250);
                var_253 = wp::mul(var_251, var_252);
                wp::add_inplace(var_68, var_245, var_250, var_253);
                var_255 = wp::extract(var_189, var_245);
                var_256 = wp::extract(var_231, var_254);
                var_257 = wp::mul(var_255, var_256);
                wp::add_inplace(var_68, var_245, var_254, var_257);
                var_260 = wp::extract(var_189, var_258);
                var_261 = wp::extract(var_231, var_259);
                var_262 = wp::mul(var_260, var_261);
                wp::add_inplace(var_68, var_258, var_259, var_262);
                var_264 = wp::extract(var_189, var_258);
                var_265 = wp::extract(var_231, var_263);
                var_266 = wp::mul(var_264, var_265);
                wp::add_inplace(var_68, var_258, var_263, var_266);
                var_268 = wp::extract(var_189, var_258);
                var_269 = wp::extract(var_231, var_267);
                var_270 = wp::mul(var_268, var_269);
                wp::add_inplace(var_68, var_258, var_267, var_270);
                // U+=wp.float64(.5)*fn*depth;D-=wp.dot(fr,rel);W+=wp.dot(f,tv);M+=wp.cross(p-T,f)       <L 78>
                var_271 = 0.5;
                var_272 = wp::mul(var_271, var_210);
                var_273 = wp::mul(var_272, var_202);
                var_274 = wp::add(var_170, var_273);
                var_275 = wp::dot(var_229, var_211);
                var_276 = wp::sub(var_172, var_275);
                var_277 = wp::dot(var_231, var_65);
                var_278 = wp::add(var_174, var_277);
                var_279 = wp::sub(var_191, var_61);
                var_280 = wp::cross(var_279, var_231);
                var_281 = wp::add(var_177, var_280);
                // rule=wp.vec3d(wp.float64(1./6.));rule[k]=wp.float64(2./3.);bary=wp.transpose(B)*rule;p=wp.transpose(x)*bary;vel=wp.transpose(v)*bary;s=signed(mesh,tri,wp.transpose(R)*(p-T));depth=wp.max(-s.phi,wp.float64(0.));normal=R*s.normal;fn=wp.float64(1e9)*area/wp.float64(3.)*depth;rel=vel-tv;tan=rel-wp.dot(rel,normal)*normal;speed=wp.length(tan);fr=wp.vec3d(wp.float64(0.))       <L 73>
                var_285 = wp::div(var_283, var_284);
                var_286 = wp::float64(var_285);
                var_287 = wp::vec_t<3, wp::float64>(var_286);
                var_290 = wp::div(var_288, var_289);
                var_291 = wp::float64(var_290);
                wp::assign_inplace(var_287, var_282, var_291);
                var_292 = wp::transpose(var_51);
                var_293 = wp::mul(var_292, var_287);
                var_294 = wp::transpose(var_54);
                var_295 = wp::mul(var_294, var_293);
                var_296 = wp::transpose(var_57);
                var_297 = wp::mul(var_296, var_293);
                var_298 = wp::transpose(var_R);
                var_299 = wp::sub(var_295, var_61);
                var_300 = wp::mul(var_298, var_299);
                var_301 = signed_1(var_mesh, var_tri, var_300);
                var_302 = &((var_301).phi);
                var_304 = wp::load(var_302);
                var_303 = wp::neg(var_304);
                var_305 = 0.0;
                var_306 = wp::max(var_303, var_305);
                var_307 = &((var_301).normal);
                var_309 = wp::load(var_307);
                var_308 = wp::mul(var_R, var_309);
                var_310 = 1000000000.0;
                var_311 = wp::mul(var_310, var_49);
                var_312 = 3.0;
                var_313 = wp::div(var_311, var_312);
                var_314 = wp::mul(var_313, var_306);
                var_315 = wp::sub(var_297, var_65);
                var_316 = wp::dot(var_315, var_308);
                var_317 = wp::mul(var_316, var_308);
                var_318 = wp::sub(var_315, var_317);
                var_319 = wp::length(var_318);
                var_320 = 0.0;
                var_321 = wp::vec_t<3, wp::float64>(var_320);
                // if speed>wp.float64(1e-30):fr=-wp.float64(.2)*fn*wp.tanh(speed/wp.float64(.001))*tan/speed       <L 74>
                var_322 = 1e-30;
                var_323 = (var_319 > var_322);
                if (var_323) {
                    var_324 = 0.2;
                    var_325 = wp::neg(var_324);
                    var_326 = wp::mul(var_325, var_314);
                    var_327 = 0.001;
                    var_328 = wp::div(var_319, var_327);
                    var_329 = wp::tanh(var_328);
                    var_330 = wp::mul(var_326, var_329);
                    var_331 = wp::mul(var_330, var_318);
                    var_332 = wp::div(var_331, var_319);
                }
                var_333 = wp::where(var_323, var_332, var_321);
                // f=fn*normal+fr                                                                 <L 75>
                var_334 = wp::mul(var_314, var_308);
                var_335 = wp::add(var_334, var_333);
                // for u in range(3):                                                             <L 76>
                // for a in range(3):forces[u,a]+=bary[u]*f[a]                                    <L 77>
                var_338 = wp::extract(var_293, var_336);
                var_339 = wp::extract(var_335, var_337);
                var_340 = wp::mul(var_338, var_339);
                wp::add_inplace(var_68, var_336, var_337, var_340);
                var_342 = wp::extract(var_293, var_336);
                var_343 = wp::extract(var_335, var_341);
                var_344 = wp::mul(var_342, var_343);
                wp::add_inplace(var_68, var_336, var_341, var_344);
                var_346 = wp::extract(var_293, var_336);
                var_347 = wp::extract(var_335, var_345);
                var_348 = wp::mul(var_346, var_347);
                wp::add_inplace(var_68, var_336, var_345, var_348);
                var_351 = wp::extract(var_293, var_349);
                var_352 = wp::extract(var_335, var_350);
                var_353 = wp::mul(var_351, var_352);
                wp::add_inplace(var_68, var_349, var_350, var_353);
                var_355 = wp::extract(var_293, var_349);
                var_356 = wp::extract(var_335, var_354);
                var_357 = wp::mul(var_355, var_356);
                wp::add_inplace(var_68, var_349, var_354, var_357);
                var_359 = wp::extract(var_293, var_349);
                var_360 = wp::extract(var_335, var_358);
                var_361 = wp::mul(var_359, var_360);
                wp::add_inplace(var_68, var_349, var_358, var_361);
                var_364 = wp::extract(var_293, var_362);
                var_365 = wp::extract(var_335, var_363);
                var_366 = wp::mul(var_364, var_365);
                wp::add_inplace(var_68, var_362, var_363, var_366);
                var_368 = wp::extract(var_293, var_362);
                var_369 = wp::extract(var_335, var_367);
                var_370 = wp::mul(var_368, var_369);
                wp::add_inplace(var_68, var_362, var_367, var_370);
                var_372 = wp::extract(var_293, var_362);
                var_373 = wp::extract(var_335, var_371);
                var_374 = wp::mul(var_372, var_373);
                wp::add_inplace(var_68, var_362, var_371, var_374);
                // U+=wp.float64(.5)*fn*depth;D-=wp.dot(fr,rel);W+=wp.dot(f,tv);M+=wp.cross(p-T,f)       <L 78>
                var_375 = 0.5;
                var_376 = wp::mul(var_375, var_314);
                var_377 = wp::mul(var_376, var_306);
                var_378 = wp::add(var_274, var_377);
                var_379 = wp::dot(var_333, var_315);
                var_380 = wp::sub(var_276, var_379);
                var_381 = wp::dot(var_335, var_65);
                var_382 = wp::add(var_278, var_381);
                var_383 = wp::sub(var_295, var_61);
                var_384 = wp::cross(var_383, var_335);
                var_385 = wp::add(var_281, var_384);
                // for u in range(3):wp.atomic_add(ff,face,u,forces[u])                           <L 79>
                var_387 = wp::extract(var_68, var_386);
                var_388 = wp::atomic_add(var_ff, var_23, var_386, var_387);
                var_390 = wp::extract(var_68, var_389);
                var_391 = wp::atomic_add(var_ff, var_23, var_389, var_390);
                var_393 = wp::extract(var_68, var_392);
                var_394 = wp::atomic_add(var_ff, var_23, var_392, var_393);
                // wp.atomic_add(uu,face,U);wp.atomic_add(dd,face,D);wp.atomic_add(ww,face,W);wp.atomic_add(mm,face,M)       <L 80>
                var_395 = wp::atomic_add(var_uu, var_23, var_378);
                var_396 = wp::atomic_add(var_dd, var_23, var_380);
                var_397 = wp::atomic_add(var_ww, var_23, var_382);
                var_398 = wp::atomic_add(var_mm, var_23, var_385);
            }
        }
    }
}



extern "C" __global__ void active_faces_b2e2de07_cuda_kernel_forward(
    wp::launch_bounds_t<1> dim,
    wp::array_t<wp::mat_t<3, 3, wp::float64>> var_local,
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
        wp::mat_t<3, 3, wp::float64>* var_1;
        wp::mat_t<3, 3, wp::float64> var_2;
        wp::mat_t<3, 3, wp::float64> var_3;
        const bool var_4 = true;
        const wp::int32 var_5 = 0;
        const wp::int32 var_6 = 0;
        wp::float64 var_7;
        const wp::int32 var_8 = 1;
        wp::float64 var_9;
        const wp::int32 var_10 = 2;
        wp::float64 var_11;
        wp::float64 var_12;
        wp::float64 var_13;
        const wp::int32 var_14 = 0;
        wp::float64 var_15;
        const wp::int32 var_16 = 1;
        wp::float64 var_17;
        const wp::int32 var_18 = 2;
        wp::float64 var_19;
        wp::float64 var_20;
        wp::float64 var_21;
        bool var_22;
        wp::float64 var_23;
        bool var_24;
        wp::float64 var_25;
        bool var_26;
        const bool var_27 = false;
        bool var_28;
        const wp::int32 var_29 = 1;
        const wp::int32 var_30 = 0;
        wp::float64 var_31;
        const wp::int32 var_32 = 1;
        wp::float64 var_33;
        const wp::int32 var_34 = 2;
        wp::float64 var_35;
        wp::float64 var_36;
        wp::float64 var_37;
        const wp::int32 var_38 = 0;
        wp::float64 var_39;
        const wp::int32 var_40 = 1;
        wp::float64 var_41;
        const wp::int32 var_42 = 2;
        wp::float64 var_43;
        wp::float64 var_44;
        wp::float64 var_45;
        bool var_46;
        wp::float64 var_47;
        bool var_48;
        wp::float64 var_49;
        bool var_50;
        const bool var_51 = false;
        bool var_52;
        const wp::int32 var_53 = 2;
        const wp::int32 var_54 = 0;
        wp::float64 var_55;
        const wp::int32 var_56 = 1;
        wp::float64 var_57;
        const wp::int32 var_58 = 2;
        wp::float64 var_59;
        wp::float64 var_60;
        wp::float64 var_61;
        const wp::int32 var_62 = 0;
        wp::float64 var_63;
        const wp::int32 var_64 = 1;
        wp::float64 var_65;
        const wp::int32 var_66 = 2;
        wp::float64 var_67;
        wp::float64 var_68;
        wp::float64 var_69;
        bool var_70;
        wp::float64 var_71;
        bool var_72;
        wp::float64 var_73;
        bool var_74;
        const bool var_75 = false;
        bool var_76;
        bool var_77;
        const wp::int32 var_78 = 0;
        wp::int32* var_79;
        const wp::int32 var_80 = 0;
        bool var_81;
        wp::int32 var_82;
        const wp::int32 var_83 = 0;
        const wp::int32 var_84 = 1;
        wp::int32 var_85;
        wp::shape_t* var_86;
        const wp::int32 var_87 = 0;
        wp::int32 var_88;
        wp::shape_t var_89;
        bool var_90;
        const wp::int32 var_91 = 0;
        const wp::int32 var_92 = 5;
        wp::int32 var_93;
        //---------
        // forward
        // def active_faces(local:wp.array(dtype=wp.mat33d),lo:wp.vec3d,hi:wp.vec3d,count:wp.array(dtype=int),ids:wp.array(dtype=int),bad:wp.array(dtype=int)):       <L 15>
        // face=wp.tid();x=local[face];overlap=True                                               <L 16>
        var_0 = builtin_tid1d();
        var_1 = wp::address(var_local, var_0);
        var_3 = wp::load(var_1);
        var_2 = wp::copy(var_3);
        // for axis in range(3):                                                                  <L 17>
        // a=wp.min(x[0,axis],wp.min(x[1,axis],x[2,axis]));b=wp.max(x[0,axis],wp.max(x[1,axis],x[2,axis]))       <L 18>
        var_7 = wp::extract(var_2, var_6, var_5);
        var_9 = wp::extract(var_2, var_8, var_5);
        var_11 = wp::extract(var_2, var_10, var_5);
        var_12 = wp::min(var_9, var_11);
        var_13 = wp::min(var_7, var_12);
        var_15 = wp::extract(var_2, var_14, var_5);
        var_17 = wp::extract(var_2, var_16, var_5);
        var_19 = wp::extract(var_2, var_18, var_5);
        var_20 = wp::max(var_17, var_19);
        var_21 = wp::max(var_15, var_20);
        // if b<lo[axis] or a>hi[axis]:overlap=False                                              <L 19>
        var_23 = wp::extract(var_lo, var_5);
        var_24 = (var_21 < var_23);
        var_22 = var_24;
        if (!var_22) {
            var_25 = wp::extract(var_hi, var_5);
            var_26 = (var_13 > var_25);
            var_22 = var_22 || var_26;
        }
        if (var_22) {
        }
        var_28 = wp::where(var_22, var_27, var_4);
        // a=wp.min(x[0,axis],wp.min(x[1,axis],x[2,axis]));b=wp.max(x[0,axis],wp.max(x[1,axis],x[2,axis]))       <L 18>
        var_31 = wp::extract(var_2, var_30, var_29);
        var_33 = wp::extract(var_2, var_32, var_29);
        var_35 = wp::extract(var_2, var_34, var_29);
        var_36 = wp::min(var_33, var_35);
        var_37 = wp::min(var_31, var_36);
        var_39 = wp::extract(var_2, var_38, var_29);
        var_41 = wp::extract(var_2, var_40, var_29);
        var_43 = wp::extract(var_2, var_42, var_29);
        var_44 = wp::max(var_41, var_43);
        var_45 = wp::max(var_39, var_44);
        // if b<lo[axis] or a>hi[axis]:overlap=False                                              <L 19>
        var_47 = wp::extract(var_lo, var_29);
        var_48 = (var_45 < var_47);
        var_46 = var_48;
        if (!var_46) {
            var_49 = wp::extract(var_hi, var_29);
            var_50 = (var_37 > var_49);
            var_46 = var_46 || var_50;
        }
        if (var_46) {
        }
        var_52 = wp::where(var_46, var_51, var_28);
        // a=wp.min(x[0,axis],wp.min(x[1,axis],x[2,axis]));b=wp.max(x[0,axis],wp.max(x[1,axis],x[2,axis]))       <L 18>
        var_55 = wp::extract(var_2, var_54, var_53);
        var_57 = wp::extract(var_2, var_56, var_53);
        var_59 = wp::extract(var_2, var_58, var_53);
        var_60 = wp::min(var_57, var_59);
        var_61 = wp::min(var_55, var_60);
        var_63 = wp::extract(var_2, var_62, var_53);
        var_65 = wp::extract(var_2, var_64, var_53);
        var_67 = wp::extract(var_2, var_66, var_53);
        var_68 = wp::max(var_65, var_67);
        var_69 = wp::max(var_63, var_68);
        // if b<lo[axis] or a>hi[axis]:overlap=False                                              <L 19>
        var_71 = wp::extract(var_lo, var_53);
        var_72 = (var_69 < var_71);
        var_70 = var_72;
        if (!var_70) {
            var_73 = wp::extract(var_hi, var_53);
            var_74 = (var_61 > var_73);
            var_70 = var_70 || var_74;
        }
        if (var_70) {
        }
        var_76 = wp::where(var_70, var_75, var_52);
        // if overlap and bad[0]==0:                                                              <L 20>
        var_77 = var_76;
        if (var_77) {
            var_79 = wp::address(var_bad, var_78);
            var_82 = wp::load(var_79);
            var_81 = (var_82 == var_80);
            var_77 = var_77 && var_81;
        }
        if (var_77) {
            // index=wp.atomic_add(count,0,1)                                                     <L 21>
            var_85 = wp::atomic_add(var_count, var_83, var_84);
            // if index>=ids.shape[0]:wp.atomic_max(bad,0,5)                                      <L 22>
            var_86 = &(var_ids.shape);
            var_89 = wp::load(var_86);
            var_88 = wp::extract(var_89, var_87);
            var_90 = (var_85 >= var_88);
            if (var_90) {
                var_93 = wp::atomic_max(var_bad, var_91, var_92);
            }
            if (!var_90) {
                // else:ids[index]=face                                                           <L 23>
                wp::array_store(var_ids, var_85, var_0);
            }
        }
    }
}



extern "C" __global__ void clip_pairs_e32e9a85_cuda_kernel_forward(
    wp::launch_bounds_t<1> dim,
    wp::array_t<wp::mat_t<3, 3, wp::float64>> var_local,
    wp::array_t<wp::vec_t<4, wp::float64>> var_planes,
    wp::int32 var_ncells,
    wp::array_t<wp::int32> var_count,
    wp::array_t<wp::int32> var_pairs,
    wp::array_t<wp::int32> var_active,
    wp::array_t<wp::int32> var_faces,
    wp::array_t<wp::int32> var_counts,
    wp::array_t<wp::vec_t<3, wp::float64>> var_polygon,
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
        wp::int32 var_14;
        wp::int32 var_15;
        wp::mat_t<3, 3, wp::float64>* var_16;
        wp::mat_t<3, 3, wp::float64> var_17;
        wp::mat_t<3, 3, wp::float64> var_18;
        wp::float64 var_19;
        wp::mat_t<10, 3, wp::float64> var_20;
        wp::float64 var_21;
        const wp::int32 var_22 = 0;
        const wp::int32 var_23 = 0;
        wp::float64 var_24;
        const wp::int32 var_25 = 1;
        const wp::int32 var_26 = 1;
        wp::float64 var_27;
        const wp::int32 var_28 = 2;
        const wp::int32 var_29 = 2;
        const wp::int32 var_30 = 3;
        wp::int32 var_31;
        const wp::int32 var_32 = 4;
        wp::range_t var_33;
        wp::int32 var_34;
        wp::vec_t<4, wp::float64>* var_35;
        wp::vec_t<4, wp::float64> var_36;
        wp::vec_t<4, wp::float64> var_37;
        const wp::int32 var_38 = 0;
        wp::float64 var_39;
        const wp::int32 var_40 = 1;
        wp::float64 var_41;
        const wp::int32 var_42 = 2;
        wp::float64 var_43;
        wp::vec_t<3, wp::float64> var_44;
        wp::vec_t<3, wp::float64> var_45;
        const wp::int32 var_46 = 3;
        wp::float64 var_47;
        wp::vec_t<3, wp::float64> var_48;
        wp::vec_t<3, wp::float64> var_49;
        wp::float64 var_50;
        wp::mat_t<10, 3, wp::float64> var_51;
        const wp::int32 var_52 = 0;
        wp::int32 var_53;
        wp::range_t var_54;
        wp::int32 var_55;
        wp::vec_t<3, wp::float64> var_56;
        const wp::int32 var_57 = 1;
        wp::int32 var_58;
        wp::int32 var_59;
        wp::vec_t<3, wp::float64> var_60;
        wp::float64 var_61;
        wp::float64 var_62;
        wp::float64 var_63;
        bool var_64;
        const wp::int32 var_65 = 10;
        bool var_66;
        const wp::int32 var_67 = 0;
        const wp::int32 var_68 = 6;
        wp::int32 var_69;
        const wp::int32 var_70 = 1;
        wp::int32 var_71;
        wp::int32 var_72;
        wp::int32 var_73;
        bool var_74;
        bool var_75;
        wp::float64 var_76;
        bool var_77;
        wp::float64 var_78;
        bool var_79;
        bool var_80;
        wp::float64 var_81;
        bool var_82;
        wp::float64 var_83;
        bool var_84;
        const wp::int32 var_85 = 10;
        bool var_86;
        const wp::int32 var_87 = 0;
        const wp::int32 var_88 = 6;
        wp::int32 var_89;
        wp::float64 var_90;
        wp::float64 var_91;
        wp::vec_t<3, wp::float64> var_92;
        wp::vec_t<3, wp::float64> var_93;
        wp::vec_t<3, wp::float64> var_94;
        const wp::int32 var_95 = 1;
        wp::int32 var_96;
        wp::int32 var_97;
        wp::int32 var_98;
        wp::mat_t<10, 3, wp::float64> var_99;
        wp::int32 var_100;
        const wp::int32 var_101 = 3;
        bool var_102;
        wp::mat_t<10, 3, wp::float64> var_103;
        wp::int32 var_104;
        bool var_105;
        const wp::int32 var_106 = 3;
        bool var_107;
        const wp::int32 var_108 = 0;
        wp::int32* var_109;
        const wp::int32 var_110 = 0;
        bool var_111;
        wp::int32 var_112;
        wp::float64 var_113;
        const wp::int32 var_114 = 1;
        wp::int32 var_115;
        const wp::int32 var_116 = 1;
        wp::range_t var_117;
        wp::int32 var_118;
        const wp::int32 var_119 = 0;
        wp::vec_t<3, wp::float64> var_120;
        wp::vec_t<3, wp::float64> var_121;
        const wp::int32 var_122 = 1;
        wp::int32 var_123;
        wp::vec_t<3, wp::float64> var_124;
        wp::mat_t<3, 3, wp::float64> var_125;
        wp::float64 var_126;
        wp::float64 var_127;
        wp::float64 var_128;
        wp::float64 var_129;
        bool var_130;
        const wp::int32 var_131 = 0;
        const wp::int32 var_132 = 1;
        wp::int32 var_133;
        wp::shape_t* var_134;
        const wp::int32 var_135 = 0;
        wp::int32 var_136;
        wp::shape_t var_137;
        bool var_138;
        const wp::int32 var_139 = 0;
        const wp::int32 var_140 = 5;
        wp::int32 var_141;
        wp::range_t var_142;
        wp::int32 var_143;
        wp::vec_t<3, wp::float64> var_144;
        wp::int32 var_145;
        wp::int32 var_146;
        wp::int32 var_147;
        //---------
        // forward
        // def clip_pairs(local:wp.array(dtype=wp.mat33d),planes:wp.array2d(dtype=wp.vec4d),ncells:int,count:wp.array(dtype=int),pairs:wp.array(dtype=int),active:wp.array(dtype=int),faces:wp.array(dtype=int),counts:wp.array(dtype=int),polygon:wp.array2d(dtype=wp.vec3d),bad:wp.array(dtype=int)):       <L 39>
        // item=wp.tid()                                                                          <L 40>
        var_0 = builtin_tid1d();
        // if item<count[0] and bad[0]==0:                                                        <L 41>
        var_3 = wp::address(var_count, var_2);
        var_5 = wp::load(var_3);
        var_4 = (var_0 < var_5);
        var_1 = var_4;
        if (var_1) {
            var_7 = wp::address(var_bad, var_6);
            var_10 = wp::load(var_7);
            var_9 = (var_10 == var_8);
            var_1 = var_1 && var_9;
        }
        if (var_1) {
            // pair=pairs[item];face=pair//ncells;cell=pair%ncells;x=local[face];poly=Poly(wp.float64(0.));poly[0,0]=wp.float64(1.);poly[1,1]=wp.float64(1.);poly[2,2]=wp.float64(1.);n=int(3)       <L 42>
            var_11 = wp::address(var_pairs, var_0);
            var_13 = wp::load(var_11);
            var_12 = wp::copy(var_13);
            var_14 = wp::floordiv(var_12, var_ncells);
            var_15 = wp::mod(var_12, var_ncells);
            var_16 = wp::address(var_local, var_14);
            var_18 = wp::load(var_16);
            var_17 = wp::copy(var_18);
            var_19 = 0.0;
            var_20 = wp::mat_t<10, 3, wp::float64>(var_19);
            var_21 = 1.0;
            wp::assign_inplace(var_20, var_22, var_23, var_21);
            var_24 = 1.0;
            wp::assign_inplace(var_20, var_25, var_26, var_24);
            var_27 = 1.0;
            wp::assign_inplace(var_20, var_28, var_29, var_27);
            var_31 = wp::int(var_30);
            // for h in range(4):                                                                 <L 43>
            var_33 = wp::range(var_32);
            start_for_0:;
                if (iter_cmp(var_33) == 0) goto end_for_0;
                var_34 = wp::iter_next(var_33);
                // plane=planes[cell,h];distance=x*wp.vec3d(plane[0],plane[1],plane[2])+wp.vec3d(plane[3]);out=Poly(wp.float64(0.));new=int(0)       <L 44>
                var_35 = wp::address(var_planes, var_15, var_34);
                var_37 = wp::load(var_35);
                var_36 = wp::copy(var_37);
                var_39 = wp::extract(var_36, var_38);
                var_41 = wp::extract(var_36, var_40);
                var_43 = wp::extract(var_36, var_42);
                var_44 = wp::vec_t<3, wp::float64>(var_39, var_41, var_43);
                var_45 = wp::mul(var_17, var_44);
                var_47 = wp::extract(var_36, var_46);
                var_48 = wp::vec_t<3, wp::float64>(var_47);
                var_49 = wp::add(var_45, var_48);
                var_50 = 0.0;
                var_51 = wp::mat_t<10, 3, wp::float64>(var_50);
                var_53 = wp::int(var_52);
                // for k in range(n):                                                             <L 45>
                var_54 = wp::range(var_31);
                start_for_2:;
                    if (iter_cmp(var_54) == 0) goto end_for_2;
                    var_55 = wp::iter_next(var_54);
                    // p0=poly[k];p1=poly[(k+1)%n];d0=wp.dot(p0,distance);d1=wp.dot(p1,distance)       <L 46>
                    var_56 = wp::extract(var_20, var_55);
                    var_58 = wp::add(var_55, var_57);
                    var_59 = wp::mod(var_58, var_31);
                    var_60 = wp::extract(var_20, var_59);
                    var_61 = wp::dot(var_56, var_49);
                    var_62 = wp::dot(var_60, var_49);
                    // if d0<=wp.float64(0.):                                                     <L 47>
                    var_63 = 0.0;
                    var_64 = (var_61 <= var_63);
                    if (var_64) {
                        // if new>=10:wp.atomic_max(bad,0,6)                                      <L 48>
                        var_66 = (var_53 >= var_65);
                        if (var_66) {
                            var_69 = wp::atomic_max(var_bad, var_67, var_68);
                        }
                        if (!var_66) {
                            // else:out[new]=p0;new+=1                                            <L 49>
                            wp::assign_inplace(var_51, var_53, var_56);
                            var_71 = wp::add(var_53, var_70);
                        }
                        var_72 = wp::where(var_66, var_53, var_71);
                    }
                    var_73 = wp::where(var_64, var_72, var_53);
                    // if (d0<wp.float64(0.) and d1>wp.float64(0.)) or (d1<wp.float64(0.) and d0>wp.float64(0.)):       <L 50>
                    var_76 = 0.0;
                    var_77 = (var_61 < var_76);
                    var_75 = var_77;
                    if (var_75) {
                        var_78 = 0.0;
                        var_79 = (var_62 > var_78);
                        var_75 = var_75 && var_79;
                    }
                    var_74 = var_75;
                    if (!var_74) {
                        var_81 = 0.0;
                        var_82 = (var_62 < var_81);
                        var_80 = var_82;
                        if (var_80) {
                            var_83 = 0.0;
                            var_84 = (var_61 > var_83);
                            var_80 = var_80 && var_84;
                        }
                        var_74 = var_74 || var_80;
                    }
                    if (var_74) {
                        // if new>=10:wp.atomic_max(bad,0,6)                                      <L 51>
                        var_86 = (var_73 >= var_85);
                        if (var_86) {
                            var_89 = wp::atomic_max(var_bad, var_87, var_88);
                        }
                        if (!var_86) {
                            // else:out[new]=p0+d0/(d0-d1)*(p1-p0);new+=1                         <L 52>
                            var_90 = wp::sub(var_61, var_62);
                            var_91 = wp::div(var_61, var_90);
                            var_92 = wp::sub(var_60, var_56);
                            var_93 = wp::mul(var_91, var_92);
                            var_94 = wp::add(var_56, var_93);
                            wp::assign_inplace(var_51, var_73, var_94);
                            var_96 = wp::add(var_73, var_95);
                        }
                        var_97 = wp::where(var_86, var_73, var_96);
                    }
                    var_98 = wp::where(var_74, var_97, var_73);
                    wp::assign(var_53, var_98);
                    goto start_for_2;
                end_for_2:;
                // poly=out;n=new                                                                 <L 53>
                var_99 = wp::copy(var_51);
                var_100 = wp::copy(var_53);
                // if n<3:break                                                                   <L 54>
                var_102 = (var_100 < var_101);
                if (var_102) {
                    wp::assign(var_20, var_99);
                    wp::assign(var_31, var_100);
                    goto end_for_0;
                }
                var_103 = wp::where(var_102, var_20, var_99);
                var_104 = wp::where(var_102, var_31, var_100);
                wp::assign(var_20, var_103);
                wp::assign(var_31, var_104);
                goto start_for_0;
            end_for_0:;
            // if n>=3 and bad[0]==0:                                                             <L 55>
            var_107 = (var_31 >= var_106);
            var_105 = var_107;
            if (var_105) {
                var_109 = wp::address(var_bad, var_108);
                var_112 = wp::load(var_109);
                var_111 = (var_112 == var_110);
                var_105 = var_105 && var_111;
            }
            if (var_105) {
                // area=wp.float64(0.)                                                            <L 56>
                var_113 = 0.0;
                // for k in range(1,n-1):area+=wp.abs(wp.determinant(wp.matrix_from_rows(poly[0],poly[k],poly[k+1])))       <L 57>
                var_115 = wp::sub(var_31, var_114);
                var_117 = wp::range(var_116, var_115);
                start_for_4:;
                    if (iter_cmp(var_117) == 0) goto end_for_4;
                    var_118 = wp::iter_next(var_117);
                    var_120 = wp::extract(var_20, var_119);
                    var_121 = wp::extract(var_20, var_118);
                    var_123 = wp::add(var_118, var_122);
                    var_124 = wp::extract(var_20, var_123);
                    var_125 = wp::matrix_from_rows<wp::float64>(var_120, var_121, var_124);
                    var_126 = wp::determinant(var_125);
                    var_127 = wp::abs(var_126);
                    var_128 = wp::add(var_113, var_127);
                    wp::assign(var_113, var_128);
                    goto start_for_4;
                end_for_4:;
                // if area>wp.float64(1e-30):                                                     <L 58>
                var_129 = 1e-30;
                var_130 = (var_113 > var_129);
                if (var_130) {
                    // slot=wp.atomic_add(active,0,1)                                             <L 59>
                    var_133 = wp::atomic_add(var_active, var_131, var_132);
                    // if slot>=faces.shape[0]:wp.atomic_max(bad,0,5)                             <L 60>
                    var_134 = &(var_faces.shape);
                    var_137 = wp::load(var_134);
                    var_136 = wp::extract(var_137, var_135);
                    var_138 = (var_133 >= var_136);
                    if (var_138) {
                        var_141 = wp::atomic_max(var_bad, var_139, var_140);
                    }
                    if (!var_138) {
                        // faces[slot]=face;counts[slot]=n                                        <L 62>
                        wp::array_store(var_faces, var_133, var_14);
                        wp::array_store(var_counts, var_133, var_31);
                        // for k in range(n):polygon[slot,k]=poly[k]                              <L 63>
                        var_142 = wp::range(var_31);
                        start_for_6:;
                            if (iter_cmp(var_142) == 0) goto end_for_6;
                            var_143 = wp::iter_next(var_142);
                            var_144 = wp::extract(var_20, var_143);
                            wp::array_store(var_polygon, var_133, var_143, var_144);
                            goto start_for_6;
                        end_for_6:;
                    }
                    var_145 = wp::where(var_138, var_118, var_143);
                }
                var_146 = wp::where(var_130, var_145, var_118);
            }
            var_147 = wp::where(var_105, var_146, var_55);
        }
    }
}


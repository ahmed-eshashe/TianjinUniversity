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


struct Value_53a65c4a
{
    wp::mat_t<3, 3, wp::float64> f;
    wp::float64 U;
    wp::float64 D;
    wp::float64 W;
    wp::vec_t<3, wp::float64> moment;
    wp::float64 error;
    wp::int32 queries;


    Value_53a65c4a() = default;
    CUDA_CALLABLE Value_53a65c4a(wp::mat_t<3, 3, wp::float64> const& f,
    wp::float64 const& U = {},
    wp::float64 const& D = {},
    wp::float64 const& W = {},
    wp::vec_t<3, wp::float64> const& moment = {},
    wp::float64 const& error = {},
    wp::int32 const& queries = {})
        : f{f}
        , U{U}
        , D{D}
        , W{W}
        , moment{moment}
        , error{error}
        , queries{queries}

    {
    }

    CUDA_CALLABLE Value_53a65c4a& operator += (const Value_53a65c4a& rhs)
    {    f += rhs.f;
    U += rhs.U;
    D += rhs.D;
    W += rhs.W;
    moment += rhs.moment;
    error += rhs.error;
    queries += rhs.queries;

        return *this;}

};

static CUDA_CALLABLE void adj_Value_53a65c4a(wp::mat_t<3, 3, wp::float64> const&,
    wp::float64 const&,
    wp::float64 const&,
    wp::float64 const&,
    wp::vec_t<3, wp::float64> const&,
    wp::float64 const&,
    wp::int32 const&,
    wp::mat_t<3, 3, wp::float64> & adj_f,
    wp::float64 & adj_U,
    wp::float64 & adj_D,
    wp::float64 & adj_W,
    wp::vec_t<3, wp::float64> & adj_moment,
    wp::float64 & adj_error,
    wp::int32 & adj_queries,
    Value_53a65c4a & adj_ret)
{
    adj_f += adj_ret.f;
    adj_U += adj_ret.U;
    adj_D += adj_ret.D;
    adj_W += adj_ret.W;
    adj_moment += adj_ret.moment;
    adj_error += adj_ret.error;
    adj_queries += adj_ret.queries;
}

// Required when compiling adjoints.
CUDA_CALLABLE Value_53a65c4a add(const Value_53a65c4a& a, const Value_53a65c4a& b)
{
    return Value_53a65c4a();
}

CUDA_CALLABLE void adj_atomic_add(Value_53a65c4a* p, Value_53a65c4a t)
{
    wp::adj_atomic_add(&p->f, t.f);
    wp::adj_atomic_add(&p->U, t.U);
    wp::adj_atomic_add(&p->D, t.D);
    wp::adj_atomic_add(&p->W, t.W);
    wp::adj_atomic_add(&p->moment, t.moment);
    wp::adj_atomic_add(&p->error, t.error);
    wp::adj_atomic_add(&p->queries, t.queries);
}




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


// /home/omen/Documents/Codex/experiments/tomato_adaptive_contact_20261112_v24/src/allocated_gpu.py:25
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
    // def signed(mesh:wp.uint64,tri:wp.array2d(dtype=wp.vec3d),p:wp.vec3d):                  <L 26>
    // r=Signed();r.phi=wp.float64(100.);r.normal=wp.vec3d(wp.float64(0.));q=wp.mesh_query_point_sign_winding_number(mesh,wp.vec3(p),10.)       <L 27>
    var_0 = Signed_7e3cff60();
    var_1 = 100.0;
    var_0.phi = var_1;
    var_2 = 0.0;
    var_3 = wp::vec_t<3, wp::float64>(var_2);
    var_0.normal = var_3;
    var_4 = wp::vec_t<3, wp::float32>(var_p);
    var_6 = wp::mesh_query_point_sign_winding_number(var_mesh, var_4, var_5, var_7, var_8);
    // if q.result:                                                                           <L 28>
    var_9 = &((var_6).result);
    var_10 = wp::load(var_9);
    if (var_10) {
        // c=closest(p,tri[q.face,0],tri[q.face,1],tri[q.face,2]);best=wp.length_sq(p-c);bestface=q.face       <L 29>
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
        // radius=wp.sqrt(best)+wp.float64(2e-7)                                              <L 33>
        var_32 = wp::sqrt(var_28);
        var_33 = 2e-07;
        var_34 = wp::add(var_32, var_33);
        // candidates=wp.mesh_query_aabb(mesh,wp.vec3(p-wp.vec3d(radius)),wp.vec3(p+wp.vec3d(radius)))       <L 34>
        var_35 = wp::vec_t<3, wp::float64>(var_34);
        var_36 = wp::sub(var_p, var_35);
        var_37 = wp::vec_t<3, wp::float32>(var_36);
        var_38 = wp::vec_t<3, wp::float64>(var_34);
        var_39 = wp::add(var_p, var_38);
        var_40 = wp::vec_t<3, wp::float32>(var_39);
        var_41 = wp::mesh_query_aabb(var_mesh, var_37, var_40);
        // for face in candidates:                                                            <L 35>
        start_for_0:;
            if (iter_cmp(var_41) == 0) goto end_for_0;
            var_42 = wp::iter_next(var_41);
            // candidate=closest(p,tri[face,0],tri[face,1],tri[face,2]);dist=wp.length_sq(p-candidate)       <L 36>
            var_44 = wp::address(var_tri, var_42, var_43);
            var_46 = wp::address(var_tri, var_42, var_45);
            var_48 = wp::address(var_tri, var_42, var_47);
            var_50 = wp::load(var_44);
            var_51 = wp::load(var_46);
            var_52 = wp::load(var_48);
            var_49 = closest_0(var_p, var_50, var_51, var_52);
            var_53 = wp::sub(var_p, var_49);
            var_54 = wp::length_sq(var_53);
            // if dist<best or (dist==best and face<bestface):best=dist;c=candidate;bestface=face       <L 37>
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
        // d=p-c;l=wp.sqrt(best);r.phi=wp.float64(q.sign)*l                                   <L 38>
        var_66 = wp::sub(var_p, var_23);
        var_67 = wp::sqrt(var_28);
        var_68 = &((var_6).sign);
        var_70 = wp::load(var_68);
        var_69 = wp::float64(var_70);
        var_71 = wp::mul(var_69, var_67);
        var_0.phi = var_71;
        // if l>wp.float64(1e-15):r.normal=wp.float64(q.sign)*d/l                             <L 39>
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
            // else:r.normal=wp.normalize(wp.cross(tri[bestface,1]-tri[bestface,0],tri[bestface,2]-tri[bestface,0]))       <L 40>
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
    // return r                                                                               <L 41>
    return var_0;
}


// /home/omen/Documents/Codex/experiments/tomato_adaptive_contact_20261112_v24/src/allocated_gpu.py:53
static CUDA_CALLABLE void bisect_0(
    wp::mat_t<3, 3, wp::float64> var_B,
    wp::mat_t<3, 3, wp::float64> var_X,
    wp::mat_t<3, 3, wp::float64> & ret_0,
    wp::mat_t<3, 3, wp::float64> & ret_1)
{
    //---------
    // primal vars
    wp::mat_t<3, 3, wp::float64> var_0;
    const wp::int32 var_1 = 0;
    wp::int32 var_2;
    const wp::int32 var_3 = 1;
    wp::int32 var_4;
    const wp::int32 var_5 = 0;
    wp::vec_t<3, wp::float64> var_6;
    const wp::int32 var_7 = 1;
    wp::vec_t<3, wp::float64> var_8;
    wp::vec_t<3, wp::float64> var_9;
    wp::float64 var_10;
    const wp::int32 var_11 = 0;
    const wp::int32 var_12 = 1;
    wp::int32 var_13;
    const wp::int32 var_14 = 3;
    wp::range_t var_15;
    wp::int32 var_16;
    wp::vec_t<3, wp::float64> var_17;
    wp::vec_t<3, wp::float64> var_18;
    wp::vec_t<3, wp::float64> var_19;
    wp::float64 var_20;
    bool var_21;
    wp::float64 var_22;
    wp::int32 var_23;
    wp::int32 var_24;
    wp::int32 var_25;
    wp::int32 var_26;
    wp::float64 var_27;
    const wp::int32 var_28 = 1;
    const wp::int32 var_29 = 1;
    wp::int32 var_30;
    const wp::int32 var_31 = 3;
    wp::range_t var_32;
    wp::int32 var_33;
    wp::vec_t<3, wp::float64> var_34;
    wp::vec_t<3, wp::float64> var_35;
    wp::vec_t<3, wp::float64> var_36;
    wp::float64 var_37;
    bool var_38;
    wp::float64 var_39;
    wp::int32 var_40;
    wp::int32 var_41;
    wp::int32 var_42;
    wp::int32 var_43;
    wp::float64 var_44;
    const wp::int32 var_45 = 2;
    const wp::int32 var_46 = 1;
    wp::int32 var_47;
    const wp::int32 var_48 = 3;
    wp::range_t var_49;
    wp::int32 var_50;
    wp::vec_t<3, wp::float64> var_51;
    wp::vec_t<3, wp::float64> var_52;
    wp::vec_t<3, wp::float64> var_53;
    wp::float64 var_54;
    bool var_55;
    wp::float64 var_56;
    wp::int32 var_57;
    wp::int32 var_58;
    wp::int32 var_59;
    wp::int32 var_60;
    wp::float64 var_61;
    wp::vec_t<3, wp::float64> var_62;
    wp::vec_t<3, wp::float64> var_63;
    wp::vec_t<3, wp::float64> var_64;
    wp::float64 var_65;
    wp::vec_t<3, wp::float64> var_66;
    wp::mat_t<3, 3, wp::float64> var_67;
    wp::mat_t<3, 3, wp::float64> var_68;
    const wp::int32 var_69 = 0;
    wp::float64 var_70;
    wp::float64 var_71;
    const wp::int32 var_72 = 1;
    wp::float64 var_73;
    wp::float64 var_74;
    const wp::int32 var_75 = 2;
    wp::float64 var_76;
    wp::float64 var_77;
    //---------
    // forward
    // def bisect(B:wp.mat33d,X:wp.mat33d):                                                   <L 54>
    // p=B*X;i=int(0);j=int(1);best=wp.length_sq(p[0]-p[1])                                   <L 55>
    var_0 = wp::mul(var_B, var_X);
    var_2 = wp::int(var_1);
    var_4 = wp::int(var_3);
    var_6 = wp::extract(var_0, var_5);
    var_8 = wp::extract(var_0, var_7);
    var_9 = wp::sub(var_6, var_8);
    var_10 = wp::length_sq(var_9);
    // for u in range(3):                                                                     <L 56>
    // for v in range(u+1,3):                                                                 <L 57>
    var_13 = wp::add(var_11, var_12);
    var_15 = wp::range(var_13, var_14);
    start_for_0:;
        if (iter_cmp(var_15) == 0) goto end_for_0;
        var_16 = wp::iter_next(var_15);
        // d=wp.length_sq(p[u]-p[v])                                                          <L 58>
        var_17 = wp::extract(var_0, var_11);
        var_18 = wp::extract(var_0, var_16);
        var_19 = wp::sub(var_17, var_18);
        var_20 = wp::length_sq(var_19);
        // if d>best:best=d;i=u;j=v                                                           <L 59>
        var_21 = (var_20 > var_10);
        if (var_21) {
            var_22 = wp::copy(var_20);
            var_23 = wp::copy(var_11);
            var_24 = wp::copy(var_16);
        }
        var_25 = wp::where(var_21, var_23, var_2);
        var_26 = wp::where(var_21, var_24, var_4);
        var_27 = wp::where(var_21, var_22, var_10);
        wp::assign(var_2, var_25);
        wp::assign(var_4, var_26);
        wp::assign(var_10, var_27);
        goto start_for_0;
    end_for_0:;
    // for v in range(u+1,3):                                                                 <L 57>
    var_30 = wp::add(var_28, var_29);
    var_32 = wp::range(var_30, var_31);
    start_for_2:;
        if (iter_cmp(var_32) == 0) goto end_for_2;
        var_33 = wp::iter_next(var_32);
        // d=wp.length_sq(p[u]-p[v])                                                          <L 58>
        var_34 = wp::extract(var_0, var_28);
        var_35 = wp::extract(var_0, var_33);
        var_36 = wp::sub(var_34, var_35);
        var_37 = wp::length_sq(var_36);
        // if d>best:best=d;i=u;j=v                                                           <L 59>
        var_38 = (var_37 > var_10);
        if (var_38) {
            var_39 = wp::copy(var_37);
            var_40 = wp::copy(var_28);
            var_41 = wp::copy(var_33);
        }
        var_42 = wp::where(var_38, var_40, var_2);
        var_43 = wp::where(var_38, var_41, var_4);
        var_44 = wp::where(var_38, var_39, var_10);
        wp::assign(var_2, var_42);
        wp::assign(var_4, var_43);
        wp::assign(var_10, var_44);
        wp::assign(var_20, var_37);
        goto start_for_2;
    end_for_2:;
    // for v in range(u+1,3):                                                                 <L 57>
    var_47 = wp::add(var_45, var_46);
    var_49 = wp::range(var_47, var_48);
    start_for_4:;
        if (iter_cmp(var_49) == 0) goto end_for_4;
        var_50 = wp::iter_next(var_49);
        // d=wp.length_sq(p[u]-p[v])                                                          <L 58>
        var_51 = wp::extract(var_0, var_45);
        var_52 = wp::extract(var_0, var_50);
        var_53 = wp::sub(var_51, var_52);
        var_54 = wp::length_sq(var_53);
        // if d>best:best=d;i=u;j=v                                                           <L 59>
        var_55 = (var_54 > var_10);
        if (var_55) {
            var_56 = wp::copy(var_54);
            var_57 = wp::copy(var_45);
            var_58 = wp::copy(var_50);
        }
        var_59 = wp::where(var_55, var_57, var_2);
        var_60 = wp::where(var_55, var_58, var_4);
        var_61 = wp::where(var_55, var_56, var_10);
        wp::assign(var_2, var_59);
        wp::assign(var_4, var_60);
        wp::assign(var_10, var_61);
        wp::assign(var_20, var_54);
        goto start_for_4;
    end_for_4:;
    // mid=(B[i]+B[j])*wp.float64(.5);L=B;H=B                                                 <L 60>
    var_62 = wp::extract(var_B, var_2);
    var_63 = wp::extract(var_B, var_4);
    var_64 = wp::add(var_62, var_63);
    var_65 = 0.5;
    var_66 = wp::mul(var_64, var_65);
    var_67 = wp::copy(var_B);
    var_68 = wp::copy(var_B);
    // for k in range(3):L[i,k]=mid[k];H[j,k]=mid[k]                                          <L 61>
    var_70 = wp::extract(var_66, var_69);
    wp::assign_inplace(var_67, var_2, var_69, var_70);
    var_71 = wp::extract(var_66, var_69);
    wp::assign_inplace(var_68, var_4, var_69, var_71);
    var_73 = wp::extract(var_66, var_72);
    wp::assign_inplace(var_67, var_2, var_72, var_73);
    var_74 = wp::extract(var_66, var_72);
    wp::assign_inplace(var_68, var_4, var_72, var_74);
    var_76 = wp::extract(var_66, var_75);
    wp::assign_inplace(var_67, var_2, var_75, var_76);
    var_77 = wp::extract(var_66, var_75);
    wp::assign_inplace(var_68, var_4, var_75, var_77);
    // return L,H                                                                             <L 62>
    ret_0 = var_67;
    ret_1 = var_68;
    return;
}


// /home/omen/Documents/Codex/experiments/tomato_adaptive_contact_20261112_v24/src/allocated_gpu.py:64
static CUDA_CALLABLE Value_53a65c4a evaluate_leaf_0(
    wp::uint64 var_mesh,
    wp::array_t<wp::vec_t<3, wp::float64>> var_tri,
    wp::mat_t<3, 3, wp::float64> var_B,
    wp::mat_t<3, 3, wp::float64> var_X,
    wp::mat_t<3, 3, wp::float64> var_V,
    wp::float64 var_A,
    wp::mat_t<3, 3, wp::float64> var_R,
    wp::vec_t<3, wp::float64> var_T,
    wp::vec_t<3, wp::float64> var_tv)
{
    //---------
    // primal vars
    Value_53a65c4a var_0;
    wp::float64 var_1;
    wp::mat_t<3, 3, wp::float64> var_2;
    wp::float64 var_3;
    wp::float64 var_4;
    wp::float64 var_5;
    wp::float64 var_6;
    wp::vec_t<3, wp::float64> var_7;
    wp::float64 var_8;
    const wp::int32 var_9 = 1;
    wp::mat_t<3, 3, wp::float64> var_10;
    const wp::int32 var_11 = 0;
    wp::vec_t<3, wp::float64> var_12;
    const wp::int32 var_13 = 1;
    wp::vec_t<3, wp::float64> var_14;
    wp::vec_t<3, wp::float64> var_15;
    const wp::int32 var_16 = 2;
    wp::vec_t<3, wp::float64> var_17;
    wp::vec_t<3, wp::float64> var_18;
    wp::float64 var_19;
    wp::vec_t<3, wp::float64> var_20;
    const wp::int32 var_21 = 0;
    wp::vec_t<3, wp::float64> var_22;
    wp::vec_t<3, wp::float64> var_23;
    wp::float64 var_24;
    const wp::int32 var_25 = 1;
    wp::vec_t<3, wp::float64> var_26;
    wp::vec_t<3, wp::float64> var_27;
    wp::float64 var_28;
    const wp::int32 var_29 = 2;
    wp::vec_t<3, wp::float64> var_30;
    wp::vec_t<3, wp::float64> var_31;
    wp::float64 var_32;
    wp::float64 var_33;
    wp::float64 var_34;
    wp::mat_t<3, 3, wp::float64> var_35;
    wp::vec_t<3, wp::float64> var_36;
    wp::vec_t<3, wp::float64> var_37;
    Signed_7e3cff60 var_38;
    wp::float64 var_39;
    wp::float64 var_40;
    wp::float64 var_41;
    wp::float64* var_42;
    wp::float64 var_43;
    wp::float64 var_44;
    bool var_45;
    wp::float64 var_46;
    wp::mat_t<3, 3, wp::float64> var_47;
    wp::mat_t<3, 3, wp::float64> var_48;
    wp::float64 var_49;
    wp::mat_t<3, 3, wp::float64> var_50;
    const bool var_51 = false;
    const wp::int32 var_52 = 0;
    const wp::int32 var_53 = 3;
    wp::int32 var_54;
    const wp::int32 var_55 = 3;
    wp::int32 var_56;
    const wp::float32 var_57 = 1.0;
    const wp::float32 var_58 = 6.0;
    wp::float32 var_59;
    wp::float64 var_60;
    wp::vec_t<3, wp::float64> var_61;
    const wp::float32 var_62 = 2.0;
    const wp::float32 var_63 = 3.0;
    wp::float32 var_64;
    wp::float64 var_65;
    wp::mat_t<3, 3, wp::float64> var_66;
    wp::float64 var_67;
    wp::float64 var_68;
    const wp::int32 var_69 = 1;
    bool var_70;
    wp::mat_t<3, 3, wp::float64> var_71;
    wp::float64 var_72;
    wp::float64 var_73;
    const wp::int32 var_74 = 2;
    bool var_75;
    wp::mat_t<3, 3, wp::float64> var_76;
    wp::float64 var_77;
    wp::float64 var_78;
    wp::mat_t<3, 3, wp::float64> var_79;
    wp::float64 var_80;
    wp::mat_t<3, 3, wp::float64> var_81;
    wp::float64 var_82;
    wp::mat_t<3, 3, wp::float64> var_83;
    wp::vec_t<3, wp::float64> var_84;
    wp::mat_t<3, 3, wp::float64> var_85;
    wp::vec_t<3, wp::float64> var_86;
    wp::mat_t<3, 3, wp::float64> var_87;
    wp::vec_t<3, wp::float64> var_88;
    wp::mat_t<3, 3, wp::float64> var_89;
    wp::vec_t<3, wp::float64> var_90;
    wp::vec_t<3, wp::float64> var_91;
    Signed_7e3cff60 var_92;
    const wp::int32 var_93 = 1;
    wp::int32* var_94;
    wp::int32 var_95;
    wp::int32 var_96;
    wp::float64* var_97;
    wp::float64 var_98;
    bool var_99;
    wp::float64 var_100;
    const bool var_101 = true;
    wp::vec_t<3, wp::float64>* var_102;
    wp::vec_t<3, wp::float64> var_103;
    wp::vec_t<3, wp::float64> var_104;
    wp::float64* var_105;
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
    const wp::int32 var_134 = 0;
    bool var_135;
    wp::float64 var_136;
    wp::float64 var_137;
    wp::float64 var_138;
    wp::float64 var_139;
    wp::float64 var_140;
    wp::float64 var_141;
    wp::mat_t<3, 3, wp::float64>* var_142;
    wp::float64* var_143;
    wp::float64 var_144;
    wp::float64 var_145;
    wp::float64* var_146;
    const wp::int32 var_147 = 1;
    const wp::int32 var_148 = 0;
    bool var_149;
    wp::float64 var_150;
    wp::float64 var_151;
    wp::float64 var_152;
    wp::float64 var_153;
    wp::float64 var_154;
    wp::float64 var_155;
    wp::mat_t<3, 3, wp::float64>* var_156;
    wp::float64* var_157;
    wp::float64 var_158;
    wp::float64 var_159;
    wp::float64* var_160;
    const wp::int32 var_161 = 2;
    const wp::int32 var_162 = 0;
    bool var_163;
    wp::float64 var_164;
    wp::float64 var_165;
    wp::float64 var_166;
    wp::float64 var_167;
    wp::float64 var_168;
    wp::float64 var_169;
    wp::mat_t<3, 3, wp::float64>* var_170;
    wp::float64* var_171;
    wp::float64 var_172;
    wp::float64 var_173;
    wp::float64* var_174;
    const wp::int32 var_175 = 1;
    const wp::int32 var_176 = 0;
    const wp::int32 var_177 = 0;
    bool var_178;
    wp::float64 var_179;
    wp::float64 var_180;
    wp::float64 var_181;
    wp::float64 var_182;
    wp::float64 var_183;
    wp::float64 var_184;
    wp::mat_t<3, 3, wp::float64>* var_185;
    wp::float64* var_186;
    wp::float64 var_187;
    wp::float64 var_188;
    wp::float64* var_189;
    const wp::int32 var_190 = 1;
    const wp::int32 var_191 = 0;
    bool var_192;
    wp::float64 var_193;
    wp::float64 var_194;
    wp::float64 var_195;
    wp::float64 var_196;
    wp::float64 var_197;
    wp::float64 var_198;
    wp::mat_t<3, 3, wp::float64>* var_199;
    wp::float64* var_200;
    wp::float64 var_201;
    wp::float64 var_202;
    wp::float64* var_203;
    const wp::int32 var_204 = 2;
    const wp::int32 var_205 = 0;
    bool var_206;
    wp::float64 var_207;
    wp::float64 var_208;
    wp::float64 var_209;
    wp::float64 var_210;
    wp::float64 var_211;
    wp::float64 var_212;
    wp::mat_t<3, 3, wp::float64>* var_213;
    wp::float64* var_214;
    wp::float64 var_215;
    wp::float64 var_216;
    wp::float64* var_217;
    const wp::int32 var_218 = 2;
    const wp::int32 var_219 = 0;
    const wp::int32 var_220 = 0;
    bool var_221;
    wp::float64 var_222;
    wp::float64 var_223;
    wp::float64 var_224;
    wp::float64 var_225;
    wp::float64 var_226;
    wp::float64 var_227;
    wp::mat_t<3, 3, wp::float64>* var_228;
    wp::float64* var_229;
    wp::float64 var_230;
    wp::float64 var_231;
    wp::float64* var_232;
    const wp::int32 var_233 = 1;
    const wp::int32 var_234 = 0;
    bool var_235;
    wp::float64 var_236;
    wp::float64 var_237;
    wp::float64 var_238;
    wp::float64 var_239;
    wp::float64 var_240;
    wp::float64 var_241;
    wp::mat_t<3, 3, wp::float64>* var_242;
    wp::float64* var_243;
    wp::float64 var_244;
    wp::float64 var_245;
    wp::float64* var_246;
    const wp::int32 var_247 = 2;
    const wp::int32 var_248 = 0;
    bool var_249;
    wp::float64 var_250;
    wp::float64 var_251;
    wp::float64 var_252;
    wp::float64 var_253;
    wp::float64 var_254;
    wp::float64 var_255;
    wp::mat_t<3, 3, wp::float64>* var_256;
    wp::float64* var_257;
    wp::float64 var_258;
    wp::float64 var_259;
    wp::float64* var_260;
    const wp::int32 var_261 = 0;
    bool var_262;
    wp::float64 var_263;
    wp::float64 var_264;
    wp::float64 var_265;
    wp::float64 var_266;
    wp::float64 var_267;
    wp::float64 var_268;
    wp::float64* var_269;
    wp::float64 var_270;
    wp::float64 var_271;
    wp::float64 var_272;
    wp::float64* var_273;
    wp::float64 var_274;
    wp::float64 var_275;
    wp::float64 var_276;
    wp::float64* var_277;
    wp::float64 var_278;
    wp::float64 var_279;
    wp::vec_t<3, wp::float64> var_280;
    wp::vec_t<3, wp::float64> var_281;
    wp::vec_t<3, wp::float64>* var_282;
    wp::vec_t<3, wp::float64> var_283;
    wp::vec_t<3, wp::float64> var_284;
    bool var_285;
    const wp::int32 var_286 = 1;
    const wp::int32 var_287 = 3;
    wp::int32 var_288;
    const wp::int32 var_289 = 3;
    wp::int32 var_290;
    const wp::float32 var_291 = 1.0;
    const wp::float32 var_292 = 6.0;
    wp::float32 var_293;
    wp::float64 var_294;
    wp::vec_t<3, wp::float64> var_295;
    const wp::float32 var_296 = 2.0;
    const wp::float32 var_297 = 3.0;
    wp::float32 var_298;
    wp::float64 var_299;
    wp::mat_t<3, 3, wp::float64> var_300;
    wp::float64 var_301;
    wp::float64 var_302;
    const wp::int32 var_303 = 1;
    bool var_304;
    wp::mat_t<3, 3, wp::float64> var_305;
    wp::float64 var_306;
    wp::float64 var_307;
    const wp::int32 var_308 = 2;
    bool var_309;
    wp::mat_t<3, 3, wp::float64> var_310;
    wp::float64 var_311;
    wp::float64 var_312;
    wp::mat_t<3, 3, wp::float64> var_313;
    wp::float64 var_314;
    wp::mat_t<3, 3, wp::float64> var_315;
    wp::float64 var_316;
    wp::mat_t<3, 3, wp::float64> var_317;
    wp::vec_t<3, wp::float64> var_318;
    wp::mat_t<3, 3, wp::float64> var_319;
    wp::vec_t<3, wp::float64> var_320;
    wp::mat_t<3, 3, wp::float64> var_321;
    wp::vec_t<3, wp::float64> var_322;
    wp::mat_t<3, 3, wp::float64> var_323;
    wp::vec_t<3, wp::float64> var_324;
    wp::vec_t<3, wp::float64> var_325;
    Signed_7e3cff60 var_326;
    const wp::int32 var_327 = 1;
    wp::int32* var_328;
    wp::int32 var_329;
    wp::int32 var_330;
    wp::float64* var_331;
    wp::float64 var_332;
    bool var_333;
    wp::float64 var_334;
    const bool var_335 = true;
    wp::vec_t<3, wp::float64>* var_336;
    wp::vec_t<3, wp::float64> var_337;
    wp::vec_t<3, wp::float64> var_338;
    wp::float64* var_339;
    wp::float64 var_340;
    wp::float64 var_341;
    wp::float64 var_342;
    wp::float64 var_343;
    wp::float64 var_344;
    wp::vec_t<3, wp::float64> var_345;
    wp::float64 var_346;
    wp::vec_t<3, wp::float64> var_347;
    wp::vec_t<3, wp::float64> var_348;
    wp::float64 var_349;
    wp::float64 var_350;
    wp::vec_t<3, wp::float64> var_351;
    wp::float64 var_352;
    bool var_353;
    wp::float64 var_354;
    wp::float64 var_355;
    wp::float64 var_356;
    wp::float64 var_357;
    wp::float64 var_358;
    wp::float64 var_359;
    wp::float64 var_360;
    wp::vec_t<3, wp::float64> var_361;
    wp::vec_t<3, wp::float64> var_362;
    wp::vec_t<3, wp::float64> var_363;
    wp::vec_t<3, wp::float64> var_364;
    wp::vec_t<3, wp::float64> var_365;
    const wp::int32 var_366 = 0;
    const wp::int32 var_367 = 0;
    const wp::int32 var_368 = 0;
    bool var_369;
    wp::float64 var_370;
    wp::float64 var_371;
    wp::float64 var_372;
    wp::float64 var_373;
    wp::float64 var_374;
    wp::float64 var_375;
    wp::mat_t<3, 3, wp::float64>* var_376;
    wp::float64* var_377;
    wp::float64 var_378;
    wp::float64 var_379;
    wp::float64* var_380;
    const wp::int32 var_381 = 1;
    const wp::int32 var_382 = 0;
    bool var_383;
    wp::float64 var_384;
    wp::float64 var_385;
    wp::float64 var_386;
    wp::float64 var_387;
    wp::float64 var_388;
    wp::float64 var_389;
    wp::mat_t<3, 3, wp::float64>* var_390;
    wp::float64* var_391;
    wp::float64 var_392;
    wp::float64 var_393;
    wp::float64* var_394;
    const wp::int32 var_395 = 2;
    const wp::int32 var_396 = 0;
    bool var_397;
    wp::float64 var_398;
    wp::float64 var_399;
    wp::float64 var_400;
    wp::float64 var_401;
    wp::float64 var_402;
    wp::float64 var_403;
    wp::mat_t<3, 3, wp::float64>* var_404;
    wp::float64* var_405;
    wp::float64 var_406;
    wp::float64 var_407;
    wp::float64* var_408;
    const wp::int32 var_409 = 1;
    const wp::int32 var_410 = 0;
    const wp::int32 var_411 = 0;
    bool var_412;
    wp::float64 var_413;
    wp::float64 var_414;
    wp::float64 var_415;
    wp::float64 var_416;
    wp::float64 var_417;
    wp::float64 var_418;
    wp::mat_t<3, 3, wp::float64>* var_419;
    wp::float64* var_420;
    wp::float64 var_421;
    wp::float64 var_422;
    wp::float64* var_423;
    const wp::int32 var_424 = 1;
    const wp::int32 var_425 = 0;
    bool var_426;
    wp::float64 var_427;
    wp::float64 var_428;
    wp::float64 var_429;
    wp::float64 var_430;
    wp::float64 var_431;
    wp::float64 var_432;
    wp::mat_t<3, 3, wp::float64>* var_433;
    wp::float64* var_434;
    wp::float64 var_435;
    wp::float64 var_436;
    wp::float64* var_437;
    const wp::int32 var_438 = 2;
    const wp::int32 var_439 = 0;
    bool var_440;
    wp::float64 var_441;
    wp::float64 var_442;
    wp::float64 var_443;
    wp::float64 var_444;
    wp::float64 var_445;
    wp::float64 var_446;
    wp::mat_t<3, 3, wp::float64>* var_447;
    wp::float64* var_448;
    wp::float64 var_449;
    wp::float64 var_450;
    wp::float64* var_451;
    const wp::int32 var_452 = 2;
    const wp::int32 var_453 = 0;
    const wp::int32 var_454 = 0;
    bool var_455;
    wp::float64 var_456;
    wp::float64 var_457;
    wp::float64 var_458;
    wp::float64 var_459;
    wp::float64 var_460;
    wp::float64 var_461;
    wp::mat_t<3, 3, wp::float64>* var_462;
    wp::float64* var_463;
    wp::float64 var_464;
    wp::float64 var_465;
    wp::float64* var_466;
    const wp::int32 var_467 = 1;
    const wp::int32 var_468 = 0;
    bool var_469;
    wp::float64 var_470;
    wp::float64 var_471;
    wp::float64 var_472;
    wp::float64 var_473;
    wp::float64 var_474;
    wp::float64 var_475;
    wp::mat_t<3, 3, wp::float64>* var_476;
    wp::float64* var_477;
    wp::float64 var_478;
    wp::float64 var_479;
    wp::float64* var_480;
    const wp::int32 var_481 = 2;
    const wp::int32 var_482 = 0;
    bool var_483;
    wp::float64 var_484;
    wp::float64 var_485;
    wp::float64 var_486;
    wp::float64 var_487;
    wp::float64 var_488;
    wp::float64 var_489;
    wp::mat_t<3, 3, wp::float64>* var_490;
    wp::float64* var_491;
    wp::float64 var_492;
    wp::float64 var_493;
    wp::float64* var_494;
    const wp::int32 var_495 = 0;
    bool var_496;
    wp::float64 var_497;
    wp::float64 var_498;
    wp::float64 var_499;
    wp::float64 var_500;
    wp::float64 var_501;
    wp::float64 var_502;
    wp::float64* var_503;
    wp::float64 var_504;
    wp::float64 var_505;
    wp::float64 var_506;
    wp::float64* var_507;
    wp::float64 var_508;
    wp::float64 var_509;
    wp::float64 var_510;
    wp::float64* var_511;
    wp::float64 var_512;
    wp::float64 var_513;
    wp::vec_t<3, wp::float64> var_514;
    wp::vec_t<3, wp::float64> var_515;
    wp::vec_t<3, wp::float64>* var_516;
    wp::vec_t<3, wp::float64> var_517;
    wp::vec_t<3, wp::float64> var_518;
    bool var_519;
    wp::vec_t<3, wp::float64> var_520;
    wp::float64 var_521;
    wp::float64 var_522;
    wp::vec_t<3, wp::float64> var_523;
    wp::vec_t<3, wp::float64> var_524;
    wp::float64 var_525;
    wp::vec_t<3, wp::float64> var_526;
    wp::vec_t<3, wp::float64> var_527;
    wp::int32 var_528;
    wp::int32 var_529;
    const wp::int32 var_530 = 2;
    const wp::int32 var_531 = 3;
    wp::int32 var_532;
    const wp::int32 var_533 = 3;
    wp::int32 var_534;
    const wp::float32 var_535 = 1.0;
    const wp::float32 var_536 = 6.0;
    wp::float32 var_537;
    wp::float64 var_538;
    wp::vec_t<3, wp::float64> var_539;
    const wp::float32 var_540 = 2.0;
    const wp::float32 var_541 = 3.0;
    wp::float32 var_542;
    wp::float64 var_543;
    wp::mat_t<3, 3, wp::float64> var_544;
    wp::float64 var_545;
    wp::float64 var_546;
    const wp::int32 var_547 = 1;
    bool var_548;
    wp::mat_t<3, 3, wp::float64> var_549;
    wp::float64 var_550;
    wp::float64 var_551;
    const wp::int32 var_552 = 2;
    bool var_553;
    wp::mat_t<3, 3, wp::float64> var_554;
    wp::float64 var_555;
    wp::float64 var_556;
    wp::mat_t<3, 3, wp::float64> var_557;
    wp::float64 var_558;
    wp::mat_t<3, 3, wp::float64> var_559;
    wp::float64 var_560;
    wp::mat_t<3, 3, wp::float64> var_561;
    wp::vec_t<3, wp::float64> var_562;
    wp::mat_t<3, 3, wp::float64> var_563;
    wp::vec_t<3, wp::float64> var_564;
    wp::mat_t<3, 3, wp::float64> var_565;
    wp::vec_t<3, wp::float64> var_566;
    wp::mat_t<3, 3, wp::float64> var_567;
    wp::vec_t<3, wp::float64> var_568;
    wp::vec_t<3, wp::float64> var_569;
    Signed_7e3cff60 var_570;
    const wp::int32 var_571 = 1;
    wp::int32* var_572;
    wp::int32 var_573;
    wp::int32 var_574;
    wp::float64* var_575;
    wp::float64 var_576;
    bool var_577;
    wp::float64 var_578;
    const bool var_579 = true;
    wp::vec_t<3, wp::float64>* var_580;
    wp::vec_t<3, wp::float64> var_581;
    wp::vec_t<3, wp::float64> var_582;
    wp::float64* var_583;
    wp::float64 var_584;
    wp::float64 var_585;
    wp::float64 var_586;
    wp::float64 var_587;
    wp::float64 var_588;
    wp::vec_t<3, wp::float64> var_589;
    wp::float64 var_590;
    wp::vec_t<3, wp::float64> var_591;
    wp::vec_t<3, wp::float64> var_592;
    wp::float64 var_593;
    wp::float64 var_594;
    wp::vec_t<3, wp::float64> var_595;
    wp::float64 var_596;
    bool var_597;
    wp::float64 var_598;
    wp::float64 var_599;
    wp::float64 var_600;
    wp::float64 var_601;
    wp::float64 var_602;
    wp::float64 var_603;
    wp::float64 var_604;
    wp::vec_t<3, wp::float64> var_605;
    wp::vec_t<3, wp::float64> var_606;
    wp::vec_t<3, wp::float64> var_607;
    wp::vec_t<3, wp::float64> var_608;
    wp::vec_t<3, wp::float64> var_609;
    const wp::int32 var_610 = 0;
    const wp::int32 var_611 = 0;
    const wp::int32 var_612 = 0;
    bool var_613;
    wp::float64 var_614;
    wp::float64 var_615;
    wp::float64 var_616;
    wp::float64 var_617;
    wp::float64 var_618;
    wp::float64 var_619;
    wp::mat_t<3, 3, wp::float64>* var_620;
    wp::float64* var_621;
    wp::float64 var_622;
    wp::float64 var_623;
    wp::float64* var_624;
    const wp::int32 var_625 = 1;
    const wp::int32 var_626 = 0;
    bool var_627;
    wp::float64 var_628;
    wp::float64 var_629;
    wp::float64 var_630;
    wp::float64 var_631;
    wp::float64 var_632;
    wp::float64 var_633;
    wp::mat_t<3, 3, wp::float64>* var_634;
    wp::float64* var_635;
    wp::float64 var_636;
    wp::float64 var_637;
    wp::float64* var_638;
    const wp::int32 var_639 = 2;
    const wp::int32 var_640 = 0;
    bool var_641;
    wp::float64 var_642;
    wp::float64 var_643;
    wp::float64 var_644;
    wp::float64 var_645;
    wp::float64 var_646;
    wp::float64 var_647;
    wp::mat_t<3, 3, wp::float64>* var_648;
    wp::float64* var_649;
    wp::float64 var_650;
    wp::float64 var_651;
    wp::float64* var_652;
    const wp::int32 var_653 = 1;
    const wp::int32 var_654 = 0;
    const wp::int32 var_655 = 0;
    bool var_656;
    wp::float64 var_657;
    wp::float64 var_658;
    wp::float64 var_659;
    wp::float64 var_660;
    wp::float64 var_661;
    wp::float64 var_662;
    wp::mat_t<3, 3, wp::float64>* var_663;
    wp::float64* var_664;
    wp::float64 var_665;
    wp::float64 var_666;
    wp::float64* var_667;
    const wp::int32 var_668 = 1;
    const wp::int32 var_669 = 0;
    bool var_670;
    wp::float64 var_671;
    wp::float64 var_672;
    wp::float64 var_673;
    wp::float64 var_674;
    wp::float64 var_675;
    wp::float64 var_676;
    wp::mat_t<3, 3, wp::float64>* var_677;
    wp::float64* var_678;
    wp::float64 var_679;
    wp::float64 var_680;
    wp::float64* var_681;
    const wp::int32 var_682 = 2;
    const wp::int32 var_683 = 0;
    bool var_684;
    wp::float64 var_685;
    wp::float64 var_686;
    wp::float64 var_687;
    wp::float64 var_688;
    wp::float64 var_689;
    wp::float64 var_690;
    wp::mat_t<3, 3, wp::float64>* var_691;
    wp::float64* var_692;
    wp::float64 var_693;
    wp::float64 var_694;
    wp::float64* var_695;
    const wp::int32 var_696 = 2;
    const wp::int32 var_697 = 0;
    const wp::int32 var_698 = 0;
    bool var_699;
    wp::float64 var_700;
    wp::float64 var_701;
    wp::float64 var_702;
    wp::float64 var_703;
    wp::float64 var_704;
    wp::float64 var_705;
    wp::mat_t<3, 3, wp::float64>* var_706;
    wp::float64* var_707;
    wp::float64 var_708;
    wp::float64 var_709;
    wp::float64* var_710;
    const wp::int32 var_711 = 1;
    const wp::int32 var_712 = 0;
    bool var_713;
    wp::float64 var_714;
    wp::float64 var_715;
    wp::float64 var_716;
    wp::float64 var_717;
    wp::float64 var_718;
    wp::float64 var_719;
    wp::mat_t<3, 3, wp::float64>* var_720;
    wp::float64* var_721;
    wp::float64 var_722;
    wp::float64 var_723;
    wp::float64* var_724;
    const wp::int32 var_725 = 2;
    const wp::int32 var_726 = 0;
    bool var_727;
    wp::float64 var_728;
    wp::float64 var_729;
    wp::float64 var_730;
    wp::float64 var_731;
    wp::float64 var_732;
    wp::float64 var_733;
    wp::mat_t<3, 3, wp::float64>* var_734;
    wp::float64* var_735;
    wp::float64 var_736;
    wp::float64 var_737;
    wp::float64* var_738;
    const wp::int32 var_739 = 0;
    bool var_740;
    wp::float64 var_741;
    wp::float64 var_742;
    wp::float64 var_743;
    wp::float64 var_744;
    wp::float64 var_745;
    wp::float64 var_746;
    wp::float64* var_747;
    wp::float64 var_748;
    wp::float64 var_749;
    wp::float64 var_750;
    wp::float64* var_751;
    wp::float64 var_752;
    wp::float64 var_753;
    wp::float64 var_754;
    wp::float64* var_755;
    wp::float64 var_756;
    wp::float64 var_757;
    wp::vec_t<3, wp::float64> var_758;
    wp::vec_t<3, wp::float64> var_759;
    wp::vec_t<3, wp::float64>* var_760;
    wp::vec_t<3, wp::float64> var_761;
    wp::vec_t<3, wp::float64> var_762;
    bool var_763;
    wp::vec_t<3, wp::float64> var_764;
    wp::float64 var_765;
    wp::float64 var_766;
    wp::vec_t<3, wp::float64> var_767;
    wp::vec_t<3, wp::float64> var_768;
    wp::float64 var_769;
    wp::vec_t<3, wp::float64> var_770;
    wp::vec_t<3, wp::float64> var_771;
    wp::int32 var_772;
    wp::int32 var_773;
    const wp::int32 var_774 = 3;
    const wp::int32 var_775 = 3;
    wp::int32 var_776;
    const wp::int32 var_777 = 3;
    wp::int32 var_778;
    const wp::float32 var_779 = 1.0;
    const wp::float32 var_780 = 6.0;
    wp::float32 var_781;
    wp::float64 var_782;
    wp::vec_t<3, wp::float64> var_783;
    const wp::float32 var_784 = 2.0;
    const wp::float32 var_785 = 3.0;
    wp::float32 var_786;
    wp::float64 var_787;
    wp::mat_t<3, 3, wp::float64> var_788;
    wp::float64 var_789;
    wp::float64 var_790;
    const wp::int32 var_791 = 1;
    bool var_792;
    wp::mat_t<3, 3, wp::float64> var_793;
    wp::float64 var_794;
    wp::float64 var_795;
    const wp::int32 var_796 = 2;
    bool var_797;
    wp::mat_t<3, 3, wp::float64> var_798;
    wp::float64 var_799;
    wp::float64 var_800;
    wp::mat_t<3, 3, wp::float64> var_801;
    wp::float64 var_802;
    wp::mat_t<3, 3, wp::float64> var_803;
    wp::float64 var_804;
    wp::mat_t<3, 3, wp::float64> var_805;
    wp::vec_t<3, wp::float64> var_806;
    wp::mat_t<3, 3, wp::float64> var_807;
    wp::vec_t<3, wp::float64> var_808;
    wp::mat_t<3, 3, wp::float64> var_809;
    wp::vec_t<3, wp::float64> var_810;
    wp::mat_t<3, 3, wp::float64> var_811;
    wp::vec_t<3, wp::float64> var_812;
    wp::vec_t<3, wp::float64> var_813;
    Signed_7e3cff60 var_814;
    const wp::int32 var_815 = 1;
    wp::int32* var_816;
    wp::int32 var_817;
    wp::int32 var_818;
    wp::float64* var_819;
    wp::float64 var_820;
    bool var_821;
    wp::float64 var_822;
    const bool var_823 = true;
    wp::vec_t<3, wp::float64>* var_824;
    wp::vec_t<3, wp::float64> var_825;
    wp::vec_t<3, wp::float64> var_826;
    wp::float64* var_827;
    wp::float64 var_828;
    wp::float64 var_829;
    wp::float64 var_830;
    wp::float64 var_831;
    wp::float64 var_832;
    wp::vec_t<3, wp::float64> var_833;
    wp::float64 var_834;
    wp::vec_t<3, wp::float64> var_835;
    wp::vec_t<3, wp::float64> var_836;
    wp::float64 var_837;
    wp::float64 var_838;
    wp::vec_t<3, wp::float64> var_839;
    wp::float64 var_840;
    bool var_841;
    wp::float64 var_842;
    wp::float64 var_843;
    wp::float64 var_844;
    wp::float64 var_845;
    wp::float64 var_846;
    wp::float64 var_847;
    wp::float64 var_848;
    wp::vec_t<3, wp::float64> var_849;
    wp::vec_t<3, wp::float64> var_850;
    wp::vec_t<3, wp::float64> var_851;
    wp::vec_t<3, wp::float64> var_852;
    wp::vec_t<3, wp::float64> var_853;
    const wp::int32 var_854 = 0;
    const wp::int32 var_855 = 0;
    const wp::int32 var_856 = 0;
    bool var_857;
    wp::float64 var_858;
    wp::float64 var_859;
    wp::float64 var_860;
    wp::float64 var_861;
    wp::float64 var_862;
    wp::float64 var_863;
    wp::mat_t<3, 3, wp::float64>* var_864;
    wp::float64* var_865;
    wp::float64 var_866;
    wp::float64 var_867;
    wp::float64* var_868;
    const wp::int32 var_869 = 1;
    const wp::int32 var_870 = 0;
    bool var_871;
    wp::float64 var_872;
    wp::float64 var_873;
    wp::float64 var_874;
    wp::float64 var_875;
    wp::float64 var_876;
    wp::float64 var_877;
    wp::mat_t<3, 3, wp::float64>* var_878;
    wp::float64* var_879;
    wp::float64 var_880;
    wp::float64 var_881;
    wp::float64* var_882;
    const wp::int32 var_883 = 2;
    const wp::int32 var_884 = 0;
    bool var_885;
    wp::float64 var_886;
    wp::float64 var_887;
    wp::float64 var_888;
    wp::float64 var_889;
    wp::float64 var_890;
    wp::float64 var_891;
    wp::mat_t<3, 3, wp::float64>* var_892;
    wp::float64* var_893;
    wp::float64 var_894;
    wp::float64 var_895;
    wp::float64* var_896;
    const wp::int32 var_897 = 1;
    const wp::int32 var_898 = 0;
    const wp::int32 var_899 = 0;
    bool var_900;
    wp::float64 var_901;
    wp::float64 var_902;
    wp::float64 var_903;
    wp::float64 var_904;
    wp::float64 var_905;
    wp::float64 var_906;
    wp::mat_t<3, 3, wp::float64>* var_907;
    wp::float64* var_908;
    wp::float64 var_909;
    wp::float64 var_910;
    wp::float64* var_911;
    const wp::int32 var_912 = 1;
    const wp::int32 var_913 = 0;
    bool var_914;
    wp::float64 var_915;
    wp::float64 var_916;
    wp::float64 var_917;
    wp::float64 var_918;
    wp::float64 var_919;
    wp::float64 var_920;
    wp::mat_t<3, 3, wp::float64>* var_921;
    wp::float64* var_922;
    wp::float64 var_923;
    wp::float64 var_924;
    wp::float64* var_925;
    const wp::int32 var_926 = 2;
    const wp::int32 var_927 = 0;
    bool var_928;
    wp::float64 var_929;
    wp::float64 var_930;
    wp::float64 var_931;
    wp::float64 var_932;
    wp::float64 var_933;
    wp::float64 var_934;
    wp::mat_t<3, 3, wp::float64>* var_935;
    wp::float64* var_936;
    wp::float64 var_937;
    wp::float64 var_938;
    wp::float64* var_939;
    const wp::int32 var_940 = 2;
    const wp::int32 var_941 = 0;
    const wp::int32 var_942 = 0;
    bool var_943;
    wp::float64 var_944;
    wp::float64 var_945;
    wp::float64 var_946;
    wp::float64 var_947;
    wp::float64 var_948;
    wp::float64 var_949;
    wp::mat_t<3, 3, wp::float64>* var_950;
    wp::float64* var_951;
    wp::float64 var_952;
    wp::float64 var_953;
    wp::float64* var_954;
    const wp::int32 var_955 = 1;
    const wp::int32 var_956 = 0;
    bool var_957;
    wp::float64 var_958;
    wp::float64 var_959;
    wp::float64 var_960;
    wp::float64 var_961;
    wp::float64 var_962;
    wp::float64 var_963;
    wp::mat_t<3, 3, wp::float64>* var_964;
    wp::float64* var_965;
    wp::float64 var_966;
    wp::float64 var_967;
    wp::float64* var_968;
    const wp::int32 var_969 = 2;
    const wp::int32 var_970 = 0;
    bool var_971;
    wp::float64 var_972;
    wp::float64 var_973;
    wp::float64 var_974;
    wp::float64 var_975;
    wp::float64 var_976;
    wp::float64 var_977;
    wp::mat_t<3, 3, wp::float64>* var_978;
    wp::float64* var_979;
    wp::float64 var_980;
    wp::float64 var_981;
    wp::float64* var_982;
    const wp::int32 var_983 = 0;
    bool var_984;
    wp::float64 var_985;
    wp::float64 var_986;
    wp::float64 var_987;
    wp::float64 var_988;
    wp::float64 var_989;
    wp::float64 var_990;
    wp::float64* var_991;
    wp::float64 var_992;
    wp::float64 var_993;
    wp::float64 var_994;
    wp::float64* var_995;
    wp::float64 var_996;
    wp::float64 var_997;
    wp::float64 var_998;
    wp::float64* var_999;
    wp::float64 var_1000;
    wp::float64 var_1001;
    wp::vec_t<3, wp::float64> var_1002;
    wp::vec_t<3, wp::float64> var_1003;
    wp::vec_t<3, wp::float64>* var_1004;
    wp::vec_t<3, wp::float64> var_1005;
    wp::vec_t<3, wp::float64> var_1006;
    bool var_1007;
    wp::vec_t<3, wp::float64> var_1008;
    wp::float64 var_1009;
    wp::float64 var_1010;
    wp::vec_t<3, wp::float64> var_1011;
    wp::vec_t<3, wp::float64> var_1012;
    wp::float64 var_1013;
    wp::vec_t<3, wp::float64> var_1014;
    wp::vec_t<3, wp::float64> var_1015;
    wp::int32 var_1016;
    wp::int32 var_1017;
    const wp::int32 var_1018 = 4;
    const wp::int32 var_1019 = 3;
    wp::int32 var_1020;
    const wp::int32 var_1021 = 3;
    wp::int32 var_1022;
    const wp::float32 var_1023 = 1.0;
    const wp::float32 var_1024 = 6.0;
    wp::float32 var_1025;
    wp::float64 var_1026;
    wp::vec_t<3, wp::float64> var_1027;
    const wp::float32 var_1028 = 2.0;
    const wp::float32 var_1029 = 3.0;
    wp::float32 var_1030;
    wp::float64 var_1031;
    wp::mat_t<3, 3, wp::float64> var_1032;
    wp::float64 var_1033;
    wp::float64 var_1034;
    const wp::int32 var_1035 = 1;
    bool var_1036;
    wp::mat_t<3, 3, wp::float64> var_1037;
    wp::float64 var_1038;
    wp::float64 var_1039;
    const wp::int32 var_1040 = 2;
    bool var_1041;
    wp::mat_t<3, 3, wp::float64> var_1042;
    wp::float64 var_1043;
    wp::float64 var_1044;
    wp::mat_t<3, 3, wp::float64> var_1045;
    wp::float64 var_1046;
    wp::mat_t<3, 3, wp::float64> var_1047;
    wp::float64 var_1048;
    wp::mat_t<3, 3, wp::float64> var_1049;
    wp::vec_t<3, wp::float64> var_1050;
    wp::mat_t<3, 3, wp::float64> var_1051;
    wp::vec_t<3, wp::float64> var_1052;
    wp::mat_t<3, 3, wp::float64> var_1053;
    wp::vec_t<3, wp::float64> var_1054;
    wp::mat_t<3, 3, wp::float64> var_1055;
    wp::vec_t<3, wp::float64> var_1056;
    wp::vec_t<3, wp::float64> var_1057;
    Signed_7e3cff60 var_1058;
    const wp::int32 var_1059 = 1;
    wp::int32* var_1060;
    wp::int32 var_1061;
    wp::int32 var_1062;
    wp::float64* var_1063;
    wp::float64 var_1064;
    bool var_1065;
    wp::float64 var_1066;
    const bool var_1067 = true;
    wp::vec_t<3, wp::float64>* var_1068;
    wp::vec_t<3, wp::float64> var_1069;
    wp::vec_t<3, wp::float64> var_1070;
    wp::float64* var_1071;
    wp::float64 var_1072;
    wp::float64 var_1073;
    wp::float64 var_1074;
    wp::float64 var_1075;
    wp::float64 var_1076;
    wp::vec_t<3, wp::float64> var_1077;
    wp::float64 var_1078;
    wp::vec_t<3, wp::float64> var_1079;
    wp::vec_t<3, wp::float64> var_1080;
    wp::float64 var_1081;
    wp::float64 var_1082;
    wp::vec_t<3, wp::float64> var_1083;
    wp::float64 var_1084;
    bool var_1085;
    wp::float64 var_1086;
    wp::float64 var_1087;
    wp::float64 var_1088;
    wp::float64 var_1089;
    wp::float64 var_1090;
    wp::float64 var_1091;
    wp::float64 var_1092;
    wp::vec_t<3, wp::float64> var_1093;
    wp::vec_t<3, wp::float64> var_1094;
    wp::vec_t<3, wp::float64> var_1095;
    wp::vec_t<3, wp::float64> var_1096;
    wp::vec_t<3, wp::float64> var_1097;
    const wp::int32 var_1098 = 0;
    const wp::int32 var_1099 = 0;
    const wp::int32 var_1100 = 0;
    bool var_1101;
    wp::float64 var_1102;
    wp::float64 var_1103;
    wp::float64 var_1104;
    wp::float64 var_1105;
    wp::float64 var_1106;
    wp::float64 var_1107;
    wp::mat_t<3, 3, wp::float64>* var_1108;
    wp::float64* var_1109;
    wp::float64 var_1110;
    wp::float64 var_1111;
    wp::float64* var_1112;
    const wp::int32 var_1113 = 1;
    const wp::int32 var_1114 = 0;
    bool var_1115;
    wp::float64 var_1116;
    wp::float64 var_1117;
    wp::float64 var_1118;
    wp::float64 var_1119;
    wp::float64 var_1120;
    wp::float64 var_1121;
    wp::mat_t<3, 3, wp::float64>* var_1122;
    wp::float64* var_1123;
    wp::float64 var_1124;
    wp::float64 var_1125;
    wp::float64* var_1126;
    const wp::int32 var_1127 = 2;
    const wp::int32 var_1128 = 0;
    bool var_1129;
    wp::float64 var_1130;
    wp::float64 var_1131;
    wp::float64 var_1132;
    wp::float64 var_1133;
    wp::float64 var_1134;
    wp::float64 var_1135;
    wp::mat_t<3, 3, wp::float64>* var_1136;
    wp::float64* var_1137;
    wp::float64 var_1138;
    wp::float64 var_1139;
    wp::float64* var_1140;
    const wp::int32 var_1141 = 1;
    const wp::int32 var_1142 = 0;
    const wp::int32 var_1143 = 0;
    bool var_1144;
    wp::float64 var_1145;
    wp::float64 var_1146;
    wp::float64 var_1147;
    wp::float64 var_1148;
    wp::float64 var_1149;
    wp::float64 var_1150;
    wp::mat_t<3, 3, wp::float64>* var_1151;
    wp::float64* var_1152;
    wp::float64 var_1153;
    wp::float64 var_1154;
    wp::float64* var_1155;
    const wp::int32 var_1156 = 1;
    const wp::int32 var_1157 = 0;
    bool var_1158;
    wp::float64 var_1159;
    wp::float64 var_1160;
    wp::float64 var_1161;
    wp::float64 var_1162;
    wp::float64 var_1163;
    wp::float64 var_1164;
    wp::mat_t<3, 3, wp::float64>* var_1165;
    wp::float64* var_1166;
    wp::float64 var_1167;
    wp::float64 var_1168;
    wp::float64* var_1169;
    const wp::int32 var_1170 = 2;
    const wp::int32 var_1171 = 0;
    bool var_1172;
    wp::float64 var_1173;
    wp::float64 var_1174;
    wp::float64 var_1175;
    wp::float64 var_1176;
    wp::float64 var_1177;
    wp::float64 var_1178;
    wp::mat_t<3, 3, wp::float64>* var_1179;
    wp::float64* var_1180;
    wp::float64 var_1181;
    wp::float64 var_1182;
    wp::float64* var_1183;
    const wp::int32 var_1184 = 2;
    const wp::int32 var_1185 = 0;
    const wp::int32 var_1186 = 0;
    bool var_1187;
    wp::float64 var_1188;
    wp::float64 var_1189;
    wp::float64 var_1190;
    wp::float64 var_1191;
    wp::float64 var_1192;
    wp::float64 var_1193;
    wp::mat_t<3, 3, wp::float64>* var_1194;
    wp::float64* var_1195;
    wp::float64 var_1196;
    wp::float64 var_1197;
    wp::float64* var_1198;
    const wp::int32 var_1199 = 1;
    const wp::int32 var_1200 = 0;
    bool var_1201;
    wp::float64 var_1202;
    wp::float64 var_1203;
    wp::float64 var_1204;
    wp::float64 var_1205;
    wp::float64 var_1206;
    wp::float64 var_1207;
    wp::mat_t<3, 3, wp::float64>* var_1208;
    wp::float64* var_1209;
    wp::float64 var_1210;
    wp::float64 var_1211;
    wp::float64* var_1212;
    const wp::int32 var_1213 = 2;
    const wp::int32 var_1214 = 0;
    bool var_1215;
    wp::float64 var_1216;
    wp::float64 var_1217;
    wp::float64 var_1218;
    wp::float64 var_1219;
    wp::float64 var_1220;
    wp::float64 var_1221;
    wp::mat_t<3, 3, wp::float64>* var_1222;
    wp::float64* var_1223;
    wp::float64 var_1224;
    wp::float64 var_1225;
    wp::float64* var_1226;
    const wp::int32 var_1227 = 0;
    bool var_1228;
    wp::float64 var_1229;
    wp::float64 var_1230;
    wp::float64 var_1231;
    wp::float64 var_1232;
    wp::float64 var_1233;
    wp::float64 var_1234;
    wp::float64* var_1235;
    wp::float64 var_1236;
    wp::float64 var_1237;
    wp::float64 var_1238;
    wp::float64* var_1239;
    wp::float64 var_1240;
    wp::float64 var_1241;
    wp::float64 var_1242;
    wp::float64* var_1243;
    wp::float64 var_1244;
    wp::float64 var_1245;
    wp::vec_t<3, wp::float64> var_1246;
    wp::vec_t<3, wp::float64> var_1247;
    wp::vec_t<3, wp::float64>* var_1248;
    wp::vec_t<3, wp::float64> var_1249;
    wp::vec_t<3, wp::float64> var_1250;
    bool var_1251;
    wp::vec_t<3, wp::float64> var_1252;
    wp::float64 var_1253;
    wp::float64 var_1254;
    wp::vec_t<3, wp::float64> var_1255;
    wp::vec_t<3, wp::float64> var_1256;
    wp::float64 var_1257;
    wp::vec_t<3, wp::float64> var_1258;
    wp::vec_t<3, wp::float64> var_1259;
    wp::int32 var_1260;
    wp::int32 var_1261;
    const wp::int32 var_1262 = 5;
    const wp::int32 var_1263 = 3;
    wp::int32 var_1264;
    const wp::int32 var_1265 = 3;
    wp::int32 var_1266;
    const wp::float32 var_1267 = 1.0;
    const wp::float32 var_1268 = 6.0;
    wp::float32 var_1269;
    wp::float64 var_1270;
    wp::vec_t<3, wp::float64> var_1271;
    const wp::float32 var_1272 = 2.0;
    const wp::float32 var_1273 = 3.0;
    wp::float32 var_1274;
    wp::float64 var_1275;
    wp::mat_t<3, 3, wp::float64> var_1276;
    wp::float64 var_1277;
    wp::float64 var_1278;
    const wp::int32 var_1279 = 1;
    bool var_1280;
    wp::mat_t<3, 3, wp::float64> var_1281;
    wp::float64 var_1282;
    wp::float64 var_1283;
    const wp::int32 var_1284 = 2;
    bool var_1285;
    wp::mat_t<3, 3, wp::float64> var_1286;
    wp::float64 var_1287;
    wp::float64 var_1288;
    wp::mat_t<3, 3, wp::float64> var_1289;
    wp::float64 var_1290;
    wp::mat_t<3, 3, wp::float64> var_1291;
    wp::float64 var_1292;
    wp::mat_t<3, 3, wp::float64> var_1293;
    wp::vec_t<3, wp::float64> var_1294;
    wp::mat_t<3, 3, wp::float64> var_1295;
    wp::vec_t<3, wp::float64> var_1296;
    wp::mat_t<3, 3, wp::float64> var_1297;
    wp::vec_t<3, wp::float64> var_1298;
    wp::mat_t<3, 3, wp::float64> var_1299;
    wp::vec_t<3, wp::float64> var_1300;
    wp::vec_t<3, wp::float64> var_1301;
    Signed_7e3cff60 var_1302;
    const wp::int32 var_1303 = 1;
    wp::int32* var_1304;
    wp::int32 var_1305;
    wp::int32 var_1306;
    wp::float64* var_1307;
    wp::float64 var_1308;
    bool var_1309;
    wp::float64 var_1310;
    const bool var_1311 = true;
    wp::vec_t<3, wp::float64>* var_1312;
    wp::vec_t<3, wp::float64> var_1313;
    wp::vec_t<3, wp::float64> var_1314;
    wp::float64* var_1315;
    wp::float64 var_1316;
    wp::float64 var_1317;
    wp::float64 var_1318;
    wp::float64 var_1319;
    wp::float64 var_1320;
    wp::vec_t<3, wp::float64> var_1321;
    wp::float64 var_1322;
    wp::vec_t<3, wp::float64> var_1323;
    wp::vec_t<3, wp::float64> var_1324;
    wp::float64 var_1325;
    wp::float64 var_1326;
    wp::vec_t<3, wp::float64> var_1327;
    wp::float64 var_1328;
    bool var_1329;
    wp::float64 var_1330;
    wp::float64 var_1331;
    wp::float64 var_1332;
    wp::float64 var_1333;
    wp::float64 var_1334;
    wp::float64 var_1335;
    wp::float64 var_1336;
    wp::vec_t<3, wp::float64> var_1337;
    wp::vec_t<3, wp::float64> var_1338;
    wp::vec_t<3, wp::float64> var_1339;
    wp::vec_t<3, wp::float64> var_1340;
    wp::vec_t<3, wp::float64> var_1341;
    const wp::int32 var_1342 = 0;
    const wp::int32 var_1343 = 0;
    const wp::int32 var_1344 = 0;
    bool var_1345;
    wp::float64 var_1346;
    wp::float64 var_1347;
    wp::float64 var_1348;
    wp::float64 var_1349;
    wp::float64 var_1350;
    wp::float64 var_1351;
    wp::mat_t<3, 3, wp::float64>* var_1352;
    wp::float64* var_1353;
    wp::float64 var_1354;
    wp::float64 var_1355;
    wp::float64* var_1356;
    const wp::int32 var_1357 = 1;
    const wp::int32 var_1358 = 0;
    bool var_1359;
    wp::float64 var_1360;
    wp::float64 var_1361;
    wp::float64 var_1362;
    wp::float64 var_1363;
    wp::float64 var_1364;
    wp::float64 var_1365;
    wp::mat_t<3, 3, wp::float64>* var_1366;
    wp::float64* var_1367;
    wp::float64 var_1368;
    wp::float64 var_1369;
    wp::float64* var_1370;
    const wp::int32 var_1371 = 2;
    const wp::int32 var_1372 = 0;
    bool var_1373;
    wp::float64 var_1374;
    wp::float64 var_1375;
    wp::float64 var_1376;
    wp::float64 var_1377;
    wp::float64 var_1378;
    wp::float64 var_1379;
    wp::mat_t<3, 3, wp::float64>* var_1380;
    wp::float64* var_1381;
    wp::float64 var_1382;
    wp::float64 var_1383;
    wp::float64* var_1384;
    const wp::int32 var_1385 = 1;
    const wp::int32 var_1386 = 0;
    const wp::int32 var_1387 = 0;
    bool var_1388;
    wp::float64 var_1389;
    wp::float64 var_1390;
    wp::float64 var_1391;
    wp::float64 var_1392;
    wp::float64 var_1393;
    wp::float64 var_1394;
    wp::mat_t<3, 3, wp::float64>* var_1395;
    wp::float64* var_1396;
    wp::float64 var_1397;
    wp::float64 var_1398;
    wp::float64* var_1399;
    const wp::int32 var_1400 = 1;
    const wp::int32 var_1401 = 0;
    bool var_1402;
    wp::float64 var_1403;
    wp::float64 var_1404;
    wp::float64 var_1405;
    wp::float64 var_1406;
    wp::float64 var_1407;
    wp::float64 var_1408;
    wp::mat_t<3, 3, wp::float64>* var_1409;
    wp::float64* var_1410;
    wp::float64 var_1411;
    wp::float64 var_1412;
    wp::float64* var_1413;
    const wp::int32 var_1414 = 2;
    const wp::int32 var_1415 = 0;
    bool var_1416;
    wp::float64 var_1417;
    wp::float64 var_1418;
    wp::float64 var_1419;
    wp::float64 var_1420;
    wp::float64 var_1421;
    wp::float64 var_1422;
    wp::mat_t<3, 3, wp::float64>* var_1423;
    wp::float64* var_1424;
    wp::float64 var_1425;
    wp::float64 var_1426;
    wp::float64* var_1427;
    const wp::int32 var_1428 = 2;
    const wp::int32 var_1429 = 0;
    const wp::int32 var_1430 = 0;
    bool var_1431;
    wp::float64 var_1432;
    wp::float64 var_1433;
    wp::float64 var_1434;
    wp::float64 var_1435;
    wp::float64 var_1436;
    wp::float64 var_1437;
    wp::mat_t<3, 3, wp::float64>* var_1438;
    wp::float64* var_1439;
    wp::float64 var_1440;
    wp::float64 var_1441;
    wp::float64* var_1442;
    const wp::int32 var_1443 = 1;
    const wp::int32 var_1444 = 0;
    bool var_1445;
    wp::float64 var_1446;
    wp::float64 var_1447;
    wp::float64 var_1448;
    wp::float64 var_1449;
    wp::float64 var_1450;
    wp::float64 var_1451;
    wp::mat_t<3, 3, wp::float64>* var_1452;
    wp::float64* var_1453;
    wp::float64 var_1454;
    wp::float64 var_1455;
    wp::float64* var_1456;
    const wp::int32 var_1457 = 2;
    const wp::int32 var_1458 = 0;
    bool var_1459;
    wp::float64 var_1460;
    wp::float64 var_1461;
    wp::float64 var_1462;
    wp::float64 var_1463;
    wp::float64 var_1464;
    wp::float64 var_1465;
    wp::mat_t<3, 3, wp::float64>* var_1466;
    wp::float64* var_1467;
    wp::float64 var_1468;
    wp::float64 var_1469;
    wp::float64* var_1470;
    const wp::int32 var_1471 = 0;
    bool var_1472;
    wp::float64 var_1473;
    wp::float64 var_1474;
    wp::float64 var_1475;
    wp::float64 var_1476;
    wp::float64 var_1477;
    wp::float64 var_1478;
    wp::float64* var_1479;
    wp::float64 var_1480;
    wp::float64 var_1481;
    wp::float64 var_1482;
    wp::float64* var_1483;
    wp::float64 var_1484;
    wp::float64 var_1485;
    wp::float64 var_1486;
    wp::float64* var_1487;
    wp::float64 var_1488;
    wp::float64 var_1489;
    wp::vec_t<3, wp::float64> var_1490;
    wp::vec_t<3, wp::float64> var_1491;
    wp::vec_t<3, wp::float64>* var_1492;
    wp::vec_t<3, wp::float64> var_1493;
    wp::vec_t<3, wp::float64> var_1494;
    bool var_1495;
    wp::vec_t<3, wp::float64> var_1496;
    wp::float64 var_1497;
    wp::float64 var_1498;
    wp::vec_t<3, wp::float64> var_1499;
    wp::vec_t<3, wp::float64> var_1500;
    wp::float64 var_1501;
    wp::vec_t<3, wp::float64> var_1502;
    wp::vec_t<3, wp::float64> var_1503;
    wp::int32 var_1504;
    wp::int32 var_1505;
    const wp::int32 var_1506 = 6;
    const wp::int32 var_1507 = 3;
    wp::int32 var_1508;
    const wp::int32 var_1509 = 3;
    wp::int32 var_1510;
    const wp::float32 var_1511 = 1.0;
    const wp::float32 var_1512 = 6.0;
    wp::float32 var_1513;
    wp::float64 var_1514;
    wp::vec_t<3, wp::float64> var_1515;
    const wp::float32 var_1516 = 2.0;
    const wp::float32 var_1517 = 3.0;
    wp::float32 var_1518;
    wp::float64 var_1519;
    wp::mat_t<3, 3, wp::float64> var_1520;
    wp::float64 var_1521;
    wp::float64 var_1522;
    const wp::int32 var_1523 = 1;
    bool var_1524;
    wp::mat_t<3, 3, wp::float64> var_1525;
    wp::float64 var_1526;
    wp::float64 var_1527;
    const wp::int32 var_1528 = 2;
    bool var_1529;
    wp::mat_t<3, 3, wp::float64> var_1530;
    wp::float64 var_1531;
    wp::float64 var_1532;
    wp::mat_t<3, 3, wp::float64> var_1533;
    wp::float64 var_1534;
    wp::mat_t<3, 3, wp::float64> var_1535;
    wp::float64 var_1536;
    wp::mat_t<3, 3, wp::float64> var_1537;
    wp::vec_t<3, wp::float64> var_1538;
    wp::mat_t<3, 3, wp::float64> var_1539;
    wp::vec_t<3, wp::float64> var_1540;
    wp::mat_t<3, 3, wp::float64> var_1541;
    wp::vec_t<3, wp::float64> var_1542;
    wp::mat_t<3, 3, wp::float64> var_1543;
    wp::vec_t<3, wp::float64> var_1544;
    wp::vec_t<3, wp::float64> var_1545;
    Signed_7e3cff60 var_1546;
    const wp::int32 var_1547 = 1;
    wp::int32* var_1548;
    wp::int32 var_1549;
    wp::int32 var_1550;
    wp::float64* var_1551;
    wp::float64 var_1552;
    bool var_1553;
    wp::float64 var_1554;
    const bool var_1555 = true;
    wp::vec_t<3, wp::float64>* var_1556;
    wp::vec_t<3, wp::float64> var_1557;
    wp::vec_t<3, wp::float64> var_1558;
    wp::float64* var_1559;
    wp::float64 var_1560;
    wp::float64 var_1561;
    wp::float64 var_1562;
    wp::float64 var_1563;
    wp::float64 var_1564;
    wp::vec_t<3, wp::float64> var_1565;
    wp::float64 var_1566;
    wp::vec_t<3, wp::float64> var_1567;
    wp::vec_t<3, wp::float64> var_1568;
    wp::float64 var_1569;
    wp::float64 var_1570;
    wp::vec_t<3, wp::float64> var_1571;
    wp::float64 var_1572;
    bool var_1573;
    wp::float64 var_1574;
    wp::float64 var_1575;
    wp::float64 var_1576;
    wp::float64 var_1577;
    wp::float64 var_1578;
    wp::float64 var_1579;
    wp::float64 var_1580;
    wp::vec_t<3, wp::float64> var_1581;
    wp::vec_t<3, wp::float64> var_1582;
    wp::vec_t<3, wp::float64> var_1583;
    wp::vec_t<3, wp::float64> var_1584;
    wp::vec_t<3, wp::float64> var_1585;
    const wp::int32 var_1586 = 0;
    const wp::int32 var_1587 = 0;
    const wp::int32 var_1588 = 0;
    bool var_1589;
    wp::float64 var_1590;
    wp::float64 var_1591;
    wp::float64 var_1592;
    wp::float64 var_1593;
    wp::float64 var_1594;
    wp::float64 var_1595;
    wp::mat_t<3, 3, wp::float64>* var_1596;
    wp::float64* var_1597;
    wp::float64 var_1598;
    wp::float64 var_1599;
    wp::float64* var_1600;
    const wp::int32 var_1601 = 1;
    const wp::int32 var_1602 = 0;
    bool var_1603;
    wp::float64 var_1604;
    wp::float64 var_1605;
    wp::float64 var_1606;
    wp::float64 var_1607;
    wp::float64 var_1608;
    wp::float64 var_1609;
    wp::mat_t<3, 3, wp::float64>* var_1610;
    wp::float64* var_1611;
    wp::float64 var_1612;
    wp::float64 var_1613;
    wp::float64* var_1614;
    const wp::int32 var_1615 = 2;
    const wp::int32 var_1616 = 0;
    bool var_1617;
    wp::float64 var_1618;
    wp::float64 var_1619;
    wp::float64 var_1620;
    wp::float64 var_1621;
    wp::float64 var_1622;
    wp::float64 var_1623;
    wp::mat_t<3, 3, wp::float64>* var_1624;
    wp::float64* var_1625;
    wp::float64 var_1626;
    wp::float64 var_1627;
    wp::float64* var_1628;
    const wp::int32 var_1629 = 1;
    const wp::int32 var_1630 = 0;
    const wp::int32 var_1631 = 0;
    bool var_1632;
    wp::float64 var_1633;
    wp::float64 var_1634;
    wp::float64 var_1635;
    wp::float64 var_1636;
    wp::float64 var_1637;
    wp::float64 var_1638;
    wp::mat_t<3, 3, wp::float64>* var_1639;
    wp::float64* var_1640;
    wp::float64 var_1641;
    wp::float64 var_1642;
    wp::float64* var_1643;
    const wp::int32 var_1644 = 1;
    const wp::int32 var_1645 = 0;
    bool var_1646;
    wp::float64 var_1647;
    wp::float64 var_1648;
    wp::float64 var_1649;
    wp::float64 var_1650;
    wp::float64 var_1651;
    wp::float64 var_1652;
    wp::mat_t<3, 3, wp::float64>* var_1653;
    wp::float64* var_1654;
    wp::float64 var_1655;
    wp::float64 var_1656;
    wp::float64* var_1657;
    const wp::int32 var_1658 = 2;
    const wp::int32 var_1659 = 0;
    bool var_1660;
    wp::float64 var_1661;
    wp::float64 var_1662;
    wp::float64 var_1663;
    wp::float64 var_1664;
    wp::float64 var_1665;
    wp::float64 var_1666;
    wp::mat_t<3, 3, wp::float64>* var_1667;
    wp::float64* var_1668;
    wp::float64 var_1669;
    wp::float64 var_1670;
    wp::float64* var_1671;
    const wp::int32 var_1672 = 2;
    const wp::int32 var_1673 = 0;
    const wp::int32 var_1674 = 0;
    bool var_1675;
    wp::float64 var_1676;
    wp::float64 var_1677;
    wp::float64 var_1678;
    wp::float64 var_1679;
    wp::float64 var_1680;
    wp::float64 var_1681;
    wp::mat_t<3, 3, wp::float64>* var_1682;
    wp::float64* var_1683;
    wp::float64 var_1684;
    wp::float64 var_1685;
    wp::float64* var_1686;
    const wp::int32 var_1687 = 1;
    const wp::int32 var_1688 = 0;
    bool var_1689;
    wp::float64 var_1690;
    wp::float64 var_1691;
    wp::float64 var_1692;
    wp::float64 var_1693;
    wp::float64 var_1694;
    wp::float64 var_1695;
    wp::mat_t<3, 3, wp::float64>* var_1696;
    wp::float64* var_1697;
    wp::float64 var_1698;
    wp::float64 var_1699;
    wp::float64* var_1700;
    const wp::int32 var_1701 = 2;
    const wp::int32 var_1702 = 0;
    bool var_1703;
    wp::float64 var_1704;
    wp::float64 var_1705;
    wp::float64 var_1706;
    wp::float64 var_1707;
    wp::float64 var_1708;
    wp::float64 var_1709;
    wp::mat_t<3, 3, wp::float64>* var_1710;
    wp::float64* var_1711;
    wp::float64 var_1712;
    wp::float64 var_1713;
    wp::float64* var_1714;
    const wp::int32 var_1715 = 0;
    bool var_1716;
    wp::float64 var_1717;
    wp::float64 var_1718;
    wp::float64 var_1719;
    wp::float64 var_1720;
    wp::float64 var_1721;
    wp::float64 var_1722;
    wp::float64* var_1723;
    wp::float64 var_1724;
    wp::float64 var_1725;
    wp::float64 var_1726;
    wp::float64* var_1727;
    wp::float64 var_1728;
    wp::float64 var_1729;
    wp::float64 var_1730;
    wp::float64* var_1731;
    wp::float64 var_1732;
    wp::float64 var_1733;
    wp::vec_t<3, wp::float64> var_1734;
    wp::vec_t<3, wp::float64> var_1735;
    wp::vec_t<3, wp::float64>* var_1736;
    wp::vec_t<3, wp::float64> var_1737;
    wp::vec_t<3, wp::float64> var_1738;
    bool var_1739;
    wp::vec_t<3, wp::float64> var_1740;
    wp::float64 var_1741;
    wp::float64 var_1742;
    wp::vec_t<3, wp::float64> var_1743;
    wp::vec_t<3, wp::float64> var_1744;
    wp::float64 var_1745;
    wp::vec_t<3, wp::float64> var_1746;
    wp::vec_t<3, wp::float64> var_1747;
    wp::int32 var_1748;
    wp::int32 var_1749;
    const wp::int32 var_1750 = 7;
    const wp::int32 var_1751 = 3;
    wp::int32 var_1752;
    const wp::int32 var_1753 = 3;
    wp::int32 var_1754;
    const wp::float32 var_1755 = 1.0;
    const wp::float32 var_1756 = 6.0;
    wp::float32 var_1757;
    wp::float64 var_1758;
    wp::vec_t<3, wp::float64> var_1759;
    const wp::float32 var_1760 = 2.0;
    const wp::float32 var_1761 = 3.0;
    wp::float32 var_1762;
    wp::float64 var_1763;
    wp::mat_t<3, 3, wp::float64> var_1764;
    wp::float64 var_1765;
    wp::float64 var_1766;
    const wp::int32 var_1767 = 1;
    bool var_1768;
    wp::mat_t<3, 3, wp::float64> var_1769;
    wp::float64 var_1770;
    wp::float64 var_1771;
    const wp::int32 var_1772 = 2;
    bool var_1773;
    wp::mat_t<3, 3, wp::float64> var_1774;
    wp::float64 var_1775;
    wp::float64 var_1776;
    wp::mat_t<3, 3, wp::float64> var_1777;
    wp::float64 var_1778;
    wp::mat_t<3, 3, wp::float64> var_1779;
    wp::float64 var_1780;
    wp::mat_t<3, 3, wp::float64> var_1781;
    wp::vec_t<3, wp::float64> var_1782;
    wp::mat_t<3, 3, wp::float64> var_1783;
    wp::vec_t<3, wp::float64> var_1784;
    wp::mat_t<3, 3, wp::float64> var_1785;
    wp::vec_t<3, wp::float64> var_1786;
    wp::mat_t<3, 3, wp::float64> var_1787;
    wp::vec_t<3, wp::float64> var_1788;
    wp::vec_t<3, wp::float64> var_1789;
    Signed_7e3cff60 var_1790;
    const wp::int32 var_1791 = 1;
    wp::int32* var_1792;
    wp::int32 var_1793;
    wp::int32 var_1794;
    wp::float64* var_1795;
    wp::float64 var_1796;
    bool var_1797;
    wp::float64 var_1798;
    const bool var_1799 = true;
    wp::vec_t<3, wp::float64>* var_1800;
    wp::vec_t<3, wp::float64> var_1801;
    wp::vec_t<3, wp::float64> var_1802;
    wp::float64* var_1803;
    wp::float64 var_1804;
    wp::float64 var_1805;
    wp::float64 var_1806;
    wp::float64 var_1807;
    wp::float64 var_1808;
    wp::vec_t<3, wp::float64> var_1809;
    wp::float64 var_1810;
    wp::vec_t<3, wp::float64> var_1811;
    wp::vec_t<3, wp::float64> var_1812;
    wp::float64 var_1813;
    wp::float64 var_1814;
    wp::vec_t<3, wp::float64> var_1815;
    wp::float64 var_1816;
    bool var_1817;
    wp::float64 var_1818;
    wp::float64 var_1819;
    wp::float64 var_1820;
    wp::float64 var_1821;
    wp::float64 var_1822;
    wp::float64 var_1823;
    wp::float64 var_1824;
    wp::vec_t<3, wp::float64> var_1825;
    wp::vec_t<3, wp::float64> var_1826;
    wp::vec_t<3, wp::float64> var_1827;
    wp::vec_t<3, wp::float64> var_1828;
    wp::vec_t<3, wp::float64> var_1829;
    const wp::int32 var_1830 = 0;
    const wp::int32 var_1831 = 0;
    const wp::int32 var_1832 = 0;
    bool var_1833;
    wp::float64 var_1834;
    wp::float64 var_1835;
    wp::float64 var_1836;
    wp::float64 var_1837;
    wp::float64 var_1838;
    wp::float64 var_1839;
    wp::mat_t<3, 3, wp::float64>* var_1840;
    wp::float64* var_1841;
    wp::float64 var_1842;
    wp::float64 var_1843;
    wp::float64* var_1844;
    const wp::int32 var_1845 = 1;
    const wp::int32 var_1846 = 0;
    bool var_1847;
    wp::float64 var_1848;
    wp::float64 var_1849;
    wp::float64 var_1850;
    wp::float64 var_1851;
    wp::float64 var_1852;
    wp::float64 var_1853;
    wp::mat_t<3, 3, wp::float64>* var_1854;
    wp::float64* var_1855;
    wp::float64 var_1856;
    wp::float64 var_1857;
    wp::float64* var_1858;
    const wp::int32 var_1859 = 2;
    const wp::int32 var_1860 = 0;
    bool var_1861;
    wp::float64 var_1862;
    wp::float64 var_1863;
    wp::float64 var_1864;
    wp::float64 var_1865;
    wp::float64 var_1866;
    wp::float64 var_1867;
    wp::mat_t<3, 3, wp::float64>* var_1868;
    wp::float64* var_1869;
    wp::float64 var_1870;
    wp::float64 var_1871;
    wp::float64* var_1872;
    const wp::int32 var_1873 = 1;
    const wp::int32 var_1874 = 0;
    const wp::int32 var_1875 = 0;
    bool var_1876;
    wp::float64 var_1877;
    wp::float64 var_1878;
    wp::float64 var_1879;
    wp::float64 var_1880;
    wp::float64 var_1881;
    wp::float64 var_1882;
    wp::mat_t<3, 3, wp::float64>* var_1883;
    wp::float64* var_1884;
    wp::float64 var_1885;
    wp::float64 var_1886;
    wp::float64* var_1887;
    const wp::int32 var_1888 = 1;
    const wp::int32 var_1889 = 0;
    bool var_1890;
    wp::float64 var_1891;
    wp::float64 var_1892;
    wp::float64 var_1893;
    wp::float64 var_1894;
    wp::float64 var_1895;
    wp::float64 var_1896;
    wp::mat_t<3, 3, wp::float64>* var_1897;
    wp::float64* var_1898;
    wp::float64 var_1899;
    wp::float64 var_1900;
    wp::float64* var_1901;
    const wp::int32 var_1902 = 2;
    const wp::int32 var_1903 = 0;
    bool var_1904;
    wp::float64 var_1905;
    wp::float64 var_1906;
    wp::float64 var_1907;
    wp::float64 var_1908;
    wp::float64 var_1909;
    wp::float64 var_1910;
    wp::mat_t<3, 3, wp::float64>* var_1911;
    wp::float64* var_1912;
    wp::float64 var_1913;
    wp::float64 var_1914;
    wp::float64* var_1915;
    const wp::int32 var_1916 = 2;
    const wp::int32 var_1917 = 0;
    const wp::int32 var_1918 = 0;
    bool var_1919;
    wp::float64 var_1920;
    wp::float64 var_1921;
    wp::float64 var_1922;
    wp::float64 var_1923;
    wp::float64 var_1924;
    wp::float64 var_1925;
    wp::mat_t<3, 3, wp::float64>* var_1926;
    wp::float64* var_1927;
    wp::float64 var_1928;
    wp::float64 var_1929;
    wp::float64* var_1930;
    const wp::int32 var_1931 = 1;
    const wp::int32 var_1932 = 0;
    bool var_1933;
    wp::float64 var_1934;
    wp::float64 var_1935;
    wp::float64 var_1936;
    wp::float64 var_1937;
    wp::float64 var_1938;
    wp::float64 var_1939;
    wp::mat_t<3, 3, wp::float64>* var_1940;
    wp::float64* var_1941;
    wp::float64 var_1942;
    wp::float64 var_1943;
    wp::float64* var_1944;
    const wp::int32 var_1945 = 2;
    const wp::int32 var_1946 = 0;
    bool var_1947;
    wp::float64 var_1948;
    wp::float64 var_1949;
    wp::float64 var_1950;
    wp::float64 var_1951;
    wp::float64 var_1952;
    wp::float64 var_1953;
    wp::mat_t<3, 3, wp::float64>* var_1954;
    wp::float64* var_1955;
    wp::float64 var_1956;
    wp::float64 var_1957;
    wp::float64* var_1958;
    const wp::int32 var_1959 = 0;
    bool var_1960;
    wp::float64 var_1961;
    wp::float64 var_1962;
    wp::float64 var_1963;
    wp::float64 var_1964;
    wp::float64 var_1965;
    wp::float64 var_1966;
    wp::float64* var_1967;
    wp::float64 var_1968;
    wp::float64 var_1969;
    wp::float64 var_1970;
    wp::float64* var_1971;
    wp::float64 var_1972;
    wp::float64 var_1973;
    wp::float64 var_1974;
    wp::float64* var_1975;
    wp::float64 var_1976;
    wp::float64 var_1977;
    wp::vec_t<3, wp::float64> var_1978;
    wp::vec_t<3, wp::float64> var_1979;
    wp::vec_t<3, wp::float64>* var_1980;
    wp::vec_t<3, wp::float64> var_1981;
    wp::vec_t<3, wp::float64> var_1982;
    bool var_1983;
    wp::vec_t<3, wp::float64> var_1984;
    wp::float64 var_1985;
    wp::float64 var_1986;
    wp::vec_t<3, wp::float64> var_1987;
    wp::vec_t<3, wp::float64> var_1988;
    wp::float64 var_1989;
    wp::vec_t<3, wp::float64> var_1990;
    wp::vec_t<3, wp::float64> var_1991;
    wp::int32 var_1992;
    wp::int32 var_1993;
    const wp::int32 var_1994 = 8;
    const wp::int32 var_1995 = 3;
    wp::int32 var_1996;
    const wp::int32 var_1997 = 3;
    wp::int32 var_1998;
    const wp::float32 var_1999 = 1.0;
    const wp::float32 var_2000 = 6.0;
    wp::float32 var_2001;
    wp::float64 var_2002;
    wp::vec_t<3, wp::float64> var_2003;
    const wp::float32 var_2004 = 2.0;
    const wp::float32 var_2005 = 3.0;
    wp::float32 var_2006;
    wp::float64 var_2007;
    wp::mat_t<3, 3, wp::float64> var_2008;
    wp::float64 var_2009;
    wp::float64 var_2010;
    const wp::int32 var_2011 = 1;
    bool var_2012;
    wp::mat_t<3, 3, wp::float64> var_2013;
    wp::float64 var_2014;
    wp::float64 var_2015;
    const wp::int32 var_2016 = 2;
    bool var_2017;
    wp::mat_t<3, 3, wp::float64> var_2018;
    wp::float64 var_2019;
    wp::float64 var_2020;
    wp::mat_t<3, 3, wp::float64> var_2021;
    wp::float64 var_2022;
    wp::mat_t<3, 3, wp::float64> var_2023;
    wp::float64 var_2024;
    wp::mat_t<3, 3, wp::float64> var_2025;
    wp::vec_t<3, wp::float64> var_2026;
    wp::mat_t<3, 3, wp::float64> var_2027;
    wp::vec_t<3, wp::float64> var_2028;
    wp::mat_t<3, 3, wp::float64> var_2029;
    wp::vec_t<3, wp::float64> var_2030;
    wp::mat_t<3, 3, wp::float64> var_2031;
    wp::vec_t<3, wp::float64> var_2032;
    wp::vec_t<3, wp::float64> var_2033;
    Signed_7e3cff60 var_2034;
    const wp::int32 var_2035 = 1;
    wp::int32* var_2036;
    wp::int32 var_2037;
    wp::int32 var_2038;
    wp::float64* var_2039;
    wp::float64 var_2040;
    bool var_2041;
    wp::float64 var_2042;
    const bool var_2043 = true;
    wp::vec_t<3, wp::float64>* var_2044;
    wp::vec_t<3, wp::float64> var_2045;
    wp::vec_t<3, wp::float64> var_2046;
    wp::float64* var_2047;
    wp::float64 var_2048;
    wp::float64 var_2049;
    wp::float64 var_2050;
    wp::float64 var_2051;
    wp::float64 var_2052;
    wp::vec_t<3, wp::float64> var_2053;
    wp::float64 var_2054;
    wp::vec_t<3, wp::float64> var_2055;
    wp::vec_t<3, wp::float64> var_2056;
    wp::float64 var_2057;
    wp::float64 var_2058;
    wp::vec_t<3, wp::float64> var_2059;
    wp::float64 var_2060;
    bool var_2061;
    wp::float64 var_2062;
    wp::float64 var_2063;
    wp::float64 var_2064;
    wp::float64 var_2065;
    wp::float64 var_2066;
    wp::float64 var_2067;
    wp::float64 var_2068;
    wp::vec_t<3, wp::float64> var_2069;
    wp::vec_t<3, wp::float64> var_2070;
    wp::vec_t<3, wp::float64> var_2071;
    wp::vec_t<3, wp::float64> var_2072;
    wp::vec_t<3, wp::float64> var_2073;
    const wp::int32 var_2074 = 0;
    const wp::int32 var_2075 = 0;
    const wp::int32 var_2076 = 0;
    bool var_2077;
    wp::float64 var_2078;
    wp::float64 var_2079;
    wp::float64 var_2080;
    wp::float64 var_2081;
    wp::float64 var_2082;
    wp::float64 var_2083;
    wp::mat_t<3, 3, wp::float64>* var_2084;
    wp::float64* var_2085;
    wp::float64 var_2086;
    wp::float64 var_2087;
    wp::float64* var_2088;
    const wp::int32 var_2089 = 1;
    const wp::int32 var_2090 = 0;
    bool var_2091;
    wp::float64 var_2092;
    wp::float64 var_2093;
    wp::float64 var_2094;
    wp::float64 var_2095;
    wp::float64 var_2096;
    wp::float64 var_2097;
    wp::mat_t<3, 3, wp::float64>* var_2098;
    wp::float64* var_2099;
    wp::float64 var_2100;
    wp::float64 var_2101;
    wp::float64* var_2102;
    const wp::int32 var_2103 = 2;
    const wp::int32 var_2104 = 0;
    bool var_2105;
    wp::float64 var_2106;
    wp::float64 var_2107;
    wp::float64 var_2108;
    wp::float64 var_2109;
    wp::float64 var_2110;
    wp::float64 var_2111;
    wp::mat_t<3, 3, wp::float64>* var_2112;
    wp::float64* var_2113;
    wp::float64 var_2114;
    wp::float64 var_2115;
    wp::float64* var_2116;
    const wp::int32 var_2117 = 1;
    const wp::int32 var_2118 = 0;
    const wp::int32 var_2119 = 0;
    bool var_2120;
    wp::float64 var_2121;
    wp::float64 var_2122;
    wp::float64 var_2123;
    wp::float64 var_2124;
    wp::float64 var_2125;
    wp::float64 var_2126;
    wp::mat_t<3, 3, wp::float64>* var_2127;
    wp::float64* var_2128;
    wp::float64 var_2129;
    wp::float64 var_2130;
    wp::float64* var_2131;
    const wp::int32 var_2132 = 1;
    const wp::int32 var_2133 = 0;
    bool var_2134;
    wp::float64 var_2135;
    wp::float64 var_2136;
    wp::float64 var_2137;
    wp::float64 var_2138;
    wp::float64 var_2139;
    wp::float64 var_2140;
    wp::mat_t<3, 3, wp::float64>* var_2141;
    wp::float64* var_2142;
    wp::float64 var_2143;
    wp::float64 var_2144;
    wp::float64* var_2145;
    const wp::int32 var_2146 = 2;
    const wp::int32 var_2147 = 0;
    bool var_2148;
    wp::float64 var_2149;
    wp::float64 var_2150;
    wp::float64 var_2151;
    wp::float64 var_2152;
    wp::float64 var_2153;
    wp::float64 var_2154;
    wp::mat_t<3, 3, wp::float64>* var_2155;
    wp::float64* var_2156;
    wp::float64 var_2157;
    wp::float64 var_2158;
    wp::float64* var_2159;
    const wp::int32 var_2160 = 2;
    const wp::int32 var_2161 = 0;
    const wp::int32 var_2162 = 0;
    bool var_2163;
    wp::float64 var_2164;
    wp::float64 var_2165;
    wp::float64 var_2166;
    wp::float64 var_2167;
    wp::float64 var_2168;
    wp::float64 var_2169;
    wp::mat_t<3, 3, wp::float64>* var_2170;
    wp::float64* var_2171;
    wp::float64 var_2172;
    wp::float64 var_2173;
    wp::float64* var_2174;
    const wp::int32 var_2175 = 1;
    const wp::int32 var_2176 = 0;
    bool var_2177;
    wp::float64 var_2178;
    wp::float64 var_2179;
    wp::float64 var_2180;
    wp::float64 var_2181;
    wp::float64 var_2182;
    wp::float64 var_2183;
    wp::mat_t<3, 3, wp::float64>* var_2184;
    wp::float64* var_2185;
    wp::float64 var_2186;
    wp::float64 var_2187;
    wp::float64* var_2188;
    const wp::int32 var_2189 = 2;
    const wp::int32 var_2190 = 0;
    bool var_2191;
    wp::float64 var_2192;
    wp::float64 var_2193;
    wp::float64 var_2194;
    wp::float64 var_2195;
    wp::float64 var_2196;
    wp::float64 var_2197;
    wp::mat_t<3, 3, wp::float64>* var_2198;
    wp::float64* var_2199;
    wp::float64 var_2200;
    wp::float64 var_2201;
    wp::float64* var_2202;
    const wp::int32 var_2203 = 0;
    bool var_2204;
    wp::float64 var_2205;
    wp::float64 var_2206;
    wp::float64 var_2207;
    wp::float64 var_2208;
    wp::float64 var_2209;
    wp::float64 var_2210;
    wp::float64* var_2211;
    wp::float64 var_2212;
    wp::float64 var_2213;
    wp::float64 var_2214;
    wp::float64* var_2215;
    wp::float64 var_2216;
    wp::float64 var_2217;
    wp::float64 var_2218;
    wp::float64* var_2219;
    wp::float64 var_2220;
    wp::float64 var_2221;
    wp::vec_t<3, wp::float64> var_2222;
    wp::vec_t<3, wp::float64> var_2223;
    wp::vec_t<3, wp::float64>* var_2224;
    wp::vec_t<3, wp::float64> var_2225;
    wp::vec_t<3, wp::float64> var_2226;
    bool var_2227;
    wp::vec_t<3, wp::float64> var_2228;
    wp::float64 var_2229;
    wp::float64 var_2230;
    wp::vec_t<3, wp::float64> var_2231;
    wp::vec_t<3, wp::float64> var_2232;
    wp::float64 var_2233;
    wp::vec_t<3, wp::float64> var_2234;
    wp::vec_t<3, wp::float64> var_2235;
    wp::int32 var_2236;
    wp::int32 var_2237;
    const wp::int32 var_2238 = 0;
    wp::mat_t<3, 3, wp::float64>* var_2239;
    wp::vec_t<3, wp::float64> var_2240;
    wp::mat_t<3, 3, wp::float64> var_2241;
    wp::vec_t<3, wp::float64> var_2242;
    wp::vec_t<3, wp::float64> var_2243;
    wp::float64 var_2244;
    wp::float64* var_2245;
    wp::float64 var_2246;
    wp::float64 var_2247;
    const wp::int32 var_2248 = 1;
    wp::mat_t<3, 3, wp::float64>* var_2249;
    wp::vec_t<3, wp::float64> var_2250;
    wp::mat_t<3, 3, wp::float64> var_2251;
    wp::vec_t<3, wp::float64> var_2252;
    wp::vec_t<3, wp::float64> var_2253;
    wp::float64 var_2254;
    wp::float64* var_2255;
    wp::float64 var_2256;
    wp::float64 var_2257;
    const wp::int32 var_2258 = 2;
    wp::mat_t<3, 3, wp::float64>* var_2259;
    wp::vec_t<3, wp::float64> var_2260;
    wp::mat_t<3, 3, wp::float64> var_2261;
    wp::vec_t<3, wp::float64> var_2262;
    wp::vec_t<3, wp::float64> var_2263;
    wp::float64 var_2264;
    wp::float64* var_2265;
    wp::float64 var_2266;
    wp::float64 var_2267;
    //---------
    // forward
    // def evaluate_leaf(mesh:wp.uint64,tri:wp.array2d(dtype=wp.vec3d),B:wp.mat33d,X:wp.mat33d,V:wp.mat33d,A:wp.float64,R:wp.mat33d,T:wp.vec3d,tv:wp.vec3d):       <L 65>
    // r=Value();r.f=wp.mat33d(wp.float64(0.));r.U=wp.float64(0.);r.D=wp.float64(0.);r.W=wp.float64(0.);r.moment=wp.vec3d(wp.float64(0.));r.error=wp.float64(0.);r.queries=1       <L 66>
    var_0 = Value_53a65c4a();
    var_1 = 0.0;
    var_2 = wp::mat_t<3, 3, wp::float64>(var_1);
    var_0.f = var_2;
    var_3 = 0.0;
    var_0.U = var_3;
    var_4 = 0.0;
    var_0.D = var_4;
    var_5 = 0.0;
    var_0.W = var_5;
    var_6 = 0.0;
    var_7 = wp::vec_t<3, wp::float64>(var_6);
    var_0.moment = var_7;
    var_8 = 0.0;
    var_0.error = var_8;
    var_0.queries = var_9;
    // p=B*X;c=(p[0]+p[1]+p[2])/wp.float64(3.);radius=wp.max(wp.length(p[0]-c),wp.max(wp.length(p[1]-c),wp.length(p[2]-c)));sd=signed(mesh,tri,wp.transpose(R)*(c-T));Ar=A*wp.abs(wp.determinant(B))       <L 67>
    var_10 = wp::mul(var_B, var_X);
    var_12 = wp::extract(var_10, var_11);
    var_14 = wp::extract(var_10, var_13);
    var_15 = wp::add(var_12, var_14);
    var_17 = wp::extract(var_10, var_16);
    var_18 = wp::add(var_15, var_17);
    var_19 = 3.0;
    var_20 = wp::div(var_18, var_19);
    var_22 = wp::extract(var_10, var_21);
    var_23 = wp::sub(var_22, var_20);
    var_24 = wp::length(var_23);
    var_26 = wp::extract(var_10, var_25);
    var_27 = wp::sub(var_26, var_20);
    var_28 = wp::length(var_27);
    var_30 = wp::extract(var_10, var_29);
    var_31 = wp::sub(var_30, var_20);
    var_32 = wp::length(var_31);
    var_33 = wp::max(var_28, var_32);
    var_34 = wp::max(var_24, var_33);
    var_35 = wp::transpose(var_R);
    var_36 = wp::sub(var_20, var_T);
    var_37 = wp::mul(var_35, var_36);
    var_38 = signed_0(var_mesh, var_tri, var_37);
    var_39 = wp::determinant(var_B);
    var_40 = wp::abs(var_39);
    var_41 = wp::mul(var_A, var_40);
    // if sd.phi<=radius+wp.float64(2e-9):                                                    <L 68>
    var_42 = &((var_38).phi);
    var_43 = 2e-09;
    var_44 = wp::add(var_34, var_43);
    var_46 = wp::load(var_42);
    var_45 = (var_46 <= var_44);
    if (var_45) {
        // L,H=bisect(B,X);low=wp.mat33d(wp.float64(0.));active=False                         <L 69>
        bisect_0(var_B, var_X, var_47, var_48);
        var_49 = 0.0;
        var_50 = wp::mat_t<3, 3, wp::float64>(var_49);
        // for k in range(9):                                                                 <L 70>
        // block=k//3;point=k%3;local=wp.vec3d(wp.float64(1./6.));local[point]=wp.float64(2./3.);C=B;weight=Ar/wp.float64(3.)       <L 71>
        var_54 = wp::floordiv(var_52, var_53);
        var_56 = wp::mod(var_52, var_55);
        var_59 = wp::div(var_57, var_58);
        var_60 = wp::float64(var_59);
        var_61 = wp::vec_t<3, wp::float64>(var_60);
        var_64 = wp::div(var_62, var_63);
        var_65 = wp::float64(var_64);
        wp::assign_inplace(var_61, var_56, var_65);
        var_66 = wp::copy(var_B);
        var_67 = 3.0;
        var_68 = wp::div(var_41, var_67);
        // if block==1:C=L;weight=Ar/wp.float64(6.)                                           <L 72>
        var_70 = (var_54 == var_69);
        if (var_70) {
            var_71 = wp::copy(var_47);
            var_72 = 6.0;
            var_73 = wp::div(var_41, var_72);
        }
        if (!var_70) {
            // elif block==2:C=H;weight=Ar/wp.float64(6.)                                     <L 73>
            var_75 = (var_54 == var_74);
            if (var_75) {
                var_76 = wp::copy(var_48);
                var_77 = 6.0;
                var_78 = wp::div(var_41, var_77);
            }
            var_79 = wp::where(var_75, var_76, var_66);
            var_80 = wp::where(var_75, var_78, var_68);
        }
        var_81 = wp::where(var_70, var_71, var_79);
        var_82 = wp::where(var_70, var_73, var_80);
        // bary=wp.transpose(C)*local;x=wp.transpose(X)*bary;v=wp.transpose(V)*bary;s=signed(mesh,tri,wp.transpose(R)*(x-T));r.queries+=1       <L 74>
        var_83 = wp::transpose(var_81);
        var_84 = wp::mul(var_83, var_61);
        var_85 = wp::transpose(var_X);
        var_86 = wp::mul(var_85, var_84);
        var_87 = wp::transpose(var_V);
        var_88 = wp::mul(var_87, var_84);
        var_89 = wp::transpose(var_R);
        var_90 = wp::sub(var_86, var_T);
        var_91 = wp::mul(var_89, var_90);
        var_92 = signed_0(var_mesh, var_tri, var_91);
        var_94 = &((var_0).queries);
        var_96 = wp::load(var_94);
        var_95 = wp::add(var_96, var_93);
        var_0.queries = var_95;
        // if s.phi<wp.float64(0.):                                                           <L 75>
        var_97 = &((var_92).phi);
        var_98 = 0.0;
        var_100 = wp::load(var_97);
        var_99 = (var_100 < var_98);
        if (var_99) {
            // active=True;normal=R*s.normal;depth=-s.phi;fn=wp.float64(1e9)*weight*depth;rel=v-tv;tan=rel-wp.dot(rel,normal)*normal;speed=wp.length(tan);fr=wp.vec3d(wp.float64(0.))       <L 76>
            var_102 = &((var_92).normal);
            var_104 = wp::load(var_102);
            var_103 = wp::mul(var_R, var_104);
            var_105 = &((var_92).phi);
            var_107 = wp::load(var_105);
            var_106 = wp::neg(var_107);
            var_108 = 1000000000.0;
            var_109 = wp::mul(var_108, var_82);
            var_110 = wp::mul(var_109, var_106);
            var_111 = wp::sub(var_88, var_tv);
            var_112 = wp::dot(var_111, var_103);
            var_113 = wp::mul(var_112, var_103);
            var_114 = wp::sub(var_111, var_113);
            var_115 = wp::length(var_114);
            var_116 = 0.0;
            var_117 = wp::vec_t<3, wp::float64>(var_116);
            // if speed>wp.float64(1e-30):fr=-wp.float64(.2)*fn*wp.tanh(speed/wp.float64(.001))*tan/speed       <L 77>
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
            // f=fn*normal+fr                                                                 <L 78>
            var_130 = wp::mul(var_110, var_103);
            var_131 = wp::add(var_130, var_129);
            // for u in range(3):                                                             <L 79>
            // for v0 in range(3):                                                            <L 80>
            // if block==0:low[u,v0]+=bary[u]*f[v0]                                           <L 81>
            var_135 = (var_54 == var_134);
            if (var_135) {
                var_136 = wp::extract(var_84, var_132);
                var_137 = wp::extract(var_131, var_133);
                var_138 = wp::mul(var_136, var_137);
                wp::add_inplace(var_50, var_132, var_133, var_138);
            }
            if (!var_135) {
                // else:r.f[u,v0]+=bary[u]*f[v0]                                              <L 82>
                var_139 = wp::extract(var_84, var_132);
                var_140 = wp::extract(var_131, var_133);
                var_141 = wp::mul(var_139, var_140);
                var_142 = &((var_0).f);
                var_143 = wp::indexref(var_142, var_132, var_133);
                var_144 = wp::load(var_143);
                var_145 = wp::add(var_144, var_141);
                var_146 = wp::indexref(var_142, var_132, var_133);
                wp::store(var_146, var_145);
            }
            // if block==0:low[u,v0]+=bary[u]*f[v0]                                           <L 81>
            var_149 = (var_54 == var_148);
            if (var_149) {
                var_150 = wp::extract(var_84, var_132);
                var_151 = wp::extract(var_131, var_147);
                var_152 = wp::mul(var_150, var_151);
                wp::add_inplace(var_50, var_132, var_147, var_152);
            }
            if (!var_149) {
                // else:r.f[u,v0]+=bary[u]*f[v0]                                              <L 82>
                var_153 = wp::extract(var_84, var_132);
                var_154 = wp::extract(var_131, var_147);
                var_155 = wp::mul(var_153, var_154);
                var_156 = &((var_0).f);
                var_157 = wp::indexref(var_156, var_132, var_147);
                var_158 = wp::load(var_157);
                var_159 = wp::add(var_158, var_155);
                var_160 = wp::indexref(var_156, var_132, var_147);
                wp::store(var_160, var_159);
            }
            // if block==0:low[u,v0]+=bary[u]*f[v0]                                           <L 81>
            var_163 = (var_54 == var_162);
            if (var_163) {
                var_164 = wp::extract(var_84, var_132);
                var_165 = wp::extract(var_131, var_161);
                var_166 = wp::mul(var_164, var_165);
                wp::add_inplace(var_50, var_132, var_161, var_166);
            }
            if (!var_163) {
                // else:r.f[u,v0]+=bary[u]*f[v0]                                              <L 82>
                var_167 = wp::extract(var_84, var_132);
                var_168 = wp::extract(var_131, var_161);
                var_169 = wp::mul(var_167, var_168);
                var_170 = &((var_0).f);
                var_171 = wp::indexref(var_170, var_132, var_161);
                var_172 = wp::load(var_171);
                var_173 = wp::add(var_172, var_169);
                var_174 = wp::indexref(var_170, var_132, var_161);
                wp::store(var_174, var_173);
            }
            // for v0 in range(3):                                                            <L 80>
            // if block==0:low[u,v0]+=bary[u]*f[v0]                                           <L 81>
            var_178 = (var_54 == var_177);
            if (var_178) {
                var_179 = wp::extract(var_84, var_175);
                var_180 = wp::extract(var_131, var_176);
                var_181 = wp::mul(var_179, var_180);
                wp::add_inplace(var_50, var_175, var_176, var_181);
            }
            if (!var_178) {
                // else:r.f[u,v0]+=bary[u]*f[v0]                                              <L 82>
                var_182 = wp::extract(var_84, var_175);
                var_183 = wp::extract(var_131, var_176);
                var_184 = wp::mul(var_182, var_183);
                var_185 = &((var_0).f);
                var_186 = wp::indexref(var_185, var_175, var_176);
                var_187 = wp::load(var_186);
                var_188 = wp::add(var_187, var_184);
                var_189 = wp::indexref(var_185, var_175, var_176);
                wp::store(var_189, var_188);
            }
            // if block==0:low[u,v0]+=bary[u]*f[v0]                                           <L 81>
            var_192 = (var_54 == var_191);
            if (var_192) {
                var_193 = wp::extract(var_84, var_175);
                var_194 = wp::extract(var_131, var_190);
                var_195 = wp::mul(var_193, var_194);
                wp::add_inplace(var_50, var_175, var_190, var_195);
            }
            if (!var_192) {
                // else:r.f[u,v0]+=bary[u]*f[v0]                                              <L 82>
                var_196 = wp::extract(var_84, var_175);
                var_197 = wp::extract(var_131, var_190);
                var_198 = wp::mul(var_196, var_197);
                var_199 = &((var_0).f);
                var_200 = wp::indexref(var_199, var_175, var_190);
                var_201 = wp::load(var_200);
                var_202 = wp::add(var_201, var_198);
                var_203 = wp::indexref(var_199, var_175, var_190);
                wp::store(var_203, var_202);
            }
            // if block==0:low[u,v0]+=bary[u]*f[v0]                                           <L 81>
            var_206 = (var_54 == var_205);
            if (var_206) {
                var_207 = wp::extract(var_84, var_175);
                var_208 = wp::extract(var_131, var_204);
                var_209 = wp::mul(var_207, var_208);
                wp::add_inplace(var_50, var_175, var_204, var_209);
            }
            if (!var_206) {
                // else:r.f[u,v0]+=bary[u]*f[v0]                                              <L 82>
                var_210 = wp::extract(var_84, var_175);
                var_211 = wp::extract(var_131, var_204);
                var_212 = wp::mul(var_210, var_211);
                var_213 = &((var_0).f);
                var_214 = wp::indexref(var_213, var_175, var_204);
                var_215 = wp::load(var_214);
                var_216 = wp::add(var_215, var_212);
                var_217 = wp::indexref(var_213, var_175, var_204);
                wp::store(var_217, var_216);
            }
            // for v0 in range(3):                                                            <L 80>
            // if block==0:low[u,v0]+=bary[u]*f[v0]                                           <L 81>
            var_221 = (var_54 == var_220);
            if (var_221) {
                var_222 = wp::extract(var_84, var_218);
                var_223 = wp::extract(var_131, var_219);
                var_224 = wp::mul(var_222, var_223);
                wp::add_inplace(var_50, var_218, var_219, var_224);
            }
            if (!var_221) {
                // else:r.f[u,v0]+=bary[u]*f[v0]                                              <L 82>
                var_225 = wp::extract(var_84, var_218);
                var_226 = wp::extract(var_131, var_219);
                var_227 = wp::mul(var_225, var_226);
                var_228 = &((var_0).f);
                var_229 = wp::indexref(var_228, var_218, var_219);
                var_230 = wp::load(var_229);
                var_231 = wp::add(var_230, var_227);
                var_232 = wp::indexref(var_228, var_218, var_219);
                wp::store(var_232, var_231);
            }
            // if block==0:low[u,v0]+=bary[u]*f[v0]                                           <L 81>
            var_235 = (var_54 == var_234);
            if (var_235) {
                var_236 = wp::extract(var_84, var_218);
                var_237 = wp::extract(var_131, var_233);
                var_238 = wp::mul(var_236, var_237);
                wp::add_inplace(var_50, var_218, var_233, var_238);
            }
            if (!var_235) {
                // else:r.f[u,v0]+=bary[u]*f[v0]                                              <L 82>
                var_239 = wp::extract(var_84, var_218);
                var_240 = wp::extract(var_131, var_233);
                var_241 = wp::mul(var_239, var_240);
                var_242 = &((var_0).f);
                var_243 = wp::indexref(var_242, var_218, var_233);
                var_244 = wp::load(var_243);
                var_245 = wp::add(var_244, var_241);
                var_246 = wp::indexref(var_242, var_218, var_233);
                wp::store(var_246, var_245);
            }
            // if block==0:low[u,v0]+=bary[u]*f[v0]                                           <L 81>
            var_249 = (var_54 == var_248);
            if (var_249) {
                var_250 = wp::extract(var_84, var_218);
                var_251 = wp::extract(var_131, var_247);
                var_252 = wp::mul(var_250, var_251);
                wp::add_inplace(var_50, var_218, var_247, var_252);
            }
            if (!var_249) {
                // else:r.f[u,v0]+=bary[u]*f[v0]                                              <L 82>
                var_253 = wp::extract(var_84, var_218);
                var_254 = wp::extract(var_131, var_247);
                var_255 = wp::mul(var_253, var_254);
                var_256 = &((var_0).f);
                var_257 = wp::indexref(var_256, var_218, var_247);
                var_258 = wp::load(var_257);
                var_259 = wp::add(var_258, var_255);
                var_260 = wp::indexref(var_256, var_218, var_247);
                wp::store(var_260, var_259);
            }
            // if block>0:r.U+=wp.float64(.5)*wp.float64(1e9)*weight*depth*depth;r.D-=wp.dot(fr,rel);r.W+=wp.dot(f,tv);r.moment+=wp.cross(x-T,f)       <L 83>
            var_262 = (var_54 > var_261);
            if (var_262) {
                var_263 = 0.5;
                var_264 = 1000000000.0;
                var_265 = wp::mul(var_263, var_264);
                var_266 = wp::mul(var_265, var_82);
                var_267 = wp::mul(var_266, var_106);
                var_268 = wp::mul(var_267, var_106);
                var_269 = &((var_0).U);
                var_271 = wp::load(var_269);
                var_270 = wp::add(var_271, var_268);
                var_0.U = var_270;
                var_272 = wp::dot(var_129, var_111);
                var_273 = &((var_0).D);
                var_275 = wp::load(var_273);
                var_274 = wp::sub(var_275, var_272);
                var_0.D = var_274;
                var_276 = wp::dot(var_131, var_tv);
                var_277 = &((var_0).W);
                var_279 = wp::load(var_277);
                var_278 = wp::add(var_279, var_276);
                var_0.W = var_278;
                var_280 = wp::sub(var_86, var_T);
                var_281 = wp::cross(var_280, var_131);
                var_282 = &((var_0).moment);
                var_284 = wp::load(var_282);
                var_283 = wp::add(var_284, var_281);
                var_0.moment = var_283;
            }
        }
        var_285 = wp::where(var_99, var_101, var_51);
        // block=k//3;point=k%3;local=wp.vec3d(wp.float64(1./6.));local[point]=wp.float64(2./3.);C=B;weight=Ar/wp.float64(3.)       <L 71>
        var_288 = wp::floordiv(var_286, var_287);
        var_290 = wp::mod(var_286, var_289);
        var_293 = wp::div(var_291, var_292);
        var_294 = wp::float64(var_293);
        var_295 = wp::vec_t<3, wp::float64>(var_294);
        var_298 = wp::div(var_296, var_297);
        var_299 = wp::float64(var_298);
        wp::assign_inplace(var_295, var_290, var_299);
        var_300 = wp::copy(var_B);
        var_301 = 3.0;
        var_302 = wp::div(var_41, var_301);
        // if block==1:C=L;weight=Ar/wp.float64(6.)                                           <L 72>
        var_304 = (var_288 == var_303);
        if (var_304) {
            var_305 = wp::copy(var_47);
            var_306 = 6.0;
            var_307 = wp::div(var_41, var_306);
        }
        if (!var_304) {
            // elif block==2:C=H;weight=Ar/wp.float64(6.)                                     <L 73>
            var_309 = (var_288 == var_308);
            if (var_309) {
                var_310 = wp::copy(var_48);
                var_311 = 6.0;
                var_312 = wp::div(var_41, var_311);
            }
            var_313 = wp::where(var_309, var_310, var_300);
            var_314 = wp::where(var_309, var_312, var_302);
        }
        var_315 = wp::where(var_304, var_305, var_313);
        var_316 = wp::where(var_304, var_307, var_314);
        // bary=wp.transpose(C)*local;x=wp.transpose(X)*bary;v=wp.transpose(V)*bary;s=signed(mesh,tri,wp.transpose(R)*(x-T));r.queries+=1       <L 74>
        var_317 = wp::transpose(var_315);
        var_318 = wp::mul(var_317, var_295);
        var_319 = wp::transpose(var_X);
        var_320 = wp::mul(var_319, var_318);
        var_321 = wp::transpose(var_V);
        var_322 = wp::mul(var_321, var_318);
        var_323 = wp::transpose(var_R);
        var_324 = wp::sub(var_320, var_T);
        var_325 = wp::mul(var_323, var_324);
        var_326 = signed_0(var_mesh, var_tri, var_325);
        var_328 = &((var_0).queries);
        var_330 = wp::load(var_328);
        var_329 = wp::add(var_330, var_327);
        var_0.queries = var_329;
        // if s.phi<wp.float64(0.):                                                           <L 75>
        var_331 = &((var_326).phi);
        var_332 = 0.0;
        var_334 = wp::load(var_331);
        var_333 = (var_334 < var_332);
        if (var_333) {
            // active=True;normal=R*s.normal;depth=-s.phi;fn=wp.float64(1e9)*weight*depth;rel=v-tv;tan=rel-wp.dot(rel,normal)*normal;speed=wp.length(tan);fr=wp.vec3d(wp.float64(0.))       <L 76>
            var_336 = &((var_326).normal);
            var_338 = wp::load(var_336);
            var_337 = wp::mul(var_R, var_338);
            var_339 = &((var_326).phi);
            var_341 = wp::load(var_339);
            var_340 = wp::neg(var_341);
            var_342 = 1000000000.0;
            var_343 = wp::mul(var_342, var_316);
            var_344 = wp::mul(var_343, var_340);
            var_345 = wp::sub(var_322, var_tv);
            var_346 = wp::dot(var_345, var_337);
            var_347 = wp::mul(var_346, var_337);
            var_348 = wp::sub(var_345, var_347);
            var_349 = wp::length(var_348);
            var_350 = 0.0;
            var_351 = wp::vec_t<3, wp::float64>(var_350);
            // if speed>wp.float64(1e-30):fr=-wp.float64(.2)*fn*wp.tanh(speed/wp.float64(.001))*tan/speed       <L 77>
            var_352 = 1e-30;
            var_353 = (var_349 > var_352);
            if (var_353) {
                var_354 = 0.2;
                var_355 = wp::neg(var_354);
                var_356 = wp::mul(var_355, var_344);
                var_357 = 0.001;
                var_358 = wp::div(var_349, var_357);
                var_359 = wp::tanh(var_358);
                var_360 = wp::mul(var_356, var_359);
                var_361 = wp::mul(var_360, var_348);
                var_362 = wp::div(var_361, var_349);
            }
            var_363 = wp::where(var_353, var_362, var_351);
            // f=fn*normal+fr                                                                 <L 78>
            var_364 = wp::mul(var_344, var_337);
            var_365 = wp::add(var_364, var_363);
            // for u in range(3):                                                             <L 79>
            // for v0 in range(3):                                                            <L 80>
            // if block==0:low[u,v0]+=bary[u]*f[v0]                                           <L 81>
            var_369 = (var_288 == var_368);
            if (var_369) {
                var_370 = wp::extract(var_318, var_366);
                var_371 = wp::extract(var_365, var_367);
                var_372 = wp::mul(var_370, var_371);
                wp::add_inplace(var_50, var_366, var_367, var_372);
            }
            if (!var_369) {
                // else:r.f[u,v0]+=bary[u]*f[v0]                                              <L 82>
                var_373 = wp::extract(var_318, var_366);
                var_374 = wp::extract(var_365, var_367);
                var_375 = wp::mul(var_373, var_374);
                var_376 = &((var_0).f);
                var_377 = wp::indexref(var_376, var_366, var_367);
                var_378 = wp::load(var_377);
                var_379 = wp::add(var_378, var_375);
                var_380 = wp::indexref(var_376, var_366, var_367);
                wp::store(var_380, var_379);
            }
            // if block==0:low[u,v0]+=bary[u]*f[v0]                                           <L 81>
            var_383 = (var_288 == var_382);
            if (var_383) {
                var_384 = wp::extract(var_318, var_366);
                var_385 = wp::extract(var_365, var_381);
                var_386 = wp::mul(var_384, var_385);
                wp::add_inplace(var_50, var_366, var_381, var_386);
            }
            if (!var_383) {
                // else:r.f[u,v0]+=bary[u]*f[v0]                                              <L 82>
                var_387 = wp::extract(var_318, var_366);
                var_388 = wp::extract(var_365, var_381);
                var_389 = wp::mul(var_387, var_388);
                var_390 = &((var_0).f);
                var_391 = wp::indexref(var_390, var_366, var_381);
                var_392 = wp::load(var_391);
                var_393 = wp::add(var_392, var_389);
                var_394 = wp::indexref(var_390, var_366, var_381);
                wp::store(var_394, var_393);
            }
            // if block==0:low[u,v0]+=bary[u]*f[v0]                                           <L 81>
            var_397 = (var_288 == var_396);
            if (var_397) {
                var_398 = wp::extract(var_318, var_366);
                var_399 = wp::extract(var_365, var_395);
                var_400 = wp::mul(var_398, var_399);
                wp::add_inplace(var_50, var_366, var_395, var_400);
            }
            if (!var_397) {
                // else:r.f[u,v0]+=bary[u]*f[v0]                                              <L 82>
                var_401 = wp::extract(var_318, var_366);
                var_402 = wp::extract(var_365, var_395);
                var_403 = wp::mul(var_401, var_402);
                var_404 = &((var_0).f);
                var_405 = wp::indexref(var_404, var_366, var_395);
                var_406 = wp::load(var_405);
                var_407 = wp::add(var_406, var_403);
                var_408 = wp::indexref(var_404, var_366, var_395);
                wp::store(var_408, var_407);
            }
            // for v0 in range(3):                                                            <L 80>
            // if block==0:low[u,v0]+=bary[u]*f[v0]                                           <L 81>
            var_412 = (var_288 == var_411);
            if (var_412) {
                var_413 = wp::extract(var_318, var_409);
                var_414 = wp::extract(var_365, var_410);
                var_415 = wp::mul(var_413, var_414);
                wp::add_inplace(var_50, var_409, var_410, var_415);
            }
            if (!var_412) {
                // else:r.f[u,v0]+=bary[u]*f[v0]                                              <L 82>
                var_416 = wp::extract(var_318, var_409);
                var_417 = wp::extract(var_365, var_410);
                var_418 = wp::mul(var_416, var_417);
                var_419 = &((var_0).f);
                var_420 = wp::indexref(var_419, var_409, var_410);
                var_421 = wp::load(var_420);
                var_422 = wp::add(var_421, var_418);
                var_423 = wp::indexref(var_419, var_409, var_410);
                wp::store(var_423, var_422);
            }
            // if block==0:low[u,v0]+=bary[u]*f[v0]                                           <L 81>
            var_426 = (var_288 == var_425);
            if (var_426) {
                var_427 = wp::extract(var_318, var_409);
                var_428 = wp::extract(var_365, var_424);
                var_429 = wp::mul(var_427, var_428);
                wp::add_inplace(var_50, var_409, var_424, var_429);
            }
            if (!var_426) {
                // else:r.f[u,v0]+=bary[u]*f[v0]                                              <L 82>
                var_430 = wp::extract(var_318, var_409);
                var_431 = wp::extract(var_365, var_424);
                var_432 = wp::mul(var_430, var_431);
                var_433 = &((var_0).f);
                var_434 = wp::indexref(var_433, var_409, var_424);
                var_435 = wp::load(var_434);
                var_436 = wp::add(var_435, var_432);
                var_437 = wp::indexref(var_433, var_409, var_424);
                wp::store(var_437, var_436);
            }
            // if block==0:low[u,v0]+=bary[u]*f[v0]                                           <L 81>
            var_440 = (var_288 == var_439);
            if (var_440) {
                var_441 = wp::extract(var_318, var_409);
                var_442 = wp::extract(var_365, var_438);
                var_443 = wp::mul(var_441, var_442);
                wp::add_inplace(var_50, var_409, var_438, var_443);
            }
            if (!var_440) {
                // else:r.f[u,v0]+=bary[u]*f[v0]                                              <L 82>
                var_444 = wp::extract(var_318, var_409);
                var_445 = wp::extract(var_365, var_438);
                var_446 = wp::mul(var_444, var_445);
                var_447 = &((var_0).f);
                var_448 = wp::indexref(var_447, var_409, var_438);
                var_449 = wp::load(var_448);
                var_450 = wp::add(var_449, var_446);
                var_451 = wp::indexref(var_447, var_409, var_438);
                wp::store(var_451, var_450);
            }
            // for v0 in range(3):                                                            <L 80>
            // if block==0:low[u,v0]+=bary[u]*f[v0]                                           <L 81>
            var_455 = (var_288 == var_454);
            if (var_455) {
                var_456 = wp::extract(var_318, var_452);
                var_457 = wp::extract(var_365, var_453);
                var_458 = wp::mul(var_456, var_457);
                wp::add_inplace(var_50, var_452, var_453, var_458);
            }
            if (!var_455) {
                // else:r.f[u,v0]+=bary[u]*f[v0]                                              <L 82>
                var_459 = wp::extract(var_318, var_452);
                var_460 = wp::extract(var_365, var_453);
                var_461 = wp::mul(var_459, var_460);
                var_462 = &((var_0).f);
                var_463 = wp::indexref(var_462, var_452, var_453);
                var_464 = wp::load(var_463);
                var_465 = wp::add(var_464, var_461);
                var_466 = wp::indexref(var_462, var_452, var_453);
                wp::store(var_466, var_465);
            }
            // if block==0:low[u,v0]+=bary[u]*f[v0]                                           <L 81>
            var_469 = (var_288 == var_468);
            if (var_469) {
                var_470 = wp::extract(var_318, var_452);
                var_471 = wp::extract(var_365, var_467);
                var_472 = wp::mul(var_470, var_471);
                wp::add_inplace(var_50, var_452, var_467, var_472);
            }
            if (!var_469) {
                // else:r.f[u,v0]+=bary[u]*f[v0]                                              <L 82>
                var_473 = wp::extract(var_318, var_452);
                var_474 = wp::extract(var_365, var_467);
                var_475 = wp::mul(var_473, var_474);
                var_476 = &((var_0).f);
                var_477 = wp::indexref(var_476, var_452, var_467);
                var_478 = wp::load(var_477);
                var_479 = wp::add(var_478, var_475);
                var_480 = wp::indexref(var_476, var_452, var_467);
                wp::store(var_480, var_479);
            }
            // if block==0:low[u,v0]+=bary[u]*f[v0]                                           <L 81>
            var_483 = (var_288 == var_482);
            if (var_483) {
                var_484 = wp::extract(var_318, var_452);
                var_485 = wp::extract(var_365, var_481);
                var_486 = wp::mul(var_484, var_485);
                wp::add_inplace(var_50, var_452, var_481, var_486);
            }
            if (!var_483) {
                // else:r.f[u,v0]+=bary[u]*f[v0]                                              <L 82>
                var_487 = wp::extract(var_318, var_452);
                var_488 = wp::extract(var_365, var_481);
                var_489 = wp::mul(var_487, var_488);
                var_490 = &((var_0).f);
                var_491 = wp::indexref(var_490, var_452, var_481);
                var_492 = wp::load(var_491);
                var_493 = wp::add(var_492, var_489);
                var_494 = wp::indexref(var_490, var_452, var_481);
                wp::store(var_494, var_493);
            }
            // if block>0:r.U+=wp.float64(.5)*wp.float64(1e9)*weight*depth*depth;r.D-=wp.dot(fr,rel);r.W+=wp.dot(f,tv);r.moment+=wp.cross(x-T,f)       <L 83>
            var_496 = (var_288 > var_495);
            if (var_496) {
                var_497 = 0.5;
                var_498 = 1000000000.0;
                var_499 = wp::mul(var_497, var_498);
                var_500 = wp::mul(var_499, var_316);
                var_501 = wp::mul(var_500, var_340);
                var_502 = wp::mul(var_501, var_340);
                var_503 = &((var_0).U);
                var_505 = wp::load(var_503);
                var_504 = wp::add(var_505, var_502);
                var_0.U = var_504;
                var_506 = wp::dot(var_363, var_345);
                var_507 = &((var_0).D);
                var_509 = wp::load(var_507);
                var_508 = wp::sub(var_509, var_506);
                var_0.D = var_508;
                var_510 = wp::dot(var_365, var_tv);
                var_511 = &((var_0).W);
                var_513 = wp::load(var_511);
                var_512 = wp::add(var_513, var_510);
                var_0.W = var_512;
                var_514 = wp::sub(var_320, var_T);
                var_515 = wp::cross(var_514, var_365);
                var_516 = &((var_0).moment);
                var_518 = wp::load(var_516);
                var_517 = wp::add(var_518, var_515);
                var_0.moment = var_517;
            }
        }
        var_519 = wp::where(var_333, var_335, var_285);
        var_520 = wp::where(var_333, var_337, var_103);
        var_521 = wp::where(var_333, var_340, var_106);
        var_522 = wp::where(var_333, var_344, var_110);
        var_523 = wp::where(var_333, var_345, var_111);
        var_524 = wp::where(var_333, var_348, var_114);
        var_525 = wp::where(var_333, var_349, var_115);
        var_526 = wp::where(var_333, var_363, var_129);
        var_527 = wp::where(var_333, var_365, var_131);
        var_528 = wp::where(var_333, var_452, var_218);
        var_529 = wp::where(var_333, var_481, var_247);
        // block=k//3;point=k%3;local=wp.vec3d(wp.float64(1./6.));local[point]=wp.float64(2./3.);C=B;weight=Ar/wp.float64(3.)       <L 71>
        var_532 = wp::floordiv(var_530, var_531);
        var_534 = wp::mod(var_530, var_533);
        var_537 = wp::div(var_535, var_536);
        var_538 = wp::float64(var_537);
        var_539 = wp::vec_t<3, wp::float64>(var_538);
        var_542 = wp::div(var_540, var_541);
        var_543 = wp::float64(var_542);
        wp::assign_inplace(var_539, var_534, var_543);
        var_544 = wp::copy(var_B);
        var_545 = 3.0;
        var_546 = wp::div(var_41, var_545);
        // if block==1:C=L;weight=Ar/wp.float64(6.)                                           <L 72>
        var_548 = (var_532 == var_547);
        if (var_548) {
            var_549 = wp::copy(var_47);
            var_550 = 6.0;
            var_551 = wp::div(var_41, var_550);
        }
        if (!var_548) {
            // elif block==2:C=H;weight=Ar/wp.float64(6.)                                     <L 73>
            var_553 = (var_532 == var_552);
            if (var_553) {
                var_554 = wp::copy(var_48);
                var_555 = 6.0;
                var_556 = wp::div(var_41, var_555);
            }
            var_557 = wp::where(var_553, var_554, var_544);
            var_558 = wp::where(var_553, var_556, var_546);
        }
        var_559 = wp::where(var_548, var_549, var_557);
        var_560 = wp::where(var_548, var_551, var_558);
        // bary=wp.transpose(C)*local;x=wp.transpose(X)*bary;v=wp.transpose(V)*bary;s=signed(mesh,tri,wp.transpose(R)*(x-T));r.queries+=1       <L 74>
        var_561 = wp::transpose(var_559);
        var_562 = wp::mul(var_561, var_539);
        var_563 = wp::transpose(var_X);
        var_564 = wp::mul(var_563, var_562);
        var_565 = wp::transpose(var_V);
        var_566 = wp::mul(var_565, var_562);
        var_567 = wp::transpose(var_R);
        var_568 = wp::sub(var_564, var_T);
        var_569 = wp::mul(var_567, var_568);
        var_570 = signed_0(var_mesh, var_tri, var_569);
        var_572 = &((var_0).queries);
        var_574 = wp::load(var_572);
        var_573 = wp::add(var_574, var_571);
        var_0.queries = var_573;
        // if s.phi<wp.float64(0.):                                                           <L 75>
        var_575 = &((var_570).phi);
        var_576 = 0.0;
        var_578 = wp::load(var_575);
        var_577 = (var_578 < var_576);
        if (var_577) {
            // active=True;normal=R*s.normal;depth=-s.phi;fn=wp.float64(1e9)*weight*depth;rel=v-tv;tan=rel-wp.dot(rel,normal)*normal;speed=wp.length(tan);fr=wp.vec3d(wp.float64(0.))       <L 76>
            var_580 = &((var_570).normal);
            var_582 = wp::load(var_580);
            var_581 = wp::mul(var_R, var_582);
            var_583 = &((var_570).phi);
            var_585 = wp::load(var_583);
            var_584 = wp::neg(var_585);
            var_586 = 1000000000.0;
            var_587 = wp::mul(var_586, var_560);
            var_588 = wp::mul(var_587, var_584);
            var_589 = wp::sub(var_566, var_tv);
            var_590 = wp::dot(var_589, var_581);
            var_591 = wp::mul(var_590, var_581);
            var_592 = wp::sub(var_589, var_591);
            var_593 = wp::length(var_592);
            var_594 = 0.0;
            var_595 = wp::vec_t<3, wp::float64>(var_594);
            // if speed>wp.float64(1e-30):fr=-wp.float64(.2)*fn*wp.tanh(speed/wp.float64(.001))*tan/speed       <L 77>
            var_596 = 1e-30;
            var_597 = (var_593 > var_596);
            if (var_597) {
                var_598 = 0.2;
                var_599 = wp::neg(var_598);
                var_600 = wp::mul(var_599, var_588);
                var_601 = 0.001;
                var_602 = wp::div(var_593, var_601);
                var_603 = wp::tanh(var_602);
                var_604 = wp::mul(var_600, var_603);
                var_605 = wp::mul(var_604, var_592);
                var_606 = wp::div(var_605, var_593);
            }
            var_607 = wp::where(var_597, var_606, var_595);
            // f=fn*normal+fr                                                                 <L 78>
            var_608 = wp::mul(var_588, var_581);
            var_609 = wp::add(var_608, var_607);
            // for u in range(3):                                                             <L 79>
            // for v0 in range(3):                                                            <L 80>
            // if block==0:low[u,v0]+=bary[u]*f[v0]                                           <L 81>
            var_613 = (var_532 == var_612);
            if (var_613) {
                var_614 = wp::extract(var_562, var_610);
                var_615 = wp::extract(var_609, var_611);
                var_616 = wp::mul(var_614, var_615);
                wp::add_inplace(var_50, var_610, var_611, var_616);
            }
            if (!var_613) {
                // else:r.f[u,v0]+=bary[u]*f[v0]                                              <L 82>
                var_617 = wp::extract(var_562, var_610);
                var_618 = wp::extract(var_609, var_611);
                var_619 = wp::mul(var_617, var_618);
                var_620 = &((var_0).f);
                var_621 = wp::indexref(var_620, var_610, var_611);
                var_622 = wp::load(var_621);
                var_623 = wp::add(var_622, var_619);
                var_624 = wp::indexref(var_620, var_610, var_611);
                wp::store(var_624, var_623);
            }
            // if block==0:low[u,v0]+=bary[u]*f[v0]                                           <L 81>
            var_627 = (var_532 == var_626);
            if (var_627) {
                var_628 = wp::extract(var_562, var_610);
                var_629 = wp::extract(var_609, var_625);
                var_630 = wp::mul(var_628, var_629);
                wp::add_inplace(var_50, var_610, var_625, var_630);
            }
            if (!var_627) {
                // else:r.f[u,v0]+=bary[u]*f[v0]                                              <L 82>
                var_631 = wp::extract(var_562, var_610);
                var_632 = wp::extract(var_609, var_625);
                var_633 = wp::mul(var_631, var_632);
                var_634 = &((var_0).f);
                var_635 = wp::indexref(var_634, var_610, var_625);
                var_636 = wp::load(var_635);
                var_637 = wp::add(var_636, var_633);
                var_638 = wp::indexref(var_634, var_610, var_625);
                wp::store(var_638, var_637);
            }
            // if block==0:low[u,v0]+=bary[u]*f[v0]                                           <L 81>
            var_641 = (var_532 == var_640);
            if (var_641) {
                var_642 = wp::extract(var_562, var_610);
                var_643 = wp::extract(var_609, var_639);
                var_644 = wp::mul(var_642, var_643);
                wp::add_inplace(var_50, var_610, var_639, var_644);
            }
            if (!var_641) {
                // else:r.f[u,v0]+=bary[u]*f[v0]                                              <L 82>
                var_645 = wp::extract(var_562, var_610);
                var_646 = wp::extract(var_609, var_639);
                var_647 = wp::mul(var_645, var_646);
                var_648 = &((var_0).f);
                var_649 = wp::indexref(var_648, var_610, var_639);
                var_650 = wp::load(var_649);
                var_651 = wp::add(var_650, var_647);
                var_652 = wp::indexref(var_648, var_610, var_639);
                wp::store(var_652, var_651);
            }
            // for v0 in range(3):                                                            <L 80>
            // if block==0:low[u,v0]+=bary[u]*f[v0]                                           <L 81>
            var_656 = (var_532 == var_655);
            if (var_656) {
                var_657 = wp::extract(var_562, var_653);
                var_658 = wp::extract(var_609, var_654);
                var_659 = wp::mul(var_657, var_658);
                wp::add_inplace(var_50, var_653, var_654, var_659);
            }
            if (!var_656) {
                // else:r.f[u,v0]+=bary[u]*f[v0]                                              <L 82>
                var_660 = wp::extract(var_562, var_653);
                var_661 = wp::extract(var_609, var_654);
                var_662 = wp::mul(var_660, var_661);
                var_663 = &((var_0).f);
                var_664 = wp::indexref(var_663, var_653, var_654);
                var_665 = wp::load(var_664);
                var_666 = wp::add(var_665, var_662);
                var_667 = wp::indexref(var_663, var_653, var_654);
                wp::store(var_667, var_666);
            }
            // if block==0:low[u,v0]+=bary[u]*f[v0]                                           <L 81>
            var_670 = (var_532 == var_669);
            if (var_670) {
                var_671 = wp::extract(var_562, var_653);
                var_672 = wp::extract(var_609, var_668);
                var_673 = wp::mul(var_671, var_672);
                wp::add_inplace(var_50, var_653, var_668, var_673);
            }
            if (!var_670) {
                // else:r.f[u,v0]+=bary[u]*f[v0]                                              <L 82>
                var_674 = wp::extract(var_562, var_653);
                var_675 = wp::extract(var_609, var_668);
                var_676 = wp::mul(var_674, var_675);
                var_677 = &((var_0).f);
                var_678 = wp::indexref(var_677, var_653, var_668);
                var_679 = wp::load(var_678);
                var_680 = wp::add(var_679, var_676);
                var_681 = wp::indexref(var_677, var_653, var_668);
                wp::store(var_681, var_680);
            }
            // if block==0:low[u,v0]+=bary[u]*f[v0]                                           <L 81>
            var_684 = (var_532 == var_683);
            if (var_684) {
                var_685 = wp::extract(var_562, var_653);
                var_686 = wp::extract(var_609, var_682);
                var_687 = wp::mul(var_685, var_686);
                wp::add_inplace(var_50, var_653, var_682, var_687);
            }
            if (!var_684) {
                // else:r.f[u,v0]+=bary[u]*f[v0]                                              <L 82>
                var_688 = wp::extract(var_562, var_653);
                var_689 = wp::extract(var_609, var_682);
                var_690 = wp::mul(var_688, var_689);
                var_691 = &((var_0).f);
                var_692 = wp::indexref(var_691, var_653, var_682);
                var_693 = wp::load(var_692);
                var_694 = wp::add(var_693, var_690);
                var_695 = wp::indexref(var_691, var_653, var_682);
                wp::store(var_695, var_694);
            }
            // for v0 in range(3):                                                            <L 80>
            // if block==0:low[u,v0]+=bary[u]*f[v0]                                           <L 81>
            var_699 = (var_532 == var_698);
            if (var_699) {
                var_700 = wp::extract(var_562, var_696);
                var_701 = wp::extract(var_609, var_697);
                var_702 = wp::mul(var_700, var_701);
                wp::add_inplace(var_50, var_696, var_697, var_702);
            }
            if (!var_699) {
                // else:r.f[u,v0]+=bary[u]*f[v0]                                              <L 82>
                var_703 = wp::extract(var_562, var_696);
                var_704 = wp::extract(var_609, var_697);
                var_705 = wp::mul(var_703, var_704);
                var_706 = &((var_0).f);
                var_707 = wp::indexref(var_706, var_696, var_697);
                var_708 = wp::load(var_707);
                var_709 = wp::add(var_708, var_705);
                var_710 = wp::indexref(var_706, var_696, var_697);
                wp::store(var_710, var_709);
            }
            // if block==0:low[u,v0]+=bary[u]*f[v0]                                           <L 81>
            var_713 = (var_532 == var_712);
            if (var_713) {
                var_714 = wp::extract(var_562, var_696);
                var_715 = wp::extract(var_609, var_711);
                var_716 = wp::mul(var_714, var_715);
                wp::add_inplace(var_50, var_696, var_711, var_716);
            }
            if (!var_713) {
                // else:r.f[u,v0]+=bary[u]*f[v0]                                              <L 82>
                var_717 = wp::extract(var_562, var_696);
                var_718 = wp::extract(var_609, var_711);
                var_719 = wp::mul(var_717, var_718);
                var_720 = &((var_0).f);
                var_721 = wp::indexref(var_720, var_696, var_711);
                var_722 = wp::load(var_721);
                var_723 = wp::add(var_722, var_719);
                var_724 = wp::indexref(var_720, var_696, var_711);
                wp::store(var_724, var_723);
            }
            // if block==0:low[u,v0]+=bary[u]*f[v0]                                           <L 81>
            var_727 = (var_532 == var_726);
            if (var_727) {
                var_728 = wp::extract(var_562, var_696);
                var_729 = wp::extract(var_609, var_725);
                var_730 = wp::mul(var_728, var_729);
                wp::add_inplace(var_50, var_696, var_725, var_730);
            }
            if (!var_727) {
                // else:r.f[u,v0]+=bary[u]*f[v0]                                              <L 82>
                var_731 = wp::extract(var_562, var_696);
                var_732 = wp::extract(var_609, var_725);
                var_733 = wp::mul(var_731, var_732);
                var_734 = &((var_0).f);
                var_735 = wp::indexref(var_734, var_696, var_725);
                var_736 = wp::load(var_735);
                var_737 = wp::add(var_736, var_733);
                var_738 = wp::indexref(var_734, var_696, var_725);
                wp::store(var_738, var_737);
            }
            // if block>0:r.U+=wp.float64(.5)*wp.float64(1e9)*weight*depth*depth;r.D-=wp.dot(fr,rel);r.W+=wp.dot(f,tv);r.moment+=wp.cross(x-T,f)       <L 83>
            var_740 = (var_532 > var_739);
            if (var_740) {
                var_741 = 0.5;
                var_742 = 1000000000.0;
                var_743 = wp::mul(var_741, var_742);
                var_744 = wp::mul(var_743, var_560);
                var_745 = wp::mul(var_744, var_584);
                var_746 = wp::mul(var_745, var_584);
                var_747 = &((var_0).U);
                var_749 = wp::load(var_747);
                var_748 = wp::add(var_749, var_746);
                var_0.U = var_748;
                var_750 = wp::dot(var_607, var_589);
                var_751 = &((var_0).D);
                var_753 = wp::load(var_751);
                var_752 = wp::sub(var_753, var_750);
                var_0.D = var_752;
                var_754 = wp::dot(var_609, var_tv);
                var_755 = &((var_0).W);
                var_757 = wp::load(var_755);
                var_756 = wp::add(var_757, var_754);
                var_0.W = var_756;
                var_758 = wp::sub(var_564, var_T);
                var_759 = wp::cross(var_758, var_609);
                var_760 = &((var_0).moment);
                var_762 = wp::load(var_760);
                var_761 = wp::add(var_762, var_759);
                var_0.moment = var_761;
            }
        }
        var_763 = wp::where(var_577, var_579, var_519);
        var_764 = wp::where(var_577, var_581, var_520);
        var_765 = wp::where(var_577, var_584, var_521);
        var_766 = wp::where(var_577, var_588, var_522);
        var_767 = wp::where(var_577, var_589, var_523);
        var_768 = wp::where(var_577, var_592, var_524);
        var_769 = wp::where(var_577, var_593, var_525);
        var_770 = wp::where(var_577, var_607, var_526);
        var_771 = wp::where(var_577, var_609, var_527);
        var_772 = wp::where(var_577, var_696, var_528);
        var_773 = wp::where(var_577, var_725, var_529);
        // block=k//3;point=k%3;local=wp.vec3d(wp.float64(1./6.));local[point]=wp.float64(2./3.);C=B;weight=Ar/wp.float64(3.)       <L 71>
        var_776 = wp::floordiv(var_774, var_775);
        var_778 = wp::mod(var_774, var_777);
        var_781 = wp::div(var_779, var_780);
        var_782 = wp::float64(var_781);
        var_783 = wp::vec_t<3, wp::float64>(var_782);
        var_786 = wp::div(var_784, var_785);
        var_787 = wp::float64(var_786);
        wp::assign_inplace(var_783, var_778, var_787);
        var_788 = wp::copy(var_B);
        var_789 = 3.0;
        var_790 = wp::div(var_41, var_789);
        // if block==1:C=L;weight=Ar/wp.float64(6.)                                           <L 72>
        var_792 = (var_776 == var_791);
        if (var_792) {
            var_793 = wp::copy(var_47);
            var_794 = 6.0;
            var_795 = wp::div(var_41, var_794);
        }
        if (!var_792) {
            // elif block==2:C=H;weight=Ar/wp.float64(6.)                                     <L 73>
            var_797 = (var_776 == var_796);
            if (var_797) {
                var_798 = wp::copy(var_48);
                var_799 = 6.0;
                var_800 = wp::div(var_41, var_799);
            }
            var_801 = wp::where(var_797, var_798, var_788);
            var_802 = wp::where(var_797, var_800, var_790);
        }
        var_803 = wp::where(var_792, var_793, var_801);
        var_804 = wp::where(var_792, var_795, var_802);
        // bary=wp.transpose(C)*local;x=wp.transpose(X)*bary;v=wp.transpose(V)*bary;s=signed(mesh,tri,wp.transpose(R)*(x-T));r.queries+=1       <L 74>
        var_805 = wp::transpose(var_803);
        var_806 = wp::mul(var_805, var_783);
        var_807 = wp::transpose(var_X);
        var_808 = wp::mul(var_807, var_806);
        var_809 = wp::transpose(var_V);
        var_810 = wp::mul(var_809, var_806);
        var_811 = wp::transpose(var_R);
        var_812 = wp::sub(var_808, var_T);
        var_813 = wp::mul(var_811, var_812);
        var_814 = signed_0(var_mesh, var_tri, var_813);
        var_816 = &((var_0).queries);
        var_818 = wp::load(var_816);
        var_817 = wp::add(var_818, var_815);
        var_0.queries = var_817;
        // if s.phi<wp.float64(0.):                                                           <L 75>
        var_819 = &((var_814).phi);
        var_820 = 0.0;
        var_822 = wp::load(var_819);
        var_821 = (var_822 < var_820);
        if (var_821) {
            // active=True;normal=R*s.normal;depth=-s.phi;fn=wp.float64(1e9)*weight*depth;rel=v-tv;tan=rel-wp.dot(rel,normal)*normal;speed=wp.length(tan);fr=wp.vec3d(wp.float64(0.))       <L 76>
            var_824 = &((var_814).normal);
            var_826 = wp::load(var_824);
            var_825 = wp::mul(var_R, var_826);
            var_827 = &((var_814).phi);
            var_829 = wp::load(var_827);
            var_828 = wp::neg(var_829);
            var_830 = 1000000000.0;
            var_831 = wp::mul(var_830, var_804);
            var_832 = wp::mul(var_831, var_828);
            var_833 = wp::sub(var_810, var_tv);
            var_834 = wp::dot(var_833, var_825);
            var_835 = wp::mul(var_834, var_825);
            var_836 = wp::sub(var_833, var_835);
            var_837 = wp::length(var_836);
            var_838 = 0.0;
            var_839 = wp::vec_t<3, wp::float64>(var_838);
            // if speed>wp.float64(1e-30):fr=-wp.float64(.2)*fn*wp.tanh(speed/wp.float64(.001))*tan/speed       <L 77>
            var_840 = 1e-30;
            var_841 = (var_837 > var_840);
            if (var_841) {
                var_842 = 0.2;
                var_843 = wp::neg(var_842);
                var_844 = wp::mul(var_843, var_832);
                var_845 = 0.001;
                var_846 = wp::div(var_837, var_845);
                var_847 = wp::tanh(var_846);
                var_848 = wp::mul(var_844, var_847);
                var_849 = wp::mul(var_848, var_836);
                var_850 = wp::div(var_849, var_837);
            }
            var_851 = wp::where(var_841, var_850, var_839);
            // f=fn*normal+fr                                                                 <L 78>
            var_852 = wp::mul(var_832, var_825);
            var_853 = wp::add(var_852, var_851);
            // for u in range(3):                                                             <L 79>
            // for v0 in range(3):                                                            <L 80>
            // if block==0:low[u,v0]+=bary[u]*f[v0]                                           <L 81>
            var_857 = (var_776 == var_856);
            if (var_857) {
                var_858 = wp::extract(var_806, var_854);
                var_859 = wp::extract(var_853, var_855);
                var_860 = wp::mul(var_858, var_859);
                wp::add_inplace(var_50, var_854, var_855, var_860);
            }
            if (!var_857) {
                // else:r.f[u,v0]+=bary[u]*f[v0]                                              <L 82>
                var_861 = wp::extract(var_806, var_854);
                var_862 = wp::extract(var_853, var_855);
                var_863 = wp::mul(var_861, var_862);
                var_864 = &((var_0).f);
                var_865 = wp::indexref(var_864, var_854, var_855);
                var_866 = wp::load(var_865);
                var_867 = wp::add(var_866, var_863);
                var_868 = wp::indexref(var_864, var_854, var_855);
                wp::store(var_868, var_867);
            }
            // if block==0:low[u,v0]+=bary[u]*f[v0]                                           <L 81>
            var_871 = (var_776 == var_870);
            if (var_871) {
                var_872 = wp::extract(var_806, var_854);
                var_873 = wp::extract(var_853, var_869);
                var_874 = wp::mul(var_872, var_873);
                wp::add_inplace(var_50, var_854, var_869, var_874);
            }
            if (!var_871) {
                // else:r.f[u,v0]+=bary[u]*f[v0]                                              <L 82>
                var_875 = wp::extract(var_806, var_854);
                var_876 = wp::extract(var_853, var_869);
                var_877 = wp::mul(var_875, var_876);
                var_878 = &((var_0).f);
                var_879 = wp::indexref(var_878, var_854, var_869);
                var_880 = wp::load(var_879);
                var_881 = wp::add(var_880, var_877);
                var_882 = wp::indexref(var_878, var_854, var_869);
                wp::store(var_882, var_881);
            }
            // if block==0:low[u,v0]+=bary[u]*f[v0]                                           <L 81>
            var_885 = (var_776 == var_884);
            if (var_885) {
                var_886 = wp::extract(var_806, var_854);
                var_887 = wp::extract(var_853, var_883);
                var_888 = wp::mul(var_886, var_887);
                wp::add_inplace(var_50, var_854, var_883, var_888);
            }
            if (!var_885) {
                // else:r.f[u,v0]+=bary[u]*f[v0]                                              <L 82>
                var_889 = wp::extract(var_806, var_854);
                var_890 = wp::extract(var_853, var_883);
                var_891 = wp::mul(var_889, var_890);
                var_892 = &((var_0).f);
                var_893 = wp::indexref(var_892, var_854, var_883);
                var_894 = wp::load(var_893);
                var_895 = wp::add(var_894, var_891);
                var_896 = wp::indexref(var_892, var_854, var_883);
                wp::store(var_896, var_895);
            }
            // for v0 in range(3):                                                            <L 80>
            // if block==0:low[u,v0]+=bary[u]*f[v0]                                           <L 81>
            var_900 = (var_776 == var_899);
            if (var_900) {
                var_901 = wp::extract(var_806, var_897);
                var_902 = wp::extract(var_853, var_898);
                var_903 = wp::mul(var_901, var_902);
                wp::add_inplace(var_50, var_897, var_898, var_903);
            }
            if (!var_900) {
                // else:r.f[u,v0]+=bary[u]*f[v0]                                              <L 82>
                var_904 = wp::extract(var_806, var_897);
                var_905 = wp::extract(var_853, var_898);
                var_906 = wp::mul(var_904, var_905);
                var_907 = &((var_0).f);
                var_908 = wp::indexref(var_907, var_897, var_898);
                var_909 = wp::load(var_908);
                var_910 = wp::add(var_909, var_906);
                var_911 = wp::indexref(var_907, var_897, var_898);
                wp::store(var_911, var_910);
            }
            // if block==0:low[u,v0]+=bary[u]*f[v0]                                           <L 81>
            var_914 = (var_776 == var_913);
            if (var_914) {
                var_915 = wp::extract(var_806, var_897);
                var_916 = wp::extract(var_853, var_912);
                var_917 = wp::mul(var_915, var_916);
                wp::add_inplace(var_50, var_897, var_912, var_917);
            }
            if (!var_914) {
                // else:r.f[u,v0]+=bary[u]*f[v0]                                              <L 82>
                var_918 = wp::extract(var_806, var_897);
                var_919 = wp::extract(var_853, var_912);
                var_920 = wp::mul(var_918, var_919);
                var_921 = &((var_0).f);
                var_922 = wp::indexref(var_921, var_897, var_912);
                var_923 = wp::load(var_922);
                var_924 = wp::add(var_923, var_920);
                var_925 = wp::indexref(var_921, var_897, var_912);
                wp::store(var_925, var_924);
            }
            // if block==0:low[u,v0]+=bary[u]*f[v0]                                           <L 81>
            var_928 = (var_776 == var_927);
            if (var_928) {
                var_929 = wp::extract(var_806, var_897);
                var_930 = wp::extract(var_853, var_926);
                var_931 = wp::mul(var_929, var_930);
                wp::add_inplace(var_50, var_897, var_926, var_931);
            }
            if (!var_928) {
                // else:r.f[u,v0]+=bary[u]*f[v0]                                              <L 82>
                var_932 = wp::extract(var_806, var_897);
                var_933 = wp::extract(var_853, var_926);
                var_934 = wp::mul(var_932, var_933);
                var_935 = &((var_0).f);
                var_936 = wp::indexref(var_935, var_897, var_926);
                var_937 = wp::load(var_936);
                var_938 = wp::add(var_937, var_934);
                var_939 = wp::indexref(var_935, var_897, var_926);
                wp::store(var_939, var_938);
            }
            // for v0 in range(3):                                                            <L 80>
            // if block==0:low[u,v0]+=bary[u]*f[v0]                                           <L 81>
            var_943 = (var_776 == var_942);
            if (var_943) {
                var_944 = wp::extract(var_806, var_940);
                var_945 = wp::extract(var_853, var_941);
                var_946 = wp::mul(var_944, var_945);
                wp::add_inplace(var_50, var_940, var_941, var_946);
            }
            if (!var_943) {
                // else:r.f[u,v0]+=bary[u]*f[v0]                                              <L 82>
                var_947 = wp::extract(var_806, var_940);
                var_948 = wp::extract(var_853, var_941);
                var_949 = wp::mul(var_947, var_948);
                var_950 = &((var_0).f);
                var_951 = wp::indexref(var_950, var_940, var_941);
                var_952 = wp::load(var_951);
                var_953 = wp::add(var_952, var_949);
                var_954 = wp::indexref(var_950, var_940, var_941);
                wp::store(var_954, var_953);
            }
            // if block==0:low[u,v0]+=bary[u]*f[v0]                                           <L 81>
            var_957 = (var_776 == var_956);
            if (var_957) {
                var_958 = wp::extract(var_806, var_940);
                var_959 = wp::extract(var_853, var_955);
                var_960 = wp::mul(var_958, var_959);
                wp::add_inplace(var_50, var_940, var_955, var_960);
            }
            if (!var_957) {
                // else:r.f[u,v0]+=bary[u]*f[v0]                                              <L 82>
                var_961 = wp::extract(var_806, var_940);
                var_962 = wp::extract(var_853, var_955);
                var_963 = wp::mul(var_961, var_962);
                var_964 = &((var_0).f);
                var_965 = wp::indexref(var_964, var_940, var_955);
                var_966 = wp::load(var_965);
                var_967 = wp::add(var_966, var_963);
                var_968 = wp::indexref(var_964, var_940, var_955);
                wp::store(var_968, var_967);
            }
            // if block==0:low[u,v0]+=bary[u]*f[v0]                                           <L 81>
            var_971 = (var_776 == var_970);
            if (var_971) {
                var_972 = wp::extract(var_806, var_940);
                var_973 = wp::extract(var_853, var_969);
                var_974 = wp::mul(var_972, var_973);
                wp::add_inplace(var_50, var_940, var_969, var_974);
            }
            if (!var_971) {
                // else:r.f[u,v0]+=bary[u]*f[v0]                                              <L 82>
                var_975 = wp::extract(var_806, var_940);
                var_976 = wp::extract(var_853, var_969);
                var_977 = wp::mul(var_975, var_976);
                var_978 = &((var_0).f);
                var_979 = wp::indexref(var_978, var_940, var_969);
                var_980 = wp::load(var_979);
                var_981 = wp::add(var_980, var_977);
                var_982 = wp::indexref(var_978, var_940, var_969);
                wp::store(var_982, var_981);
            }
            // if block>0:r.U+=wp.float64(.5)*wp.float64(1e9)*weight*depth*depth;r.D-=wp.dot(fr,rel);r.W+=wp.dot(f,tv);r.moment+=wp.cross(x-T,f)       <L 83>
            var_984 = (var_776 > var_983);
            if (var_984) {
                var_985 = 0.5;
                var_986 = 1000000000.0;
                var_987 = wp::mul(var_985, var_986);
                var_988 = wp::mul(var_987, var_804);
                var_989 = wp::mul(var_988, var_828);
                var_990 = wp::mul(var_989, var_828);
                var_991 = &((var_0).U);
                var_993 = wp::load(var_991);
                var_992 = wp::add(var_993, var_990);
                var_0.U = var_992;
                var_994 = wp::dot(var_851, var_833);
                var_995 = &((var_0).D);
                var_997 = wp::load(var_995);
                var_996 = wp::sub(var_997, var_994);
                var_0.D = var_996;
                var_998 = wp::dot(var_853, var_tv);
                var_999 = &((var_0).W);
                var_1001 = wp::load(var_999);
                var_1000 = wp::add(var_1001, var_998);
                var_0.W = var_1000;
                var_1002 = wp::sub(var_808, var_T);
                var_1003 = wp::cross(var_1002, var_853);
                var_1004 = &((var_0).moment);
                var_1006 = wp::load(var_1004);
                var_1005 = wp::add(var_1006, var_1003);
                var_0.moment = var_1005;
            }
        }
        var_1007 = wp::where(var_821, var_823, var_763);
        var_1008 = wp::where(var_821, var_825, var_764);
        var_1009 = wp::where(var_821, var_828, var_765);
        var_1010 = wp::where(var_821, var_832, var_766);
        var_1011 = wp::where(var_821, var_833, var_767);
        var_1012 = wp::where(var_821, var_836, var_768);
        var_1013 = wp::where(var_821, var_837, var_769);
        var_1014 = wp::where(var_821, var_851, var_770);
        var_1015 = wp::where(var_821, var_853, var_771);
        var_1016 = wp::where(var_821, var_940, var_772);
        var_1017 = wp::where(var_821, var_969, var_773);
        // block=k//3;point=k%3;local=wp.vec3d(wp.float64(1./6.));local[point]=wp.float64(2./3.);C=B;weight=Ar/wp.float64(3.)       <L 71>
        var_1020 = wp::floordiv(var_1018, var_1019);
        var_1022 = wp::mod(var_1018, var_1021);
        var_1025 = wp::div(var_1023, var_1024);
        var_1026 = wp::float64(var_1025);
        var_1027 = wp::vec_t<3, wp::float64>(var_1026);
        var_1030 = wp::div(var_1028, var_1029);
        var_1031 = wp::float64(var_1030);
        wp::assign_inplace(var_1027, var_1022, var_1031);
        var_1032 = wp::copy(var_B);
        var_1033 = 3.0;
        var_1034 = wp::div(var_41, var_1033);
        // if block==1:C=L;weight=Ar/wp.float64(6.)                                           <L 72>
        var_1036 = (var_1020 == var_1035);
        if (var_1036) {
            var_1037 = wp::copy(var_47);
            var_1038 = 6.0;
            var_1039 = wp::div(var_41, var_1038);
        }
        if (!var_1036) {
            // elif block==2:C=H;weight=Ar/wp.float64(6.)                                     <L 73>
            var_1041 = (var_1020 == var_1040);
            if (var_1041) {
                var_1042 = wp::copy(var_48);
                var_1043 = 6.0;
                var_1044 = wp::div(var_41, var_1043);
            }
            var_1045 = wp::where(var_1041, var_1042, var_1032);
            var_1046 = wp::where(var_1041, var_1044, var_1034);
        }
        var_1047 = wp::where(var_1036, var_1037, var_1045);
        var_1048 = wp::where(var_1036, var_1039, var_1046);
        // bary=wp.transpose(C)*local;x=wp.transpose(X)*bary;v=wp.transpose(V)*bary;s=signed(mesh,tri,wp.transpose(R)*(x-T));r.queries+=1       <L 74>
        var_1049 = wp::transpose(var_1047);
        var_1050 = wp::mul(var_1049, var_1027);
        var_1051 = wp::transpose(var_X);
        var_1052 = wp::mul(var_1051, var_1050);
        var_1053 = wp::transpose(var_V);
        var_1054 = wp::mul(var_1053, var_1050);
        var_1055 = wp::transpose(var_R);
        var_1056 = wp::sub(var_1052, var_T);
        var_1057 = wp::mul(var_1055, var_1056);
        var_1058 = signed_0(var_mesh, var_tri, var_1057);
        var_1060 = &((var_0).queries);
        var_1062 = wp::load(var_1060);
        var_1061 = wp::add(var_1062, var_1059);
        var_0.queries = var_1061;
        // if s.phi<wp.float64(0.):                                                           <L 75>
        var_1063 = &((var_1058).phi);
        var_1064 = 0.0;
        var_1066 = wp::load(var_1063);
        var_1065 = (var_1066 < var_1064);
        if (var_1065) {
            // active=True;normal=R*s.normal;depth=-s.phi;fn=wp.float64(1e9)*weight*depth;rel=v-tv;tan=rel-wp.dot(rel,normal)*normal;speed=wp.length(tan);fr=wp.vec3d(wp.float64(0.))       <L 76>
            var_1068 = &((var_1058).normal);
            var_1070 = wp::load(var_1068);
            var_1069 = wp::mul(var_R, var_1070);
            var_1071 = &((var_1058).phi);
            var_1073 = wp::load(var_1071);
            var_1072 = wp::neg(var_1073);
            var_1074 = 1000000000.0;
            var_1075 = wp::mul(var_1074, var_1048);
            var_1076 = wp::mul(var_1075, var_1072);
            var_1077 = wp::sub(var_1054, var_tv);
            var_1078 = wp::dot(var_1077, var_1069);
            var_1079 = wp::mul(var_1078, var_1069);
            var_1080 = wp::sub(var_1077, var_1079);
            var_1081 = wp::length(var_1080);
            var_1082 = 0.0;
            var_1083 = wp::vec_t<3, wp::float64>(var_1082);
            // if speed>wp.float64(1e-30):fr=-wp.float64(.2)*fn*wp.tanh(speed/wp.float64(.001))*tan/speed       <L 77>
            var_1084 = 1e-30;
            var_1085 = (var_1081 > var_1084);
            if (var_1085) {
                var_1086 = 0.2;
                var_1087 = wp::neg(var_1086);
                var_1088 = wp::mul(var_1087, var_1076);
                var_1089 = 0.001;
                var_1090 = wp::div(var_1081, var_1089);
                var_1091 = wp::tanh(var_1090);
                var_1092 = wp::mul(var_1088, var_1091);
                var_1093 = wp::mul(var_1092, var_1080);
                var_1094 = wp::div(var_1093, var_1081);
            }
            var_1095 = wp::where(var_1085, var_1094, var_1083);
            // f=fn*normal+fr                                                                 <L 78>
            var_1096 = wp::mul(var_1076, var_1069);
            var_1097 = wp::add(var_1096, var_1095);
            // for u in range(3):                                                             <L 79>
            // for v0 in range(3):                                                            <L 80>
            // if block==0:low[u,v0]+=bary[u]*f[v0]                                           <L 81>
            var_1101 = (var_1020 == var_1100);
            if (var_1101) {
                var_1102 = wp::extract(var_1050, var_1098);
                var_1103 = wp::extract(var_1097, var_1099);
                var_1104 = wp::mul(var_1102, var_1103);
                wp::add_inplace(var_50, var_1098, var_1099, var_1104);
            }
            if (!var_1101) {
                // else:r.f[u,v0]+=bary[u]*f[v0]                                              <L 82>
                var_1105 = wp::extract(var_1050, var_1098);
                var_1106 = wp::extract(var_1097, var_1099);
                var_1107 = wp::mul(var_1105, var_1106);
                var_1108 = &((var_0).f);
                var_1109 = wp::indexref(var_1108, var_1098, var_1099);
                var_1110 = wp::load(var_1109);
                var_1111 = wp::add(var_1110, var_1107);
                var_1112 = wp::indexref(var_1108, var_1098, var_1099);
                wp::store(var_1112, var_1111);
            }
            // if block==0:low[u,v0]+=bary[u]*f[v0]                                           <L 81>
            var_1115 = (var_1020 == var_1114);
            if (var_1115) {
                var_1116 = wp::extract(var_1050, var_1098);
                var_1117 = wp::extract(var_1097, var_1113);
                var_1118 = wp::mul(var_1116, var_1117);
                wp::add_inplace(var_50, var_1098, var_1113, var_1118);
            }
            if (!var_1115) {
                // else:r.f[u,v0]+=bary[u]*f[v0]                                              <L 82>
                var_1119 = wp::extract(var_1050, var_1098);
                var_1120 = wp::extract(var_1097, var_1113);
                var_1121 = wp::mul(var_1119, var_1120);
                var_1122 = &((var_0).f);
                var_1123 = wp::indexref(var_1122, var_1098, var_1113);
                var_1124 = wp::load(var_1123);
                var_1125 = wp::add(var_1124, var_1121);
                var_1126 = wp::indexref(var_1122, var_1098, var_1113);
                wp::store(var_1126, var_1125);
            }
            // if block==0:low[u,v0]+=bary[u]*f[v0]                                           <L 81>
            var_1129 = (var_1020 == var_1128);
            if (var_1129) {
                var_1130 = wp::extract(var_1050, var_1098);
                var_1131 = wp::extract(var_1097, var_1127);
                var_1132 = wp::mul(var_1130, var_1131);
                wp::add_inplace(var_50, var_1098, var_1127, var_1132);
            }
            if (!var_1129) {
                // else:r.f[u,v0]+=bary[u]*f[v0]                                              <L 82>
                var_1133 = wp::extract(var_1050, var_1098);
                var_1134 = wp::extract(var_1097, var_1127);
                var_1135 = wp::mul(var_1133, var_1134);
                var_1136 = &((var_0).f);
                var_1137 = wp::indexref(var_1136, var_1098, var_1127);
                var_1138 = wp::load(var_1137);
                var_1139 = wp::add(var_1138, var_1135);
                var_1140 = wp::indexref(var_1136, var_1098, var_1127);
                wp::store(var_1140, var_1139);
            }
            // for v0 in range(3):                                                            <L 80>
            // if block==0:low[u,v0]+=bary[u]*f[v0]                                           <L 81>
            var_1144 = (var_1020 == var_1143);
            if (var_1144) {
                var_1145 = wp::extract(var_1050, var_1141);
                var_1146 = wp::extract(var_1097, var_1142);
                var_1147 = wp::mul(var_1145, var_1146);
                wp::add_inplace(var_50, var_1141, var_1142, var_1147);
            }
            if (!var_1144) {
                // else:r.f[u,v0]+=bary[u]*f[v0]                                              <L 82>
                var_1148 = wp::extract(var_1050, var_1141);
                var_1149 = wp::extract(var_1097, var_1142);
                var_1150 = wp::mul(var_1148, var_1149);
                var_1151 = &((var_0).f);
                var_1152 = wp::indexref(var_1151, var_1141, var_1142);
                var_1153 = wp::load(var_1152);
                var_1154 = wp::add(var_1153, var_1150);
                var_1155 = wp::indexref(var_1151, var_1141, var_1142);
                wp::store(var_1155, var_1154);
            }
            // if block==0:low[u,v0]+=bary[u]*f[v0]                                           <L 81>
            var_1158 = (var_1020 == var_1157);
            if (var_1158) {
                var_1159 = wp::extract(var_1050, var_1141);
                var_1160 = wp::extract(var_1097, var_1156);
                var_1161 = wp::mul(var_1159, var_1160);
                wp::add_inplace(var_50, var_1141, var_1156, var_1161);
            }
            if (!var_1158) {
                // else:r.f[u,v0]+=bary[u]*f[v0]                                              <L 82>
                var_1162 = wp::extract(var_1050, var_1141);
                var_1163 = wp::extract(var_1097, var_1156);
                var_1164 = wp::mul(var_1162, var_1163);
                var_1165 = &((var_0).f);
                var_1166 = wp::indexref(var_1165, var_1141, var_1156);
                var_1167 = wp::load(var_1166);
                var_1168 = wp::add(var_1167, var_1164);
                var_1169 = wp::indexref(var_1165, var_1141, var_1156);
                wp::store(var_1169, var_1168);
            }
            // if block==0:low[u,v0]+=bary[u]*f[v0]                                           <L 81>
            var_1172 = (var_1020 == var_1171);
            if (var_1172) {
                var_1173 = wp::extract(var_1050, var_1141);
                var_1174 = wp::extract(var_1097, var_1170);
                var_1175 = wp::mul(var_1173, var_1174);
                wp::add_inplace(var_50, var_1141, var_1170, var_1175);
            }
            if (!var_1172) {
                // else:r.f[u,v0]+=bary[u]*f[v0]                                              <L 82>
                var_1176 = wp::extract(var_1050, var_1141);
                var_1177 = wp::extract(var_1097, var_1170);
                var_1178 = wp::mul(var_1176, var_1177);
                var_1179 = &((var_0).f);
                var_1180 = wp::indexref(var_1179, var_1141, var_1170);
                var_1181 = wp::load(var_1180);
                var_1182 = wp::add(var_1181, var_1178);
                var_1183 = wp::indexref(var_1179, var_1141, var_1170);
                wp::store(var_1183, var_1182);
            }
            // for v0 in range(3):                                                            <L 80>
            // if block==0:low[u,v0]+=bary[u]*f[v0]                                           <L 81>
            var_1187 = (var_1020 == var_1186);
            if (var_1187) {
                var_1188 = wp::extract(var_1050, var_1184);
                var_1189 = wp::extract(var_1097, var_1185);
                var_1190 = wp::mul(var_1188, var_1189);
                wp::add_inplace(var_50, var_1184, var_1185, var_1190);
            }
            if (!var_1187) {
                // else:r.f[u,v0]+=bary[u]*f[v0]                                              <L 82>
                var_1191 = wp::extract(var_1050, var_1184);
                var_1192 = wp::extract(var_1097, var_1185);
                var_1193 = wp::mul(var_1191, var_1192);
                var_1194 = &((var_0).f);
                var_1195 = wp::indexref(var_1194, var_1184, var_1185);
                var_1196 = wp::load(var_1195);
                var_1197 = wp::add(var_1196, var_1193);
                var_1198 = wp::indexref(var_1194, var_1184, var_1185);
                wp::store(var_1198, var_1197);
            }
            // if block==0:low[u,v0]+=bary[u]*f[v0]                                           <L 81>
            var_1201 = (var_1020 == var_1200);
            if (var_1201) {
                var_1202 = wp::extract(var_1050, var_1184);
                var_1203 = wp::extract(var_1097, var_1199);
                var_1204 = wp::mul(var_1202, var_1203);
                wp::add_inplace(var_50, var_1184, var_1199, var_1204);
            }
            if (!var_1201) {
                // else:r.f[u,v0]+=bary[u]*f[v0]                                              <L 82>
                var_1205 = wp::extract(var_1050, var_1184);
                var_1206 = wp::extract(var_1097, var_1199);
                var_1207 = wp::mul(var_1205, var_1206);
                var_1208 = &((var_0).f);
                var_1209 = wp::indexref(var_1208, var_1184, var_1199);
                var_1210 = wp::load(var_1209);
                var_1211 = wp::add(var_1210, var_1207);
                var_1212 = wp::indexref(var_1208, var_1184, var_1199);
                wp::store(var_1212, var_1211);
            }
            // if block==0:low[u,v0]+=bary[u]*f[v0]                                           <L 81>
            var_1215 = (var_1020 == var_1214);
            if (var_1215) {
                var_1216 = wp::extract(var_1050, var_1184);
                var_1217 = wp::extract(var_1097, var_1213);
                var_1218 = wp::mul(var_1216, var_1217);
                wp::add_inplace(var_50, var_1184, var_1213, var_1218);
            }
            if (!var_1215) {
                // else:r.f[u,v0]+=bary[u]*f[v0]                                              <L 82>
                var_1219 = wp::extract(var_1050, var_1184);
                var_1220 = wp::extract(var_1097, var_1213);
                var_1221 = wp::mul(var_1219, var_1220);
                var_1222 = &((var_0).f);
                var_1223 = wp::indexref(var_1222, var_1184, var_1213);
                var_1224 = wp::load(var_1223);
                var_1225 = wp::add(var_1224, var_1221);
                var_1226 = wp::indexref(var_1222, var_1184, var_1213);
                wp::store(var_1226, var_1225);
            }
            // if block>0:r.U+=wp.float64(.5)*wp.float64(1e9)*weight*depth*depth;r.D-=wp.dot(fr,rel);r.W+=wp.dot(f,tv);r.moment+=wp.cross(x-T,f)       <L 83>
            var_1228 = (var_1020 > var_1227);
            if (var_1228) {
                var_1229 = 0.5;
                var_1230 = 1000000000.0;
                var_1231 = wp::mul(var_1229, var_1230);
                var_1232 = wp::mul(var_1231, var_1048);
                var_1233 = wp::mul(var_1232, var_1072);
                var_1234 = wp::mul(var_1233, var_1072);
                var_1235 = &((var_0).U);
                var_1237 = wp::load(var_1235);
                var_1236 = wp::add(var_1237, var_1234);
                var_0.U = var_1236;
                var_1238 = wp::dot(var_1095, var_1077);
                var_1239 = &((var_0).D);
                var_1241 = wp::load(var_1239);
                var_1240 = wp::sub(var_1241, var_1238);
                var_0.D = var_1240;
                var_1242 = wp::dot(var_1097, var_tv);
                var_1243 = &((var_0).W);
                var_1245 = wp::load(var_1243);
                var_1244 = wp::add(var_1245, var_1242);
                var_0.W = var_1244;
                var_1246 = wp::sub(var_1052, var_T);
                var_1247 = wp::cross(var_1246, var_1097);
                var_1248 = &((var_0).moment);
                var_1250 = wp::load(var_1248);
                var_1249 = wp::add(var_1250, var_1247);
                var_0.moment = var_1249;
            }
        }
        var_1251 = wp::where(var_1065, var_1067, var_1007);
        var_1252 = wp::where(var_1065, var_1069, var_1008);
        var_1253 = wp::where(var_1065, var_1072, var_1009);
        var_1254 = wp::where(var_1065, var_1076, var_1010);
        var_1255 = wp::where(var_1065, var_1077, var_1011);
        var_1256 = wp::where(var_1065, var_1080, var_1012);
        var_1257 = wp::where(var_1065, var_1081, var_1013);
        var_1258 = wp::where(var_1065, var_1095, var_1014);
        var_1259 = wp::where(var_1065, var_1097, var_1015);
        var_1260 = wp::where(var_1065, var_1184, var_1016);
        var_1261 = wp::where(var_1065, var_1213, var_1017);
        // block=k//3;point=k%3;local=wp.vec3d(wp.float64(1./6.));local[point]=wp.float64(2./3.);C=B;weight=Ar/wp.float64(3.)       <L 71>
        var_1264 = wp::floordiv(var_1262, var_1263);
        var_1266 = wp::mod(var_1262, var_1265);
        var_1269 = wp::div(var_1267, var_1268);
        var_1270 = wp::float64(var_1269);
        var_1271 = wp::vec_t<3, wp::float64>(var_1270);
        var_1274 = wp::div(var_1272, var_1273);
        var_1275 = wp::float64(var_1274);
        wp::assign_inplace(var_1271, var_1266, var_1275);
        var_1276 = wp::copy(var_B);
        var_1277 = 3.0;
        var_1278 = wp::div(var_41, var_1277);
        // if block==1:C=L;weight=Ar/wp.float64(6.)                                           <L 72>
        var_1280 = (var_1264 == var_1279);
        if (var_1280) {
            var_1281 = wp::copy(var_47);
            var_1282 = 6.0;
            var_1283 = wp::div(var_41, var_1282);
        }
        if (!var_1280) {
            // elif block==2:C=H;weight=Ar/wp.float64(6.)                                     <L 73>
            var_1285 = (var_1264 == var_1284);
            if (var_1285) {
                var_1286 = wp::copy(var_48);
                var_1287 = 6.0;
                var_1288 = wp::div(var_41, var_1287);
            }
            var_1289 = wp::where(var_1285, var_1286, var_1276);
            var_1290 = wp::where(var_1285, var_1288, var_1278);
        }
        var_1291 = wp::where(var_1280, var_1281, var_1289);
        var_1292 = wp::where(var_1280, var_1283, var_1290);
        // bary=wp.transpose(C)*local;x=wp.transpose(X)*bary;v=wp.transpose(V)*bary;s=signed(mesh,tri,wp.transpose(R)*(x-T));r.queries+=1       <L 74>
        var_1293 = wp::transpose(var_1291);
        var_1294 = wp::mul(var_1293, var_1271);
        var_1295 = wp::transpose(var_X);
        var_1296 = wp::mul(var_1295, var_1294);
        var_1297 = wp::transpose(var_V);
        var_1298 = wp::mul(var_1297, var_1294);
        var_1299 = wp::transpose(var_R);
        var_1300 = wp::sub(var_1296, var_T);
        var_1301 = wp::mul(var_1299, var_1300);
        var_1302 = signed_0(var_mesh, var_tri, var_1301);
        var_1304 = &((var_0).queries);
        var_1306 = wp::load(var_1304);
        var_1305 = wp::add(var_1306, var_1303);
        var_0.queries = var_1305;
        // if s.phi<wp.float64(0.):                                                           <L 75>
        var_1307 = &((var_1302).phi);
        var_1308 = 0.0;
        var_1310 = wp::load(var_1307);
        var_1309 = (var_1310 < var_1308);
        if (var_1309) {
            // active=True;normal=R*s.normal;depth=-s.phi;fn=wp.float64(1e9)*weight*depth;rel=v-tv;tan=rel-wp.dot(rel,normal)*normal;speed=wp.length(tan);fr=wp.vec3d(wp.float64(0.))       <L 76>
            var_1312 = &((var_1302).normal);
            var_1314 = wp::load(var_1312);
            var_1313 = wp::mul(var_R, var_1314);
            var_1315 = &((var_1302).phi);
            var_1317 = wp::load(var_1315);
            var_1316 = wp::neg(var_1317);
            var_1318 = 1000000000.0;
            var_1319 = wp::mul(var_1318, var_1292);
            var_1320 = wp::mul(var_1319, var_1316);
            var_1321 = wp::sub(var_1298, var_tv);
            var_1322 = wp::dot(var_1321, var_1313);
            var_1323 = wp::mul(var_1322, var_1313);
            var_1324 = wp::sub(var_1321, var_1323);
            var_1325 = wp::length(var_1324);
            var_1326 = 0.0;
            var_1327 = wp::vec_t<3, wp::float64>(var_1326);
            // if speed>wp.float64(1e-30):fr=-wp.float64(.2)*fn*wp.tanh(speed/wp.float64(.001))*tan/speed       <L 77>
            var_1328 = 1e-30;
            var_1329 = (var_1325 > var_1328);
            if (var_1329) {
                var_1330 = 0.2;
                var_1331 = wp::neg(var_1330);
                var_1332 = wp::mul(var_1331, var_1320);
                var_1333 = 0.001;
                var_1334 = wp::div(var_1325, var_1333);
                var_1335 = wp::tanh(var_1334);
                var_1336 = wp::mul(var_1332, var_1335);
                var_1337 = wp::mul(var_1336, var_1324);
                var_1338 = wp::div(var_1337, var_1325);
            }
            var_1339 = wp::where(var_1329, var_1338, var_1327);
            // f=fn*normal+fr                                                                 <L 78>
            var_1340 = wp::mul(var_1320, var_1313);
            var_1341 = wp::add(var_1340, var_1339);
            // for u in range(3):                                                             <L 79>
            // for v0 in range(3):                                                            <L 80>
            // if block==0:low[u,v0]+=bary[u]*f[v0]                                           <L 81>
            var_1345 = (var_1264 == var_1344);
            if (var_1345) {
                var_1346 = wp::extract(var_1294, var_1342);
                var_1347 = wp::extract(var_1341, var_1343);
                var_1348 = wp::mul(var_1346, var_1347);
                wp::add_inplace(var_50, var_1342, var_1343, var_1348);
            }
            if (!var_1345) {
                // else:r.f[u,v0]+=bary[u]*f[v0]                                              <L 82>
                var_1349 = wp::extract(var_1294, var_1342);
                var_1350 = wp::extract(var_1341, var_1343);
                var_1351 = wp::mul(var_1349, var_1350);
                var_1352 = &((var_0).f);
                var_1353 = wp::indexref(var_1352, var_1342, var_1343);
                var_1354 = wp::load(var_1353);
                var_1355 = wp::add(var_1354, var_1351);
                var_1356 = wp::indexref(var_1352, var_1342, var_1343);
                wp::store(var_1356, var_1355);
            }
            // if block==0:low[u,v0]+=bary[u]*f[v0]                                           <L 81>
            var_1359 = (var_1264 == var_1358);
            if (var_1359) {
                var_1360 = wp::extract(var_1294, var_1342);
                var_1361 = wp::extract(var_1341, var_1357);
                var_1362 = wp::mul(var_1360, var_1361);
                wp::add_inplace(var_50, var_1342, var_1357, var_1362);
            }
            if (!var_1359) {
                // else:r.f[u,v0]+=bary[u]*f[v0]                                              <L 82>
                var_1363 = wp::extract(var_1294, var_1342);
                var_1364 = wp::extract(var_1341, var_1357);
                var_1365 = wp::mul(var_1363, var_1364);
                var_1366 = &((var_0).f);
                var_1367 = wp::indexref(var_1366, var_1342, var_1357);
                var_1368 = wp::load(var_1367);
                var_1369 = wp::add(var_1368, var_1365);
                var_1370 = wp::indexref(var_1366, var_1342, var_1357);
                wp::store(var_1370, var_1369);
            }
            // if block==0:low[u,v0]+=bary[u]*f[v0]                                           <L 81>
            var_1373 = (var_1264 == var_1372);
            if (var_1373) {
                var_1374 = wp::extract(var_1294, var_1342);
                var_1375 = wp::extract(var_1341, var_1371);
                var_1376 = wp::mul(var_1374, var_1375);
                wp::add_inplace(var_50, var_1342, var_1371, var_1376);
            }
            if (!var_1373) {
                // else:r.f[u,v0]+=bary[u]*f[v0]                                              <L 82>
                var_1377 = wp::extract(var_1294, var_1342);
                var_1378 = wp::extract(var_1341, var_1371);
                var_1379 = wp::mul(var_1377, var_1378);
                var_1380 = &((var_0).f);
                var_1381 = wp::indexref(var_1380, var_1342, var_1371);
                var_1382 = wp::load(var_1381);
                var_1383 = wp::add(var_1382, var_1379);
                var_1384 = wp::indexref(var_1380, var_1342, var_1371);
                wp::store(var_1384, var_1383);
            }
            // for v0 in range(3):                                                            <L 80>
            // if block==0:low[u,v0]+=bary[u]*f[v0]                                           <L 81>
            var_1388 = (var_1264 == var_1387);
            if (var_1388) {
                var_1389 = wp::extract(var_1294, var_1385);
                var_1390 = wp::extract(var_1341, var_1386);
                var_1391 = wp::mul(var_1389, var_1390);
                wp::add_inplace(var_50, var_1385, var_1386, var_1391);
            }
            if (!var_1388) {
                // else:r.f[u,v0]+=bary[u]*f[v0]                                              <L 82>
                var_1392 = wp::extract(var_1294, var_1385);
                var_1393 = wp::extract(var_1341, var_1386);
                var_1394 = wp::mul(var_1392, var_1393);
                var_1395 = &((var_0).f);
                var_1396 = wp::indexref(var_1395, var_1385, var_1386);
                var_1397 = wp::load(var_1396);
                var_1398 = wp::add(var_1397, var_1394);
                var_1399 = wp::indexref(var_1395, var_1385, var_1386);
                wp::store(var_1399, var_1398);
            }
            // if block==0:low[u,v0]+=bary[u]*f[v0]                                           <L 81>
            var_1402 = (var_1264 == var_1401);
            if (var_1402) {
                var_1403 = wp::extract(var_1294, var_1385);
                var_1404 = wp::extract(var_1341, var_1400);
                var_1405 = wp::mul(var_1403, var_1404);
                wp::add_inplace(var_50, var_1385, var_1400, var_1405);
            }
            if (!var_1402) {
                // else:r.f[u,v0]+=bary[u]*f[v0]                                              <L 82>
                var_1406 = wp::extract(var_1294, var_1385);
                var_1407 = wp::extract(var_1341, var_1400);
                var_1408 = wp::mul(var_1406, var_1407);
                var_1409 = &((var_0).f);
                var_1410 = wp::indexref(var_1409, var_1385, var_1400);
                var_1411 = wp::load(var_1410);
                var_1412 = wp::add(var_1411, var_1408);
                var_1413 = wp::indexref(var_1409, var_1385, var_1400);
                wp::store(var_1413, var_1412);
            }
            // if block==0:low[u,v0]+=bary[u]*f[v0]                                           <L 81>
            var_1416 = (var_1264 == var_1415);
            if (var_1416) {
                var_1417 = wp::extract(var_1294, var_1385);
                var_1418 = wp::extract(var_1341, var_1414);
                var_1419 = wp::mul(var_1417, var_1418);
                wp::add_inplace(var_50, var_1385, var_1414, var_1419);
            }
            if (!var_1416) {
                // else:r.f[u,v0]+=bary[u]*f[v0]                                              <L 82>
                var_1420 = wp::extract(var_1294, var_1385);
                var_1421 = wp::extract(var_1341, var_1414);
                var_1422 = wp::mul(var_1420, var_1421);
                var_1423 = &((var_0).f);
                var_1424 = wp::indexref(var_1423, var_1385, var_1414);
                var_1425 = wp::load(var_1424);
                var_1426 = wp::add(var_1425, var_1422);
                var_1427 = wp::indexref(var_1423, var_1385, var_1414);
                wp::store(var_1427, var_1426);
            }
            // for v0 in range(3):                                                            <L 80>
            // if block==0:low[u,v0]+=bary[u]*f[v0]                                           <L 81>
            var_1431 = (var_1264 == var_1430);
            if (var_1431) {
                var_1432 = wp::extract(var_1294, var_1428);
                var_1433 = wp::extract(var_1341, var_1429);
                var_1434 = wp::mul(var_1432, var_1433);
                wp::add_inplace(var_50, var_1428, var_1429, var_1434);
            }
            if (!var_1431) {
                // else:r.f[u,v0]+=bary[u]*f[v0]                                              <L 82>
                var_1435 = wp::extract(var_1294, var_1428);
                var_1436 = wp::extract(var_1341, var_1429);
                var_1437 = wp::mul(var_1435, var_1436);
                var_1438 = &((var_0).f);
                var_1439 = wp::indexref(var_1438, var_1428, var_1429);
                var_1440 = wp::load(var_1439);
                var_1441 = wp::add(var_1440, var_1437);
                var_1442 = wp::indexref(var_1438, var_1428, var_1429);
                wp::store(var_1442, var_1441);
            }
            // if block==0:low[u,v0]+=bary[u]*f[v0]                                           <L 81>
            var_1445 = (var_1264 == var_1444);
            if (var_1445) {
                var_1446 = wp::extract(var_1294, var_1428);
                var_1447 = wp::extract(var_1341, var_1443);
                var_1448 = wp::mul(var_1446, var_1447);
                wp::add_inplace(var_50, var_1428, var_1443, var_1448);
            }
            if (!var_1445) {
                // else:r.f[u,v0]+=bary[u]*f[v0]                                              <L 82>
                var_1449 = wp::extract(var_1294, var_1428);
                var_1450 = wp::extract(var_1341, var_1443);
                var_1451 = wp::mul(var_1449, var_1450);
                var_1452 = &((var_0).f);
                var_1453 = wp::indexref(var_1452, var_1428, var_1443);
                var_1454 = wp::load(var_1453);
                var_1455 = wp::add(var_1454, var_1451);
                var_1456 = wp::indexref(var_1452, var_1428, var_1443);
                wp::store(var_1456, var_1455);
            }
            // if block==0:low[u,v0]+=bary[u]*f[v0]                                           <L 81>
            var_1459 = (var_1264 == var_1458);
            if (var_1459) {
                var_1460 = wp::extract(var_1294, var_1428);
                var_1461 = wp::extract(var_1341, var_1457);
                var_1462 = wp::mul(var_1460, var_1461);
                wp::add_inplace(var_50, var_1428, var_1457, var_1462);
            }
            if (!var_1459) {
                // else:r.f[u,v0]+=bary[u]*f[v0]                                              <L 82>
                var_1463 = wp::extract(var_1294, var_1428);
                var_1464 = wp::extract(var_1341, var_1457);
                var_1465 = wp::mul(var_1463, var_1464);
                var_1466 = &((var_0).f);
                var_1467 = wp::indexref(var_1466, var_1428, var_1457);
                var_1468 = wp::load(var_1467);
                var_1469 = wp::add(var_1468, var_1465);
                var_1470 = wp::indexref(var_1466, var_1428, var_1457);
                wp::store(var_1470, var_1469);
            }
            // if block>0:r.U+=wp.float64(.5)*wp.float64(1e9)*weight*depth*depth;r.D-=wp.dot(fr,rel);r.W+=wp.dot(f,tv);r.moment+=wp.cross(x-T,f)       <L 83>
            var_1472 = (var_1264 > var_1471);
            if (var_1472) {
                var_1473 = 0.5;
                var_1474 = 1000000000.0;
                var_1475 = wp::mul(var_1473, var_1474);
                var_1476 = wp::mul(var_1475, var_1292);
                var_1477 = wp::mul(var_1476, var_1316);
                var_1478 = wp::mul(var_1477, var_1316);
                var_1479 = &((var_0).U);
                var_1481 = wp::load(var_1479);
                var_1480 = wp::add(var_1481, var_1478);
                var_0.U = var_1480;
                var_1482 = wp::dot(var_1339, var_1321);
                var_1483 = &((var_0).D);
                var_1485 = wp::load(var_1483);
                var_1484 = wp::sub(var_1485, var_1482);
                var_0.D = var_1484;
                var_1486 = wp::dot(var_1341, var_tv);
                var_1487 = &((var_0).W);
                var_1489 = wp::load(var_1487);
                var_1488 = wp::add(var_1489, var_1486);
                var_0.W = var_1488;
                var_1490 = wp::sub(var_1296, var_T);
                var_1491 = wp::cross(var_1490, var_1341);
                var_1492 = &((var_0).moment);
                var_1494 = wp::load(var_1492);
                var_1493 = wp::add(var_1494, var_1491);
                var_0.moment = var_1493;
            }
        }
        var_1495 = wp::where(var_1309, var_1311, var_1251);
        var_1496 = wp::where(var_1309, var_1313, var_1252);
        var_1497 = wp::where(var_1309, var_1316, var_1253);
        var_1498 = wp::where(var_1309, var_1320, var_1254);
        var_1499 = wp::where(var_1309, var_1321, var_1255);
        var_1500 = wp::where(var_1309, var_1324, var_1256);
        var_1501 = wp::where(var_1309, var_1325, var_1257);
        var_1502 = wp::where(var_1309, var_1339, var_1258);
        var_1503 = wp::where(var_1309, var_1341, var_1259);
        var_1504 = wp::where(var_1309, var_1428, var_1260);
        var_1505 = wp::where(var_1309, var_1457, var_1261);
        // block=k//3;point=k%3;local=wp.vec3d(wp.float64(1./6.));local[point]=wp.float64(2./3.);C=B;weight=Ar/wp.float64(3.)       <L 71>
        var_1508 = wp::floordiv(var_1506, var_1507);
        var_1510 = wp::mod(var_1506, var_1509);
        var_1513 = wp::div(var_1511, var_1512);
        var_1514 = wp::float64(var_1513);
        var_1515 = wp::vec_t<3, wp::float64>(var_1514);
        var_1518 = wp::div(var_1516, var_1517);
        var_1519 = wp::float64(var_1518);
        wp::assign_inplace(var_1515, var_1510, var_1519);
        var_1520 = wp::copy(var_B);
        var_1521 = 3.0;
        var_1522 = wp::div(var_41, var_1521);
        // if block==1:C=L;weight=Ar/wp.float64(6.)                                           <L 72>
        var_1524 = (var_1508 == var_1523);
        if (var_1524) {
            var_1525 = wp::copy(var_47);
            var_1526 = 6.0;
            var_1527 = wp::div(var_41, var_1526);
        }
        if (!var_1524) {
            // elif block==2:C=H;weight=Ar/wp.float64(6.)                                     <L 73>
            var_1529 = (var_1508 == var_1528);
            if (var_1529) {
                var_1530 = wp::copy(var_48);
                var_1531 = 6.0;
                var_1532 = wp::div(var_41, var_1531);
            }
            var_1533 = wp::where(var_1529, var_1530, var_1520);
            var_1534 = wp::where(var_1529, var_1532, var_1522);
        }
        var_1535 = wp::where(var_1524, var_1525, var_1533);
        var_1536 = wp::where(var_1524, var_1527, var_1534);
        // bary=wp.transpose(C)*local;x=wp.transpose(X)*bary;v=wp.transpose(V)*bary;s=signed(mesh,tri,wp.transpose(R)*(x-T));r.queries+=1       <L 74>
        var_1537 = wp::transpose(var_1535);
        var_1538 = wp::mul(var_1537, var_1515);
        var_1539 = wp::transpose(var_X);
        var_1540 = wp::mul(var_1539, var_1538);
        var_1541 = wp::transpose(var_V);
        var_1542 = wp::mul(var_1541, var_1538);
        var_1543 = wp::transpose(var_R);
        var_1544 = wp::sub(var_1540, var_T);
        var_1545 = wp::mul(var_1543, var_1544);
        var_1546 = signed_0(var_mesh, var_tri, var_1545);
        var_1548 = &((var_0).queries);
        var_1550 = wp::load(var_1548);
        var_1549 = wp::add(var_1550, var_1547);
        var_0.queries = var_1549;
        // if s.phi<wp.float64(0.):                                                           <L 75>
        var_1551 = &((var_1546).phi);
        var_1552 = 0.0;
        var_1554 = wp::load(var_1551);
        var_1553 = (var_1554 < var_1552);
        if (var_1553) {
            // active=True;normal=R*s.normal;depth=-s.phi;fn=wp.float64(1e9)*weight*depth;rel=v-tv;tan=rel-wp.dot(rel,normal)*normal;speed=wp.length(tan);fr=wp.vec3d(wp.float64(0.))       <L 76>
            var_1556 = &((var_1546).normal);
            var_1558 = wp::load(var_1556);
            var_1557 = wp::mul(var_R, var_1558);
            var_1559 = &((var_1546).phi);
            var_1561 = wp::load(var_1559);
            var_1560 = wp::neg(var_1561);
            var_1562 = 1000000000.0;
            var_1563 = wp::mul(var_1562, var_1536);
            var_1564 = wp::mul(var_1563, var_1560);
            var_1565 = wp::sub(var_1542, var_tv);
            var_1566 = wp::dot(var_1565, var_1557);
            var_1567 = wp::mul(var_1566, var_1557);
            var_1568 = wp::sub(var_1565, var_1567);
            var_1569 = wp::length(var_1568);
            var_1570 = 0.0;
            var_1571 = wp::vec_t<3, wp::float64>(var_1570);
            // if speed>wp.float64(1e-30):fr=-wp.float64(.2)*fn*wp.tanh(speed/wp.float64(.001))*tan/speed       <L 77>
            var_1572 = 1e-30;
            var_1573 = (var_1569 > var_1572);
            if (var_1573) {
                var_1574 = 0.2;
                var_1575 = wp::neg(var_1574);
                var_1576 = wp::mul(var_1575, var_1564);
                var_1577 = 0.001;
                var_1578 = wp::div(var_1569, var_1577);
                var_1579 = wp::tanh(var_1578);
                var_1580 = wp::mul(var_1576, var_1579);
                var_1581 = wp::mul(var_1580, var_1568);
                var_1582 = wp::div(var_1581, var_1569);
            }
            var_1583 = wp::where(var_1573, var_1582, var_1571);
            // f=fn*normal+fr                                                                 <L 78>
            var_1584 = wp::mul(var_1564, var_1557);
            var_1585 = wp::add(var_1584, var_1583);
            // for u in range(3):                                                             <L 79>
            // for v0 in range(3):                                                            <L 80>
            // if block==0:low[u,v0]+=bary[u]*f[v0]                                           <L 81>
            var_1589 = (var_1508 == var_1588);
            if (var_1589) {
                var_1590 = wp::extract(var_1538, var_1586);
                var_1591 = wp::extract(var_1585, var_1587);
                var_1592 = wp::mul(var_1590, var_1591);
                wp::add_inplace(var_50, var_1586, var_1587, var_1592);
            }
            if (!var_1589) {
                // else:r.f[u,v0]+=bary[u]*f[v0]                                              <L 82>
                var_1593 = wp::extract(var_1538, var_1586);
                var_1594 = wp::extract(var_1585, var_1587);
                var_1595 = wp::mul(var_1593, var_1594);
                var_1596 = &((var_0).f);
                var_1597 = wp::indexref(var_1596, var_1586, var_1587);
                var_1598 = wp::load(var_1597);
                var_1599 = wp::add(var_1598, var_1595);
                var_1600 = wp::indexref(var_1596, var_1586, var_1587);
                wp::store(var_1600, var_1599);
            }
            // if block==0:low[u,v0]+=bary[u]*f[v0]                                           <L 81>
            var_1603 = (var_1508 == var_1602);
            if (var_1603) {
                var_1604 = wp::extract(var_1538, var_1586);
                var_1605 = wp::extract(var_1585, var_1601);
                var_1606 = wp::mul(var_1604, var_1605);
                wp::add_inplace(var_50, var_1586, var_1601, var_1606);
            }
            if (!var_1603) {
                // else:r.f[u,v0]+=bary[u]*f[v0]                                              <L 82>
                var_1607 = wp::extract(var_1538, var_1586);
                var_1608 = wp::extract(var_1585, var_1601);
                var_1609 = wp::mul(var_1607, var_1608);
                var_1610 = &((var_0).f);
                var_1611 = wp::indexref(var_1610, var_1586, var_1601);
                var_1612 = wp::load(var_1611);
                var_1613 = wp::add(var_1612, var_1609);
                var_1614 = wp::indexref(var_1610, var_1586, var_1601);
                wp::store(var_1614, var_1613);
            }
            // if block==0:low[u,v0]+=bary[u]*f[v0]                                           <L 81>
            var_1617 = (var_1508 == var_1616);
            if (var_1617) {
                var_1618 = wp::extract(var_1538, var_1586);
                var_1619 = wp::extract(var_1585, var_1615);
                var_1620 = wp::mul(var_1618, var_1619);
                wp::add_inplace(var_50, var_1586, var_1615, var_1620);
            }
            if (!var_1617) {
                // else:r.f[u,v0]+=bary[u]*f[v0]                                              <L 82>
                var_1621 = wp::extract(var_1538, var_1586);
                var_1622 = wp::extract(var_1585, var_1615);
                var_1623 = wp::mul(var_1621, var_1622);
                var_1624 = &((var_0).f);
                var_1625 = wp::indexref(var_1624, var_1586, var_1615);
                var_1626 = wp::load(var_1625);
                var_1627 = wp::add(var_1626, var_1623);
                var_1628 = wp::indexref(var_1624, var_1586, var_1615);
                wp::store(var_1628, var_1627);
            }
            // for v0 in range(3):                                                            <L 80>
            // if block==0:low[u,v0]+=bary[u]*f[v0]                                           <L 81>
            var_1632 = (var_1508 == var_1631);
            if (var_1632) {
                var_1633 = wp::extract(var_1538, var_1629);
                var_1634 = wp::extract(var_1585, var_1630);
                var_1635 = wp::mul(var_1633, var_1634);
                wp::add_inplace(var_50, var_1629, var_1630, var_1635);
            }
            if (!var_1632) {
                // else:r.f[u,v0]+=bary[u]*f[v0]                                              <L 82>
                var_1636 = wp::extract(var_1538, var_1629);
                var_1637 = wp::extract(var_1585, var_1630);
                var_1638 = wp::mul(var_1636, var_1637);
                var_1639 = &((var_0).f);
                var_1640 = wp::indexref(var_1639, var_1629, var_1630);
                var_1641 = wp::load(var_1640);
                var_1642 = wp::add(var_1641, var_1638);
                var_1643 = wp::indexref(var_1639, var_1629, var_1630);
                wp::store(var_1643, var_1642);
            }
            // if block==0:low[u,v0]+=bary[u]*f[v0]                                           <L 81>
            var_1646 = (var_1508 == var_1645);
            if (var_1646) {
                var_1647 = wp::extract(var_1538, var_1629);
                var_1648 = wp::extract(var_1585, var_1644);
                var_1649 = wp::mul(var_1647, var_1648);
                wp::add_inplace(var_50, var_1629, var_1644, var_1649);
            }
            if (!var_1646) {
                // else:r.f[u,v0]+=bary[u]*f[v0]                                              <L 82>
                var_1650 = wp::extract(var_1538, var_1629);
                var_1651 = wp::extract(var_1585, var_1644);
                var_1652 = wp::mul(var_1650, var_1651);
                var_1653 = &((var_0).f);
                var_1654 = wp::indexref(var_1653, var_1629, var_1644);
                var_1655 = wp::load(var_1654);
                var_1656 = wp::add(var_1655, var_1652);
                var_1657 = wp::indexref(var_1653, var_1629, var_1644);
                wp::store(var_1657, var_1656);
            }
            // if block==0:low[u,v0]+=bary[u]*f[v0]                                           <L 81>
            var_1660 = (var_1508 == var_1659);
            if (var_1660) {
                var_1661 = wp::extract(var_1538, var_1629);
                var_1662 = wp::extract(var_1585, var_1658);
                var_1663 = wp::mul(var_1661, var_1662);
                wp::add_inplace(var_50, var_1629, var_1658, var_1663);
            }
            if (!var_1660) {
                // else:r.f[u,v0]+=bary[u]*f[v0]                                              <L 82>
                var_1664 = wp::extract(var_1538, var_1629);
                var_1665 = wp::extract(var_1585, var_1658);
                var_1666 = wp::mul(var_1664, var_1665);
                var_1667 = &((var_0).f);
                var_1668 = wp::indexref(var_1667, var_1629, var_1658);
                var_1669 = wp::load(var_1668);
                var_1670 = wp::add(var_1669, var_1666);
                var_1671 = wp::indexref(var_1667, var_1629, var_1658);
                wp::store(var_1671, var_1670);
            }
            // for v0 in range(3):                                                            <L 80>
            // if block==0:low[u,v0]+=bary[u]*f[v0]                                           <L 81>
            var_1675 = (var_1508 == var_1674);
            if (var_1675) {
                var_1676 = wp::extract(var_1538, var_1672);
                var_1677 = wp::extract(var_1585, var_1673);
                var_1678 = wp::mul(var_1676, var_1677);
                wp::add_inplace(var_50, var_1672, var_1673, var_1678);
            }
            if (!var_1675) {
                // else:r.f[u,v0]+=bary[u]*f[v0]                                              <L 82>
                var_1679 = wp::extract(var_1538, var_1672);
                var_1680 = wp::extract(var_1585, var_1673);
                var_1681 = wp::mul(var_1679, var_1680);
                var_1682 = &((var_0).f);
                var_1683 = wp::indexref(var_1682, var_1672, var_1673);
                var_1684 = wp::load(var_1683);
                var_1685 = wp::add(var_1684, var_1681);
                var_1686 = wp::indexref(var_1682, var_1672, var_1673);
                wp::store(var_1686, var_1685);
            }
            // if block==0:low[u,v0]+=bary[u]*f[v0]                                           <L 81>
            var_1689 = (var_1508 == var_1688);
            if (var_1689) {
                var_1690 = wp::extract(var_1538, var_1672);
                var_1691 = wp::extract(var_1585, var_1687);
                var_1692 = wp::mul(var_1690, var_1691);
                wp::add_inplace(var_50, var_1672, var_1687, var_1692);
            }
            if (!var_1689) {
                // else:r.f[u,v0]+=bary[u]*f[v0]                                              <L 82>
                var_1693 = wp::extract(var_1538, var_1672);
                var_1694 = wp::extract(var_1585, var_1687);
                var_1695 = wp::mul(var_1693, var_1694);
                var_1696 = &((var_0).f);
                var_1697 = wp::indexref(var_1696, var_1672, var_1687);
                var_1698 = wp::load(var_1697);
                var_1699 = wp::add(var_1698, var_1695);
                var_1700 = wp::indexref(var_1696, var_1672, var_1687);
                wp::store(var_1700, var_1699);
            }
            // if block==0:low[u,v0]+=bary[u]*f[v0]                                           <L 81>
            var_1703 = (var_1508 == var_1702);
            if (var_1703) {
                var_1704 = wp::extract(var_1538, var_1672);
                var_1705 = wp::extract(var_1585, var_1701);
                var_1706 = wp::mul(var_1704, var_1705);
                wp::add_inplace(var_50, var_1672, var_1701, var_1706);
            }
            if (!var_1703) {
                // else:r.f[u,v0]+=bary[u]*f[v0]                                              <L 82>
                var_1707 = wp::extract(var_1538, var_1672);
                var_1708 = wp::extract(var_1585, var_1701);
                var_1709 = wp::mul(var_1707, var_1708);
                var_1710 = &((var_0).f);
                var_1711 = wp::indexref(var_1710, var_1672, var_1701);
                var_1712 = wp::load(var_1711);
                var_1713 = wp::add(var_1712, var_1709);
                var_1714 = wp::indexref(var_1710, var_1672, var_1701);
                wp::store(var_1714, var_1713);
            }
            // if block>0:r.U+=wp.float64(.5)*wp.float64(1e9)*weight*depth*depth;r.D-=wp.dot(fr,rel);r.W+=wp.dot(f,tv);r.moment+=wp.cross(x-T,f)       <L 83>
            var_1716 = (var_1508 > var_1715);
            if (var_1716) {
                var_1717 = 0.5;
                var_1718 = 1000000000.0;
                var_1719 = wp::mul(var_1717, var_1718);
                var_1720 = wp::mul(var_1719, var_1536);
                var_1721 = wp::mul(var_1720, var_1560);
                var_1722 = wp::mul(var_1721, var_1560);
                var_1723 = &((var_0).U);
                var_1725 = wp::load(var_1723);
                var_1724 = wp::add(var_1725, var_1722);
                var_0.U = var_1724;
                var_1726 = wp::dot(var_1583, var_1565);
                var_1727 = &((var_0).D);
                var_1729 = wp::load(var_1727);
                var_1728 = wp::sub(var_1729, var_1726);
                var_0.D = var_1728;
                var_1730 = wp::dot(var_1585, var_tv);
                var_1731 = &((var_0).W);
                var_1733 = wp::load(var_1731);
                var_1732 = wp::add(var_1733, var_1730);
                var_0.W = var_1732;
                var_1734 = wp::sub(var_1540, var_T);
                var_1735 = wp::cross(var_1734, var_1585);
                var_1736 = &((var_0).moment);
                var_1738 = wp::load(var_1736);
                var_1737 = wp::add(var_1738, var_1735);
                var_0.moment = var_1737;
            }
        }
        var_1739 = wp::where(var_1553, var_1555, var_1495);
        var_1740 = wp::where(var_1553, var_1557, var_1496);
        var_1741 = wp::where(var_1553, var_1560, var_1497);
        var_1742 = wp::where(var_1553, var_1564, var_1498);
        var_1743 = wp::where(var_1553, var_1565, var_1499);
        var_1744 = wp::where(var_1553, var_1568, var_1500);
        var_1745 = wp::where(var_1553, var_1569, var_1501);
        var_1746 = wp::where(var_1553, var_1583, var_1502);
        var_1747 = wp::where(var_1553, var_1585, var_1503);
        var_1748 = wp::where(var_1553, var_1672, var_1504);
        var_1749 = wp::where(var_1553, var_1701, var_1505);
        // block=k//3;point=k%3;local=wp.vec3d(wp.float64(1./6.));local[point]=wp.float64(2./3.);C=B;weight=Ar/wp.float64(3.)       <L 71>
        var_1752 = wp::floordiv(var_1750, var_1751);
        var_1754 = wp::mod(var_1750, var_1753);
        var_1757 = wp::div(var_1755, var_1756);
        var_1758 = wp::float64(var_1757);
        var_1759 = wp::vec_t<3, wp::float64>(var_1758);
        var_1762 = wp::div(var_1760, var_1761);
        var_1763 = wp::float64(var_1762);
        wp::assign_inplace(var_1759, var_1754, var_1763);
        var_1764 = wp::copy(var_B);
        var_1765 = 3.0;
        var_1766 = wp::div(var_41, var_1765);
        // if block==1:C=L;weight=Ar/wp.float64(6.)                                           <L 72>
        var_1768 = (var_1752 == var_1767);
        if (var_1768) {
            var_1769 = wp::copy(var_47);
            var_1770 = 6.0;
            var_1771 = wp::div(var_41, var_1770);
        }
        if (!var_1768) {
            // elif block==2:C=H;weight=Ar/wp.float64(6.)                                     <L 73>
            var_1773 = (var_1752 == var_1772);
            if (var_1773) {
                var_1774 = wp::copy(var_48);
                var_1775 = 6.0;
                var_1776 = wp::div(var_41, var_1775);
            }
            var_1777 = wp::where(var_1773, var_1774, var_1764);
            var_1778 = wp::where(var_1773, var_1776, var_1766);
        }
        var_1779 = wp::where(var_1768, var_1769, var_1777);
        var_1780 = wp::where(var_1768, var_1771, var_1778);
        // bary=wp.transpose(C)*local;x=wp.transpose(X)*bary;v=wp.transpose(V)*bary;s=signed(mesh,tri,wp.transpose(R)*(x-T));r.queries+=1       <L 74>
        var_1781 = wp::transpose(var_1779);
        var_1782 = wp::mul(var_1781, var_1759);
        var_1783 = wp::transpose(var_X);
        var_1784 = wp::mul(var_1783, var_1782);
        var_1785 = wp::transpose(var_V);
        var_1786 = wp::mul(var_1785, var_1782);
        var_1787 = wp::transpose(var_R);
        var_1788 = wp::sub(var_1784, var_T);
        var_1789 = wp::mul(var_1787, var_1788);
        var_1790 = signed_0(var_mesh, var_tri, var_1789);
        var_1792 = &((var_0).queries);
        var_1794 = wp::load(var_1792);
        var_1793 = wp::add(var_1794, var_1791);
        var_0.queries = var_1793;
        // if s.phi<wp.float64(0.):                                                           <L 75>
        var_1795 = &((var_1790).phi);
        var_1796 = 0.0;
        var_1798 = wp::load(var_1795);
        var_1797 = (var_1798 < var_1796);
        if (var_1797) {
            // active=True;normal=R*s.normal;depth=-s.phi;fn=wp.float64(1e9)*weight*depth;rel=v-tv;tan=rel-wp.dot(rel,normal)*normal;speed=wp.length(tan);fr=wp.vec3d(wp.float64(0.))       <L 76>
            var_1800 = &((var_1790).normal);
            var_1802 = wp::load(var_1800);
            var_1801 = wp::mul(var_R, var_1802);
            var_1803 = &((var_1790).phi);
            var_1805 = wp::load(var_1803);
            var_1804 = wp::neg(var_1805);
            var_1806 = 1000000000.0;
            var_1807 = wp::mul(var_1806, var_1780);
            var_1808 = wp::mul(var_1807, var_1804);
            var_1809 = wp::sub(var_1786, var_tv);
            var_1810 = wp::dot(var_1809, var_1801);
            var_1811 = wp::mul(var_1810, var_1801);
            var_1812 = wp::sub(var_1809, var_1811);
            var_1813 = wp::length(var_1812);
            var_1814 = 0.0;
            var_1815 = wp::vec_t<3, wp::float64>(var_1814);
            // if speed>wp.float64(1e-30):fr=-wp.float64(.2)*fn*wp.tanh(speed/wp.float64(.001))*tan/speed       <L 77>
            var_1816 = 1e-30;
            var_1817 = (var_1813 > var_1816);
            if (var_1817) {
                var_1818 = 0.2;
                var_1819 = wp::neg(var_1818);
                var_1820 = wp::mul(var_1819, var_1808);
                var_1821 = 0.001;
                var_1822 = wp::div(var_1813, var_1821);
                var_1823 = wp::tanh(var_1822);
                var_1824 = wp::mul(var_1820, var_1823);
                var_1825 = wp::mul(var_1824, var_1812);
                var_1826 = wp::div(var_1825, var_1813);
            }
            var_1827 = wp::where(var_1817, var_1826, var_1815);
            // f=fn*normal+fr                                                                 <L 78>
            var_1828 = wp::mul(var_1808, var_1801);
            var_1829 = wp::add(var_1828, var_1827);
            // for u in range(3):                                                             <L 79>
            // for v0 in range(3):                                                            <L 80>
            // if block==0:low[u,v0]+=bary[u]*f[v0]                                           <L 81>
            var_1833 = (var_1752 == var_1832);
            if (var_1833) {
                var_1834 = wp::extract(var_1782, var_1830);
                var_1835 = wp::extract(var_1829, var_1831);
                var_1836 = wp::mul(var_1834, var_1835);
                wp::add_inplace(var_50, var_1830, var_1831, var_1836);
            }
            if (!var_1833) {
                // else:r.f[u,v0]+=bary[u]*f[v0]                                              <L 82>
                var_1837 = wp::extract(var_1782, var_1830);
                var_1838 = wp::extract(var_1829, var_1831);
                var_1839 = wp::mul(var_1837, var_1838);
                var_1840 = &((var_0).f);
                var_1841 = wp::indexref(var_1840, var_1830, var_1831);
                var_1842 = wp::load(var_1841);
                var_1843 = wp::add(var_1842, var_1839);
                var_1844 = wp::indexref(var_1840, var_1830, var_1831);
                wp::store(var_1844, var_1843);
            }
            // if block==0:low[u,v0]+=bary[u]*f[v0]                                           <L 81>
            var_1847 = (var_1752 == var_1846);
            if (var_1847) {
                var_1848 = wp::extract(var_1782, var_1830);
                var_1849 = wp::extract(var_1829, var_1845);
                var_1850 = wp::mul(var_1848, var_1849);
                wp::add_inplace(var_50, var_1830, var_1845, var_1850);
            }
            if (!var_1847) {
                // else:r.f[u,v0]+=bary[u]*f[v0]                                              <L 82>
                var_1851 = wp::extract(var_1782, var_1830);
                var_1852 = wp::extract(var_1829, var_1845);
                var_1853 = wp::mul(var_1851, var_1852);
                var_1854 = &((var_0).f);
                var_1855 = wp::indexref(var_1854, var_1830, var_1845);
                var_1856 = wp::load(var_1855);
                var_1857 = wp::add(var_1856, var_1853);
                var_1858 = wp::indexref(var_1854, var_1830, var_1845);
                wp::store(var_1858, var_1857);
            }
            // if block==0:low[u,v0]+=bary[u]*f[v0]                                           <L 81>
            var_1861 = (var_1752 == var_1860);
            if (var_1861) {
                var_1862 = wp::extract(var_1782, var_1830);
                var_1863 = wp::extract(var_1829, var_1859);
                var_1864 = wp::mul(var_1862, var_1863);
                wp::add_inplace(var_50, var_1830, var_1859, var_1864);
            }
            if (!var_1861) {
                // else:r.f[u,v0]+=bary[u]*f[v0]                                              <L 82>
                var_1865 = wp::extract(var_1782, var_1830);
                var_1866 = wp::extract(var_1829, var_1859);
                var_1867 = wp::mul(var_1865, var_1866);
                var_1868 = &((var_0).f);
                var_1869 = wp::indexref(var_1868, var_1830, var_1859);
                var_1870 = wp::load(var_1869);
                var_1871 = wp::add(var_1870, var_1867);
                var_1872 = wp::indexref(var_1868, var_1830, var_1859);
                wp::store(var_1872, var_1871);
            }
            // for v0 in range(3):                                                            <L 80>
            // if block==0:low[u,v0]+=bary[u]*f[v0]                                           <L 81>
            var_1876 = (var_1752 == var_1875);
            if (var_1876) {
                var_1877 = wp::extract(var_1782, var_1873);
                var_1878 = wp::extract(var_1829, var_1874);
                var_1879 = wp::mul(var_1877, var_1878);
                wp::add_inplace(var_50, var_1873, var_1874, var_1879);
            }
            if (!var_1876) {
                // else:r.f[u,v0]+=bary[u]*f[v0]                                              <L 82>
                var_1880 = wp::extract(var_1782, var_1873);
                var_1881 = wp::extract(var_1829, var_1874);
                var_1882 = wp::mul(var_1880, var_1881);
                var_1883 = &((var_0).f);
                var_1884 = wp::indexref(var_1883, var_1873, var_1874);
                var_1885 = wp::load(var_1884);
                var_1886 = wp::add(var_1885, var_1882);
                var_1887 = wp::indexref(var_1883, var_1873, var_1874);
                wp::store(var_1887, var_1886);
            }
            // if block==0:low[u,v0]+=bary[u]*f[v0]                                           <L 81>
            var_1890 = (var_1752 == var_1889);
            if (var_1890) {
                var_1891 = wp::extract(var_1782, var_1873);
                var_1892 = wp::extract(var_1829, var_1888);
                var_1893 = wp::mul(var_1891, var_1892);
                wp::add_inplace(var_50, var_1873, var_1888, var_1893);
            }
            if (!var_1890) {
                // else:r.f[u,v0]+=bary[u]*f[v0]                                              <L 82>
                var_1894 = wp::extract(var_1782, var_1873);
                var_1895 = wp::extract(var_1829, var_1888);
                var_1896 = wp::mul(var_1894, var_1895);
                var_1897 = &((var_0).f);
                var_1898 = wp::indexref(var_1897, var_1873, var_1888);
                var_1899 = wp::load(var_1898);
                var_1900 = wp::add(var_1899, var_1896);
                var_1901 = wp::indexref(var_1897, var_1873, var_1888);
                wp::store(var_1901, var_1900);
            }
            // if block==0:low[u,v0]+=bary[u]*f[v0]                                           <L 81>
            var_1904 = (var_1752 == var_1903);
            if (var_1904) {
                var_1905 = wp::extract(var_1782, var_1873);
                var_1906 = wp::extract(var_1829, var_1902);
                var_1907 = wp::mul(var_1905, var_1906);
                wp::add_inplace(var_50, var_1873, var_1902, var_1907);
            }
            if (!var_1904) {
                // else:r.f[u,v0]+=bary[u]*f[v0]                                              <L 82>
                var_1908 = wp::extract(var_1782, var_1873);
                var_1909 = wp::extract(var_1829, var_1902);
                var_1910 = wp::mul(var_1908, var_1909);
                var_1911 = &((var_0).f);
                var_1912 = wp::indexref(var_1911, var_1873, var_1902);
                var_1913 = wp::load(var_1912);
                var_1914 = wp::add(var_1913, var_1910);
                var_1915 = wp::indexref(var_1911, var_1873, var_1902);
                wp::store(var_1915, var_1914);
            }
            // for v0 in range(3):                                                            <L 80>
            // if block==0:low[u,v0]+=bary[u]*f[v0]                                           <L 81>
            var_1919 = (var_1752 == var_1918);
            if (var_1919) {
                var_1920 = wp::extract(var_1782, var_1916);
                var_1921 = wp::extract(var_1829, var_1917);
                var_1922 = wp::mul(var_1920, var_1921);
                wp::add_inplace(var_50, var_1916, var_1917, var_1922);
            }
            if (!var_1919) {
                // else:r.f[u,v0]+=bary[u]*f[v0]                                              <L 82>
                var_1923 = wp::extract(var_1782, var_1916);
                var_1924 = wp::extract(var_1829, var_1917);
                var_1925 = wp::mul(var_1923, var_1924);
                var_1926 = &((var_0).f);
                var_1927 = wp::indexref(var_1926, var_1916, var_1917);
                var_1928 = wp::load(var_1927);
                var_1929 = wp::add(var_1928, var_1925);
                var_1930 = wp::indexref(var_1926, var_1916, var_1917);
                wp::store(var_1930, var_1929);
            }
            // if block==0:low[u,v0]+=bary[u]*f[v0]                                           <L 81>
            var_1933 = (var_1752 == var_1932);
            if (var_1933) {
                var_1934 = wp::extract(var_1782, var_1916);
                var_1935 = wp::extract(var_1829, var_1931);
                var_1936 = wp::mul(var_1934, var_1935);
                wp::add_inplace(var_50, var_1916, var_1931, var_1936);
            }
            if (!var_1933) {
                // else:r.f[u,v0]+=bary[u]*f[v0]                                              <L 82>
                var_1937 = wp::extract(var_1782, var_1916);
                var_1938 = wp::extract(var_1829, var_1931);
                var_1939 = wp::mul(var_1937, var_1938);
                var_1940 = &((var_0).f);
                var_1941 = wp::indexref(var_1940, var_1916, var_1931);
                var_1942 = wp::load(var_1941);
                var_1943 = wp::add(var_1942, var_1939);
                var_1944 = wp::indexref(var_1940, var_1916, var_1931);
                wp::store(var_1944, var_1943);
            }
            // if block==0:low[u,v0]+=bary[u]*f[v0]                                           <L 81>
            var_1947 = (var_1752 == var_1946);
            if (var_1947) {
                var_1948 = wp::extract(var_1782, var_1916);
                var_1949 = wp::extract(var_1829, var_1945);
                var_1950 = wp::mul(var_1948, var_1949);
                wp::add_inplace(var_50, var_1916, var_1945, var_1950);
            }
            if (!var_1947) {
                // else:r.f[u,v0]+=bary[u]*f[v0]                                              <L 82>
                var_1951 = wp::extract(var_1782, var_1916);
                var_1952 = wp::extract(var_1829, var_1945);
                var_1953 = wp::mul(var_1951, var_1952);
                var_1954 = &((var_0).f);
                var_1955 = wp::indexref(var_1954, var_1916, var_1945);
                var_1956 = wp::load(var_1955);
                var_1957 = wp::add(var_1956, var_1953);
                var_1958 = wp::indexref(var_1954, var_1916, var_1945);
                wp::store(var_1958, var_1957);
            }
            // if block>0:r.U+=wp.float64(.5)*wp.float64(1e9)*weight*depth*depth;r.D-=wp.dot(fr,rel);r.W+=wp.dot(f,tv);r.moment+=wp.cross(x-T,f)       <L 83>
            var_1960 = (var_1752 > var_1959);
            if (var_1960) {
                var_1961 = 0.5;
                var_1962 = 1000000000.0;
                var_1963 = wp::mul(var_1961, var_1962);
                var_1964 = wp::mul(var_1963, var_1780);
                var_1965 = wp::mul(var_1964, var_1804);
                var_1966 = wp::mul(var_1965, var_1804);
                var_1967 = &((var_0).U);
                var_1969 = wp::load(var_1967);
                var_1968 = wp::add(var_1969, var_1966);
                var_0.U = var_1968;
                var_1970 = wp::dot(var_1827, var_1809);
                var_1971 = &((var_0).D);
                var_1973 = wp::load(var_1971);
                var_1972 = wp::sub(var_1973, var_1970);
                var_0.D = var_1972;
                var_1974 = wp::dot(var_1829, var_tv);
                var_1975 = &((var_0).W);
                var_1977 = wp::load(var_1975);
                var_1976 = wp::add(var_1977, var_1974);
                var_0.W = var_1976;
                var_1978 = wp::sub(var_1784, var_T);
                var_1979 = wp::cross(var_1978, var_1829);
                var_1980 = &((var_0).moment);
                var_1982 = wp::load(var_1980);
                var_1981 = wp::add(var_1982, var_1979);
                var_0.moment = var_1981;
            }
        }
        var_1983 = wp::where(var_1797, var_1799, var_1739);
        var_1984 = wp::where(var_1797, var_1801, var_1740);
        var_1985 = wp::where(var_1797, var_1804, var_1741);
        var_1986 = wp::where(var_1797, var_1808, var_1742);
        var_1987 = wp::where(var_1797, var_1809, var_1743);
        var_1988 = wp::where(var_1797, var_1812, var_1744);
        var_1989 = wp::where(var_1797, var_1813, var_1745);
        var_1990 = wp::where(var_1797, var_1827, var_1746);
        var_1991 = wp::where(var_1797, var_1829, var_1747);
        var_1992 = wp::where(var_1797, var_1916, var_1748);
        var_1993 = wp::where(var_1797, var_1945, var_1749);
        // block=k//3;point=k%3;local=wp.vec3d(wp.float64(1./6.));local[point]=wp.float64(2./3.);C=B;weight=Ar/wp.float64(3.)       <L 71>
        var_1996 = wp::floordiv(var_1994, var_1995);
        var_1998 = wp::mod(var_1994, var_1997);
        var_2001 = wp::div(var_1999, var_2000);
        var_2002 = wp::float64(var_2001);
        var_2003 = wp::vec_t<3, wp::float64>(var_2002);
        var_2006 = wp::div(var_2004, var_2005);
        var_2007 = wp::float64(var_2006);
        wp::assign_inplace(var_2003, var_1998, var_2007);
        var_2008 = wp::copy(var_B);
        var_2009 = 3.0;
        var_2010 = wp::div(var_41, var_2009);
        // if block==1:C=L;weight=Ar/wp.float64(6.)                                           <L 72>
        var_2012 = (var_1996 == var_2011);
        if (var_2012) {
            var_2013 = wp::copy(var_47);
            var_2014 = 6.0;
            var_2015 = wp::div(var_41, var_2014);
        }
        if (!var_2012) {
            // elif block==2:C=H;weight=Ar/wp.float64(6.)                                     <L 73>
            var_2017 = (var_1996 == var_2016);
            if (var_2017) {
                var_2018 = wp::copy(var_48);
                var_2019 = 6.0;
                var_2020 = wp::div(var_41, var_2019);
            }
            var_2021 = wp::where(var_2017, var_2018, var_2008);
            var_2022 = wp::where(var_2017, var_2020, var_2010);
        }
        var_2023 = wp::where(var_2012, var_2013, var_2021);
        var_2024 = wp::where(var_2012, var_2015, var_2022);
        // bary=wp.transpose(C)*local;x=wp.transpose(X)*bary;v=wp.transpose(V)*bary;s=signed(mesh,tri,wp.transpose(R)*(x-T));r.queries+=1       <L 74>
        var_2025 = wp::transpose(var_2023);
        var_2026 = wp::mul(var_2025, var_2003);
        var_2027 = wp::transpose(var_X);
        var_2028 = wp::mul(var_2027, var_2026);
        var_2029 = wp::transpose(var_V);
        var_2030 = wp::mul(var_2029, var_2026);
        var_2031 = wp::transpose(var_R);
        var_2032 = wp::sub(var_2028, var_T);
        var_2033 = wp::mul(var_2031, var_2032);
        var_2034 = signed_0(var_mesh, var_tri, var_2033);
        var_2036 = &((var_0).queries);
        var_2038 = wp::load(var_2036);
        var_2037 = wp::add(var_2038, var_2035);
        var_0.queries = var_2037;
        // if s.phi<wp.float64(0.):                                                           <L 75>
        var_2039 = &((var_2034).phi);
        var_2040 = 0.0;
        var_2042 = wp::load(var_2039);
        var_2041 = (var_2042 < var_2040);
        if (var_2041) {
            // active=True;normal=R*s.normal;depth=-s.phi;fn=wp.float64(1e9)*weight*depth;rel=v-tv;tan=rel-wp.dot(rel,normal)*normal;speed=wp.length(tan);fr=wp.vec3d(wp.float64(0.))       <L 76>
            var_2044 = &((var_2034).normal);
            var_2046 = wp::load(var_2044);
            var_2045 = wp::mul(var_R, var_2046);
            var_2047 = &((var_2034).phi);
            var_2049 = wp::load(var_2047);
            var_2048 = wp::neg(var_2049);
            var_2050 = 1000000000.0;
            var_2051 = wp::mul(var_2050, var_2024);
            var_2052 = wp::mul(var_2051, var_2048);
            var_2053 = wp::sub(var_2030, var_tv);
            var_2054 = wp::dot(var_2053, var_2045);
            var_2055 = wp::mul(var_2054, var_2045);
            var_2056 = wp::sub(var_2053, var_2055);
            var_2057 = wp::length(var_2056);
            var_2058 = 0.0;
            var_2059 = wp::vec_t<3, wp::float64>(var_2058);
            // if speed>wp.float64(1e-30):fr=-wp.float64(.2)*fn*wp.tanh(speed/wp.float64(.001))*tan/speed       <L 77>
            var_2060 = 1e-30;
            var_2061 = (var_2057 > var_2060);
            if (var_2061) {
                var_2062 = 0.2;
                var_2063 = wp::neg(var_2062);
                var_2064 = wp::mul(var_2063, var_2052);
                var_2065 = 0.001;
                var_2066 = wp::div(var_2057, var_2065);
                var_2067 = wp::tanh(var_2066);
                var_2068 = wp::mul(var_2064, var_2067);
                var_2069 = wp::mul(var_2068, var_2056);
                var_2070 = wp::div(var_2069, var_2057);
            }
            var_2071 = wp::where(var_2061, var_2070, var_2059);
            // f=fn*normal+fr                                                                 <L 78>
            var_2072 = wp::mul(var_2052, var_2045);
            var_2073 = wp::add(var_2072, var_2071);
            // for u in range(3):                                                             <L 79>
            // for v0 in range(3):                                                            <L 80>
            // if block==0:low[u,v0]+=bary[u]*f[v0]                                           <L 81>
            var_2077 = (var_1996 == var_2076);
            if (var_2077) {
                var_2078 = wp::extract(var_2026, var_2074);
                var_2079 = wp::extract(var_2073, var_2075);
                var_2080 = wp::mul(var_2078, var_2079);
                wp::add_inplace(var_50, var_2074, var_2075, var_2080);
            }
            if (!var_2077) {
                // else:r.f[u,v0]+=bary[u]*f[v0]                                              <L 82>
                var_2081 = wp::extract(var_2026, var_2074);
                var_2082 = wp::extract(var_2073, var_2075);
                var_2083 = wp::mul(var_2081, var_2082);
                var_2084 = &((var_0).f);
                var_2085 = wp::indexref(var_2084, var_2074, var_2075);
                var_2086 = wp::load(var_2085);
                var_2087 = wp::add(var_2086, var_2083);
                var_2088 = wp::indexref(var_2084, var_2074, var_2075);
                wp::store(var_2088, var_2087);
            }
            // if block==0:low[u,v0]+=bary[u]*f[v0]                                           <L 81>
            var_2091 = (var_1996 == var_2090);
            if (var_2091) {
                var_2092 = wp::extract(var_2026, var_2074);
                var_2093 = wp::extract(var_2073, var_2089);
                var_2094 = wp::mul(var_2092, var_2093);
                wp::add_inplace(var_50, var_2074, var_2089, var_2094);
            }
            if (!var_2091) {
                // else:r.f[u,v0]+=bary[u]*f[v0]                                              <L 82>
                var_2095 = wp::extract(var_2026, var_2074);
                var_2096 = wp::extract(var_2073, var_2089);
                var_2097 = wp::mul(var_2095, var_2096);
                var_2098 = &((var_0).f);
                var_2099 = wp::indexref(var_2098, var_2074, var_2089);
                var_2100 = wp::load(var_2099);
                var_2101 = wp::add(var_2100, var_2097);
                var_2102 = wp::indexref(var_2098, var_2074, var_2089);
                wp::store(var_2102, var_2101);
            }
            // if block==0:low[u,v0]+=bary[u]*f[v0]                                           <L 81>
            var_2105 = (var_1996 == var_2104);
            if (var_2105) {
                var_2106 = wp::extract(var_2026, var_2074);
                var_2107 = wp::extract(var_2073, var_2103);
                var_2108 = wp::mul(var_2106, var_2107);
                wp::add_inplace(var_50, var_2074, var_2103, var_2108);
            }
            if (!var_2105) {
                // else:r.f[u,v0]+=bary[u]*f[v0]                                              <L 82>
                var_2109 = wp::extract(var_2026, var_2074);
                var_2110 = wp::extract(var_2073, var_2103);
                var_2111 = wp::mul(var_2109, var_2110);
                var_2112 = &((var_0).f);
                var_2113 = wp::indexref(var_2112, var_2074, var_2103);
                var_2114 = wp::load(var_2113);
                var_2115 = wp::add(var_2114, var_2111);
                var_2116 = wp::indexref(var_2112, var_2074, var_2103);
                wp::store(var_2116, var_2115);
            }
            // for v0 in range(3):                                                            <L 80>
            // if block==0:low[u,v0]+=bary[u]*f[v0]                                           <L 81>
            var_2120 = (var_1996 == var_2119);
            if (var_2120) {
                var_2121 = wp::extract(var_2026, var_2117);
                var_2122 = wp::extract(var_2073, var_2118);
                var_2123 = wp::mul(var_2121, var_2122);
                wp::add_inplace(var_50, var_2117, var_2118, var_2123);
            }
            if (!var_2120) {
                // else:r.f[u,v0]+=bary[u]*f[v0]                                              <L 82>
                var_2124 = wp::extract(var_2026, var_2117);
                var_2125 = wp::extract(var_2073, var_2118);
                var_2126 = wp::mul(var_2124, var_2125);
                var_2127 = &((var_0).f);
                var_2128 = wp::indexref(var_2127, var_2117, var_2118);
                var_2129 = wp::load(var_2128);
                var_2130 = wp::add(var_2129, var_2126);
                var_2131 = wp::indexref(var_2127, var_2117, var_2118);
                wp::store(var_2131, var_2130);
            }
            // if block==0:low[u,v0]+=bary[u]*f[v0]                                           <L 81>
            var_2134 = (var_1996 == var_2133);
            if (var_2134) {
                var_2135 = wp::extract(var_2026, var_2117);
                var_2136 = wp::extract(var_2073, var_2132);
                var_2137 = wp::mul(var_2135, var_2136);
                wp::add_inplace(var_50, var_2117, var_2132, var_2137);
            }
            if (!var_2134) {
                // else:r.f[u,v0]+=bary[u]*f[v0]                                              <L 82>
                var_2138 = wp::extract(var_2026, var_2117);
                var_2139 = wp::extract(var_2073, var_2132);
                var_2140 = wp::mul(var_2138, var_2139);
                var_2141 = &((var_0).f);
                var_2142 = wp::indexref(var_2141, var_2117, var_2132);
                var_2143 = wp::load(var_2142);
                var_2144 = wp::add(var_2143, var_2140);
                var_2145 = wp::indexref(var_2141, var_2117, var_2132);
                wp::store(var_2145, var_2144);
            }
            // if block==0:low[u,v0]+=bary[u]*f[v0]                                           <L 81>
            var_2148 = (var_1996 == var_2147);
            if (var_2148) {
                var_2149 = wp::extract(var_2026, var_2117);
                var_2150 = wp::extract(var_2073, var_2146);
                var_2151 = wp::mul(var_2149, var_2150);
                wp::add_inplace(var_50, var_2117, var_2146, var_2151);
            }
            if (!var_2148) {
                // else:r.f[u,v0]+=bary[u]*f[v0]                                              <L 82>
                var_2152 = wp::extract(var_2026, var_2117);
                var_2153 = wp::extract(var_2073, var_2146);
                var_2154 = wp::mul(var_2152, var_2153);
                var_2155 = &((var_0).f);
                var_2156 = wp::indexref(var_2155, var_2117, var_2146);
                var_2157 = wp::load(var_2156);
                var_2158 = wp::add(var_2157, var_2154);
                var_2159 = wp::indexref(var_2155, var_2117, var_2146);
                wp::store(var_2159, var_2158);
            }
            // for v0 in range(3):                                                            <L 80>
            // if block==0:low[u,v0]+=bary[u]*f[v0]                                           <L 81>
            var_2163 = (var_1996 == var_2162);
            if (var_2163) {
                var_2164 = wp::extract(var_2026, var_2160);
                var_2165 = wp::extract(var_2073, var_2161);
                var_2166 = wp::mul(var_2164, var_2165);
                wp::add_inplace(var_50, var_2160, var_2161, var_2166);
            }
            if (!var_2163) {
                // else:r.f[u,v0]+=bary[u]*f[v0]                                              <L 82>
                var_2167 = wp::extract(var_2026, var_2160);
                var_2168 = wp::extract(var_2073, var_2161);
                var_2169 = wp::mul(var_2167, var_2168);
                var_2170 = &((var_0).f);
                var_2171 = wp::indexref(var_2170, var_2160, var_2161);
                var_2172 = wp::load(var_2171);
                var_2173 = wp::add(var_2172, var_2169);
                var_2174 = wp::indexref(var_2170, var_2160, var_2161);
                wp::store(var_2174, var_2173);
            }
            // if block==0:low[u,v0]+=bary[u]*f[v0]                                           <L 81>
            var_2177 = (var_1996 == var_2176);
            if (var_2177) {
                var_2178 = wp::extract(var_2026, var_2160);
                var_2179 = wp::extract(var_2073, var_2175);
                var_2180 = wp::mul(var_2178, var_2179);
                wp::add_inplace(var_50, var_2160, var_2175, var_2180);
            }
            if (!var_2177) {
                // else:r.f[u,v0]+=bary[u]*f[v0]                                              <L 82>
                var_2181 = wp::extract(var_2026, var_2160);
                var_2182 = wp::extract(var_2073, var_2175);
                var_2183 = wp::mul(var_2181, var_2182);
                var_2184 = &((var_0).f);
                var_2185 = wp::indexref(var_2184, var_2160, var_2175);
                var_2186 = wp::load(var_2185);
                var_2187 = wp::add(var_2186, var_2183);
                var_2188 = wp::indexref(var_2184, var_2160, var_2175);
                wp::store(var_2188, var_2187);
            }
            // if block==0:low[u,v0]+=bary[u]*f[v0]                                           <L 81>
            var_2191 = (var_1996 == var_2190);
            if (var_2191) {
                var_2192 = wp::extract(var_2026, var_2160);
                var_2193 = wp::extract(var_2073, var_2189);
                var_2194 = wp::mul(var_2192, var_2193);
                wp::add_inplace(var_50, var_2160, var_2189, var_2194);
            }
            if (!var_2191) {
                // else:r.f[u,v0]+=bary[u]*f[v0]                                              <L 82>
                var_2195 = wp::extract(var_2026, var_2160);
                var_2196 = wp::extract(var_2073, var_2189);
                var_2197 = wp::mul(var_2195, var_2196);
                var_2198 = &((var_0).f);
                var_2199 = wp::indexref(var_2198, var_2160, var_2189);
                var_2200 = wp::load(var_2199);
                var_2201 = wp::add(var_2200, var_2197);
                var_2202 = wp::indexref(var_2198, var_2160, var_2189);
                wp::store(var_2202, var_2201);
            }
            // if block>0:r.U+=wp.float64(.5)*wp.float64(1e9)*weight*depth*depth;r.D-=wp.dot(fr,rel);r.W+=wp.dot(f,tv);r.moment+=wp.cross(x-T,f)       <L 83>
            var_2204 = (var_1996 > var_2203);
            if (var_2204) {
                var_2205 = 0.5;
                var_2206 = 1000000000.0;
                var_2207 = wp::mul(var_2205, var_2206);
                var_2208 = wp::mul(var_2207, var_2024);
                var_2209 = wp::mul(var_2208, var_2048);
                var_2210 = wp::mul(var_2209, var_2048);
                var_2211 = &((var_0).U);
                var_2213 = wp::load(var_2211);
                var_2212 = wp::add(var_2213, var_2210);
                var_0.U = var_2212;
                var_2214 = wp::dot(var_2071, var_2053);
                var_2215 = &((var_0).D);
                var_2217 = wp::load(var_2215);
                var_2216 = wp::sub(var_2217, var_2214);
                var_0.D = var_2216;
                var_2218 = wp::dot(var_2073, var_tv);
                var_2219 = &((var_0).W);
                var_2221 = wp::load(var_2219);
                var_2220 = wp::add(var_2221, var_2218);
                var_0.W = var_2220;
                var_2222 = wp::sub(var_2028, var_T);
                var_2223 = wp::cross(var_2222, var_2073);
                var_2224 = &((var_0).moment);
                var_2226 = wp::load(var_2224);
                var_2225 = wp::add(var_2226, var_2223);
                var_0.moment = var_2225;
            }
        }
        var_2227 = wp::where(var_2041, var_2043, var_1983);
        var_2228 = wp::where(var_2041, var_2045, var_1984);
        var_2229 = wp::where(var_2041, var_2048, var_1985);
        var_2230 = wp::where(var_2041, var_2052, var_1986);
        var_2231 = wp::where(var_2041, var_2053, var_1987);
        var_2232 = wp::where(var_2041, var_2056, var_1988);
        var_2233 = wp::where(var_2041, var_2057, var_1989);
        var_2234 = wp::where(var_2041, var_2071, var_1990);
        var_2235 = wp::where(var_2041, var_2073, var_1991);
        var_2236 = wp::where(var_2041, var_2160, var_1992);
        var_2237 = wp::where(var_2041, var_2189, var_1993);
        // for u in range(3):r.error+=wp.length(r.f[u]-low[u])                                <L 84>
        var_2239 = &((var_0).f);
        var_2241 = wp::load(var_2239);
        var_2240 = wp::extract(var_2241, var_2238);
        var_2242 = wp::extract(var_50, var_2238);
        var_2243 = wp::sub(var_2240, var_2242);
        var_2244 = wp::length(var_2243);
        var_2245 = &((var_0).error);
        var_2247 = wp::load(var_2245);
        var_2246 = wp::add(var_2247, var_2244);
        var_0.error = var_2246;
        var_2249 = &((var_0).f);
        var_2251 = wp::load(var_2249);
        var_2250 = wp::extract(var_2251, var_2248);
        var_2252 = wp::extract(var_50, var_2248);
        var_2253 = wp::sub(var_2250, var_2252);
        var_2254 = wp::length(var_2253);
        var_2255 = &((var_0).error);
        var_2257 = wp::load(var_2255);
        var_2256 = wp::add(var_2257, var_2254);
        var_0.error = var_2256;
        var_2259 = &((var_0).f);
        var_2261 = wp::load(var_2259);
        var_2260 = wp::extract(var_2261, var_2258);
        var_2262 = wp::extract(var_50, var_2258);
        var_2263 = wp::sub(var_2260, var_2262);
        var_2264 = wp::length(var_2263);
        var_2265 = &((var_0).error);
        var_2267 = wp::load(var_2265);
        var_2266 = wp::add(var_2267, var_2264);
        var_0.error = var_2266;
    }
    // return r                                                                               <L 86>
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


// /home/omen/Documents/Codex/experiments/tomato_adaptive_contact_20261112_v24/src/allocated_gpu.py:25
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


// /home/omen/Documents/Codex/experiments/tomato_adaptive_contact_20261112_v24/src/allocated_gpu.py:53
static CUDA_CALLABLE void adj_bisect_0(
    wp::mat_t<3, 3, wp::float64> var_B,
    wp::mat_t<3, 3, wp::float64> var_X,
    wp::mat_t<3, 3, wp::float64> & ret_0,
    wp::mat_t<3, 3, wp::float64> & ret_1,
    wp::mat_t<3, 3, wp::float64> & adj_B,
    wp::mat_t<3, 3, wp::float64> & adj_X,
    wp::mat_t<3, 3, wp::float64> & adj_ret_0,
    wp::mat_t<3, 3, wp::float64> & adj_ret_1)
{
	// reverse mode disabled (module option "enable_backward" is False or no dependent kernel found with "enable_backward")
}


// /home/omen/Documents/Codex/experiments/tomato_adaptive_contact_20261112_v24/src/allocated_gpu.py:64
static CUDA_CALLABLE void adj_evaluate_leaf_0(
    wp::uint64 var_mesh,
    wp::array_t<wp::vec_t<3, wp::float64>> var_tri,
    wp::mat_t<3, 3, wp::float64> var_B,
    wp::mat_t<3, 3, wp::float64> var_X,
    wp::mat_t<3, 3, wp::float64> var_V,
    wp::float64 var_A,
    wp::mat_t<3, 3, wp::float64> var_R,
    wp::vec_t<3, wp::float64> var_T,
    wp::vec_t<3, wp::float64> var_tv,
    wp::uint64 & adj_mesh,
    wp::array_t<wp::vec_t<3, wp::float64>> & adj_tri,
    wp::mat_t<3, 3, wp::float64> & adj_B,
    wp::mat_t<3, 3, wp::float64> & adj_X,
    wp::mat_t<3, 3, wp::float64> & adj_V,
    wp::float64 & adj_A,
    wp::mat_t<3, 3, wp::float64> & adj_R,
    wp::vec_t<3, wp::float64> & adj_T,
    wp::vec_t<3, wp::float64> & adj_tv,
    Value_53a65c4a & adj_ret)
{
	// reverse mode disabled (module option "enable_backward" is False or no dependent kernel found with "enable_backward")
}



extern "C" __global__ void collect_42ce4f39_cuda_kernel_forward(
    wp::launch_bounds_t<1> dim,
    wp::int32 var_ncells,
    wp::array_t<wp::vec_t<3, wp::float32>> var_ff,
    wp::array_t<wp::float32> var_uu,
    wp::array_t<wp::float32> var_dd,
    wp::array_t<wp::float32> var_ww,
    wp::array_t<wp::vec_t<3, wp::float32>> var_mm,
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
        wp::float64 var_5;
        wp::vec_t<3, wp::float64> var_6;
        wp::float64 var_7;
        wp::float64 var_8;
        wp::float64 var_9;
        wp::float64 var_10;
        wp::vec_t<3, wp::float64> var_11;
        wp::range_t var_12;
        wp::int32 var_13;
        wp::int32 var_14;
        wp::int32 var_15;
        const wp::int32 var_16 = 3;
        wp::int32 var_17;
        wp::int32 var_18;
        wp::vec_t<3, wp::float32>* var_19;
        wp::vec_t<3, wp::float64> var_20;
        wp::vec_t<3, wp::float32> var_21;
        wp::vec_t<3, wp::float64> var_22;
        wp::float32* var_23;
        wp::float64 var_24;
        wp::float32 var_25;
        wp::float64 var_26;
        wp::float32* var_27;
        wp::float64 var_28;
        wp::float32 var_29;
        wp::float64 var_30;
        wp::float32* var_31;
        wp::float64 var_32;
        wp::float32 var_33;
        wp::float64 var_34;
        wp::vec_t<3, wp::float32>* var_35;
        wp::vec_t<3, wp::float64> var_36;
        wp::vec_t<3, wp::float32> var_37;
        wp::vec_t<3, wp::float64> var_38;
        wp::vec_t<3, wp::float32> var_39;
        wp::float32 var_40;
        wp::float32 var_41;
        wp::float32 var_42;
        wp::vec_t<3, wp::float32> var_43;
        //---------
        // forward
        // def collect(ncells:int,ff:wp.array(dtype=wp.vec3),uu:wp.array(dtype=float),dd:wp.array(dtype=float),ww:wp.array(dtype=float),mm:wp.array(dtype=wp.vec3),cf:wp.array(dtype=wp.vec3),cu:wp.array(dtype=float),cp:wp.array(dtype=float),power:wp.array(dtype=float),moment:wp.array(dtype=wp.vec3)):       <L 179>
        // k=wp.tid();face=k//3;vertex=k%3;f=wp.vec3d(wp.float64(0.));u=wp.float64(0.);d=wp.float64(0.);w=wp.float64(0.);m=wp.vec3d(wp.float64(0.))       <L 180>
        var_0 = builtin_tid1d();
        var_2 = wp::floordiv(var_0, var_1);
        var_4 = wp::mod(var_0, var_3);
        var_5 = 0.0;
        var_6 = wp::vec_t<3, wp::float64>(var_5);
        var_7 = 0.0;
        var_8 = 0.0;
        var_9 = 0.0;
        var_10 = 0.0;
        var_11 = wp::vec_t<3, wp::float64>(var_10);
        // for c in range(ncells):                                                                <L 181>
        var_12 = wp::range(var_ncells);
        start_for_0:;
            if (iter_cmp(var_12) == 0) goto end_for_0;
            var_13 = wp::iter_next(var_12);
            // j=(face*ncells+c)*3+vertex;f+=wp.vec3d(ff[j]);u+=wp.float64(uu[j]);d+=wp.float64(dd[j]);w+=wp.float64(ww[j]);m+=wp.vec3d(mm[j])       <L 182>
            var_14 = wp::mul(var_2, var_ncells);
            var_15 = wp::add(var_14, var_13);
            var_17 = wp::mul(var_15, var_16);
            var_18 = wp::add(var_17, var_4);
            var_19 = wp::address(var_ff, var_18);
            var_21 = wp::load(var_19);
            var_20 = wp::vec_t<3, wp::float64>(var_21);
            var_22 = wp::add(var_6, var_20);
            var_23 = wp::address(var_uu, var_18);
            var_25 = wp::load(var_23);
            var_24 = wp::float64(var_25);
            var_26 = wp::add(var_7, var_24);
            var_27 = wp::address(var_dd, var_18);
            var_29 = wp::load(var_27);
            var_28 = wp::float64(var_29);
            var_30 = wp::add(var_8, var_28);
            var_31 = wp::address(var_ww, var_18);
            var_33 = wp::load(var_31);
            var_32 = wp::float64(var_33);
            var_34 = wp::add(var_9, var_32);
            var_35 = wp::address(var_mm, var_18);
            var_37 = wp::load(var_35);
            var_36 = wp::vec_t<3, wp::float64>(var_37);
            var_38 = wp::add(var_11, var_36);
            wp::assign(var_6, var_22);
            wp::assign(var_7, var_26);
            wp::assign(var_8, var_30);
            wp::assign(var_9, var_34);
            wp::assign(var_11, var_38);
            goto start_for_0;
        end_for_0:;
        // cf[k]=wp.vec3(f);cu[k]=float(u);cp[k]=float(d);power[k]=float(w);moment[k]=wp.vec3(m)       <L 183>
        var_39 = wp::vec_t<3, wp::float32>(var_6);
        wp::array_store(var_cf, var_0, var_39);
        var_40 = wp::float(var_7);
        wp::array_store(var_cu, var_0, var_40);
        var_41 = wp::float(var_8);
        wp::array_store(var_cp, var_0, var_41);
        var_42 = wp::float(var_9);
        wp::array_store(var_power, var_0, var_42);
        var_43 = wp::vec_t<3, wp::float32>(var_11);
        wp::array_store(var_moment, var_0, var_43);
    }
}



extern "C" __global__ void integrate_6467655c_cuda_kernel_forward(
    wp::launch_bounds_t<1> dim,
    wp::uint64 var_mesh,
    wp::array_t<wp::vec_t<3, wp::float64>> var_tri,
    wp::vec_t<3, wp::float64> var_bbmin,
    wp::vec_t<3, wp::float64> var_bbmax,
    wp::array_t<wp::vec_t<4, wp::float64>> var_planes,
    wp::array_t<wp::vec_t<3, wp::float64>> var_bounds,
    wp::int32 var_ncells,
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
    wp::array_t<wp::float64> var_areas,
    wp::float64 var_area_total,
    wp::array_t<wp::vec_t<3, wp::float32>> var_q,
    wp::array_t<wp::vec_t<3, wp::float32>> var_vel,
    wp::array_t<wp::vec_t<3, wp::float64>> var_polygon,
    wp::array_t<wp::mat_t<3, 3, wp::float64>> var_Bs,
    wp::array_t<Value_53a65c4a> var_vals,
    wp::array_t<wp::int32> var_depths,
    wp::array_t<wp::int32> var_counts,
    wp::array_t<wp::int32> var_query_counts,
    wp::array_t<wp::vec_t<3, wp::float32>> var_cf,
    wp::array_t<wp::float32> var_cu,
    wp::array_t<wp::float32> var_cp,
    wp::array_t<wp::float32> var_power,
    wp::array_t<wp::vec_t<3, wp::float32>> var_moment,
    wp::array_t<wp::int32> var_bad,
    wp::array_t<wp::float64> var_failure,
    wp::int32 var_cap,
    wp::float64 var_relative_tol,
    wp::float64 var_absolute_tol,
    wp::int32 var_maxdepth,
    wp::array_t<wp::int32> var_polycounts,
    wp::array_t<wp::int32> var_polysources,
    wp::array_t<wp::int32> var_active_count)
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
        wp::float64 var_3;
        wp::mat_t<3, 3, wp::float64> var_4;
        wp::float64 var_5;
        wp::mat_t<3, 3, wp::float64> var_6;
        wp::float64 var_7;
        wp::mat_t<3, 3, wp::float64> var_8;
        const wp::int32 var_9 = 0;
        wp::float64* var_10;
        wp::float64 var_11;
        wp::float64 var_12;
        wp::float64 var_13;
        wp::float64 var_14;
        wp::float64 var_15;
        bool var_16;
        wp::float64 var_17;
        wp::float64 var_18;
        wp::float64 var_19;
        wp::float64 var_20;
        wp::float64 var_21;
        wp::float64 var_22;
        wp::float64 var_23;
        wp::float64 var_24;
        wp::float64 var_25;
        wp::float64 var_26;
        wp::float64 var_27;
        wp::float64 var_28;
        wp::float64 var_29;
        wp::float64 var_30;
        wp::float64 var_31;
        bool var_32;
        wp::float64 var_33;
        wp::float64 var_34;
        wp::float64 var_35;
        wp::float64 var_36;
        bool var_37;
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
        wp::float64 var_52;
        wp::float64 var_53;
        wp::float64 var_54;
        wp::float64 var_55;
        wp::float64 var_56;
        wp::float64 var_57;
        wp::float64 var_58;
        wp::float64 var_59;
        wp::vec_t<3, wp::float64> var_60;
        wp::vec_t<3, wp::float64> var_61;
        wp::vec_t<3, wp::float64> var_62;
        const wp::int32 var_63 = 0;
        const wp::int32 var_64 = 3;
        wp::int32 var_65;
        wp::int32 var_66;
        wp::vec_t<3, wp::float64>* var_67;
        wp::vec_t<3, wp::float64> var_68;
        wp::vec_t<3, wp::float64> var_69;
        wp::float64 var_70;
        wp::vec_t<3, wp::float64> var_71;
        wp::int32* var_72;
        const wp::int32 var_73 = 1;
        wp::int32 var_74;
        wp::int32* var_75;
        wp::range_t var_76;
        wp::int32 var_77;
        wp::int32 var_78;
        wp::int32 var_79;
        wp::float64* var_80;
        wp::int32* var_81;
        wp::vec_t<3, wp::float32>* var_82;
        wp::int32 var_83;
        wp::vec_t<3, wp::float64> var_84;
        wp::vec_t<3, wp::float32> var_85;
        wp::vec_t<3, wp::float64> var_86;
        wp::float64 var_87;
        wp::vec_t<3, wp::float64> var_88;
        wp::float64* var_89;
        wp::int32* var_90;
        wp::vec_t<3, wp::float32>* var_91;
        wp::int32 var_92;
        wp::vec_t<3, wp::float64> var_93;
        wp::vec_t<3, wp::float32> var_94;
        wp::vec_t<3, wp::float64> var_95;
        wp::float64 var_96;
        wp::vec_t<3, wp::float64> var_97;
        wp::mat_t<3, 3, wp::float64> var_98;
        wp::vec_t<3, wp::float64> var_99;
        wp::vec_t<3, wp::float64> var_100;
        const wp::int32 var_101 = 0;
        wp::float64 var_102;
        wp::float64 var_103;
        wp::float64 var_104;
        const wp::int32 var_105 = 1;
        wp::float64 var_106;
        wp::float64 var_107;
        wp::float64 var_108;
        const wp::int32 var_109 = 2;
        wp::float64 var_110;
        wp::float64 var_111;
        wp::float64 var_112;
        const wp::int32 var_113 = 3;
        wp::int32 var_114;
        wp::int32 var_115;
        const wp::float32 var_116 = 0.0;
        wp::vec_t<3, wp::float32> var_117;
        const wp::float32 var_118 = 0.0;
        const wp::float32 var_119 = 0.0;
        const wp::float32 var_120 = 0.0;
        const wp::float32 var_121 = 0.0;
        wp::vec_t<3, wp::float32> var_122;
        const wp::int32 var_123 = 1;
        const wp::int32 var_124 = 3;
        wp::int32 var_125;
        wp::int32 var_126;
        wp::vec_t<3, wp::float64>* var_127;
        wp::vec_t<3, wp::float64> var_128;
        wp::vec_t<3, wp::float64> var_129;
        wp::float64 var_130;
        wp::vec_t<3, wp::float64> var_131;
        wp::int32* var_132;
        const wp::int32 var_133 = 1;
        wp::int32 var_134;
        wp::int32* var_135;
        wp::range_t var_136;
        wp::int32 var_137;
        wp::int32 var_138;
        wp::int32 var_139;
        wp::float64* var_140;
        wp::int32* var_141;
        wp::vec_t<3, wp::float32>* var_142;
        wp::int32 var_143;
        wp::vec_t<3, wp::float64> var_144;
        wp::vec_t<3, wp::float32> var_145;
        wp::vec_t<3, wp::float64> var_146;
        wp::float64 var_147;
        wp::vec_t<3, wp::float64> var_148;
        wp::float64* var_149;
        wp::int32* var_150;
        wp::vec_t<3, wp::float32>* var_151;
        wp::int32 var_152;
        wp::vec_t<3, wp::float64> var_153;
        wp::vec_t<3, wp::float32> var_154;
        wp::vec_t<3, wp::float64> var_155;
        wp::float64 var_156;
        wp::vec_t<3, wp::float64> var_157;
        wp::mat_t<3, 3, wp::float64> var_158;
        wp::vec_t<3, wp::float64> var_159;
        wp::vec_t<3, wp::float64> var_160;
        const wp::int32 var_161 = 0;
        wp::float64 var_162;
        wp::float64 var_163;
        wp::float64 var_164;
        const wp::int32 var_165 = 1;
        wp::float64 var_166;
        wp::float64 var_167;
        wp::float64 var_168;
        const wp::int32 var_169 = 2;
        wp::float64 var_170;
        wp::float64 var_171;
        wp::float64 var_172;
        const wp::int32 var_173 = 3;
        wp::int32 var_174;
        wp::int32 var_175;
        const wp::float32 var_176 = 0.0;
        wp::vec_t<3, wp::float32> var_177;
        const wp::float32 var_178 = 0.0;
        const wp::float32 var_179 = 0.0;
        const wp::float32 var_180 = 0.0;
        const wp::float32 var_181 = 0.0;
        wp::vec_t<3, wp::float32> var_182;
        const wp::int32 var_183 = 2;
        const wp::int32 var_184 = 3;
        wp::int32 var_185;
        wp::int32 var_186;
        wp::vec_t<3, wp::float64>* var_187;
        wp::vec_t<3, wp::float64> var_188;
        wp::vec_t<3, wp::float64> var_189;
        wp::float64 var_190;
        wp::vec_t<3, wp::float64> var_191;
        wp::int32* var_192;
        const wp::int32 var_193 = 1;
        wp::int32 var_194;
        wp::int32* var_195;
        wp::range_t var_196;
        wp::int32 var_197;
        wp::int32 var_198;
        wp::int32 var_199;
        wp::float64* var_200;
        wp::int32* var_201;
        wp::vec_t<3, wp::float32>* var_202;
        wp::int32 var_203;
        wp::vec_t<3, wp::float64> var_204;
        wp::vec_t<3, wp::float32> var_205;
        wp::vec_t<3, wp::float64> var_206;
        wp::float64 var_207;
        wp::vec_t<3, wp::float64> var_208;
        wp::float64* var_209;
        wp::int32* var_210;
        wp::vec_t<3, wp::float32>* var_211;
        wp::int32 var_212;
        wp::vec_t<3, wp::float64> var_213;
        wp::vec_t<3, wp::float32> var_214;
        wp::vec_t<3, wp::float64> var_215;
        wp::float64 var_216;
        wp::vec_t<3, wp::float64> var_217;
        wp::mat_t<3, 3, wp::float64> var_218;
        wp::vec_t<3, wp::float64> var_219;
        wp::vec_t<3, wp::float64> var_220;
        const wp::int32 var_221 = 0;
        wp::float64 var_222;
        wp::float64 var_223;
        wp::float64 var_224;
        const wp::int32 var_225 = 1;
        wp::float64 var_226;
        wp::float64 var_227;
        wp::float64 var_228;
        const wp::int32 var_229 = 2;
        wp::float64 var_230;
        wp::float64 var_231;
        wp::float64 var_232;
        const wp::int32 var_233 = 3;
        wp::int32 var_234;
        wp::int32 var_235;
        const wp::float32 var_236 = 0.0;
        wp::vec_t<3, wp::float32> var_237;
        const wp::float32 var_238 = 0.0;
        const wp::float32 var_239 = 0.0;
        const wp::float32 var_240 = 0.0;
        const wp::float32 var_241 = 0.0;
        wp::vec_t<3, wp::float32> var_242;
        const wp::int32 var_243 = 0;
        const wp::int32 var_244 = 0;
        const bool var_245 = true;
        const wp::int32 var_246 = 0;
        const wp::int32 var_247 = 0;
        wp::float64 var_248;
        const wp::int32 var_249 = 1;
        wp::float64 var_250;
        const wp::int32 var_251 = 2;
        wp::float64 var_252;
        wp::float64 var_253;
        wp::float64 var_254;
        const wp::int32 var_255 = 0;
        wp::float64 var_256;
        const wp::int32 var_257 = 1;
        wp::float64 var_258;
        const wp::int32 var_259 = 2;
        wp::float64 var_260;
        wp::float64 var_261;
        wp::float64 var_262;
        bool var_263;
        const wp::int32 var_264 = 0;
        wp::vec_t<3, wp::float64>* var_265;
        wp::float64 var_266;
        wp::vec_t<3, wp::float64> var_267;
        bool var_268;
        const wp::int32 var_269 = 1;
        wp::vec_t<3, wp::float64>* var_270;
        wp::float64 var_271;
        wp::vec_t<3, wp::float64> var_272;
        bool var_273;
        const bool var_274 = false;
        bool var_275;
        const wp::int32 var_276 = 1;
        const wp::int32 var_277 = 0;
        wp::float64 var_278;
        const wp::int32 var_279 = 1;
        wp::float64 var_280;
        const wp::int32 var_281 = 2;
        wp::float64 var_282;
        wp::float64 var_283;
        wp::float64 var_284;
        const wp::int32 var_285 = 0;
        wp::float64 var_286;
        const wp::int32 var_287 = 1;
        wp::float64 var_288;
        const wp::int32 var_289 = 2;
        wp::float64 var_290;
        wp::float64 var_291;
        wp::float64 var_292;
        bool var_293;
        const wp::int32 var_294 = 0;
        wp::vec_t<3, wp::float64>* var_295;
        wp::float64 var_296;
        wp::vec_t<3, wp::float64> var_297;
        bool var_298;
        const wp::int32 var_299 = 1;
        wp::vec_t<3, wp::float64>* var_300;
        wp::float64 var_301;
        wp::vec_t<3, wp::float64> var_302;
        bool var_303;
        const bool var_304 = false;
        bool var_305;
        const wp::int32 var_306 = 2;
        const wp::int32 var_307 = 0;
        wp::float64 var_308;
        const wp::int32 var_309 = 1;
        wp::float64 var_310;
        const wp::int32 var_311 = 2;
        wp::float64 var_312;
        wp::float64 var_313;
        wp::float64 var_314;
        const wp::int32 var_315 = 0;
        wp::float64 var_316;
        const wp::int32 var_317 = 1;
        wp::float64 var_318;
        const wp::int32 var_319 = 2;
        wp::float64 var_320;
        wp::float64 var_321;
        wp::float64 var_322;
        bool var_323;
        const wp::int32 var_324 = 0;
        wp::vec_t<3, wp::float64>* var_325;
        wp::float64 var_326;
        wp::vec_t<3, wp::float64> var_327;
        bool var_328;
        const wp::int32 var_329 = 1;
        wp::vec_t<3, wp::float64>* var_330;
        wp::float64 var_331;
        wp::vec_t<3, wp::float64> var_332;
        bool var_333;
        const bool var_334 = false;
        bool var_335;
        bool var_336;
        wp::int32* var_337;
        const wp::int32 var_338 = 3;
        bool var_339;
        wp::int32 var_340;
        const wp::int32 var_341 = 0;
        wp::int32* var_342;
        const wp::int32 var_343 = 0;
        bool var_344;
        wp::int32 var_345;
        wp::int32* var_346;
        wp::int32 var_347;
        wp::int32 var_348;
        wp::int32* var_349;
        wp::int32 var_350;
        wp::int32 var_351;
        bool var_352;
        const wp::int32 var_353 = 3;
        bool var_354;
        const wp::int32 var_355 = 0;
        wp::int32* var_356;
        const wp::int32 var_357 = 0;
        bool var_358;
        wp::int32 var_359;
        wp::float64 var_360;
        wp::mat_t<3, 3, wp::float64> var_361;
        wp::float64 var_362;
        wp::float64 var_363;
        wp::float64 var_364;
        wp::float64 var_365;
        wp::vec_t<3, wp::float64> var_366;
        wp::float64 var_367;
        const wp::int32 var_368 = 0;
        wp::int32 var_369;
        const wp::int32 var_370 = 0;
        wp::int32 var_371;
        const wp::int32 var_372 = 1;
        wp::int32 var_373;
        const wp::int32 var_374 = 1;
        wp::range_t var_375;
        wp::int32 var_376;
        const wp::int32 var_377 = 0;
        wp::vec_t<3, wp::float64>* var_378;
        wp::vec_t<3, wp::float64>* var_379;
        const wp::int32 var_380 = 1;
        wp::int32 var_381;
        wp::vec_t<3, wp::float64>* var_382;
        wp::mat_t<3, 3, wp::float64> var_383;
        wp::vec_t<3, wp::float64> var_384;
        wp::vec_t<3, wp::float64> var_385;
        wp::vec_t<3, wp::float64> var_386;
        wp::float64* var_387;
        Value_53a65c4a var_388;
        wp::float64 var_389;
        const wp::int32 var_390 = 0;
        const wp::int32 var_391 = 1;
        wp::int32 var_392;
        wp::mat_t<3, 3, wp::float64>* var_393;
        wp::mat_t<3, 3, wp::float64> var_394;
        wp::mat_t<3, 3, wp::float64> var_395;
        wp::float64* var_396;
        wp::float64 var_397;
        wp::float64 var_398;
        wp::float64* var_399;
        wp::float64 var_400;
        wp::float64 var_401;
        wp::float64* var_402;
        wp::float64 var_403;
        wp::float64 var_404;
        wp::vec_t<3, wp::float64>* var_405;
        wp::vec_t<3, wp::float64> var_406;
        wp::vec_t<3, wp::float64> var_407;
        wp::float64* var_408;
        wp::float64 var_409;
        wp::float64 var_410;
        wp::int32* var_411;
        wp::int32 var_412;
        wp::int32 var_413;
        const wp::int32 var_414 = 0;
        wp::int32* var_415;
        wp::float64 var_416;
        wp::int32 var_417;
        wp::float64 var_418;
        wp::float64 var_419;
        const wp::int32 var_420 = 0;
        wp::vec_t<3, wp::float64> var_421;
        wp::float64 var_422;
        wp::float64 var_423;
        const wp::int32 var_424 = 1;
        wp::vec_t<3, wp::float64> var_425;
        wp::float64 var_426;
        wp::float64 var_427;
        const wp::int32 var_428 = 2;
        wp::vec_t<3, wp::float64> var_429;
        wp::float64 var_430;
        wp::float64 var_431;
        wp::int32 var_432;
        wp::int32 var_433;
        bool var_434;
        wp::float64 var_435;
        wp::float64 var_436;
        bool var_437;
        const wp::int32 var_438 = 0;
        wp::int32* var_439;
        const wp::int32 var_440 = 0;
        bool var_441;
        wp::int32 var_442;
        bool var_443;
        const wp::int32 var_444 = 0;
        const wp::int32 var_445 = 5;
        wp::int32 var_446;
        const wp::int32 var_447 = 0;
        bool var_448;
        wp::float64 var_449;
        const wp::int32 var_450 = 0;
        const wp::int32 var_451 = 1;
        const wp::int32 var_452 = 2;
        const wp::int32 var_453 = 3;
        wp::float64 var_454;
        const wp::int32 var_455 = 4;
        wp::float64 var_456;
        wp::range_t var_457;
        wp::int32 var_458;
        Value_53a65c4a* var_459;
        wp::float64* var_460;
        wp::float64 var_461;
        wp::float64 var_462;
        const wp::int32 var_463 = 5;
        wp::int32 var_464;
        const wp::int32 var_465 = 0;
        wp::int32 var_466;
        wp::float64 var_467;
        wp::range_t var_468;
        wp::int32 var_469;
        Value_53a65c4a* var_470;
        wp::float64* var_471;
        bool var_472;
        wp::float64 var_473;
        wp::int32 var_474;
        Value_53a65c4a* var_475;
        wp::float64* var_476;
        wp::float64 var_477;
        wp::float64 var_478;
        wp::int32 var_479;
        wp::float64 var_480;
        wp::int32* var_481;
        wp::int32 var_482;
        wp::int32 var_483;
        bool var_484;
        const wp::int32 var_485 = 0;
        const wp::int32 var_486 = 7;
        wp::int32 var_487;
        wp::int32 var_488;
        wp::mat_t<3, 3, wp::float64>* var_489;
        wp::mat_t<3, 3, wp::float64> var_490;
        wp::mat_t<3, 3, wp::float64> var_491;
        Value_53a65c4a* var_492;
        Value_53a65c4a var_493;
        Value_53a65c4a var_494;
        wp::mat_t<3, 3, wp::float64> var_495;
        wp::mat_t<3, 3, wp::float64> var_496;
        wp::float64* var_497;
        Value_53a65c4a var_498;
        wp::float64 var_499;
        wp::float64* var_500;
        Value_53a65c4a var_501;
        wp::float64 var_502;
        wp::mat_t<3, 3, wp::float64>* var_503;
        wp::mat_t<3, 3, wp::float64>* var_504;
        wp::mat_t<3, 3, wp::float64> var_505;
        wp::mat_t<3, 3, wp::float64> var_506;
        wp::mat_t<3, 3, wp::float64> var_507;
        wp::mat_t<3, 3, wp::float64>* var_508;
        wp::mat_t<3, 3, wp::float64> var_509;
        wp::mat_t<3, 3, wp::float64> var_510;
        wp::mat_t<3, 3, wp::float64> var_511;
        wp::float64* var_512;
        wp::float64* var_513;
        wp::float64 var_514;
        wp::float64 var_515;
        wp::float64 var_516;
        wp::float64* var_517;
        wp::float64 var_518;
        wp::float64 var_519;
        wp::float64 var_520;
        wp::float64* var_521;
        wp::float64* var_522;
        wp::float64 var_523;
        wp::float64 var_524;
        wp::float64 var_525;
        wp::float64* var_526;
        wp::float64 var_527;
        wp::float64 var_528;
        wp::float64 var_529;
        wp::float64* var_530;
        wp::float64* var_531;
        wp::float64 var_532;
        wp::float64 var_533;
        wp::float64 var_534;
        wp::float64* var_535;
        wp::float64 var_536;
        wp::float64 var_537;
        wp::float64 var_538;
        wp::vec_t<3, wp::float64>* var_539;
        wp::vec_t<3, wp::float64>* var_540;
        wp::vec_t<3, wp::float64> var_541;
        wp::vec_t<3, wp::float64> var_542;
        wp::vec_t<3, wp::float64> var_543;
        wp::vec_t<3, wp::float64>* var_544;
        wp::vec_t<3, wp::float64> var_545;
        wp::vec_t<3, wp::float64> var_546;
        wp::vec_t<3, wp::float64> var_547;
        wp::float64* var_548;
        wp::float64* var_549;
        wp::float64 var_550;
        wp::float64 var_551;
        wp::float64 var_552;
        wp::float64* var_553;
        wp::float64 var_554;
        wp::float64 var_555;
        wp::float64 var_556;
        wp::int32* var_557;
        wp::int32* var_558;
        wp::int32 var_559;
        wp::int32 var_560;
        wp::int32 var_561;
        wp::int32 var_562;
        const wp::int32 var_563 = 1;
        wp::int32 var_564;
        const wp::int32 var_565 = 1;
        wp::int32 var_566;
        const wp::int32 var_567 = 1;
        wp::int32 var_568;
        wp::float64 var_569;
        const wp::int32 var_570 = 0;
        wp::vec_t<3, wp::float64> var_571;
        wp::float64 var_572;
        wp::float64 var_573;
        const wp::int32 var_574 = 1;
        wp::vec_t<3, wp::float64> var_575;
        wp::float64 var_576;
        wp::float64 var_577;
        const wp::int32 var_578 = 2;
        wp::vec_t<3, wp::float64> var_579;
        wp::float64 var_580;
        wp::float64 var_581;
        const wp::int32 var_582 = 0;
        wp::int32* var_583;
        const wp::int32 var_584 = 0;
        bool var_585;
        wp::int32 var_586;
        const wp::int32 var_587 = 0;
        const wp::int32 var_588 = 3;
        wp::int32 var_589;
        wp::int32 var_590;
        wp::vec_t<3, wp::float64> var_591;
        wp::vec_t<3, wp::float32> var_592;
        wp::float64 var_593;
        wp::float64 var_594;
        wp::float32 var_595;
        wp::float64 var_596;
        wp::float64 var_597;
        wp::float32 var_598;
        wp::float64 var_599;
        wp::float64 var_600;
        wp::float32 var_601;
        wp::float64 var_602;
        wp::vec_t<3, wp::float64> var_603;
        wp::vec_t<3, wp::float32> var_604;
        const wp::int32 var_605 = 1;
        const wp::int32 var_606 = 3;
        wp::int32 var_607;
        wp::int32 var_608;
        wp::vec_t<3, wp::float64> var_609;
        wp::vec_t<3, wp::float32> var_610;
        wp::float64 var_611;
        wp::float64 var_612;
        wp::float32 var_613;
        wp::float64 var_614;
        wp::float64 var_615;
        wp::float32 var_616;
        wp::float64 var_617;
        wp::float64 var_618;
        wp::float32 var_619;
        wp::float64 var_620;
        wp::vec_t<3, wp::float64> var_621;
        wp::vec_t<3, wp::float32> var_622;
        const wp::int32 var_623 = 2;
        const wp::int32 var_624 = 3;
        wp::int32 var_625;
        wp::int32 var_626;
        wp::vec_t<3, wp::float64> var_627;
        wp::vec_t<3, wp::float32> var_628;
        wp::float64 var_629;
        wp::float64 var_630;
        wp::float32 var_631;
        wp::float64 var_632;
        wp::float64 var_633;
        wp::float32 var_634;
        wp::float64 var_635;
        wp::float64 var_636;
        wp::float32 var_637;
        wp::float64 var_638;
        wp::vec_t<3, wp::float64> var_639;
        wp::vec_t<3, wp::float32> var_640;
        wp::int32 var_641;
        wp::int32 var_642;
        wp::int32 var_643;
        wp::int32 var_644;
        wp::int32 var_645;
        wp::int32 var_646;
        wp::int32 var_647;
        wp::int32 var_648;
        //---------
        // forward
        // def integrate(mesh:wp.uint64,tri:wp.array2d(dtype=wp.vec3d),bbmin:wp.vec3d,bbmax:wp.vec3d,planes:wp.array2d(dtype=wp.vec4d),bounds:wp.array2d(dtype=wp.vec3d),ncells:int,R:wp.mat33d,T0:wp.vec3d,travel:wp.vec3d,load:wp.float64,hold:wp.float64,clock:wp.array(dtype=wp.float64),ptr:wp.array(dtype=int),ids:wp.array(dtype=int),w:wp.array(dtype=wp.float64),ref:wp.array(dtype=wp.vec3d),areas:wp.array(dtype=wp.float64),area_total:wp.float64,q:wp.array(dtype=wp.vec3),vel:wp.array(dtype=wp.vec3),polygon:wp.array3d(dtype=wp.vec3d),Bs:wp.array2d(dtype=wp.mat33d),vals:wp.array2d(dtype=Value),depths:wp.array2d(dtype=int),counts:wp.array(dtype=int),query_counts:wp.array(dtype=int),cf:wp.array(dtype=wp.vec3),cu:wp.array(dtype=float),cp:wp.array(dtype=float),power:wp.array(dtype=float),moment:wp.array(dtype=wp.vec3),bad:wp.array(dtype=int),failure:wp.array(dtype=wp.float64),cap:int,relative_tol:wp.float64,absolute_tol:wp.float64,maxdepth:int,polycounts:wp.array(dtype=int),polysources:wp.array(dtype=int),active_count:wp.array(dtype=int)):       <L 130>
        // pair=wp.tid();face=pair//ncells;cell=pair%ncells;X=wp.mat33d(wp.float64(0.));V=wp.mat33d(wp.float64(0.));local=wp.mat33d(wp.float64(0.));t=clock[0];shape=wp.float64(0.);speed=wp.float64(0.);pi=wp.float64(3.141592653589793)       <L 131>
        var_0 = builtin_tid1d();
        var_1 = wp::floordiv(var_0, var_ncells);
        var_2 = wp::mod(var_0, var_ncells);
        var_3 = 0.0;
        var_4 = wp::mat_t<3, 3, wp::float64>(var_3);
        var_5 = 0.0;
        var_6 = wp::mat_t<3, 3, wp::float64>(var_5);
        var_7 = 0.0;
        var_8 = wp::mat_t<3, 3, wp::float64>(var_7);
        var_10 = wp::address(var_clock, var_9);
        var_12 = wp::load(var_10);
        var_11 = wp::copy(var_12);
        var_13 = 0.0;
        var_14 = 0.0;
        var_15 = 3.141592653589793;
        // if t<load:shape=wp.float64(.5)*(wp.float64(1.)-wp.cos(pi*t/load));speed=wp.float64(.5)*pi/load*wp.sin(pi*t/load)       <L 132>
        var_16 = (var_11 < var_load);
        if (var_16) {
            var_17 = 0.5;
            var_18 = 1.0;
            var_19 = wp::mul(var_15, var_11);
            var_20 = wp::div(var_19, var_load);
            var_21 = wp::cos(var_20);
            var_22 = wp::sub(var_18, var_21);
            var_23 = wp::mul(var_17, var_22);
            var_24 = 0.5;
            var_25 = wp::mul(var_24, var_15);
            var_26 = wp::div(var_25, var_load);
            var_27 = wp::mul(var_15, var_11);
            var_28 = wp::div(var_27, var_load);
            var_29 = wp::sin(var_28);
            var_30 = wp::mul(var_26, var_29);
        }
        if (!var_16) {
            // elif t<load+hold:shape=wp.float64(1.)                                              <L 133>
            var_31 = wp::add(var_load, var_hold);
            var_32 = (var_11 < var_31);
            if (var_32) {
                var_33 = 1.0;
            }
            if (!var_32) {
                // elif t<wp.float64(2.)*load+hold:                                               <L 134>
                var_34 = 2.0;
                var_35 = wp::mul(var_34, var_load);
                var_36 = wp::add(var_35, var_hold);
                var_37 = (var_11 < var_36);
                if (var_37) {
                    // z=(t-load-hold)/load;shape=wp.float64(.5)*(wp.float64(1.)+wp.cos(pi*z));speed=-wp.float64(.5)*pi/load*wp.sin(pi*z)       <L 135>
                    var_38 = wp::sub(var_11, var_load);
                    var_39 = wp::sub(var_38, var_hold);
                    var_40 = wp::div(var_39, var_load);
                    var_41 = 0.5;
                    var_42 = 1.0;
                    var_43 = wp::mul(var_15, var_40);
                    var_44 = wp::cos(var_43);
                    var_45 = wp::add(var_42, var_44);
                    var_46 = wp::mul(var_41, var_45);
                    var_47 = 0.5;
                    var_48 = wp::neg(var_47);
                    var_49 = wp::mul(var_48, var_15);
                    var_50 = wp::div(var_49, var_load);
                    var_51 = wp::mul(var_15, var_40);
                    var_52 = wp::sin(var_51);
                    var_53 = wp::mul(var_50, var_52);
                }
                var_54 = wp::where(var_37, var_46, var_13);
                var_55 = wp::where(var_37, var_53, var_14);
            }
            var_56 = wp::where(var_32, var_33, var_54);
            var_57 = wp::where(var_32, var_14, var_55);
        }
        var_58 = wp::where(var_16, var_23, var_56);
        var_59 = wp::where(var_16, var_30, var_57);
        // T=T0+travel*shape;tv=travel*speed                                                      <L 136>
        var_60 = wp::mul(var_travel, var_58);
        var_61 = wp::add(var_T0, var_60);
        var_62 = wp::mul(var_travel, var_59);
        // for vertex in range(3):                                                                <L 137>
        // k=3*face+vertex;x=ref[k];v=wp.vec3d(wp.float64(0.))                                    <L 138>
        var_65 = wp::mul(var_64, var_1);
        var_66 = wp::add(var_65, var_63);
        var_67 = wp::address(var_ref, var_66);
        var_69 = wp::load(var_67);
        var_68 = wp::copy(var_69);
        var_70 = 0.0;
        var_71 = wp::vec_t<3, wp::float64>(var_70);
        // for j in range(ptr[k],ptr[k+1]):x+=w[j]*wp.vec3d(q[ids[j]]);v+=w[j]*wp.vec3d(vel[ids[j]])       <L 139>
        var_72 = wp::address(var_ptr, var_66);
        var_74 = wp::add(var_66, var_73);
        var_75 = wp::address(var_ptr, var_74);
        var_77 = wp::load(var_72);
        var_78 = wp::load(var_75);
        var_76 = wp::range(var_77, var_78);
        start_for_0:;
            if (iter_cmp(var_76) == 0) goto end_for_0;
            var_79 = wp::iter_next(var_76);
            var_80 = wp::address(var_w, var_79);
            var_81 = wp::address(var_ids, var_79);
            var_83 = wp::load(var_81);
            var_82 = wp::address(var_q, var_83);
            var_85 = wp::load(var_82);
            var_84 = wp::vec_t<3, wp::float64>(var_85);
            var_87 = wp::load(var_80);
            var_86 = wp::mul(var_87, var_84);
            var_88 = wp::add(var_68, var_86);
            var_89 = wp::address(var_w, var_79);
            var_90 = wp::address(var_ids, var_79);
            var_92 = wp::load(var_90);
            var_91 = wp::address(var_vel, var_92);
            var_94 = wp::load(var_91);
            var_93 = wp::vec_t<3, wp::float64>(var_94);
            var_96 = wp::load(var_89);
            var_95 = wp::mul(var_96, var_93);
            var_97 = wp::add(var_71, var_95);
            wp::assign(var_68, var_88);
            wp::assign(var_71, var_97);
            goto start_for_0;
        end_for_0:;
        // xp=wp.transpose(R)*(x-T)                                                               <L 140>
        var_98 = wp::transpose(var_R);
        var_99 = wp::sub(var_68, var_61);
        var_100 = wp::mul(var_98, var_99);
        // for j in range(3):X[vertex,j]=x[j];V[vertex,j]=v[j];local[vertex,j]=xp[j]              <L 141>
        var_102 = wp::extract(var_68, var_101);
        wp::assign_inplace(var_4, var_63, var_101, var_102);
        var_103 = wp::extract(var_71, var_101);
        wp::assign_inplace(var_6, var_63, var_101, var_103);
        var_104 = wp::extract(var_100, var_101);
        wp::assign_inplace(var_8, var_63, var_101, var_104);
        var_106 = wp::extract(var_68, var_105);
        wp::assign_inplace(var_4, var_63, var_105, var_106);
        var_107 = wp::extract(var_71, var_105);
        wp::assign_inplace(var_6, var_63, var_105, var_107);
        var_108 = wp::extract(var_100, var_105);
        wp::assign_inplace(var_8, var_63, var_105, var_108);
        var_110 = wp::extract(var_68, var_109);
        wp::assign_inplace(var_4, var_63, var_109, var_110);
        var_111 = wp::extract(var_71, var_109);
        wp::assign_inplace(var_6, var_63, var_109, var_111);
        var_112 = wp::extract(var_100, var_109);
        wp::assign_inplace(var_8, var_63, var_109, var_112);
        // out=3*pair+vertex;cf[out]=wp.vec3(0.);cu[out]=0.;cp[out]=0.;power[out]=0.;moment[out]=wp.vec3(0.)       <L 142>
        var_114 = wp::mul(var_113, var_0);
        var_115 = wp::add(var_114, var_63);
        var_117 = wp::vec_t<3, wp::float32>(var_116);
        wp::array_store(var_cf, var_115, var_117);
        wp::array_store(var_cu, var_115, var_118);
        wp::array_store(var_cp, var_115, var_119);
        wp::array_store(var_power, var_115, var_120);
        var_122 = wp::vec_t<3, wp::float32>(var_121);
        wp::array_store(var_moment, var_115, var_122);
        // k=3*face+vertex;x=ref[k];v=wp.vec3d(wp.float64(0.))                                    <L 138>
        var_125 = wp::mul(var_124, var_1);
        var_126 = wp::add(var_125, var_123);
        var_127 = wp::address(var_ref, var_126);
        var_129 = wp::load(var_127);
        var_128 = wp::copy(var_129);
        var_130 = 0.0;
        var_131 = wp::vec_t<3, wp::float64>(var_130);
        // for j in range(ptr[k],ptr[k+1]):x+=w[j]*wp.vec3d(q[ids[j]]);v+=w[j]*wp.vec3d(vel[ids[j]])       <L 139>
        var_132 = wp::address(var_ptr, var_126);
        var_134 = wp::add(var_126, var_133);
        var_135 = wp::address(var_ptr, var_134);
        var_137 = wp::load(var_132);
        var_138 = wp::load(var_135);
        var_136 = wp::range(var_137, var_138);
        start_for_2:;
            if (iter_cmp(var_136) == 0) goto end_for_2;
            var_139 = wp::iter_next(var_136);
            var_140 = wp::address(var_w, var_139);
            var_141 = wp::address(var_ids, var_139);
            var_143 = wp::load(var_141);
            var_142 = wp::address(var_q, var_143);
            var_145 = wp::load(var_142);
            var_144 = wp::vec_t<3, wp::float64>(var_145);
            var_147 = wp::load(var_140);
            var_146 = wp::mul(var_147, var_144);
            var_148 = wp::add(var_128, var_146);
            var_149 = wp::address(var_w, var_139);
            var_150 = wp::address(var_ids, var_139);
            var_152 = wp::load(var_150);
            var_151 = wp::address(var_vel, var_152);
            var_154 = wp::load(var_151);
            var_153 = wp::vec_t<3, wp::float64>(var_154);
            var_156 = wp::load(var_149);
            var_155 = wp::mul(var_156, var_153);
            var_157 = wp::add(var_131, var_155);
            wp::assign(var_128, var_148);
            wp::assign(var_131, var_157);
            goto start_for_2;
        end_for_2:;
        // xp=wp.transpose(R)*(x-T)                                                               <L 140>
        var_158 = wp::transpose(var_R);
        var_159 = wp::sub(var_128, var_61);
        var_160 = wp::mul(var_158, var_159);
        // for j in range(3):X[vertex,j]=x[j];V[vertex,j]=v[j];local[vertex,j]=xp[j]              <L 141>
        var_162 = wp::extract(var_128, var_161);
        wp::assign_inplace(var_4, var_123, var_161, var_162);
        var_163 = wp::extract(var_131, var_161);
        wp::assign_inplace(var_6, var_123, var_161, var_163);
        var_164 = wp::extract(var_160, var_161);
        wp::assign_inplace(var_8, var_123, var_161, var_164);
        var_166 = wp::extract(var_128, var_165);
        wp::assign_inplace(var_4, var_123, var_165, var_166);
        var_167 = wp::extract(var_131, var_165);
        wp::assign_inplace(var_6, var_123, var_165, var_167);
        var_168 = wp::extract(var_160, var_165);
        wp::assign_inplace(var_8, var_123, var_165, var_168);
        var_170 = wp::extract(var_128, var_169);
        wp::assign_inplace(var_4, var_123, var_169, var_170);
        var_171 = wp::extract(var_131, var_169);
        wp::assign_inplace(var_6, var_123, var_169, var_171);
        var_172 = wp::extract(var_160, var_169);
        wp::assign_inplace(var_8, var_123, var_169, var_172);
        // out=3*pair+vertex;cf[out]=wp.vec3(0.);cu[out]=0.;cp[out]=0.;power[out]=0.;moment[out]=wp.vec3(0.)       <L 142>
        var_174 = wp::mul(var_173, var_0);
        var_175 = wp::add(var_174, var_123);
        var_177 = wp::vec_t<3, wp::float32>(var_176);
        wp::array_store(var_cf, var_175, var_177);
        wp::array_store(var_cu, var_175, var_178);
        wp::array_store(var_cp, var_175, var_179);
        wp::array_store(var_power, var_175, var_180);
        var_182 = wp::vec_t<3, wp::float32>(var_181);
        wp::array_store(var_moment, var_175, var_182);
        // k=3*face+vertex;x=ref[k];v=wp.vec3d(wp.float64(0.))                                    <L 138>
        var_185 = wp::mul(var_184, var_1);
        var_186 = wp::add(var_185, var_183);
        var_187 = wp::address(var_ref, var_186);
        var_189 = wp::load(var_187);
        var_188 = wp::copy(var_189);
        var_190 = 0.0;
        var_191 = wp::vec_t<3, wp::float64>(var_190);
        // for j in range(ptr[k],ptr[k+1]):x+=w[j]*wp.vec3d(q[ids[j]]);v+=w[j]*wp.vec3d(vel[ids[j]])       <L 139>
        var_192 = wp::address(var_ptr, var_186);
        var_194 = wp::add(var_186, var_193);
        var_195 = wp::address(var_ptr, var_194);
        var_197 = wp::load(var_192);
        var_198 = wp::load(var_195);
        var_196 = wp::range(var_197, var_198);
        start_for_4:;
            if (iter_cmp(var_196) == 0) goto end_for_4;
            var_199 = wp::iter_next(var_196);
            var_200 = wp::address(var_w, var_199);
            var_201 = wp::address(var_ids, var_199);
            var_203 = wp::load(var_201);
            var_202 = wp::address(var_q, var_203);
            var_205 = wp::load(var_202);
            var_204 = wp::vec_t<3, wp::float64>(var_205);
            var_207 = wp::load(var_200);
            var_206 = wp::mul(var_207, var_204);
            var_208 = wp::add(var_188, var_206);
            var_209 = wp::address(var_w, var_199);
            var_210 = wp::address(var_ids, var_199);
            var_212 = wp::load(var_210);
            var_211 = wp::address(var_vel, var_212);
            var_214 = wp::load(var_211);
            var_213 = wp::vec_t<3, wp::float64>(var_214);
            var_216 = wp::load(var_209);
            var_215 = wp::mul(var_216, var_213);
            var_217 = wp::add(var_191, var_215);
            wp::assign(var_188, var_208);
            wp::assign(var_191, var_217);
            goto start_for_4;
        end_for_4:;
        // xp=wp.transpose(R)*(x-T)                                                               <L 140>
        var_218 = wp::transpose(var_R);
        var_219 = wp::sub(var_188, var_61);
        var_220 = wp::mul(var_218, var_219);
        // for j in range(3):X[vertex,j]=x[j];V[vertex,j]=v[j];local[vertex,j]=xp[j]              <L 141>
        var_222 = wp::extract(var_188, var_221);
        wp::assign_inplace(var_4, var_183, var_221, var_222);
        var_223 = wp::extract(var_191, var_221);
        wp::assign_inplace(var_6, var_183, var_221, var_223);
        var_224 = wp::extract(var_220, var_221);
        wp::assign_inplace(var_8, var_183, var_221, var_224);
        var_226 = wp::extract(var_188, var_225);
        wp::assign_inplace(var_4, var_183, var_225, var_226);
        var_227 = wp::extract(var_191, var_225);
        wp::assign_inplace(var_6, var_183, var_225, var_227);
        var_228 = wp::extract(var_220, var_225);
        wp::assign_inplace(var_8, var_183, var_225, var_228);
        var_230 = wp::extract(var_188, var_229);
        wp::assign_inplace(var_4, var_183, var_229, var_230);
        var_231 = wp::extract(var_191, var_229);
        wp::assign_inplace(var_6, var_183, var_229, var_231);
        var_232 = wp::extract(var_220, var_229);
        wp::assign_inplace(var_8, var_183, var_229, var_232);
        // out=3*pair+vertex;cf[out]=wp.vec3(0.);cu[out]=0.;cp[out]=0.;power[out]=0.;moment[out]=wp.vec3(0.)       <L 142>
        var_234 = wp::mul(var_233, var_0);
        var_235 = wp::add(var_234, var_183);
        var_237 = wp::vec_t<3, wp::float32>(var_236);
        wp::array_store(var_cf, var_235, var_237);
        wp::array_store(var_cu, var_235, var_238);
        wp::array_store(var_cp, var_235, var_239);
        wp::array_store(var_power, var_235, var_240);
        var_242 = wp::vec_t<3, wp::float32>(var_241);
        wp::array_store(var_moment, var_235, var_242);
        // counts[pair]=0;query_counts[pair]=0                                                    <L 143>
        wp::array_store(var_counts, var_0, var_243);
        wp::array_store(var_query_counts, var_0, var_244);
        // intersects=True                                                                        <L 144>
        // for axis in range(3):                                                                  <L 145>
        // lo=wp.min(local[0,axis],wp.min(local[1,axis],local[2,axis]));hi=wp.max(local[0,axis],wp.max(local[1,axis],local[2,axis]))       <L 146>
        var_248 = wp::extract(var_8, var_247, var_246);
        var_250 = wp::extract(var_8, var_249, var_246);
        var_252 = wp::extract(var_8, var_251, var_246);
        var_253 = wp::min(var_250, var_252);
        var_254 = wp::min(var_248, var_253);
        var_256 = wp::extract(var_8, var_255, var_246);
        var_258 = wp::extract(var_8, var_257, var_246);
        var_260 = wp::extract(var_8, var_259, var_246);
        var_261 = wp::max(var_258, var_260);
        var_262 = wp::max(var_256, var_261);
        // if hi<bounds[cell,0][axis] or lo>bounds[cell,1][axis]:intersects=False                 <L 147>
        var_265 = wp::address(var_bounds, var_2, var_264);
        var_267 = wp::load(var_265);
        var_266 = wp::extract(var_267, var_246);
        var_268 = (var_262 < var_266);
        var_263 = var_268;
        if (!var_263) {
            var_270 = wp::address(var_bounds, var_2, var_269);
            var_272 = wp::load(var_270);
            var_271 = wp::extract(var_272, var_246);
            var_273 = (var_254 > var_271);
            var_263 = var_263 || var_273;
        }
        if (var_263) {
        }
        var_275 = wp::where(var_263, var_274, var_245);
        // lo=wp.min(local[0,axis],wp.min(local[1,axis],local[2,axis]));hi=wp.max(local[0,axis],wp.max(local[1,axis],local[2,axis]))       <L 146>
        var_278 = wp::extract(var_8, var_277, var_276);
        var_280 = wp::extract(var_8, var_279, var_276);
        var_282 = wp::extract(var_8, var_281, var_276);
        var_283 = wp::min(var_280, var_282);
        var_284 = wp::min(var_278, var_283);
        var_286 = wp::extract(var_8, var_285, var_276);
        var_288 = wp::extract(var_8, var_287, var_276);
        var_290 = wp::extract(var_8, var_289, var_276);
        var_291 = wp::max(var_288, var_290);
        var_292 = wp::max(var_286, var_291);
        // if hi<bounds[cell,0][axis] or lo>bounds[cell,1][axis]:intersects=False                 <L 147>
        var_295 = wp::address(var_bounds, var_2, var_294);
        var_297 = wp::load(var_295);
        var_296 = wp::extract(var_297, var_276);
        var_298 = (var_292 < var_296);
        var_293 = var_298;
        if (!var_293) {
            var_300 = wp::address(var_bounds, var_2, var_299);
            var_302 = wp::load(var_300);
            var_301 = wp::extract(var_302, var_276);
            var_303 = (var_284 > var_301);
            var_293 = var_293 || var_303;
        }
        if (var_293) {
        }
        var_305 = wp::where(var_293, var_304, var_275);
        // lo=wp.min(local[0,axis],wp.min(local[1,axis],local[2,axis]));hi=wp.max(local[0,axis],wp.max(local[1,axis],local[2,axis]))       <L 146>
        var_308 = wp::extract(var_8, var_307, var_306);
        var_310 = wp::extract(var_8, var_309, var_306);
        var_312 = wp::extract(var_8, var_311, var_306);
        var_313 = wp::min(var_310, var_312);
        var_314 = wp::min(var_308, var_313);
        var_316 = wp::extract(var_8, var_315, var_306);
        var_318 = wp::extract(var_8, var_317, var_306);
        var_320 = wp::extract(var_8, var_319, var_306);
        var_321 = wp::max(var_318, var_320);
        var_322 = wp::max(var_316, var_321);
        // if hi<bounds[cell,0][axis] or lo>bounds[cell,1][axis]:intersects=False                 <L 147>
        var_325 = wp::address(var_bounds, var_2, var_324);
        var_327 = wp::load(var_325);
        var_326 = wp::extract(var_327, var_306);
        var_328 = (var_322 < var_326);
        var_323 = var_328;
        if (!var_323) {
            var_330 = wp::address(var_bounds, var_2, var_329);
            var_332 = wp::load(var_330);
            var_331 = wp::extract(var_332, var_306);
            var_333 = (var_314 > var_331);
            var_323 = var_323 || var_333;
        }
        if (var_323) {
        }
        var_335 = wp::where(var_323, var_334, var_305);
        // if polycounts[pair]>=3 and bad[0]==0:                                                  <L 148>
        var_337 = wp::address(var_polycounts, var_0);
        var_340 = wp::load(var_337);
        var_339 = (var_340 >= var_338);
        var_336 = var_339;
        if (var_336) {
            var_342 = wp::address(var_bad, var_341);
            var_345 = wp::load(var_342);
            var_344 = (var_345 == var_343);
            var_336 = var_336 && var_344;
        }
        if (var_336) {
            // n=polycounts[pair];src=polysources[pair]                                           <L 149>
            var_346 = wp::address(var_polycounts, var_0);
            var_348 = wp::load(var_346);
            var_347 = wp::copy(var_348);
            var_349 = wp::address(var_polysources, var_0);
            var_351 = wp::load(var_349);
            var_350 = wp::copy(var_351);
            // if n>=3 and bad[0]==0:                                                             <L 150>
            var_354 = (var_347 >= var_353);
            var_352 = var_354;
            if (var_352) {
                var_356 = wp::address(var_bad, var_355);
                var_359 = wp::load(var_356);
                var_358 = (var_359 == var_357);
                var_352 = var_352 && var_358;
            }
            if (var_352) {
                // total=wp.mat33d(wp.float64(0.));U=wp.float64(0.);D=wp.float64(0.);W=wp.float64(0.);M=wp.vec3d(wp.float64(0.));err=wp.float64(0.);count=int(0);queries=int(0)       <L 151>
                var_360 = 0.0;
                var_361 = wp::mat_t<3, 3, wp::float64>(var_360);
                var_362 = 0.0;
                var_363 = 0.0;
                var_364 = 0.0;
                var_365 = 0.0;
                var_366 = wp::vec_t<3, wp::float64>(var_365);
                var_367 = 0.0;
                var_369 = wp::int(var_368);
                var_371 = wp::int(var_370);
                // for k in range(1,n-1):                                                         <L 152>
                var_373 = wp::sub(var_347, var_372);
                var_375 = wp::range(var_374, var_373);
                start_for_6:;
                    if (iter_cmp(var_375) == 0) goto end_for_6;
                    var_376 = wp::iter_next(var_375);
                    // B=wp.matrix_from_rows(polygon[pair,src,0],polygon[pair,src,k],polygon[pair,src,k+1]);r=evaluate_leaf(mesh,tri,B,X,V,areas[face],R,T,tv);Bs[pair,count]=B;vals[pair,count]=r;depths[pair,count]=0;count+=1;total+=r.f;U+=r.U;D+=r.D;W+=r.W;M+=r.moment;err+=r.error;queries+=r.queries       <L 153>
                    var_378 = wp::address(var_polygon, var_0, var_350, var_377);
                    var_379 = wp::address(var_polygon, var_0, var_350, var_376);
                    var_381 = wp::add(var_376, var_380);
                    var_382 = wp::address(var_polygon, var_0, var_350, var_381);
                    var_384 = wp::load(var_378);
                    var_385 = wp::load(var_379);
                    var_386 = wp::load(var_382);
                    var_383 = wp::matrix_from_rows<wp::float64>(var_384, var_385, var_386);
                    var_387 = wp::address(var_areas, var_1);
                    var_389 = wp::load(var_387);
                    var_388 = evaluate_leaf_0(var_mesh, var_tri, var_383, var_4, var_6, var_389, var_R, var_61, var_62);
                    wp::array_store(var_Bs, var_0, var_369, var_383);
                    wp::array_store(var_vals, var_0, var_369, var_388);
                    wp::array_store(var_depths, var_0, var_369, var_390);
                    var_392 = wp::add(var_369, var_391);
                    var_393 = &((var_388).f);
                    var_395 = wp::load(var_393);
                    var_394 = wp::add(var_361, var_395);
                    var_396 = &((var_388).U);
                    var_398 = wp::load(var_396);
                    var_397 = wp::add(var_362, var_398);
                    var_399 = &((var_388).D);
                    var_401 = wp::load(var_399);
                    var_400 = wp::add(var_363, var_401);
                    var_402 = &((var_388).W);
                    var_404 = wp::load(var_402);
                    var_403 = wp::add(var_364, var_404);
                    var_405 = &((var_388).moment);
                    var_407 = wp::load(var_405);
                    var_406 = wp::add(var_366, var_407);
                    var_408 = &((var_388).error);
                    var_410 = wp::load(var_408);
                    var_409 = wp::add(var_367, var_410);
                    var_411 = &((var_388).queries);
                    var_413 = wp::load(var_411);
                    var_412 = wp::add(var_371, var_413);
                    wp::assign(var_361, var_394);
                    wp::assign(var_362, var_397);
                    wp::assign(var_363, var_400);
                    wp::assign(var_364, var_403);
                    wp::assign(var_366, var_406);
                    wp::assign(var_367, var_409);
                    wp::assign(var_369, var_392);
                    wp::assign(var_371, var_412);
                    goto start_for_6;
                end_for_6:;
                // atol=absolute_tol/wp.float64(active_count[0]);fscale=wp.float64(0.)            <L 154>
                var_415 = wp::address(var_active_count, var_414);
                var_417 = wp::load(var_415);
                var_416 = wp::float64(var_417);
                var_418 = wp::div(var_absolute_tol, var_416);
                var_419 = 0.0;
                // for k in range(3):fscale+=wp.length(total[k])                                  <L 155>
                var_421 = wp::extract(var_361, var_420);
                var_422 = wp::length(var_421);
                var_423 = wp::add(var_419, var_422);
                var_425 = wp::extract(var_361, var_424);
                var_426 = wp::length(var_425);
                var_427 = wp::add(var_423, var_426);
                var_429 = wp::extract(var_361, var_428);
                var_430 = wp::length(var_429);
                var_431 = wp::add(var_427, var_430);
                // while err>atol+relative_tol*fscale and bad[0]==0:                              <L 156>
                var_432 = wp::copy(var_428);
                var_433 = wp::copy(var_229);
        start_while_8:;
                var_435 = wp::mul(var_relative_tol, var_431);
                var_436 = wp::add(var_418, var_435);
                var_437 = (var_367 > var_436);
                var_434 = var_437;
                if (var_434) {
                    var_439 = wp::address(var_bad, var_438);
                    var_442 = wp::load(var_439);
                    var_441 = (var_442 == var_440);
                    var_434 = var_434 && var_441;
                }
        if ((var_434) == false) goto end_while_8;
                    // if count>=cap:                                                             <L 157>
                    var_443 = (var_369 >= var_cap);
                    if (var_443) {
                        // if wp.atomic_max(bad,0,5)==0:                                          <L 158>
                        var_446 = wp::atomic_max(var_bad, var_444, var_445);
                        var_448 = (var_446 == var_447);
                        if (var_448) {
                            // failure[0]=wp.float64(pair);failure[1]=err;failure[2]=fscale;failure[3]=t;failure[4]=wp.float64(count);actual_error=wp.float64(0.)       <L 159>
                            var_449 = wp::float64(var_0);
                            wp::array_store(var_failure, var_450, var_449);
                            wp::array_store(var_failure, var_451, var_367);
                            wp::array_store(var_failure, var_452, var_431);
                            wp::array_store(var_failure, var_453, var_11);
                            var_454 = wp::float64(var_369);
                            wp::array_store(var_failure, var_455, var_454);
                            var_456 = 0.0;
                            // for j in range(count):actual_error+=vals[pair,j].error             <L 160>
                            var_457 = wp::range(var_369);
                            start_for_10:;
                                if (iter_cmp(var_457) == 0) goto end_for_10;
                                var_458 = wp::iter_next(var_457);
                                var_459 = wp::address(var_vals, var_0, var_458);
                                var_460 = &(((*wp::address(var_vals, var_0, var_458))).error);
                                var_462 = wp::load(var_460);
                                var_461 = wp::add(var_456, var_462);
                                wp::assign(var_456, var_461);
                                goto start_for_10;
                            end_for_10:;
                            // failure[5]=actual_error                                            <L 161>
                            wp::array_store(var_failure, var_463, var_456);
                        }
                        var_464 = wp::where(var_448, var_458, var_433);
                        // break                                                                  <L 162>
                        wp::assign(var_433, var_464);
                        goto end_while_8;
                    }
                    // worst=int(0);worsterr=wp.float64(-1.)                                      <L 163>
                    var_466 = wp::int(var_465);
                    var_467 = -1.0;
                    // for k in range(count):                                                     <L 164>
                    var_468 = wp::range(var_369);
                    start_for_12:;
                        if (iter_cmp(var_468) == 0) goto end_for_12;
                        var_469 = wp::iter_next(var_468);
                        // if vals[pair,k].error>worsterr:worst=k;worsterr=vals[pair,k].error       <L 165>
                        var_470 = wp::address(var_vals, var_0, var_469);
                        var_471 = &(((*wp::address(var_vals, var_0, var_469))).error);
                        var_473 = wp::load(var_471);
                        var_472 = (var_473 > var_467);
                        if (var_472) {
                            var_474 = wp::copy(var_469);
                            var_475 = wp::address(var_vals, var_0, var_469);
                            var_476 = &(((*wp::address(var_vals, var_0, var_469))).error);
                            var_478 = wp::load(var_476);
                            var_477 = wp::copy(var_478);
                        }
                        var_479 = wp::where(var_472, var_474, var_466);
                        var_480 = wp::where(var_472, var_477, var_467);
                        wp::assign(var_466, var_479);
                        wp::assign(var_467, var_480);
                        goto start_for_12;
                    end_for_12:;
                    // depth=depths[pair,worst]                                                   <L 166>
                    var_481 = wp::address(var_depths, var_0, var_466);
                    var_483 = wp::load(var_481);
                    var_482 = wp::copy(var_483);
                    // if depth>=maxdepth:wp.atomic_max(bad,0,7);break                            <L 167>
                    var_484 = (var_482 >= var_maxdepth);
                    if (var_484) {
                        var_487 = wp::atomic_max(var_bad, var_485, var_486);
                        wp::assign(var_432, var_469);
                        goto end_while_8;
                    }
                    var_488 = wp::where(var_484, var_432, var_469);
                    // B=Bs[pair,worst];old=vals[pair,worst];L,H=bisect(B,X);a=evaluate_leaf(mesh,tri,L,X,V,areas[face],R,T,tv);b=evaluate_leaf(mesh,tri,H,X,V,areas[face],R,T,tv)       <L 168>
                    var_489 = wp::address(var_Bs, var_0, var_466);
                    var_491 = wp::load(var_489);
                    var_490 = wp::copy(var_491);
                    var_492 = wp::address(var_vals, var_0, var_466);
                    var_494 = wp::load(var_492);
                    var_493 = wp::copy(var_494);
                    bisect_0(var_490, var_4, var_495, var_496);
                    var_497 = wp::address(var_areas, var_1);
                    var_499 = wp::load(var_497);
                    var_498 = evaluate_leaf_0(var_mesh, var_tri, var_495, var_4, var_6, var_499, var_R, var_61, var_62);
                    var_500 = wp::address(var_areas, var_1);
                    var_502 = wp::load(var_500);
                    var_501 = evaluate_leaf_0(var_mesh, var_tri, var_496, var_4, var_6, var_502, var_R, var_61, var_62);
                    // total+=a.f+b.f-old.f;U+=a.U+b.U-old.U;D+=a.D+b.D-old.D;W+=a.W+b.W-old.W;M+=a.moment+b.moment-old.moment;err+=a.error+b.error-old.error;queries+=a.queries+b.queries       <L 169>
                    var_503 = &((var_498).f);
                    var_504 = &((var_501).f);
                    var_506 = wp::load(var_503);
                    var_507 = wp::load(var_504);
                    var_505 = wp::add(var_506, var_507);
                    var_508 = &((var_493).f);
                    var_510 = wp::load(var_508);
                    var_509 = wp::sub(var_505, var_510);
                    var_511 = wp::add(var_361, var_509);
                    var_512 = &((var_498).U);
                    var_513 = &((var_501).U);
                    var_515 = wp::load(var_512);
                    var_516 = wp::load(var_513);
                    var_514 = wp::add(var_515, var_516);
                    var_517 = &((var_493).U);
                    var_519 = wp::load(var_517);
                    var_518 = wp::sub(var_514, var_519);
                    var_520 = wp::add(var_362, var_518);
                    var_521 = &((var_498).D);
                    var_522 = &((var_501).D);
                    var_524 = wp::load(var_521);
                    var_525 = wp::load(var_522);
                    var_523 = wp::add(var_524, var_525);
                    var_526 = &((var_493).D);
                    var_528 = wp::load(var_526);
                    var_527 = wp::sub(var_523, var_528);
                    var_529 = wp::add(var_363, var_527);
                    var_530 = &((var_498).W);
                    var_531 = &((var_501).W);
                    var_533 = wp::load(var_530);
                    var_534 = wp::load(var_531);
                    var_532 = wp::add(var_533, var_534);
                    var_535 = &((var_493).W);
                    var_537 = wp::load(var_535);
                    var_536 = wp::sub(var_532, var_537);
                    var_538 = wp::add(var_364, var_536);
                    var_539 = &((var_498).moment);
                    var_540 = &((var_501).moment);
                    var_542 = wp::load(var_539);
                    var_543 = wp::load(var_540);
                    var_541 = wp::add(var_542, var_543);
                    var_544 = &((var_493).moment);
                    var_546 = wp::load(var_544);
                    var_545 = wp::sub(var_541, var_546);
                    var_547 = wp::add(var_366, var_545);
                    var_548 = &((var_498).error);
                    var_549 = &((var_501).error);
                    var_551 = wp::load(var_548);
                    var_552 = wp::load(var_549);
                    var_550 = wp::add(var_551, var_552);
                    var_553 = &((var_493).error);
                    var_555 = wp::load(var_553);
                    var_554 = wp::sub(var_550, var_555);
                    var_556 = wp::add(var_367, var_554);
                    var_557 = &((var_498).queries);
                    var_558 = &((var_501).queries);
                    var_560 = wp::load(var_557);
                    var_561 = wp::load(var_558);
                    var_559 = wp::add(var_560, var_561);
                    var_562 = wp::add(var_371, var_559);
                    // Bs[pair,worst]=L;vals[pair,worst]=a;depths[pair,worst]=depth+1;Bs[pair,count]=H;vals[pair,count]=b;depths[pair,count]=depth+1;count+=1;fscale=wp.float64(0.)       <L 170>
                    wp::array_store(var_Bs, var_0, var_466, var_495);
                    wp::array_store(var_vals, var_0, var_466, var_498);
                    var_564 = wp::add(var_482, var_563);
                    wp::array_store(var_depths, var_0, var_466, var_564);
                    wp::array_store(var_Bs, var_0, var_369, var_496);
                    wp::array_store(var_vals, var_0, var_369, var_501);
                    var_566 = wp::add(var_482, var_565);
                    wp::array_store(var_depths, var_0, var_369, var_566);
                    var_568 = wp::add(var_369, var_567);
                    var_569 = 0.0;
                    // for k in range(3):fscale+=wp.length(total[k])                              <L 171>
                    var_571 = wp::extract(var_511, var_570);
                    var_572 = wp::length(var_571);
                    var_573 = wp::add(var_569, var_572);
                    var_575 = wp::extract(var_511, var_574);
                    var_576 = wp::length(var_575);
                    var_577 = wp::add(var_573, var_576);
                    var_579 = wp::extract(var_511, var_578);
                    var_580 = wp::length(var_579);
                    var_581 = wp::add(var_577, var_580);
                    wp::assign(var_432, var_578);
                    wp::assign(var_361, var_511);
                    wp::assign(var_362, var_520);
                    wp::assign(var_363, var_529);
                    wp::assign(var_364, var_538);
                    wp::assign(var_366, var_547);
                    wp::assign(var_367, var_556);
                    wp::assign(var_369, var_568);
                    wp::assign(var_371, var_562);
                    wp::assign(var_383, var_490);
                    wp::assign(var_431, var_581);
        goto start_while_8;
        end_while_8:;
                // counts[pair]=count;query_counts[pair]=queries                                  <L 172>
                wp::array_store(var_counts, var_0, var_369);
                wp::array_store(var_query_counts, var_0, var_371);
                // if bad[0]==0:                                                                  <L 173>
                var_583 = wp::address(var_bad, var_582);
                var_586 = wp::load(var_583);
                var_585 = (var_586 == var_584);
                if (var_585) {
                    // for vertex in range(3):                                                    <L 174>
                    // k=3*pair+vertex;cf[k]=wp.vec3(total[vertex]);cu[k]=float(U/wp.float64(3.));cp[k]=float(D/wp.float64(3.));power[k]=float(W/wp.float64(3.));moment[k]=wp.vec3(M/wp.float64(3.))       <L 175>
                    var_589 = wp::mul(var_588, var_0);
                    var_590 = wp::add(var_589, var_587);
                    var_591 = wp::extract(var_361, var_587);
                    var_592 = wp::vec_t<3, wp::float32>(var_591);
                    wp::array_store(var_cf, var_590, var_592);
                    var_593 = 3.0;
                    var_594 = wp::div(var_362, var_593);
                    var_595 = wp::float(var_594);
                    wp::array_store(var_cu, var_590, var_595);
                    var_596 = 3.0;
                    var_597 = wp::div(var_363, var_596);
                    var_598 = wp::float(var_597);
                    wp::array_store(var_cp, var_590, var_598);
                    var_599 = 3.0;
                    var_600 = wp::div(var_364, var_599);
                    var_601 = wp::float(var_600);
                    wp::array_store(var_power, var_590, var_601);
                    var_602 = 3.0;
                    var_603 = wp::div(var_366, var_602);
                    var_604 = wp::vec_t<3, wp::float32>(var_603);
                    wp::array_store(var_moment, var_590, var_604);
                    var_607 = wp::mul(var_606, var_0);
                    var_608 = wp::add(var_607, var_605);
                    var_609 = wp::extract(var_361, var_605);
                    var_610 = wp::vec_t<3, wp::float32>(var_609);
                    wp::array_store(var_cf, var_608, var_610);
                    var_611 = 3.0;
                    var_612 = wp::div(var_362, var_611);
                    var_613 = wp::float(var_612);
                    wp::array_store(var_cu, var_608, var_613);
                    var_614 = 3.0;
                    var_615 = wp::div(var_363, var_614);
                    var_616 = wp::float(var_615);
                    wp::array_store(var_cp, var_608, var_616);
                    var_617 = 3.0;
                    var_618 = wp::div(var_364, var_617);
                    var_619 = wp::float(var_618);
                    wp::array_store(var_power, var_608, var_619);
                    var_620 = 3.0;
                    var_621 = wp::div(var_366, var_620);
                    var_622 = wp::vec_t<3, wp::float32>(var_621);
                    wp::array_store(var_moment, var_608, var_622);
                    var_625 = wp::mul(var_624, var_0);
                    var_626 = wp::add(var_625, var_623);
                    var_627 = wp::extract(var_361, var_623);
                    var_628 = wp::vec_t<3, wp::float32>(var_627);
                    wp::array_store(var_cf, var_626, var_628);
                    var_629 = 3.0;
                    var_630 = wp::div(var_362, var_629);
                    var_631 = wp::float(var_630);
                    wp::array_store(var_cu, var_626, var_631);
                    var_632 = 3.0;
                    var_633 = wp::div(var_363, var_632);
                    var_634 = wp::float(var_633);
                    wp::array_store(var_cp, var_626, var_634);
                    var_635 = 3.0;
                    var_636 = wp::div(var_364, var_635);
                    var_637 = wp::float(var_636);
                    wp::array_store(var_power, var_626, var_637);
                    var_638 = 3.0;
                    var_639 = wp::div(var_366, var_638);
                    var_640 = wp::vec_t<3, wp::float32>(var_639);
                    wp::array_store(var_moment, var_626, var_640);
                }
                var_641 = wp::where(var_585, var_623, var_183);
                var_642 = wp::where(var_585, var_626, var_432);
            }
            var_643 = wp::where(var_352, var_641, var_183);
            var_644 = wp::where(var_352, var_642, var_186);
            var_645 = wp::where(var_352, var_433, var_229);
        }
        var_646 = wp::where(var_336, var_643, var_183);
        var_647 = wp::where(var_336, var_644, var_186);
        var_648 = wp::where(var_336, var_645, var_229);
    }
}



extern "C" __global__ void prepare_domains_7bcd20a2_cuda_kernel_forward(
    wp::launch_bounds_t<1> dim,
    wp::uint64 var_mesh,
    wp::array_t<wp::vec_t<3, wp::float64>> var_tri,
    wp::vec_t<3, wp::float64> var_bbmin,
    wp::vec_t<3, wp::float64> var_bbmax,
    wp::array_t<wp::vec_t<4, wp::float64>> var_planes,
    wp::array_t<wp::vec_t<3, wp::float64>> var_bounds,
    wp::int32 var_ncells,
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
    wp::array_t<wp::float64> var_areas,
    wp::float64 var_area_total,
    wp::array_t<wp::vec_t<3, wp::float32>> var_q,
    wp::array_t<wp::vec_t<3, wp::float32>> var_vel,
    wp::array_t<wp::vec_t<3, wp::float64>> var_polygon,
    wp::array_t<wp::mat_t<3, 3, wp::float64>> var_Bs,
    wp::array_t<Value_53a65c4a> var_vals,
    wp::array_t<wp::int32> var_depths,
    wp::array_t<wp::int32> var_counts,
    wp::array_t<wp::int32> var_query_counts,
    wp::array_t<wp::vec_t<3, wp::float32>> var_cf,
    wp::array_t<wp::float32> var_cu,
    wp::array_t<wp::float32> var_cp,
    wp::array_t<wp::float32> var_power,
    wp::array_t<wp::vec_t<3, wp::float32>> var_moment,
    wp::array_t<wp::int32> var_bad,
    wp::array_t<wp::float64> var_failure,
    wp::int32 var_cap,
    wp::float64 var_relative_tol,
    wp::float64 var_absolute_tol,
    wp::int32 var_maxdepth,
    wp::array_t<wp::int32> var_polycounts,
    wp::array_t<wp::int32> var_polysources,
    wp::array_t<wp::int32> var_active_count)
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
        wp::float64 var_3;
        wp::mat_t<3, 3, wp::float64> var_4;
        wp::float64 var_5;
        wp::mat_t<3, 3, wp::float64> var_6;
        wp::float64 var_7;
        wp::mat_t<3, 3, wp::float64> var_8;
        const wp::int32 var_9 = 0;
        wp::float64* var_10;
        wp::float64 var_11;
        wp::float64 var_12;
        wp::float64 var_13;
        wp::float64 var_14;
        wp::float64 var_15;
        bool var_16;
        wp::float64 var_17;
        wp::float64 var_18;
        wp::float64 var_19;
        wp::float64 var_20;
        wp::float64 var_21;
        wp::float64 var_22;
        wp::float64 var_23;
        wp::float64 var_24;
        wp::float64 var_25;
        wp::float64 var_26;
        wp::float64 var_27;
        wp::float64 var_28;
        wp::float64 var_29;
        wp::float64 var_30;
        wp::float64 var_31;
        bool var_32;
        wp::float64 var_33;
        wp::float64 var_34;
        wp::float64 var_35;
        wp::float64 var_36;
        bool var_37;
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
        wp::float64 var_52;
        wp::float64 var_53;
        wp::float64 var_54;
        wp::float64 var_55;
        wp::float64 var_56;
        wp::float64 var_57;
        wp::float64 var_58;
        wp::float64 var_59;
        wp::vec_t<3, wp::float64> var_60;
        wp::vec_t<3, wp::float64> var_61;
        wp::vec_t<3, wp::float64> var_62;
        const wp::int32 var_63 = 0;
        const wp::int32 var_64 = 3;
        wp::int32 var_65;
        wp::int32 var_66;
        wp::vec_t<3, wp::float64>* var_67;
        wp::vec_t<3, wp::float64> var_68;
        wp::vec_t<3, wp::float64> var_69;
        wp::float64 var_70;
        wp::vec_t<3, wp::float64> var_71;
        wp::int32* var_72;
        const wp::int32 var_73 = 1;
        wp::int32 var_74;
        wp::int32* var_75;
        wp::range_t var_76;
        wp::int32 var_77;
        wp::int32 var_78;
        wp::int32 var_79;
        wp::float64* var_80;
        wp::int32* var_81;
        wp::vec_t<3, wp::float32>* var_82;
        wp::int32 var_83;
        wp::vec_t<3, wp::float64> var_84;
        wp::vec_t<3, wp::float32> var_85;
        wp::vec_t<3, wp::float64> var_86;
        wp::float64 var_87;
        wp::vec_t<3, wp::float64> var_88;
        wp::float64* var_89;
        wp::int32* var_90;
        wp::vec_t<3, wp::float32>* var_91;
        wp::int32 var_92;
        wp::vec_t<3, wp::float64> var_93;
        wp::vec_t<3, wp::float32> var_94;
        wp::vec_t<3, wp::float64> var_95;
        wp::float64 var_96;
        wp::vec_t<3, wp::float64> var_97;
        wp::mat_t<3, 3, wp::float64> var_98;
        wp::vec_t<3, wp::float64> var_99;
        wp::vec_t<3, wp::float64> var_100;
        const wp::int32 var_101 = 0;
        wp::float64 var_102;
        wp::float64 var_103;
        wp::float64 var_104;
        const wp::int32 var_105 = 1;
        wp::float64 var_106;
        wp::float64 var_107;
        wp::float64 var_108;
        const wp::int32 var_109 = 2;
        wp::float64 var_110;
        wp::float64 var_111;
        wp::float64 var_112;
        const wp::int32 var_113 = 3;
        wp::int32 var_114;
        wp::int32 var_115;
        const wp::float32 var_116 = 0.0;
        wp::vec_t<3, wp::float32> var_117;
        const wp::float32 var_118 = 0.0;
        const wp::float32 var_119 = 0.0;
        const wp::float32 var_120 = 0.0;
        const wp::float32 var_121 = 0.0;
        wp::vec_t<3, wp::float32> var_122;
        const wp::int32 var_123 = 1;
        const wp::int32 var_124 = 3;
        wp::int32 var_125;
        wp::int32 var_126;
        wp::vec_t<3, wp::float64>* var_127;
        wp::vec_t<3, wp::float64> var_128;
        wp::vec_t<3, wp::float64> var_129;
        wp::float64 var_130;
        wp::vec_t<3, wp::float64> var_131;
        wp::int32* var_132;
        const wp::int32 var_133 = 1;
        wp::int32 var_134;
        wp::int32* var_135;
        wp::range_t var_136;
        wp::int32 var_137;
        wp::int32 var_138;
        wp::int32 var_139;
        wp::float64* var_140;
        wp::int32* var_141;
        wp::vec_t<3, wp::float32>* var_142;
        wp::int32 var_143;
        wp::vec_t<3, wp::float64> var_144;
        wp::vec_t<3, wp::float32> var_145;
        wp::vec_t<3, wp::float64> var_146;
        wp::float64 var_147;
        wp::vec_t<3, wp::float64> var_148;
        wp::float64* var_149;
        wp::int32* var_150;
        wp::vec_t<3, wp::float32>* var_151;
        wp::int32 var_152;
        wp::vec_t<3, wp::float64> var_153;
        wp::vec_t<3, wp::float32> var_154;
        wp::vec_t<3, wp::float64> var_155;
        wp::float64 var_156;
        wp::vec_t<3, wp::float64> var_157;
        wp::mat_t<3, 3, wp::float64> var_158;
        wp::vec_t<3, wp::float64> var_159;
        wp::vec_t<3, wp::float64> var_160;
        const wp::int32 var_161 = 0;
        wp::float64 var_162;
        wp::float64 var_163;
        wp::float64 var_164;
        const wp::int32 var_165 = 1;
        wp::float64 var_166;
        wp::float64 var_167;
        wp::float64 var_168;
        const wp::int32 var_169 = 2;
        wp::float64 var_170;
        wp::float64 var_171;
        wp::float64 var_172;
        const wp::int32 var_173 = 3;
        wp::int32 var_174;
        wp::int32 var_175;
        const wp::float32 var_176 = 0.0;
        wp::vec_t<3, wp::float32> var_177;
        const wp::float32 var_178 = 0.0;
        const wp::float32 var_179 = 0.0;
        const wp::float32 var_180 = 0.0;
        const wp::float32 var_181 = 0.0;
        wp::vec_t<3, wp::float32> var_182;
        const wp::int32 var_183 = 2;
        const wp::int32 var_184 = 3;
        wp::int32 var_185;
        wp::int32 var_186;
        wp::vec_t<3, wp::float64>* var_187;
        wp::vec_t<3, wp::float64> var_188;
        wp::vec_t<3, wp::float64> var_189;
        wp::float64 var_190;
        wp::vec_t<3, wp::float64> var_191;
        wp::int32* var_192;
        const wp::int32 var_193 = 1;
        wp::int32 var_194;
        wp::int32* var_195;
        wp::range_t var_196;
        wp::int32 var_197;
        wp::int32 var_198;
        wp::int32 var_199;
        wp::float64* var_200;
        wp::int32* var_201;
        wp::vec_t<3, wp::float32>* var_202;
        wp::int32 var_203;
        wp::vec_t<3, wp::float64> var_204;
        wp::vec_t<3, wp::float32> var_205;
        wp::vec_t<3, wp::float64> var_206;
        wp::float64 var_207;
        wp::vec_t<3, wp::float64> var_208;
        wp::float64* var_209;
        wp::int32* var_210;
        wp::vec_t<3, wp::float32>* var_211;
        wp::int32 var_212;
        wp::vec_t<3, wp::float64> var_213;
        wp::vec_t<3, wp::float32> var_214;
        wp::vec_t<3, wp::float64> var_215;
        wp::float64 var_216;
        wp::vec_t<3, wp::float64> var_217;
        wp::mat_t<3, 3, wp::float64> var_218;
        wp::vec_t<3, wp::float64> var_219;
        wp::vec_t<3, wp::float64> var_220;
        const wp::int32 var_221 = 0;
        wp::float64 var_222;
        wp::float64 var_223;
        wp::float64 var_224;
        const wp::int32 var_225 = 1;
        wp::float64 var_226;
        wp::float64 var_227;
        wp::float64 var_228;
        const wp::int32 var_229 = 2;
        wp::float64 var_230;
        wp::float64 var_231;
        wp::float64 var_232;
        const wp::int32 var_233 = 3;
        wp::int32 var_234;
        wp::int32 var_235;
        const wp::float32 var_236 = 0.0;
        wp::vec_t<3, wp::float32> var_237;
        const wp::float32 var_238 = 0.0;
        const wp::float32 var_239 = 0.0;
        const wp::float32 var_240 = 0.0;
        const wp::float32 var_241 = 0.0;
        wp::vec_t<3, wp::float32> var_242;
        const wp::int32 var_243 = 0;
        const wp::int32 var_244 = 0;
        const bool var_245 = true;
        const wp::int32 var_246 = 0;
        const wp::int32 var_247 = 0;
        wp::float64 var_248;
        const wp::int32 var_249 = 1;
        wp::float64 var_250;
        const wp::int32 var_251 = 2;
        wp::float64 var_252;
        wp::float64 var_253;
        wp::float64 var_254;
        const wp::int32 var_255 = 0;
        wp::float64 var_256;
        const wp::int32 var_257 = 1;
        wp::float64 var_258;
        const wp::int32 var_259 = 2;
        wp::float64 var_260;
        wp::float64 var_261;
        wp::float64 var_262;
        bool var_263;
        const wp::int32 var_264 = 0;
        wp::vec_t<3, wp::float64>* var_265;
        wp::float64 var_266;
        wp::vec_t<3, wp::float64> var_267;
        bool var_268;
        const wp::int32 var_269 = 1;
        wp::vec_t<3, wp::float64>* var_270;
        wp::float64 var_271;
        wp::vec_t<3, wp::float64> var_272;
        bool var_273;
        const bool var_274 = false;
        bool var_275;
        const wp::int32 var_276 = 1;
        const wp::int32 var_277 = 0;
        wp::float64 var_278;
        const wp::int32 var_279 = 1;
        wp::float64 var_280;
        const wp::int32 var_281 = 2;
        wp::float64 var_282;
        wp::float64 var_283;
        wp::float64 var_284;
        const wp::int32 var_285 = 0;
        wp::float64 var_286;
        const wp::int32 var_287 = 1;
        wp::float64 var_288;
        const wp::int32 var_289 = 2;
        wp::float64 var_290;
        wp::float64 var_291;
        wp::float64 var_292;
        bool var_293;
        const wp::int32 var_294 = 0;
        wp::vec_t<3, wp::float64>* var_295;
        wp::float64 var_296;
        wp::vec_t<3, wp::float64> var_297;
        bool var_298;
        const wp::int32 var_299 = 1;
        wp::vec_t<3, wp::float64>* var_300;
        wp::float64 var_301;
        wp::vec_t<3, wp::float64> var_302;
        bool var_303;
        const bool var_304 = false;
        bool var_305;
        const wp::int32 var_306 = 2;
        const wp::int32 var_307 = 0;
        wp::float64 var_308;
        const wp::int32 var_309 = 1;
        wp::float64 var_310;
        const wp::int32 var_311 = 2;
        wp::float64 var_312;
        wp::float64 var_313;
        wp::float64 var_314;
        const wp::int32 var_315 = 0;
        wp::float64 var_316;
        const wp::int32 var_317 = 1;
        wp::float64 var_318;
        const wp::int32 var_319 = 2;
        wp::float64 var_320;
        wp::float64 var_321;
        wp::float64 var_322;
        bool var_323;
        const wp::int32 var_324 = 0;
        wp::vec_t<3, wp::float64>* var_325;
        wp::float64 var_326;
        wp::vec_t<3, wp::float64> var_327;
        bool var_328;
        const wp::int32 var_329 = 1;
        wp::vec_t<3, wp::float64>* var_330;
        wp::float64 var_331;
        wp::vec_t<3, wp::float64> var_332;
        bool var_333;
        const bool var_334 = false;
        bool var_335;
        const wp::int32 var_336 = 0;
        const wp::int32 var_337 = 0;
        bool var_338;
        const wp::int32 var_339 = 0;
        wp::int32* var_340;
        const wp::int32 var_341 = 0;
        bool var_342;
        wp::int32 var_343;
        const wp::int32 var_344 = 0;
        wp::float64 var_345;
        wp::vec_t<3, wp::float64> var_346;
        wp::float64 var_347;
        const wp::int32 var_348 = 0;
        const wp::int32 var_349 = 1;
        wp::float64 var_350;
        wp::vec_t<3, wp::float64> var_351;
        wp::float64 var_352;
        const wp::int32 var_353 = 0;
        const wp::int32 var_354 = 2;
        wp::float64 var_355;
        wp::vec_t<3, wp::float64> var_356;
        wp::float64 var_357;
        const wp::int32 var_358 = 0;
        const wp::int32 var_359 = 3;
        wp::int32 var_360;
        const wp::int32 var_361 = 0;
        wp::int32 var_362;
        const wp::int32 var_363 = 1;
        wp::int32 var_364;
        const wp::int32 var_365 = 4;
        wp::range_t var_366;
        wp::int32 var_367;
        wp::int32 var_368;
        wp::vec_t<4, wp::float64>* var_369;
        wp::vec_t<4, wp::float64> var_370;
        wp::vec_t<4, wp::float64> var_371;
        const wp::int32 var_372 = 0;
        wp::float64 var_373;
        const wp::int32 var_374 = 1;
        wp::float64 var_375;
        const wp::int32 var_376 = 2;
        wp::float64 var_377;
        wp::vec_t<3, wp::float64> var_378;
        wp::vec_t<3, wp::float64> var_379;
        const wp::int32 var_380 = 3;
        wp::float64 var_381;
        wp::vec_t<3, wp::float64> var_382;
        wp::vec_t<3, wp::float64> var_383;
        const wp::int32 var_384 = 0;
        wp::int32 var_385;
        wp::range_t var_386;
        wp::int32 var_387;
        wp::vec_t<3, wp::float64>* var_388;
        wp::vec_t<3, wp::float64> var_389;
        wp::vec_t<3, wp::float64> var_390;
        const wp::int32 var_391 = 1;
        wp::int32 var_392;
        wp::int32 var_393;
        wp::vec_t<3, wp::float64>* var_394;
        wp::vec_t<3, wp::float64> var_395;
        wp::vec_t<3, wp::float64> var_396;
        wp::float64 var_397;
        wp::float64 var_398;
        wp::float64 var_399;
        bool var_400;
        const wp::int32 var_401 = 10;
        bool var_402;
        const wp::int32 var_403 = 0;
        const wp::int32 var_404 = 6;
        wp::int32 var_405;
        const wp::int32 var_406 = 1;
        wp::int32 var_407;
        wp::int32 var_408;
        wp::int32 var_409;
        bool var_410;
        bool var_411;
        wp::float64 var_412;
        bool var_413;
        wp::float64 var_414;
        bool var_415;
        bool var_416;
        wp::float64 var_417;
        bool var_418;
        wp::float64 var_419;
        bool var_420;
        const wp::int32 var_421 = 10;
        bool var_422;
        const wp::int32 var_423 = 0;
        const wp::int32 var_424 = 6;
        wp::int32 var_425;
        wp::float64 var_426;
        wp::float64 var_427;
        wp::vec_t<3, wp::float64> var_428;
        wp::vec_t<3, wp::float64> var_429;
        wp::vec_t<3, wp::float64> var_430;
        const wp::int32 var_431 = 1;
        wp::int32 var_432;
        wp::int32 var_433;
        wp::int32 var_434;
        wp::int32 var_435;
        wp::int32 var_436;
        wp::int32 var_437;
        wp::int32 var_438;
        const wp::int32 var_439 = 3;
        bool var_440;
        wp::int32 var_441;
        wp::int32 var_442;
        wp::int32 var_443;
        wp::int32 var_444;
        const wp::int32 var_445 = 3;
        bool var_446;
        wp::float64 var_447;
        const wp::int32 var_448 = 1;
        wp::int32 var_449;
        const wp::int32 var_450 = 1;
        wp::range_t var_451;
        wp::int32 var_452;
        const wp::int32 var_453 = 0;
        wp::vec_t<3, wp::float64>* var_454;
        wp::vec_t<3, wp::float64>* var_455;
        const wp::int32 var_456 = 1;
        wp::int32 var_457;
        wp::vec_t<3, wp::float64>* var_458;
        wp::mat_t<3, 3, wp::float64> var_459;
        wp::vec_t<3, wp::float64> var_460;
        wp::vec_t<3, wp::float64> var_461;
        wp::vec_t<3, wp::float64> var_462;
        wp::float64 var_463;
        wp::float64 var_464;
        wp::float64 var_465;
        wp::float64 var_466;
        bool var_467;
        const wp::int32 var_468 = 0;
        const wp::int32 var_469 = 1;
        wp::int32 var_470;
        wp::int32 var_471;
        wp::int32 var_472;
        //---------
        // forward
        // def prepare_domains(mesh:wp.uint64,tri:wp.array2d(dtype=wp.vec3d),bbmin:wp.vec3d,bbmax:wp.vec3d,planes:wp.array2d(dtype=wp.vec4d),bounds:wp.array2d(dtype=wp.vec3d),ncells:int,R:wp.mat33d,T0:wp.vec3d,travel:wp.vec3d,load:wp.float64,hold:wp.float64,clock:wp.array(dtype=wp.float64),ptr:wp.array(dtype=int),ids:wp.array(dtype=int),w:wp.array(dtype=wp.float64),ref:wp.array(dtype=wp.vec3d),areas:wp.array(dtype=wp.float64),area_total:wp.float64,q:wp.array(dtype=wp.vec3),vel:wp.array(dtype=wp.vec3),polygon:wp.array3d(dtype=wp.vec3d),Bs:wp.array2d(dtype=wp.mat33d),vals:wp.array2d(dtype=Value),depths:wp.array2d(dtype=int),counts:wp.array(dtype=int),query_counts:wp.array(dtype=int),cf:wp.array(dtype=wp.vec3),cu:wp.array(dtype=float),cp:wp.array(dtype=float),power:wp.array(dtype=float),moment:wp.array(dtype=wp.vec3),bad:wp.array(dtype=int),failure:wp.array(dtype=wp.float64),cap:int,relative_tol:wp.float64,absolute_tol:wp.float64,maxdepth:int,polycounts:wp.array(dtype=int),polysources:wp.array(dtype=int),active_count:wp.array(dtype=int)):       <L 89>
        // pair=wp.tid();face=pair//ncells;cell=pair%ncells;X=wp.mat33d(wp.float64(0.));V=wp.mat33d(wp.float64(0.));local=wp.mat33d(wp.float64(0.));t=clock[0];shape=wp.float64(0.);speed=wp.float64(0.);pi=wp.float64(3.141592653589793)       <L 90>
        var_0 = builtin_tid1d();
        var_1 = wp::floordiv(var_0, var_ncells);
        var_2 = wp::mod(var_0, var_ncells);
        var_3 = 0.0;
        var_4 = wp::mat_t<3, 3, wp::float64>(var_3);
        var_5 = 0.0;
        var_6 = wp::mat_t<3, 3, wp::float64>(var_5);
        var_7 = 0.0;
        var_8 = wp::mat_t<3, 3, wp::float64>(var_7);
        var_10 = wp::address(var_clock, var_9);
        var_12 = wp::load(var_10);
        var_11 = wp::copy(var_12);
        var_13 = 0.0;
        var_14 = 0.0;
        var_15 = 3.141592653589793;
        // if t<load:shape=wp.float64(.5)*(wp.float64(1.)-wp.cos(pi*t/load));speed=wp.float64(.5)*pi/load*wp.sin(pi*t/load)       <L 91>
        var_16 = (var_11 < var_load);
        if (var_16) {
            var_17 = 0.5;
            var_18 = 1.0;
            var_19 = wp::mul(var_15, var_11);
            var_20 = wp::div(var_19, var_load);
            var_21 = wp::cos(var_20);
            var_22 = wp::sub(var_18, var_21);
            var_23 = wp::mul(var_17, var_22);
            var_24 = 0.5;
            var_25 = wp::mul(var_24, var_15);
            var_26 = wp::div(var_25, var_load);
            var_27 = wp::mul(var_15, var_11);
            var_28 = wp::div(var_27, var_load);
            var_29 = wp::sin(var_28);
            var_30 = wp::mul(var_26, var_29);
        }
        if (!var_16) {
            // elif t<load+hold:shape=wp.float64(1.)                                              <L 92>
            var_31 = wp::add(var_load, var_hold);
            var_32 = (var_11 < var_31);
            if (var_32) {
                var_33 = 1.0;
            }
            if (!var_32) {
                // elif t<wp.float64(2.)*load+hold:                                               <L 93>
                var_34 = 2.0;
                var_35 = wp::mul(var_34, var_load);
                var_36 = wp::add(var_35, var_hold);
                var_37 = (var_11 < var_36);
                if (var_37) {
                    // z=(t-load-hold)/load;shape=wp.float64(.5)*(wp.float64(1.)+wp.cos(pi*z));speed=-wp.float64(.5)*pi/load*wp.sin(pi*z)       <L 94>
                    var_38 = wp::sub(var_11, var_load);
                    var_39 = wp::sub(var_38, var_hold);
                    var_40 = wp::div(var_39, var_load);
                    var_41 = 0.5;
                    var_42 = 1.0;
                    var_43 = wp::mul(var_15, var_40);
                    var_44 = wp::cos(var_43);
                    var_45 = wp::add(var_42, var_44);
                    var_46 = wp::mul(var_41, var_45);
                    var_47 = 0.5;
                    var_48 = wp::neg(var_47);
                    var_49 = wp::mul(var_48, var_15);
                    var_50 = wp::div(var_49, var_load);
                    var_51 = wp::mul(var_15, var_40);
                    var_52 = wp::sin(var_51);
                    var_53 = wp::mul(var_50, var_52);
                }
                var_54 = wp::where(var_37, var_46, var_13);
                var_55 = wp::where(var_37, var_53, var_14);
            }
            var_56 = wp::where(var_32, var_33, var_54);
            var_57 = wp::where(var_32, var_14, var_55);
        }
        var_58 = wp::where(var_16, var_23, var_56);
        var_59 = wp::where(var_16, var_30, var_57);
        // T=T0+travel*shape;tv=travel*speed                                                      <L 95>
        var_60 = wp::mul(var_travel, var_58);
        var_61 = wp::add(var_T0, var_60);
        var_62 = wp::mul(var_travel, var_59);
        // for vertex in range(3):                                                                <L 96>
        // k=3*face+vertex;x=ref[k];v=wp.vec3d(wp.float64(0.))                                    <L 97>
        var_65 = wp::mul(var_64, var_1);
        var_66 = wp::add(var_65, var_63);
        var_67 = wp::address(var_ref, var_66);
        var_69 = wp::load(var_67);
        var_68 = wp::copy(var_69);
        var_70 = 0.0;
        var_71 = wp::vec_t<3, wp::float64>(var_70);
        // for j in range(ptr[k],ptr[k+1]):x+=w[j]*wp.vec3d(q[ids[j]]);v+=w[j]*wp.vec3d(vel[ids[j]])       <L 98>
        var_72 = wp::address(var_ptr, var_66);
        var_74 = wp::add(var_66, var_73);
        var_75 = wp::address(var_ptr, var_74);
        var_77 = wp::load(var_72);
        var_78 = wp::load(var_75);
        var_76 = wp::range(var_77, var_78);
        start_for_0:;
            if (iter_cmp(var_76) == 0) goto end_for_0;
            var_79 = wp::iter_next(var_76);
            var_80 = wp::address(var_w, var_79);
            var_81 = wp::address(var_ids, var_79);
            var_83 = wp::load(var_81);
            var_82 = wp::address(var_q, var_83);
            var_85 = wp::load(var_82);
            var_84 = wp::vec_t<3, wp::float64>(var_85);
            var_87 = wp::load(var_80);
            var_86 = wp::mul(var_87, var_84);
            var_88 = wp::add(var_68, var_86);
            var_89 = wp::address(var_w, var_79);
            var_90 = wp::address(var_ids, var_79);
            var_92 = wp::load(var_90);
            var_91 = wp::address(var_vel, var_92);
            var_94 = wp::load(var_91);
            var_93 = wp::vec_t<3, wp::float64>(var_94);
            var_96 = wp::load(var_89);
            var_95 = wp::mul(var_96, var_93);
            var_97 = wp::add(var_71, var_95);
            wp::assign(var_68, var_88);
            wp::assign(var_71, var_97);
            goto start_for_0;
        end_for_0:;
        // xp=wp.transpose(R)*(x-T)                                                               <L 99>
        var_98 = wp::transpose(var_R);
        var_99 = wp::sub(var_68, var_61);
        var_100 = wp::mul(var_98, var_99);
        // for j in range(3):X[vertex,j]=x[j];V[vertex,j]=v[j];local[vertex,j]=xp[j]              <L 100>
        var_102 = wp::extract(var_68, var_101);
        wp::assign_inplace(var_4, var_63, var_101, var_102);
        var_103 = wp::extract(var_71, var_101);
        wp::assign_inplace(var_6, var_63, var_101, var_103);
        var_104 = wp::extract(var_100, var_101);
        wp::assign_inplace(var_8, var_63, var_101, var_104);
        var_106 = wp::extract(var_68, var_105);
        wp::assign_inplace(var_4, var_63, var_105, var_106);
        var_107 = wp::extract(var_71, var_105);
        wp::assign_inplace(var_6, var_63, var_105, var_107);
        var_108 = wp::extract(var_100, var_105);
        wp::assign_inplace(var_8, var_63, var_105, var_108);
        var_110 = wp::extract(var_68, var_109);
        wp::assign_inplace(var_4, var_63, var_109, var_110);
        var_111 = wp::extract(var_71, var_109);
        wp::assign_inplace(var_6, var_63, var_109, var_111);
        var_112 = wp::extract(var_100, var_109);
        wp::assign_inplace(var_8, var_63, var_109, var_112);
        // out=3*pair+vertex;cf[out]=wp.vec3(0.);cu[out]=0.;cp[out]=0.;power[out]=0.;moment[out]=wp.vec3(0.)       <L 101>
        var_114 = wp::mul(var_113, var_0);
        var_115 = wp::add(var_114, var_63);
        var_117 = wp::vec_t<3, wp::float32>(var_116);
        wp::array_store(var_cf, var_115, var_117);
        wp::array_store(var_cu, var_115, var_118);
        wp::array_store(var_cp, var_115, var_119);
        wp::array_store(var_power, var_115, var_120);
        var_122 = wp::vec_t<3, wp::float32>(var_121);
        wp::array_store(var_moment, var_115, var_122);
        // k=3*face+vertex;x=ref[k];v=wp.vec3d(wp.float64(0.))                                    <L 97>
        var_125 = wp::mul(var_124, var_1);
        var_126 = wp::add(var_125, var_123);
        var_127 = wp::address(var_ref, var_126);
        var_129 = wp::load(var_127);
        var_128 = wp::copy(var_129);
        var_130 = 0.0;
        var_131 = wp::vec_t<3, wp::float64>(var_130);
        // for j in range(ptr[k],ptr[k+1]):x+=w[j]*wp.vec3d(q[ids[j]]);v+=w[j]*wp.vec3d(vel[ids[j]])       <L 98>
        var_132 = wp::address(var_ptr, var_126);
        var_134 = wp::add(var_126, var_133);
        var_135 = wp::address(var_ptr, var_134);
        var_137 = wp::load(var_132);
        var_138 = wp::load(var_135);
        var_136 = wp::range(var_137, var_138);
        start_for_2:;
            if (iter_cmp(var_136) == 0) goto end_for_2;
            var_139 = wp::iter_next(var_136);
            var_140 = wp::address(var_w, var_139);
            var_141 = wp::address(var_ids, var_139);
            var_143 = wp::load(var_141);
            var_142 = wp::address(var_q, var_143);
            var_145 = wp::load(var_142);
            var_144 = wp::vec_t<3, wp::float64>(var_145);
            var_147 = wp::load(var_140);
            var_146 = wp::mul(var_147, var_144);
            var_148 = wp::add(var_128, var_146);
            var_149 = wp::address(var_w, var_139);
            var_150 = wp::address(var_ids, var_139);
            var_152 = wp::load(var_150);
            var_151 = wp::address(var_vel, var_152);
            var_154 = wp::load(var_151);
            var_153 = wp::vec_t<3, wp::float64>(var_154);
            var_156 = wp::load(var_149);
            var_155 = wp::mul(var_156, var_153);
            var_157 = wp::add(var_131, var_155);
            wp::assign(var_128, var_148);
            wp::assign(var_131, var_157);
            goto start_for_2;
        end_for_2:;
        // xp=wp.transpose(R)*(x-T)                                                               <L 99>
        var_158 = wp::transpose(var_R);
        var_159 = wp::sub(var_128, var_61);
        var_160 = wp::mul(var_158, var_159);
        // for j in range(3):X[vertex,j]=x[j];V[vertex,j]=v[j];local[vertex,j]=xp[j]              <L 100>
        var_162 = wp::extract(var_128, var_161);
        wp::assign_inplace(var_4, var_123, var_161, var_162);
        var_163 = wp::extract(var_131, var_161);
        wp::assign_inplace(var_6, var_123, var_161, var_163);
        var_164 = wp::extract(var_160, var_161);
        wp::assign_inplace(var_8, var_123, var_161, var_164);
        var_166 = wp::extract(var_128, var_165);
        wp::assign_inplace(var_4, var_123, var_165, var_166);
        var_167 = wp::extract(var_131, var_165);
        wp::assign_inplace(var_6, var_123, var_165, var_167);
        var_168 = wp::extract(var_160, var_165);
        wp::assign_inplace(var_8, var_123, var_165, var_168);
        var_170 = wp::extract(var_128, var_169);
        wp::assign_inplace(var_4, var_123, var_169, var_170);
        var_171 = wp::extract(var_131, var_169);
        wp::assign_inplace(var_6, var_123, var_169, var_171);
        var_172 = wp::extract(var_160, var_169);
        wp::assign_inplace(var_8, var_123, var_169, var_172);
        // out=3*pair+vertex;cf[out]=wp.vec3(0.);cu[out]=0.;cp[out]=0.;power[out]=0.;moment[out]=wp.vec3(0.)       <L 101>
        var_174 = wp::mul(var_173, var_0);
        var_175 = wp::add(var_174, var_123);
        var_177 = wp::vec_t<3, wp::float32>(var_176);
        wp::array_store(var_cf, var_175, var_177);
        wp::array_store(var_cu, var_175, var_178);
        wp::array_store(var_cp, var_175, var_179);
        wp::array_store(var_power, var_175, var_180);
        var_182 = wp::vec_t<3, wp::float32>(var_181);
        wp::array_store(var_moment, var_175, var_182);
        // k=3*face+vertex;x=ref[k];v=wp.vec3d(wp.float64(0.))                                    <L 97>
        var_185 = wp::mul(var_184, var_1);
        var_186 = wp::add(var_185, var_183);
        var_187 = wp::address(var_ref, var_186);
        var_189 = wp::load(var_187);
        var_188 = wp::copy(var_189);
        var_190 = 0.0;
        var_191 = wp::vec_t<3, wp::float64>(var_190);
        // for j in range(ptr[k],ptr[k+1]):x+=w[j]*wp.vec3d(q[ids[j]]);v+=w[j]*wp.vec3d(vel[ids[j]])       <L 98>
        var_192 = wp::address(var_ptr, var_186);
        var_194 = wp::add(var_186, var_193);
        var_195 = wp::address(var_ptr, var_194);
        var_197 = wp::load(var_192);
        var_198 = wp::load(var_195);
        var_196 = wp::range(var_197, var_198);
        start_for_4:;
            if (iter_cmp(var_196) == 0) goto end_for_4;
            var_199 = wp::iter_next(var_196);
            var_200 = wp::address(var_w, var_199);
            var_201 = wp::address(var_ids, var_199);
            var_203 = wp::load(var_201);
            var_202 = wp::address(var_q, var_203);
            var_205 = wp::load(var_202);
            var_204 = wp::vec_t<3, wp::float64>(var_205);
            var_207 = wp::load(var_200);
            var_206 = wp::mul(var_207, var_204);
            var_208 = wp::add(var_188, var_206);
            var_209 = wp::address(var_w, var_199);
            var_210 = wp::address(var_ids, var_199);
            var_212 = wp::load(var_210);
            var_211 = wp::address(var_vel, var_212);
            var_214 = wp::load(var_211);
            var_213 = wp::vec_t<3, wp::float64>(var_214);
            var_216 = wp::load(var_209);
            var_215 = wp::mul(var_216, var_213);
            var_217 = wp::add(var_191, var_215);
            wp::assign(var_188, var_208);
            wp::assign(var_191, var_217);
            goto start_for_4;
        end_for_4:;
        // xp=wp.transpose(R)*(x-T)                                                               <L 99>
        var_218 = wp::transpose(var_R);
        var_219 = wp::sub(var_188, var_61);
        var_220 = wp::mul(var_218, var_219);
        // for j in range(3):X[vertex,j]=x[j];V[vertex,j]=v[j];local[vertex,j]=xp[j]              <L 100>
        var_222 = wp::extract(var_188, var_221);
        wp::assign_inplace(var_4, var_183, var_221, var_222);
        var_223 = wp::extract(var_191, var_221);
        wp::assign_inplace(var_6, var_183, var_221, var_223);
        var_224 = wp::extract(var_220, var_221);
        wp::assign_inplace(var_8, var_183, var_221, var_224);
        var_226 = wp::extract(var_188, var_225);
        wp::assign_inplace(var_4, var_183, var_225, var_226);
        var_227 = wp::extract(var_191, var_225);
        wp::assign_inplace(var_6, var_183, var_225, var_227);
        var_228 = wp::extract(var_220, var_225);
        wp::assign_inplace(var_8, var_183, var_225, var_228);
        var_230 = wp::extract(var_188, var_229);
        wp::assign_inplace(var_4, var_183, var_229, var_230);
        var_231 = wp::extract(var_191, var_229);
        wp::assign_inplace(var_6, var_183, var_229, var_231);
        var_232 = wp::extract(var_220, var_229);
        wp::assign_inplace(var_8, var_183, var_229, var_232);
        // out=3*pair+vertex;cf[out]=wp.vec3(0.);cu[out]=0.;cp[out]=0.;power[out]=0.;moment[out]=wp.vec3(0.)       <L 101>
        var_234 = wp::mul(var_233, var_0);
        var_235 = wp::add(var_234, var_183);
        var_237 = wp::vec_t<3, wp::float32>(var_236);
        wp::array_store(var_cf, var_235, var_237);
        wp::array_store(var_cu, var_235, var_238);
        wp::array_store(var_cp, var_235, var_239);
        wp::array_store(var_power, var_235, var_240);
        var_242 = wp::vec_t<3, wp::float32>(var_241);
        wp::array_store(var_moment, var_235, var_242);
        // counts[pair]=0;query_counts[pair]=0                                                    <L 102>
        wp::array_store(var_counts, var_0, var_243);
        wp::array_store(var_query_counts, var_0, var_244);
        // intersects=True                                                                        <L 103>
        // for axis in range(3):                                                                  <L 104>
        // lo=wp.min(local[0,axis],wp.min(local[1,axis],local[2,axis]));hi=wp.max(local[0,axis],wp.max(local[1,axis],local[2,axis]))       <L 105>
        var_248 = wp::extract(var_8, var_247, var_246);
        var_250 = wp::extract(var_8, var_249, var_246);
        var_252 = wp::extract(var_8, var_251, var_246);
        var_253 = wp::min(var_250, var_252);
        var_254 = wp::min(var_248, var_253);
        var_256 = wp::extract(var_8, var_255, var_246);
        var_258 = wp::extract(var_8, var_257, var_246);
        var_260 = wp::extract(var_8, var_259, var_246);
        var_261 = wp::max(var_258, var_260);
        var_262 = wp::max(var_256, var_261);
        // if hi<bounds[cell,0][axis] or lo>bounds[cell,1][axis]:intersects=False                 <L 106>
        var_265 = wp::address(var_bounds, var_2, var_264);
        var_267 = wp::load(var_265);
        var_266 = wp::extract(var_267, var_246);
        var_268 = (var_262 < var_266);
        var_263 = var_268;
        if (!var_263) {
            var_270 = wp::address(var_bounds, var_2, var_269);
            var_272 = wp::load(var_270);
            var_271 = wp::extract(var_272, var_246);
            var_273 = (var_254 > var_271);
            var_263 = var_263 || var_273;
        }
        if (var_263) {
        }
        var_275 = wp::where(var_263, var_274, var_245);
        // lo=wp.min(local[0,axis],wp.min(local[1,axis],local[2,axis]));hi=wp.max(local[0,axis],wp.max(local[1,axis],local[2,axis]))       <L 105>
        var_278 = wp::extract(var_8, var_277, var_276);
        var_280 = wp::extract(var_8, var_279, var_276);
        var_282 = wp::extract(var_8, var_281, var_276);
        var_283 = wp::min(var_280, var_282);
        var_284 = wp::min(var_278, var_283);
        var_286 = wp::extract(var_8, var_285, var_276);
        var_288 = wp::extract(var_8, var_287, var_276);
        var_290 = wp::extract(var_8, var_289, var_276);
        var_291 = wp::max(var_288, var_290);
        var_292 = wp::max(var_286, var_291);
        // if hi<bounds[cell,0][axis] or lo>bounds[cell,1][axis]:intersects=False                 <L 106>
        var_295 = wp::address(var_bounds, var_2, var_294);
        var_297 = wp::load(var_295);
        var_296 = wp::extract(var_297, var_276);
        var_298 = (var_292 < var_296);
        var_293 = var_298;
        if (!var_293) {
            var_300 = wp::address(var_bounds, var_2, var_299);
            var_302 = wp::load(var_300);
            var_301 = wp::extract(var_302, var_276);
            var_303 = (var_284 > var_301);
            var_293 = var_293 || var_303;
        }
        if (var_293) {
        }
        var_305 = wp::where(var_293, var_304, var_275);
        // lo=wp.min(local[0,axis],wp.min(local[1,axis],local[2,axis]));hi=wp.max(local[0,axis],wp.max(local[1,axis],local[2,axis]))       <L 105>
        var_308 = wp::extract(var_8, var_307, var_306);
        var_310 = wp::extract(var_8, var_309, var_306);
        var_312 = wp::extract(var_8, var_311, var_306);
        var_313 = wp::min(var_310, var_312);
        var_314 = wp::min(var_308, var_313);
        var_316 = wp::extract(var_8, var_315, var_306);
        var_318 = wp::extract(var_8, var_317, var_306);
        var_320 = wp::extract(var_8, var_319, var_306);
        var_321 = wp::max(var_318, var_320);
        var_322 = wp::max(var_316, var_321);
        // if hi<bounds[cell,0][axis] or lo>bounds[cell,1][axis]:intersects=False                 <L 106>
        var_325 = wp::address(var_bounds, var_2, var_324);
        var_327 = wp::load(var_325);
        var_326 = wp::extract(var_327, var_306);
        var_328 = (var_322 < var_326);
        var_323 = var_328;
        if (!var_323) {
            var_330 = wp::address(var_bounds, var_2, var_329);
            var_332 = wp::load(var_330);
            var_331 = wp::extract(var_332, var_306);
            var_333 = (var_314 > var_331);
            var_323 = var_323 || var_333;
        }
        if (var_323) {
        }
        var_335 = wp::where(var_323, var_334, var_305);
        // polycounts[pair]=0;polysources[pair]=0                                                 <L 107>
        wp::array_store(var_polycounts, var_0, var_336);
        wp::array_store(var_polysources, var_0, var_337);
        // if intersects and bad[0]==0:                                                           <L 108>
        var_338 = var_335;
        if (var_338) {
            var_340 = wp::address(var_bad, var_339);
            var_343 = wp::load(var_340);
            var_342 = (var_343 == var_341);
            var_338 = var_338 && var_342;
        }
        if (var_338) {
            // for k in range(3):unit=wp.vec3d(wp.float64(0.));unit[k]=wp.float64(1.);polygon[pair,0,k]=unit       <L 109>
            var_345 = 0.0;
            var_346 = wp::vec_t<3, wp::float64>(var_345);
            var_347 = 1.0;
            wp::assign_inplace(var_346, var_344, var_347);
            wp::array_store(var_polygon, var_0, var_348, var_344, var_346);
            var_350 = 0.0;
            var_351 = wp::vec_t<3, wp::float64>(var_350);
            var_352 = 1.0;
            wp::assign_inplace(var_351, var_349, var_352);
            wp::array_store(var_polygon, var_0, var_353, var_349, var_351);
            var_355 = 0.0;
            var_356 = wp::vec_t<3, wp::float64>(var_355);
            var_357 = 1.0;
            wp::assign_inplace(var_356, var_354, var_357);
            wp::array_store(var_polygon, var_0, var_358, var_354, var_356);
            // n=int(3);src=int(0);dst=int(1)                                                     <L 110>
            var_360 = wp::int(var_359);
            var_362 = wp::int(var_361);
            var_364 = wp::int(var_363);
            // for h in range(4):                                                                 <L 111>
            var_366 = wp::range(var_365);
            var_367 = wp::copy(var_354);
            start_for_6:;
                if (iter_cmp(var_366) == 0) goto end_for_6;
                var_368 = wp::iter_next(var_366);
                // plane=planes[cell,h];normal=wp.vec3d(plane[0],plane[1],plane[2]);distance=local*normal+wp.vec3d(plane[3]);nnew=int(0)       <L 112>
                var_369 = wp::address(var_planes, var_2, var_368);
                var_371 = wp::load(var_369);
                var_370 = wp::copy(var_371);
                var_373 = wp::extract(var_370, var_372);
                var_375 = wp::extract(var_370, var_374);
                var_377 = wp::extract(var_370, var_376);
                var_378 = wp::vec_t<3, wp::float64>(var_373, var_375, var_377);
                var_379 = wp::mul(var_8, var_378);
                var_381 = wp::extract(var_370, var_380);
                var_382 = wp::vec_t<3, wp::float64>(var_381);
                var_383 = wp::add(var_379, var_382);
                var_385 = wp::int(var_384);
                // for k in range(n):                                                             <L 113>
                var_386 = wp::range(var_360);
                start_for_8:;
                    if (iter_cmp(var_386) == 0) goto end_for_8;
                    var_387 = wp::iter_next(var_386);
                    // p0=polygon[pair,src,k];p1=polygon[pair,src,(k+1)%n];d0=wp.dot(p0,distance);d1=wp.dot(p1,distance)       <L 114>
                    var_388 = wp::address(var_polygon, var_0, var_362, var_387);
                    var_390 = wp::load(var_388);
                    var_389 = wp::copy(var_390);
                    var_392 = wp::add(var_387, var_391);
                    var_393 = wp::mod(var_392, var_360);
                    var_394 = wp::address(var_polygon, var_0, var_362, var_393);
                    var_396 = wp::load(var_394);
                    var_395 = wp::copy(var_396);
                    var_397 = wp::dot(var_389, var_383);
                    var_398 = wp::dot(var_395, var_383);
                    // if d0<=wp.float64(0.):                                                     <L 115>
                    var_399 = 0.0;
                    var_400 = (var_397 <= var_399);
                    if (var_400) {
                        // if nnew>=10:wp.atomic_max(bad,0,6)                                     <L 116>
                        var_402 = (var_385 >= var_401);
                        if (var_402) {
                            var_405 = wp::atomic_max(var_bad, var_403, var_404);
                        }
                        if (!var_402) {
                            // else:polygon[pair,dst,nnew]=p0;nnew+=1                             <L 117>
                            wp::array_store(var_polygon, var_0, var_364, var_385, var_389);
                            var_407 = wp::add(var_385, var_406);
                        }
                        var_408 = wp::where(var_402, var_385, var_407);
                    }
                    var_409 = wp::where(var_400, var_408, var_385);
                    // if (d0<wp.float64(0.) and d1>wp.float64(0.)) or (d1<wp.float64(0.) and d0>wp.float64(0.)):       <L 118>
                    var_412 = 0.0;
                    var_413 = (var_397 < var_412);
                    var_411 = var_413;
                    if (var_411) {
                        var_414 = 0.0;
                        var_415 = (var_398 > var_414);
                        var_411 = var_411 && var_415;
                    }
                    var_410 = var_411;
                    if (!var_410) {
                        var_417 = 0.0;
                        var_418 = (var_398 < var_417);
                        var_416 = var_418;
                        if (var_416) {
                            var_419 = 0.0;
                            var_420 = (var_397 > var_419);
                            var_416 = var_416 && var_420;
                        }
                        var_410 = var_410 || var_416;
                    }
                    if (var_410) {
                        // if nnew>=10:wp.atomic_max(bad,0,6)                                     <L 119>
                        var_422 = (var_409 >= var_421);
                        if (var_422) {
                            var_425 = wp::atomic_max(var_bad, var_423, var_424);
                        }
                        if (!var_422) {
                            // else:polygon[pair,dst,nnew]=p0+d0/(d0-d1)*(p1-p0);nnew+=1          <L 120>
                            var_426 = wp::sub(var_397, var_398);
                            var_427 = wp::div(var_397, var_426);
                            var_428 = wp::sub(var_395, var_389);
                            var_429 = wp::mul(var_427, var_428);
                            var_430 = wp::add(var_389, var_429);
                            wp::array_store(var_polygon, var_0, var_364, var_409, var_430);
                            var_432 = wp::add(var_409, var_431);
                        }
                        var_433 = wp::where(var_422, var_409, var_432);
                    }
                    var_434 = wp::where(var_410, var_433, var_409);
                    wp::assign(var_385, var_434);
                    goto start_for_8;
                end_for_8:;
                // n=nnew;tmp=src;src=dst;dst=tmp                                                 <L 121>
                var_435 = wp::copy(var_385);
                var_436 = wp::copy(var_362);
                var_437 = wp::copy(var_364);
                var_438 = wp::copy(var_436);
                // if n<3:break                                                                   <L 122>
                var_440 = (var_435 < var_439);
                if (var_440) {
                    wp::assign(var_367, var_387);
                    wp::assign(var_360, var_435);
                    wp::assign(var_362, var_437);
                    wp::assign(var_364, var_438);
                    goto end_for_6;
                }
                var_441 = wp::where(var_440, var_367, var_387);
                var_442 = wp::where(var_440, var_360, var_435);
                var_443 = wp::where(var_440, var_362, var_437);
                var_444 = wp::where(var_440, var_364, var_438);
                wp::assign(var_367, var_441);
                wp::assign(var_360, var_442);
                wp::assign(var_362, var_443);
                wp::assign(var_364, var_444);
                goto start_for_6;
            end_for_6:;
            // if n>=3:                                                                           <L 123>
            var_446 = (var_360 >= var_445);
            if (var_446) {
                // area=wp.float64(0.)                                                            <L 124>
                var_447 = 0.0;
                // for k in range(1,n-1):                                                         <L 125>
                var_449 = wp::sub(var_360, var_448);
                var_451 = wp::range(var_450, var_449);
                start_for_10:;
                    if (iter_cmp(var_451) == 0) goto end_for_10;
                    var_452 = wp::iter_next(var_451);
                    // B=wp.matrix_from_rows(polygon[pair,src,0],polygon[pair,src,k],polygon[pair,src,k+1]);area+=wp.abs(wp.determinant(B))       <L 126>
                    var_454 = wp::address(var_polygon, var_0, var_362, var_453);
                    var_455 = wp::address(var_polygon, var_0, var_362, var_452);
                    var_457 = wp::add(var_452, var_456);
                    var_458 = wp::address(var_polygon, var_0, var_362, var_457);
                    var_460 = wp::load(var_454);
                    var_461 = wp::load(var_455);
                    var_462 = wp::load(var_458);
                    var_459 = wp::matrix_from_rows<wp::float64>(var_460, var_461, var_462);
                    var_463 = wp::determinant(var_459);
                    var_464 = wp::abs(var_463);
                    var_465 = wp::add(var_447, var_464);
                    wp::assign(var_447, var_465);
                    goto start_for_10;
                end_for_10:;
                // if area>wp.float64(1e-30):polycounts[pair]=n;polysources[pair]=src;wp.atomic_add(active_count,0,1)       <L 127>
                var_466 = 1e-30;
                var_467 = (var_447 > var_466);
                if (var_467) {
                    wp::array_store(var_polycounts, var_0, var_360);
                    wp::array_store(var_polysources, var_0, var_362);
                    var_470 = wp::atomic_add(var_active_count, var_468, var_469);
                }
            }
            var_471 = wp::where(var_446, var_452, var_367);
        }
        var_472 = wp::where(var_338, var_471, var_186);
    }
}


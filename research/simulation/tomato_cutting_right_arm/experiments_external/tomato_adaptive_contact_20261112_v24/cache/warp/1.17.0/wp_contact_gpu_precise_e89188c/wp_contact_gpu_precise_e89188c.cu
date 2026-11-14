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



extern "C" __global__ void tick_precise_0d566969_cuda_kernel_forward(
    wp::launch_bounds_t<1> dim,
    wp::array_t<wp::float64> var_clock,
    wp::float64 var_dt,
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
        const wp::int32 var_0 = 0;
        wp::int32* var_1;
        const wp::int32 var_2 = 0;
        bool var_3;
        wp::int32 var_4;
        const wp::int32 var_5 = 0;
        wp::float64 var_6;
        //---------
        // forward
        // def tick_precise(clock:wp.array(dtype=wp.float64),dt:wp.float64,bad:wp.array(dtype=int)):       <L 50>
        // if bad[0]==0:clock[0]+=dt                                                              <L 51>
        var_1 = wp::address(var_bad, var_0);
        var_4 = wp::load(var_1);
        var_3 = (var_4 == var_2);
        if (var_3) {
            var_6 = wp::atomic_add(var_clock, var_5, var_dt);
        }
    }
}



extern "C" __global__ void samples_precise_5b6db664_cuda_kernel_forward(
    wp::launch_bounds_t<1> dim,
    wp::uint64 var_mesh,
    wp::array_t<wp::vec_t<3, wp::float64>> var_tri,
    wp::vec_t<3, wp::float64> var_bbmin,
    wp::vec_t<3, wp::float64> var_bbmax,
    wp::mat_t<3, 3, wp::float64> var_R,
    wp::vec_t<3, wp::float64> var_T0,
    wp::vec_t<3, wp::float64> var_travel,
    wp::float64 var_load,
    wp::float64 var_hold,
    wp::array_t<wp::float64> var_clock,
    wp::array_t<wp::int32> var_ptr,
    wp::array_t<wp::int32> var_ids,
    wp::array_t<wp::float64> var_w,
    wp::array_t<wp::vec_t<3, wp::float64>> var_X,
    wp::array_t<wp::float32> var_A,
    wp::array_t<wp::vec_t<3, wp::float32>> var_u,
    wp::array_t<wp::vec_t<3, wp::float32>> var_v,
    wp::array_t<wp::vec_t<3, wp::float32>> var_cf,
    wp::array_t<wp::float32> var_cu,
    wp::array_t<wp::float32> var_cp,
    wp::array_t<wp::float32> var_power,
    wp::array_t<wp::vec_t<3, wp::float32>> var_moment,
    wp::array_t<wp::float32> var_phiout,
    wp::int32 var_mode)
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
        wp::float64 var_58;
        wp::vec_t<3, wp::float64> var_59;
        wp::int32* var_60;
        const wp::int32 var_61 = 1;
        wp::int32 var_62;
        wp::int32* var_63;
        wp::range_t var_64;
        wp::int32 var_65;
        wp::int32 var_66;
        wp::int32 var_67;
        wp::float64* var_68;
        wp::int32* var_69;
        wp::vec_t<3, wp::float32>* var_70;
        wp::int32 var_71;
        wp::vec_t<3, wp::float64> var_72;
        wp::vec_t<3, wp::float32> var_73;
        wp::vec_t<3, wp::float64> var_74;
        wp::float64 var_75;
        wp::vec_t<3, wp::float64> var_76;
        wp::float64* var_77;
        wp::int32* var_78;
        wp::vec_t<3, wp::float32>* var_79;
        wp::int32 var_80;
        wp::vec_t<3, wp::float64> var_81;
        wp::vec_t<3, wp::float32> var_82;
        wp::vec_t<3, wp::float64> var_83;
        wp::float64 var_84;
        wp::vec_t<3, wp::float64> var_85;
        wp::mat_t<3, 3, wp::float64> var_86;
        wp::vec_t<3, wp::float64> var_87;
        wp::vec_t<3, wp::float64> var_88;
        wp::float64 var_89;
        wp::float64 var_90;
        wp::vec_t<3, wp::float64> var_91;
        const bool var_92 = true;
        const wp::int32 var_93 = 0;
        bool var_94;
        wp::float64 var_95;
        wp::float64 var_96;
        bool var_97;
        wp::float64 var_98;
        wp::float64 var_99;
        bool var_100;
        const bool var_101 = false;
        bool var_102;
        const wp::int32 var_103 = 1;
        bool var_104;
        wp::float64 var_105;
        wp::float64 var_106;
        bool var_107;
        wp::float64 var_108;
        wp::float64 var_109;
        bool var_110;
        const bool var_111 = false;
        bool var_112;
        const wp::int32 var_113 = 2;
        bool var_114;
        wp::float64 var_115;
        wp::float64 var_116;
        bool var_117;
        wp::float64 var_118;
        wp::float64 var_119;
        bool var_120;
        const bool var_121 = false;
        bool var_122;
        wp::vec_t<3, wp::float32> var_123;
        const wp::float32 var_124 = 10.0;
        wp::mesh_query_point_t var_125;
        const wp::float32 var_126 = 2.0;
        const wp::float32 var_127 = 0.5;
        bool* var_128;
        bool var_129;
        wp::int32* var_130;
        const wp::int32 var_131 = 0;
        wp::vec_t<3, wp::float64>* var_132;
        wp::int32 var_133;
        wp::int32* var_134;
        const wp::int32 var_135 = 1;
        wp::vec_t<3, wp::float64>* var_136;
        wp::int32 var_137;
        wp::int32* var_138;
        const wp::int32 var_139 = 2;
        wp::vec_t<3, wp::float64>* var_140;
        wp::int32 var_141;
        wp::vec_t<3, wp::float64> var_142;
        wp::vec_t<3, wp::float64> var_143;
        wp::vec_t<3, wp::float64> var_144;
        wp::vec_t<3, wp::float64> var_145;
        wp::vec_t<3, wp::float64> var_146;
        wp::float64 var_147;
        wp::float32* var_148;
        wp::float64 var_149;
        wp::float32 var_150;
        wp::float64 var_151;
        wp::float64 var_152;
        bool var_153;
        wp::float32* var_154;
        wp::float64 var_155;
        wp::float32 var_156;
        wp::vec_t<3, wp::float64> var_157;
        wp::vec_t<3, wp::float64> var_158;
        wp::vec_t<3, wp::float64> var_159;
        wp::int32* var_160;
        const wp::int32 var_161 = 1;
        wp::vec_t<3, wp::float64>* var_162;
        wp::int32 var_163;
        wp::int32* var_164;
        const wp::int32 var_165 = 0;
        wp::vec_t<3, wp::float64>* var_166;
        wp::int32 var_167;
        wp::vec_t<3, wp::float64> var_168;
        wp::vec_t<3, wp::float64> var_169;
        wp::vec_t<3, wp::float64> var_170;
        wp::int32* var_171;
        const wp::int32 var_172 = 2;
        wp::vec_t<3, wp::float64>* var_173;
        wp::int32 var_174;
        wp::int32* var_175;
        const wp::int32 var_176 = 0;
        wp::vec_t<3, wp::float64>* var_177;
        wp::int32 var_178;
        wp::vec_t<3, wp::float64> var_179;
        wp::vec_t<3, wp::float64> var_180;
        wp::vec_t<3, wp::float64> var_181;
        wp::vec_t<3, wp::float64> var_182;
        wp::vec_t<3, wp::float64> var_183;
        wp::vec_t<3, wp::float64> var_184;
        wp::vec_t<3, wp::float64> var_185;
        bool var_186;
        wp::float64 var_187;
        bool var_188;
        wp::vec_t<3, wp::float64> var_189;
        bool var_190;
        wp::float64 var_191;
        wp::vec_t<3, wp::float64> var_192;
        const wp::int32 var_193 = 1;
        bool var_194;
        const wp::int32 var_195 = 1;
        wp::float64 var_196;
        const wp::int32 var_197 = 1;
        wp::float64 var_198;
        wp::float64 var_199;
        wp::float64 var_200;
        wp::float64 var_201;
        wp::float64 var_202;
        wp::vec_t<3, wp::float64> var_203;
        wp::float64 var_204;
        wp::vec_t<3, wp::float64> var_205;
        wp::float64 var_206;
        wp::float64 var_207;
        wp::float64 var_208;
        wp::float64 var_209;
        wp::float32* var_210;
        wp::float64 var_211;
        wp::float32 var_212;
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
        wp::vec_t<3, wp::float32> var_236;
        wp::float64 var_237;
        wp::float64 var_238;
        wp::float64 var_239;
        wp::float32* var_240;
        wp::float64 var_241;
        wp::float32 var_242;
        wp::float64 var_243;
        wp::float64 var_244;
        wp::float64 var_245;
        wp::float32 var_246;
        wp::float64 var_247;
        wp::float64 var_248;
        wp::float32 var_249;
        wp::float64 var_250;
        wp::float32 var_251;
        wp::vec_t<3, wp::float64> var_252;
        wp::vec_t<3, wp::float64> var_253;
        wp::vec_t<3, wp::float32> var_254;
        wp::float32 var_255;
        //---------
        // forward
        // def samples_precise(mesh:wp.uint64,tri:wp.array2d(dtype=wp.vec3d),bbmin:wp.vec3d,bbmax:wp.vec3d,R:wp.mat33d,T0:wp.vec3d,travel:wp.vec3d,load:wp.float64,hold:wp.float64,clock:wp.array(dtype=wp.float64),ptr:wp.array(dtype=int),ids:wp.array(dtype=int),w:wp.array(dtype=wp.float64),X:wp.array(dtype=wp.vec3d),A:wp.array(dtype=float),u:wp.array(dtype=wp.vec3),v:wp.array(dtype=wp.vec3),cf:wp.array(dtype=wp.vec3),cu:wp.array(dtype=float),cp:wp.array(dtype=float),power:wp.array(dtype=float),moment:wp.array(dtype=wp.vec3),phiout:wp.array(dtype=float),mode:int):       <L 26>
        // i=wp.tid();t=clock[0];s=wp.float64(0.);speed=wp.float64(0.);pi=wp.float64(3.141592653589793)       <L 27>
        var_0 = builtin_tid1d();
        var_2 = wp::address(var_clock, var_1);
        var_4 = wp::load(var_2);
        var_3 = wp::copy(var_4);
        var_5 = 0.0;
        var_6 = 0.0;
        var_7 = 3.141592653589793;
        // if t<load:s=wp.float64(.5)*(wp.float64(1.)-wp.cos(pi*t/load));speed=wp.float64(.5)*pi/load*wp.sin(pi*t/load)       <L 28>
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
            // elif t<load+hold:s=wp.float64(1.)                                                  <L 29>
            var_23 = wp::add(var_load, var_hold);
            var_24 = (var_3 < var_23);
            if (var_24) {
                var_25 = 1.0;
            }
            if (!var_24) {
                // elif t<wp.float64(2.)*load+hold:                                               <L 30>
                var_26 = 2.0;
                var_27 = wp::mul(var_26, var_load);
                var_28 = wp::add(var_27, var_hold);
                var_29 = (var_3 < var_28);
                if (var_29) {
                    // a=(t-load-hold)/load;s=wp.float64(.5)*(wp.float64(1.)+wp.cos(pi*a));speed=-wp.float64(.5)*pi/load*wp.sin(pi*a)       <L 31>
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
        // T=T0+travel*s;tv=travel*speed;x=X[i];vel=wp.vec3d(wp.float64(0.))                      <L 32>
        var_52 = wp::mul(var_travel, var_50);
        var_53 = wp::add(var_T0, var_52);
        var_54 = wp::mul(var_travel, var_51);
        var_55 = wp::address(var_X, var_0);
        var_57 = wp::load(var_55);
        var_56 = wp::copy(var_57);
        var_58 = 0.0;
        var_59 = wp::vec_t<3, wp::float64>(var_58);
        // for k in range(ptr[i],ptr[i+1]):x+=w[k]*wp.vec3d(u[ids[k]]);vel+=w[k]*wp.vec3d(v[ids[k]])       <L 33>
        var_60 = wp::address(var_ptr, var_0);
        var_62 = wp::add(var_0, var_61);
        var_63 = wp::address(var_ptr, var_62);
        var_65 = wp::load(var_60);
        var_66 = wp::load(var_63);
        var_64 = wp::range(var_65, var_66);
        start_for_0:;
            if (iter_cmp(var_64) == 0) goto end_for_0;
            var_67 = wp::iter_next(var_64);
            var_68 = wp::address(var_w, var_67);
            var_69 = wp::address(var_ids, var_67);
            var_71 = wp::load(var_69);
            var_70 = wp::address(var_u, var_71);
            var_73 = wp::load(var_70);
            var_72 = wp::vec_t<3, wp::float64>(var_73);
            var_75 = wp::load(var_68);
            var_74 = wp::mul(var_75, var_72);
            var_76 = wp::add(var_56, var_74);
            var_77 = wp::address(var_w, var_67);
            var_78 = wp::address(var_ids, var_67);
            var_80 = wp::load(var_78);
            var_79 = wp::address(var_v, var_80);
            var_82 = wp::load(var_79);
            var_81 = wp::vec_t<3, wp::float64>(var_82);
            var_84 = wp::load(var_77);
            var_83 = wp::mul(var_84, var_81);
            var_85 = wp::add(var_59, var_83);
            wp::assign(var_56, var_76);
            wp::assign(var_59, var_85);
            goto start_for_0;
        end_for_0:;
        // p=wp.transpose(R)*(x-T);phi=wp.float64(100.);normal=wp.vec3d(wp.float64(0.))           <L 34>
        var_86 = wp::transpose(var_R);
        var_87 = wp::sub(var_56, var_53);
        var_88 = wp::mul(var_86, var_87);
        var_89 = 100.0;
        var_90 = 0.0;
        var_91 = wp::vec_t<3, wp::float64>(var_90);
        // inside=True                                                                            <L 35>
        // for axis in range(3):                                                                  <L 36>
        // if p[axis]<bbmin[axis] or p[axis]>bbmax[axis]:inside=False                             <L 37>
        var_95 = wp::extract(var_88, var_93);
        var_96 = wp::extract(var_bbmin, var_93);
        var_97 = (var_95 < var_96);
        var_94 = var_97;
        if (!var_94) {
            var_98 = wp::extract(var_88, var_93);
            var_99 = wp::extract(var_bbmax, var_93);
            var_100 = (var_98 > var_99);
            var_94 = var_94 || var_100;
        }
        if (var_94) {
        }
        var_102 = wp::where(var_94, var_101, var_92);
        var_105 = wp::extract(var_88, var_103);
        var_106 = wp::extract(var_bbmin, var_103);
        var_107 = (var_105 < var_106);
        var_104 = var_107;
        if (!var_104) {
            var_108 = wp::extract(var_88, var_103);
            var_109 = wp::extract(var_bbmax, var_103);
            var_110 = (var_108 > var_109);
            var_104 = var_104 || var_110;
        }
        if (var_104) {
        }
        var_112 = wp::where(var_104, var_111, var_102);
        var_115 = wp::extract(var_88, var_113);
        var_116 = wp::extract(var_bbmin, var_113);
        var_117 = (var_115 < var_116);
        var_114 = var_117;
        if (!var_114) {
            var_118 = wp::extract(var_88, var_113);
            var_119 = wp::extract(var_bbmax, var_113);
            var_120 = (var_118 > var_119);
            var_114 = var_114 || var_120;
        }
        if (var_114) {
        }
        var_122 = wp::where(var_114, var_121, var_112);
        // if inside:                                                                             <L 38>
        if (var_122) {
            // r=wp.mesh_query_point_sign_winding_number(mesh,wp.vec3(p),10.)                     <L 39>
            var_123 = wp::vec_t<3, wp::float32>(var_88);
            var_125 = wp::mesh_query_point_sign_winding_number(var_mesh, var_123, var_124, var_126, var_127);
            // if r.result:                                                                       <L 40>
            var_128 = &((var_125).result);
            var_129 = wp::load(var_128);
            if (var_129) {
                // c=closest(p,tri[r.face,0],tri[r.face,1],tri[r.face,2]);d=p-c;l=wp.length(d);phi=wp.float64(r.sign)*l       <L 41>
                var_130 = &((var_125).face);
                var_133 = wp::load(var_130);
                var_132 = wp::address(var_tri, var_133, var_131);
                var_134 = &((var_125).face);
                var_137 = wp::load(var_134);
                var_136 = wp::address(var_tri, var_137, var_135);
                var_138 = &((var_125).face);
                var_141 = wp::load(var_138);
                var_140 = wp::address(var_tri, var_141, var_139);
                var_143 = wp::load(var_132);
                var_144 = wp::load(var_136);
                var_145 = wp::load(var_140);
                var_142 = closest_0(var_88, var_143, var_144, var_145);
                var_146 = wp::sub(var_88, var_142);
                var_147 = wp::length(var_146);
                var_148 = &((var_125).sign);
                var_150 = wp::load(var_148);
                var_149 = wp::float64(var_150);
                var_151 = wp::mul(var_149, var_147);
                // if l>wp.float64(1.e-15):normal=R*(wp.float64(r.sign)*d/l)                      <L 42>
                var_152 = 1e-15;
                var_153 = (var_147 > var_152);
                if (var_153) {
                    var_154 = &((var_125).sign);
                    var_156 = wp::load(var_154);
                    var_155 = wp::float64(var_156);
                    var_157 = wp::mul(var_155, var_146);
                    var_158 = wp::div(var_157, var_147);
                    var_159 = wp::mul(var_R, var_158);
                }
                if (!var_153) {
                    // else:normal=R*wp.normalize(wp.cross(tri[r.face,1]-tri[r.face,0],tri[r.face,2]-tri[r.face,0]))       <L 43>
                    var_160 = &((var_125).face);
                    var_163 = wp::load(var_160);
                    var_162 = wp::address(var_tri, var_163, var_161);
                    var_164 = &((var_125).face);
                    var_167 = wp::load(var_164);
                    var_166 = wp::address(var_tri, var_167, var_165);
                    var_169 = wp::load(var_162);
                    var_170 = wp::load(var_166);
                    var_168 = wp::sub(var_169, var_170);
                    var_171 = &((var_125).face);
                    var_174 = wp::load(var_171);
                    var_173 = wp::address(var_tri, var_174, var_172);
                    var_175 = &((var_125).face);
                    var_178 = wp::load(var_175);
                    var_177 = wp::address(var_tri, var_178, var_176);
                    var_180 = wp::load(var_173);
                    var_181 = wp::load(var_177);
                    var_179 = wp::sub(var_180, var_181);
                    var_182 = wp::cross(var_168, var_179);
                    var_183 = wp::normalize(var_182);
                    var_184 = wp::mul(var_R, var_183);
                }
                var_185 = wp::where(var_153, var_159, var_184);
            }
            var_186 = wp::load(var_128);
            var_188 = wp::load(var_128);
            var_187 = wp::where(var_188, var_151, var_89);
            var_190 = wp::load(var_128);
            var_189 = wp::where(var_190, var_185, var_91);
        }
        var_191 = wp::where(var_122, var_187, var_89);
        var_192 = wp::where(var_122, var_189, var_91);
        // if mode==1:phi=T[1]-x[1];normal=wp.vec3d(wp.float64(0.),wp.float64(-1.),wp.float64(0.))       <L 44>
        var_194 = (var_mode == var_193);
        if (var_194) {
            var_196 = wp::extract(var_53, var_195);
            var_198 = wp::extract(var_56, var_197);
            var_199 = wp::sub(var_196, var_198);
            var_200 = 0.0;
            var_201 = -1.0;
            var_202 = 0.0;
            var_203 = wp::vec_t<3, wp::float64>(var_200, var_201, var_202);
        }
        var_204 = wp::where(var_194, var_199, var_191);
        var_205 = wp::where(var_194, var_203, var_192);
        // depth=wp.max(-phi,wp.float64(0.));fn=wp.float64(1.e9)*wp.float64(A[i])*depth;rel=vel-tv;tangent=rel-wp.dot(rel,normal)*normal;vs=wp.length(tangent);fr=wp.vec3d(wp.float64(0.))       <L 45>
        var_206 = wp::neg(var_204);
        var_207 = 0.0;
        var_208 = wp::max(var_206, var_207);
        var_209 = 1000000000.0;
        var_210 = wp::address(var_A, var_0);
        var_212 = wp::load(var_210);
        var_211 = wp::float64(var_212);
        var_213 = wp::mul(var_209, var_211);
        var_214 = wp::mul(var_213, var_208);
        var_215 = wp::sub(var_59, var_54);
        var_216 = wp::dot(var_215, var_205);
        var_217 = wp::mul(var_216, var_205);
        var_218 = wp::sub(var_215, var_217);
        var_219 = wp::length(var_218);
        var_220 = 0.0;
        var_221 = wp::vec_t<3, wp::float64>(var_220);
        // if vs>wp.float64(1.e-30):fr=-wp.float64(.2)*fn*wp.tanh(vs/wp.float64(.001))*tangent/vs       <L 46>
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
        // f=fn*normal+fr;cf[i]=wp.vec3(f);cu[i]=float(wp.float64(.5)*wp.float64(1.e9)*wp.float64(A[i])*depth*depth);cp[i]=float(-wp.dot(fr,rel));power[i]=float(wp.dot(f,tv));moment[i]=wp.vec3(wp.cross(x-T,f));phiout[i]=float(phi)       <L 47>
        var_234 = wp::mul(var_214, var_205);
        var_235 = wp::add(var_234, var_233);
        var_236 = wp::vec_t<3, wp::float32>(var_235);
        wp::array_store(var_cf, var_0, var_236);
        var_237 = 0.5;
        var_238 = 1000000000.0;
        var_239 = wp::mul(var_237, var_238);
        var_240 = wp::address(var_A, var_0);
        var_242 = wp::load(var_240);
        var_241 = wp::float64(var_242);
        var_243 = wp::mul(var_239, var_241);
        var_244 = wp::mul(var_243, var_208);
        var_245 = wp::mul(var_244, var_208);
        var_246 = wp::float(var_245);
        wp::array_store(var_cu, var_0, var_246);
        var_247 = wp::dot(var_233, var_215);
        var_248 = wp::neg(var_247);
        var_249 = wp::float(var_248);
        wp::array_store(var_cp, var_0, var_249);
        var_250 = wp::dot(var_235, var_54);
        var_251 = wp::float(var_250);
        wp::array_store(var_power, var_0, var_251);
        var_252 = wp::sub(var_56, var_53);
        var_253 = wp::cross(var_252, var_235);
        var_254 = wp::vec_t<3, wp::float32>(var_253);
        wp::array_store(var_moment, var_0, var_254);
        var_255 = wp::float(var_204);
        wp::array_store(var_phiout, var_0, var_255);
    }
}


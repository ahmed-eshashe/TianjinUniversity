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


// /home/omen/Documents/Codex/experiments/tomato_apic_repair_20261110_v03/src/apic_kernels.py:2
static CUDA_CALLABLE wp::float64 basis_0(
    wp::int32 var_i,
    wp::float64 var_x)
{
    //---------
    // primal vars
    wp::float64 var_0;
    const wp::int32 var_1 = 0;
    bool var_2;
    wp::float64 var_3;
    wp::float64 var_4;
    wp::float64 var_5;
    wp::float64 var_6;
    wp::float64 var_7;
    wp::float64 var_8;
    wp::float64 var_9;
    const wp::int32 var_10 = 1;
    bool var_11;
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
    wp::float64 var_24;
    wp::float64 var_25;
    wp::float64 var_26;
    wp::float64 var_27;
    //---------
    // forward
    // def basis(i:int,x:wp.float64):                                                         <L 3>
    // r=wp.float64(0.0)                                                                      <L 4>
    var_0 = 0.0;
    // if i==0:r=wp.float64(.5)*(wp.float64(1.5)-x)*(wp.float64(1.5)-x)                       <L 5>
    var_2 = (var_i == var_1);
    if (var_2) {
        var_3 = 0.5;
        var_4 = 1.5;
        var_5 = wp::sub(var_4, var_x);
        var_6 = wp::mul(var_3, var_5);
        var_7 = 1.5;
        var_8 = wp::sub(var_7, var_x);
        var_9 = wp::mul(var_6, var_8);
    }
    if (!var_2) {
        // elif i==1:r=wp.float64(.75)-(x-wp.float64(1.0))*(x-wp.float64(1.0))                <L 6>
        var_11 = (var_i == var_10);
        if (var_11) {
            var_12 = 0.75;
            var_13 = 1.0;
            var_14 = wp::sub(var_x, var_13);
            var_15 = 1.0;
            var_16 = wp::sub(var_x, var_15);
            var_17 = wp::mul(var_14, var_16);
            var_18 = wp::sub(var_12, var_17);
        }
        if (!var_11) {
            // else:r=wp.float64(.5)*(x-wp.float64(.5))*(x-wp.float64(.5))                    <L 7>
            var_19 = 0.5;
            var_20 = 0.5;
            var_21 = wp::sub(var_x, var_20);
            var_22 = wp::mul(var_19, var_21);
            var_23 = 0.5;
            var_24 = wp::sub(var_x, var_23);
            var_25 = wp::mul(var_22, var_24);
        }
        var_26 = wp::where(var_11, var_18, var_25);
    }
    var_27 = wp::where(var_2, var_9, var_26);
    // return r                                                                               <L 8>
    return var_27;
}


// /home/omen/Documents/Codex/experiments/tomato_apic_repair_20261110_v03/src/apic_kernels.py:9
static CUDA_CALLABLE wp::float64 dbasis_0(
    wp::int32 var_i,
    wp::float64 var_x)
{
    //---------
    // primal vars
    wp::float64 var_0;
    const wp::int32 var_1 = 0;
    bool var_2;
    wp::float64 var_3;
    wp::float64 var_4;
    const wp::int32 var_5 = 1;
    bool var_6;
    wp::float64 var_7;
    wp::float64 var_8;
    wp::float64 var_9;
    wp::float64 var_10;
    wp::float64 var_11;
    wp::float64 var_12;
    wp::float64 var_13;
    wp::float64 var_14;
    wp::float64 var_15;
    //---------
    // forward
    // def dbasis(i:int,x:wp.float64):                                                        <L 10>
    // r=wp.float64(0.0)                                                                      <L 11>
    var_0 = 0.0;
    // if i==0:r=x-wp.float64(1.5)                                                            <L 12>
    var_2 = (var_i == var_1);
    if (var_2) {
        var_3 = 1.5;
        var_4 = wp::sub(var_x, var_3);
    }
    if (!var_2) {
        // elif i==1:r=-wp.float64(2.0)*(x-wp.float64(1.0))                                   <L 13>
        var_6 = (var_i == var_5);
        if (var_6) {
            var_7 = 2.0;
            var_8 = wp::neg(var_7);
            var_9 = 1.0;
            var_10 = wp::sub(var_x, var_9);
            var_11 = wp::mul(var_8, var_10);
        }
        if (!var_6) {
            // else:r=x-wp.float64(.5)                                                        <L 14>
            var_12 = 0.5;
            var_13 = wp::sub(var_x, var_12);
        }
        var_14 = wp::where(var_6, var_11, var_13);
    }
    var_15 = wp::where(var_2, var_4, var_14);
    // return r                                                                               <L 15>
    return var_15;
}


// /home/omen/Documents/Codex/experiments/tomato_apic_repair_20261110_v03/src/apic_kernels.py:16
static CUDA_CALLABLE bool compatible_0(
    wp::int32 var_a,
    wp::int32 var_b)
{
    //---------
    // primal vars
    const wp::int32 var_0 = 81;
    wp::int32 var_1;
    const wp::int32 var_2 = 81;
    wp::int32 var_3;
    bool var_4;
    const wp::int32 var_5 = 81;
    wp::int32 var_6;
    const wp::int32 var_7 = 81;
    wp::int32 var_8;
    const wp::int32 var_9 = 0;
    const wp::int32 var_10 = 3;
    wp::int32 var_11;
    const wp::int32 var_12 = 3;
    wp::int32 var_13;
    wp::int32 var_14;
    const wp::int32 var_15 = 2;
    bool var_16;
    const bool var_17 = false;
    bool var_18;
    const wp::int32 var_19 = 3;
    wp::int32 var_20;
    const wp::int32 var_21 = 3;
    wp::int32 var_22;
    const wp::int32 var_23 = 1;
    const wp::int32 var_24 = 3;
    wp::int32 var_25;
    const wp::int32 var_26 = 3;
    wp::int32 var_27;
    wp::int32 var_28;
    const wp::int32 var_29 = 2;
    bool var_30;
    const bool var_31 = false;
    bool var_32;
    const wp::int32 var_33 = 3;
    wp::int32 var_34;
    const wp::int32 var_35 = 3;
    wp::int32 var_36;
    const wp::int32 var_37 = 2;
    const wp::int32 var_38 = 3;
    wp::int32 var_39;
    const wp::int32 var_40 = 3;
    wp::int32 var_41;
    wp::int32 var_42;
    const wp::int32 var_43 = 2;
    bool var_44;
    const bool var_45 = false;
    bool var_46;
    const wp::int32 var_47 = 3;
    wp::int32 var_48;
    const wp::int32 var_49 = 3;
    wp::int32 var_50;
    const wp::int32 var_51 = 3;
    const wp::int32 var_52 = 3;
    wp::int32 var_53;
    const wp::int32 var_54 = 3;
    wp::int32 var_55;
    wp::int32 var_56;
    const wp::int32 var_57 = 2;
    bool var_58;
    const bool var_59 = false;
    bool var_60;
    const wp::int32 var_61 = 3;
    wp::int32 var_62;
    const wp::int32 var_63 = 3;
    wp::int32 var_64;
    //---------
    // forward
    // def compatible(a:int,b:int):                                                           <L 17>
    // good=a//81==b//81                                                                      <L 18>
    var_1 = wp::floordiv(var_a, var_0);
    var_3 = wp::floordiv(var_b, var_2);
    var_4 = (var_1 == var_3);
    // a=a%81;b=b%81                                                                          <L 19>
    var_6 = wp::mod(var_a, var_5);
    var_8 = wp::mod(var_b, var_7);
    // for j in range(4):                                                                     <L 20>
    // x=a%3;y=b%3                                                                            <L 21>
    var_11 = wp::mod(var_6, var_10);
    var_13 = wp::mod(var_8, var_12);
    // if x*y==2:good=False                                                                   <L 22>
    var_14 = wp::mul(var_11, var_13);
    var_16 = (var_14 == var_15);
    if (var_16) {
    }
    var_18 = wp::where(var_16, var_17, var_4);
    // a=a//3;b=b//3                                                                          <L 23>
    var_20 = wp::floordiv(var_6, var_19);
    var_22 = wp::floordiv(var_8, var_21);
    // x=a%3;y=b%3                                                                            <L 21>
    var_25 = wp::mod(var_20, var_24);
    var_27 = wp::mod(var_22, var_26);
    // if x*y==2:good=False                                                                   <L 22>
    var_28 = wp::mul(var_25, var_27);
    var_30 = (var_28 == var_29);
    if (var_30) {
    }
    var_32 = wp::where(var_30, var_31, var_18);
    // a=a//3;b=b//3                                                                          <L 23>
    var_34 = wp::floordiv(var_20, var_33);
    var_36 = wp::floordiv(var_22, var_35);
    // x=a%3;y=b%3                                                                            <L 21>
    var_39 = wp::mod(var_34, var_38);
    var_41 = wp::mod(var_36, var_40);
    // if x*y==2:good=False                                                                   <L 22>
    var_42 = wp::mul(var_39, var_41);
    var_44 = (var_42 == var_43);
    if (var_44) {
    }
    var_46 = wp::where(var_44, var_45, var_32);
    // a=a//3;b=b//3                                                                          <L 23>
    var_48 = wp::floordiv(var_34, var_47);
    var_50 = wp::floordiv(var_36, var_49);
    // x=a%3;y=b%3                                                                            <L 21>
    var_53 = wp::mod(var_48, var_52);
    var_55 = wp::mod(var_50, var_54);
    // if x*y==2:good=False                                                                   <L 22>
    var_56 = wp::mul(var_53, var_55);
    var_58 = (var_56 == var_57);
    if (var_58) {
    }
    var_60 = wp::where(var_58, var_59, var_46);
    // a=a//3;b=b//3                                                                          <L 23>
    var_62 = wp::floordiv(var_48, var_61);
    var_64 = wp::floordiv(var_50, var_63);
    // return good                                                                            <L 24>
    return var_60;
}


// /home/omen/Documents/Codex/experiments/tomato_apic_repair_20261110_v03/src/apic_kernels.py:2
static CUDA_CALLABLE void adj_basis_0(
    wp::int32 var_i,
    wp::float64 var_x,
    wp::int32 & adj_i,
    wp::float64 & adj_x,
    wp::float64 & adj_ret)
{
	// reverse mode disabled (module option "enable_backward" is False or no dependent kernel found with "enable_backward")
}


// /home/omen/Documents/Codex/experiments/tomato_apic_repair_20261110_v03/src/apic_kernels.py:9
static CUDA_CALLABLE void adj_dbasis_0(
    wp::int32 var_i,
    wp::float64 var_x,
    wp::int32 & adj_i,
    wp::float64 & adj_x,
    wp::float64 & adj_ret)
{
	// reverse mode disabled (module option "enable_backward" is False or no dependent kernel found with "enable_backward")
}


// /home/omen/Documents/Codex/experiments/tomato_apic_repair_20261110_v03/src/apic_kernels.py:16
static CUDA_CALLABLE void adj_compatible_0(
    wp::int32 var_a,
    wp::int32 var_b,
    wp::int32 & adj_a,
    wp::int32 & adj_b,
    bool & adj_ret)
{
	// reverse mode disabled (module option "enable_backward" is False or no dependent kernel found with "enable_backward")
}



extern "C" __global__ void grid_energy_04890b1f_cuda_kernel_forward(
    wp::launch_bounds_t<2> dim,
    wp::array_t<wp::float64> var_m,
    wp::array_t<wp::vec_t<3, wp::float64>> var_vg,
    wp::array_t<wp::float64> var_stats)
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
        const wp::int32 var_2 = 4;
        wp::float64 var_3;
        wp::float64* var_4;
        wp::float64 var_5;
        wp::float64 var_6;
        wp::vec_t<3, wp::float64>* var_7;
        wp::vec_t<3, wp::float64>* var_8;
        wp::float64 var_9;
        wp::vec_t<3, wp::float64> var_10;
        wp::vec_t<3, wp::float64> var_11;
        wp::float64 var_12;
        wp::float64 var_13;
        //---------
        // forward
        // def grid_energy(m:wp.array2d(dtype=wp.float64),vg:wp.array2d(dtype=wp.vec3d),stats:wp.array(dtype=wp.float64)):       <L 59>
        // a,i=wp.tid();wp.atomic_add(stats,4,wp.float64(.5)*m[a,i]*wp.dot(vg[a,i],vg[a,i]))       <L 60>
        builtin_tid2d(var_0, var_1);
        var_3 = 0.5;
        var_4 = wp::address(var_m, var_0, var_1);
        var_6 = wp::load(var_4);
        var_5 = wp::mul(var_3, var_6);
        var_7 = wp::address(var_vg, var_0, var_1);
        var_8 = wp::address(var_vg, var_0, var_1);
        var_10 = wp::load(var_7);
        var_11 = wp::load(var_8);
        var_9 = wp::dot(var_10, var_11);
        var_12 = wp::mul(var_5, var_9);
        var_13 = wp::atomic_add(var_stats, var_2, var_12);
    }
}



extern "C" __global__ void stencil_current_10fc4fa3_cuda_kernel_forward(
    wp::launch_bounds_t<1> dim,
    wp::array_t<wp::vec_t<3, wp::float64>> var_x,
    wp::float64 var_h,
    wp::vec_t<3, wp::int32> var_origin,
    wp::vec_t<3, wp::int32> var_dims,
    wp::array_t<wp::int32> var_ids,
    wp::array_t<wp::float64> var_w,
    wp::array_t<wp::vec_t<3, wp::float64>> var_g,
    wp::array_t<wp::vec_t<3, wp::float64>> var_r,
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
        wp::vec_t<3, wp::float64>* var_1;
        wp::vec_t<3, wp::float64> var_2;
        wp::vec_t<3, wp::float64> var_3;
        const wp::int32 var_4 = 0;
        wp::float64 var_5;
        wp::float64 var_6;
        wp::float64 var_7;
        wp::float64 var_8;
        wp::int32 var_9;
        const wp::int32 var_10 = 1;
        wp::float64 var_11;
        wp::float64 var_12;
        wp::float64 var_13;
        wp::float64 var_14;
        wp::int32 var_15;
        const wp::int32 var_16 = 2;
        wp::float64 var_17;
        wp::float64 var_18;
        wp::float64 var_19;
        wp::float64 var_20;
        wp::int32 var_21;
        wp::vec_t<3, wp::int32> var_22;
        const wp::int32 var_23 = 0;
        wp::int32 var_24;
        wp::float64 var_25;
        const wp::int32 var_26 = 1;
        wp::int32 var_27;
        wp::float64 var_28;
        const wp::int32 var_29 = 2;
        wp::int32 var_30;
        wp::float64 var_31;
        wp::vec_t<3, wp::float64> var_32;
        wp::vec_t<3, wp::float64> var_33;
        const wp::int32 var_34 = 0;
        const wp::int32 var_35 = 0;
        const wp::int32 var_36 = 0;
        const wp::int32 var_37 = 9;
        wp::int32 var_38;
        const wp::int32 var_39 = 3;
        wp::int32 var_40;
        wp::int32 var_41;
        wp::int32 var_42;
        wp::vec_t<3, wp::int32> var_43;
        wp::vec_t<3, wp::int32> var_44;
        wp::vec_t<3, wp::int32> var_45;
        bool var_46;
        const wp::int32 var_47 = 0;
        wp::int32 var_48;
        const wp::int32 var_49 = 0;
        bool var_50;
        const wp::int32 var_51 = 1;
        wp::int32 var_52;
        const wp::int32 var_53 = 0;
        bool var_54;
        const wp::int32 var_55 = 2;
        wp::int32 var_56;
        const wp::int32 var_57 = 0;
        bool var_58;
        const wp::int32 var_59 = 0;
        wp::int32 var_60;
        const wp::int32 var_61 = 0;
        wp::int32 var_62;
        bool var_63;
        const wp::int32 var_64 = 1;
        wp::int32 var_65;
        const wp::int32 var_66 = 1;
        wp::int32 var_67;
        bool var_68;
        const wp::int32 var_69 = 2;
        wp::int32 var_70;
        const wp::int32 var_71 = 2;
        wp::int32 var_72;
        bool var_73;
        const wp::int32 var_74 = 0;
        const wp::int32 var_75 = 1;
        wp::int32 var_76;
        const wp::int32 var_77 = 0;
        wp::float64 var_78;
        wp::float64 var_79;
        wp::vec_t<3, wp::float64> var_80;
        wp::float64 var_81;
        wp::vec_t<3, wp::float64> var_82;
        const wp::int32 var_83 = 0;
        wp::int32 var_84;
        const wp::int32 var_85 = 1;
        wp::int32 var_86;
        wp::int32 var_87;
        const wp::int32 var_88 = 1;
        wp::int32 var_89;
        wp::int32 var_90;
        const wp::int32 var_91 = 2;
        wp::int32 var_92;
        wp::int32 var_93;
        const wp::int32 var_94 = 2;
        wp::int32 var_95;
        wp::int32 var_96;
        const wp::int32 var_97 = 0;
        wp::float64 var_98;
        wp::float64 var_99;
        const wp::int32 var_100 = 1;
        wp::float64 var_101;
        wp::float64 var_102;
        const wp::int32 var_103 = 2;
        wp::float64 var_104;
        wp::float64 var_105;
        wp::float64 var_106;
        wp::float64 var_107;
        const wp::int32 var_108 = 0;
        wp::float64 var_109;
        wp::float64 var_110;
        wp::float64 var_111;
        wp::float64 var_112;
        const wp::int32 var_113 = 1;
        wp::float64 var_114;
        wp::float64 var_115;
        wp::float64 var_116;
        wp::float64 var_117;
        wp::float64 var_118;
        const wp::int32 var_119 = 2;
        wp::float64 var_120;
        wp::float64 var_121;
        wp::float64 var_122;
        wp::vec_t<3, wp::float64> var_123;
        wp::vec_t<3, wp::float64> var_124;
        const wp::int32 var_125 = 0;
        wp::int32 var_126;
        wp::float64 var_127;
        const wp::int32 var_128 = 1;
        wp::int32 var_129;
        wp::float64 var_130;
        const wp::int32 var_131 = 2;
        wp::int32 var_132;
        wp::float64 var_133;
        wp::vec_t<3, wp::float64> var_134;
        wp::vec_t<3, wp::float64> var_135;
        wp::vec_t<3, wp::float64>* var_136;
        wp::vec_t<3, wp::float64> var_137;
        wp::vec_t<3, wp::float64> var_138;
        const wp::int32 var_139 = 1;
        const wp::int32 var_140 = 9;
        wp::int32 var_141;
        const wp::int32 var_142 = 3;
        wp::int32 var_143;
        wp::int32 var_144;
        wp::int32 var_145;
        wp::vec_t<3, wp::int32> var_146;
        wp::vec_t<3, wp::int32> var_147;
        wp::vec_t<3, wp::int32> var_148;
        bool var_149;
        const wp::int32 var_150 = 0;
        wp::int32 var_151;
        const wp::int32 var_152 = 0;
        bool var_153;
        const wp::int32 var_154 = 1;
        wp::int32 var_155;
        const wp::int32 var_156 = 0;
        bool var_157;
        const wp::int32 var_158 = 2;
        wp::int32 var_159;
        const wp::int32 var_160 = 0;
        bool var_161;
        const wp::int32 var_162 = 0;
        wp::int32 var_163;
        const wp::int32 var_164 = 0;
        wp::int32 var_165;
        bool var_166;
        const wp::int32 var_167 = 1;
        wp::int32 var_168;
        const wp::int32 var_169 = 1;
        wp::int32 var_170;
        bool var_171;
        const wp::int32 var_172 = 2;
        wp::int32 var_173;
        const wp::int32 var_174 = 2;
        wp::int32 var_175;
        bool var_176;
        const wp::int32 var_177 = 0;
        const wp::int32 var_178 = 1;
        wp::int32 var_179;
        const wp::int32 var_180 = 0;
        wp::float64 var_181;
        wp::float64 var_182;
        wp::vec_t<3, wp::float64> var_183;
        wp::float64 var_184;
        wp::vec_t<3, wp::float64> var_185;
        const wp::int32 var_186 = 0;
        wp::int32 var_187;
        const wp::int32 var_188 = 1;
        wp::int32 var_189;
        wp::int32 var_190;
        const wp::int32 var_191 = 1;
        wp::int32 var_192;
        wp::int32 var_193;
        const wp::int32 var_194 = 2;
        wp::int32 var_195;
        wp::int32 var_196;
        const wp::int32 var_197 = 2;
        wp::int32 var_198;
        wp::int32 var_199;
        const wp::int32 var_200 = 0;
        wp::float64 var_201;
        wp::float64 var_202;
        const wp::int32 var_203 = 1;
        wp::float64 var_204;
        wp::float64 var_205;
        const wp::int32 var_206 = 2;
        wp::float64 var_207;
        wp::float64 var_208;
        wp::float64 var_209;
        wp::float64 var_210;
        const wp::int32 var_211 = 0;
        wp::float64 var_212;
        wp::float64 var_213;
        wp::float64 var_214;
        wp::float64 var_215;
        const wp::int32 var_216 = 1;
        wp::float64 var_217;
        wp::float64 var_218;
        wp::float64 var_219;
        wp::float64 var_220;
        wp::float64 var_221;
        const wp::int32 var_222 = 2;
        wp::float64 var_223;
        wp::float64 var_224;
        wp::float64 var_225;
        wp::vec_t<3, wp::float64> var_226;
        wp::vec_t<3, wp::float64> var_227;
        const wp::int32 var_228 = 0;
        wp::int32 var_229;
        wp::float64 var_230;
        const wp::int32 var_231 = 1;
        wp::int32 var_232;
        wp::float64 var_233;
        const wp::int32 var_234 = 2;
        wp::int32 var_235;
        wp::float64 var_236;
        wp::vec_t<3, wp::float64> var_237;
        wp::vec_t<3, wp::float64> var_238;
        wp::vec_t<3, wp::float64>* var_239;
        wp::vec_t<3, wp::float64> var_240;
        wp::vec_t<3, wp::float64> var_241;
        wp::float64 var_242;
        wp::float64 var_243;
        wp::float64 var_244;
        const wp::int32 var_245 = 2;
        const wp::int32 var_246 = 9;
        wp::int32 var_247;
        const wp::int32 var_248 = 3;
        wp::int32 var_249;
        wp::int32 var_250;
        wp::int32 var_251;
        wp::vec_t<3, wp::int32> var_252;
        wp::vec_t<3, wp::int32> var_253;
        wp::vec_t<3, wp::int32> var_254;
        bool var_255;
        const wp::int32 var_256 = 0;
        wp::int32 var_257;
        const wp::int32 var_258 = 0;
        bool var_259;
        const wp::int32 var_260 = 1;
        wp::int32 var_261;
        const wp::int32 var_262 = 0;
        bool var_263;
        const wp::int32 var_264 = 2;
        wp::int32 var_265;
        const wp::int32 var_266 = 0;
        bool var_267;
        const wp::int32 var_268 = 0;
        wp::int32 var_269;
        const wp::int32 var_270 = 0;
        wp::int32 var_271;
        bool var_272;
        const wp::int32 var_273 = 1;
        wp::int32 var_274;
        const wp::int32 var_275 = 1;
        wp::int32 var_276;
        bool var_277;
        const wp::int32 var_278 = 2;
        wp::int32 var_279;
        const wp::int32 var_280 = 2;
        wp::int32 var_281;
        bool var_282;
        const wp::int32 var_283 = 0;
        const wp::int32 var_284 = 1;
        wp::int32 var_285;
        const wp::int32 var_286 = 0;
        wp::float64 var_287;
        wp::float64 var_288;
        wp::vec_t<3, wp::float64> var_289;
        wp::float64 var_290;
        wp::vec_t<3, wp::float64> var_291;
        const wp::int32 var_292 = 0;
        wp::int32 var_293;
        const wp::int32 var_294 = 1;
        wp::int32 var_295;
        wp::int32 var_296;
        const wp::int32 var_297 = 1;
        wp::int32 var_298;
        wp::int32 var_299;
        const wp::int32 var_300 = 2;
        wp::int32 var_301;
        wp::int32 var_302;
        const wp::int32 var_303 = 2;
        wp::int32 var_304;
        wp::int32 var_305;
        const wp::int32 var_306 = 0;
        wp::float64 var_307;
        wp::float64 var_308;
        const wp::int32 var_309 = 1;
        wp::float64 var_310;
        wp::float64 var_311;
        const wp::int32 var_312 = 2;
        wp::float64 var_313;
        wp::float64 var_314;
        wp::float64 var_315;
        wp::float64 var_316;
        const wp::int32 var_317 = 0;
        wp::float64 var_318;
        wp::float64 var_319;
        wp::float64 var_320;
        wp::float64 var_321;
        const wp::int32 var_322 = 1;
        wp::float64 var_323;
        wp::float64 var_324;
        wp::float64 var_325;
        wp::float64 var_326;
        wp::float64 var_327;
        const wp::int32 var_328 = 2;
        wp::float64 var_329;
        wp::float64 var_330;
        wp::float64 var_331;
        wp::vec_t<3, wp::float64> var_332;
        wp::vec_t<3, wp::float64> var_333;
        const wp::int32 var_334 = 0;
        wp::int32 var_335;
        wp::float64 var_336;
        const wp::int32 var_337 = 1;
        wp::int32 var_338;
        wp::float64 var_339;
        const wp::int32 var_340 = 2;
        wp::int32 var_341;
        wp::float64 var_342;
        wp::vec_t<3, wp::float64> var_343;
        wp::vec_t<3, wp::float64> var_344;
        wp::vec_t<3, wp::float64>* var_345;
        wp::vec_t<3, wp::float64> var_346;
        wp::vec_t<3, wp::float64> var_347;
        wp::float64 var_348;
        wp::float64 var_349;
        wp::float64 var_350;
        const wp::int32 var_351 = 1;
        const wp::int32 var_352 = 0;
        const wp::int32 var_353 = 9;
        wp::int32 var_354;
        const wp::int32 var_355 = 3;
        wp::int32 var_356;
        wp::int32 var_357;
        wp::int32 var_358;
        wp::vec_t<3, wp::int32> var_359;
        wp::vec_t<3, wp::int32> var_360;
        wp::vec_t<3, wp::int32> var_361;
        bool var_362;
        const wp::int32 var_363 = 0;
        wp::int32 var_364;
        const wp::int32 var_365 = 0;
        bool var_366;
        const wp::int32 var_367 = 1;
        wp::int32 var_368;
        const wp::int32 var_369 = 0;
        bool var_370;
        const wp::int32 var_371 = 2;
        wp::int32 var_372;
        const wp::int32 var_373 = 0;
        bool var_374;
        const wp::int32 var_375 = 0;
        wp::int32 var_376;
        const wp::int32 var_377 = 0;
        wp::int32 var_378;
        bool var_379;
        const wp::int32 var_380 = 1;
        wp::int32 var_381;
        const wp::int32 var_382 = 1;
        wp::int32 var_383;
        bool var_384;
        const wp::int32 var_385 = 2;
        wp::int32 var_386;
        const wp::int32 var_387 = 2;
        wp::int32 var_388;
        bool var_389;
        const wp::int32 var_390 = 0;
        const wp::int32 var_391 = 1;
        wp::int32 var_392;
        const wp::int32 var_393 = 0;
        wp::float64 var_394;
        wp::float64 var_395;
        wp::vec_t<3, wp::float64> var_396;
        wp::float64 var_397;
        wp::vec_t<3, wp::float64> var_398;
        const wp::int32 var_399 = 0;
        wp::int32 var_400;
        const wp::int32 var_401 = 1;
        wp::int32 var_402;
        wp::int32 var_403;
        const wp::int32 var_404 = 1;
        wp::int32 var_405;
        wp::int32 var_406;
        const wp::int32 var_407 = 2;
        wp::int32 var_408;
        wp::int32 var_409;
        const wp::int32 var_410 = 2;
        wp::int32 var_411;
        wp::int32 var_412;
        const wp::int32 var_413 = 0;
        wp::float64 var_414;
        wp::float64 var_415;
        const wp::int32 var_416 = 1;
        wp::float64 var_417;
        wp::float64 var_418;
        const wp::int32 var_419 = 2;
        wp::float64 var_420;
        wp::float64 var_421;
        wp::float64 var_422;
        wp::float64 var_423;
        const wp::int32 var_424 = 0;
        wp::float64 var_425;
        wp::float64 var_426;
        wp::float64 var_427;
        wp::float64 var_428;
        const wp::int32 var_429 = 1;
        wp::float64 var_430;
        wp::float64 var_431;
        wp::float64 var_432;
        wp::float64 var_433;
        wp::float64 var_434;
        const wp::int32 var_435 = 2;
        wp::float64 var_436;
        wp::float64 var_437;
        wp::float64 var_438;
        wp::vec_t<3, wp::float64> var_439;
        wp::vec_t<3, wp::float64> var_440;
        const wp::int32 var_441 = 0;
        wp::int32 var_442;
        wp::float64 var_443;
        const wp::int32 var_444 = 1;
        wp::int32 var_445;
        wp::float64 var_446;
        const wp::int32 var_447 = 2;
        wp::int32 var_448;
        wp::float64 var_449;
        wp::vec_t<3, wp::float64> var_450;
        wp::vec_t<3, wp::float64> var_451;
        wp::vec_t<3, wp::float64>* var_452;
        wp::vec_t<3, wp::float64> var_453;
        wp::vec_t<3, wp::float64> var_454;
        wp::float64 var_455;
        wp::float64 var_456;
        wp::float64 var_457;
        const wp::int32 var_458 = 1;
        const wp::int32 var_459 = 9;
        wp::int32 var_460;
        const wp::int32 var_461 = 3;
        wp::int32 var_462;
        wp::int32 var_463;
        wp::int32 var_464;
        wp::vec_t<3, wp::int32> var_465;
        wp::vec_t<3, wp::int32> var_466;
        wp::vec_t<3, wp::int32> var_467;
        bool var_468;
        const wp::int32 var_469 = 0;
        wp::int32 var_470;
        const wp::int32 var_471 = 0;
        bool var_472;
        const wp::int32 var_473 = 1;
        wp::int32 var_474;
        const wp::int32 var_475 = 0;
        bool var_476;
        const wp::int32 var_477 = 2;
        wp::int32 var_478;
        const wp::int32 var_479 = 0;
        bool var_480;
        const wp::int32 var_481 = 0;
        wp::int32 var_482;
        const wp::int32 var_483 = 0;
        wp::int32 var_484;
        bool var_485;
        const wp::int32 var_486 = 1;
        wp::int32 var_487;
        const wp::int32 var_488 = 1;
        wp::int32 var_489;
        bool var_490;
        const wp::int32 var_491 = 2;
        wp::int32 var_492;
        const wp::int32 var_493 = 2;
        wp::int32 var_494;
        bool var_495;
        const wp::int32 var_496 = 0;
        const wp::int32 var_497 = 1;
        wp::int32 var_498;
        const wp::int32 var_499 = 0;
        wp::float64 var_500;
        wp::float64 var_501;
        wp::vec_t<3, wp::float64> var_502;
        wp::float64 var_503;
        wp::vec_t<3, wp::float64> var_504;
        const wp::int32 var_505 = 0;
        wp::int32 var_506;
        const wp::int32 var_507 = 1;
        wp::int32 var_508;
        wp::int32 var_509;
        const wp::int32 var_510 = 1;
        wp::int32 var_511;
        wp::int32 var_512;
        const wp::int32 var_513 = 2;
        wp::int32 var_514;
        wp::int32 var_515;
        const wp::int32 var_516 = 2;
        wp::int32 var_517;
        wp::int32 var_518;
        const wp::int32 var_519 = 0;
        wp::float64 var_520;
        wp::float64 var_521;
        const wp::int32 var_522 = 1;
        wp::float64 var_523;
        wp::float64 var_524;
        const wp::int32 var_525 = 2;
        wp::float64 var_526;
        wp::float64 var_527;
        wp::float64 var_528;
        wp::float64 var_529;
        const wp::int32 var_530 = 0;
        wp::float64 var_531;
        wp::float64 var_532;
        wp::float64 var_533;
        wp::float64 var_534;
        const wp::int32 var_535 = 1;
        wp::float64 var_536;
        wp::float64 var_537;
        wp::float64 var_538;
        wp::float64 var_539;
        wp::float64 var_540;
        const wp::int32 var_541 = 2;
        wp::float64 var_542;
        wp::float64 var_543;
        wp::float64 var_544;
        wp::vec_t<3, wp::float64> var_545;
        wp::vec_t<3, wp::float64> var_546;
        const wp::int32 var_547 = 0;
        wp::int32 var_548;
        wp::float64 var_549;
        const wp::int32 var_550 = 1;
        wp::int32 var_551;
        wp::float64 var_552;
        const wp::int32 var_553 = 2;
        wp::int32 var_554;
        wp::float64 var_555;
        wp::vec_t<3, wp::float64> var_556;
        wp::vec_t<3, wp::float64> var_557;
        wp::vec_t<3, wp::float64>* var_558;
        wp::vec_t<3, wp::float64> var_559;
        wp::vec_t<3, wp::float64> var_560;
        wp::float64 var_561;
        wp::float64 var_562;
        wp::float64 var_563;
        const wp::int32 var_564 = 2;
        const wp::int32 var_565 = 9;
        wp::int32 var_566;
        const wp::int32 var_567 = 3;
        wp::int32 var_568;
        wp::int32 var_569;
        wp::int32 var_570;
        wp::vec_t<3, wp::int32> var_571;
        wp::vec_t<3, wp::int32> var_572;
        wp::vec_t<3, wp::int32> var_573;
        bool var_574;
        const wp::int32 var_575 = 0;
        wp::int32 var_576;
        const wp::int32 var_577 = 0;
        bool var_578;
        const wp::int32 var_579 = 1;
        wp::int32 var_580;
        const wp::int32 var_581 = 0;
        bool var_582;
        const wp::int32 var_583 = 2;
        wp::int32 var_584;
        const wp::int32 var_585 = 0;
        bool var_586;
        const wp::int32 var_587 = 0;
        wp::int32 var_588;
        const wp::int32 var_589 = 0;
        wp::int32 var_590;
        bool var_591;
        const wp::int32 var_592 = 1;
        wp::int32 var_593;
        const wp::int32 var_594 = 1;
        wp::int32 var_595;
        bool var_596;
        const wp::int32 var_597 = 2;
        wp::int32 var_598;
        const wp::int32 var_599 = 2;
        wp::int32 var_600;
        bool var_601;
        const wp::int32 var_602 = 0;
        const wp::int32 var_603 = 1;
        wp::int32 var_604;
        const wp::int32 var_605 = 0;
        wp::float64 var_606;
        wp::float64 var_607;
        wp::vec_t<3, wp::float64> var_608;
        wp::float64 var_609;
        wp::vec_t<3, wp::float64> var_610;
        const wp::int32 var_611 = 0;
        wp::int32 var_612;
        const wp::int32 var_613 = 1;
        wp::int32 var_614;
        wp::int32 var_615;
        const wp::int32 var_616 = 1;
        wp::int32 var_617;
        wp::int32 var_618;
        const wp::int32 var_619 = 2;
        wp::int32 var_620;
        wp::int32 var_621;
        const wp::int32 var_622 = 2;
        wp::int32 var_623;
        wp::int32 var_624;
        const wp::int32 var_625 = 0;
        wp::float64 var_626;
        wp::float64 var_627;
        const wp::int32 var_628 = 1;
        wp::float64 var_629;
        wp::float64 var_630;
        const wp::int32 var_631 = 2;
        wp::float64 var_632;
        wp::float64 var_633;
        wp::float64 var_634;
        wp::float64 var_635;
        const wp::int32 var_636 = 0;
        wp::float64 var_637;
        wp::float64 var_638;
        wp::float64 var_639;
        wp::float64 var_640;
        const wp::int32 var_641 = 1;
        wp::float64 var_642;
        wp::float64 var_643;
        wp::float64 var_644;
        wp::float64 var_645;
        wp::float64 var_646;
        const wp::int32 var_647 = 2;
        wp::float64 var_648;
        wp::float64 var_649;
        wp::float64 var_650;
        wp::vec_t<3, wp::float64> var_651;
        wp::vec_t<3, wp::float64> var_652;
        const wp::int32 var_653 = 0;
        wp::int32 var_654;
        wp::float64 var_655;
        const wp::int32 var_656 = 1;
        wp::int32 var_657;
        wp::float64 var_658;
        const wp::int32 var_659 = 2;
        wp::int32 var_660;
        wp::float64 var_661;
        wp::vec_t<3, wp::float64> var_662;
        wp::vec_t<3, wp::float64> var_663;
        wp::vec_t<3, wp::float64>* var_664;
        wp::vec_t<3, wp::float64> var_665;
        wp::vec_t<3, wp::float64> var_666;
        wp::float64 var_667;
        wp::float64 var_668;
        wp::float64 var_669;
        const wp::int32 var_670 = 2;
        const wp::int32 var_671 = 0;
        const wp::int32 var_672 = 9;
        wp::int32 var_673;
        const wp::int32 var_674 = 3;
        wp::int32 var_675;
        wp::int32 var_676;
        wp::int32 var_677;
        wp::vec_t<3, wp::int32> var_678;
        wp::vec_t<3, wp::int32> var_679;
        wp::vec_t<3, wp::int32> var_680;
        bool var_681;
        const wp::int32 var_682 = 0;
        wp::int32 var_683;
        const wp::int32 var_684 = 0;
        bool var_685;
        const wp::int32 var_686 = 1;
        wp::int32 var_687;
        const wp::int32 var_688 = 0;
        bool var_689;
        const wp::int32 var_690 = 2;
        wp::int32 var_691;
        const wp::int32 var_692 = 0;
        bool var_693;
        const wp::int32 var_694 = 0;
        wp::int32 var_695;
        const wp::int32 var_696 = 0;
        wp::int32 var_697;
        bool var_698;
        const wp::int32 var_699 = 1;
        wp::int32 var_700;
        const wp::int32 var_701 = 1;
        wp::int32 var_702;
        bool var_703;
        const wp::int32 var_704 = 2;
        wp::int32 var_705;
        const wp::int32 var_706 = 2;
        wp::int32 var_707;
        bool var_708;
        const wp::int32 var_709 = 0;
        const wp::int32 var_710 = 1;
        wp::int32 var_711;
        const wp::int32 var_712 = 0;
        wp::float64 var_713;
        wp::float64 var_714;
        wp::vec_t<3, wp::float64> var_715;
        wp::float64 var_716;
        wp::vec_t<3, wp::float64> var_717;
        const wp::int32 var_718 = 0;
        wp::int32 var_719;
        const wp::int32 var_720 = 1;
        wp::int32 var_721;
        wp::int32 var_722;
        const wp::int32 var_723 = 1;
        wp::int32 var_724;
        wp::int32 var_725;
        const wp::int32 var_726 = 2;
        wp::int32 var_727;
        wp::int32 var_728;
        const wp::int32 var_729 = 2;
        wp::int32 var_730;
        wp::int32 var_731;
        const wp::int32 var_732 = 0;
        wp::float64 var_733;
        wp::float64 var_734;
        const wp::int32 var_735 = 1;
        wp::float64 var_736;
        wp::float64 var_737;
        const wp::int32 var_738 = 2;
        wp::float64 var_739;
        wp::float64 var_740;
        wp::float64 var_741;
        wp::float64 var_742;
        const wp::int32 var_743 = 0;
        wp::float64 var_744;
        wp::float64 var_745;
        wp::float64 var_746;
        wp::float64 var_747;
        const wp::int32 var_748 = 1;
        wp::float64 var_749;
        wp::float64 var_750;
        wp::float64 var_751;
        wp::float64 var_752;
        wp::float64 var_753;
        const wp::int32 var_754 = 2;
        wp::float64 var_755;
        wp::float64 var_756;
        wp::float64 var_757;
        wp::vec_t<3, wp::float64> var_758;
        wp::vec_t<3, wp::float64> var_759;
        const wp::int32 var_760 = 0;
        wp::int32 var_761;
        wp::float64 var_762;
        const wp::int32 var_763 = 1;
        wp::int32 var_764;
        wp::float64 var_765;
        const wp::int32 var_766 = 2;
        wp::int32 var_767;
        wp::float64 var_768;
        wp::vec_t<3, wp::float64> var_769;
        wp::vec_t<3, wp::float64> var_770;
        wp::vec_t<3, wp::float64>* var_771;
        wp::vec_t<3, wp::float64> var_772;
        wp::vec_t<3, wp::float64> var_773;
        wp::float64 var_774;
        wp::float64 var_775;
        wp::float64 var_776;
        const wp::int32 var_777 = 1;
        const wp::int32 var_778 = 9;
        wp::int32 var_779;
        const wp::int32 var_780 = 3;
        wp::int32 var_781;
        wp::int32 var_782;
        wp::int32 var_783;
        wp::vec_t<3, wp::int32> var_784;
        wp::vec_t<3, wp::int32> var_785;
        wp::vec_t<3, wp::int32> var_786;
        bool var_787;
        const wp::int32 var_788 = 0;
        wp::int32 var_789;
        const wp::int32 var_790 = 0;
        bool var_791;
        const wp::int32 var_792 = 1;
        wp::int32 var_793;
        const wp::int32 var_794 = 0;
        bool var_795;
        const wp::int32 var_796 = 2;
        wp::int32 var_797;
        const wp::int32 var_798 = 0;
        bool var_799;
        const wp::int32 var_800 = 0;
        wp::int32 var_801;
        const wp::int32 var_802 = 0;
        wp::int32 var_803;
        bool var_804;
        const wp::int32 var_805 = 1;
        wp::int32 var_806;
        const wp::int32 var_807 = 1;
        wp::int32 var_808;
        bool var_809;
        const wp::int32 var_810 = 2;
        wp::int32 var_811;
        const wp::int32 var_812 = 2;
        wp::int32 var_813;
        bool var_814;
        const wp::int32 var_815 = 0;
        const wp::int32 var_816 = 1;
        wp::int32 var_817;
        const wp::int32 var_818 = 0;
        wp::float64 var_819;
        wp::float64 var_820;
        wp::vec_t<3, wp::float64> var_821;
        wp::float64 var_822;
        wp::vec_t<3, wp::float64> var_823;
        const wp::int32 var_824 = 0;
        wp::int32 var_825;
        const wp::int32 var_826 = 1;
        wp::int32 var_827;
        wp::int32 var_828;
        const wp::int32 var_829 = 1;
        wp::int32 var_830;
        wp::int32 var_831;
        const wp::int32 var_832 = 2;
        wp::int32 var_833;
        wp::int32 var_834;
        const wp::int32 var_835 = 2;
        wp::int32 var_836;
        wp::int32 var_837;
        const wp::int32 var_838 = 0;
        wp::float64 var_839;
        wp::float64 var_840;
        const wp::int32 var_841 = 1;
        wp::float64 var_842;
        wp::float64 var_843;
        const wp::int32 var_844 = 2;
        wp::float64 var_845;
        wp::float64 var_846;
        wp::float64 var_847;
        wp::float64 var_848;
        const wp::int32 var_849 = 0;
        wp::float64 var_850;
        wp::float64 var_851;
        wp::float64 var_852;
        wp::float64 var_853;
        const wp::int32 var_854 = 1;
        wp::float64 var_855;
        wp::float64 var_856;
        wp::float64 var_857;
        wp::float64 var_858;
        wp::float64 var_859;
        const wp::int32 var_860 = 2;
        wp::float64 var_861;
        wp::float64 var_862;
        wp::float64 var_863;
        wp::vec_t<3, wp::float64> var_864;
        wp::vec_t<3, wp::float64> var_865;
        const wp::int32 var_866 = 0;
        wp::int32 var_867;
        wp::float64 var_868;
        const wp::int32 var_869 = 1;
        wp::int32 var_870;
        wp::float64 var_871;
        const wp::int32 var_872 = 2;
        wp::int32 var_873;
        wp::float64 var_874;
        wp::vec_t<3, wp::float64> var_875;
        wp::vec_t<3, wp::float64> var_876;
        wp::vec_t<3, wp::float64>* var_877;
        wp::vec_t<3, wp::float64> var_878;
        wp::vec_t<3, wp::float64> var_879;
        wp::float64 var_880;
        wp::float64 var_881;
        wp::float64 var_882;
        const wp::int32 var_883 = 2;
        const wp::int32 var_884 = 9;
        wp::int32 var_885;
        const wp::int32 var_886 = 3;
        wp::int32 var_887;
        wp::int32 var_888;
        wp::int32 var_889;
        wp::vec_t<3, wp::int32> var_890;
        wp::vec_t<3, wp::int32> var_891;
        wp::vec_t<3, wp::int32> var_892;
        bool var_893;
        const wp::int32 var_894 = 0;
        wp::int32 var_895;
        const wp::int32 var_896 = 0;
        bool var_897;
        const wp::int32 var_898 = 1;
        wp::int32 var_899;
        const wp::int32 var_900 = 0;
        bool var_901;
        const wp::int32 var_902 = 2;
        wp::int32 var_903;
        const wp::int32 var_904 = 0;
        bool var_905;
        const wp::int32 var_906 = 0;
        wp::int32 var_907;
        const wp::int32 var_908 = 0;
        wp::int32 var_909;
        bool var_910;
        const wp::int32 var_911 = 1;
        wp::int32 var_912;
        const wp::int32 var_913 = 1;
        wp::int32 var_914;
        bool var_915;
        const wp::int32 var_916 = 2;
        wp::int32 var_917;
        const wp::int32 var_918 = 2;
        wp::int32 var_919;
        bool var_920;
        const wp::int32 var_921 = 0;
        const wp::int32 var_922 = 1;
        wp::int32 var_923;
        const wp::int32 var_924 = 0;
        wp::float64 var_925;
        wp::float64 var_926;
        wp::vec_t<3, wp::float64> var_927;
        wp::float64 var_928;
        wp::vec_t<3, wp::float64> var_929;
        const wp::int32 var_930 = 0;
        wp::int32 var_931;
        const wp::int32 var_932 = 1;
        wp::int32 var_933;
        wp::int32 var_934;
        const wp::int32 var_935 = 1;
        wp::int32 var_936;
        wp::int32 var_937;
        const wp::int32 var_938 = 2;
        wp::int32 var_939;
        wp::int32 var_940;
        const wp::int32 var_941 = 2;
        wp::int32 var_942;
        wp::int32 var_943;
        const wp::int32 var_944 = 0;
        wp::float64 var_945;
        wp::float64 var_946;
        const wp::int32 var_947 = 1;
        wp::float64 var_948;
        wp::float64 var_949;
        const wp::int32 var_950 = 2;
        wp::float64 var_951;
        wp::float64 var_952;
        wp::float64 var_953;
        wp::float64 var_954;
        const wp::int32 var_955 = 0;
        wp::float64 var_956;
        wp::float64 var_957;
        wp::float64 var_958;
        wp::float64 var_959;
        const wp::int32 var_960 = 1;
        wp::float64 var_961;
        wp::float64 var_962;
        wp::float64 var_963;
        wp::float64 var_964;
        wp::float64 var_965;
        const wp::int32 var_966 = 2;
        wp::float64 var_967;
        wp::float64 var_968;
        wp::float64 var_969;
        wp::vec_t<3, wp::float64> var_970;
        wp::vec_t<3, wp::float64> var_971;
        const wp::int32 var_972 = 0;
        wp::int32 var_973;
        wp::float64 var_974;
        const wp::int32 var_975 = 1;
        wp::int32 var_976;
        wp::float64 var_977;
        const wp::int32 var_978 = 2;
        wp::int32 var_979;
        wp::float64 var_980;
        wp::vec_t<3, wp::float64> var_981;
        wp::vec_t<3, wp::float64> var_982;
        wp::vec_t<3, wp::float64>* var_983;
        wp::vec_t<3, wp::float64> var_984;
        wp::vec_t<3, wp::float64> var_985;
        wp::float64 var_986;
        wp::float64 var_987;
        wp::float64 var_988;
        const wp::int32 var_989 = 1;
        const wp::int32 var_990 = 0;
        const wp::int32 var_991 = 0;
        const wp::int32 var_992 = 9;
        wp::int32 var_993;
        const wp::int32 var_994 = 3;
        wp::int32 var_995;
        wp::int32 var_996;
        wp::int32 var_997;
        wp::vec_t<3, wp::int32> var_998;
        wp::vec_t<3, wp::int32> var_999;
        wp::vec_t<3, wp::int32> var_1000;
        bool var_1001;
        const wp::int32 var_1002 = 0;
        wp::int32 var_1003;
        const wp::int32 var_1004 = 0;
        bool var_1005;
        const wp::int32 var_1006 = 1;
        wp::int32 var_1007;
        const wp::int32 var_1008 = 0;
        bool var_1009;
        const wp::int32 var_1010 = 2;
        wp::int32 var_1011;
        const wp::int32 var_1012 = 0;
        bool var_1013;
        const wp::int32 var_1014 = 0;
        wp::int32 var_1015;
        const wp::int32 var_1016 = 0;
        wp::int32 var_1017;
        bool var_1018;
        const wp::int32 var_1019 = 1;
        wp::int32 var_1020;
        const wp::int32 var_1021 = 1;
        wp::int32 var_1022;
        bool var_1023;
        const wp::int32 var_1024 = 2;
        wp::int32 var_1025;
        const wp::int32 var_1026 = 2;
        wp::int32 var_1027;
        bool var_1028;
        const wp::int32 var_1029 = 0;
        const wp::int32 var_1030 = 1;
        wp::int32 var_1031;
        const wp::int32 var_1032 = 0;
        wp::float64 var_1033;
        wp::float64 var_1034;
        wp::vec_t<3, wp::float64> var_1035;
        wp::float64 var_1036;
        wp::vec_t<3, wp::float64> var_1037;
        const wp::int32 var_1038 = 0;
        wp::int32 var_1039;
        const wp::int32 var_1040 = 1;
        wp::int32 var_1041;
        wp::int32 var_1042;
        const wp::int32 var_1043 = 1;
        wp::int32 var_1044;
        wp::int32 var_1045;
        const wp::int32 var_1046 = 2;
        wp::int32 var_1047;
        wp::int32 var_1048;
        const wp::int32 var_1049 = 2;
        wp::int32 var_1050;
        wp::int32 var_1051;
        const wp::int32 var_1052 = 0;
        wp::float64 var_1053;
        wp::float64 var_1054;
        const wp::int32 var_1055 = 1;
        wp::float64 var_1056;
        wp::float64 var_1057;
        const wp::int32 var_1058 = 2;
        wp::float64 var_1059;
        wp::float64 var_1060;
        wp::float64 var_1061;
        wp::float64 var_1062;
        const wp::int32 var_1063 = 0;
        wp::float64 var_1064;
        wp::float64 var_1065;
        wp::float64 var_1066;
        wp::float64 var_1067;
        const wp::int32 var_1068 = 1;
        wp::float64 var_1069;
        wp::float64 var_1070;
        wp::float64 var_1071;
        wp::float64 var_1072;
        wp::float64 var_1073;
        const wp::int32 var_1074 = 2;
        wp::float64 var_1075;
        wp::float64 var_1076;
        wp::float64 var_1077;
        wp::vec_t<3, wp::float64> var_1078;
        wp::vec_t<3, wp::float64> var_1079;
        const wp::int32 var_1080 = 0;
        wp::int32 var_1081;
        wp::float64 var_1082;
        const wp::int32 var_1083 = 1;
        wp::int32 var_1084;
        wp::float64 var_1085;
        const wp::int32 var_1086 = 2;
        wp::int32 var_1087;
        wp::float64 var_1088;
        wp::vec_t<3, wp::float64> var_1089;
        wp::vec_t<3, wp::float64> var_1090;
        wp::vec_t<3, wp::float64>* var_1091;
        wp::vec_t<3, wp::float64> var_1092;
        wp::vec_t<3, wp::float64> var_1093;
        wp::float64 var_1094;
        wp::float64 var_1095;
        wp::float64 var_1096;
        const wp::int32 var_1097 = 1;
        const wp::int32 var_1098 = 9;
        wp::int32 var_1099;
        const wp::int32 var_1100 = 3;
        wp::int32 var_1101;
        wp::int32 var_1102;
        wp::int32 var_1103;
        wp::vec_t<3, wp::int32> var_1104;
        wp::vec_t<3, wp::int32> var_1105;
        wp::vec_t<3, wp::int32> var_1106;
        bool var_1107;
        const wp::int32 var_1108 = 0;
        wp::int32 var_1109;
        const wp::int32 var_1110 = 0;
        bool var_1111;
        const wp::int32 var_1112 = 1;
        wp::int32 var_1113;
        const wp::int32 var_1114 = 0;
        bool var_1115;
        const wp::int32 var_1116 = 2;
        wp::int32 var_1117;
        const wp::int32 var_1118 = 0;
        bool var_1119;
        const wp::int32 var_1120 = 0;
        wp::int32 var_1121;
        const wp::int32 var_1122 = 0;
        wp::int32 var_1123;
        bool var_1124;
        const wp::int32 var_1125 = 1;
        wp::int32 var_1126;
        const wp::int32 var_1127 = 1;
        wp::int32 var_1128;
        bool var_1129;
        const wp::int32 var_1130 = 2;
        wp::int32 var_1131;
        const wp::int32 var_1132 = 2;
        wp::int32 var_1133;
        bool var_1134;
        const wp::int32 var_1135 = 0;
        const wp::int32 var_1136 = 1;
        wp::int32 var_1137;
        const wp::int32 var_1138 = 0;
        wp::float64 var_1139;
        wp::float64 var_1140;
        wp::vec_t<3, wp::float64> var_1141;
        wp::float64 var_1142;
        wp::vec_t<3, wp::float64> var_1143;
        const wp::int32 var_1144 = 0;
        wp::int32 var_1145;
        const wp::int32 var_1146 = 1;
        wp::int32 var_1147;
        wp::int32 var_1148;
        const wp::int32 var_1149 = 1;
        wp::int32 var_1150;
        wp::int32 var_1151;
        const wp::int32 var_1152 = 2;
        wp::int32 var_1153;
        wp::int32 var_1154;
        const wp::int32 var_1155 = 2;
        wp::int32 var_1156;
        wp::int32 var_1157;
        const wp::int32 var_1158 = 0;
        wp::float64 var_1159;
        wp::float64 var_1160;
        const wp::int32 var_1161 = 1;
        wp::float64 var_1162;
        wp::float64 var_1163;
        const wp::int32 var_1164 = 2;
        wp::float64 var_1165;
        wp::float64 var_1166;
        wp::float64 var_1167;
        wp::float64 var_1168;
        const wp::int32 var_1169 = 0;
        wp::float64 var_1170;
        wp::float64 var_1171;
        wp::float64 var_1172;
        wp::float64 var_1173;
        const wp::int32 var_1174 = 1;
        wp::float64 var_1175;
        wp::float64 var_1176;
        wp::float64 var_1177;
        wp::float64 var_1178;
        wp::float64 var_1179;
        const wp::int32 var_1180 = 2;
        wp::float64 var_1181;
        wp::float64 var_1182;
        wp::float64 var_1183;
        wp::vec_t<3, wp::float64> var_1184;
        wp::vec_t<3, wp::float64> var_1185;
        const wp::int32 var_1186 = 0;
        wp::int32 var_1187;
        wp::float64 var_1188;
        const wp::int32 var_1189 = 1;
        wp::int32 var_1190;
        wp::float64 var_1191;
        const wp::int32 var_1192 = 2;
        wp::int32 var_1193;
        wp::float64 var_1194;
        wp::vec_t<3, wp::float64> var_1195;
        wp::vec_t<3, wp::float64> var_1196;
        wp::vec_t<3, wp::float64>* var_1197;
        wp::vec_t<3, wp::float64> var_1198;
        wp::vec_t<3, wp::float64> var_1199;
        wp::float64 var_1200;
        wp::float64 var_1201;
        wp::float64 var_1202;
        const wp::int32 var_1203 = 2;
        const wp::int32 var_1204 = 9;
        wp::int32 var_1205;
        const wp::int32 var_1206 = 3;
        wp::int32 var_1207;
        wp::int32 var_1208;
        wp::int32 var_1209;
        wp::vec_t<3, wp::int32> var_1210;
        wp::vec_t<3, wp::int32> var_1211;
        wp::vec_t<3, wp::int32> var_1212;
        bool var_1213;
        const wp::int32 var_1214 = 0;
        wp::int32 var_1215;
        const wp::int32 var_1216 = 0;
        bool var_1217;
        const wp::int32 var_1218 = 1;
        wp::int32 var_1219;
        const wp::int32 var_1220 = 0;
        bool var_1221;
        const wp::int32 var_1222 = 2;
        wp::int32 var_1223;
        const wp::int32 var_1224 = 0;
        bool var_1225;
        const wp::int32 var_1226 = 0;
        wp::int32 var_1227;
        const wp::int32 var_1228 = 0;
        wp::int32 var_1229;
        bool var_1230;
        const wp::int32 var_1231 = 1;
        wp::int32 var_1232;
        const wp::int32 var_1233 = 1;
        wp::int32 var_1234;
        bool var_1235;
        const wp::int32 var_1236 = 2;
        wp::int32 var_1237;
        const wp::int32 var_1238 = 2;
        wp::int32 var_1239;
        bool var_1240;
        const wp::int32 var_1241 = 0;
        const wp::int32 var_1242 = 1;
        wp::int32 var_1243;
        const wp::int32 var_1244 = 0;
        wp::float64 var_1245;
        wp::float64 var_1246;
        wp::vec_t<3, wp::float64> var_1247;
        wp::float64 var_1248;
        wp::vec_t<3, wp::float64> var_1249;
        const wp::int32 var_1250 = 0;
        wp::int32 var_1251;
        const wp::int32 var_1252 = 1;
        wp::int32 var_1253;
        wp::int32 var_1254;
        const wp::int32 var_1255 = 1;
        wp::int32 var_1256;
        wp::int32 var_1257;
        const wp::int32 var_1258 = 2;
        wp::int32 var_1259;
        wp::int32 var_1260;
        const wp::int32 var_1261 = 2;
        wp::int32 var_1262;
        wp::int32 var_1263;
        const wp::int32 var_1264 = 0;
        wp::float64 var_1265;
        wp::float64 var_1266;
        const wp::int32 var_1267 = 1;
        wp::float64 var_1268;
        wp::float64 var_1269;
        const wp::int32 var_1270 = 2;
        wp::float64 var_1271;
        wp::float64 var_1272;
        wp::float64 var_1273;
        wp::float64 var_1274;
        const wp::int32 var_1275 = 0;
        wp::float64 var_1276;
        wp::float64 var_1277;
        wp::float64 var_1278;
        wp::float64 var_1279;
        const wp::int32 var_1280 = 1;
        wp::float64 var_1281;
        wp::float64 var_1282;
        wp::float64 var_1283;
        wp::float64 var_1284;
        wp::float64 var_1285;
        const wp::int32 var_1286 = 2;
        wp::float64 var_1287;
        wp::float64 var_1288;
        wp::float64 var_1289;
        wp::vec_t<3, wp::float64> var_1290;
        wp::vec_t<3, wp::float64> var_1291;
        const wp::int32 var_1292 = 0;
        wp::int32 var_1293;
        wp::float64 var_1294;
        const wp::int32 var_1295 = 1;
        wp::int32 var_1296;
        wp::float64 var_1297;
        const wp::int32 var_1298 = 2;
        wp::int32 var_1299;
        wp::float64 var_1300;
        wp::vec_t<3, wp::float64> var_1301;
        wp::vec_t<3, wp::float64> var_1302;
        wp::vec_t<3, wp::float64>* var_1303;
        wp::vec_t<3, wp::float64> var_1304;
        wp::vec_t<3, wp::float64> var_1305;
        wp::float64 var_1306;
        wp::float64 var_1307;
        wp::float64 var_1308;
        const wp::int32 var_1309 = 1;
        const wp::int32 var_1310 = 0;
        const wp::int32 var_1311 = 9;
        wp::int32 var_1312;
        const wp::int32 var_1313 = 3;
        wp::int32 var_1314;
        wp::int32 var_1315;
        wp::int32 var_1316;
        wp::vec_t<3, wp::int32> var_1317;
        wp::vec_t<3, wp::int32> var_1318;
        wp::vec_t<3, wp::int32> var_1319;
        bool var_1320;
        const wp::int32 var_1321 = 0;
        wp::int32 var_1322;
        const wp::int32 var_1323 = 0;
        bool var_1324;
        const wp::int32 var_1325 = 1;
        wp::int32 var_1326;
        const wp::int32 var_1327 = 0;
        bool var_1328;
        const wp::int32 var_1329 = 2;
        wp::int32 var_1330;
        const wp::int32 var_1331 = 0;
        bool var_1332;
        const wp::int32 var_1333 = 0;
        wp::int32 var_1334;
        const wp::int32 var_1335 = 0;
        wp::int32 var_1336;
        bool var_1337;
        const wp::int32 var_1338 = 1;
        wp::int32 var_1339;
        const wp::int32 var_1340 = 1;
        wp::int32 var_1341;
        bool var_1342;
        const wp::int32 var_1343 = 2;
        wp::int32 var_1344;
        const wp::int32 var_1345 = 2;
        wp::int32 var_1346;
        bool var_1347;
        const wp::int32 var_1348 = 0;
        const wp::int32 var_1349 = 1;
        wp::int32 var_1350;
        const wp::int32 var_1351 = 0;
        wp::float64 var_1352;
        wp::float64 var_1353;
        wp::vec_t<3, wp::float64> var_1354;
        wp::float64 var_1355;
        wp::vec_t<3, wp::float64> var_1356;
        const wp::int32 var_1357 = 0;
        wp::int32 var_1358;
        const wp::int32 var_1359 = 1;
        wp::int32 var_1360;
        wp::int32 var_1361;
        const wp::int32 var_1362 = 1;
        wp::int32 var_1363;
        wp::int32 var_1364;
        const wp::int32 var_1365 = 2;
        wp::int32 var_1366;
        wp::int32 var_1367;
        const wp::int32 var_1368 = 2;
        wp::int32 var_1369;
        wp::int32 var_1370;
        const wp::int32 var_1371 = 0;
        wp::float64 var_1372;
        wp::float64 var_1373;
        const wp::int32 var_1374 = 1;
        wp::float64 var_1375;
        wp::float64 var_1376;
        const wp::int32 var_1377 = 2;
        wp::float64 var_1378;
        wp::float64 var_1379;
        wp::float64 var_1380;
        wp::float64 var_1381;
        const wp::int32 var_1382 = 0;
        wp::float64 var_1383;
        wp::float64 var_1384;
        wp::float64 var_1385;
        wp::float64 var_1386;
        const wp::int32 var_1387 = 1;
        wp::float64 var_1388;
        wp::float64 var_1389;
        wp::float64 var_1390;
        wp::float64 var_1391;
        wp::float64 var_1392;
        const wp::int32 var_1393 = 2;
        wp::float64 var_1394;
        wp::float64 var_1395;
        wp::float64 var_1396;
        wp::vec_t<3, wp::float64> var_1397;
        wp::vec_t<3, wp::float64> var_1398;
        const wp::int32 var_1399 = 0;
        wp::int32 var_1400;
        wp::float64 var_1401;
        const wp::int32 var_1402 = 1;
        wp::int32 var_1403;
        wp::float64 var_1404;
        const wp::int32 var_1405 = 2;
        wp::int32 var_1406;
        wp::float64 var_1407;
        wp::vec_t<3, wp::float64> var_1408;
        wp::vec_t<3, wp::float64> var_1409;
        wp::vec_t<3, wp::float64>* var_1410;
        wp::vec_t<3, wp::float64> var_1411;
        wp::vec_t<3, wp::float64> var_1412;
        wp::float64 var_1413;
        wp::float64 var_1414;
        wp::float64 var_1415;
        const wp::int32 var_1416 = 1;
        const wp::int32 var_1417 = 9;
        wp::int32 var_1418;
        const wp::int32 var_1419 = 3;
        wp::int32 var_1420;
        wp::int32 var_1421;
        wp::int32 var_1422;
        wp::vec_t<3, wp::int32> var_1423;
        wp::vec_t<3, wp::int32> var_1424;
        wp::vec_t<3, wp::int32> var_1425;
        bool var_1426;
        const wp::int32 var_1427 = 0;
        wp::int32 var_1428;
        const wp::int32 var_1429 = 0;
        bool var_1430;
        const wp::int32 var_1431 = 1;
        wp::int32 var_1432;
        const wp::int32 var_1433 = 0;
        bool var_1434;
        const wp::int32 var_1435 = 2;
        wp::int32 var_1436;
        const wp::int32 var_1437 = 0;
        bool var_1438;
        const wp::int32 var_1439 = 0;
        wp::int32 var_1440;
        const wp::int32 var_1441 = 0;
        wp::int32 var_1442;
        bool var_1443;
        const wp::int32 var_1444 = 1;
        wp::int32 var_1445;
        const wp::int32 var_1446 = 1;
        wp::int32 var_1447;
        bool var_1448;
        const wp::int32 var_1449 = 2;
        wp::int32 var_1450;
        const wp::int32 var_1451 = 2;
        wp::int32 var_1452;
        bool var_1453;
        const wp::int32 var_1454 = 0;
        const wp::int32 var_1455 = 1;
        wp::int32 var_1456;
        const wp::int32 var_1457 = 0;
        wp::float64 var_1458;
        wp::float64 var_1459;
        wp::vec_t<3, wp::float64> var_1460;
        wp::float64 var_1461;
        wp::vec_t<3, wp::float64> var_1462;
        const wp::int32 var_1463 = 0;
        wp::int32 var_1464;
        const wp::int32 var_1465 = 1;
        wp::int32 var_1466;
        wp::int32 var_1467;
        const wp::int32 var_1468 = 1;
        wp::int32 var_1469;
        wp::int32 var_1470;
        const wp::int32 var_1471 = 2;
        wp::int32 var_1472;
        wp::int32 var_1473;
        const wp::int32 var_1474 = 2;
        wp::int32 var_1475;
        wp::int32 var_1476;
        const wp::int32 var_1477 = 0;
        wp::float64 var_1478;
        wp::float64 var_1479;
        const wp::int32 var_1480 = 1;
        wp::float64 var_1481;
        wp::float64 var_1482;
        const wp::int32 var_1483 = 2;
        wp::float64 var_1484;
        wp::float64 var_1485;
        wp::float64 var_1486;
        wp::float64 var_1487;
        const wp::int32 var_1488 = 0;
        wp::float64 var_1489;
        wp::float64 var_1490;
        wp::float64 var_1491;
        wp::float64 var_1492;
        const wp::int32 var_1493 = 1;
        wp::float64 var_1494;
        wp::float64 var_1495;
        wp::float64 var_1496;
        wp::float64 var_1497;
        wp::float64 var_1498;
        const wp::int32 var_1499 = 2;
        wp::float64 var_1500;
        wp::float64 var_1501;
        wp::float64 var_1502;
        wp::vec_t<3, wp::float64> var_1503;
        wp::vec_t<3, wp::float64> var_1504;
        const wp::int32 var_1505 = 0;
        wp::int32 var_1506;
        wp::float64 var_1507;
        const wp::int32 var_1508 = 1;
        wp::int32 var_1509;
        wp::float64 var_1510;
        const wp::int32 var_1511 = 2;
        wp::int32 var_1512;
        wp::float64 var_1513;
        wp::vec_t<3, wp::float64> var_1514;
        wp::vec_t<3, wp::float64> var_1515;
        wp::vec_t<3, wp::float64>* var_1516;
        wp::vec_t<3, wp::float64> var_1517;
        wp::vec_t<3, wp::float64> var_1518;
        wp::float64 var_1519;
        wp::float64 var_1520;
        wp::float64 var_1521;
        const wp::int32 var_1522 = 2;
        const wp::int32 var_1523 = 9;
        wp::int32 var_1524;
        const wp::int32 var_1525 = 3;
        wp::int32 var_1526;
        wp::int32 var_1527;
        wp::int32 var_1528;
        wp::vec_t<3, wp::int32> var_1529;
        wp::vec_t<3, wp::int32> var_1530;
        wp::vec_t<3, wp::int32> var_1531;
        bool var_1532;
        const wp::int32 var_1533 = 0;
        wp::int32 var_1534;
        const wp::int32 var_1535 = 0;
        bool var_1536;
        const wp::int32 var_1537 = 1;
        wp::int32 var_1538;
        const wp::int32 var_1539 = 0;
        bool var_1540;
        const wp::int32 var_1541 = 2;
        wp::int32 var_1542;
        const wp::int32 var_1543 = 0;
        bool var_1544;
        const wp::int32 var_1545 = 0;
        wp::int32 var_1546;
        const wp::int32 var_1547 = 0;
        wp::int32 var_1548;
        bool var_1549;
        const wp::int32 var_1550 = 1;
        wp::int32 var_1551;
        const wp::int32 var_1552 = 1;
        wp::int32 var_1553;
        bool var_1554;
        const wp::int32 var_1555 = 2;
        wp::int32 var_1556;
        const wp::int32 var_1557 = 2;
        wp::int32 var_1558;
        bool var_1559;
        const wp::int32 var_1560 = 0;
        const wp::int32 var_1561 = 1;
        wp::int32 var_1562;
        const wp::int32 var_1563 = 0;
        wp::float64 var_1564;
        wp::float64 var_1565;
        wp::vec_t<3, wp::float64> var_1566;
        wp::float64 var_1567;
        wp::vec_t<3, wp::float64> var_1568;
        const wp::int32 var_1569 = 0;
        wp::int32 var_1570;
        const wp::int32 var_1571 = 1;
        wp::int32 var_1572;
        wp::int32 var_1573;
        const wp::int32 var_1574 = 1;
        wp::int32 var_1575;
        wp::int32 var_1576;
        const wp::int32 var_1577 = 2;
        wp::int32 var_1578;
        wp::int32 var_1579;
        const wp::int32 var_1580 = 2;
        wp::int32 var_1581;
        wp::int32 var_1582;
        const wp::int32 var_1583 = 0;
        wp::float64 var_1584;
        wp::float64 var_1585;
        const wp::int32 var_1586 = 1;
        wp::float64 var_1587;
        wp::float64 var_1588;
        const wp::int32 var_1589 = 2;
        wp::float64 var_1590;
        wp::float64 var_1591;
        wp::float64 var_1592;
        wp::float64 var_1593;
        const wp::int32 var_1594 = 0;
        wp::float64 var_1595;
        wp::float64 var_1596;
        wp::float64 var_1597;
        wp::float64 var_1598;
        const wp::int32 var_1599 = 1;
        wp::float64 var_1600;
        wp::float64 var_1601;
        wp::float64 var_1602;
        wp::float64 var_1603;
        wp::float64 var_1604;
        const wp::int32 var_1605 = 2;
        wp::float64 var_1606;
        wp::float64 var_1607;
        wp::float64 var_1608;
        wp::vec_t<3, wp::float64> var_1609;
        wp::vec_t<3, wp::float64> var_1610;
        const wp::int32 var_1611 = 0;
        wp::int32 var_1612;
        wp::float64 var_1613;
        const wp::int32 var_1614 = 1;
        wp::int32 var_1615;
        wp::float64 var_1616;
        const wp::int32 var_1617 = 2;
        wp::int32 var_1618;
        wp::float64 var_1619;
        wp::vec_t<3, wp::float64> var_1620;
        wp::vec_t<3, wp::float64> var_1621;
        wp::vec_t<3, wp::float64>* var_1622;
        wp::vec_t<3, wp::float64> var_1623;
        wp::vec_t<3, wp::float64> var_1624;
        wp::float64 var_1625;
        wp::float64 var_1626;
        wp::float64 var_1627;
        const wp::int32 var_1628 = 2;
        const wp::int32 var_1629 = 0;
        const wp::int32 var_1630 = 9;
        wp::int32 var_1631;
        const wp::int32 var_1632 = 3;
        wp::int32 var_1633;
        wp::int32 var_1634;
        wp::int32 var_1635;
        wp::vec_t<3, wp::int32> var_1636;
        wp::vec_t<3, wp::int32> var_1637;
        wp::vec_t<3, wp::int32> var_1638;
        bool var_1639;
        const wp::int32 var_1640 = 0;
        wp::int32 var_1641;
        const wp::int32 var_1642 = 0;
        bool var_1643;
        const wp::int32 var_1644 = 1;
        wp::int32 var_1645;
        const wp::int32 var_1646 = 0;
        bool var_1647;
        const wp::int32 var_1648 = 2;
        wp::int32 var_1649;
        const wp::int32 var_1650 = 0;
        bool var_1651;
        const wp::int32 var_1652 = 0;
        wp::int32 var_1653;
        const wp::int32 var_1654 = 0;
        wp::int32 var_1655;
        bool var_1656;
        const wp::int32 var_1657 = 1;
        wp::int32 var_1658;
        const wp::int32 var_1659 = 1;
        wp::int32 var_1660;
        bool var_1661;
        const wp::int32 var_1662 = 2;
        wp::int32 var_1663;
        const wp::int32 var_1664 = 2;
        wp::int32 var_1665;
        bool var_1666;
        const wp::int32 var_1667 = 0;
        const wp::int32 var_1668 = 1;
        wp::int32 var_1669;
        const wp::int32 var_1670 = 0;
        wp::float64 var_1671;
        wp::float64 var_1672;
        wp::vec_t<3, wp::float64> var_1673;
        wp::float64 var_1674;
        wp::vec_t<3, wp::float64> var_1675;
        const wp::int32 var_1676 = 0;
        wp::int32 var_1677;
        const wp::int32 var_1678 = 1;
        wp::int32 var_1679;
        wp::int32 var_1680;
        const wp::int32 var_1681 = 1;
        wp::int32 var_1682;
        wp::int32 var_1683;
        const wp::int32 var_1684 = 2;
        wp::int32 var_1685;
        wp::int32 var_1686;
        const wp::int32 var_1687 = 2;
        wp::int32 var_1688;
        wp::int32 var_1689;
        const wp::int32 var_1690 = 0;
        wp::float64 var_1691;
        wp::float64 var_1692;
        const wp::int32 var_1693 = 1;
        wp::float64 var_1694;
        wp::float64 var_1695;
        const wp::int32 var_1696 = 2;
        wp::float64 var_1697;
        wp::float64 var_1698;
        wp::float64 var_1699;
        wp::float64 var_1700;
        const wp::int32 var_1701 = 0;
        wp::float64 var_1702;
        wp::float64 var_1703;
        wp::float64 var_1704;
        wp::float64 var_1705;
        const wp::int32 var_1706 = 1;
        wp::float64 var_1707;
        wp::float64 var_1708;
        wp::float64 var_1709;
        wp::float64 var_1710;
        wp::float64 var_1711;
        const wp::int32 var_1712 = 2;
        wp::float64 var_1713;
        wp::float64 var_1714;
        wp::float64 var_1715;
        wp::vec_t<3, wp::float64> var_1716;
        wp::vec_t<3, wp::float64> var_1717;
        const wp::int32 var_1718 = 0;
        wp::int32 var_1719;
        wp::float64 var_1720;
        const wp::int32 var_1721 = 1;
        wp::int32 var_1722;
        wp::float64 var_1723;
        const wp::int32 var_1724 = 2;
        wp::int32 var_1725;
        wp::float64 var_1726;
        wp::vec_t<3, wp::float64> var_1727;
        wp::vec_t<3, wp::float64> var_1728;
        wp::vec_t<3, wp::float64>* var_1729;
        wp::vec_t<3, wp::float64> var_1730;
        wp::vec_t<3, wp::float64> var_1731;
        wp::float64 var_1732;
        wp::float64 var_1733;
        wp::float64 var_1734;
        const wp::int32 var_1735 = 1;
        const wp::int32 var_1736 = 9;
        wp::int32 var_1737;
        const wp::int32 var_1738 = 3;
        wp::int32 var_1739;
        wp::int32 var_1740;
        wp::int32 var_1741;
        wp::vec_t<3, wp::int32> var_1742;
        wp::vec_t<3, wp::int32> var_1743;
        wp::vec_t<3, wp::int32> var_1744;
        bool var_1745;
        const wp::int32 var_1746 = 0;
        wp::int32 var_1747;
        const wp::int32 var_1748 = 0;
        bool var_1749;
        const wp::int32 var_1750 = 1;
        wp::int32 var_1751;
        const wp::int32 var_1752 = 0;
        bool var_1753;
        const wp::int32 var_1754 = 2;
        wp::int32 var_1755;
        const wp::int32 var_1756 = 0;
        bool var_1757;
        const wp::int32 var_1758 = 0;
        wp::int32 var_1759;
        const wp::int32 var_1760 = 0;
        wp::int32 var_1761;
        bool var_1762;
        const wp::int32 var_1763 = 1;
        wp::int32 var_1764;
        const wp::int32 var_1765 = 1;
        wp::int32 var_1766;
        bool var_1767;
        const wp::int32 var_1768 = 2;
        wp::int32 var_1769;
        const wp::int32 var_1770 = 2;
        wp::int32 var_1771;
        bool var_1772;
        const wp::int32 var_1773 = 0;
        const wp::int32 var_1774 = 1;
        wp::int32 var_1775;
        const wp::int32 var_1776 = 0;
        wp::float64 var_1777;
        wp::float64 var_1778;
        wp::vec_t<3, wp::float64> var_1779;
        wp::float64 var_1780;
        wp::vec_t<3, wp::float64> var_1781;
        const wp::int32 var_1782 = 0;
        wp::int32 var_1783;
        const wp::int32 var_1784 = 1;
        wp::int32 var_1785;
        wp::int32 var_1786;
        const wp::int32 var_1787 = 1;
        wp::int32 var_1788;
        wp::int32 var_1789;
        const wp::int32 var_1790 = 2;
        wp::int32 var_1791;
        wp::int32 var_1792;
        const wp::int32 var_1793 = 2;
        wp::int32 var_1794;
        wp::int32 var_1795;
        const wp::int32 var_1796 = 0;
        wp::float64 var_1797;
        wp::float64 var_1798;
        const wp::int32 var_1799 = 1;
        wp::float64 var_1800;
        wp::float64 var_1801;
        const wp::int32 var_1802 = 2;
        wp::float64 var_1803;
        wp::float64 var_1804;
        wp::float64 var_1805;
        wp::float64 var_1806;
        const wp::int32 var_1807 = 0;
        wp::float64 var_1808;
        wp::float64 var_1809;
        wp::float64 var_1810;
        wp::float64 var_1811;
        const wp::int32 var_1812 = 1;
        wp::float64 var_1813;
        wp::float64 var_1814;
        wp::float64 var_1815;
        wp::float64 var_1816;
        wp::float64 var_1817;
        const wp::int32 var_1818 = 2;
        wp::float64 var_1819;
        wp::float64 var_1820;
        wp::float64 var_1821;
        wp::vec_t<3, wp::float64> var_1822;
        wp::vec_t<3, wp::float64> var_1823;
        const wp::int32 var_1824 = 0;
        wp::int32 var_1825;
        wp::float64 var_1826;
        const wp::int32 var_1827 = 1;
        wp::int32 var_1828;
        wp::float64 var_1829;
        const wp::int32 var_1830 = 2;
        wp::int32 var_1831;
        wp::float64 var_1832;
        wp::vec_t<3, wp::float64> var_1833;
        wp::vec_t<3, wp::float64> var_1834;
        wp::vec_t<3, wp::float64>* var_1835;
        wp::vec_t<3, wp::float64> var_1836;
        wp::vec_t<3, wp::float64> var_1837;
        wp::float64 var_1838;
        wp::float64 var_1839;
        wp::float64 var_1840;
        const wp::int32 var_1841 = 2;
        const wp::int32 var_1842 = 9;
        wp::int32 var_1843;
        const wp::int32 var_1844 = 3;
        wp::int32 var_1845;
        wp::int32 var_1846;
        wp::int32 var_1847;
        wp::vec_t<3, wp::int32> var_1848;
        wp::vec_t<3, wp::int32> var_1849;
        wp::vec_t<3, wp::int32> var_1850;
        bool var_1851;
        const wp::int32 var_1852 = 0;
        wp::int32 var_1853;
        const wp::int32 var_1854 = 0;
        bool var_1855;
        const wp::int32 var_1856 = 1;
        wp::int32 var_1857;
        const wp::int32 var_1858 = 0;
        bool var_1859;
        const wp::int32 var_1860 = 2;
        wp::int32 var_1861;
        const wp::int32 var_1862 = 0;
        bool var_1863;
        const wp::int32 var_1864 = 0;
        wp::int32 var_1865;
        const wp::int32 var_1866 = 0;
        wp::int32 var_1867;
        bool var_1868;
        const wp::int32 var_1869 = 1;
        wp::int32 var_1870;
        const wp::int32 var_1871 = 1;
        wp::int32 var_1872;
        bool var_1873;
        const wp::int32 var_1874 = 2;
        wp::int32 var_1875;
        const wp::int32 var_1876 = 2;
        wp::int32 var_1877;
        bool var_1878;
        const wp::int32 var_1879 = 0;
        const wp::int32 var_1880 = 1;
        wp::int32 var_1881;
        const wp::int32 var_1882 = 0;
        wp::float64 var_1883;
        wp::float64 var_1884;
        wp::vec_t<3, wp::float64> var_1885;
        wp::float64 var_1886;
        wp::vec_t<3, wp::float64> var_1887;
        const wp::int32 var_1888 = 0;
        wp::int32 var_1889;
        const wp::int32 var_1890 = 1;
        wp::int32 var_1891;
        wp::int32 var_1892;
        const wp::int32 var_1893 = 1;
        wp::int32 var_1894;
        wp::int32 var_1895;
        const wp::int32 var_1896 = 2;
        wp::int32 var_1897;
        wp::int32 var_1898;
        const wp::int32 var_1899 = 2;
        wp::int32 var_1900;
        wp::int32 var_1901;
        const wp::int32 var_1902 = 0;
        wp::float64 var_1903;
        wp::float64 var_1904;
        const wp::int32 var_1905 = 1;
        wp::float64 var_1906;
        wp::float64 var_1907;
        const wp::int32 var_1908 = 2;
        wp::float64 var_1909;
        wp::float64 var_1910;
        wp::float64 var_1911;
        wp::float64 var_1912;
        const wp::int32 var_1913 = 0;
        wp::float64 var_1914;
        wp::float64 var_1915;
        wp::float64 var_1916;
        wp::float64 var_1917;
        const wp::int32 var_1918 = 1;
        wp::float64 var_1919;
        wp::float64 var_1920;
        wp::float64 var_1921;
        wp::float64 var_1922;
        wp::float64 var_1923;
        const wp::int32 var_1924 = 2;
        wp::float64 var_1925;
        wp::float64 var_1926;
        wp::float64 var_1927;
        wp::vec_t<3, wp::float64> var_1928;
        wp::vec_t<3, wp::float64> var_1929;
        const wp::int32 var_1930 = 0;
        wp::int32 var_1931;
        wp::float64 var_1932;
        const wp::int32 var_1933 = 1;
        wp::int32 var_1934;
        wp::float64 var_1935;
        const wp::int32 var_1936 = 2;
        wp::int32 var_1937;
        wp::float64 var_1938;
        wp::vec_t<3, wp::float64> var_1939;
        wp::vec_t<3, wp::float64> var_1940;
        wp::vec_t<3, wp::float64>* var_1941;
        wp::vec_t<3, wp::float64> var_1942;
        wp::vec_t<3, wp::float64> var_1943;
        wp::float64 var_1944;
        wp::float64 var_1945;
        wp::float64 var_1946;
        const wp::int32 var_1947 = 2;
        const wp::int32 var_1948 = 0;
        const wp::int32 var_1949 = 0;
        const wp::int32 var_1950 = 9;
        wp::int32 var_1951;
        const wp::int32 var_1952 = 3;
        wp::int32 var_1953;
        wp::int32 var_1954;
        wp::int32 var_1955;
        wp::vec_t<3, wp::int32> var_1956;
        wp::vec_t<3, wp::int32> var_1957;
        wp::vec_t<3, wp::int32> var_1958;
        bool var_1959;
        const wp::int32 var_1960 = 0;
        wp::int32 var_1961;
        const wp::int32 var_1962 = 0;
        bool var_1963;
        const wp::int32 var_1964 = 1;
        wp::int32 var_1965;
        const wp::int32 var_1966 = 0;
        bool var_1967;
        const wp::int32 var_1968 = 2;
        wp::int32 var_1969;
        const wp::int32 var_1970 = 0;
        bool var_1971;
        const wp::int32 var_1972 = 0;
        wp::int32 var_1973;
        const wp::int32 var_1974 = 0;
        wp::int32 var_1975;
        bool var_1976;
        const wp::int32 var_1977 = 1;
        wp::int32 var_1978;
        const wp::int32 var_1979 = 1;
        wp::int32 var_1980;
        bool var_1981;
        const wp::int32 var_1982 = 2;
        wp::int32 var_1983;
        const wp::int32 var_1984 = 2;
        wp::int32 var_1985;
        bool var_1986;
        const wp::int32 var_1987 = 0;
        const wp::int32 var_1988 = 1;
        wp::int32 var_1989;
        const wp::int32 var_1990 = 0;
        wp::float64 var_1991;
        wp::float64 var_1992;
        wp::vec_t<3, wp::float64> var_1993;
        wp::float64 var_1994;
        wp::vec_t<3, wp::float64> var_1995;
        const wp::int32 var_1996 = 0;
        wp::int32 var_1997;
        const wp::int32 var_1998 = 1;
        wp::int32 var_1999;
        wp::int32 var_2000;
        const wp::int32 var_2001 = 1;
        wp::int32 var_2002;
        wp::int32 var_2003;
        const wp::int32 var_2004 = 2;
        wp::int32 var_2005;
        wp::int32 var_2006;
        const wp::int32 var_2007 = 2;
        wp::int32 var_2008;
        wp::int32 var_2009;
        const wp::int32 var_2010 = 0;
        wp::float64 var_2011;
        wp::float64 var_2012;
        const wp::int32 var_2013 = 1;
        wp::float64 var_2014;
        wp::float64 var_2015;
        const wp::int32 var_2016 = 2;
        wp::float64 var_2017;
        wp::float64 var_2018;
        wp::float64 var_2019;
        wp::float64 var_2020;
        const wp::int32 var_2021 = 0;
        wp::float64 var_2022;
        wp::float64 var_2023;
        wp::float64 var_2024;
        wp::float64 var_2025;
        const wp::int32 var_2026 = 1;
        wp::float64 var_2027;
        wp::float64 var_2028;
        wp::float64 var_2029;
        wp::float64 var_2030;
        wp::float64 var_2031;
        const wp::int32 var_2032 = 2;
        wp::float64 var_2033;
        wp::float64 var_2034;
        wp::float64 var_2035;
        wp::vec_t<3, wp::float64> var_2036;
        wp::vec_t<3, wp::float64> var_2037;
        const wp::int32 var_2038 = 0;
        wp::int32 var_2039;
        wp::float64 var_2040;
        const wp::int32 var_2041 = 1;
        wp::int32 var_2042;
        wp::float64 var_2043;
        const wp::int32 var_2044 = 2;
        wp::int32 var_2045;
        wp::float64 var_2046;
        wp::vec_t<3, wp::float64> var_2047;
        wp::vec_t<3, wp::float64> var_2048;
        wp::vec_t<3, wp::float64>* var_2049;
        wp::vec_t<3, wp::float64> var_2050;
        wp::vec_t<3, wp::float64> var_2051;
        wp::float64 var_2052;
        wp::float64 var_2053;
        wp::float64 var_2054;
        const wp::int32 var_2055 = 1;
        const wp::int32 var_2056 = 9;
        wp::int32 var_2057;
        const wp::int32 var_2058 = 3;
        wp::int32 var_2059;
        wp::int32 var_2060;
        wp::int32 var_2061;
        wp::vec_t<3, wp::int32> var_2062;
        wp::vec_t<3, wp::int32> var_2063;
        wp::vec_t<3, wp::int32> var_2064;
        bool var_2065;
        const wp::int32 var_2066 = 0;
        wp::int32 var_2067;
        const wp::int32 var_2068 = 0;
        bool var_2069;
        const wp::int32 var_2070 = 1;
        wp::int32 var_2071;
        const wp::int32 var_2072 = 0;
        bool var_2073;
        const wp::int32 var_2074 = 2;
        wp::int32 var_2075;
        const wp::int32 var_2076 = 0;
        bool var_2077;
        const wp::int32 var_2078 = 0;
        wp::int32 var_2079;
        const wp::int32 var_2080 = 0;
        wp::int32 var_2081;
        bool var_2082;
        const wp::int32 var_2083 = 1;
        wp::int32 var_2084;
        const wp::int32 var_2085 = 1;
        wp::int32 var_2086;
        bool var_2087;
        const wp::int32 var_2088 = 2;
        wp::int32 var_2089;
        const wp::int32 var_2090 = 2;
        wp::int32 var_2091;
        bool var_2092;
        const wp::int32 var_2093 = 0;
        const wp::int32 var_2094 = 1;
        wp::int32 var_2095;
        const wp::int32 var_2096 = 0;
        wp::float64 var_2097;
        wp::float64 var_2098;
        wp::vec_t<3, wp::float64> var_2099;
        wp::float64 var_2100;
        wp::vec_t<3, wp::float64> var_2101;
        const wp::int32 var_2102 = 0;
        wp::int32 var_2103;
        const wp::int32 var_2104 = 1;
        wp::int32 var_2105;
        wp::int32 var_2106;
        const wp::int32 var_2107 = 1;
        wp::int32 var_2108;
        wp::int32 var_2109;
        const wp::int32 var_2110 = 2;
        wp::int32 var_2111;
        wp::int32 var_2112;
        const wp::int32 var_2113 = 2;
        wp::int32 var_2114;
        wp::int32 var_2115;
        const wp::int32 var_2116 = 0;
        wp::float64 var_2117;
        wp::float64 var_2118;
        const wp::int32 var_2119 = 1;
        wp::float64 var_2120;
        wp::float64 var_2121;
        const wp::int32 var_2122 = 2;
        wp::float64 var_2123;
        wp::float64 var_2124;
        wp::float64 var_2125;
        wp::float64 var_2126;
        const wp::int32 var_2127 = 0;
        wp::float64 var_2128;
        wp::float64 var_2129;
        wp::float64 var_2130;
        wp::float64 var_2131;
        const wp::int32 var_2132 = 1;
        wp::float64 var_2133;
        wp::float64 var_2134;
        wp::float64 var_2135;
        wp::float64 var_2136;
        wp::float64 var_2137;
        const wp::int32 var_2138 = 2;
        wp::float64 var_2139;
        wp::float64 var_2140;
        wp::float64 var_2141;
        wp::vec_t<3, wp::float64> var_2142;
        wp::vec_t<3, wp::float64> var_2143;
        const wp::int32 var_2144 = 0;
        wp::int32 var_2145;
        wp::float64 var_2146;
        const wp::int32 var_2147 = 1;
        wp::int32 var_2148;
        wp::float64 var_2149;
        const wp::int32 var_2150 = 2;
        wp::int32 var_2151;
        wp::float64 var_2152;
        wp::vec_t<3, wp::float64> var_2153;
        wp::vec_t<3, wp::float64> var_2154;
        wp::vec_t<3, wp::float64>* var_2155;
        wp::vec_t<3, wp::float64> var_2156;
        wp::vec_t<3, wp::float64> var_2157;
        wp::float64 var_2158;
        wp::float64 var_2159;
        wp::float64 var_2160;
        const wp::int32 var_2161 = 2;
        const wp::int32 var_2162 = 9;
        wp::int32 var_2163;
        const wp::int32 var_2164 = 3;
        wp::int32 var_2165;
        wp::int32 var_2166;
        wp::int32 var_2167;
        wp::vec_t<3, wp::int32> var_2168;
        wp::vec_t<3, wp::int32> var_2169;
        wp::vec_t<3, wp::int32> var_2170;
        bool var_2171;
        const wp::int32 var_2172 = 0;
        wp::int32 var_2173;
        const wp::int32 var_2174 = 0;
        bool var_2175;
        const wp::int32 var_2176 = 1;
        wp::int32 var_2177;
        const wp::int32 var_2178 = 0;
        bool var_2179;
        const wp::int32 var_2180 = 2;
        wp::int32 var_2181;
        const wp::int32 var_2182 = 0;
        bool var_2183;
        const wp::int32 var_2184 = 0;
        wp::int32 var_2185;
        const wp::int32 var_2186 = 0;
        wp::int32 var_2187;
        bool var_2188;
        const wp::int32 var_2189 = 1;
        wp::int32 var_2190;
        const wp::int32 var_2191 = 1;
        wp::int32 var_2192;
        bool var_2193;
        const wp::int32 var_2194 = 2;
        wp::int32 var_2195;
        const wp::int32 var_2196 = 2;
        wp::int32 var_2197;
        bool var_2198;
        const wp::int32 var_2199 = 0;
        const wp::int32 var_2200 = 1;
        wp::int32 var_2201;
        const wp::int32 var_2202 = 0;
        wp::float64 var_2203;
        wp::float64 var_2204;
        wp::vec_t<3, wp::float64> var_2205;
        wp::float64 var_2206;
        wp::vec_t<3, wp::float64> var_2207;
        const wp::int32 var_2208 = 0;
        wp::int32 var_2209;
        const wp::int32 var_2210 = 1;
        wp::int32 var_2211;
        wp::int32 var_2212;
        const wp::int32 var_2213 = 1;
        wp::int32 var_2214;
        wp::int32 var_2215;
        const wp::int32 var_2216 = 2;
        wp::int32 var_2217;
        wp::int32 var_2218;
        const wp::int32 var_2219 = 2;
        wp::int32 var_2220;
        wp::int32 var_2221;
        const wp::int32 var_2222 = 0;
        wp::float64 var_2223;
        wp::float64 var_2224;
        const wp::int32 var_2225 = 1;
        wp::float64 var_2226;
        wp::float64 var_2227;
        const wp::int32 var_2228 = 2;
        wp::float64 var_2229;
        wp::float64 var_2230;
        wp::float64 var_2231;
        wp::float64 var_2232;
        const wp::int32 var_2233 = 0;
        wp::float64 var_2234;
        wp::float64 var_2235;
        wp::float64 var_2236;
        wp::float64 var_2237;
        const wp::int32 var_2238 = 1;
        wp::float64 var_2239;
        wp::float64 var_2240;
        wp::float64 var_2241;
        wp::float64 var_2242;
        wp::float64 var_2243;
        const wp::int32 var_2244 = 2;
        wp::float64 var_2245;
        wp::float64 var_2246;
        wp::float64 var_2247;
        wp::vec_t<3, wp::float64> var_2248;
        wp::vec_t<3, wp::float64> var_2249;
        const wp::int32 var_2250 = 0;
        wp::int32 var_2251;
        wp::float64 var_2252;
        const wp::int32 var_2253 = 1;
        wp::int32 var_2254;
        wp::float64 var_2255;
        const wp::int32 var_2256 = 2;
        wp::int32 var_2257;
        wp::float64 var_2258;
        wp::vec_t<3, wp::float64> var_2259;
        wp::vec_t<3, wp::float64> var_2260;
        wp::vec_t<3, wp::float64>* var_2261;
        wp::vec_t<3, wp::float64> var_2262;
        wp::vec_t<3, wp::float64> var_2263;
        wp::float64 var_2264;
        wp::float64 var_2265;
        wp::float64 var_2266;
        const wp::int32 var_2267 = 1;
        const wp::int32 var_2268 = 0;
        const wp::int32 var_2269 = 9;
        wp::int32 var_2270;
        const wp::int32 var_2271 = 3;
        wp::int32 var_2272;
        wp::int32 var_2273;
        wp::int32 var_2274;
        wp::vec_t<3, wp::int32> var_2275;
        wp::vec_t<3, wp::int32> var_2276;
        wp::vec_t<3, wp::int32> var_2277;
        bool var_2278;
        const wp::int32 var_2279 = 0;
        wp::int32 var_2280;
        const wp::int32 var_2281 = 0;
        bool var_2282;
        const wp::int32 var_2283 = 1;
        wp::int32 var_2284;
        const wp::int32 var_2285 = 0;
        bool var_2286;
        const wp::int32 var_2287 = 2;
        wp::int32 var_2288;
        const wp::int32 var_2289 = 0;
        bool var_2290;
        const wp::int32 var_2291 = 0;
        wp::int32 var_2292;
        const wp::int32 var_2293 = 0;
        wp::int32 var_2294;
        bool var_2295;
        const wp::int32 var_2296 = 1;
        wp::int32 var_2297;
        const wp::int32 var_2298 = 1;
        wp::int32 var_2299;
        bool var_2300;
        const wp::int32 var_2301 = 2;
        wp::int32 var_2302;
        const wp::int32 var_2303 = 2;
        wp::int32 var_2304;
        bool var_2305;
        const wp::int32 var_2306 = 0;
        const wp::int32 var_2307 = 1;
        wp::int32 var_2308;
        const wp::int32 var_2309 = 0;
        wp::float64 var_2310;
        wp::float64 var_2311;
        wp::vec_t<3, wp::float64> var_2312;
        wp::float64 var_2313;
        wp::vec_t<3, wp::float64> var_2314;
        const wp::int32 var_2315 = 0;
        wp::int32 var_2316;
        const wp::int32 var_2317 = 1;
        wp::int32 var_2318;
        wp::int32 var_2319;
        const wp::int32 var_2320 = 1;
        wp::int32 var_2321;
        wp::int32 var_2322;
        const wp::int32 var_2323 = 2;
        wp::int32 var_2324;
        wp::int32 var_2325;
        const wp::int32 var_2326 = 2;
        wp::int32 var_2327;
        wp::int32 var_2328;
        const wp::int32 var_2329 = 0;
        wp::float64 var_2330;
        wp::float64 var_2331;
        const wp::int32 var_2332 = 1;
        wp::float64 var_2333;
        wp::float64 var_2334;
        const wp::int32 var_2335 = 2;
        wp::float64 var_2336;
        wp::float64 var_2337;
        wp::float64 var_2338;
        wp::float64 var_2339;
        const wp::int32 var_2340 = 0;
        wp::float64 var_2341;
        wp::float64 var_2342;
        wp::float64 var_2343;
        wp::float64 var_2344;
        const wp::int32 var_2345 = 1;
        wp::float64 var_2346;
        wp::float64 var_2347;
        wp::float64 var_2348;
        wp::float64 var_2349;
        wp::float64 var_2350;
        const wp::int32 var_2351 = 2;
        wp::float64 var_2352;
        wp::float64 var_2353;
        wp::float64 var_2354;
        wp::vec_t<3, wp::float64> var_2355;
        wp::vec_t<3, wp::float64> var_2356;
        const wp::int32 var_2357 = 0;
        wp::int32 var_2358;
        wp::float64 var_2359;
        const wp::int32 var_2360 = 1;
        wp::int32 var_2361;
        wp::float64 var_2362;
        const wp::int32 var_2363 = 2;
        wp::int32 var_2364;
        wp::float64 var_2365;
        wp::vec_t<3, wp::float64> var_2366;
        wp::vec_t<3, wp::float64> var_2367;
        wp::vec_t<3, wp::float64>* var_2368;
        wp::vec_t<3, wp::float64> var_2369;
        wp::vec_t<3, wp::float64> var_2370;
        wp::float64 var_2371;
        wp::float64 var_2372;
        wp::float64 var_2373;
        const wp::int32 var_2374 = 1;
        const wp::int32 var_2375 = 9;
        wp::int32 var_2376;
        const wp::int32 var_2377 = 3;
        wp::int32 var_2378;
        wp::int32 var_2379;
        wp::int32 var_2380;
        wp::vec_t<3, wp::int32> var_2381;
        wp::vec_t<3, wp::int32> var_2382;
        wp::vec_t<3, wp::int32> var_2383;
        bool var_2384;
        const wp::int32 var_2385 = 0;
        wp::int32 var_2386;
        const wp::int32 var_2387 = 0;
        bool var_2388;
        const wp::int32 var_2389 = 1;
        wp::int32 var_2390;
        const wp::int32 var_2391 = 0;
        bool var_2392;
        const wp::int32 var_2393 = 2;
        wp::int32 var_2394;
        const wp::int32 var_2395 = 0;
        bool var_2396;
        const wp::int32 var_2397 = 0;
        wp::int32 var_2398;
        const wp::int32 var_2399 = 0;
        wp::int32 var_2400;
        bool var_2401;
        const wp::int32 var_2402 = 1;
        wp::int32 var_2403;
        const wp::int32 var_2404 = 1;
        wp::int32 var_2405;
        bool var_2406;
        const wp::int32 var_2407 = 2;
        wp::int32 var_2408;
        const wp::int32 var_2409 = 2;
        wp::int32 var_2410;
        bool var_2411;
        const wp::int32 var_2412 = 0;
        const wp::int32 var_2413 = 1;
        wp::int32 var_2414;
        const wp::int32 var_2415 = 0;
        wp::float64 var_2416;
        wp::float64 var_2417;
        wp::vec_t<3, wp::float64> var_2418;
        wp::float64 var_2419;
        wp::vec_t<3, wp::float64> var_2420;
        const wp::int32 var_2421 = 0;
        wp::int32 var_2422;
        const wp::int32 var_2423 = 1;
        wp::int32 var_2424;
        wp::int32 var_2425;
        const wp::int32 var_2426 = 1;
        wp::int32 var_2427;
        wp::int32 var_2428;
        const wp::int32 var_2429 = 2;
        wp::int32 var_2430;
        wp::int32 var_2431;
        const wp::int32 var_2432 = 2;
        wp::int32 var_2433;
        wp::int32 var_2434;
        const wp::int32 var_2435 = 0;
        wp::float64 var_2436;
        wp::float64 var_2437;
        const wp::int32 var_2438 = 1;
        wp::float64 var_2439;
        wp::float64 var_2440;
        const wp::int32 var_2441 = 2;
        wp::float64 var_2442;
        wp::float64 var_2443;
        wp::float64 var_2444;
        wp::float64 var_2445;
        const wp::int32 var_2446 = 0;
        wp::float64 var_2447;
        wp::float64 var_2448;
        wp::float64 var_2449;
        wp::float64 var_2450;
        const wp::int32 var_2451 = 1;
        wp::float64 var_2452;
        wp::float64 var_2453;
        wp::float64 var_2454;
        wp::float64 var_2455;
        wp::float64 var_2456;
        const wp::int32 var_2457 = 2;
        wp::float64 var_2458;
        wp::float64 var_2459;
        wp::float64 var_2460;
        wp::vec_t<3, wp::float64> var_2461;
        wp::vec_t<3, wp::float64> var_2462;
        const wp::int32 var_2463 = 0;
        wp::int32 var_2464;
        wp::float64 var_2465;
        const wp::int32 var_2466 = 1;
        wp::int32 var_2467;
        wp::float64 var_2468;
        const wp::int32 var_2469 = 2;
        wp::int32 var_2470;
        wp::float64 var_2471;
        wp::vec_t<3, wp::float64> var_2472;
        wp::vec_t<3, wp::float64> var_2473;
        wp::vec_t<3, wp::float64>* var_2474;
        wp::vec_t<3, wp::float64> var_2475;
        wp::vec_t<3, wp::float64> var_2476;
        wp::float64 var_2477;
        wp::float64 var_2478;
        wp::float64 var_2479;
        const wp::int32 var_2480 = 2;
        const wp::int32 var_2481 = 9;
        wp::int32 var_2482;
        const wp::int32 var_2483 = 3;
        wp::int32 var_2484;
        wp::int32 var_2485;
        wp::int32 var_2486;
        wp::vec_t<3, wp::int32> var_2487;
        wp::vec_t<3, wp::int32> var_2488;
        wp::vec_t<3, wp::int32> var_2489;
        bool var_2490;
        const wp::int32 var_2491 = 0;
        wp::int32 var_2492;
        const wp::int32 var_2493 = 0;
        bool var_2494;
        const wp::int32 var_2495 = 1;
        wp::int32 var_2496;
        const wp::int32 var_2497 = 0;
        bool var_2498;
        const wp::int32 var_2499 = 2;
        wp::int32 var_2500;
        const wp::int32 var_2501 = 0;
        bool var_2502;
        const wp::int32 var_2503 = 0;
        wp::int32 var_2504;
        const wp::int32 var_2505 = 0;
        wp::int32 var_2506;
        bool var_2507;
        const wp::int32 var_2508 = 1;
        wp::int32 var_2509;
        const wp::int32 var_2510 = 1;
        wp::int32 var_2511;
        bool var_2512;
        const wp::int32 var_2513 = 2;
        wp::int32 var_2514;
        const wp::int32 var_2515 = 2;
        wp::int32 var_2516;
        bool var_2517;
        const wp::int32 var_2518 = 0;
        const wp::int32 var_2519 = 1;
        wp::int32 var_2520;
        const wp::int32 var_2521 = 0;
        wp::float64 var_2522;
        wp::float64 var_2523;
        wp::vec_t<3, wp::float64> var_2524;
        wp::float64 var_2525;
        wp::vec_t<3, wp::float64> var_2526;
        const wp::int32 var_2527 = 0;
        wp::int32 var_2528;
        const wp::int32 var_2529 = 1;
        wp::int32 var_2530;
        wp::int32 var_2531;
        const wp::int32 var_2532 = 1;
        wp::int32 var_2533;
        wp::int32 var_2534;
        const wp::int32 var_2535 = 2;
        wp::int32 var_2536;
        wp::int32 var_2537;
        const wp::int32 var_2538 = 2;
        wp::int32 var_2539;
        wp::int32 var_2540;
        const wp::int32 var_2541 = 0;
        wp::float64 var_2542;
        wp::float64 var_2543;
        const wp::int32 var_2544 = 1;
        wp::float64 var_2545;
        wp::float64 var_2546;
        const wp::int32 var_2547 = 2;
        wp::float64 var_2548;
        wp::float64 var_2549;
        wp::float64 var_2550;
        wp::float64 var_2551;
        const wp::int32 var_2552 = 0;
        wp::float64 var_2553;
        wp::float64 var_2554;
        wp::float64 var_2555;
        wp::float64 var_2556;
        const wp::int32 var_2557 = 1;
        wp::float64 var_2558;
        wp::float64 var_2559;
        wp::float64 var_2560;
        wp::float64 var_2561;
        wp::float64 var_2562;
        const wp::int32 var_2563 = 2;
        wp::float64 var_2564;
        wp::float64 var_2565;
        wp::float64 var_2566;
        wp::vec_t<3, wp::float64> var_2567;
        wp::vec_t<3, wp::float64> var_2568;
        const wp::int32 var_2569 = 0;
        wp::int32 var_2570;
        wp::float64 var_2571;
        const wp::int32 var_2572 = 1;
        wp::int32 var_2573;
        wp::float64 var_2574;
        const wp::int32 var_2575 = 2;
        wp::int32 var_2576;
        wp::float64 var_2577;
        wp::vec_t<3, wp::float64> var_2578;
        wp::vec_t<3, wp::float64> var_2579;
        wp::vec_t<3, wp::float64>* var_2580;
        wp::vec_t<3, wp::float64> var_2581;
        wp::vec_t<3, wp::float64> var_2582;
        wp::float64 var_2583;
        wp::float64 var_2584;
        wp::float64 var_2585;
        const wp::int32 var_2586 = 2;
        const wp::int32 var_2587 = 0;
        const wp::int32 var_2588 = 9;
        wp::int32 var_2589;
        const wp::int32 var_2590 = 3;
        wp::int32 var_2591;
        wp::int32 var_2592;
        wp::int32 var_2593;
        wp::vec_t<3, wp::int32> var_2594;
        wp::vec_t<3, wp::int32> var_2595;
        wp::vec_t<3, wp::int32> var_2596;
        bool var_2597;
        const wp::int32 var_2598 = 0;
        wp::int32 var_2599;
        const wp::int32 var_2600 = 0;
        bool var_2601;
        const wp::int32 var_2602 = 1;
        wp::int32 var_2603;
        const wp::int32 var_2604 = 0;
        bool var_2605;
        const wp::int32 var_2606 = 2;
        wp::int32 var_2607;
        const wp::int32 var_2608 = 0;
        bool var_2609;
        const wp::int32 var_2610 = 0;
        wp::int32 var_2611;
        const wp::int32 var_2612 = 0;
        wp::int32 var_2613;
        bool var_2614;
        const wp::int32 var_2615 = 1;
        wp::int32 var_2616;
        const wp::int32 var_2617 = 1;
        wp::int32 var_2618;
        bool var_2619;
        const wp::int32 var_2620 = 2;
        wp::int32 var_2621;
        const wp::int32 var_2622 = 2;
        wp::int32 var_2623;
        bool var_2624;
        const wp::int32 var_2625 = 0;
        const wp::int32 var_2626 = 1;
        wp::int32 var_2627;
        const wp::int32 var_2628 = 0;
        wp::float64 var_2629;
        wp::float64 var_2630;
        wp::vec_t<3, wp::float64> var_2631;
        wp::float64 var_2632;
        wp::vec_t<3, wp::float64> var_2633;
        const wp::int32 var_2634 = 0;
        wp::int32 var_2635;
        const wp::int32 var_2636 = 1;
        wp::int32 var_2637;
        wp::int32 var_2638;
        const wp::int32 var_2639 = 1;
        wp::int32 var_2640;
        wp::int32 var_2641;
        const wp::int32 var_2642 = 2;
        wp::int32 var_2643;
        wp::int32 var_2644;
        const wp::int32 var_2645 = 2;
        wp::int32 var_2646;
        wp::int32 var_2647;
        const wp::int32 var_2648 = 0;
        wp::float64 var_2649;
        wp::float64 var_2650;
        const wp::int32 var_2651 = 1;
        wp::float64 var_2652;
        wp::float64 var_2653;
        const wp::int32 var_2654 = 2;
        wp::float64 var_2655;
        wp::float64 var_2656;
        wp::float64 var_2657;
        wp::float64 var_2658;
        const wp::int32 var_2659 = 0;
        wp::float64 var_2660;
        wp::float64 var_2661;
        wp::float64 var_2662;
        wp::float64 var_2663;
        const wp::int32 var_2664 = 1;
        wp::float64 var_2665;
        wp::float64 var_2666;
        wp::float64 var_2667;
        wp::float64 var_2668;
        wp::float64 var_2669;
        const wp::int32 var_2670 = 2;
        wp::float64 var_2671;
        wp::float64 var_2672;
        wp::float64 var_2673;
        wp::vec_t<3, wp::float64> var_2674;
        wp::vec_t<3, wp::float64> var_2675;
        const wp::int32 var_2676 = 0;
        wp::int32 var_2677;
        wp::float64 var_2678;
        const wp::int32 var_2679 = 1;
        wp::int32 var_2680;
        wp::float64 var_2681;
        const wp::int32 var_2682 = 2;
        wp::int32 var_2683;
        wp::float64 var_2684;
        wp::vec_t<3, wp::float64> var_2685;
        wp::vec_t<3, wp::float64> var_2686;
        wp::vec_t<3, wp::float64>* var_2687;
        wp::vec_t<3, wp::float64> var_2688;
        wp::vec_t<3, wp::float64> var_2689;
        wp::float64 var_2690;
        wp::float64 var_2691;
        wp::float64 var_2692;
        const wp::int32 var_2693 = 1;
        const wp::int32 var_2694 = 9;
        wp::int32 var_2695;
        const wp::int32 var_2696 = 3;
        wp::int32 var_2697;
        wp::int32 var_2698;
        wp::int32 var_2699;
        wp::vec_t<3, wp::int32> var_2700;
        wp::vec_t<3, wp::int32> var_2701;
        wp::vec_t<3, wp::int32> var_2702;
        bool var_2703;
        const wp::int32 var_2704 = 0;
        wp::int32 var_2705;
        const wp::int32 var_2706 = 0;
        bool var_2707;
        const wp::int32 var_2708 = 1;
        wp::int32 var_2709;
        const wp::int32 var_2710 = 0;
        bool var_2711;
        const wp::int32 var_2712 = 2;
        wp::int32 var_2713;
        const wp::int32 var_2714 = 0;
        bool var_2715;
        const wp::int32 var_2716 = 0;
        wp::int32 var_2717;
        const wp::int32 var_2718 = 0;
        wp::int32 var_2719;
        bool var_2720;
        const wp::int32 var_2721 = 1;
        wp::int32 var_2722;
        const wp::int32 var_2723 = 1;
        wp::int32 var_2724;
        bool var_2725;
        const wp::int32 var_2726 = 2;
        wp::int32 var_2727;
        const wp::int32 var_2728 = 2;
        wp::int32 var_2729;
        bool var_2730;
        const wp::int32 var_2731 = 0;
        const wp::int32 var_2732 = 1;
        wp::int32 var_2733;
        const wp::int32 var_2734 = 0;
        wp::float64 var_2735;
        wp::float64 var_2736;
        wp::vec_t<3, wp::float64> var_2737;
        wp::float64 var_2738;
        wp::vec_t<3, wp::float64> var_2739;
        const wp::int32 var_2740 = 0;
        wp::int32 var_2741;
        const wp::int32 var_2742 = 1;
        wp::int32 var_2743;
        wp::int32 var_2744;
        const wp::int32 var_2745 = 1;
        wp::int32 var_2746;
        wp::int32 var_2747;
        const wp::int32 var_2748 = 2;
        wp::int32 var_2749;
        wp::int32 var_2750;
        const wp::int32 var_2751 = 2;
        wp::int32 var_2752;
        wp::int32 var_2753;
        const wp::int32 var_2754 = 0;
        wp::float64 var_2755;
        wp::float64 var_2756;
        const wp::int32 var_2757 = 1;
        wp::float64 var_2758;
        wp::float64 var_2759;
        const wp::int32 var_2760 = 2;
        wp::float64 var_2761;
        wp::float64 var_2762;
        wp::float64 var_2763;
        wp::float64 var_2764;
        const wp::int32 var_2765 = 0;
        wp::float64 var_2766;
        wp::float64 var_2767;
        wp::float64 var_2768;
        wp::float64 var_2769;
        const wp::int32 var_2770 = 1;
        wp::float64 var_2771;
        wp::float64 var_2772;
        wp::float64 var_2773;
        wp::float64 var_2774;
        wp::float64 var_2775;
        const wp::int32 var_2776 = 2;
        wp::float64 var_2777;
        wp::float64 var_2778;
        wp::float64 var_2779;
        wp::vec_t<3, wp::float64> var_2780;
        wp::vec_t<3, wp::float64> var_2781;
        const wp::int32 var_2782 = 0;
        wp::int32 var_2783;
        wp::float64 var_2784;
        const wp::int32 var_2785 = 1;
        wp::int32 var_2786;
        wp::float64 var_2787;
        const wp::int32 var_2788 = 2;
        wp::int32 var_2789;
        wp::float64 var_2790;
        wp::vec_t<3, wp::float64> var_2791;
        wp::vec_t<3, wp::float64> var_2792;
        wp::vec_t<3, wp::float64>* var_2793;
        wp::vec_t<3, wp::float64> var_2794;
        wp::vec_t<3, wp::float64> var_2795;
        wp::float64 var_2796;
        wp::float64 var_2797;
        wp::float64 var_2798;
        const wp::int32 var_2799 = 2;
        const wp::int32 var_2800 = 9;
        wp::int32 var_2801;
        const wp::int32 var_2802 = 3;
        wp::int32 var_2803;
        wp::int32 var_2804;
        wp::int32 var_2805;
        wp::vec_t<3, wp::int32> var_2806;
        wp::vec_t<3, wp::int32> var_2807;
        wp::vec_t<3, wp::int32> var_2808;
        bool var_2809;
        const wp::int32 var_2810 = 0;
        wp::int32 var_2811;
        const wp::int32 var_2812 = 0;
        bool var_2813;
        const wp::int32 var_2814 = 1;
        wp::int32 var_2815;
        const wp::int32 var_2816 = 0;
        bool var_2817;
        const wp::int32 var_2818 = 2;
        wp::int32 var_2819;
        const wp::int32 var_2820 = 0;
        bool var_2821;
        const wp::int32 var_2822 = 0;
        wp::int32 var_2823;
        const wp::int32 var_2824 = 0;
        wp::int32 var_2825;
        bool var_2826;
        const wp::int32 var_2827 = 1;
        wp::int32 var_2828;
        const wp::int32 var_2829 = 1;
        wp::int32 var_2830;
        bool var_2831;
        const wp::int32 var_2832 = 2;
        wp::int32 var_2833;
        const wp::int32 var_2834 = 2;
        wp::int32 var_2835;
        bool var_2836;
        const wp::int32 var_2837 = 0;
        const wp::int32 var_2838 = 1;
        wp::int32 var_2839;
        const wp::int32 var_2840 = 0;
        wp::float64 var_2841;
        wp::float64 var_2842;
        wp::vec_t<3, wp::float64> var_2843;
        wp::float64 var_2844;
        wp::vec_t<3, wp::float64> var_2845;
        const wp::int32 var_2846 = 0;
        wp::int32 var_2847;
        const wp::int32 var_2848 = 1;
        wp::int32 var_2849;
        wp::int32 var_2850;
        const wp::int32 var_2851 = 1;
        wp::int32 var_2852;
        wp::int32 var_2853;
        const wp::int32 var_2854 = 2;
        wp::int32 var_2855;
        wp::int32 var_2856;
        const wp::int32 var_2857 = 2;
        wp::int32 var_2858;
        wp::int32 var_2859;
        const wp::int32 var_2860 = 0;
        wp::float64 var_2861;
        wp::float64 var_2862;
        const wp::int32 var_2863 = 1;
        wp::float64 var_2864;
        wp::float64 var_2865;
        const wp::int32 var_2866 = 2;
        wp::float64 var_2867;
        wp::float64 var_2868;
        wp::float64 var_2869;
        wp::float64 var_2870;
        const wp::int32 var_2871 = 0;
        wp::float64 var_2872;
        wp::float64 var_2873;
        wp::float64 var_2874;
        wp::float64 var_2875;
        const wp::int32 var_2876 = 1;
        wp::float64 var_2877;
        wp::float64 var_2878;
        wp::float64 var_2879;
        wp::float64 var_2880;
        wp::float64 var_2881;
        const wp::int32 var_2882 = 2;
        wp::float64 var_2883;
        wp::float64 var_2884;
        wp::float64 var_2885;
        wp::vec_t<3, wp::float64> var_2886;
        wp::vec_t<3, wp::float64> var_2887;
        const wp::int32 var_2888 = 0;
        wp::int32 var_2889;
        wp::float64 var_2890;
        const wp::int32 var_2891 = 1;
        wp::int32 var_2892;
        wp::float64 var_2893;
        const wp::int32 var_2894 = 2;
        wp::int32 var_2895;
        wp::float64 var_2896;
        wp::vec_t<3, wp::float64> var_2897;
        wp::vec_t<3, wp::float64> var_2898;
        wp::vec_t<3, wp::float64>* var_2899;
        wp::vec_t<3, wp::float64> var_2900;
        wp::vec_t<3, wp::float64> var_2901;
        wp::float64 var_2902;
        wp::float64 var_2903;
        wp::float64 var_2904;
        //---------
        // forward
        // def stencil_current(x:wp.array(dtype=wp.vec3d),h:wp.float64,origin:wp.vec3i,dims:wp.vec3i,ids:wp.array2d(dtype=int),w:wp.array2d(dtype=wp.float64),g:wp.array2d(dtype=wp.vec3d),r:wp.array2d(dtype=wp.vec3d),bad:wp.array(dtype=int)):       <L 26>
        // p=wp.tid();z=x[p]/h;base=wp.vec3i(int(wp.floor(z[0]-wp.float64(.5))),int(wp.floor(z[1]-wp.float64(.5))),int(wp.floor(z[2]-wp.float64(.5))));f=z-wp.vec3d(wp.float64(base[0]),wp.float64(base[1]),wp.float64(base[2]))       <L 27>
        var_0 = builtin_tid1d();
        var_1 = wp::address(var_x, var_0);
        var_3 = wp::load(var_1);
        var_2 = wp::div(var_3, var_h);
        var_5 = wp::extract(var_2, var_4);
        var_6 = 0.5;
        var_7 = wp::sub(var_5, var_6);
        var_8 = wp::floor(var_7);
        var_9 = wp::int(var_8);
        var_11 = wp::extract(var_2, var_10);
        var_12 = 0.5;
        var_13 = wp::sub(var_11, var_12);
        var_14 = wp::floor(var_13);
        var_15 = wp::int(var_14);
        var_17 = wp::extract(var_2, var_16);
        var_18 = 0.5;
        var_19 = wp::sub(var_17, var_18);
        var_20 = wp::floor(var_19);
        var_21 = wp::int(var_20);
        var_22 = wp::vec_t<3, wp::int32>(var_9, var_15, var_21);
        var_24 = wp::extract(var_22, var_23);
        var_25 = wp::float64(var_24);
        var_27 = wp::extract(var_22, var_26);
        var_28 = wp::float64(var_27);
        var_30 = wp::extract(var_22, var_29);
        var_31 = wp::float64(var_30);
        var_32 = wp::vec_t<3, wp::float64>(var_25, var_28, var_31);
        var_33 = wp::sub(var_2, var_32);
        // for a in range(3):                                                                     <L 28>
        // for b in range(3):                                                                     <L 29>
        // for c in range(3):                                                                     <L 30>
        // s=9*a+3*b+c;node=base+wp.vec3i(a,b,c);j=node-origin                                    <L 31>
        var_38 = wp::mul(var_37, var_34);
        var_40 = wp::mul(var_39, var_35);
        var_41 = wp::add(var_38, var_40);
        var_42 = wp::add(var_41, var_36);
        var_43 = wp::vec_t<3, wp::int32>(var_34, var_35, var_36);
        var_44 = wp::add(var_22, var_43);
        var_45 = wp::sub(var_44, var_origin);
        // if j[0]<0 or j[1]<0 or j[2]<0 or j[0]>=dims[0] or j[1]>=dims[1] or j[2]>=dims[2]:wp.atomic_add(bad,0,1);ids[p,s]=0;w[p,s]=wp.float64(0.0);g[p,s]=wp.vec3d(wp.float64(0.0));r[p,s]=wp.vec3d(wp.float64(0.0))       <L 32>
        var_48 = wp::extract(var_45, var_47);
        var_50 = (var_48 < var_49);
        var_46 = var_50;
        if (!var_46) {
            var_52 = wp::extract(var_45, var_51);
            var_54 = (var_52 < var_53);
            var_46 = var_46 || var_54;
        }
        if (!var_46) {
            var_56 = wp::extract(var_45, var_55);
            var_58 = (var_56 < var_57);
            var_46 = var_46 || var_58;
        }
        if (!var_46) {
            var_60 = wp::extract(var_45, var_59);
            var_62 = wp::extract(var_dims, var_61);
            var_63 = (var_60 >= var_62);
            var_46 = var_46 || var_63;
        }
        if (!var_46) {
            var_65 = wp::extract(var_45, var_64);
            var_67 = wp::extract(var_dims, var_66);
            var_68 = (var_65 >= var_67);
            var_46 = var_46 || var_68;
        }
        if (!var_46) {
            var_70 = wp::extract(var_45, var_69);
            var_72 = wp::extract(var_dims, var_71);
            var_73 = (var_70 >= var_72);
            var_46 = var_46 || var_73;
        }
        if (var_46) {
            var_76 = wp::atomic_add(var_bad, var_74, var_75);
            wp::array_store(var_ids, var_0, var_42, var_77);
            var_78 = 0.0;
            wp::array_store(var_w, var_0, var_42, var_78);
            var_79 = 0.0;
            var_80 = wp::vec_t<3, wp::float64>(var_79);
            wp::array_store(var_g, var_0, var_42, var_80);
            var_81 = 0.0;
            var_82 = wp::vec_t<3, wp::float64>(var_81);
            wp::array_store(var_r, var_0, var_42, var_82);
        }
        if (!var_46) {
            // ids[p,s]=(j[0]*dims[1]+j[1])*dims[2]+j[2];wx=basis(a,f[0]);wy=basis(b,f[1]);wz=basis(c,f[2]);w[p,s]=wx*wy*wz;g[p,s]=wp.vec3d(dbasis(a,f[0])*wy*wz,wx*dbasis(b,f[1])*wz,wx*wy*dbasis(c,f[2]))/h;r[p,s]=wp.vec3d(wp.float64(node[0]),wp.float64(node[1]),wp.float64(node[2]))*h-x[p]       <L 34>
            var_84 = wp::extract(var_45, var_83);
            var_86 = wp::extract(var_dims, var_85);
            var_87 = wp::mul(var_84, var_86);
            var_89 = wp::extract(var_45, var_88);
            var_90 = wp::add(var_87, var_89);
            var_92 = wp::extract(var_dims, var_91);
            var_93 = wp::mul(var_90, var_92);
            var_95 = wp::extract(var_45, var_94);
            var_96 = wp::add(var_93, var_95);
            wp::array_store(var_ids, var_0, var_42, var_96);
            var_98 = wp::extract(var_33, var_97);
            var_99 = basis_0(var_34, var_98);
            var_101 = wp::extract(var_33, var_100);
            var_102 = basis_0(var_35, var_101);
            var_104 = wp::extract(var_33, var_103);
            var_105 = basis_0(var_36, var_104);
            var_106 = wp::mul(var_99, var_102);
            var_107 = wp::mul(var_106, var_105);
            wp::array_store(var_w, var_0, var_42, var_107);
            var_109 = wp::extract(var_33, var_108);
            var_110 = dbasis_0(var_34, var_109);
            var_111 = wp::mul(var_110, var_102);
            var_112 = wp::mul(var_111, var_105);
            var_114 = wp::extract(var_33, var_113);
            var_115 = dbasis_0(var_35, var_114);
            var_116 = wp::mul(var_99, var_115);
            var_117 = wp::mul(var_116, var_105);
            var_118 = wp::mul(var_99, var_102);
            var_120 = wp::extract(var_33, var_119);
            var_121 = dbasis_0(var_36, var_120);
            var_122 = wp::mul(var_118, var_121);
            var_123 = wp::vec_t<3, wp::float64>(var_112, var_117, var_122);
            var_124 = wp::div(var_123, var_h);
            wp::array_store(var_g, var_0, var_42, var_124);
            var_126 = wp::extract(var_44, var_125);
            var_127 = wp::float64(var_126);
            var_129 = wp::extract(var_44, var_128);
            var_130 = wp::float64(var_129);
            var_132 = wp::extract(var_44, var_131);
            var_133 = wp::float64(var_132);
            var_134 = wp::vec_t<3, wp::float64>(var_127, var_130, var_133);
            var_135 = wp::mul(var_134, var_h);
            var_136 = wp::address(var_x, var_0);
            var_138 = wp::load(var_136);
            var_137 = wp::sub(var_135, var_138);
            wp::array_store(var_r, var_0, var_42, var_137);
        }
        // s=9*a+3*b+c;node=base+wp.vec3i(a,b,c);j=node-origin                                    <L 31>
        var_141 = wp::mul(var_140, var_34);
        var_143 = wp::mul(var_142, var_35);
        var_144 = wp::add(var_141, var_143);
        var_145 = wp::add(var_144, var_139);
        var_146 = wp::vec_t<3, wp::int32>(var_34, var_35, var_139);
        var_147 = wp::add(var_22, var_146);
        var_148 = wp::sub(var_147, var_origin);
        // if j[0]<0 or j[1]<0 or j[2]<0 or j[0]>=dims[0] or j[1]>=dims[1] or j[2]>=dims[2]:wp.atomic_add(bad,0,1);ids[p,s]=0;w[p,s]=wp.float64(0.0);g[p,s]=wp.vec3d(wp.float64(0.0));r[p,s]=wp.vec3d(wp.float64(0.0))       <L 32>
        var_151 = wp::extract(var_148, var_150);
        var_153 = (var_151 < var_152);
        var_149 = var_153;
        if (!var_149) {
            var_155 = wp::extract(var_148, var_154);
            var_157 = (var_155 < var_156);
            var_149 = var_149 || var_157;
        }
        if (!var_149) {
            var_159 = wp::extract(var_148, var_158);
            var_161 = (var_159 < var_160);
            var_149 = var_149 || var_161;
        }
        if (!var_149) {
            var_163 = wp::extract(var_148, var_162);
            var_165 = wp::extract(var_dims, var_164);
            var_166 = (var_163 >= var_165);
            var_149 = var_149 || var_166;
        }
        if (!var_149) {
            var_168 = wp::extract(var_148, var_167);
            var_170 = wp::extract(var_dims, var_169);
            var_171 = (var_168 >= var_170);
            var_149 = var_149 || var_171;
        }
        if (!var_149) {
            var_173 = wp::extract(var_148, var_172);
            var_175 = wp::extract(var_dims, var_174);
            var_176 = (var_173 >= var_175);
            var_149 = var_149 || var_176;
        }
        if (var_149) {
            var_179 = wp::atomic_add(var_bad, var_177, var_178);
            wp::array_store(var_ids, var_0, var_145, var_180);
            var_181 = 0.0;
            wp::array_store(var_w, var_0, var_145, var_181);
            var_182 = 0.0;
            var_183 = wp::vec_t<3, wp::float64>(var_182);
            wp::array_store(var_g, var_0, var_145, var_183);
            var_184 = 0.0;
            var_185 = wp::vec_t<3, wp::float64>(var_184);
            wp::array_store(var_r, var_0, var_145, var_185);
        }
        if (!var_149) {
            // ids[p,s]=(j[0]*dims[1]+j[1])*dims[2]+j[2];wx=basis(a,f[0]);wy=basis(b,f[1]);wz=basis(c,f[2]);w[p,s]=wx*wy*wz;g[p,s]=wp.vec3d(dbasis(a,f[0])*wy*wz,wx*dbasis(b,f[1])*wz,wx*wy*dbasis(c,f[2]))/h;r[p,s]=wp.vec3d(wp.float64(node[0]),wp.float64(node[1]),wp.float64(node[2]))*h-x[p]       <L 34>
            var_187 = wp::extract(var_148, var_186);
            var_189 = wp::extract(var_dims, var_188);
            var_190 = wp::mul(var_187, var_189);
            var_192 = wp::extract(var_148, var_191);
            var_193 = wp::add(var_190, var_192);
            var_195 = wp::extract(var_dims, var_194);
            var_196 = wp::mul(var_193, var_195);
            var_198 = wp::extract(var_148, var_197);
            var_199 = wp::add(var_196, var_198);
            wp::array_store(var_ids, var_0, var_145, var_199);
            var_201 = wp::extract(var_33, var_200);
            var_202 = basis_0(var_34, var_201);
            var_204 = wp::extract(var_33, var_203);
            var_205 = basis_0(var_35, var_204);
            var_207 = wp::extract(var_33, var_206);
            var_208 = basis_0(var_139, var_207);
            var_209 = wp::mul(var_202, var_205);
            var_210 = wp::mul(var_209, var_208);
            wp::array_store(var_w, var_0, var_145, var_210);
            var_212 = wp::extract(var_33, var_211);
            var_213 = dbasis_0(var_34, var_212);
            var_214 = wp::mul(var_213, var_205);
            var_215 = wp::mul(var_214, var_208);
            var_217 = wp::extract(var_33, var_216);
            var_218 = dbasis_0(var_35, var_217);
            var_219 = wp::mul(var_202, var_218);
            var_220 = wp::mul(var_219, var_208);
            var_221 = wp::mul(var_202, var_205);
            var_223 = wp::extract(var_33, var_222);
            var_224 = dbasis_0(var_139, var_223);
            var_225 = wp::mul(var_221, var_224);
            var_226 = wp::vec_t<3, wp::float64>(var_215, var_220, var_225);
            var_227 = wp::div(var_226, var_h);
            wp::array_store(var_g, var_0, var_145, var_227);
            var_229 = wp::extract(var_147, var_228);
            var_230 = wp::float64(var_229);
            var_232 = wp::extract(var_147, var_231);
            var_233 = wp::float64(var_232);
            var_235 = wp::extract(var_147, var_234);
            var_236 = wp::float64(var_235);
            var_237 = wp::vec_t<3, wp::float64>(var_230, var_233, var_236);
            var_238 = wp::mul(var_237, var_h);
            var_239 = wp::address(var_x, var_0);
            var_241 = wp::load(var_239);
            var_240 = wp::sub(var_238, var_241);
            wp::array_store(var_r, var_0, var_145, var_240);
        }
        var_242 = wp::where(var_149, var_99, var_202);
        var_243 = wp::where(var_149, var_102, var_205);
        var_244 = wp::where(var_149, var_105, var_208);
        // s=9*a+3*b+c;node=base+wp.vec3i(a,b,c);j=node-origin                                    <L 31>
        var_247 = wp::mul(var_246, var_34);
        var_249 = wp::mul(var_248, var_35);
        var_250 = wp::add(var_247, var_249);
        var_251 = wp::add(var_250, var_245);
        var_252 = wp::vec_t<3, wp::int32>(var_34, var_35, var_245);
        var_253 = wp::add(var_22, var_252);
        var_254 = wp::sub(var_253, var_origin);
        // if j[0]<0 or j[1]<0 or j[2]<0 or j[0]>=dims[0] or j[1]>=dims[1] or j[2]>=dims[2]:wp.atomic_add(bad,0,1);ids[p,s]=0;w[p,s]=wp.float64(0.0);g[p,s]=wp.vec3d(wp.float64(0.0));r[p,s]=wp.vec3d(wp.float64(0.0))       <L 32>
        var_257 = wp::extract(var_254, var_256);
        var_259 = (var_257 < var_258);
        var_255 = var_259;
        if (!var_255) {
            var_261 = wp::extract(var_254, var_260);
            var_263 = (var_261 < var_262);
            var_255 = var_255 || var_263;
        }
        if (!var_255) {
            var_265 = wp::extract(var_254, var_264);
            var_267 = (var_265 < var_266);
            var_255 = var_255 || var_267;
        }
        if (!var_255) {
            var_269 = wp::extract(var_254, var_268);
            var_271 = wp::extract(var_dims, var_270);
            var_272 = (var_269 >= var_271);
            var_255 = var_255 || var_272;
        }
        if (!var_255) {
            var_274 = wp::extract(var_254, var_273);
            var_276 = wp::extract(var_dims, var_275);
            var_277 = (var_274 >= var_276);
            var_255 = var_255 || var_277;
        }
        if (!var_255) {
            var_279 = wp::extract(var_254, var_278);
            var_281 = wp::extract(var_dims, var_280);
            var_282 = (var_279 >= var_281);
            var_255 = var_255 || var_282;
        }
        if (var_255) {
            var_285 = wp::atomic_add(var_bad, var_283, var_284);
            wp::array_store(var_ids, var_0, var_251, var_286);
            var_287 = 0.0;
            wp::array_store(var_w, var_0, var_251, var_287);
            var_288 = 0.0;
            var_289 = wp::vec_t<3, wp::float64>(var_288);
            wp::array_store(var_g, var_0, var_251, var_289);
            var_290 = 0.0;
            var_291 = wp::vec_t<3, wp::float64>(var_290);
            wp::array_store(var_r, var_0, var_251, var_291);
        }
        if (!var_255) {
            // ids[p,s]=(j[0]*dims[1]+j[1])*dims[2]+j[2];wx=basis(a,f[0]);wy=basis(b,f[1]);wz=basis(c,f[2]);w[p,s]=wx*wy*wz;g[p,s]=wp.vec3d(dbasis(a,f[0])*wy*wz,wx*dbasis(b,f[1])*wz,wx*wy*dbasis(c,f[2]))/h;r[p,s]=wp.vec3d(wp.float64(node[0]),wp.float64(node[1]),wp.float64(node[2]))*h-x[p]       <L 34>
            var_293 = wp::extract(var_254, var_292);
            var_295 = wp::extract(var_dims, var_294);
            var_296 = wp::mul(var_293, var_295);
            var_298 = wp::extract(var_254, var_297);
            var_299 = wp::add(var_296, var_298);
            var_301 = wp::extract(var_dims, var_300);
            var_302 = wp::mul(var_299, var_301);
            var_304 = wp::extract(var_254, var_303);
            var_305 = wp::add(var_302, var_304);
            wp::array_store(var_ids, var_0, var_251, var_305);
            var_307 = wp::extract(var_33, var_306);
            var_308 = basis_0(var_34, var_307);
            var_310 = wp::extract(var_33, var_309);
            var_311 = basis_0(var_35, var_310);
            var_313 = wp::extract(var_33, var_312);
            var_314 = basis_0(var_245, var_313);
            var_315 = wp::mul(var_308, var_311);
            var_316 = wp::mul(var_315, var_314);
            wp::array_store(var_w, var_0, var_251, var_316);
            var_318 = wp::extract(var_33, var_317);
            var_319 = dbasis_0(var_34, var_318);
            var_320 = wp::mul(var_319, var_311);
            var_321 = wp::mul(var_320, var_314);
            var_323 = wp::extract(var_33, var_322);
            var_324 = dbasis_0(var_35, var_323);
            var_325 = wp::mul(var_308, var_324);
            var_326 = wp::mul(var_325, var_314);
            var_327 = wp::mul(var_308, var_311);
            var_329 = wp::extract(var_33, var_328);
            var_330 = dbasis_0(var_245, var_329);
            var_331 = wp::mul(var_327, var_330);
            var_332 = wp::vec_t<3, wp::float64>(var_321, var_326, var_331);
            var_333 = wp::div(var_332, var_h);
            wp::array_store(var_g, var_0, var_251, var_333);
            var_335 = wp::extract(var_253, var_334);
            var_336 = wp::float64(var_335);
            var_338 = wp::extract(var_253, var_337);
            var_339 = wp::float64(var_338);
            var_341 = wp::extract(var_253, var_340);
            var_342 = wp::float64(var_341);
            var_343 = wp::vec_t<3, wp::float64>(var_336, var_339, var_342);
            var_344 = wp::mul(var_343, var_h);
            var_345 = wp::address(var_x, var_0);
            var_347 = wp::load(var_345);
            var_346 = wp::sub(var_344, var_347);
            wp::array_store(var_r, var_0, var_251, var_346);
        }
        var_348 = wp::where(var_255, var_242, var_308);
        var_349 = wp::where(var_255, var_243, var_311);
        var_350 = wp::where(var_255, var_244, var_314);
        // for c in range(3):                                                                     <L 30>
        // s=9*a+3*b+c;node=base+wp.vec3i(a,b,c);j=node-origin                                    <L 31>
        var_354 = wp::mul(var_353, var_34);
        var_356 = wp::mul(var_355, var_351);
        var_357 = wp::add(var_354, var_356);
        var_358 = wp::add(var_357, var_352);
        var_359 = wp::vec_t<3, wp::int32>(var_34, var_351, var_352);
        var_360 = wp::add(var_22, var_359);
        var_361 = wp::sub(var_360, var_origin);
        // if j[0]<0 or j[1]<0 or j[2]<0 or j[0]>=dims[0] or j[1]>=dims[1] or j[2]>=dims[2]:wp.atomic_add(bad,0,1);ids[p,s]=0;w[p,s]=wp.float64(0.0);g[p,s]=wp.vec3d(wp.float64(0.0));r[p,s]=wp.vec3d(wp.float64(0.0))       <L 32>
        var_364 = wp::extract(var_361, var_363);
        var_366 = (var_364 < var_365);
        var_362 = var_366;
        if (!var_362) {
            var_368 = wp::extract(var_361, var_367);
            var_370 = (var_368 < var_369);
            var_362 = var_362 || var_370;
        }
        if (!var_362) {
            var_372 = wp::extract(var_361, var_371);
            var_374 = (var_372 < var_373);
            var_362 = var_362 || var_374;
        }
        if (!var_362) {
            var_376 = wp::extract(var_361, var_375);
            var_378 = wp::extract(var_dims, var_377);
            var_379 = (var_376 >= var_378);
            var_362 = var_362 || var_379;
        }
        if (!var_362) {
            var_381 = wp::extract(var_361, var_380);
            var_383 = wp::extract(var_dims, var_382);
            var_384 = (var_381 >= var_383);
            var_362 = var_362 || var_384;
        }
        if (!var_362) {
            var_386 = wp::extract(var_361, var_385);
            var_388 = wp::extract(var_dims, var_387);
            var_389 = (var_386 >= var_388);
            var_362 = var_362 || var_389;
        }
        if (var_362) {
            var_392 = wp::atomic_add(var_bad, var_390, var_391);
            wp::array_store(var_ids, var_0, var_358, var_393);
            var_394 = 0.0;
            wp::array_store(var_w, var_0, var_358, var_394);
            var_395 = 0.0;
            var_396 = wp::vec_t<3, wp::float64>(var_395);
            wp::array_store(var_g, var_0, var_358, var_396);
            var_397 = 0.0;
            var_398 = wp::vec_t<3, wp::float64>(var_397);
            wp::array_store(var_r, var_0, var_358, var_398);
        }
        if (!var_362) {
            // ids[p,s]=(j[0]*dims[1]+j[1])*dims[2]+j[2];wx=basis(a,f[0]);wy=basis(b,f[1]);wz=basis(c,f[2]);w[p,s]=wx*wy*wz;g[p,s]=wp.vec3d(dbasis(a,f[0])*wy*wz,wx*dbasis(b,f[1])*wz,wx*wy*dbasis(c,f[2]))/h;r[p,s]=wp.vec3d(wp.float64(node[0]),wp.float64(node[1]),wp.float64(node[2]))*h-x[p]       <L 34>
            var_400 = wp::extract(var_361, var_399);
            var_402 = wp::extract(var_dims, var_401);
            var_403 = wp::mul(var_400, var_402);
            var_405 = wp::extract(var_361, var_404);
            var_406 = wp::add(var_403, var_405);
            var_408 = wp::extract(var_dims, var_407);
            var_409 = wp::mul(var_406, var_408);
            var_411 = wp::extract(var_361, var_410);
            var_412 = wp::add(var_409, var_411);
            wp::array_store(var_ids, var_0, var_358, var_412);
            var_414 = wp::extract(var_33, var_413);
            var_415 = basis_0(var_34, var_414);
            var_417 = wp::extract(var_33, var_416);
            var_418 = basis_0(var_351, var_417);
            var_420 = wp::extract(var_33, var_419);
            var_421 = basis_0(var_352, var_420);
            var_422 = wp::mul(var_415, var_418);
            var_423 = wp::mul(var_422, var_421);
            wp::array_store(var_w, var_0, var_358, var_423);
            var_425 = wp::extract(var_33, var_424);
            var_426 = dbasis_0(var_34, var_425);
            var_427 = wp::mul(var_426, var_418);
            var_428 = wp::mul(var_427, var_421);
            var_430 = wp::extract(var_33, var_429);
            var_431 = dbasis_0(var_351, var_430);
            var_432 = wp::mul(var_415, var_431);
            var_433 = wp::mul(var_432, var_421);
            var_434 = wp::mul(var_415, var_418);
            var_436 = wp::extract(var_33, var_435);
            var_437 = dbasis_0(var_352, var_436);
            var_438 = wp::mul(var_434, var_437);
            var_439 = wp::vec_t<3, wp::float64>(var_428, var_433, var_438);
            var_440 = wp::div(var_439, var_h);
            wp::array_store(var_g, var_0, var_358, var_440);
            var_442 = wp::extract(var_360, var_441);
            var_443 = wp::float64(var_442);
            var_445 = wp::extract(var_360, var_444);
            var_446 = wp::float64(var_445);
            var_448 = wp::extract(var_360, var_447);
            var_449 = wp::float64(var_448);
            var_450 = wp::vec_t<3, wp::float64>(var_443, var_446, var_449);
            var_451 = wp::mul(var_450, var_h);
            var_452 = wp::address(var_x, var_0);
            var_454 = wp::load(var_452);
            var_453 = wp::sub(var_451, var_454);
            wp::array_store(var_r, var_0, var_358, var_453);
        }
        var_455 = wp::where(var_362, var_348, var_415);
        var_456 = wp::where(var_362, var_349, var_418);
        var_457 = wp::where(var_362, var_350, var_421);
        // s=9*a+3*b+c;node=base+wp.vec3i(a,b,c);j=node-origin                                    <L 31>
        var_460 = wp::mul(var_459, var_34);
        var_462 = wp::mul(var_461, var_351);
        var_463 = wp::add(var_460, var_462);
        var_464 = wp::add(var_463, var_458);
        var_465 = wp::vec_t<3, wp::int32>(var_34, var_351, var_458);
        var_466 = wp::add(var_22, var_465);
        var_467 = wp::sub(var_466, var_origin);
        // if j[0]<0 or j[1]<0 or j[2]<0 or j[0]>=dims[0] or j[1]>=dims[1] or j[2]>=dims[2]:wp.atomic_add(bad,0,1);ids[p,s]=0;w[p,s]=wp.float64(0.0);g[p,s]=wp.vec3d(wp.float64(0.0));r[p,s]=wp.vec3d(wp.float64(0.0))       <L 32>
        var_470 = wp::extract(var_467, var_469);
        var_472 = (var_470 < var_471);
        var_468 = var_472;
        if (!var_468) {
            var_474 = wp::extract(var_467, var_473);
            var_476 = (var_474 < var_475);
            var_468 = var_468 || var_476;
        }
        if (!var_468) {
            var_478 = wp::extract(var_467, var_477);
            var_480 = (var_478 < var_479);
            var_468 = var_468 || var_480;
        }
        if (!var_468) {
            var_482 = wp::extract(var_467, var_481);
            var_484 = wp::extract(var_dims, var_483);
            var_485 = (var_482 >= var_484);
            var_468 = var_468 || var_485;
        }
        if (!var_468) {
            var_487 = wp::extract(var_467, var_486);
            var_489 = wp::extract(var_dims, var_488);
            var_490 = (var_487 >= var_489);
            var_468 = var_468 || var_490;
        }
        if (!var_468) {
            var_492 = wp::extract(var_467, var_491);
            var_494 = wp::extract(var_dims, var_493);
            var_495 = (var_492 >= var_494);
            var_468 = var_468 || var_495;
        }
        if (var_468) {
            var_498 = wp::atomic_add(var_bad, var_496, var_497);
            wp::array_store(var_ids, var_0, var_464, var_499);
            var_500 = 0.0;
            wp::array_store(var_w, var_0, var_464, var_500);
            var_501 = 0.0;
            var_502 = wp::vec_t<3, wp::float64>(var_501);
            wp::array_store(var_g, var_0, var_464, var_502);
            var_503 = 0.0;
            var_504 = wp::vec_t<3, wp::float64>(var_503);
            wp::array_store(var_r, var_0, var_464, var_504);
        }
        if (!var_468) {
            // ids[p,s]=(j[0]*dims[1]+j[1])*dims[2]+j[2];wx=basis(a,f[0]);wy=basis(b,f[1]);wz=basis(c,f[2]);w[p,s]=wx*wy*wz;g[p,s]=wp.vec3d(dbasis(a,f[0])*wy*wz,wx*dbasis(b,f[1])*wz,wx*wy*dbasis(c,f[2]))/h;r[p,s]=wp.vec3d(wp.float64(node[0]),wp.float64(node[1]),wp.float64(node[2]))*h-x[p]       <L 34>
            var_506 = wp::extract(var_467, var_505);
            var_508 = wp::extract(var_dims, var_507);
            var_509 = wp::mul(var_506, var_508);
            var_511 = wp::extract(var_467, var_510);
            var_512 = wp::add(var_509, var_511);
            var_514 = wp::extract(var_dims, var_513);
            var_515 = wp::mul(var_512, var_514);
            var_517 = wp::extract(var_467, var_516);
            var_518 = wp::add(var_515, var_517);
            wp::array_store(var_ids, var_0, var_464, var_518);
            var_520 = wp::extract(var_33, var_519);
            var_521 = basis_0(var_34, var_520);
            var_523 = wp::extract(var_33, var_522);
            var_524 = basis_0(var_351, var_523);
            var_526 = wp::extract(var_33, var_525);
            var_527 = basis_0(var_458, var_526);
            var_528 = wp::mul(var_521, var_524);
            var_529 = wp::mul(var_528, var_527);
            wp::array_store(var_w, var_0, var_464, var_529);
            var_531 = wp::extract(var_33, var_530);
            var_532 = dbasis_0(var_34, var_531);
            var_533 = wp::mul(var_532, var_524);
            var_534 = wp::mul(var_533, var_527);
            var_536 = wp::extract(var_33, var_535);
            var_537 = dbasis_0(var_351, var_536);
            var_538 = wp::mul(var_521, var_537);
            var_539 = wp::mul(var_538, var_527);
            var_540 = wp::mul(var_521, var_524);
            var_542 = wp::extract(var_33, var_541);
            var_543 = dbasis_0(var_458, var_542);
            var_544 = wp::mul(var_540, var_543);
            var_545 = wp::vec_t<3, wp::float64>(var_534, var_539, var_544);
            var_546 = wp::div(var_545, var_h);
            wp::array_store(var_g, var_0, var_464, var_546);
            var_548 = wp::extract(var_466, var_547);
            var_549 = wp::float64(var_548);
            var_551 = wp::extract(var_466, var_550);
            var_552 = wp::float64(var_551);
            var_554 = wp::extract(var_466, var_553);
            var_555 = wp::float64(var_554);
            var_556 = wp::vec_t<3, wp::float64>(var_549, var_552, var_555);
            var_557 = wp::mul(var_556, var_h);
            var_558 = wp::address(var_x, var_0);
            var_560 = wp::load(var_558);
            var_559 = wp::sub(var_557, var_560);
            wp::array_store(var_r, var_0, var_464, var_559);
        }
        var_561 = wp::where(var_468, var_455, var_521);
        var_562 = wp::where(var_468, var_456, var_524);
        var_563 = wp::where(var_468, var_457, var_527);
        // s=9*a+3*b+c;node=base+wp.vec3i(a,b,c);j=node-origin                                    <L 31>
        var_566 = wp::mul(var_565, var_34);
        var_568 = wp::mul(var_567, var_351);
        var_569 = wp::add(var_566, var_568);
        var_570 = wp::add(var_569, var_564);
        var_571 = wp::vec_t<3, wp::int32>(var_34, var_351, var_564);
        var_572 = wp::add(var_22, var_571);
        var_573 = wp::sub(var_572, var_origin);
        // if j[0]<0 or j[1]<0 or j[2]<0 or j[0]>=dims[0] or j[1]>=dims[1] or j[2]>=dims[2]:wp.atomic_add(bad,0,1);ids[p,s]=0;w[p,s]=wp.float64(0.0);g[p,s]=wp.vec3d(wp.float64(0.0));r[p,s]=wp.vec3d(wp.float64(0.0))       <L 32>
        var_576 = wp::extract(var_573, var_575);
        var_578 = (var_576 < var_577);
        var_574 = var_578;
        if (!var_574) {
            var_580 = wp::extract(var_573, var_579);
            var_582 = (var_580 < var_581);
            var_574 = var_574 || var_582;
        }
        if (!var_574) {
            var_584 = wp::extract(var_573, var_583);
            var_586 = (var_584 < var_585);
            var_574 = var_574 || var_586;
        }
        if (!var_574) {
            var_588 = wp::extract(var_573, var_587);
            var_590 = wp::extract(var_dims, var_589);
            var_591 = (var_588 >= var_590);
            var_574 = var_574 || var_591;
        }
        if (!var_574) {
            var_593 = wp::extract(var_573, var_592);
            var_595 = wp::extract(var_dims, var_594);
            var_596 = (var_593 >= var_595);
            var_574 = var_574 || var_596;
        }
        if (!var_574) {
            var_598 = wp::extract(var_573, var_597);
            var_600 = wp::extract(var_dims, var_599);
            var_601 = (var_598 >= var_600);
            var_574 = var_574 || var_601;
        }
        if (var_574) {
            var_604 = wp::atomic_add(var_bad, var_602, var_603);
            wp::array_store(var_ids, var_0, var_570, var_605);
            var_606 = 0.0;
            wp::array_store(var_w, var_0, var_570, var_606);
            var_607 = 0.0;
            var_608 = wp::vec_t<3, wp::float64>(var_607);
            wp::array_store(var_g, var_0, var_570, var_608);
            var_609 = 0.0;
            var_610 = wp::vec_t<3, wp::float64>(var_609);
            wp::array_store(var_r, var_0, var_570, var_610);
        }
        if (!var_574) {
            // ids[p,s]=(j[0]*dims[1]+j[1])*dims[2]+j[2];wx=basis(a,f[0]);wy=basis(b,f[1]);wz=basis(c,f[2]);w[p,s]=wx*wy*wz;g[p,s]=wp.vec3d(dbasis(a,f[0])*wy*wz,wx*dbasis(b,f[1])*wz,wx*wy*dbasis(c,f[2]))/h;r[p,s]=wp.vec3d(wp.float64(node[0]),wp.float64(node[1]),wp.float64(node[2]))*h-x[p]       <L 34>
            var_612 = wp::extract(var_573, var_611);
            var_614 = wp::extract(var_dims, var_613);
            var_615 = wp::mul(var_612, var_614);
            var_617 = wp::extract(var_573, var_616);
            var_618 = wp::add(var_615, var_617);
            var_620 = wp::extract(var_dims, var_619);
            var_621 = wp::mul(var_618, var_620);
            var_623 = wp::extract(var_573, var_622);
            var_624 = wp::add(var_621, var_623);
            wp::array_store(var_ids, var_0, var_570, var_624);
            var_626 = wp::extract(var_33, var_625);
            var_627 = basis_0(var_34, var_626);
            var_629 = wp::extract(var_33, var_628);
            var_630 = basis_0(var_351, var_629);
            var_632 = wp::extract(var_33, var_631);
            var_633 = basis_0(var_564, var_632);
            var_634 = wp::mul(var_627, var_630);
            var_635 = wp::mul(var_634, var_633);
            wp::array_store(var_w, var_0, var_570, var_635);
            var_637 = wp::extract(var_33, var_636);
            var_638 = dbasis_0(var_34, var_637);
            var_639 = wp::mul(var_638, var_630);
            var_640 = wp::mul(var_639, var_633);
            var_642 = wp::extract(var_33, var_641);
            var_643 = dbasis_0(var_351, var_642);
            var_644 = wp::mul(var_627, var_643);
            var_645 = wp::mul(var_644, var_633);
            var_646 = wp::mul(var_627, var_630);
            var_648 = wp::extract(var_33, var_647);
            var_649 = dbasis_0(var_564, var_648);
            var_650 = wp::mul(var_646, var_649);
            var_651 = wp::vec_t<3, wp::float64>(var_640, var_645, var_650);
            var_652 = wp::div(var_651, var_h);
            wp::array_store(var_g, var_0, var_570, var_652);
            var_654 = wp::extract(var_572, var_653);
            var_655 = wp::float64(var_654);
            var_657 = wp::extract(var_572, var_656);
            var_658 = wp::float64(var_657);
            var_660 = wp::extract(var_572, var_659);
            var_661 = wp::float64(var_660);
            var_662 = wp::vec_t<3, wp::float64>(var_655, var_658, var_661);
            var_663 = wp::mul(var_662, var_h);
            var_664 = wp::address(var_x, var_0);
            var_666 = wp::load(var_664);
            var_665 = wp::sub(var_663, var_666);
            wp::array_store(var_r, var_0, var_570, var_665);
        }
        var_667 = wp::where(var_574, var_561, var_627);
        var_668 = wp::where(var_574, var_562, var_630);
        var_669 = wp::where(var_574, var_563, var_633);
        // for c in range(3):                                                                     <L 30>
        // s=9*a+3*b+c;node=base+wp.vec3i(a,b,c);j=node-origin                                    <L 31>
        var_673 = wp::mul(var_672, var_34);
        var_675 = wp::mul(var_674, var_670);
        var_676 = wp::add(var_673, var_675);
        var_677 = wp::add(var_676, var_671);
        var_678 = wp::vec_t<3, wp::int32>(var_34, var_670, var_671);
        var_679 = wp::add(var_22, var_678);
        var_680 = wp::sub(var_679, var_origin);
        // if j[0]<0 or j[1]<0 or j[2]<0 or j[0]>=dims[0] or j[1]>=dims[1] or j[2]>=dims[2]:wp.atomic_add(bad,0,1);ids[p,s]=0;w[p,s]=wp.float64(0.0);g[p,s]=wp.vec3d(wp.float64(0.0));r[p,s]=wp.vec3d(wp.float64(0.0))       <L 32>
        var_683 = wp::extract(var_680, var_682);
        var_685 = (var_683 < var_684);
        var_681 = var_685;
        if (!var_681) {
            var_687 = wp::extract(var_680, var_686);
            var_689 = (var_687 < var_688);
            var_681 = var_681 || var_689;
        }
        if (!var_681) {
            var_691 = wp::extract(var_680, var_690);
            var_693 = (var_691 < var_692);
            var_681 = var_681 || var_693;
        }
        if (!var_681) {
            var_695 = wp::extract(var_680, var_694);
            var_697 = wp::extract(var_dims, var_696);
            var_698 = (var_695 >= var_697);
            var_681 = var_681 || var_698;
        }
        if (!var_681) {
            var_700 = wp::extract(var_680, var_699);
            var_702 = wp::extract(var_dims, var_701);
            var_703 = (var_700 >= var_702);
            var_681 = var_681 || var_703;
        }
        if (!var_681) {
            var_705 = wp::extract(var_680, var_704);
            var_707 = wp::extract(var_dims, var_706);
            var_708 = (var_705 >= var_707);
            var_681 = var_681 || var_708;
        }
        if (var_681) {
            var_711 = wp::atomic_add(var_bad, var_709, var_710);
            wp::array_store(var_ids, var_0, var_677, var_712);
            var_713 = 0.0;
            wp::array_store(var_w, var_0, var_677, var_713);
            var_714 = 0.0;
            var_715 = wp::vec_t<3, wp::float64>(var_714);
            wp::array_store(var_g, var_0, var_677, var_715);
            var_716 = 0.0;
            var_717 = wp::vec_t<3, wp::float64>(var_716);
            wp::array_store(var_r, var_0, var_677, var_717);
        }
        if (!var_681) {
            // ids[p,s]=(j[0]*dims[1]+j[1])*dims[2]+j[2];wx=basis(a,f[0]);wy=basis(b,f[1]);wz=basis(c,f[2]);w[p,s]=wx*wy*wz;g[p,s]=wp.vec3d(dbasis(a,f[0])*wy*wz,wx*dbasis(b,f[1])*wz,wx*wy*dbasis(c,f[2]))/h;r[p,s]=wp.vec3d(wp.float64(node[0]),wp.float64(node[1]),wp.float64(node[2]))*h-x[p]       <L 34>
            var_719 = wp::extract(var_680, var_718);
            var_721 = wp::extract(var_dims, var_720);
            var_722 = wp::mul(var_719, var_721);
            var_724 = wp::extract(var_680, var_723);
            var_725 = wp::add(var_722, var_724);
            var_727 = wp::extract(var_dims, var_726);
            var_728 = wp::mul(var_725, var_727);
            var_730 = wp::extract(var_680, var_729);
            var_731 = wp::add(var_728, var_730);
            wp::array_store(var_ids, var_0, var_677, var_731);
            var_733 = wp::extract(var_33, var_732);
            var_734 = basis_0(var_34, var_733);
            var_736 = wp::extract(var_33, var_735);
            var_737 = basis_0(var_670, var_736);
            var_739 = wp::extract(var_33, var_738);
            var_740 = basis_0(var_671, var_739);
            var_741 = wp::mul(var_734, var_737);
            var_742 = wp::mul(var_741, var_740);
            wp::array_store(var_w, var_0, var_677, var_742);
            var_744 = wp::extract(var_33, var_743);
            var_745 = dbasis_0(var_34, var_744);
            var_746 = wp::mul(var_745, var_737);
            var_747 = wp::mul(var_746, var_740);
            var_749 = wp::extract(var_33, var_748);
            var_750 = dbasis_0(var_670, var_749);
            var_751 = wp::mul(var_734, var_750);
            var_752 = wp::mul(var_751, var_740);
            var_753 = wp::mul(var_734, var_737);
            var_755 = wp::extract(var_33, var_754);
            var_756 = dbasis_0(var_671, var_755);
            var_757 = wp::mul(var_753, var_756);
            var_758 = wp::vec_t<3, wp::float64>(var_747, var_752, var_757);
            var_759 = wp::div(var_758, var_h);
            wp::array_store(var_g, var_0, var_677, var_759);
            var_761 = wp::extract(var_679, var_760);
            var_762 = wp::float64(var_761);
            var_764 = wp::extract(var_679, var_763);
            var_765 = wp::float64(var_764);
            var_767 = wp::extract(var_679, var_766);
            var_768 = wp::float64(var_767);
            var_769 = wp::vec_t<3, wp::float64>(var_762, var_765, var_768);
            var_770 = wp::mul(var_769, var_h);
            var_771 = wp::address(var_x, var_0);
            var_773 = wp::load(var_771);
            var_772 = wp::sub(var_770, var_773);
            wp::array_store(var_r, var_0, var_677, var_772);
        }
        var_774 = wp::where(var_681, var_667, var_734);
        var_775 = wp::where(var_681, var_668, var_737);
        var_776 = wp::where(var_681, var_669, var_740);
        // s=9*a+3*b+c;node=base+wp.vec3i(a,b,c);j=node-origin                                    <L 31>
        var_779 = wp::mul(var_778, var_34);
        var_781 = wp::mul(var_780, var_670);
        var_782 = wp::add(var_779, var_781);
        var_783 = wp::add(var_782, var_777);
        var_784 = wp::vec_t<3, wp::int32>(var_34, var_670, var_777);
        var_785 = wp::add(var_22, var_784);
        var_786 = wp::sub(var_785, var_origin);
        // if j[0]<0 or j[1]<0 or j[2]<0 or j[0]>=dims[0] or j[1]>=dims[1] or j[2]>=dims[2]:wp.atomic_add(bad,0,1);ids[p,s]=0;w[p,s]=wp.float64(0.0);g[p,s]=wp.vec3d(wp.float64(0.0));r[p,s]=wp.vec3d(wp.float64(0.0))       <L 32>
        var_789 = wp::extract(var_786, var_788);
        var_791 = (var_789 < var_790);
        var_787 = var_791;
        if (!var_787) {
            var_793 = wp::extract(var_786, var_792);
            var_795 = (var_793 < var_794);
            var_787 = var_787 || var_795;
        }
        if (!var_787) {
            var_797 = wp::extract(var_786, var_796);
            var_799 = (var_797 < var_798);
            var_787 = var_787 || var_799;
        }
        if (!var_787) {
            var_801 = wp::extract(var_786, var_800);
            var_803 = wp::extract(var_dims, var_802);
            var_804 = (var_801 >= var_803);
            var_787 = var_787 || var_804;
        }
        if (!var_787) {
            var_806 = wp::extract(var_786, var_805);
            var_808 = wp::extract(var_dims, var_807);
            var_809 = (var_806 >= var_808);
            var_787 = var_787 || var_809;
        }
        if (!var_787) {
            var_811 = wp::extract(var_786, var_810);
            var_813 = wp::extract(var_dims, var_812);
            var_814 = (var_811 >= var_813);
            var_787 = var_787 || var_814;
        }
        if (var_787) {
            var_817 = wp::atomic_add(var_bad, var_815, var_816);
            wp::array_store(var_ids, var_0, var_783, var_818);
            var_819 = 0.0;
            wp::array_store(var_w, var_0, var_783, var_819);
            var_820 = 0.0;
            var_821 = wp::vec_t<3, wp::float64>(var_820);
            wp::array_store(var_g, var_0, var_783, var_821);
            var_822 = 0.0;
            var_823 = wp::vec_t<3, wp::float64>(var_822);
            wp::array_store(var_r, var_0, var_783, var_823);
        }
        if (!var_787) {
            // ids[p,s]=(j[0]*dims[1]+j[1])*dims[2]+j[2];wx=basis(a,f[0]);wy=basis(b,f[1]);wz=basis(c,f[2]);w[p,s]=wx*wy*wz;g[p,s]=wp.vec3d(dbasis(a,f[0])*wy*wz,wx*dbasis(b,f[1])*wz,wx*wy*dbasis(c,f[2]))/h;r[p,s]=wp.vec3d(wp.float64(node[0]),wp.float64(node[1]),wp.float64(node[2]))*h-x[p]       <L 34>
            var_825 = wp::extract(var_786, var_824);
            var_827 = wp::extract(var_dims, var_826);
            var_828 = wp::mul(var_825, var_827);
            var_830 = wp::extract(var_786, var_829);
            var_831 = wp::add(var_828, var_830);
            var_833 = wp::extract(var_dims, var_832);
            var_834 = wp::mul(var_831, var_833);
            var_836 = wp::extract(var_786, var_835);
            var_837 = wp::add(var_834, var_836);
            wp::array_store(var_ids, var_0, var_783, var_837);
            var_839 = wp::extract(var_33, var_838);
            var_840 = basis_0(var_34, var_839);
            var_842 = wp::extract(var_33, var_841);
            var_843 = basis_0(var_670, var_842);
            var_845 = wp::extract(var_33, var_844);
            var_846 = basis_0(var_777, var_845);
            var_847 = wp::mul(var_840, var_843);
            var_848 = wp::mul(var_847, var_846);
            wp::array_store(var_w, var_0, var_783, var_848);
            var_850 = wp::extract(var_33, var_849);
            var_851 = dbasis_0(var_34, var_850);
            var_852 = wp::mul(var_851, var_843);
            var_853 = wp::mul(var_852, var_846);
            var_855 = wp::extract(var_33, var_854);
            var_856 = dbasis_0(var_670, var_855);
            var_857 = wp::mul(var_840, var_856);
            var_858 = wp::mul(var_857, var_846);
            var_859 = wp::mul(var_840, var_843);
            var_861 = wp::extract(var_33, var_860);
            var_862 = dbasis_0(var_777, var_861);
            var_863 = wp::mul(var_859, var_862);
            var_864 = wp::vec_t<3, wp::float64>(var_853, var_858, var_863);
            var_865 = wp::div(var_864, var_h);
            wp::array_store(var_g, var_0, var_783, var_865);
            var_867 = wp::extract(var_785, var_866);
            var_868 = wp::float64(var_867);
            var_870 = wp::extract(var_785, var_869);
            var_871 = wp::float64(var_870);
            var_873 = wp::extract(var_785, var_872);
            var_874 = wp::float64(var_873);
            var_875 = wp::vec_t<3, wp::float64>(var_868, var_871, var_874);
            var_876 = wp::mul(var_875, var_h);
            var_877 = wp::address(var_x, var_0);
            var_879 = wp::load(var_877);
            var_878 = wp::sub(var_876, var_879);
            wp::array_store(var_r, var_0, var_783, var_878);
        }
        var_880 = wp::where(var_787, var_774, var_840);
        var_881 = wp::where(var_787, var_775, var_843);
        var_882 = wp::where(var_787, var_776, var_846);
        // s=9*a+3*b+c;node=base+wp.vec3i(a,b,c);j=node-origin                                    <L 31>
        var_885 = wp::mul(var_884, var_34);
        var_887 = wp::mul(var_886, var_670);
        var_888 = wp::add(var_885, var_887);
        var_889 = wp::add(var_888, var_883);
        var_890 = wp::vec_t<3, wp::int32>(var_34, var_670, var_883);
        var_891 = wp::add(var_22, var_890);
        var_892 = wp::sub(var_891, var_origin);
        // if j[0]<0 or j[1]<0 or j[2]<0 or j[0]>=dims[0] or j[1]>=dims[1] or j[2]>=dims[2]:wp.atomic_add(bad,0,1);ids[p,s]=0;w[p,s]=wp.float64(0.0);g[p,s]=wp.vec3d(wp.float64(0.0));r[p,s]=wp.vec3d(wp.float64(0.0))       <L 32>
        var_895 = wp::extract(var_892, var_894);
        var_897 = (var_895 < var_896);
        var_893 = var_897;
        if (!var_893) {
            var_899 = wp::extract(var_892, var_898);
            var_901 = (var_899 < var_900);
            var_893 = var_893 || var_901;
        }
        if (!var_893) {
            var_903 = wp::extract(var_892, var_902);
            var_905 = (var_903 < var_904);
            var_893 = var_893 || var_905;
        }
        if (!var_893) {
            var_907 = wp::extract(var_892, var_906);
            var_909 = wp::extract(var_dims, var_908);
            var_910 = (var_907 >= var_909);
            var_893 = var_893 || var_910;
        }
        if (!var_893) {
            var_912 = wp::extract(var_892, var_911);
            var_914 = wp::extract(var_dims, var_913);
            var_915 = (var_912 >= var_914);
            var_893 = var_893 || var_915;
        }
        if (!var_893) {
            var_917 = wp::extract(var_892, var_916);
            var_919 = wp::extract(var_dims, var_918);
            var_920 = (var_917 >= var_919);
            var_893 = var_893 || var_920;
        }
        if (var_893) {
            var_923 = wp::atomic_add(var_bad, var_921, var_922);
            wp::array_store(var_ids, var_0, var_889, var_924);
            var_925 = 0.0;
            wp::array_store(var_w, var_0, var_889, var_925);
            var_926 = 0.0;
            var_927 = wp::vec_t<3, wp::float64>(var_926);
            wp::array_store(var_g, var_0, var_889, var_927);
            var_928 = 0.0;
            var_929 = wp::vec_t<3, wp::float64>(var_928);
            wp::array_store(var_r, var_0, var_889, var_929);
        }
        if (!var_893) {
            // ids[p,s]=(j[0]*dims[1]+j[1])*dims[2]+j[2];wx=basis(a,f[0]);wy=basis(b,f[1]);wz=basis(c,f[2]);w[p,s]=wx*wy*wz;g[p,s]=wp.vec3d(dbasis(a,f[0])*wy*wz,wx*dbasis(b,f[1])*wz,wx*wy*dbasis(c,f[2]))/h;r[p,s]=wp.vec3d(wp.float64(node[0]),wp.float64(node[1]),wp.float64(node[2]))*h-x[p]       <L 34>
            var_931 = wp::extract(var_892, var_930);
            var_933 = wp::extract(var_dims, var_932);
            var_934 = wp::mul(var_931, var_933);
            var_936 = wp::extract(var_892, var_935);
            var_937 = wp::add(var_934, var_936);
            var_939 = wp::extract(var_dims, var_938);
            var_940 = wp::mul(var_937, var_939);
            var_942 = wp::extract(var_892, var_941);
            var_943 = wp::add(var_940, var_942);
            wp::array_store(var_ids, var_0, var_889, var_943);
            var_945 = wp::extract(var_33, var_944);
            var_946 = basis_0(var_34, var_945);
            var_948 = wp::extract(var_33, var_947);
            var_949 = basis_0(var_670, var_948);
            var_951 = wp::extract(var_33, var_950);
            var_952 = basis_0(var_883, var_951);
            var_953 = wp::mul(var_946, var_949);
            var_954 = wp::mul(var_953, var_952);
            wp::array_store(var_w, var_0, var_889, var_954);
            var_956 = wp::extract(var_33, var_955);
            var_957 = dbasis_0(var_34, var_956);
            var_958 = wp::mul(var_957, var_949);
            var_959 = wp::mul(var_958, var_952);
            var_961 = wp::extract(var_33, var_960);
            var_962 = dbasis_0(var_670, var_961);
            var_963 = wp::mul(var_946, var_962);
            var_964 = wp::mul(var_963, var_952);
            var_965 = wp::mul(var_946, var_949);
            var_967 = wp::extract(var_33, var_966);
            var_968 = dbasis_0(var_883, var_967);
            var_969 = wp::mul(var_965, var_968);
            var_970 = wp::vec_t<3, wp::float64>(var_959, var_964, var_969);
            var_971 = wp::div(var_970, var_h);
            wp::array_store(var_g, var_0, var_889, var_971);
            var_973 = wp::extract(var_891, var_972);
            var_974 = wp::float64(var_973);
            var_976 = wp::extract(var_891, var_975);
            var_977 = wp::float64(var_976);
            var_979 = wp::extract(var_891, var_978);
            var_980 = wp::float64(var_979);
            var_981 = wp::vec_t<3, wp::float64>(var_974, var_977, var_980);
            var_982 = wp::mul(var_981, var_h);
            var_983 = wp::address(var_x, var_0);
            var_985 = wp::load(var_983);
            var_984 = wp::sub(var_982, var_985);
            wp::array_store(var_r, var_0, var_889, var_984);
        }
        var_986 = wp::where(var_893, var_880, var_946);
        var_987 = wp::where(var_893, var_881, var_949);
        var_988 = wp::where(var_893, var_882, var_952);
        // for b in range(3):                                                                     <L 29>
        // for c in range(3):                                                                     <L 30>
        // s=9*a+3*b+c;node=base+wp.vec3i(a,b,c);j=node-origin                                    <L 31>
        var_993 = wp::mul(var_992, var_989);
        var_995 = wp::mul(var_994, var_990);
        var_996 = wp::add(var_993, var_995);
        var_997 = wp::add(var_996, var_991);
        var_998 = wp::vec_t<3, wp::int32>(var_989, var_990, var_991);
        var_999 = wp::add(var_22, var_998);
        var_1000 = wp::sub(var_999, var_origin);
        // if j[0]<0 or j[1]<0 or j[2]<0 or j[0]>=dims[0] or j[1]>=dims[1] or j[2]>=dims[2]:wp.atomic_add(bad,0,1);ids[p,s]=0;w[p,s]=wp.float64(0.0);g[p,s]=wp.vec3d(wp.float64(0.0));r[p,s]=wp.vec3d(wp.float64(0.0))       <L 32>
        var_1003 = wp::extract(var_1000, var_1002);
        var_1005 = (var_1003 < var_1004);
        var_1001 = var_1005;
        if (!var_1001) {
            var_1007 = wp::extract(var_1000, var_1006);
            var_1009 = (var_1007 < var_1008);
            var_1001 = var_1001 || var_1009;
        }
        if (!var_1001) {
            var_1011 = wp::extract(var_1000, var_1010);
            var_1013 = (var_1011 < var_1012);
            var_1001 = var_1001 || var_1013;
        }
        if (!var_1001) {
            var_1015 = wp::extract(var_1000, var_1014);
            var_1017 = wp::extract(var_dims, var_1016);
            var_1018 = (var_1015 >= var_1017);
            var_1001 = var_1001 || var_1018;
        }
        if (!var_1001) {
            var_1020 = wp::extract(var_1000, var_1019);
            var_1022 = wp::extract(var_dims, var_1021);
            var_1023 = (var_1020 >= var_1022);
            var_1001 = var_1001 || var_1023;
        }
        if (!var_1001) {
            var_1025 = wp::extract(var_1000, var_1024);
            var_1027 = wp::extract(var_dims, var_1026);
            var_1028 = (var_1025 >= var_1027);
            var_1001 = var_1001 || var_1028;
        }
        if (var_1001) {
            var_1031 = wp::atomic_add(var_bad, var_1029, var_1030);
            wp::array_store(var_ids, var_0, var_997, var_1032);
            var_1033 = 0.0;
            wp::array_store(var_w, var_0, var_997, var_1033);
            var_1034 = 0.0;
            var_1035 = wp::vec_t<3, wp::float64>(var_1034);
            wp::array_store(var_g, var_0, var_997, var_1035);
            var_1036 = 0.0;
            var_1037 = wp::vec_t<3, wp::float64>(var_1036);
            wp::array_store(var_r, var_0, var_997, var_1037);
        }
        if (!var_1001) {
            // ids[p,s]=(j[0]*dims[1]+j[1])*dims[2]+j[2];wx=basis(a,f[0]);wy=basis(b,f[1]);wz=basis(c,f[2]);w[p,s]=wx*wy*wz;g[p,s]=wp.vec3d(dbasis(a,f[0])*wy*wz,wx*dbasis(b,f[1])*wz,wx*wy*dbasis(c,f[2]))/h;r[p,s]=wp.vec3d(wp.float64(node[0]),wp.float64(node[1]),wp.float64(node[2]))*h-x[p]       <L 34>
            var_1039 = wp::extract(var_1000, var_1038);
            var_1041 = wp::extract(var_dims, var_1040);
            var_1042 = wp::mul(var_1039, var_1041);
            var_1044 = wp::extract(var_1000, var_1043);
            var_1045 = wp::add(var_1042, var_1044);
            var_1047 = wp::extract(var_dims, var_1046);
            var_1048 = wp::mul(var_1045, var_1047);
            var_1050 = wp::extract(var_1000, var_1049);
            var_1051 = wp::add(var_1048, var_1050);
            wp::array_store(var_ids, var_0, var_997, var_1051);
            var_1053 = wp::extract(var_33, var_1052);
            var_1054 = basis_0(var_989, var_1053);
            var_1056 = wp::extract(var_33, var_1055);
            var_1057 = basis_0(var_990, var_1056);
            var_1059 = wp::extract(var_33, var_1058);
            var_1060 = basis_0(var_991, var_1059);
            var_1061 = wp::mul(var_1054, var_1057);
            var_1062 = wp::mul(var_1061, var_1060);
            wp::array_store(var_w, var_0, var_997, var_1062);
            var_1064 = wp::extract(var_33, var_1063);
            var_1065 = dbasis_0(var_989, var_1064);
            var_1066 = wp::mul(var_1065, var_1057);
            var_1067 = wp::mul(var_1066, var_1060);
            var_1069 = wp::extract(var_33, var_1068);
            var_1070 = dbasis_0(var_990, var_1069);
            var_1071 = wp::mul(var_1054, var_1070);
            var_1072 = wp::mul(var_1071, var_1060);
            var_1073 = wp::mul(var_1054, var_1057);
            var_1075 = wp::extract(var_33, var_1074);
            var_1076 = dbasis_0(var_991, var_1075);
            var_1077 = wp::mul(var_1073, var_1076);
            var_1078 = wp::vec_t<3, wp::float64>(var_1067, var_1072, var_1077);
            var_1079 = wp::div(var_1078, var_h);
            wp::array_store(var_g, var_0, var_997, var_1079);
            var_1081 = wp::extract(var_999, var_1080);
            var_1082 = wp::float64(var_1081);
            var_1084 = wp::extract(var_999, var_1083);
            var_1085 = wp::float64(var_1084);
            var_1087 = wp::extract(var_999, var_1086);
            var_1088 = wp::float64(var_1087);
            var_1089 = wp::vec_t<3, wp::float64>(var_1082, var_1085, var_1088);
            var_1090 = wp::mul(var_1089, var_h);
            var_1091 = wp::address(var_x, var_0);
            var_1093 = wp::load(var_1091);
            var_1092 = wp::sub(var_1090, var_1093);
            wp::array_store(var_r, var_0, var_997, var_1092);
        }
        var_1094 = wp::where(var_1001, var_986, var_1054);
        var_1095 = wp::where(var_1001, var_987, var_1057);
        var_1096 = wp::where(var_1001, var_988, var_1060);
        // s=9*a+3*b+c;node=base+wp.vec3i(a,b,c);j=node-origin                                    <L 31>
        var_1099 = wp::mul(var_1098, var_989);
        var_1101 = wp::mul(var_1100, var_990);
        var_1102 = wp::add(var_1099, var_1101);
        var_1103 = wp::add(var_1102, var_1097);
        var_1104 = wp::vec_t<3, wp::int32>(var_989, var_990, var_1097);
        var_1105 = wp::add(var_22, var_1104);
        var_1106 = wp::sub(var_1105, var_origin);
        // if j[0]<0 or j[1]<0 or j[2]<0 or j[0]>=dims[0] or j[1]>=dims[1] or j[2]>=dims[2]:wp.atomic_add(bad,0,1);ids[p,s]=0;w[p,s]=wp.float64(0.0);g[p,s]=wp.vec3d(wp.float64(0.0));r[p,s]=wp.vec3d(wp.float64(0.0))       <L 32>
        var_1109 = wp::extract(var_1106, var_1108);
        var_1111 = (var_1109 < var_1110);
        var_1107 = var_1111;
        if (!var_1107) {
            var_1113 = wp::extract(var_1106, var_1112);
            var_1115 = (var_1113 < var_1114);
            var_1107 = var_1107 || var_1115;
        }
        if (!var_1107) {
            var_1117 = wp::extract(var_1106, var_1116);
            var_1119 = (var_1117 < var_1118);
            var_1107 = var_1107 || var_1119;
        }
        if (!var_1107) {
            var_1121 = wp::extract(var_1106, var_1120);
            var_1123 = wp::extract(var_dims, var_1122);
            var_1124 = (var_1121 >= var_1123);
            var_1107 = var_1107 || var_1124;
        }
        if (!var_1107) {
            var_1126 = wp::extract(var_1106, var_1125);
            var_1128 = wp::extract(var_dims, var_1127);
            var_1129 = (var_1126 >= var_1128);
            var_1107 = var_1107 || var_1129;
        }
        if (!var_1107) {
            var_1131 = wp::extract(var_1106, var_1130);
            var_1133 = wp::extract(var_dims, var_1132);
            var_1134 = (var_1131 >= var_1133);
            var_1107 = var_1107 || var_1134;
        }
        if (var_1107) {
            var_1137 = wp::atomic_add(var_bad, var_1135, var_1136);
            wp::array_store(var_ids, var_0, var_1103, var_1138);
            var_1139 = 0.0;
            wp::array_store(var_w, var_0, var_1103, var_1139);
            var_1140 = 0.0;
            var_1141 = wp::vec_t<3, wp::float64>(var_1140);
            wp::array_store(var_g, var_0, var_1103, var_1141);
            var_1142 = 0.0;
            var_1143 = wp::vec_t<3, wp::float64>(var_1142);
            wp::array_store(var_r, var_0, var_1103, var_1143);
        }
        if (!var_1107) {
            // ids[p,s]=(j[0]*dims[1]+j[1])*dims[2]+j[2];wx=basis(a,f[0]);wy=basis(b,f[1]);wz=basis(c,f[2]);w[p,s]=wx*wy*wz;g[p,s]=wp.vec3d(dbasis(a,f[0])*wy*wz,wx*dbasis(b,f[1])*wz,wx*wy*dbasis(c,f[2]))/h;r[p,s]=wp.vec3d(wp.float64(node[0]),wp.float64(node[1]),wp.float64(node[2]))*h-x[p]       <L 34>
            var_1145 = wp::extract(var_1106, var_1144);
            var_1147 = wp::extract(var_dims, var_1146);
            var_1148 = wp::mul(var_1145, var_1147);
            var_1150 = wp::extract(var_1106, var_1149);
            var_1151 = wp::add(var_1148, var_1150);
            var_1153 = wp::extract(var_dims, var_1152);
            var_1154 = wp::mul(var_1151, var_1153);
            var_1156 = wp::extract(var_1106, var_1155);
            var_1157 = wp::add(var_1154, var_1156);
            wp::array_store(var_ids, var_0, var_1103, var_1157);
            var_1159 = wp::extract(var_33, var_1158);
            var_1160 = basis_0(var_989, var_1159);
            var_1162 = wp::extract(var_33, var_1161);
            var_1163 = basis_0(var_990, var_1162);
            var_1165 = wp::extract(var_33, var_1164);
            var_1166 = basis_0(var_1097, var_1165);
            var_1167 = wp::mul(var_1160, var_1163);
            var_1168 = wp::mul(var_1167, var_1166);
            wp::array_store(var_w, var_0, var_1103, var_1168);
            var_1170 = wp::extract(var_33, var_1169);
            var_1171 = dbasis_0(var_989, var_1170);
            var_1172 = wp::mul(var_1171, var_1163);
            var_1173 = wp::mul(var_1172, var_1166);
            var_1175 = wp::extract(var_33, var_1174);
            var_1176 = dbasis_0(var_990, var_1175);
            var_1177 = wp::mul(var_1160, var_1176);
            var_1178 = wp::mul(var_1177, var_1166);
            var_1179 = wp::mul(var_1160, var_1163);
            var_1181 = wp::extract(var_33, var_1180);
            var_1182 = dbasis_0(var_1097, var_1181);
            var_1183 = wp::mul(var_1179, var_1182);
            var_1184 = wp::vec_t<3, wp::float64>(var_1173, var_1178, var_1183);
            var_1185 = wp::div(var_1184, var_h);
            wp::array_store(var_g, var_0, var_1103, var_1185);
            var_1187 = wp::extract(var_1105, var_1186);
            var_1188 = wp::float64(var_1187);
            var_1190 = wp::extract(var_1105, var_1189);
            var_1191 = wp::float64(var_1190);
            var_1193 = wp::extract(var_1105, var_1192);
            var_1194 = wp::float64(var_1193);
            var_1195 = wp::vec_t<3, wp::float64>(var_1188, var_1191, var_1194);
            var_1196 = wp::mul(var_1195, var_h);
            var_1197 = wp::address(var_x, var_0);
            var_1199 = wp::load(var_1197);
            var_1198 = wp::sub(var_1196, var_1199);
            wp::array_store(var_r, var_0, var_1103, var_1198);
        }
        var_1200 = wp::where(var_1107, var_1094, var_1160);
        var_1201 = wp::where(var_1107, var_1095, var_1163);
        var_1202 = wp::where(var_1107, var_1096, var_1166);
        // s=9*a+3*b+c;node=base+wp.vec3i(a,b,c);j=node-origin                                    <L 31>
        var_1205 = wp::mul(var_1204, var_989);
        var_1207 = wp::mul(var_1206, var_990);
        var_1208 = wp::add(var_1205, var_1207);
        var_1209 = wp::add(var_1208, var_1203);
        var_1210 = wp::vec_t<3, wp::int32>(var_989, var_990, var_1203);
        var_1211 = wp::add(var_22, var_1210);
        var_1212 = wp::sub(var_1211, var_origin);
        // if j[0]<0 or j[1]<0 or j[2]<0 or j[0]>=dims[0] or j[1]>=dims[1] or j[2]>=dims[2]:wp.atomic_add(bad,0,1);ids[p,s]=0;w[p,s]=wp.float64(0.0);g[p,s]=wp.vec3d(wp.float64(0.0));r[p,s]=wp.vec3d(wp.float64(0.0))       <L 32>
        var_1215 = wp::extract(var_1212, var_1214);
        var_1217 = (var_1215 < var_1216);
        var_1213 = var_1217;
        if (!var_1213) {
            var_1219 = wp::extract(var_1212, var_1218);
            var_1221 = (var_1219 < var_1220);
            var_1213 = var_1213 || var_1221;
        }
        if (!var_1213) {
            var_1223 = wp::extract(var_1212, var_1222);
            var_1225 = (var_1223 < var_1224);
            var_1213 = var_1213 || var_1225;
        }
        if (!var_1213) {
            var_1227 = wp::extract(var_1212, var_1226);
            var_1229 = wp::extract(var_dims, var_1228);
            var_1230 = (var_1227 >= var_1229);
            var_1213 = var_1213 || var_1230;
        }
        if (!var_1213) {
            var_1232 = wp::extract(var_1212, var_1231);
            var_1234 = wp::extract(var_dims, var_1233);
            var_1235 = (var_1232 >= var_1234);
            var_1213 = var_1213 || var_1235;
        }
        if (!var_1213) {
            var_1237 = wp::extract(var_1212, var_1236);
            var_1239 = wp::extract(var_dims, var_1238);
            var_1240 = (var_1237 >= var_1239);
            var_1213 = var_1213 || var_1240;
        }
        if (var_1213) {
            var_1243 = wp::atomic_add(var_bad, var_1241, var_1242);
            wp::array_store(var_ids, var_0, var_1209, var_1244);
            var_1245 = 0.0;
            wp::array_store(var_w, var_0, var_1209, var_1245);
            var_1246 = 0.0;
            var_1247 = wp::vec_t<3, wp::float64>(var_1246);
            wp::array_store(var_g, var_0, var_1209, var_1247);
            var_1248 = 0.0;
            var_1249 = wp::vec_t<3, wp::float64>(var_1248);
            wp::array_store(var_r, var_0, var_1209, var_1249);
        }
        if (!var_1213) {
            // ids[p,s]=(j[0]*dims[1]+j[1])*dims[2]+j[2];wx=basis(a,f[0]);wy=basis(b,f[1]);wz=basis(c,f[2]);w[p,s]=wx*wy*wz;g[p,s]=wp.vec3d(dbasis(a,f[0])*wy*wz,wx*dbasis(b,f[1])*wz,wx*wy*dbasis(c,f[2]))/h;r[p,s]=wp.vec3d(wp.float64(node[0]),wp.float64(node[1]),wp.float64(node[2]))*h-x[p]       <L 34>
            var_1251 = wp::extract(var_1212, var_1250);
            var_1253 = wp::extract(var_dims, var_1252);
            var_1254 = wp::mul(var_1251, var_1253);
            var_1256 = wp::extract(var_1212, var_1255);
            var_1257 = wp::add(var_1254, var_1256);
            var_1259 = wp::extract(var_dims, var_1258);
            var_1260 = wp::mul(var_1257, var_1259);
            var_1262 = wp::extract(var_1212, var_1261);
            var_1263 = wp::add(var_1260, var_1262);
            wp::array_store(var_ids, var_0, var_1209, var_1263);
            var_1265 = wp::extract(var_33, var_1264);
            var_1266 = basis_0(var_989, var_1265);
            var_1268 = wp::extract(var_33, var_1267);
            var_1269 = basis_0(var_990, var_1268);
            var_1271 = wp::extract(var_33, var_1270);
            var_1272 = basis_0(var_1203, var_1271);
            var_1273 = wp::mul(var_1266, var_1269);
            var_1274 = wp::mul(var_1273, var_1272);
            wp::array_store(var_w, var_0, var_1209, var_1274);
            var_1276 = wp::extract(var_33, var_1275);
            var_1277 = dbasis_0(var_989, var_1276);
            var_1278 = wp::mul(var_1277, var_1269);
            var_1279 = wp::mul(var_1278, var_1272);
            var_1281 = wp::extract(var_33, var_1280);
            var_1282 = dbasis_0(var_990, var_1281);
            var_1283 = wp::mul(var_1266, var_1282);
            var_1284 = wp::mul(var_1283, var_1272);
            var_1285 = wp::mul(var_1266, var_1269);
            var_1287 = wp::extract(var_33, var_1286);
            var_1288 = dbasis_0(var_1203, var_1287);
            var_1289 = wp::mul(var_1285, var_1288);
            var_1290 = wp::vec_t<3, wp::float64>(var_1279, var_1284, var_1289);
            var_1291 = wp::div(var_1290, var_h);
            wp::array_store(var_g, var_0, var_1209, var_1291);
            var_1293 = wp::extract(var_1211, var_1292);
            var_1294 = wp::float64(var_1293);
            var_1296 = wp::extract(var_1211, var_1295);
            var_1297 = wp::float64(var_1296);
            var_1299 = wp::extract(var_1211, var_1298);
            var_1300 = wp::float64(var_1299);
            var_1301 = wp::vec_t<3, wp::float64>(var_1294, var_1297, var_1300);
            var_1302 = wp::mul(var_1301, var_h);
            var_1303 = wp::address(var_x, var_0);
            var_1305 = wp::load(var_1303);
            var_1304 = wp::sub(var_1302, var_1305);
            wp::array_store(var_r, var_0, var_1209, var_1304);
        }
        var_1306 = wp::where(var_1213, var_1200, var_1266);
        var_1307 = wp::where(var_1213, var_1201, var_1269);
        var_1308 = wp::where(var_1213, var_1202, var_1272);
        // for c in range(3):                                                                     <L 30>
        // s=9*a+3*b+c;node=base+wp.vec3i(a,b,c);j=node-origin                                    <L 31>
        var_1312 = wp::mul(var_1311, var_989);
        var_1314 = wp::mul(var_1313, var_1309);
        var_1315 = wp::add(var_1312, var_1314);
        var_1316 = wp::add(var_1315, var_1310);
        var_1317 = wp::vec_t<3, wp::int32>(var_989, var_1309, var_1310);
        var_1318 = wp::add(var_22, var_1317);
        var_1319 = wp::sub(var_1318, var_origin);
        // if j[0]<0 or j[1]<0 or j[2]<0 or j[0]>=dims[0] or j[1]>=dims[1] or j[2]>=dims[2]:wp.atomic_add(bad,0,1);ids[p,s]=0;w[p,s]=wp.float64(0.0);g[p,s]=wp.vec3d(wp.float64(0.0));r[p,s]=wp.vec3d(wp.float64(0.0))       <L 32>
        var_1322 = wp::extract(var_1319, var_1321);
        var_1324 = (var_1322 < var_1323);
        var_1320 = var_1324;
        if (!var_1320) {
            var_1326 = wp::extract(var_1319, var_1325);
            var_1328 = (var_1326 < var_1327);
            var_1320 = var_1320 || var_1328;
        }
        if (!var_1320) {
            var_1330 = wp::extract(var_1319, var_1329);
            var_1332 = (var_1330 < var_1331);
            var_1320 = var_1320 || var_1332;
        }
        if (!var_1320) {
            var_1334 = wp::extract(var_1319, var_1333);
            var_1336 = wp::extract(var_dims, var_1335);
            var_1337 = (var_1334 >= var_1336);
            var_1320 = var_1320 || var_1337;
        }
        if (!var_1320) {
            var_1339 = wp::extract(var_1319, var_1338);
            var_1341 = wp::extract(var_dims, var_1340);
            var_1342 = (var_1339 >= var_1341);
            var_1320 = var_1320 || var_1342;
        }
        if (!var_1320) {
            var_1344 = wp::extract(var_1319, var_1343);
            var_1346 = wp::extract(var_dims, var_1345);
            var_1347 = (var_1344 >= var_1346);
            var_1320 = var_1320 || var_1347;
        }
        if (var_1320) {
            var_1350 = wp::atomic_add(var_bad, var_1348, var_1349);
            wp::array_store(var_ids, var_0, var_1316, var_1351);
            var_1352 = 0.0;
            wp::array_store(var_w, var_0, var_1316, var_1352);
            var_1353 = 0.0;
            var_1354 = wp::vec_t<3, wp::float64>(var_1353);
            wp::array_store(var_g, var_0, var_1316, var_1354);
            var_1355 = 0.0;
            var_1356 = wp::vec_t<3, wp::float64>(var_1355);
            wp::array_store(var_r, var_0, var_1316, var_1356);
        }
        if (!var_1320) {
            // ids[p,s]=(j[0]*dims[1]+j[1])*dims[2]+j[2];wx=basis(a,f[0]);wy=basis(b,f[1]);wz=basis(c,f[2]);w[p,s]=wx*wy*wz;g[p,s]=wp.vec3d(dbasis(a,f[0])*wy*wz,wx*dbasis(b,f[1])*wz,wx*wy*dbasis(c,f[2]))/h;r[p,s]=wp.vec3d(wp.float64(node[0]),wp.float64(node[1]),wp.float64(node[2]))*h-x[p]       <L 34>
            var_1358 = wp::extract(var_1319, var_1357);
            var_1360 = wp::extract(var_dims, var_1359);
            var_1361 = wp::mul(var_1358, var_1360);
            var_1363 = wp::extract(var_1319, var_1362);
            var_1364 = wp::add(var_1361, var_1363);
            var_1366 = wp::extract(var_dims, var_1365);
            var_1367 = wp::mul(var_1364, var_1366);
            var_1369 = wp::extract(var_1319, var_1368);
            var_1370 = wp::add(var_1367, var_1369);
            wp::array_store(var_ids, var_0, var_1316, var_1370);
            var_1372 = wp::extract(var_33, var_1371);
            var_1373 = basis_0(var_989, var_1372);
            var_1375 = wp::extract(var_33, var_1374);
            var_1376 = basis_0(var_1309, var_1375);
            var_1378 = wp::extract(var_33, var_1377);
            var_1379 = basis_0(var_1310, var_1378);
            var_1380 = wp::mul(var_1373, var_1376);
            var_1381 = wp::mul(var_1380, var_1379);
            wp::array_store(var_w, var_0, var_1316, var_1381);
            var_1383 = wp::extract(var_33, var_1382);
            var_1384 = dbasis_0(var_989, var_1383);
            var_1385 = wp::mul(var_1384, var_1376);
            var_1386 = wp::mul(var_1385, var_1379);
            var_1388 = wp::extract(var_33, var_1387);
            var_1389 = dbasis_0(var_1309, var_1388);
            var_1390 = wp::mul(var_1373, var_1389);
            var_1391 = wp::mul(var_1390, var_1379);
            var_1392 = wp::mul(var_1373, var_1376);
            var_1394 = wp::extract(var_33, var_1393);
            var_1395 = dbasis_0(var_1310, var_1394);
            var_1396 = wp::mul(var_1392, var_1395);
            var_1397 = wp::vec_t<3, wp::float64>(var_1386, var_1391, var_1396);
            var_1398 = wp::div(var_1397, var_h);
            wp::array_store(var_g, var_0, var_1316, var_1398);
            var_1400 = wp::extract(var_1318, var_1399);
            var_1401 = wp::float64(var_1400);
            var_1403 = wp::extract(var_1318, var_1402);
            var_1404 = wp::float64(var_1403);
            var_1406 = wp::extract(var_1318, var_1405);
            var_1407 = wp::float64(var_1406);
            var_1408 = wp::vec_t<3, wp::float64>(var_1401, var_1404, var_1407);
            var_1409 = wp::mul(var_1408, var_h);
            var_1410 = wp::address(var_x, var_0);
            var_1412 = wp::load(var_1410);
            var_1411 = wp::sub(var_1409, var_1412);
            wp::array_store(var_r, var_0, var_1316, var_1411);
        }
        var_1413 = wp::where(var_1320, var_1306, var_1373);
        var_1414 = wp::where(var_1320, var_1307, var_1376);
        var_1415 = wp::where(var_1320, var_1308, var_1379);
        // s=9*a+3*b+c;node=base+wp.vec3i(a,b,c);j=node-origin                                    <L 31>
        var_1418 = wp::mul(var_1417, var_989);
        var_1420 = wp::mul(var_1419, var_1309);
        var_1421 = wp::add(var_1418, var_1420);
        var_1422 = wp::add(var_1421, var_1416);
        var_1423 = wp::vec_t<3, wp::int32>(var_989, var_1309, var_1416);
        var_1424 = wp::add(var_22, var_1423);
        var_1425 = wp::sub(var_1424, var_origin);
        // if j[0]<0 or j[1]<0 or j[2]<0 or j[0]>=dims[0] or j[1]>=dims[1] or j[2]>=dims[2]:wp.atomic_add(bad,0,1);ids[p,s]=0;w[p,s]=wp.float64(0.0);g[p,s]=wp.vec3d(wp.float64(0.0));r[p,s]=wp.vec3d(wp.float64(0.0))       <L 32>
        var_1428 = wp::extract(var_1425, var_1427);
        var_1430 = (var_1428 < var_1429);
        var_1426 = var_1430;
        if (!var_1426) {
            var_1432 = wp::extract(var_1425, var_1431);
            var_1434 = (var_1432 < var_1433);
            var_1426 = var_1426 || var_1434;
        }
        if (!var_1426) {
            var_1436 = wp::extract(var_1425, var_1435);
            var_1438 = (var_1436 < var_1437);
            var_1426 = var_1426 || var_1438;
        }
        if (!var_1426) {
            var_1440 = wp::extract(var_1425, var_1439);
            var_1442 = wp::extract(var_dims, var_1441);
            var_1443 = (var_1440 >= var_1442);
            var_1426 = var_1426 || var_1443;
        }
        if (!var_1426) {
            var_1445 = wp::extract(var_1425, var_1444);
            var_1447 = wp::extract(var_dims, var_1446);
            var_1448 = (var_1445 >= var_1447);
            var_1426 = var_1426 || var_1448;
        }
        if (!var_1426) {
            var_1450 = wp::extract(var_1425, var_1449);
            var_1452 = wp::extract(var_dims, var_1451);
            var_1453 = (var_1450 >= var_1452);
            var_1426 = var_1426 || var_1453;
        }
        if (var_1426) {
            var_1456 = wp::atomic_add(var_bad, var_1454, var_1455);
            wp::array_store(var_ids, var_0, var_1422, var_1457);
            var_1458 = 0.0;
            wp::array_store(var_w, var_0, var_1422, var_1458);
            var_1459 = 0.0;
            var_1460 = wp::vec_t<3, wp::float64>(var_1459);
            wp::array_store(var_g, var_0, var_1422, var_1460);
            var_1461 = 0.0;
            var_1462 = wp::vec_t<3, wp::float64>(var_1461);
            wp::array_store(var_r, var_0, var_1422, var_1462);
        }
        if (!var_1426) {
            // ids[p,s]=(j[0]*dims[1]+j[1])*dims[2]+j[2];wx=basis(a,f[0]);wy=basis(b,f[1]);wz=basis(c,f[2]);w[p,s]=wx*wy*wz;g[p,s]=wp.vec3d(dbasis(a,f[0])*wy*wz,wx*dbasis(b,f[1])*wz,wx*wy*dbasis(c,f[2]))/h;r[p,s]=wp.vec3d(wp.float64(node[0]),wp.float64(node[1]),wp.float64(node[2]))*h-x[p]       <L 34>
            var_1464 = wp::extract(var_1425, var_1463);
            var_1466 = wp::extract(var_dims, var_1465);
            var_1467 = wp::mul(var_1464, var_1466);
            var_1469 = wp::extract(var_1425, var_1468);
            var_1470 = wp::add(var_1467, var_1469);
            var_1472 = wp::extract(var_dims, var_1471);
            var_1473 = wp::mul(var_1470, var_1472);
            var_1475 = wp::extract(var_1425, var_1474);
            var_1476 = wp::add(var_1473, var_1475);
            wp::array_store(var_ids, var_0, var_1422, var_1476);
            var_1478 = wp::extract(var_33, var_1477);
            var_1479 = basis_0(var_989, var_1478);
            var_1481 = wp::extract(var_33, var_1480);
            var_1482 = basis_0(var_1309, var_1481);
            var_1484 = wp::extract(var_33, var_1483);
            var_1485 = basis_0(var_1416, var_1484);
            var_1486 = wp::mul(var_1479, var_1482);
            var_1487 = wp::mul(var_1486, var_1485);
            wp::array_store(var_w, var_0, var_1422, var_1487);
            var_1489 = wp::extract(var_33, var_1488);
            var_1490 = dbasis_0(var_989, var_1489);
            var_1491 = wp::mul(var_1490, var_1482);
            var_1492 = wp::mul(var_1491, var_1485);
            var_1494 = wp::extract(var_33, var_1493);
            var_1495 = dbasis_0(var_1309, var_1494);
            var_1496 = wp::mul(var_1479, var_1495);
            var_1497 = wp::mul(var_1496, var_1485);
            var_1498 = wp::mul(var_1479, var_1482);
            var_1500 = wp::extract(var_33, var_1499);
            var_1501 = dbasis_0(var_1416, var_1500);
            var_1502 = wp::mul(var_1498, var_1501);
            var_1503 = wp::vec_t<3, wp::float64>(var_1492, var_1497, var_1502);
            var_1504 = wp::div(var_1503, var_h);
            wp::array_store(var_g, var_0, var_1422, var_1504);
            var_1506 = wp::extract(var_1424, var_1505);
            var_1507 = wp::float64(var_1506);
            var_1509 = wp::extract(var_1424, var_1508);
            var_1510 = wp::float64(var_1509);
            var_1512 = wp::extract(var_1424, var_1511);
            var_1513 = wp::float64(var_1512);
            var_1514 = wp::vec_t<3, wp::float64>(var_1507, var_1510, var_1513);
            var_1515 = wp::mul(var_1514, var_h);
            var_1516 = wp::address(var_x, var_0);
            var_1518 = wp::load(var_1516);
            var_1517 = wp::sub(var_1515, var_1518);
            wp::array_store(var_r, var_0, var_1422, var_1517);
        }
        var_1519 = wp::where(var_1426, var_1413, var_1479);
        var_1520 = wp::where(var_1426, var_1414, var_1482);
        var_1521 = wp::where(var_1426, var_1415, var_1485);
        // s=9*a+3*b+c;node=base+wp.vec3i(a,b,c);j=node-origin                                    <L 31>
        var_1524 = wp::mul(var_1523, var_989);
        var_1526 = wp::mul(var_1525, var_1309);
        var_1527 = wp::add(var_1524, var_1526);
        var_1528 = wp::add(var_1527, var_1522);
        var_1529 = wp::vec_t<3, wp::int32>(var_989, var_1309, var_1522);
        var_1530 = wp::add(var_22, var_1529);
        var_1531 = wp::sub(var_1530, var_origin);
        // if j[0]<0 or j[1]<0 or j[2]<0 or j[0]>=dims[0] or j[1]>=dims[1] or j[2]>=dims[2]:wp.atomic_add(bad,0,1);ids[p,s]=0;w[p,s]=wp.float64(0.0);g[p,s]=wp.vec3d(wp.float64(0.0));r[p,s]=wp.vec3d(wp.float64(0.0))       <L 32>
        var_1534 = wp::extract(var_1531, var_1533);
        var_1536 = (var_1534 < var_1535);
        var_1532 = var_1536;
        if (!var_1532) {
            var_1538 = wp::extract(var_1531, var_1537);
            var_1540 = (var_1538 < var_1539);
            var_1532 = var_1532 || var_1540;
        }
        if (!var_1532) {
            var_1542 = wp::extract(var_1531, var_1541);
            var_1544 = (var_1542 < var_1543);
            var_1532 = var_1532 || var_1544;
        }
        if (!var_1532) {
            var_1546 = wp::extract(var_1531, var_1545);
            var_1548 = wp::extract(var_dims, var_1547);
            var_1549 = (var_1546 >= var_1548);
            var_1532 = var_1532 || var_1549;
        }
        if (!var_1532) {
            var_1551 = wp::extract(var_1531, var_1550);
            var_1553 = wp::extract(var_dims, var_1552);
            var_1554 = (var_1551 >= var_1553);
            var_1532 = var_1532 || var_1554;
        }
        if (!var_1532) {
            var_1556 = wp::extract(var_1531, var_1555);
            var_1558 = wp::extract(var_dims, var_1557);
            var_1559 = (var_1556 >= var_1558);
            var_1532 = var_1532 || var_1559;
        }
        if (var_1532) {
            var_1562 = wp::atomic_add(var_bad, var_1560, var_1561);
            wp::array_store(var_ids, var_0, var_1528, var_1563);
            var_1564 = 0.0;
            wp::array_store(var_w, var_0, var_1528, var_1564);
            var_1565 = 0.0;
            var_1566 = wp::vec_t<3, wp::float64>(var_1565);
            wp::array_store(var_g, var_0, var_1528, var_1566);
            var_1567 = 0.0;
            var_1568 = wp::vec_t<3, wp::float64>(var_1567);
            wp::array_store(var_r, var_0, var_1528, var_1568);
        }
        if (!var_1532) {
            // ids[p,s]=(j[0]*dims[1]+j[1])*dims[2]+j[2];wx=basis(a,f[0]);wy=basis(b,f[1]);wz=basis(c,f[2]);w[p,s]=wx*wy*wz;g[p,s]=wp.vec3d(dbasis(a,f[0])*wy*wz,wx*dbasis(b,f[1])*wz,wx*wy*dbasis(c,f[2]))/h;r[p,s]=wp.vec3d(wp.float64(node[0]),wp.float64(node[1]),wp.float64(node[2]))*h-x[p]       <L 34>
            var_1570 = wp::extract(var_1531, var_1569);
            var_1572 = wp::extract(var_dims, var_1571);
            var_1573 = wp::mul(var_1570, var_1572);
            var_1575 = wp::extract(var_1531, var_1574);
            var_1576 = wp::add(var_1573, var_1575);
            var_1578 = wp::extract(var_dims, var_1577);
            var_1579 = wp::mul(var_1576, var_1578);
            var_1581 = wp::extract(var_1531, var_1580);
            var_1582 = wp::add(var_1579, var_1581);
            wp::array_store(var_ids, var_0, var_1528, var_1582);
            var_1584 = wp::extract(var_33, var_1583);
            var_1585 = basis_0(var_989, var_1584);
            var_1587 = wp::extract(var_33, var_1586);
            var_1588 = basis_0(var_1309, var_1587);
            var_1590 = wp::extract(var_33, var_1589);
            var_1591 = basis_0(var_1522, var_1590);
            var_1592 = wp::mul(var_1585, var_1588);
            var_1593 = wp::mul(var_1592, var_1591);
            wp::array_store(var_w, var_0, var_1528, var_1593);
            var_1595 = wp::extract(var_33, var_1594);
            var_1596 = dbasis_0(var_989, var_1595);
            var_1597 = wp::mul(var_1596, var_1588);
            var_1598 = wp::mul(var_1597, var_1591);
            var_1600 = wp::extract(var_33, var_1599);
            var_1601 = dbasis_0(var_1309, var_1600);
            var_1602 = wp::mul(var_1585, var_1601);
            var_1603 = wp::mul(var_1602, var_1591);
            var_1604 = wp::mul(var_1585, var_1588);
            var_1606 = wp::extract(var_33, var_1605);
            var_1607 = dbasis_0(var_1522, var_1606);
            var_1608 = wp::mul(var_1604, var_1607);
            var_1609 = wp::vec_t<3, wp::float64>(var_1598, var_1603, var_1608);
            var_1610 = wp::div(var_1609, var_h);
            wp::array_store(var_g, var_0, var_1528, var_1610);
            var_1612 = wp::extract(var_1530, var_1611);
            var_1613 = wp::float64(var_1612);
            var_1615 = wp::extract(var_1530, var_1614);
            var_1616 = wp::float64(var_1615);
            var_1618 = wp::extract(var_1530, var_1617);
            var_1619 = wp::float64(var_1618);
            var_1620 = wp::vec_t<3, wp::float64>(var_1613, var_1616, var_1619);
            var_1621 = wp::mul(var_1620, var_h);
            var_1622 = wp::address(var_x, var_0);
            var_1624 = wp::load(var_1622);
            var_1623 = wp::sub(var_1621, var_1624);
            wp::array_store(var_r, var_0, var_1528, var_1623);
        }
        var_1625 = wp::where(var_1532, var_1519, var_1585);
        var_1626 = wp::where(var_1532, var_1520, var_1588);
        var_1627 = wp::where(var_1532, var_1521, var_1591);
        // for c in range(3):                                                                     <L 30>
        // s=9*a+3*b+c;node=base+wp.vec3i(a,b,c);j=node-origin                                    <L 31>
        var_1631 = wp::mul(var_1630, var_989);
        var_1633 = wp::mul(var_1632, var_1628);
        var_1634 = wp::add(var_1631, var_1633);
        var_1635 = wp::add(var_1634, var_1629);
        var_1636 = wp::vec_t<3, wp::int32>(var_989, var_1628, var_1629);
        var_1637 = wp::add(var_22, var_1636);
        var_1638 = wp::sub(var_1637, var_origin);
        // if j[0]<0 or j[1]<0 or j[2]<0 or j[0]>=dims[0] or j[1]>=dims[1] or j[2]>=dims[2]:wp.atomic_add(bad,0,1);ids[p,s]=0;w[p,s]=wp.float64(0.0);g[p,s]=wp.vec3d(wp.float64(0.0));r[p,s]=wp.vec3d(wp.float64(0.0))       <L 32>
        var_1641 = wp::extract(var_1638, var_1640);
        var_1643 = (var_1641 < var_1642);
        var_1639 = var_1643;
        if (!var_1639) {
            var_1645 = wp::extract(var_1638, var_1644);
            var_1647 = (var_1645 < var_1646);
            var_1639 = var_1639 || var_1647;
        }
        if (!var_1639) {
            var_1649 = wp::extract(var_1638, var_1648);
            var_1651 = (var_1649 < var_1650);
            var_1639 = var_1639 || var_1651;
        }
        if (!var_1639) {
            var_1653 = wp::extract(var_1638, var_1652);
            var_1655 = wp::extract(var_dims, var_1654);
            var_1656 = (var_1653 >= var_1655);
            var_1639 = var_1639 || var_1656;
        }
        if (!var_1639) {
            var_1658 = wp::extract(var_1638, var_1657);
            var_1660 = wp::extract(var_dims, var_1659);
            var_1661 = (var_1658 >= var_1660);
            var_1639 = var_1639 || var_1661;
        }
        if (!var_1639) {
            var_1663 = wp::extract(var_1638, var_1662);
            var_1665 = wp::extract(var_dims, var_1664);
            var_1666 = (var_1663 >= var_1665);
            var_1639 = var_1639 || var_1666;
        }
        if (var_1639) {
            var_1669 = wp::atomic_add(var_bad, var_1667, var_1668);
            wp::array_store(var_ids, var_0, var_1635, var_1670);
            var_1671 = 0.0;
            wp::array_store(var_w, var_0, var_1635, var_1671);
            var_1672 = 0.0;
            var_1673 = wp::vec_t<3, wp::float64>(var_1672);
            wp::array_store(var_g, var_0, var_1635, var_1673);
            var_1674 = 0.0;
            var_1675 = wp::vec_t<3, wp::float64>(var_1674);
            wp::array_store(var_r, var_0, var_1635, var_1675);
        }
        if (!var_1639) {
            // ids[p,s]=(j[0]*dims[1]+j[1])*dims[2]+j[2];wx=basis(a,f[0]);wy=basis(b,f[1]);wz=basis(c,f[2]);w[p,s]=wx*wy*wz;g[p,s]=wp.vec3d(dbasis(a,f[0])*wy*wz,wx*dbasis(b,f[1])*wz,wx*wy*dbasis(c,f[2]))/h;r[p,s]=wp.vec3d(wp.float64(node[0]),wp.float64(node[1]),wp.float64(node[2]))*h-x[p]       <L 34>
            var_1677 = wp::extract(var_1638, var_1676);
            var_1679 = wp::extract(var_dims, var_1678);
            var_1680 = wp::mul(var_1677, var_1679);
            var_1682 = wp::extract(var_1638, var_1681);
            var_1683 = wp::add(var_1680, var_1682);
            var_1685 = wp::extract(var_dims, var_1684);
            var_1686 = wp::mul(var_1683, var_1685);
            var_1688 = wp::extract(var_1638, var_1687);
            var_1689 = wp::add(var_1686, var_1688);
            wp::array_store(var_ids, var_0, var_1635, var_1689);
            var_1691 = wp::extract(var_33, var_1690);
            var_1692 = basis_0(var_989, var_1691);
            var_1694 = wp::extract(var_33, var_1693);
            var_1695 = basis_0(var_1628, var_1694);
            var_1697 = wp::extract(var_33, var_1696);
            var_1698 = basis_0(var_1629, var_1697);
            var_1699 = wp::mul(var_1692, var_1695);
            var_1700 = wp::mul(var_1699, var_1698);
            wp::array_store(var_w, var_0, var_1635, var_1700);
            var_1702 = wp::extract(var_33, var_1701);
            var_1703 = dbasis_0(var_989, var_1702);
            var_1704 = wp::mul(var_1703, var_1695);
            var_1705 = wp::mul(var_1704, var_1698);
            var_1707 = wp::extract(var_33, var_1706);
            var_1708 = dbasis_0(var_1628, var_1707);
            var_1709 = wp::mul(var_1692, var_1708);
            var_1710 = wp::mul(var_1709, var_1698);
            var_1711 = wp::mul(var_1692, var_1695);
            var_1713 = wp::extract(var_33, var_1712);
            var_1714 = dbasis_0(var_1629, var_1713);
            var_1715 = wp::mul(var_1711, var_1714);
            var_1716 = wp::vec_t<3, wp::float64>(var_1705, var_1710, var_1715);
            var_1717 = wp::div(var_1716, var_h);
            wp::array_store(var_g, var_0, var_1635, var_1717);
            var_1719 = wp::extract(var_1637, var_1718);
            var_1720 = wp::float64(var_1719);
            var_1722 = wp::extract(var_1637, var_1721);
            var_1723 = wp::float64(var_1722);
            var_1725 = wp::extract(var_1637, var_1724);
            var_1726 = wp::float64(var_1725);
            var_1727 = wp::vec_t<3, wp::float64>(var_1720, var_1723, var_1726);
            var_1728 = wp::mul(var_1727, var_h);
            var_1729 = wp::address(var_x, var_0);
            var_1731 = wp::load(var_1729);
            var_1730 = wp::sub(var_1728, var_1731);
            wp::array_store(var_r, var_0, var_1635, var_1730);
        }
        var_1732 = wp::where(var_1639, var_1625, var_1692);
        var_1733 = wp::where(var_1639, var_1626, var_1695);
        var_1734 = wp::where(var_1639, var_1627, var_1698);
        // s=9*a+3*b+c;node=base+wp.vec3i(a,b,c);j=node-origin                                    <L 31>
        var_1737 = wp::mul(var_1736, var_989);
        var_1739 = wp::mul(var_1738, var_1628);
        var_1740 = wp::add(var_1737, var_1739);
        var_1741 = wp::add(var_1740, var_1735);
        var_1742 = wp::vec_t<3, wp::int32>(var_989, var_1628, var_1735);
        var_1743 = wp::add(var_22, var_1742);
        var_1744 = wp::sub(var_1743, var_origin);
        // if j[0]<0 or j[1]<0 or j[2]<0 or j[0]>=dims[0] or j[1]>=dims[1] or j[2]>=dims[2]:wp.atomic_add(bad,0,1);ids[p,s]=0;w[p,s]=wp.float64(0.0);g[p,s]=wp.vec3d(wp.float64(0.0));r[p,s]=wp.vec3d(wp.float64(0.0))       <L 32>
        var_1747 = wp::extract(var_1744, var_1746);
        var_1749 = (var_1747 < var_1748);
        var_1745 = var_1749;
        if (!var_1745) {
            var_1751 = wp::extract(var_1744, var_1750);
            var_1753 = (var_1751 < var_1752);
            var_1745 = var_1745 || var_1753;
        }
        if (!var_1745) {
            var_1755 = wp::extract(var_1744, var_1754);
            var_1757 = (var_1755 < var_1756);
            var_1745 = var_1745 || var_1757;
        }
        if (!var_1745) {
            var_1759 = wp::extract(var_1744, var_1758);
            var_1761 = wp::extract(var_dims, var_1760);
            var_1762 = (var_1759 >= var_1761);
            var_1745 = var_1745 || var_1762;
        }
        if (!var_1745) {
            var_1764 = wp::extract(var_1744, var_1763);
            var_1766 = wp::extract(var_dims, var_1765);
            var_1767 = (var_1764 >= var_1766);
            var_1745 = var_1745 || var_1767;
        }
        if (!var_1745) {
            var_1769 = wp::extract(var_1744, var_1768);
            var_1771 = wp::extract(var_dims, var_1770);
            var_1772 = (var_1769 >= var_1771);
            var_1745 = var_1745 || var_1772;
        }
        if (var_1745) {
            var_1775 = wp::atomic_add(var_bad, var_1773, var_1774);
            wp::array_store(var_ids, var_0, var_1741, var_1776);
            var_1777 = 0.0;
            wp::array_store(var_w, var_0, var_1741, var_1777);
            var_1778 = 0.0;
            var_1779 = wp::vec_t<3, wp::float64>(var_1778);
            wp::array_store(var_g, var_0, var_1741, var_1779);
            var_1780 = 0.0;
            var_1781 = wp::vec_t<3, wp::float64>(var_1780);
            wp::array_store(var_r, var_0, var_1741, var_1781);
        }
        if (!var_1745) {
            // ids[p,s]=(j[0]*dims[1]+j[1])*dims[2]+j[2];wx=basis(a,f[0]);wy=basis(b,f[1]);wz=basis(c,f[2]);w[p,s]=wx*wy*wz;g[p,s]=wp.vec3d(dbasis(a,f[0])*wy*wz,wx*dbasis(b,f[1])*wz,wx*wy*dbasis(c,f[2]))/h;r[p,s]=wp.vec3d(wp.float64(node[0]),wp.float64(node[1]),wp.float64(node[2]))*h-x[p]       <L 34>
            var_1783 = wp::extract(var_1744, var_1782);
            var_1785 = wp::extract(var_dims, var_1784);
            var_1786 = wp::mul(var_1783, var_1785);
            var_1788 = wp::extract(var_1744, var_1787);
            var_1789 = wp::add(var_1786, var_1788);
            var_1791 = wp::extract(var_dims, var_1790);
            var_1792 = wp::mul(var_1789, var_1791);
            var_1794 = wp::extract(var_1744, var_1793);
            var_1795 = wp::add(var_1792, var_1794);
            wp::array_store(var_ids, var_0, var_1741, var_1795);
            var_1797 = wp::extract(var_33, var_1796);
            var_1798 = basis_0(var_989, var_1797);
            var_1800 = wp::extract(var_33, var_1799);
            var_1801 = basis_0(var_1628, var_1800);
            var_1803 = wp::extract(var_33, var_1802);
            var_1804 = basis_0(var_1735, var_1803);
            var_1805 = wp::mul(var_1798, var_1801);
            var_1806 = wp::mul(var_1805, var_1804);
            wp::array_store(var_w, var_0, var_1741, var_1806);
            var_1808 = wp::extract(var_33, var_1807);
            var_1809 = dbasis_0(var_989, var_1808);
            var_1810 = wp::mul(var_1809, var_1801);
            var_1811 = wp::mul(var_1810, var_1804);
            var_1813 = wp::extract(var_33, var_1812);
            var_1814 = dbasis_0(var_1628, var_1813);
            var_1815 = wp::mul(var_1798, var_1814);
            var_1816 = wp::mul(var_1815, var_1804);
            var_1817 = wp::mul(var_1798, var_1801);
            var_1819 = wp::extract(var_33, var_1818);
            var_1820 = dbasis_0(var_1735, var_1819);
            var_1821 = wp::mul(var_1817, var_1820);
            var_1822 = wp::vec_t<3, wp::float64>(var_1811, var_1816, var_1821);
            var_1823 = wp::div(var_1822, var_h);
            wp::array_store(var_g, var_0, var_1741, var_1823);
            var_1825 = wp::extract(var_1743, var_1824);
            var_1826 = wp::float64(var_1825);
            var_1828 = wp::extract(var_1743, var_1827);
            var_1829 = wp::float64(var_1828);
            var_1831 = wp::extract(var_1743, var_1830);
            var_1832 = wp::float64(var_1831);
            var_1833 = wp::vec_t<3, wp::float64>(var_1826, var_1829, var_1832);
            var_1834 = wp::mul(var_1833, var_h);
            var_1835 = wp::address(var_x, var_0);
            var_1837 = wp::load(var_1835);
            var_1836 = wp::sub(var_1834, var_1837);
            wp::array_store(var_r, var_0, var_1741, var_1836);
        }
        var_1838 = wp::where(var_1745, var_1732, var_1798);
        var_1839 = wp::where(var_1745, var_1733, var_1801);
        var_1840 = wp::where(var_1745, var_1734, var_1804);
        // s=9*a+3*b+c;node=base+wp.vec3i(a,b,c);j=node-origin                                    <L 31>
        var_1843 = wp::mul(var_1842, var_989);
        var_1845 = wp::mul(var_1844, var_1628);
        var_1846 = wp::add(var_1843, var_1845);
        var_1847 = wp::add(var_1846, var_1841);
        var_1848 = wp::vec_t<3, wp::int32>(var_989, var_1628, var_1841);
        var_1849 = wp::add(var_22, var_1848);
        var_1850 = wp::sub(var_1849, var_origin);
        // if j[0]<0 or j[1]<0 or j[2]<0 or j[0]>=dims[0] or j[1]>=dims[1] or j[2]>=dims[2]:wp.atomic_add(bad,0,1);ids[p,s]=0;w[p,s]=wp.float64(0.0);g[p,s]=wp.vec3d(wp.float64(0.0));r[p,s]=wp.vec3d(wp.float64(0.0))       <L 32>
        var_1853 = wp::extract(var_1850, var_1852);
        var_1855 = (var_1853 < var_1854);
        var_1851 = var_1855;
        if (!var_1851) {
            var_1857 = wp::extract(var_1850, var_1856);
            var_1859 = (var_1857 < var_1858);
            var_1851 = var_1851 || var_1859;
        }
        if (!var_1851) {
            var_1861 = wp::extract(var_1850, var_1860);
            var_1863 = (var_1861 < var_1862);
            var_1851 = var_1851 || var_1863;
        }
        if (!var_1851) {
            var_1865 = wp::extract(var_1850, var_1864);
            var_1867 = wp::extract(var_dims, var_1866);
            var_1868 = (var_1865 >= var_1867);
            var_1851 = var_1851 || var_1868;
        }
        if (!var_1851) {
            var_1870 = wp::extract(var_1850, var_1869);
            var_1872 = wp::extract(var_dims, var_1871);
            var_1873 = (var_1870 >= var_1872);
            var_1851 = var_1851 || var_1873;
        }
        if (!var_1851) {
            var_1875 = wp::extract(var_1850, var_1874);
            var_1877 = wp::extract(var_dims, var_1876);
            var_1878 = (var_1875 >= var_1877);
            var_1851 = var_1851 || var_1878;
        }
        if (var_1851) {
            var_1881 = wp::atomic_add(var_bad, var_1879, var_1880);
            wp::array_store(var_ids, var_0, var_1847, var_1882);
            var_1883 = 0.0;
            wp::array_store(var_w, var_0, var_1847, var_1883);
            var_1884 = 0.0;
            var_1885 = wp::vec_t<3, wp::float64>(var_1884);
            wp::array_store(var_g, var_0, var_1847, var_1885);
            var_1886 = 0.0;
            var_1887 = wp::vec_t<3, wp::float64>(var_1886);
            wp::array_store(var_r, var_0, var_1847, var_1887);
        }
        if (!var_1851) {
            // ids[p,s]=(j[0]*dims[1]+j[1])*dims[2]+j[2];wx=basis(a,f[0]);wy=basis(b,f[1]);wz=basis(c,f[2]);w[p,s]=wx*wy*wz;g[p,s]=wp.vec3d(dbasis(a,f[0])*wy*wz,wx*dbasis(b,f[1])*wz,wx*wy*dbasis(c,f[2]))/h;r[p,s]=wp.vec3d(wp.float64(node[0]),wp.float64(node[1]),wp.float64(node[2]))*h-x[p]       <L 34>
            var_1889 = wp::extract(var_1850, var_1888);
            var_1891 = wp::extract(var_dims, var_1890);
            var_1892 = wp::mul(var_1889, var_1891);
            var_1894 = wp::extract(var_1850, var_1893);
            var_1895 = wp::add(var_1892, var_1894);
            var_1897 = wp::extract(var_dims, var_1896);
            var_1898 = wp::mul(var_1895, var_1897);
            var_1900 = wp::extract(var_1850, var_1899);
            var_1901 = wp::add(var_1898, var_1900);
            wp::array_store(var_ids, var_0, var_1847, var_1901);
            var_1903 = wp::extract(var_33, var_1902);
            var_1904 = basis_0(var_989, var_1903);
            var_1906 = wp::extract(var_33, var_1905);
            var_1907 = basis_0(var_1628, var_1906);
            var_1909 = wp::extract(var_33, var_1908);
            var_1910 = basis_0(var_1841, var_1909);
            var_1911 = wp::mul(var_1904, var_1907);
            var_1912 = wp::mul(var_1911, var_1910);
            wp::array_store(var_w, var_0, var_1847, var_1912);
            var_1914 = wp::extract(var_33, var_1913);
            var_1915 = dbasis_0(var_989, var_1914);
            var_1916 = wp::mul(var_1915, var_1907);
            var_1917 = wp::mul(var_1916, var_1910);
            var_1919 = wp::extract(var_33, var_1918);
            var_1920 = dbasis_0(var_1628, var_1919);
            var_1921 = wp::mul(var_1904, var_1920);
            var_1922 = wp::mul(var_1921, var_1910);
            var_1923 = wp::mul(var_1904, var_1907);
            var_1925 = wp::extract(var_33, var_1924);
            var_1926 = dbasis_0(var_1841, var_1925);
            var_1927 = wp::mul(var_1923, var_1926);
            var_1928 = wp::vec_t<3, wp::float64>(var_1917, var_1922, var_1927);
            var_1929 = wp::div(var_1928, var_h);
            wp::array_store(var_g, var_0, var_1847, var_1929);
            var_1931 = wp::extract(var_1849, var_1930);
            var_1932 = wp::float64(var_1931);
            var_1934 = wp::extract(var_1849, var_1933);
            var_1935 = wp::float64(var_1934);
            var_1937 = wp::extract(var_1849, var_1936);
            var_1938 = wp::float64(var_1937);
            var_1939 = wp::vec_t<3, wp::float64>(var_1932, var_1935, var_1938);
            var_1940 = wp::mul(var_1939, var_h);
            var_1941 = wp::address(var_x, var_0);
            var_1943 = wp::load(var_1941);
            var_1942 = wp::sub(var_1940, var_1943);
            wp::array_store(var_r, var_0, var_1847, var_1942);
        }
        var_1944 = wp::where(var_1851, var_1838, var_1904);
        var_1945 = wp::where(var_1851, var_1839, var_1907);
        var_1946 = wp::where(var_1851, var_1840, var_1910);
        // for b in range(3):                                                                     <L 29>
        // for c in range(3):                                                                     <L 30>
        // s=9*a+3*b+c;node=base+wp.vec3i(a,b,c);j=node-origin                                    <L 31>
        var_1951 = wp::mul(var_1950, var_1947);
        var_1953 = wp::mul(var_1952, var_1948);
        var_1954 = wp::add(var_1951, var_1953);
        var_1955 = wp::add(var_1954, var_1949);
        var_1956 = wp::vec_t<3, wp::int32>(var_1947, var_1948, var_1949);
        var_1957 = wp::add(var_22, var_1956);
        var_1958 = wp::sub(var_1957, var_origin);
        // if j[0]<0 or j[1]<0 or j[2]<0 or j[0]>=dims[0] or j[1]>=dims[1] or j[2]>=dims[2]:wp.atomic_add(bad,0,1);ids[p,s]=0;w[p,s]=wp.float64(0.0);g[p,s]=wp.vec3d(wp.float64(0.0));r[p,s]=wp.vec3d(wp.float64(0.0))       <L 32>
        var_1961 = wp::extract(var_1958, var_1960);
        var_1963 = (var_1961 < var_1962);
        var_1959 = var_1963;
        if (!var_1959) {
            var_1965 = wp::extract(var_1958, var_1964);
            var_1967 = (var_1965 < var_1966);
            var_1959 = var_1959 || var_1967;
        }
        if (!var_1959) {
            var_1969 = wp::extract(var_1958, var_1968);
            var_1971 = (var_1969 < var_1970);
            var_1959 = var_1959 || var_1971;
        }
        if (!var_1959) {
            var_1973 = wp::extract(var_1958, var_1972);
            var_1975 = wp::extract(var_dims, var_1974);
            var_1976 = (var_1973 >= var_1975);
            var_1959 = var_1959 || var_1976;
        }
        if (!var_1959) {
            var_1978 = wp::extract(var_1958, var_1977);
            var_1980 = wp::extract(var_dims, var_1979);
            var_1981 = (var_1978 >= var_1980);
            var_1959 = var_1959 || var_1981;
        }
        if (!var_1959) {
            var_1983 = wp::extract(var_1958, var_1982);
            var_1985 = wp::extract(var_dims, var_1984);
            var_1986 = (var_1983 >= var_1985);
            var_1959 = var_1959 || var_1986;
        }
        if (var_1959) {
            var_1989 = wp::atomic_add(var_bad, var_1987, var_1988);
            wp::array_store(var_ids, var_0, var_1955, var_1990);
            var_1991 = 0.0;
            wp::array_store(var_w, var_0, var_1955, var_1991);
            var_1992 = 0.0;
            var_1993 = wp::vec_t<3, wp::float64>(var_1992);
            wp::array_store(var_g, var_0, var_1955, var_1993);
            var_1994 = 0.0;
            var_1995 = wp::vec_t<3, wp::float64>(var_1994);
            wp::array_store(var_r, var_0, var_1955, var_1995);
        }
        if (!var_1959) {
            // ids[p,s]=(j[0]*dims[1]+j[1])*dims[2]+j[2];wx=basis(a,f[0]);wy=basis(b,f[1]);wz=basis(c,f[2]);w[p,s]=wx*wy*wz;g[p,s]=wp.vec3d(dbasis(a,f[0])*wy*wz,wx*dbasis(b,f[1])*wz,wx*wy*dbasis(c,f[2]))/h;r[p,s]=wp.vec3d(wp.float64(node[0]),wp.float64(node[1]),wp.float64(node[2]))*h-x[p]       <L 34>
            var_1997 = wp::extract(var_1958, var_1996);
            var_1999 = wp::extract(var_dims, var_1998);
            var_2000 = wp::mul(var_1997, var_1999);
            var_2002 = wp::extract(var_1958, var_2001);
            var_2003 = wp::add(var_2000, var_2002);
            var_2005 = wp::extract(var_dims, var_2004);
            var_2006 = wp::mul(var_2003, var_2005);
            var_2008 = wp::extract(var_1958, var_2007);
            var_2009 = wp::add(var_2006, var_2008);
            wp::array_store(var_ids, var_0, var_1955, var_2009);
            var_2011 = wp::extract(var_33, var_2010);
            var_2012 = basis_0(var_1947, var_2011);
            var_2014 = wp::extract(var_33, var_2013);
            var_2015 = basis_0(var_1948, var_2014);
            var_2017 = wp::extract(var_33, var_2016);
            var_2018 = basis_0(var_1949, var_2017);
            var_2019 = wp::mul(var_2012, var_2015);
            var_2020 = wp::mul(var_2019, var_2018);
            wp::array_store(var_w, var_0, var_1955, var_2020);
            var_2022 = wp::extract(var_33, var_2021);
            var_2023 = dbasis_0(var_1947, var_2022);
            var_2024 = wp::mul(var_2023, var_2015);
            var_2025 = wp::mul(var_2024, var_2018);
            var_2027 = wp::extract(var_33, var_2026);
            var_2028 = dbasis_0(var_1948, var_2027);
            var_2029 = wp::mul(var_2012, var_2028);
            var_2030 = wp::mul(var_2029, var_2018);
            var_2031 = wp::mul(var_2012, var_2015);
            var_2033 = wp::extract(var_33, var_2032);
            var_2034 = dbasis_0(var_1949, var_2033);
            var_2035 = wp::mul(var_2031, var_2034);
            var_2036 = wp::vec_t<3, wp::float64>(var_2025, var_2030, var_2035);
            var_2037 = wp::div(var_2036, var_h);
            wp::array_store(var_g, var_0, var_1955, var_2037);
            var_2039 = wp::extract(var_1957, var_2038);
            var_2040 = wp::float64(var_2039);
            var_2042 = wp::extract(var_1957, var_2041);
            var_2043 = wp::float64(var_2042);
            var_2045 = wp::extract(var_1957, var_2044);
            var_2046 = wp::float64(var_2045);
            var_2047 = wp::vec_t<3, wp::float64>(var_2040, var_2043, var_2046);
            var_2048 = wp::mul(var_2047, var_h);
            var_2049 = wp::address(var_x, var_0);
            var_2051 = wp::load(var_2049);
            var_2050 = wp::sub(var_2048, var_2051);
            wp::array_store(var_r, var_0, var_1955, var_2050);
        }
        var_2052 = wp::where(var_1959, var_1944, var_2012);
        var_2053 = wp::where(var_1959, var_1945, var_2015);
        var_2054 = wp::where(var_1959, var_1946, var_2018);
        // s=9*a+3*b+c;node=base+wp.vec3i(a,b,c);j=node-origin                                    <L 31>
        var_2057 = wp::mul(var_2056, var_1947);
        var_2059 = wp::mul(var_2058, var_1948);
        var_2060 = wp::add(var_2057, var_2059);
        var_2061 = wp::add(var_2060, var_2055);
        var_2062 = wp::vec_t<3, wp::int32>(var_1947, var_1948, var_2055);
        var_2063 = wp::add(var_22, var_2062);
        var_2064 = wp::sub(var_2063, var_origin);
        // if j[0]<0 or j[1]<0 or j[2]<0 or j[0]>=dims[0] or j[1]>=dims[1] or j[2]>=dims[2]:wp.atomic_add(bad,0,1);ids[p,s]=0;w[p,s]=wp.float64(0.0);g[p,s]=wp.vec3d(wp.float64(0.0));r[p,s]=wp.vec3d(wp.float64(0.0))       <L 32>
        var_2067 = wp::extract(var_2064, var_2066);
        var_2069 = (var_2067 < var_2068);
        var_2065 = var_2069;
        if (!var_2065) {
            var_2071 = wp::extract(var_2064, var_2070);
            var_2073 = (var_2071 < var_2072);
            var_2065 = var_2065 || var_2073;
        }
        if (!var_2065) {
            var_2075 = wp::extract(var_2064, var_2074);
            var_2077 = (var_2075 < var_2076);
            var_2065 = var_2065 || var_2077;
        }
        if (!var_2065) {
            var_2079 = wp::extract(var_2064, var_2078);
            var_2081 = wp::extract(var_dims, var_2080);
            var_2082 = (var_2079 >= var_2081);
            var_2065 = var_2065 || var_2082;
        }
        if (!var_2065) {
            var_2084 = wp::extract(var_2064, var_2083);
            var_2086 = wp::extract(var_dims, var_2085);
            var_2087 = (var_2084 >= var_2086);
            var_2065 = var_2065 || var_2087;
        }
        if (!var_2065) {
            var_2089 = wp::extract(var_2064, var_2088);
            var_2091 = wp::extract(var_dims, var_2090);
            var_2092 = (var_2089 >= var_2091);
            var_2065 = var_2065 || var_2092;
        }
        if (var_2065) {
            var_2095 = wp::atomic_add(var_bad, var_2093, var_2094);
            wp::array_store(var_ids, var_0, var_2061, var_2096);
            var_2097 = 0.0;
            wp::array_store(var_w, var_0, var_2061, var_2097);
            var_2098 = 0.0;
            var_2099 = wp::vec_t<3, wp::float64>(var_2098);
            wp::array_store(var_g, var_0, var_2061, var_2099);
            var_2100 = 0.0;
            var_2101 = wp::vec_t<3, wp::float64>(var_2100);
            wp::array_store(var_r, var_0, var_2061, var_2101);
        }
        if (!var_2065) {
            // ids[p,s]=(j[0]*dims[1]+j[1])*dims[2]+j[2];wx=basis(a,f[0]);wy=basis(b,f[1]);wz=basis(c,f[2]);w[p,s]=wx*wy*wz;g[p,s]=wp.vec3d(dbasis(a,f[0])*wy*wz,wx*dbasis(b,f[1])*wz,wx*wy*dbasis(c,f[2]))/h;r[p,s]=wp.vec3d(wp.float64(node[0]),wp.float64(node[1]),wp.float64(node[2]))*h-x[p]       <L 34>
            var_2103 = wp::extract(var_2064, var_2102);
            var_2105 = wp::extract(var_dims, var_2104);
            var_2106 = wp::mul(var_2103, var_2105);
            var_2108 = wp::extract(var_2064, var_2107);
            var_2109 = wp::add(var_2106, var_2108);
            var_2111 = wp::extract(var_dims, var_2110);
            var_2112 = wp::mul(var_2109, var_2111);
            var_2114 = wp::extract(var_2064, var_2113);
            var_2115 = wp::add(var_2112, var_2114);
            wp::array_store(var_ids, var_0, var_2061, var_2115);
            var_2117 = wp::extract(var_33, var_2116);
            var_2118 = basis_0(var_1947, var_2117);
            var_2120 = wp::extract(var_33, var_2119);
            var_2121 = basis_0(var_1948, var_2120);
            var_2123 = wp::extract(var_33, var_2122);
            var_2124 = basis_0(var_2055, var_2123);
            var_2125 = wp::mul(var_2118, var_2121);
            var_2126 = wp::mul(var_2125, var_2124);
            wp::array_store(var_w, var_0, var_2061, var_2126);
            var_2128 = wp::extract(var_33, var_2127);
            var_2129 = dbasis_0(var_1947, var_2128);
            var_2130 = wp::mul(var_2129, var_2121);
            var_2131 = wp::mul(var_2130, var_2124);
            var_2133 = wp::extract(var_33, var_2132);
            var_2134 = dbasis_0(var_1948, var_2133);
            var_2135 = wp::mul(var_2118, var_2134);
            var_2136 = wp::mul(var_2135, var_2124);
            var_2137 = wp::mul(var_2118, var_2121);
            var_2139 = wp::extract(var_33, var_2138);
            var_2140 = dbasis_0(var_2055, var_2139);
            var_2141 = wp::mul(var_2137, var_2140);
            var_2142 = wp::vec_t<3, wp::float64>(var_2131, var_2136, var_2141);
            var_2143 = wp::div(var_2142, var_h);
            wp::array_store(var_g, var_0, var_2061, var_2143);
            var_2145 = wp::extract(var_2063, var_2144);
            var_2146 = wp::float64(var_2145);
            var_2148 = wp::extract(var_2063, var_2147);
            var_2149 = wp::float64(var_2148);
            var_2151 = wp::extract(var_2063, var_2150);
            var_2152 = wp::float64(var_2151);
            var_2153 = wp::vec_t<3, wp::float64>(var_2146, var_2149, var_2152);
            var_2154 = wp::mul(var_2153, var_h);
            var_2155 = wp::address(var_x, var_0);
            var_2157 = wp::load(var_2155);
            var_2156 = wp::sub(var_2154, var_2157);
            wp::array_store(var_r, var_0, var_2061, var_2156);
        }
        var_2158 = wp::where(var_2065, var_2052, var_2118);
        var_2159 = wp::where(var_2065, var_2053, var_2121);
        var_2160 = wp::where(var_2065, var_2054, var_2124);
        // s=9*a+3*b+c;node=base+wp.vec3i(a,b,c);j=node-origin                                    <L 31>
        var_2163 = wp::mul(var_2162, var_1947);
        var_2165 = wp::mul(var_2164, var_1948);
        var_2166 = wp::add(var_2163, var_2165);
        var_2167 = wp::add(var_2166, var_2161);
        var_2168 = wp::vec_t<3, wp::int32>(var_1947, var_1948, var_2161);
        var_2169 = wp::add(var_22, var_2168);
        var_2170 = wp::sub(var_2169, var_origin);
        // if j[0]<0 or j[1]<0 or j[2]<0 or j[0]>=dims[0] or j[1]>=dims[1] or j[2]>=dims[2]:wp.atomic_add(bad,0,1);ids[p,s]=0;w[p,s]=wp.float64(0.0);g[p,s]=wp.vec3d(wp.float64(0.0));r[p,s]=wp.vec3d(wp.float64(0.0))       <L 32>
        var_2173 = wp::extract(var_2170, var_2172);
        var_2175 = (var_2173 < var_2174);
        var_2171 = var_2175;
        if (!var_2171) {
            var_2177 = wp::extract(var_2170, var_2176);
            var_2179 = (var_2177 < var_2178);
            var_2171 = var_2171 || var_2179;
        }
        if (!var_2171) {
            var_2181 = wp::extract(var_2170, var_2180);
            var_2183 = (var_2181 < var_2182);
            var_2171 = var_2171 || var_2183;
        }
        if (!var_2171) {
            var_2185 = wp::extract(var_2170, var_2184);
            var_2187 = wp::extract(var_dims, var_2186);
            var_2188 = (var_2185 >= var_2187);
            var_2171 = var_2171 || var_2188;
        }
        if (!var_2171) {
            var_2190 = wp::extract(var_2170, var_2189);
            var_2192 = wp::extract(var_dims, var_2191);
            var_2193 = (var_2190 >= var_2192);
            var_2171 = var_2171 || var_2193;
        }
        if (!var_2171) {
            var_2195 = wp::extract(var_2170, var_2194);
            var_2197 = wp::extract(var_dims, var_2196);
            var_2198 = (var_2195 >= var_2197);
            var_2171 = var_2171 || var_2198;
        }
        if (var_2171) {
            var_2201 = wp::atomic_add(var_bad, var_2199, var_2200);
            wp::array_store(var_ids, var_0, var_2167, var_2202);
            var_2203 = 0.0;
            wp::array_store(var_w, var_0, var_2167, var_2203);
            var_2204 = 0.0;
            var_2205 = wp::vec_t<3, wp::float64>(var_2204);
            wp::array_store(var_g, var_0, var_2167, var_2205);
            var_2206 = 0.0;
            var_2207 = wp::vec_t<3, wp::float64>(var_2206);
            wp::array_store(var_r, var_0, var_2167, var_2207);
        }
        if (!var_2171) {
            // ids[p,s]=(j[0]*dims[1]+j[1])*dims[2]+j[2];wx=basis(a,f[0]);wy=basis(b,f[1]);wz=basis(c,f[2]);w[p,s]=wx*wy*wz;g[p,s]=wp.vec3d(dbasis(a,f[0])*wy*wz,wx*dbasis(b,f[1])*wz,wx*wy*dbasis(c,f[2]))/h;r[p,s]=wp.vec3d(wp.float64(node[0]),wp.float64(node[1]),wp.float64(node[2]))*h-x[p]       <L 34>
            var_2209 = wp::extract(var_2170, var_2208);
            var_2211 = wp::extract(var_dims, var_2210);
            var_2212 = wp::mul(var_2209, var_2211);
            var_2214 = wp::extract(var_2170, var_2213);
            var_2215 = wp::add(var_2212, var_2214);
            var_2217 = wp::extract(var_dims, var_2216);
            var_2218 = wp::mul(var_2215, var_2217);
            var_2220 = wp::extract(var_2170, var_2219);
            var_2221 = wp::add(var_2218, var_2220);
            wp::array_store(var_ids, var_0, var_2167, var_2221);
            var_2223 = wp::extract(var_33, var_2222);
            var_2224 = basis_0(var_1947, var_2223);
            var_2226 = wp::extract(var_33, var_2225);
            var_2227 = basis_0(var_1948, var_2226);
            var_2229 = wp::extract(var_33, var_2228);
            var_2230 = basis_0(var_2161, var_2229);
            var_2231 = wp::mul(var_2224, var_2227);
            var_2232 = wp::mul(var_2231, var_2230);
            wp::array_store(var_w, var_0, var_2167, var_2232);
            var_2234 = wp::extract(var_33, var_2233);
            var_2235 = dbasis_0(var_1947, var_2234);
            var_2236 = wp::mul(var_2235, var_2227);
            var_2237 = wp::mul(var_2236, var_2230);
            var_2239 = wp::extract(var_33, var_2238);
            var_2240 = dbasis_0(var_1948, var_2239);
            var_2241 = wp::mul(var_2224, var_2240);
            var_2242 = wp::mul(var_2241, var_2230);
            var_2243 = wp::mul(var_2224, var_2227);
            var_2245 = wp::extract(var_33, var_2244);
            var_2246 = dbasis_0(var_2161, var_2245);
            var_2247 = wp::mul(var_2243, var_2246);
            var_2248 = wp::vec_t<3, wp::float64>(var_2237, var_2242, var_2247);
            var_2249 = wp::div(var_2248, var_h);
            wp::array_store(var_g, var_0, var_2167, var_2249);
            var_2251 = wp::extract(var_2169, var_2250);
            var_2252 = wp::float64(var_2251);
            var_2254 = wp::extract(var_2169, var_2253);
            var_2255 = wp::float64(var_2254);
            var_2257 = wp::extract(var_2169, var_2256);
            var_2258 = wp::float64(var_2257);
            var_2259 = wp::vec_t<3, wp::float64>(var_2252, var_2255, var_2258);
            var_2260 = wp::mul(var_2259, var_h);
            var_2261 = wp::address(var_x, var_0);
            var_2263 = wp::load(var_2261);
            var_2262 = wp::sub(var_2260, var_2263);
            wp::array_store(var_r, var_0, var_2167, var_2262);
        }
        var_2264 = wp::where(var_2171, var_2158, var_2224);
        var_2265 = wp::where(var_2171, var_2159, var_2227);
        var_2266 = wp::where(var_2171, var_2160, var_2230);
        // for c in range(3):                                                                     <L 30>
        // s=9*a+3*b+c;node=base+wp.vec3i(a,b,c);j=node-origin                                    <L 31>
        var_2270 = wp::mul(var_2269, var_1947);
        var_2272 = wp::mul(var_2271, var_2267);
        var_2273 = wp::add(var_2270, var_2272);
        var_2274 = wp::add(var_2273, var_2268);
        var_2275 = wp::vec_t<3, wp::int32>(var_1947, var_2267, var_2268);
        var_2276 = wp::add(var_22, var_2275);
        var_2277 = wp::sub(var_2276, var_origin);
        // if j[0]<0 or j[1]<0 or j[2]<0 or j[0]>=dims[0] or j[1]>=dims[1] or j[2]>=dims[2]:wp.atomic_add(bad,0,1);ids[p,s]=0;w[p,s]=wp.float64(0.0);g[p,s]=wp.vec3d(wp.float64(0.0));r[p,s]=wp.vec3d(wp.float64(0.0))       <L 32>
        var_2280 = wp::extract(var_2277, var_2279);
        var_2282 = (var_2280 < var_2281);
        var_2278 = var_2282;
        if (!var_2278) {
            var_2284 = wp::extract(var_2277, var_2283);
            var_2286 = (var_2284 < var_2285);
            var_2278 = var_2278 || var_2286;
        }
        if (!var_2278) {
            var_2288 = wp::extract(var_2277, var_2287);
            var_2290 = (var_2288 < var_2289);
            var_2278 = var_2278 || var_2290;
        }
        if (!var_2278) {
            var_2292 = wp::extract(var_2277, var_2291);
            var_2294 = wp::extract(var_dims, var_2293);
            var_2295 = (var_2292 >= var_2294);
            var_2278 = var_2278 || var_2295;
        }
        if (!var_2278) {
            var_2297 = wp::extract(var_2277, var_2296);
            var_2299 = wp::extract(var_dims, var_2298);
            var_2300 = (var_2297 >= var_2299);
            var_2278 = var_2278 || var_2300;
        }
        if (!var_2278) {
            var_2302 = wp::extract(var_2277, var_2301);
            var_2304 = wp::extract(var_dims, var_2303);
            var_2305 = (var_2302 >= var_2304);
            var_2278 = var_2278 || var_2305;
        }
        if (var_2278) {
            var_2308 = wp::atomic_add(var_bad, var_2306, var_2307);
            wp::array_store(var_ids, var_0, var_2274, var_2309);
            var_2310 = 0.0;
            wp::array_store(var_w, var_0, var_2274, var_2310);
            var_2311 = 0.0;
            var_2312 = wp::vec_t<3, wp::float64>(var_2311);
            wp::array_store(var_g, var_0, var_2274, var_2312);
            var_2313 = 0.0;
            var_2314 = wp::vec_t<3, wp::float64>(var_2313);
            wp::array_store(var_r, var_0, var_2274, var_2314);
        }
        if (!var_2278) {
            // ids[p,s]=(j[0]*dims[1]+j[1])*dims[2]+j[2];wx=basis(a,f[0]);wy=basis(b,f[1]);wz=basis(c,f[2]);w[p,s]=wx*wy*wz;g[p,s]=wp.vec3d(dbasis(a,f[0])*wy*wz,wx*dbasis(b,f[1])*wz,wx*wy*dbasis(c,f[2]))/h;r[p,s]=wp.vec3d(wp.float64(node[0]),wp.float64(node[1]),wp.float64(node[2]))*h-x[p]       <L 34>
            var_2316 = wp::extract(var_2277, var_2315);
            var_2318 = wp::extract(var_dims, var_2317);
            var_2319 = wp::mul(var_2316, var_2318);
            var_2321 = wp::extract(var_2277, var_2320);
            var_2322 = wp::add(var_2319, var_2321);
            var_2324 = wp::extract(var_dims, var_2323);
            var_2325 = wp::mul(var_2322, var_2324);
            var_2327 = wp::extract(var_2277, var_2326);
            var_2328 = wp::add(var_2325, var_2327);
            wp::array_store(var_ids, var_0, var_2274, var_2328);
            var_2330 = wp::extract(var_33, var_2329);
            var_2331 = basis_0(var_1947, var_2330);
            var_2333 = wp::extract(var_33, var_2332);
            var_2334 = basis_0(var_2267, var_2333);
            var_2336 = wp::extract(var_33, var_2335);
            var_2337 = basis_0(var_2268, var_2336);
            var_2338 = wp::mul(var_2331, var_2334);
            var_2339 = wp::mul(var_2338, var_2337);
            wp::array_store(var_w, var_0, var_2274, var_2339);
            var_2341 = wp::extract(var_33, var_2340);
            var_2342 = dbasis_0(var_1947, var_2341);
            var_2343 = wp::mul(var_2342, var_2334);
            var_2344 = wp::mul(var_2343, var_2337);
            var_2346 = wp::extract(var_33, var_2345);
            var_2347 = dbasis_0(var_2267, var_2346);
            var_2348 = wp::mul(var_2331, var_2347);
            var_2349 = wp::mul(var_2348, var_2337);
            var_2350 = wp::mul(var_2331, var_2334);
            var_2352 = wp::extract(var_33, var_2351);
            var_2353 = dbasis_0(var_2268, var_2352);
            var_2354 = wp::mul(var_2350, var_2353);
            var_2355 = wp::vec_t<3, wp::float64>(var_2344, var_2349, var_2354);
            var_2356 = wp::div(var_2355, var_h);
            wp::array_store(var_g, var_0, var_2274, var_2356);
            var_2358 = wp::extract(var_2276, var_2357);
            var_2359 = wp::float64(var_2358);
            var_2361 = wp::extract(var_2276, var_2360);
            var_2362 = wp::float64(var_2361);
            var_2364 = wp::extract(var_2276, var_2363);
            var_2365 = wp::float64(var_2364);
            var_2366 = wp::vec_t<3, wp::float64>(var_2359, var_2362, var_2365);
            var_2367 = wp::mul(var_2366, var_h);
            var_2368 = wp::address(var_x, var_0);
            var_2370 = wp::load(var_2368);
            var_2369 = wp::sub(var_2367, var_2370);
            wp::array_store(var_r, var_0, var_2274, var_2369);
        }
        var_2371 = wp::where(var_2278, var_2264, var_2331);
        var_2372 = wp::where(var_2278, var_2265, var_2334);
        var_2373 = wp::where(var_2278, var_2266, var_2337);
        // s=9*a+3*b+c;node=base+wp.vec3i(a,b,c);j=node-origin                                    <L 31>
        var_2376 = wp::mul(var_2375, var_1947);
        var_2378 = wp::mul(var_2377, var_2267);
        var_2379 = wp::add(var_2376, var_2378);
        var_2380 = wp::add(var_2379, var_2374);
        var_2381 = wp::vec_t<3, wp::int32>(var_1947, var_2267, var_2374);
        var_2382 = wp::add(var_22, var_2381);
        var_2383 = wp::sub(var_2382, var_origin);
        // if j[0]<0 or j[1]<0 or j[2]<0 or j[0]>=dims[0] or j[1]>=dims[1] or j[2]>=dims[2]:wp.atomic_add(bad,0,1);ids[p,s]=0;w[p,s]=wp.float64(0.0);g[p,s]=wp.vec3d(wp.float64(0.0));r[p,s]=wp.vec3d(wp.float64(0.0))       <L 32>
        var_2386 = wp::extract(var_2383, var_2385);
        var_2388 = (var_2386 < var_2387);
        var_2384 = var_2388;
        if (!var_2384) {
            var_2390 = wp::extract(var_2383, var_2389);
            var_2392 = (var_2390 < var_2391);
            var_2384 = var_2384 || var_2392;
        }
        if (!var_2384) {
            var_2394 = wp::extract(var_2383, var_2393);
            var_2396 = (var_2394 < var_2395);
            var_2384 = var_2384 || var_2396;
        }
        if (!var_2384) {
            var_2398 = wp::extract(var_2383, var_2397);
            var_2400 = wp::extract(var_dims, var_2399);
            var_2401 = (var_2398 >= var_2400);
            var_2384 = var_2384 || var_2401;
        }
        if (!var_2384) {
            var_2403 = wp::extract(var_2383, var_2402);
            var_2405 = wp::extract(var_dims, var_2404);
            var_2406 = (var_2403 >= var_2405);
            var_2384 = var_2384 || var_2406;
        }
        if (!var_2384) {
            var_2408 = wp::extract(var_2383, var_2407);
            var_2410 = wp::extract(var_dims, var_2409);
            var_2411 = (var_2408 >= var_2410);
            var_2384 = var_2384 || var_2411;
        }
        if (var_2384) {
            var_2414 = wp::atomic_add(var_bad, var_2412, var_2413);
            wp::array_store(var_ids, var_0, var_2380, var_2415);
            var_2416 = 0.0;
            wp::array_store(var_w, var_0, var_2380, var_2416);
            var_2417 = 0.0;
            var_2418 = wp::vec_t<3, wp::float64>(var_2417);
            wp::array_store(var_g, var_0, var_2380, var_2418);
            var_2419 = 0.0;
            var_2420 = wp::vec_t<3, wp::float64>(var_2419);
            wp::array_store(var_r, var_0, var_2380, var_2420);
        }
        if (!var_2384) {
            // ids[p,s]=(j[0]*dims[1]+j[1])*dims[2]+j[2];wx=basis(a,f[0]);wy=basis(b,f[1]);wz=basis(c,f[2]);w[p,s]=wx*wy*wz;g[p,s]=wp.vec3d(dbasis(a,f[0])*wy*wz,wx*dbasis(b,f[1])*wz,wx*wy*dbasis(c,f[2]))/h;r[p,s]=wp.vec3d(wp.float64(node[0]),wp.float64(node[1]),wp.float64(node[2]))*h-x[p]       <L 34>
            var_2422 = wp::extract(var_2383, var_2421);
            var_2424 = wp::extract(var_dims, var_2423);
            var_2425 = wp::mul(var_2422, var_2424);
            var_2427 = wp::extract(var_2383, var_2426);
            var_2428 = wp::add(var_2425, var_2427);
            var_2430 = wp::extract(var_dims, var_2429);
            var_2431 = wp::mul(var_2428, var_2430);
            var_2433 = wp::extract(var_2383, var_2432);
            var_2434 = wp::add(var_2431, var_2433);
            wp::array_store(var_ids, var_0, var_2380, var_2434);
            var_2436 = wp::extract(var_33, var_2435);
            var_2437 = basis_0(var_1947, var_2436);
            var_2439 = wp::extract(var_33, var_2438);
            var_2440 = basis_0(var_2267, var_2439);
            var_2442 = wp::extract(var_33, var_2441);
            var_2443 = basis_0(var_2374, var_2442);
            var_2444 = wp::mul(var_2437, var_2440);
            var_2445 = wp::mul(var_2444, var_2443);
            wp::array_store(var_w, var_0, var_2380, var_2445);
            var_2447 = wp::extract(var_33, var_2446);
            var_2448 = dbasis_0(var_1947, var_2447);
            var_2449 = wp::mul(var_2448, var_2440);
            var_2450 = wp::mul(var_2449, var_2443);
            var_2452 = wp::extract(var_33, var_2451);
            var_2453 = dbasis_0(var_2267, var_2452);
            var_2454 = wp::mul(var_2437, var_2453);
            var_2455 = wp::mul(var_2454, var_2443);
            var_2456 = wp::mul(var_2437, var_2440);
            var_2458 = wp::extract(var_33, var_2457);
            var_2459 = dbasis_0(var_2374, var_2458);
            var_2460 = wp::mul(var_2456, var_2459);
            var_2461 = wp::vec_t<3, wp::float64>(var_2450, var_2455, var_2460);
            var_2462 = wp::div(var_2461, var_h);
            wp::array_store(var_g, var_0, var_2380, var_2462);
            var_2464 = wp::extract(var_2382, var_2463);
            var_2465 = wp::float64(var_2464);
            var_2467 = wp::extract(var_2382, var_2466);
            var_2468 = wp::float64(var_2467);
            var_2470 = wp::extract(var_2382, var_2469);
            var_2471 = wp::float64(var_2470);
            var_2472 = wp::vec_t<3, wp::float64>(var_2465, var_2468, var_2471);
            var_2473 = wp::mul(var_2472, var_h);
            var_2474 = wp::address(var_x, var_0);
            var_2476 = wp::load(var_2474);
            var_2475 = wp::sub(var_2473, var_2476);
            wp::array_store(var_r, var_0, var_2380, var_2475);
        }
        var_2477 = wp::where(var_2384, var_2371, var_2437);
        var_2478 = wp::where(var_2384, var_2372, var_2440);
        var_2479 = wp::where(var_2384, var_2373, var_2443);
        // s=9*a+3*b+c;node=base+wp.vec3i(a,b,c);j=node-origin                                    <L 31>
        var_2482 = wp::mul(var_2481, var_1947);
        var_2484 = wp::mul(var_2483, var_2267);
        var_2485 = wp::add(var_2482, var_2484);
        var_2486 = wp::add(var_2485, var_2480);
        var_2487 = wp::vec_t<3, wp::int32>(var_1947, var_2267, var_2480);
        var_2488 = wp::add(var_22, var_2487);
        var_2489 = wp::sub(var_2488, var_origin);
        // if j[0]<0 or j[1]<0 or j[2]<0 or j[0]>=dims[0] or j[1]>=dims[1] or j[2]>=dims[2]:wp.atomic_add(bad,0,1);ids[p,s]=0;w[p,s]=wp.float64(0.0);g[p,s]=wp.vec3d(wp.float64(0.0));r[p,s]=wp.vec3d(wp.float64(0.0))       <L 32>
        var_2492 = wp::extract(var_2489, var_2491);
        var_2494 = (var_2492 < var_2493);
        var_2490 = var_2494;
        if (!var_2490) {
            var_2496 = wp::extract(var_2489, var_2495);
            var_2498 = (var_2496 < var_2497);
            var_2490 = var_2490 || var_2498;
        }
        if (!var_2490) {
            var_2500 = wp::extract(var_2489, var_2499);
            var_2502 = (var_2500 < var_2501);
            var_2490 = var_2490 || var_2502;
        }
        if (!var_2490) {
            var_2504 = wp::extract(var_2489, var_2503);
            var_2506 = wp::extract(var_dims, var_2505);
            var_2507 = (var_2504 >= var_2506);
            var_2490 = var_2490 || var_2507;
        }
        if (!var_2490) {
            var_2509 = wp::extract(var_2489, var_2508);
            var_2511 = wp::extract(var_dims, var_2510);
            var_2512 = (var_2509 >= var_2511);
            var_2490 = var_2490 || var_2512;
        }
        if (!var_2490) {
            var_2514 = wp::extract(var_2489, var_2513);
            var_2516 = wp::extract(var_dims, var_2515);
            var_2517 = (var_2514 >= var_2516);
            var_2490 = var_2490 || var_2517;
        }
        if (var_2490) {
            var_2520 = wp::atomic_add(var_bad, var_2518, var_2519);
            wp::array_store(var_ids, var_0, var_2486, var_2521);
            var_2522 = 0.0;
            wp::array_store(var_w, var_0, var_2486, var_2522);
            var_2523 = 0.0;
            var_2524 = wp::vec_t<3, wp::float64>(var_2523);
            wp::array_store(var_g, var_0, var_2486, var_2524);
            var_2525 = 0.0;
            var_2526 = wp::vec_t<3, wp::float64>(var_2525);
            wp::array_store(var_r, var_0, var_2486, var_2526);
        }
        if (!var_2490) {
            // ids[p,s]=(j[0]*dims[1]+j[1])*dims[2]+j[2];wx=basis(a,f[0]);wy=basis(b,f[1]);wz=basis(c,f[2]);w[p,s]=wx*wy*wz;g[p,s]=wp.vec3d(dbasis(a,f[0])*wy*wz,wx*dbasis(b,f[1])*wz,wx*wy*dbasis(c,f[2]))/h;r[p,s]=wp.vec3d(wp.float64(node[0]),wp.float64(node[1]),wp.float64(node[2]))*h-x[p]       <L 34>
            var_2528 = wp::extract(var_2489, var_2527);
            var_2530 = wp::extract(var_dims, var_2529);
            var_2531 = wp::mul(var_2528, var_2530);
            var_2533 = wp::extract(var_2489, var_2532);
            var_2534 = wp::add(var_2531, var_2533);
            var_2536 = wp::extract(var_dims, var_2535);
            var_2537 = wp::mul(var_2534, var_2536);
            var_2539 = wp::extract(var_2489, var_2538);
            var_2540 = wp::add(var_2537, var_2539);
            wp::array_store(var_ids, var_0, var_2486, var_2540);
            var_2542 = wp::extract(var_33, var_2541);
            var_2543 = basis_0(var_1947, var_2542);
            var_2545 = wp::extract(var_33, var_2544);
            var_2546 = basis_0(var_2267, var_2545);
            var_2548 = wp::extract(var_33, var_2547);
            var_2549 = basis_0(var_2480, var_2548);
            var_2550 = wp::mul(var_2543, var_2546);
            var_2551 = wp::mul(var_2550, var_2549);
            wp::array_store(var_w, var_0, var_2486, var_2551);
            var_2553 = wp::extract(var_33, var_2552);
            var_2554 = dbasis_0(var_1947, var_2553);
            var_2555 = wp::mul(var_2554, var_2546);
            var_2556 = wp::mul(var_2555, var_2549);
            var_2558 = wp::extract(var_33, var_2557);
            var_2559 = dbasis_0(var_2267, var_2558);
            var_2560 = wp::mul(var_2543, var_2559);
            var_2561 = wp::mul(var_2560, var_2549);
            var_2562 = wp::mul(var_2543, var_2546);
            var_2564 = wp::extract(var_33, var_2563);
            var_2565 = dbasis_0(var_2480, var_2564);
            var_2566 = wp::mul(var_2562, var_2565);
            var_2567 = wp::vec_t<3, wp::float64>(var_2556, var_2561, var_2566);
            var_2568 = wp::div(var_2567, var_h);
            wp::array_store(var_g, var_0, var_2486, var_2568);
            var_2570 = wp::extract(var_2488, var_2569);
            var_2571 = wp::float64(var_2570);
            var_2573 = wp::extract(var_2488, var_2572);
            var_2574 = wp::float64(var_2573);
            var_2576 = wp::extract(var_2488, var_2575);
            var_2577 = wp::float64(var_2576);
            var_2578 = wp::vec_t<3, wp::float64>(var_2571, var_2574, var_2577);
            var_2579 = wp::mul(var_2578, var_h);
            var_2580 = wp::address(var_x, var_0);
            var_2582 = wp::load(var_2580);
            var_2581 = wp::sub(var_2579, var_2582);
            wp::array_store(var_r, var_0, var_2486, var_2581);
        }
        var_2583 = wp::where(var_2490, var_2477, var_2543);
        var_2584 = wp::where(var_2490, var_2478, var_2546);
        var_2585 = wp::where(var_2490, var_2479, var_2549);
        // for c in range(3):                                                                     <L 30>
        // s=9*a+3*b+c;node=base+wp.vec3i(a,b,c);j=node-origin                                    <L 31>
        var_2589 = wp::mul(var_2588, var_1947);
        var_2591 = wp::mul(var_2590, var_2586);
        var_2592 = wp::add(var_2589, var_2591);
        var_2593 = wp::add(var_2592, var_2587);
        var_2594 = wp::vec_t<3, wp::int32>(var_1947, var_2586, var_2587);
        var_2595 = wp::add(var_22, var_2594);
        var_2596 = wp::sub(var_2595, var_origin);
        // if j[0]<0 or j[1]<0 or j[2]<0 or j[0]>=dims[0] or j[1]>=dims[1] or j[2]>=dims[2]:wp.atomic_add(bad,0,1);ids[p,s]=0;w[p,s]=wp.float64(0.0);g[p,s]=wp.vec3d(wp.float64(0.0));r[p,s]=wp.vec3d(wp.float64(0.0))       <L 32>
        var_2599 = wp::extract(var_2596, var_2598);
        var_2601 = (var_2599 < var_2600);
        var_2597 = var_2601;
        if (!var_2597) {
            var_2603 = wp::extract(var_2596, var_2602);
            var_2605 = (var_2603 < var_2604);
            var_2597 = var_2597 || var_2605;
        }
        if (!var_2597) {
            var_2607 = wp::extract(var_2596, var_2606);
            var_2609 = (var_2607 < var_2608);
            var_2597 = var_2597 || var_2609;
        }
        if (!var_2597) {
            var_2611 = wp::extract(var_2596, var_2610);
            var_2613 = wp::extract(var_dims, var_2612);
            var_2614 = (var_2611 >= var_2613);
            var_2597 = var_2597 || var_2614;
        }
        if (!var_2597) {
            var_2616 = wp::extract(var_2596, var_2615);
            var_2618 = wp::extract(var_dims, var_2617);
            var_2619 = (var_2616 >= var_2618);
            var_2597 = var_2597 || var_2619;
        }
        if (!var_2597) {
            var_2621 = wp::extract(var_2596, var_2620);
            var_2623 = wp::extract(var_dims, var_2622);
            var_2624 = (var_2621 >= var_2623);
            var_2597 = var_2597 || var_2624;
        }
        if (var_2597) {
            var_2627 = wp::atomic_add(var_bad, var_2625, var_2626);
            wp::array_store(var_ids, var_0, var_2593, var_2628);
            var_2629 = 0.0;
            wp::array_store(var_w, var_0, var_2593, var_2629);
            var_2630 = 0.0;
            var_2631 = wp::vec_t<3, wp::float64>(var_2630);
            wp::array_store(var_g, var_0, var_2593, var_2631);
            var_2632 = 0.0;
            var_2633 = wp::vec_t<3, wp::float64>(var_2632);
            wp::array_store(var_r, var_0, var_2593, var_2633);
        }
        if (!var_2597) {
            // ids[p,s]=(j[0]*dims[1]+j[1])*dims[2]+j[2];wx=basis(a,f[0]);wy=basis(b,f[1]);wz=basis(c,f[2]);w[p,s]=wx*wy*wz;g[p,s]=wp.vec3d(dbasis(a,f[0])*wy*wz,wx*dbasis(b,f[1])*wz,wx*wy*dbasis(c,f[2]))/h;r[p,s]=wp.vec3d(wp.float64(node[0]),wp.float64(node[1]),wp.float64(node[2]))*h-x[p]       <L 34>
            var_2635 = wp::extract(var_2596, var_2634);
            var_2637 = wp::extract(var_dims, var_2636);
            var_2638 = wp::mul(var_2635, var_2637);
            var_2640 = wp::extract(var_2596, var_2639);
            var_2641 = wp::add(var_2638, var_2640);
            var_2643 = wp::extract(var_dims, var_2642);
            var_2644 = wp::mul(var_2641, var_2643);
            var_2646 = wp::extract(var_2596, var_2645);
            var_2647 = wp::add(var_2644, var_2646);
            wp::array_store(var_ids, var_0, var_2593, var_2647);
            var_2649 = wp::extract(var_33, var_2648);
            var_2650 = basis_0(var_1947, var_2649);
            var_2652 = wp::extract(var_33, var_2651);
            var_2653 = basis_0(var_2586, var_2652);
            var_2655 = wp::extract(var_33, var_2654);
            var_2656 = basis_0(var_2587, var_2655);
            var_2657 = wp::mul(var_2650, var_2653);
            var_2658 = wp::mul(var_2657, var_2656);
            wp::array_store(var_w, var_0, var_2593, var_2658);
            var_2660 = wp::extract(var_33, var_2659);
            var_2661 = dbasis_0(var_1947, var_2660);
            var_2662 = wp::mul(var_2661, var_2653);
            var_2663 = wp::mul(var_2662, var_2656);
            var_2665 = wp::extract(var_33, var_2664);
            var_2666 = dbasis_0(var_2586, var_2665);
            var_2667 = wp::mul(var_2650, var_2666);
            var_2668 = wp::mul(var_2667, var_2656);
            var_2669 = wp::mul(var_2650, var_2653);
            var_2671 = wp::extract(var_33, var_2670);
            var_2672 = dbasis_0(var_2587, var_2671);
            var_2673 = wp::mul(var_2669, var_2672);
            var_2674 = wp::vec_t<3, wp::float64>(var_2663, var_2668, var_2673);
            var_2675 = wp::div(var_2674, var_h);
            wp::array_store(var_g, var_0, var_2593, var_2675);
            var_2677 = wp::extract(var_2595, var_2676);
            var_2678 = wp::float64(var_2677);
            var_2680 = wp::extract(var_2595, var_2679);
            var_2681 = wp::float64(var_2680);
            var_2683 = wp::extract(var_2595, var_2682);
            var_2684 = wp::float64(var_2683);
            var_2685 = wp::vec_t<3, wp::float64>(var_2678, var_2681, var_2684);
            var_2686 = wp::mul(var_2685, var_h);
            var_2687 = wp::address(var_x, var_0);
            var_2689 = wp::load(var_2687);
            var_2688 = wp::sub(var_2686, var_2689);
            wp::array_store(var_r, var_0, var_2593, var_2688);
        }
        var_2690 = wp::where(var_2597, var_2583, var_2650);
        var_2691 = wp::where(var_2597, var_2584, var_2653);
        var_2692 = wp::where(var_2597, var_2585, var_2656);
        // s=9*a+3*b+c;node=base+wp.vec3i(a,b,c);j=node-origin                                    <L 31>
        var_2695 = wp::mul(var_2694, var_1947);
        var_2697 = wp::mul(var_2696, var_2586);
        var_2698 = wp::add(var_2695, var_2697);
        var_2699 = wp::add(var_2698, var_2693);
        var_2700 = wp::vec_t<3, wp::int32>(var_1947, var_2586, var_2693);
        var_2701 = wp::add(var_22, var_2700);
        var_2702 = wp::sub(var_2701, var_origin);
        // if j[0]<0 or j[1]<0 or j[2]<0 or j[0]>=dims[0] or j[1]>=dims[1] or j[2]>=dims[2]:wp.atomic_add(bad,0,1);ids[p,s]=0;w[p,s]=wp.float64(0.0);g[p,s]=wp.vec3d(wp.float64(0.0));r[p,s]=wp.vec3d(wp.float64(0.0))       <L 32>
        var_2705 = wp::extract(var_2702, var_2704);
        var_2707 = (var_2705 < var_2706);
        var_2703 = var_2707;
        if (!var_2703) {
            var_2709 = wp::extract(var_2702, var_2708);
            var_2711 = (var_2709 < var_2710);
            var_2703 = var_2703 || var_2711;
        }
        if (!var_2703) {
            var_2713 = wp::extract(var_2702, var_2712);
            var_2715 = (var_2713 < var_2714);
            var_2703 = var_2703 || var_2715;
        }
        if (!var_2703) {
            var_2717 = wp::extract(var_2702, var_2716);
            var_2719 = wp::extract(var_dims, var_2718);
            var_2720 = (var_2717 >= var_2719);
            var_2703 = var_2703 || var_2720;
        }
        if (!var_2703) {
            var_2722 = wp::extract(var_2702, var_2721);
            var_2724 = wp::extract(var_dims, var_2723);
            var_2725 = (var_2722 >= var_2724);
            var_2703 = var_2703 || var_2725;
        }
        if (!var_2703) {
            var_2727 = wp::extract(var_2702, var_2726);
            var_2729 = wp::extract(var_dims, var_2728);
            var_2730 = (var_2727 >= var_2729);
            var_2703 = var_2703 || var_2730;
        }
        if (var_2703) {
            var_2733 = wp::atomic_add(var_bad, var_2731, var_2732);
            wp::array_store(var_ids, var_0, var_2699, var_2734);
            var_2735 = 0.0;
            wp::array_store(var_w, var_0, var_2699, var_2735);
            var_2736 = 0.0;
            var_2737 = wp::vec_t<3, wp::float64>(var_2736);
            wp::array_store(var_g, var_0, var_2699, var_2737);
            var_2738 = 0.0;
            var_2739 = wp::vec_t<3, wp::float64>(var_2738);
            wp::array_store(var_r, var_0, var_2699, var_2739);
        }
        if (!var_2703) {
            // ids[p,s]=(j[0]*dims[1]+j[1])*dims[2]+j[2];wx=basis(a,f[0]);wy=basis(b,f[1]);wz=basis(c,f[2]);w[p,s]=wx*wy*wz;g[p,s]=wp.vec3d(dbasis(a,f[0])*wy*wz,wx*dbasis(b,f[1])*wz,wx*wy*dbasis(c,f[2]))/h;r[p,s]=wp.vec3d(wp.float64(node[0]),wp.float64(node[1]),wp.float64(node[2]))*h-x[p]       <L 34>
            var_2741 = wp::extract(var_2702, var_2740);
            var_2743 = wp::extract(var_dims, var_2742);
            var_2744 = wp::mul(var_2741, var_2743);
            var_2746 = wp::extract(var_2702, var_2745);
            var_2747 = wp::add(var_2744, var_2746);
            var_2749 = wp::extract(var_dims, var_2748);
            var_2750 = wp::mul(var_2747, var_2749);
            var_2752 = wp::extract(var_2702, var_2751);
            var_2753 = wp::add(var_2750, var_2752);
            wp::array_store(var_ids, var_0, var_2699, var_2753);
            var_2755 = wp::extract(var_33, var_2754);
            var_2756 = basis_0(var_1947, var_2755);
            var_2758 = wp::extract(var_33, var_2757);
            var_2759 = basis_0(var_2586, var_2758);
            var_2761 = wp::extract(var_33, var_2760);
            var_2762 = basis_0(var_2693, var_2761);
            var_2763 = wp::mul(var_2756, var_2759);
            var_2764 = wp::mul(var_2763, var_2762);
            wp::array_store(var_w, var_0, var_2699, var_2764);
            var_2766 = wp::extract(var_33, var_2765);
            var_2767 = dbasis_0(var_1947, var_2766);
            var_2768 = wp::mul(var_2767, var_2759);
            var_2769 = wp::mul(var_2768, var_2762);
            var_2771 = wp::extract(var_33, var_2770);
            var_2772 = dbasis_0(var_2586, var_2771);
            var_2773 = wp::mul(var_2756, var_2772);
            var_2774 = wp::mul(var_2773, var_2762);
            var_2775 = wp::mul(var_2756, var_2759);
            var_2777 = wp::extract(var_33, var_2776);
            var_2778 = dbasis_0(var_2693, var_2777);
            var_2779 = wp::mul(var_2775, var_2778);
            var_2780 = wp::vec_t<3, wp::float64>(var_2769, var_2774, var_2779);
            var_2781 = wp::div(var_2780, var_h);
            wp::array_store(var_g, var_0, var_2699, var_2781);
            var_2783 = wp::extract(var_2701, var_2782);
            var_2784 = wp::float64(var_2783);
            var_2786 = wp::extract(var_2701, var_2785);
            var_2787 = wp::float64(var_2786);
            var_2789 = wp::extract(var_2701, var_2788);
            var_2790 = wp::float64(var_2789);
            var_2791 = wp::vec_t<3, wp::float64>(var_2784, var_2787, var_2790);
            var_2792 = wp::mul(var_2791, var_h);
            var_2793 = wp::address(var_x, var_0);
            var_2795 = wp::load(var_2793);
            var_2794 = wp::sub(var_2792, var_2795);
            wp::array_store(var_r, var_0, var_2699, var_2794);
        }
        var_2796 = wp::where(var_2703, var_2690, var_2756);
        var_2797 = wp::where(var_2703, var_2691, var_2759);
        var_2798 = wp::where(var_2703, var_2692, var_2762);
        // s=9*a+3*b+c;node=base+wp.vec3i(a,b,c);j=node-origin                                    <L 31>
        var_2801 = wp::mul(var_2800, var_1947);
        var_2803 = wp::mul(var_2802, var_2586);
        var_2804 = wp::add(var_2801, var_2803);
        var_2805 = wp::add(var_2804, var_2799);
        var_2806 = wp::vec_t<3, wp::int32>(var_1947, var_2586, var_2799);
        var_2807 = wp::add(var_22, var_2806);
        var_2808 = wp::sub(var_2807, var_origin);
        // if j[0]<0 or j[1]<0 or j[2]<0 or j[0]>=dims[0] or j[1]>=dims[1] or j[2]>=dims[2]:wp.atomic_add(bad,0,1);ids[p,s]=0;w[p,s]=wp.float64(0.0);g[p,s]=wp.vec3d(wp.float64(0.0));r[p,s]=wp.vec3d(wp.float64(0.0))       <L 32>
        var_2811 = wp::extract(var_2808, var_2810);
        var_2813 = (var_2811 < var_2812);
        var_2809 = var_2813;
        if (!var_2809) {
            var_2815 = wp::extract(var_2808, var_2814);
            var_2817 = (var_2815 < var_2816);
            var_2809 = var_2809 || var_2817;
        }
        if (!var_2809) {
            var_2819 = wp::extract(var_2808, var_2818);
            var_2821 = (var_2819 < var_2820);
            var_2809 = var_2809 || var_2821;
        }
        if (!var_2809) {
            var_2823 = wp::extract(var_2808, var_2822);
            var_2825 = wp::extract(var_dims, var_2824);
            var_2826 = (var_2823 >= var_2825);
            var_2809 = var_2809 || var_2826;
        }
        if (!var_2809) {
            var_2828 = wp::extract(var_2808, var_2827);
            var_2830 = wp::extract(var_dims, var_2829);
            var_2831 = (var_2828 >= var_2830);
            var_2809 = var_2809 || var_2831;
        }
        if (!var_2809) {
            var_2833 = wp::extract(var_2808, var_2832);
            var_2835 = wp::extract(var_dims, var_2834);
            var_2836 = (var_2833 >= var_2835);
            var_2809 = var_2809 || var_2836;
        }
        if (var_2809) {
            var_2839 = wp::atomic_add(var_bad, var_2837, var_2838);
            wp::array_store(var_ids, var_0, var_2805, var_2840);
            var_2841 = 0.0;
            wp::array_store(var_w, var_0, var_2805, var_2841);
            var_2842 = 0.0;
            var_2843 = wp::vec_t<3, wp::float64>(var_2842);
            wp::array_store(var_g, var_0, var_2805, var_2843);
            var_2844 = 0.0;
            var_2845 = wp::vec_t<3, wp::float64>(var_2844);
            wp::array_store(var_r, var_0, var_2805, var_2845);
        }
        if (!var_2809) {
            // ids[p,s]=(j[0]*dims[1]+j[1])*dims[2]+j[2];wx=basis(a,f[0]);wy=basis(b,f[1]);wz=basis(c,f[2]);w[p,s]=wx*wy*wz;g[p,s]=wp.vec3d(dbasis(a,f[0])*wy*wz,wx*dbasis(b,f[1])*wz,wx*wy*dbasis(c,f[2]))/h;r[p,s]=wp.vec3d(wp.float64(node[0]),wp.float64(node[1]),wp.float64(node[2]))*h-x[p]       <L 34>
            var_2847 = wp::extract(var_2808, var_2846);
            var_2849 = wp::extract(var_dims, var_2848);
            var_2850 = wp::mul(var_2847, var_2849);
            var_2852 = wp::extract(var_2808, var_2851);
            var_2853 = wp::add(var_2850, var_2852);
            var_2855 = wp::extract(var_dims, var_2854);
            var_2856 = wp::mul(var_2853, var_2855);
            var_2858 = wp::extract(var_2808, var_2857);
            var_2859 = wp::add(var_2856, var_2858);
            wp::array_store(var_ids, var_0, var_2805, var_2859);
            var_2861 = wp::extract(var_33, var_2860);
            var_2862 = basis_0(var_1947, var_2861);
            var_2864 = wp::extract(var_33, var_2863);
            var_2865 = basis_0(var_2586, var_2864);
            var_2867 = wp::extract(var_33, var_2866);
            var_2868 = basis_0(var_2799, var_2867);
            var_2869 = wp::mul(var_2862, var_2865);
            var_2870 = wp::mul(var_2869, var_2868);
            wp::array_store(var_w, var_0, var_2805, var_2870);
            var_2872 = wp::extract(var_33, var_2871);
            var_2873 = dbasis_0(var_1947, var_2872);
            var_2874 = wp::mul(var_2873, var_2865);
            var_2875 = wp::mul(var_2874, var_2868);
            var_2877 = wp::extract(var_33, var_2876);
            var_2878 = dbasis_0(var_2586, var_2877);
            var_2879 = wp::mul(var_2862, var_2878);
            var_2880 = wp::mul(var_2879, var_2868);
            var_2881 = wp::mul(var_2862, var_2865);
            var_2883 = wp::extract(var_33, var_2882);
            var_2884 = dbasis_0(var_2799, var_2883);
            var_2885 = wp::mul(var_2881, var_2884);
            var_2886 = wp::vec_t<3, wp::float64>(var_2875, var_2880, var_2885);
            var_2887 = wp::div(var_2886, var_h);
            wp::array_store(var_g, var_0, var_2805, var_2887);
            var_2889 = wp::extract(var_2807, var_2888);
            var_2890 = wp::float64(var_2889);
            var_2892 = wp::extract(var_2807, var_2891);
            var_2893 = wp::float64(var_2892);
            var_2895 = wp::extract(var_2807, var_2894);
            var_2896 = wp::float64(var_2895);
            var_2897 = wp::vec_t<3, wp::float64>(var_2890, var_2893, var_2896);
            var_2898 = wp::mul(var_2897, var_h);
            var_2899 = wp::address(var_x, var_0);
            var_2901 = wp::load(var_2899);
            var_2900 = wp::sub(var_2898, var_2901);
            wp::array_store(var_r, var_0, var_2805, var_2900);
        }
        var_2902 = wp::where(var_2809, var_2796, var_2862);
        var_2903 = wp::where(var_2809, var_2797, var_2865);
        var_2904 = wp::where(var_2809, var_2798, var_2868);
    }
}



extern "C" __global__ void g2p_170966a4_cuda_kernel_forward(
    wp::launch_bounds_t<1> dim,
    wp::array_t<wp::vec_t<3, wp::float64>> var_x,
    wp::array_t<wp::vec_t<3, wp::float64>> var_v,
    wp::array_t<wp::mat_t<3, 3, wp::float64>> var_C,
    wp::array_t<wp::mat_t<3, 3, wp::float64>> var_F,
    wp::array_t<wp::int32> var_codes,
    wp::array_t<wp::int32> var_lookup,
    wp::array_t<wp::int32> var_ids,
    wp::array_t<wp::float64> var_w,
    wp::array_t<wp::vec_t<3, wp::float64>> var_g,
    wp::array_t<wp::vec_t<3, wp::float64>> var_r,
    wp::array_t<wp::vec_t<3, wp::float64>> var_vg,
    wp::float64 var_dt,
    wp::float64 var_h,
    wp::float64 var_mass,
    wp::array_t<wp::float64> var_stats)
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
        wp::int32* var_1;
        wp::int32* var_2;
        wp::int32 var_3;
        wp::int32 var_4;
        wp::int32 var_5;
        wp::float64 var_6;
        wp::vec_t<3, wp::float64> var_7;
        wp::float64 var_8;
        wp::mat_t<3, 3, wp::float64> var_9;
        wp::float64 var_10;
        wp::mat_t<3, 3, wp::float64> var_11;
        const wp::int32 var_12 = 27;
        wp::range_t var_13;
        wp::int32 var_14;
        wp::int32* var_15;
        wp::vec_t<3, wp::float64>* var_16;
        wp::int32 var_17;
        wp::vec_t<3, wp::float64> var_18;
        wp::vec_t<3, wp::float64> var_19;
        wp::float64* var_20;
        wp::vec_t<3, wp::float64> var_21;
        wp::float64 var_22;
        wp::vec_t<3, wp::float64> var_23;
        wp::float64 var_24;
        wp::float64 var_25;
        wp::float64 var_26;
        wp::float64* var_27;
        wp::float64 var_28;
        wp::float64 var_29;
        wp::vec_t<3, wp::float64>* var_30;
        wp::mat_t<3, 3, wp::float64> var_31;
        wp::vec_t<3, wp::float64> var_32;
        wp::mat_t<3, 3, wp::float64> var_33;
        wp::mat_t<3, 3, wp::float64> var_34;
        wp::vec_t<3, wp::float64>* var_35;
        wp::mat_t<3, 3, wp::float64> var_36;
        wp::vec_t<3, wp::float64> var_37;
        wp::mat_t<3, 3, wp::float64> var_38;
        const wp::int32 var_39 = 3;
        wp::mat_t<3, 3, wp::float64> var_40;
        wp::vec_t<3, wp::float64>* var_41;
        wp::vec_t<3, wp::float64> var_42;
        wp::vec_t<3, wp::float64> var_43;
        wp::vec_t<3, wp::float64> var_44;
        wp::mat_t<3, 3, wp::float64> var_45;
        wp::mat_t<3, 3, wp::float64> var_46;
        wp::mat_t<3, 3, wp::float64>* var_47;
        wp::mat_t<3, 3, wp::float64> var_48;
        wp::mat_t<3, 3, wp::float64> var_49;
        wp::float64 var_50;
        const wp::int32 var_51 = 0;
        const wp::int32 var_52 = 0;
        wp::float64 var_53;
        wp::float64 var_54;
        wp::float64 var_55;
        wp::float64 var_56;
        const wp::int32 var_57 = 1;
        wp::float64 var_58;
        wp::float64 var_59;
        wp::float64 var_60;
        wp::float64 var_61;
        const wp::int32 var_62 = 2;
        wp::float64 var_63;
        wp::float64 var_64;
        wp::float64 var_65;
        wp::float64 var_66;
        const wp::int32 var_67 = 1;
        const wp::int32 var_68 = 0;
        wp::float64 var_69;
        wp::float64 var_70;
        wp::float64 var_71;
        wp::float64 var_72;
        const wp::int32 var_73 = 1;
        wp::float64 var_74;
        wp::float64 var_75;
        wp::float64 var_76;
        wp::float64 var_77;
        const wp::int32 var_78 = 2;
        wp::float64 var_79;
        wp::float64 var_80;
        wp::float64 var_81;
        wp::float64 var_82;
        const wp::int32 var_83 = 2;
        const wp::int32 var_84 = 0;
        wp::float64 var_85;
        wp::float64 var_86;
        wp::float64 var_87;
        wp::float64 var_88;
        const wp::int32 var_89 = 1;
        wp::float64 var_90;
        wp::float64 var_91;
        wp::float64 var_92;
        wp::float64 var_93;
        const wp::int32 var_94 = 2;
        wp::float64 var_95;
        wp::float64 var_96;
        wp::float64 var_97;
        wp::float64 var_98;
        const wp::int32 var_99 = 5;
        wp::float64 var_100;
        wp::float64 var_101;
        wp::float64 var_102;
        wp::float64 var_103;
        wp::float64 var_104;
        wp::float64 var_105;
        wp::float64 var_106;
        wp::float64 var_107;
        wp::float64 var_108;
        wp::float64 var_109;
        //---------
        // forward
        // def g2p(x:wp.array(dtype=wp.vec3d),v:wp.array(dtype=wp.vec3d),C:wp.array(dtype=wp.mat33d),F:wp.array(dtype=wp.mat33d),codes:wp.array(dtype=int),lookup:wp.array(dtype=int),ids:wp.array2d(dtype=int),w:wp.array2d(dtype=wp.float64),g:wp.array2d(dtype=wp.vec3d),r:wp.array2d(dtype=wp.vec3d),vg:wp.array2d(dtype=wp.vec3d),dt:wp.float64,h:wp.float64,mass:wp.float64,stats:wp.array(dtype=wp.float64)):       <L 62>
        // p=wp.tid();a=lookup[codes[p]];vv=wp.vec3d(wp.float64(0.0));cc=wp.mat33d(wp.float64(0.0));L=wp.mat33d(wp.float64(0.0))       <L 63>
        var_0 = builtin_tid1d();
        var_1 = wp::address(var_codes, var_0);
        var_3 = wp::load(var_1);
        var_2 = wp::address(var_lookup, var_3);
        var_5 = wp::load(var_2);
        var_4 = wp::copy(var_5);
        var_6 = 0.0;
        var_7 = wp::vec_t<3, wp::float64>(var_6);
        var_8 = 0.0;
        var_9 = wp::mat_t<3, 3, wp::float64>(var_8);
        var_10 = 0.0;
        var_11 = wp::mat_t<3, 3, wp::float64>(var_10);
        // for s in range(27):                                                                    <L 64>
        var_13 = wp::range(var_12);
        start_for_0:;
            if (iter_cmp(var_13) == 0) goto end_for_0;
            var_14 = wp::iter_next(var_13);
            // z=vg[a,ids[p,s]];vv+=w[p,s]*z;cc+=wp.float64(4.0)/h/h*w[p,s]*wp.outer(z,r[p,s]);L+=wp.outer(z,g[p,s])       <L 65>
            var_15 = wp::address(var_ids, var_0, var_14);
            var_17 = wp::load(var_15);
            var_16 = wp::address(var_vg, var_4, var_17);
            var_19 = wp::load(var_16);
            var_18 = wp::copy(var_19);
            var_20 = wp::address(var_w, var_0, var_14);
            var_22 = wp::load(var_20);
            var_21 = wp::mul(var_22, var_18);
            var_23 = wp::add(var_7, var_21);
            var_24 = 4.0;
            var_25 = wp::div(var_24, var_h);
            var_26 = wp::div(var_25, var_h);
            var_27 = wp::address(var_w, var_0, var_14);
            var_29 = wp::load(var_27);
            var_28 = wp::mul(var_26, var_29);
            var_30 = wp::address(var_r, var_0, var_14);
            var_32 = wp::load(var_30);
            var_31 = wp::outer(var_18, var_32);
            var_33 = wp::mul(var_28, var_31);
            var_34 = wp::add(var_9, var_33);
            var_35 = wp::address(var_g, var_0, var_14);
            var_37 = wp::load(var_35);
            var_36 = wp::outer(var_18, var_37);
            var_38 = wp::add(var_11, var_36);
            wp::assign(var_7, var_23);
            wp::assign(var_9, var_34);
            wp::assign(var_11, var_38);
            goto start_for_0;
        end_for_0:;
        // I=wp.identity(n=3,dtype=wp.float64);v[p]=vv;C[p]=cc;x[p]=x[p]+dt*vv;F[p]=(I+dt*L)*F[p];cn=wp.float64(0.0)       <L 66>
        var_40 = wp::identity<3, wp::float64>();
        wp::array_store(var_v, var_0, var_7);
        wp::array_store(var_C, var_0, var_9);
        var_41 = wp::address(var_x, var_0);
        var_42 = wp::mul(var_dt, var_7);
        var_44 = wp::load(var_41);
        var_43 = wp::add(var_44, var_42);
        wp::array_store(var_x, var_0, var_43);
        var_45 = wp::mul(var_dt, var_11);
        var_46 = wp::add(var_40, var_45);
        var_47 = wp::address(var_F, var_0);
        var_49 = wp::load(var_47);
        var_48 = wp::mul(var_46, var_49);
        wp::array_store(var_F, var_0, var_48);
        var_50 = 0.0;
        // for i in range(3):                                                                     <L 67>
        // for j in range(3):cn+=cc[i,j]*cc[i,j]                                                  <L 68>
        var_53 = wp::extract(var_9, var_51, var_52);
        var_54 = wp::extract(var_9, var_51, var_52);
        var_55 = wp::mul(var_53, var_54);
        var_56 = wp::add(var_50, var_55);
        var_58 = wp::extract(var_9, var_51, var_57);
        var_59 = wp::extract(var_9, var_51, var_57);
        var_60 = wp::mul(var_58, var_59);
        var_61 = wp::add(var_56, var_60);
        var_63 = wp::extract(var_9, var_51, var_62);
        var_64 = wp::extract(var_9, var_51, var_62);
        var_65 = wp::mul(var_63, var_64);
        var_66 = wp::add(var_61, var_65);
        var_69 = wp::extract(var_9, var_67, var_68);
        var_70 = wp::extract(var_9, var_67, var_68);
        var_71 = wp::mul(var_69, var_70);
        var_72 = wp::add(var_66, var_71);
        var_74 = wp::extract(var_9, var_67, var_73);
        var_75 = wp::extract(var_9, var_67, var_73);
        var_76 = wp::mul(var_74, var_75);
        var_77 = wp::add(var_72, var_76);
        var_79 = wp::extract(var_9, var_67, var_78);
        var_80 = wp::extract(var_9, var_67, var_78);
        var_81 = wp::mul(var_79, var_80);
        var_82 = wp::add(var_77, var_81);
        var_85 = wp::extract(var_9, var_83, var_84);
        var_86 = wp::extract(var_9, var_83, var_84);
        var_87 = wp::mul(var_85, var_86);
        var_88 = wp::add(var_82, var_87);
        var_90 = wp::extract(var_9, var_83, var_89);
        var_91 = wp::extract(var_9, var_83, var_89);
        var_92 = wp::mul(var_90, var_91);
        var_93 = wp::add(var_88, var_92);
        var_95 = wp::extract(var_9, var_83, var_94);
        var_96 = wp::extract(var_9, var_83, var_94);
        var_97 = wp::mul(var_95, var_96);
        var_98 = wp::add(var_93, var_97);
        // wp.atomic_add(stats,5,wp.float64(.5)*mass*(wp.dot(vv,vv)+h*h/wp.float64(4.0)*cn))       <L 69>
        var_100 = 0.5;
        var_101 = wp::mul(var_100, var_mass);
        var_102 = wp::dot(var_7, var_7);
        var_103 = wp::mul(var_h, var_h);
        var_104 = 4.0;
        var_105 = wp::div(var_103, var_104);
        var_106 = wp::mul(var_105, var_98);
        var_107 = wp::add(var_102, var_106);
        var_108 = wp::mul(var_101, var_107);
        var_109 = wp::atomic_add(var_stats, var_99, var_108);
    }
}



extern "C" __global__ void tally_35d6e19b_cuda_kernel_forward(
    wp::launch_bounds_t<1> dim,
    wp::array_t<wp::float64> var_stats,
    wp::array_t<wp::float64> var_totals)
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
        wp::float64* var_1;
        const wp::int32 var_2 = 2;
        wp::float64* var_3;
        wp::float64 var_4;
        wp::float64 var_5;
        wp::float64 var_6;
        const wp::int32 var_7 = 4;
        wp::float64* var_8;
        wp::float64 var_9;
        wp::float64 var_10;
        const wp::int32 var_11 = 5;
        wp::float64* var_12;
        wp::float64 var_13;
        wp::float64 var_14;
        const wp::int32 var_15 = 0;
        wp::float64 var_16;
        const wp::int32 var_17 = 3;
        wp::float64* var_18;
        const wp::int32 var_19 = 4;
        wp::float64* var_20;
        wp::float64 var_21;
        wp::float64 var_22;
        wp::float64 var_23;
        const wp::int32 var_24 = 1;
        wp::float64 var_25;
        //---------
        // forward
        // def tally(stats:wp.array(dtype=wp.float64),totals:wp.array(dtype=wp.float64)):         <L 71>
        // totals[0]+=stats[0]-stats[2]+stats[4]-stats[5];totals[1]+=stats[3]-stats[4]            <L 72>
        var_1 = wp::address(var_stats, var_0);
        var_3 = wp::address(var_stats, var_2);
        var_5 = wp::load(var_1);
        var_6 = wp::load(var_3);
        var_4 = wp::sub(var_5, var_6);
        var_8 = wp::address(var_stats, var_7);
        var_10 = wp::load(var_8);
        var_9 = wp::add(var_4, var_10);
        var_12 = wp::address(var_stats, var_11);
        var_14 = wp::load(var_12);
        var_13 = wp::sub(var_9, var_14);
        var_16 = wp::atomic_add(var_totals, var_15, var_13);
        var_18 = wp::address(var_stats, var_17);
        var_20 = wp::address(var_stats, var_19);
        var_22 = wp::load(var_18);
        var_23 = wp::load(var_20);
        var_21 = wp::sub(var_22, var_23);
        var_25 = wp::atomic_add(var_totals, var_24, var_21);
    }
}



extern "C" __global__ void grid_update_4d65019d_cuda_kernel_forward(
    wp::launch_bounds_t<2> dim,
    wp::array_t<wp::float64> var_m,
    wp::array_t<wp::vec_t<3, wp::float64>> var_p,
    wp::array_t<wp::vec_t<3, wp::float64>> var_f,
    wp::array_t<wp::int32> var_active,
    wp::int32 var_count,
    wp::float64 var_dt,
    wp::array_t<wp::vec_t<3, wp::float64>> var_vg,
    wp::array_t<wp::float64> var_stats)
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
        wp::float64* var_2;
        wp::float64 var_3;
        wp::float64 var_4;
        wp::vec_t<3, wp::float64>* var_5;
        wp::vec_t<3, wp::float64> var_6;
        wp::vec_t<3, wp::float64> var_7;
        wp::float64 var_8;
        wp::float64 var_9;
        wp::vec_t<3, wp::float64> var_10;
        wp::range_t var_11;
        wp::int32 var_12;
        wp::float64* var_13;
        wp::float64 var_14;
        wp::float64 var_15;
        wp::float64 var_16;
        bool var_17;
        wp::float64 var_18;
        wp::vec_t<3, wp::float64> var_19;
        wp::range_t var_20;
        wp::int32 var_21;
        bool var_22;
        bool var_23;
        wp::int32* var_24;
        wp::int32* var_25;
        bool var_26;
        wp::int32 var_27;
        wp::int32 var_28;
        wp::vec_t<3, wp::float64>* var_29;
        wp::vec_t<3, wp::float64> var_30;
        wp::vec_t<3, wp::float64> var_31;
        wp::float64* var_32;
        wp::vec_t<3, wp::float64> var_33;
        wp::float64 var_34;
        wp::vec_t<3, wp::float64> var_35;
        wp::vec_t<3, wp::float64> var_36;
        wp::vec_t<3, wp::float64> var_37;
        wp::vec_t<3, wp::float64> var_38;
        wp::vec_t<3, wp::float64> var_39;
        wp::vec_t<3, wp::float64>* var_40;
        wp::vec_t<3, wp::float64> var_41;
        wp::vec_t<3, wp::float64> var_42;
        wp::vec_t<3, wp::float64> var_43;
        wp::vec_t<3, wp::float64> var_44;
        const wp::int32 var_45 = 1;
        wp::float64 var_46;
        wp::float64 var_47;
        wp::float64 var_48;
        wp::float64 var_49;
        wp::float64 var_50;
        const wp::int32 var_51 = 2;
        wp::float64 var_52;
        wp::float64 var_53;
        wp::float64 var_54;
        wp::float64 var_55;
        wp::float64 var_56;
        const wp::int32 var_57 = 3;
        wp::float64 var_58;
        wp::float64 var_59;
        wp::float64 var_60;
        wp::float64 var_61;
        wp::float64 var_62;
        wp::int32 var_63;
        //---------
        // forward
        // def grid_update(m:wp.array2d(dtype=wp.float64),p:wp.array2d(dtype=wp.vec3d),f:wp.array2d(dtype=wp.vec3d),active:wp.array(dtype=int),count:int,dt:wp.float64,vg:wp.array2d(dtype=wp.vec3d),stats:wp.array(dtype=wp.float64)):       <L 50>
        // a,i=wp.tid();ma=m[a,i];pa=p[a,i];M=wp.float64(0.0);vg[a,i]=wp.vec3d(wp.float64(0.0))       <L 51>
        builtin_tid2d(var_0, var_1);
        var_2 = wp::address(var_m, var_0, var_1);
        var_4 = wp::load(var_2);
        var_3 = wp::copy(var_4);
        var_5 = wp::address(var_p, var_0, var_1);
        var_7 = wp::load(var_5);
        var_6 = wp::copy(var_7);
        var_8 = 0.0;
        var_9 = 0.0;
        var_10 = wp::vec_t<3, wp::float64>(var_9);
        wp::array_store(var_vg, var_0, var_1, var_10);
        // for b in range(count):M+=m[b,i]                                                        <L 52>
        var_11 = wp::range(var_count);
        start_for_0:;
            if (iter_cmp(var_11) == 0) goto end_for_0;
            var_12 = wp::iter_next(var_11);
            var_13 = wp::address(var_m, var_12, var_1);
            var_15 = wp::load(var_13);
            var_14 = wp::add(var_8, var_15);
            wp::assign(var_8, var_14);
            goto start_for_0;
        end_for_0:;
        // if ma>wp.float64(0.0):                                                                 <L 53>
        var_16 = 0.0;
        var_17 = (var_3 > var_16);
        if (var_17) {
            // dp=wp.vec3d(wp.float64(0.0))                                                       <L 54>
            var_18 = 0.0;
            var_19 = wp::vec_t<3, wp::float64>(var_18);
            // for b in range(count):                                                             <L 55>
            var_20 = wp::range(var_count);
            start_for_2:;
                if (iter_cmp(var_20) == 0) goto end_for_2;
                var_21 = wp::iter_next(var_20);
                // if b!=a and compatible(active[a],active[b]):dp+=ma*p[b,i]-m[b,i]*pa            <L 56>
                var_23 = (var_21 != var_0);
                var_22 = var_23;
                if (var_22) {
                    var_24 = wp::address(var_active, var_0);
                    var_25 = wp::address(var_active, var_21);
                    var_27 = wp::load(var_24);
                    var_28 = wp::load(var_25);
                    var_26 = compatible_0(var_27, var_28);
                    var_22 = var_22 && var_26;
                }
                if (var_22) {
                    var_29 = wp::address(var_p, var_21, var_1);
                    var_31 = wp::load(var_29);
                    var_30 = wp::mul(var_3, var_31);
                    var_32 = wp::address(var_m, var_21, var_1);
                    var_34 = wp::load(var_32);
                    var_33 = wp::mul(var_34, var_6);
                    var_35 = wp::sub(var_30, var_33);
                    var_36 = wp::add(var_19, var_35);
                }
                var_37 = wp::where(var_22, var_36, var_19);
                wp::assign(var_19, var_37);
                goto start_for_2;
            end_for_2:;
            // coupled=pa+dp/M;v=(coupled+dt*f[a,i])/ma;vg[a,i]=v;wp.atomic_add(stats,1,wp.float64(.5)*wp.dot(pa,pa)/ma);wp.atomic_add(stats,2,wp.float64(.5)*wp.dot(coupled,coupled)/ma);wp.atomic_add(stats,3,wp.float64(.5)*ma*wp.dot(v,v))       <L 57>
            var_38 = wp::div(var_19, var_8);
            var_39 = wp::add(var_6, var_38);
            var_40 = wp::address(var_f, var_0, var_1);
            var_42 = wp::load(var_40);
            var_41 = wp::mul(var_dt, var_42);
            var_43 = wp::add(var_39, var_41);
            var_44 = wp::div(var_43, var_3);
            wp::array_store(var_vg, var_0, var_1, var_44);
            var_46 = 0.5;
            var_47 = wp::dot(var_6, var_6);
            var_48 = wp::mul(var_46, var_47);
            var_49 = wp::div(var_48, var_3);
            var_50 = wp::atomic_add(var_stats, var_45, var_49);
            var_52 = 0.5;
            var_53 = wp::dot(var_39, var_39);
            var_54 = wp::mul(var_52, var_53);
            var_55 = wp::div(var_54, var_3);
            var_56 = wp::atomic_add(var_stats, var_51, var_55);
            var_58 = 0.5;
            var_59 = wp::mul(var_58, var_3);
            var_60 = wp::dot(var_44, var_44);
            var_61 = wp::mul(var_59, var_60);
            var_62 = wp::atomic_add(var_stats, var_57, var_61);
        }
        var_63 = wp::where(var_17, var_21, var_12);
    }
}



extern "C" __global__ void clear_530ee3ed_cuda_kernel_forward(
    wp::launch_bounds_t<2> dim,
    wp::array_t<wp::float64> var_m,
    wp::array_t<wp::vec_t<3, wp::float64>> var_p,
    wp::array_t<wp::vec_t<3, wp::float64>> var_f)
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
        wp::float64 var_2;
        wp::float64 var_3;
        wp::vec_t<3, wp::float64> var_4;
        wp::float64 var_5;
        wp::vec_t<3, wp::float64> var_6;
        //---------
        // forward
        // def clear(m:wp.array2d(dtype=wp.float64),p:wp.array2d(dtype=wp.vec3d),f:wp.array2d(dtype=wp.vec3d)):       <L 36>
        // a,i=wp.tid();m[a,i]=wp.float64(0.0);p[a,i]=wp.vec3d(wp.float64(0.0));f[a,i]=wp.vec3d(wp.float64(0.0))       <L 37>
        builtin_tid2d(var_0, var_1);
        var_2 = 0.0;
        wp::array_store(var_m, var_0, var_1, var_2);
        var_3 = 0.0;
        var_4 = wp::vec_t<3, wp::float64>(var_3);
        wp::array_store(var_p, var_0, var_1, var_4);
        var_5 = 0.0;
        var_6 = wp::vec_t<3, wp::float64>(var_5);
        wp::array_store(var_f, var_0, var_1, var_6);
    }
}



extern "C" __global__ void p2g_ca577be2_cuda_kernel_forward(
    wp::launch_bounds_t<1> dim,
    wp::array_t<wp::vec_t<3, wp::float64>> var_v,
    wp::array_t<wp::mat_t<3, 3, wp::float64>> var_C,
    wp::array_t<wp::mat_t<3, 3, wp::float64>> var_F,
    wp::array_t<wp::int32> var_codes,
    wp::array_t<wp::int32> var_lookup,
    wp::array_t<wp::int32> var_ids,
    wp::array_t<wp::float64> var_w,
    wp::array_t<wp::vec_t<3, wp::float64>> var_g,
    wp::array_t<wp::vec_t<3, wp::float64>> var_r,
    wp::array_t<wp::vec_t<3, wp::float64>> var_external,
    wp::float64 var_mass,
    wp::float64 var_vol,
    wp::float64 var_mu,
    wp::float64 var_lam,
    wp::float64 var_h,
    wp::array_t<wp::float64> var_m,
    wp::array_t<wp::vec_t<3, wp::float64>> var_p,
    wp::array_t<wp::vec_t<3, wp::float64>> var_force,
    wp::array_t<wp::float64> var_stats,
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
        wp::int32* var_1;
        wp::int32* var_2;
        wp::int32 var_3;
        wp::int32 var_4;
        wp::int32 var_5;
        wp::mat_t<3, 3, wp::float64>* var_6;
        wp::float64 var_7;
        wp::mat_t<3, 3, wp::float64> var_8;
        wp::float64 var_9;
        const wp::int32 var_10 = 0;
        const wp::int32 var_11 = 0;
        wp::mat_t<3, 3, wp::float64>* var_12;
        wp::float64 var_13;
        wp::mat_t<3, 3, wp::float64> var_14;
        wp::mat_t<3, 3, wp::float64>* var_15;
        wp::float64 var_16;
        wp::mat_t<3, 3, wp::float64> var_17;
        wp::float64 var_18;
        wp::float64 var_19;
        const wp::int32 var_20 = 1;
        wp::mat_t<3, 3, wp::float64>* var_21;
        wp::float64 var_22;
        wp::mat_t<3, 3, wp::float64> var_23;
        wp::mat_t<3, 3, wp::float64>* var_24;
        wp::float64 var_25;
        wp::mat_t<3, 3, wp::float64> var_26;
        wp::float64 var_27;
        wp::float64 var_28;
        const wp::int32 var_29 = 2;
        wp::mat_t<3, 3, wp::float64>* var_30;
        wp::float64 var_31;
        wp::mat_t<3, 3, wp::float64> var_32;
        wp::mat_t<3, 3, wp::float64>* var_33;
        wp::float64 var_34;
        wp::mat_t<3, 3, wp::float64> var_35;
        wp::float64 var_36;
        wp::float64 var_37;
        const wp::int32 var_38 = 1;
        const wp::int32 var_39 = 0;
        wp::mat_t<3, 3, wp::float64>* var_40;
        wp::float64 var_41;
        wp::mat_t<3, 3, wp::float64> var_42;
        wp::mat_t<3, 3, wp::float64>* var_43;
        wp::float64 var_44;
        wp::mat_t<3, 3, wp::float64> var_45;
        wp::float64 var_46;
        wp::float64 var_47;
        const wp::int32 var_48 = 1;
        wp::mat_t<3, 3, wp::float64>* var_49;
        wp::float64 var_50;
        wp::mat_t<3, 3, wp::float64> var_51;
        wp::mat_t<3, 3, wp::float64>* var_52;
        wp::float64 var_53;
        wp::mat_t<3, 3, wp::float64> var_54;
        wp::float64 var_55;
        wp::float64 var_56;
        const wp::int32 var_57 = 2;
        wp::mat_t<3, 3, wp::float64>* var_58;
        wp::float64 var_59;
        wp::mat_t<3, 3, wp::float64> var_60;
        wp::mat_t<3, 3, wp::float64>* var_61;
        wp::float64 var_62;
        wp::mat_t<3, 3, wp::float64> var_63;
        wp::float64 var_64;
        wp::float64 var_65;
        const wp::int32 var_66 = 2;
        const wp::int32 var_67 = 0;
        wp::mat_t<3, 3, wp::float64>* var_68;
        wp::float64 var_69;
        wp::mat_t<3, 3, wp::float64> var_70;
        wp::mat_t<3, 3, wp::float64>* var_71;
        wp::float64 var_72;
        wp::mat_t<3, 3, wp::float64> var_73;
        wp::float64 var_74;
        wp::float64 var_75;
        const wp::int32 var_76 = 1;
        wp::mat_t<3, 3, wp::float64>* var_77;
        wp::float64 var_78;
        wp::mat_t<3, 3, wp::float64> var_79;
        wp::mat_t<3, 3, wp::float64>* var_80;
        wp::float64 var_81;
        wp::mat_t<3, 3, wp::float64> var_82;
        wp::float64 var_83;
        wp::float64 var_84;
        const wp::int32 var_85 = 2;
        wp::mat_t<3, 3, wp::float64>* var_86;
        wp::float64 var_87;
        wp::mat_t<3, 3, wp::float64> var_88;
        wp::mat_t<3, 3, wp::float64>* var_89;
        wp::float64 var_90;
        wp::mat_t<3, 3, wp::float64> var_91;
        wp::float64 var_92;
        wp::float64 var_93;
        const wp::int32 var_94 = 0;
        wp::float64 var_95;
        wp::float64 var_96;
        wp::vec_t<3, wp::float64>* var_97;
        wp::vec_t<3, wp::float64>* var_98;
        wp::float64 var_99;
        wp::vec_t<3, wp::float64> var_100;
        wp::vec_t<3, wp::float64> var_101;
        wp::float64 var_102;
        wp::float64 var_103;
        wp::float64 var_104;
        wp::float64 var_105;
        wp::float64 var_106;
        wp::float64 var_107;
        wp::float64 var_108;
        bool var_109;
        wp::float64 var_110;
        bool var_111;
        wp::float64 var_112;
        bool var_113;
        bool var_114;
        bool var_115;
        const wp::int32 var_116 = 0;
        const wp::int32 var_117 = 1;
        wp::int32 var_118;
        wp::mat_t<3, 3, wp::float64>* var_119;
        wp::mat_t<3, 3, wp::float64> var_120;
        wp::mat_t<3, 3, wp::float64> var_121;
        wp::float64 var_122;
        wp::float64 var_123;
        wp::float64 var_124;
        wp::mat_t<3, 3, wp::float64>* var_125;
        wp::mat_t<3, 3, wp::float64> var_126;
        wp::mat_t<3, 3, wp::float64> var_127;
        wp::mat_t<3, 3, wp::float64> var_128;
        wp::mat_t<3, 3, wp::float64> var_129;
        wp::mat_t<3, 3, wp::float64> var_130;
        wp::mat_t<3, 3, wp::float64>* var_131;
        wp::mat_t<3, 3, wp::float64> var_132;
        wp::mat_t<3, 3, wp::float64> var_133;
        wp::mat_t<3, 3, wp::float64> var_134;
        const wp::int32 var_135 = 27;
        wp::range_t var_136;
        wp::int32 var_137;
        wp::int32 var_138;
        wp::int32* var_139;
        wp::int32 var_140;
        wp::int32 var_141;
        wp::float64* var_142;
        wp::float64 var_143;
        wp::float64 var_144;
        wp::float64 var_145;
        wp::vec_t<3, wp::float64>* var_146;
        wp::mat_t<3, 3, wp::float64>* var_147;
        wp::vec_t<3, wp::float64>* var_148;
        wp::vec_t<3, wp::float64> var_149;
        wp::mat_t<3, 3, wp::float64> var_150;
        wp::vec_t<3, wp::float64> var_151;
        wp::vec_t<3, wp::float64> var_152;
        wp::vec_t<3, wp::float64> var_153;
        wp::vec_t<3, wp::float64> var_154;
        wp::vec_t<3, wp::float64> var_155;
        wp::float64 var_156;
        wp::vec_t<3, wp::float64>* var_157;
        wp::vec_t<3, wp::float64> var_158;
        wp::vec_t<3, wp::float64> var_159;
        wp::vec_t<3, wp::float64> var_160;
        wp::float64* var_161;
        wp::vec_t<3, wp::float64>* var_162;
        wp::vec_t<3, wp::float64> var_163;
        wp::float64 var_164;
        wp::vec_t<3, wp::float64> var_165;
        wp::vec_t<3, wp::float64> var_166;
        wp::vec_t<3, wp::float64> var_167;
        wp::int32 var_168;
        //---------
        // forward
        // def p2g(v:wp.array(dtype=wp.vec3d),C:wp.array(dtype=wp.mat33d),F:wp.array(dtype=wp.mat33d),codes:wp.array(dtype=int),lookup:wp.array(dtype=int),ids:wp.array2d(dtype=int),w:wp.array2d(dtype=wp.float64),g:wp.array2d(dtype=wp.vec3d),r:wp.array2d(dtype=wp.vec3d),external:wp.array(dtype=wp.vec3d),mass:wp.float64,vol:wp.float64,mu:wp.float64,lam:wp.float64,h:wp.float64,m:wp.array2d(dtype=wp.float64),p:wp.array2d(dtype=wp.vec3d),force:wp.array2d(dtype=wp.vec3d),stats:wp.array(dtype=wp.float64),bad:wp.array(dtype=int)):       <L 39>
        // k=wp.tid();a=lookup[codes[k]];J=wp.determinant(F[k]);cn=wp.float64(0.0)                <L 40>
        var_0 = builtin_tid1d();
        var_1 = wp::address(var_codes, var_0);
        var_3 = wp::load(var_1);
        var_2 = wp::address(var_lookup, var_3);
        var_5 = wp::load(var_2);
        var_4 = wp::copy(var_5);
        var_6 = wp::address(var_F, var_0);
        var_8 = wp::load(var_6);
        var_7 = wp::determinant(var_8);
        var_9 = 0.0;
        // for i in range(3):                                                                     <L 41>
        // for j in range(3):cn+=C[k][i,j]*C[k][i,j]                                              <L 42>
        var_12 = wp::address(var_C, var_0);
        var_14 = wp::load(var_12);
        var_13 = wp::extract(var_14, var_10, var_11);
        var_15 = wp::address(var_C, var_0);
        var_17 = wp::load(var_15);
        var_16 = wp::extract(var_17, var_10, var_11);
        var_18 = wp::mul(var_13, var_16);
        var_19 = wp::add(var_9, var_18);
        var_21 = wp::address(var_C, var_0);
        var_23 = wp::load(var_21);
        var_22 = wp::extract(var_23, var_10, var_20);
        var_24 = wp::address(var_C, var_0);
        var_26 = wp::load(var_24);
        var_25 = wp::extract(var_26, var_10, var_20);
        var_27 = wp::mul(var_22, var_25);
        var_28 = wp::add(var_19, var_27);
        var_30 = wp::address(var_C, var_0);
        var_32 = wp::load(var_30);
        var_31 = wp::extract(var_32, var_10, var_29);
        var_33 = wp::address(var_C, var_0);
        var_35 = wp::load(var_33);
        var_34 = wp::extract(var_35, var_10, var_29);
        var_36 = wp::mul(var_31, var_34);
        var_37 = wp::add(var_28, var_36);
        var_40 = wp::address(var_C, var_0);
        var_42 = wp::load(var_40);
        var_41 = wp::extract(var_42, var_38, var_39);
        var_43 = wp::address(var_C, var_0);
        var_45 = wp::load(var_43);
        var_44 = wp::extract(var_45, var_38, var_39);
        var_46 = wp::mul(var_41, var_44);
        var_47 = wp::add(var_37, var_46);
        var_49 = wp::address(var_C, var_0);
        var_51 = wp::load(var_49);
        var_50 = wp::extract(var_51, var_38, var_48);
        var_52 = wp::address(var_C, var_0);
        var_54 = wp::load(var_52);
        var_53 = wp::extract(var_54, var_38, var_48);
        var_55 = wp::mul(var_50, var_53);
        var_56 = wp::add(var_47, var_55);
        var_58 = wp::address(var_C, var_0);
        var_60 = wp::load(var_58);
        var_59 = wp::extract(var_60, var_38, var_57);
        var_61 = wp::address(var_C, var_0);
        var_63 = wp::load(var_61);
        var_62 = wp::extract(var_63, var_38, var_57);
        var_64 = wp::mul(var_59, var_62);
        var_65 = wp::add(var_56, var_64);
        var_68 = wp::address(var_C, var_0);
        var_70 = wp::load(var_68);
        var_69 = wp::extract(var_70, var_66, var_67);
        var_71 = wp::address(var_C, var_0);
        var_73 = wp::load(var_71);
        var_72 = wp::extract(var_73, var_66, var_67);
        var_74 = wp::mul(var_69, var_72);
        var_75 = wp::add(var_65, var_74);
        var_77 = wp::address(var_C, var_0);
        var_79 = wp::load(var_77);
        var_78 = wp::extract(var_79, var_66, var_76);
        var_80 = wp::address(var_C, var_0);
        var_82 = wp::load(var_80);
        var_81 = wp::extract(var_82, var_66, var_76);
        var_83 = wp::mul(var_78, var_81);
        var_84 = wp::add(var_75, var_83);
        var_86 = wp::address(var_C, var_0);
        var_88 = wp::load(var_86);
        var_87 = wp::extract(var_88, var_66, var_85);
        var_89 = wp::address(var_C, var_0);
        var_91 = wp::load(var_89);
        var_90 = wp::extract(var_91, var_66, var_85);
        var_92 = wp::mul(var_87, var_90);
        var_93 = wp::add(var_84, var_92);
        // wp.atomic_add(stats,0,wp.float64(.5)*mass*(wp.dot(v[k],v[k])+h*h/wp.float64(4.0)*cn))       <L 43>
        var_95 = 0.5;
        var_96 = wp::mul(var_95, var_mass);
        var_97 = wp::address(var_v, var_0);
        var_98 = wp::address(var_v, var_0);
        var_100 = wp::load(var_97);
        var_101 = wp::load(var_98);
        var_99 = wp::dot(var_100, var_101);
        var_102 = wp::mul(var_h, var_h);
        var_103 = 4.0;
        var_104 = wp::div(var_102, var_103);
        var_105 = wp::mul(var_104, var_93);
        var_106 = wp::add(var_99, var_105);
        var_107 = wp::mul(var_96, var_106);
        var_108 = wp::atomic_add(var_stats, var_94, var_107);
        // if J<=wp.float64(.1) or J>=wp.float64(10.0) or not wp.isfinite(J):wp.atomic_add(bad,0,1)       <L 44>
        var_110 = 0.1;
        var_111 = (var_7 <= var_110);
        var_109 = var_111;
        if (!var_109) {
            var_112 = 10.0;
            var_113 = (var_7 >= var_112);
            var_109 = var_109 || var_113;
        }
        if (!var_109) {
            var_114 = wp::isfinite(var_7);
            var_115 = wp::unot(var_114);
            var_109 = var_109 || var_115;
        }
        if (var_109) {
            var_118 = wp::atomic_add(var_bad, var_116, var_117);
        }
        if (!var_109) {
            // P=mu*F[k]+(lam*wp.log(J)-mu)*wp.transpose(wp.inverse(F[k]));tau=P*wp.transpose(F[k])       <L 46>
            var_119 = wp::address(var_F, var_0);
            var_121 = wp::load(var_119);
            var_120 = wp::mul(var_mu, var_121);
            var_122 = wp::log(var_7);
            var_123 = wp::mul(var_lam, var_122);
            var_124 = wp::sub(var_123, var_mu);
            var_125 = wp::address(var_F, var_0);
            var_127 = wp::load(var_125);
            var_126 = wp::inverse(var_127);
            var_128 = wp::transpose(var_126);
            var_129 = wp::mul(var_124, var_128);
            var_130 = wp::add(var_120, var_129);
            var_131 = wp::address(var_F, var_0);
            var_133 = wp::load(var_131);
            var_132 = wp::transpose(var_133);
            var_134 = wp::mul(var_130, var_132);
            // for s in range(27):                                                                <L 47>
            var_136 = wp::range(var_135);
            var_137 = wp::copy(var_66);
            start_for_0:;
                if (iter_cmp(var_136) == 0) goto end_for_0;
                var_138 = wp::iter_next(var_136);
                // i=ids[k,s];wm=mass*w[k,s];wp.atomic_add(m,a,i,wm);wp.atomic_add(p,a,i,wm*(v[k]+C[k]*r[k,s]));wp.atomic_add(force,a,i,-vol*(tau*g[k,s])+w[k,s]*external[k])       <L 48>
                var_139 = wp::address(var_ids, var_0, var_138);
                var_141 = wp::load(var_139);
                var_140 = wp::copy(var_141);
                var_142 = wp::address(var_w, var_0, var_138);
                var_144 = wp::load(var_142);
                var_143 = wp::mul(var_mass, var_144);
                var_145 = wp::atomic_add(var_m, var_4, var_140, var_143);
                var_146 = wp::address(var_v, var_0);
                var_147 = wp::address(var_C, var_0);
                var_148 = wp::address(var_r, var_0, var_138);
                var_150 = wp::load(var_147);
                var_151 = wp::load(var_148);
                var_149 = wp::mul(var_150, var_151);
                var_153 = wp::load(var_146);
                var_152 = wp::add(var_153, var_149);
                var_154 = wp::mul(var_143, var_152);
                var_155 = wp::atomic_add(var_p, var_4, var_140, var_154);
                var_156 = wp::neg(var_vol);
                var_157 = wp::address(var_g, var_0, var_138);
                var_159 = wp::load(var_157);
                var_158 = wp::mul(var_134, var_159);
                var_160 = wp::mul(var_156, var_158);
                var_161 = wp::address(var_w, var_0, var_138);
                var_162 = wp::address(var_external, var_0);
                var_164 = wp::load(var_161);
                var_165 = wp::load(var_162);
                var_163 = wp::mul(var_164, var_165);
                var_166 = wp::add(var_160, var_163);
                var_167 = wp::atomic_add(var_force, var_4, var_140, var_166);
                wp::assign(var_137, var_140);
                goto start_for_0;
            end_for_0:;
        }
        var_168 = wp::where(var_109, var_66, var_137);
    }
}


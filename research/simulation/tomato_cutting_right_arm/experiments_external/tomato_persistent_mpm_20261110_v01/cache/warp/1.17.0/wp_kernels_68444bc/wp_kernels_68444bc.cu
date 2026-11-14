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


// /home/omen/Documents/Codex/experiments/tomato_persistent_mpm_20261110_v01/src/kernels.py:16
static CUDA_CALLABLE bool compatible_0(
    wp::int32 var_a,
    wp::int32 var_b)
{
    //---------
    // primal vars
    const bool var_0 = true;
    const wp::int32 var_1 = 0;
    const wp::int32 var_2 = 3;
    wp::int32 var_3;
    const wp::int32 var_4 = 3;
    wp::int32 var_5;
    wp::int32 var_6;
    const wp::int32 var_7 = 2;
    bool var_8;
    const bool var_9 = false;
    bool var_10;
    const wp::int32 var_11 = 3;
    wp::int32 var_12;
    const wp::int32 var_13 = 3;
    wp::int32 var_14;
    const wp::int32 var_15 = 1;
    const wp::int32 var_16 = 3;
    wp::int32 var_17;
    const wp::int32 var_18 = 3;
    wp::int32 var_19;
    wp::int32 var_20;
    const wp::int32 var_21 = 2;
    bool var_22;
    const bool var_23 = false;
    bool var_24;
    const wp::int32 var_25 = 3;
    wp::int32 var_26;
    const wp::int32 var_27 = 3;
    wp::int32 var_28;
    const wp::int32 var_29 = 2;
    const wp::int32 var_30 = 3;
    wp::int32 var_31;
    const wp::int32 var_32 = 3;
    wp::int32 var_33;
    wp::int32 var_34;
    const wp::int32 var_35 = 2;
    bool var_36;
    const bool var_37 = false;
    bool var_38;
    const wp::int32 var_39 = 3;
    wp::int32 var_40;
    const wp::int32 var_41 = 3;
    wp::int32 var_42;
    const wp::int32 var_43 = 3;
    const wp::int32 var_44 = 3;
    wp::int32 var_45;
    const wp::int32 var_46 = 3;
    wp::int32 var_47;
    wp::int32 var_48;
    const wp::int32 var_49 = 2;
    bool var_50;
    const bool var_51 = false;
    bool var_52;
    const wp::int32 var_53 = 3;
    wp::int32 var_54;
    const wp::int32 var_55 = 3;
    wp::int32 var_56;
    //---------
    // forward
    // def compatible(a:int,b:int):                                                           <L 17>
    // good=True                                                                              <L 18>
    // for k in range(4):                                                                     <L 19>
    // x=a%3;y=b%3                                                                            <L 20>
    var_3 = wp::mod(var_a, var_2);
    var_5 = wp::mod(var_b, var_4);
    // if x*y==2:good=False                                                                   <L 21>
    var_6 = wp::mul(var_3, var_5);
    var_8 = (var_6 == var_7);
    if (var_8) {
    }
    var_10 = wp::where(var_8, var_9, var_0);
    // a=a//3;b=b//3                                                                          <L 22>
    var_12 = wp::floordiv(var_a, var_11);
    var_14 = wp::floordiv(var_b, var_13);
    // x=a%3;y=b%3                                                                            <L 20>
    var_17 = wp::mod(var_12, var_16);
    var_19 = wp::mod(var_14, var_18);
    // if x*y==2:good=False                                                                   <L 21>
    var_20 = wp::mul(var_17, var_19);
    var_22 = (var_20 == var_21);
    if (var_22) {
    }
    var_24 = wp::where(var_22, var_23, var_10);
    // a=a//3;b=b//3                                                                          <L 22>
    var_26 = wp::floordiv(var_12, var_25);
    var_28 = wp::floordiv(var_14, var_27);
    // x=a%3;y=b%3                                                                            <L 20>
    var_31 = wp::mod(var_26, var_30);
    var_33 = wp::mod(var_28, var_32);
    // if x*y==2:good=False                                                                   <L 21>
    var_34 = wp::mul(var_31, var_33);
    var_36 = (var_34 == var_35);
    if (var_36) {
    }
    var_38 = wp::where(var_36, var_37, var_24);
    // a=a//3;b=b//3                                                                          <L 22>
    var_40 = wp::floordiv(var_26, var_39);
    var_42 = wp::floordiv(var_28, var_41);
    // x=a%3;y=b%3                                                                            <L 20>
    var_45 = wp::mod(var_40, var_44);
    var_47 = wp::mod(var_42, var_46);
    // if x*y==2:good=False                                                                   <L 21>
    var_48 = wp::mul(var_45, var_47);
    var_50 = (var_48 == var_49);
    if (var_50) {
    }
    var_52 = wp::where(var_50, var_51, var_38);
    // a=a//3;b=b//3                                                                          <L 22>
    var_54 = wp::floordiv(var_40, var_53);
    var_56 = wp::floordiv(var_42, var_55);
    // return good                                                                            <L 23>
    return var_52;
}


// /home/omen/Documents/Codex/experiments/tomato_persistent_mpm_20261110_v01/src/kernels.py:3
static CUDA_CALLABLE wp::mat_t<3, 3, wp::float32> stress_0(
    wp::mat_t<3, 3, wp::float32> var_F,
    wp::float32 var_mu,
    wp::float32 var_lam)
{
    //---------
    // primal vars
    wp::float32 var_0;
    wp::mat_t<3, 3, wp::float32> var_1;
    wp::float32 var_2;
    wp::float32 var_3;
    wp::float32 var_4;
    wp::mat_t<3, 3, wp::float32> var_5;
    wp::mat_t<3, 3, wp::float32> var_6;
    wp::mat_t<3, 3, wp::float32> var_7;
    wp::mat_t<3, 3, wp::float32> var_8;
    //---------
    // forward
    // def stress(F:wp.mat33,mu:float,lam:float):                                             <L 4>
    // J=wp.determinant(F)                                                                    <L 5>
    var_0 = wp::determinant(var_F);
    // return mu*F+(lam*wp.log(J)-mu)*wp.transpose(wp.inverse(F))                             <L 6>
    var_1 = wp::mul(var_mu, var_F);
    var_2 = wp::log(var_0);
    var_3 = wp::mul(var_lam, var_2);
    var_4 = wp::sub(var_3, var_mu);
    var_5 = wp::inverse(var_F);
    var_6 = wp::transpose(var_5);
    var_7 = wp::mul(var_4, var_6);
    var_8 = wp::add(var_1, var_7);
    return var_8;
}


// /home/omen/Documents/Codex/experiments/tomato_persistent_mpm_20261110_v01/src/kernels.py:16
static CUDA_CALLABLE void adj_compatible_0(
    wp::int32 var_a,
    wp::int32 var_b,
    wp::int32 & adj_a,
    wp::int32 & adj_b,
    bool & adj_ret)
{
	// reverse mode disabled (module option "enable_backward" is False or no dependent kernel found with "enable_backward")
}


// /home/omen/Documents/Codex/experiments/tomato_persistent_mpm_20261110_v01/src/kernels.py:3
static CUDA_CALLABLE void adj_stress_0(
    wp::mat_t<3, 3, wp::float32> var_F,
    wp::float32 var_mu,
    wp::float32 var_lam,
    wp::mat_t<3, 3, wp::float32> & adj_F,
    wp::float32 & adj_mu,
    wp::float32 & adj_lam,
    wp::mat_t<3, 3, wp::float32> & adj_ret)
{
	// reverse mode disabled (module option "enable_backward" is False or no dependent kernel found with "enable_backward")
}



extern "C" __global__ void remap_couple_039a69b2_cuda_kernel_forward(
    wp::launch_bounds_t<2> dim,
    wp::array_t<wp::float32> var_m,
    wp::array_t<wp::vec_t<3, wp::float32>> var_r,
    wp::array_t<wp::int32> var_active,
    wp::int32 var_count,
    wp::array_t<wp::vec_t<3, wp::float32>> var_vr)
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
        wp::float32* var_2;
        wp::float32 var_3;
        wp::float32 var_4;
        wp::vec_t<3, wp::float32>* var_5;
        wp::vec_t<3, wp::float32> var_6;
        wp::vec_t<3, wp::float32> var_7;
        const wp::float32 var_8 = 0.0;
        wp::float32 var_9;
        wp::range_t var_10;
        wp::int32 var_11;
        wp::float32* var_12;
        wp::float32 var_13;
        wp::float32 var_14;
        const wp::float32 var_15 = 0.0;
        wp::vec_t<3, wp::float32> var_16;
        const wp::float32 var_17 = 0.0;
        bool var_18;
        const wp::float32 var_19 = 0.0;
        wp::vec_t<3, wp::float32> var_20;
        wp::range_t var_21;
        wp::int32 var_22;
        bool var_23;
        bool var_24;
        wp::int32* var_25;
        wp::int32* var_26;
        bool var_27;
        wp::int32 var_28;
        wp::int32 var_29;
        wp::vec_t<3, wp::float32>* var_30;
        wp::vec_t<3, wp::float32> var_31;
        wp::vec_t<3, wp::float32> var_32;
        wp::float32* var_33;
        wp::vec_t<3, wp::float32> var_34;
        wp::float32 var_35;
        wp::vec_t<3, wp::float32> var_36;
        wp::vec_t<3, wp::float32> var_37;
        wp::vec_t<3, wp::float32> var_38;
        wp::vec_t<3, wp::float32> var_39;
        wp::vec_t<3, wp::float32> var_40;
        wp::vec_t<3, wp::float32> var_41;
        wp::int32 var_42;
        //---------
        // forward
        // def remap_couple(m:wp.array2d(dtype=float),r:wp.array2d(dtype=wp.vec3),active:wp.array(dtype=int),count:int,vr:wp.array2d(dtype=wp.vec3)):       <L 65>
        // a,i=wp.tid();ma=m[a,i];ra=r[a,i];M=float(0.0)                                          <L 66>
        builtin_tid2d(var_0, var_1);
        var_2 = wp::address(var_m, var_0, var_1);
        var_4 = wp::load(var_2);
        var_3 = wp::copy(var_4);
        var_5 = wp::address(var_r, var_0, var_1);
        var_7 = wp::load(var_5);
        var_6 = wp::copy(var_7);
        var_9 = wp::float(var_8);
        // for b in range(count):M+=m[b,i]                                                        <L 67>
        var_10 = wp::range(var_count);
        start_for_0:;
            if (iter_cmp(var_10) == 0) goto end_for_0;
            var_11 = wp::iter_next(var_10);
            var_12 = wp::address(var_m, var_11, var_1);
            var_14 = wp::load(var_12);
            var_13 = wp::add(var_9, var_14);
            wp::assign(var_9, var_13);
            goto start_for_0;
        end_for_0:;
        // vr[a,i]=wp.vec3(0.0)                                                                   <L 68>
        var_16 = wp::vec_t<3, wp::float32>(var_15);
        wp::array_store(var_vr, var_0, var_1, var_16);
        // if ma>0.0:                                                                             <L 69>
        var_18 = (var_3 > var_17);
        if (var_18) {
            // dp=wp.vec3(0.0)                                                                    <L 70>
            var_20 = wp::vec_t<3, wp::float32>(var_19);
            // for b in range(count):                                                             <L 71>
            var_21 = wp::range(var_count);
            start_for_2:;
                if (iter_cmp(var_21) == 0) goto end_for_2;
                var_22 = wp::iter_next(var_21);
                // if b!=a and compatible(active[a],active[b]):dp+=ma*r[b,i]-m[b,i]*ra            <L 72>
                var_24 = (var_22 != var_0);
                var_23 = var_24;
                if (var_23) {
                    var_25 = wp::address(var_active, var_0);
                    var_26 = wp::address(var_active, var_22);
                    var_28 = wp::load(var_25);
                    var_29 = wp::load(var_26);
                    var_27 = compatible_0(var_28, var_29);
                    var_23 = var_23 && var_27;
                }
                if (var_23) {
                    var_30 = wp::address(var_r, var_22, var_1);
                    var_32 = wp::load(var_30);
                    var_31 = wp::mul(var_3, var_32);
                    var_33 = wp::address(var_m, var_22, var_1);
                    var_35 = wp::load(var_33);
                    var_34 = wp::mul(var_35, var_6);
                    var_36 = wp::sub(var_31, var_34);
                    var_37 = wp::add(var_20, var_36);
                }
                var_38 = wp::where(var_23, var_37, var_20);
                wp::assign(var_20, var_38);
                goto start_for_2;
            end_for_2:;
            // vr[a,i]=(ra+dp/M)/ma                                                               <L 73>
            var_39 = wp::div(var_20, var_9);
            var_40 = wp::add(var_6, var_39);
            var_41 = wp::div(var_40, var_3);
            wp::array_store(var_vr, var_0, var_1, var_41);
        }
        var_42 = wp::where(var_18, var_22, var_11);
    }
}



extern "C" __global__ void remap_1941ab9b_cuda_kernel_forward(
    wp::launch_bounds_t<1> dim,
    wp::array_t<wp::vec_t<3, wp::float32>> var_v,
    wp::array_t<wp::int32> var_codes,
    wp::array_t<wp::int32> var_lookup,
    wp::array_t<wp::int32> var_ids,
    wp::array_t<wp::float32> var_w,
    wp::float32 var_mass,
    wp::array_t<wp::vec_t<3, wp::float32>> var_r)
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
        const wp::int32 var_6 = 27;
        wp::range_t var_7;
        wp::int32 var_8;
        wp::int32* var_9;
        wp::float32* var_10;
        wp::float32 var_11;
        wp::float32 var_12;
        wp::vec_t<3, wp::float32>* var_13;
        wp::vec_t<3, wp::float32> var_14;
        wp::vec_t<3, wp::float32> var_15;
        wp::vec_t<3, wp::float32> var_16;
        wp::int32 var_17;
        //---------
        // forward
        // def remap(v:wp.array(dtype=wp.vec3),codes:wp.array(dtype=int),lookup:wp.array(dtype=int),ids:wp.array2d(dtype=int),w:wp.array2d(dtype=float),mass:float,r:wp.array2d(dtype=wp.vec3)):       <L 60>
        // p=wp.tid();a=lookup[codes[p]]                                                          <L 61>
        var_0 = builtin_tid1d();
        var_1 = wp::address(var_codes, var_0);
        var_3 = wp::load(var_1);
        var_2 = wp::address(var_lookup, var_3);
        var_5 = wp::load(var_2);
        var_4 = wp::copy(var_5);
        // for k in range(27):wp.atomic_add(r,a,ids[p,k],mass*w[p,k]*v[p])                        <L 62>
        var_7 = wp::range(var_6);
        start_for_0:;
            if (iter_cmp(var_7) == 0) goto end_for_0;
            var_8 = wp::iter_next(var_7);
            var_9 = wp::address(var_ids, var_0, var_8);
            var_10 = wp::address(var_w, var_0, var_8);
            var_12 = wp::load(var_10);
            var_11 = wp::mul(var_mass, var_12);
            var_13 = wp::address(var_v, var_0);
            var_15 = wp::load(var_13);
            var_14 = wp::mul(var_11, var_15);
            var_17 = wp::load(var_9);
            var_16 = wp::atomic_add(var_r, var_4, var_17, var_14);
            goto start_for_0;
        end_for_0:;
    }
}



extern "C" __global__ void assign_sweep_4d1579be_cuda_kernel_forward(
    wp::launch_bounds_t<1> dim,
    wp::array_t<wp::vec_t<3, wp::float32>> var_x,
    wp::array_t<wp::int32> var_codes,
    wp::vec_t<3, wp::float32> var_old,
    wp::vec_t<3, wp::float32> var_new,
    wp::vec_t<3, wp::float32> var_normal,
    wp::vec_t<3, wp::float32> var_edge,
    wp::float32 var_half_length,
    wp::float32 var_band,
    wp::int32 var_power)
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
        wp::vec_t<3, wp::float32> var_1;
        wp::float32 var_2;
        bool var_3;
        const wp::float32 var_4 = 0.0;
        bool var_5;
        wp::int32* var_6;
        wp::int32 var_7;
        wp::int32 var_8;
        const wp::int32 var_9 = 3;
        wp::int32 var_10;
        const wp::int32 var_11 = 0;
        bool var_12;
        wp::vec_t<3, wp::float32>* var_13;
        wp::vec_t<3, wp::float32> var_14;
        wp::vec_t<3, wp::float32> var_15;
        wp::vec_t<3, wp::float32> var_16;
        wp::float32 var_17;
        wp::float32 var_18;
        wp::float32 var_19;
        bool var_20;
        wp::float32 var_21;
        bool var_22;
        wp::float32 var_23;
        bool var_24;
        const wp::float32 var_25 = -1e-08;
        bool var_26;
        const wp::float32 var_27 = 1e-08;
        wp::float32 var_28;
        bool var_29;
        const wp::int32 var_30 = 2;
        wp::int32 var_31;
        const wp::float32 var_32 = 0.0;
        bool var_33;
        const wp::int32 var_34 = 1;
        wp::int32 var_35;
        wp::int32* var_36;
        wp::int32 var_37;
        wp::int32 var_38;
        wp::int32 var_39;
        //---------
        // forward
        // def assign_sweep(x:wp.array(dtype=wp.vec3),codes:wp.array(dtype=int),old:wp.vec3,new:wp.vec3,normal:wp.vec3,edge:wp.vec3,half_length:float,band:float,power:int):       <L 82>
        // p=wp.tid();advance=new-old;dist=wp.length(advance)                                     <L 83>
        var_0 = builtin_tid1d();
        var_1 = wp::sub(var_new, var_old);
        var_2 = wp::length(var_1);
        // if dist>0.0 and (codes[p]//power)%3==0:                                                <L 84>
        var_5 = (var_2 > var_4);
        var_3 = var_5;
        if (var_3) {
            var_6 = wp::address(var_codes, var_0);
            var_8 = wp::load(var_6);
            var_7 = wp::floordiv(var_8, var_power);
            var_10 = wp::mod(var_7, var_9);
            var_12 = (var_10 == var_11);
            var_3 = var_3 && var_12;
        }
        if (var_3) {
            // r=x[p]-old;d=advance/dist;s=wp.dot(r,normal);ell=wp.dot(r,edge);t=wp.dot(r,d)       <L 85>
            var_13 = wp::address(var_x, var_0);
            var_15 = wp::load(var_13);
            var_14 = wp::sub(var_15, var_old);
            var_16 = wp::div(var_1, var_2);
            var_17 = wp::dot(var_14, var_normal);
            var_18 = wp::dot(var_14, var_edge);
            var_19 = wp::dot(var_14, var_16);
            // if wp.abs(s)<=band and wp.abs(ell)<=half_length and t>=-1e-8 and t<=dist+1e-8:       <L 86>
            var_21 = wp::abs(var_17);
            var_22 = (var_21 <= var_band);
            var_20 = var_22;
            if (var_20) {
                var_23 = wp::abs(var_18);
                var_24 = (var_23 <= var_half_length);
                var_20 = var_20 && var_24;
            }
            if (var_20) {
                var_26 = (var_19 >= var_25);
                var_20 = var_20 && var_26;
            }
            if (var_20) {
                var_28 = wp::add(var_2, var_27);
                var_29 = (var_19 <= var_28);
                var_20 = var_20 && var_29;
            }
            if (var_20) {
                // digit=int(2)                                                                   <L 87>
                var_31 = wp::int(var_30);
                // if s<0.0:digit=1                                                               <L 88>
                var_33 = (var_17 < var_32);
                if (var_33) {
                }
                var_35 = wp::where(var_33, var_34, var_31);
                // codes[p]=codes[p]+digit*power                                                  <L 89>
                var_36 = wp::address(var_codes, var_0);
                var_37 = wp::mul(var_35, var_power);
                var_39 = wp::load(var_36);
                var_38 = wp::add(var_39, var_37);
                wp::array_store(var_codes, var_0, var_38);
            }
        }
    }
}



extern "C" __global__ void deform_6a09bfbe_cuda_kernel_forward(
    wp::launch_bounds_t<1> dim,
    wp::array_t<wp::mat_t<3, 3, wp::float32>> var_F,
    wp::array_t<wp::int32> var_codes,
    wp::array_t<wp::int32> var_lookup,
    wp::array_t<wp::int32> var_ids,
    wp::array_t<wp::vec_t<3, wp::float32>> var_g,
    wp::array_t<wp::vec_t<3, wp::float32>> var_vr,
    wp::float32 var_dt)
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
        const wp::float32 var_6 = 0.0;
        wp::mat_t<3, 3, wp::float32> var_7;
        const wp::int32 var_8 = 27;
        wp::range_t var_9;
        wp::int32 var_10;
        wp::int32* var_11;
        wp::vec_t<3, wp::float32>* var_12;
        wp::int32 var_13;
        wp::vec_t<3, wp::float32>* var_14;
        wp::mat_t<3, 3, wp::float32> var_15;
        wp::vec_t<3, wp::float32> var_16;
        wp::vec_t<3, wp::float32> var_17;
        wp::mat_t<3, 3, wp::float32> var_18;
        wp::mat_t<3, 3, wp::float32>* var_19;
        wp::mat_t<3, 3, wp::float32> var_20;
        wp::mat_t<3, 3, wp::float32> var_21;
        wp::mat_t<3, 3, wp::float32> var_22;
        //---------
        // forward
        // def deform(F:wp.array(dtype=wp.mat33),codes:wp.array(dtype=int),lookup:wp.array(dtype=int),ids:wp.array2d(dtype=int),g:wp.array2d(dtype=wp.vec3),vr:wp.array2d(dtype=wp.vec3),dt:float):       <L 76>
        // p=wp.tid();a=lookup[codes[p]];L=wp.mat33(0.0)                                          <L 77>
        var_0 = builtin_tid1d();
        var_1 = wp::address(var_codes, var_0);
        var_3 = wp::load(var_1);
        var_2 = wp::address(var_lookup, var_3);
        var_5 = wp::load(var_2);
        var_4 = wp::copy(var_5);
        var_7 = wp::mat_t<3, 3, wp::float32>(var_6);
        // for k in range(27):L+=wp.outer(vr[a,ids[p,k]],g[p,k])                                  <L 78>
        var_9 = wp::range(var_8);
        start_for_0:;
            if (iter_cmp(var_9) == 0) goto end_for_0;
            var_10 = wp::iter_next(var_9);
            var_11 = wp::address(var_ids, var_0, var_10);
            var_13 = wp::load(var_11);
            var_12 = wp::address(var_vr, var_4, var_13);
            var_14 = wp::address(var_g, var_0, var_10);
            var_16 = wp::load(var_12);
            var_17 = wp::load(var_14);
            var_15 = wp::outer(var_16, var_17);
            var_18 = wp::add(var_7, var_15);
            wp::assign(var_7, var_18);
            goto start_for_0;
        end_for_0:;
        // F[p]=F[p]+dt*L                                                                         <L 79>
        var_19 = wp::address(var_F, var_0);
        var_20 = wp::mul(var_dt, var_7);
        var_22 = wp::load(var_19);
        var_21 = wp::add(var_22, var_20);
        wp::array_store(var_F, var_0, var_21);
    }
}



extern "C" __global__ void clear_grid_7c6862c7_cuda_kernel_forward(
    wp::launch_bounds_t<2> dim,
    wp::array_t<wp::float32> var_m,
    wp::array_t<wp::vec_t<3, wp::float32>> var_p,
    wp::array_t<wp::vec_t<3, wp::float32>> var_q,
    wp::array_t<wp::vec_t<3, wp::float32>> var_r)
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
        const wp::float32 var_3 = 0.0;
        wp::vec_t<3, wp::float32> var_4;
        const wp::float32 var_5 = 0.0;
        wp::vec_t<3, wp::float32> var_6;
        const wp::float32 var_7 = 0.0;
        wp::vec_t<3, wp::float32> var_8;
        //---------
        // forward
        // def clear_grid(m:wp.array2d(dtype=float),p:wp.array2d(dtype=wp.vec3),q:wp.array2d(dtype=wp.vec3),r:wp.array2d(dtype=wp.vec3)):       <L 26>
        // a,i=wp.tid();m[a,i]=0.0;p[a,i]=wp.vec3(0.0);q[a,i]=wp.vec3(0.0);r[a,i]=wp.vec3(0.0)       <L 27>
        builtin_tid2d(var_0, var_1);
        wp::array_store(var_m, var_0, var_1, var_2);
        var_4 = wp::vec_t<3, wp::float32>(var_3);
        wp::array_store(var_p, var_0, var_1, var_4);
        var_6 = wp::vec_t<3, wp::float32>(var_5);
        wp::array_store(var_q, var_0, var_1, var_6);
        var_8 = wp::vec_t<3, wp::float32>(var_7);
        wp::array_store(var_r, var_0, var_1, var_8);
    }
}



extern "C" __global__ void grid_update_7ca8bf4b_cuda_kernel_forward(
    wp::launch_bounds_t<2> dim,
    wp::array_t<wp::float32> var_m,
    wp::array_t<wp::vec_t<3, wp::float32>> var_p,
    wp::array_t<wp::vec_t<3, wp::float32>> var_q,
    wp::array_t<wp::int32> var_active,
    wp::int32 var_count,
    wp::array_t<wp::vec_t<3, wp::float32>> var_v0,
    wp::array_t<wp::vec_t<3, wp::float32>> var_v1)
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
        wp::float32* var_2;
        wp::float32 var_3;
        wp::float32 var_4;
        wp::vec_t<3, wp::float32>* var_5;
        wp::vec_t<3, wp::float32> var_6;
        wp::vec_t<3, wp::float32> var_7;
        wp::vec_t<3, wp::float32>* var_8;
        wp::vec_t<3, wp::float32> var_9;
        wp::vec_t<3, wp::float32> var_10;
        const wp::float32 var_11 = 0.0;
        wp::float32 var_12;
        wp::range_t var_13;
        wp::int32 var_14;
        wp::float32* var_15;
        wp::float32 var_16;
        wp::float32 var_17;
        const wp::float32 var_18 = 0.0;
        wp::vec_t<3, wp::float32> var_19;
        const wp::float32 var_20 = 0.0;
        wp::vec_t<3, wp::float32> var_21;
        const wp::float32 var_22 = 0.0;
        bool var_23;
        const wp::float32 var_24 = 0.0;
        wp::vec_t<3, wp::float32> var_25;
        const wp::float32 var_26 = 0.0;
        wp::vec_t<3, wp::float32> var_27;
        wp::range_t var_28;
        wp::int32 var_29;
        bool var_30;
        bool var_31;
        wp::int32* var_32;
        wp::int32* var_33;
        bool var_34;
        wp::int32 var_35;
        wp::int32 var_36;
        wp::vec_t<3, wp::float32>* var_37;
        wp::vec_t<3, wp::float32> var_38;
        wp::vec_t<3, wp::float32> var_39;
        wp::float32* var_40;
        wp::vec_t<3, wp::float32> var_41;
        wp::float32 var_42;
        wp::vec_t<3, wp::float32> var_43;
        wp::vec_t<3, wp::float32> var_44;
        wp::vec_t<3, wp::float32>* var_45;
        wp::vec_t<3, wp::float32> var_46;
        wp::vec_t<3, wp::float32> var_47;
        wp::float32* var_48;
        wp::vec_t<3, wp::float32> var_49;
        wp::float32 var_50;
        wp::vec_t<3, wp::float32> var_51;
        wp::vec_t<3, wp::float32> var_52;
        wp::vec_t<3, wp::float32> var_53;
        wp::vec_t<3, wp::float32> var_54;
        wp::vec_t<3, wp::float32> var_55;
        wp::vec_t<3, wp::float32> var_56;
        wp::vec_t<3, wp::float32> var_57;
        wp::vec_t<3, wp::float32> var_58;
        wp::vec_t<3, wp::float32> var_59;
        wp::vec_t<3, wp::float32> var_60;
        wp::int32 var_61;
        //---------
        // forward
        // def grid_update(m:wp.array2d(dtype=float),p:wp.array2d(dtype=wp.vec3),q:wp.array2d(dtype=wp.vec3),active:wp.array(dtype=int),count:int,v0:wp.array2d(dtype=wp.vec3),v1:wp.array2d(dtype=wp.vec3)):       <L 41>
        // a,i=wp.tid();ma=m[a,i];pa=p[a,i];qa=q[a,i];M=float(0.0)                                <L 42>
        builtin_tid2d(var_0, var_1);
        var_2 = wp::address(var_m, var_0, var_1);
        var_4 = wp::load(var_2);
        var_3 = wp::copy(var_4);
        var_5 = wp::address(var_p, var_0, var_1);
        var_7 = wp::load(var_5);
        var_6 = wp::copy(var_7);
        var_8 = wp::address(var_q, var_0, var_1);
        var_10 = wp::load(var_8);
        var_9 = wp::copy(var_10);
        var_12 = wp::float(var_11);
        // for b in range(count):M+=m[b,i]                                                        <L 43>
        var_13 = wp::range(var_count);
        start_for_0:;
            if (iter_cmp(var_13) == 0) goto end_for_0;
            var_14 = wp::iter_next(var_13);
            var_15 = wp::address(var_m, var_14, var_1);
            var_17 = wp::load(var_15);
            var_16 = wp::add(var_12, var_17);
            wp::assign(var_12, var_16);
            goto start_for_0;
        end_for_0:;
        // v0[a,i]=wp.vec3(0.0);v1[a,i]=wp.vec3(0.0)                                              <L 44>
        var_19 = wp::vec_t<3, wp::float32>(var_18);
        wp::array_store(var_v0, var_0, var_1, var_19);
        var_21 = wp::vec_t<3, wp::float32>(var_20);
        wp::array_store(var_v1, var_0, var_1, var_21);
        // if ma>0.0:                                                                             <L 45>
        var_23 = (var_3 > var_22);
        if (var_23) {
            // dp=wp.vec3(0.0);dq=wp.vec3(0.0)                                                    <L 46>
            var_25 = wp::vec_t<3, wp::float32>(var_24);
            var_27 = wp::vec_t<3, wp::float32>(var_26);
            // for b in range(count):                                                             <L 47>
            var_28 = wp::range(var_count);
            start_for_2:;
                if (iter_cmp(var_28) == 0) goto end_for_2;
                var_29 = wp::iter_next(var_28);
                // if b!=a and compatible(active[a],active[b]):                                   <L 48>
                var_31 = (var_29 != var_0);
                var_30 = var_31;
                if (var_30) {
                    var_32 = wp::address(var_active, var_0);
                    var_33 = wp::address(var_active, var_29);
                    var_35 = wp::load(var_32);
                    var_36 = wp::load(var_33);
                    var_34 = compatible_0(var_35, var_36);
                    var_30 = var_30 && var_34;
                }
                if (var_30) {
                    // dp+=ma*p[b,i]-m[b,i]*pa;dq+=ma*q[b,i]-m[b,i]*qa                            <L 49>
                    var_37 = wp::address(var_p, var_29, var_1);
                    var_39 = wp::load(var_37);
                    var_38 = wp::mul(var_3, var_39);
                    var_40 = wp::address(var_m, var_29, var_1);
                    var_42 = wp::load(var_40);
                    var_41 = wp::mul(var_42, var_6);
                    var_43 = wp::sub(var_38, var_41);
                    var_44 = wp::add(var_25, var_43);
                    var_45 = wp::address(var_q, var_29, var_1);
                    var_47 = wp::load(var_45);
                    var_46 = wp::mul(var_3, var_47);
                    var_48 = wp::address(var_m, var_29, var_1);
                    var_50 = wp::load(var_48);
                    var_49 = wp::mul(var_50, var_9);
                    var_51 = wp::sub(var_46, var_49);
                    var_52 = wp::add(var_27, var_51);
                }
                var_53 = wp::where(var_30, var_44, var_25);
                var_54 = wp::where(var_30, var_52, var_27);
                wp::assign(var_25, var_53);
                wp::assign(var_27, var_54);
                goto start_for_2;
            end_for_2:;
            // v0[a,i]=pa/ma;v1[a,i]=(pa+qa+(dp+dq)/M)/ma                                         <L 50>
            var_55 = wp::div(var_6, var_3);
            wp::array_store(var_v0, var_0, var_1, var_55);
            var_56 = wp::add(var_6, var_9);
            var_57 = wp::add(var_25, var_27);
            var_58 = wp::div(var_57, var_12);
            var_59 = wp::add(var_56, var_58);
            var_60 = wp::div(var_59, var_3);
            wp::array_store(var_v1, var_0, var_1, var_60);
        }
        var_61 = wp::where(var_23, var_29, var_14);
    }
}



extern "C" __global__ void g2p_cbb0f94a_cuda_kernel_forward(
    wp::launch_bounds_t<1> dim,
    wp::array_t<wp::vec_t<3, wp::float32>> var_x,
    wp::array_t<wp::vec_t<3, wp::float32>> var_v,
    wp::array_t<wp::int32> var_codes,
    wp::array_t<wp::int32> var_lookup,
    wp::array_t<wp::int32> var_ids,
    wp::array_t<wp::float32> var_w,
    wp::array_t<wp::vec_t<3, wp::float32>> var_v0,
    wp::array_t<wp::vec_t<3, wp::float32>> var_v1,
    wp::float32 var_dt)
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
        const wp::float32 var_6 = 0.0;
        wp::vec_t<3, wp::float32> var_7;
        const wp::int32 var_8 = 27;
        wp::range_t var_9;
        wp::int32 var_10;
        wp::int32* var_11;
        wp::int32 var_12;
        wp::int32 var_13;
        wp::float32* var_14;
        wp::vec_t<3, wp::float32>* var_15;
        wp::vec_t<3, wp::float32>* var_16;
        wp::vec_t<3, wp::float32> var_17;
        wp::vec_t<3, wp::float32> var_18;
        wp::vec_t<3, wp::float32> var_19;
        wp::vec_t<3, wp::float32> var_20;
        wp::float32 var_21;
        wp::vec_t<3, wp::float32> var_22;
        wp::vec_t<3, wp::float32>* var_23;
        wp::vec_t<3, wp::float32> var_24;
        wp::vec_t<3, wp::float32> var_25;
        wp::vec_t<3, wp::float32>* var_26;
        wp::vec_t<3, wp::float32>* var_27;
        wp::vec_t<3, wp::float32> var_28;
        wp::vec_t<3, wp::float32> var_29;
        wp::vec_t<3, wp::float32> var_30;
        wp::vec_t<3, wp::float32> var_31;
        //---------
        // forward
        // def g2p(x:wp.array(dtype=wp.vec3),v:wp.array(dtype=wp.vec3),codes:wp.array(dtype=int),lookup:wp.array(dtype=int),ids:wp.array2d(dtype=int),w:wp.array2d(dtype=float),v0:wp.array2d(dtype=wp.vec3),v1:wp.array2d(dtype=wp.vec3),dt:float):       <L 53>
        // p=wp.tid();a=lookup[codes[p]];dv=wp.vec3(0.0)                                          <L 54>
        var_0 = builtin_tid1d();
        var_1 = wp::address(var_codes, var_0);
        var_3 = wp::load(var_1);
        var_2 = wp::address(var_lookup, var_3);
        var_5 = wp::load(var_2);
        var_4 = wp::copy(var_5);
        var_7 = wp::vec_t<3, wp::float32>(var_6);
        // for k in range(27):                                                                    <L 55>
        var_9 = wp::range(var_8);
        start_for_0:;
            if (iter_cmp(var_9) == 0) goto end_for_0;
            var_10 = wp::iter_next(var_9);
            // i=ids[p,k];dv+=w[p,k]*(v1[a,i]-v0[a,i])                                            <L 56>
            var_11 = wp::address(var_ids, var_0, var_10);
            var_13 = wp::load(var_11);
            var_12 = wp::copy(var_13);
            var_14 = wp::address(var_w, var_0, var_10);
            var_15 = wp::address(var_v1, var_4, var_12);
            var_16 = wp::address(var_v0, var_4, var_12);
            var_18 = wp::load(var_15);
            var_19 = wp::load(var_16);
            var_17 = wp::sub(var_18, var_19);
            var_21 = wp::load(var_14);
            var_20 = wp::mul(var_21, var_17);
            var_22 = wp::add(var_7, var_20);
            wp::assign(var_7, var_22);
            goto start_for_0;
        end_for_0:;
        // v[p]=v[p]+dv;x[p]=x[p]+dt*v[p]                                                         <L 57>
        var_23 = wp::address(var_v, var_0);
        var_25 = wp::load(var_23);
        var_24 = wp::add(var_25, var_7);
        wp::array_store(var_v, var_0, var_24);
        var_26 = wp::address(var_x, var_0);
        var_27 = wp::address(var_v, var_0);
        var_29 = wp::load(var_27);
        var_28 = wp::mul(var_dt, var_29);
        var_31 = wp::load(var_26);
        var_30 = wp::add(var_31, var_28);
        wp::array_store(var_x, var_0, var_30);
    }
}



extern "C" __global__ void constitutive_d620e7ec_cuda_kernel_forward(
    wp::launch_bounds_t<1> dim,
    wp::array_t<wp::mat_t<3, 3, wp::float32>> var_F,
    wp::float32 var_mu,
    wp::float32 var_lam,
    wp::array_t<wp::mat_t<3, 3, wp::float32>> var_P,
    wp::array_t<wp::float32> var_W)
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
        wp::mat_t<3, 3, wp::float32>* var_1;
        wp::mat_t<3, 3, wp::float32> var_2;
        wp::mat_t<3, 3, wp::float32> var_3;
        wp::float32 var_4;
        wp::mat_t<3, 3, wp::float32> var_5;
        const wp::float32 var_6 = 0.0;
        wp::float32 var_7;
        const wp::int32 var_8 = 0;
        const wp::int32 var_9 = 0;
        wp::float32 var_10;
        wp::float32 var_11;
        wp::float32 var_12;
        wp::float32 var_13;
        const wp::int32 var_14 = 1;
        wp::float32 var_15;
        wp::float32 var_16;
        wp::float32 var_17;
        wp::float32 var_18;
        const wp::int32 var_19 = 2;
        wp::float32 var_20;
        wp::float32 var_21;
        wp::float32 var_22;
        wp::float32 var_23;
        const wp::int32 var_24 = 1;
        const wp::int32 var_25 = 0;
        wp::float32 var_26;
        wp::float32 var_27;
        wp::float32 var_28;
        wp::float32 var_29;
        const wp::int32 var_30 = 1;
        wp::float32 var_31;
        wp::float32 var_32;
        wp::float32 var_33;
        wp::float32 var_34;
        const wp::int32 var_35 = 2;
        wp::float32 var_36;
        wp::float32 var_37;
        wp::float32 var_38;
        wp::float32 var_39;
        const wp::int32 var_40 = 2;
        const wp::int32 var_41 = 0;
        wp::float32 var_42;
        wp::float32 var_43;
        wp::float32 var_44;
        wp::float32 var_45;
        const wp::int32 var_46 = 1;
        wp::float32 var_47;
        wp::float32 var_48;
        wp::float32 var_49;
        wp::float32 var_50;
        const wp::int32 var_51 = 2;
        wp::float32 var_52;
        wp::float32 var_53;
        wp::float32 var_54;
        wp::float32 var_55;
        wp::float32 var_56;
        const wp::float32 var_57 = 0.5;
        wp::float32 var_58;
        const wp::float32 var_59 = 3.0;
        wp::float32 var_60;
        wp::float32 var_61;
        wp::float32 var_62;
        wp::float32 var_63;
        const wp::float32 var_64 = 0.5;
        wp::float32 var_65;
        wp::float32 var_66;
        wp::float32 var_67;
        wp::float32 var_68;
        //---------
        // forward
        // def constitutive(F:wp.array(dtype=wp.mat33),mu:float,lam:float,P:wp.array(dtype=wp.mat33),W:wp.array(dtype=float)):       <L 9>
        // p=wp.tid();f=F[p];j=wp.determinant(f);P[p]=stress(f,mu,lam)                            <L 10>
        var_0 = builtin_tid1d();
        var_1 = wp::address(var_F, var_0);
        var_3 = wp::load(var_1);
        var_2 = wp::copy(var_3);
        var_4 = wp::determinant(var_2);
        var_5 = stress_0(var_2, var_mu, var_lam);
        wp::array_store(var_P, var_0, var_5);
        // norm= float(0.0)                                                                       <L 11>
        var_7 = wp::float(var_6);
        // for a in range(3):                                                                     <L 12>
        // for b in range(3):norm+=f[a,b]*f[a,b]                                                  <L 13>
        var_10 = wp::extract(var_2, var_8, var_9);
        var_11 = wp::extract(var_2, var_8, var_9);
        var_12 = wp::mul(var_10, var_11);
        var_13 = wp::add(var_7, var_12);
        var_15 = wp::extract(var_2, var_8, var_14);
        var_16 = wp::extract(var_2, var_8, var_14);
        var_17 = wp::mul(var_15, var_16);
        var_18 = wp::add(var_13, var_17);
        var_20 = wp::extract(var_2, var_8, var_19);
        var_21 = wp::extract(var_2, var_8, var_19);
        var_22 = wp::mul(var_20, var_21);
        var_23 = wp::add(var_18, var_22);
        var_26 = wp::extract(var_2, var_24, var_25);
        var_27 = wp::extract(var_2, var_24, var_25);
        var_28 = wp::mul(var_26, var_27);
        var_29 = wp::add(var_23, var_28);
        var_31 = wp::extract(var_2, var_24, var_30);
        var_32 = wp::extract(var_2, var_24, var_30);
        var_33 = wp::mul(var_31, var_32);
        var_34 = wp::add(var_29, var_33);
        var_36 = wp::extract(var_2, var_24, var_35);
        var_37 = wp::extract(var_2, var_24, var_35);
        var_38 = wp::mul(var_36, var_37);
        var_39 = wp::add(var_34, var_38);
        var_42 = wp::extract(var_2, var_40, var_41);
        var_43 = wp::extract(var_2, var_40, var_41);
        var_44 = wp::mul(var_42, var_43);
        var_45 = wp::add(var_39, var_44);
        var_47 = wp::extract(var_2, var_40, var_46);
        var_48 = wp::extract(var_2, var_40, var_46);
        var_49 = wp::mul(var_47, var_48);
        var_50 = wp::add(var_45, var_49);
        var_52 = wp::extract(var_2, var_40, var_51);
        var_53 = wp::extract(var_2, var_40, var_51);
        var_54 = wp::mul(var_52, var_53);
        var_55 = wp::add(var_50, var_54);
        // lj=wp.log(j);W[p]=mu*.5*(norm-3.0)-mu*lj+lam*.5*lj*lj                                  <L 14>
        var_56 = wp::log(var_4);
        var_58 = wp::mul(var_mu, var_57);
        var_60 = wp::sub(var_55, var_59);
        var_61 = wp::mul(var_58, var_60);
        var_62 = wp::mul(var_mu, var_56);
        var_63 = wp::sub(var_61, var_62);
        var_65 = wp::mul(var_lam, var_64);
        var_66 = wp::mul(var_65, var_56);
        var_67 = wp::mul(var_66, var_56);
        var_68 = wp::add(var_63, var_67);
        wp::array_store(var_W, var_0, var_68);
    }
}



extern "C" __global__ void p2g_f993bbc3_cuda_kernel_forward(
    wp::launch_bounds_t<1> dim,
    wp::array_t<wp::vec_t<3, wp::float32>> var_v,
    wp::array_t<wp::mat_t<3, 3, wp::float32>> var_F,
    wp::array_t<wp::int32> var_codes,
    wp::array_t<wp::int32> var_lookup,
    wp::array_t<wp::int32> var_ids,
    wp::array_t<wp::float32> var_w,
    wp::array_t<wp::vec_t<3, wp::float32>> var_g,
    wp::float32 var_mass,
    wp::float32 var_vol,
    wp::float32 var_mu,
    wp::float32 var_lam,
    wp::float32 var_dt,
    wp::array_t<wp::float32> var_m,
    wp::array_t<wp::vec_t<3, wp::float32>> var_p,
    wp::array_t<wp::vec_t<3, wp::float32>> var_q,
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
        wp::mat_t<3, 3, wp::float32>* var_6;
        wp::float32 var_7;
        wp::mat_t<3, 3, wp::float32> var_8;
        bool var_9;
        const wp::float32 var_10 = 0.1;
        bool var_11;
        const wp::float32 var_12 = 10.0;
        bool var_13;
        bool var_14;
        bool var_15;
        const wp::int32 var_16 = 0;
        const wp::int32 var_17 = 1;
        wp::int32 var_18;
        wp::mat_t<3, 3, wp::float32>* var_19;
        wp::mat_t<3, 3, wp::float32> var_20;
        wp::mat_t<3, 3, wp::float32> var_21;
        const wp::int32 var_22 = 27;
        wp::range_t var_23;
        wp::int32 var_24;
        wp::int32* var_25;
        wp::int32 var_26;
        wp::int32 var_27;
        wp::float32* var_28;
        wp::float32 var_29;
        wp::float32 var_30;
        wp::float32 var_31;
        wp::vec_t<3, wp::float32>* var_32;
        wp::vec_t<3, wp::float32> var_33;
        wp::vec_t<3, wp::float32> var_34;
        wp::vec_t<3, wp::float32> var_35;
        wp::float32 var_36;
        wp::float32 var_37;
        wp::vec_t<3, wp::float32>* var_38;
        wp::vec_t<3, wp::float32> var_39;
        wp::vec_t<3, wp::float32> var_40;
        wp::vec_t<3, wp::float32> var_41;
        wp::vec_t<3, wp::float32> var_42;
        //---------
        // forward
        // def p2g(v:wp.array(dtype=wp.vec3),F:wp.array(dtype=wp.mat33),codes:wp.array(dtype=int),lookup:wp.array(dtype=int),ids:wp.array2d(dtype=int),w:wp.array2d(dtype=float),g:wp.array2d(dtype=wp.vec3),mass:float,vol:float,mu:float,lam:float,dt:float,m:wp.array2d(dtype=float),p:wp.array2d(dtype=wp.vec3),q:wp.array2d(dtype=wp.vec3),bad:wp.array(dtype=int)):       <L 30>
        // k=wp.tid();a=lookup[codes[k]];j=wp.determinant(F[k])                                   <L 31>
        var_0 = builtin_tid1d();
        var_1 = wp::address(var_codes, var_0);
        var_3 = wp::load(var_1);
        var_2 = wp::address(var_lookup, var_3);
        var_5 = wp::load(var_2);
        var_4 = wp::copy(var_5);
        var_6 = wp::address(var_F, var_0);
        var_8 = wp::load(var_6);
        var_7 = wp::determinant(var_8);
        // if j<0.1 or j>10.0 or not wp.isfinite(j):                                              <L 32>
        var_11 = (var_7 < var_10);
        var_9 = var_11;
        if (!var_9) {
            var_13 = (var_7 > var_12);
            var_9 = var_9 || var_13;
        }
        if (!var_9) {
            var_14 = wp::isfinite(var_7);
            var_15 = wp::unot(var_14);
            var_9 = var_9 || var_15;
        }
        if (var_9) {
            // wp.atomic_add(bad,0,1)                                                             <L 33>
            var_18 = wp::atomic_add(var_bad, var_16, var_17);
        }
        if (!var_9) {
            // P=stress(F[k],mu,lam)                                                              <L 35>
            var_19 = wp::address(var_F, var_0);
            var_21 = wp::load(var_19);
            var_20 = stress_0(var_21, var_mu, var_lam);
            // for s in range(27):                                                                <L 36>
            var_23 = wp::range(var_22);
            start_for_0:;
                if (iter_cmp(var_23) == 0) goto end_for_0;
                var_24 = wp::iter_next(var_23);
                // i=ids[k,s];wm=mass*w[k,s]                                                      <L 37>
                var_25 = wp::address(var_ids, var_0, var_24);
                var_27 = wp::load(var_25);
                var_26 = wp::copy(var_27);
                var_28 = wp::address(var_w, var_0, var_24);
                var_30 = wp::load(var_28);
                var_29 = wp::mul(var_mass, var_30);
                // wp.atomic_add(m,a,i,wm);wp.atomic_add(p,a,i,wm*v[k]);wp.atomic_add(q,a,i,-dt*vol*(P*g[k,s]))       <L 38>
                var_31 = wp::atomic_add(var_m, var_4, var_26, var_29);
                var_32 = wp::address(var_v, var_0);
                var_34 = wp::load(var_32);
                var_33 = wp::mul(var_29, var_34);
                var_35 = wp::atomic_add(var_p, var_4, var_26, var_33);
                var_36 = wp::neg(var_dt);
                var_37 = wp::mul(var_36, var_vol);
                var_38 = wp::address(var_g, var_0, var_24);
                var_40 = wp::load(var_38);
                var_39 = wp::mul(var_20, var_40);
                var_41 = wp::mul(var_37, var_39);
                var_42 = wp::atomic_add(var_q, var_4, var_26, var_41);
                goto start_for_0;
            end_for_0:;
        }
    }
}


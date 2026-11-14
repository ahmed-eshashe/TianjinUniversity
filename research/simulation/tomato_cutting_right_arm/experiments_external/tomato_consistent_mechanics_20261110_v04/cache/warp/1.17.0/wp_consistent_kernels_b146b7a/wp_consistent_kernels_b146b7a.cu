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



extern "C" __global__ void reconstruct_106743c3_cuda_kernel_forward(
    wp::launch_bounds_t<1> dim,
    wp::array_t<wp::vec_t<3, wp::float64>> var_q,
    wp::array_t<wp::vec_t<3, wp::float64>> var_vg,
    wp::array_t<wp::int32> var_ids,
    wp::array_t<wp::float64> var_w,
    wp::array_t<wp::vec_t<3, wp::float64>> var_g,
    wp::array_t<wp::vec_t<3, wp::float64>> var_x,
    wp::array_t<wp::vec_t<3, wp::float64>> var_v,
    wp::array_t<wp::mat_t<3, 3, wp::float64>> var_F)
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
        wp::float64 var_1;
        wp::vec_t<3, wp::float64> var_2;
        wp::float64 var_3;
        wp::vec_t<3, wp::float64> var_4;
        wp::float64 var_5;
        wp::mat_t<3, 3, wp::float64> var_6;
        const wp::int32 var_7 = 27;
        wp::range_t var_8;
        wp::int32 var_9;
        wp::int32* var_10;
        wp::int32 var_11;
        wp::int32 var_12;
        wp::float64* var_13;
        wp::vec_t<3, wp::float64>* var_14;
        wp::vec_t<3, wp::float64> var_15;
        wp::float64 var_16;
        wp::vec_t<3, wp::float64> var_17;
        wp::vec_t<3, wp::float64> var_18;
        wp::float64* var_19;
        wp::vec_t<3, wp::float64>* var_20;
        wp::vec_t<3, wp::float64> var_21;
        wp::float64 var_22;
        wp::vec_t<3, wp::float64> var_23;
        wp::vec_t<3, wp::float64> var_24;
        wp::vec_t<3, wp::float64>* var_25;
        wp::vec_t<3, wp::float64>* var_26;
        wp::mat_t<3, 3, wp::float64> var_27;
        wp::vec_t<3, wp::float64> var_28;
        wp::vec_t<3, wp::float64> var_29;
        wp::mat_t<3, 3, wp::float64> var_30;
        //---------
        // forward
        // def reconstruct(q:wp.array(dtype=wp.vec3d),vg:wp.array(dtype=wp.vec3d),ids:wp.array2d(dtype=int),w:wp.array2d(dtype=wp.float64),g:wp.array2d(dtype=wp.vec3d),x:wp.array(dtype=wp.vec3d),v:wp.array(dtype=wp.vec3d),F:wp.array(dtype=wp.mat33d)):       <L 28>
        // p=wp.tid();xx=wp.vec3d(wp.float64(0.0));vv=wp.vec3d(wp.float64(0.0));ff=wp.mat33d(wp.float64(0.0))       <L 29>
        var_0 = builtin_tid1d();
        var_1 = 0.0;
        var_2 = wp::vec_t<3, wp::float64>(var_1);
        var_3 = 0.0;
        var_4 = wp::vec_t<3, wp::float64>(var_3);
        var_5 = 0.0;
        var_6 = wp::mat_t<3, 3, wp::float64>(var_5);
        // for s in range(27):                                                                    <L 30>
        var_8 = wp::range(var_7);
        start_for_0:;
            if (iter_cmp(var_8) == 0) goto end_for_0;
            var_9 = wp::iter_next(var_8);
            // i=ids[p,s];xx+=w[p,s]*q[i];vv+=w[p,s]*vg[i];ff+=wp.outer(q[i],g[p,s])              <L 31>
            var_10 = wp::address(var_ids, var_0, var_9);
            var_12 = wp::load(var_10);
            var_11 = wp::copy(var_12);
            var_13 = wp::address(var_w, var_0, var_9);
            var_14 = wp::address(var_q, var_11);
            var_16 = wp::load(var_13);
            var_17 = wp::load(var_14);
            var_15 = wp::mul(var_16, var_17);
            var_18 = wp::add(var_2, var_15);
            var_19 = wp::address(var_w, var_0, var_9);
            var_20 = wp::address(var_vg, var_11);
            var_22 = wp::load(var_19);
            var_23 = wp::load(var_20);
            var_21 = wp::mul(var_22, var_23);
            var_24 = wp::add(var_4, var_21);
            var_25 = wp::address(var_q, var_11);
            var_26 = wp::address(var_g, var_0, var_9);
            var_28 = wp::load(var_25);
            var_29 = wp::load(var_26);
            var_27 = wp::outer(var_28, var_29);
            var_30 = wp::add(var_6, var_27);
            wp::assign(var_2, var_18);
            wp::assign(var_4, var_24);
            wp::assign(var_6, var_30);
            goto start_for_0;
        end_for_0:;
        // x[p]=xx;v[p]=vv;F[p]=ff                                                                <L 32>
        wp::array_store(var_x, var_0, var_2);
        wp::array_store(var_v, var_0, var_4);
        wp::array_store(var_F, var_0, var_6);
    }
}



extern "C" __global__ void internal_14ba5b4d_cuda_kernel_forward(
    wp::launch_bounds_t<1> dim,
    wp::array_t<wp::vec_t<3, wp::float64>> var_q,
    wp::array_t<wp::int32> var_ids,
    wp::array_t<wp::float64> var_w,
    wp::array_t<wp::vec_t<3, wp::float64>> var_g,
    wp::array_t<wp::vec_t<3, wp::float64>> var_external,
    wp::float64 var_vol,
    wp::float64 var_mu,
    wp::float64 var_lam,
    wp::array_t<wp::vec_t<3, wp::float64>> var_force,
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
        wp::float64 var_1;
        wp::mat_t<3, 3, wp::float64> var_2;
        const wp::int32 var_3 = 27;
        wp::range_t var_4;
        wp::int32 var_5;
        wp::int32* var_6;
        wp::vec_t<3, wp::float64>* var_7;
        wp::int32 var_8;
        wp::vec_t<3, wp::float64>* var_9;
        wp::mat_t<3, 3, wp::float64> var_10;
        wp::vec_t<3, wp::float64> var_11;
        wp::vec_t<3, wp::float64> var_12;
        wp::mat_t<3, 3, wp::float64> var_13;
        wp::float64 var_14;
        bool var_15;
        wp::float64 var_16;
        bool var_17;
        wp::float64 var_18;
        bool var_19;
        bool var_20;
        bool var_21;
        const wp::int32 var_22 = 0;
        const wp::int32 var_23 = 1;
        wp::int32 var_24;
        wp::mat_t<3, 3, wp::float64> var_25;
        wp::float64 var_26;
        wp::float64 var_27;
        wp::float64 var_28;
        wp::mat_t<3, 3, wp::float64> var_29;
        wp::mat_t<3, 3, wp::float64> var_30;
        wp::mat_t<3, 3, wp::float64> var_31;
        wp::mat_t<3, 3, wp::float64> var_32;
        const wp::int32 var_33 = 27;
        wp::range_t var_34;
        wp::int32 var_35;
        wp::int32* var_36;
        wp::float64 var_37;
        wp::vec_t<3, wp::float64>* var_38;
        wp::vec_t<3, wp::float64> var_39;
        wp::vec_t<3, wp::float64> var_40;
        wp::vec_t<3, wp::float64> var_41;
        wp::float64* var_42;
        wp::vec_t<3, wp::float64>* var_43;
        wp::vec_t<3, wp::float64> var_44;
        wp::float64 var_45;
        wp::vec_t<3, wp::float64> var_46;
        wp::vec_t<3, wp::float64> var_47;
        wp::vec_t<3, wp::float64> var_48;
        wp::int32 var_49;
        wp::int32 var_50;
        //---------
        // forward
        // def internal(q:wp.array(dtype=wp.vec3d),ids:wp.array2d(dtype=int),w:wp.array2d(dtype=wp.float64),g:wp.array2d(dtype=wp.vec3d),external:wp.array(dtype=wp.vec3d),vol:wp.float64,mu:wp.float64,lam:wp.float64,force:wp.array(dtype=wp.vec3d),bad:wp.array(dtype=int)):       <L 3>
        // p=wp.tid();F=wp.mat33d(wp.float64(0.0))                                                <L 4>
        var_0 = builtin_tid1d();
        var_1 = 0.0;
        var_2 = wp::mat_t<3, 3, wp::float64>(var_1);
        // for s in range(27):F+=wp.outer(q[ids[p,s]],g[p,s])                                     <L 5>
        var_4 = wp::range(var_3);
        start_for_0:;
            if (iter_cmp(var_4) == 0) goto end_for_0;
            var_5 = wp::iter_next(var_4);
            var_6 = wp::address(var_ids, var_0, var_5);
            var_8 = wp::load(var_6);
            var_7 = wp::address(var_q, var_8);
            var_9 = wp::address(var_g, var_0, var_5);
            var_11 = wp::load(var_7);
            var_12 = wp::load(var_9);
            var_10 = wp::outer(var_11, var_12);
            var_13 = wp::add(var_2, var_10);
            wp::assign(var_2, var_13);
            goto start_for_0;
        end_for_0:;
        // J=wp.determinant(F)                                                                    <L 6>
        var_14 = wp::determinant(var_2);
        // if J<=wp.float64(.1) or J>=wp.float64(10.0) or not wp.isfinite(J):wp.atomic_add(bad,0,1)       <L 7>
        var_16 = 0.1;
        var_17 = (var_14 <= var_16);
        var_15 = var_17;
        if (!var_15) {
            var_18 = 10.0;
            var_19 = (var_14 >= var_18);
            var_15 = var_15 || var_19;
        }
        if (!var_15) {
            var_20 = wp::isfinite(var_14);
            var_21 = wp::unot(var_20);
            var_15 = var_15 || var_21;
        }
        if (var_15) {
            var_24 = wp::atomic_add(var_bad, var_22, var_23);
        }
        if (!var_15) {
            // P=mu*F+(lam*wp.log(J)-mu)*wp.transpose(wp.inverse(F))                              <L 9>
            var_25 = wp::mul(var_mu, var_2);
            var_26 = wp::log(var_14);
            var_27 = wp::mul(var_lam, var_26);
            var_28 = wp::sub(var_27, var_mu);
            var_29 = wp::inverse(var_2);
            var_30 = wp::transpose(var_29);
            var_31 = wp::mul(var_28, var_30);
            var_32 = wp::add(var_25, var_31);
            // for s in range(27):wp.atomic_add(force,ids[p,s],-vol*(P*g[p,s])+w[p,s]*external[p])       <L 10>
            var_34 = wp::range(var_33);
            start_for_2:;
                if (iter_cmp(var_34) == 0) goto end_for_2;
                var_35 = wp::iter_next(var_34);
                var_36 = wp::address(var_ids, var_0, var_35);
                var_37 = wp::neg(var_vol);
                var_38 = wp::address(var_g, var_0, var_35);
                var_40 = wp::load(var_38);
                var_39 = wp::mul(var_32, var_40);
                var_41 = wp::mul(var_37, var_39);
                var_42 = wp::address(var_w, var_0, var_35);
                var_43 = wp::address(var_external, var_0);
                var_45 = wp::load(var_42);
                var_46 = wp::load(var_43);
                var_44 = wp::mul(var_45, var_46);
                var_47 = wp::add(var_41, var_44);
                var_49 = wp::load(var_36);
                var_48 = wp::atomic_add(var_force, var_49, var_47);
                goto start_for_2;
            end_for_2:;
        }
        var_50 = wp::where(var_15, var_5, var_35);
    }
}



extern "C" __global__ void solve_axis_4debe580_cuda_kernel_forward(
    wp::launch_bounds_t<1> dim,
    wp::array_t<wp::vec_t<3, wp::float64>> var_src,
    wp::array_t<wp::vec_t<3, wp::float64>> var_dest,
    wp::array_t<wp::float64> var_inverse,
    wp::vec_t<3, wp::int32> var_dims,
    wp::int32 var_axis,
    wp::float64 var_scale)
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
        wp::vec_t<3, wp::float64> var_17;
        const wp::int32 var_18 = 0;
        bool var_19;
        const wp::int32 var_20 = 0;
        wp::int32 var_21;
        wp::range_t var_22;
        wp::int32 var_23;
        wp::float64* var_24;
        const wp::int32 var_25 = 1;
        wp::int32 var_26;
        wp::int32 var_27;
        wp::int32 var_28;
        const wp::int32 var_29 = 2;
        wp::int32 var_30;
        wp::int32 var_31;
        wp::int32 var_32;
        wp::vec_t<3, wp::float64>* var_33;
        wp::vec_t<3, wp::float64> var_34;
        wp::float64 var_35;
        wp::vec_t<3, wp::float64> var_36;
        wp::vec_t<3, wp::float64> var_37;
        const wp::int32 var_38 = 1;
        bool var_39;
        const wp::int32 var_40 = 1;
        wp::int32 var_41;
        wp::range_t var_42;
        wp::int32 var_43;
        wp::float64* var_44;
        const wp::int32 var_45 = 1;
        wp::int32 var_46;
        wp::int32 var_47;
        wp::int32 var_48;
        const wp::int32 var_49 = 2;
        wp::int32 var_50;
        wp::int32 var_51;
        wp::int32 var_52;
        wp::vec_t<3, wp::float64>* var_53;
        wp::vec_t<3, wp::float64> var_54;
        wp::float64 var_55;
        wp::vec_t<3, wp::float64> var_56;
        wp::vec_t<3, wp::float64> var_57;
        const wp::int32 var_58 = 2;
        wp::int32 var_59;
        wp::range_t var_60;
        wp::int32 var_61;
        wp::float64* var_62;
        const wp::int32 var_63 = 1;
        wp::int32 var_64;
        wp::int32 var_65;
        wp::int32 var_66;
        const wp::int32 var_67 = 2;
        wp::int32 var_68;
        wp::int32 var_69;
        wp::int32 var_70;
        wp::vec_t<3, wp::float64>* var_71;
        wp::vec_t<3, wp::float64> var_72;
        wp::float64 var_73;
        wp::vec_t<3, wp::float64> var_74;
        wp::vec_t<3, wp::float64> var_75;
        wp::int32 var_76;
        wp::int32 var_77;
        wp::vec_t<3, wp::float64> var_78;
        //---------
        // forward
        // def solve_axis(src:wp.array(dtype=wp.vec3d),dest:wp.array(dtype=wp.vec3d),inverse:wp.array2d(dtype=wp.float64),dims:wp.vec3i,axis:int,scale:wp.float64):       <L 12>
        // n=wp.tid();i=n//(dims[1]*dims[2]);j=(n//dims[2])%dims[1];k=n%dims[2];out=wp.vec3d(wp.float64(0.0))       <L 13>
        var_0 = builtin_tid1d();
        var_2 = wp::extract(var_dims, var_1);
        var_4 = wp::extract(var_dims, var_3);
        var_5 = wp::mul(var_2, var_4);
        var_6 = wp::floordiv(var_0, var_5);
        var_8 = wp::extract(var_dims, var_7);
        var_9 = wp::floordiv(var_0, var_8);
        var_11 = wp::extract(var_dims, var_10);
        var_12 = wp::mod(var_9, var_11);
        var_14 = wp::extract(var_dims, var_13);
        var_15 = wp::mod(var_0, var_14);
        var_16 = 0.0;
        var_17 = wp::vec_t<3, wp::float64>(var_16);
        // if axis==0:                                                                            <L 14>
        var_19 = (var_axis == var_18);
        if (var_19) {
            // for z in range(dims[0]):out+=inverse[i,z]*src[(z*dims[1]+j)*dims[2]+k]             <L 15>
            var_21 = wp::extract(var_dims, var_20);
            var_22 = wp::range(var_21);
            start_for_0:;
                if (iter_cmp(var_22) == 0) goto end_for_0;
                var_23 = wp::iter_next(var_22);
                var_24 = wp::address(var_inverse, var_6, var_23);
                var_26 = wp::extract(var_dims, var_25);
                var_27 = wp::mul(var_23, var_26);
                var_28 = wp::add(var_27, var_12);
                var_30 = wp::extract(var_dims, var_29);
                var_31 = wp::mul(var_28, var_30);
                var_32 = wp::add(var_31, var_15);
                var_33 = wp::address(var_src, var_32);
                var_35 = wp::load(var_24);
                var_36 = wp::load(var_33);
                var_34 = wp::mul(var_35, var_36);
                var_37 = wp::add(var_17, var_34);
                wp::assign(var_17, var_37);
                goto start_for_0;
            end_for_0:;
        }
        if (!var_19) {
            // elif axis==1:                                                                      <L 16>
            var_39 = (var_axis == var_38);
            if (var_39) {
                // for z in range(dims[1]):out+=inverse[j,z]*src[(i*dims[1]+z)*dims[2]+k]         <L 17>
                var_41 = wp::extract(var_dims, var_40);
                var_42 = wp::range(var_41);
                start_for_2:;
                    if (iter_cmp(var_42) == 0) goto end_for_2;
                    var_43 = wp::iter_next(var_42);
                    var_44 = wp::address(var_inverse, var_12, var_43);
                    var_46 = wp::extract(var_dims, var_45);
                    var_47 = wp::mul(var_6, var_46);
                    var_48 = wp::add(var_47, var_43);
                    var_50 = wp::extract(var_dims, var_49);
                    var_51 = wp::mul(var_48, var_50);
                    var_52 = wp::add(var_51, var_15);
                    var_53 = wp::address(var_src, var_52);
                    var_55 = wp::load(var_44);
                    var_56 = wp::load(var_53);
                    var_54 = wp::mul(var_55, var_56);
                    var_57 = wp::add(var_17, var_54);
                    wp::assign(var_17, var_57);
                    goto start_for_2;
                end_for_2:;
            }
            if (!var_39) {
                // for z in range(dims[2]):out+=inverse[k,z]*src[(i*dims[1]+j)*dims[2]+z]         <L 19>
                var_59 = wp::extract(var_dims, var_58);
                var_60 = wp::range(var_59);
                start_for_4:;
                    if (iter_cmp(var_60) == 0) goto end_for_4;
                    var_61 = wp::iter_next(var_60);
                    var_62 = wp::address(var_inverse, var_15, var_61);
                    var_64 = wp::extract(var_dims, var_63);
                    var_65 = wp::mul(var_6, var_64);
                    var_66 = wp::add(var_65, var_12);
                    var_68 = wp::extract(var_dims, var_67);
                    var_69 = wp::mul(var_66, var_68);
                    var_70 = wp::add(var_69, var_61);
                    var_71 = wp::address(var_src, var_70);
                    var_73 = wp::load(var_62);
                    var_74 = wp::load(var_71);
                    var_72 = wp::mul(var_73, var_74);
                    var_75 = wp::add(var_17, var_72);
                    wp::assign(var_17, var_75);
                    goto start_for_4;
                end_for_4:;
            }
            var_76 = wp::where(var_39, var_43, var_61);
        }
        var_77 = wp::where(var_19, var_23, var_76);
        // dest[n]=scale*out                                                                      <L 20>
        var_78 = wp::mul(var_scale, var_17);
        wp::array_store(var_dest, var_0, var_78);
    }
}



extern "C" __global__ void drift_57c9e63c_cuda_kernel_forward(
    wp::launch_bounds_t<1> dim,
    wp::array_t<wp::vec_t<3, wp::float64>> var_q,
    wp::array_t<wp::vec_t<3, wp::float64>> var_vg,
    wp::array_t<wp::vec_t<3, wp::float64>> var_a,
    wp::float64 var_dt)
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
        wp::float64 var_2;
        wp::float64 var_3;
        wp::vec_t<3, wp::float64>* var_4;
        wp::vec_t<3, wp::float64> var_5;
        wp::vec_t<3, wp::float64> var_6;
        wp::vec_t<3, wp::float64> var_7;
        wp::vec_t<3, wp::float64> var_8;
        wp::vec_t<3, wp::float64> var_9;
        wp::vec_t<3, wp::float64> var_10;
        //---------
        // forward
        // def drift(q:wp.array(dtype=wp.vec3d),vg:wp.array(dtype=wp.vec3d),a:wp.array(dtype=wp.vec3d),dt:wp.float64):       <L 22>
        // i=wp.tid();vh=vg[i]+wp.float64(.5)*dt*a[i];q[i]+=dt*vh;vg[i]=vh                        <L 23>
        var_0 = builtin_tid1d();
        var_1 = wp::address(var_vg, var_0);
        var_2 = 0.5;
        var_3 = wp::mul(var_2, var_dt);
        var_4 = wp::address(var_a, var_0);
        var_6 = wp::load(var_4);
        var_5 = wp::mul(var_3, var_6);
        var_8 = wp::load(var_1);
        var_7 = wp::add(var_8, var_5);
        var_9 = wp::mul(var_dt, var_7);
        var_10 = wp::atomic_add(var_q, var_0, var_9);
        wp::array_store(var_vg, var_0, var_7);
    }
}



extern "C" __global__ void kick_7d09d196_cuda_kernel_forward(
    wp::launch_bounds_t<1> dim,
    wp::array_t<wp::vec_t<3, wp::float64>> var_vg,
    wp::array_t<wp::vec_t<3, wp::float64>> var_a,
    wp::float64 var_dt)
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
        wp::float64 var_1;
        wp::float64 var_2;
        wp::vec_t<3, wp::float64>* var_3;
        wp::vec_t<3, wp::float64> var_4;
        wp::vec_t<3, wp::float64> var_5;
        wp::vec_t<3, wp::float64> var_6;
        //---------
        // forward
        // def kick(vg:wp.array(dtype=wp.vec3d),a:wp.array(dtype=wp.vec3d),dt:wp.float64):        <L 25>
        // i=wp.tid();vg[i]+=wp.float64(.5)*dt*a[i]                                               <L 26>
        var_0 = builtin_tid1d();
        var_1 = 0.5;
        var_2 = wp::mul(var_1, var_dt);
        var_3 = wp::address(var_a, var_0);
        var_5 = wp::load(var_3);
        var_4 = wp::mul(var_2, var_5);
        var_6 = wp::atomic_add(var_vg, var_0, var_4);
    }
}


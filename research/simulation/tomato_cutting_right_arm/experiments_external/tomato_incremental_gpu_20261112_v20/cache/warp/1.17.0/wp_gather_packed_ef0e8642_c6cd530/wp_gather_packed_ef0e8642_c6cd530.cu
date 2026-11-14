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



extern "C" __global__ void gather_packed_b858a976_cuda_kernel_forward(
    wp::launch_bounds_t<1> dim,
    wp::array_t<wp::int32> var_ptr,
    wp::array_t<wp::int32> var_idx,
    wp::array_t<wp::vec_t<3, wp::float32>> var_grad,
    wp::array_t<wp::mat_t<3, 3, wp::float32>> var_P,
    wp::array_t<wp::vec_t<3, wp::float32>> var_external,
    wp::array_t<wp::vec_t<3, wp::float32>> var_force,
    wp::int32 var_n)
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
        const wp::int32 var_1 = 32;
        wp::int32 var_2;
        const wp::int32 var_3 = 32;
        wp::int32 var_4;
        const wp::float32 var_5 = 0.0;
        wp::vec_t<3, wp::float32> var_6;
        bool var_7;
        wp::int32* var_8;
        wp::int32 var_9;
        wp::int32 var_10;
        const wp::int32 var_11 = 1;
        wp::int32 var_12;
        wp::int32* var_13;
        const wp::int32 var_14 = 32;
        wp::range_t var_15;
        wp::int32 var_16;
        wp::int32 var_17;
        wp::int32* var_18;
        wp::mat_t<3, 3, wp::float32>* var_19;
        wp::int32 var_20;
        wp::vec_t<3, wp::float32>* var_21;
        wp::vec_t<3, wp::float32> var_22;
        wp::mat_t<3, 3, wp::float32> var_23;
        wp::vec_t<3, wp::float32> var_24;
        wp::vec_t<3, wp::float32> var_25;
        const wp::int32 var_26 = 0;
        bool var_27;
        wp::vec_t<3, wp::float32>* var_28;
        wp::vec_t<3, wp::float32> var_29;
        wp::vec_t<3, wp::float32> var_30;
        wp::vec_t<3, wp::float32> var_31;
        wp::vec_t<3, wp::float32> var_32;
        const bool var_33 = true;
        wp::tile_shared_t<wp::vec_t<3, wp::float32>,wp::tile_layout_strided_t<wp::tile_shape_t<128>, wp::tile_stride_t<1>>, true> var_34 = wp::tile_alloc_empty<wp::vec_t<3, wp::float32>,wp::tile_shape_t<128>,wp::tile_stride_t<1>,false>();
        const wp::int32 var_35 = 4;
        const wp::int32 var_36 = 32;
        wp::tuple_t<wp::int32, wp::int32> var_37;
        wp::tile_shared_t<wp::vec_t<3, wp::float32>,wp::tile_layout_strided_t<wp::tile_shape_t<4,32>, wp::tile_stride_t<32,1>>, false> var_38 = nullptr;
        const wp::int32 var_39 = 1;
        wp::tile_register_t<wp::vec_t<3, wp::float32>,wp::tile_layout_register_t<wp::tile_shape_t<4>>> var_40 = wp::tile_register_t<wp::vec_t<3, wp::float32>,wp::tile_layout_register_t<wp::tile_shape_t<4>>>{};
        const wp::int32 var_41 = 128;
        wp::int32 var_42;
        const wp::int32 var_43 = 4;
        wp::int32 var_44;
        //---------
        // forward
        // def gather_packed(ptr:wp.array(dtype=int),idx:wp.array(dtype=int),grad:wp.array(dtype=wp.vec3),P:wp.array(dtype=wp.mat33),external:wp.array(dtype=wp.vec3),force:wp.array(dtype=wp.vec3),n:int):       <L 31>
        // t=wp.tid()                                                                             <L 32>
        var_0 = builtin_tid1d();
        // i=t//32                                                                                <L 33>
        var_2 = wp::floordiv(var_0, var_1);
        // lane=t%32                                                                              <L 34>
        var_4 = wp::mod(var_0, var_3);
        // f=wp.vec3(0.0)                                                                         <L 35>
        var_6 = wp::vec_t<3, wp::float32>(var_5);
        // if i<n:                                                                                <L 36>
        var_7 = (var_2 < var_n);
        if (var_7) {
            // for e in range(ptr[i]+lane,ptr[i+1],32):f-=P[idx[e]]*grad[e]                       <L 37>
            var_8 = wp::address(var_ptr, var_2);
            var_10 = wp::load(var_8);
            var_9 = wp::add(var_10, var_4);
            var_12 = wp::add(var_2, var_11);
            var_13 = wp::address(var_ptr, var_12);
            var_16 = wp::load(var_13);
            var_15 = wp::range(var_9, var_16, var_14);
            start_for_0:;
                if (iter_cmp(var_15) == 0) goto end_for_0;
                var_17 = wp::iter_next(var_15);
                var_18 = wp::address(var_idx, var_17);
                var_20 = wp::load(var_18);
                var_19 = wp::address(var_P, var_20);
                var_21 = wp::address(var_grad, var_17);
                var_23 = wp::load(var_19);
                var_24 = wp::load(var_21);
                var_22 = wp::mul(var_23, var_24);
                var_25 = wp::sub(var_6, var_22);
                wp::assign(var_6, var_25);
                goto start_for_0;
            end_for_0:;
            // if lane==0:f+=external[i]                                                          <L 38>
            var_27 = (var_4 == var_26);
            if (var_27) {
                var_28 = wp::address(var_external, var_2);
                var_30 = wp::load(var_28);
                var_29 = wp::add(var_6, var_30);
            }
            var_31 = wp::where(var_27, var_29, var_6);
        }
        var_32 = wp::where(var_7, var_31, var_6);
        // values=wp.tile_reshape(wp.tile(f,preserve_type=True),(4,32))                           <L 39>
        var_34 = wp::tile<wp::vec_t<3, wp::float32>>(var_32);
        var_37 = wp::tuple(var_35, var_36);
        var_38 = wp::tile_reshape<wp::tile_shared_t<wp::vec_t<3, wp::float32>,wp::tile_layout_strided_t<wp::tile_shape_t<4,32>, wp::tile_stride_t<32,1>>, false>>(var_34);
        // total=wp.tile_sum(values,axis=1)                                                       <L 40>
        var_40 = wp::tile_sum<1>(var_38);
        // wp.tile_store(force,total,offset=(t//128)*4)                                           <L 41>
        var_42 = wp::floordiv(var_0, var_41);
        var_44 = wp::mul(var_42, var_43);
        wp::tile_store<wp::vec_t<3, wp::float32>, true, false>(var_force, var_44, var_40);
    }
}



extern "C" __global__ void gather_packed_b858a976_cuda_kernel_backward(
    wp::launch_bounds_t<1> dim,
    wp::array_t<wp::int32> var_ptr,
    wp::array_t<wp::int32> var_idx,
    wp::array_t<wp::vec_t<3, wp::float32>> var_grad,
    wp::array_t<wp::mat_t<3, 3, wp::float32>> var_P,
    wp::array_t<wp::vec_t<3, wp::float32>> var_external,
    wp::array_t<wp::vec_t<3, wp::float32>> var_force,
    wp::int32 var_n,
    wp::array_t<wp::int32> adj_ptr,
    wp::array_t<wp::int32> adj_idx,
    wp::array_t<wp::vec_t<3, wp::float32>> adj_grad,
    wp::array_t<wp::mat_t<3, 3, wp::float32>> adj_P,
    wp::array_t<wp::vec_t<3, wp::float32>> adj_external,
    wp::array_t<wp::vec_t<3, wp::float32>> adj_force,
    wp::int32 adj_n)
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
        const wp::int32 var_1 = 32;
        wp::int32 var_2;
        const wp::int32 var_3 = 32;
        wp::int32 var_4;
        const wp::float32 var_5 = 0.0;
        wp::vec_t<3, wp::float32> var_6;
        bool var_7;
        wp::int32* var_8;
        wp::int32 var_9;
        wp::int32 var_10;
        const wp::int32 var_11 = 1;
        wp::int32 var_12;
        wp::int32* var_13;
        const wp::int32 var_14 = 32;
        wp::range_t var_15;
        wp::int32 var_16;
        wp::int32 var_17;
        wp::int32* var_18;
        wp::mat_t<3, 3, wp::float32>* var_19;
        wp::int32 var_20;
        wp::vec_t<3, wp::float32>* var_21;
        wp::vec_t<3, wp::float32> var_22;
        wp::mat_t<3, 3, wp::float32> var_23;
        wp::vec_t<3, wp::float32> var_24;
        wp::vec_t<3, wp::float32> var_25;
        const wp::int32 var_26 = 0;
        bool var_27;
        wp::vec_t<3, wp::float32>* var_28;
        wp::vec_t<3, wp::float32> var_29;
        wp::vec_t<3, wp::float32> var_30;
        wp::vec_t<3, wp::float32> var_31;
        wp::vec_t<3, wp::float32> var_32;
        const bool var_33 = true;
        wp::tile_shared_t<wp::vec_t<3, wp::float32>,wp::tile_layout_strided_t<wp::tile_shape_t<128>, wp::tile_stride_t<1>>, true> var_34 = wp::tile_alloc_empty<wp::vec_t<3, wp::float32>,wp::tile_shape_t<128>,wp::tile_stride_t<1>,true>();
        const wp::int32 var_35 = 4;
        const wp::int32 var_36 = 32;
        wp::tuple_t<wp::int32, wp::int32> var_37;
        wp::tile_shared_t<wp::vec_t<3, wp::float32>,wp::tile_layout_strided_t<wp::tile_shape_t<4,32>, wp::tile_stride_t<32,1>>, false> var_38 = nullptr;
        const wp::int32 var_39 = 1;
        wp::tile_register_t<wp::vec_t<3, wp::float32>,wp::tile_layout_register_t<wp::tile_shape_t<4>>> var_40 = wp::tile_register_t<wp::vec_t<3, wp::float32>,wp::tile_layout_register_t<wp::tile_shape_t<4>>>{};
        const wp::int32 var_41 = 128;
        wp::int32 var_42;
        const wp::int32 var_43 = 4;
        wp::int32 var_44;
        //---------
        // dual vars
        wp::int32 adj_0 = {};
        wp::int32 adj_1 = {};
        wp::int32 adj_2 = {};
        wp::int32 adj_3 = {};
        wp::int32 adj_4 = {};
        wp::float32 adj_5 = {};
        wp::vec_t<3, wp::float32> adj_6 = {};
        bool adj_7 = {};
        wp::int32 adj_8 = {};
        wp::int32 adj_9 = {};
        wp::int32 adj_10 = {};
        wp::int32 adj_11 = {};
        wp::int32 adj_12 = {};
        wp::int32 adj_13 = {};
        wp::int32 adj_14 = {};
        wp::range_t adj_15 = {};
        wp::int32 adj_16 = {};
        wp::int32 adj_17 = {};
        wp::int32 adj_18 = {};
        wp::mat_t<3, 3, wp::float32> adj_19 = {};
        wp::int32 adj_20 = {};
        wp::vec_t<3, wp::float32> adj_21 = {};
        wp::vec_t<3, wp::float32> adj_22 = {};
        wp::mat_t<3, 3, wp::float32> adj_23 = {};
        wp::vec_t<3, wp::float32> adj_24 = {};
        wp::vec_t<3, wp::float32> adj_25 = {};
        wp::int32 adj_26 = {};
        bool adj_27 = {};
        wp::vec_t<3, wp::float32> adj_28 = {};
        wp::vec_t<3, wp::float32> adj_29 = {};
        wp::vec_t<3, wp::float32> adj_30 = {};
        wp::vec_t<3, wp::float32> adj_31 = {};
        wp::vec_t<3, wp::float32> adj_32 = {};
        bool adj_33 = {};
        wp::tile_shared_t<wp::vec_t<3, wp::float32>,wp::tile_layout_strided_t<wp::tile_shape_t<128>, wp::tile_stride_t<1>>, true>& adj_34 = var_34;
        wp::int32 adj_35 = {};
        wp::int32 adj_36 = {};
        wp::tuple_t<wp::int32, wp::int32> adj_37 = {};
        wp::tile_shared_t<wp::vec_t<3, wp::float32>,wp::tile_layout_strided_t<wp::tile_shape_t<4,32>, wp::tile_stride_t<32,1>>, false>& adj_38 = var_38;
        wp::int32 adj_39 = {};
        wp::tile_register_t<wp::vec_t<3, wp::float32>,wp::tile_layout_register_t<wp::tile_shape_t<4>>> adj_40{};
        wp::int32 adj_41 = {};
        wp::int32 adj_42 = {};
        wp::int32 adj_43 = {};
        wp::int32 adj_44 = {};
        //---------
        // forward
        // def gather_packed(ptr:wp.array(dtype=int),idx:wp.array(dtype=int),grad:wp.array(dtype=wp.vec3),P:wp.array(dtype=wp.mat33),external:wp.array(dtype=wp.vec3),force:wp.array(dtype=wp.vec3),n:int):       <L 31>
        // t=wp.tid()                                                                             <L 32>
        var_0 = builtin_tid1d();
        // i=t//32                                                                                <L 33>
        var_2 = wp::floordiv(var_0, var_1);
        // lane=t%32                                                                              <L 34>
        var_4 = wp::mod(var_0, var_3);
        // f=wp.vec3(0.0)                                                                         <L 35>
        var_6 = wp::vec_t<3, wp::float32>(var_5);
        // if i<n:                                                                                <L 36>
        var_7 = (var_2 < var_n);
        if (var_7) {
            // for e in range(ptr[i]+lane,ptr[i+1],32):f-=P[idx[e]]*grad[e]                       <L 37>
            var_8 = wp::address(var_ptr, var_2);
            var_10 = wp::load(var_8);
            var_9 = wp::add(var_10, var_4);
            var_12 = wp::add(var_2, var_11);
            var_13 = wp::address(var_ptr, var_12);
            var_16 = wp::load(var_13);
            var_15 = wp::range(var_9, var_16, var_14);
            // if lane==0:f+=external[i]                                                          <L 38>
            var_27 = (var_4 == var_26);
            if (var_27) {
                var_28 = wp::address(var_external, var_2);
                var_30 = wp::load(var_28);
                var_29 = wp::add(var_6, var_30);
            }
            var_31 = wp::where(var_27, var_29, var_6);
        }
        var_32 = wp::where(var_7, var_31, var_6);
        // values=wp.tile_reshape(wp.tile(f,preserve_type=True),(4,32))                           <L 39>
        var_34 = wp::tile<wp::vec_t<3, wp::float32>>(var_32);
        var_37 = wp::tuple(var_35, var_36);
        var_38 = wp::tile_reshape<wp::tile_shared_t<wp::vec_t<3, wp::float32>,wp::tile_layout_strided_t<wp::tile_shape_t<4,32>, wp::tile_stride_t<32,1>>, false>>(var_34);
        // total=wp.tile_sum(values,axis=1)                                                       <L 40>
        var_40 = wp::tile_sum<1>(var_38);
        // wp.tile_store(force,total,offset=(t//128)*4)                                           <L 41>
        var_42 = wp::floordiv(var_0, var_41);
        var_44 = wp::mul(var_42, var_43);
        // wp::tile_store<wp::vec_t<3, wp::float32>, true, false>(var_force, var_44, var_40);
        //---------
        // reverse
        wp::adj_tile_store(var_force, var_44, var_40, adj_force, adj_44, adj_40);
        wp::adj_mul(var_42, var_43, adj_42, adj_43, adj_44);
        // adj: wp.tile_store(force,total,offset=(t//128)*4)                                      <L 41>
        wp::adj_tile_sum(var_38, adj_38, adj_40);
        // adj: total=wp.tile_sum(values,axis=1)                                                  <L 40>
        wp::adj_tile_reshape(var_34, adj_34, adj_38);
        wp::adj_tile(var_32, adj_32, adj_34);
        // adj: values=wp.tile_reshape(wp.tile(f,preserve_type=True),(4,32))                      <L 39>
        wp::adj_where(var_7, var_31, var_6, adj_7, adj_31, adj_6, adj_32);
        if (var_7) {
            wp::adj_where(var_27, var_29, var_6, adj_27, adj_29, adj_6, adj_31);
            if (var_27) {
                wp::adj_add(var_6, var_30, adj_6, adj_28, adj_29);
                wp::adj_address(var_external, var_2, adj_external, adj_2, adj_28);
            }
            // adj: if lane==0:f+=external[i]                                                     <L 38>
            var_15 = wp::iter_reverse(var_15);
            start_for_0:;
                if (iter_cmp(var_15) == 0) goto end_for_0;
                var_17 = wp::iter_next(var_15);
            	adj_18 = {};
            	adj_19 = {};
            	adj_20 = {};
            	adj_21 = {};
            	adj_22 = {};
            	adj_23 = {};
            	adj_24 = {};
            	adj_25 = {};
                var_18 = wp::address(var_idx, var_17);
                var_20 = wp::load(var_18);
                var_19 = wp::address(var_P, var_20);
                var_21 = wp::address(var_grad, var_17);
                var_23 = wp::load(var_19);
                var_24 = wp::load(var_21);
                var_22 = wp::mul(var_23, var_24);
                var_25 = wp::sub(var_6, var_22);
                wp::assign(var_6, var_25);
                wp::adj_assign(var_6, var_25, adj_6, adj_25);
                wp::adj_sub(var_6, var_22, adj_6, adj_22, adj_25);
                wp::adj_mul(var_23, var_24, adj_19, adj_21, adj_22);
                wp::adj_address(var_grad, var_17, adj_grad, adj_17, adj_21);
                wp::adj_address(var_P, var_20, adj_P, adj_18, adj_19);
                wp::adj_address(var_idx, var_17, adj_idx, adj_17, adj_18);
            	goto start_for_0;
            end_for_0:;
            wp::adj_address(var_ptr, var_12, adj_ptr, adj_12, adj_13);
            wp::adj_add(var_2, var_11, adj_2, adj_11, adj_12);
            wp::adj_add(var_10, var_4, adj_8, adj_4, adj_9);
            wp::adj_address(var_ptr, var_2, adj_ptr, adj_2, adj_8);
            // adj: for e in range(ptr[i]+lane,ptr[i+1],32):f-=P[idx[e]]*grad[e]                  <L 37>
        }
        // adj: if i<n:                                                                           <L 36>
        wp::adj_vec_t(var_5, adj_5, adj_6);
        // adj: f=wp.vec3(0.0)                                                                    <L 35>
        wp::adj_mod(var_0, var_3, adj_0, adj_3, adj_4);
        // adj: lane=t%32                                                                         <L 34>
        // adj: i=t//32                                                                           <L 33>
        // adj: t=wp.tid()                                                                        <L 32>
        // adj: def gather_packed(ptr:wp.array(dtype=int),idx:wp.array(dtype=int),grad:wp.array(dtype=wp.vec3),P:wp.array(dtype=wp.mat33),external:wp.array(dtype=wp.vec3),force:wp.array(dtype=wp.vec3),n:int):  <L 31>
        continue;
    }
}


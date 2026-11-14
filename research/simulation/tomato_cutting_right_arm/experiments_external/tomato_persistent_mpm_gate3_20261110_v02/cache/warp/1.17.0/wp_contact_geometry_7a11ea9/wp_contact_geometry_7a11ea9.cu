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



extern "C" __global__ void cad_query_9ddb0e61_cuda_kernel_forward(
    wp::launch_bounds_t<1> dim,
    wp::uint64 var_mesh,
    wp::array_t<wp::vec_t<3, wp::float32>> var_points,
    wp::array_t<wp::float32> var_phi,
    wp::array_t<wp::vec_t<3, wp::float32>> var_normal,
    wp::array_t<wp::vec_t<3, wp::float32>> var_closest,
    wp::array_t<wp::int32> var_face)
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
        wp::vec_t<3, wp::float32>* var_1;
        wp::vec_t<3, wp::float32> var_2;
        wp::vec_t<3, wp::float32> var_3;
        const wp::float32 var_4 = 10.0;
        wp::mesh_query_point_t var_5;
        const wp::float32 var_6 = 2.0;
        const wp::float32 var_7 = 0.5;
        bool* var_8;
        bool var_9;
        wp::int32* var_10;
        wp::float32* var_11;
        wp::float32* var_12;
        wp::vec_t<3, wp::float32> var_13;
        wp::int32 var_14;
        wp::float32 var_15;
        wp::float32 var_16;
        wp::vec_t<3, wp::float32> var_17;
        wp::float32 var_18;
        wp::float32* var_19;
        wp::float32 var_20;
        wp::float32 var_21;
        wp::int32* var_22;
        wp::int32 var_23;
        const wp::float32 var_24 = 1e-12;
        bool var_25;
        wp::float32* var_26;
        wp::vec_t<3, wp::float32> var_27;
        wp::float32 var_28;
        wp::vec_t<3, wp::float32> var_29;
        wp::int32* var_30;
        wp::vec_t<3, wp::float32> var_31;
        wp::int32 var_32;
        bool var_33;
        bool var_34;
        const wp::float32 var_35 = 100.0;
        const wp::float32 var_36 = 0.0;
        wp::vec_t<3, wp::float32> var_37;
        const wp::int32 var_38 = -1;
        bool var_39;
        //---------
        // forward
        // def cad_query(mesh:wp.uint64,points:wp.array(dtype=wp.vec3),phi:wp.array(dtype=float),normal:wp.array(dtype=wp.vec3),closest:wp.array(dtype=wp.vec3),face:wp.array(dtype=int)):       <L 14>
        // i=wp.tid();p=points[i];q=wp.mesh_query_point_sign_winding_number(mesh,p,10.0)          <L 15>
        var_0 = builtin_tid1d();
        var_1 = wp::address(var_points, var_0);
        var_3 = wp::load(var_1);
        var_2 = wp::copy(var_3);
        var_5 = wp::mesh_query_point_sign_winding_number(var_mesh, var_2, var_4, var_6, var_7);
        // if q.result:                                                                           <L 16>
        var_8 = &((var_5).result);
        var_9 = wp::load(var_8);
        if (var_9) {
            // c=wp.mesh_eval_position(mesh,q.face,q.u,q.v);d=p-c;distance=wp.length(d);phi[i]=q.sign*distance;closest[i]=c;face[i]=q.face       <L 17>
            var_10 = &((var_5).face);
            var_11 = &((var_5).u);
            var_12 = &((var_5).v);
            var_14 = wp::load(var_10);
            var_15 = wp::load(var_11);
            var_16 = wp::load(var_12);
            var_13 = wp::mesh_eval_position(var_mesh, var_14, var_15, var_16);
            var_17 = wp::sub(var_2, var_13);
            var_18 = wp::length(var_17);
            var_19 = &((var_5).sign);
            var_21 = wp::load(var_19);
            var_20 = wp::mul(var_21, var_18);
            wp::array_store(var_phi, var_0, var_20);
            wp::array_store(var_closest, var_0, var_13);
            var_22 = &((var_5).face);
            var_23 = wp::load(var_22);
            wp::array_store(var_face, var_0, var_23);
            // if distance>1e-12:normal[i]=q.sign*d/distance                                      <L 18>
            var_25 = (var_18 > var_24);
            if (var_25) {
                var_26 = &((var_5).sign);
                var_28 = wp::load(var_26);
                var_27 = wp::mul(var_28, var_17);
                var_29 = wp::div(var_27, var_18);
                wp::array_store(var_normal, var_0, var_29);
            }
            if (!var_25) {
                // else:normal[i]=wp.mesh_eval_face_normal(mesh,q.face)                           <L 19>
                var_30 = &((var_5).face);
                var_32 = wp::load(var_30);
                var_31 = wp::mesh_eval_face_normal(var_mesh, var_32);
                wp::array_store(var_normal, var_0, var_31);
            }
        }
        var_33 = wp::load(var_8);
        var_34 = wp::load(var_8);
        if (!var_34) {
            // else:phi[i]=100.0;normal[i]=wp.vec3(0.0);closest[i]=p;face[i]=-1                   <L 20>
            wp::array_store(var_phi, var_0, var_35);
            var_37 = wp::vec_t<3, wp::float32>(var_36);
            wp::array_store(var_normal, var_0, var_37);
            wp::array_store(var_closest, var_0, var_2);
            wp::array_store(var_face, var_0, var_38);
        }
        var_39 = wp::load(var_8);
    }
}


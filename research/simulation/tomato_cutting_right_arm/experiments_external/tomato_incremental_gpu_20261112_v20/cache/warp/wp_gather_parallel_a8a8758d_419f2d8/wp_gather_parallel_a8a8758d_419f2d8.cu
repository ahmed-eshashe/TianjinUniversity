#define WP_NO_BFLOAT16

#define WP_TILE_BLOCK_DIM 32
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


struct Incidence_0a73c0b4
{
    wp::array_t<wp::int32> ptr;
    wp::array_t<wp::int32> idx;
    wp::array_t<wp::vec_t<3, wp::float32>> grad;
    wp::array_t<wp::mat_t<3, 3, wp::float32>> P;


    Incidence_0a73c0b4() = default;
    CUDA_CALLABLE Incidence_0a73c0b4(wp::array_t<wp::int32> const& ptr,
    wp::array_t<wp::int32> const& idx = {},
    wp::array_t<wp::vec_t<3, wp::float32>> const& grad = {},
    wp::array_t<wp::mat_t<3, 3, wp::float32>> const& P = {})
        : ptr{ptr}
        , idx{idx}
        , grad{grad}
        , P{P}

    {
    }

    CUDA_CALLABLE Incidence_0a73c0b4& operator += (const Incidence_0a73c0b4& rhs)
    {
        return *this;}

};

static CUDA_CALLABLE void adj_Incidence_0a73c0b4(wp::array_t<wp::int32> const&,
    wp::array_t<wp::int32> const&,
    wp::array_t<wp::vec_t<3, wp::float32>> const&,
    wp::array_t<wp::mat_t<3, 3, wp::float32>> const&,
    wp::array_t<wp::int32> & adj_ptr,
    wp::array_t<wp::int32> & adj_idx,
    wp::array_t<wp::vec_t<3, wp::float32>> & adj_grad,
    wp::array_t<wp::mat_t<3, 3, wp::float32>> & adj_P,
    Incidence_0a73c0b4 & adj_ret)
{
    adj_ptr = adj_ret.ptr;
    adj_idx = adj_ret.idx;
    adj_grad = adj_ret.grad;
    adj_P = adj_ret.P;
}

// Required when compiling adjoints.
CUDA_CALLABLE Incidence_0a73c0b4 add(const Incidence_0a73c0b4& a, const Incidence_0a73c0b4& b)
{
    return Incidence_0a73c0b4();
}

CUDA_CALLABLE void adj_atomic_add(Incidence_0a73c0b4* p, Incidence_0a73c0b4 t)
{
    wp::adj_atomic_add(&p->ptr, t.ptr);
    wp::adj_atomic_add(&p->idx, t.idx);
    wp::adj_atomic_add(&p->grad, t.grad);
    wp::adj_atomic_add(&p->P, t.P);
}




// /home/omen/Documents/Codex/experiments/tomato_incremental_gpu_20261112_v20/src/parallel_force.py:11
static CUDA_CALLABLE wp::vec_t<3, wp::float32> lane_force_0(
    wp::int32 var_lane,
    wp::int32 var_i,
    Incidence_0a73c0b4 var_data)
{
    //---------
    // primal vars
    const wp::float32 var_0 = 0.0;
    wp::vec_t<3, wp::float32> var_1;
    wp::array_t<wp::int32>* var_2;
    wp::int32* var_3;
    wp::array_t<wp::int32> var_4;
    wp::int32 var_5;
    wp::int32 var_6;
    wp::array_t<wp::int32>* var_7;
    const wp::int32 var_8 = 1;
    wp::int32 var_9;
    wp::int32* var_10;
    wp::array_t<wp::int32> var_11;
    const wp::int32 var_12 = 32;
    wp::range_t var_13;
    wp::int32 var_14;
    wp::int32 var_15;
    wp::array_t<wp::mat_t<3, 3, wp::float32>>* var_16;
    wp::array_t<wp::int32>* var_17;
    wp::int32* var_18;
    wp::array_t<wp::int32> var_19;
    wp::mat_t<3, 3, wp::float32>* var_20;
    wp::array_t<wp::mat_t<3, 3, wp::float32>> var_21;
    wp::int32 var_22;
    wp::array_t<wp::vec_t<3, wp::float32>>* var_23;
    wp::vec_t<3, wp::float32>* var_24;
    wp::array_t<wp::vec_t<3, wp::float32>> var_25;
    wp::vec_t<3, wp::float32> var_26;
    wp::mat_t<3, 3, wp::float32> var_27;
    wp::vec_t<3, wp::float32> var_28;
    wp::vec_t<3, wp::float32> var_29;
    //---------
    // forward
    // def lane_force(lane:int,i:int,data:Incidence):                                         <L 12>
    // f=wp.vec3(0.0)                                                                         <L 13>
    var_1 = wp::vec_t<3, wp::float32>(var_0);
    // for e in range(data.ptr[i]+lane,data.ptr[i+1],32):f-=data.P[data.idx[e]]*data.grad[e]       <L 14>
    var_2 = &((var_data).ptr);
    var_4 = wp::load(var_2);
    var_3 = wp::address(var_4, var_i);
    var_6 = wp::load(var_3);
    var_5 = wp::add(var_6, var_lane);
    var_7 = &((var_data).ptr);
    var_9 = wp::add(var_i, var_8);
    var_11 = wp::load(var_7);
    var_10 = wp::address(var_11, var_9);
    var_14 = wp::load(var_10);
    var_13 = wp::range(var_5, var_14, var_12);
    start_for_0:;
        if (iter_cmp(var_13) == 0) goto end_for_0;
        var_15 = wp::iter_next(var_13);
        var_16 = &((var_data).P);
        var_17 = &((var_data).idx);
        var_19 = wp::load(var_17);
        var_18 = wp::address(var_19, var_15);
        var_21 = wp::load(var_16);
        var_22 = wp::load(var_18);
        var_20 = wp::address(var_21, var_22);
        var_23 = &((var_data).grad);
        var_25 = wp::load(var_23);
        var_24 = wp::address(var_25, var_15);
        var_27 = wp::load(var_20);
        var_28 = wp::load(var_24);
        var_26 = wp::mul(var_27, var_28);
        var_29 = wp::sub(var_1, var_26);
        wp::assign(var_1, var_29);
        goto start_for_0;
    end_for_0:;
    // return f                                                                               <L 15>
    return var_1;
}


// /home/omen/Documents/Codex/experiments/tomato_incremental_gpu_20261112_v20/src/parallel_force.py:11
static CUDA_CALLABLE void adj_lane_force_0(
    wp::int32 var_lane,
    wp::int32 var_i,
    Incidence_0a73c0b4 var_data,
    wp::int32 & adj_lane,
    wp::int32 & adj_i,
    Incidence_0a73c0b4 & adj_data,
    wp::vec_t<3, wp::float32> & adj_ret)
{
    //---------
    // primal vars
    const wp::float32 var_0 = 0.0;
    wp::vec_t<3, wp::float32> var_1;
    wp::array_t<wp::int32>* var_2;
    wp::int32* var_3;
    wp::array_t<wp::int32> var_4;
    wp::int32 var_5;
    wp::int32 var_6;
    wp::array_t<wp::int32>* var_7;
    const wp::int32 var_8 = 1;
    wp::int32 var_9;
    wp::int32* var_10;
    wp::array_t<wp::int32> var_11;
    const wp::int32 var_12 = 32;
    wp::range_t var_13;
    wp::int32 var_14;
    wp::int32 var_15;
    wp::array_t<wp::mat_t<3, 3, wp::float32>>* var_16;
    wp::array_t<wp::int32>* var_17;
    wp::int32* var_18;
    wp::array_t<wp::int32> var_19;
    wp::mat_t<3, 3, wp::float32>* var_20;
    wp::array_t<wp::mat_t<3, 3, wp::float32>> var_21;
    wp::int32 var_22;
    wp::array_t<wp::vec_t<3, wp::float32>>* var_23;
    wp::vec_t<3, wp::float32>* var_24;
    wp::array_t<wp::vec_t<3, wp::float32>> var_25;
    wp::vec_t<3, wp::float32> var_26;
    wp::mat_t<3, 3, wp::float32> var_27;
    wp::vec_t<3, wp::float32> var_28;
    wp::vec_t<3, wp::float32> var_29;
    //---------
    // dual vars
    wp::float32 adj_0 = {};
    wp::vec_t<3, wp::float32> adj_1 = {};
    wp::array_t<wp::int32> adj_2 = {};
    wp::int32 adj_3 = {};
    wp::array_t<wp::int32> adj_4 = {};
    wp::int32 adj_5 = {};
    wp::int32 adj_6 = {};
    wp::array_t<wp::int32> adj_7 = {};
    wp::int32 adj_8 = {};
    wp::int32 adj_9 = {};
    wp::int32 adj_10 = {};
    wp::array_t<wp::int32> adj_11 = {};
    wp::int32 adj_12 = {};
    wp::range_t adj_13 = {};
    wp::int32 adj_14 = {};
    wp::int32 adj_15 = {};
    wp::array_t<wp::mat_t<3, 3, wp::float32>> adj_16 = {};
    wp::array_t<wp::int32> adj_17 = {};
    wp::int32 adj_18 = {};
    wp::array_t<wp::int32> adj_19 = {};
    wp::mat_t<3, 3, wp::float32> adj_20 = {};
    wp::array_t<wp::mat_t<3, 3, wp::float32>> adj_21 = {};
    wp::int32 adj_22 = {};
    wp::array_t<wp::vec_t<3, wp::float32>> adj_23 = {};
    wp::vec_t<3, wp::float32> adj_24 = {};
    wp::array_t<wp::vec_t<3, wp::float32>> adj_25 = {};
    wp::vec_t<3, wp::float32> adj_26 = {};
    wp::mat_t<3, 3, wp::float32> adj_27 = {};
    wp::vec_t<3, wp::float32> adj_28 = {};
    wp::vec_t<3, wp::float32> adj_29 = {};
    //---------
    // forward
    // def lane_force(lane:int,i:int,data:Incidence):                                         <L 12>
    // f=wp.vec3(0.0)                                                                         <L 13>
    var_1 = wp::vec_t<3, wp::float32>(var_0);
    // for e in range(data.ptr[i]+lane,data.ptr[i+1],32):f-=data.P[data.idx[e]]*data.grad[e]       <L 14>
    var_2 = &((var_data).ptr);
    var_4 = wp::load(var_2);
    var_3 = wp::address(var_4, var_i);
    var_6 = wp::load(var_3);
    var_5 = wp::add(var_6, var_lane);
    var_7 = &((var_data).ptr);
    var_9 = wp::add(var_i, var_8);
    var_11 = wp::load(var_7);
    var_10 = wp::address(var_11, var_9);
    var_14 = wp::load(var_10);
    var_13 = wp::range(var_5, var_14, var_12);
    // return f                                                                               <L 15>
    goto label2;
    //---------
    // reverse
    label2:;
    adj_1 += adj_ret;
    // adj: return f                                                                          <L 15>
    var_13 = wp::iter_reverse(var_13);
    start_for_0:;
        if (iter_cmp(var_13) == 0) goto end_for_0;
        var_15 = wp::iter_next(var_13);
    	adj_16 = {};
    	adj_17 = {};
    	adj_18 = {};
    	adj_19 = {};
    	adj_20 = {};
    	adj_21 = {};
    	adj_22 = {};
    	adj_23 = {};
    	adj_24 = {};
    	adj_25 = {};
    	adj_26 = {};
    	adj_27 = {};
    	adj_28 = {};
    	adj_29 = {};
        var_16 = &((var_data).P);
        var_17 = &((var_data).idx);
        var_19 = wp::load(var_17);
        var_18 = wp::address(var_19, var_15);
        var_21 = wp::load(var_16);
        var_22 = wp::load(var_18);
        var_20 = wp::address(var_21, var_22);
        var_23 = &((var_data).grad);
        var_25 = wp::load(var_23);
        var_24 = wp::address(var_25, var_15);
        var_27 = wp::load(var_20);
        var_28 = wp::load(var_24);
        var_26 = wp::mul(var_27, var_28);
        var_29 = wp::sub(var_1, var_26);
        wp::assign(var_1, var_29);
        wp::adj_assign(var_1, var_29, adj_1, adj_29);
        wp::adj_sub(var_1, var_26, adj_1, adj_26, adj_29);
        wp::adj_mul(var_27, var_28, adj_20, adj_24, adj_26);
        wp::adj_address(var_25, var_15, adj_23, adj_15, adj_24);
        adj_data.grad = adj_23;
        wp::adj_address(var_21, var_22, adj_16, adj_18, adj_20);
        wp::adj_address(var_19, var_15, adj_17, adj_15, adj_18);
        adj_data.idx = adj_17;
        adj_data.P = adj_16;
    	goto start_for_0;
    end_for_0:;
    wp::adj_address(var_11, var_9, adj_7, adj_9, adj_10);
    wp::adj_add(var_i, var_8, adj_i, adj_8, adj_9);
    adj_data.ptr = adj_7;
    wp::adj_add(var_6, var_lane, adj_3, adj_lane, adj_5);
    wp::adj_address(var_4, var_i, adj_2, adj_i, adj_3);
    adj_data.ptr = adj_2;
    // adj: for e in range(data.ptr[i]+lane,data.ptr[i+1],32):f-=data.P[data.idx[e]]*data.grad[e]  <L 14>
    wp::adj_vec_t(var_0, adj_0, adj_1);
    // adj: f=wp.vec3(0.0)                                                                    <L 13>
    // adj: def lane_force(lane:int,i:int,data:Incidence):                                    <L 12>
    return;
}



extern "C" __global__ void gather_parallel_5a1dda83_cuda_kernel_forward(
    wp::launch_bounds_t<1> dim,
    wp::array_t<wp::int32> var_ptr,
    wp::array_t<wp::int32> var_idx,
    wp::array_t<wp::vec_t<3, wp::float32>> var_grad,
    wp::array_t<wp::mat_t<3, 3, wp::float32>> var_P,
    wp::array_t<wp::vec_t<3, wp::float32>> var_external,
    wp::array_t<wp::vec_t<3, wp::float32>> var_force)
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
        Incidence_0a73c0b4 var_1;
        const wp::int32 var_2 = 32;
        wp::tile_register_t<wp::int32,wp::tile_layout_register_t<wp::tile_shape_t<32>>> var_3 = wp::tile_register_t<wp::int32,wp::tile_layout_register_t<wp::tile_shape_t<32>>>{};
        const wp::int32 var_4 = 0;
        const wp::int32 var_5 = 1;
        wp::tile_register_t<wp::vec_t<3, wp::float32>,wp::tile_layout_register_t<wp::tile_shape_t<32>>> var_6 = wp::tile_register_t<wp::vec_t<3, wp::float32>,wp::tile_layout_register_t<wp::tile_shape_t<32>>>{};
        wp::tile_register_t<wp::vec_t<3, wp::float32>,wp::tile_layout_register_t<wp::tile_shape_t<1>>> var_7 = wp::tile_register_t<wp::vec_t<3, wp::float32>,wp::tile_layout_register_t<wp::tile_shape_t<1>>>{};
        const wp::int32 var_8 = 1;
        wp::vec_t<3, wp::float32>* var_9;
        wp::tile_register_t<wp::vec_t<3, wp::float32>,wp::tile_layout_register_t<wp::tile_shape_t<1>>> var_10 = wp::tile_register_t<wp::vec_t<3, wp::float32>,wp::tile_layout_register_t<wp::tile_shape_t<1>>>{};
        wp::vec_t<3, wp::float32> var_11;
        wp::tile_register_t<wp::vec_t<3, wp::float32>,wp::tile_layout_register_t<wp::tile_shape_t<1>>> var_12 = wp::tile_register_t<wp::vec_t<3, wp::float32>,wp::tile_layout_register_t<wp::tile_shape_t<1>>>{};
        //---------
        // forward
        // def gather_parallel(ptr:wp.array(dtype=int),idx:wp.array(dtype=int),grad:wp.array(dtype=wp.vec3),P:wp.array(dtype=wp.mat33),external:wp.array(dtype=wp.vec3),force:wp.array(dtype=wp.vec3)):       <L 18>
        // i=wp.tid()                                                                             <L 19>
        var_0 = builtin_tid1d();
        // data=Incidence()                                                                       <L 20>
        var_1 = Incidence_0a73c0b4();
        // data.ptr=ptr                                                                           <L 21>
        var_1.ptr = var_ptr;
        // data.idx=idx                                                                           <L 22>
        var_1.idx = var_idx;
        // data.grad=grad                                                                         <L 23>
        var_1.grad = var_grad;
        // data.P=P                                                                               <L 24>
        var_1.P = var_P;
        // lanes=wp.tile_arange(32,dtype=int)                                                     <L 25>
        var_3 = wp::tile_arange<wp::int32, 32>(var_4, var_2, var_5);
        // values=wp.tile_map(lane_force,lanes,i,data)                                            <L 26>
        var_6 = wp::tile_map(lane_force_0, var_3, var_0, var_1);
        // total=wp.tile_sum(values)                                                              <L 27>
        var_7 = wp::tile_sum(var_6);
        // wp.tile_store(force,total+wp.tile_full(1,value=external[i],dtype=wp.vec3),offset=i)       <L 28>
        var_9 = wp::address(var_external, var_0);
        var_11 = wp::load(var_9);
        var_10 = wp::tile_full<wp::vec_t<3, wp::float32>, 1>(var_11);
        var_12 = wp::tile_add(var_7, var_10);
        wp::tile_store<wp::vec_t<3, wp::float32>, true, false>(var_force, var_0, var_12);
    }
}



extern "C" __global__ void gather_parallel_5a1dda83_cuda_kernel_backward(
    wp::launch_bounds_t<1> dim,
    wp::array_t<wp::int32> var_ptr,
    wp::array_t<wp::int32> var_idx,
    wp::array_t<wp::vec_t<3, wp::float32>> var_grad,
    wp::array_t<wp::mat_t<3, 3, wp::float32>> var_P,
    wp::array_t<wp::vec_t<3, wp::float32>> var_external,
    wp::array_t<wp::vec_t<3, wp::float32>> var_force,
    wp::array_t<wp::int32> adj_ptr,
    wp::array_t<wp::int32> adj_idx,
    wp::array_t<wp::vec_t<3, wp::float32>> adj_grad,
    wp::array_t<wp::mat_t<3, 3, wp::float32>> adj_P,
    wp::array_t<wp::vec_t<3, wp::float32>> adj_external,
    wp::array_t<wp::vec_t<3, wp::float32>> adj_force)
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
        Incidence_0a73c0b4 var_1;
        const wp::int32 var_2 = 32;
        wp::tile_register_t<wp::int32,wp::tile_layout_register_t<wp::tile_shape_t<32>>> var_3 = wp::tile_register_t<wp::int32,wp::tile_layout_register_t<wp::tile_shape_t<32>>>{};
        const wp::int32 var_4 = 0;
        const wp::int32 var_5 = 1;
        wp::tile_register_t<wp::vec_t<3, wp::float32>,wp::tile_layout_register_t<wp::tile_shape_t<32>>> var_6 = wp::tile_register_t<wp::vec_t<3, wp::float32>,wp::tile_layout_register_t<wp::tile_shape_t<32>>>{};
        wp::tile_register_t<wp::vec_t<3, wp::float32>,wp::tile_layout_register_t<wp::tile_shape_t<1>>> var_7 = wp::tile_register_t<wp::vec_t<3, wp::float32>,wp::tile_layout_register_t<wp::tile_shape_t<1>>>{};
        const wp::int32 var_8 = 1;
        wp::vec_t<3, wp::float32>* var_9;
        wp::tile_register_t<wp::vec_t<3, wp::float32>,wp::tile_layout_register_t<wp::tile_shape_t<1>>> var_10 = wp::tile_register_t<wp::vec_t<3, wp::float32>,wp::tile_layout_register_t<wp::tile_shape_t<1>>>{};
        wp::vec_t<3, wp::float32> var_11;
        wp::tile_register_t<wp::vec_t<3, wp::float32>,wp::tile_layout_register_t<wp::tile_shape_t<1>>> var_12 = wp::tile_register_t<wp::vec_t<3, wp::float32>,wp::tile_layout_register_t<wp::tile_shape_t<1>>>{};
        //---------
        // dual vars
        wp::int32 adj_0 = {};
        Incidence_0a73c0b4 adj_1 = {};
        wp::int32 adj_2 = {};
        wp::tile_register_t<wp::int32,wp::tile_layout_register_t<wp::tile_shape_t<32>>> adj_3{};
        wp::int32 adj_4 = {};
        wp::int32 adj_5 = {};
        wp::tile_register_t<wp::vec_t<3, wp::float32>,wp::tile_layout_register_t<wp::tile_shape_t<32>>> adj_6{};
        wp::tile_register_t<wp::vec_t<3, wp::float32>,wp::tile_layout_register_t<wp::tile_shape_t<1>>> adj_7{};
        wp::int32 adj_8 = {};
        wp::vec_t<3, wp::float32> adj_9 = {};
        wp::tile_register_t<wp::vec_t<3, wp::float32>,wp::tile_layout_register_t<wp::tile_shape_t<1>>> adj_10{};
        wp::vec_t<3, wp::float32> adj_11 = {};
        wp::tile_register_t<wp::vec_t<3, wp::float32>,wp::tile_layout_register_t<wp::tile_shape_t<1>>> adj_12{};
        //---------
        // forward
        // def gather_parallel(ptr:wp.array(dtype=int),idx:wp.array(dtype=int),grad:wp.array(dtype=wp.vec3),P:wp.array(dtype=wp.mat33),external:wp.array(dtype=wp.vec3),force:wp.array(dtype=wp.vec3)):       <L 18>
        // i=wp.tid()                                                                             <L 19>
        var_0 = builtin_tid1d();
        // data=Incidence()                                                                       <L 20>
        var_1 = Incidence_0a73c0b4();
        // data.ptr=ptr                                                                           <L 21>
        var_1.ptr = var_ptr;
        // data.idx=idx                                                                           <L 22>
        var_1.idx = var_idx;
        // data.grad=grad                                                                         <L 23>
        var_1.grad = var_grad;
        // data.P=P                                                                               <L 24>
        var_1.P = var_P;
        // lanes=wp.tile_arange(32,dtype=int)                                                     <L 25>
        var_3 = wp::tile_arange<wp::int32, 32>(var_4, var_2, var_5);
        // values=wp.tile_map(lane_force,lanes,i,data)                                            <L 26>
        var_6 = wp::tile_map(lane_force_0, var_3, var_0, var_1);
        // total=wp.tile_sum(values)                                                              <L 27>
        var_7 = wp::tile_sum(var_6);
        // wp.tile_store(force,total+wp.tile_full(1,value=external[i],dtype=wp.vec3),offset=i)       <L 28>
        var_9 = wp::address(var_external, var_0);
        var_11 = wp::load(var_9);
        var_10 = wp::tile_full<wp::vec_t<3, wp::float32>, 1>(var_11);
        var_12 = wp::tile_add(var_7, var_10);
        // wp::tile_store<wp::vec_t<3, wp::float32>, true, false>(var_force, var_0, var_12);
        //---------
        // reverse
        wp::adj_tile_store(var_force, var_0, var_12, adj_force, adj_0, adj_12);
        wp::adj_tile_add(var_7, var_10, adj_7, adj_10, adj_12);
        wp::adj_address(var_external, var_0, adj_external, adj_0, adj_9);
        // adj: wp.tile_store(force,total+wp.tile_full(1,value=external[i],dtype=wp.vec3),offset=i)  <L 28>
        wp::adj_tile_sum(var_6, adj_6, adj_7);
        // adj: total=wp.tile_sum(values)                                                         <L 27>
        wp::adj_tile_map(lane_force_0, var_3, var_0, var_1, adj_lane_force_0, adj_3, adj_0, adj_1, adj_6);
        // adj: values=wp.tile_map(lane_force,lanes,i,data)                                       <L 26>
        // adj: lanes=wp.tile_arange(32,dtype=int)                                                <L 25>
        adj_1.P = {};
        // adj: data.P=P                                                                          <L 24>
        adj_1.grad = {};
        // adj: data.grad=grad                                                                    <L 23>
        adj_1.idx = {};
        // adj: data.idx=idx                                                                      <L 22>
        adj_1.ptr = {};
        // adj: data.ptr=ptr                                                                      <L 21>
        // adj: data=Incidence()                                                                  <L 20>
        // adj: i=wp.tid()                                                                        <L 19>
        // adj: def gather_parallel(ptr:wp.array(dtype=int),idx:wp.array(dtype=int),grad:wp.array(dtype=wp.vec3),P:wp.array(dtype=wp.mat33),external:wp.array(dtype=wp.vec3),force:wp.array(dtype=wp.vec3)):  <L 18>
        continue;
    }
}


#define WP_NO_BFLOAT16

#define WP_TILE_BLOCK_DIM 1
#define WP_NO_CRT
#include "builtin.h"
#include "deterministic.h"

#define builtin_tid1d() wp::tid(task_index, dim)
#define builtin_tid2d(x, y) wp::tid(x, y, task_index, dim)
#define builtin_tid3d(x, y, z) wp::tid(x, y, z, task_index, dim)
#define builtin_tid4d(x, y, z, w) wp::tid(x, y, z, w, task_index, dim)

#define builtin_block_dim() wp::block_dim()


// avoid namespacing of float type for casting to float type, this is to avoid wp::float(x), which is not valid in C++
#define float(x) cast_float(x)
#define adj_float(x, adj_x, adj_ret) adj_cast_float(x, adj_x, adj_ret)

#define int(x) cast_int(x)
#define adj_int(x, adj_x, adj_ret) adj_cast_int(x, adj_x, adj_ret)

struct wp_args_set_forces_to_dual_buffers_index_0184dbed {
    wp::array_t<wp::int64> env_ids;
    wp::array_t<wp::int32> body_ids;
    wp::array_t<wp::vec_t<3, wp::float32>> forces;
    wp::array_t<wp::vec_t<3, wp::float32>> torques;
    wp::array_t<wp::vec_t<3, wp::float32>> positions;
    wp::array_t<wp::vec_t<3, wp::float32>> global_force_w;
    wp::array_t<wp::vec_t<3, wp::float32>> global_torque_w;
    wp::array_t<wp::vec_t<3, wp::float32>> global_force_at_com_w;
    wp::array_t<wp::vec_t<3, wp::float32>> local_force_b;
    wp::array_t<wp::vec_t<3, wp::float32>> local_torque_b;
    bool is_global;
};


void set_forces_to_dual_buffers_index_0184dbed_cpu_kernel_forward(
    wp::launch_bounds_t<2> dim,
    size_t task_index,
    wp_args_set_forces_to_dual_buffers_index_0184dbed *_wp_args)
{
    //---------
    // argument vars
    wp::array_t<wp::int64> var_env_ids = _wp_args->env_ids;
    wp::array_t<wp::int32> var_body_ids = _wp_args->body_ids;
    wp::array_t<wp::vec_t<3, wp::float32>> var_forces = _wp_args->forces;
    wp::array_t<wp::vec_t<3, wp::float32>> var_torques = _wp_args->torques;
    wp::array_t<wp::vec_t<3, wp::float32>> var_positions = _wp_args->positions;
    wp::array_t<wp::vec_t<3, wp::float32>> var_global_force_w = _wp_args->global_force_w;
    wp::array_t<wp::vec_t<3, wp::float32>> var_global_torque_w = _wp_args->global_torque_w;
    wp::array_t<wp::vec_t<3, wp::float32>> var_global_force_at_com_w = _wp_args->global_force_at_com_w;
    wp::array_t<wp::vec_t<3, wp::float32>> var_local_force_b = _wp_args->local_force_b;
    wp::array_t<wp::vec_t<3, wp::float32>> var_local_torque_b = _wp_args->local_torque_b;
    bool var_is_global = _wp_args->is_global;
    //---------
    // primal vars
    wp::int32 var_0;
    wp::int32 var_1;
    wp::int64* var_2;
    wp::int32 var_3;
    wp::int64 var_4;
    wp::int32* var_5;
    wp::int32 var_6;
    wp::int32 var_7;
    wp::vec_t<3, wp::float32>* var_8;
    wp::vec_t<3, wp::float32> var_9;
    wp::vec_t<3, wp::float32>* var_10;
    wp::vec_t<3, wp::float32> var_11;
    wp::vec_t<3, wp::float32>* var_12;
    wp::vec_t<3, wp::float32>* var_13;
    wp::vec_t<3, wp::float32>* var_14;
    wp::vec_t<3, wp::float32> var_15;
    wp::vec_t<3, wp::float32> var_16;
    wp::vec_t<3, wp::float32> var_17;
    wp::vec_t<3, wp::float32> var_18;
    wp::vec_t<3, wp::float32> var_19;
    wp::vec_t<3, wp::float32>* var_20;
    wp::vec_t<3, wp::float32>* var_21;
    wp::vec_t<3, wp::float32> var_22;
    wp::vec_t<3, wp::float32> var_23;
    wp::vec_t<3, wp::float32> var_24;
    wp::vec_t<3, wp::float32>* var_25;
    wp::vec_t<3, wp::float32> var_26;
    wp::vec_t<3, wp::float32>* var_27;
    wp::vec_t<3, wp::float32> var_28;
    wp::vec_t<3, wp::float32>* var_29;
    wp::vec_t<3, wp::float32> var_30;
    wp::vec_t<3, wp::float32>* var_31;
    wp::vec_t<3, wp::float32>* var_32;
    wp::vec_t<3, wp::float32>* var_33;
    wp::vec_t<3, wp::float32> var_34;
    wp::vec_t<3, wp::float32> var_35;
    wp::vec_t<3, wp::float32> var_36;
    wp::vec_t<3, wp::float32> var_37;
    wp::vec_t<3, wp::float32> var_38;
    wp::vec_t<3, wp::float32>* var_39;
    wp::vec_t<3, wp::float32>* var_40;
    wp::vec_t<3, wp::float32> var_41;
    wp::vec_t<3, wp::float32> var_42;
    wp::vec_t<3, wp::float32> var_43;
    //---------
    // forward
    // def set_forces_to_dual_buffers_index(                                                  <L 1>
    // tid_env, tid_body = wp.tid()                                                           <L 25>
    builtin_tid2d(var_0, var_1);
    // ei = wp.int32(env_ids[tid_env])                                                        <L 26>
    var_2 = wp::address(var_env_ids, var_0);
    var_4 = wp::load(var_2);
    var_3 = wp::int32(var_4);
    // bi = wp.int32(body_ids[tid_body])                                                      <L 27>
    var_5 = wp::address(var_body_ids, var_1);
    var_7 = wp::load(var_5);
    var_6 = wp::int32(var_7);
    // if is_global:                                                                          <L 29>
    if (var_is_global) {
        // if torques:                                                                        <L 30>
        if (var_torques) {
            // global_torque_w[ei, bi] = torques[tid_env, tid_body]                           <L 31>
            var_8 = wp::address(var_torques, var_0, var_1);
            var_9 = wp::load(var_8);
            wp::array_store(var_global_torque_w, var_3, var_6, var_9);
        }
        // if forces:                                                                         <L 32>
        if (var_forces) {
            // if positions:                                                                  <L 33>
            if (var_positions) {
                // global_force_w[ei, bi] = forces[tid_env, tid_body]                         <L 34>
                var_10 = wp::address(var_forces, var_0, var_1);
                var_11 = wp::load(var_10);
                wp::array_store(var_global_force_w, var_3, var_6, var_11);
                // if torques:                                                                <L 35>
                if (var_torques) {
                    // global_torque_w[ei, bi] = global_torque_w[ei, bi] + wp.cross(          <L 36>
                    var_12 = wp::address(var_global_torque_w, var_3, var_6);
                    // positions[tid_env, tid_body], forces[tid_env, tid_body]                <L 37>
                    var_13 = wp::address(var_positions, var_0, var_1);
                    var_14 = wp::address(var_forces, var_0, var_1);
                    var_16 = wp::load(var_13);
                    var_17 = wp::load(var_14);
                    var_15 = wp::cross(var_16, var_17);
                    var_19 = wp::load(var_12);
                    var_18 = wp::add(var_19, var_15);
                    // global_torque_w[ei, bi] = global_torque_w[ei, bi] + wp.cross(          <L 36>
                    wp::array_store(var_global_torque_w, var_3, var_6, var_18);
                }
                if (!var_torques) {
                    // global_torque_w[ei, bi] = wp.cross(positions[tid_env, tid_body], forces[tid_env, tid_body])       <L 40>
                    var_20 = wp::address(var_positions, var_0, var_1);
                    var_21 = wp::address(var_forces, var_0, var_1);
                    var_23 = wp::load(var_20);
                    var_24 = wp::load(var_21);
                    var_22 = wp::cross(var_23, var_24);
                    wp::array_store(var_global_torque_w, var_3, var_6, var_22);
                }
            }
            if (!var_positions) {
                // global_force_at_com_w[ei, bi] = forces[tid_env, tid_body]                  <L 42>
                var_25 = wp::address(var_forces, var_0, var_1);
                var_26 = wp::load(var_25);
                wp::array_store(var_global_force_at_com_w, var_3, var_6, var_26);
            }
        }
    }
    if (!var_is_global) {
        // if torques:                                                                        <L 44>
        if (var_torques) {
            // local_torque_b[ei, bi] = torques[tid_env, tid_body]                            <L 45>
            var_27 = wp::address(var_torques, var_0, var_1);
            var_28 = wp::load(var_27);
            wp::array_store(var_local_torque_b, var_3, var_6, var_28);
        }
        // if forces:                                                                         <L 46>
        if (var_forces) {
            // local_force_b[ei, bi] = forces[tid_env, tid_body]                              <L 47>
            var_29 = wp::address(var_forces, var_0, var_1);
            var_30 = wp::load(var_29);
            wp::array_store(var_local_force_b, var_3, var_6, var_30);
            // if positions:                                                                  <L 48>
            if (var_positions) {
                // if torques:                                                                <L 49>
                if (var_torques) {
                    // local_torque_b[ei, bi] = local_torque_b[ei, bi] + wp.cross(            <L 50>
                    var_31 = wp::address(var_local_torque_b, var_3, var_6);
                    // positions[tid_env, tid_body], forces[tid_env, tid_body]                <L 51>
                    var_32 = wp::address(var_positions, var_0, var_1);
                    var_33 = wp::address(var_forces, var_0, var_1);
                    var_35 = wp::load(var_32);
                    var_36 = wp::load(var_33);
                    var_34 = wp::cross(var_35, var_36);
                    var_38 = wp::load(var_31);
                    var_37 = wp::add(var_38, var_34);
                    // local_torque_b[ei, bi] = local_torque_b[ei, bi] + wp.cross(            <L 50>
                    wp::array_store(var_local_torque_b, var_3, var_6, var_37);
                }
                if (!var_torques) {
                    // local_torque_b[ei, bi] = wp.cross(positions[tid_env, tid_body], forces[tid_env, tid_body])       <L 54>
                    var_39 = wp::address(var_positions, var_0, var_1);
                    var_40 = wp::address(var_forces, var_0, var_1);
                    var_42 = wp::load(var_39);
                    var_43 = wp::load(var_40);
                    var_41 = wp::cross(var_42, var_43);
                    wp::array_store(var_local_torque_b, var_3, var_6, var_41);
                }
            }
        }
    }
}



void set_forces_to_dual_buffers_index_0184dbed_cpu_kernel_backward(
    wp::launch_bounds_t<2> dim,
    size_t task_index,
    wp_args_set_forces_to_dual_buffers_index_0184dbed *_wp_args,
    wp_args_set_forces_to_dual_buffers_index_0184dbed *_wp_adj_args)
{
    //---------
    // argument vars
    wp::array_t<wp::int64> var_env_ids = _wp_args->env_ids;
    wp::array_t<wp::int32> var_body_ids = _wp_args->body_ids;
    wp::array_t<wp::vec_t<3, wp::float32>> var_forces = _wp_args->forces;
    wp::array_t<wp::vec_t<3, wp::float32>> var_torques = _wp_args->torques;
    wp::array_t<wp::vec_t<3, wp::float32>> var_positions = _wp_args->positions;
    wp::array_t<wp::vec_t<3, wp::float32>> var_global_force_w = _wp_args->global_force_w;
    wp::array_t<wp::vec_t<3, wp::float32>> var_global_torque_w = _wp_args->global_torque_w;
    wp::array_t<wp::vec_t<3, wp::float32>> var_global_force_at_com_w = _wp_args->global_force_at_com_w;
    wp::array_t<wp::vec_t<3, wp::float32>> var_local_force_b = _wp_args->local_force_b;
    wp::array_t<wp::vec_t<3, wp::float32>> var_local_torque_b = _wp_args->local_torque_b;
    bool var_is_global = _wp_args->is_global;
    wp::array_t<wp::int64> adj_env_ids = _wp_adj_args->env_ids;
    wp::array_t<wp::int32> adj_body_ids = _wp_adj_args->body_ids;
    wp::array_t<wp::vec_t<3, wp::float32>> adj_forces = _wp_adj_args->forces;
    wp::array_t<wp::vec_t<3, wp::float32>> adj_torques = _wp_adj_args->torques;
    wp::array_t<wp::vec_t<3, wp::float32>> adj_positions = _wp_adj_args->positions;
    wp::array_t<wp::vec_t<3, wp::float32>> adj_global_force_w = _wp_adj_args->global_force_w;
    wp::array_t<wp::vec_t<3, wp::float32>> adj_global_torque_w = _wp_adj_args->global_torque_w;
    wp::array_t<wp::vec_t<3, wp::float32>> adj_global_force_at_com_w = _wp_adj_args->global_force_at_com_w;
    wp::array_t<wp::vec_t<3, wp::float32>> adj_local_force_b = _wp_adj_args->local_force_b;
    wp::array_t<wp::vec_t<3, wp::float32>> adj_local_torque_b = _wp_adj_args->local_torque_b;
    bool adj_is_global = _wp_adj_args->is_global;
    //---------
    // primal vars
    wp::int32 var_0;
    wp::int32 var_1;
    wp::int64* var_2;
    wp::int32 var_3;
    wp::int64 var_4;
    wp::int32* var_5;
    wp::int32 var_6;
    wp::int32 var_7;
    wp::vec_t<3, wp::float32>* var_8;
    wp::vec_t<3, wp::float32> var_9;
    wp::vec_t<3, wp::float32>* var_10;
    wp::vec_t<3, wp::float32> var_11;
    wp::vec_t<3, wp::float32>* var_12;
    wp::vec_t<3, wp::float32>* var_13;
    wp::vec_t<3, wp::float32>* var_14;
    wp::vec_t<3, wp::float32> var_15;
    wp::vec_t<3, wp::float32> var_16;
    wp::vec_t<3, wp::float32> var_17;
    wp::vec_t<3, wp::float32> var_18;
    wp::vec_t<3, wp::float32> var_19;
    wp::vec_t<3, wp::float32>* var_20;
    wp::vec_t<3, wp::float32>* var_21;
    wp::vec_t<3, wp::float32> var_22;
    wp::vec_t<3, wp::float32> var_23;
    wp::vec_t<3, wp::float32> var_24;
    wp::vec_t<3, wp::float32>* var_25;
    wp::vec_t<3, wp::float32> var_26;
    wp::vec_t<3, wp::float32>* var_27;
    wp::vec_t<3, wp::float32> var_28;
    wp::vec_t<3, wp::float32>* var_29;
    wp::vec_t<3, wp::float32> var_30;
    wp::vec_t<3, wp::float32>* var_31;
    wp::vec_t<3, wp::float32>* var_32;
    wp::vec_t<3, wp::float32>* var_33;
    wp::vec_t<3, wp::float32> var_34;
    wp::vec_t<3, wp::float32> var_35;
    wp::vec_t<3, wp::float32> var_36;
    wp::vec_t<3, wp::float32> var_37;
    wp::vec_t<3, wp::float32> var_38;
    wp::vec_t<3, wp::float32>* var_39;
    wp::vec_t<3, wp::float32>* var_40;
    wp::vec_t<3, wp::float32> var_41;
    wp::vec_t<3, wp::float32> var_42;
    wp::vec_t<3, wp::float32> var_43;
    //---------
    // dual vars
    wp::int32 adj_0 = {};
    wp::int32 adj_1 = {};
    wp::int64 adj_2 = {};
    wp::int32 adj_3 = {};
    wp::int64 adj_4 = {};
    wp::int32 adj_5 = {};
    wp::int32 adj_6 = {};
    wp::int32 adj_7 = {};
    wp::vec_t<3, wp::float32> adj_8 = {};
    wp::vec_t<3, wp::float32> adj_9 = {};
    wp::vec_t<3, wp::float32> adj_10 = {};
    wp::vec_t<3, wp::float32> adj_11 = {};
    wp::vec_t<3, wp::float32> adj_12 = {};
    wp::vec_t<3, wp::float32> adj_13 = {};
    wp::vec_t<3, wp::float32> adj_14 = {};
    wp::vec_t<3, wp::float32> adj_15 = {};
    wp::vec_t<3, wp::float32> adj_16 = {};
    wp::vec_t<3, wp::float32> adj_17 = {};
    wp::vec_t<3, wp::float32> adj_18 = {};
    wp::vec_t<3, wp::float32> adj_19 = {};
    wp::vec_t<3, wp::float32> adj_20 = {};
    wp::vec_t<3, wp::float32> adj_21 = {};
    wp::vec_t<3, wp::float32> adj_22 = {};
    wp::vec_t<3, wp::float32> adj_23 = {};
    wp::vec_t<3, wp::float32> adj_24 = {};
    wp::vec_t<3, wp::float32> adj_25 = {};
    wp::vec_t<3, wp::float32> adj_26 = {};
    wp::vec_t<3, wp::float32> adj_27 = {};
    wp::vec_t<3, wp::float32> adj_28 = {};
    wp::vec_t<3, wp::float32> adj_29 = {};
    wp::vec_t<3, wp::float32> adj_30 = {};
    wp::vec_t<3, wp::float32> adj_31 = {};
    wp::vec_t<3, wp::float32> adj_32 = {};
    wp::vec_t<3, wp::float32> adj_33 = {};
    wp::vec_t<3, wp::float32> adj_34 = {};
    wp::vec_t<3, wp::float32> adj_35 = {};
    wp::vec_t<3, wp::float32> adj_36 = {};
    wp::vec_t<3, wp::float32> adj_37 = {};
    wp::vec_t<3, wp::float32> adj_38 = {};
    wp::vec_t<3, wp::float32> adj_39 = {};
    wp::vec_t<3, wp::float32> adj_40 = {};
    wp::vec_t<3, wp::float32> adj_41 = {};
    wp::vec_t<3, wp::float32> adj_42 = {};
    wp::vec_t<3, wp::float32> adj_43 = {};
    //---------
    // forward
    // def set_forces_to_dual_buffers_index(                                                  <L 1>
    // tid_env, tid_body = wp.tid()                                                           <L 25>
    builtin_tid2d(var_0, var_1);
    // ei = wp.int32(env_ids[tid_env])                                                        <L 26>
    var_2 = wp::address(var_env_ids, var_0);
    var_4 = wp::load(var_2);
    var_3 = wp::int32(var_4);
    // bi = wp.int32(body_ids[tid_body])                                                      <L 27>
    var_5 = wp::address(var_body_ids, var_1);
    var_7 = wp::load(var_5);
    var_6 = wp::int32(var_7);
    // if is_global:                                                                          <L 29>
    if (var_is_global) {
        // if torques:                                                                        <L 30>
        if (var_torques) {
            // global_torque_w[ei, bi] = torques[tid_env, tid_body]                           <L 31>
            var_8 = wp::address(var_torques, var_0, var_1);
            var_9 = wp::load(var_8);
            // wp::array_store(var_global_torque_w, var_3, var_6, var_9);
        }
        // if forces:                                                                         <L 32>
        if (var_forces) {
            // if positions:                                                                  <L 33>
            if (var_positions) {
                // global_force_w[ei, bi] = forces[tid_env, tid_body]                         <L 34>
                var_10 = wp::address(var_forces, var_0, var_1);
                var_11 = wp::load(var_10);
                // wp::array_store(var_global_force_w, var_3, var_6, var_11);
                // if torques:                                                                <L 35>
                if (var_torques) {
                    // global_torque_w[ei, bi] = global_torque_w[ei, bi] + wp.cross(          <L 36>
                    var_12 = wp::address(var_global_torque_w, var_3, var_6);
                    // positions[tid_env, tid_body], forces[tid_env, tid_body]                <L 37>
                    var_13 = wp::address(var_positions, var_0, var_1);
                    var_14 = wp::address(var_forces, var_0, var_1);
                    var_16 = wp::load(var_13);
                    var_17 = wp::load(var_14);
                    var_15 = wp::cross(var_16, var_17);
                    var_19 = wp::load(var_12);
                    var_18 = wp::add(var_19, var_15);
                    // global_torque_w[ei, bi] = global_torque_w[ei, bi] + wp.cross(          <L 36>
                    // wp::array_store(var_global_torque_w, var_3, var_6, var_18);
                }
                if (!var_torques) {
                    // global_torque_w[ei, bi] = wp.cross(positions[tid_env, tid_body], forces[tid_env, tid_body])       <L 40>
                    var_20 = wp::address(var_positions, var_0, var_1);
                    var_21 = wp::address(var_forces, var_0, var_1);
                    var_23 = wp::load(var_20);
                    var_24 = wp::load(var_21);
                    var_22 = wp::cross(var_23, var_24);
                    // wp::array_store(var_global_torque_w, var_3, var_6, var_22);
                }
            }
            if (!var_positions) {
                // global_force_at_com_w[ei, bi] = forces[tid_env, tid_body]                  <L 42>
                var_25 = wp::address(var_forces, var_0, var_1);
                var_26 = wp::load(var_25);
                // wp::array_store(var_global_force_at_com_w, var_3, var_6, var_26);
            }
        }
    }
    if (!var_is_global) {
        // if torques:                                                                        <L 44>
        if (var_torques) {
            // local_torque_b[ei, bi] = torques[tid_env, tid_body]                            <L 45>
            var_27 = wp::address(var_torques, var_0, var_1);
            var_28 = wp::load(var_27);
            // wp::array_store(var_local_torque_b, var_3, var_6, var_28);
        }
        // if forces:                                                                         <L 46>
        if (var_forces) {
            // local_force_b[ei, bi] = forces[tid_env, tid_body]                              <L 47>
            var_29 = wp::address(var_forces, var_0, var_1);
            var_30 = wp::load(var_29);
            // wp::array_store(var_local_force_b, var_3, var_6, var_30);
            // if positions:                                                                  <L 48>
            if (var_positions) {
                // if torques:                                                                <L 49>
                if (var_torques) {
                    // local_torque_b[ei, bi] = local_torque_b[ei, bi] + wp.cross(            <L 50>
                    var_31 = wp::address(var_local_torque_b, var_3, var_6);
                    // positions[tid_env, tid_body], forces[tid_env, tid_body]                <L 51>
                    var_32 = wp::address(var_positions, var_0, var_1);
                    var_33 = wp::address(var_forces, var_0, var_1);
                    var_35 = wp::load(var_32);
                    var_36 = wp::load(var_33);
                    var_34 = wp::cross(var_35, var_36);
                    var_38 = wp::load(var_31);
                    var_37 = wp::add(var_38, var_34);
                    // local_torque_b[ei, bi] = local_torque_b[ei, bi] + wp.cross(            <L 50>
                    // wp::array_store(var_local_torque_b, var_3, var_6, var_37);
                }
                if (!var_torques) {
                    // local_torque_b[ei, bi] = wp.cross(positions[tid_env, tid_body], forces[tid_env, tid_body])       <L 54>
                    var_39 = wp::address(var_positions, var_0, var_1);
                    var_40 = wp::address(var_forces, var_0, var_1);
                    var_42 = wp::load(var_39);
                    var_43 = wp::load(var_40);
                    var_41 = wp::cross(var_42, var_43);
                    // wp::array_store(var_local_torque_b, var_3, var_6, var_41);
                }
            }
        }
    }
    //---------
    // reverse
    if (!var_is_global) {
        if (var_forces) {
            if (var_positions) {
                if (!var_torques) {
                    wp::adj_array_store(var_local_torque_b, var_3, var_6, var_41, adj_local_torque_b, adj_3, adj_6, adj_41);
                    wp::adj_cross(var_42, var_43, adj_39, adj_40, adj_41);
                    wp::adj_address(var_forces, var_0, var_1, adj_forces, adj_0, adj_1, adj_40);
                    wp::adj_address(var_positions, var_0, var_1, adj_positions, adj_0, adj_1, adj_39);
                    // adj: local_torque_b[ei, bi] = wp.cross(positions[tid_env, tid_body], forces[tid_env, tid_body])  <L 54>
                }
                if (var_torques) {
                    wp::adj_array_store(var_local_torque_b, var_3, var_6, var_37, adj_local_torque_b, adj_3, adj_6, adj_37);
                    // adj: local_torque_b[ei, bi] = local_torque_b[ei, bi] + wp.cross(       <L 50>
                    wp::adj_add(var_38, var_34, adj_31, adj_34, adj_37);
                    wp::adj_cross(var_35, var_36, adj_32, adj_33, adj_34);
                    wp::adj_address(var_forces, var_0, var_1, adj_forces, adj_0, adj_1, adj_33);
                    wp::adj_address(var_positions, var_0, var_1, adj_positions, adj_0, adj_1, adj_32);
                    // adj: positions[tid_env, tid_body], forces[tid_env, tid_body]           <L 51>
                    wp::adj_address(var_local_torque_b, var_3, var_6, adj_local_torque_b, adj_3, adj_6, adj_31);
                    // adj: local_torque_b[ei, bi] = local_torque_b[ei, bi] + wp.cross(       <L 50>
                }
                // adj: if torques:                                                           <L 49>
            }
            // adj: if positions:                                                             <L 48>
            wp::adj_array_store(var_local_force_b, var_3, var_6, var_30, adj_local_force_b, adj_3, adj_6, adj_29);
            wp::adj_address(var_forces, var_0, var_1, adj_forces, adj_0, adj_1, adj_29);
            // adj: local_force_b[ei, bi] = forces[tid_env, tid_body]                         <L 47>
        }
        // adj: if forces:                                                                    <L 46>
        if (var_torques) {
            wp::adj_array_store(var_local_torque_b, var_3, var_6, var_28, adj_local_torque_b, adj_3, adj_6, adj_27);
            wp::adj_address(var_torques, var_0, var_1, adj_torques, adj_0, adj_1, adj_27);
            // adj: local_torque_b[ei, bi] = torques[tid_env, tid_body]                       <L 45>
        }
        // adj: if torques:                                                                   <L 44>
    }
    if (var_is_global) {
        if (var_forces) {
            if (!var_positions) {
                wp::adj_array_store(var_global_force_at_com_w, var_3, var_6, var_26, adj_global_force_at_com_w, adj_3, adj_6, adj_25);
                wp::adj_address(var_forces, var_0, var_1, adj_forces, adj_0, adj_1, adj_25);
                // adj: global_force_at_com_w[ei, bi] = forces[tid_env, tid_body]             <L 42>
            }
            if (var_positions) {
                if (!var_torques) {
                    wp::adj_array_store(var_global_torque_w, var_3, var_6, var_22, adj_global_torque_w, adj_3, adj_6, adj_22);
                    wp::adj_cross(var_23, var_24, adj_20, adj_21, adj_22);
                    wp::adj_address(var_forces, var_0, var_1, adj_forces, adj_0, adj_1, adj_21);
                    wp::adj_address(var_positions, var_0, var_1, adj_positions, adj_0, adj_1, adj_20);
                    // adj: global_torque_w[ei, bi] = wp.cross(positions[tid_env, tid_body], forces[tid_env, tid_body])  <L 40>
                }
                if (var_torques) {
                    wp::adj_array_store(var_global_torque_w, var_3, var_6, var_18, adj_global_torque_w, adj_3, adj_6, adj_18);
                    // adj: global_torque_w[ei, bi] = global_torque_w[ei, bi] + wp.cross(     <L 36>
                    wp::adj_add(var_19, var_15, adj_12, adj_15, adj_18);
                    wp::adj_cross(var_16, var_17, adj_13, adj_14, adj_15);
                    wp::adj_address(var_forces, var_0, var_1, adj_forces, adj_0, adj_1, adj_14);
                    wp::adj_address(var_positions, var_0, var_1, adj_positions, adj_0, adj_1, adj_13);
                    // adj: positions[tid_env, tid_body], forces[tid_env, tid_body]           <L 37>
                    wp::adj_address(var_global_torque_w, var_3, var_6, adj_global_torque_w, adj_3, adj_6, adj_12);
                    // adj: global_torque_w[ei, bi] = global_torque_w[ei, bi] + wp.cross(     <L 36>
                }
                // adj: if torques:                                                           <L 35>
                wp::adj_array_store(var_global_force_w, var_3, var_6, var_11, adj_global_force_w, adj_3, adj_6, adj_10);
                wp::adj_address(var_forces, var_0, var_1, adj_forces, adj_0, adj_1, adj_10);
                // adj: global_force_w[ei, bi] = forces[tid_env, tid_body]                    <L 34>
            }
            // adj: if positions:                                                             <L 33>
        }
        // adj: if forces:                                                                    <L 32>
        if (var_torques) {
            wp::adj_array_store(var_global_torque_w, var_3, var_6, var_9, adj_global_torque_w, adj_3, adj_6, adj_8);
            wp::adj_address(var_torques, var_0, var_1, adj_torques, adj_0, adj_1, adj_8);
            // adj: global_torque_w[ei, bi] = torques[tid_env, tid_body]                      <L 31>
        }
        // adj: if torques:                                                                   <L 30>
    }
    // adj: if is_global:                                                                     <L 29>
    wp::adj_address(var_body_ids, var_1, adj_body_ids, adj_1, adj_5);
    // adj: bi = wp.int32(body_ids[tid_body])                                                 <L 27>
    wp::adj_address(var_env_ids, var_0, adj_env_ids, adj_0, adj_2);
    // adj: ei = wp.int32(env_ids[tid_env])                                                   <L 26>
    // adj: tid_env, tid_body = wp.tid()                                                      <L 25>
    // adj: def set_forces_to_dual_buffers_index(                                             <L 1>
    return;
}



extern "C" {

// Python CPU entry points
WP_API void set_forces_to_dual_buffers_index_0184dbed_cpu_forward(
    wp::launch_bounds_t<2> *dim,
    wp_args_set_forces_to_dual_buffers_index_0184dbed *_wp_args)
{
    wp::tile_shared_storage_t tile_mem;
#if defined(WP_ENABLE_TILES_IN_STACK_MEMORY)
    wp::shared_tile_storage = &tile_mem;
#endif

    for (size_t task_index = 0; task_index < dim->size; ++task_index)
    {
        set_forces_to_dual_buffers_index_0184dbed_cpu_kernel_forward(*dim, task_index, _wp_args);
    }
}

} // extern C



extern "C" {

WP_API void set_forces_to_dual_buffers_index_0184dbed_cpu_backward(
    wp::launch_bounds_t<2> *dim,
    wp_args_set_forces_to_dual_buffers_index_0184dbed *_wp_args,
    wp_args_set_forces_to_dual_buffers_index_0184dbed *_wp_adj_args)
{
    wp::tile_shared_storage_t tile_mem;
#if defined(WP_ENABLE_TILES_IN_STACK_MEMORY)
    wp::shared_tile_storage = &tile_mem;
#endif

    for (size_t task_index = 0; task_index < dim->size; ++task_index)
    {
        set_forces_to_dual_buffers_index_0184dbed_cpu_kernel_backward(*dim, task_index, _wp_args, _wp_adj_args);
    }
}

} // extern C

struct wp_args_gather_subtract_2d_047d6694 {
    wp::array_t<wp::float32> a;
    wp::array_t<wp::int32> env_ids;
    wp::array_t<wp::int64> item_ids;
    wp::array_t<wp::float32> b;
    wp::array_t<wp::float32> out;
};


void gather_subtract_2d_047d6694_cpu_kernel_forward(
    wp::launch_bounds_t<2> dim,
    size_t task_index,
    wp_args_gather_subtract_2d_047d6694 *_wp_args)
{
    //---------
    // argument vars
    wp::array_t<wp::float32> var_a = _wp_args->a;
    wp::array_t<wp::int32> var_env_ids = _wp_args->env_ids;
    wp::array_t<wp::int64> var_item_ids = _wp_args->item_ids;
    wp::array_t<wp::float32> var_b = _wp_args->b;
    wp::array_t<wp::float32> var_out = _wp_args->out;
    //---------
    // primal vars
    wp::int32 var_0;
    wp::int32 var_1;
    wp::int32* var_2;
    wp::int32 var_3;
    wp::int32 var_4;
    wp::int64* var_5;
    wp::int32 var_6;
    wp::int64 var_7;
    wp::float32* var_8;
    wp::float32* var_9;
    wp::float32 var_10;
    wp::float32 var_11;
    wp::float32 var_12;
    //---------
    // forward
    // def gather_subtract_2d(                                                                <L 1>
    // i, j = wp.tid()                                                                        <L 17>
    builtin_tid2d(var_0, var_1);
    // out[i, j] = a[wp.int32(env_ids[i]), wp.int32(item_ids[j])] - b[i, j]                   <L 18>
    var_2 = wp::address(var_env_ids, var_0);
    var_4 = wp::load(var_2);
    var_3 = wp::int32(var_4);
    var_5 = wp::address(var_item_ids, var_1);
    var_7 = wp::load(var_5);
    var_6 = wp::int32(var_7);
    var_8 = wp::address(var_a, var_3, var_6);
    var_9 = wp::address(var_b, var_0, var_1);
    var_11 = wp::load(var_8);
    var_12 = wp::load(var_9);
    var_10 = wp::sub(var_11, var_12);
    wp::array_store(var_out, var_0, var_1, var_10);
}



void gather_subtract_2d_047d6694_cpu_kernel_backward(
    wp::launch_bounds_t<2> dim,
    size_t task_index,
    wp_args_gather_subtract_2d_047d6694 *_wp_args,
    wp_args_gather_subtract_2d_047d6694 *_wp_adj_args)
{
    //---------
    // argument vars
    wp::array_t<wp::float32> var_a = _wp_args->a;
    wp::array_t<wp::int32> var_env_ids = _wp_args->env_ids;
    wp::array_t<wp::int64> var_item_ids = _wp_args->item_ids;
    wp::array_t<wp::float32> var_b = _wp_args->b;
    wp::array_t<wp::float32> var_out = _wp_args->out;
    wp::array_t<wp::float32> adj_a = _wp_adj_args->a;
    wp::array_t<wp::int32> adj_env_ids = _wp_adj_args->env_ids;
    wp::array_t<wp::int64> adj_item_ids = _wp_adj_args->item_ids;
    wp::array_t<wp::float32> adj_b = _wp_adj_args->b;
    wp::array_t<wp::float32> adj_out = _wp_adj_args->out;
    //---------
    // primal vars
    wp::int32 var_0;
    wp::int32 var_1;
    wp::int32* var_2;
    wp::int32 var_3;
    wp::int32 var_4;
    wp::int64* var_5;
    wp::int32 var_6;
    wp::int64 var_7;
    wp::float32* var_8;
    wp::float32* var_9;
    wp::float32 var_10;
    wp::float32 var_11;
    wp::float32 var_12;
    //---------
    // dual vars
    wp::int32 adj_0 = {};
    wp::int32 adj_1 = {};
    wp::int32 adj_2 = {};
    wp::int32 adj_3 = {};
    wp::int32 adj_4 = {};
    wp::int64 adj_5 = {};
    wp::int32 adj_6 = {};
    wp::int64 adj_7 = {};
    wp::float32 adj_8 = {};
    wp::float32 adj_9 = {};
    wp::float32 adj_10 = {};
    wp::float32 adj_11 = {};
    wp::float32 adj_12 = {};
    //---------
    // forward
    // def gather_subtract_2d(                                                                <L 1>
    // i, j = wp.tid()                                                                        <L 17>
    builtin_tid2d(var_0, var_1);
    // out[i, j] = a[wp.int32(env_ids[i]), wp.int32(item_ids[j])] - b[i, j]                   <L 18>
    var_2 = wp::address(var_env_ids, var_0);
    var_4 = wp::load(var_2);
    var_3 = wp::int32(var_4);
    var_5 = wp::address(var_item_ids, var_1);
    var_7 = wp::load(var_5);
    var_6 = wp::int32(var_7);
    var_8 = wp::address(var_a, var_3, var_6);
    var_9 = wp::address(var_b, var_0, var_1);
    var_11 = wp::load(var_8);
    var_12 = wp::load(var_9);
    var_10 = wp::sub(var_11, var_12);
    // wp::array_store(var_out, var_0, var_1, var_10);
    //---------
    // reverse
    wp::adj_array_store(var_out, var_0, var_1, var_10, adj_out, adj_0, adj_1, adj_10);
    wp::adj_sub(var_11, var_12, adj_8, adj_9, adj_10);
    wp::adj_address(var_b, var_0, var_1, adj_b, adj_0, adj_1, adj_9);
    wp::adj_address(var_a, var_3, var_6, adj_a, adj_3, adj_6, adj_8);
    wp::adj_address(var_item_ids, var_1, adj_item_ids, adj_1, adj_5);
    wp::adj_address(var_env_ids, var_0, adj_env_ids, adj_0, adj_2);
    // adj: out[i, j] = a[wp.int32(env_ids[i]), wp.int32(item_ids[j])] - b[i, j]              <L 18>
    // adj: i, j = wp.tid()                                                                   <L 17>
    // adj: def gather_subtract_2d(                                                           <L 1>
    return;
}



extern "C" {

// Python CPU entry points
WP_API void gather_subtract_2d_047d6694_cpu_forward(
    wp::launch_bounds_t<2> *dim,
    wp_args_gather_subtract_2d_047d6694 *_wp_args)
{
    wp::tile_shared_storage_t tile_mem;
#if defined(WP_ENABLE_TILES_IN_STACK_MEMORY)
    wp::shared_tile_storage = &tile_mem;
#endif

    for (size_t task_index = 0; task_index < dim->size; ++task_index)
    {
        gather_subtract_2d_047d6694_cpu_kernel_forward(*dim, task_index, _wp_args);
    }
}

} // extern C



extern "C" {

WP_API void gather_subtract_2d_047d6694_cpu_backward(
    wp::launch_bounds_t<2> *dim,
    wp_args_gather_subtract_2d_047d6694 *_wp_args,
    wp_args_gather_subtract_2d_047d6694 *_wp_adj_args)
{
    wp::tile_shared_storage_t tile_mem;
#if defined(WP_ENABLE_TILES_IN_STACK_MEMORY)
    wp::shared_tile_storage = &tile_mem;
#endif

    for (size_t task_index = 0; task_index < dim->size; ++task_index)
    {
        gather_subtract_2d_047d6694_cpu_kernel_backward(*dim, task_index, _wp_args, _wp_adj_args);
    }
}

} // extern C

struct wp_args_gather_subtract_2d_059b77eb {
    wp::array_t<wp::float32> a;
    wp::array_t<wp::int64> env_ids;
    wp::array_t<wp::int64> item_ids;
    wp::array_t<wp::float32> b;
    wp::array_t<wp::float32> out;
};


void gather_subtract_2d_059b77eb_cpu_kernel_forward(
    wp::launch_bounds_t<2> dim,
    size_t task_index,
    wp_args_gather_subtract_2d_059b77eb *_wp_args)
{
    //---------
    // argument vars
    wp::array_t<wp::float32> var_a = _wp_args->a;
    wp::array_t<wp::int64> var_env_ids = _wp_args->env_ids;
    wp::array_t<wp::int64> var_item_ids = _wp_args->item_ids;
    wp::array_t<wp::float32> var_b = _wp_args->b;
    wp::array_t<wp::float32> var_out = _wp_args->out;
    //---------
    // primal vars
    wp::int32 var_0;
    wp::int32 var_1;
    wp::int64* var_2;
    wp::int32 var_3;
    wp::int64 var_4;
    wp::int64* var_5;
    wp::int32 var_6;
    wp::int64 var_7;
    wp::float32* var_8;
    wp::float32* var_9;
    wp::float32 var_10;
    wp::float32 var_11;
    wp::float32 var_12;
    //---------
    // forward
    // def gather_subtract_2d(                                                                <L 1>
    // i, j = wp.tid()                                                                        <L 17>
    builtin_tid2d(var_0, var_1);
    // out[i, j] = a[wp.int32(env_ids[i]), wp.int32(item_ids[j])] - b[i, j]                   <L 18>
    var_2 = wp::address(var_env_ids, var_0);
    var_4 = wp::load(var_2);
    var_3 = wp::int32(var_4);
    var_5 = wp::address(var_item_ids, var_1);
    var_7 = wp::load(var_5);
    var_6 = wp::int32(var_7);
    var_8 = wp::address(var_a, var_3, var_6);
    var_9 = wp::address(var_b, var_0, var_1);
    var_11 = wp::load(var_8);
    var_12 = wp::load(var_9);
    var_10 = wp::sub(var_11, var_12);
    wp::array_store(var_out, var_0, var_1, var_10);
}



void gather_subtract_2d_059b77eb_cpu_kernel_backward(
    wp::launch_bounds_t<2> dim,
    size_t task_index,
    wp_args_gather_subtract_2d_059b77eb *_wp_args,
    wp_args_gather_subtract_2d_059b77eb *_wp_adj_args)
{
    //---------
    // argument vars
    wp::array_t<wp::float32> var_a = _wp_args->a;
    wp::array_t<wp::int64> var_env_ids = _wp_args->env_ids;
    wp::array_t<wp::int64> var_item_ids = _wp_args->item_ids;
    wp::array_t<wp::float32> var_b = _wp_args->b;
    wp::array_t<wp::float32> var_out = _wp_args->out;
    wp::array_t<wp::float32> adj_a = _wp_adj_args->a;
    wp::array_t<wp::int64> adj_env_ids = _wp_adj_args->env_ids;
    wp::array_t<wp::int64> adj_item_ids = _wp_adj_args->item_ids;
    wp::array_t<wp::float32> adj_b = _wp_adj_args->b;
    wp::array_t<wp::float32> adj_out = _wp_adj_args->out;
    //---------
    // primal vars
    wp::int32 var_0;
    wp::int32 var_1;
    wp::int64* var_2;
    wp::int32 var_3;
    wp::int64 var_4;
    wp::int64* var_5;
    wp::int32 var_6;
    wp::int64 var_7;
    wp::float32* var_8;
    wp::float32* var_9;
    wp::float32 var_10;
    wp::float32 var_11;
    wp::float32 var_12;
    //---------
    // dual vars
    wp::int32 adj_0 = {};
    wp::int32 adj_1 = {};
    wp::int64 adj_2 = {};
    wp::int32 adj_3 = {};
    wp::int64 adj_4 = {};
    wp::int64 adj_5 = {};
    wp::int32 adj_6 = {};
    wp::int64 adj_7 = {};
    wp::float32 adj_8 = {};
    wp::float32 adj_9 = {};
    wp::float32 adj_10 = {};
    wp::float32 adj_11 = {};
    wp::float32 adj_12 = {};
    //---------
    // forward
    // def gather_subtract_2d(                                                                <L 1>
    // i, j = wp.tid()                                                                        <L 17>
    builtin_tid2d(var_0, var_1);
    // out[i, j] = a[wp.int32(env_ids[i]), wp.int32(item_ids[j])] - b[i, j]                   <L 18>
    var_2 = wp::address(var_env_ids, var_0);
    var_4 = wp::load(var_2);
    var_3 = wp::int32(var_4);
    var_5 = wp::address(var_item_ids, var_1);
    var_7 = wp::load(var_5);
    var_6 = wp::int32(var_7);
    var_8 = wp::address(var_a, var_3, var_6);
    var_9 = wp::address(var_b, var_0, var_1);
    var_11 = wp::load(var_8);
    var_12 = wp::load(var_9);
    var_10 = wp::sub(var_11, var_12);
    // wp::array_store(var_out, var_0, var_1, var_10);
    //---------
    // reverse
    wp::adj_array_store(var_out, var_0, var_1, var_10, adj_out, adj_0, adj_1, adj_10);
    wp::adj_sub(var_11, var_12, adj_8, adj_9, adj_10);
    wp::adj_address(var_b, var_0, var_1, adj_b, adj_0, adj_1, adj_9);
    wp::adj_address(var_a, var_3, var_6, adj_a, adj_3, adj_6, adj_8);
    wp::adj_address(var_item_ids, var_1, adj_item_ids, adj_1, adj_5);
    wp::adj_address(var_env_ids, var_0, adj_env_ids, adj_0, adj_2);
    // adj: out[i, j] = a[wp.int32(env_ids[i]), wp.int32(item_ids[j])] - b[i, j]              <L 18>
    // adj: i, j = wp.tid()                                                                   <L 17>
    // adj: def gather_subtract_2d(                                                           <L 1>
    return;
}



extern "C" {

// Python CPU entry points
WP_API void gather_subtract_2d_059b77eb_cpu_forward(
    wp::launch_bounds_t<2> *dim,
    wp_args_gather_subtract_2d_059b77eb *_wp_args)
{
    wp::tile_shared_storage_t tile_mem;
#if defined(WP_ENABLE_TILES_IN_STACK_MEMORY)
    wp::shared_tile_storage = &tile_mem;
#endif

    for (size_t task_index = 0; task_index < dim->size; ++task_index)
    {
        gather_subtract_2d_059b77eb_cpu_kernel_forward(*dim, task_index, _wp_args);
    }
}

} // extern C



extern "C" {

WP_API void gather_subtract_2d_059b77eb_cpu_backward(
    wp::launch_bounds_t<2> *dim,
    wp_args_gather_subtract_2d_059b77eb *_wp_args,
    wp_args_gather_subtract_2d_059b77eb *_wp_adj_args)
{
    wp::tile_shared_storage_t tile_mem;
#if defined(WP_ENABLE_TILES_IN_STACK_MEMORY)
    wp::shared_tile_storage = &tile_mem;
#endif

    for (size_t task_index = 0; task_index < dim->size; ++task_index)
    {
        gather_subtract_2d_059b77eb_cpu_kernel_backward(*dim, task_index, _wp_args, _wp_adj_args);
    }
}

} // extern C

struct wp_args_add_forces_to_dual_buffers_index_1a379c01 {
    wp::array_t<wp::int32> env_ids;
    wp::array_t<wp::int32> body_ids;
    wp::array_t<wp::vec_t<3, wp::float32>> forces;
    wp::array_t<wp::vec_t<3, wp::float32>> torques;
    wp::array_t<wp::vec_t<3, wp::float32>> positions;
    wp::array_t<wp::vec_t<3, wp::float32>> global_force_w;
    wp::array_t<wp::vec_t<3, wp::float32>> global_torque_w;
    wp::array_t<wp::vec_t<3, wp::float32>> global_force_at_com_w;
    wp::array_t<wp::vec_t<3, wp::float32>> local_force_b;
    wp::array_t<wp::vec_t<3, wp::float32>> local_torque_b;
    bool is_global;
};


void add_forces_to_dual_buffers_index_1a379c01_cpu_kernel_forward(
    wp::launch_bounds_t<2> dim,
    size_t task_index,
    wp_args_add_forces_to_dual_buffers_index_1a379c01 *_wp_args)
{
    //---------
    // argument vars
    wp::array_t<wp::int32> var_env_ids = _wp_args->env_ids;
    wp::array_t<wp::int32> var_body_ids = _wp_args->body_ids;
    wp::array_t<wp::vec_t<3, wp::float32>> var_forces = _wp_args->forces;
    wp::array_t<wp::vec_t<3, wp::float32>> var_torques = _wp_args->torques;
    wp::array_t<wp::vec_t<3, wp::float32>> var_positions = _wp_args->positions;
    wp::array_t<wp::vec_t<3, wp::float32>> var_global_force_w = _wp_args->global_force_w;
    wp::array_t<wp::vec_t<3, wp::float32>> var_global_torque_w = _wp_args->global_torque_w;
    wp::array_t<wp::vec_t<3, wp::float32>> var_global_force_at_com_w = _wp_args->global_force_at_com_w;
    wp::array_t<wp::vec_t<3, wp::float32>> var_local_force_b = _wp_args->local_force_b;
    wp::array_t<wp::vec_t<3, wp::float32>> var_local_torque_b = _wp_args->local_torque_b;
    bool var_is_global = _wp_args->is_global;
    //---------
    // primal vars
    wp::int32 var_0;
    wp::int32 var_1;
    wp::int32* var_2;
    wp::int32 var_3;
    wp::int32 var_4;
    wp::int32* var_5;
    wp::int32 var_6;
    wp::int32 var_7;
    wp::vec_t<3, wp::float32>* var_8;
    wp::vec_t<3, wp::float32>* var_9;
    wp::vec_t<3, wp::float32> var_10;
    wp::vec_t<3, wp::float32> var_11;
    wp::vec_t<3, wp::float32> var_12;
    wp::vec_t<3, wp::float32>* var_13;
    wp::vec_t<3, wp::float32>* var_14;
    wp::vec_t<3, wp::float32>* var_15;
    wp::vec_t<3, wp::float32> var_16;
    wp::vec_t<3, wp::float32> var_17;
    wp::vec_t<3, wp::float32> var_18;
    wp::vec_t<3, wp::float32> var_19;
    wp::vec_t<3, wp::float32> var_20;
    wp::vec_t<3, wp::float32>* var_21;
    wp::vec_t<3, wp::float32>* var_22;
    wp::vec_t<3, wp::float32> var_23;
    wp::vec_t<3, wp::float32> var_24;
    wp::vec_t<3, wp::float32> var_25;
    wp::vec_t<3, wp::float32>* var_26;
    wp::vec_t<3, wp::float32>* var_27;
    wp::vec_t<3, wp::float32> var_28;
    wp::vec_t<3, wp::float32> var_29;
    wp::vec_t<3, wp::float32> var_30;
    wp::vec_t<3, wp::float32>* var_31;
    wp::vec_t<3, wp::float32>* var_32;
    wp::vec_t<3, wp::float32> var_33;
    wp::vec_t<3, wp::float32> var_34;
    wp::vec_t<3, wp::float32> var_35;
    wp::vec_t<3, wp::float32>* var_36;
    wp::vec_t<3, wp::float32>* var_37;
    wp::vec_t<3, wp::float32>* var_38;
    wp::vec_t<3, wp::float32> var_39;
    wp::vec_t<3, wp::float32> var_40;
    wp::vec_t<3, wp::float32> var_41;
    wp::vec_t<3, wp::float32> var_42;
    wp::vec_t<3, wp::float32> var_43;
    wp::vec_t<3, wp::float32>* var_44;
    wp::vec_t<3, wp::float32>* var_45;
    wp::vec_t<3, wp::float32> var_46;
    wp::vec_t<3, wp::float32> var_47;
    wp::vec_t<3, wp::float32> var_48;
    //---------
    // forward
    // def add_forces_to_dual_buffers_index(                                                  <L 1>
    // tid_env, tid_body = wp.tid()                                                           <L 19>
    builtin_tid2d(var_0, var_1);
    // ei = wp.int32(env_ids[tid_env])                                                        <L 20>
    var_2 = wp::address(var_env_ids, var_0);
    var_4 = wp::load(var_2);
    var_3 = wp::int32(var_4);
    // bi = wp.int32(body_ids[tid_body])                                                      <L 21>
    var_5 = wp::address(var_body_ids, var_1);
    var_7 = wp::load(var_5);
    var_6 = wp::int32(var_7);
    // if is_global:                                                                          <L 23>
    if (var_is_global) {
        // if forces:                                                                         <L 24>
        if (var_forces) {
            // if positions:                                                                  <L 25>
            if (var_positions) {
                // global_force_w[ei, bi] = global_force_w[ei, bi] + forces[tid_env, tid_body]       <L 26>
                var_8 = wp::address(var_global_force_w, var_3, var_6);
                var_9 = wp::address(var_forces, var_0, var_1);
                var_11 = wp::load(var_8);
                var_12 = wp::load(var_9);
                var_10 = wp::add(var_11, var_12);
                wp::array_store(var_global_force_w, var_3, var_6, var_10);
                // global_torque_w[ei, bi] = global_torque_w[ei, bi] + wp.cross(              <L 27>
                var_13 = wp::address(var_global_torque_w, var_3, var_6);
                // positions[tid_env, tid_body], forces[tid_env, tid_body]                    <L 28>
                var_14 = wp::address(var_positions, var_0, var_1);
                var_15 = wp::address(var_forces, var_0, var_1);
                var_17 = wp::load(var_14);
                var_18 = wp::load(var_15);
                var_16 = wp::cross(var_17, var_18);
                var_20 = wp::load(var_13);
                var_19 = wp::add(var_20, var_16);
                // global_torque_w[ei, bi] = global_torque_w[ei, bi] + wp.cross(              <L 27>
                wp::array_store(var_global_torque_w, var_3, var_6, var_19);
            }
            if (!var_positions) {
                // global_force_at_com_w[ei, bi] = global_force_at_com_w[ei, bi] + forces[tid_env, tid_body]       <L 31>
                var_21 = wp::address(var_global_force_at_com_w, var_3, var_6);
                var_22 = wp::address(var_forces, var_0, var_1);
                var_24 = wp::load(var_21);
                var_25 = wp::load(var_22);
                var_23 = wp::add(var_24, var_25);
                wp::array_store(var_global_force_at_com_w, var_3, var_6, var_23);
            }
        }
        // if torques:                                                                        <L 32>
        if (var_torques) {
            // global_torque_w[ei, bi] = global_torque_w[ei, bi] + torques[tid_env, tid_body]       <L 33>
            var_26 = wp::address(var_global_torque_w, var_3, var_6);
            var_27 = wp::address(var_torques, var_0, var_1);
            var_29 = wp::load(var_26);
            var_30 = wp::load(var_27);
            var_28 = wp::add(var_29, var_30);
            wp::array_store(var_global_torque_w, var_3, var_6, var_28);
        }
    }
    if (!var_is_global) {
        // if forces:                                                                         <L 35>
        if (var_forces) {
            // local_force_b[ei, bi] = local_force_b[ei, bi] + forces[tid_env, tid_body]       <L 36>
            var_31 = wp::address(var_local_force_b, var_3, var_6);
            var_32 = wp::address(var_forces, var_0, var_1);
            var_34 = wp::load(var_31);
            var_35 = wp::load(var_32);
            var_33 = wp::add(var_34, var_35);
            wp::array_store(var_local_force_b, var_3, var_6, var_33);
            // if positions:                                                                  <L 37>
            if (var_positions) {
                // local_torque_b[ei, bi] = local_torque_b[ei, bi] + wp.cross(                <L 38>
                var_36 = wp::address(var_local_torque_b, var_3, var_6);
                // positions[tid_env, tid_body], forces[tid_env, tid_body]                    <L 39>
                var_37 = wp::address(var_positions, var_0, var_1);
                var_38 = wp::address(var_forces, var_0, var_1);
                var_40 = wp::load(var_37);
                var_41 = wp::load(var_38);
                var_39 = wp::cross(var_40, var_41);
                var_43 = wp::load(var_36);
                var_42 = wp::add(var_43, var_39);
                // local_torque_b[ei, bi] = local_torque_b[ei, bi] + wp.cross(                <L 38>
                wp::array_store(var_local_torque_b, var_3, var_6, var_42);
            }
        }
        // if torques:                                                                        <L 41>
        if (var_torques) {
            // local_torque_b[ei, bi] = local_torque_b[ei, bi] + torques[tid_env, tid_body]       <L 42>
            var_44 = wp::address(var_local_torque_b, var_3, var_6);
            var_45 = wp::address(var_torques, var_0, var_1);
            var_47 = wp::load(var_44);
            var_48 = wp::load(var_45);
            var_46 = wp::add(var_47, var_48);
            wp::array_store(var_local_torque_b, var_3, var_6, var_46);
        }
    }
}



void add_forces_to_dual_buffers_index_1a379c01_cpu_kernel_backward(
    wp::launch_bounds_t<2> dim,
    size_t task_index,
    wp_args_add_forces_to_dual_buffers_index_1a379c01 *_wp_args,
    wp_args_add_forces_to_dual_buffers_index_1a379c01 *_wp_adj_args)
{
    //---------
    // argument vars
    wp::array_t<wp::int32> var_env_ids = _wp_args->env_ids;
    wp::array_t<wp::int32> var_body_ids = _wp_args->body_ids;
    wp::array_t<wp::vec_t<3, wp::float32>> var_forces = _wp_args->forces;
    wp::array_t<wp::vec_t<3, wp::float32>> var_torques = _wp_args->torques;
    wp::array_t<wp::vec_t<3, wp::float32>> var_positions = _wp_args->positions;
    wp::array_t<wp::vec_t<3, wp::float32>> var_global_force_w = _wp_args->global_force_w;
    wp::array_t<wp::vec_t<3, wp::float32>> var_global_torque_w = _wp_args->global_torque_w;
    wp::array_t<wp::vec_t<3, wp::float32>> var_global_force_at_com_w = _wp_args->global_force_at_com_w;
    wp::array_t<wp::vec_t<3, wp::float32>> var_local_force_b = _wp_args->local_force_b;
    wp::array_t<wp::vec_t<3, wp::float32>> var_local_torque_b = _wp_args->local_torque_b;
    bool var_is_global = _wp_args->is_global;
    wp::array_t<wp::int32> adj_env_ids = _wp_adj_args->env_ids;
    wp::array_t<wp::int32> adj_body_ids = _wp_adj_args->body_ids;
    wp::array_t<wp::vec_t<3, wp::float32>> adj_forces = _wp_adj_args->forces;
    wp::array_t<wp::vec_t<3, wp::float32>> adj_torques = _wp_adj_args->torques;
    wp::array_t<wp::vec_t<3, wp::float32>> adj_positions = _wp_adj_args->positions;
    wp::array_t<wp::vec_t<3, wp::float32>> adj_global_force_w = _wp_adj_args->global_force_w;
    wp::array_t<wp::vec_t<3, wp::float32>> adj_global_torque_w = _wp_adj_args->global_torque_w;
    wp::array_t<wp::vec_t<3, wp::float32>> adj_global_force_at_com_w = _wp_adj_args->global_force_at_com_w;
    wp::array_t<wp::vec_t<3, wp::float32>> adj_local_force_b = _wp_adj_args->local_force_b;
    wp::array_t<wp::vec_t<3, wp::float32>> adj_local_torque_b = _wp_adj_args->local_torque_b;
    bool adj_is_global = _wp_adj_args->is_global;
    //---------
    // primal vars
    wp::int32 var_0;
    wp::int32 var_1;
    wp::int32* var_2;
    wp::int32 var_3;
    wp::int32 var_4;
    wp::int32* var_5;
    wp::int32 var_6;
    wp::int32 var_7;
    wp::vec_t<3, wp::float32>* var_8;
    wp::vec_t<3, wp::float32>* var_9;
    wp::vec_t<3, wp::float32> var_10;
    wp::vec_t<3, wp::float32> var_11;
    wp::vec_t<3, wp::float32> var_12;
    wp::vec_t<3, wp::float32>* var_13;
    wp::vec_t<3, wp::float32>* var_14;
    wp::vec_t<3, wp::float32>* var_15;
    wp::vec_t<3, wp::float32> var_16;
    wp::vec_t<3, wp::float32> var_17;
    wp::vec_t<3, wp::float32> var_18;
    wp::vec_t<3, wp::float32> var_19;
    wp::vec_t<3, wp::float32> var_20;
    wp::vec_t<3, wp::float32>* var_21;
    wp::vec_t<3, wp::float32>* var_22;
    wp::vec_t<3, wp::float32> var_23;
    wp::vec_t<3, wp::float32> var_24;
    wp::vec_t<3, wp::float32> var_25;
    wp::vec_t<3, wp::float32>* var_26;
    wp::vec_t<3, wp::float32>* var_27;
    wp::vec_t<3, wp::float32> var_28;
    wp::vec_t<3, wp::float32> var_29;
    wp::vec_t<3, wp::float32> var_30;
    wp::vec_t<3, wp::float32>* var_31;
    wp::vec_t<3, wp::float32>* var_32;
    wp::vec_t<3, wp::float32> var_33;
    wp::vec_t<3, wp::float32> var_34;
    wp::vec_t<3, wp::float32> var_35;
    wp::vec_t<3, wp::float32>* var_36;
    wp::vec_t<3, wp::float32>* var_37;
    wp::vec_t<3, wp::float32>* var_38;
    wp::vec_t<3, wp::float32> var_39;
    wp::vec_t<3, wp::float32> var_40;
    wp::vec_t<3, wp::float32> var_41;
    wp::vec_t<3, wp::float32> var_42;
    wp::vec_t<3, wp::float32> var_43;
    wp::vec_t<3, wp::float32>* var_44;
    wp::vec_t<3, wp::float32>* var_45;
    wp::vec_t<3, wp::float32> var_46;
    wp::vec_t<3, wp::float32> var_47;
    wp::vec_t<3, wp::float32> var_48;
    //---------
    // dual vars
    wp::int32 adj_0 = {};
    wp::int32 adj_1 = {};
    wp::int32 adj_2 = {};
    wp::int32 adj_3 = {};
    wp::int32 adj_4 = {};
    wp::int32 adj_5 = {};
    wp::int32 adj_6 = {};
    wp::int32 adj_7 = {};
    wp::vec_t<3, wp::float32> adj_8 = {};
    wp::vec_t<3, wp::float32> adj_9 = {};
    wp::vec_t<3, wp::float32> adj_10 = {};
    wp::vec_t<3, wp::float32> adj_11 = {};
    wp::vec_t<3, wp::float32> adj_12 = {};
    wp::vec_t<3, wp::float32> adj_13 = {};
    wp::vec_t<3, wp::float32> adj_14 = {};
    wp::vec_t<3, wp::float32> adj_15 = {};
    wp::vec_t<3, wp::float32> adj_16 = {};
    wp::vec_t<3, wp::float32> adj_17 = {};
    wp::vec_t<3, wp::float32> adj_18 = {};
    wp::vec_t<3, wp::float32> adj_19 = {};
    wp::vec_t<3, wp::float32> adj_20 = {};
    wp::vec_t<3, wp::float32> adj_21 = {};
    wp::vec_t<3, wp::float32> adj_22 = {};
    wp::vec_t<3, wp::float32> adj_23 = {};
    wp::vec_t<3, wp::float32> adj_24 = {};
    wp::vec_t<3, wp::float32> adj_25 = {};
    wp::vec_t<3, wp::float32> adj_26 = {};
    wp::vec_t<3, wp::float32> adj_27 = {};
    wp::vec_t<3, wp::float32> adj_28 = {};
    wp::vec_t<3, wp::float32> adj_29 = {};
    wp::vec_t<3, wp::float32> adj_30 = {};
    wp::vec_t<3, wp::float32> adj_31 = {};
    wp::vec_t<3, wp::float32> adj_32 = {};
    wp::vec_t<3, wp::float32> adj_33 = {};
    wp::vec_t<3, wp::float32> adj_34 = {};
    wp::vec_t<3, wp::float32> adj_35 = {};
    wp::vec_t<3, wp::float32> adj_36 = {};
    wp::vec_t<3, wp::float32> adj_37 = {};
    wp::vec_t<3, wp::float32> adj_38 = {};
    wp::vec_t<3, wp::float32> adj_39 = {};
    wp::vec_t<3, wp::float32> adj_40 = {};
    wp::vec_t<3, wp::float32> adj_41 = {};
    wp::vec_t<3, wp::float32> adj_42 = {};
    wp::vec_t<3, wp::float32> adj_43 = {};
    wp::vec_t<3, wp::float32> adj_44 = {};
    wp::vec_t<3, wp::float32> adj_45 = {};
    wp::vec_t<3, wp::float32> adj_46 = {};
    wp::vec_t<3, wp::float32> adj_47 = {};
    wp::vec_t<3, wp::float32> adj_48 = {};
    //---------
    // forward
    // def add_forces_to_dual_buffers_index(                                                  <L 1>
    // tid_env, tid_body = wp.tid()                                                           <L 19>
    builtin_tid2d(var_0, var_1);
    // ei = wp.int32(env_ids[tid_env])                                                        <L 20>
    var_2 = wp::address(var_env_ids, var_0);
    var_4 = wp::load(var_2);
    var_3 = wp::int32(var_4);
    // bi = wp.int32(body_ids[tid_body])                                                      <L 21>
    var_5 = wp::address(var_body_ids, var_1);
    var_7 = wp::load(var_5);
    var_6 = wp::int32(var_7);
    // if is_global:                                                                          <L 23>
    if (var_is_global) {
        // if forces:                                                                         <L 24>
        if (var_forces) {
            // if positions:                                                                  <L 25>
            if (var_positions) {
                // global_force_w[ei, bi] = global_force_w[ei, bi] + forces[tid_env, tid_body]       <L 26>
                var_8 = wp::address(var_global_force_w, var_3, var_6);
                var_9 = wp::address(var_forces, var_0, var_1);
                var_11 = wp::load(var_8);
                var_12 = wp::load(var_9);
                var_10 = wp::add(var_11, var_12);
                // wp::array_store(var_global_force_w, var_3, var_6, var_10);
                // global_torque_w[ei, bi] = global_torque_w[ei, bi] + wp.cross(              <L 27>
                var_13 = wp::address(var_global_torque_w, var_3, var_6);
                // positions[tid_env, tid_body], forces[tid_env, tid_body]                    <L 28>
                var_14 = wp::address(var_positions, var_0, var_1);
                var_15 = wp::address(var_forces, var_0, var_1);
                var_17 = wp::load(var_14);
                var_18 = wp::load(var_15);
                var_16 = wp::cross(var_17, var_18);
                var_20 = wp::load(var_13);
                var_19 = wp::add(var_20, var_16);
                // global_torque_w[ei, bi] = global_torque_w[ei, bi] + wp.cross(              <L 27>
                // wp::array_store(var_global_torque_w, var_3, var_6, var_19);
            }
            if (!var_positions) {
                // global_force_at_com_w[ei, bi] = global_force_at_com_w[ei, bi] + forces[tid_env, tid_body]       <L 31>
                var_21 = wp::address(var_global_force_at_com_w, var_3, var_6);
                var_22 = wp::address(var_forces, var_0, var_1);
                var_24 = wp::load(var_21);
                var_25 = wp::load(var_22);
                var_23 = wp::add(var_24, var_25);
                // wp::array_store(var_global_force_at_com_w, var_3, var_6, var_23);
            }
        }
        // if torques:                                                                        <L 32>
        if (var_torques) {
            // global_torque_w[ei, bi] = global_torque_w[ei, bi] + torques[tid_env, tid_body]       <L 33>
            var_26 = wp::address(var_global_torque_w, var_3, var_6);
            var_27 = wp::address(var_torques, var_0, var_1);
            var_29 = wp::load(var_26);
            var_30 = wp::load(var_27);
            var_28 = wp::add(var_29, var_30);
            // wp::array_store(var_global_torque_w, var_3, var_6, var_28);
        }
    }
    if (!var_is_global) {
        // if forces:                                                                         <L 35>
        if (var_forces) {
            // local_force_b[ei, bi] = local_force_b[ei, bi] + forces[tid_env, tid_body]       <L 36>
            var_31 = wp::address(var_local_force_b, var_3, var_6);
            var_32 = wp::address(var_forces, var_0, var_1);
            var_34 = wp::load(var_31);
            var_35 = wp::load(var_32);
            var_33 = wp::add(var_34, var_35);
            // wp::array_store(var_local_force_b, var_3, var_6, var_33);
            // if positions:                                                                  <L 37>
            if (var_positions) {
                // local_torque_b[ei, bi] = local_torque_b[ei, bi] + wp.cross(                <L 38>
                var_36 = wp::address(var_local_torque_b, var_3, var_6);
                // positions[tid_env, tid_body], forces[tid_env, tid_body]                    <L 39>
                var_37 = wp::address(var_positions, var_0, var_1);
                var_38 = wp::address(var_forces, var_0, var_1);
                var_40 = wp::load(var_37);
                var_41 = wp::load(var_38);
                var_39 = wp::cross(var_40, var_41);
                var_43 = wp::load(var_36);
                var_42 = wp::add(var_43, var_39);
                // local_torque_b[ei, bi] = local_torque_b[ei, bi] + wp.cross(                <L 38>
                // wp::array_store(var_local_torque_b, var_3, var_6, var_42);
            }
        }
        // if torques:                                                                        <L 41>
        if (var_torques) {
            // local_torque_b[ei, bi] = local_torque_b[ei, bi] + torques[tid_env, tid_body]       <L 42>
            var_44 = wp::address(var_local_torque_b, var_3, var_6);
            var_45 = wp::address(var_torques, var_0, var_1);
            var_47 = wp::load(var_44);
            var_48 = wp::load(var_45);
            var_46 = wp::add(var_47, var_48);
            // wp::array_store(var_local_torque_b, var_3, var_6, var_46);
        }
    }
    //---------
    // reverse
    if (!var_is_global) {
        if (var_torques) {
            wp::adj_array_store(var_local_torque_b, var_3, var_6, var_46, adj_local_torque_b, adj_3, adj_6, adj_46);
            wp::adj_add(var_47, var_48, adj_44, adj_45, adj_46);
            wp::adj_address(var_torques, var_0, var_1, adj_torques, adj_0, adj_1, adj_45);
            wp::adj_address(var_local_torque_b, var_3, var_6, adj_local_torque_b, adj_3, adj_6, adj_44);
            // adj: local_torque_b[ei, bi] = local_torque_b[ei, bi] + torques[tid_env, tid_body]  <L 42>
        }
        // adj: if torques:                                                                   <L 41>
        if (var_forces) {
            if (var_positions) {
                wp::adj_array_store(var_local_torque_b, var_3, var_6, var_42, adj_local_torque_b, adj_3, adj_6, adj_42);
                // adj: local_torque_b[ei, bi] = local_torque_b[ei, bi] + wp.cross(           <L 38>
                wp::adj_add(var_43, var_39, adj_36, adj_39, adj_42);
                wp::adj_cross(var_40, var_41, adj_37, adj_38, adj_39);
                wp::adj_address(var_forces, var_0, var_1, adj_forces, adj_0, adj_1, adj_38);
                wp::adj_address(var_positions, var_0, var_1, adj_positions, adj_0, adj_1, adj_37);
                // adj: positions[tid_env, tid_body], forces[tid_env, tid_body]               <L 39>
                wp::adj_address(var_local_torque_b, var_3, var_6, adj_local_torque_b, adj_3, adj_6, adj_36);
                // adj: local_torque_b[ei, bi] = local_torque_b[ei, bi] + wp.cross(           <L 38>
            }
            // adj: if positions:                                                             <L 37>
            wp::adj_array_store(var_local_force_b, var_3, var_6, var_33, adj_local_force_b, adj_3, adj_6, adj_33);
            wp::adj_add(var_34, var_35, adj_31, adj_32, adj_33);
            wp::adj_address(var_forces, var_0, var_1, adj_forces, adj_0, adj_1, adj_32);
            wp::adj_address(var_local_force_b, var_3, var_6, adj_local_force_b, adj_3, adj_6, adj_31);
            // adj: local_force_b[ei, bi] = local_force_b[ei, bi] + forces[tid_env, tid_body]  <L 36>
        }
        // adj: if forces:                                                                    <L 35>
    }
    if (var_is_global) {
        if (var_torques) {
            wp::adj_array_store(var_global_torque_w, var_3, var_6, var_28, adj_global_torque_w, adj_3, adj_6, adj_28);
            wp::adj_add(var_29, var_30, adj_26, adj_27, adj_28);
            wp::adj_address(var_torques, var_0, var_1, adj_torques, adj_0, adj_1, adj_27);
            wp::adj_address(var_global_torque_w, var_3, var_6, adj_global_torque_w, adj_3, adj_6, adj_26);
            // adj: global_torque_w[ei, bi] = global_torque_w[ei, bi] + torques[tid_env, tid_body]  <L 33>
        }
        // adj: if torques:                                                                   <L 32>
        if (var_forces) {
            if (!var_positions) {
                wp::adj_array_store(var_global_force_at_com_w, var_3, var_6, var_23, adj_global_force_at_com_w, adj_3, adj_6, adj_23);
                wp::adj_add(var_24, var_25, adj_21, adj_22, adj_23);
                wp::adj_address(var_forces, var_0, var_1, adj_forces, adj_0, adj_1, adj_22);
                wp::adj_address(var_global_force_at_com_w, var_3, var_6, adj_global_force_at_com_w, adj_3, adj_6, adj_21);
                // adj: global_force_at_com_w[ei, bi] = global_force_at_com_w[ei, bi] + forces[tid_env, tid_body]  <L 31>
            }
            if (var_positions) {
                wp::adj_array_store(var_global_torque_w, var_3, var_6, var_19, adj_global_torque_w, adj_3, adj_6, adj_19);
                // adj: global_torque_w[ei, bi] = global_torque_w[ei, bi] + wp.cross(         <L 27>
                wp::adj_add(var_20, var_16, adj_13, adj_16, adj_19);
                wp::adj_cross(var_17, var_18, adj_14, adj_15, adj_16);
                wp::adj_address(var_forces, var_0, var_1, adj_forces, adj_0, adj_1, adj_15);
                wp::adj_address(var_positions, var_0, var_1, adj_positions, adj_0, adj_1, adj_14);
                // adj: positions[tid_env, tid_body], forces[tid_env, tid_body]               <L 28>
                wp::adj_address(var_global_torque_w, var_3, var_6, adj_global_torque_w, adj_3, adj_6, adj_13);
                // adj: global_torque_w[ei, bi] = global_torque_w[ei, bi] + wp.cross(         <L 27>
                wp::adj_array_store(var_global_force_w, var_3, var_6, var_10, adj_global_force_w, adj_3, adj_6, adj_10);
                wp::adj_add(var_11, var_12, adj_8, adj_9, adj_10);
                wp::adj_address(var_forces, var_0, var_1, adj_forces, adj_0, adj_1, adj_9);
                wp::adj_address(var_global_force_w, var_3, var_6, adj_global_force_w, adj_3, adj_6, adj_8);
                // adj: global_force_w[ei, bi] = global_force_w[ei, bi] + forces[tid_env, tid_body]  <L 26>
            }
            // adj: if positions:                                                             <L 25>
        }
        // adj: if forces:                                                                    <L 24>
    }
    // adj: if is_global:                                                                     <L 23>
    wp::adj_address(var_body_ids, var_1, adj_body_ids, adj_1, adj_5);
    // adj: bi = wp.int32(body_ids[tid_body])                                                 <L 21>
    wp::adj_address(var_env_ids, var_0, adj_env_ids, adj_0, adj_2);
    // adj: ei = wp.int32(env_ids[tid_env])                                                   <L 20>
    // adj: tid_env, tid_body = wp.tid()                                                      <L 19>
    // adj: def add_forces_to_dual_buffers_index(                                             <L 1>
    return;
}



extern "C" {

// Python CPU entry points
WP_API void add_forces_to_dual_buffers_index_1a379c01_cpu_forward(
    wp::launch_bounds_t<2> *dim,
    wp_args_add_forces_to_dual_buffers_index_1a379c01 *_wp_args)
{
    wp::tile_shared_storage_t tile_mem;
#if defined(WP_ENABLE_TILES_IN_STACK_MEMORY)
    wp::shared_tile_storage = &tile_mem;
#endif

    for (size_t task_index = 0; task_index < dim->size; ++task_index)
    {
        add_forces_to_dual_buffers_index_1a379c01_cpu_kernel_forward(*dim, task_index, _wp_args);
    }
}

} // extern C



extern "C" {

WP_API void add_forces_to_dual_buffers_index_1a379c01_cpu_backward(
    wp::launch_bounds_t<2> *dim,
    wp_args_add_forces_to_dual_buffers_index_1a379c01 *_wp_args,
    wp_args_add_forces_to_dual_buffers_index_1a379c01 *_wp_adj_args)
{
    wp::tile_shared_storage_t tile_mem;
#if defined(WP_ENABLE_TILES_IN_STACK_MEMORY)
    wp::shared_tile_storage = &tile_mem;
#endif

    for (size_t task_index = 0; task_index < dim->size; ++task_index)
    {
        add_forces_to_dual_buffers_index_1a379c01_cpu_kernel_backward(*dim, task_index, _wp_args, _wp_adj_args);
    }
}

} // extern C

struct wp_args_set_forces_to_dual_buffers_index_2f170b0a {
    wp::array_t<wp::int32> env_ids;
    wp::array_t<wp::int64> body_ids;
    wp::array_t<wp::vec_t<3, wp::float32>> forces;
    wp::array_t<wp::vec_t<3, wp::float32>> torques;
    wp::array_t<wp::vec_t<3, wp::float32>> positions;
    wp::array_t<wp::vec_t<3, wp::float32>> global_force_w;
    wp::array_t<wp::vec_t<3, wp::float32>> global_torque_w;
    wp::array_t<wp::vec_t<3, wp::float32>> global_force_at_com_w;
    wp::array_t<wp::vec_t<3, wp::float32>> local_force_b;
    wp::array_t<wp::vec_t<3, wp::float32>> local_torque_b;
    bool is_global;
};


void set_forces_to_dual_buffers_index_2f170b0a_cpu_kernel_forward(
    wp::launch_bounds_t<2> dim,
    size_t task_index,
    wp_args_set_forces_to_dual_buffers_index_2f170b0a *_wp_args)
{
    //---------
    // argument vars
    wp::array_t<wp::int32> var_env_ids = _wp_args->env_ids;
    wp::array_t<wp::int64> var_body_ids = _wp_args->body_ids;
    wp::array_t<wp::vec_t<3, wp::float32>> var_forces = _wp_args->forces;
    wp::array_t<wp::vec_t<3, wp::float32>> var_torques = _wp_args->torques;
    wp::array_t<wp::vec_t<3, wp::float32>> var_positions = _wp_args->positions;
    wp::array_t<wp::vec_t<3, wp::float32>> var_global_force_w = _wp_args->global_force_w;
    wp::array_t<wp::vec_t<3, wp::float32>> var_global_torque_w = _wp_args->global_torque_w;
    wp::array_t<wp::vec_t<3, wp::float32>> var_global_force_at_com_w = _wp_args->global_force_at_com_w;
    wp::array_t<wp::vec_t<3, wp::float32>> var_local_force_b = _wp_args->local_force_b;
    wp::array_t<wp::vec_t<3, wp::float32>> var_local_torque_b = _wp_args->local_torque_b;
    bool var_is_global = _wp_args->is_global;
    //---------
    // primal vars
    wp::int32 var_0;
    wp::int32 var_1;
    wp::int32* var_2;
    wp::int32 var_3;
    wp::int32 var_4;
    wp::int64* var_5;
    wp::int32 var_6;
    wp::int64 var_7;
    wp::vec_t<3, wp::float32>* var_8;
    wp::vec_t<3, wp::float32> var_9;
    wp::vec_t<3, wp::float32>* var_10;
    wp::vec_t<3, wp::float32> var_11;
    wp::vec_t<3, wp::float32>* var_12;
    wp::vec_t<3, wp::float32>* var_13;
    wp::vec_t<3, wp::float32>* var_14;
    wp::vec_t<3, wp::float32> var_15;
    wp::vec_t<3, wp::float32> var_16;
    wp::vec_t<3, wp::float32> var_17;
    wp::vec_t<3, wp::float32> var_18;
    wp::vec_t<3, wp::float32> var_19;
    wp::vec_t<3, wp::float32>* var_20;
    wp::vec_t<3, wp::float32>* var_21;
    wp::vec_t<3, wp::float32> var_22;
    wp::vec_t<3, wp::float32> var_23;
    wp::vec_t<3, wp::float32> var_24;
    wp::vec_t<3, wp::float32>* var_25;
    wp::vec_t<3, wp::float32> var_26;
    wp::vec_t<3, wp::float32>* var_27;
    wp::vec_t<3, wp::float32> var_28;
    wp::vec_t<3, wp::float32>* var_29;
    wp::vec_t<3, wp::float32> var_30;
    wp::vec_t<3, wp::float32>* var_31;
    wp::vec_t<3, wp::float32>* var_32;
    wp::vec_t<3, wp::float32>* var_33;
    wp::vec_t<3, wp::float32> var_34;
    wp::vec_t<3, wp::float32> var_35;
    wp::vec_t<3, wp::float32> var_36;
    wp::vec_t<3, wp::float32> var_37;
    wp::vec_t<3, wp::float32> var_38;
    wp::vec_t<3, wp::float32>* var_39;
    wp::vec_t<3, wp::float32>* var_40;
    wp::vec_t<3, wp::float32> var_41;
    wp::vec_t<3, wp::float32> var_42;
    wp::vec_t<3, wp::float32> var_43;
    //---------
    // forward
    // def set_forces_to_dual_buffers_index(                                                  <L 1>
    // tid_env, tid_body = wp.tid()                                                           <L 25>
    builtin_tid2d(var_0, var_1);
    // ei = wp.int32(env_ids[tid_env])                                                        <L 26>
    var_2 = wp::address(var_env_ids, var_0);
    var_4 = wp::load(var_2);
    var_3 = wp::int32(var_4);
    // bi = wp.int32(body_ids[tid_body])                                                      <L 27>
    var_5 = wp::address(var_body_ids, var_1);
    var_7 = wp::load(var_5);
    var_6 = wp::int32(var_7);
    // if is_global:                                                                          <L 29>
    if (var_is_global) {
        // if torques:                                                                        <L 30>
        if (var_torques) {
            // global_torque_w[ei, bi] = torques[tid_env, tid_body]                           <L 31>
            var_8 = wp::address(var_torques, var_0, var_1);
            var_9 = wp::load(var_8);
            wp::array_store(var_global_torque_w, var_3, var_6, var_9);
        }
        // if forces:                                                                         <L 32>
        if (var_forces) {
            // if positions:                                                                  <L 33>
            if (var_positions) {
                // global_force_w[ei, bi] = forces[tid_env, tid_body]                         <L 34>
                var_10 = wp::address(var_forces, var_0, var_1);
                var_11 = wp::load(var_10);
                wp::array_store(var_global_force_w, var_3, var_6, var_11);
                // if torques:                                                                <L 35>
                if (var_torques) {
                    // global_torque_w[ei, bi] = global_torque_w[ei, bi] + wp.cross(          <L 36>
                    var_12 = wp::address(var_global_torque_w, var_3, var_6);
                    // positions[tid_env, tid_body], forces[tid_env, tid_body]                <L 37>
                    var_13 = wp::address(var_positions, var_0, var_1);
                    var_14 = wp::address(var_forces, var_0, var_1);
                    var_16 = wp::load(var_13);
                    var_17 = wp::load(var_14);
                    var_15 = wp::cross(var_16, var_17);
                    var_19 = wp::load(var_12);
                    var_18 = wp::add(var_19, var_15);
                    // global_torque_w[ei, bi] = global_torque_w[ei, bi] + wp.cross(          <L 36>
                    wp::array_store(var_global_torque_w, var_3, var_6, var_18);
                }
                if (!var_torques) {
                    // global_torque_w[ei, bi] = wp.cross(positions[tid_env, tid_body], forces[tid_env, tid_body])       <L 40>
                    var_20 = wp::address(var_positions, var_0, var_1);
                    var_21 = wp::address(var_forces, var_0, var_1);
                    var_23 = wp::load(var_20);
                    var_24 = wp::load(var_21);
                    var_22 = wp::cross(var_23, var_24);
                    wp::array_store(var_global_torque_w, var_3, var_6, var_22);
                }
            }
            if (!var_positions) {
                // global_force_at_com_w[ei, bi] = forces[tid_env, tid_body]                  <L 42>
                var_25 = wp::address(var_forces, var_0, var_1);
                var_26 = wp::load(var_25);
                wp::array_store(var_global_force_at_com_w, var_3, var_6, var_26);
            }
        }
    }
    if (!var_is_global) {
        // if torques:                                                                        <L 44>
        if (var_torques) {
            // local_torque_b[ei, bi] = torques[tid_env, tid_body]                            <L 45>
            var_27 = wp::address(var_torques, var_0, var_1);
            var_28 = wp::load(var_27);
            wp::array_store(var_local_torque_b, var_3, var_6, var_28);
        }
        // if forces:                                                                         <L 46>
        if (var_forces) {
            // local_force_b[ei, bi] = forces[tid_env, tid_body]                              <L 47>
            var_29 = wp::address(var_forces, var_0, var_1);
            var_30 = wp::load(var_29);
            wp::array_store(var_local_force_b, var_3, var_6, var_30);
            // if positions:                                                                  <L 48>
            if (var_positions) {
                // if torques:                                                                <L 49>
                if (var_torques) {
                    // local_torque_b[ei, bi] = local_torque_b[ei, bi] + wp.cross(            <L 50>
                    var_31 = wp::address(var_local_torque_b, var_3, var_6);
                    // positions[tid_env, tid_body], forces[tid_env, tid_body]                <L 51>
                    var_32 = wp::address(var_positions, var_0, var_1);
                    var_33 = wp::address(var_forces, var_0, var_1);
                    var_35 = wp::load(var_32);
                    var_36 = wp::load(var_33);
                    var_34 = wp::cross(var_35, var_36);
                    var_38 = wp::load(var_31);
                    var_37 = wp::add(var_38, var_34);
                    // local_torque_b[ei, bi] = local_torque_b[ei, bi] + wp.cross(            <L 50>
                    wp::array_store(var_local_torque_b, var_3, var_6, var_37);
                }
                if (!var_torques) {
                    // local_torque_b[ei, bi] = wp.cross(positions[tid_env, tid_body], forces[tid_env, tid_body])       <L 54>
                    var_39 = wp::address(var_positions, var_0, var_1);
                    var_40 = wp::address(var_forces, var_0, var_1);
                    var_42 = wp::load(var_39);
                    var_43 = wp::load(var_40);
                    var_41 = wp::cross(var_42, var_43);
                    wp::array_store(var_local_torque_b, var_3, var_6, var_41);
                }
            }
        }
    }
}



void set_forces_to_dual_buffers_index_2f170b0a_cpu_kernel_backward(
    wp::launch_bounds_t<2> dim,
    size_t task_index,
    wp_args_set_forces_to_dual_buffers_index_2f170b0a *_wp_args,
    wp_args_set_forces_to_dual_buffers_index_2f170b0a *_wp_adj_args)
{
    //---------
    // argument vars
    wp::array_t<wp::int32> var_env_ids = _wp_args->env_ids;
    wp::array_t<wp::int64> var_body_ids = _wp_args->body_ids;
    wp::array_t<wp::vec_t<3, wp::float32>> var_forces = _wp_args->forces;
    wp::array_t<wp::vec_t<3, wp::float32>> var_torques = _wp_args->torques;
    wp::array_t<wp::vec_t<3, wp::float32>> var_positions = _wp_args->positions;
    wp::array_t<wp::vec_t<3, wp::float32>> var_global_force_w = _wp_args->global_force_w;
    wp::array_t<wp::vec_t<3, wp::float32>> var_global_torque_w = _wp_args->global_torque_w;
    wp::array_t<wp::vec_t<3, wp::float32>> var_global_force_at_com_w = _wp_args->global_force_at_com_w;
    wp::array_t<wp::vec_t<3, wp::float32>> var_local_force_b = _wp_args->local_force_b;
    wp::array_t<wp::vec_t<3, wp::float32>> var_local_torque_b = _wp_args->local_torque_b;
    bool var_is_global = _wp_args->is_global;
    wp::array_t<wp::int32> adj_env_ids = _wp_adj_args->env_ids;
    wp::array_t<wp::int64> adj_body_ids = _wp_adj_args->body_ids;
    wp::array_t<wp::vec_t<3, wp::float32>> adj_forces = _wp_adj_args->forces;
    wp::array_t<wp::vec_t<3, wp::float32>> adj_torques = _wp_adj_args->torques;
    wp::array_t<wp::vec_t<3, wp::float32>> adj_positions = _wp_adj_args->positions;
    wp::array_t<wp::vec_t<3, wp::float32>> adj_global_force_w = _wp_adj_args->global_force_w;
    wp::array_t<wp::vec_t<3, wp::float32>> adj_global_torque_w = _wp_adj_args->global_torque_w;
    wp::array_t<wp::vec_t<3, wp::float32>> adj_global_force_at_com_w = _wp_adj_args->global_force_at_com_w;
    wp::array_t<wp::vec_t<3, wp::float32>> adj_local_force_b = _wp_adj_args->local_force_b;
    wp::array_t<wp::vec_t<3, wp::float32>> adj_local_torque_b = _wp_adj_args->local_torque_b;
    bool adj_is_global = _wp_adj_args->is_global;
    //---------
    // primal vars
    wp::int32 var_0;
    wp::int32 var_1;
    wp::int32* var_2;
    wp::int32 var_3;
    wp::int32 var_4;
    wp::int64* var_5;
    wp::int32 var_6;
    wp::int64 var_7;
    wp::vec_t<3, wp::float32>* var_8;
    wp::vec_t<3, wp::float32> var_9;
    wp::vec_t<3, wp::float32>* var_10;
    wp::vec_t<3, wp::float32> var_11;
    wp::vec_t<3, wp::float32>* var_12;
    wp::vec_t<3, wp::float32>* var_13;
    wp::vec_t<3, wp::float32>* var_14;
    wp::vec_t<3, wp::float32> var_15;
    wp::vec_t<3, wp::float32> var_16;
    wp::vec_t<3, wp::float32> var_17;
    wp::vec_t<3, wp::float32> var_18;
    wp::vec_t<3, wp::float32> var_19;
    wp::vec_t<3, wp::float32>* var_20;
    wp::vec_t<3, wp::float32>* var_21;
    wp::vec_t<3, wp::float32> var_22;
    wp::vec_t<3, wp::float32> var_23;
    wp::vec_t<3, wp::float32> var_24;
    wp::vec_t<3, wp::float32>* var_25;
    wp::vec_t<3, wp::float32> var_26;
    wp::vec_t<3, wp::float32>* var_27;
    wp::vec_t<3, wp::float32> var_28;
    wp::vec_t<3, wp::float32>* var_29;
    wp::vec_t<3, wp::float32> var_30;
    wp::vec_t<3, wp::float32>* var_31;
    wp::vec_t<3, wp::float32>* var_32;
    wp::vec_t<3, wp::float32>* var_33;
    wp::vec_t<3, wp::float32> var_34;
    wp::vec_t<3, wp::float32> var_35;
    wp::vec_t<3, wp::float32> var_36;
    wp::vec_t<3, wp::float32> var_37;
    wp::vec_t<3, wp::float32> var_38;
    wp::vec_t<3, wp::float32>* var_39;
    wp::vec_t<3, wp::float32>* var_40;
    wp::vec_t<3, wp::float32> var_41;
    wp::vec_t<3, wp::float32> var_42;
    wp::vec_t<3, wp::float32> var_43;
    //---------
    // dual vars
    wp::int32 adj_0 = {};
    wp::int32 adj_1 = {};
    wp::int32 adj_2 = {};
    wp::int32 adj_3 = {};
    wp::int32 adj_4 = {};
    wp::int64 adj_5 = {};
    wp::int32 adj_6 = {};
    wp::int64 adj_7 = {};
    wp::vec_t<3, wp::float32> adj_8 = {};
    wp::vec_t<3, wp::float32> adj_9 = {};
    wp::vec_t<3, wp::float32> adj_10 = {};
    wp::vec_t<3, wp::float32> adj_11 = {};
    wp::vec_t<3, wp::float32> adj_12 = {};
    wp::vec_t<3, wp::float32> adj_13 = {};
    wp::vec_t<3, wp::float32> adj_14 = {};
    wp::vec_t<3, wp::float32> adj_15 = {};
    wp::vec_t<3, wp::float32> adj_16 = {};
    wp::vec_t<3, wp::float32> adj_17 = {};
    wp::vec_t<3, wp::float32> adj_18 = {};
    wp::vec_t<3, wp::float32> adj_19 = {};
    wp::vec_t<3, wp::float32> adj_20 = {};
    wp::vec_t<3, wp::float32> adj_21 = {};
    wp::vec_t<3, wp::float32> adj_22 = {};
    wp::vec_t<3, wp::float32> adj_23 = {};
    wp::vec_t<3, wp::float32> adj_24 = {};
    wp::vec_t<3, wp::float32> adj_25 = {};
    wp::vec_t<3, wp::float32> adj_26 = {};
    wp::vec_t<3, wp::float32> adj_27 = {};
    wp::vec_t<3, wp::float32> adj_28 = {};
    wp::vec_t<3, wp::float32> adj_29 = {};
    wp::vec_t<3, wp::float32> adj_30 = {};
    wp::vec_t<3, wp::float32> adj_31 = {};
    wp::vec_t<3, wp::float32> adj_32 = {};
    wp::vec_t<3, wp::float32> adj_33 = {};
    wp::vec_t<3, wp::float32> adj_34 = {};
    wp::vec_t<3, wp::float32> adj_35 = {};
    wp::vec_t<3, wp::float32> adj_36 = {};
    wp::vec_t<3, wp::float32> adj_37 = {};
    wp::vec_t<3, wp::float32> adj_38 = {};
    wp::vec_t<3, wp::float32> adj_39 = {};
    wp::vec_t<3, wp::float32> adj_40 = {};
    wp::vec_t<3, wp::float32> adj_41 = {};
    wp::vec_t<3, wp::float32> adj_42 = {};
    wp::vec_t<3, wp::float32> adj_43 = {};
    //---------
    // forward
    // def set_forces_to_dual_buffers_index(                                                  <L 1>
    // tid_env, tid_body = wp.tid()                                                           <L 25>
    builtin_tid2d(var_0, var_1);
    // ei = wp.int32(env_ids[tid_env])                                                        <L 26>
    var_2 = wp::address(var_env_ids, var_0);
    var_4 = wp::load(var_2);
    var_3 = wp::int32(var_4);
    // bi = wp.int32(body_ids[tid_body])                                                      <L 27>
    var_5 = wp::address(var_body_ids, var_1);
    var_7 = wp::load(var_5);
    var_6 = wp::int32(var_7);
    // if is_global:                                                                          <L 29>
    if (var_is_global) {
        // if torques:                                                                        <L 30>
        if (var_torques) {
            // global_torque_w[ei, bi] = torques[tid_env, tid_body]                           <L 31>
            var_8 = wp::address(var_torques, var_0, var_1);
            var_9 = wp::load(var_8);
            // wp::array_store(var_global_torque_w, var_3, var_6, var_9);
        }
        // if forces:                                                                         <L 32>
        if (var_forces) {
            // if positions:                                                                  <L 33>
            if (var_positions) {
                // global_force_w[ei, bi] = forces[tid_env, tid_body]                         <L 34>
                var_10 = wp::address(var_forces, var_0, var_1);
                var_11 = wp::load(var_10);
                // wp::array_store(var_global_force_w, var_3, var_6, var_11);
                // if torques:                                                                <L 35>
                if (var_torques) {
                    // global_torque_w[ei, bi] = global_torque_w[ei, bi] + wp.cross(          <L 36>
                    var_12 = wp::address(var_global_torque_w, var_3, var_6);
                    // positions[tid_env, tid_body], forces[tid_env, tid_body]                <L 37>
                    var_13 = wp::address(var_positions, var_0, var_1);
                    var_14 = wp::address(var_forces, var_0, var_1);
                    var_16 = wp::load(var_13);
                    var_17 = wp::load(var_14);
                    var_15 = wp::cross(var_16, var_17);
                    var_19 = wp::load(var_12);
                    var_18 = wp::add(var_19, var_15);
                    // global_torque_w[ei, bi] = global_torque_w[ei, bi] + wp.cross(          <L 36>
                    // wp::array_store(var_global_torque_w, var_3, var_6, var_18);
                }
                if (!var_torques) {
                    // global_torque_w[ei, bi] = wp.cross(positions[tid_env, tid_body], forces[tid_env, tid_body])       <L 40>
                    var_20 = wp::address(var_positions, var_0, var_1);
                    var_21 = wp::address(var_forces, var_0, var_1);
                    var_23 = wp::load(var_20);
                    var_24 = wp::load(var_21);
                    var_22 = wp::cross(var_23, var_24);
                    // wp::array_store(var_global_torque_w, var_3, var_6, var_22);
                }
            }
            if (!var_positions) {
                // global_force_at_com_w[ei, bi] = forces[tid_env, tid_body]                  <L 42>
                var_25 = wp::address(var_forces, var_0, var_1);
                var_26 = wp::load(var_25);
                // wp::array_store(var_global_force_at_com_w, var_3, var_6, var_26);
            }
        }
    }
    if (!var_is_global) {
        // if torques:                                                                        <L 44>
        if (var_torques) {
            // local_torque_b[ei, bi] = torques[tid_env, tid_body]                            <L 45>
            var_27 = wp::address(var_torques, var_0, var_1);
            var_28 = wp::load(var_27);
            // wp::array_store(var_local_torque_b, var_3, var_6, var_28);
        }
        // if forces:                                                                         <L 46>
        if (var_forces) {
            // local_force_b[ei, bi] = forces[tid_env, tid_body]                              <L 47>
            var_29 = wp::address(var_forces, var_0, var_1);
            var_30 = wp::load(var_29);
            // wp::array_store(var_local_force_b, var_3, var_6, var_30);
            // if positions:                                                                  <L 48>
            if (var_positions) {
                // if torques:                                                                <L 49>
                if (var_torques) {
                    // local_torque_b[ei, bi] = local_torque_b[ei, bi] + wp.cross(            <L 50>
                    var_31 = wp::address(var_local_torque_b, var_3, var_6);
                    // positions[tid_env, tid_body], forces[tid_env, tid_body]                <L 51>
                    var_32 = wp::address(var_positions, var_0, var_1);
                    var_33 = wp::address(var_forces, var_0, var_1);
                    var_35 = wp::load(var_32);
                    var_36 = wp::load(var_33);
                    var_34 = wp::cross(var_35, var_36);
                    var_38 = wp::load(var_31);
                    var_37 = wp::add(var_38, var_34);
                    // local_torque_b[ei, bi] = local_torque_b[ei, bi] + wp.cross(            <L 50>
                    // wp::array_store(var_local_torque_b, var_3, var_6, var_37);
                }
                if (!var_torques) {
                    // local_torque_b[ei, bi] = wp.cross(positions[tid_env, tid_body], forces[tid_env, tid_body])       <L 54>
                    var_39 = wp::address(var_positions, var_0, var_1);
                    var_40 = wp::address(var_forces, var_0, var_1);
                    var_42 = wp::load(var_39);
                    var_43 = wp::load(var_40);
                    var_41 = wp::cross(var_42, var_43);
                    // wp::array_store(var_local_torque_b, var_3, var_6, var_41);
                }
            }
        }
    }
    //---------
    // reverse
    if (!var_is_global) {
        if (var_forces) {
            if (var_positions) {
                if (!var_torques) {
                    wp::adj_array_store(var_local_torque_b, var_3, var_6, var_41, adj_local_torque_b, adj_3, adj_6, adj_41);
                    wp::adj_cross(var_42, var_43, adj_39, adj_40, adj_41);
                    wp::adj_address(var_forces, var_0, var_1, adj_forces, adj_0, adj_1, adj_40);
                    wp::adj_address(var_positions, var_0, var_1, adj_positions, adj_0, adj_1, adj_39);
                    // adj: local_torque_b[ei, bi] = wp.cross(positions[tid_env, tid_body], forces[tid_env, tid_body])  <L 54>
                }
                if (var_torques) {
                    wp::adj_array_store(var_local_torque_b, var_3, var_6, var_37, adj_local_torque_b, adj_3, adj_6, adj_37);
                    // adj: local_torque_b[ei, bi] = local_torque_b[ei, bi] + wp.cross(       <L 50>
                    wp::adj_add(var_38, var_34, adj_31, adj_34, adj_37);
                    wp::adj_cross(var_35, var_36, adj_32, adj_33, adj_34);
                    wp::adj_address(var_forces, var_0, var_1, adj_forces, adj_0, adj_1, adj_33);
                    wp::adj_address(var_positions, var_0, var_1, adj_positions, adj_0, adj_1, adj_32);
                    // adj: positions[tid_env, tid_body], forces[tid_env, tid_body]           <L 51>
                    wp::adj_address(var_local_torque_b, var_3, var_6, adj_local_torque_b, adj_3, adj_6, adj_31);
                    // adj: local_torque_b[ei, bi] = local_torque_b[ei, bi] + wp.cross(       <L 50>
                }
                // adj: if torques:                                                           <L 49>
            }
            // adj: if positions:                                                             <L 48>
            wp::adj_array_store(var_local_force_b, var_3, var_6, var_30, adj_local_force_b, adj_3, adj_6, adj_29);
            wp::adj_address(var_forces, var_0, var_1, adj_forces, adj_0, adj_1, adj_29);
            // adj: local_force_b[ei, bi] = forces[tid_env, tid_body]                         <L 47>
        }
        // adj: if forces:                                                                    <L 46>
        if (var_torques) {
            wp::adj_array_store(var_local_torque_b, var_3, var_6, var_28, adj_local_torque_b, adj_3, adj_6, adj_27);
            wp::adj_address(var_torques, var_0, var_1, adj_torques, adj_0, adj_1, adj_27);
            // adj: local_torque_b[ei, bi] = torques[tid_env, tid_body]                       <L 45>
        }
        // adj: if torques:                                                                   <L 44>
    }
    if (var_is_global) {
        if (var_forces) {
            if (!var_positions) {
                wp::adj_array_store(var_global_force_at_com_w, var_3, var_6, var_26, adj_global_force_at_com_w, adj_3, adj_6, adj_25);
                wp::adj_address(var_forces, var_0, var_1, adj_forces, adj_0, adj_1, adj_25);
                // adj: global_force_at_com_w[ei, bi] = forces[tid_env, tid_body]             <L 42>
            }
            if (var_positions) {
                if (!var_torques) {
                    wp::adj_array_store(var_global_torque_w, var_3, var_6, var_22, adj_global_torque_w, adj_3, adj_6, adj_22);
                    wp::adj_cross(var_23, var_24, adj_20, adj_21, adj_22);
                    wp::adj_address(var_forces, var_0, var_1, adj_forces, adj_0, adj_1, adj_21);
                    wp::adj_address(var_positions, var_0, var_1, adj_positions, adj_0, adj_1, adj_20);
                    // adj: global_torque_w[ei, bi] = wp.cross(positions[tid_env, tid_body], forces[tid_env, tid_body])  <L 40>
                }
                if (var_torques) {
                    wp::adj_array_store(var_global_torque_w, var_3, var_6, var_18, adj_global_torque_w, adj_3, adj_6, adj_18);
                    // adj: global_torque_w[ei, bi] = global_torque_w[ei, bi] + wp.cross(     <L 36>
                    wp::adj_add(var_19, var_15, adj_12, adj_15, adj_18);
                    wp::adj_cross(var_16, var_17, adj_13, adj_14, adj_15);
                    wp::adj_address(var_forces, var_0, var_1, adj_forces, adj_0, adj_1, adj_14);
                    wp::adj_address(var_positions, var_0, var_1, adj_positions, adj_0, adj_1, adj_13);
                    // adj: positions[tid_env, tid_body], forces[tid_env, tid_body]           <L 37>
                    wp::adj_address(var_global_torque_w, var_3, var_6, adj_global_torque_w, adj_3, adj_6, adj_12);
                    // adj: global_torque_w[ei, bi] = global_torque_w[ei, bi] + wp.cross(     <L 36>
                }
                // adj: if torques:                                                           <L 35>
                wp::adj_array_store(var_global_force_w, var_3, var_6, var_11, adj_global_force_w, adj_3, adj_6, adj_10);
                wp::adj_address(var_forces, var_0, var_1, adj_forces, adj_0, adj_1, adj_10);
                // adj: global_force_w[ei, bi] = forces[tid_env, tid_body]                    <L 34>
            }
            // adj: if positions:                                                             <L 33>
        }
        // adj: if forces:                                                                    <L 32>
        if (var_torques) {
            wp::adj_array_store(var_global_torque_w, var_3, var_6, var_9, adj_global_torque_w, adj_3, adj_6, adj_8);
            wp::adj_address(var_torques, var_0, var_1, adj_torques, adj_0, adj_1, adj_8);
            // adj: global_torque_w[ei, bi] = torques[tid_env, tid_body]                      <L 31>
        }
        // adj: if torques:                                                                   <L 30>
    }
    // adj: if is_global:                                                                     <L 29>
    wp::adj_address(var_body_ids, var_1, adj_body_ids, adj_1, adj_5);
    // adj: bi = wp.int32(body_ids[tid_body])                                                 <L 27>
    wp::adj_address(var_env_ids, var_0, adj_env_ids, adj_0, adj_2);
    // adj: ei = wp.int32(env_ids[tid_env])                                                   <L 26>
    // adj: tid_env, tid_body = wp.tid()                                                      <L 25>
    // adj: def set_forces_to_dual_buffers_index(                                             <L 1>
    return;
}



extern "C" {

// Python CPU entry points
WP_API void set_forces_to_dual_buffers_index_2f170b0a_cpu_forward(
    wp::launch_bounds_t<2> *dim,
    wp_args_set_forces_to_dual_buffers_index_2f170b0a *_wp_args)
{
    wp::tile_shared_storage_t tile_mem;
#if defined(WP_ENABLE_TILES_IN_STACK_MEMORY)
    wp::shared_tile_storage = &tile_mem;
#endif

    for (size_t task_index = 0; task_index < dim->size; ++task_index)
    {
        set_forces_to_dual_buffers_index_2f170b0a_cpu_kernel_forward(*dim, task_index, _wp_args);
    }
}

} // extern C



extern "C" {

WP_API void set_forces_to_dual_buffers_index_2f170b0a_cpu_backward(
    wp::launch_bounds_t<2> *dim,
    wp_args_set_forces_to_dual_buffers_index_2f170b0a *_wp_args,
    wp_args_set_forces_to_dual_buffers_index_2f170b0a *_wp_adj_args)
{
    wp::tile_shared_storage_t tile_mem;
#if defined(WP_ENABLE_TILES_IN_STACK_MEMORY)
    wp::shared_tile_storage = &tile_mem;
#endif

    for (size_t task_index = 0; task_index < dim->size; ++task_index)
    {
        set_forces_to_dual_buffers_index_2f170b0a_cpu_kernel_backward(*dim, task_index, _wp_args, _wp_adj_args);
    }
}

} // extern C

struct wp_args_set_forces_to_dual_buffers_index_3e4a4295 {
    wp::array_t<wp::int64> env_ids;
    wp::array_t<wp::int64> body_ids;
    wp::array_t<wp::vec_t<3, wp::float32>> forces;
    wp::array_t<wp::vec_t<3, wp::float32>> torques;
    wp::array_t<wp::vec_t<3, wp::float32>> positions;
    wp::array_t<wp::vec_t<3, wp::float32>> global_force_w;
    wp::array_t<wp::vec_t<3, wp::float32>> global_torque_w;
    wp::array_t<wp::vec_t<3, wp::float32>> global_force_at_com_w;
    wp::array_t<wp::vec_t<3, wp::float32>> local_force_b;
    wp::array_t<wp::vec_t<3, wp::float32>> local_torque_b;
    bool is_global;
};


void set_forces_to_dual_buffers_index_3e4a4295_cpu_kernel_forward(
    wp::launch_bounds_t<2> dim,
    size_t task_index,
    wp_args_set_forces_to_dual_buffers_index_3e4a4295 *_wp_args)
{
    //---------
    // argument vars
    wp::array_t<wp::int64> var_env_ids = _wp_args->env_ids;
    wp::array_t<wp::int64> var_body_ids = _wp_args->body_ids;
    wp::array_t<wp::vec_t<3, wp::float32>> var_forces = _wp_args->forces;
    wp::array_t<wp::vec_t<3, wp::float32>> var_torques = _wp_args->torques;
    wp::array_t<wp::vec_t<3, wp::float32>> var_positions = _wp_args->positions;
    wp::array_t<wp::vec_t<3, wp::float32>> var_global_force_w = _wp_args->global_force_w;
    wp::array_t<wp::vec_t<3, wp::float32>> var_global_torque_w = _wp_args->global_torque_w;
    wp::array_t<wp::vec_t<3, wp::float32>> var_global_force_at_com_w = _wp_args->global_force_at_com_w;
    wp::array_t<wp::vec_t<3, wp::float32>> var_local_force_b = _wp_args->local_force_b;
    wp::array_t<wp::vec_t<3, wp::float32>> var_local_torque_b = _wp_args->local_torque_b;
    bool var_is_global = _wp_args->is_global;
    //---------
    // primal vars
    wp::int32 var_0;
    wp::int32 var_1;
    wp::int64* var_2;
    wp::int32 var_3;
    wp::int64 var_4;
    wp::int64* var_5;
    wp::int32 var_6;
    wp::int64 var_7;
    wp::vec_t<3, wp::float32>* var_8;
    wp::vec_t<3, wp::float32> var_9;
    wp::vec_t<3, wp::float32>* var_10;
    wp::vec_t<3, wp::float32> var_11;
    wp::vec_t<3, wp::float32>* var_12;
    wp::vec_t<3, wp::float32>* var_13;
    wp::vec_t<3, wp::float32>* var_14;
    wp::vec_t<3, wp::float32> var_15;
    wp::vec_t<3, wp::float32> var_16;
    wp::vec_t<3, wp::float32> var_17;
    wp::vec_t<3, wp::float32> var_18;
    wp::vec_t<3, wp::float32> var_19;
    wp::vec_t<3, wp::float32>* var_20;
    wp::vec_t<3, wp::float32>* var_21;
    wp::vec_t<3, wp::float32> var_22;
    wp::vec_t<3, wp::float32> var_23;
    wp::vec_t<3, wp::float32> var_24;
    wp::vec_t<3, wp::float32>* var_25;
    wp::vec_t<3, wp::float32> var_26;
    wp::vec_t<3, wp::float32>* var_27;
    wp::vec_t<3, wp::float32> var_28;
    wp::vec_t<3, wp::float32>* var_29;
    wp::vec_t<3, wp::float32> var_30;
    wp::vec_t<3, wp::float32>* var_31;
    wp::vec_t<3, wp::float32>* var_32;
    wp::vec_t<3, wp::float32>* var_33;
    wp::vec_t<3, wp::float32> var_34;
    wp::vec_t<3, wp::float32> var_35;
    wp::vec_t<3, wp::float32> var_36;
    wp::vec_t<3, wp::float32> var_37;
    wp::vec_t<3, wp::float32> var_38;
    wp::vec_t<3, wp::float32>* var_39;
    wp::vec_t<3, wp::float32>* var_40;
    wp::vec_t<3, wp::float32> var_41;
    wp::vec_t<3, wp::float32> var_42;
    wp::vec_t<3, wp::float32> var_43;
    //---------
    // forward
    // def set_forces_to_dual_buffers_index(                                                  <L 1>
    // tid_env, tid_body = wp.tid()                                                           <L 25>
    builtin_tid2d(var_0, var_1);
    // ei = wp.int32(env_ids[tid_env])                                                        <L 26>
    var_2 = wp::address(var_env_ids, var_0);
    var_4 = wp::load(var_2);
    var_3 = wp::int32(var_4);
    // bi = wp.int32(body_ids[tid_body])                                                      <L 27>
    var_5 = wp::address(var_body_ids, var_1);
    var_7 = wp::load(var_5);
    var_6 = wp::int32(var_7);
    // if is_global:                                                                          <L 29>
    if (var_is_global) {
        // if torques:                                                                        <L 30>
        if (var_torques) {
            // global_torque_w[ei, bi] = torques[tid_env, tid_body]                           <L 31>
            var_8 = wp::address(var_torques, var_0, var_1);
            var_9 = wp::load(var_8);
            wp::array_store(var_global_torque_w, var_3, var_6, var_9);
        }
        // if forces:                                                                         <L 32>
        if (var_forces) {
            // if positions:                                                                  <L 33>
            if (var_positions) {
                // global_force_w[ei, bi] = forces[tid_env, tid_body]                         <L 34>
                var_10 = wp::address(var_forces, var_0, var_1);
                var_11 = wp::load(var_10);
                wp::array_store(var_global_force_w, var_3, var_6, var_11);
                // if torques:                                                                <L 35>
                if (var_torques) {
                    // global_torque_w[ei, bi] = global_torque_w[ei, bi] + wp.cross(          <L 36>
                    var_12 = wp::address(var_global_torque_w, var_3, var_6);
                    // positions[tid_env, tid_body], forces[tid_env, tid_body]                <L 37>
                    var_13 = wp::address(var_positions, var_0, var_1);
                    var_14 = wp::address(var_forces, var_0, var_1);
                    var_16 = wp::load(var_13);
                    var_17 = wp::load(var_14);
                    var_15 = wp::cross(var_16, var_17);
                    var_19 = wp::load(var_12);
                    var_18 = wp::add(var_19, var_15);
                    // global_torque_w[ei, bi] = global_torque_w[ei, bi] + wp.cross(          <L 36>
                    wp::array_store(var_global_torque_w, var_3, var_6, var_18);
                }
                if (!var_torques) {
                    // global_torque_w[ei, bi] = wp.cross(positions[tid_env, tid_body], forces[tid_env, tid_body])       <L 40>
                    var_20 = wp::address(var_positions, var_0, var_1);
                    var_21 = wp::address(var_forces, var_0, var_1);
                    var_23 = wp::load(var_20);
                    var_24 = wp::load(var_21);
                    var_22 = wp::cross(var_23, var_24);
                    wp::array_store(var_global_torque_w, var_3, var_6, var_22);
                }
            }
            if (!var_positions) {
                // global_force_at_com_w[ei, bi] = forces[tid_env, tid_body]                  <L 42>
                var_25 = wp::address(var_forces, var_0, var_1);
                var_26 = wp::load(var_25);
                wp::array_store(var_global_force_at_com_w, var_3, var_6, var_26);
            }
        }
    }
    if (!var_is_global) {
        // if torques:                                                                        <L 44>
        if (var_torques) {
            // local_torque_b[ei, bi] = torques[tid_env, tid_body]                            <L 45>
            var_27 = wp::address(var_torques, var_0, var_1);
            var_28 = wp::load(var_27);
            wp::array_store(var_local_torque_b, var_3, var_6, var_28);
        }
        // if forces:                                                                         <L 46>
        if (var_forces) {
            // local_force_b[ei, bi] = forces[tid_env, tid_body]                              <L 47>
            var_29 = wp::address(var_forces, var_0, var_1);
            var_30 = wp::load(var_29);
            wp::array_store(var_local_force_b, var_3, var_6, var_30);
            // if positions:                                                                  <L 48>
            if (var_positions) {
                // if torques:                                                                <L 49>
                if (var_torques) {
                    // local_torque_b[ei, bi] = local_torque_b[ei, bi] + wp.cross(            <L 50>
                    var_31 = wp::address(var_local_torque_b, var_3, var_6);
                    // positions[tid_env, tid_body], forces[tid_env, tid_body]                <L 51>
                    var_32 = wp::address(var_positions, var_0, var_1);
                    var_33 = wp::address(var_forces, var_0, var_1);
                    var_35 = wp::load(var_32);
                    var_36 = wp::load(var_33);
                    var_34 = wp::cross(var_35, var_36);
                    var_38 = wp::load(var_31);
                    var_37 = wp::add(var_38, var_34);
                    // local_torque_b[ei, bi] = local_torque_b[ei, bi] + wp.cross(            <L 50>
                    wp::array_store(var_local_torque_b, var_3, var_6, var_37);
                }
                if (!var_torques) {
                    // local_torque_b[ei, bi] = wp.cross(positions[tid_env, tid_body], forces[tid_env, tid_body])       <L 54>
                    var_39 = wp::address(var_positions, var_0, var_1);
                    var_40 = wp::address(var_forces, var_0, var_1);
                    var_42 = wp::load(var_39);
                    var_43 = wp::load(var_40);
                    var_41 = wp::cross(var_42, var_43);
                    wp::array_store(var_local_torque_b, var_3, var_6, var_41);
                }
            }
        }
    }
}



void set_forces_to_dual_buffers_index_3e4a4295_cpu_kernel_backward(
    wp::launch_bounds_t<2> dim,
    size_t task_index,
    wp_args_set_forces_to_dual_buffers_index_3e4a4295 *_wp_args,
    wp_args_set_forces_to_dual_buffers_index_3e4a4295 *_wp_adj_args)
{
    //---------
    // argument vars
    wp::array_t<wp::int64> var_env_ids = _wp_args->env_ids;
    wp::array_t<wp::int64> var_body_ids = _wp_args->body_ids;
    wp::array_t<wp::vec_t<3, wp::float32>> var_forces = _wp_args->forces;
    wp::array_t<wp::vec_t<3, wp::float32>> var_torques = _wp_args->torques;
    wp::array_t<wp::vec_t<3, wp::float32>> var_positions = _wp_args->positions;
    wp::array_t<wp::vec_t<3, wp::float32>> var_global_force_w = _wp_args->global_force_w;
    wp::array_t<wp::vec_t<3, wp::float32>> var_global_torque_w = _wp_args->global_torque_w;
    wp::array_t<wp::vec_t<3, wp::float32>> var_global_force_at_com_w = _wp_args->global_force_at_com_w;
    wp::array_t<wp::vec_t<3, wp::float32>> var_local_force_b = _wp_args->local_force_b;
    wp::array_t<wp::vec_t<3, wp::float32>> var_local_torque_b = _wp_args->local_torque_b;
    bool var_is_global = _wp_args->is_global;
    wp::array_t<wp::int64> adj_env_ids = _wp_adj_args->env_ids;
    wp::array_t<wp::int64> adj_body_ids = _wp_adj_args->body_ids;
    wp::array_t<wp::vec_t<3, wp::float32>> adj_forces = _wp_adj_args->forces;
    wp::array_t<wp::vec_t<3, wp::float32>> adj_torques = _wp_adj_args->torques;
    wp::array_t<wp::vec_t<3, wp::float32>> adj_positions = _wp_adj_args->positions;
    wp::array_t<wp::vec_t<3, wp::float32>> adj_global_force_w = _wp_adj_args->global_force_w;
    wp::array_t<wp::vec_t<3, wp::float32>> adj_global_torque_w = _wp_adj_args->global_torque_w;
    wp::array_t<wp::vec_t<3, wp::float32>> adj_global_force_at_com_w = _wp_adj_args->global_force_at_com_w;
    wp::array_t<wp::vec_t<3, wp::float32>> adj_local_force_b = _wp_adj_args->local_force_b;
    wp::array_t<wp::vec_t<3, wp::float32>> adj_local_torque_b = _wp_adj_args->local_torque_b;
    bool adj_is_global = _wp_adj_args->is_global;
    //---------
    // primal vars
    wp::int32 var_0;
    wp::int32 var_1;
    wp::int64* var_2;
    wp::int32 var_3;
    wp::int64 var_4;
    wp::int64* var_5;
    wp::int32 var_6;
    wp::int64 var_7;
    wp::vec_t<3, wp::float32>* var_8;
    wp::vec_t<3, wp::float32> var_9;
    wp::vec_t<3, wp::float32>* var_10;
    wp::vec_t<3, wp::float32> var_11;
    wp::vec_t<3, wp::float32>* var_12;
    wp::vec_t<3, wp::float32>* var_13;
    wp::vec_t<3, wp::float32>* var_14;
    wp::vec_t<3, wp::float32> var_15;
    wp::vec_t<3, wp::float32> var_16;
    wp::vec_t<3, wp::float32> var_17;
    wp::vec_t<3, wp::float32> var_18;
    wp::vec_t<3, wp::float32> var_19;
    wp::vec_t<3, wp::float32>* var_20;
    wp::vec_t<3, wp::float32>* var_21;
    wp::vec_t<3, wp::float32> var_22;
    wp::vec_t<3, wp::float32> var_23;
    wp::vec_t<3, wp::float32> var_24;
    wp::vec_t<3, wp::float32>* var_25;
    wp::vec_t<3, wp::float32> var_26;
    wp::vec_t<3, wp::float32>* var_27;
    wp::vec_t<3, wp::float32> var_28;
    wp::vec_t<3, wp::float32>* var_29;
    wp::vec_t<3, wp::float32> var_30;
    wp::vec_t<3, wp::float32>* var_31;
    wp::vec_t<3, wp::float32>* var_32;
    wp::vec_t<3, wp::float32>* var_33;
    wp::vec_t<3, wp::float32> var_34;
    wp::vec_t<3, wp::float32> var_35;
    wp::vec_t<3, wp::float32> var_36;
    wp::vec_t<3, wp::float32> var_37;
    wp::vec_t<3, wp::float32> var_38;
    wp::vec_t<3, wp::float32>* var_39;
    wp::vec_t<3, wp::float32>* var_40;
    wp::vec_t<3, wp::float32> var_41;
    wp::vec_t<3, wp::float32> var_42;
    wp::vec_t<3, wp::float32> var_43;
    //---------
    // dual vars
    wp::int32 adj_0 = {};
    wp::int32 adj_1 = {};
    wp::int64 adj_2 = {};
    wp::int32 adj_3 = {};
    wp::int64 adj_4 = {};
    wp::int64 adj_5 = {};
    wp::int32 adj_6 = {};
    wp::int64 adj_7 = {};
    wp::vec_t<3, wp::float32> adj_8 = {};
    wp::vec_t<3, wp::float32> adj_9 = {};
    wp::vec_t<3, wp::float32> adj_10 = {};
    wp::vec_t<3, wp::float32> adj_11 = {};
    wp::vec_t<3, wp::float32> adj_12 = {};
    wp::vec_t<3, wp::float32> adj_13 = {};
    wp::vec_t<3, wp::float32> adj_14 = {};
    wp::vec_t<3, wp::float32> adj_15 = {};
    wp::vec_t<3, wp::float32> adj_16 = {};
    wp::vec_t<3, wp::float32> adj_17 = {};
    wp::vec_t<3, wp::float32> adj_18 = {};
    wp::vec_t<3, wp::float32> adj_19 = {};
    wp::vec_t<3, wp::float32> adj_20 = {};
    wp::vec_t<3, wp::float32> adj_21 = {};
    wp::vec_t<3, wp::float32> adj_22 = {};
    wp::vec_t<3, wp::float32> adj_23 = {};
    wp::vec_t<3, wp::float32> adj_24 = {};
    wp::vec_t<3, wp::float32> adj_25 = {};
    wp::vec_t<3, wp::float32> adj_26 = {};
    wp::vec_t<3, wp::float32> adj_27 = {};
    wp::vec_t<3, wp::float32> adj_28 = {};
    wp::vec_t<3, wp::float32> adj_29 = {};
    wp::vec_t<3, wp::float32> adj_30 = {};
    wp::vec_t<3, wp::float32> adj_31 = {};
    wp::vec_t<3, wp::float32> adj_32 = {};
    wp::vec_t<3, wp::float32> adj_33 = {};
    wp::vec_t<3, wp::float32> adj_34 = {};
    wp::vec_t<3, wp::float32> adj_35 = {};
    wp::vec_t<3, wp::float32> adj_36 = {};
    wp::vec_t<3, wp::float32> adj_37 = {};
    wp::vec_t<3, wp::float32> adj_38 = {};
    wp::vec_t<3, wp::float32> adj_39 = {};
    wp::vec_t<3, wp::float32> adj_40 = {};
    wp::vec_t<3, wp::float32> adj_41 = {};
    wp::vec_t<3, wp::float32> adj_42 = {};
    wp::vec_t<3, wp::float32> adj_43 = {};
    //---------
    // forward
    // def set_forces_to_dual_buffers_index(                                                  <L 1>
    // tid_env, tid_body = wp.tid()                                                           <L 25>
    builtin_tid2d(var_0, var_1);
    // ei = wp.int32(env_ids[tid_env])                                                        <L 26>
    var_2 = wp::address(var_env_ids, var_0);
    var_4 = wp::load(var_2);
    var_3 = wp::int32(var_4);
    // bi = wp.int32(body_ids[tid_body])                                                      <L 27>
    var_5 = wp::address(var_body_ids, var_1);
    var_7 = wp::load(var_5);
    var_6 = wp::int32(var_7);
    // if is_global:                                                                          <L 29>
    if (var_is_global) {
        // if torques:                                                                        <L 30>
        if (var_torques) {
            // global_torque_w[ei, bi] = torques[tid_env, tid_body]                           <L 31>
            var_8 = wp::address(var_torques, var_0, var_1);
            var_9 = wp::load(var_8);
            // wp::array_store(var_global_torque_w, var_3, var_6, var_9);
        }
        // if forces:                                                                         <L 32>
        if (var_forces) {
            // if positions:                                                                  <L 33>
            if (var_positions) {
                // global_force_w[ei, bi] = forces[tid_env, tid_body]                         <L 34>
                var_10 = wp::address(var_forces, var_0, var_1);
                var_11 = wp::load(var_10);
                // wp::array_store(var_global_force_w, var_3, var_6, var_11);
                // if torques:                                                                <L 35>
                if (var_torques) {
                    // global_torque_w[ei, bi] = global_torque_w[ei, bi] + wp.cross(          <L 36>
                    var_12 = wp::address(var_global_torque_w, var_3, var_6);
                    // positions[tid_env, tid_body], forces[tid_env, tid_body]                <L 37>
                    var_13 = wp::address(var_positions, var_0, var_1);
                    var_14 = wp::address(var_forces, var_0, var_1);
                    var_16 = wp::load(var_13);
                    var_17 = wp::load(var_14);
                    var_15 = wp::cross(var_16, var_17);
                    var_19 = wp::load(var_12);
                    var_18 = wp::add(var_19, var_15);
                    // global_torque_w[ei, bi] = global_torque_w[ei, bi] + wp.cross(          <L 36>
                    // wp::array_store(var_global_torque_w, var_3, var_6, var_18);
                }
                if (!var_torques) {
                    // global_torque_w[ei, bi] = wp.cross(positions[tid_env, tid_body], forces[tid_env, tid_body])       <L 40>
                    var_20 = wp::address(var_positions, var_0, var_1);
                    var_21 = wp::address(var_forces, var_0, var_1);
                    var_23 = wp::load(var_20);
                    var_24 = wp::load(var_21);
                    var_22 = wp::cross(var_23, var_24);
                    // wp::array_store(var_global_torque_w, var_3, var_6, var_22);
                }
            }
            if (!var_positions) {
                // global_force_at_com_w[ei, bi] = forces[tid_env, tid_body]                  <L 42>
                var_25 = wp::address(var_forces, var_0, var_1);
                var_26 = wp::load(var_25);
                // wp::array_store(var_global_force_at_com_w, var_3, var_6, var_26);
            }
        }
    }
    if (!var_is_global) {
        // if torques:                                                                        <L 44>
        if (var_torques) {
            // local_torque_b[ei, bi] = torques[tid_env, tid_body]                            <L 45>
            var_27 = wp::address(var_torques, var_0, var_1);
            var_28 = wp::load(var_27);
            // wp::array_store(var_local_torque_b, var_3, var_6, var_28);
        }
        // if forces:                                                                         <L 46>
        if (var_forces) {
            // local_force_b[ei, bi] = forces[tid_env, tid_body]                              <L 47>
            var_29 = wp::address(var_forces, var_0, var_1);
            var_30 = wp::load(var_29);
            // wp::array_store(var_local_force_b, var_3, var_6, var_30);
            // if positions:                                                                  <L 48>
            if (var_positions) {
                // if torques:                                                                <L 49>
                if (var_torques) {
                    // local_torque_b[ei, bi] = local_torque_b[ei, bi] + wp.cross(            <L 50>
                    var_31 = wp::address(var_local_torque_b, var_3, var_6);
                    // positions[tid_env, tid_body], forces[tid_env, tid_body]                <L 51>
                    var_32 = wp::address(var_positions, var_0, var_1);
                    var_33 = wp::address(var_forces, var_0, var_1);
                    var_35 = wp::load(var_32);
                    var_36 = wp::load(var_33);
                    var_34 = wp::cross(var_35, var_36);
                    var_38 = wp::load(var_31);
                    var_37 = wp::add(var_38, var_34);
                    // local_torque_b[ei, bi] = local_torque_b[ei, bi] + wp.cross(            <L 50>
                    // wp::array_store(var_local_torque_b, var_3, var_6, var_37);
                }
                if (!var_torques) {
                    // local_torque_b[ei, bi] = wp.cross(positions[tid_env, tid_body], forces[tid_env, tid_body])       <L 54>
                    var_39 = wp::address(var_positions, var_0, var_1);
                    var_40 = wp::address(var_forces, var_0, var_1);
                    var_42 = wp::load(var_39);
                    var_43 = wp::load(var_40);
                    var_41 = wp::cross(var_42, var_43);
                    // wp::array_store(var_local_torque_b, var_3, var_6, var_41);
                }
            }
        }
    }
    //---------
    // reverse
    if (!var_is_global) {
        if (var_forces) {
            if (var_positions) {
                if (!var_torques) {
                    wp::adj_array_store(var_local_torque_b, var_3, var_6, var_41, adj_local_torque_b, adj_3, adj_6, adj_41);
                    wp::adj_cross(var_42, var_43, adj_39, adj_40, adj_41);
                    wp::adj_address(var_forces, var_0, var_1, adj_forces, adj_0, adj_1, adj_40);
                    wp::adj_address(var_positions, var_0, var_1, adj_positions, adj_0, adj_1, adj_39);
                    // adj: local_torque_b[ei, bi] = wp.cross(positions[tid_env, tid_body], forces[tid_env, tid_body])  <L 54>
                }
                if (var_torques) {
                    wp::adj_array_store(var_local_torque_b, var_3, var_6, var_37, adj_local_torque_b, adj_3, adj_6, adj_37);
                    // adj: local_torque_b[ei, bi] = local_torque_b[ei, bi] + wp.cross(       <L 50>
                    wp::adj_add(var_38, var_34, adj_31, adj_34, adj_37);
                    wp::adj_cross(var_35, var_36, adj_32, adj_33, adj_34);
                    wp::adj_address(var_forces, var_0, var_1, adj_forces, adj_0, adj_1, adj_33);
                    wp::adj_address(var_positions, var_0, var_1, adj_positions, adj_0, adj_1, adj_32);
                    // adj: positions[tid_env, tid_body], forces[tid_env, tid_body]           <L 51>
                    wp::adj_address(var_local_torque_b, var_3, var_6, adj_local_torque_b, adj_3, adj_6, adj_31);
                    // adj: local_torque_b[ei, bi] = local_torque_b[ei, bi] + wp.cross(       <L 50>
                }
                // adj: if torques:                                                           <L 49>
            }
            // adj: if positions:                                                             <L 48>
            wp::adj_array_store(var_local_force_b, var_3, var_6, var_30, adj_local_force_b, adj_3, adj_6, adj_29);
            wp::adj_address(var_forces, var_0, var_1, adj_forces, adj_0, adj_1, adj_29);
            // adj: local_force_b[ei, bi] = forces[tid_env, tid_body]                         <L 47>
        }
        // adj: if forces:                                                                    <L 46>
        if (var_torques) {
            wp::adj_array_store(var_local_torque_b, var_3, var_6, var_28, adj_local_torque_b, adj_3, adj_6, adj_27);
            wp::adj_address(var_torques, var_0, var_1, adj_torques, adj_0, adj_1, adj_27);
            // adj: local_torque_b[ei, bi] = torques[tid_env, tid_body]                       <L 45>
        }
        // adj: if torques:                                                                   <L 44>
    }
    if (var_is_global) {
        if (var_forces) {
            if (!var_positions) {
                wp::adj_array_store(var_global_force_at_com_w, var_3, var_6, var_26, adj_global_force_at_com_w, adj_3, adj_6, adj_25);
                wp::adj_address(var_forces, var_0, var_1, adj_forces, adj_0, adj_1, adj_25);
                // adj: global_force_at_com_w[ei, bi] = forces[tid_env, tid_body]             <L 42>
            }
            if (var_positions) {
                if (!var_torques) {
                    wp::adj_array_store(var_global_torque_w, var_3, var_6, var_22, adj_global_torque_w, adj_3, adj_6, adj_22);
                    wp::adj_cross(var_23, var_24, adj_20, adj_21, adj_22);
                    wp::adj_address(var_forces, var_0, var_1, adj_forces, adj_0, adj_1, adj_21);
                    wp::adj_address(var_positions, var_0, var_1, adj_positions, adj_0, adj_1, adj_20);
                    // adj: global_torque_w[ei, bi] = wp.cross(positions[tid_env, tid_body], forces[tid_env, tid_body])  <L 40>
                }
                if (var_torques) {
                    wp::adj_array_store(var_global_torque_w, var_3, var_6, var_18, adj_global_torque_w, adj_3, adj_6, adj_18);
                    // adj: global_torque_w[ei, bi] = global_torque_w[ei, bi] + wp.cross(     <L 36>
                    wp::adj_add(var_19, var_15, adj_12, adj_15, adj_18);
                    wp::adj_cross(var_16, var_17, adj_13, adj_14, adj_15);
                    wp::adj_address(var_forces, var_0, var_1, adj_forces, adj_0, adj_1, adj_14);
                    wp::adj_address(var_positions, var_0, var_1, adj_positions, adj_0, adj_1, adj_13);
                    // adj: positions[tid_env, tid_body], forces[tid_env, tid_body]           <L 37>
                    wp::adj_address(var_global_torque_w, var_3, var_6, adj_global_torque_w, adj_3, adj_6, adj_12);
                    // adj: global_torque_w[ei, bi] = global_torque_w[ei, bi] + wp.cross(     <L 36>
                }
                // adj: if torques:                                                           <L 35>
                wp::adj_array_store(var_global_force_w, var_3, var_6, var_11, adj_global_force_w, adj_3, adj_6, adj_10);
                wp::adj_address(var_forces, var_0, var_1, adj_forces, adj_0, adj_1, adj_10);
                // adj: global_force_w[ei, bi] = forces[tid_env, tid_body]                    <L 34>
            }
            // adj: if positions:                                                             <L 33>
        }
        // adj: if forces:                                                                    <L 32>
        if (var_torques) {
            wp::adj_array_store(var_global_torque_w, var_3, var_6, var_9, adj_global_torque_w, adj_3, adj_6, adj_8);
            wp::adj_address(var_torques, var_0, var_1, adj_torques, adj_0, adj_1, adj_8);
            // adj: global_torque_w[ei, bi] = torques[tid_env, tid_body]                      <L 31>
        }
        // adj: if torques:                                                                   <L 30>
    }
    // adj: if is_global:                                                                     <L 29>
    wp::adj_address(var_body_ids, var_1, adj_body_ids, adj_1, adj_5);
    // adj: bi = wp.int32(body_ids[tid_body])                                                 <L 27>
    wp::adj_address(var_env_ids, var_0, adj_env_ids, adj_0, adj_2);
    // adj: ei = wp.int32(env_ids[tid_env])                                                   <L 26>
    // adj: tid_env, tid_body = wp.tid()                                                      <L 25>
    // adj: def set_forces_to_dual_buffers_index(                                             <L 1>
    return;
}



extern "C" {

// Python CPU entry points
WP_API void set_forces_to_dual_buffers_index_3e4a4295_cpu_forward(
    wp::launch_bounds_t<2> *dim,
    wp_args_set_forces_to_dual_buffers_index_3e4a4295 *_wp_args)
{
    wp::tile_shared_storage_t tile_mem;
#if defined(WP_ENABLE_TILES_IN_STACK_MEMORY)
    wp::shared_tile_storage = &tile_mem;
#endif

    for (size_t task_index = 0; task_index < dim->size; ++task_index)
    {
        set_forces_to_dual_buffers_index_3e4a4295_cpu_kernel_forward(*dim, task_index, _wp_args);
    }
}

} // extern C



extern "C" {

WP_API void set_forces_to_dual_buffers_index_3e4a4295_cpu_backward(
    wp::launch_bounds_t<2> *dim,
    wp_args_set_forces_to_dual_buffers_index_3e4a4295 *_wp_args,
    wp_args_set_forces_to_dual_buffers_index_3e4a4295 *_wp_adj_args)
{
    wp::tile_shared_storage_t tile_mem;
#if defined(WP_ENABLE_TILES_IN_STACK_MEMORY)
    wp::shared_tile_storage = &tile_mem;
#endif

    for (size_t task_index = 0; task_index < dim->size; ++task_index)
    {
        set_forces_to_dual_buffers_index_3e4a4295_cpu_kernel_backward(*dim, task_index, _wp_args, _wp_adj_args);
    }
}

} // extern C

struct wp_args_add_raw_wrench_buffers_4ab44a2b {
    wp::array_t<wp::vec_t<3, wp::float32>> src_gf;
    wp::array_t<wp::vec_t<3, wp::float32>> src_gt;
    wp::array_t<wp::vec_t<3, wp::float32>> src_gfc;
    wp::array_t<wp::vec_t<3, wp::float32>> src_lf;
    wp::array_t<wp::vec_t<3, wp::float32>> src_lt;
    wp::array_t<wp::vec_t<3, wp::float32>> dst_gf;
    wp::array_t<wp::vec_t<3, wp::float32>> dst_gt;
    wp::array_t<wp::vec_t<3, wp::float32>> dst_gfc;
    wp::array_t<wp::vec_t<3, wp::float32>> dst_lf;
    wp::array_t<wp::vec_t<3, wp::float32>> dst_lt;
};


void add_raw_wrench_buffers_4ab44a2b_cpu_kernel_forward(
    wp::launch_bounds_t<2> dim,
    size_t task_index,
    wp_args_add_raw_wrench_buffers_4ab44a2b *_wp_args)
{
    //---------
    // argument vars
    wp::array_t<wp::vec_t<3, wp::float32>> var_src_gf = _wp_args->src_gf;
    wp::array_t<wp::vec_t<3, wp::float32>> var_src_gt = _wp_args->src_gt;
    wp::array_t<wp::vec_t<3, wp::float32>> var_src_gfc = _wp_args->src_gfc;
    wp::array_t<wp::vec_t<3, wp::float32>> var_src_lf = _wp_args->src_lf;
    wp::array_t<wp::vec_t<3, wp::float32>> var_src_lt = _wp_args->src_lt;
    wp::array_t<wp::vec_t<3, wp::float32>> var_dst_gf = _wp_args->dst_gf;
    wp::array_t<wp::vec_t<3, wp::float32>> var_dst_gt = _wp_args->dst_gt;
    wp::array_t<wp::vec_t<3, wp::float32>> var_dst_gfc = _wp_args->dst_gfc;
    wp::array_t<wp::vec_t<3, wp::float32>> var_dst_lf = _wp_args->dst_lf;
    wp::array_t<wp::vec_t<3, wp::float32>> var_dst_lt = _wp_args->dst_lt;
    //---------
    // primal vars
    wp::int32 var_0;
    wp::int32 var_1;
    wp::vec_t<3, wp::float32>* var_2;
    wp::vec_t<3, wp::float32>* var_3;
    wp::vec_t<3, wp::float32> var_4;
    wp::vec_t<3, wp::float32> var_5;
    wp::vec_t<3, wp::float32> var_6;
    wp::vec_t<3, wp::float32>* var_7;
    wp::vec_t<3, wp::float32>* var_8;
    wp::vec_t<3, wp::float32> var_9;
    wp::vec_t<3, wp::float32> var_10;
    wp::vec_t<3, wp::float32> var_11;
    wp::vec_t<3, wp::float32>* var_12;
    wp::vec_t<3, wp::float32>* var_13;
    wp::vec_t<3, wp::float32> var_14;
    wp::vec_t<3, wp::float32> var_15;
    wp::vec_t<3, wp::float32> var_16;
    wp::vec_t<3, wp::float32>* var_17;
    wp::vec_t<3, wp::float32>* var_18;
    wp::vec_t<3, wp::float32> var_19;
    wp::vec_t<3, wp::float32> var_20;
    wp::vec_t<3, wp::float32> var_21;
    wp::vec_t<3, wp::float32>* var_22;
    wp::vec_t<3, wp::float32>* var_23;
    wp::vec_t<3, wp::float32> var_24;
    wp::vec_t<3, wp::float32> var_25;
    wp::vec_t<3, wp::float32> var_26;
    //---------
    // forward
    // def add_raw_wrench_buffers(                                                            <L 602>
    // tid_env, tid_body = wp.tid()                                                           <L 620>
    builtin_tid2d(var_0, var_1);
    // dst_gf[tid_env, tid_body] = dst_gf[tid_env, tid_body] + src_gf[tid_env, tid_body]       <L 621>
    var_2 = wp::address(var_dst_gf, var_0, var_1);
    var_3 = wp::address(var_src_gf, var_0, var_1);
    var_5 = wp::load(var_2);
    var_6 = wp::load(var_3);
    var_4 = wp::add(var_5, var_6);
    wp::array_store(var_dst_gf, var_0, var_1, var_4);
    // dst_gt[tid_env, tid_body] = dst_gt[tid_env, tid_body] + src_gt[tid_env, tid_body]       <L 622>
    var_7 = wp::address(var_dst_gt, var_0, var_1);
    var_8 = wp::address(var_src_gt, var_0, var_1);
    var_10 = wp::load(var_7);
    var_11 = wp::load(var_8);
    var_9 = wp::add(var_10, var_11);
    wp::array_store(var_dst_gt, var_0, var_1, var_9);
    // dst_gfc[tid_env, tid_body] = dst_gfc[tid_env, tid_body] + src_gfc[tid_env, tid_body]       <L 623>
    var_12 = wp::address(var_dst_gfc, var_0, var_1);
    var_13 = wp::address(var_src_gfc, var_0, var_1);
    var_15 = wp::load(var_12);
    var_16 = wp::load(var_13);
    var_14 = wp::add(var_15, var_16);
    wp::array_store(var_dst_gfc, var_0, var_1, var_14);
    // dst_lf[tid_env, tid_body] = dst_lf[tid_env, tid_body] + src_lf[tid_env, tid_body]       <L 624>
    var_17 = wp::address(var_dst_lf, var_0, var_1);
    var_18 = wp::address(var_src_lf, var_0, var_1);
    var_20 = wp::load(var_17);
    var_21 = wp::load(var_18);
    var_19 = wp::add(var_20, var_21);
    wp::array_store(var_dst_lf, var_0, var_1, var_19);
    // dst_lt[tid_env, tid_body] = dst_lt[tid_env, tid_body] + src_lt[tid_env, tid_body]       <L 625>
    var_22 = wp::address(var_dst_lt, var_0, var_1);
    var_23 = wp::address(var_src_lt, var_0, var_1);
    var_25 = wp::load(var_22);
    var_26 = wp::load(var_23);
    var_24 = wp::add(var_25, var_26);
    wp::array_store(var_dst_lt, var_0, var_1, var_24);
}



void add_raw_wrench_buffers_4ab44a2b_cpu_kernel_backward(
    wp::launch_bounds_t<2> dim,
    size_t task_index,
    wp_args_add_raw_wrench_buffers_4ab44a2b *_wp_args,
    wp_args_add_raw_wrench_buffers_4ab44a2b *_wp_adj_args)
{
    //---------
    // argument vars
    wp::array_t<wp::vec_t<3, wp::float32>> var_src_gf = _wp_args->src_gf;
    wp::array_t<wp::vec_t<3, wp::float32>> var_src_gt = _wp_args->src_gt;
    wp::array_t<wp::vec_t<3, wp::float32>> var_src_gfc = _wp_args->src_gfc;
    wp::array_t<wp::vec_t<3, wp::float32>> var_src_lf = _wp_args->src_lf;
    wp::array_t<wp::vec_t<3, wp::float32>> var_src_lt = _wp_args->src_lt;
    wp::array_t<wp::vec_t<3, wp::float32>> var_dst_gf = _wp_args->dst_gf;
    wp::array_t<wp::vec_t<3, wp::float32>> var_dst_gt = _wp_args->dst_gt;
    wp::array_t<wp::vec_t<3, wp::float32>> var_dst_gfc = _wp_args->dst_gfc;
    wp::array_t<wp::vec_t<3, wp::float32>> var_dst_lf = _wp_args->dst_lf;
    wp::array_t<wp::vec_t<3, wp::float32>> var_dst_lt = _wp_args->dst_lt;
    wp::array_t<wp::vec_t<3, wp::float32>> adj_src_gf = _wp_adj_args->src_gf;
    wp::array_t<wp::vec_t<3, wp::float32>> adj_src_gt = _wp_adj_args->src_gt;
    wp::array_t<wp::vec_t<3, wp::float32>> adj_src_gfc = _wp_adj_args->src_gfc;
    wp::array_t<wp::vec_t<3, wp::float32>> adj_src_lf = _wp_adj_args->src_lf;
    wp::array_t<wp::vec_t<3, wp::float32>> adj_src_lt = _wp_adj_args->src_lt;
    wp::array_t<wp::vec_t<3, wp::float32>> adj_dst_gf = _wp_adj_args->dst_gf;
    wp::array_t<wp::vec_t<3, wp::float32>> adj_dst_gt = _wp_adj_args->dst_gt;
    wp::array_t<wp::vec_t<3, wp::float32>> adj_dst_gfc = _wp_adj_args->dst_gfc;
    wp::array_t<wp::vec_t<3, wp::float32>> adj_dst_lf = _wp_adj_args->dst_lf;
    wp::array_t<wp::vec_t<3, wp::float32>> adj_dst_lt = _wp_adj_args->dst_lt;
    //---------
    // primal vars
    wp::int32 var_0;
    wp::int32 var_1;
    wp::vec_t<3, wp::float32>* var_2;
    wp::vec_t<3, wp::float32>* var_3;
    wp::vec_t<3, wp::float32> var_4;
    wp::vec_t<3, wp::float32> var_5;
    wp::vec_t<3, wp::float32> var_6;
    wp::vec_t<3, wp::float32>* var_7;
    wp::vec_t<3, wp::float32>* var_8;
    wp::vec_t<3, wp::float32> var_9;
    wp::vec_t<3, wp::float32> var_10;
    wp::vec_t<3, wp::float32> var_11;
    wp::vec_t<3, wp::float32>* var_12;
    wp::vec_t<3, wp::float32>* var_13;
    wp::vec_t<3, wp::float32> var_14;
    wp::vec_t<3, wp::float32> var_15;
    wp::vec_t<3, wp::float32> var_16;
    wp::vec_t<3, wp::float32>* var_17;
    wp::vec_t<3, wp::float32>* var_18;
    wp::vec_t<3, wp::float32> var_19;
    wp::vec_t<3, wp::float32> var_20;
    wp::vec_t<3, wp::float32> var_21;
    wp::vec_t<3, wp::float32>* var_22;
    wp::vec_t<3, wp::float32>* var_23;
    wp::vec_t<3, wp::float32> var_24;
    wp::vec_t<3, wp::float32> var_25;
    wp::vec_t<3, wp::float32> var_26;
    //---------
    // dual vars
    wp::int32 adj_0 = {};
    wp::int32 adj_1 = {};
    wp::vec_t<3, wp::float32> adj_2 = {};
    wp::vec_t<3, wp::float32> adj_3 = {};
    wp::vec_t<3, wp::float32> adj_4 = {};
    wp::vec_t<3, wp::float32> adj_5 = {};
    wp::vec_t<3, wp::float32> adj_6 = {};
    wp::vec_t<3, wp::float32> adj_7 = {};
    wp::vec_t<3, wp::float32> adj_8 = {};
    wp::vec_t<3, wp::float32> adj_9 = {};
    wp::vec_t<3, wp::float32> adj_10 = {};
    wp::vec_t<3, wp::float32> adj_11 = {};
    wp::vec_t<3, wp::float32> adj_12 = {};
    wp::vec_t<3, wp::float32> adj_13 = {};
    wp::vec_t<3, wp::float32> adj_14 = {};
    wp::vec_t<3, wp::float32> adj_15 = {};
    wp::vec_t<3, wp::float32> adj_16 = {};
    wp::vec_t<3, wp::float32> adj_17 = {};
    wp::vec_t<3, wp::float32> adj_18 = {};
    wp::vec_t<3, wp::float32> adj_19 = {};
    wp::vec_t<3, wp::float32> adj_20 = {};
    wp::vec_t<3, wp::float32> adj_21 = {};
    wp::vec_t<3, wp::float32> adj_22 = {};
    wp::vec_t<3, wp::float32> adj_23 = {};
    wp::vec_t<3, wp::float32> adj_24 = {};
    wp::vec_t<3, wp::float32> adj_25 = {};
    wp::vec_t<3, wp::float32> adj_26 = {};
    //---------
    // forward
    // def add_raw_wrench_buffers(                                                            <L 602>
    // tid_env, tid_body = wp.tid()                                                           <L 620>
    builtin_tid2d(var_0, var_1);
    // dst_gf[tid_env, tid_body] = dst_gf[tid_env, tid_body] + src_gf[tid_env, tid_body]       <L 621>
    var_2 = wp::address(var_dst_gf, var_0, var_1);
    var_3 = wp::address(var_src_gf, var_0, var_1);
    var_5 = wp::load(var_2);
    var_6 = wp::load(var_3);
    var_4 = wp::add(var_5, var_6);
    // wp::array_store(var_dst_gf, var_0, var_1, var_4);
    // dst_gt[tid_env, tid_body] = dst_gt[tid_env, tid_body] + src_gt[tid_env, tid_body]       <L 622>
    var_7 = wp::address(var_dst_gt, var_0, var_1);
    var_8 = wp::address(var_src_gt, var_0, var_1);
    var_10 = wp::load(var_7);
    var_11 = wp::load(var_8);
    var_9 = wp::add(var_10, var_11);
    // wp::array_store(var_dst_gt, var_0, var_1, var_9);
    // dst_gfc[tid_env, tid_body] = dst_gfc[tid_env, tid_body] + src_gfc[tid_env, tid_body]       <L 623>
    var_12 = wp::address(var_dst_gfc, var_0, var_1);
    var_13 = wp::address(var_src_gfc, var_0, var_1);
    var_15 = wp::load(var_12);
    var_16 = wp::load(var_13);
    var_14 = wp::add(var_15, var_16);
    // wp::array_store(var_dst_gfc, var_0, var_1, var_14);
    // dst_lf[tid_env, tid_body] = dst_lf[tid_env, tid_body] + src_lf[tid_env, tid_body]       <L 624>
    var_17 = wp::address(var_dst_lf, var_0, var_1);
    var_18 = wp::address(var_src_lf, var_0, var_1);
    var_20 = wp::load(var_17);
    var_21 = wp::load(var_18);
    var_19 = wp::add(var_20, var_21);
    // wp::array_store(var_dst_lf, var_0, var_1, var_19);
    // dst_lt[tid_env, tid_body] = dst_lt[tid_env, tid_body] + src_lt[tid_env, tid_body]       <L 625>
    var_22 = wp::address(var_dst_lt, var_0, var_1);
    var_23 = wp::address(var_src_lt, var_0, var_1);
    var_25 = wp::load(var_22);
    var_26 = wp::load(var_23);
    var_24 = wp::add(var_25, var_26);
    // wp::array_store(var_dst_lt, var_0, var_1, var_24);
    //---------
    // reverse
    wp::adj_array_store(var_dst_lt, var_0, var_1, var_24, adj_dst_lt, adj_0, adj_1, adj_24);
    wp::adj_add(var_25, var_26, adj_22, adj_23, adj_24);
    wp::adj_address(var_src_lt, var_0, var_1, adj_src_lt, adj_0, adj_1, adj_23);
    wp::adj_address(var_dst_lt, var_0, var_1, adj_dst_lt, adj_0, adj_1, adj_22);
    // adj: dst_lt[tid_env, tid_body] = dst_lt[tid_env, tid_body] + src_lt[tid_env, tid_body]  <L 625>
    wp::adj_array_store(var_dst_lf, var_0, var_1, var_19, adj_dst_lf, adj_0, adj_1, adj_19);
    wp::adj_add(var_20, var_21, adj_17, adj_18, adj_19);
    wp::adj_address(var_src_lf, var_0, var_1, adj_src_lf, adj_0, adj_1, adj_18);
    wp::adj_address(var_dst_lf, var_0, var_1, adj_dst_lf, adj_0, adj_1, adj_17);
    // adj: dst_lf[tid_env, tid_body] = dst_lf[tid_env, tid_body] + src_lf[tid_env, tid_body]  <L 624>
    wp::adj_array_store(var_dst_gfc, var_0, var_1, var_14, adj_dst_gfc, adj_0, adj_1, adj_14);
    wp::adj_add(var_15, var_16, adj_12, adj_13, adj_14);
    wp::adj_address(var_src_gfc, var_0, var_1, adj_src_gfc, adj_0, adj_1, adj_13);
    wp::adj_address(var_dst_gfc, var_0, var_1, adj_dst_gfc, adj_0, adj_1, adj_12);
    // adj: dst_gfc[tid_env, tid_body] = dst_gfc[tid_env, tid_body] + src_gfc[tid_env, tid_body]  <L 623>
    wp::adj_array_store(var_dst_gt, var_0, var_1, var_9, adj_dst_gt, adj_0, adj_1, adj_9);
    wp::adj_add(var_10, var_11, adj_7, adj_8, adj_9);
    wp::adj_address(var_src_gt, var_0, var_1, adj_src_gt, adj_0, adj_1, adj_8);
    wp::adj_address(var_dst_gt, var_0, var_1, adj_dst_gt, adj_0, adj_1, adj_7);
    // adj: dst_gt[tid_env, tid_body] = dst_gt[tid_env, tid_body] + src_gt[tid_env, tid_body]  <L 622>
    wp::adj_array_store(var_dst_gf, var_0, var_1, var_4, adj_dst_gf, adj_0, adj_1, adj_4);
    wp::adj_add(var_5, var_6, adj_2, adj_3, adj_4);
    wp::adj_address(var_src_gf, var_0, var_1, adj_src_gf, adj_0, adj_1, adj_3);
    wp::adj_address(var_dst_gf, var_0, var_1, adj_dst_gf, adj_0, adj_1, adj_2);
    // adj: dst_gf[tid_env, tid_body] = dst_gf[tid_env, tid_body] + src_gf[tid_env, tid_body]  <L 621>
    // adj: tid_env, tid_body = wp.tid()                                                      <L 620>
    // adj: def add_raw_wrench_buffers(                                                       <L 602>
    return;
}



extern "C" {

// Python CPU entry points
WP_API void add_raw_wrench_buffers_4ab44a2b_cpu_forward(
    wp::launch_bounds_t<2> *dim,
    wp_args_add_raw_wrench_buffers_4ab44a2b *_wp_args)
{
    wp::tile_shared_storage_t tile_mem;
#if defined(WP_ENABLE_TILES_IN_STACK_MEMORY)
    wp::shared_tile_storage = &tile_mem;
#endif

    for (size_t task_index = 0; task_index < dim->size; ++task_index)
    {
        add_raw_wrench_buffers_4ab44a2b_cpu_kernel_forward(*dim, task_index, _wp_args);
    }
}

} // extern C



extern "C" {

WP_API void add_raw_wrench_buffers_4ab44a2b_cpu_backward(
    wp::launch_bounds_t<2> *dim,
    wp_args_add_raw_wrench_buffers_4ab44a2b *_wp_args,
    wp_args_add_raw_wrench_buffers_4ab44a2b *_wp_adj_args)
{
    wp::tile_shared_storage_t tile_mem;
#if defined(WP_ENABLE_TILES_IN_STACK_MEMORY)
    wp::shared_tile_storage = &tile_mem;
#endif

    for (size_t task_index = 0; task_index < dim->size; ++task_index)
    {
        add_raw_wrench_buffers_4ab44a2b_cpu_kernel_backward(*dim, task_index, _wp_args, _wp_adj_args);
    }
}

} // extern C

struct wp_args_reset_wrench_composer_index_4b6bf2f5 {
    wp::array_t<wp::int32> env_ids;
    wp::array_t<wp::vec_t<3, wp::float32>> global_force_w;
    wp::array_t<wp::vec_t<3, wp::float32>> global_torque_w;
    wp::array_t<wp::vec_t<3, wp::float32>> global_force_at_com_w;
    wp::array_t<wp::vec_t<3, wp::float32>> local_force_b;
    wp::array_t<wp::vec_t<3, wp::float32>> local_torque_b;
    wp::array_t<wp::vec_t<3, wp::float32>> out_force_b;
    wp::array_t<wp::vec_t<3, wp::float32>> out_torque_b;
};


void reset_wrench_composer_index_4b6bf2f5_cpu_kernel_forward(
    wp::launch_bounds_t<2> dim,
    size_t task_index,
    wp_args_reset_wrench_composer_index_4b6bf2f5 *_wp_args)
{
    //---------
    // argument vars
    wp::array_t<wp::int32> var_env_ids = _wp_args->env_ids;
    wp::array_t<wp::vec_t<3, wp::float32>> var_global_force_w = _wp_args->global_force_w;
    wp::array_t<wp::vec_t<3, wp::float32>> var_global_torque_w = _wp_args->global_torque_w;
    wp::array_t<wp::vec_t<3, wp::float32>> var_global_force_at_com_w = _wp_args->global_force_at_com_w;
    wp::array_t<wp::vec_t<3, wp::float32>> var_local_force_b = _wp_args->local_force_b;
    wp::array_t<wp::vec_t<3, wp::float32>> var_local_torque_b = _wp_args->local_torque_b;
    wp::array_t<wp::vec_t<3, wp::float32>> var_out_force_b = _wp_args->out_force_b;
    wp::array_t<wp::vec_t<3, wp::float32>> var_out_torque_b = _wp_args->out_torque_b;
    //---------
    // primal vars
    wp::int32 var_0;
    wp::int32 var_1;
    wp::int32* var_2;
    wp::int32 var_3;
    wp::int32 var_4;
    const wp::float32 var_5 = 0.0;
    wp::vec_t<3, wp::float32> var_6;
    //---------
    // forward
    // def reset_wrench_composer_index(                                                       <L 1>
    // tid_env, tid_body = wp.tid()                                                           <L 15>
    builtin_tid2d(var_0, var_1);
    // ei = wp.int32(env_ids[tid_env])                                                        <L 16>
    var_2 = wp::address(var_env_ids, var_0);
    var_4 = wp::load(var_2);
    var_3 = wp::int32(var_4);
    // z = wp.vec3f(0.0)                                                                      <L 17>
    var_6 = wp::vec_t<3, wp::float32>(var_5);
    // global_force_w[ei, tid_body] = z                                                       <L 18>
    wp::array_store(var_global_force_w, var_3, var_1, var_6);
    // global_torque_w[ei, tid_body] = z                                                      <L 19>
    wp::array_store(var_global_torque_w, var_3, var_1, var_6);
    // global_force_at_com_w[ei, tid_body] = z                                                <L 20>
    wp::array_store(var_global_force_at_com_w, var_3, var_1, var_6);
    // local_force_b[ei, tid_body] = z                                                        <L 21>
    wp::array_store(var_local_force_b, var_3, var_1, var_6);
    // local_torque_b[ei, tid_body] = z                                                       <L 22>
    wp::array_store(var_local_torque_b, var_3, var_1, var_6);
    // out_force_b[ei, tid_body] = z                                                          <L 23>
    wp::array_store(var_out_force_b, var_3, var_1, var_6);
    // out_torque_b[ei, tid_body] = z                                                         <L 24>
    wp::array_store(var_out_torque_b, var_3, var_1, var_6);
}



void reset_wrench_composer_index_4b6bf2f5_cpu_kernel_backward(
    wp::launch_bounds_t<2> dim,
    size_t task_index,
    wp_args_reset_wrench_composer_index_4b6bf2f5 *_wp_args,
    wp_args_reset_wrench_composer_index_4b6bf2f5 *_wp_adj_args)
{
    //---------
    // argument vars
    wp::array_t<wp::int32> var_env_ids = _wp_args->env_ids;
    wp::array_t<wp::vec_t<3, wp::float32>> var_global_force_w = _wp_args->global_force_w;
    wp::array_t<wp::vec_t<3, wp::float32>> var_global_torque_w = _wp_args->global_torque_w;
    wp::array_t<wp::vec_t<3, wp::float32>> var_global_force_at_com_w = _wp_args->global_force_at_com_w;
    wp::array_t<wp::vec_t<3, wp::float32>> var_local_force_b = _wp_args->local_force_b;
    wp::array_t<wp::vec_t<3, wp::float32>> var_local_torque_b = _wp_args->local_torque_b;
    wp::array_t<wp::vec_t<3, wp::float32>> var_out_force_b = _wp_args->out_force_b;
    wp::array_t<wp::vec_t<3, wp::float32>> var_out_torque_b = _wp_args->out_torque_b;
    wp::array_t<wp::int32> adj_env_ids = _wp_adj_args->env_ids;
    wp::array_t<wp::vec_t<3, wp::float32>> adj_global_force_w = _wp_adj_args->global_force_w;
    wp::array_t<wp::vec_t<3, wp::float32>> adj_global_torque_w = _wp_adj_args->global_torque_w;
    wp::array_t<wp::vec_t<3, wp::float32>> adj_global_force_at_com_w = _wp_adj_args->global_force_at_com_w;
    wp::array_t<wp::vec_t<3, wp::float32>> adj_local_force_b = _wp_adj_args->local_force_b;
    wp::array_t<wp::vec_t<3, wp::float32>> adj_local_torque_b = _wp_adj_args->local_torque_b;
    wp::array_t<wp::vec_t<3, wp::float32>> adj_out_force_b = _wp_adj_args->out_force_b;
    wp::array_t<wp::vec_t<3, wp::float32>> adj_out_torque_b = _wp_adj_args->out_torque_b;
    //---------
    // primal vars
    wp::int32 var_0;
    wp::int32 var_1;
    wp::int32* var_2;
    wp::int32 var_3;
    wp::int32 var_4;
    const wp::float32 var_5 = 0.0;
    wp::vec_t<3, wp::float32> var_6;
    //---------
    // dual vars
    wp::int32 adj_0 = {};
    wp::int32 adj_1 = {};
    wp::int32 adj_2 = {};
    wp::int32 adj_3 = {};
    wp::int32 adj_4 = {};
    wp::float32 adj_5 = {};
    wp::vec_t<3, wp::float32> adj_6 = {};
    //---------
    // forward
    // def reset_wrench_composer_index(                                                       <L 1>
    // tid_env, tid_body = wp.tid()                                                           <L 15>
    builtin_tid2d(var_0, var_1);
    // ei = wp.int32(env_ids[tid_env])                                                        <L 16>
    var_2 = wp::address(var_env_ids, var_0);
    var_4 = wp::load(var_2);
    var_3 = wp::int32(var_4);
    // z = wp.vec3f(0.0)                                                                      <L 17>
    var_6 = wp::vec_t<3, wp::float32>(var_5);
    // global_force_w[ei, tid_body] = z                                                       <L 18>
    // wp::array_store(var_global_force_w, var_3, var_1, var_6);
    // global_torque_w[ei, tid_body] = z                                                      <L 19>
    // wp::array_store(var_global_torque_w, var_3, var_1, var_6);
    // global_force_at_com_w[ei, tid_body] = z                                                <L 20>
    // wp::array_store(var_global_force_at_com_w, var_3, var_1, var_6);
    // local_force_b[ei, tid_body] = z                                                        <L 21>
    // wp::array_store(var_local_force_b, var_3, var_1, var_6);
    // local_torque_b[ei, tid_body] = z                                                       <L 22>
    // wp::array_store(var_local_torque_b, var_3, var_1, var_6);
    // out_force_b[ei, tid_body] = z                                                          <L 23>
    // wp::array_store(var_out_force_b, var_3, var_1, var_6);
    // out_torque_b[ei, tid_body] = z                                                         <L 24>
    // wp::array_store(var_out_torque_b, var_3, var_1, var_6);
    //---------
    // reverse
    wp::adj_array_store(var_out_torque_b, var_3, var_1, var_6, adj_out_torque_b, adj_3, adj_1, adj_6);
    // adj: out_torque_b[ei, tid_body] = z                                                    <L 24>
    wp::adj_array_store(var_out_force_b, var_3, var_1, var_6, adj_out_force_b, adj_3, adj_1, adj_6);
    // adj: out_force_b[ei, tid_body] = z                                                     <L 23>
    wp::adj_array_store(var_local_torque_b, var_3, var_1, var_6, adj_local_torque_b, adj_3, adj_1, adj_6);
    // adj: local_torque_b[ei, tid_body] = z                                                  <L 22>
    wp::adj_array_store(var_local_force_b, var_3, var_1, var_6, adj_local_force_b, adj_3, adj_1, adj_6);
    // adj: local_force_b[ei, tid_body] = z                                                   <L 21>
    wp::adj_array_store(var_global_force_at_com_w, var_3, var_1, var_6, adj_global_force_at_com_w, adj_3, adj_1, adj_6);
    // adj: global_force_at_com_w[ei, tid_body] = z                                           <L 20>
    wp::adj_array_store(var_global_torque_w, var_3, var_1, var_6, adj_global_torque_w, adj_3, adj_1, adj_6);
    // adj: global_torque_w[ei, tid_body] = z                                                 <L 19>
    wp::adj_array_store(var_global_force_w, var_3, var_1, var_6, adj_global_force_w, adj_3, adj_1, adj_6);
    // adj: global_force_w[ei, tid_body] = z                                                  <L 18>
    wp::adj_vec_t(var_5, adj_5, adj_6);
    // adj: z = wp.vec3f(0.0)                                                                 <L 17>
    wp::adj_address(var_env_ids, var_0, adj_env_ids, adj_0, adj_2);
    // adj: ei = wp.int32(env_ids[tid_env])                                                   <L 16>
    // adj: tid_env, tid_body = wp.tid()                                                      <L 15>
    // adj: def reset_wrench_composer_index(                                                  <L 1>
    return;
}



extern "C" {

// Python CPU entry points
WP_API void reset_wrench_composer_index_4b6bf2f5_cpu_forward(
    wp::launch_bounds_t<2> *dim,
    wp_args_reset_wrench_composer_index_4b6bf2f5 *_wp_args)
{
    wp::tile_shared_storage_t tile_mem;
#if defined(WP_ENABLE_TILES_IN_STACK_MEMORY)
    wp::shared_tile_storage = &tile_mem;
#endif

    for (size_t task_index = 0; task_index < dim->size; ++task_index)
    {
        reset_wrench_composer_index_4b6bf2f5_cpu_kernel_forward(*dim, task_index, _wp_args);
    }
}

} // extern C



extern "C" {

WP_API void reset_wrench_composer_index_4b6bf2f5_cpu_backward(
    wp::launch_bounds_t<2> *dim,
    wp_args_reset_wrench_composer_index_4b6bf2f5 *_wp_args,
    wp_args_reset_wrench_composer_index_4b6bf2f5 *_wp_adj_args)
{
    wp::tile_shared_storage_t tile_mem;
#if defined(WP_ENABLE_TILES_IN_STACK_MEMORY)
    wp::shared_tile_storage = &tile_mem;
#endif

    for (size_t task_index = 0; task_index < dim->size; ++task_index)
    {
        reset_wrench_composer_index_4b6bf2f5_cpu_kernel_backward(*dim, task_index, _wp_args, _wp_adj_args);
    }
}

} // extern C

struct wp_args_gather_subtract_2d_4c8aec8a {
    wp::array_t<wp::float32> a;
    wp::array_t<wp::int64> env_ids;
    wp::array_t<wp::int32> item_ids;
    wp::array_t<wp::float32> b;
    wp::array_t<wp::float32> out;
};


void gather_subtract_2d_4c8aec8a_cpu_kernel_forward(
    wp::launch_bounds_t<2> dim,
    size_t task_index,
    wp_args_gather_subtract_2d_4c8aec8a *_wp_args)
{
    //---------
    // argument vars
    wp::array_t<wp::float32> var_a = _wp_args->a;
    wp::array_t<wp::int64> var_env_ids = _wp_args->env_ids;
    wp::array_t<wp::int32> var_item_ids = _wp_args->item_ids;
    wp::array_t<wp::float32> var_b = _wp_args->b;
    wp::array_t<wp::float32> var_out = _wp_args->out;
    //---------
    // primal vars
    wp::int32 var_0;
    wp::int32 var_1;
    wp::int64* var_2;
    wp::int32 var_3;
    wp::int64 var_4;
    wp::int32* var_5;
    wp::int32 var_6;
    wp::int32 var_7;
    wp::float32* var_8;
    wp::float32* var_9;
    wp::float32 var_10;
    wp::float32 var_11;
    wp::float32 var_12;
    //---------
    // forward
    // def gather_subtract_2d(                                                                <L 1>
    // i, j = wp.tid()                                                                        <L 17>
    builtin_tid2d(var_0, var_1);
    // out[i, j] = a[wp.int32(env_ids[i]), wp.int32(item_ids[j])] - b[i, j]                   <L 18>
    var_2 = wp::address(var_env_ids, var_0);
    var_4 = wp::load(var_2);
    var_3 = wp::int32(var_4);
    var_5 = wp::address(var_item_ids, var_1);
    var_7 = wp::load(var_5);
    var_6 = wp::int32(var_7);
    var_8 = wp::address(var_a, var_3, var_6);
    var_9 = wp::address(var_b, var_0, var_1);
    var_11 = wp::load(var_8);
    var_12 = wp::load(var_9);
    var_10 = wp::sub(var_11, var_12);
    wp::array_store(var_out, var_0, var_1, var_10);
}



void gather_subtract_2d_4c8aec8a_cpu_kernel_backward(
    wp::launch_bounds_t<2> dim,
    size_t task_index,
    wp_args_gather_subtract_2d_4c8aec8a *_wp_args,
    wp_args_gather_subtract_2d_4c8aec8a *_wp_adj_args)
{
    //---------
    // argument vars
    wp::array_t<wp::float32> var_a = _wp_args->a;
    wp::array_t<wp::int64> var_env_ids = _wp_args->env_ids;
    wp::array_t<wp::int32> var_item_ids = _wp_args->item_ids;
    wp::array_t<wp::float32> var_b = _wp_args->b;
    wp::array_t<wp::float32> var_out = _wp_args->out;
    wp::array_t<wp::float32> adj_a = _wp_adj_args->a;
    wp::array_t<wp::int64> adj_env_ids = _wp_adj_args->env_ids;
    wp::array_t<wp::int32> adj_item_ids = _wp_adj_args->item_ids;
    wp::array_t<wp::float32> adj_b = _wp_adj_args->b;
    wp::array_t<wp::float32> adj_out = _wp_adj_args->out;
    //---------
    // primal vars
    wp::int32 var_0;
    wp::int32 var_1;
    wp::int64* var_2;
    wp::int32 var_3;
    wp::int64 var_4;
    wp::int32* var_5;
    wp::int32 var_6;
    wp::int32 var_7;
    wp::float32* var_8;
    wp::float32* var_9;
    wp::float32 var_10;
    wp::float32 var_11;
    wp::float32 var_12;
    //---------
    // dual vars
    wp::int32 adj_0 = {};
    wp::int32 adj_1 = {};
    wp::int64 adj_2 = {};
    wp::int32 adj_3 = {};
    wp::int64 adj_4 = {};
    wp::int32 adj_5 = {};
    wp::int32 adj_6 = {};
    wp::int32 adj_7 = {};
    wp::float32 adj_8 = {};
    wp::float32 adj_9 = {};
    wp::float32 adj_10 = {};
    wp::float32 adj_11 = {};
    wp::float32 adj_12 = {};
    //---------
    // forward
    // def gather_subtract_2d(                                                                <L 1>
    // i, j = wp.tid()                                                                        <L 17>
    builtin_tid2d(var_0, var_1);
    // out[i, j] = a[wp.int32(env_ids[i]), wp.int32(item_ids[j])] - b[i, j]                   <L 18>
    var_2 = wp::address(var_env_ids, var_0);
    var_4 = wp::load(var_2);
    var_3 = wp::int32(var_4);
    var_5 = wp::address(var_item_ids, var_1);
    var_7 = wp::load(var_5);
    var_6 = wp::int32(var_7);
    var_8 = wp::address(var_a, var_3, var_6);
    var_9 = wp::address(var_b, var_0, var_1);
    var_11 = wp::load(var_8);
    var_12 = wp::load(var_9);
    var_10 = wp::sub(var_11, var_12);
    // wp::array_store(var_out, var_0, var_1, var_10);
    //---------
    // reverse
    wp::adj_array_store(var_out, var_0, var_1, var_10, adj_out, adj_0, adj_1, adj_10);
    wp::adj_sub(var_11, var_12, adj_8, adj_9, adj_10);
    wp::adj_address(var_b, var_0, var_1, adj_b, adj_0, adj_1, adj_9);
    wp::adj_address(var_a, var_3, var_6, adj_a, adj_3, adj_6, adj_8);
    wp::adj_address(var_item_ids, var_1, adj_item_ids, adj_1, adj_5);
    wp::adj_address(var_env_ids, var_0, adj_env_ids, adj_0, adj_2);
    // adj: out[i, j] = a[wp.int32(env_ids[i]), wp.int32(item_ids[j])] - b[i, j]              <L 18>
    // adj: i, j = wp.tid()                                                                   <L 17>
    // adj: def gather_subtract_2d(                                                           <L 1>
    return;
}



extern "C" {

// Python CPU entry points
WP_API void gather_subtract_2d_4c8aec8a_cpu_forward(
    wp::launch_bounds_t<2> *dim,
    wp_args_gather_subtract_2d_4c8aec8a *_wp_args)
{
    wp::tile_shared_storage_t tile_mem;
#if defined(WP_ENABLE_TILES_IN_STACK_MEMORY)
    wp::shared_tile_storage = &tile_mem;
#endif

    for (size_t task_index = 0; task_index < dim->size; ++task_index)
    {
        gather_subtract_2d_4c8aec8a_cpu_kernel_forward(*dim, task_index, _wp_args);
    }
}

} // extern C



extern "C" {

WP_API void gather_subtract_2d_4c8aec8a_cpu_backward(
    wp::launch_bounds_t<2> *dim,
    wp_args_gather_subtract_2d_4c8aec8a *_wp_args,
    wp_args_gather_subtract_2d_4c8aec8a *_wp_adj_args)
{
    wp::tile_shared_storage_t tile_mem;
#if defined(WP_ENABLE_TILES_IN_STACK_MEMORY)
    wp::shared_tile_storage = &tile_mem;
#endif

    for (size_t task_index = 0; task_index < dim->size; ++task_index)
    {
        gather_subtract_2d_4c8aec8a_cpu_kernel_backward(*dim, task_index, _wp_args, _wp_adj_args);
    }
}

} // extern C

struct wp_args_set_forces_to_dual_buffers_index_58b2d837 {
    wp::array_t<wp::int32> env_ids;
    wp::array_t<wp::int32> body_ids;
    wp::array_t<wp::vec_t<3, wp::float32>> forces;
    wp::array_t<wp::vec_t<3, wp::float32>> torques;
    wp::array_t<wp::vec_t<3, wp::float32>> positions;
    wp::array_t<wp::vec_t<3, wp::float32>> global_force_w;
    wp::array_t<wp::vec_t<3, wp::float32>> global_torque_w;
    wp::array_t<wp::vec_t<3, wp::float32>> global_force_at_com_w;
    wp::array_t<wp::vec_t<3, wp::float32>> local_force_b;
    wp::array_t<wp::vec_t<3, wp::float32>> local_torque_b;
    bool is_global;
};


void set_forces_to_dual_buffers_index_58b2d837_cpu_kernel_forward(
    wp::launch_bounds_t<2> dim,
    size_t task_index,
    wp_args_set_forces_to_dual_buffers_index_58b2d837 *_wp_args)
{
    //---------
    // argument vars
    wp::array_t<wp::int32> var_env_ids = _wp_args->env_ids;
    wp::array_t<wp::int32> var_body_ids = _wp_args->body_ids;
    wp::array_t<wp::vec_t<3, wp::float32>> var_forces = _wp_args->forces;
    wp::array_t<wp::vec_t<3, wp::float32>> var_torques = _wp_args->torques;
    wp::array_t<wp::vec_t<3, wp::float32>> var_positions = _wp_args->positions;
    wp::array_t<wp::vec_t<3, wp::float32>> var_global_force_w = _wp_args->global_force_w;
    wp::array_t<wp::vec_t<3, wp::float32>> var_global_torque_w = _wp_args->global_torque_w;
    wp::array_t<wp::vec_t<3, wp::float32>> var_global_force_at_com_w = _wp_args->global_force_at_com_w;
    wp::array_t<wp::vec_t<3, wp::float32>> var_local_force_b = _wp_args->local_force_b;
    wp::array_t<wp::vec_t<3, wp::float32>> var_local_torque_b = _wp_args->local_torque_b;
    bool var_is_global = _wp_args->is_global;
    //---------
    // primal vars
    wp::int32 var_0;
    wp::int32 var_1;
    wp::int32* var_2;
    wp::int32 var_3;
    wp::int32 var_4;
    wp::int32* var_5;
    wp::int32 var_6;
    wp::int32 var_7;
    wp::vec_t<3, wp::float32>* var_8;
    wp::vec_t<3, wp::float32> var_9;
    wp::vec_t<3, wp::float32>* var_10;
    wp::vec_t<3, wp::float32> var_11;
    wp::vec_t<3, wp::float32>* var_12;
    wp::vec_t<3, wp::float32>* var_13;
    wp::vec_t<3, wp::float32>* var_14;
    wp::vec_t<3, wp::float32> var_15;
    wp::vec_t<3, wp::float32> var_16;
    wp::vec_t<3, wp::float32> var_17;
    wp::vec_t<3, wp::float32> var_18;
    wp::vec_t<3, wp::float32> var_19;
    wp::vec_t<3, wp::float32>* var_20;
    wp::vec_t<3, wp::float32>* var_21;
    wp::vec_t<3, wp::float32> var_22;
    wp::vec_t<3, wp::float32> var_23;
    wp::vec_t<3, wp::float32> var_24;
    wp::vec_t<3, wp::float32>* var_25;
    wp::vec_t<3, wp::float32> var_26;
    wp::vec_t<3, wp::float32>* var_27;
    wp::vec_t<3, wp::float32> var_28;
    wp::vec_t<3, wp::float32>* var_29;
    wp::vec_t<3, wp::float32> var_30;
    wp::vec_t<3, wp::float32>* var_31;
    wp::vec_t<3, wp::float32>* var_32;
    wp::vec_t<3, wp::float32>* var_33;
    wp::vec_t<3, wp::float32> var_34;
    wp::vec_t<3, wp::float32> var_35;
    wp::vec_t<3, wp::float32> var_36;
    wp::vec_t<3, wp::float32> var_37;
    wp::vec_t<3, wp::float32> var_38;
    wp::vec_t<3, wp::float32>* var_39;
    wp::vec_t<3, wp::float32>* var_40;
    wp::vec_t<3, wp::float32> var_41;
    wp::vec_t<3, wp::float32> var_42;
    wp::vec_t<3, wp::float32> var_43;
    //---------
    // forward
    // def set_forces_to_dual_buffers_index(                                                  <L 1>
    // tid_env, tid_body = wp.tid()                                                           <L 25>
    builtin_tid2d(var_0, var_1);
    // ei = wp.int32(env_ids[tid_env])                                                        <L 26>
    var_2 = wp::address(var_env_ids, var_0);
    var_4 = wp::load(var_2);
    var_3 = wp::int32(var_4);
    // bi = wp.int32(body_ids[tid_body])                                                      <L 27>
    var_5 = wp::address(var_body_ids, var_1);
    var_7 = wp::load(var_5);
    var_6 = wp::int32(var_7);
    // if is_global:                                                                          <L 29>
    if (var_is_global) {
        // if torques:                                                                        <L 30>
        if (var_torques) {
            // global_torque_w[ei, bi] = torques[tid_env, tid_body]                           <L 31>
            var_8 = wp::address(var_torques, var_0, var_1);
            var_9 = wp::load(var_8);
            wp::array_store(var_global_torque_w, var_3, var_6, var_9);
        }
        // if forces:                                                                         <L 32>
        if (var_forces) {
            // if positions:                                                                  <L 33>
            if (var_positions) {
                // global_force_w[ei, bi] = forces[tid_env, tid_body]                         <L 34>
                var_10 = wp::address(var_forces, var_0, var_1);
                var_11 = wp::load(var_10);
                wp::array_store(var_global_force_w, var_3, var_6, var_11);
                // if torques:                                                                <L 35>
                if (var_torques) {
                    // global_torque_w[ei, bi] = global_torque_w[ei, bi] + wp.cross(          <L 36>
                    var_12 = wp::address(var_global_torque_w, var_3, var_6);
                    // positions[tid_env, tid_body], forces[tid_env, tid_body]                <L 37>
                    var_13 = wp::address(var_positions, var_0, var_1);
                    var_14 = wp::address(var_forces, var_0, var_1);
                    var_16 = wp::load(var_13);
                    var_17 = wp::load(var_14);
                    var_15 = wp::cross(var_16, var_17);
                    var_19 = wp::load(var_12);
                    var_18 = wp::add(var_19, var_15);
                    // global_torque_w[ei, bi] = global_torque_w[ei, bi] + wp.cross(          <L 36>
                    wp::array_store(var_global_torque_w, var_3, var_6, var_18);
                }
                if (!var_torques) {
                    // global_torque_w[ei, bi] = wp.cross(positions[tid_env, tid_body], forces[tid_env, tid_body])       <L 40>
                    var_20 = wp::address(var_positions, var_0, var_1);
                    var_21 = wp::address(var_forces, var_0, var_1);
                    var_23 = wp::load(var_20);
                    var_24 = wp::load(var_21);
                    var_22 = wp::cross(var_23, var_24);
                    wp::array_store(var_global_torque_w, var_3, var_6, var_22);
                }
            }
            if (!var_positions) {
                // global_force_at_com_w[ei, bi] = forces[tid_env, tid_body]                  <L 42>
                var_25 = wp::address(var_forces, var_0, var_1);
                var_26 = wp::load(var_25);
                wp::array_store(var_global_force_at_com_w, var_3, var_6, var_26);
            }
        }
    }
    if (!var_is_global) {
        // if torques:                                                                        <L 44>
        if (var_torques) {
            // local_torque_b[ei, bi] = torques[tid_env, tid_body]                            <L 45>
            var_27 = wp::address(var_torques, var_0, var_1);
            var_28 = wp::load(var_27);
            wp::array_store(var_local_torque_b, var_3, var_6, var_28);
        }
        // if forces:                                                                         <L 46>
        if (var_forces) {
            // local_force_b[ei, bi] = forces[tid_env, tid_body]                              <L 47>
            var_29 = wp::address(var_forces, var_0, var_1);
            var_30 = wp::load(var_29);
            wp::array_store(var_local_force_b, var_3, var_6, var_30);
            // if positions:                                                                  <L 48>
            if (var_positions) {
                // if torques:                                                                <L 49>
                if (var_torques) {
                    // local_torque_b[ei, bi] = local_torque_b[ei, bi] + wp.cross(            <L 50>
                    var_31 = wp::address(var_local_torque_b, var_3, var_6);
                    // positions[tid_env, tid_body], forces[tid_env, tid_body]                <L 51>
                    var_32 = wp::address(var_positions, var_0, var_1);
                    var_33 = wp::address(var_forces, var_0, var_1);
                    var_35 = wp::load(var_32);
                    var_36 = wp::load(var_33);
                    var_34 = wp::cross(var_35, var_36);
                    var_38 = wp::load(var_31);
                    var_37 = wp::add(var_38, var_34);
                    // local_torque_b[ei, bi] = local_torque_b[ei, bi] + wp.cross(            <L 50>
                    wp::array_store(var_local_torque_b, var_3, var_6, var_37);
                }
                if (!var_torques) {
                    // local_torque_b[ei, bi] = wp.cross(positions[tid_env, tid_body], forces[tid_env, tid_body])       <L 54>
                    var_39 = wp::address(var_positions, var_0, var_1);
                    var_40 = wp::address(var_forces, var_0, var_1);
                    var_42 = wp::load(var_39);
                    var_43 = wp::load(var_40);
                    var_41 = wp::cross(var_42, var_43);
                    wp::array_store(var_local_torque_b, var_3, var_6, var_41);
                }
            }
        }
    }
}



void set_forces_to_dual_buffers_index_58b2d837_cpu_kernel_backward(
    wp::launch_bounds_t<2> dim,
    size_t task_index,
    wp_args_set_forces_to_dual_buffers_index_58b2d837 *_wp_args,
    wp_args_set_forces_to_dual_buffers_index_58b2d837 *_wp_adj_args)
{
    //---------
    // argument vars
    wp::array_t<wp::int32> var_env_ids = _wp_args->env_ids;
    wp::array_t<wp::int32> var_body_ids = _wp_args->body_ids;
    wp::array_t<wp::vec_t<3, wp::float32>> var_forces = _wp_args->forces;
    wp::array_t<wp::vec_t<3, wp::float32>> var_torques = _wp_args->torques;
    wp::array_t<wp::vec_t<3, wp::float32>> var_positions = _wp_args->positions;
    wp::array_t<wp::vec_t<3, wp::float32>> var_global_force_w = _wp_args->global_force_w;
    wp::array_t<wp::vec_t<3, wp::float32>> var_global_torque_w = _wp_args->global_torque_w;
    wp::array_t<wp::vec_t<3, wp::float32>> var_global_force_at_com_w = _wp_args->global_force_at_com_w;
    wp::array_t<wp::vec_t<3, wp::float32>> var_local_force_b = _wp_args->local_force_b;
    wp::array_t<wp::vec_t<3, wp::float32>> var_local_torque_b = _wp_args->local_torque_b;
    bool var_is_global = _wp_args->is_global;
    wp::array_t<wp::int32> adj_env_ids = _wp_adj_args->env_ids;
    wp::array_t<wp::int32> adj_body_ids = _wp_adj_args->body_ids;
    wp::array_t<wp::vec_t<3, wp::float32>> adj_forces = _wp_adj_args->forces;
    wp::array_t<wp::vec_t<3, wp::float32>> adj_torques = _wp_adj_args->torques;
    wp::array_t<wp::vec_t<3, wp::float32>> adj_positions = _wp_adj_args->positions;
    wp::array_t<wp::vec_t<3, wp::float32>> adj_global_force_w = _wp_adj_args->global_force_w;
    wp::array_t<wp::vec_t<3, wp::float32>> adj_global_torque_w = _wp_adj_args->global_torque_w;
    wp::array_t<wp::vec_t<3, wp::float32>> adj_global_force_at_com_w = _wp_adj_args->global_force_at_com_w;
    wp::array_t<wp::vec_t<3, wp::float32>> adj_local_force_b = _wp_adj_args->local_force_b;
    wp::array_t<wp::vec_t<3, wp::float32>> adj_local_torque_b = _wp_adj_args->local_torque_b;
    bool adj_is_global = _wp_adj_args->is_global;
    //---------
    // primal vars
    wp::int32 var_0;
    wp::int32 var_1;
    wp::int32* var_2;
    wp::int32 var_3;
    wp::int32 var_4;
    wp::int32* var_5;
    wp::int32 var_6;
    wp::int32 var_7;
    wp::vec_t<3, wp::float32>* var_8;
    wp::vec_t<3, wp::float32> var_9;
    wp::vec_t<3, wp::float32>* var_10;
    wp::vec_t<3, wp::float32> var_11;
    wp::vec_t<3, wp::float32>* var_12;
    wp::vec_t<3, wp::float32>* var_13;
    wp::vec_t<3, wp::float32>* var_14;
    wp::vec_t<3, wp::float32> var_15;
    wp::vec_t<3, wp::float32> var_16;
    wp::vec_t<3, wp::float32> var_17;
    wp::vec_t<3, wp::float32> var_18;
    wp::vec_t<3, wp::float32> var_19;
    wp::vec_t<3, wp::float32>* var_20;
    wp::vec_t<3, wp::float32>* var_21;
    wp::vec_t<3, wp::float32> var_22;
    wp::vec_t<3, wp::float32> var_23;
    wp::vec_t<3, wp::float32> var_24;
    wp::vec_t<3, wp::float32>* var_25;
    wp::vec_t<3, wp::float32> var_26;
    wp::vec_t<3, wp::float32>* var_27;
    wp::vec_t<3, wp::float32> var_28;
    wp::vec_t<3, wp::float32>* var_29;
    wp::vec_t<3, wp::float32> var_30;
    wp::vec_t<3, wp::float32>* var_31;
    wp::vec_t<3, wp::float32>* var_32;
    wp::vec_t<3, wp::float32>* var_33;
    wp::vec_t<3, wp::float32> var_34;
    wp::vec_t<3, wp::float32> var_35;
    wp::vec_t<3, wp::float32> var_36;
    wp::vec_t<3, wp::float32> var_37;
    wp::vec_t<3, wp::float32> var_38;
    wp::vec_t<3, wp::float32>* var_39;
    wp::vec_t<3, wp::float32>* var_40;
    wp::vec_t<3, wp::float32> var_41;
    wp::vec_t<3, wp::float32> var_42;
    wp::vec_t<3, wp::float32> var_43;
    //---------
    // dual vars
    wp::int32 adj_0 = {};
    wp::int32 adj_1 = {};
    wp::int32 adj_2 = {};
    wp::int32 adj_3 = {};
    wp::int32 adj_4 = {};
    wp::int32 adj_5 = {};
    wp::int32 adj_6 = {};
    wp::int32 adj_7 = {};
    wp::vec_t<3, wp::float32> adj_8 = {};
    wp::vec_t<3, wp::float32> adj_9 = {};
    wp::vec_t<3, wp::float32> adj_10 = {};
    wp::vec_t<3, wp::float32> adj_11 = {};
    wp::vec_t<3, wp::float32> adj_12 = {};
    wp::vec_t<3, wp::float32> adj_13 = {};
    wp::vec_t<3, wp::float32> adj_14 = {};
    wp::vec_t<3, wp::float32> adj_15 = {};
    wp::vec_t<3, wp::float32> adj_16 = {};
    wp::vec_t<3, wp::float32> adj_17 = {};
    wp::vec_t<3, wp::float32> adj_18 = {};
    wp::vec_t<3, wp::float32> adj_19 = {};
    wp::vec_t<3, wp::float32> adj_20 = {};
    wp::vec_t<3, wp::float32> adj_21 = {};
    wp::vec_t<3, wp::float32> adj_22 = {};
    wp::vec_t<3, wp::float32> adj_23 = {};
    wp::vec_t<3, wp::float32> adj_24 = {};
    wp::vec_t<3, wp::float32> adj_25 = {};
    wp::vec_t<3, wp::float32> adj_26 = {};
    wp::vec_t<3, wp::float32> adj_27 = {};
    wp::vec_t<3, wp::float32> adj_28 = {};
    wp::vec_t<3, wp::float32> adj_29 = {};
    wp::vec_t<3, wp::float32> adj_30 = {};
    wp::vec_t<3, wp::float32> adj_31 = {};
    wp::vec_t<3, wp::float32> adj_32 = {};
    wp::vec_t<3, wp::float32> adj_33 = {};
    wp::vec_t<3, wp::float32> adj_34 = {};
    wp::vec_t<3, wp::float32> adj_35 = {};
    wp::vec_t<3, wp::float32> adj_36 = {};
    wp::vec_t<3, wp::float32> adj_37 = {};
    wp::vec_t<3, wp::float32> adj_38 = {};
    wp::vec_t<3, wp::float32> adj_39 = {};
    wp::vec_t<3, wp::float32> adj_40 = {};
    wp::vec_t<3, wp::float32> adj_41 = {};
    wp::vec_t<3, wp::float32> adj_42 = {};
    wp::vec_t<3, wp::float32> adj_43 = {};
    //---------
    // forward
    // def set_forces_to_dual_buffers_index(                                                  <L 1>
    // tid_env, tid_body = wp.tid()                                                           <L 25>
    builtin_tid2d(var_0, var_1);
    // ei = wp.int32(env_ids[tid_env])                                                        <L 26>
    var_2 = wp::address(var_env_ids, var_0);
    var_4 = wp::load(var_2);
    var_3 = wp::int32(var_4);
    // bi = wp.int32(body_ids[tid_body])                                                      <L 27>
    var_5 = wp::address(var_body_ids, var_1);
    var_7 = wp::load(var_5);
    var_6 = wp::int32(var_7);
    // if is_global:                                                                          <L 29>
    if (var_is_global) {
        // if torques:                                                                        <L 30>
        if (var_torques) {
            // global_torque_w[ei, bi] = torques[tid_env, tid_body]                           <L 31>
            var_8 = wp::address(var_torques, var_0, var_1);
            var_9 = wp::load(var_8);
            // wp::array_store(var_global_torque_w, var_3, var_6, var_9);
        }
        // if forces:                                                                         <L 32>
        if (var_forces) {
            // if positions:                                                                  <L 33>
            if (var_positions) {
                // global_force_w[ei, bi] = forces[tid_env, tid_body]                         <L 34>
                var_10 = wp::address(var_forces, var_0, var_1);
                var_11 = wp::load(var_10);
                // wp::array_store(var_global_force_w, var_3, var_6, var_11);
                // if torques:                                                                <L 35>
                if (var_torques) {
                    // global_torque_w[ei, bi] = global_torque_w[ei, bi] + wp.cross(          <L 36>
                    var_12 = wp::address(var_global_torque_w, var_3, var_6);
                    // positions[tid_env, tid_body], forces[tid_env, tid_body]                <L 37>
                    var_13 = wp::address(var_positions, var_0, var_1);
                    var_14 = wp::address(var_forces, var_0, var_1);
                    var_16 = wp::load(var_13);
                    var_17 = wp::load(var_14);
                    var_15 = wp::cross(var_16, var_17);
                    var_19 = wp::load(var_12);
                    var_18 = wp::add(var_19, var_15);
                    // global_torque_w[ei, bi] = global_torque_w[ei, bi] + wp.cross(          <L 36>
                    // wp::array_store(var_global_torque_w, var_3, var_6, var_18);
                }
                if (!var_torques) {
                    // global_torque_w[ei, bi] = wp.cross(positions[tid_env, tid_body], forces[tid_env, tid_body])       <L 40>
                    var_20 = wp::address(var_positions, var_0, var_1);
                    var_21 = wp::address(var_forces, var_0, var_1);
                    var_23 = wp::load(var_20);
                    var_24 = wp::load(var_21);
                    var_22 = wp::cross(var_23, var_24);
                    // wp::array_store(var_global_torque_w, var_3, var_6, var_22);
                }
            }
            if (!var_positions) {
                // global_force_at_com_w[ei, bi] = forces[tid_env, tid_body]                  <L 42>
                var_25 = wp::address(var_forces, var_0, var_1);
                var_26 = wp::load(var_25);
                // wp::array_store(var_global_force_at_com_w, var_3, var_6, var_26);
            }
        }
    }
    if (!var_is_global) {
        // if torques:                                                                        <L 44>
        if (var_torques) {
            // local_torque_b[ei, bi] = torques[tid_env, tid_body]                            <L 45>
            var_27 = wp::address(var_torques, var_0, var_1);
            var_28 = wp::load(var_27);
            // wp::array_store(var_local_torque_b, var_3, var_6, var_28);
        }
        // if forces:                                                                         <L 46>
        if (var_forces) {
            // local_force_b[ei, bi] = forces[tid_env, tid_body]                              <L 47>
            var_29 = wp::address(var_forces, var_0, var_1);
            var_30 = wp::load(var_29);
            // wp::array_store(var_local_force_b, var_3, var_6, var_30);
            // if positions:                                                                  <L 48>
            if (var_positions) {
                // if torques:                                                                <L 49>
                if (var_torques) {
                    // local_torque_b[ei, bi] = local_torque_b[ei, bi] + wp.cross(            <L 50>
                    var_31 = wp::address(var_local_torque_b, var_3, var_6);
                    // positions[tid_env, tid_body], forces[tid_env, tid_body]                <L 51>
                    var_32 = wp::address(var_positions, var_0, var_1);
                    var_33 = wp::address(var_forces, var_0, var_1);
                    var_35 = wp::load(var_32);
                    var_36 = wp::load(var_33);
                    var_34 = wp::cross(var_35, var_36);
                    var_38 = wp::load(var_31);
                    var_37 = wp::add(var_38, var_34);
                    // local_torque_b[ei, bi] = local_torque_b[ei, bi] + wp.cross(            <L 50>
                    // wp::array_store(var_local_torque_b, var_3, var_6, var_37);
                }
                if (!var_torques) {
                    // local_torque_b[ei, bi] = wp.cross(positions[tid_env, tid_body], forces[tid_env, tid_body])       <L 54>
                    var_39 = wp::address(var_positions, var_0, var_1);
                    var_40 = wp::address(var_forces, var_0, var_1);
                    var_42 = wp::load(var_39);
                    var_43 = wp::load(var_40);
                    var_41 = wp::cross(var_42, var_43);
                    // wp::array_store(var_local_torque_b, var_3, var_6, var_41);
                }
            }
        }
    }
    //---------
    // reverse
    if (!var_is_global) {
        if (var_forces) {
            if (var_positions) {
                if (!var_torques) {
                    wp::adj_array_store(var_local_torque_b, var_3, var_6, var_41, adj_local_torque_b, adj_3, adj_6, adj_41);
                    wp::adj_cross(var_42, var_43, adj_39, adj_40, adj_41);
                    wp::adj_address(var_forces, var_0, var_1, adj_forces, adj_0, adj_1, adj_40);
                    wp::adj_address(var_positions, var_0, var_1, adj_positions, adj_0, adj_1, adj_39);
                    // adj: local_torque_b[ei, bi] = wp.cross(positions[tid_env, tid_body], forces[tid_env, tid_body])  <L 54>
                }
                if (var_torques) {
                    wp::adj_array_store(var_local_torque_b, var_3, var_6, var_37, adj_local_torque_b, adj_3, adj_6, adj_37);
                    // adj: local_torque_b[ei, bi] = local_torque_b[ei, bi] + wp.cross(       <L 50>
                    wp::adj_add(var_38, var_34, adj_31, adj_34, adj_37);
                    wp::adj_cross(var_35, var_36, adj_32, adj_33, adj_34);
                    wp::adj_address(var_forces, var_0, var_1, adj_forces, adj_0, adj_1, adj_33);
                    wp::adj_address(var_positions, var_0, var_1, adj_positions, adj_0, adj_1, adj_32);
                    // adj: positions[tid_env, tid_body], forces[tid_env, tid_body]           <L 51>
                    wp::adj_address(var_local_torque_b, var_3, var_6, adj_local_torque_b, adj_3, adj_6, adj_31);
                    // adj: local_torque_b[ei, bi] = local_torque_b[ei, bi] + wp.cross(       <L 50>
                }
                // adj: if torques:                                                           <L 49>
            }
            // adj: if positions:                                                             <L 48>
            wp::adj_array_store(var_local_force_b, var_3, var_6, var_30, adj_local_force_b, adj_3, adj_6, adj_29);
            wp::adj_address(var_forces, var_0, var_1, adj_forces, adj_0, adj_1, adj_29);
            // adj: local_force_b[ei, bi] = forces[tid_env, tid_body]                         <L 47>
        }
        // adj: if forces:                                                                    <L 46>
        if (var_torques) {
            wp::adj_array_store(var_local_torque_b, var_3, var_6, var_28, adj_local_torque_b, adj_3, adj_6, adj_27);
            wp::adj_address(var_torques, var_0, var_1, adj_torques, adj_0, adj_1, adj_27);
            // adj: local_torque_b[ei, bi] = torques[tid_env, tid_body]                       <L 45>
        }
        // adj: if torques:                                                                   <L 44>
    }
    if (var_is_global) {
        if (var_forces) {
            if (!var_positions) {
                wp::adj_array_store(var_global_force_at_com_w, var_3, var_6, var_26, adj_global_force_at_com_w, adj_3, adj_6, adj_25);
                wp::adj_address(var_forces, var_0, var_1, adj_forces, adj_0, adj_1, adj_25);
                // adj: global_force_at_com_w[ei, bi] = forces[tid_env, tid_body]             <L 42>
            }
            if (var_positions) {
                if (!var_torques) {
                    wp::adj_array_store(var_global_torque_w, var_3, var_6, var_22, adj_global_torque_w, adj_3, adj_6, adj_22);
                    wp::adj_cross(var_23, var_24, adj_20, adj_21, adj_22);
                    wp::adj_address(var_forces, var_0, var_1, adj_forces, adj_0, adj_1, adj_21);
                    wp::adj_address(var_positions, var_0, var_1, adj_positions, adj_0, adj_1, adj_20);
                    // adj: global_torque_w[ei, bi] = wp.cross(positions[tid_env, tid_body], forces[tid_env, tid_body])  <L 40>
                }
                if (var_torques) {
                    wp::adj_array_store(var_global_torque_w, var_3, var_6, var_18, adj_global_torque_w, adj_3, adj_6, adj_18);
                    // adj: global_torque_w[ei, bi] = global_torque_w[ei, bi] + wp.cross(     <L 36>
                    wp::adj_add(var_19, var_15, adj_12, adj_15, adj_18);
                    wp::adj_cross(var_16, var_17, adj_13, adj_14, adj_15);
                    wp::adj_address(var_forces, var_0, var_1, adj_forces, adj_0, adj_1, adj_14);
                    wp::adj_address(var_positions, var_0, var_1, adj_positions, adj_0, adj_1, adj_13);
                    // adj: positions[tid_env, tid_body], forces[tid_env, tid_body]           <L 37>
                    wp::adj_address(var_global_torque_w, var_3, var_6, adj_global_torque_w, adj_3, adj_6, adj_12);
                    // adj: global_torque_w[ei, bi] = global_torque_w[ei, bi] + wp.cross(     <L 36>
                }
                // adj: if torques:                                                           <L 35>
                wp::adj_array_store(var_global_force_w, var_3, var_6, var_11, adj_global_force_w, adj_3, adj_6, adj_10);
                wp::adj_address(var_forces, var_0, var_1, adj_forces, adj_0, adj_1, adj_10);
                // adj: global_force_w[ei, bi] = forces[tid_env, tid_body]                    <L 34>
            }
            // adj: if positions:                                                             <L 33>
        }
        // adj: if forces:                                                                    <L 32>
        if (var_torques) {
            wp::adj_array_store(var_global_torque_w, var_3, var_6, var_9, adj_global_torque_w, adj_3, adj_6, adj_8);
            wp::adj_address(var_torques, var_0, var_1, adj_torques, adj_0, adj_1, adj_8);
            // adj: global_torque_w[ei, bi] = torques[tid_env, tid_body]                      <L 31>
        }
        // adj: if torques:                                                                   <L 30>
    }
    // adj: if is_global:                                                                     <L 29>
    wp::adj_address(var_body_ids, var_1, adj_body_ids, adj_1, adj_5);
    // adj: bi = wp.int32(body_ids[tid_body])                                                 <L 27>
    wp::adj_address(var_env_ids, var_0, adj_env_ids, adj_0, adj_2);
    // adj: ei = wp.int32(env_ids[tid_env])                                                   <L 26>
    // adj: tid_env, tid_body = wp.tid()                                                      <L 25>
    // adj: def set_forces_to_dual_buffers_index(                                             <L 1>
    return;
}



extern "C" {

// Python CPU entry points
WP_API void set_forces_to_dual_buffers_index_58b2d837_cpu_forward(
    wp::launch_bounds_t<2> *dim,
    wp_args_set_forces_to_dual_buffers_index_58b2d837 *_wp_args)
{
    wp::tile_shared_storage_t tile_mem;
#if defined(WP_ENABLE_TILES_IN_STACK_MEMORY)
    wp::shared_tile_storage = &tile_mem;
#endif

    for (size_t task_index = 0; task_index < dim->size; ++task_index)
    {
        set_forces_to_dual_buffers_index_58b2d837_cpu_kernel_forward(*dim, task_index, _wp_args);
    }
}

} // extern C



extern "C" {

WP_API void set_forces_to_dual_buffers_index_58b2d837_cpu_backward(
    wp::launch_bounds_t<2> *dim,
    wp_args_set_forces_to_dual_buffers_index_58b2d837 *_wp_args,
    wp_args_set_forces_to_dual_buffers_index_58b2d837 *_wp_adj_args)
{
    wp::tile_shared_storage_t tile_mem;
#if defined(WP_ENABLE_TILES_IN_STACK_MEMORY)
    wp::shared_tile_storage = &tile_mem;
#endif

    for (size_t task_index = 0; task_index < dim->size; ++task_index)
    {
        set_forces_to_dual_buffers_index_58b2d837_cpu_kernel_backward(*dim, task_index, _wp_args, _wp_adj_args);
    }
}

} // extern C

struct wp_args_compose_wrench_to_body_frame_64cf3c01 {
    wp::array_t<wp::vec_t<3, wp::float32>> global_force_w;
    wp::array_t<wp::vec_t<3, wp::float32>> global_torque_w;
    wp::array_t<wp::vec_t<3, wp::float32>> global_force_at_com_w;
    wp::array_t<wp::vec_t<3, wp::float32>> local_force_b;
    wp::array_t<wp::vec_t<3, wp::float32>> local_torque_b;
    wp::array_t<wp::vec_t<3, wp::float32>> com_pos_w;
    wp::array_t<wp::quat_t<wp::float32>> link_quat_w;
    wp::array_t<wp::vec_t<3, wp::float32>> out_force_b;
    wp::array_t<wp::vec_t<3, wp::float32>> out_torque_b;
};


void compose_wrench_to_body_frame_64cf3c01_cpu_kernel_forward(
    wp::launch_bounds_t<2> dim,
    size_t task_index,
    wp_args_compose_wrench_to_body_frame_64cf3c01 *_wp_args)
{
    //---------
    // argument vars
    wp::array_t<wp::vec_t<3, wp::float32>> var_global_force_w = _wp_args->global_force_w;
    wp::array_t<wp::vec_t<3, wp::float32>> var_global_torque_w = _wp_args->global_torque_w;
    wp::array_t<wp::vec_t<3, wp::float32>> var_global_force_at_com_w = _wp_args->global_force_at_com_w;
    wp::array_t<wp::vec_t<3, wp::float32>> var_local_force_b = _wp_args->local_force_b;
    wp::array_t<wp::vec_t<3, wp::float32>> var_local_torque_b = _wp_args->local_torque_b;
    wp::array_t<wp::vec_t<3, wp::float32>> var_com_pos_w = _wp_args->com_pos_w;
    wp::array_t<wp::quat_t<wp::float32>> var_link_quat_w = _wp_args->link_quat_w;
    wp::array_t<wp::vec_t<3, wp::float32>> var_out_force_b = _wp_args->out_force_b;
    wp::array_t<wp::vec_t<3, wp::float32>> var_out_torque_b = _wp_args->out_torque_b;
    //---------
    // primal vars
    wp::int32 var_0;
    wp::int32 var_1;
    wp::vec_t<3, wp::float32>* var_2;
    wp::vec_t<3, wp::float32>* var_3;
    wp::vec_t<3, wp::float32> var_4;
    wp::vec_t<3, wp::float32> var_5;
    wp::vec_t<3, wp::float32> var_6;
    wp::vec_t<3, wp::float32>* var_7;
    wp::vec_t<3, wp::float32>* var_8;
    wp::vec_t<3, wp::float32>* var_9;
    wp::vec_t<3, wp::float32> var_10;
    wp::vec_t<3, wp::float32> var_11;
    wp::vec_t<3, wp::float32> var_12;
    wp::vec_t<3, wp::float32> var_13;
    wp::vec_t<3, wp::float32> var_14;
    wp::quat_t<wp::float32>* var_15;
    wp::vec_t<3, wp::float32> var_16;
    wp::quat_t<wp::float32> var_17;
    wp::vec_t<3, wp::float32>* var_18;
    wp::vec_t<3, wp::float32> var_19;
    wp::vec_t<3, wp::float32> var_20;
    wp::quat_t<wp::float32>* var_21;
    wp::vec_t<3, wp::float32> var_22;
    wp::quat_t<wp::float32> var_23;
    wp::vec_t<3, wp::float32>* var_24;
    wp::vec_t<3, wp::float32> var_25;
    wp::vec_t<3, wp::float32> var_26;
    //---------
    // forward
    // def compose_wrench_to_body_frame(                                                      <L 629>
    // tid_env, tid_body = wp.tid()                                                           <L 649>
    builtin_tid2d(var_0, var_1);
    // total_force_w = global_force_w[tid_env, tid_body] + global_force_at_com_w[tid_env, tid_body]       <L 650>
    var_2 = wp::address(var_global_force_w, var_0, var_1);
    var_3 = wp::address(var_global_force_at_com_w, var_0, var_1);
    var_5 = wp::load(var_2);
    var_6 = wp::load(var_3);
    var_4 = wp::add(var_5, var_6);
    // corrected_torque_w = global_torque_w[tid_env, tid_body] - wp.cross(                    <L 651>
    var_7 = wp::address(var_global_torque_w, var_0, var_1);
    // com_pos_w[tid_env, tid_body], global_force_w[tid_env, tid_body]                        <L 652>
    var_8 = wp::address(var_com_pos_w, var_0, var_1);
    var_9 = wp::address(var_global_force_w, var_0, var_1);
    var_11 = wp::load(var_8);
    var_12 = wp::load(var_9);
    var_10 = wp::cross(var_11, var_12);
    var_14 = wp::load(var_7);
    var_13 = wp::sub(var_14, var_10);
    // out_force_b[tid_env, tid_body] = (                                                     <L 654>
    // wp.quat_rotate_inv(link_quat_w[tid_env, tid_body], total_force_w) + local_force_b[tid_env, tid_body]       <L 655>
    var_15 = wp::address(var_link_quat_w, var_0, var_1);
    var_17 = wp::load(var_15);
    var_16 = wp::quat_rotate_inv(var_17, var_4);
    var_18 = wp::address(var_local_force_b, var_0, var_1);
    var_20 = wp::load(var_18);
    var_19 = wp::add(var_16, var_20);
    // out_force_b[tid_env, tid_body] = (                                                     <L 654>
    wp::array_store(var_out_force_b, var_0, var_1, var_19);
    // out_torque_b[tid_env, tid_body] = (                                                    <L 657>
    // wp.quat_rotate_inv(link_quat_w[tid_env, tid_body], corrected_torque_w) + local_torque_b[tid_env, tid_body]       <L 658>
    var_21 = wp::address(var_link_quat_w, var_0, var_1);
    var_23 = wp::load(var_21);
    var_22 = wp::quat_rotate_inv(var_23, var_13);
    var_24 = wp::address(var_local_torque_b, var_0, var_1);
    var_26 = wp::load(var_24);
    var_25 = wp::add(var_22, var_26);
    // out_torque_b[tid_env, tid_body] = (                                                    <L 657>
    wp::array_store(var_out_torque_b, var_0, var_1, var_25);
}



void compose_wrench_to_body_frame_64cf3c01_cpu_kernel_backward(
    wp::launch_bounds_t<2> dim,
    size_t task_index,
    wp_args_compose_wrench_to_body_frame_64cf3c01 *_wp_args,
    wp_args_compose_wrench_to_body_frame_64cf3c01 *_wp_adj_args)
{
    //---------
    // argument vars
    wp::array_t<wp::vec_t<3, wp::float32>> var_global_force_w = _wp_args->global_force_w;
    wp::array_t<wp::vec_t<3, wp::float32>> var_global_torque_w = _wp_args->global_torque_w;
    wp::array_t<wp::vec_t<3, wp::float32>> var_global_force_at_com_w = _wp_args->global_force_at_com_w;
    wp::array_t<wp::vec_t<3, wp::float32>> var_local_force_b = _wp_args->local_force_b;
    wp::array_t<wp::vec_t<3, wp::float32>> var_local_torque_b = _wp_args->local_torque_b;
    wp::array_t<wp::vec_t<3, wp::float32>> var_com_pos_w = _wp_args->com_pos_w;
    wp::array_t<wp::quat_t<wp::float32>> var_link_quat_w = _wp_args->link_quat_w;
    wp::array_t<wp::vec_t<3, wp::float32>> var_out_force_b = _wp_args->out_force_b;
    wp::array_t<wp::vec_t<3, wp::float32>> var_out_torque_b = _wp_args->out_torque_b;
    wp::array_t<wp::vec_t<3, wp::float32>> adj_global_force_w = _wp_adj_args->global_force_w;
    wp::array_t<wp::vec_t<3, wp::float32>> adj_global_torque_w = _wp_adj_args->global_torque_w;
    wp::array_t<wp::vec_t<3, wp::float32>> adj_global_force_at_com_w = _wp_adj_args->global_force_at_com_w;
    wp::array_t<wp::vec_t<3, wp::float32>> adj_local_force_b = _wp_adj_args->local_force_b;
    wp::array_t<wp::vec_t<3, wp::float32>> adj_local_torque_b = _wp_adj_args->local_torque_b;
    wp::array_t<wp::vec_t<3, wp::float32>> adj_com_pos_w = _wp_adj_args->com_pos_w;
    wp::array_t<wp::quat_t<wp::float32>> adj_link_quat_w = _wp_adj_args->link_quat_w;
    wp::array_t<wp::vec_t<3, wp::float32>> adj_out_force_b = _wp_adj_args->out_force_b;
    wp::array_t<wp::vec_t<3, wp::float32>> adj_out_torque_b = _wp_adj_args->out_torque_b;
    //---------
    // primal vars
    wp::int32 var_0;
    wp::int32 var_1;
    wp::vec_t<3, wp::float32>* var_2;
    wp::vec_t<3, wp::float32>* var_3;
    wp::vec_t<3, wp::float32> var_4;
    wp::vec_t<3, wp::float32> var_5;
    wp::vec_t<3, wp::float32> var_6;
    wp::vec_t<3, wp::float32>* var_7;
    wp::vec_t<3, wp::float32>* var_8;
    wp::vec_t<3, wp::float32>* var_9;
    wp::vec_t<3, wp::float32> var_10;
    wp::vec_t<3, wp::float32> var_11;
    wp::vec_t<3, wp::float32> var_12;
    wp::vec_t<3, wp::float32> var_13;
    wp::vec_t<3, wp::float32> var_14;
    wp::quat_t<wp::float32>* var_15;
    wp::vec_t<3, wp::float32> var_16;
    wp::quat_t<wp::float32> var_17;
    wp::vec_t<3, wp::float32>* var_18;
    wp::vec_t<3, wp::float32> var_19;
    wp::vec_t<3, wp::float32> var_20;
    wp::quat_t<wp::float32>* var_21;
    wp::vec_t<3, wp::float32> var_22;
    wp::quat_t<wp::float32> var_23;
    wp::vec_t<3, wp::float32>* var_24;
    wp::vec_t<3, wp::float32> var_25;
    wp::vec_t<3, wp::float32> var_26;
    //---------
    // dual vars
    wp::int32 adj_0 = {};
    wp::int32 adj_1 = {};
    wp::vec_t<3, wp::float32> adj_2 = {};
    wp::vec_t<3, wp::float32> adj_3 = {};
    wp::vec_t<3, wp::float32> adj_4 = {};
    wp::vec_t<3, wp::float32> adj_5 = {};
    wp::vec_t<3, wp::float32> adj_6 = {};
    wp::vec_t<3, wp::float32> adj_7 = {};
    wp::vec_t<3, wp::float32> adj_8 = {};
    wp::vec_t<3, wp::float32> adj_9 = {};
    wp::vec_t<3, wp::float32> adj_10 = {};
    wp::vec_t<3, wp::float32> adj_11 = {};
    wp::vec_t<3, wp::float32> adj_12 = {};
    wp::vec_t<3, wp::float32> adj_13 = {};
    wp::vec_t<3, wp::float32> adj_14 = {};
    wp::quat_t<wp::float32> adj_15 = {};
    wp::vec_t<3, wp::float32> adj_16 = {};
    wp::quat_t<wp::float32> adj_17 = {};
    wp::vec_t<3, wp::float32> adj_18 = {};
    wp::vec_t<3, wp::float32> adj_19 = {};
    wp::vec_t<3, wp::float32> adj_20 = {};
    wp::quat_t<wp::float32> adj_21 = {};
    wp::vec_t<3, wp::float32> adj_22 = {};
    wp::quat_t<wp::float32> adj_23 = {};
    wp::vec_t<3, wp::float32> adj_24 = {};
    wp::vec_t<3, wp::float32> adj_25 = {};
    wp::vec_t<3, wp::float32> adj_26 = {};
    //---------
    // forward
    // def compose_wrench_to_body_frame(                                                      <L 629>
    // tid_env, tid_body = wp.tid()                                                           <L 649>
    builtin_tid2d(var_0, var_1);
    // total_force_w = global_force_w[tid_env, tid_body] + global_force_at_com_w[tid_env, tid_body]       <L 650>
    var_2 = wp::address(var_global_force_w, var_0, var_1);
    var_3 = wp::address(var_global_force_at_com_w, var_0, var_1);
    var_5 = wp::load(var_2);
    var_6 = wp::load(var_3);
    var_4 = wp::add(var_5, var_6);
    // corrected_torque_w = global_torque_w[tid_env, tid_body] - wp.cross(                    <L 651>
    var_7 = wp::address(var_global_torque_w, var_0, var_1);
    // com_pos_w[tid_env, tid_body], global_force_w[tid_env, tid_body]                        <L 652>
    var_8 = wp::address(var_com_pos_w, var_0, var_1);
    var_9 = wp::address(var_global_force_w, var_0, var_1);
    var_11 = wp::load(var_8);
    var_12 = wp::load(var_9);
    var_10 = wp::cross(var_11, var_12);
    var_14 = wp::load(var_7);
    var_13 = wp::sub(var_14, var_10);
    // out_force_b[tid_env, tid_body] = (                                                     <L 654>
    // wp.quat_rotate_inv(link_quat_w[tid_env, tid_body], total_force_w) + local_force_b[tid_env, tid_body]       <L 655>
    var_15 = wp::address(var_link_quat_w, var_0, var_1);
    var_17 = wp::load(var_15);
    var_16 = wp::quat_rotate_inv(var_17, var_4);
    var_18 = wp::address(var_local_force_b, var_0, var_1);
    var_20 = wp::load(var_18);
    var_19 = wp::add(var_16, var_20);
    // out_force_b[tid_env, tid_body] = (                                                     <L 654>
    // wp::array_store(var_out_force_b, var_0, var_1, var_19);
    // out_torque_b[tid_env, tid_body] = (                                                    <L 657>
    // wp.quat_rotate_inv(link_quat_w[tid_env, tid_body], corrected_torque_w) + local_torque_b[tid_env, tid_body]       <L 658>
    var_21 = wp::address(var_link_quat_w, var_0, var_1);
    var_23 = wp::load(var_21);
    var_22 = wp::quat_rotate_inv(var_23, var_13);
    var_24 = wp::address(var_local_torque_b, var_0, var_1);
    var_26 = wp::load(var_24);
    var_25 = wp::add(var_22, var_26);
    // out_torque_b[tid_env, tid_body] = (                                                    <L 657>
    // wp::array_store(var_out_torque_b, var_0, var_1, var_25);
    //---------
    // reverse
    wp::adj_array_store(var_out_torque_b, var_0, var_1, var_25, adj_out_torque_b, adj_0, adj_1, adj_25);
    // adj: out_torque_b[tid_env, tid_body] = (                                               <L 657>
    wp::adj_add(var_22, var_26, adj_22, adj_24, adj_25);
    wp::adj_address(var_local_torque_b, var_0, var_1, adj_local_torque_b, adj_0, adj_1, adj_24);
    wp::adj_quat_rotate_inv(var_23, var_13, adj_21, adj_13, adj_22);
    wp::adj_address(var_link_quat_w, var_0, var_1, adj_link_quat_w, adj_0, adj_1, adj_21);
    // adj: wp.quat_rotate_inv(link_quat_w[tid_env, tid_body], corrected_torque_w) + local_torque_b[tid_env, tid_body]  <L 658>
    // adj: out_torque_b[tid_env, tid_body] = (                                               <L 657>
    wp::adj_array_store(var_out_force_b, var_0, var_1, var_19, adj_out_force_b, adj_0, adj_1, adj_19);
    // adj: out_force_b[tid_env, tid_body] = (                                                <L 654>
    wp::adj_add(var_16, var_20, adj_16, adj_18, adj_19);
    wp::adj_address(var_local_force_b, var_0, var_1, adj_local_force_b, adj_0, adj_1, adj_18);
    wp::adj_quat_rotate_inv(var_17, var_4, adj_15, adj_4, adj_16);
    wp::adj_address(var_link_quat_w, var_0, var_1, adj_link_quat_w, adj_0, adj_1, adj_15);
    // adj: wp.quat_rotate_inv(link_quat_w[tid_env, tid_body], total_force_w) + local_force_b[tid_env, tid_body]  <L 655>
    // adj: out_force_b[tid_env, tid_body] = (                                                <L 654>
    wp::adj_sub(var_14, var_10, adj_7, adj_10, adj_13);
    wp::adj_cross(var_11, var_12, adj_8, adj_9, adj_10);
    wp::adj_address(var_global_force_w, var_0, var_1, adj_global_force_w, adj_0, adj_1, adj_9);
    wp::adj_address(var_com_pos_w, var_0, var_1, adj_com_pos_w, adj_0, adj_1, adj_8);
    // adj: com_pos_w[tid_env, tid_body], global_force_w[tid_env, tid_body]                   <L 652>
    wp::adj_address(var_global_torque_w, var_0, var_1, adj_global_torque_w, adj_0, adj_1, adj_7);
    // adj: corrected_torque_w = global_torque_w[tid_env, tid_body] - wp.cross(               <L 651>
    wp::adj_add(var_5, var_6, adj_2, adj_3, adj_4);
    wp::adj_address(var_global_force_at_com_w, var_0, var_1, adj_global_force_at_com_w, adj_0, adj_1, adj_3);
    wp::adj_address(var_global_force_w, var_0, var_1, adj_global_force_w, adj_0, adj_1, adj_2);
    // adj: total_force_w = global_force_w[tid_env, tid_body] + global_force_at_com_w[tid_env, tid_body]  <L 650>
    // adj: tid_env, tid_body = wp.tid()                                                      <L 649>
    // adj: def compose_wrench_to_body_frame(                                                 <L 629>
    return;
}



extern "C" {

// Python CPU entry points
WP_API void compose_wrench_to_body_frame_64cf3c01_cpu_forward(
    wp::launch_bounds_t<2> *dim,
    wp_args_compose_wrench_to_body_frame_64cf3c01 *_wp_args)
{
    wp::tile_shared_storage_t tile_mem;
#if defined(WP_ENABLE_TILES_IN_STACK_MEMORY)
    wp::shared_tile_storage = &tile_mem;
#endif

    for (size_t task_index = 0; task_index < dim->size; ++task_index)
    {
        compose_wrench_to_body_frame_64cf3c01_cpu_kernel_forward(*dim, task_index, _wp_args);
    }
}

} // extern C



extern "C" {

WP_API void compose_wrench_to_body_frame_64cf3c01_cpu_backward(
    wp::launch_bounds_t<2> *dim,
    wp_args_compose_wrench_to_body_frame_64cf3c01 *_wp_args,
    wp_args_compose_wrench_to_body_frame_64cf3c01 *_wp_adj_args)
{
    wp::tile_shared_storage_t tile_mem;
#if defined(WP_ENABLE_TILES_IN_STACK_MEMORY)
    wp::shared_tile_storage = &tile_mem;
#endif

    for (size_t task_index = 0; task_index < dim->size; ++task_index)
    {
        compose_wrench_to_body_frame_64cf3c01_cpu_kernel_backward(*dim, task_index, _wp_args, _wp_adj_args);
    }
}

} // extern C

struct wp_args_raycast_mesh_masked_kernel_68eaf428 {
    wp::uint64 mesh;
    wp::array_t<bool> env_mask;
    wp::array_t<wp::vec_t<3, wp::float32>> ray_starts;
    wp::array_t<wp::vec_t<3, wp::float32>> ray_directions;
    wp::float32 max_dist;
    wp::int32 return_distance;
    wp::int32 return_normal;
    wp::array_t<wp::vec_t<3, wp::float32>> ray_hits;
    wp::array_t<wp::float32> ray_distance;
    wp::array_t<wp::vec_t<3, wp::float32>> ray_normal;
};


void raycast_mesh_masked_kernel_68eaf428_cpu_kernel_forward(
    wp::launch_bounds_t<2> dim,
    size_t task_index,
    wp_args_raycast_mesh_masked_kernel_68eaf428 *_wp_args)
{
    //---------
    // argument vars
    wp::uint64 var_mesh = _wp_args->mesh;
    wp::array_t<bool> var_env_mask = _wp_args->env_mask;
    wp::array_t<wp::vec_t<3, wp::float32>> var_ray_starts = _wp_args->ray_starts;
    wp::array_t<wp::vec_t<3, wp::float32>> var_ray_directions = _wp_args->ray_directions;
    wp::float32 var_max_dist = _wp_args->max_dist;
    wp::int32 var_return_distance = _wp_args->return_distance;
    wp::int32 var_return_normal = _wp_args->return_normal;
    wp::array_t<wp::vec_t<3, wp::float32>> var_ray_hits = _wp_args->ray_hits;
    wp::array_t<wp::float32> var_ray_distance = _wp_args->ray_distance;
    wp::array_t<wp::vec_t<3, wp::float32>> var_ray_normal = _wp_args->ray_normal;
    //---------
    // primal vars
    wp::int32 var_0;
    wp::int32 var_1;
    bool* var_2;
    bool var_3;
    bool var_4;
    const wp::float32 var_5 = 0.0;
    wp::float32 var_6;
    const wp::float32 var_7 = 0.0;
    wp::float32 var_8;
    const wp::float32 var_9 = 0.0;
    wp::float32 var_10;
    const wp::float32 var_11 = 0.0;
    wp::float32 var_12;
    wp::vec_t<3, wp::float32> var_13;
    const wp::int32 var_14 = 0;
    wp::int32 var_15;
    wp::vec_t<3, wp::float32>* var_16;
    wp::vec_t<3, wp::float32>* var_17;
    bool var_18;
    const wp::int32 var_19 = -1;
    wp::vec_t<3, wp::float32> var_20;
    wp::vec_t<3, wp::float32> var_21;
    wp::vec_t<3, wp::float32>* var_22;
    wp::vec_t<3, wp::float32>* var_23;
    wp::vec_t<3, wp::float32> var_24;
    wp::vec_t<3, wp::float32> var_25;
    wp::vec_t<3, wp::float32> var_26;
    wp::vec_t<3, wp::float32> var_27;
    const wp::int32 var_28 = 1;
    bool var_29;
    const wp::int32 var_30 = 1;
    bool var_31;
    //---------
    // forward
    // def raycast_mesh_masked_kernel(                                                        <L 86>
    // env, ray = wp.tid()                                                                    <L 122>
    builtin_tid2d(var_0, var_1);
    // if not env_mask[env]:                                                                  <L 123>
    var_2 = wp::address(var_env_mask, var_0);
    var_4 = wp::load(var_2);
    var_3 = wp::unot(var_4);
    if (var_3) {
        // return                                                                             <L 124>
        return;
    }
    // t = float(0.0)                                                                         <L 126>
    var_6 = wp::float(var_5);
    // u = float(0.0)                                                                         <L 127>
    var_8 = wp::float(var_7);
    // v = float(0.0)                                                                         <L 128>
    var_10 = wp::float(var_9);
    // sign = float(0.0)                                                                      <L 129>
    var_12 = wp::float(var_11);
    // n = wp.vec3f()                                                                         <L 130>
    var_13 = wp::vec_t<3, wp::float32>();
    // f = int(0)                                                                             <L 131>
    var_15 = wp::int(var_14);
    // hit = wp.mesh_query_ray(mesh, ray_starts[env, ray], ray_directions[env, ray], max_dist, t, u, v, sign, n, f)       <L 133>
    var_16 = wp::address(var_ray_starts, var_0, var_1);
    var_17 = wp::address(var_ray_directions, var_0, var_1);
    var_20 = wp::load(var_16);
    var_21 = wp::load(var_17);
    var_18 = wp::mesh_query_ray(var_mesh, var_20, var_21, var_max_dist, var_6, var_8, var_10, var_12, var_13, var_15, var_19);
    // if hit:                                                                                <L 134>
    if (var_18) {
        // ray_hits[env, ray] = ray_starts[env, ray] + t * ray_directions[env, ray]           <L 135>
        var_22 = wp::address(var_ray_starts, var_0, var_1);
        var_23 = wp::address(var_ray_directions, var_0, var_1);
        var_25 = wp::load(var_23);
        var_24 = wp::mul(var_6, var_25);
        var_27 = wp::load(var_22);
        var_26 = wp::add(var_27, var_24);
        wp::array_store(var_ray_hits, var_0, var_1, var_26);
        // if return_distance == 1:                                                           <L 136>
        var_29 = (var_return_distance == var_28);
        if (var_29) {
            // ray_distance[env, ray] = t                                                     <L 137>
            wp::array_store(var_ray_distance, var_0, var_1, var_6);
        }
        // if return_normal == 1:                                                             <L 138>
        var_31 = (var_return_normal == var_30);
        if (var_31) {
            // ray_normal[env, ray] = n                                                       <L 139>
            wp::array_store(var_ray_normal, var_0, var_1, var_13);
        }
    }
}



extern "C" {

// Python CPU entry points
WP_API void raycast_mesh_masked_kernel_68eaf428_cpu_forward(
    wp::launch_bounds_t<2> *dim,
    wp_args_raycast_mesh_masked_kernel_68eaf428 *_wp_args)
{
    wp::tile_shared_storage_t tile_mem;
#if defined(WP_ENABLE_TILES_IN_STACK_MEMORY)
    wp::shared_tile_storage = &tile_mem;
#endif

    for (size_t task_index = 0; task_index < dim->size; ++task_index)
    {
        raycast_mesh_masked_kernel_68eaf428_cpu_kernel_forward(*dim, task_index, _wp_args);
    }
}

} // extern C

struct wp_args_reshape_tiled_image_7c3c328a {
    wp::array_t<wp::uint8> tiled_image_buffer;
    wp::array_t<wp::uint8> batched_image;
    wp::int32 image_height;
    wp::int32 image_width;
    wp::int32 num_channels;
    wp::int32 num_tiles_x;
};


void reshape_tiled_image_7c3c328a_cpu_kernel_forward(
    wp::launch_bounds_t<3> dim,
    size_t task_index,
    wp_args_reshape_tiled_image_7c3c328a *_wp_args)
{
    //---------
    // argument vars
    wp::array_t<wp::uint8> var_tiled_image_buffer = _wp_args->tiled_image_buffer;
    wp::array_t<wp::uint8> var_batched_image = _wp_args->batched_image;
    wp::int32 var_image_height = _wp_args->image_height;
    wp::int32 var_image_width = _wp_args->image_width;
    wp::int32 var_num_channels = _wp_args->num_channels;
    wp::int32 var_num_tiles_x = _wp_args->num_tiles_x;
    //---------
    // primal vars
    wp::int32 var_0;
    wp::int32 var_1;
    wp::int32 var_2;
    wp::int32 var_3;
    wp::int32 var_4;
    wp::int32 var_5;
    wp::int32 var_6;
    wp::int32 var_7;
    wp::int32 var_8;
    wp::range_t var_9;
    wp::int32 var_10;
    wp::uint8* var_11;
    wp::uint8 var_12;
    wp::uint8 var_13;
    //---------
    // forward
    // def reshape_tiled_image(                                                               <L 1>
    // camera_id, height_id, width_id = wp.tid()                                              <L 30>
    builtin_tid3d(var_0, var_1, var_2);
    // tile_x_id = camera_id % num_tiles_x                                                    <L 33>
    var_3 = wp::mod(var_0, var_num_tiles_x);
    // tile_y_id = camera_id // num_tiles_x                                                   <L 34>
    var_4 = wp::floordiv(var_0, var_num_tiles_x);
    // row = image_height * tile_y_id + height_id                                             <L 36>
    var_5 = wp::mul(var_image_height, var_4);
    var_6 = wp::add(var_5, var_1);
    // col = image_width * tile_x_id + width_id                                               <L 37>
    var_7 = wp::mul(var_image_width, var_3);
    var_8 = wp::add(var_7, var_2);
    // for i in range(num_channels):                                                          <L 40>
    var_9 = wp::range(var_num_channels);
    start_for_0:;
        if (iter_cmp(var_9) == 0) goto end_for_0;
        var_10 = wp::iter_next(var_9);
        // batched_image[camera_id, height_id, width_id, i] = batched_image.dtype(tiled_image_buffer[row, col, i])       <L 41>
        var_11 = wp::address(var_tiled_image_buffer, var_6, var_8, var_10);
        var_13 = wp::load(var_11);
        var_12 = wp::uint8(var_13);
        wp::array_store(var_batched_image, var_0, var_1, var_2, var_10, var_12);
        goto start_for_0;
    end_for_0:;
}



extern "C" {

// Python CPU entry points
WP_API void reshape_tiled_image_7c3c328a_cpu_forward(
    wp::launch_bounds_t<3> *dim,
    wp_args_reshape_tiled_image_7c3c328a *_wp_args)
{
    wp::tile_shared_storage_t tile_mem;
#if defined(WP_ENABLE_TILES_IN_STACK_MEMORY)
    wp::shared_tile_storage = &tile_mem;
#endif

    for (size_t task_index = 0; task_index < dim->size; ++task_index)
    {
        reshape_tiled_image_7c3c328a_cpu_kernel_forward(*dim, task_index, _wp_args);
    }
}

} // extern C

struct wp_args_gather_subtract_2d_83675472 {
    wp::array_t<wp::float32> a;
    wp::array_t<wp::int32> env_ids;
    wp::array_t<wp::int32> item_ids;
    wp::array_t<wp::float32> b;
    wp::array_t<wp::float32> out;
};


void gather_subtract_2d_83675472_cpu_kernel_forward(
    wp::launch_bounds_t<2> dim,
    size_t task_index,
    wp_args_gather_subtract_2d_83675472 *_wp_args)
{
    //---------
    // argument vars
    wp::array_t<wp::float32> var_a = _wp_args->a;
    wp::array_t<wp::int32> var_env_ids = _wp_args->env_ids;
    wp::array_t<wp::int32> var_item_ids = _wp_args->item_ids;
    wp::array_t<wp::float32> var_b = _wp_args->b;
    wp::array_t<wp::float32> var_out = _wp_args->out;
    //---------
    // primal vars
    wp::int32 var_0;
    wp::int32 var_1;
    wp::int32* var_2;
    wp::int32 var_3;
    wp::int32 var_4;
    wp::int32* var_5;
    wp::int32 var_6;
    wp::int32 var_7;
    wp::float32* var_8;
    wp::float32* var_9;
    wp::float32 var_10;
    wp::float32 var_11;
    wp::float32 var_12;
    //---------
    // forward
    // def gather_subtract_2d(                                                                <L 1>
    // i, j = wp.tid()                                                                        <L 17>
    builtin_tid2d(var_0, var_1);
    // out[i, j] = a[wp.int32(env_ids[i]), wp.int32(item_ids[j])] - b[i, j]                   <L 18>
    var_2 = wp::address(var_env_ids, var_0);
    var_4 = wp::load(var_2);
    var_3 = wp::int32(var_4);
    var_5 = wp::address(var_item_ids, var_1);
    var_7 = wp::load(var_5);
    var_6 = wp::int32(var_7);
    var_8 = wp::address(var_a, var_3, var_6);
    var_9 = wp::address(var_b, var_0, var_1);
    var_11 = wp::load(var_8);
    var_12 = wp::load(var_9);
    var_10 = wp::sub(var_11, var_12);
    wp::array_store(var_out, var_0, var_1, var_10);
}



void gather_subtract_2d_83675472_cpu_kernel_backward(
    wp::launch_bounds_t<2> dim,
    size_t task_index,
    wp_args_gather_subtract_2d_83675472 *_wp_args,
    wp_args_gather_subtract_2d_83675472 *_wp_adj_args)
{
    //---------
    // argument vars
    wp::array_t<wp::float32> var_a = _wp_args->a;
    wp::array_t<wp::int32> var_env_ids = _wp_args->env_ids;
    wp::array_t<wp::int32> var_item_ids = _wp_args->item_ids;
    wp::array_t<wp::float32> var_b = _wp_args->b;
    wp::array_t<wp::float32> var_out = _wp_args->out;
    wp::array_t<wp::float32> adj_a = _wp_adj_args->a;
    wp::array_t<wp::int32> adj_env_ids = _wp_adj_args->env_ids;
    wp::array_t<wp::int32> adj_item_ids = _wp_adj_args->item_ids;
    wp::array_t<wp::float32> adj_b = _wp_adj_args->b;
    wp::array_t<wp::float32> adj_out = _wp_adj_args->out;
    //---------
    // primal vars
    wp::int32 var_0;
    wp::int32 var_1;
    wp::int32* var_2;
    wp::int32 var_3;
    wp::int32 var_4;
    wp::int32* var_5;
    wp::int32 var_6;
    wp::int32 var_7;
    wp::float32* var_8;
    wp::float32* var_9;
    wp::float32 var_10;
    wp::float32 var_11;
    wp::float32 var_12;
    //---------
    // dual vars
    wp::int32 adj_0 = {};
    wp::int32 adj_1 = {};
    wp::int32 adj_2 = {};
    wp::int32 adj_3 = {};
    wp::int32 adj_4 = {};
    wp::int32 adj_5 = {};
    wp::int32 adj_6 = {};
    wp::int32 adj_7 = {};
    wp::float32 adj_8 = {};
    wp::float32 adj_9 = {};
    wp::float32 adj_10 = {};
    wp::float32 adj_11 = {};
    wp::float32 adj_12 = {};
    //---------
    // forward
    // def gather_subtract_2d(                                                                <L 1>
    // i, j = wp.tid()                                                                        <L 17>
    builtin_tid2d(var_0, var_1);
    // out[i, j] = a[wp.int32(env_ids[i]), wp.int32(item_ids[j])] - b[i, j]                   <L 18>
    var_2 = wp::address(var_env_ids, var_0);
    var_4 = wp::load(var_2);
    var_3 = wp::int32(var_4);
    var_5 = wp::address(var_item_ids, var_1);
    var_7 = wp::load(var_5);
    var_6 = wp::int32(var_7);
    var_8 = wp::address(var_a, var_3, var_6);
    var_9 = wp::address(var_b, var_0, var_1);
    var_11 = wp::load(var_8);
    var_12 = wp::load(var_9);
    var_10 = wp::sub(var_11, var_12);
    // wp::array_store(var_out, var_0, var_1, var_10);
    //---------
    // reverse
    wp::adj_array_store(var_out, var_0, var_1, var_10, adj_out, adj_0, adj_1, adj_10);
    wp::adj_sub(var_11, var_12, adj_8, adj_9, adj_10);
    wp::adj_address(var_b, var_0, var_1, adj_b, adj_0, adj_1, adj_9);
    wp::adj_address(var_a, var_3, var_6, adj_a, adj_3, adj_6, adj_8);
    wp::adj_address(var_item_ids, var_1, adj_item_ids, adj_1, adj_5);
    wp::adj_address(var_env_ids, var_0, adj_env_ids, adj_0, adj_2);
    // adj: out[i, j] = a[wp.int32(env_ids[i]), wp.int32(item_ids[j])] - b[i, j]              <L 18>
    // adj: i, j = wp.tid()                                                                   <L 17>
    // adj: def gather_subtract_2d(                                                           <L 1>
    return;
}



extern "C" {

// Python CPU entry points
WP_API void gather_subtract_2d_83675472_cpu_forward(
    wp::launch_bounds_t<2> *dim,
    wp_args_gather_subtract_2d_83675472 *_wp_args)
{
    wp::tile_shared_storage_t tile_mem;
#if defined(WP_ENABLE_TILES_IN_STACK_MEMORY)
    wp::shared_tile_storage = &tile_mem;
#endif

    for (size_t task_index = 0; task_index < dim->size; ++task_index)
    {
        gather_subtract_2d_83675472_cpu_kernel_forward(*dim, task_index, _wp_args);
    }
}

} // extern C



extern "C" {

WP_API void gather_subtract_2d_83675472_cpu_backward(
    wp::launch_bounds_t<2> *dim,
    wp_args_gather_subtract_2d_83675472 *_wp_args,
    wp_args_gather_subtract_2d_83675472 *_wp_adj_args)
{
    wp::tile_shared_storage_t tile_mem;
#if defined(WP_ENABLE_TILES_IN_STACK_MEMORY)
    wp::shared_tile_storage = &tile_mem;
#endif

    for (size_t task_index = 0; task_index < dim->size; ++task_index)
    {
        gather_subtract_2d_83675472_cpu_kernel_backward(*dim, task_index, _wp_args, _wp_adj_args);
    }
}

} // extern C

struct wp_args_raycast_dynamic_meshes_kernel_85f1976d {
    wp::array_t<bool> env_mask;
    wp::array_t<wp::uint64> mesh;
    wp::array_t<wp::vec_t<3, wp::float32>> ray_starts;
    wp::array_t<wp::vec_t<3, wp::float32>> ray_directions;
    wp::array_t<wp::vec_t<3, wp::float32>> ray_hits;
    wp::array_t<wp::float32> ray_distance;
    wp::array_t<wp::vec_t<3, wp::float32>> ray_normal;
    wp::array_t<wp::int32> ray_face_id;
    wp::array_t<wp::int16> ray_mesh_id;
    wp::array_t<wp::vec_t<3, wp::float32>> mesh_positions;
    wp::array_t<wp::quat_t<wp::float32>> mesh_rotations;
    wp::float32 max_dist;
    wp::int32 return_normal;
    wp::int32 return_face_id;
    wp::int32 return_mesh_id;
};


void raycast_dynamic_meshes_kernel_85f1976d_cpu_kernel_forward(
    wp::launch_bounds_t<3> dim,
    size_t task_index,
    wp_args_raycast_dynamic_meshes_kernel_85f1976d *_wp_args)
{
    //---------
    // argument vars
    wp::array_t<bool> var_env_mask = _wp_args->env_mask;
    wp::array_t<wp::uint64> var_mesh = _wp_args->mesh;
    wp::array_t<wp::vec_t<3, wp::float32>> var_ray_starts = _wp_args->ray_starts;
    wp::array_t<wp::vec_t<3, wp::float32>> var_ray_directions = _wp_args->ray_directions;
    wp::array_t<wp::vec_t<3, wp::float32>> var_ray_hits = _wp_args->ray_hits;
    wp::array_t<wp::float32> var_ray_distance = _wp_args->ray_distance;
    wp::array_t<wp::vec_t<3, wp::float32>> var_ray_normal = _wp_args->ray_normal;
    wp::array_t<wp::int32> var_ray_face_id = _wp_args->ray_face_id;
    wp::array_t<wp::int16> var_ray_mesh_id = _wp_args->ray_mesh_id;
    wp::array_t<wp::vec_t<3, wp::float32>> var_mesh_positions = _wp_args->mesh_positions;
    wp::array_t<wp::quat_t<wp::float32>> var_mesh_rotations = _wp_args->mesh_rotations;
    wp::float32 var_max_dist = _wp_args->max_dist;
    wp::int32 var_return_normal = _wp_args->return_normal;
    wp::int32 var_return_face_id = _wp_args->return_face_id;
    wp::int32 var_return_mesh_id = _wp_args->return_mesh_id;
    //---------
    // primal vars
    wp::int32 var_0;
    wp::int32 var_1;
    wp::int32 var_2;
    bool* var_3;
    bool var_4;
    bool var_5;
    wp::vec_t<3, wp::float32>* var_6;
    wp::quat_t<wp::float32>* var_7;
    wp::transform_t<wp::float32> var_8;
    wp::vec_t<3, wp::float32> var_9;
    wp::quat_t<wp::float32> var_10;
    wp::transform_t<wp::float32> var_11;
    wp::vec_t<3, wp::float32>* var_12;
    wp::vec_t<3, wp::float32> var_13;
    wp::vec_t<3, wp::float32> var_14;
    wp::vec_t<3, wp::float32>* var_15;
    wp::vec_t<3, wp::float32> var_16;
    wp::vec_t<3, wp::float32> var_17;
    wp::uint64* var_18;
    wp::mesh_query_ray_t var_19;
    const wp::int32 var_20 = -1;
    wp::uint64 var_21;
    bool* var_22;
    bool var_23;
    wp::float32* var_24;
    wp::float32 var_25;
    wp::float32 var_26;
    wp::float32* var_27;
    wp::float32* var_28;
    bool var_29;
    wp::float32 var_30;
    wp::float32 var_31;
    wp::float32* var_32;
    wp::vec_t<3, wp::float32> var_33;
    wp::float32 var_34;
    wp::vec_t<3, wp::float32> var_35;
    wp::vec_t<3, wp::float32> var_36;
    const wp::int32 var_37 = 1;
    bool var_38;
    wp::vec_t<3, wp::float32>* var_39;
    wp::vec_t<3, wp::float32> var_40;
    wp::vec_t<3, wp::float32> var_41;
    const wp::int32 var_42 = 1;
    bool var_43;
    wp::int32* var_44;
    wp::int32 var_45;
    const wp::int32 var_46 = 1;
    bool var_47;
    wp::int16 var_48;
    bool var_49;
    //---------
    // forward
    // def raycast_dynamic_meshes_kernel(                                                     <L 233>
    // tid_mesh_id, tid_env, tid_ray = wp.tid()                                               <L 298>
    builtin_tid3d(var_0, var_1, var_2);
    // if not env_mask[tid_env]:                                                              <L 299>
    var_3 = wp::address(var_env_mask, var_1);
    var_5 = wp::load(var_3);
    var_4 = wp::unot(var_5);
    if (var_4) {
        // return                                                                             <L 300>
        return;
    }
    // mesh_pose = wp.transform(mesh_positions[tid_env, tid_mesh_id], mesh_rotations[tid_env, tid_mesh_id])       <L 302>
    var_6 = wp::address(var_mesh_positions, var_1, var_0);
    var_7 = wp::address(var_mesh_rotations, var_1, var_0);
    var_9 = wp::load(var_6);
    var_10 = wp::load(var_7);
    var_8 = wp::transform_t<wp::float32>(var_9, var_10);
    // mesh_pose_inv = wp.transform_inverse(mesh_pose)                                        <L 303>
    var_11 = wp::transform_inverse(var_8);
    // direction = wp.transform_vector(mesh_pose_inv, ray_directions[tid_env, tid_ray])       <L 304>
    var_12 = wp::address(var_ray_directions, var_1, var_2);
    var_14 = wp::load(var_12);
    var_13 = wp::transform_vector(var_11, var_14);
    // start_pos = wp.transform_point(mesh_pose_inv, ray_starts[tid_env, tid_ray])            <L 305>
    var_15 = wp::address(var_ray_starts, var_1, var_2);
    var_17 = wp::load(var_15);
    var_16 = wp::transform_point(var_11, var_17);
    // mesh_query_ray_t = wp.mesh_query_ray(mesh[tid_env, tid_mesh_id], start_pos, direction, max_dist)       <L 308>
    var_18 = wp::address(var_mesh, var_1, var_0);
    var_21 = wp::load(var_18);
    var_19 = wp::mesh_query_ray(var_21, var_16, var_13, var_max_dist, var_20);
    // if mesh_query_ray_t.result:                                                            <L 310>
    var_22 = &((var_19).result);
    var_23 = wp::load(var_22);
    if (var_23) {
        // wp.atomic_min(ray_distance, tid_env, tid_ray, mesh_query_ray_t.t)                  <L 311>
        var_24 = &((var_19).t);
        var_26 = wp::load(var_24);
        var_25 = wp::atomic_min(var_ray_distance, var_1, var_2, var_26);
        // if mesh_query_ray_t.t == ray_distance[tid_env, tid_ray]:                           <L 317>
        var_27 = &((var_19).t);
        var_28 = wp::address(var_ray_distance, var_1, var_2);
        var_30 = wp::load(var_27);
        var_31 = wp::load(var_28);
        var_29 = (var_30 == var_31);
        if (var_29) {
            // hit_pos = start_pos + mesh_query_ray_t.t * direction                           <L 319>
            var_32 = &((var_19).t);
            var_34 = wp::load(var_32);
            var_33 = wp::mul(var_34, var_13);
            var_35 = wp::add(var_16, var_33);
            // ray_hits[tid_env, tid_ray] = wp.transform_point(mesh_pose, hit_pos)            <L 320>
            var_36 = wp::transform_point(var_8, var_35);
            wp::array_store(var_ray_hits, var_1, var_2, var_36);
            // if return_normal == 1:                                                         <L 323>
            var_38 = (var_return_normal == var_37);
            if (var_38) {
                // n = wp.transform_vector(mesh_pose, mesh_query_ray_t.normal)                <L 324>
                var_39 = &((var_19).normal);
                var_41 = wp::load(var_39);
                var_40 = wp::transform_vector(var_8, var_41);
                // ray_normal[tid_env, tid_ray] = n                                           <L 325>
                wp::array_store(var_ray_normal, var_1, var_2, var_40);
            }
            // if return_face_id == 1:                                                        <L 326>
            var_43 = (var_return_face_id == var_42);
            if (var_43) {
                // ray_face_id[tid_env, tid_ray] = mesh_query_ray_t.face                      <L 327>
                var_44 = &((var_19).face);
                var_45 = wp::load(var_44);
                wp::array_store(var_ray_face_id, var_1, var_2, var_45);
            }
            // if return_mesh_id == 1:                                                        <L 328>
            var_47 = (var_return_mesh_id == var_46);
            if (var_47) {
                // ray_mesh_id[tid_env, tid_ray] = wp.int16(tid_mesh_id)                      <L 329>
                var_48 = wp::int16(var_0);
                wp::array_store(var_ray_mesh_id, var_1, var_2, var_48);
            }
        }
    }
    var_49 = wp::load(var_22);
}



extern "C" {

// Python CPU entry points
WP_API void raycast_dynamic_meshes_kernel_85f1976d_cpu_forward(
    wp::launch_bounds_t<3> *dim,
    wp_args_raycast_dynamic_meshes_kernel_85f1976d *_wp_args)
{
    wp::tile_shared_storage_t tile_mem;
#if defined(WP_ENABLE_TILES_IN_STACK_MEMORY)
    wp::shared_tile_storage = &tile_mem;
#endif

    for (size_t task_index = 0; task_index < dim->size; ++task_index)
    {
        raycast_dynamic_meshes_kernel_85f1976d_cpu_kernel_forward(*dim, task_index, _wp_args);
    }
}

} // extern C

struct wp_args_add_forces_to_dual_buffers_index_a340e469 {
    wp::array_t<wp::int64> env_ids;
    wp::array_t<wp::int64> body_ids;
    wp::array_t<wp::vec_t<3, wp::float32>> forces;
    wp::array_t<wp::vec_t<3, wp::float32>> torques;
    wp::array_t<wp::vec_t<3, wp::float32>> positions;
    wp::array_t<wp::vec_t<3, wp::float32>> global_force_w;
    wp::array_t<wp::vec_t<3, wp::float32>> global_torque_w;
    wp::array_t<wp::vec_t<3, wp::float32>> global_force_at_com_w;
    wp::array_t<wp::vec_t<3, wp::float32>> local_force_b;
    wp::array_t<wp::vec_t<3, wp::float32>> local_torque_b;
    bool is_global;
};


void add_forces_to_dual_buffers_index_a340e469_cpu_kernel_forward(
    wp::launch_bounds_t<2> dim,
    size_t task_index,
    wp_args_add_forces_to_dual_buffers_index_a340e469 *_wp_args)
{
    //---------
    // argument vars
    wp::array_t<wp::int64> var_env_ids = _wp_args->env_ids;
    wp::array_t<wp::int64> var_body_ids = _wp_args->body_ids;
    wp::array_t<wp::vec_t<3, wp::float32>> var_forces = _wp_args->forces;
    wp::array_t<wp::vec_t<3, wp::float32>> var_torques = _wp_args->torques;
    wp::array_t<wp::vec_t<3, wp::float32>> var_positions = _wp_args->positions;
    wp::array_t<wp::vec_t<3, wp::float32>> var_global_force_w = _wp_args->global_force_w;
    wp::array_t<wp::vec_t<3, wp::float32>> var_global_torque_w = _wp_args->global_torque_w;
    wp::array_t<wp::vec_t<3, wp::float32>> var_global_force_at_com_w = _wp_args->global_force_at_com_w;
    wp::array_t<wp::vec_t<3, wp::float32>> var_local_force_b = _wp_args->local_force_b;
    wp::array_t<wp::vec_t<3, wp::float32>> var_local_torque_b = _wp_args->local_torque_b;
    bool var_is_global = _wp_args->is_global;
    //---------
    // primal vars
    wp::int32 var_0;
    wp::int32 var_1;
    wp::int64* var_2;
    wp::int32 var_3;
    wp::int64 var_4;
    wp::int64* var_5;
    wp::int32 var_6;
    wp::int64 var_7;
    wp::vec_t<3, wp::float32>* var_8;
    wp::vec_t<3, wp::float32>* var_9;
    wp::vec_t<3, wp::float32> var_10;
    wp::vec_t<3, wp::float32> var_11;
    wp::vec_t<3, wp::float32> var_12;
    wp::vec_t<3, wp::float32>* var_13;
    wp::vec_t<3, wp::float32>* var_14;
    wp::vec_t<3, wp::float32>* var_15;
    wp::vec_t<3, wp::float32> var_16;
    wp::vec_t<3, wp::float32> var_17;
    wp::vec_t<3, wp::float32> var_18;
    wp::vec_t<3, wp::float32> var_19;
    wp::vec_t<3, wp::float32> var_20;
    wp::vec_t<3, wp::float32>* var_21;
    wp::vec_t<3, wp::float32>* var_22;
    wp::vec_t<3, wp::float32> var_23;
    wp::vec_t<3, wp::float32> var_24;
    wp::vec_t<3, wp::float32> var_25;
    wp::vec_t<3, wp::float32>* var_26;
    wp::vec_t<3, wp::float32>* var_27;
    wp::vec_t<3, wp::float32> var_28;
    wp::vec_t<3, wp::float32> var_29;
    wp::vec_t<3, wp::float32> var_30;
    wp::vec_t<3, wp::float32>* var_31;
    wp::vec_t<3, wp::float32>* var_32;
    wp::vec_t<3, wp::float32> var_33;
    wp::vec_t<3, wp::float32> var_34;
    wp::vec_t<3, wp::float32> var_35;
    wp::vec_t<3, wp::float32>* var_36;
    wp::vec_t<3, wp::float32>* var_37;
    wp::vec_t<3, wp::float32>* var_38;
    wp::vec_t<3, wp::float32> var_39;
    wp::vec_t<3, wp::float32> var_40;
    wp::vec_t<3, wp::float32> var_41;
    wp::vec_t<3, wp::float32> var_42;
    wp::vec_t<3, wp::float32> var_43;
    wp::vec_t<3, wp::float32>* var_44;
    wp::vec_t<3, wp::float32>* var_45;
    wp::vec_t<3, wp::float32> var_46;
    wp::vec_t<3, wp::float32> var_47;
    wp::vec_t<3, wp::float32> var_48;
    //---------
    // forward
    // def add_forces_to_dual_buffers_index(                                                  <L 1>
    // tid_env, tid_body = wp.tid()                                                           <L 19>
    builtin_tid2d(var_0, var_1);
    // ei = wp.int32(env_ids[tid_env])                                                        <L 20>
    var_2 = wp::address(var_env_ids, var_0);
    var_4 = wp::load(var_2);
    var_3 = wp::int32(var_4);
    // bi = wp.int32(body_ids[tid_body])                                                      <L 21>
    var_5 = wp::address(var_body_ids, var_1);
    var_7 = wp::load(var_5);
    var_6 = wp::int32(var_7);
    // if is_global:                                                                          <L 23>
    if (var_is_global) {
        // if forces:                                                                         <L 24>
        if (var_forces) {
            // if positions:                                                                  <L 25>
            if (var_positions) {
                // global_force_w[ei, bi] = global_force_w[ei, bi] + forces[tid_env, tid_body]       <L 26>
                var_8 = wp::address(var_global_force_w, var_3, var_6);
                var_9 = wp::address(var_forces, var_0, var_1);
                var_11 = wp::load(var_8);
                var_12 = wp::load(var_9);
                var_10 = wp::add(var_11, var_12);
                wp::array_store(var_global_force_w, var_3, var_6, var_10);
                // global_torque_w[ei, bi] = global_torque_w[ei, bi] + wp.cross(              <L 27>
                var_13 = wp::address(var_global_torque_w, var_3, var_6);
                // positions[tid_env, tid_body], forces[tid_env, tid_body]                    <L 28>
                var_14 = wp::address(var_positions, var_0, var_1);
                var_15 = wp::address(var_forces, var_0, var_1);
                var_17 = wp::load(var_14);
                var_18 = wp::load(var_15);
                var_16 = wp::cross(var_17, var_18);
                var_20 = wp::load(var_13);
                var_19 = wp::add(var_20, var_16);
                // global_torque_w[ei, bi] = global_torque_w[ei, bi] + wp.cross(              <L 27>
                wp::array_store(var_global_torque_w, var_3, var_6, var_19);
            }
            if (!var_positions) {
                // global_force_at_com_w[ei, bi] = global_force_at_com_w[ei, bi] + forces[tid_env, tid_body]       <L 31>
                var_21 = wp::address(var_global_force_at_com_w, var_3, var_6);
                var_22 = wp::address(var_forces, var_0, var_1);
                var_24 = wp::load(var_21);
                var_25 = wp::load(var_22);
                var_23 = wp::add(var_24, var_25);
                wp::array_store(var_global_force_at_com_w, var_3, var_6, var_23);
            }
        }
        // if torques:                                                                        <L 32>
        if (var_torques) {
            // global_torque_w[ei, bi] = global_torque_w[ei, bi] + torques[tid_env, tid_body]       <L 33>
            var_26 = wp::address(var_global_torque_w, var_3, var_6);
            var_27 = wp::address(var_torques, var_0, var_1);
            var_29 = wp::load(var_26);
            var_30 = wp::load(var_27);
            var_28 = wp::add(var_29, var_30);
            wp::array_store(var_global_torque_w, var_3, var_6, var_28);
        }
    }
    if (!var_is_global) {
        // if forces:                                                                         <L 35>
        if (var_forces) {
            // local_force_b[ei, bi] = local_force_b[ei, bi] + forces[tid_env, tid_body]       <L 36>
            var_31 = wp::address(var_local_force_b, var_3, var_6);
            var_32 = wp::address(var_forces, var_0, var_1);
            var_34 = wp::load(var_31);
            var_35 = wp::load(var_32);
            var_33 = wp::add(var_34, var_35);
            wp::array_store(var_local_force_b, var_3, var_6, var_33);
            // if positions:                                                                  <L 37>
            if (var_positions) {
                // local_torque_b[ei, bi] = local_torque_b[ei, bi] + wp.cross(                <L 38>
                var_36 = wp::address(var_local_torque_b, var_3, var_6);
                // positions[tid_env, tid_body], forces[tid_env, tid_body]                    <L 39>
                var_37 = wp::address(var_positions, var_0, var_1);
                var_38 = wp::address(var_forces, var_0, var_1);
                var_40 = wp::load(var_37);
                var_41 = wp::load(var_38);
                var_39 = wp::cross(var_40, var_41);
                var_43 = wp::load(var_36);
                var_42 = wp::add(var_43, var_39);
                // local_torque_b[ei, bi] = local_torque_b[ei, bi] + wp.cross(                <L 38>
                wp::array_store(var_local_torque_b, var_3, var_6, var_42);
            }
        }
        // if torques:                                                                        <L 41>
        if (var_torques) {
            // local_torque_b[ei, bi] = local_torque_b[ei, bi] + torques[tid_env, tid_body]       <L 42>
            var_44 = wp::address(var_local_torque_b, var_3, var_6);
            var_45 = wp::address(var_torques, var_0, var_1);
            var_47 = wp::load(var_44);
            var_48 = wp::load(var_45);
            var_46 = wp::add(var_47, var_48);
            wp::array_store(var_local_torque_b, var_3, var_6, var_46);
        }
    }
}



void add_forces_to_dual_buffers_index_a340e469_cpu_kernel_backward(
    wp::launch_bounds_t<2> dim,
    size_t task_index,
    wp_args_add_forces_to_dual_buffers_index_a340e469 *_wp_args,
    wp_args_add_forces_to_dual_buffers_index_a340e469 *_wp_adj_args)
{
    //---------
    // argument vars
    wp::array_t<wp::int64> var_env_ids = _wp_args->env_ids;
    wp::array_t<wp::int64> var_body_ids = _wp_args->body_ids;
    wp::array_t<wp::vec_t<3, wp::float32>> var_forces = _wp_args->forces;
    wp::array_t<wp::vec_t<3, wp::float32>> var_torques = _wp_args->torques;
    wp::array_t<wp::vec_t<3, wp::float32>> var_positions = _wp_args->positions;
    wp::array_t<wp::vec_t<3, wp::float32>> var_global_force_w = _wp_args->global_force_w;
    wp::array_t<wp::vec_t<3, wp::float32>> var_global_torque_w = _wp_args->global_torque_w;
    wp::array_t<wp::vec_t<3, wp::float32>> var_global_force_at_com_w = _wp_args->global_force_at_com_w;
    wp::array_t<wp::vec_t<3, wp::float32>> var_local_force_b = _wp_args->local_force_b;
    wp::array_t<wp::vec_t<3, wp::float32>> var_local_torque_b = _wp_args->local_torque_b;
    bool var_is_global = _wp_args->is_global;
    wp::array_t<wp::int64> adj_env_ids = _wp_adj_args->env_ids;
    wp::array_t<wp::int64> adj_body_ids = _wp_adj_args->body_ids;
    wp::array_t<wp::vec_t<3, wp::float32>> adj_forces = _wp_adj_args->forces;
    wp::array_t<wp::vec_t<3, wp::float32>> adj_torques = _wp_adj_args->torques;
    wp::array_t<wp::vec_t<3, wp::float32>> adj_positions = _wp_adj_args->positions;
    wp::array_t<wp::vec_t<3, wp::float32>> adj_global_force_w = _wp_adj_args->global_force_w;
    wp::array_t<wp::vec_t<3, wp::float32>> adj_global_torque_w = _wp_adj_args->global_torque_w;
    wp::array_t<wp::vec_t<3, wp::float32>> adj_global_force_at_com_w = _wp_adj_args->global_force_at_com_w;
    wp::array_t<wp::vec_t<3, wp::float32>> adj_local_force_b = _wp_adj_args->local_force_b;
    wp::array_t<wp::vec_t<3, wp::float32>> adj_local_torque_b = _wp_adj_args->local_torque_b;
    bool adj_is_global = _wp_adj_args->is_global;
    //---------
    // primal vars
    wp::int32 var_0;
    wp::int32 var_1;
    wp::int64* var_2;
    wp::int32 var_3;
    wp::int64 var_4;
    wp::int64* var_5;
    wp::int32 var_6;
    wp::int64 var_7;
    wp::vec_t<3, wp::float32>* var_8;
    wp::vec_t<3, wp::float32>* var_9;
    wp::vec_t<3, wp::float32> var_10;
    wp::vec_t<3, wp::float32> var_11;
    wp::vec_t<3, wp::float32> var_12;
    wp::vec_t<3, wp::float32>* var_13;
    wp::vec_t<3, wp::float32>* var_14;
    wp::vec_t<3, wp::float32>* var_15;
    wp::vec_t<3, wp::float32> var_16;
    wp::vec_t<3, wp::float32> var_17;
    wp::vec_t<3, wp::float32> var_18;
    wp::vec_t<3, wp::float32> var_19;
    wp::vec_t<3, wp::float32> var_20;
    wp::vec_t<3, wp::float32>* var_21;
    wp::vec_t<3, wp::float32>* var_22;
    wp::vec_t<3, wp::float32> var_23;
    wp::vec_t<3, wp::float32> var_24;
    wp::vec_t<3, wp::float32> var_25;
    wp::vec_t<3, wp::float32>* var_26;
    wp::vec_t<3, wp::float32>* var_27;
    wp::vec_t<3, wp::float32> var_28;
    wp::vec_t<3, wp::float32> var_29;
    wp::vec_t<3, wp::float32> var_30;
    wp::vec_t<3, wp::float32>* var_31;
    wp::vec_t<3, wp::float32>* var_32;
    wp::vec_t<3, wp::float32> var_33;
    wp::vec_t<3, wp::float32> var_34;
    wp::vec_t<3, wp::float32> var_35;
    wp::vec_t<3, wp::float32>* var_36;
    wp::vec_t<3, wp::float32>* var_37;
    wp::vec_t<3, wp::float32>* var_38;
    wp::vec_t<3, wp::float32> var_39;
    wp::vec_t<3, wp::float32> var_40;
    wp::vec_t<3, wp::float32> var_41;
    wp::vec_t<3, wp::float32> var_42;
    wp::vec_t<3, wp::float32> var_43;
    wp::vec_t<3, wp::float32>* var_44;
    wp::vec_t<3, wp::float32>* var_45;
    wp::vec_t<3, wp::float32> var_46;
    wp::vec_t<3, wp::float32> var_47;
    wp::vec_t<3, wp::float32> var_48;
    //---------
    // dual vars
    wp::int32 adj_0 = {};
    wp::int32 adj_1 = {};
    wp::int64 adj_2 = {};
    wp::int32 adj_3 = {};
    wp::int64 adj_4 = {};
    wp::int64 adj_5 = {};
    wp::int32 adj_6 = {};
    wp::int64 adj_7 = {};
    wp::vec_t<3, wp::float32> adj_8 = {};
    wp::vec_t<3, wp::float32> adj_9 = {};
    wp::vec_t<3, wp::float32> adj_10 = {};
    wp::vec_t<3, wp::float32> adj_11 = {};
    wp::vec_t<3, wp::float32> adj_12 = {};
    wp::vec_t<3, wp::float32> adj_13 = {};
    wp::vec_t<3, wp::float32> adj_14 = {};
    wp::vec_t<3, wp::float32> adj_15 = {};
    wp::vec_t<3, wp::float32> adj_16 = {};
    wp::vec_t<3, wp::float32> adj_17 = {};
    wp::vec_t<3, wp::float32> adj_18 = {};
    wp::vec_t<3, wp::float32> adj_19 = {};
    wp::vec_t<3, wp::float32> adj_20 = {};
    wp::vec_t<3, wp::float32> adj_21 = {};
    wp::vec_t<3, wp::float32> adj_22 = {};
    wp::vec_t<3, wp::float32> adj_23 = {};
    wp::vec_t<3, wp::float32> adj_24 = {};
    wp::vec_t<3, wp::float32> adj_25 = {};
    wp::vec_t<3, wp::float32> adj_26 = {};
    wp::vec_t<3, wp::float32> adj_27 = {};
    wp::vec_t<3, wp::float32> adj_28 = {};
    wp::vec_t<3, wp::float32> adj_29 = {};
    wp::vec_t<3, wp::float32> adj_30 = {};
    wp::vec_t<3, wp::float32> adj_31 = {};
    wp::vec_t<3, wp::float32> adj_32 = {};
    wp::vec_t<3, wp::float32> adj_33 = {};
    wp::vec_t<3, wp::float32> adj_34 = {};
    wp::vec_t<3, wp::float32> adj_35 = {};
    wp::vec_t<3, wp::float32> adj_36 = {};
    wp::vec_t<3, wp::float32> adj_37 = {};
    wp::vec_t<3, wp::float32> adj_38 = {};
    wp::vec_t<3, wp::float32> adj_39 = {};
    wp::vec_t<3, wp::float32> adj_40 = {};
    wp::vec_t<3, wp::float32> adj_41 = {};
    wp::vec_t<3, wp::float32> adj_42 = {};
    wp::vec_t<3, wp::float32> adj_43 = {};
    wp::vec_t<3, wp::float32> adj_44 = {};
    wp::vec_t<3, wp::float32> adj_45 = {};
    wp::vec_t<3, wp::float32> adj_46 = {};
    wp::vec_t<3, wp::float32> adj_47 = {};
    wp::vec_t<3, wp::float32> adj_48 = {};
    //---------
    // forward
    // def add_forces_to_dual_buffers_index(                                                  <L 1>
    // tid_env, tid_body = wp.tid()                                                           <L 19>
    builtin_tid2d(var_0, var_1);
    // ei = wp.int32(env_ids[tid_env])                                                        <L 20>
    var_2 = wp::address(var_env_ids, var_0);
    var_4 = wp::load(var_2);
    var_3 = wp::int32(var_4);
    // bi = wp.int32(body_ids[tid_body])                                                      <L 21>
    var_5 = wp::address(var_body_ids, var_1);
    var_7 = wp::load(var_5);
    var_6 = wp::int32(var_7);
    // if is_global:                                                                          <L 23>
    if (var_is_global) {
        // if forces:                                                                         <L 24>
        if (var_forces) {
            // if positions:                                                                  <L 25>
            if (var_positions) {
                // global_force_w[ei, bi] = global_force_w[ei, bi] + forces[tid_env, tid_body]       <L 26>
                var_8 = wp::address(var_global_force_w, var_3, var_6);
                var_9 = wp::address(var_forces, var_0, var_1);
                var_11 = wp::load(var_8);
                var_12 = wp::load(var_9);
                var_10 = wp::add(var_11, var_12);
                // wp::array_store(var_global_force_w, var_3, var_6, var_10);
                // global_torque_w[ei, bi] = global_torque_w[ei, bi] + wp.cross(              <L 27>
                var_13 = wp::address(var_global_torque_w, var_3, var_6);
                // positions[tid_env, tid_body], forces[tid_env, tid_body]                    <L 28>
                var_14 = wp::address(var_positions, var_0, var_1);
                var_15 = wp::address(var_forces, var_0, var_1);
                var_17 = wp::load(var_14);
                var_18 = wp::load(var_15);
                var_16 = wp::cross(var_17, var_18);
                var_20 = wp::load(var_13);
                var_19 = wp::add(var_20, var_16);
                // global_torque_w[ei, bi] = global_torque_w[ei, bi] + wp.cross(              <L 27>
                // wp::array_store(var_global_torque_w, var_3, var_6, var_19);
            }
            if (!var_positions) {
                // global_force_at_com_w[ei, bi] = global_force_at_com_w[ei, bi] + forces[tid_env, tid_body]       <L 31>
                var_21 = wp::address(var_global_force_at_com_w, var_3, var_6);
                var_22 = wp::address(var_forces, var_0, var_1);
                var_24 = wp::load(var_21);
                var_25 = wp::load(var_22);
                var_23 = wp::add(var_24, var_25);
                // wp::array_store(var_global_force_at_com_w, var_3, var_6, var_23);
            }
        }
        // if torques:                                                                        <L 32>
        if (var_torques) {
            // global_torque_w[ei, bi] = global_torque_w[ei, bi] + torques[tid_env, tid_body]       <L 33>
            var_26 = wp::address(var_global_torque_w, var_3, var_6);
            var_27 = wp::address(var_torques, var_0, var_1);
            var_29 = wp::load(var_26);
            var_30 = wp::load(var_27);
            var_28 = wp::add(var_29, var_30);
            // wp::array_store(var_global_torque_w, var_3, var_6, var_28);
        }
    }
    if (!var_is_global) {
        // if forces:                                                                         <L 35>
        if (var_forces) {
            // local_force_b[ei, bi] = local_force_b[ei, bi] + forces[tid_env, tid_body]       <L 36>
            var_31 = wp::address(var_local_force_b, var_3, var_6);
            var_32 = wp::address(var_forces, var_0, var_1);
            var_34 = wp::load(var_31);
            var_35 = wp::load(var_32);
            var_33 = wp::add(var_34, var_35);
            // wp::array_store(var_local_force_b, var_3, var_6, var_33);
            // if positions:                                                                  <L 37>
            if (var_positions) {
                // local_torque_b[ei, bi] = local_torque_b[ei, bi] + wp.cross(                <L 38>
                var_36 = wp::address(var_local_torque_b, var_3, var_6);
                // positions[tid_env, tid_body], forces[tid_env, tid_body]                    <L 39>
                var_37 = wp::address(var_positions, var_0, var_1);
                var_38 = wp::address(var_forces, var_0, var_1);
                var_40 = wp::load(var_37);
                var_41 = wp::load(var_38);
                var_39 = wp::cross(var_40, var_41);
                var_43 = wp::load(var_36);
                var_42 = wp::add(var_43, var_39);
                // local_torque_b[ei, bi] = local_torque_b[ei, bi] + wp.cross(                <L 38>
                // wp::array_store(var_local_torque_b, var_3, var_6, var_42);
            }
        }
        // if torques:                                                                        <L 41>
        if (var_torques) {
            // local_torque_b[ei, bi] = local_torque_b[ei, bi] + torques[tid_env, tid_body]       <L 42>
            var_44 = wp::address(var_local_torque_b, var_3, var_6);
            var_45 = wp::address(var_torques, var_0, var_1);
            var_47 = wp::load(var_44);
            var_48 = wp::load(var_45);
            var_46 = wp::add(var_47, var_48);
            // wp::array_store(var_local_torque_b, var_3, var_6, var_46);
        }
    }
    //---------
    // reverse
    if (!var_is_global) {
        if (var_torques) {
            wp::adj_array_store(var_local_torque_b, var_3, var_6, var_46, adj_local_torque_b, adj_3, adj_6, adj_46);
            wp::adj_add(var_47, var_48, adj_44, adj_45, adj_46);
            wp::adj_address(var_torques, var_0, var_1, adj_torques, adj_0, adj_1, adj_45);
            wp::adj_address(var_local_torque_b, var_3, var_6, adj_local_torque_b, adj_3, adj_6, adj_44);
            // adj: local_torque_b[ei, bi] = local_torque_b[ei, bi] + torques[tid_env, tid_body]  <L 42>
        }
        // adj: if torques:                                                                   <L 41>
        if (var_forces) {
            if (var_positions) {
                wp::adj_array_store(var_local_torque_b, var_3, var_6, var_42, adj_local_torque_b, adj_3, adj_6, adj_42);
                // adj: local_torque_b[ei, bi] = local_torque_b[ei, bi] + wp.cross(           <L 38>
                wp::adj_add(var_43, var_39, adj_36, adj_39, adj_42);
                wp::adj_cross(var_40, var_41, adj_37, adj_38, adj_39);
                wp::adj_address(var_forces, var_0, var_1, adj_forces, adj_0, adj_1, adj_38);
                wp::adj_address(var_positions, var_0, var_1, adj_positions, adj_0, adj_1, adj_37);
                // adj: positions[tid_env, tid_body], forces[tid_env, tid_body]               <L 39>
                wp::adj_address(var_local_torque_b, var_3, var_6, adj_local_torque_b, adj_3, adj_6, adj_36);
                // adj: local_torque_b[ei, bi] = local_torque_b[ei, bi] + wp.cross(           <L 38>
            }
            // adj: if positions:                                                             <L 37>
            wp::adj_array_store(var_local_force_b, var_3, var_6, var_33, adj_local_force_b, adj_3, adj_6, adj_33);
            wp::adj_add(var_34, var_35, adj_31, adj_32, adj_33);
            wp::adj_address(var_forces, var_0, var_1, adj_forces, adj_0, adj_1, adj_32);
            wp::adj_address(var_local_force_b, var_3, var_6, adj_local_force_b, adj_3, adj_6, adj_31);
            // adj: local_force_b[ei, bi] = local_force_b[ei, bi] + forces[tid_env, tid_body]  <L 36>
        }
        // adj: if forces:                                                                    <L 35>
    }
    if (var_is_global) {
        if (var_torques) {
            wp::adj_array_store(var_global_torque_w, var_3, var_6, var_28, adj_global_torque_w, adj_3, adj_6, adj_28);
            wp::adj_add(var_29, var_30, adj_26, adj_27, adj_28);
            wp::adj_address(var_torques, var_0, var_1, adj_torques, adj_0, adj_1, adj_27);
            wp::adj_address(var_global_torque_w, var_3, var_6, adj_global_torque_w, adj_3, adj_6, adj_26);
            // adj: global_torque_w[ei, bi] = global_torque_w[ei, bi] + torques[tid_env, tid_body]  <L 33>
        }
        // adj: if torques:                                                                   <L 32>
        if (var_forces) {
            if (!var_positions) {
                wp::adj_array_store(var_global_force_at_com_w, var_3, var_6, var_23, adj_global_force_at_com_w, adj_3, adj_6, adj_23);
                wp::adj_add(var_24, var_25, adj_21, adj_22, adj_23);
                wp::adj_address(var_forces, var_0, var_1, adj_forces, adj_0, adj_1, adj_22);
                wp::adj_address(var_global_force_at_com_w, var_3, var_6, adj_global_force_at_com_w, adj_3, adj_6, adj_21);
                // adj: global_force_at_com_w[ei, bi] = global_force_at_com_w[ei, bi] + forces[tid_env, tid_body]  <L 31>
            }
            if (var_positions) {
                wp::adj_array_store(var_global_torque_w, var_3, var_6, var_19, adj_global_torque_w, adj_3, adj_6, adj_19);
                // adj: global_torque_w[ei, bi] = global_torque_w[ei, bi] + wp.cross(         <L 27>
                wp::adj_add(var_20, var_16, adj_13, adj_16, adj_19);
                wp::adj_cross(var_17, var_18, adj_14, adj_15, adj_16);
                wp::adj_address(var_forces, var_0, var_1, adj_forces, adj_0, adj_1, adj_15);
                wp::adj_address(var_positions, var_0, var_1, adj_positions, adj_0, adj_1, adj_14);
                // adj: positions[tid_env, tid_body], forces[tid_env, tid_body]               <L 28>
                wp::adj_address(var_global_torque_w, var_3, var_6, adj_global_torque_w, adj_3, adj_6, adj_13);
                // adj: global_torque_w[ei, bi] = global_torque_w[ei, bi] + wp.cross(         <L 27>
                wp::adj_array_store(var_global_force_w, var_3, var_6, var_10, adj_global_force_w, adj_3, adj_6, adj_10);
                wp::adj_add(var_11, var_12, adj_8, adj_9, adj_10);
                wp::adj_address(var_forces, var_0, var_1, adj_forces, adj_0, adj_1, adj_9);
                wp::adj_address(var_global_force_w, var_3, var_6, adj_global_force_w, adj_3, adj_6, adj_8);
                // adj: global_force_w[ei, bi] = global_force_w[ei, bi] + forces[tid_env, tid_body]  <L 26>
            }
            // adj: if positions:                                                             <L 25>
        }
        // adj: if forces:                                                                    <L 24>
    }
    // adj: if is_global:                                                                     <L 23>
    wp::adj_address(var_body_ids, var_1, adj_body_ids, adj_1, adj_5);
    // adj: bi = wp.int32(body_ids[tid_body])                                                 <L 21>
    wp::adj_address(var_env_ids, var_0, adj_env_ids, adj_0, adj_2);
    // adj: ei = wp.int32(env_ids[tid_env])                                                   <L 20>
    // adj: tid_env, tid_body = wp.tid()                                                      <L 19>
    // adj: def add_forces_to_dual_buffers_index(                                             <L 1>
    return;
}



extern "C" {

// Python CPU entry points
WP_API void add_forces_to_dual_buffers_index_a340e469_cpu_forward(
    wp::launch_bounds_t<2> *dim,
    wp_args_add_forces_to_dual_buffers_index_a340e469 *_wp_args)
{
    wp::tile_shared_storage_t tile_mem;
#if defined(WP_ENABLE_TILES_IN_STACK_MEMORY)
    wp::shared_tile_storage = &tile_mem;
#endif

    for (size_t task_index = 0; task_index < dim->size; ++task_index)
    {
        add_forces_to_dual_buffers_index_a340e469_cpu_kernel_forward(*dim, task_index, _wp_args);
    }
}

} // extern C



extern "C" {

WP_API void add_forces_to_dual_buffers_index_a340e469_cpu_backward(
    wp::launch_bounds_t<2> *dim,
    wp_args_add_forces_to_dual_buffers_index_a340e469 *_wp_args,
    wp_args_add_forces_to_dual_buffers_index_a340e469 *_wp_adj_args)
{
    wp::tile_shared_storage_t tile_mem;
#if defined(WP_ENABLE_TILES_IN_STACK_MEMORY)
    wp::shared_tile_storage = &tile_mem;
#endif

    for (size_t task_index = 0; task_index < dim->size; ++task_index)
    {
        add_forces_to_dual_buffers_index_a340e469_cpu_kernel_backward(*dim, task_index, _wp_args, _wp_adj_args);
    }
}

} // extern C

struct wp_args_spatial_sum_uint8_tiled_a95be22f {
    wp::array_t<wp::uint8> src;
    wp::array_t<wp::int32> partials;
    wp::int32 tile_size;
    wp::int32 channel_dim;
};


void spatial_sum_uint8_tiled_a95be22f_cpu_kernel_forward(
    wp::launch_bounds_t<3> dim,
    size_t task_index,
    wp_args_spatial_sum_uint8_tiled_a95be22f *_wp_args)
{
    //---------
    // argument vars
    wp::array_t<wp::uint8> var_src = _wp_args->src;
    wp::array_t<wp::int32> var_partials = _wp_args->partials;
    wp::int32 var_tile_size = _wp_args->tile_size;
    wp::int32 var_channel_dim = _wp_args->channel_dim;
    //---------
    // primal vars
    wp::int32 var_0;
    wp::int32 var_1;
    wp::int32 var_2;
    wp::int32 var_3;
    const wp::int32 var_4 = 0;
    wp::int32 var_5;
    const wp::int32 var_6 = 1;
    bool var_7;
    wp::int32 var_8;
    wp::shape_t* var_9;
    const wp::int32 var_10 = 2;
    wp::int32 var_11;
    wp::shape_t var_12;
    wp::int32 var_13;
    wp::range_t var_14;
    wp::int32 var_15;
    wp::shape_t* var_16;
    const wp::int32 var_17 = 3;
    wp::int32 var_18;
    wp::shape_t var_19;
    wp::range_t var_20;
    wp::int32 var_21;
    wp::uint8* var_22;
    wp::int32 var_23;
    wp::uint8 var_24;
    wp::int32 var_25;
    wp::int32 var_26;
    wp::shape_t* var_27;
    const wp::int32 var_28 = 1;
    wp::int32 var_29;
    wp::shape_t var_30;
    wp::int32 var_31;
    wp::range_t var_32;
    wp::int32 var_33;
    wp::shape_t* var_34;
    const wp::int32 var_35 = 2;
    wp::int32 var_36;
    wp::shape_t var_37;
    wp::range_t var_38;
    wp::int32 var_39;
    wp::uint8* var_40;
    wp::int32 var_41;
    wp::uint8 var_42;
    wp::int32 var_43;
    wp::int32 var_44;
    wp::int32 var_45;
    wp::int32 var_46;
    //---------
    // forward
    // def spatial_sum_uint8_tiled(                                                           <L 754>
    // b, tile, c = wp.tid()                                                                  <L 774>
    builtin_tid3d(var_0, var_1, var_2);
    // h_start = tile * tile_size                                                             <L 775>
    var_3 = wp::mul(var_1, var_tile_size);
    // s = wp.int32(0)                                                                        <L 776>
    var_5 = wp::int32(var_4);
    // if channel_dim == 1:                                                                   <L 777>
    var_7 = (var_channel_dim == var_6);
    if (var_7) {
        // h_end = wp.min(h_start + tile_size, src.shape[2])                                  <L 779>
        var_8 = wp::add(var_3, var_tile_size);
        var_9 = &(var_src.shape);
        var_12 = wp::load(var_9);
        var_11 = wp::extract(var_12, var_10);
        var_13 = wp::min(var_8, var_11);
        // for i in range(h_start, h_end):                                                    <L 780>
        var_14 = wp::range(var_3, var_13);
        start_for_0:;
            if (iter_cmp(var_14) == 0) goto end_for_0;
            var_15 = wp::iter_next(var_14);
            // for j in range(src.shape[3]):                                                  <L 781>
            var_16 = &(var_src.shape);
            var_19 = wp::load(var_16);
            var_18 = wp::extract(var_19, var_17);
            var_20 = wp::range(var_18);
            start_for_2:;
                if (iter_cmp(var_20) == 0) goto end_for_2;
                var_21 = wp::iter_next(var_20);
                // s += wp.int32(src[b, c, i, j])                                             <L 782>
                var_22 = wp::address(var_src, var_0, var_2, var_15, var_21);
                var_24 = wp::load(var_22);
                var_23 = wp::int32(var_24);
                var_25 = wp::add(var_5, var_23);
                wp::assign(var_5, var_25);
                goto start_for_2;
            end_for_2:;
            goto start_for_0;
        end_for_0:;
    }
    if (!var_7) {
        // h_end = wp.min(h_start + tile_size, src.shape[1])                                  <L 785>
        var_26 = wp::add(var_3, var_tile_size);
        var_27 = &(var_src.shape);
        var_30 = wp::load(var_27);
        var_29 = wp::extract(var_30, var_28);
        var_31 = wp::min(var_26, var_29);
        // for i in range(h_start, h_end):                                                    <L 786>
        var_32 = wp::range(var_3, var_31);
        start_for_4:;
            if (iter_cmp(var_32) == 0) goto end_for_4;
            var_33 = wp::iter_next(var_32);
            // for j in range(src.shape[2]):                                                  <L 787>
            var_34 = &(var_src.shape);
            var_37 = wp::load(var_34);
            var_36 = wp::extract(var_37, var_35);
            var_38 = wp::range(var_36);
            start_for_6:;
                if (iter_cmp(var_38) == 0) goto end_for_6;
                var_39 = wp::iter_next(var_38);
                // s += wp.int32(src[b, i, j, c])                                             <L 788>
                var_40 = wp::address(var_src, var_0, var_33, var_39, var_2);
                var_42 = wp::load(var_40);
                var_41 = wp::int32(var_42);
                var_43 = wp::add(var_5, var_41);
                wp::assign(var_5, var_43);
                goto start_for_6;
            end_for_6:;
            goto start_for_4;
        end_for_4:;
    }
    var_44 = wp::where(var_7, var_13, var_31);
    var_45 = wp::where(var_7, var_15, var_33);
    var_46 = wp::where(var_7, var_21, var_39);
    // partials[b, tile, c] = s                                                               <L 789>
    wp::array_store(var_partials, var_0, var_1, var_2, var_5);
}



extern "C" {

// Python CPU entry points
WP_API void spatial_sum_uint8_tiled_a95be22f_cpu_forward(
    wp::launch_bounds_t<3> *dim,
    wp_args_spatial_sum_uint8_tiled_a95be22f *_wp_args)
{
    wp::tile_shared_storage_t tile_mem;
#if defined(WP_ENABLE_TILES_IN_STACK_MEMORY)
    wp::shared_tile_storage = &tile_mem;
#endif

    for (size_t task_index = 0; task_index < dim->size; ++task_index)
    {
        spatial_sum_uint8_tiled_a95be22f_cpu_kernel_forward(*dim, task_index, _wp_args);
    }
}

} // extern C

struct wp_args_add_forces_to_dual_buffers_index_ba5a2f71 {
    wp::array_t<wp::int32> env_ids;
    wp::array_t<wp::int64> body_ids;
    wp::array_t<wp::vec_t<3, wp::float32>> forces;
    wp::array_t<wp::vec_t<3, wp::float32>> torques;
    wp::array_t<wp::vec_t<3, wp::float32>> positions;
    wp::array_t<wp::vec_t<3, wp::float32>> global_force_w;
    wp::array_t<wp::vec_t<3, wp::float32>> global_torque_w;
    wp::array_t<wp::vec_t<3, wp::float32>> global_force_at_com_w;
    wp::array_t<wp::vec_t<3, wp::float32>> local_force_b;
    wp::array_t<wp::vec_t<3, wp::float32>> local_torque_b;
    bool is_global;
};


void add_forces_to_dual_buffers_index_ba5a2f71_cpu_kernel_forward(
    wp::launch_bounds_t<2> dim,
    size_t task_index,
    wp_args_add_forces_to_dual_buffers_index_ba5a2f71 *_wp_args)
{
    //---------
    // argument vars
    wp::array_t<wp::int32> var_env_ids = _wp_args->env_ids;
    wp::array_t<wp::int64> var_body_ids = _wp_args->body_ids;
    wp::array_t<wp::vec_t<3, wp::float32>> var_forces = _wp_args->forces;
    wp::array_t<wp::vec_t<3, wp::float32>> var_torques = _wp_args->torques;
    wp::array_t<wp::vec_t<3, wp::float32>> var_positions = _wp_args->positions;
    wp::array_t<wp::vec_t<3, wp::float32>> var_global_force_w = _wp_args->global_force_w;
    wp::array_t<wp::vec_t<3, wp::float32>> var_global_torque_w = _wp_args->global_torque_w;
    wp::array_t<wp::vec_t<3, wp::float32>> var_global_force_at_com_w = _wp_args->global_force_at_com_w;
    wp::array_t<wp::vec_t<3, wp::float32>> var_local_force_b = _wp_args->local_force_b;
    wp::array_t<wp::vec_t<3, wp::float32>> var_local_torque_b = _wp_args->local_torque_b;
    bool var_is_global = _wp_args->is_global;
    //---------
    // primal vars
    wp::int32 var_0;
    wp::int32 var_1;
    wp::int32* var_2;
    wp::int32 var_3;
    wp::int32 var_4;
    wp::int64* var_5;
    wp::int32 var_6;
    wp::int64 var_7;
    wp::vec_t<3, wp::float32>* var_8;
    wp::vec_t<3, wp::float32>* var_9;
    wp::vec_t<3, wp::float32> var_10;
    wp::vec_t<3, wp::float32> var_11;
    wp::vec_t<3, wp::float32> var_12;
    wp::vec_t<3, wp::float32>* var_13;
    wp::vec_t<3, wp::float32>* var_14;
    wp::vec_t<3, wp::float32>* var_15;
    wp::vec_t<3, wp::float32> var_16;
    wp::vec_t<3, wp::float32> var_17;
    wp::vec_t<3, wp::float32> var_18;
    wp::vec_t<3, wp::float32> var_19;
    wp::vec_t<3, wp::float32> var_20;
    wp::vec_t<3, wp::float32>* var_21;
    wp::vec_t<3, wp::float32>* var_22;
    wp::vec_t<3, wp::float32> var_23;
    wp::vec_t<3, wp::float32> var_24;
    wp::vec_t<3, wp::float32> var_25;
    wp::vec_t<3, wp::float32>* var_26;
    wp::vec_t<3, wp::float32>* var_27;
    wp::vec_t<3, wp::float32> var_28;
    wp::vec_t<3, wp::float32> var_29;
    wp::vec_t<3, wp::float32> var_30;
    wp::vec_t<3, wp::float32>* var_31;
    wp::vec_t<3, wp::float32>* var_32;
    wp::vec_t<3, wp::float32> var_33;
    wp::vec_t<3, wp::float32> var_34;
    wp::vec_t<3, wp::float32> var_35;
    wp::vec_t<3, wp::float32>* var_36;
    wp::vec_t<3, wp::float32>* var_37;
    wp::vec_t<3, wp::float32>* var_38;
    wp::vec_t<3, wp::float32> var_39;
    wp::vec_t<3, wp::float32> var_40;
    wp::vec_t<3, wp::float32> var_41;
    wp::vec_t<3, wp::float32> var_42;
    wp::vec_t<3, wp::float32> var_43;
    wp::vec_t<3, wp::float32>* var_44;
    wp::vec_t<3, wp::float32>* var_45;
    wp::vec_t<3, wp::float32> var_46;
    wp::vec_t<3, wp::float32> var_47;
    wp::vec_t<3, wp::float32> var_48;
    //---------
    // forward
    // def add_forces_to_dual_buffers_index(                                                  <L 1>
    // tid_env, tid_body = wp.tid()                                                           <L 19>
    builtin_tid2d(var_0, var_1);
    // ei = wp.int32(env_ids[tid_env])                                                        <L 20>
    var_2 = wp::address(var_env_ids, var_0);
    var_4 = wp::load(var_2);
    var_3 = wp::int32(var_4);
    // bi = wp.int32(body_ids[tid_body])                                                      <L 21>
    var_5 = wp::address(var_body_ids, var_1);
    var_7 = wp::load(var_5);
    var_6 = wp::int32(var_7);
    // if is_global:                                                                          <L 23>
    if (var_is_global) {
        // if forces:                                                                         <L 24>
        if (var_forces) {
            // if positions:                                                                  <L 25>
            if (var_positions) {
                // global_force_w[ei, bi] = global_force_w[ei, bi] + forces[tid_env, tid_body]       <L 26>
                var_8 = wp::address(var_global_force_w, var_3, var_6);
                var_9 = wp::address(var_forces, var_0, var_1);
                var_11 = wp::load(var_8);
                var_12 = wp::load(var_9);
                var_10 = wp::add(var_11, var_12);
                wp::array_store(var_global_force_w, var_3, var_6, var_10);
                // global_torque_w[ei, bi] = global_torque_w[ei, bi] + wp.cross(              <L 27>
                var_13 = wp::address(var_global_torque_w, var_3, var_6);
                // positions[tid_env, tid_body], forces[tid_env, tid_body]                    <L 28>
                var_14 = wp::address(var_positions, var_0, var_1);
                var_15 = wp::address(var_forces, var_0, var_1);
                var_17 = wp::load(var_14);
                var_18 = wp::load(var_15);
                var_16 = wp::cross(var_17, var_18);
                var_20 = wp::load(var_13);
                var_19 = wp::add(var_20, var_16);
                // global_torque_w[ei, bi] = global_torque_w[ei, bi] + wp.cross(              <L 27>
                wp::array_store(var_global_torque_w, var_3, var_6, var_19);
            }
            if (!var_positions) {
                // global_force_at_com_w[ei, bi] = global_force_at_com_w[ei, bi] + forces[tid_env, tid_body]       <L 31>
                var_21 = wp::address(var_global_force_at_com_w, var_3, var_6);
                var_22 = wp::address(var_forces, var_0, var_1);
                var_24 = wp::load(var_21);
                var_25 = wp::load(var_22);
                var_23 = wp::add(var_24, var_25);
                wp::array_store(var_global_force_at_com_w, var_3, var_6, var_23);
            }
        }
        // if torques:                                                                        <L 32>
        if (var_torques) {
            // global_torque_w[ei, bi] = global_torque_w[ei, bi] + torques[tid_env, tid_body]       <L 33>
            var_26 = wp::address(var_global_torque_w, var_3, var_6);
            var_27 = wp::address(var_torques, var_0, var_1);
            var_29 = wp::load(var_26);
            var_30 = wp::load(var_27);
            var_28 = wp::add(var_29, var_30);
            wp::array_store(var_global_torque_w, var_3, var_6, var_28);
        }
    }
    if (!var_is_global) {
        // if forces:                                                                         <L 35>
        if (var_forces) {
            // local_force_b[ei, bi] = local_force_b[ei, bi] + forces[tid_env, tid_body]       <L 36>
            var_31 = wp::address(var_local_force_b, var_3, var_6);
            var_32 = wp::address(var_forces, var_0, var_1);
            var_34 = wp::load(var_31);
            var_35 = wp::load(var_32);
            var_33 = wp::add(var_34, var_35);
            wp::array_store(var_local_force_b, var_3, var_6, var_33);
            // if positions:                                                                  <L 37>
            if (var_positions) {
                // local_torque_b[ei, bi] = local_torque_b[ei, bi] + wp.cross(                <L 38>
                var_36 = wp::address(var_local_torque_b, var_3, var_6);
                // positions[tid_env, tid_body], forces[tid_env, tid_body]                    <L 39>
                var_37 = wp::address(var_positions, var_0, var_1);
                var_38 = wp::address(var_forces, var_0, var_1);
                var_40 = wp::load(var_37);
                var_41 = wp::load(var_38);
                var_39 = wp::cross(var_40, var_41);
                var_43 = wp::load(var_36);
                var_42 = wp::add(var_43, var_39);
                // local_torque_b[ei, bi] = local_torque_b[ei, bi] + wp.cross(                <L 38>
                wp::array_store(var_local_torque_b, var_3, var_6, var_42);
            }
        }
        // if torques:                                                                        <L 41>
        if (var_torques) {
            // local_torque_b[ei, bi] = local_torque_b[ei, bi] + torques[tid_env, tid_body]       <L 42>
            var_44 = wp::address(var_local_torque_b, var_3, var_6);
            var_45 = wp::address(var_torques, var_0, var_1);
            var_47 = wp::load(var_44);
            var_48 = wp::load(var_45);
            var_46 = wp::add(var_47, var_48);
            wp::array_store(var_local_torque_b, var_3, var_6, var_46);
        }
    }
}



void add_forces_to_dual_buffers_index_ba5a2f71_cpu_kernel_backward(
    wp::launch_bounds_t<2> dim,
    size_t task_index,
    wp_args_add_forces_to_dual_buffers_index_ba5a2f71 *_wp_args,
    wp_args_add_forces_to_dual_buffers_index_ba5a2f71 *_wp_adj_args)
{
    //---------
    // argument vars
    wp::array_t<wp::int32> var_env_ids = _wp_args->env_ids;
    wp::array_t<wp::int64> var_body_ids = _wp_args->body_ids;
    wp::array_t<wp::vec_t<3, wp::float32>> var_forces = _wp_args->forces;
    wp::array_t<wp::vec_t<3, wp::float32>> var_torques = _wp_args->torques;
    wp::array_t<wp::vec_t<3, wp::float32>> var_positions = _wp_args->positions;
    wp::array_t<wp::vec_t<3, wp::float32>> var_global_force_w = _wp_args->global_force_w;
    wp::array_t<wp::vec_t<3, wp::float32>> var_global_torque_w = _wp_args->global_torque_w;
    wp::array_t<wp::vec_t<3, wp::float32>> var_global_force_at_com_w = _wp_args->global_force_at_com_w;
    wp::array_t<wp::vec_t<3, wp::float32>> var_local_force_b = _wp_args->local_force_b;
    wp::array_t<wp::vec_t<3, wp::float32>> var_local_torque_b = _wp_args->local_torque_b;
    bool var_is_global = _wp_args->is_global;
    wp::array_t<wp::int32> adj_env_ids = _wp_adj_args->env_ids;
    wp::array_t<wp::int64> adj_body_ids = _wp_adj_args->body_ids;
    wp::array_t<wp::vec_t<3, wp::float32>> adj_forces = _wp_adj_args->forces;
    wp::array_t<wp::vec_t<3, wp::float32>> adj_torques = _wp_adj_args->torques;
    wp::array_t<wp::vec_t<3, wp::float32>> adj_positions = _wp_adj_args->positions;
    wp::array_t<wp::vec_t<3, wp::float32>> adj_global_force_w = _wp_adj_args->global_force_w;
    wp::array_t<wp::vec_t<3, wp::float32>> adj_global_torque_w = _wp_adj_args->global_torque_w;
    wp::array_t<wp::vec_t<3, wp::float32>> adj_global_force_at_com_w = _wp_adj_args->global_force_at_com_w;
    wp::array_t<wp::vec_t<3, wp::float32>> adj_local_force_b = _wp_adj_args->local_force_b;
    wp::array_t<wp::vec_t<3, wp::float32>> adj_local_torque_b = _wp_adj_args->local_torque_b;
    bool adj_is_global = _wp_adj_args->is_global;
    //---------
    // primal vars
    wp::int32 var_0;
    wp::int32 var_1;
    wp::int32* var_2;
    wp::int32 var_3;
    wp::int32 var_4;
    wp::int64* var_5;
    wp::int32 var_6;
    wp::int64 var_7;
    wp::vec_t<3, wp::float32>* var_8;
    wp::vec_t<3, wp::float32>* var_9;
    wp::vec_t<3, wp::float32> var_10;
    wp::vec_t<3, wp::float32> var_11;
    wp::vec_t<3, wp::float32> var_12;
    wp::vec_t<3, wp::float32>* var_13;
    wp::vec_t<3, wp::float32>* var_14;
    wp::vec_t<3, wp::float32>* var_15;
    wp::vec_t<3, wp::float32> var_16;
    wp::vec_t<3, wp::float32> var_17;
    wp::vec_t<3, wp::float32> var_18;
    wp::vec_t<3, wp::float32> var_19;
    wp::vec_t<3, wp::float32> var_20;
    wp::vec_t<3, wp::float32>* var_21;
    wp::vec_t<3, wp::float32>* var_22;
    wp::vec_t<3, wp::float32> var_23;
    wp::vec_t<3, wp::float32> var_24;
    wp::vec_t<3, wp::float32> var_25;
    wp::vec_t<3, wp::float32>* var_26;
    wp::vec_t<3, wp::float32>* var_27;
    wp::vec_t<3, wp::float32> var_28;
    wp::vec_t<3, wp::float32> var_29;
    wp::vec_t<3, wp::float32> var_30;
    wp::vec_t<3, wp::float32>* var_31;
    wp::vec_t<3, wp::float32>* var_32;
    wp::vec_t<3, wp::float32> var_33;
    wp::vec_t<3, wp::float32> var_34;
    wp::vec_t<3, wp::float32> var_35;
    wp::vec_t<3, wp::float32>* var_36;
    wp::vec_t<3, wp::float32>* var_37;
    wp::vec_t<3, wp::float32>* var_38;
    wp::vec_t<3, wp::float32> var_39;
    wp::vec_t<3, wp::float32> var_40;
    wp::vec_t<3, wp::float32> var_41;
    wp::vec_t<3, wp::float32> var_42;
    wp::vec_t<3, wp::float32> var_43;
    wp::vec_t<3, wp::float32>* var_44;
    wp::vec_t<3, wp::float32>* var_45;
    wp::vec_t<3, wp::float32> var_46;
    wp::vec_t<3, wp::float32> var_47;
    wp::vec_t<3, wp::float32> var_48;
    //---------
    // dual vars
    wp::int32 adj_0 = {};
    wp::int32 adj_1 = {};
    wp::int32 adj_2 = {};
    wp::int32 adj_3 = {};
    wp::int32 adj_4 = {};
    wp::int64 adj_5 = {};
    wp::int32 adj_6 = {};
    wp::int64 adj_7 = {};
    wp::vec_t<3, wp::float32> adj_8 = {};
    wp::vec_t<3, wp::float32> adj_9 = {};
    wp::vec_t<3, wp::float32> adj_10 = {};
    wp::vec_t<3, wp::float32> adj_11 = {};
    wp::vec_t<3, wp::float32> adj_12 = {};
    wp::vec_t<3, wp::float32> adj_13 = {};
    wp::vec_t<3, wp::float32> adj_14 = {};
    wp::vec_t<3, wp::float32> adj_15 = {};
    wp::vec_t<3, wp::float32> adj_16 = {};
    wp::vec_t<3, wp::float32> adj_17 = {};
    wp::vec_t<3, wp::float32> adj_18 = {};
    wp::vec_t<3, wp::float32> adj_19 = {};
    wp::vec_t<3, wp::float32> adj_20 = {};
    wp::vec_t<3, wp::float32> adj_21 = {};
    wp::vec_t<3, wp::float32> adj_22 = {};
    wp::vec_t<3, wp::float32> adj_23 = {};
    wp::vec_t<3, wp::float32> adj_24 = {};
    wp::vec_t<3, wp::float32> adj_25 = {};
    wp::vec_t<3, wp::float32> adj_26 = {};
    wp::vec_t<3, wp::float32> adj_27 = {};
    wp::vec_t<3, wp::float32> adj_28 = {};
    wp::vec_t<3, wp::float32> adj_29 = {};
    wp::vec_t<3, wp::float32> adj_30 = {};
    wp::vec_t<3, wp::float32> adj_31 = {};
    wp::vec_t<3, wp::float32> adj_32 = {};
    wp::vec_t<3, wp::float32> adj_33 = {};
    wp::vec_t<3, wp::float32> adj_34 = {};
    wp::vec_t<3, wp::float32> adj_35 = {};
    wp::vec_t<3, wp::float32> adj_36 = {};
    wp::vec_t<3, wp::float32> adj_37 = {};
    wp::vec_t<3, wp::float32> adj_38 = {};
    wp::vec_t<3, wp::float32> adj_39 = {};
    wp::vec_t<3, wp::float32> adj_40 = {};
    wp::vec_t<3, wp::float32> adj_41 = {};
    wp::vec_t<3, wp::float32> adj_42 = {};
    wp::vec_t<3, wp::float32> adj_43 = {};
    wp::vec_t<3, wp::float32> adj_44 = {};
    wp::vec_t<3, wp::float32> adj_45 = {};
    wp::vec_t<3, wp::float32> adj_46 = {};
    wp::vec_t<3, wp::float32> adj_47 = {};
    wp::vec_t<3, wp::float32> adj_48 = {};
    //---------
    // forward
    // def add_forces_to_dual_buffers_index(                                                  <L 1>
    // tid_env, tid_body = wp.tid()                                                           <L 19>
    builtin_tid2d(var_0, var_1);
    // ei = wp.int32(env_ids[tid_env])                                                        <L 20>
    var_2 = wp::address(var_env_ids, var_0);
    var_4 = wp::load(var_2);
    var_3 = wp::int32(var_4);
    // bi = wp.int32(body_ids[tid_body])                                                      <L 21>
    var_5 = wp::address(var_body_ids, var_1);
    var_7 = wp::load(var_5);
    var_6 = wp::int32(var_7);
    // if is_global:                                                                          <L 23>
    if (var_is_global) {
        // if forces:                                                                         <L 24>
        if (var_forces) {
            // if positions:                                                                  <L 25>
            if (var_positions) {
                // global_force_w[ei, bi] = global_force_w[ei, bi] + forces[tid_env, tid_body]       <L 26>
                var_8 = wp::address(var_global_force_w, var_3, var_6);
                var_9 = wp::address(var_forces, var_0, var_1);
                var_11 = wp::load(var_8);
                var_12 = wp::load(var_9);
                var_10 = wp::add(var_11, var_12);
                // wp::array_store(var_global_force_w, var_3, var_6, var_10);
                // global_torque_w[ei, bi] = global_torque_w[ei, bi] + wp.cross(              <L 27>
                var_13 = wp::address(var_global_torque_w, var_3, var_6);
                // positions[tid_env, tid_body], forces[tid_env, tid_body]                    <L 28>
                var_14 = wp::address(var_positions, var_0, var_1);
                var_15 = wp::address(var_forces, var_0, var_1);
                var_17 = wp::load(var_14);
                var_18 = wp::load(var_15);
                var_16 = wp::cross(var_17, var_18);
                var_20 = wp::load(var_13);
                var_19 = wp::add(var_20, var_16);
                // global_torque_w[ei, bi] = global_torque_w[ei, bi] + wp.cross(              <L 27>
                // wp::array_store(var_global_torque_w, var_3, var_6, var_19);
            }
            if (!var_positions) {
                // global_force_at_com_w[ei, bi] = global_force_at_com_w[ei, bi] + forces[tid_env, tid_body]       <L 31>
                var_21 = wp::address(var_global_force_at_com_w, var_3, var_6);
                var_22 = wp::address(var_forces, var_0, var_1);
                var_24 = wp::load(var_21);
                var_25 = wp::load(var_22);
                var_23 = wp::add(var_24, var_25);
                // wp::array_store(var_global_force_at_com_w, var_3, var_6, var_23);
            }
        }
        // if torques:                                                                        <L 32>
        if (var_torques) {
            // global_torque_w[ei, bi] = global_torque_w[ei, bi] + torques[tid_env, tid_body]       <L 33>
            var_26 = wp::address(var_global_torque_w, var_3, var_6);
            var_27 = wp::address(var_torques, var_0, var_1);
            var_29 = wp::load(var_26);
            var_30 = wp::load(var_27);
            var_28 = wp::add(var_29, var_30);
            // wp::array_store(var_global_torque_w, var_3, var_6, var_28);
        }
    }
    if (!var_is_global) {
        // if forces:                                                                         <L 35>
        if (var_forces) {
            // local_force_b[ei, bi] = local_force_b[ei, bi] + forces[tid_env, tid_body]       <L 36>
            var_31 = wp::address(var_local_force_b, var_3, var_6);
            var_32 = wp::address(var_forces, var_0, var_1);
            var_34 = wp::load(var_31);
            var_35 = wp::load(var_32);
            var_33 = wp::add(var_34, var_35);
            // wp::array_store(var_local_force_b, var_3, var_6, var_33);
            // if positions:                                                                  <L 37>
            if (var_positions) {
                // local_torque_b[ei, bi] = local_torque_b[ei, bi] + wp.cross(                <L 38>
                var_36 = wp::address(var_local_torque_b, var_3, var_6);
                // positions[tid_env, tid_body], forces[tid_env, tid_body]                    <L 39>
                var_37 = wp::address(var_positions, var_0, var_1);
                var_38 = wp::address(var_forces, var_0, var_1);
                var_40 = wp::load(var_37);
                var_41 = wp::load(var_38);
                var_39 = wp::cross(var_40, var_41);
                var_43 = wp::load(var_36);
                var_42 = wp::add(var_43, var_39);
                // local_torque_b[ei, bi] = local_torque_b[ei, bi] + wp.cross(                <L 38>
                // wp::array_store(var_local_torque_b, var_3, var_6, var_42);
            }
        }
        // if torques:                                                                        <L 41>
        if (var_torques) {
            // local_torque_b[ei, bi] = local_torque_b[ei, bi] + torques[tid_env, tid_body]       <L 42>
            var_44 = wp::address(var_local_torque_b, var_3, var_6);
            var_45 = wp::address(var_torques, var_0, var_1);
            var_47 = wp::load(var_44);
            var_48 = wp::load(var_45);
            var_46 = wp::add(var_47, var_48);
            // wp::array_store(var_local_torque_b, var_3, var_6, var_46);
        }
    }
    //---------
    // reverse
    if (!var_is_global) {
        if (var_torques) {
            wp::adj_array_store(var_local_torque_b, var_3, var_6, var_46, adj_local_torque_b, adj_3, adj_6, adj_46);
            wp::adj_add(var_47, var_48, adj_44, adj_45, adj_46);
            wp::adj_address(var_torques, var_0, var_1, adj_torques, adj_0, adj_1, adj_45);
            wp::adj_address(var_local_torque_b, var_3, var_6, adj_local_torque_b, adj_3, adj_6, adj_44);
            // adj: local_torque_b[ei, bi] = local_torque_b[ei, bi] + torques[tid_env, tid_body]  <L 42>
        }
        // adj: if torques:                                                                   <L 41>
        if (var_forces) {
            if (var_positions) {
                wp::adj_array_store(var_local_torque_b, var_3, var_6, var_42, adj_local_torque_b, adj_3, adj_6, adj_42);
                // adj: local_torque_b[ei, bi] = local_torque_b[ei, bi] + wp.cross(           <L 38>
                wp::adj_add(var_43, var_39, adj_36, adj_39, adj_42);
                wp::adj_cross(var_40, var_41, adj_37, adj_38, adj_39);
                wp::adj_address(var_forces, var_0, var_1, adj_forces, adj_0, adj_1, adj_38);
                wp::adj_address(var_positions, var_0, var_1, adj_positions, adj_0, adj_1, adj_37);
                // adj: positions[tid_env, tid_body], forces[tid_env, tid_body]               <L 39>
                wp::adj_address(var_local_torque_b, var_3, var_6, adj_local_torque_b, adj_3, adj_6, adj_36);
                // adj: local_torque_b[ei, bi] = local_torque_b[ei, bi] + wp.cross(           <L 38>
            }
            // adj: if positions:                                                             <L 37>
            wp::adj_array_store(var_local_force_b, var_3, var_6, var_33, adj_local_force_b, adj_3, adj_6, adj_33);
            wp::adj_add(var_34, var_35, adj_31, adj_32, adj_33);
            wp::adj_address(var_forces, var_0, var_1, adj_forces, adj_0, adj_1, adj_32);
            wp::adj_address(var_local_force_b, var_3, var_6, adj_local_force_b, adj_3, adj_6, adj_31);
            // adj: local_force_b[ei, bi] = local_force_b[ei, bi] + forces[tid_env, tid_body]  <L 36>
        }
        // adj: if forces:                                                                    <L 35>
    }
    if (var_is_global) {
        if (var_torques) {
            wp::adj_array_store(var_global_torque_w, var_3, var_6, var_28, adj_global_torque_w, adj_3, adj_6, adj_28);
            wp::adj_add(var_29, var_30, adj_26, adj_27, adj_28);
            wp::adj_address(var_torques, var_0, var_1, adj_torques, adj_0, adj_1, adj_27);
            wp::adj_address(var_global_torque_w, var_3, var_6, adj_global_torque_w, adj_3, adj_6, adj_26);
            // adj: global_torque_w[ei, bi] = global_torque_w[ei, bi] + torques[tid_env, tid_body]  <L 33>
        }
        // adj: if torques:                                                                   <L 32>
        if (var_forces) {
            if (!var_positions) {
                wp::adj_array_store(var_global_force_at_com_w, var_3, var_6, var_23, adj_global_force_at_com_w, adj_3, adj_6, adj_23);
                wp::adj_add(var_24, var_25, adj_21, adj_22, adj_23);
                wp::adj_address(var_forces, var_0, var_1, adj_forces, adj_0, adj_1, adj_22);
                wp::adj_address(var_global_force_at_com_w, var_3, var_6, adj_global_force_at_com_w, adj_3, adj_6, adj_21);
                // adj: global_force_at_com_w[ei, bi] = global_force_at_com_w[ei, bi] + forces[tid_env, tid_body]  <L 31>
            }
            if (var_positions) {
                wp::adj_array_store(var_global_torque_w, var_3, var_6, var_19, adj_global_torque_w, adj_3, adj_6, adj_19);
                // adj: global_torque_w[ei, bi] = global_torque_w[ei, bi] + wp.cross(         <L 27>
                wp::adj_add(var_20, var_16, adj_13, adj_16, adj_19);
                wp::adj_cross(var_17, var_18, adj_14, adj_15, adj_16);
                wp::adj_address(var_forces, var_0, var_1, adj_forces, adj_0, adj_1, adj_15);
                wp::adj_address(var_positions, var_0, var_1, adj_positions, adj_0, adj_1, adj_14);
                // adj: positions[tid_env, tid_body], forces[tid_env, tid_body]               <L 28>
                wp::adj_address(var_global_torque_w, var_3, var_6, adj_global_torque_w, adj_3, adj_6, adj_13);
                // adj: global_torque_w[ei, bi] = global_torque_w[ei, bi] + wp.cross(         <L 27>
                wp::adj_array_store(var_global_force_w, var_3, var_6, var_10, adj_global_force_w, adj_3, adj_6, adj_10);
                wp::adj_add(var_11, var_12, adj_8, adj_9, adj_10);
                wp::adj_address(var_forces, var_0, var_1, adj_forces, adj_0, adj_1, adj_9);
                wp::adj_address(var_global_force_w, var_3, var_6, adj_global_force_w, adj_3, adj_6, adj_8);
                // adj: global_force_w[ei, bi] = global_force_w[ei, bi] + forces[tid_env, tid_body]  <L 26>
            }
            // adj: if positions:                                                             <L 25>
        }
        // adj: if forces:                                                                    <L 24>
    }
    // adj: if is_global:                                                                     <L 23>
    wp::adj_address(var_body_ids, var_1, adj_body_ids, adj_1, adj_5);
    // adj: bi = wp.int32(body_ids[tid_body])                                                 <L 21>
    wp::adj_address(var_env_ids, var_0, adj_env_ids, adj_0, adj_2);
    // adj: ei = wp.int32(env_ids[tid_env])                                                   <L 20>
    // adj: tid_env, tid_body = wp.tid()                                                      <L 19>
    // adj: def add_forces_to_dual_buffers_index(                                             <L 1>
    return;
}



extern "C" {

// Python CPU entry points
WP_API void add_forces_to_dual_buffers_index_ba5a2f71_cpu_forward(
    wp::launch_bounds_t<2> *dim,
    wp_args_add_forces_to_dual_buffers_index_ba5a2f71 *_wp_args)
{
    wp::tile_shared_storage_t tile_mem;
#if defined(WP_ENABLE_TILES_IN_STACK_MEMORY)
    wp::shared_tile_storage = &tile_mem;
#endif

    for (size_t task_index = 0; task_index < dim->size; ++task_index)
    {
        add_forces_to_dual_buffers_index_ba5a2f71_cpu_kernel_forward(*dim, task_index, _wp_args);
    }
}

} // extern C



extern "C" {

WP_API void add_forces_to_dual_buffers_index_ba5a2f71_cpu_backward(
    wp::launch_bounds_t<2> *dim,
    wp_args_add_forces_to_dual_buffers_index_ba5a2f71 *_wp_args,
    wp_args_add_forces_to_dual_buffers_index_ba5a2f71 *_wp_adj_args)
{
    wp::tile_shared_storage_t tile_mem;
#if defined(WP_ENABLE_TILES_IN_STACK_MEMORY)
    wp::shared_tile_storage = &tile_mem;
#endif

    for (size_t task_index = 0; task_index < dim->size; ++task_index)
    {
        add_forces_to_dual_buffers_index_ba5a2f71_cpu_kernel_backward(*dim, task_index, _wp_args, _wp_adj_args);
    }
}

} // extern C

struct wp_args_set_forces_to_dual_buffers_mask_bc5bdbe3 {
    wp::array_t<bool> env_mask;
    wp::array_t<bool> body_mask;
    wp::array_t<wp::vec_t<3, wp::float32>> forces;
    wp::array_t<wp::vec_t<3, wp::float32>> torques;
    wp::array_t<wp::vec_t<3, wp::float32>> positions;
    wp::array_t<wp::vec_t<3, wp::float32>> global_force_w;
    wp::array_t<wp::vec_t<3, wp::float32>> global_torque_w;
    wp::array_t<wp::vec_t<3, wp::float32>> global_force_at_com_w;
    wp::array_t<wp::vec_t<3, wp::float32>> local_force_b;
    wp::array_t<wp::vec_t<3, wp::float32>> local_torque_b;
    bool is_global;
};


void set_forces_to_dual_buffers_mask_bc5bdbe3_cpu_kernel_forward(
    wp::launch_bounds_t<2> dim,
    size_t task_index,
    wp_args_set_forces_to_dual_buffers_mask_bc5bdbe3 *_wp_args)
{
    //---------
    // argument vars
    wp::array_t<bool> var_env_mask = _wp_args->env_mask;
    wp::array_t<bool> var_body_mask = _wp_args->body_mask;
    wp::array_t<wp::vec_t<3, wp::float32>> var_forces = _wp_args->forces;
    wp::array_t<wp::vec_t<3, wp::float32>> var_torques = _wp_args->torques;
    wp::array_t<wp::vec_t<3, wp::float32>> var_positions = _wp_args->positions;
    wp::array_t<wp::vec_t<3, wp::float32>> var_global_force_w = _wp_args->global_force_w;
    wp::array_t<wp::vec_t<3, wp::float32>> var_global_torque_w = _wp_args->global_torque_w;
    wp::array_t<wp::vec_t<3, wp::float32>> var_global_force_at_com_w = _wp_args->global_force_at_com_w;
    wp::array_t<wp::vec_t<3, wp::float32>> var_local_force_b = _wp_args->local_force_b;
    wp::array_t<wp::vec_t<3, wp::float32>> var_local_torque_b = _wp_args->local_torque_b;
    bool var_is_global = _wp_args->is_global;
    //---------
    // primal vars
    wp::int32 var_0;
    wp::int32 var_1;
    bool var_2;
    bool* var_3;
    bool var_4;
    bool* var_5;
    bool var_6;
    wp::vec_t<3, wp::float32>* var_7;
    wp::vec_t<3, wp::float32> var_8;
    wp::vec_t<3, wp::float32>* var_9;
    wp::vec_t<3, wp::float32> var_10;
    wp::vec_t<3, wp::float32>* var_11;
    wp::vec_t<3, wp::float32>* var_12;
    wp::vec_t<3, wp::float32>* var_13;
    wp::vec_t<3, wp::float32> var_14;
    wp::vec_t<3, wp::float32> var_15;
    wp::vec_t<3, wp::float32> var_16;
    wp::vec_t<3, wp::float32> var_17;
    wp::vec_t<3, wp::float32> var_18;
    wp::vec_t<3, wp::float32>* var_19;
    wp::vec_t<3, wp::float32>* var_20;
    wp::vec_t<3, wp::float32> var_21;
    wp::vec_t<3, wp::float32> var_22;
    wp::vec_t<3, wp::float32> var_23;
    wp::vec_t<3, wp::float32>* var_24;
    wp::vec_t<3, wp::float32> var_25;
    wp::vec_t<3, wp::float32>* var_26;
    wp::vec_t<3, wp::float32> var_27;
    wp::vec_t<3, wp::float32>* var_28;
    wp::vec_t<3, wp::float32> var_29;
    wp::vec_t<3, wp::float32>* var_30;
    wp::vec_t<3, wp::float32>* var_31;
    wp::vec_t<3, wp::float32>* var_32;
    wp::vec_t<3, wp::float32> var_33;
    wp::vec_t<3, wp::float32> var_34;
    wp::vec_t<3, wp::float32> var_35;
    wp::vec_t<3, wp::float32> var_36;
    wp::vec_t<3, wp::float32> var_37;
    wp::vec_t<3, wp::float32>* var_38;
    wp::vec_t<3, wp::float32>* var_39;
    wp::vec_t<3, wp::float32> var_40;
    wp::vec_t<3, wp::float32> var_41;
    wp::vec_t<3, wp::float32> var_42;
    //---------
    // forward
    // def set_forces_to_dual_buffers_mask(                                                   <L 500>
    // tid_env, tid_body = wp.tid()                                                           <L 519>
    builtin_tid2d(var_0, var_1);
    // if env_mask[tid_env] and body_mask[tid_body]:                                          <L 521>
    var_3 = wp::address(var_env_mask, var_0);
    var_4 = wp::load(var_3);
    var_2 = var_4;
    if (var_2) {
        var_5 = wp::address(var_body_mask, var_1);
        var_6 = wp::load(var_5);
        var_2 = var_2 && var_6;
    }
    if (var_2) {
        // if is_global:                                                                      <L 522>
        if (var_is_global) {
            // if torques:                                                                    <L 523>
            if (var_torques) {
                // global_torque_w[tid_env, tid_body] = torques[tid_env, tid_body]            <L 524>
                var_7 = wp::address(var_torques, var_0, var_1);
                var_8 = wp::load(var_7);
                wp::array_store(var_global_torque_w, var_0, var_1, var_8);
            }
            // if forces:                                                                     <L 525>
            if (var_forces) {
                // if positions:                                                              <L 526>
                if (var_positions) {
                    // global_force_w[tid_env, tid_body] = forces[tid_env, tid_body]          <L 527>
                    var_9 = wp::address(var_forces, var_0, var_1);
                    var_10 = wp::load(var_9);
                    wp::array_store(var_global_force_w, var_0, var_1, var_10);
                    // if torques:                                                            <L 528>
                    if (var_torques) {
                        // global_torque_w[tid_env, tid_body] = global_torque_w[tid_env, tid_body] + wp.cross(       <L 529>
                        var_11 = wp::address(var_global_torque_w, var_0, var_1);
                        // positions[tid_env, tid_body], forces[tid_env, tid_body]            <L 530>
                        var_12 = wp::address(var_positions, var_0, var_1);
                        var_13 = wp::address(var_forces, var_0, var_1);
                        var_15 = wp::load(var_12);
                        var_16 = wp::load(var_13);
                        var_14 = wp::cross(var_15, var_16);
                        var_18 = wp::load(var_11);
                        var_17 = wp::add(var_18, var_14);
                        // global_torque_w[tid_env, tid_body] = global_torque_w[tid_env, tid_body] + wp.cross(       <L 529>
                        wp::array_store(var_global_torque_w, var_0, var_1, var_17);
                    }
                    if (!var_torques) {
                        // global_torque_w[tid_env, tid_body] = wp.cross(                     <L 533>
                        // positions[tid_env, tid_body], forces[tid_env, tid_body]            <L 534>
                        var_19 = wp::address(var_positions, var_0, var_1);
                        var_20 = wp::address(var_forces, var_0, var_1);
                        var_22 = wp::load(var_19);
                        var_23 = wp::load(var_20);
                        var_21 = wp::cross(var_22, var_23);
                        // global_torque_w[tid_env, tid_body] = wp.cross(                     <L 533>
                        wp::array_store(var_global_torque_w, var_0, var_1, var_21);
                    }
                }
                if (!var_positions) {
                    // global_force_at_com_w[tid_env, tid_body] = forces[tid_env, tid_body]       <L 537>
                    var_24 = wp::address(var_forces, var_0, var_1);
                    var_25 = wp::load(var_24);
                    wp::array_store(var_global_force_at_com_w, var_0, var_1, var_25);
                }
            }
        }
        if (!var_is_global) {
            // if torques:                                                                    <L 539>
            if (var_torques) {
                // local_torque_b[tid_env, tid_body] = torques[tid_env, tid_body]             <L 540>
                var_26 = wp::address(var_torques, var_0, var_1);
                var_27 = wp::load(var_26);
                wp::array_store(var_local_torque_b, var_0, var_1, var_27);
            }
            // if forces:                                                                     <L 541>
            if (var_forces) {
                // local_force_b[tid_env, tid_body] = forces[tid_env, tid_body]               <L 542>
                var_28 = wp::address(var_forces, var_0, var_1);
                var_29 = wp::load(var_28);
                wp::array_store(var_local_force_b, var_0, var_1, var_29);
                // if positions:                                                              <L 543>
                if (var_positions) {
                    // if torques:                                                            <L 544>
                    if (var_torques) {
                        // local_torque_b[tid_env, tid_body] = local_torque_b[tid_env, tid_body] + wp.cross(       <L 545>
                        var_30 = wp::address(var_local_torque_b, var_0, var_1);
                        // positions[tid_env, tid_body], forces[tid_env, tid_body]            <L 546>
                        var_31 = wp::address(var_positions, var_0, var_1);
                        var_32 = wp::address(var_forces, var_0, var_1);
                        var_34 = wp::load(var_31);
                        var_35 = wp::load(var_32);
                        var_33 = wp::cross(var_34, var_35);
                        var_37 = wp::load(var_30);
                        var_36 = wp::add(var_37, var_33);
                        // local_torque_b[tid_env, tid_body] = local_torque_b[tid_env, tid_body] + wp.cross(       <L 545>
                        wp::array_store(var_local_torque_b, var_0, var_1, var_36);
                    }
                    if (!var_torques) {
                        // local_torque_b[tid_env, tid_body] = wp.cross(                      <L 549>
                        // positions[tid_env, tid_body], forces[tid_env, tid_body]            <L 550>
                        var_38 = wp::address(var_positions, var_0, var_1);
                        var_39 = wp::address(var_forces, var_0, var_1);
                        var_41 = wp::load(var_38);
                        var_42 = wp::load(var_39);
                        var_40 = wp::cross(var_41, var_42);
                        // local_torque_b[tid_env, tid_body] = wp.cross(                      <L 549>
                        wp::array_store(var_local_torque_b, var_0, var_1, var_40);
                    }
                }
            }
        }
    }
}



void set_forces_to_dual_buffers_mask_bc5bdbe3_cpu_kernel_backward(
    wp::launch_bounds_t<2> dim,
    size_t task_index,
    wp_args_set_forces_to_dual_buffers_mask_bc5bdbe3 *_wp_args,
    wp_args_set_forces_to_dual_buffers_mask_bc5bdbe3 *_wp_adj_args)
{
    //---------
    // argument vars
    wp::array_t<bool> var_env_mask = _wp_args->env_mask;
    wp::array_t<bool> var_body_mask = _wp_args->body_mask;
    wp::array_t<wp::vec_t<3, wp::float32>> var_forces = _wp_args->forces;
    wp::array_t<wp::vec_t<3, wp::float32>> var_torques = _wp_args->torques;
    wp::array_t<wp::vec_t<3, wp::float32>> var_positions = _wp_args->positions;
    wp::array_t<wp::vec_t<3, wp::float32>> var_global_force_w = _wp_args->global_force_w;
    wp::array_t<wp::vec_t<3, wp::float32>> var_global_torque_w = _wp_args->global_torque_w;
    wp::array_t<wp::vec_t<3, wp::float32>> var_global_force_at_com_w = _wp_args->global_force_at_com_w;
    wp::array_t<wp::vec_t<3, wp::float32>> var_local_force_b = _wp_args->local_force_b;
    wp::array_t<wp::vec_t<3, wp::float32>> var_local_torque_b = _wp_args->local_torque_b;
    bool var_is_global = _wp_args->is_global;
    wp::array_t<bool> adj_env_mask = _wp_adj_args->env_mask;
    wp::array_t<bool> adj_body_mask = _wp_adj_args->body_mask;
    wp::array_t<wp::vec_t<3, wp::float32>> adj_forces = _wp_adj_args->forces;
    wp::array_t<wp::vec_t<3, wp::float32>> adj_torques = _wp_adj_args->torques;
    wp::array_t<wp::vec_t<3, wp::float32>> adj_positions = _wp_adj_args->positions;
    wp::array_t<wp::vec_t<3, wp::float32>> adj_global_force_w = _wp_adj_args->global_force_w;
    wp::array_t<wp::vec_t<3, wp::float32>> adj_global_torque_w = _wp_adj_args->global_torque_w;
    wp::array_t<wp::vec_t<3, wp::float32>> adj_global_force_at_com_w = _wp_adj_args->global_force_at_com_w;
    wp::array_t<wp::vec_t<3, wp::float32>> adj_local_force_b = _wp_adj_args->local_force_b;
    wp::array_t<wp::vec_t<3, wp::float32>> adj_local_torque_b = _wp_adj_args->local_torque_b;
    bool adj_is_global = _wp_adj_args->is_global;
    //---------
    // primal vars
    wp::int32 var_0;
    wp::int32 var_1;
    bool var_2;
    bool* var_3;
    bool var_4;
    bool* var_5;
    bool var_6;
    wp::vec_t<3, wp::float32>* var_7;
    wp::vec_t<3, wp::float32> var_8;
    wp::vec_t<3, wp::float32>* var_9;
    wp::vec_t<3, wp::float32> var_10;
    wp::vec_t<3, wp::float32>* var_11;
    wp::vec_t<3, wp::float32>* var_12;
    wp::vec_t<3, wp::float32>* var_13;
    wp::vec_t<3, wp::float32> var_14;
    wp::vec_t<3, wp::float32> var_15;
    wp::vec_t<3, wp::float32> var_16;
    wp::vec_t<3, wp::float32> var_17;
    wp::vec_t<3, wp::float32> var_18;
    wp::vec_t<3, wp::float32>* var_19;
    wp::vec_t<3, wp::float32>* var_20;
    wp::vec_t<3, wp::float32> var_21;
    wp::vec_t<3, wp::float32> var_22;
    wp::vec_t<3, wp::float32> var_23;
    wp::vec_t<3, wp::float32>* var_24;
    wp::vec_t<3, wp::float32> var_25;
    wp::vec_t<3, wp::float32>* var_26;
    wp::vec_t<3, wp::float32> var_27;
    wp::vec_t<3, wp::float32>* var_28;
    wp::vec_t<3, wp::float32> var_29;
    wp::vec_t<3, wp::float32>* var_30;
    wp::vec_t<3, wp::float32>* var_31;
    wp::vec_t<3, wp::float32>* var_32;
    wp::vec_t<3, wp::float32> var_33;
    wp::vec_t<3, wp::float32> var_34;
    wp::vec_t<3, wp::float32> var_35;
    wp::vec_t<3, wp::float32> var_36;
    wp::vec_t<3, wp::float32> var_37;
    wp::vec_t<3, wp::float32>* var_38;
    wp::vec_t<3, wp::float32>* var_39;
    wp::vec_t<3, wp::float32> var_40;
    wp::vec_t<3, wp::float32> var_41;
    wp::vec_t<3, wp::float32> var_42;
    //---------
    // dual vars
    wp::int32 adj_0 = {};
    wp::int32 adj_1 = {};
    bool adj_2 = {};
    bool adj_3 = {};
    bool adj_4 = {};
    bool adj_5 = {};
    bool adj_6 = {};
    wp::vec_t<3, wp::float32> adj_7 = {};
    wp::vec_t<3, wp::float32> adj_8 = {};
    wp::vec_t<3, wp::float32> adj_9 = {};
    wp::vec_t<3, wp::float32> adj_10 = {};
    wp::vec_t<3, wp::float32> adj_11 = {};
    wp::vec_t<3, wp::float32> adj_12 = {};
    wp::vec_t<3, wp::float32> adj_13 = {};
    wp::vec_t<3, wp::float32> adj_14 = {};
    wp::vec_t<3, wp::float32> adj_15 = {};
    wp::vec_t<3, wp::float32> adj_16 = {};
    wp::vec_t<3, wp::float32> adj_17 = {};
    wp::vec_t<3, wp::float32> adj_18 = {};
    wp::vec_t<3, wp::float32> adj_19 = {};
    wp::vec_t<3, wp::float32> adj_20 = {};
    wp::vec_t<3, wp::float32> adj_21 = {};
    wp::vec_t<3, wp::float32> adj_22 = {};
    wp::vec_t<3, wp::float32> adj_23 = {};
    wp::vec_t<3, wp::float32> adj_24 = {};
    wp::vec_t<3, wp::float32> adj_25 = {};
    wp::vec_t<3, wp::float32> adj_26 = {};
    wp::vec_t<3, wp::float32> adj_27 = {};
    wp::vec_t<3, wp::float32> adj_28 = {};
    wp::vec_t<3, wp::float32> adj_29 = {};
    wp::vec_t<3, wp::float32> adj_30 = {};
    wp::vec_t<3, wp::float32> adj_31 = {};
    wp::vec_t<3, wp::float32> adj_32 = {};
    wp::vec_t<3, wp::float32> adj_33 = {};
    wp::vec_t<3, wp::float32> adj_34 = {};
    wp::vec_t<3, wp::float32> adj_35 = {};
    wp::vec_t<3, wp::float32> adj_36 = {};
    wp::vec_t<3, wp::float32> adj_37 = {};
    wp::vec_t<3, wp::float32> adj_38 = {};
    wp::vec_t<3, wp::float32> adj_39 = {};
    wp::vec_t<3, wp::float32> adj_40 = {};
    wp::vec_t<3, wp::float32> adj_41 = {};
    wp::vec_t<3, wp::float32> adj_42 = {};
    //---------
    // forward
    // def set_forces_to_dual_buffers_mask(                                                   <L 500>
    // tid_env, tid_body = wp.tid()                                                           <L 519>
    builtin_tid2d(var_0, var_1);
    // if env_mask[tid_env] and body_mask[tid_body]:                                          <L 521>
    var_3 = wp::address(var_env_mask, var_0);
    var_4 = wp::load(var_3);
    var_2 = var_4;
    if (var_2) {
        var_5 = wp::address(var_body_mask, var_1);
        var_6 = wp::load(var_5);
        var_2 = var_2 && var_6;
    }
    if (var_2) {
        // if is_global:                                                                      <L 522>
        if (var_is_global) {
            // if torques:                                                                    <L 523>
            if (var_torques) {
                // global_torque_w[tid_env, tid_body] = torques[tid_env, tid_body]            <L 524>
                var_7 = wp::address(var_torques, var_0, var_1);
                var_8 = wp::load(var_7);
                // wp::array_store(var_global_torque_w, var_0, var_1, var_8);
            }
            // if forces:                                                                     <L 525>
            if (var_forces) {
                // if positions:                                                              <L 526>
                if (var_positions) {
                    // global_force_w[tid_env, tid_body] = forces[tid_env, tid_body]          <L 527>
                    var_9 = wp::address(var_forces, var_0, var_1);
                    var_10 = wp::load(var_9);
                    // wp::array_store(var_global_force_w, var_0, var_1, var_10);
                    // if torques:                                                            <L 528>
                    if (var_torques) {
                        // global_torque_w[tid_env, tid_body] = global_torque_w[tid_env, tid_body] + wp.cross(       <L 529>
                        var_11 = wp::address(var_global_torque_w, var_0, var_1);
                        // positions[tid_env, tid_body], forces[tid_env, tid_body]            <L 530>
                        var_12 = wp::address(var_positions, var_0, var_1);
                        var_13 = wp::address(var_forces, var_0, var_1);
                        var_15 = wp::load(var_12);
                        var_16 = wp::load(var_13);
                        var_14 = wp::cross(var_15, var_16);
                        var_18 = wp::load(var_11);
                        var_17 = wp::add(var_18, var_14);
                        // global_torque_w[tid_env, tid_body] = global_torque_w[tid_env, tid_body] + wp.cross(       <L 529>
                        // wp::array_store(var_global_torque_w, var_0, var_1, var_17);
                    }
                    if (!var_torques) {
                        // global_torque_w[tid_env, tid_body] = wp.cross(                     <L 533>
                        // positions[tid_env, tid_body], forces[tid_env, tid_body]            <L 534>
                        var_19 = wp::address(var_positions, var_0, var_1);
                        var_20 = wp::address(var_forces, var_0, var_1);
                        var_22 = wp::load(var_19);
                        var_23 = wp::load(var_20);
                        var_21 = wp::cross(var_22, var_23);
                        // global_torque_w[tid_env, tid_body] = wp.cross(                     <L 533>
                        // wp::array_store(var_global_torque_w, var_0, var_1, var_21);
                    }
                }
                if (!var_positions) {
                    // global_force_at_com_w[tid_env, tid_body] = forces[tid_env, tid_body]       <L 537>
                    var_24 = wp::address(var_forces, var_0, var_1);
                    var_25 = wp::load(var_24);
                    // wp::array_store(var_global_force_at_com_w, var_0, var_1, var_25);
                }
            }
        }
        if (!var_is_global) {
            // if torques:                                                                    <L 539>
            if (var_torques) {
                // local_torque_b[tid_env, tid_body] = torques[tid_env, tid_body]             <L 540>
                var_26 = wp::address(var_torques, var_0, var_1);
                var_27 = wp::load(var_26);
                // wp::array_store(var_local_torque_b, var_0, var_1, var_27);
            }
            // if forces:                                                                     <L 541>
            if (var_forces) {
                // local_force_b[tid_env, tid_body] = forces[tid_env, tid_body]               <L 542>
                var_28 = wp::address(var_forces, var_0, var_1);
                var_29 = wp::load(var_28);
                // wp::array_store(var_local_force_b, var_0, var_1, var_29);
                // if positions:                                                              <L 543>
                if (var_positions) {
                    // if torques:                                                            <L 544>
                    if (var_torques) {
                        // local_torque_b[tid_env, tid_body] = local_torque_b[tid_env, tid_body] + wp.cross(       <L 545>
                        var_30 = wp::address(var_local_torque_b, var_0, var_1);
                        // positions[tid_env, tid_body], forces[tid_env, tid_body]            <L 546>
                        var_31 = wp::address(var_positions, var_0, var_1);
                        var_32 = wp::address(var_forces, var_0, var_1);
                        var_34 = wp::load(var_31);
                        var_35 = wp::load(var_32);
                        var_33 = wp::cross(var_34, var_35);
                        var_37 = wp::load(var_30);
                        var_36 = wp::add(var_37, var_33);
                        // local_torque_b[tid_env, tid_body] = local_torque_b[tid_env, tid_body] + wp.cross(       <L 545>
                        // wp::array_store(var_local_torque_b, var_0, var_1, var_36);
                    }
                    if (!var_torques) {
                        // local_torque_b[tid_env, tid_body] = wp.cross(                      <L 549>
                        // positions[tid_env, tid_body], forces[tid_env, tid_body]            <L 550>
                        var_38 = wp::address(var_positions, var_0, var_1);
                        var_39 = wp::address(var_forces, var_0, var_1);
                        var_41 = wp::load(var_38);
                        var_42 = wp::load(var_39);
                        var_40 = wp::cross(var_41, var_42);
                        // local_torque_b[tid_env, tid_body] = wp.cross(                      <L 549>
                        // wp::array_store(var_local_torque_b, var_0, var_1, var_40);
                    }
                }
            }
        }
    }
    //---------
    // reverse
    if (var_2) {
        if (!var_is_global) {
            if (var_forces) {
                if (var_positions) {
                    if (!var_torques) {
                        wp::adj_array_store(var_local_torque_b, var_0, var_1, var_40, adj_local_torque_b, adj_0, adj_1, adj_40);
                        // adj: local_torque_b[tid_env, tid_body] = wp.cross(                 <L 549>
                        wp::adj_cross(var_41, var_42, adj_38, adj_39, adj_40);
                        wp::adj_address(var_forces, var_0, var_1, adj_forces, adj_0, adj_1, adj_39);
                        wp::adj_address(var_positions, var_0, var_1, adj_positions, adj_0, adj_1, adj_38);
                        // adj: positions[tid_env, tid_body], forces[tid_env, tid_body]       <L 550>
                        // adj: local_torque_b[tid_env, tid_body] = wp.cross(                 <L 549>
                    }
                    if (var_torques) {
                        wp::adj_array_store(var_local_torque_b, var_0, var_1, var_36, adj_local_torque_b, adj_0, adj_1, adj_36);
                        // adj: local_torque_b[tid_env, tid_body] = local_torque_b[tid_env, tid_body] + wp.cross(  <L 545>
                        wp::adj_add(var_37, var_33, adj_30, adj_33, adj_36);
                        wp::adj_cross(var_34, var_35, adj_31, adj_32, adj_33);
                        wp::adj_address(var_forces, var_0, var_1, adj_forces, adj_0, adj_1, adj_32);
                        wp::adj_address(var_positions, var_0, var_1, adj_positions, adj_0, adj_1, adj_31);
                        // adj: positions[tid_env, tid_body], forces[tid_env, tid_body]       <L 546>
                        wp::adj_address(var_local_torque_b, var_0, var_1, adj_local_torque_b, adj_0, adj_1, adj_30);
                        // adj: local_torque_b[tid_env, tid_body] = local_torque_b[tid_env, tid_body] + wp.cross(  <L 545>
                    }
                    // adj: if torques:                                                       <L 544>
                }
                // adj: if positions:                                                         <L 543>
                wp::adj_array_store(var_local_force_b, var_0, var_1, var_29, adj_local_force_b, adj_0, adj_1, adj_28);
                wp::adj_address(var_forces, var_0, var_1, adj_forces, adj_0, adj_1, adj_28);
                // adj: local_force_b[tid_env, tid_body] = forces[tid_env, tid_body]          <L 542>
            }
            // adj: if forces:                                                                <L 541>
            if (var_torques) {
                wp::adj_array_store(var_local_torque_b, var_0, var_1, var_27, adj_local_torque_b, adj_0, adj_1, adj_26);
                wp::adj_address(var_torques, var_0, var_1, adj_torques, adj_0, adj_1, adj_26);
                // adj: local_torque_b[tid_env, tid_body] = torques[tid_env, tid_body]        <L 540>
            }
            // adj: if torques:                                                               <L 539>
        }
        if (var_is_global) {
            if (var_forces) {
                if (!var_positions) {
                    wp::adj_array_store(var_global_force_at_com_w, var_0, var_1, var_25, adj_global_force_at_com_w, adj_0, adj_1, adj_24);
                    wp::adj_address(var_forces, var_0, var_1, adj_forces, adj_0, adj_1, adj_24);
                    // adj: global_force_at_com_w[tid_env, tid_body] = forces[tid_env, tid_body]  <L 537>
                }
                if (var_positions) {
                    if (!var_torques) {
                        wp::adj_array_store(var_global_torque_w, var_0, var_1, var_21, adj_global_torque_w, adj_0, adj_1, adj_21);
                        // adj: global_torque_w[tid_env, tid_body] = wp.cross(                <L 533>
                        wp::adj_cross(var_22, var_23, adj_19, adj_20, adj_21);
                        wp::adj_address(var_forces, var_0, var_1, adj_forces, adj_0, adj_1, adj_20);
                        wp::adj_address(var_positions, var_0, var_1, adj_positions, adj_0, adj_1, adj_19);
                        // adj: positions[tid_env, tid_body], forces[tid_env, tid_body]       <L 534>
                        // adj: global_torque_w[tid_env, tid_body] = wp.cross(                <L 533>
                    }
                    if (var_torques) {
                        wp::adj_array_store(var_global_torque_w, var_0, var_1, var_17, adj_global_torque_w, adj_0, adj_1, adj_17);
                        // adj: global_torque_w[tid_env, tid_body] = global_torque_w[tid_env, tid_body] + wp.cross(  <L 529>
                        wp::adj_add(var_18, var_14, adj_11, adj_14, adj_17);
                        wp::adj_cross(var_15, var_16, adj_12, adj_13, adj_14);
                        wp::adj_address(var_forces, var_0, var_1, adj_forces, adj_0, adj_1, adj_13);
                        wp::adj_address(var_positions, var_0, var_1, adj_positions, adj_0, adj_1, adj_12);
                        // adj: positions[tid_env, tid_body], forces[tid_env, tid_body]       <L 530>
                        wp::adj_address(var_global_torque_w, var_0, var_1, adj_global_torque_w, adj_0, adj_1, adj_11);
                        // adj: global_torque_w[tid_env, tid_body] = global_torque_w[tid_env, tid_body] + wp.cross(  <L 529>
                    }
                    // adj: if torques:                                                       <L 528>
                    wp::adj_array_store(var_global_force_w, var_0, var_1, var_10, adj_global_force_w, adj_0, adj_1, adj_9);
                    wp::adj_address(var_forces, var_0, var_1, adj_forces, adj_0, adj_1, adj_9);
                    // adj: global_force_w[tid_env, tid_body] = forces[tid_env, tid_body]     <L 527>
                }
                // adj: if positions:                                                         <L 526>
            }
            // adj: if forces:                                                                <L 525>
            if (var_torques) {
                wp::adj_array_store(var_global_torque_w, var_0, var_1, var_8, adj_global_torque_w, adj_0, adj_1, adj_7);
                wp::adj_address(var_torques, var_0, var_1, adj_torques, adj_0, adj_1, adj_7);
                // adj: global_torque_w[tid_env, tid_body] = torques[tid_env, tid_body]       <L 524>
            }
            // adj: if torques:                                                               <L 523>
        }
        // adj: if is_global:                                                                 <L 522>
    }
    if (var_2) {
        wp::adj_address(var_body_mask, var_1, adj_body_mask, adj_1, adj_5);
    }
    wp::adj_address(var_env_mask, var_0, adj_env_mask, adj_0, adj_3);
    // adj: if env_mask[tid_env] and body_mask[tid_body]:                                     <L 521>
    // adj: tid_env, tid_body = wp.tid()                                                      <L 519>
    // adj: def set_forces_to_dual_buffers_mask(                                              <L 500>
    return;
}



extern "C" {

// Python CPU entry points
WP_API void set_forces_to_dual_buffers_mask_bc5bdbe3_cpu_forward(
    wp::launch_bounds_t<2> *dim,
    wp_args_set_forces_to_dual_buffers_mask_bc5bdbe3 *_wp_args)
{
    wp::tile_shared_storage_t tile_mem;
#if defined(WP_ENABLE_TILES_IN_STACK_MEMORY)
    wp::shared_tile_storage = &tile_mem;
#endif

    for (size_t task_index = 0; task_index < dim->size; ++task_index)
    {
        set_forces_to_dual_buffers_mask_bc5bdbe3_cpu_kernel_forward(*dim, task_index, _wp_args);
    }
}

} // extern C



extern "C" {

WP_API void set_forces_to_dual_buffers_mask_bc5bdbe3_cpu_backward(
    wp::launch_bounds_t<2> *dim,
    wp_args_set_forces_to_dual_buffers_mask_bc5bdbe3 *_wp_args,
    wp_args_set_forces_to_dual_buffers_mask_bc5bdbe3 *_wp_adj_args)
{
    wp::tile_shared_storage_t tile_mem;
#if defined(WP_ENABLE_TILES_IN_STACK_MEMORY)
    wp::shared_tile_storage = &tile_mem;
#endif

    for (size_t task_index = 0; task_index < dim->size; ++task_index)
    {
        set_forces_to_dual_buffers_mask_bc5bdbe3_cpu_kernel_backward(*dim, task_index, _wp_args, _wp_adj_args);
    }
}

} // extern C

struct wp_args_subtract_2d_bcb5c18e {
    wp::array_t<wp::float32> a;
    wp::array_t<wp::float32> b;
    wp::array_t<wp::float32> out;
};


void subtract_2d_bcb5c18e_cpu_kernel_forward(
    wp::launch_bounds_t<2> dim,
    size_t task_index,
    wp_args_subtract_2d_bcb5c18e *_wp_args)
{
    //---------
    // argument vars
    wp::array_t<wp::float32> var_a = _wp_args->a;
    wp::array_t<wp::float32> var_b = _wp_args->b;
    wp::array_t<wp::float32> var_out = _wp_args->out;
    //---------
    // primal vars
    wp::int32 var_0;
    wp::int32 var_1;
    wp::float32* var_2;
    wp::float32* var_3;
    wp::float32 var_4;
    wp::float32 var_5;
    wp::float32 var_6;
    //---------
    // forward
    // def subtract_2d(                                                                       <L 825>
    // i, j = wp.tid()                                                                        <L 831>
    builtin_tid2d(var_0, var_1);
    // out[i, j] = a[i, j] - b[i, j]                                                          <L 832>
    var_2 = wp::address(var_a, var_0, var_1);
    var_3 = wp::address(var_b, var_0, var_1);
    var_5 = wp::load(var_2);
    var_6 = wp::load(var_3);
    var_4 = wp::sub(var_5, var_6);
    wp::array_store(var_out, var_0, var_1, var_4);
}



void subtract_2d_bcb5c18e_cpu_kernel_backward(
    wp::launch_bounds_t<2> dim,
    size_t task_index,
    wp_args_subtract_2d_bcb5c18e *_wp_args,
    wp_args_subtract_2d_bcb5c18e *_wp_adj_args)
{
    //---------
    // argument vars
    wp::array_t<wp::float32> var_a = _wp_args->a;
    wp::array_t<wp::float32> var_b = _wp_args->b;
    wp::array_t<wp::float32> var_out = _wp_args->out;
    wp::array_t<wp::float32> adj_a = _wp_adj_args->a;
    wp::array_t<wp::float32> adj_b = _wp_adj_args->b;
    wp::array_t<wp::float32> adj_out = _wp_adj_args->out;
    //---------
    // primal vars
    wp::int32 var_0;
    wp::int32 var_1;
    wp::float32* var_2;
    wp::float32* var_3;
    wp::float32 var_4;
    wp::float32 var_5;
    wp::float32 var_6;
    //---------
    // dual vars
    wp::int32 adj_0 = {};
    wp::int32 adj_1 = {};
    wp::float32 adj_2 = {};
    wp::float32 adj_3 = {};
    wp::float32 adj_4 = {};
    wp::float32 adj_5 = {};
    wp::float32 adj_6 = {};
    //---------
    // forward
    // def subtract_2d(                                                                       <L 825>
    // i, j = wp.tid()                                                                        <L 831>
    builtin_tid2d(var_0, var_1);
    // out[i, j] = a[i, j] - b[i, j]                                                          <L 832>
    var_2 = wp::address(var_a, var_0, var_1);
    var_3 = wp::address(var_b, var_0, var_1);
    var_5 = wp::load(var_2);
    var_6 = wp::load(var_3);
    var_4 = wp::sub(var_5, var_6);
    // wp::array_store(var_out, var_0, var_1, var_4);
    //---------
    // reverse
    wp::adj_array_store(var_out, var_0, var_1, var_4, adj_out, adj_0, adj_1, adj_4);
    wp::adj_sub(var_5, var_6, adj_2, adj_3, adj_4);
    wp::adj_address(var_b, var_0, var_1, adj_b, adj_0, adj_1, adj_3);
    wp::adj_address(var_a, var_0, var_1, adj_a, adj_0, adj_1, adj_2);
    // adj: out[i, j] = a[i, j] - b[i, j]                                                     <L 832>
    // adj: i, j = wp.tid()                                                                   <L 831>
    // adj: def subtract_2d(                                                                  <L 825>
    return;
}



extern "C" {

// Python CPU entry points
WP_API void subtract_2d_bcb5c18e_cpu_forward(
    wp::launch_bounds_t<2> *dim,
    wp_args_subtract_2d_bcb5c18e *_wp_args)
{
    wp::tile_shared_storage_t tile_mem;
#if defined(WP_ENABLE_TILES_IN_STACK_MEMORY)
    wp::shared_tile_storage = &tile_mem;
#endif

    for (size_t task_index = 0; task_index < dim->size; ++task_index)
    {
        subtract_2d_bcb5c18e_cpu_kernel_forward(*dim, task_index, _wp_args);
    }
}

} // extern C



extern "C" {

WP_API void subtract_2d_bcb5c18e_cpu_backward(
    wp::launch_bounds_t<2> *dim,
    wp_args_subtract_2d_bcb5c18e *_wp_args,
    wp_args_subtract_2d_bcb5c18e *_wp_adj_args)
{
    wp::tile_shared_storage_t tile_mem;
#if defined(WP_ENABLE_TILES_IN_STACK_MEMORY)
    wp::shared_tile_storage = &tile_mem;
#endif

    for (size_t task_index = 0; task_index < dim->size; ++task_index)
    {
        subtract_2d_bcb5c18e_cpu_kernel_backward(*dim, task_index, _wp_args, _wp_adj_args);
    }
}

} // extern C

struct wp_args_reset_wrench_composer_mask_bd82acc5 {
    wp::array_t<bool> env_mask;
    wp::array_t<wp::vec_t<3, wp::float32>> global_force_w;
    wp::array_t<wp::vec_t<3, wp::float32>> global_torque_w;
    wp::array_t<wp::vec_t<3, wp::float32>> global_force_at_com_w;
    wp::array_t<wp::vec_t<3, wp::float32>> local_force_b;
    wp::array_t<wp::vec_t<3, wp::float32>> local_torque_b;
    wp::array_t<wp::vec_t<3, wp::float32>> out_force_b;
    wp::array_t<wp::vec_t<3, wp::float32>> out_torque_b;
};


void reset_wrench_composer_mask_bd82acc5_cpu_kernel_forward(
    wp::launch_bounds_t<2> dim,
    size_t task_index,
    wp_args_reset_wrench_composer_mask_bd82acc5 *_wp_args)
{
    //---------
    // argument vars
    wp::array_t<bool> var_env_mask = _wp_args->env_mask;
    wp::array_t<wp::vec_t<3, wp::float32>> var_global_force_w = _wp_args->global_force_w;
    wp::array_t<wp::vec_t<3, wp::float32>> var_global_torque_w = _wp_args->global_torque_w;
    wp::array_t<wp::vec_t<3, wp::float32>> var_global_force_at_com_w = _wp_args->global_force_at_com_w;
    wp::array_t<wp::vec_t<3, wp::float32>> var_local_force_b = _wp_args->local_force_b;
    wp::array_t<wp::vec_t<3, wp::float32>> var_local_torque_b = _wp_args->local_torque_b;
    wp::array_t<wp::vec_t<3, wp::float32>> var_out_force_b = _wp_args->out_force_b;
    wp::array_t<wp::vec_t<3, wp::float32>> var_out_torque_b = _wp_args->out_torque_b;
    //---------
    // primal vars
    wp::int32 var_0;
    wp::int32 var_1;
    bool* var_2;
    bool var_3;
    const wp::float32 var_4 = 0.0;
    wp::vec_t<3, wp::float32> var_5;
    bool var_6;
    //---------
    // forward
    // def reset_wrench_composer_mask(                                                        <L 793>
    // tid_env, tid_body = wp.tid()                                                           <L 807>
    builtin_tid2d(var_0, var_1);
    // if env_mask[tid_env]:                                                                  <L 808>
    var_2 = wp::address(var_env_mask, var_0);
    var_3 = wp::load(var_2);
    if (var_3) {
        // z = wp.vec3f(0.0)                                                                  <L 809>
        var_5 = wp::vec_t<3, wp::float32>(var_4);
        // global_force_w[tid_env, tid_body] = z                                              <L 810>
        wp::array_store(var_global_force_w, var_0, var_1, var_5);
        // global_torque_w[tid_env, tid_body] = z                                             <L 811>
        wp::array_store(var_global_torque_w, var_0, var_1, var_5);
        // global_force_at_com_w[tid_env, tid_body] = z                                       <L 812>
        wp::array_store(var_global_force_at_com_w, var_0, var_1, var_5);
        // local_force_b[tid_env, tid_body] = z                                               <L 813>
        wp::array_store(var_local_force_b, var_0, var_1, var_5);
        // local_torque_b[tid_env, tid_body] = z                                              <L 814>
        wp::array_store(var_local_torque_b, var_0, var_1, var_5);
        // out_force_b[tid_env, tid_body] = z                                                 <L 815>
        wp::array_store(var_out_force_b, var_0, var_1, var_5);
        // out_torque_b[tid_env, tid_body] = z                                                <L 816>
        wp::array_store(var_out_torque_b, var_0, var_1, var_5);
    }
    var_6 = wp::load(var_2);
}



void reset_wrench_composer_mask_bd82acc5_cpu_kernel_backward(
    wp::launch_bounds_t<2> dim,
    size_t task_index,
    wp_args_reset_wrench_composer_mask_bd82acc5 *_wp_args,
    wp_args_reset_wrench_composer_mask_bd82acc5 *_wp_adj_args)
{
    //---------
    // argument vars
    wp::array_t<bool> var_env_mask = _wp_args->env_mask;
    wp::array_t<wp::vec_t<3, wp::float32>> var_global_force_w = _wp_args->global_force_w;
    wp::array_t<wp::vec_t<3, wp::float32>> var_global_torque_w = _wp_args->global_torque_w;
    wp::array_t<wp::vec_t<3, wp::float32>> var_global_force_at_com_w = _wp_args->global_force_at_com_w;
    wp::array_t<wp::vec_t<3, wp::float32>> var_local_force_b = _wp_args->local_force_b;
    wp::array_t<wp::vec_t<3, wp::float32>> var_local_torque_b = _wp_args->local_torque_b;
    wp::array_t<wp::vec_t<3, wp::float32>> var_out_force_b = _wp_args->out_force_b;
    wp::array_t<wp::vec_t<3, wp::float32>> var_out_torque_b = _wp_args->out_torque_b;
    wp::array_t<bool> adj_env_mask = _wp_adj_args->env_mask;
    wp::array_t<wp::vec_t<3, wp::float32>> adj_global_force_w = _wp_adj_args->global_force_w;
    wp::array_t<wp::vec_t<3, wp::float32>> adj_global_torque_w = _wp_adj_args->global_torque_w;
    wp::array_t<wp::vec_t<3, wp::float32>> adj_global_force_at_com_w = _wp_adj_args->global_force_at_com_w;
    wp::array_t<wp::vec_t<3, wp::float32>> adj_local_force_b = _wp_adj_args->local_force_b;
    wp::array_t<wp::vec_t<3, wp::float32>> adj_local_torque_b = _wp_adj_args->local_torque_b;
    wp::array_t<wp::vec_t<3, wp::float32>> adj_out_force_b = _wp_adj_args->out_force_b;
    wp::array_t<wp::vec_t<3, wp::float32>> adj_out_torque_b = _wp_adj_args->out_torque_b;
    //---------
    // primal vars
    wp::int32 var_0;
    wp::int32 var_1;
    bool* var_2;
    bool var_3;
    const wp::float32 var_4 = 0.0;
    wp::vec_t<3, wp::float32> var_5;
    bool var_6;
    //---------
    // dual vars
    wp::int32 adj_0 = {};
    wp::int32 adj_1 = {};
    bool adj_2 = {};
    bool adj_3 = {};
    wp::float32 adj_4 = {};
    wp::vec_t<3, wp::float32> adj_5 = {};
    bool adj_6 = {};
    //---------
    // forward
    // def reset_wrench_composer_mask(                                                        <L 793>
    // tid_env, tid_body = wp.tid()                                                           <L 807>
    builtin_tid2d(var_0, var_1);
    // if env_mask[tid_env]:                                                                  <L 808>
    var_2 = wp::address(var_env_mask, var_0);
    var_3 = wp::load(var_2);
    if (var_3) {
        // z = wp.vec3f(0.0)                                                                  <L 809>
        var_5 = wp::vec_t<3, wp::float32>(var_4);
        // global_force_w[tid_env, tid_body] = z                                              <L 810>
        // wp::array_store(var_global_force_w, var_0, var_1, var_5);
        // global_torque_w[tid_env, tid_body] = z                                             <L 811>
        // wp::array_store(var_global_torque_w, var_0, var_1, var_5);
        // global_force_at_com_w[tid_env, tid_body] = z                                       <L 812>
        // wp::array_store(var_global_force_at_com_w, var_0, var_1, var_5);
        // local_force_b[tid_env, tid_body] = z                                               <L 813>
        // wp::array_store(var_local_force_b, var_0, var_1, var_5);
        // local_torque_b[tid_env, tid_body] = z                                              <L 814>
        // wp::array_store(var_local_torque_b, var_0, var_1, var_5);
        // out_force_b[tid_env, tid_body] = z                                                 <L 815>
        // wp::array_store(var_out_force_b, var_0, var_1, var_5);
        // out_torque_b[tid_env, tid_body] = z                                                <L 816>
        // wp::array_store(var_out_torque_b, var_0, var_1, var_5);
    }
    var_6 = wp::load(var_2);
    //---------
    // reverse
    if (var_6) {
        wp::adj_array_store(var_out_torque_b, var_0, var_1, var_5, adj_out_torque_b, adj_0, adj_1, adj_5);
        // adj: out_torque_b[tid_env, tid_body] = z                                           <L 816>
        wp::adj_array_store(var_out_force_b, var_0, var_1, var_5, adj_out_force_b, adj_0, adj_1, adj_5);
        // adj: out_force_b[tid_env, tid_body] = z                                            <L 815>
        wp::adj_array_store(var_local_torque_b, var_0, var_1, var_5, adj_local_torque_b, adj_0, adj_1, adj_5);
        // adj: local_torque_b[tid_env, tid_body] = z                                         <L 814>
        wp::adj_array_store(var_local_force_b, var_0, var_1, var_5, adj_local_force_b, adj_0, adj_1, adj_5);
        // adj: local_force_b[tid_env, tid_body] = z                                          <L 813>
        wp::adj_array_store(var_global_force_at_com_w, var_0, var_1, var_5, adj_global_force_at_com_w, adj_0, adj_1, adj_5);
        // adj: global_force_at_com_w[tid_env, tid_body] = z                                  <L 812>
        wp::adj_array_store(var_global_torque_w, var_0, var_1, var_5, adj_global_torque_w, adj_0, adj_1, adj_5);
        // adj: global_torque_w[tid_env, tid_body] = z                                        <L 811>
        wp::adj_array_store(var_global_force_w, var_0, var_1, var_5, adj_global_force_w, adj_0, adj_1, adj_5);
        // adj: global_force_w[tid_env, tid_body] = z                                         <L 810>
        wp::adj_vec_t(var_4, adj_4, adj_5);
        // adj: z = wp.vec3f(0.0)                                                             <L 809>
    }
    wp::adj_address(var_env_mask, var_0, adj_env_mask, adj_0, adj_2);
    // adj: if env_mask[tid_env]:                                                             <L 808>
    // adj: tid_env, tid_body = wp.tid()                                                      <L 807>
    // adj: def reset_wrench_composer_mask(                                                   <L 793>
    return;
}



extern "C" {

// Python CPU entry points
WP_API void reset_wrench_composer_mask_bd82acc5_cpu_forward(
    wp::launch_bounds_t<2> *dim,
    wp_args_reset_wrench_composer_mask_bd82acc5 *_wp_args)
{
    wp::tile_shared_storage_t tile_mem;
#if defined(WP_ENABLE_TILES_IN_STACK_MEMORY)
    wp::shared_tile_storage = &tile_mem;
#endif

    for (size_t task_index = 0; task_index < dim->size; ++task_index)
    {
        reset_wrench_composer_mask_bd82acc5_cpu_kernel_forward(*dim, task_index, _wp_args);
    }
}

} // extern C



extern "C" {

WP_API void reset_wrench_composer_mask_bd82acc5_cpu_backward(
    wp::launch_bounds_t<2> *dim,
    wp_args_reset_wrench_composer_mask_bd82acc5 *_wp_args,
    wp_args_reset_wrench_composer_mask_bd82acc5 *_wp_adj_args)
{
    wp::tile_shared_storage_t tile_mem;
#if defined(WP_ENABLE_TILES_IN_STACK_MEMORY)
    wp::shared_tile_storage = &tile_mem;
#endif

    for (size_t task_index = 0; task_index < dim->size; ++task_index)
    {
        reset_wrench_composer_mask_bd82acc5_cpu_kernel_backward(*dim, task_index, _wp_args, _wp_adj_args);
    }
}

} // extern C

struct wp_args_normalize_image_uint8_c55e8d3c {
    wp::array_t<wp::uint8> src;
    wp::array_t<wp::float32> mean;
    wp::array_t<wp::float32> out;
    wp::int32 channel_dim;
};


void normalize_image_uint8_c55e8d3c_cpu_kernel_forward(
    wp::launch_bounds_t<4> dim,
    size_t task_index,
    wp_args_normalize_image_uint8_c55e8d3c *_wp_args)
{
    //---------
    // argument vars
    wp::array_t<wp::uint8> var_src = _wp_args->src;
    wp::array_t<wp::float32> var_mean = _wp_args->mean;
    wp::array_t<wp::float32> var_out = _wp_args->out;
    wp::int32 var_channel_dim = _wp_args->channel_dim;
    //---------
    // primal vars
    wp::int32 var_0;
    wp::int32 var_1;
    wp::int32 var_2;
    wp::int32 var_3;
    const wp::int32 var_4 = 1;
    bool var_5;
    wp::int32 var_6;
    wp::int32 var_7;
    wp::int32 var_8;
    wp::uint8* var_9;
    wp::float32 var_10;
    wp::uint8 var_11;
    const wp::float32 var_12 = 255.0;
    wp::float32 var_13;
    wp::float32* var_14;
    wp::float32 var_15;
    wp::float32 var_16;
    //---------
    // forward
    // def normalize_image_uint8(                                                             <L 723>
    // b, d1, d2, d3 = wp.tid()                                                               <L 745>
    builtin_tid4d(var_0, var_1, var_2, var_3);
    // if channel_dim == 1:                                                                   <L 746>
    var_5 = (var_channel_dim == var_4);
    if (var_5) {
        // c = d1                                                                             <L 747>
        var_6 = wp::copy(var_1);
    }
    if (!var_5) {
        // c = d3                                                                             <L 749>
        var_7 = wp::copy(var_3);
    }
    var_8 = wp::where(var_5, var_6, var_7);
    // out[b, d1, d2, d3] = wp.float32(src[b, d1, d2, d3]) / 255.0 - mean[b, c]               <L 750>
    var_9 = wp::address(var_src, var_0, var_1, var_2, var_3);
    var_11 = wp::load(var_9);
    var_10 = wp::float32(var_11);
    var_13 = wp::div(var_10, var_12);
    var_14 = wp::address(var_mean, var_0, var_8);
    var_16 = wp::load(var_14);
    var_15 = wp::sub(var_13, var_16);
    wp::array_store(var_out, var_0, var_1, var_2, var_3, var_15);
}



extern "C" {

// Python CPU entry points
WP_API void normalize_image_uint8_c55e8d3c_cpu_forward(
    wp::launch_bounds_t<4> *dim,
    wp_args_normalize_image_uint8_c55e8d3c *_wp_args)
{
    wp::tile_shared_storage_t tile_mem;
#if defined(WP_ENABLE_TILES_IN_STACK_MEMORY)
    wp::shared_tile_storage = &tile_mem;
#endif

    for (size_t task_index = 0; task_index < dim->size; ++task_index)
    {
        normalize_image_uint8_c55e8d3c_cpu_kernel_forward(*dim, task_index, _wp_args);
    }
}

} // extern C

struct wp_args_reshape_tiled_image_c848d4a1 {
    wp::array_t<wp::float32> tiled_image_buffer;
    wp::array_t<wp::float32> batched_image;
    wp::int32 image_height;
    wp::int32 image_width;
    wp::int32 num_channels;
    wp::int32 num_tiles_x;
};


void reshape_tiled_image_c848d4a1_cpu_kernel_forward(
    wp::launch_bounds_t<3> dim,
    size_t task_index,
    wp_args_reshape_tiled_image_c848d4a1 *_wp_args)
{
    //---------
    // argument vars
    wp::array_t<wp::float32> var_tiled_image_buffer = _wp_args->tiled_image_buffer;
    wp::array_t<wp::float32> var_batched_image = _wp_args->batched_image;
    wp::int32 var_image_height = _wp_args->image_height;
    wp::int32 var_image_width = _wp_args->image_width;
    wp::int32 var_num_channels = _wp_args->num_channels;
    wp::int32 var_num_tiles_x = _wp_args->num_tiles_x;
    //---------
    // primal vars
    wp::int32 var_0;
    wp::int32 var_1;
    wp::int32 var_2;
    wp::int32 var_3;
    wp::int32 var_4;
    wp::int32 var_5;
    wp::int32 var_6;
    wp::int32 var_7;
    wp::int32 var_8;
    wp::range_t var_9;
    wp::int32 var_10;
    wp::float32* var_11;
    wp::float32 var_12;
    wp::float32 var_13;
    //---------
    // forward
    // def reshape_tiled_image(                                                               <L 1>
    // camera_id, height_id, width_id = wp.tid()                                              <L 30>
    builtin_tid3d(var_0, var_1, var_2);
    // tile_x_id = camera_id % num_tiles_x                                                    <L 33>
    var_3 = wp::mod(var_0, var_num_tiles_x);
    // tile_y_id = camera_id // num_tiles_x                                                   <L 34>
    var_4 = wp::floordiv(var_0, var_num_tiles_x);
    // row = image_height * tile_y_id + height_id                                             <L 36>
    var_5 = wp::mul(var_image_height, var_4);
    var_6 = wp::add(var_5, var_1);
    // col = image_width * tile_x_id + width_id                                               <L 37>
    var_7 = wp::mul(var_image_width, var_3);
    var_8 = wp::add(var_7, var_2);
    // for i in range(num_channels):                                                          <L 40>
    var_9 = wp::range(var_num_channels);
    start_for_0:;
        if (iter_cmp(var_9) == 0) goto end_for_0;
        var_10 = wp::iter_next(var_9);
        // batched_image[camera_id, height_id, width_id, i] = batched_image.dtype(tiled_image_buffer[row, col, i])       <L 41>
        var_11 = wp::address(var_tiled_image_buffer, var_6, var_8, var_10);
        var_13 = wp::load(var_11);
        var_12 = wp::float32(var_13);
        wp::array_store(var_batched_image, var_0, var_1, var_2, var_10, var_12);
        goto start_for_0;
    end_for_0:;
}



extern "C" {

// Python CPU entry points
WP_API void reshape_tiled_image_c848d4a1_cpu_forward(
    wp::launch_bounds_t<3> *dim,
    wp_args_reshape_tiled_image_c848d4a1 *_wp_args)
{
    wp::tile_shared_storage_t tile_mem;
#if defined(WP_ENABLE_TILES_IN_STACK_MEMORY)
    wp::shared_tile_storage = &tile_mem;
#endif

    for (size_t task_index = 0; task_index < dim->size; ++task_index)
    {
        reshape_tiled_image_c848d4a1_cpu_kernel_forward(*dim, task_index, _wp_args);
    }
}

} // extern C

struct wp_args_raycast_static_meshes_kernel_ccfc0303 {
    wp::array_t<wp::uint64> mesh;
    wp::array_t<wp::vec_t<3, wp::float32>> ray_starts;
    wp::array_t<wp::vec_t<3, wp::float32>> ray_directions;
    wp::array_t<wp::vec_t<3, wp::float32>> ray_hits;
    wp::array_t<wp::float32> ray_distance;
    wp::array_t<wp::vec_t<3, wp::float32>> ray_normal;
    wp::array_t<wp::int32> ray_face_id;
    wp::array_t<wp::int16> ray_mesh_id;
    wp::float32 max_dist;
    wp::int32 return_normal;
    wp::int32 return_face_id;
    wp::int32 return_mesh_id;
};


void raycast_static_meshes_kernel_ccfc0303_cpu_kernel_forward(
    wp::launch_bounds_t<3> dim,
    size_t task_index,
    wp_args_raycast_static_meshes_kernel_ccfc0303 *_wp_args)
{
    //---------
    // argument vars
    wp::array_t<wp::uint64> var_mesh = _wp_args->mesh;
    wp::array_t<wp::vec_t<3, wp::float32>> var_ray_starts = _wp_args->ray_starts;
    wp::array_t<wp::vec_t<3, wp::float32>> var_ray_directions = _wp_args->ray_directions;
    wp::array_t<wp::vec_t<3, wp::float32>> var_ray_hits = _wp_args->ray_hits;
    wp::array_t<wp::float32> var_ray_distance = _wp_args->ray_distance;
    wp::array_t<wp::vec_t<3, wp::float32>> var_ray_normal = _wp_args->ray_normal;
    wp::array_t<wp::int32> var_ray_face_id = _wp_args->ray_face_id;
    wp::array_t<wp::int16> var_ray_mesh_id = _wp_args->ray_mesh_id;
    wp::float32 var_max_dist = _wp_args->max_dist;
    wp::int32 var_return_normal = _wp_args->return_normal;
    wp::int32 var_return_face_id = _wp_args->return_face_id;
    wp::int32 var_return_mesh_id = _wp_args->return_mesh_id;
    //---------
    // primal vars
    wp::int32 var_0;
    wp::int32 var_1;
    wp::int32 var_2;
    wp::vec_t<3, wp::float32>* var_3;
    wp::vec_t<3, wp::float32> var_4;
    wp::vec_t<3, wp::float32> var_5;
    wp::vec_t<3, wp::float32>* var_6;
    wp::vec_t<3, wp::float32> var_7;
    wp::vec_t<3, wp::float32> var_8;
    wp::uint64* var_9;
    wp::mesh_query_ray_t var_10;
    const wp::int32 var_11 = -1;
    wp::uint64 var_12;
    bool* var_13;
    bool var_14;
    wp::float32* var_15;
    wp::float32 var_16;
    wp::float32 var_17;
    wp::float32* var_18;
    wp::float32* var_19;
    bool var_20;
    wp::float32 var_21;
    wp::float32 var_22;
    wp::float32* var_23;
    wp::vec_t<3, wp::float32> var_24;
    wp::float32 var_25;
    wp::vec_t<3, wp::float32> var_26;
    const wp::int32 var_27 = 1;
    bool var_28;
    wp::vec_t<3, wp::float32>* var_29;
    wp::vec_t<3, wp::float32> var_30;
    const wp::int32 var_31 = 1;
    bool var_32;
    wp::int32* var_33;
    wp::int32 var_34;
    const wp::int32 var_35 = 1;
    bool var_36;
    wp::int16 var_37;
    bool var_38;
    //---------
    // forward
    // def raycast_static_meshes_kernel(                                                      <L 143>
    // tid_mesh_id, tid_env, tid_ray = wp.tid()                                               <L 203>
    builtin_tid3d(var_0, var_1, var_2);
    // direction = ray_directions[tid_env, tid_ray]                                           <L 205>
    var_3 = wp::address(var_ray_directions, var_1, var_2);
    var_5 = wp::load(var_3);
    var_4 = wp::copy(var_5);
    // start_pos = ray_starts[tid_env, tid_ray]                                               <L 206>
    var_6 = wp::address(var_ray_starts, var_1, var_2);
    var_8 = wp::load(var_6);
    var_7 = wp::copy(var_8);
    // mesh_query_ray_t = wp.mesh_query_ray(mesh[tid_env, tid_mesh_id], start_pos, direction, max_dist)       <L 209>
    var_9 = wp::address(var_mesh, var_1, var_0);
    var_12 = wp::load(var_9);
    var_10 = wp::mesh_query_ray(var_12, var_7, var_4, var_max_dist, var_11);
    // if mesh_query_ray_t.result:                                                            <L 212>
    var_13 = &((var_10).result);
    var_14 = wp::load(var_13);
    if (var_14) {
        // wp.atomic_min(ray_distance, tid_env, tid_ray, mesh_query_ray_t.t)                  <L 213>
        var_15 = &((var_10).t);
        var_17 = wp::load(var_15);
        var_16 = wp::atomic_min(var_ray_distance, var_1, var_2, var_17);
        // if mesh_query_ray_t.t == ray_distance[tid_env, tid_ray]:                           <L 219>
        var_18 = &((var_10).t);
        var_19 = wp::address(var_ray_distance, var_1, var_2);
        var_21 = wp::load(var_18);
        var_22 = wp::load(var_19);
        var_20 = (var_21 == var_22);
        if (var_20) {
            // ray_hits[tid_env, tid_ray] = start_pos + mesh_query_ray_t.t * direction        <L 221>
            var_23 = &((var_10).t);
            var_25 = wp::load(var_23);
            var_24 = wp::mul(var_25, var_4);
            var_26 = wp::add(var_7, var_24);
            wp::array_store(var_ray_hits, var_1, var_2, var_26);
            // if return_normal == 1:                                                         <L 224>
            var_28 = (var_return_normal == var_27);
            if (var_28) {
                // ray_normal[tid_env, tid_ray] = mesh_query_ray_t.normal                     <L 225>
                var_29 = &((var_10).normal);
                var_30 = wp::load(var_29);
                wp::array_store(var_ray_normal, var_1, var_2, var_30);
            }
            // if return_face_id == 1:                                                        <L 226>
            var_32 = (var_return_face_id == var_31);
            if (var_32) {
                // ray_face_id[tid_env, tid_ray] = mesh_query_ray_t.face                      <L 227>
                var_33 = &((var_10).face);
                var_34 = wp::load(var_33);
                wp::array_store(var_ray_face_id, var_1, var_2, var_34);
            }
            // if return_mesh_id == 1:                                                        <L 228>
            var_36 = (var_return_mesh_id == var_35);
            if (var_36) {
                // ray_mesh_id[tid_env, tid_ray] = wp.int16(tid_mesh_id)                      <L 229>
                var_37 = wp::int16(var_0);
                wp::array_store(var_ray_mesh_id, var_1, var_2, var_37);
            }
        }
    }
    var_38 = wp::load(var_13);
}



extern "C" {

// Python CPU entry points
WP_API void raycast_static_meshes_kernel_ccfc0303_cpu_forward(
    wp::launch_bounds_t<3> *dim,
    wp_args_raycast_static_meshes_kernel_ccfc0303 *_wp_args)
{
    wp::tile_shared_storage_t tile_mem;
#if defined(WP_ENABLE_TILES_IN_STACK_MEMORY)
    wp::shared_tile_storage = &tile_mem;
#endif

    for (size_t task_index = 0; task_index < dim->size; ++task_index)
    {
        raycast_static_meshes_kernel_ccfc0303_cpu_kernel_forward(*dim, task_index, _wp_args);
    }
}

} // extern C

struct wp_args_reshape_tiled_image_d99be20f {
    wp::array_t<wp::uint32> tiled_image_buffer;
    wp::array_t<wp::uint32> batched_image;
    wp::int32 image_height;
    wp::int32 image_width;
    wp::int32 num_channels;
    wp::int32 num_tiles_x;
};


void reshape_tiled_image_d99be20f_cpu_kernel_forward(
    wp::launch_bounds_t<3> dim,
    size_t task_index,
    wp_args_reshape_tiled_image_d99be20f *_wp_args)
{
    //---------
    // argument vars
    wp::array_t<wp::uint32> var_tiled_image_buffer = _wp_args->tiled_image_buffer;
    wp::array_t<wp::uint32> var_batched_image = _wp_args->batched_image;
    wp::int32 var_image_height = _wp_args->image_height;
    wp::int32 var_image_width = _wp_args->image_width;
    wp::int32 var_num_channels = _wp_args->num_channels;
    wp::int32 var_num_tiles_x = _wp_args->num_tiles_x;
    //---------
    // primal vars
    wp::int32 var_0;
    wp::int32 var_1;
    wp::int32 var_2;
    wp::int32 var_3;
    wp::int32 var_4;
    wp::int32 var_5;
    wp::int32 var_6;
    wp::int32 var_7;
    wp::int32 var_8;
    wp::range_t var_9;
    wp::int32 var_10;
    wp::uint32* var_11;
    wp::uint32 var_12;
    wp::uint32 var_13;
    //---------
    // forward
    // def reshape_tiled_image(                                                               <L 1>
    // camera_id, height_id, width_id = wp.tid()                                              <L 30>
    builtin_tid3d(var_0, var_1, var_2);
    // tile_x_id = camera_id % num_tiles_x                                                    <L 33>
    var_3 = wp::mod(var_0, var_num_tiles_x);
    // tile_y_id = camera_id // num_tiles_x                                                   <L 34>
    var_4 = wp::floordiv(var_0, var_num_tiles_x);
    // row = image_height * tile_y_id + height_id                                             <L 36>
    var_5 = wp::mul(var_image_height, var_4);
    var_6 = wp::add(var_5, var_1);
    // col = image_width * tile_x_id + width_id                                               <L 37>
    var_7 = wp::mul(var_image_width, var_3);
    var_8 = wp::add(var_7, var_2);
    // for i in range(num_channels):                                                          <L 40>
    var_9 = wp::range(var_num_channels);
    start_for_0:;
        if (iter_cmp(var_9) == 0) goto end_for_0;
        var_10 = wp::iter_next(var_9);
        // batched_image[camera_id, height_id, width_id, i] = batched_image.dtype(tiled_image_buffer[row, col, i])       <L 41>
        var_11 = wp::address(var_tiled_image_buffer, var_6, var_8, var_10);
        var_13 = wp::load(var_11);
        var_12 = wp::uint32(var_13);
        wp::array_store(var_batched_image, var_0, var_1, var_2, var_10, var_12);
        goto start_for_0;
    end_for_0:;
}



extern "C" {

// Python CPU entry points
WP_API void reshape_tiled_image_d99be20f_cpu_forward(
    wp::launch_bounds_t<3> *dim,
    wp_args_reshape_tiled_image_d99be20f *_wp_args)
{
    wp::tile_shared_storage_t tile_mem;
#if defined(WP_ENABLE_TILES_IN_STACK_MEMORY)
    wp::shared_tile_storage = &tile_mem;
#endif

    for (size_t task_index = 0; task_index < dim->size; ++task_index)
    {
        reshape_tiled_image_d99be20f_cpu_kernel_forward(*dim, task_index, _wp_args);
    }
}

} // extern C

struct wp_args_reset_wrench_composer_index_e5b6717a {
    wp::array_t<wp::int64> env_ids;
    wp::array_t<wp::vec_t<3, wp::float32>> global_force_w;
    wp::array_t<wp::vec_t<3, wp::float32>> global_torque_w;
    wp::array_t<wp::vec_t<3, wp::float32>> global_force_at_com_w;
    wp::array_t<wp::vec_t<3, wp::float32>> local_force_b;
    wp::array_t<wp::vec_t<3, wp::float32>> local_torque_b;
    wp::array_t<wp::vec_t<3, wp::float32>> out_force_b;
    wp::array_t<wp::vec_t<3, wp::float32>> out_torque_b;
};


void reset_wrench_composer_index_e5b6717a_cpu_kernel_forward(
    wp::launch_bounds_t<2> dim,
    size_t task_index,
    wp_args_reset_wrench_composer_index_e5b6717a *_wp_args)
{
    //---------
    // argument vars
    wp::array_t<wp::int64> var_env_ids = _wp_args->env_ids;
    wp::array_t<wp::vec_t<3, wp::float32>> var_global_force_w = _wp_args->global_force_w;
    wp::array_t<wp::vec_t<3, wp::float32>> var_global_torque_w = _wp_args->global_torque_w;
    wp::array_t<wp::vec_t<3, wp::float32>> var_global_force_at_com_w = _wp_args->global_force_at_com_w;
    wp::array_t<wp::vec_t<3, wp::float32>> var_local_force_b = _wp_args->local_force_b;
    wp::array_t<wp::vec_t<3, wp::float32>> var_local_torque_b = _wp_args->local_torque_b;
    wp::array_t<wp::vec_t<3, wp::float32>> var_out_force_b = _wp_args->out_force_b;
    wp::array_t<wp::vec_t<3, wp::float32>> var_out_torque_b = _wp_args->out_torque_b;
    //---------
    // primal vars
    wp::int32 var_0;
    wp::int32 var_1;
    wp::int64* var_2;
    wp::int32 var_3;
    wp::int64 var_4;
    const wp::float32 var_5 = 0.0;
    wp::vec_t<3, wp::float32> var_6;
    //---------
    // forward
    // def reset_wrench_composer_index(                                                       <L 1>
    // tid_env, tid_body = wp.tid()                                                           <L 15>
    builtin_tid2d(var_0, var_1);
    // ei = wp.int32(env_ids[tid_env])                                                        <L 16>
    var_2 = wp::address(var_env_ids, var_0);
    var_4 = wp::load(var_2);
    var_3 = wp::int32(var_4);
    // z = wp.vec3f(0.0)                                                                      <L 17>
    var_6 = wp::vec_t<3, wp::float32>(var_5);
    // global_force_w[ei, tid_body] = z                                                       <L 18>
    wp::array_store(var_global_force_w, var_3, var_1, var_6);
    // global_torque_w[ei, tid_body] = z                                                      <L 19>
    wp::array_store(var_global_torque_w, var_3, var_1, var_6);
    // global_force_at_com_w[ei, tid_body] = z                                                <L 20>
    wp::array_store(var_global_force_at_com_w, var_3, var_1, var_6);
    // local_force_b[ei, tid_body] = z                                                        <L 21>
    wp::array_store(var_local_force_b, var_3, var_1, var_6);
    // local_torque_b[ei, tid_body] = z                                                       <L 22>
    wp::array_store(var_local_torque_b, var_3, var_1, var_6);
    // out_force_b[ei, tid_body] = z                                                          <L 23>
    wp::array_store(var_out_force_b, var_3, var_1, var_6);
    // out_torque_b[ei, tid_body] = z                                                         <L 24>
    wp::array_store(var_out_torque_b, var_3, var_1, var_6);
}



void reset_wrench_composer_index_e5b6717a_cpu_kernel_backward(
    wp::launch_bounds_t<2> dim,
    size_t task_index,
    wp_args_reset_wrench_composer_index_e5b6717a *_wp_args,
    wp_args_reset_wrench_composer_index_e5b6717a *_wp_adj_args)
{
    //---------
    // argument vars
    wp::array_t<wp::int64> var_env_ids = _wp_args->env_ids;
    wp::array_t<wp::vec_t<3, wp::float32>> var_global_force_w = _wp_args->global_force_w;
    wp::array_t<wp::vec_t<3, wp::float32>> var_global_torque_w = _wp_args->global_torque_w;
    wp::array_t<wp::vec_t<3, wp::float32>> var_global_force_at_com_w = _wp_args->global_force_at_com_w;
    wp::array_t<wp::vec_t<3, wp::float32>> var_local_force_b = _wp_args->local_force_b;
    wp::array_t<wp::vec_t<3, wp::float32>> var_local_torque_b = _wp_args->local_torque_b;
    wp::array_t<wp::vec_t<3, wp::float32>> var_out_force_b = _wp_args->out_force_b;
    wp::array_t<wp::vec_t<3, wp::float32>> var_out_torque_b = _wp_args->out_torque_b;
    wp::array_t<wp::int64> adj_env_ids = _wp_adj_args->env_ids;
    wp::array_t<wp::vec_t<3, wp::float32>> adj_global_force_w = _wp_adj_args->global_force_w;
    wp::array_t<wp::vec_t<3, wp::float32>> adj_global_torque_w = _wp_adj_args->global_torque_w;
    wp::array_t<wp::vec_t<3, wp::float32>> adj_global_force_at_com_w = _wp_adj_args->global_force_at_com_w;
    wp::array_t<wp::vec_t<3, wp::float32>> adj_local_force_b = _wp_adj_args->local_force_b;
    wp::array_t<wp::vec_t<3, wp::float32>> adj_local_torque_b = _wp_adj_args->local_torque_b;
    wp::array_t<wp::vec_t<3, wp::float32>> adj_out_force_b = _wp_adj_args->out_force_b;
    wp::array_t<wp::vec_t<3, wp::float32>> adj_out_torque_b = _wp_adj_args->out_torque_b;
    //---------
    // primal vars
    wp::int32 var_0;
    wp::int32 var_1;
    wp::int64* var_2;
    wp::int32 var_3;
    wp::int64 var_4;
    const wp::float32 var_5 = 0.0;
    wp::vec_t<3, wp::float32> var_6;
    //---------
    // dual vars
    wp::int32 adj_0 = {};
    wp::int32 adj_1 = {};
    wp::int64 adj_2 = {};
    wp::int32 adj_3 = {};
    wp::int64 adj_4 = {};
    wp::float32 adj_5 = {};
    wp::vec_t<3, wp::float32> adj_6 = {};
    //---------
    // forward
    // def reset_wrench_composer_index(                                                       <L 1>
    // tid_env, tid_body = wp.tid()                                                           <L 15>
    builtin_tid2d(var_0, var_1);
    // ei = wp.int32(env_ids[tid_env])                                                        <L 16>
    var_2 = wp::address(var_env_ids, var_0);
    var_4 = wp::load(var_2);
    var_3 = wp::int32(var_4);
    // z = wp.vec3f(0.0)                                                                      <L 17>
    var_6 = wp::vec_t<3, wp::float32>(var_5);
    // global_force_w[ei, tid_body] = z                                                       <L 18>
    // wp::array_store(var_global_force_w, var_3, var_1, var_6);
    // global_torque_w[ei, tid_body] = z                                                      <L 19>
    // wp::array_store(var_global_torque_w, var_3, var_1, var_6);
    // global_force_at_com_w[ei, tid_body] = z                                                <L 20>
    // wp::array_store(var_global_force_at_com_w, var_3, var_1, var_6);
    // local_force_b[ei, tid_body] = z                                                        <L 21>
    // wp::array_store(var_local_force_b, var_3, var_1, var_6);
    // local_torque_b[ei, tid_body] = z                                                       <L 22>
    // wp::array_store(var_local_torque_b, var_3, var_1, var_6);
    // out_force_b[ei, tid_body] = z                                                          <L 23>
    // wp::array_store(var_out_force_b, var_3, var_1, var_6);
    // out_torque_b[ei, tid_body] = z                                                         <L 24>
    // wp::array_store(var_out_torque_b, var_3, var_1, var_6);
    //---------
    // reverse
    wp::adj_array_store(var_out_torque_b, var_3, var_1, var_6, adj_out_torque_b, adj_3, adj_1, adj_6);
    // adj: out_torque_b[ei, tid_body] = z                                                    <L 24>
    wp::adj_array_store(var_out_force_b, var_3, var_1, var_6, adj_out_force_b, adj_3, adj_1, adj_6);
    // adj: out_force_b[ei, tid_body] = z                                                     <L 23>
    wp::adj_array_store(var_local_torque_b, var_3, var_1, var_6, adj_local_torque_b, adj_3, adj_1, adj_6);
    // adj: local_torque_b[ei, tid_body] = z                                                  <L 22>
    wp::adj_array_store(var_local_force_b, var_3, var_1, var_6, adj_local_force_b, adj_3, adj_1, adj_6);
    // adj: local_force_b[ei, tid_body] = z                                                   <L 21>
    wp::adj_array_store(var_global_force_at_com_w, var_3, var_1, var_6, adj_global_force_at_com_w, adj_3, adj_1, adj_6);
    // adj: global_force_at_com_w[ei, tid_body] = z                                           <L 20>
    wp::adj_array_store(var_global_torque_w, var_3, var_1, var_6, adj_global_torque_w, adj_3, adj_1, adj_6);
    // adj: global_torque_w[ei, tid_body] = z                                                 <L 19>
    wp::adj_array_store(var_global_force_w, var_3, var_1, var_6, adj_global_force_w, adj_3, adj_1, adj_6);
    // adj: global_force_w[ei, tid_body] = z                                                  <L 18>
    wp::adj_vec_t(var_5, adj_5, adj_6);
    // adj: z = wp.vec3f(0.0)                                                                 <L 17>
    wp::adj_address(var_env_ids, var_0, adj_env_ids, adj_0, adj_2);
    // adj: ei = wp.int32(env_ids[tid_env])                                                   <L 16>
    // adj: tid_env, tid_body = wp.tid()                                                      <L 15>
    // adj: def reset_wrench_composer_index(                                                  <L 1>
    return;
}



extern "C" {

// Python CPU entry points
WP_API void reset_wrench_composer_index_e5b6717a_cpu_forward(
    wp::launch_bounds_t<2> *dim,
    wp_args_reset_wrench_composer_index_e5b6717a *_wp_args)
{
    wp::tile_shared_storage_t tile_mem;
#if defined(WP_ENABLE_TILES_IN_STACK_MEMORY)
    wp::shared_tile_storage = &tile_mem;
#endif

    for (size_t task_index = 0; task_index < dim->size; ++task_index)
    {
        reset_wrench_composer_index_e5b6717a_cpu_kernel_forward(*dim, task_index, _wp_args);
    }
}

} // extern C



extern "C" {

WP_API void reset_wrench_composer_index_e5b6717a_cpu_backward(
    wp::launch_bounds_t<2> *dim,
    wp_args_reset_wrench_composer_index_e5b6717a *_wp_args,
    wp_args_reset_wrench_composer_index_e5b6717a *_wp_adj_args)
{
    wp::tile_shared_storage_t tile_mem;
#if defined(WP_ENABLE_TILES_IN_STACK_MEMORY)
    wp::shared_tile_storage = &tile_mem;
#endif

    for (size_t task_index = 0; task_index < dim->size; ++task_index)
    {
        reset_wrench_composer_index_e5b6717a_cpu_kernel_backward(*dim, task_index, _wp_args, _wp_adj_args);
    }
}

} // extern C

struct wp_args_add_forces_to_dual_buffers_mask_e7b2db0e {
    wp::array_t<bool> env_mask;
    wp::array_t<bool> body_mask;
    wp::array_t<wp::vec_t<3, wp::float32>> forces;
    wp::array_t<wp::vec_t<3, wp::float32>> torques;
    wp::array_t<wp::vec_t<3, wp::float32>> positions;
    wp::array_t<wp::vec_t<3, wp::float32>> global_force_w;
    wp::array_t<wp::vec_t<3, wp::float32>> global_torque_w;
    wp::array_t<wp::vec_t<3, wp::float32>> global_force_at_com_w;
    wp::array_t<wp::vec_t<3, wp::float32>> local_force_b;
    wp::array_t<wp::vec_t<3, wp::float32>> local_torque_b;
    bool is_global;
};


void add_forces_to_dual_buffers_mask_e7b2db0e_cpu_kernel_forward(
    wp::launch_bounds_t<2> dim,
    size_t task_index,
    wp_args_add_forces_to_dual_buffers_mask_e7b2db0e *_wp_args)
{
    //---------
    // argument vars
    wp::array_t<bool> var_env_mask = _wp_args->env_mask;
    wp::array_t<bool> var_body_mask = _wp_args->body_mask;
    wp::array_t<wp::vec_t<3, wp::float32>> var_forces = _wp_args->forces;
    wp::array_t<wp::vec_t<3, wp::float32>> var_torques = _wp_args->torques;
    wp::array_t<wp::vec_t<3, wp::float32>> var_positions = _wp_args->positions;
    wp::array_t<wp::vec_t<3, wp::float32>> var_global_force_w = _wp_args->global_force_w;
    wp::array_t<wp::vec_t<3, wp::float32>> var_global_torque_w = _wp_args->global_torque_w;
    wp::array_t<wp::vec_t<3, wp::float32>> var_global_force_at_com_w = _wp_args->global_force_at_com_w;
    wp::array_t<wp::vec_t<3, wp::float32>> var_local_force_b = _wp_args->local_force_b;
    wp::array_t<wp::vec_t<3, wp::float32>> var_local_torque_b = _wp_args->local_torque_b;
    bool var_is_global = _wp_args->is_global;
    //---------
    // primal vars
    wp::int32 var_0;
    wp::int32 var_1;
    bool var_2;
    bool* var_3;
    bool var_4;
    bool* var_5;
    bool var_6;
    wp::vec_t<3, wp::float32>* var_7;
    wp::vec_t<3, wp::float32>* var_8;
    wp::vec_t<3, wp::float32> var_9;
    wp::vec_t<3, wp::float32> var_10;
    wp::vec_t<3, wp::float32> var_11;
    wp::vec_t<3, wp::float32>* var_12;
    wp::vec_t<3, wp::float32>* var_13;
    wp::vec_t<3, wp::float32>* var_14;
    wp::vec_t<3, wp::float32> var_15;
    wp::vec_t<3, wp::float32> var_16;
    wp::vec_t<3, wp::float32> var_17;
    wp::vec_t<3, wp::float32> var_18;
    wp::vec_t<3, wp::float32> var_19;
    wp::vec_t<3, wp::float32>* var_20;
    wp::vec_t<3, wp::float32>* var_21;
    wp::vec_t<3, wp::float32> var_22;
    wp::vec_t<3, wp::float32> var_23;
    wp::vec_t<3, wp::float32> var_24;
    wp::vec_t<3, wp::float32>* var_25;
    wp::vec_t<3, wp::float32>* var_26;
    wp::vec_t<3, wp::float32> var_27;
    wp::vec_t<3, wp::float32> var_28;
    wp::vec_t<3, wp::float32> var_29;
    wp::vec_t<3, wp::float32>* var_30;
    wp::vec_t<3, wp::float32>* var_31;
    wp::vec_t<3, wp::float32> var_32;
    wp::vec_t<3, wp::float32> var_33;
    wp::vec_t<3, wp::float32> var_34;
    wp::vec_t<3, wp::float32>* var_35;
    wp::vec_t<3, wp::float32>* var_36;
    wp::vec_t<3, wp::float32>* var_37;
    wp::vec_t<3, wp::float32> var_38;
    wp::vec_t<3, wp::float32> var_39;
    wp::vec_t<3, wp::float32> var_40;
    wp::vec_t<3, wp::float32> var_41;
    wp::vec_t<3, wp::float32> var_42;
    wp::vec_t<3, wp::float32>* var_43;
    wp::vec_t<3, wp::float32>* var_44;
    wp::vec_t<3, wp::float32> var_45;
    wp::vec_t<3, wp::float32> var_46;
    wp::vec_t<3, wp::float32> var_47;
    //---------
    // forward
    // def add_forces_to_dual_buffers_mask(                                                   <L 555>
    // tid_env, tid_body = wp.tid()                                                           <L 574>
    builtin_tid2d(var_0, var_1);
    // if env_mask[tid_env] and body_mask[tid_body]:                                          <L 576>
    var_3 = wp::address(var_env_mask, var_0);
    var_4 = wp::load(var_3);
    var_2 = var_4;
    if (var_2) {
        var_5 = wp::address(var_body_mask, var_1);
        var_6 = wp::load(var_5);
        var_2 = var_2 && var_6;
    }
    if (var_2) {
        // if is_global:                                                                      <L 577>
        if (var_is_global) {
            // if forces:                                                                     <L 578>
            if (var_forces) {
                // if positions:                                                              <L 579>
                if (var_positions) {
                    // global_force_w[tid_env, tid_body] = global_force_w[tid_env, tid_body] + forces[tid_env, tid_body]       <L 580>
                    var_7 = wp::address(var_global_force_w, var_0, var_1);
                    var_8 = wp::address(var_forces, var_0, var_1);
                    var_10 = wp::load(var_7);
                    var_11 = wp::load(var_8);
                    var_9 = wp::add(var_10, var_11);
                    wp::array_store(var_global_force_w, var_0, var_1, var_9);
                    // global_torque_w[tid_env, tid_body] = global_torque_w[tid_env, tid_body] + wp.cross(       <L 581>
                    var_12 = wp::address(var_global_torque_w, var_0, var_1);
                    // positions[tid_env, tid_body], forces[tid_env, tid_body]                <L 582>
                    var_13 = wp::address(var_positions, var_0, var_1);
                    var_14 = wp::address(var_forces, var_0, var_1);
                    var_16 = wp::load(var_13);
                    var_17 = wp::load(var_14);
                    var_15 = wp::cross(var_16, var_17);
                    var_19 = wp::load(var_12);
                    var_18 = wp::add(var_19, var_15);
                    // global_torque_w[tid_env, tid_body] = global_torque_w[tid_env, tid_body] + wp.cross(       <L 581>
                    wp::array_store(var_global_torque_w, var_0, var_1, var_18);
                }
                if (!var_positions) {
                    // global_force_at_com_w[tid_env, tid_body] = (                           <L 585>
                    // global_force_at_com_w[tid_env, tid_body] + forces[tid_env, tid_body]       <L 586>
                    var_20 = wp::address(var_global_force_at_com_w, var_0, var_1);
                    var_21 = wp::address(var_forces, var_0, var_1);
                    var_23 = wp::load(var_20);
                    var_24 = wp::load(var_21);
                    var_22 = wp::add(var_23, var_24);
                    // global_force_at_com_w[tid_env, tid_body] = (                           <L 585>
                    wp::array_store(var_global_force_at_com_w, var_0, var_1, var_22);
                }
            }
            // if torques:                                                                    <L 588>
            if (var_torques) {
                // global_torque_w[tid_env, tid_body] = global_torque_w[tid_env, tid_body] + torques[tid_env, tid_body]       <L 589>
                var_25 = wp::address(var_global_torque_w, var_0, var_1);
                var_26 = wp::address(var_torques, var_0, var_1);
                var_28 = wp::load(var_25);
                var_29 = wp::load(var_26);
                var_27 = wp::add(var_28, var_29);
                wp::array_store(var_global_torque_w, var_0, var_1, var_27);
            }
        }
        if (!var_is_global) {
            // if forces:                                                                     <L 591>
            if (var_forces) {
                // local_force_b[tid_env, tid_body] = local_force_b[tid_env, tid_body] + forces[tid_env, tid_body]       <L 592>
                var_30 = wp::address(var_local_force_b, var_0, var_1);
                var_31 = wp::address(var_forces, var_0, var_1);
                var_33 = wp::load(var_30);
                var_34 = wp::load(var_31);
                var_32 = wp::add(var_33, var_34);
                wp::array_store(var_local_force_b, var_0, var_1, var_32);
                // if positions:                                                              <L 593>
                if (var_positions) {
                    // local_torque_b[tid_env, tid_body] = local_torque_b[tid_env, tid_body] + wp.cross(       <L 594>
                    var_35 = wp::address(var_local_torque_b, var_0, var_1);
                    // positions[tid_env, tid_body], forces[tid_env, tid_body]                <L 595>
                    var_36 = wp::address(var_positions, var_0, var_1);
                    var_37 = wp::address(var_forces, var_0, var_1);
                    var_39 = wp::load(var_36);
                    var_40 = wp::load(var_37);
                    var_38 = wp::cross(var_39, var_40);
                    var_42 = wp::load(var_35);
                    var_41 = wp::add(var_42, var_38);
                    // local_torque_b[tid_env, tid_body] = local_torque_b[tid_env, tid_body] + wp.cross(       <L 594>
                    wp::array_store(var_local_torque_b, var_0, var_1, var_41);
                }
            }
            // if torques:                                                                    <L 597>
            if (var_torques) {
                // local_torque_b[tid_env, tid_body] = local_torque_b[tid_env, tid_body] + torques[tid_env, tid_body]       <L 598>
                var_43 = wp::address(var_local_torque_b, var_0, var_1);
                var_44 = wp::address(var_torques, var_0, var_1);
                var_46 = wp::load(var_43);
                var_47 = wp::load(var_44);
                var_45 = wp::add(var_46, var_47);
                wp::array_store(var_local_torque_b, var_0, var_1, var_45);
            }
        }
    }
}



void add_forces_to_dual_buffers_mask_e7b2db0e_cpu_kernel_backward(
    wp::launch_bounds_t<2> dim,
    size_t task_index,
    wp_args_add_forces_to_dual_buffers_mask_e7b2db0e *_wp_args,
    wp_args_add_forces_to_dual_buffers_mask_e7b2db0e *_wp_adj_args)
{
    //---------
    // argument vars
    wp::array_t<bool> var_env_mask = _wp_args->env_mask;
    wp::array_t<bool> var_body_mask = _wp_args->body_mask;
    wp::array_t<wp::vec_t<3, wp::float32>> var_forces = _wp_args->forces;
    wp::array_t<wp::vec_t<3, wp::float32>> var_torques = _wp_args->torques;
    wp::array_t<wp::vec_t<3, wp::float32>> var_positions = _wp_args->positions;
    wp::array_t<wp::vec_t<3, wp::float32>> var_global_force_w = _wp_args->global_force_w;
    wp::array_t<wp::vec_t<3, wp::float32>> var_global_torque_w = _wp_args->global_torque_w;
    wp::array_t<wp::vec_t<3, wp::float32>> var_global_force_at_com_w = _wp_args->global_force_at_com_w;
    wp::array_t<wp::vec_t<3, wp::float32>> var_local_force_b = _wp_args->local_force_b;
    wp::array_t<wp::vec_t<3, wp::float32>> var_local_torque_b = _wp_args->local_torque_b;
    bool var_is_global = _wp_args->is_global;
    wp::array_t<bool> adj_env_mask = _wp_adj_args->env_mask;
    wp::array_t<bool> adj_body_mask = _wp_adj_args->body_mask;
    wp::array_t<wp::vec_t<3, wp::float32>> adj_forces = _wp_adj_args->forces;
    wp::array_t<wp::vec_t<3, wp::float32>> adj_torques = _wp_adj_args->torques;
    wp::array_t<wp::vec_t<3, wp::float32>> adj_positions = _wp_adj_args->positions;
    wp::array_t<wp::vec_t<3, wp::float32>> adj_global_force_w = _wp_adj_args->global_force_w;
    wp::array_t<wp::vec_t<3, wp::float32>> adj_global_torque_w = _wp_adj_args->global_torque_w;
    wp::array_t<wp::vec_t<3, wp::float32>> adj_global_force_at_com_w = _wp_adj_args->global_force_at_com_w;
    wp::array_t<wp::vec_t<3, wp::float32>> adj_local_force_b = _wp_adj_args->local_force_b;
    wp::array_t<wp::vec_t<3, wp::float32>> adj_local_torque_b = _wp_adj_args->local_torque_b;
    bool adj_is_global = _wp_adj_args->is_global;
    //---------
    // primal vars
    wp::int32 var_0;
    wp::int32 var_1;
    bool var_2;
    bool* var_3;
    bool var_4;
    bool* var_5;
    bool var_6;
    wp::vec_t<3, wp::float32>* var_7;
    wp::vec_t<3, wp::float32>* var_8;
    wp::vec_t<3, wp::float32> var_9;
    wp::vec_t<3, wp::float32> var_10;
    wp::vec_t<3, wp::float32> var_11;
    wp::vec_t<3, wp::float32>* var_12;
    wp::vec_t<3, wp::float32>* var_13;
    wp::vec_t<3, wp::float32>* var_14;
    wp::vec_t<3, wp::float32> var_15;
    wp::vec_t<3, wp::float32> var_16;
    wp::vec_t<3, wp::float32> var_17;
    wp::vec_t<3, wp::float32> var_18;
    wp::vec_t<3, wp::float32> var_19;
    wp::vec_t<3, wp::float32>* var_20;
    wp::vec_t<3, wp::float32>* var_21;
    wp::vec_t<3, wp::float32> var_22;
    wp::vec_t<3, wp::float32> var_23;
    wp::vec_t<3, wp::float32> var_24;
    wp::vec_t<3, wp::float32>* var_25;
    wp::vec_t<3, wp::float32>* var_26;
    wp::vec_t<3, wp::float32> var_27;
    wp::vec_t<3, wp::float32> var_28;
    wp::vec_t<3, wp::float32> var_29;
    wp::vec_t<3, wp::float32>* var_30;
    wp::vec_t<3, wp::float32>* var_31;
    wp::vec_t<3, wp::float32> var_32;
    wp::vec_t<3, wp::float32> var_33;
    wp::vec_t<3, wp::float32> var_34;
    wp::vec_t<3, wp::float32>* var_35;
    wp::vec_t<3, wp::float32>* var_36;
    wp::vec_t<3, wp::float32>* var_37;
    wp::vec_t<3, wp::float32> var_38;
    wp::vec_t<3, wp::float32> var_39;
    wp::vec_t<3, wp::float32> var_40;
    wp::vec_t<3, wp::float32> var_41;
    wp::vec_t<3, wp::float32> var_42;
    wp::vec_t<3, wp::float32>* var_43;
    wp::vec_t<3, wp::float32>* var_44;
    wp::vec_t<3, wp::float32> var_45;
    wp::vec_t<3, wp::float32> var_46;
    wp::vec_t<3, wp::float32> var_47;
    //---------
    // dual vars
    wp::int32 adj_0 = {};
    wp::int32 adj_1 = {};
    bool adj_2 = {};
    bool adj_3 = {};
    bool adj_4 = {};
    bool adj_5 = {};
    bool adj_6 = {};
    wp::vec_t<3, wp::float32> adj_7 = {};
    wp::vec_t<3, wp::float32> adj_8 = {};
    wp::vec_t<3, wp::float32> adj_9 = {};
    wp::vec_t<3, wp::float32> adj_10 = {};
    wp::vec_t<3, wp::float32> adj_11 = {};
    wp::vec_t<3, wp::float32> adj_12 = {};
    wp::vec_t<3, wp::float32> adj_13 = {};
    wp::vec_t<3, wp::float32> adj_14 = {};
    wp::vec_t<3, wp::float32> adj_15 = {};
    wp::vec_t<3, wp::float32> adj_16 = {};
    wp::vec_t<3, wp::float32> adj_17 = {};
    wp::vec_t<3, wp::float32> adj_18 = {};
    wp::vec_t<3, wp::float32> adj_19 = {};
    wp::vec_t<3, wp::float32> adj_20 = {};
    wp::vec_t<3, wp::float32> adj_21 = {};
    wp::vec_t<3, wp::float32> adj_22 = {};
    wp::vec_t<3, wp::float32> adj_23 = {};
    wp::vec_t<3, wp::float32> adj_24 = {};
    wp::vec_t<3, wp::float32> adj_25 = {};
    wp::vec_t<3, wp::float32> adj_26 = {};
    wp::vec_t<3, wp::float32> adj_27 = {};
    wp::vec_t<3, wp::float32> adj_28 = {};
    wp::vec_t<3, wp::float32> adj_29 = {};
    wp::vec_t<3, wp::float32> adj_30 = {};
    wp::vec_t<3, wp::float32> adj_31 = {};
    wp::vec_t<3, wp::float32> adj_32 = {};
    wp::vec_t<3, wp::float32> adj_33 = {};
    wp::vec_t<3, wp::float32> adj_34 = {};
    wp::vec_t<3, wp::float32> adj_35 = {};
    wp::vec_t<3, wp::float32> adj_36 = {};
    wp::vec_t<3, wp::float32> adj_37 = {};
    wp::vec_t<3, wp::float32> adj_38 = {};
    wp::vec_t<3, wp::float32> adj_39 = {};
    wp::vec_t<3, wp::float32> adj_40 = {};
    wp::vec_t<3, wp::float32> adj_41 = {};
    wp::vec_t<3, wp::float32> adj_42 = {};
    wp::vec_t<3, wp::float32> adj_43 = {};
    wp::vec_t<3, wp::float32> adj_44 = {};
    wp::vec_t<3, wp::float32> adj_45 = {};
    wp::vec_t<3, wp::float32> adj_46 = {};
    wp::vec_t<3, wp::float32> adj_47 = {};
    //---------
    // forward
    // def add_forces_to_dual_buffers_mask(                                                   <L 555>
    // tid_env, tid_body = wp.tid()                                                           <L 574>
    builtin_tid2d(var_0, var_1);
    // if env_mask[tid_env] and body_mask[tid_body]:                                          <L 576>
    var_3 = wp::address(var_env_mask, var_0);
    var_4 = wp::load(var_3);
    var_2 = var_4;
    if (var_2) {
        var_5 = wp::address(var_body_mask, var_1);
        var_6 = wp::load(var_5);
        var_2 = var_2 && var_6;
    }
    if (var_2) {
        // if is_global:                                                                      <L 577>
        if (var_is_global) {
            // if forces:                                                                     <L 578>
            if (var_forces) {
                // if positions:                                                              <L 579>
                if (var_positions) {
                    // global_force_w[tid_env, tid_body] = global_force_w[tid_env, tid_body] + forces[tid_env, tid_body]       <L 580>
                    var_7 = wp::address(var_global_force_w, var_0, var_1);
                    var_8 = wp::address(var_forces, var_0, var_1);
                    var_10 = wp::load(var_7);
                    var_11 = wp::load(var_8);
                    var_9 = wp::add(var_10, var_11);
                    // wp::array_store(var_global_force_w, var_0, var_1, var_9);
                    // global_torque_w[tid_env, tid_body] = global_torque_w[tid_env, tid_body] + wp.cross(       <L 581>
                    var_12 = wp::address(var_global_torque_w, var_0, var_1);
                    // positions[tid_env, tid_body], forces[tid_env, tid_body]                <L 582>
                    var_13 = wp::address(var_positions, var_0, var_1);
                    var_14 = wp::address(var_forces, var_0, var_1);
                    var_16 = wp::load(var_13);
                    var_17 = wp::load(var_14);
                    var_15 = wp::cross(var_16, var_17);
                    var_19 = wp::load(var_12);
                    var_18 = wp::add(var_19, var_15);
                    // global_torque_w[tid_env, tid_body] = global_torque_w[tid_env, tid_body] + wp.cross(       <L 581>
                    // wp::array_store(var_global_torque_w, var_0, var_1, var_18);
                }
                if (!var_positions) {
                    // global_force_at_com_w[tid_env, tid_body] = (                           <L 585>
                    // global_force_at_com_w[tid_env, tid_body] + forces[tid_env, tid_body]       <L 586>
                    var_20 = wp::address(var_global_force_at_com_w, var_0, var_1);
                    var_21 = wp::address(var_forces, var_0, var_1);
                    var_23 = wp::load(var_20);
                    var_24 = wp::load(var_21);
                    var_22 = wp::add(var_23, var_24);
                    // global_force_at_com_w[tid_env, tid_body] = (                           <L 585>
                    // wp::array_store(var_global_force_at_com_w, var_0, var_1, var_22);
                }
            }
            // if torques:                                                                    <L 588>
            if (var_torques) {
                // global_torque_w[tid_env, tid_body] = global_torque_w[tid_env, tid_body] + torques[tid_env, tid_body]       <L 589>
                var_25 = wp::address(var_global_torque_w, var_0, var_1);
                var_26 = wp::address(var_torques, var_0, var_1);
                var_28 = wp::load(var_25);
                var_29 = wp::load(var_26);
                var_27 = wp::add(var_28, var_29);
                // wp::array_store(var_global_torque_w, var_0, var_1, var_27);
            }
        }
        if (!var_is_global) {
            // if forces:                                                                     <L 591>
            if (var_forces) {
                // local_force_b[tid_env, tid_body] = local_force_b[tid_env, tid_body] + forces[tid_env, tid_body]       <L 592>
                var_30 = wp::address(var_local_force_b, var_0, var_1);
                var_31 = wp::address(var_forces, var_0, var_1);
                var_33 = wp::load(var_30);
                var_34 = wp::load(var_31);
                var_32 = wp::add(var_33, var_34);
                // wp::array_store(var_local_force_b, var_0, var_1, var_32);
                // if positions:                                                              <L 593>
                if (var_positions) {
                    // local_torque_b[tid_env, tid_body] = local_torque_b[tid_env, tid_body] + wp.cross(       <L 594>
                    var_35 = wp::address(var_local_torque_b, var_0, var_1);
                    // positions[tid_env, tid_body], forces[tid_env, tid_body]                <L 595>
                    var_36 = wp::address(var_positions, var_0, var_1);
                    var_37 = wp::address(var_forces, var_0, var_1);
                    var_39 = wp::load(var_36);
                    var_40 = wp::load(var_37);
                    var_38 = wp::cross(var_39, var_40);
                    var_42 = wp::load(var_35);
                    var_41 = wp::add(var_42, var_38);
                    // local_torque_b[tid_env, tid_body] = local_torque_b[tid_env, tid_body] + wp.cross(       <L 594>
                    // wp::array_store(var_local_torque_b, var_0, var_1, var_41);
                }
            }
            // if torques:                                                                    <L 597>
            if (var_torques) {
                // local_torque_b[tid_env, tid_body] = local_torque_b[tid_env, tid_body] + torques[tid_env, tid_body]       <L 598>
                var_43 = wp::address(var_local_torque_b, var_0, var_1);
                var_44 = wp::address(var_torques, var_0, var_1);
                var_46 = wp::load(var_43);
                var_47 = wp::load(var_44);
                var_45 = wp::add(var_46, var_47);
                // wp::array_store(var_local_torque_b, var_0, var_1, var_45);
            }
        }
    }
    //---------
    // reverse
    if (var_2) {
        if (!var_is_global) {
            if (var_torques) {
                wp::adj_array_store(var_local_torque_b, var_0, var_1, var_45, adj_local_torque_b, adj_0, adj_1, adj_45);
                wp::adj_add(var_46, var_47, adj_43, adj_44, adj_45);
                wp::adj_address(var_torques, var_0, var_1, adj_torques, adj_0, adj_1, adj_44);
                wp::adj_address(var_local_torque_b, var_0, var_1, adj_local_torque_b, adj_0, adj_1, adj_43);
                // adj: local_torque_b[tid_env, tid_body] = local_torque_b[tid_env, tid_body] + torques[tid_env, tid_body]  <L 598>
            }
            // adj: if torques:                                                               <L 597>
            if (var_forces) {
                if (var_positions) {
                    wp::adj_array_store(var_local_torque_b, var_0, var_1, var_41, adj_local_torque_b, adj_0, adj_1, adj_41);
                    // adj: local_torque_b[tid_env, tid_body] = local_torque_b[tid_env, tid_body] + wp.cross(  <L 594>
                    wp::adj_add(var_42, var_38, adj_35, adj_38, adj_41);
                    wp::adj_cross(var_39, var_40, adj_36, adj_37, adj_38);
                    wp::adj_address(var_forces, var_0, var_1, adj_forces, adj_0, adj_1, adj_37);
                    wp::adj_address(var_positions, var_0, var_1, adj_positions, adj_0, adj_1, adj_36);
                    // adj: positions[tid_env, tid_body], forces[tid_env, tid_body]           <L 595>
                    wp::adj_address(var_local_torque_b, var_0, var_1, adj_local_torque_b, adj_0, adj_1, adj_35);
                    // adj: local_torque_b[tid_env, tid_body] = local_torque_b[tid_env, tid_body] + wp.cross(  <L 594>
                }
                // adj: if positions:                                                         <L 593>
                wp::adj_array_store(var_local_force_b, var_0, var_1, var_32, adj_local_force_b, adj_0, adj_1, adj_32);
                wp::adj_add(var_33, var_34, adj_30, adj_31, adj_32);
                wp::adj_address(var_forces, var_0, var_1, adj_forces, adj_0, adj_1, adj_31);
                wp::adj_address(var_local_force_b, var_0, var_1, adj_local_force_b, adj_0, adj_1, adj_30);
                // adj: local_force_b[tid_env, tid_body] = local_force_b[tid_env, tid_body] + forces[tid_env, tid_body]  <L 592>
            }
            // adj: if forces:                                                                <L 591>
        }
        if (var_is_global) {
            if (var_torques) {
                wp::adj_array_store(var_global_torque_w, var_0, var_1, var_27, adj_global_torque_w, adj_0, adj_1, adj_27);
                wp::adj_add(var_28, var_29, adj_25, adj_26, adj_27);
                wp::adj_address(var_torques, var_0, var_1, adj_torques, adj_0, adj_1, adj_26);
                wp::adj_address(var_global_torque_w, var_0, var_1, adj_global_torque_w, adj_0, adj_1, adj_25);
                // adj: global_torque_w[tid_env, tid_body] = global_torque_w[tid_env, tid_body] + torques[tid_env, tid_body]  <L 589>
            }
            // adj: if torques:                                                               <L 588>
            if (var_forces) {
                if (!var_positions) {
                    wp::adj_array_store(var_global_force_at_com_w, var_0, var_1, var_22, adj_global_force_at_com_w, adj_0, adj_1, adj_22);
                    // adj: global_force_at_com_w[tid_env, tid_body] = (                      <L 585>
                    wp::adj_add(var_23, var_24, adj_20, adj_21, adj_22);
                    wp::adj_address(var_forces, var_0, var_1, adj_forces, adj_0, adj_1, adj_21);
                    wp::adj_address(var_global_force_at_com_w, var_0, var_1, adj_global_force_at_com_w, adj_0, adj_1, adj_20);
                    // adj: global_force_at_com_w[tid_env, tid_body] + forces[tid_env, tid_body]  <L 586>
                    // adj: global_force_at_com_w[tid_env, tid_body] = (                      <L 585>
                }
                if (var_positions) {
                    wp::adj_array_store(var_global_torque_w, var_0, var_1, var_18, adj_global_torque_w, adj_0, adj_1, adj_18);
                    // adj: global_torque_w[tid_env, tid_body] = global_torque_w[tid_env, tid_body] + wp.cross(  <L 581>
                    wp::adj_add(var_19, var_15, adj_12, adj_15, adj_18);
                    wp::adj_cross(var_16, var_17, adj_13, adj_14, adj_15);
                    wp::adj_address(var_forces, var_0, var_1, adj_forces, adj_0, adj_1, adj_14);
                    wp::adj_address(var_positions, var_0, var_1, adj_positions, adj_0, adj_1, adj_13);
                    // adj: positions[tid_env, tid_body], forces[tid_env, tid_body]           <L 582>
                    wp::adj_address(var_global_torque_w, var_0, var_1, adj_global_torque_w, adj_0, adj_1, adj_12);
                    // adj: global_torque_w[tid_env, tid_body] = global_torque_w[tid_env, tid_body] + wp.cross(  <L 581>
                    wp::adj_array_store(var_global_force_w, var_0, var_1, var_9, adj_global_force_w, adj_0, adj_1, adj_9);
                    wp::adj_add(var_10, var_11, adj_7, adj_8, adj_9);
                    wp::adj_address(var_forces, var_0, var_1, adj_forces, adj_0, adj_1, adj_8);
                    wp::adj_address(var_global_force_w, var_0, var_1, adj_global_force_w, adj_0, adj_1, adj_7);
                    // adj: global_force_w[tid_env, tid_body] = global_force_w[tid_env, tid_body] + forces[tid_env, tid_body]  <L 580>
                }
                // adj: if positions:                                                         <L 579>
            }
            // adj: if forces:                                                                <L 578>
        }
        // adj: if is_global:                                                                 <L 577>
    }
    if (var_2) {
        wp::adj_address(var_body_mask, var_1, adj_body_mask, adj_1, adj_5);
    }
    wp::adj_address(var_env_mask, var_0, adj_env_mask, adj_0, adj_3);
    // adj: if env_mask[tid_env] and body_mask[tid_body]:                                     <L 576>
    // adj: tid_env, tid_body = wp.tid()                                                      <L 574>
    // adj: def add_forces_to_dual_buffers_mask(                                              <L 555>
    return;
}



extern "C" {

// Python CPU entry points
WP_API void add_forces_to_dual_buffers_mask_e7b2db0e_cpu_forward(
    wp::launch_bounds_t<2> *dim,
    wp_args_add_forces_to_dual_buffers_mask_e7b2db0e *_wp_args)
{
    wp::tile_shared_storage_t tile_mem;
#if defined(WP_ENABLE_TILES_IN_STACK_MEMORY)
    wp::shared_tile_storage = &tile_mem;
#endif

    for (size_t task_index = 0; task_index < dim->size; ++task_index)
    {
        add_forces_to_dual_buffers_mask_e7b2db0e_cpu_kernel_forward(*dim, task_index, _wp_args);
    }
}

} // extern C



extern "C" {

WP_API void add_forces_to_dual_buffers_mask_e7b2db0e_cpu_backward(
    wp::launch_bounds_t<2> *dim,
    wp_args_add_forces_to_dual_buffers_mask_e7b2db0e *_wp_args,
    wp_args_add_forces_to_dual_buffers_mask_e7b2db0e *_wp_adj_args)
{
    wp::tile_shared_storage_t tile_mem;
#if defined(WP_ENABLE_TILES_IN_STACK_MEMORY)
    wp::shared_tile_storage = &tile_mem;
#endif

    for (size_t task_index = 0; task_index < dim->size; ++task_index)
    {
        add_forces_to_dual_buffers_mask_e7b2db0e_cpu_kernel_backward(*dim, task_index, _wp_args, _wp_adj_args);
    }
}

} // extern C

struct wp_args_raycast_mesh_kernel_fa49f9a1 {
    wp::uint64 mesh;
    wp::array_t<wp::vec_t<3, wp::float32>> ray_starts;
    wp::array_t<wp::vec_t<3, wp::float32>> ray_directions;
    wp::array_t<wp::vec_t<3, wp::float32>> ray_hits;
    wp::array_t<wp::float32> ray_distance;
    wp::array_t<wp::vec_t<3, wp::float32>> ray_normal;
    wp::array_t<wp::int32> ray_face_id;
    wp::float32 max_dist;
    wp::int32 return_distance;
    wp::int32 return_normal;
    wp::int32 return_face_id;
};


void raycast_mesh_kernel_fa49f9a1_cpu_kernel_forward(
    wp::launch_bounds_t<1> dim,
    size_t task_index,
    wp_args_raycast_mesh_kernel_fa49f9a1 *_wp_args)
{
    //---------
    // argument vars
    wp::uint64 var_mesh = _wp_args->mesh;
    wp::array_t<wp::vec_t<3, wp::float32>> var_ray_starts = _wp_args->ray_starts;
    wp::array_t<wp::vec_t<3, wp::float32>> var_ray_directions = _wp_args->ray_directions;
    wp::array_t<wp::vec_t<3, wp::float32>> var_ray_hits = _wp_args->ray_hits;
    wp::array_t<wp::float32> var_ray_distance = _wp_args->ray_distance;
    wp::array_t<wp::vec_t<3, wp::float32>> var_ray_normal = _wp_args->ray_normal;
    wp::array_t<wp::int32> var_ray_face_id = _wp_args->ray_face_id;
    wp::float32 var_max_dist = _wp_args->max_dist;
    wp::int32 var_return_distance = _wp_args->return_distance;
    wp::int32 var_return_normal = _wp_args->return_normal;
    wp::int32 var_return_face_id = _wp_args->return_face_id;
    //---------
    // primal vars
    wp::int32 var_0;
    const wp::float32 var_1 = 0.0;
    wp::float32 var_2;
    const wp::float32 var_3 = 0.0;
    wp::float32 var_4;
    const wp::float32 var_5 = 0.0;
    wp::float32 var_6;
    const wp::float32 var_7 = 0.0;
    wp::float32 var_8;
    wp::vec_t<3, wp::float32> var_9;
    const wp::int32 var_10 = 0;
    wp::int32 var_11;
    wp::vec_t<3, wp::float32>* var_12;
    wp::vec_t<3, wp::float32>* var_13;
    bool var_14;
    const wp::int32 var_15 = -1;
    wp::vec_t<3, wp::float32> var_16;
    wp::vec_t<3, wp::float32> var_17;
    wp::vec_t<3, wp::float32>* var_18;
    wp::vec_t<3, wp::float32>* var_19;
    wp::vec_t<3, wp::float32> var_20;
    wp::vec_t<3, wp::float32> var_21;
    wp::vec_t<3, wp::float32> var_22;
    wp::vec_t<3, wp::float32> var_23;
    const wp::int32 var_24 = 1;
    bool var_25;
    const wp::int32 var_26 = 1;
    bool var_27;
    const wp::int32 var_28 = 1;
    bool var_29;
    //---------
    // forward
    // def raycast_mesh_kernel(                                                               <L 21>
    // tid = wp.tid()                                                                         <L 63>
    var_0 = builtin_tid1d();
    // t = float(0.0)  # hit distance along ray                                               <L 65>
    var_2 = wp::float(var_1);
    // u = float(0.0)  # hit face barycentric u                                               <L 66>
    var_4 = wp::float(var_3);
    // v = float(0.0)  # hit face barycentric v                                               <L 67>
    var_6 = wp::float(var_5);
    // sign = float(0.0)  # hit face sign                                                     <L 68>
    var_8 = wp::float(var_7);
    // n = wp.vec3()  # hit face normal                                                       <L 69>
    var_9 = wp::vec_t<3, wp::float32>();
    // f = int(0)  # hit face index                                                           <L 70>
    var_11 = wp::int(var_10);
    // hit_success = wp.mesh_query_ray(mesh, ray_starts[tid], ray_directions[tid], max_dist, t, u, v, sign, n, f)       <L 73>
    var_12 = wp::address(var_ray_starts, var_0);
    var_13 = wp::address(var_ray_directions, var_0);
    var_16 = wp::load(var_12);
    var_17 = wp::load(var_13);
    var_14 = wp::mesh_query_ray(var_mesh, var_16, var_17, var_max_dist, var_2, var_4, var_6, var_8, var_9, var_11, var_15);
    // if hit_success:                                                                        <L 75>
    if (var_14) {
        // ray_hits[tid] = ray_starts[tid] + t * ray_directions[tid]                          <L 76>
        var_18 = wp::address(var_ray_starts, var_0);
        var_19 = wp::address(var_ray_directions, var_0);
        var_21 = wp::load(var_19);
        var_20 = wp::mul(var_2, var_21);
        var_23 = wp::load(var_18);
        var_22 = wp::add(var_23, var_20);
        wp::array_store(var_ray_hits, var_0, var_22);
        // if return_distance == 1:                                                           <L 77>
        var_25 = (var_return_distance == var_24);
        if (var_25) {
            // ray_distance[tid] = t                                                          <L 78>
            wp::array_store(var_ray_distance, var_0, var_2);
        }
        // if return_normal == 1:                                                             <L 79>
        var_27 = (var_return_normal == var_26);
        if (var_27) {
            // ray_normal[tid] = n                                                            <L 80>
            wp::array_store(var_ray_normal, var_0, var_9);
        }
        // if return_face_id == 1:                                                            <L 81>
        var_29 = (var_return_face_id == var_28);
        if (var_29) {
            // ray_face_id[tid] = f                                                           <L 82>
            wp::array_store(var_ray_face_id, var_0, var_11);
        }
    }
}



extern "C" {

// Python CPU entry points
WP_API void raycast_mesh_kernel_fa49f9a1_cpu_forward(
    wp::launch_bounds_t<1> *dim,
    wp_args_raycast_mesh_kernel_fa49f9a1 *_wp_args)
{
    wp::tile_shared_storage_t tile_mem;
#if defined(WP_ENABLE_TILES_IN_STACK_MEMORY)
    wp::shared_tile_storage = &tile_mem;
#endif

    for (size_t task_index = 0; task_index < dim->size; ++task_index)
    {
        raycast_mesh_kernel_fa49f9a1_cpu_kernel_forward(*dim, task_index, _wp_args);
    }
}

} // extern C

struct wp_args_add_forces_to_dual_buffers_index_fcc4e425 {
    wp::array_t<wp::int64> env_ids;
    wp::array_t<wp::int32> body_ids;
    wp::array_t<wp::vec_t<3, wp::float32>> forces;
    wp::array_t<wp::vec_t<3, wp::float32>> torques;
    wp::array_t<wp::vec_t<3, wp::float32>> positions;
    wp::array_t<wp::vec_t<3, wp::float32>> global_force_w;
    wp::array_t<wp::vec_t<3, wp::float32>> global_torque_w;
    wp::array_t<wp::vec_t<3, wp::float32>> global_force_at_com_w;
    wp::array_t<wp::vec_t<3, wp::float32>> local_force_b;
    wp::array_t<wp::vec_t<3, wp::float32>> local_torque_b;
    bool is_global;
};


void add_forces_to_dual_buffers_index_fcc4e425_cpu_kernel_forward(
    wp::launch_bounds_t<2> dim,
    size_t task_index,
    wp_args_add_forces_to_dual_buffers_index_fcc4e425 *_wp_args)
{
    //---------
    // argument vars
    wp::array_t<wp::int64> var_env_ids = _wp_args->env_ids;
    wp::array_t<wp::int32> var_body_ids = _wp_args->body_ids;
    wp::array_t<wp::vec_t<3, wp::float32>> var_forces = _wp_args->forces;
    wp::array_t<wp::vec_t<3, wp::float32>> var_torques = _wp_args->torques;
    wp::array_t<wp::vec_t<3, wp::float32>> var_positions = _wp_args->positions;
    wp::array_t<wp::vec_t<3, wp::float32>> var_global_force_w = _wp_args->global_force_w;
    wp::array_t<wp::vec_t<3, wp::float32>> var_global_torque_w = _wp_args->global_torque_w;
    wp::array_t<wp::vec_t<3, wp::float32>> var_global_force_at_com_w = _wp_args->global_force_at_com_w;
    wp::array_t<wp::vec_t<3, wp::float32>> var_local_force_b = _wp_args->local_force_b;
    wp::array_t<wp::vec_t<3, wp::float32>> var_local_torque_b = _wp_args->local_torque_b;
    bool var_is_global = _wp_args->is_global;
    //---------
    // primal vars
    wp::int32 var_0;
    wp::int32 var_1;
    wp::int64* var_2;
    wp::int32 var_3;
    wp::int64 var_4;
    wp::int32* var_5;
    wp::int32 var_6;
    wp::int32 var_7;
    wp::vec_t<3, wp::float32>* var_8;
    wp::vec_t<3, wp::float32>* var_9;
    wp::vec_t<3, wp::float32> var_10;
    wp::vec_t<3, wp::float32> var_11;
    wp::vec_t<3, wp::float32> var_12;
    wp::vec_t<3, wp::float32>* var_13;
    wp::vec_t<3, wp::float32>* var_14;
    wp::vec_t<3, wp::float32>* var_15;
    wp::vec_t<3, wp::float32> var_16;
    wp::vec_t<3, wp::float32> var_17;
    wp::vec_t<3, wp::float32> var_18;
    wp::vec_t<3, wp::float32> var_19;
    wp::vec_t<3, wp::float32> var_20;
    wp::vec_t<3, wp::float32>* var_21;
    wp::vec_t<3, wp::float32>* var_22;
    wp::vec_t<3, wp::float32> var_23;
    wp::vec_t<3, wp::float32> var_24;
    wp::vec_t<3, wp::float32> var_25;
    wp::vec_t<3, wp::float32>* var_26;
    wp::vec_t<3, wp::float32>* var_27;
    wp::vec_t<3, wp::float32> var_28;
    wp::vec_t<3, wp::float32> var_29;
    wp::vec_t<3, wp::float32> var_30;
    wp::vec_t<3, wp::float32>* var_31;
    wp::vec_t<3, wp::float32>* var_32;
    wp::vec_t<3, wp::float32> var_33;
    wp::vec_t<3, wp::float32> var_34;
    wp::vec_t<3, wp::float32> var_35;
    wp::vec_t<3, wp::float32>* var_36;
    wp::vec_t<3, wp::float32>* var_37;
    wp::vec_t<3, wp::float32>* var_38;
    wp::vec_t<3, wp::float32> var_39;
    wp::vec_t<3, wp::float32> var_40;
    wp::vec_t<3, wp::float32> var_41;
    wp::vec_t<3, wp::float32> var_42;
    wp::vec_t<3, wp::float32> var_43;
    wp::vec_t<3, wp::float32>* var_44;
    wp::vec_t<3, wp::float32>* var_45;
    wp::vec_t<3, wp::float32> var_46;
    wp::vec_t<3, wp::float32> var_47;
    wp::vec_t<3, wp::float32> var_48;
    //---------
    // forward
    // def add_forces_to_dual_buffers_index(                                                  <L 1>
    // tid_env, tid_body = wp.tid()                                                           <L 19>
    builtin_tid2d(var_0, var_1);
    // ei = wp.int32(env_ids[tid_env])                                                        <L 20>
    var_2 = wp::address(var_env_ids, var_0);
    var_4 = wp::load(var_2);
    var_3 = wp::int32(var_4);
    // bi = wp.int32(body_ids[tid_body])                                                      <L 21>
    var_5 = wp::address(var_body_ids, var_1);
    var_7 = wp::load(var_5);
    var_6 = wp::int32(var_7);
    // if is_global:                                                                          <L 23>
    if (var_is_global) {
        // if forces:                                                                         <L 24>
        if (var_forces) {
            // if positions:                                                                  <L 25>
            if (var_positions) {
                // global_force_w[ei, bi] = global_force_w[ei, bi] + forces[tid_env, tid_body]       <L 26>
                var_8 = wp::address(var_global_force_w, var_3, var_6);
                var_9 = wp::address(var_forces, var_0, var_1);
                var_11 = wp::load(var_8);
                var_12 = wp::load(var_9);
                var_10 = wp::add(var_11, var_12);
                wp::array_store(var_global_force_w, var_3, var_6, var_10);
                // global_torque_w[ei, bi] = global_torque_w[ei, bi] + wp.cross(              <L 27>
                var_13 = wp::address(var_global_torque_w, var_3, var_6);
                // positions[tid_env, tid_body], forces[tid_env, tid_body]                    <L 28>
                var_14 = wp::address(var_positions, var_0, var_1);
                var_15 = wp::address(var_forces, var_0, var_1);
                var_17 = wp::load(var_14);
                var_18 = wp::load(var_15);
                var_16 = wp::cross(var_17, var_18);
                var_20 = wp::load(var_13);
                var_19 = wp::add(var_20, var_16);
                // global_torque_w[ei, bi] = global_torque_w[ei, bi] + wp.cross(              <L 27>
                wp::array_store(var_global_torque_w, var_3, var_6, var_19);
            }
            if (!var_positions) {
                // global_force_at_com_w[ei, bi] = global_force_at_com_w[ei, bi] + forces[tid_env, tid_body]       <L 31>
                var_21 = wp::address(var_global_force_at_com_w, var_3, var_6);
                var_22 = wp::address(var_forces, var_0, var_1);
                var_24 = wp::load(var_21);
                var_25 = wp::load(var_22);
                var_23 = wp::add(var_24, var_25);
                wp::array_store(var_global_force_at_com_w, var_3, var_6, var_23);
            }
        }
        // if torques:                                                                        <L 32>
        if (var_torques) {
            // global_torque_w[ei, bi] = global_torque_w[ei, bi] + torques[tid_env, tid_body]       <L 33>
            var_26 = wp::address(var_global_torque_w, var_3, var_6);
            var_27 = wp::address(var_torques, var_0, var_1);
            var_29 = wp::load(var_26);
            var_30 = wp::load(var_27);
            var_28 = wp::add(var_29, var_30);
            wp::array_store(var_global_torque_w, var_3, var_6, var_28);
        }
    }
    if (!var_is_global) {
        // if forces:                                                                         <L 35>
        if (var_forces) {
            // local_force_b[ei, bi] = local_force_b[ei, bi] + forces[tid_env, tid_body]       <L 36>
            var_31 = wp::address(var_local_force_b, var_3, var_6);
            var_32 = wp::address(var_forces, var_0, var_1);
            var_34 = wp::load(var_31);
            var_35 = wp::load(var_32);
            var_33 = wp::add(var_34, var_35);
            wp::array_store(var_local_force_b, var_3, var_6, var_33);
            // if positions:                                                                  <L 37>
            if (var_positions) {
                // local_torque_b[ei, bi] = local_torque_b[ei, bi] + wp.cross(                <L 38>
                var_36 = wp::address(var_local_torque_b, var_3, var_6);
                // positions[tid_env, tid_body], forces[tid_env, tid_body]                    <L 39>
                var_37 = wp::address(var_positions, var_0, var_1);
                var_38 = wp::address(var_forces, var_0, var_1);
                var_40 = wp::load(var_37);
                var_41 = wp::load(var_38);
                var_39 = wp::cross(var_40, var_41);
                var_43 = wp::load(var_36);
                var_42 = wp::add(var_43, var_39);
                // local_torque_b[ei, bi] = local_torque_b[ei, bi] + wp.cross(                <L 38>
                wp::array_store(var_local_torque_b, var_3, var_6, var_42);
            }
        }
        // if torques:                                                                        <L 41>
        if (var_torques) {
            // local_torque_b[ei, bi] = local_torque_b[ei, bi] + torques[tid_env, tid_body]       <L 42>
            var_44 = wp::address(var_local_torque_b, var_3, var_6);
            var_45 = wp::address(var_torques, var_0, var_1);
            var_47 = wp::load(var_44);
            var_48 = wp::load(var_45);
            var_46 = wp::add(var_47, var_48);
            wp::array_store(var_local_torque_b, var_3, var_6, var_46);
        }
    }
}



void add_forces_to_dual_buffers_index_fcc4e425_cpu_kernel_backward(
    wp::launch_bounds_t<2> dim,
    size_t task_index,
    wp_args_add_forces_to_dual_buffers_index_fcc4e425 *_wp_args,
    wp_args_add_forces_to_dual_buffers_index_fcc4e425 *_wp_adj_args)
{
    //---------
    // argument vars
    wp::array_t<wp::int64> var_env_ids = _wp_args->env_ids;
    wp::array_t<wp::int32> var_body_ids = _wp_args->body_ids;
    wp::array_t<wp::vec_t<3, wp::float32>> var_forces = _wp_args->forces;
    wp::array_t<wp::vec_t<3, wp::float32>> var_torques = _wp_args->torques;
    wp::array_t<wp::vec_t<3, wp::float32>> var_positions = _wp_args->positions;
    wp::array_t<wp::vec_t<3, wp::float32>> var_global_force_w = _wp_args->global_force_w;
    wp::array_t<wp::vec_t<3, wp::float32>> var_global_torque_w = _wp_args->global_torque_w;
    wp::array_t<wp::vec_t<3, wp::float32>> var_global_force_at_com_w = _wp_args->global_force_at_com_w;
    wp::array_t<wp::vec_t<3, wp::float32>> var_local_force_b = _wp_args->local_force_b;
    wp::array_t<wp::vec_t<3, wp::float32>> var_local_torque_b = _wp_args->local_torque_b;
    bool var_is_global = _wp_args->is_global;
    wp::array_t<wp::int64> adj_env_ids = _wp_adj_args->env_ids;
    wp::array_t<wp::int32> adj_body_ids = _wp_adj_args->body_ids;
    wp::array_t<wp::vec_t<3, wp::float32>> adj_forces = _wp_adj_args->forces;
    wp::array_t<wp::vec_t<3, wp::float32>> adj_torques = _wp_adj_args->torques;
    wp::array_t<wp::vec_t<3, wp::float32>> adj_positions = _wp_adj_args->positions;
    wp::array_t<wp::vec_t<3, wp::float32>> adj_global_force_w = _wp_adj_args->global_force_w;
    wp::array_t<wp::vec_t<3, wp::float32>> adj_global_torque_w = _wp_adj_args->global_torque_w;
    wp::array_t<wp::vec_t<3, wp::float32>> adj_global_force_at_com_w = _wp_adj_args->global_force_at_com_w;
    wp::array_t<wp::vec_t<3, wp::float32>> adj_local_force_b = _wp_adj_args->local_force_b;
    wp::array_t<wp::vec_t<3, wp::float32>> adj_local_torque_b = _wp_adj_args->local_torque_b;
    bool adj_is_global = _wp_adj_args->is_global;
    //---------
    // primal vars
    wp::int32 var_0;
    wp::int32 var_1;
    wp::int64* var_2;
    wp::int32 var_3;
    wp::int64 var_4;
    wp::int32* var_5;
    wp::int32 var_6;
    wp::int32 var_7;
    wp::vec_t<3, wp::float32>* var_8;
    wp::vec_t<3, wp::float32>* var_9;
    wp::vec_t<3, wp::float32> var_10;
    wp::vec_t<3, wp::float32> var_11;
    wp::vec_t<3, wp::float32> var_12;
    wp::vec_t<3, wp::float32>* var_13;
    wp::vec_t<3, wp::float32>* var_14;
    wp::vec_t<3, wp::float32>* var_15;
    wp::vec_t<3, wp::float32> var_16;
    wp::vec_t<3, wp::float32> var_17;
    wp::vec_t<3, wp::float32> var_18;
    wp::vec_t<3, wp::float32> var_19;
    wp::vec_t<3, wp::float32> var_20;
    wp::vec_t<3, wp::float32>* var_21;
    wp::vec_t<3, wp::float32>* var_22;
    wp::vec_t<3, wp::float32> var_23;
    wp::vec_t<3, wp::float32> var_24;
    wp::vec_t<3, wp::float32> var_25;
    wp::vec_t<3, wp::float32>* var_26;
    wp::vec_t<3, wp::float32>* var_27;
    wp::vec_t<3, wp::float32> var_28;
    wp::vec_t<3, wp::float32> var_29;
    wp::vec_t<3, wp::float32> var_30;
    wp::vec_t<3, wp::float32>* var_31;
    wp::vec_t<3, wp::float32>* var_32;
    wp::vec_t<3, wp::float32> var_33;
    wp::vec_t<3, wp::float32> var_34;
    wp::vec_t<3, wp::float32> var_35;
    wp::vec_t<3, wp::float32>* var_36;
    wp::vec_t<3, wp::float32>* var_37;
    wp::vec_t<3, wp::float32>* var_38;
    wp::vec_t<3, wp::float32> var_39;
    wp::vec_t<3, wp::float32> var_40;
    wp::vec_t<3, wp::float32> var_41;
    wp::vec_t<3, wp::float32> var_42;
    wp::vec_t<3, wp::float32> var_43;
    wp::vec_t<3, wp::float32>* var_44;
    wp::vec_t<3, wp::float32>* var_45;
    wp::vec_t<3, wp::float32> var_46;
    wp::vec_t<3, wp::float32> var_47;
    wp::vec_t<3, wp::float32> var_48;
    //---------
    // dual vars
    wp::int32 adj_0 = {};
    wp::int32 adj_1 = {};
    wp::int64 adj_2 = {};
    wp::int32 adj_3 = {};
    wp::int64 adj_4 = {};
    wp::int32 adj_5 = {};
    wp::int32 adj_6 = {};
    wp::int32 adj_7 = {};
    wp::vec_t<3, wp::float32> adj_8 = {};
    wp::vec_t<3, wp::float32> adj_9 = {};
    wp::vec_t<3, wp::float32> adj_10 = {};
    wp::vec_t<3, wp::float32> adj_11 = {};
    wp::vec_t<3, wp::float32> adj_12 = {};
    wp::vec_t<3, wp::float32> adj_13 = {};
    wp::vec_t<3, wp::float32> adj_14 = {};
    wp::vec_t<3, wp::float32> adj_15 = {};
    wp::vec_t<3, wp::float32> adj_16 = {};
    wp::vec_t<3, wp::float32> adj_17 = {};
    wp::vec_t<3, wp::float32> adj_18 = {};
    wp::vec_t<3, wp::float32> adj_19 = {};
    wp::vec_t<3, wp::float32> adj_20 = {};
    wp::vec_t<3, wp::float32> adj_21 = {};
    wp::vec_t<3, wp::float32> adj_22 = {};
    wp::vec_t<3, wp::float32> adj_23 = {};
    wp::vec_t<3, wp::float32> adj_24 = {};
    wp::vec_t<3, wp::float32> adj_25 = {};
    wp::vec_t<3, wp::float32> adj_26 = {};
    wp::vec_t<3, wp::float32> adj_27 = {};
    wp::vec_t<3, wp::float32> adj_28 = {};
    wp::vec_t<3, wp::float32> adj_29 = {};
    wp::vec_t<3, wp::float32> adj_30 = {};
    wp::vec_t<3, wp::float32> adj_31 = {};
    wp::vec_t<3, wp::float32> adj_32 = {};
    wp::vec_t<3, wp::float32> adj_33 = {};
    wp::vec_t<3, wp::float32> adj_34 = {};
    wp::vec_t<3, wp::float32> adj_35 = {};
    wp::vec_t<3, wp::float32> adj_36 = {};
    wp::vec_t<3, wp::float32> adj_37 = {};
    wp::vec_t<3, wp::float32> adj_38 = {};
    wp::vec_t<3, wp::float32> adj_39 = {};
    wp::vec_t<3, wp::float32> adj_40 = {};
    wp::vec_t<3, wp::float32> adj_41 = {};
    wp::vec_t<3, wp::float32> adj_42 = {};
    wp::vec_t<3, wp::float32> adj_43 = {};
    wp::vec_t<3, wp::float32> adj_44 = {};
    wp::vec_t<3, wp::float32> adj_45 = {};
    wp::vec_t<3, wp::float32> adj_46 = {};
    wp::vec_t<3, wp::float32> adj_47 = {};
    wp::vec_t<3, wp::float32> adj_48 = {};
    //---------
    // forward
    // def add_forces_to_dual_buffers_index(                                                  <L 1>
    // tid_env, tid_body = wp.tid()                                                           <L 19>
    builtin_tid2d(var_0, var_1);
    // ei = wp.int32(env_ids[tid_env])                                                        <L 20>
    var_2 = wp::address(var_env_ids, var_0);
    var_4 = wp::load(var_2);
    var_3 = wp::int32(var_4);
    // bi = wp.int32(body_ids[tid_body])                                                      <L 21>
    var_5 = wp::address(var_body_ids, var_1);
    var_7 = wp::load(var_5);
    var_6 = wp::int32(var_7);
    // if is_global:                                                                          <L 23>
    if (var_is_global) {
        // if forces:                                                                         <L 24>
        if (var_forces) {
            // if positions:                                                                  <L 25>
            if (var_positions) {
                // global_force_w[ei, bi] = global_force_w[ei, bi] + forces[tid_env, tid_body]       <L 26>
                var_8 = wp::address(var_global_force_w, var_3, var_6);
                var_9 = wp::address(var_forces, var_0, var_1);
                var_11 = wp::load(var_8);
                var_12 = wp::load(var_9);
                var_10 = wp::add(var_11, var_12);
                // wp::array_store(var_global_force_w, var_3, var_6, var_10);
                // global_torque_w[ei, bi] = global_torque_w[ei, bi] + wp.cross(              <L 27>
                var_13 = wp::address(var_global_torque_w, var_3, var_6);
                // positions[tid_env, tid_body], forces[tid_env, tid_body]                    <L 28>
                var_14 = wp::address(var_positions, var_0, var_1);
                var_15 = wp::address(var_forces, var_0, var_1);
                var_17 = wp::load(var_14);
                var_18 = wp::load(var_15);
                var_16 = wp::cross(var_17, var_18);
                var_20 = wp::load(var_13);
                var_19 = wp::add(var_20, var_16);
                // global_torque_w[ei, bi] = global_torque_w[ei, bi] + wp.cross(              <L 27>
                // wp::array_store(var_global_torque_w, var_3, var_6, var_19);
            }
            if (!var_positions) {
                // global_force_at_com_w[ei, bi] = global_force_at_com_w[ei, bi] + forces[tid_env, tid_body]       <L 31>
                var_21 = wp::address(var_global_force_at_com_w, var_3, var_6);
                var_22 = wp::address(var_forces, var_0, var_1);
                var_24 = wp::load(var_21);
                var_25 = wp::load(var_22);
                var_23 = wp::add(var_24, var_25);
                // wp::array_store(var_global_force_at_com_w, var_3, var_6, var_23);
            }
        }
        // if torques:                                                                        <L 32>
        if (var_torques) {
            // global_torque_w[ei, bi] = global_torque_w[ei, bi] + torques[tid_env, tid_body]       <L 33>
            var_26 = wp::address(var_global_torque_w, var_3, var_6);
            var_27 = wp::address(var_torques, var_0, var_1);
            var_29 = wp::load(var_26);
            var_30 = wp::load(var_27);
            var_28 = wp::add(var_29, var_30);
            // wp::array_store(var_global_torque_w, var_3, var_6, var_28);
        }
    }
    if (!var_is_global) {
        // if forces:                                                                         <L 35>
        if (var_forces) {
            // local_force_b[ei, bi] = local_force_b[ei, bi] + forces[tid_env, tid_body]       <L 36>
            var_31 = wp::address(var_local_force_b, var_3, var_6);
            var_32 = wp::address(var_forces, var_0, var_1);
            var_34 = wp::load(var_31);
            var_35 = wp::load(var_32);
            var_33 = wp::add(var_34, var_35);
            // wp::array_store(var_local_force_b, var_3, var_6, var_33);
            // if positions:                                                                  <L 37>
            if (var_positions) {
                // local_torque_b[ei, bi] = local_torque_b[ei, bi] + wp.cross(                <L 38>
                var_36 = wp::address(var_local_torque_b, var_3, var_6);
                // positions[tid_env, tid_body], forces[tid_env, tid_body]                    <L 39>
                var_37 = wp::address(var_positions, var_0, var_1);
                var_38 = wp::address(var_forces, var_0, var_1);
                var_40 = wp::load(var_37);
                var_41 = wp::load(var_38);
                var_39 = wp::cross(var_40, var_41);
                var_43 = wp::load(var_36);
                var_42 = wp::add(var_43, var_39);
                // local_torque_b[ei, bi] = local_torque_b[ei, bi] + wp.cross(                <L 38>
                // wp::array_store(var_local_torque_b, var_3, var_6, var_42);
            }
        }
        // if torques:                                                                        <L 41>
        if (var_torques) {
            // local_torque_b[ei, bi] = local_torque_b[ei, bi] + torques[tid_env, tid_body]       <L 42>
            var_44 = wp::address(var_local_torque_b, var_3, var_6);
            var_45 = wp::address(var_torques, var_0, var_1);
            var_47 = wp::load(var_44);
            var_48 = wp::load(var_45);
            var_46 = wp::add(var_47, var_48);
            // wp::array_store(var_local_torque_b, var_3, var_6, var_46);
        }
    }
    //---------
    // reverse
    if (!var_is_global) {
        if (var_torques) {
            wp::adj_array_store(var_local_torque_b, var_3, var_6, var_46, adj_local_torque_b, adj_3, adj_6, adj_46);
            wp::adj_add(var_47, var_48, adj_44, adj_45, adj_46);
            wp::adj_address(var_torques, var_0, var_1, adj_torques, adj_0, adj_1, adj_45);
            wp::adj_address(var_local_torque_b, var_3, var_6, adj_local_torque_b, adj_3, adj_6, adj_44);
            // adj: local_torque_b[ei, bi] = local_torque_b[ei, bi] + torques[tid_env, tid_body]  <L 42>
        }
        // adj: if torques:                                                                   <L 41>
        if (var_forces) {
            if (var_positions) {
                wp::adj_array_store(var_local_torque_b, var_3, var_6, var_42, adj_local_torque_b, adj_3, adj_6, adj_42);
                // adj: local_torque_b[ei, bi] = local_torque_b[ei, bi] + wp.cross(           <L 38>
                wp::adj_add(var_43, var_39, adj_36, adj_39, adj_42);
                wp::adj_cross(var_40, var_41, adj_37, adj_38, adj_39);
                wp::adj_address(var_forces, var_0, var_1, adj_forces, adj_0, adj_1, adj_38);
                wp::adj_address(var_positions, var_0, var_1, adj_positions, adj_0, adj_1, adj_37);
                // adj: positions[tid_env, tid_body], forces[tid_env, tid_body]               <L 39>
                wp::adj_address(var_local_torque_b, var_3, var_6, adj_local_torque_b, adj_3, adj_6, adj_36);
                // adj: local_torque_b[ei, bi] = local_torque_b[ei, bi] + wp.cross(           <L 38>
            }
            // adj: if positions:                                                             <L 37>
            wp::adj_array_store(var_local_force_b, var_3, var_6, var_33, adj_local_force_b, adj_3, adj_6, adj_33);
            wp::adj_add(var_34, var_35, adj_31, adj_32, adj_33);
            wp::adj_address(var_forces, var_0, var_1, adj_forces, adj_0, adj_1, adj_32);
            wp::adj_address(var_local_force_b, var_3, var_6, adj_local_force_b, adj_3, adj_6, adj_31);
            // adj: local_force_b[ei, bi] = local_force_b[ei, bi] + forces[tid_env, tid_body]  <L 36>
        }
        // adj: if forces:                                                                    <L 35>
    }
    if (var_is_global) {
        if (var_torques) {
            wp::adj_array_store(var_global_torque_w, var_3, var_6, var_28, adj_global_torque_w, adj_3, adj_6, adj_28);
            wp::adj_add(var_29, var_30, adj_26, adj_27, adj_28);
            wp::adj_address(var_torques, var_0, var_1, adj_torques, adj_0, adj_1, adj_27);
            wp::adj_address(var_global_torque_w, var_3, var_6, adj_global_torque_w, adj_3, adj_6, adj_26);
            // adj: global_torque_w[ei, bi] = global_torque_w[ei, bi] + torques[tid_env, tid_body]  <L 33>
        }
        // adj: if torques:                                                                   <L 32>
        if (var_forces) {
            if (!var_positions) {
                wp::adj_array_store(var_global_force_at_com_w, var_3, var_6, var_23, adj_global_force_at_com_w, adj_3, adj_6, adj_23);
                wp::adj_add(var_24, var_25, adj_21, adj_22, adj_23);
                wp::adj_address(var_forces, var_0, var_1, adj_forces, adj_0, adj_1, adj_22);
                wp::adj_address(var_global_force_at_com_w, var_3, var_6, adj_global_force_at_com_w, adj_3, adj_6, adj_21);
                // adj: global_force_at_com_w[ei, bi] = global_force_at_com_w[ei, bi] + forces[tid_env, tid_body]  <L 31>
            }
            if (var_positions) {
                wp::adj_array_store(var_global_torque_w, var_3, var_6, var_19, adj_global_torque_w, adj_3, adj_6, adj_19);
                // adj: global_torque_w[ei, bi] = global_torque_w[ei, bi] + wp.cross(         <L 27>
                wp::adj_add(var_20, var_16, adj_13, adj_16, adj_19);
                wp::adj_cross(var_17, var_18, adj_14, adj_15, adj_16);
                wp::adj_address(var_forces, var_0, var_1, adj_forces, adj_0, adj_1, adj_15);
                wp::adj_address(var_positions, var_0, var_1, adj_positions, adj_0, adj_1, adj_14);
                // adj: positions[tid_env, tid_body], forces[tid_env, tid_body]               <L 28>
                wp::adj_address(var_global_torque_w, var_3, var_6, adj_global_torque_w, adj_3, adj_6, adj_13);
                // adj: global_torque_w[ei, bi] = global_torque_w[ei, bi] + wp.cross(         <L 27>
                wp::adj_array_store(var_global_force_w, var_3, var_6, var_10, adj_global_force_w, adj_3, adj_6, adj_10);
                wp::adj_add(var_11, var_12, adj_8, adj_9, adj_10);
                wp::adj_address(var_forces, var_0, var_1, adj_forces, adj_0, adj_1, adj_9);
                wp::adj_address(var_global_force_w, var_3, var_6, adj_global_force_w, adj_3, adj_6, adj_8);
                // adj: global_force_w[ei, bi] = global_force_w[ei, bi] + forces[tid_env, tid_body]  <L 26>
            }
            // adj: if positions:                                                             <L 25>
        }
        // adj: if forces:                                                                    <L 24>
    }
    // adj: if is_global:                                                                     <L 23>
    wp::adj_address(var_body_ids, var_1, adj_body_ids, adj_1, adj_5);
    // adj: bi = wp.int32(body_ids[tid_body])                                                 <L 21>
    wp::adj_address(var_env_ids, var_0, adj_env_ids, adj_0, adj_2);
    // adj: ei = wp.int32(env_ids[tid_env])                                                   <L 20>
    // adj: tid_env, tid_body = wp.tid()                                                      <L 19>
    // adj: def add_forces_to_dual_buffers_index(                                             <L 1>
    return;
}



extern "C" {

// Python CPU entry points
WP_API void add_forces_to_dual_buffers_index_fcc4e425_cpu_forward(
    wp::launch_bounds_t<2> *dim,
    wp_args_add_forces_to_dual_buffers_index_fcc4e425 *_wp_args)
{
    wp::tile_shared_storage_t tile_mem;
#if defined(WP_ENABLE_TILES_IN_STACK_MEMORY)
    wp::shared_tile_storage = &tile_mem;
#endif

    for (size_t task_index = 0; task_index < dim->size; ++task_index)
    {
        add_forces_to_dual_buffers_index_fcc4e425_cpu_kernel_forward(*dim, task_index, _wp_args);
    }
}

} // extern C



extern "C" {

WP_API void add_forces_to_dual_buffers_index_fcc4e425_cpu_backward(
    wp::launch_bounds_t<2> *dim,
    wp_args_add_forces_to_dual_buffers_index_fcc4e425 *_wp_args,
    wp_args_add_forces_to_dual_buffers_index_fcc4e425 *_wp_adj_args)
{
    wp::tile_shared_storage_t tile_mem;
#if defined(WP_ENABLE_TILES_IN_STACK_MEMORY)
    wp::shared_tile_storage = &tile_mem;
#endif

    for (size_t task_index = 0; task_index < dim->size; ++task_index)
    {
        add_forces_to_dual_buffers_index_fcc4e425_cpu_kernel_backward(*dim, task_index, _wp_args, _wp_adj_args);
    }
}

} // extern C


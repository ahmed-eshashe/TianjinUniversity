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



extern "C" __global__ void samples_0631dbf4_cuda_kernel_forward(
    wp::launch_bounds_t<1> dim,
    wp::uint64 var_mesh,
    wp::mat_t<3, 3, wp::float32> var_R,
    wp::vec_t<3, wp::float32> var_T0,
    wp::vec_t<3, wp::float32> var_travel,
    wp::float32 var_load,
    wp::float32 var_hold,
    wp::array_t<wp::float32> var_clock,
    wp::array_t<wp::int32> var_ptr,
    wp::array_t<wp::int32> var_ids,
    wp::array_t<wp::float32> var_w,
    wp::array_t<wp::vec_t<3, wp::float32>> var_X,
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
        wp::float32* var_2;
        wp::float32 var_3;
        wp::float32 var_4;
        const wp::float32 var_5 = 0.0;
        wp::float32 var_6;
        const wp::float32 var_7 = 0.0;
        wp::float32 var_8;
        bool var_9;
        const wp::float32 var_10 = 0.5;
        const wp::float32 var_11 = 1.0;
        const wp::float32 var_12 = 3.141592653589793;
        wp::float32 var_13;
        wp::float32 var_14;
        wp::float32 var_15;
        wp::float32 var_16;
        wp::float32 var_17;
        const wp::float32 var_18 = 0.5;
        const wp::float32 var_19 = 3.141592653589793;
        wp::float32 var_20;
        wp::float32 var_21;
        const wp::float32 var_22 = 3.141592653589793;
        wp::float32 var_23;
        wp::float32 var_24;
        wp::float32 var_25;
        wp::float32 var_26;
        wp::float32 var_27;
        bool var_28;
        const wp::float32 var_29 = 1.0;
        const wp::float32 var_30 = 2.0;
        wp::float32 var_31;
        wp::float32 var_32;
        bool var_33;
        wp::float32 var_34;
        wp::float32 var_35;
        wp::float32 var_36;
        const wp::float32 var_37 = 0.5;
        const wp::float32 var_38 = 1.0;
        const wp::float32 var_39 = 3.141592653589793;
        wp::float32 var_40;
        wp::float32 var_41;
        wp::float32 var_42;
        wp::float32 var_43;
        const wp::float32 var_44 = -0.5;
        const wp::float32 var_45 = 3.141592653589793;
        wp::float32 var_46;
        wp::float32 var_47;
        const wp::float32 var_48 = 3.141592653589793;
        wp::float32 var_49;
        wp::float32 var_50;
        wp::float32 var_51;
        wp::float32 var_52;
        wp::float32 var_53;
        wp::float32 var_54;
        wp::float32 var_55;
        wp::float32 var_56;
        wp::float32 var_57;
        wp::vec_t<3, wp::float32> var_58;
        wp::vec_t<3, wp::float32> var_59;
        wp::vec_t<3, wp::float32> var_60;
        wp::vec_t<3, wp::float32>* var_61;
        wp::vec_t<3, wp::float32> var_62;
        wp::vec_t<3, wp::float32> var_63;
        const wp::float32 var_64 = 0.0;
        wp::vec_t<3, wp::float32> var_65;
        wp::int32* var_66;
        const wp::int32 var_67 = 1;
        wp::int32 var_68;
        wp::int32* var_69;
        wp::range_t var_70;
        wp::int32 var_71;
        wp::int32 var_72;
        wp::int32 var_73;
        wp::float32* var_74;
        wp::int32* var_75;
        wp::vec_t<3, wp::float32>* var_76;
        wp::int32 var_77;
        wp::vec_t<3, wp::float32> var_78;
        wp::float32 var_79;
        wp::vec_t<3, wp::float32> var_80;
        wp::vec_t<3, wp::float32> var_81;
        wp::float32* var_82;
        wp::int32* var_83;
        wp::vec_t<3, wp::float32>* var_84;
        wp::int32 var_85;
        wp::vec_t<3, wp::float32> var_86;
        wp::float32 var_87;
        wp::vec_t<3, wp::float32> var_88;
        wp::vec_t<3, wp::float32> var_89;
        wp::mat_t<3, 3, wp::float32> var_90;
        wp::vec_t<3, wp::float32> var_91;
        wp::vec_t<3, wp::float32> var_92;
        const wp::float32 var_93 = 10.0;
        wp::mesh_query_point_t var_94;
        const wp::float32 var_95 = 2.0;
        const wp::float32 var_96 = 0.5;
        const wp::float32 var_97 = 100.0;
        wp::float32 var_98;
        const wp::float32 var_99 = 0.0;
        wp::vec_t<3, wp::float32> var_100;
        bool* var_101;
        bool var_102;
        wp::int32* var_103;
        wp::float32* var_104;
        wp::float32* var_105;
        wp::vec_t<3, wp::float32> var_106;
        wp::int32 var_107;
        wp::float32 var_108;
        wp::float32 var_109;
        wp::vec_t<3, wp::float32> var_110;
        wp::float32 var_111;
        wp::float32* var_112;
        wp::float32 var_113;
        wp::float32 var_114;
        const wp::float32 var_115 = 1e-12;
        bool var_116;
        wp::float32* var_117;
        wp::vec_t<3, wp::float32> var_118;
        wp::float32 var_119;
        wp::vec_t<3, wp::float32> var_120;
        wp::vec_t<3, wp::float32> var_121;
        wp::int32* var_122;
        wp::vec_t<3, wp::float32> var_123;
        wp::int32 var_124;
        wp::vec_t<3, wp::float32> var_125;
        wp::vec_t<3, wp::float32> var_126;
        bool var_127;
        wp::float32 var_128;
        bool var_129;
        wp::vec_t<3, wp::float32> var_130;
        bool var_131;
        const wp::int32 var_132 = 1;
        bool var_133;
        const wp::int32 var_134 = 1;
        wp::float32 var_135;
        const wp::int32 var_136 = 1;
        wp::float32 var_137;
        wp::float32 var_138;
        const wp::float32 var_139 = 0.0;
        const wp::float32 var_140 = -1.0;
        const wp::float32 var_141 = 0.0;
        wp::vec_t<3, wp::float32> var_142;
        wp::float32 var_143;
        wp::vec_t<3, wp::float32> var_144;
        wp::float32 var_145;
        const wp::float32 var_146 = 0.0;
        wp::float32 var_147;
        const wp::float32 var_148 = 1000000000.0;
        wp::float32* var_149;
        wp::float32 var_150;
        wp::float32 var_151;
        wp::float32 var_152;
        wp::vec_t<3, wp::float32> var_153;
        wp::float32 var_154;
        wp::vec_t<3, wp::float32> var_155;
        wp::vec_t<3, wp::float32> var_156;
        wp::float32 var_157;
        const wp::float32 var_158 = 0.0;
        wp::vec_t<3, wp::float32> var_159;
        const wp::float32 var_160 = 1e-30;
        bool var_161;
        const wp::float32 var_162 = -0.2;
        wp::float32 var_163;
        const wp::float32 var_164 = 0.001;
        wp::float32 var_165;
        wp::float32 var_166;
        wp::float32 var_167;
        wp::vec_t<3, wp::float32> var_168;
        wp::vec_t<3, wp::float32> var_169;
        wp::vec_t<3, wp::float32> var_170;
        wp::vec_t<3, wp::float32> var_171;
        wp::vec_t<3, wp::float32> var_172;
        const wp::float32 var_173 = 0.5;
        const wp::float32 var_174 = 1000000000.0;
        wp::float32 var_175;
        wp::float32* var_176;
        wp::float32 var_177;
        wp::float32 var_178;
        wp::float32 var_179;
        wp::float32 var_180;
        wp::float32 var_181;
        wp::float32 var_182;
        wp::float32 var_183;
        wp::vec_t<3, wp::float32> var_184;
        wp::vec_t<3, wp::float32> var_185;
        //---------
        // forward
        // def samples(mesh:wp.uint64,R:wp.mat33,T0:wp.vec3,travel:wp.vec3,load:float,hold:float,clock:wp.array(dtype=float),ptr:wp.array(dtype=int),ids:wp.array(dtype=int),w:wp.array(dtype=float),X:wp.array(dtype=wp.vec3),A:wp.array(dtype=float),u:wp.array(dtype=wp.vec3),v:wp.array(dtype=wp.vec3),cf:wp.array(dtype=wp.vec3),cu:wp.array(dtype=float),cp:wp.array(dtype=float),power:wp.array(dtype=float),moment:wp.array(dtype=wp.vec3),phiout:wp.array(dtype=float),mode:int):       <L 12>
        // i=wp.tid();t=clock[0];s=float(0.);speed=float(0.)                                      <L 13>
        var_0 = builtin_tid1d();
        var_2 = wp::address(var_clock, var_1);
        var_4 = wp::load(var_2);
        var_3 = wp::copy(var_4);
        var_6 = wp::float(var_5);
        var_8 = wp::float(var_7);
        // if t<load:s=.5*(1.-wp.cos(wp.pi*t/load));speed=.5*wp.pi/load*wp.sin(wp.pi*t/load)       <L 14>
        var_9 = (var_3 < var_load);
        if (var_9) {
            var_13 = wp::mul(var_12, var_3);
            var_14 = wp::div(var_13, var_load);
            var_15 = wp::cos(var_14);
            var_16 = wp::sub(var_11, var_15);
            var_17 = wp::mul(var_10, var_16);
            var_20 = wp::mul(var_18, var_19);
            var_21 = wp::div(var_20, var_load);
            var_23 = wp::mul(var_22, var_3);
            var_24 = wp::div(var_23, var_load);
            var_25 = wp::sin(var_24);
            var_26 = wp::mul(var_21, var_25);
        }
        if (!var_9) {
            // elif t<load+hold:s=1.                                                              <L 15>
            var_27 = wp::add(var_load, var_hold);
            var_28 = (var_3 < var_27);
            if (var_28) {
            }
            if (!var_28) {
                // elif t<2.*load+hold:                                                           <L 16>
                var_31 = wp::mul(var_30, var_load);
                var_32 = wp::add(var_31, var_hold);
                var_33 = (var_3 < var_32);
                if (var_33) {
                    // a=(t-load-hold)/load;s=.5*(1.+wp.cos(wp.pi*a));speed=-.5*wp.pi/load*wp.sin(wp.pi*a)       <L 17>
                    var_34 = wp::sub(var_3, var_load);
                    var_35 = wp::sub(var_34, var_hold);
                    var_36 = wp::div(var_35, var_load);
                    var_40 = wp::mul(var_39, var_36);
                    var_41 = wp::cos(var_40);
                    var_42 = wp::add(var_38, var_41);
                    var_43 = wp::mul(var_37, var_42);
                    var_46 = wp::mul(var_44, var_45);
                    var_47 = wp::div(var_46, var_load);
                    var_49 = wp::mul(var_48, var_36);
                    var_50 = wp::sin(var_49);
                    var_51 = wp::mul(var_47, var_50);
                }
                var_52 = wp::where(var_33, var_43, var_6);
                var_53 = wp::where(var_33, var_51, var_8);
            }
            var_54 = wp::where(var_28, var_29, var_52);
            var_55 = wp::where(var_28, var_8, var_53);
        }
        var_56 = wp::where(var_9, var_17, var_54);
        var_57 = wp::where(var_9, var_26, var_55);
        // T=T0+travel*s;tv=travel*speed;x=X[i];vel=wp.vec3(0.)                                   <L 18>
        var_58 = wp::mul(var_travel, var_56);
        var_59 = wp::add(var_T0, var_58);
        var_60 = wp::mul(var_travel, var_57);
        var_61 = wp::address(var_X, var_0);
        var_63 = wp::load(var_61);
        var_62 = wp::copy(var_63);
        var_65 = wp::vec_t<3, wp::float32>(var_64);
        // for k in range(ptr[i],ptr[i+1]):x+=w[k]*u[ids[k]];vel+=w[k]*v[ids[k]]                  <L 19>
        var_66 = wp::address(var_ptr, var_0);
        var_68 = wp::add(var_0, var_67);
        var_69 = wp::address(var_ptr, var_68);
        var_71 = wp::load(var_66);
        var_72 = wp::load(var_69);
        var_70 = wp::range(var_71, var_72);
        start_for_0:;
            if (iter_cmp(var_70) == 0) goto end_for_0;
            var_73 = wp::iter_next(var_70);
            var_74 = wp::address(var_w, var_73);
            var_75 = wp::address(var_ids, var_73);
            var_77 = wp::load(var_75);
            var_76 = wp::address(var_u, var_77);
            var_79 = wp::load(var_74);
            var_80 = wp::load(var_76);
            var_78 = wp::mul(var_79, var_80);
            var_81 = wp::add(var_62, var_78);
            var_82 = wp::address(var_w, var_73);
            var_83 = wp::address(var_ids, var_73);
            var_85 = wp::load(var_83);
            var_84 = wp::address(var_v, var_85);
            var_87 = wp::load(var_82);
            var_88 = wp::load(var_84);
            var_86 = wp::mul(var_87, var_88);
            var_89 = wp::add(var_65, var_86);
            wp::assign(var_62, var_81);
            wp::assign(var_65, var_89);
            goto start_for_0;
        end_for_0:;
        // p=wp.transpose(R)*(x-T);r=wp.mesh_query_point_sign_winding_number(mesh,p,10.);phi=float(100.);normal=wp.vec3(0.)       <L 20>
        var_90 = wp::transpose(var_R);
        var_91 = wp::sub(var_62, var_59);
        var_92 = wp::mul(var_90, var_91);
        var_94 = wp::mesh_query_point_sign_winding_number(var_mesh, var_92, var_93, var_95, var_96);
        var_98 = wp::float(var_97);
        var_100 = wp::vec_t<3, wp::float32>(var_99);
        // if r.result:                                                                           <L 21>
        var_101 = &((var_94).result);
        var_102 = wp::load(var_101);
        if (var_102) {
            // c=wp.mesh_eval_position(mesh,r.face,r.u,r.v);d=p-c;l=wp.length(d);phi=r.sign*l       <L 22>
            var_103 = &((var_94).face);
            var_104 = &((var_94).u);
            var_105 = &((var_94).v);
            var_107 = wp::load(var_103);
            var_108 = wp::load(var_104);
            var_109 = wp::load(var_105);
            var_106 = wp::mesh_eval_position(var_mesh, var_107, var_108, var_109);
            var_110 = wp::sub(var_92, var_106);
            var_111 = wp::length(var_110);
            var_112 = &((var_94).sign);
            var_114 = wp::load(var_112);
            var_113 = wp::mul(var_114, var_111);
            // if l>1.e-12:normal=R*(r.sign*d/l)                                                  <L 23>
            var_116 = (var_111 > var_115);
            if (var_116) {
                var_117 = &((var_94).sign);
                var_119 = wp::load(var_117);
                var_118 = wp::mul(var_119, var_110);
                var_120 = wp::div(var_118, var_111);
                var_121 = wp::mul(var_R, var_120);
            }
            if (!var_116) {
                // else:normal=R*wp.mesh_eval_face_normal(mesh,r.face)                            <L 24>
                var_122 = &((var_94).face);
                var_124 = wp::load(var_122);
                var_123 = wp::mesh_eval_face_normal(var_mesh, var_124);
                var_125 = wp::mul(var_R, var_123);
            }
            var_126 = wp::where(var_116, var_121, var_125);
        }
        var_127 = wp::load(var_101);
        var_129 = wp::load(var_101);
        var_128 = wp::where(var_129, var_113, var_98);
        var_131 = wp::load(var_101);
        var_130 = wp::where(var_131, var_126, var_100);
        // if mode==1:phi=T[1]-x[1];normal=wp.vec3(0.,-1.,0.) # analytical plane only             <L 25>
        var_133 = (var_mode == var_132);
        if (var_133) {
            var_135 = wp::extract(var_59, var_134);
            var_137 = wp::extract(var_62, var_136);
            var_138 = wp::sub(var_135, var_137);
            var_142 = wp::vec_t<3, wp::float32>(var_139, var_140, var_141);
        }
        var_143 = wp::where(var_133, var_138, var_128);
        var_144 = wp::where(var_133, var_142, var_130);
        // depth=wp.max(-phi,0.);fn=1.e9*A[i]*depth;rel=vel-tv;tangent=rel-wp.dot(rel,normal)*normal;vs=wp.length(tangent);fr=wp.vec3(0.)       <L 26>
        var_145 = wp::neg(var_143);
        var_147 = wp::max(var_145, var_146);
        var_149 = wp::address(var_A, var_0);
        var_151 = wp::load(var_149);
        var_150 = wp::mul(var_148, var_151);
        var_152 = wp::mul(var_150, var_147);
        var_153 = wp::sub(var_65, var_60);
        var_154 = wp::dot(var_153, var_144);
        var_155 = wp::mul(var_154, var_144);
        var_156 = wp::sub(var_153, var_155);
        var_157 = wp::length(var_156);
        var_159 = wp::vec_t<3, wp::float32>(var_158);
        // if vs>1.e-30:fr=-.2*fn*wp.tanh(vs/.001)*tangent/vs                                     <L 27>
        var_161 = (var_157 > var_160);
        if (var_161) {
            var_163 = wp::mul(var_162, var_152);
            var_165 = wp::div(var_157, var_164);
            var_166 = wp::tanh(var_165);
            var_167 = wp::mul(var_163, var_166);
            var_168 = wp::mul(var_167, var_156);
            var_169 = wp::div(var_168, var_157);
        }
        var_170 = wp::where(var_161, var_169, var_159);
        // f=fn*normal+fr;cf[i]=f;cu[i]=.5*1.e9*A[i]*depth*depth;cp[i]=-wp.dot(fr,rel);power[i]=wp.dot(f,tv);moment[i]=wp.cross(x-T,f);phiout[i]=phi       <L 28>
        var_171 = wp::mul(var_152, var_144);
        var_172 = wp::add(var_171, var_170);
        wp::array_store(var_cf, var_0, var_172);
        var_175 = wp::mul(var_173, var_174);
        var_176 = wp::address(var_A, var_0);
        var_178 = wp::load(var_176);
        var_177 = wp::mul(var_175, var_178);
        var_179 = wp::mul(var_177, var_147);
        var_180 = wp::mul(var_179, var_147);
        wp::array_store(var_cu, var_0, var_180);
        var_181 = wp::dot(var_170, var_153);
        var_182 = wp::neg(var_181);
        wp::array_store(var_cp, var_0, var_182);
        var_183 = wp::dot(var_172, var_60);
        wp::array_store(var_power, var_0, var_183);
        var_184 = wp::sub(var_62, var_59);
        var_185 = wp::cross(var_184, var_172);
        wp::array_store(var_moment, var_0, var_185);
        wp::array_store(var_phiout, var_0, var_143);
    }
}



extern "C" __global__ void ledger_4901a6e5_cuda_kernel_forward(
    wp::launch_bounds_t<1> dim,
    wp::array_t<wp::vec_t<3, wp::float32>> var_cf,
    wp::array_t<wp::float32> var_cp,
    wp::array_t<wp::float32> var_power,
    wp::array_t<wp::vec_t<3, wp::float32>> var_moment,
    wp::array_t<wp::vec_t<3, wp::float32>> var_impulse,
    wp::array_t<wp::vec_t<3, wp::float32>> var_angular,
    wp::array_t<wp::float32> var_work,
    wp::array_t<wp::float32> var_diss,
    wp::float32 var_dt,
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
        const wp::int32 var_1 = 0;
        wp::int32* var_2;
        const wp::int32 var_3 = 0;
        bool var_4;
        wp::int32 var_5;
        wp::vec_t<3, wp::float32>* var_6;
        wp::vec_t<3, wp::float32> var_7;
        wp::vec_t<3, wp::float32> var_8;
        wp::vec_t<3, wp::float32> var_9;
        wp::vec_t<3, wp::float32>* var_10;
        wp::vec_t<3, wp::float32> var_11;
        wp::vec_t<3, wp::float32> var_12;
        wp::vec_t<3, wp::float32> var_13;
        wp::float32* var_14;
        wp::float32 var_15;
        wp::float32 var_16;
        wp::float32 var_17;
        wp::float32* var_18;
        wp::float32 var_19;
        wp::float32 var_20;
        wp::float32 var_21;
        //---------
        // forward
        // def ledger(cf:wp.array(dtype=wp.vec3),cp:wp.array(dtype=float),power:wp.array(dtype=float),moment:wp.array(dtype=wp.vec3),impulse:wp.array(dtype=wp.vec3),angular:wp.array(dtype=wp.vec3),work:wp.array(dtype=float),diss:wp.array(dtype=float),dt:float,bad:wp.array(dtype=int)):       <L 67>
        // i=wp.tid()                                                                             <L 68>
        var_0 = builtin_tid1d();
        // if bad[0]==0:impulse[i]+=dt*cf[i];angular[i]+=dt*moment[i];work[i]+=dt*power[i];diss[i]+=dt*cp[i]       <L 69>
        var_2 = wp::address(var_bad, var_1);
        var_5 = wp::load(var_2);
        var_4 = (var_5 == var_3);
        if (var_4) {
            var_6 = wp::address(var_cf, var_0);
            var_8 = wp::load(var_6);
            var_7 = wp::mul(var_dt, var_8);
            var_9 = wp::atomic_add(var_impulse, var_0, var_7);
            var_10 = wp::address(var_moment, var_0);
            var_12 = wp::load(var_10);
            var_11 = wp::mul(var_dt, var_12);
            var_13 = wp::atomic_add(var_angular, var_0, var_11);
            var_14 = wp::address(var_power, var_0);
            var_16 = wp::load(var_14);
            var_15 = wp::mul(var_dt, var_16);
            var_17 = wp::atomic_add(var_work, var_0, var_15);
            var_18 = wp::address(var_cp, var_0);
            var_20 = wp::load(var_18);
            var_19 = wp::mul(var_dt, var_20);
            var_21 = wp::atomic_add(var_diss, var_0, var_19);
        }
    }
}



extern "C" __global__ void kick_6022e0b1_cuda_kernel_forward(
    wp::launch_bounds_t<1> dim,
    wp::array_t<wp::int32> var_mptr,
    wp::array_t<wp::int32> var_midx,
    wp::array_t<wp::float32> var_mi,
    wp::array_t<wp::vec_t<3, wp::float32>> var_force,
    wp::array_t<wp::vec_t<3, wp::float32>> var_v,
    wp::array_t<wp::int32> var_fixed,
    wp::array_t<wp::vec_t<3, wp::float32>> var_support,
    wp::float32 var_dt,
    wp::int32 var_n,
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
        bool var_2;
        const wp::int32 var_3 = 0;
        wp::int32* var_4;
        const wp::int32 var_5 = 0;
        bool var_6;
        wp::int32 var_7;
        wp::int32* var_8;
        const wp::int32 var_9 = 0;
        bool var_10;
        wp::int32 var_11;
        wp::vec_t<3, wp::float32>* var_12;
        wp::vec_t<3, wp::float32> var_13;
        wp::vec_t<3, wp::float32> var_14;
        wp::vec_t<3, wp::float32> var_15;
        const wp::float32 var_16 = 0.0;
        wp::vec_t<3, wp::float32> var_17;
        const wp::float32 var_18 = 0.0;
        wp::vec_t<3, wp::float32> var_19;
        wp::int32* var_20;
        const wp::int32 var_21 = 1;
        wp::int32 var_22;
        wp::int32* var_23;
        wp::range_t var_24;
        wp::int32 var_25;
        wp::int32 var_26;
        wp::int32 var_27;
        wp::float32* var_28;
        wp::int32* var_29;
        wp::vec_t<3, wp::float32>* var_30;
        wp::int32 var_31;
        wp::vec_t<3, wp::float32> var_32;
        wp::float32 var_33;
        wp::vec_t<3, wp::float32> var_34;
        wp::vec_t<3, wp::float32> var_35;
        wp::vec_t<3, wp::float32> var_36;
        wp::vec_t<3, wp::float32> var_37;
        //---------
        // forward
        // def kick(mptr:wp.array(dtype=int),midx:wp.array(dtype=int),mi:wp.array(dtype=float),force:wp.array(dtype=wp.vec3),v:wp.array(dtype=wp.vec3),fixed:wp.array(dtype=int),support:wp.array(dtype=wp.vec3),dt:float,n:int,bad:wp.array(dtype=int)):       <L 47>
        // i=wp.tid()                                                                             <L 48>
        var_0 = builtin_tid1d();
        // if i<n and bad[0]==0:                                                                  <L 49>
        var_2 = (var_0 < var_n);
        var_1 = var_2;
        if (var_1) {
            var_4 = wp::address(var_bad, var_3);
            var_7 = wp::load(var_4);
            var_6 = (var_7 == var_5);
            var_1 = var_1 && var_6;
        }
        if (var_1) {
            // if fixed[i]!=0:support[i]-=dt*force[i];v[i]=wp.vec3(0.)                            <L 50>
            var_8 = wp::address(var_fixed, var_0);
            var_11 = wp::load(var_8);
            var_10 = (var_11 != var_9);
            if (var_10) {
                var_12 = wp::address(var_force, var_0);
                var_14 = wp::load(var_12);
                var_13 = wp::mul(var_dt, var_14);
                var_15 = wp::atomic_sub(var_support, var_0, var_13);
                var_17 = wp::vec_t<3, wp::float32>(var_16);
                wp::array_store(var_v, var_0, var_17);
            }
            if (!var_10) {
                // acc=wp.vec3(0.)                                                                <L 52>
                var_19 = wp::vec_t<3, wp::float32>(var_18);
                // for k in range(mptr[i],mptr[i+1]):acc+=mi[k]*force[midx[k]]                    <L 53>
                var_20 = wp::address(var_mptr, var_0);
                var_22 = wp::add(var_0, var_21);
                var_23 = wp::address(var_mptr, var_22);
                var_25 = wp::load(var_20);
                var_26 = wp::load(var_23);
                var_24 = wp::range(var_25, var_26);
                start_for_0:;
                    if (iter_cmp(var_24) == 0) goto end_for_0;
                    var_27 = wp::iter_next(var_24);
                    var_28 = wp::address(var_mi, var_27);
                    var_29 = wp::address(var_midx, var_27);
                    var_31 = wp::load(var_29);
                    var_30 = wp::address(var_force, var_31);
                    var_33 = wp::load(var_28);
                    var_34 = wp::load(var_30);
                    var_32 = wp::mul(var_33, var_34);
                    var_35 = wp::add(var_19, var_32);
                    wp::assign(var_19, var_35);
                    goto start_for_0;
                end_for_0:;
                // v[i]+=dt*acc                                                                   <L 54>
                var_36 = wp::mul(var_dt, var_19);
                var_37 = wp::atomic_add(var_v, var_0, var_36);
            }
        }
    }
}



extern "C" __global__ void tick_68454d84_cuda_kernel_forward(
    wp::launch_bounds_t<1> dim,
    wp::array_t<wp::float32> var_clock,
    wp::float32 var_dt,
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
        wp::float32 var_6;
        //---------
        // forward
        // def tick(clock:wp.array(dtype=float),dt:float,bad:wp.array(dtype=int)):                <L 63>
        // if bad[0]==0:clock[0]+=dt                                                              <L 64>
        var_1 = wp::address(var_bad, var_0);
        var_4 = wp::load(var_1);
        var_3 = (var_4 == var_2);
        if (var_3) {
            var_6 = wp::atomic_add(var_clock, var_5, var_dt);
        }
    }
}



extern "C" __global__ void drift_7933513b_cuda_kernel_forward(
    wp::launch_bounds_t<1> dim,
    wp::array_t<wp::vec_t<3, wp::float32>> var_q,
    wp::array_t<wp::vec_t<3, wp::float32>> var_v,
    wp::float32 var_dt,
    wp::int32 var_n,
    wp::array_t<wp::int32> var_bad,
    wp::array_t<wp::float32> var_maxspeed)
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
        bool var_2;
        const wp::int32 var_3 = 0;
        wp::int32* var_4;
        const wp::int32 var_5 = 0;
        bool var_6;
        wp::int32 var_7;
        const wp::int32 var_8 = 0;
        wp::vec_t<3, wp::float32>* var_9;
        wp::float32 var_10;
        wp::vec_t<3, wp::float32> var_11;
        wp::float32 var_12;
        wp::vec_t<3, wp::float32>* var_13;
        wp::vec_t<3, wp::float32> var_14;
        wp::vec_t<3, wp::float32> var_15;
        wp::vec_t<3, wp::float32> var_16;
        //---------
        // forward
        // def drift(q:wp.array(dtype=wp.vec3),v:wp.array(dtype=wp.vec3),dt:float,n:int,bad:wp.array(dtype=int),maxspeed:wp.array(dtype=float)):       <L 57>
        // i=wp.tid()                                                                             <L 58>
        var_0 = builtin_tid1d();
        // if i<n and bad[0]==0:                                                                  <L 59>
        var_2 = (var_0 < var_n);
        var_1 = var_2;
        if (var_1) {
            var_4 = wp::address(var_bad, var_3);
            var_7 = wp::load(var_4);
            var_6 = (var_7 == var_5);
            var_1 = var_1 && var_6;
        }
        if (var_1) {
            // wp.atomic_max(maxspeed,0,wp.length(v[i]));q[i]+=dt*v[i]                            <L 60>
            var_9 = wp::address(var_v, var_0);
            var_11 = wp::load(var_9);
            var_10 = wp::length(var_11);
            var_12 = wp::atomic_max(var_maxspeed, var_8, var_10);
            var_13 = wp::address(var_v, var_0);
            var_15 = wp::load(var_13);
            var_14 = wp::mul(var_dt, var_15);
            var_16 = wp::atomic_add(var_q, var_0, var_14);
        }
    }
}



extern "C" __global__ void pullback_d6698a46_cuda_kernel_forward(
    wp::launch_bounds_t<1> dim,
    wp::array_t<wp::int32> var_ptr,
    wp::array_t<wp::int32> var_ids,
    wp::array_t<wp::float32> var_w,
    wp::array_t<wp::vec_t<3, wp::float32>> var_cf,
    wp::array_t<wp::vec_t<3, wp::float32>> var_external,
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
        bool var_1;
        const wp::float32 var_2 = 0.0;
        wp::vec_t<3, wp::float32> var_3;
        wp::int32* var_4;
        const wp::int32 var_5 = 1;
        wp::int32 var_6;
        wp::int32* var_7;
        wp::range_t var_8;
        wp::int32 var_9;
        wp::int32 var_10;
        wp::int32 var_11;
        wp::float32* var_12;
        wp::int32* var_13;
        wp::vec_t<3, wp::float32>* var_14;
        wp::int32 var_15;
        wp::vec_t<3, wp::float32> var_16;
        wp::float32 var_17;
        wp::vec_t<3, wp::float32> var_18;
        wp::vec_t<3, wp::float32> var_19;
        //---------
        // forward
        // def pullback(ptr:wp.array(dtype=int),ids:wp.array(dtype=int),w:wp.array(dtype=float),cf:wp.array(dtype=wp.vec3),external:wp.array(dtype=wp.vec3),n:int):       <L 31>
        // i=wp.tid()                                                                             <L 32>
        var_0 = builtin_tid1d();
        // if i<n:                                                                                <L 33>
        var_1 = (var_0 < var_n);
        if (var_1) {
            // f=wp.vec3(0.)                                                                      <L 34>
            var_3 = wp::vec_t<3, wp::float32>(var_2);
            // for k in range(ptr[i],ptr[i+1]):f+=w[k]*cf[ids[k]]                                 <L 35>
            var_4 = wp::address(var_ptr, var_0);
            var_6 = wp::add(var_0, var_5);
            var_7 = wp::address(var_ptr, var_6);
            var_9 = wp::load(var_4);
            var_10 = wp::load(var_7);
            var_8 = wp::range(var_9, var_10);
            start_for_0:;
                if (iter_cmp(var_8) == 0) goto end_for_0;
                var_11 = wp::iter_next(var_8);
                var_12 = wp::address(var_w, var_11);
                var_13 = wp::address(var_ids, var_11);
                var_15 = wp::load(var_13);
                var_14 = wp::address(var_cf, var_15);
                var_17 = wp::load(var_12);
                var_18 = wp::load(var_14);
                var_16 = wp::mul(var_17, var_18);
                var_19 = wp::add(var_3, var_16);
                wp::assign(var_3, var_19);
                goto start_for_0;
            end_for_0:;
            // external[i]=f                                                                      <L 36>
            wp::array_store(var_external, var_0, var_3);
        }
    }
}



extern "C" __global__ void guard_f8a98f0a_cuda_kernel_forward(
    wp::launch_bounds_t<1> dim,
    wp::array_t<wp::vec_t<3, wp::float32>> var_cf,
    wp::array_t<wp::int32> var_bad,
    wp::array_t<wp::float32> var_peak,
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
        const wp::int32 var_1 = 0;
        bool var_2;
        const wp::float32 var_3 = 0.0;
        wp::vec_t<3, wp::float32> var_4;
        const wp::float32 var_5 = 0.0;
        wp::float32 var_6;
        wp::range_t var_7;
        wp::int32 var_8;
        wp::vec_t<3, wp::float32>* var_9;
        wp::vec_t<3, wp::float32> var_10;
        wp::vec_t<3, wp::float32> var_11;
        wp::vec_t<3, wp::float32>* var_12;
        wp::float32 var_13;
        wp::vec_t<3, wp::float32> var_14;
        wp::float32 var_15;
        wp::float32 var_16;
        wp::float32 var_17;
        const wp::int32 var_18 = 0;
        wp::float32* var_19;
        wp::float32 var_20;
        wp::float32 var_21;
        const wp::int32 var_22 = 0;
        bool var_23;
        const wp::float32 var_24 = 2.0;
        bool var_25;
        bool var_26;
        bool var_27;
        const wp::int32 var_28 = 0;
        const wp::int32 var_29 = 3;
        wp::int32 var_30;
        //---------
        // forward
        // def guard(cf:wp.array(dtype=wp.vec3),bad:wp.array(dtype=int),peak:wp.array(dtype=float),n:int):       <L 39>
        // if wp.tid()==0:                                                                        <L 40>
        var_0 = builtin_tid1d();
        var_2 = (var_0 == var_1);
        if (var_2) {
            // total=wp.vec3(0.);mag=float(0.)                                                    <L 41>
            var_4 = wp::vec_t<3, wp::float32>(var_3);
            var_6 = wp::float(var_5);
            // for i in range(n):total+=cf[i];mag+=wp.length(cf[i])                               <L 42>
            var_7 = wp::range(var_n);
            start_for_0:;
                if (iter_cmp(var_7) == 0) goto end_for_0;
                var_8 = wp::iter_next(var_7);
                var_9 = wp::address(var_cf, var_8);
                var_11 = wp::load(var_9);
                var_10 = wp::add(var_4, var_11);
                var_12 = wp::address(var_cf, var_8);
                var_14 = wp::load(var_12);
                var_13 = wp::length(var_14);
                var_15 = wp::add(var_6, var_13);
                wp::assign(var_4, var_10);
                wp::assign(var_6, var_15);
                goto start_for_0;
            end_for_0:;
            // value=wp.max(mag,wp.length(total));peak[0]=wp.max(peak[0],value)                   <L 43>
            var_16 = wp::length(var_4);
            var_17 = wp::max(var_6, var_16);
            var_19 = wp::address(var_peak, var_18);
            var_21 = wp::load(var_19);
            var_20 = wp::max(var_21, var_17);
            wp::array_store(var_peak, var_22, var_20);
            // if value>2. or not wp.isfinite(value):wp.atomic_max(bad,0,3)                       <L 44>
            var_25 = (var_17 > var_24);
            var_23 = var_25;
            if (!var_23) {
                var_26 = wp::isfinite(var_17);
                var_27 = wp::unot(var_26);
                var_23 = var_23 || var_27;
            }
            if (var_23) {
                var_30 = wp::atomic_max(var_bad, var_28, var_29);
            }
        }
    }
}


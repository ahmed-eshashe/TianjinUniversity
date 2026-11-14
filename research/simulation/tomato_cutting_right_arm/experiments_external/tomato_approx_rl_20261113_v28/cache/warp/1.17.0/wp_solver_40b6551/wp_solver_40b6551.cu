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


// /home/omen/Documents/Codex/experiments/tomato_approx_rl_20261113_v28/src/solver.py:64
static CUDA_CALLABLE void knife_normal_0(
    wp::vec_t<3, wp::float32> var_p,
    wp::float32 var_half_length,
    wp::vec_t<3, wp::float32> & ret_0,
    wp::float32 & ret_1)
{
    //---------
    // primal vars
    const wp::int32 var_0 = 0;
    wp::float32 var_1;
    const wp::int32 var_2 = 1;
    wp::float32 var_3;
    wp::vec_t<2, wp::float32> var_4;
    const wp::float32 var_5 = 1000000000.0;
    wp::float32 var_6;
    const wp::float32 var_7 = 0.0;
    wp::vec_t<2, wp::float32> var_8;
    const wp::int32 var_9 = 0;
    const wp::float32 var_10 = 0.0;
    const wp::float32 var_11 = 0.0;
    wp::vec_t<2, wp::float32> var_12;
    const wp::float32 var_13 = 0.0005;
    const wp::float32 var_14 = 0.03;
    wp::vec_t<2, wp::float32> var_15;
    const wp::int32 var_16 = 1;
    bool var_17;
    const wp::float32 var_18 = 0.0005;
    const wp::float32 var_19 = 0.03;
    wp::vec_t<2, wp::float32> var_20;
    const wp::float32 var_21 = -0.0005;
    const wp::float32 var_22 = 0.03;
    wp::vec_t<2, wp::float32> var_23;
    wp::vec_t<2, wp::float32> var_24;
    wp::vec_t<2, wp::float32> var_25;
    const wp::int32 var_26 = 2;
    bool var_27;
    const wp::float32 var_28 = -0.0005;
    const wp::float32 var_29 = 0.03;
    wp::vec_t<2, wp::float32> var_30;
    const wp::float32 var_31 = 0.0;
    const wp::float32 var_32 = 0.0;
    wp::vec_t<2, wp::float32> var_33;
    wp::vec_t<2, wp::float32> var_34;
    wp::vec_t<2, wp::float32> var_35;
    wp::vec_t<2, wp::float32> var_36;
    wp::vec_t<2, wp::float32> var_37;
    wp::float32 var_38;
    wp::float32 var_39;
    wp::float32 var_40;
    const wp::float32 var_41 = 0.0;
    const wp::float32 var_42 = 1.0;
    wp::float32 var_43;
    wp::vec_t<2, wp::float32> var_44;
    wp::vec_t<2, wp::float32> var_45;
    wp::vec_t<2, wp::float32> var_46;
    wp::float32 var_47;
    bool var_48;
    wp::float32 var_49;
    wp::vec_t<2, wp::float32> var_50;
    wp::float32 var_51;
    wp::vec_t<2, wp::float32> var_52;
    const wp::int32 var_53 = 1;
    const wp::float32 var_54 = 0.0;
    const wp::float32 var_55 = 0.0;
    wp::vec_t<2, wp::float32> var_56;
    const wp::float32 var_57 = 0.0005;
    const wp::float32 var_58 = 0.03;
    wp::vec_t<2, wp::float32> var_59;
    const wp::int32 var_60 = 1;
    bool var_61;
    const wp::float32 var_62 = 0.0005;
    const wp::float32 var_63 = 0.03;
    wp::vec_t<2, wp::float32> var_64;
    const wp::float32 var_65 = -0.0005;
    const wp::float32 var_66 = 0.03;
    wp::vec_t<2, wp::float32> var_67;
    wp::vec_t<2, wp::float32> var_68;
    wp::vec_t<2, wp::float32> var_69;
    const wp::int32 var_70 = 2;
    bool var_71;
    const wp::float32 var_72 = -0.0005;
    const wp::float32 var_73 = 0.03;
    wp::vec_t<2, wp::float32> var_74;
    const wp::float32 var_75 = 0.0;
    const wp::float32 var_76 = 0.0;
    wp::vec_t<2, wp::float32> var_77;
    wp::vec_t<2, wp::float32> var_78;
    wp::vec_t<2, wp::float32> var_79;
    wp::vec_t<2, wp::float32> var_80;
    wp::vec_t<2, wp::float32> var_81;
    wp::float32 var_82;
    wp::float32 var_83;
    wp::float32 var_84;
    const wp::float32 var_85 = 0.0;
    const wp::float32 var_86 = 1.0;
    wp::float32 var_87;
    wp::vec_t<2, wp::float32> var_88;
    wp::vec_t<2, wp::float32> var_89;
    wp::vec_t<2, wp::float32> var_90;
    wp::float32 var_91;
    bool var_92;
    wp::float32 var_93;
    wp::vec_t<2, wp::float32> var_94;
    wp::float32 var_95;
    wp::vec_t<2, wp::float32> var_96;
    const wp::int32 var_97 = 2;
    const wp::float32 var_98 = 0.0;
    const wp::float32 var_99 = 0.0;
    wp::vec_t<2, wp::float32> var_100;
    const wp::float32 var_101 = 0.0005;
    const wp::float32 var_102 = 0.03;
    wp::vec_t<2, wp::float32> var_103;
    const wp::int32 var_104 = 1;
    bool var_105;
    const wp::float32 var_106 = 0.0005;
    const wp::float32 var_107 = 0.03;
    wp::vec_t<2, wp::float32> var_108;
    const wp::float32 var_109 = -0.0005;
    const wp::float32 var_110 = 0.03;
    wp::vec_t<2, wp::float32> var_111;
    wp::vec_t<2, wp::float32> var_112;
    wp::vec_t<2, wp::float32> var_113;
    const wp::int32 var_114 = 2;
    bool var_115;
    const wp::float32 var_116 = -0.0005;
    const wp::float32 var_117 = 0.03;
    wp::vec_t<2, wp::float32> var_118;
    const wp::float32 var_119 = 0.0;
    const wp::float32 var_120 = 0.0;
    wp::vec_t<2, wp::float32> var_121;
    wp::vec_t<2, wp::float32> var_122;
    wp::vec_t<2, wp::float32> var_123;
    wp::vec_t<2, wp::float32> var_124;
    wp::vec_t<2, wp::float32> var_125;
    wp::float32 var_126;
    wp::float32 var_127;
    wp::float32 var_128;
    const wp::float32 var_129 = 0.0;
    const wp::float32 var_130 = 1.0;
    wp::float32 var_131;
    wp::vec_t<2, wp::float32> var_132;
    wp::vec_t<2, wp::float32> var_133;
    wp::vec_t<2, wp::float32> var_134;
    wp::float32 var_135;
    bool var_136;
    wp::float32 var_137;
    wp::vec_t<2, wp::float32> var_138;
    wp::float32 var_139;
    wp::vec_t<2, wp::float32> var_140;
    bool var_141;
    const wp::int32 var_142 = 1;
    wp::float32 var_143;
    const wp::float32 var_144 = 0.0;
    bool var_145;
    const wp::int32 var_146 = 1;
    wp::float32 var_147;
    const wp::float32 var_148 = 0.03;
    bool var_149;
    const wp::int32 var_150 = 0;
    wp::float32 var_151;
    wp::float32 var_152;
    const wp::int32 var_153 = 1;
    wp::float32 var_154;
    const wp::float32 var_155 = 60.0;
    wp::float32 var_156;
    bool var_157;
    const wp::float32 var_158 = 1.0;
    const wp::float32 var_159 = 0.0;
    wp::vec_t<2, wp::float32> var_160;
    wp::float32 var_161;
    const wp::float32 var_162 = 1e-12;
    bool var_163;
    wp::vec_t<2, wp::float32> var_164;
    wp::vec_t<2, wp::float32> var_165;
    wp::vec_t<2, wp::float32> var_166;
    wp::float32 var_167;
    wp::vec_t<2, wp::float32> var_168;
    wp::vec_t<2, wp::float32> var_169;
    wp::float32 var_170;
    const wp::int32 var_171 = 2;
    wp::float32 var_172;
    wp::float32 var_173;
    wp::float32 var_174;
    const wp::float32 var_175 = 0.0;
    wp::float32 var_176;
    const wp::float32 var_177 = 0.0;
    wp::float32 var_178;
    wp::float32 var_179;
    wp::float32 var_180;
    wp::float32 var_181;
    wp::float32 var_182;
    wp::float32 var_183;
    const wp::float32 var_184 = 0.0;
    wp::float32 var_185;
    wp::float32 var_186;
    const wp::int32 var_187 = 0;
    wp::float32 var_188;
    const wp::int32 var_189 = 1;
    wp::float32 var_190;
    const wp::float32 var_191 = 0.0;
    wp::vec_t<3, wp::float32> var_192;
    bool var_193;
    bool var_194;
    const wp::float32 var_195 = 0.0;
    bool var_196;
    const wp::float32 var_197 = 0.0;
    const wp::float32 var_198 = 0.0;
    const wp::int32 var_199 = 2;
    wp::float32 var_200;
    wp::float32 var_201;
    wp::vec_t<3, wp::float32> var_202;
    const wp::float32 var_203 = 0.0;
    bool var_204;
    wp::float32 var_205;
    wp::float32 var_206;
    wp::float32 var_207;
    wp::float32 var_208;
    const wp::int32 var_209 = 0;
    wp::float32 var_210;
    wp::float32 var_211;
    const wp::int32 var_212 = 1;
    wp::float32 var_213;
    wp::float32 var_214;
    const wp::int32 var_215 = 2;
    wp::float32 var_216;
    wp::float32 var_217;
    wp::float32 var_218;
    wp::vec_t<3, wp::float32> var_219;
    wp::vec_t<3, wp::float32> var_220;
    wp::vec_t<3, wp::float32> var_221;
    wp::vec_t<3, wp::float32> var_222;
    //---------
    // forward
    // def knife_normal(p:wp.vec3,half_length:float):                                         <L 65>
    // q=wp.vec2(p[0],p[1]);best=float(1e9);near=wp.vec2(0.)                                  <L 67>
    var_1 = wp::extract(var_p, var_0);
    var_3 = wp::extract(var_p, var_2);
    var_4 = wp::vec_t<2, wp::float32>(var_1, var_3);
    var_6 = wp::float(var_5);
    var_8 = wp::vec_t<2, wp::float32>(var_7);
    // for k in range(3):                                                                     <L 68>
    // a=wp.vec2(0.,0.);b=wp.vec2(.0005,.03)                                                  <L 69>
    var_12 = wp::vec_t<2, wp::float32>(var_10, var_11);
    var_15 = wp::vec_t<2, wp::float32>(var_13, var_14);
    // if k==1:a=wp.vec2(.0005,.03);b=wp.vec2(-.0005,.03)                                     <L 70>
    var_17 = (var_9 == var_16);
    if (var_17) {
        var_20 = wp::vec_t<2, wp::float32>(var_18, var_19);
        var_23 = wp::vec_t<2, wp::float32>(var_21, var_22);
    }
    var_24 = wp::where(var_17, var_20, var_12);
    var_25 = wp::where(var_17, var_23, var_15);
    // if k==2:a=wp.vec2(-.0005,.03);b=wp.vec2(0.,0.)                                         <L 71>
    var_27 = (var_9 == var_26);
    if (var_27) {
        var_30 = wp::vec_t<2, wp::float32>(var_28, var_29);
        var_33 = wp::vec_t<2, wp::float32>(var_31, var_32);
    }
    var_34 = wp::where(var_27, var_30, var_24);
    var_35 = wp::where(var_27, var_33, var_25);
    // ab=b-a;t=wp.clamp(wp.dot(q-a,ab)/wp.dot(ab,ab),0.,1.);point=a+t*ab;d=wp.length(q-point)       <L 72>
    var_36 = wp::sub(var_35, var_34);
    var_37 = wp::sub(var_4, var_34);
    var_38 = wp::dot(var_37, var_36);
    var_39 = wp::dot(var_36, var_36);
    var_40 = wp::div(var_38, var_39);
    var_43 = wp::clamp(var_40, var_41, var_42);
    var_44 = wp::mul(var_43, var_36);
    var_45 = wp::add(var_34, var_44);
    var_46 = wp::sub(var_4, var_45);
    var_47 = wp::length(var_46);
    // if d<best:best=d;near=point                                                            <L 73>
    var_48 = (var_47 < var_6);
    if (var_48) {
        var_49 = wp::copy(var_47);
        var_50 = wp::copy(var_45);
    }
    var_51 = wp::where(var_48, var_49, var_6);
    var_52 = wp::where(var_48, var_50, var_8);
    // a=wp.vec2(0.,0.);b=wp.vec2(.0005,.03)                                                  <L 69>
    var_56 = wp::vec_t<2, wp::float32>(var_54, var_55);
    var_59 = wp::vec_t<2, wp::float32>(var_57, var_58);
    // if k==1:a=wp.vec2(.0005,.03);b=wp.vec2(-.0005,.03)                                     <L 70>
    var_61 = (var_53 == var_60);
    if (var_61) {
        var_64 = wp::vec_t<2, wp::float32>(var_62, var_63);
        var_67 = wp::vec_t<2, wp::float32>(var_65, var_66);
    }
    var_68 = wp::where(var_61, var_64, var_56);
    var_69 = wp::where(var_61, var_67, var_59);
    // if k==2:a=wp.vec2(-.0005,.03);b=wp.vec2(0.,0.)                                         <L 71>
    var_71 = (var_53 == var_70);
    if (var_71) {
        var_74 = wp::vec_t<2, wp::float32>(var_72, var_73);
        var_77 = wp::vec_t<2, wp::float32>(var_75, var_76);
    }
    var_78 = wp::where(var_71, var_74, var_68);
    var_79 = wp::where(var_71, var_77, var_69);
    // ab=b-a;t=wp.clamp(wp.dot(q-a,ab)/wp.dot(ab,ab),0.,1.);point=a+t*ab;d=wp.length(q-point)       <L 72>
    var_80 = wp::sub(var_79, var_78);
    var_81 = wp::sub(var_4, var_78);
    var_82 = wp::dot(var_81, var_80);
    var_83 = wp::dot(var_80, var_80);
    var_84 = wp::div(var_82, var_83);
    var_87 = wp::clamp(var_84, var_85, var_86);
    var_88 = wp::mul(var_87, var_80);
    var_89 = wp::add(var_78, var_88);
    var_90 = wp::sub(var_4, var_89);
    var_91 = wp::length(var_90);
    // if d<best:best=d;near=point                                                            <L 73>
    var_92 = (var_91 < var_51);
    if (var_92) {
        var_93 = wp::copy(var_91);
        var_94 = wp::copy(var_89);
    }
    var_95 = wp::where(var_92, var_93, var_51);
    var_96 = wp::where(var_92, var_94, var_52);
    // a=wp.vec2(0.,0.);b=wp.vec2(.0005,.03)                                                  <L 69>
    var_100 = wp::vec_t<2, wp::float32>(var_98, var_99);
    var_103 = wp::vec_t<2, wp::float32>(var_101, var_102);
    // if k==1:a=wp.vec2(.0005,.03);b=wp.vec2(-.0005,.03)                                     <L 70>
    var_105 = (var_97 == var_104);
    if (var_105) {
        var_108 = wp::vec_t<2, wp::float32>(var_106, var_107);
        var_111 = wp::vec_t<2, wp::float32>(var_109, var_110);
    }
    var_112 = wp::where(var_105, var_108, var_100);
    var_113 = wp::where(var_105, var_111, var_103);
    // if k==2:a=wp.vec2(-.0005,.03);b=wp.vec2(0.,0.)                                         <L 71>
    var_115 = (var_97 == var_114);
    if (var_115) {
        var_118 = wp::vec_t<2, wp::float32>(var_116, var_117);
        var_121 = wp::vec_t<2, wp::float32>(var_119, var_120);
    }
    var_122 = wp::where(var_115, var_118, var_112);
    var_123 = wp::where(var_115, var_121, var_113);
    // ab=b-a;t=wp.clamp(wp.dot(q-a,ab)/wp.dot(ab,ab),0.,1.);point=a+t*ab;d=wp.length(q-point)       <L 72>
    var_124 = wp::sub(var_123, var_122);
    var_125 = wp::sub(var_4, var_122);
    var_126 = wp::dot(var_125, var_124);
    var_127 = wp::dot(var_124, var_124);
    var_128 = wp::div(var_126, var_127);
    var_131 = wp::clamp(var_128, var_129, var_130);
    var_132 = wp::mul(var_131, var_124);
    var_133 = wp::add(var_122, var_132);
    var_134 = wp::sub(var_4, var_133);
    var_135 = wp::length(var_134);
    // if d<best:best=d;near=point                                                            <L 73>
    var_136 = (var_135 < var_95);
    if (var_136) {
        var_137 = wp::copy(var_135);
        var_138 = wp::copy(var_133);
    }
    var_139 = wp::where(var_136, var_137, var_95);
    var_140 = wp::where(var_136, var_138, var_96);
    // inside=p[1]>=0. and p[1]<=.03 and wp.abs(p[0])<=p[1]/60.                               <L 74>
    var_143 = wp::extract(var_p, var_142);
    var_145 = (var_143 >= var_144);
    var_141 = var_145;
    if (var_141) {
        var_147 = wp::extract(var_p, var_146);
        var_149 = (var_147 <= var_148);
        var_141 = var_141 && var_149;
    }
    if (var_141) {
        var_151 = wp::extract(var_p, var_150);
        var_152 = wp::abs(var_151);
        var_154 = wp::extract(var_p, var_153);
        var_156 = wp::div(var_154, var_155);
        var_157 = (var_152 <= var_156);
        var_141 = var_141 && var_157;
    }
    // normal2=wp.vec2(1.,0.);distance2=best                                                  <L 75>
    var_160 = wp::vec_t<2, wp::float32>(var_158, var_159);
    var_161 = wp::copy(var_139);
    // if best>1e-12:normal2=(q-near)/best                                                    <L 76>
    var_163 = (var_139 > var_162);
    if (var_163) {
        var_164 = wp::sub(var_4, var_140);
        var_165 = wp::div(var_164, var_139);
    }
    var_166 = wp::where(var_163, var_165, var_160);
    // if inside:distance2=-best;normal2=-normal2                                             <L 77>
    if (var_141) {
        var_167 = wp::neg(var_139);
        var_168 = wp::neg(var_166);
    }
    var_169 = wp::where(var_141, var_168, var_166);
    var_170 = wp::where(var_141, var_167, var_161);
    // dz=wp.abs(p[2])-half_length;az=wp.max(dz,0.);axy=wp.max(distance2,0.);distance=wp.sqrt(az*az+axy*axy)+wp.min(wp.max(distance2,dz),0.);normal=wp.vec3(normal2[0],normal2[1],0.)       <L 78>
    var_172 = wp::extract(var_p, var_171);
    var_173 = wp::abs(var_172);
    var_174 = wp::sub(var_173, var_half_length);
    var_176 = wp::max(var_174, var_175);
    var_178 = wp::max(var_170, var_177);
    var_179 = wp::mul(var_176, var_176);
    var_180 = wp::mul(var_178, var_178);
    var_181 = wp::add(var_179, var_180);
    var_182 = wp::sqrt(var_181);
    var_183 = wp::max(var_170, var_174);
    var_185 = wp::min(var_183, var_184);
    var_186 = wp::add(var_182, var_185);
    var_188 = wp::extract(var_169, var_187);
    var_190 = wp::extract(var_169, var_189);
    var_192 = wp::vec_t<3, wp::float32>(var_188, var_190, var_191);
    // if dz>distance2 and distance2<=0.:normal=wp.vec3(0.,0.,wp.sign(p[2]))                  <L 79>
    var_194 = (var_174 > var_170);
    var_193 = var_194;
    if (var_193) {
        var_196 = (var_170 <= var_195);
        var_193 = var_193 && var_196;
    }
    if (var_193) {
        var_200 = wp::extract(var_p, var_199);
        var_201 = wp::sign(var_200);
        var_202 = wp::vec_t<3, wp::float32>(var_197, var_198, var_201);
    }
    if (!var_193) {
        // elif az>0.:                                                                        <L 80>
        var_204 = (var_176 > var_203);
        if (var_204) {
            // norm=wp.sqrt(az*az+axy*axy);normal=wp.vec3(axy*normal2[0],axy*normal2[1],az*wp.sign(p[2]))/norm       <L 81>
            var_205 = wp::mul(var_176, var_176);
            var_206 = wp::mul(var_178, var_178);
            var_207 = wp::add(var_205, var_206);
            var_208 = wp::sqrt(var_207);
            var_210 = wp::extract(var_169, var_209);
            var_211 = wp::mul(var_178, var_210);
            var_213 = wp::extract(var_169, var_212);
            var_214 = wp::mul(var_178, var_213);
            var_216 = wp::extract(var_p, var_215);
            var_217 = wp::sign(var_216);
            var_218 = wp::mul(var_176, var_217);
            var_219 = wp::vec_t<3, wp::float32>(var_211, var_214, var_218);
            var_220 = wp::div(var_219, var_208);
        }
        var_221 = wp::where(var_204, var_220, var_192);
    }
    var_222 = wp::where(var_193, var_202, var_221);
    // return normal,distance                                                                 <L 82>
    ret_0 = var_222;
    ret_1 = var_186;
    return;
}


// /home/omen/Documents/Codex/experiments/tomato_approx_rl_20261113_v28/src/solver.py:64
static CUDA_CALLABLE void adj_knife_normal_0(
    wp::vec_t<3, wp::float32> var_p,
    wp::float32 var_half_length,
    wp::vec_t<3, wp::float32> & ret_0,
    wp::float32 & ret_1,
    wp::vec_t<3, wp::float32> & adj_p,
    wp::float32 & adj_half_length,
    wp::vec_t<3, wp::float32> & adj_ret_0,
    wp::float32 & adj_ret_1)
{
	// reverse mode disabled (module option "enable_backward" is False or no dependent kernel found with "enable_backward")
}



extern "C" __global__ void bonds_0502009f_cuda_kernel_forward(
    wp::launch_bounds_t<1> dim,
    wp::array_t<wp::vec_t<3, wp::float32>> var_x,
    wp::array_t<wp::vec_t<3, wp::float32>> var_v,
    wp::array_t<wp::vec_t<3, wp::float32>> var_force,
    wp::array_t<wp::vec_t<2, wp::int32>> var_edge,
    wp::array_t<wp::float32> var_rest,
    wp::array_t<wp::float32> var_stiffness,
    wp::array_t<wp::float32> var_mass,
    wp::array_t<wp::float32> var_area,
    wp::array_t<wp::int32> var_alive,
    wp::array_t<wp::float32> var_paid,
    wp::array_t<wp::vec_t<3, wp::float32>> var_tool,
    wp::array_t<wp::vec_t<3, wp::float32>> var_velocity,
    wp::array_t<wp::quat_t<wp::float32>> var_rotation,
    wp::array_t<wp::vec_t<3, wp::float32>> var_reaction,
    wp::array_t<wp::float32> var_load,
    wp::array_t<wp::float32> var_ledger,
    wp::array_t<wp::int32> var_bad,
    wp::float32 var_h,
    wp::float32 var_dt,
    wp::int32 var_n,
    wp::int32 var_nb,
    wp::float32 var_half_length,
    wp::int32 var_cut_enabled)
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
        bool var_3;
        wp::int32* var_4;
        const wp::int32 var_5 = 0;
        bool var_6;
        wp::int32 var_7;
        wp::int32* var_8;
        const wp::int32 var_9 = 0;
        bool var_10;
        wp::int32 var_11;
        wp::vec_t<2, wp::int32>* var_12;
        wp::vec_t<2, wp::int32> var_13;
        wp::vec_t<2, wp::int32> var_14;
        wp::int32 var_15;
        const wp::int32 var_16 = 0;
        wp::int32 var_17;
        wp::int32 var_18;
        wp::int32 var_19;
        const wp::int32 var_20 = 1;
        wp::int32 var_21;
        wp::int32 var_22;
        wp::vec_t<3, wp::float32>* var_23;
        wp::vec_t<3, wp::float32>* var_24;
        wp::vec_t<3, wp::float32> var_25;
        wp::vec_t<3, wp::float32> var_26;
        wp::vec_t<3, wp::float32> var_27;
        wp::float32 var_28;
        const wp::float32 var_29 = 1e-08;
        bool var_30;
        const wp::int32 var_31 = 2;
        wp::int32 var_32;
        wp::vec_t<3, wp::float32> var_33;
        wp::float32* var_34;
        wp::float32 var_35;
        wp::float32 var_36;
        wp::vec_t<3, wp::float32>* var_37;
        wp::vec_t<3, wp::float32>* var_38;
        wp::vec_t<3, wp::float32> var_39;
        wp::vec_t<3, wp::float32> var_40;
        wp::vec_t<3, wp::float32> var_41;
        wp::float32 var_42;
        const wp::int32 var_43 = 0;
        wp::int32 var_44;
        wp::float32* var_45;
        const wp::int32 var_46 = 1;
        wp::int32 var_47;
        wp::float32* var_48;
        wp::float32 var_49;
        wp::float32 var_50;
        wp::float32 var_51;
        const wp::int32 var_52 = 0;
        wp::int32 var_53;
        wp::float32* var_54;
        const wp::int32 var_55 = 1;
        wp::int32 var_56;
        wp::float32* var_57;
        wp::float32 var_58;
        wp::float32 var_59;
        wp::float32 var_60;
        wp::float32 var_61;
        const wp::float32 var_62 = 2.0;
        const wp::float32 var_63 = 0.02;
        wp::float32 var_64;
        wp::float32* var_65;
        wp::float32 var_66;
        wp::float32 var_67;
        wp::float32 var_68;
        wp::float32 var_69;
        wp::float32* var_70;
        wp::float32 var_71;
        wp::float32 var_72;
        wp::float32 var_73;
        wp::float32 var_74;
        wp::vec_t<3, wp::float32> var_75;
        wp::vec_t<3, wp::float32> var_76;
        wp::vec_t<3, wp::float32> var_77;
        const wp::int32 var_78 = 0;
        wp::float32 var_79;
        wp::float32 var_80;
        wp::float32 var_81;
        wp::float32 var_82;
        const wp::int32 var_83 = 0;
        bool var_84;
        wp::quat_t<wp::float32>* var_85;
        wp::vec_t<3, wp::float32>* var_86;
        wp::vec_t<3, wp::float32>* var_87;
        wp::vec_t<3, wp::float32> var_88;
        wp::vec_t<3, wp::float32> var_89;
        wp::vec_t<3, wp::float32> var_90;
        wp::vec_t<3, wp::float32> var_91;
        wp::quat_t<wp::float32> var_92;
        wp::quat_t<wp::float32>* var_93;
        wp::vec_t<3, wp::float32>* var_94;
        wp::vec_t<3, wp::float32>* var_95;
        wp::vec_t<3, wp::float32> var_96;
        wp::vec_t<3, wp::float32> var_97;
        wp::vec_t<3, wp::float32> var_98;
        wp::vec_t<3, wp::float32> var_99;
        wp::quat_t<wp::float32> var_100;
        const wp::int32 var_101 = 0;
        wp::float32 var_102;
        const wp::int32 var_103 = 0;
        wp::float32 var_104;
        wp::float32 var_105;
        const wp::float32 var_106 = 0.0;
        bool var_107;
        const wp::int32 var_108 = 0;
        wp::float32 var_109;
        const wp::int32 var_110 = 0;
        wp::float32 var_111;
        const wp::int32 var_112 = 0;
        wp::float32 var_113;
        wp::float32 var_114;
        wp::float32 var_115;
        wp::vec_t<3, wp::float32> var_116;
        wp::vec_t<3, wp::float32> var_117;
        wp::vec_t<3, wp::float32> var_118;
        bool var_119;
        const wp::int32 var_120 = 2;
        wp::float32 var_121;
        wp::float32 var_122;
        bool var_123;
        const wp::int32 var_124 = 1;
        wp::float32 var_125;
        const wp::float32 var_126 = -0.5;
        wp::float32 var_127;
        bool var_128;
        const wp::int32 var_129 = 1;
        wp::float32 var_130;
        const wp::float32 var_131 = 0.03;
        bool var_132;
        const wp::float32 var_133 = 1.0;
        wp::float32 var_134;
        wp::vec_t<3, wp::float32>* var_135;
        wp::vec_t<3, wp::float32> var_136;
        wp::vec_t<3, wp::float32> var_137;
        wp::vec_t<3, wp::float32>* var_138;
        wp::vec_t<3, wp::float32> var_139;
        wp::vec_t<3, wp::float32> var_140;
        wp::vec_t<3, wp::float32> var_141;
        wp::vec_t<3, wp::float32>* var_142;
        wp::vec_t<3, wp::float32> var_143;
        wp::vec_t<3, wp::float32> var_144;
        wp::quat_t<wp::float32>* var_145;
        wp::vec_t<3, wp::float32> var_146;
        wp::quat_t<wp::float32> var_147;
        const wp::int32 var_148 = 1;
        wp::float32 var_149;
        wp::float32 var_150;
        const wp::float32 var_151 = 0.0;
        wp::float32 var_152;
        const wp::float32 var_153 = 0.25;
        const wp::int32 var_154 = 2;
        wp::float32 var_155;
        wp::float32 var_156;
        wp::float32 var_157;
        wp::float32 var_158;
        wp::float32 var_159;
        const wp::float32 var_160 = 80.0;
        wp::float32* var_161;
        wp::float32 var_162;
        wp::float32 var_163;
        wp::float32* var_164;
        wp::float32 var_165;
        wp::float32 var_166;
        const wp::float32 var_167 = 0.0;
        wp::float32 var_168;
        bool var_169;
        const wp::float32 var_170 = 0.0;
        bool var_171;
        const wp::float32 var_172 = 1e-08;
        bool var_173;
        const wp::float32 var_174 = 0.0;
        bool var_175;
        wp::float32 var_176;
        wp::float32 var_177;
        wp::float32 var_178;
        wp::float32 var_179;
        wp::float32 var_180;
        wp::float32 var_181;
        wp::vec_t<3, wp::float32> var_182;
        wp::vec_t<3, wp::float32> var_183;
        const wp::float32 var_184 = 1.0;
        wp::float32 var_185;
        wp::vec_t<3, wp::float32> var_186;
        wp::vec_t<3, wp::float32> var_187;
        wp::vec_t<3, wp::float32> var_188;
        wp::vec_t<3, wp::float32> var_189;
        wp::vec_t<3, wp::float32> var_190;
        wp::float32 var_191;
        wp::float32 var_192;
        const wp::int32 var_193 = 1;
        wp::float32 var_194;
        const wp::int32 var_195 = 2;
        wp::vec_t<3, wp::float32>* var_196;
        wp::float32 var_197;
        wp::vec_t<3, wp::float32> var_198;
        wp::float32 var_199;
        wp::float32 var_200;
        wp::float32 var_201;
        wp::float32* var_202;
        const wp::float32 var_203 = 1.0;
        const wp::float32 var_204 = 1e-05;
        wp::float32 var_205;
        wp::float32 var_206;
        bool var_207;
        wp::float32 var_208;
        const wp::int32 var_209 = 0;
        const wp::int32 var_210 = 3;
        const wp::float32 var_211 = 0.5;
        wp::float32* var_212;
        wp::float32 var_213;
        wp::float32 var_214;
        wp::float32 var_215;
        wp::float32 var_216;
        wp::float32 var_217;
        //---------
        // forward
        // def bonds(x:wp.array(dtype=wp.vec3),v:wp.array(dtype=wp.vec3),force:wp.array(dtype=wp.vec3),edge:wp.array(dtype=wp.vec2i),rest:wp.array(dtype=float),stiffness:wp.array(dtype=float),mass:wp.array(dtype=float),area:wp.array(dtype=float),alive:wp.array(dtype=int),paid:wp.array(dtype=float),tool:wp.array(dtype=wp.vec3),velocity:wp.array(dtype=wp.vec3),rotation:wp.array(dtype=wp.quat),reaction:wp.array(dtype=wp.vec3),load:wp.array(dtype=float),ledger:wp.array2d(dtype=float),bad:wp.array(dtype=int),h:float,dt:float,n:int,nb:int,half_length:float,cut_enabled:int):       <L 31>
        // idx=wp.tid();e=idx//nb;b=idx%nb                                                        <L 32>
        var_0 = builtin_tid1d();
        var_1 = wp::floordiv(var_0, var_nb);
        var_2 = wp::mod(var_0, var_nb);
        // if bad[e]!=0 or alive[idx]==0:return                                                   <L 33>
        var_4 = wp::address(var_bad, var_1);
        var_7 = wp::load(var_4);
        var_6 = (var_7 != var_5);
        var_3 = var_6;
        if (!var_3) {
            var_8 = wp::address(var_alive, var_0);
            var_11 = wp::load(var_8);
            var_10 = (var_11 == var_9);
            var_3 = var_3 || var_10;
        }
        if (var_3) {
            continue;
        }
        // ends=edge[b];i=e*n+ends[0];j=e*n+ends[1];delta=x[j]-x[i];length=wp.length(delta)       <L 34>
        var_12 = wp::address(var_edge, var_2);
        var_14 = wp::load(var_12);
        var_13 = wp::copy(var_14);
        var_15 = wp::mul(var_1, var_n);
        var_17 = wp::extract(var_13, var_16);
        var_18 = wp::add(var_15, var_17);
        var_19 = wp::mul(var_1, var_n);
        var_21 = wp::extract(var_13, var_20);
        var_22 = wp::add(var_19, var_21);
        var_23 = wp::address(var_x, var_22);
        var_24 = wp::address(var_x, var_18);
        var_26 = wp::load(var_23);
        var_27 = wp::load(var_24);
        var_25 = wp::sub(var_26, var_27);
        var_28 = wp::length(var_25);
        // if length<1e-8:wp.atomic_max(bad,e,2);return                                           <L 35>
        var_30 = (var_28 < var_29);
        if (var_30) {
            var_32 = wp::atomic_max(var_bad, var_1, var_31);
            continue;
        }
        // direction=delta/length;strain=length-rest[b];relative=wp.dot(v[j]-v[i],direction);reduced=mass[ends[0]]*mass[ends[1]]/(mass[ends[0]]+mass[ends[1]]);damping=2.*.02*wp.sqrt(stiffness[b]*reduced);f=(stiffness[b]*strain+damping*relative)*direction       <L 36>
        var_33 = wp::div(var_25, var_28);
        var_34 = wp::address(var_rest, var_2);
        var_36 = wp::load(var_34);
        var_35 = wp::sub(var_28, var_36);
        var_37 = wp::address(var_v, var_22);
        var_38 = wp::address(var_v, var_18);
        var_40 = wp::load(var_37);
        var_41 = wp::load(var_38);
        var_39 = wp::sub(var_40, var_41);
        var_42 = wp::dot(var_39, var_33);
        var_44 = wp::extract(var_13, var_43);
        var_45 = wp::address(var_mass, var_44);
        var_47 = wp::extract(var_13, var_46);
        var_48 = wp::address(var_mass, var_47);
        var_50 = wp::load(var_45);
        var_51 = wp::load(var_48);
        var_49 = wp::mul(var_50, var_51);
        var_53 = wp::extract(var_13, var_52);
        var_54 = wp::address(var_mass, var_53);
        var_56 = wp::extract(var_13, var_55);
        var_57 = wp::address(var_mass, var_56);
        var_59 = wp::load(var_54);
        var_60 = wp::load(var_57);
        var_58 = wp::add(var_59, var_60);
        var_61 = wp::div(var_49, var_58);
        var_64 = wp::mul(var_62, var_63);
        var_65 = wp::address(var_stiffness, var_2);
        var_67 = wp::load(var_65);
        var_66 = wp::mul(var_67, var_61);
        var_68 = wp::sqrt(var_66);
        var_69 = wp::mul(var_64, var_68);
        var_70 = wp::address(var_stiffness, var_2);
        var_72 = wp::load(var_70);
        var_71 = wp::mul(var_72, var_35);
        var_73 = wp::mul(var_69, var_42);
        var_74 = wp::add(var_71, var_73);
        var_75 = wp::mul(var_74, var_33);
        // wp.atomic_add(force,i,f);wp.atomic_sub(force,j,f);wp.atomic_add(ledger,e,0,damping*relative*relative*dt)       <L 37>
        var_76 = wp::atomic_add(var_force, var_18, var_75);
        var_77 = wp::atomic_sub(var_force, var_22, var_75);
        var_79 = wp::mul(var_69, var_42);
        var_80 = wp::mul(var_79, var_42);
        var_81 = wp::mul(var_80, var_dt);
        var_82 = wp::atomic_add(var_ledger, var_1, var_78, var_81);
        // if cut_enabled==0:return                                                               <L 38>
        var_84 = (var_cut_enabled == var_83);
        if (var_84) {
            continue;
        }
        // a=wp.quat_rotate_inv(rotation[e],x[i]-tool[e]);c=wp.quat_rotate_inv(rotation[e],x[j]-tool[e])       <L 39>
        var_85 = wp::address(var_rotation, var_1);
        var_86 = wp::address(var_x, var_18);
        var_87 = wp::address(var_tool, var_1);
        var_89 = wp::load(var_86);
        var_90 = wp::load(var_87);
        var_88 = wp::sub(var_89, var_90);
        var_92 = wp::load(var_85);
        var_91 = wp::quat_rotate_inv(var_92, var_88);
        var_93 = wp::address(var_rotation, var_1);
        var_94 = wp::address(var_x, var_22);
        var_95 = wp::address(var_tool, var_1);
        var_97 = wp::load(var_94);
        var_98 = wp::load(var_95);
        var_96 = wp::sub(var_97, var_98);
        var_100 = wp::load(var_93);
        var_99 = wp::quat_rotate_inv(var_100, var_96);
        // if a[0]*c[0]>=0.:return                                                                <L 40>
        var_102 = wp::extract(var_91, var_101);
        var_104 = wp::extract(var_99, var_103);
        var_105 = wp::mul(var_102, var_104);
        var_107 = (var_105 >= var_106);
        if (var_107) {
            continue;
        }
        // t=a[0]/(a[0]-c[0]);p=a+t*(c-a)                                                         <L 41>
        var_109 = wp::extract(var_91, var_108);
        var_111 = wp::extract(var_91, var_110);
        var_113 = wp::extract(var_99, var_112);
        var_114 = wp::sub(var_111, var_113);
        var_115 = wp::div(var_109, var_114);
        var_116 = wp::sub(var_99, var_91);
        var_117 = wp::mul(var_115, var_116);
        var_118 = wp::add(var_91, var_117);
        // if wp.abs(p[2])>half_length or p[1]<-.5*h or p[1]>.03:return                           <L 42>
        var_121 = wp::extract(var_118, var_120);
        var_122 = wp::abs(var_121);
        var_123 = (var_122 > var_half_length);
        var_119 = var_123;
        if (!var_119) {
            var_125 = wp::extract(var_118, var_124);
            var_127 = wp::mul(var_126, var_h);
            var_128 = (var_125 < var_127);
            var_119 = var_119 || var_128;
        }
        if (!var_119) {
            var_130 = wp::extract(var_118, var_129);
            var_132 = (var_130 > var_131);
            var_119 = var_119 || var_132;
        }
        if (var_119) {
            continue;
        }
        // midpoint_v=(1.-t)*v[i]+t*v[j];rel=velocity[e]-midpoint_v;local=wp.quat_rotate_inv(rotation[e],rel);advance=wp.max(-local[1],0.)+.25*wp.abs(local[2]);speed=wp.length(rel);budget=80.*area[b];remaining=wp.max(budget-paid[idx],0.)       <L 43>
        var_134 = wp::sub(var_133, var_115);
        var_135 = wp::address(var_v, var_18);
        var_137 = wp::load(var_135);
        var_136 = wp::mul(var_134, var_137);
        var_138 = wp::address(var_v, var_22);
        var_140 = wp::load(var_138);
        var_139 = wp::mul(var_115, var_140);
        var_141 = wp::add(var_136, var_139);
        var_142 = wp::address(var_velocity, var_1);
        var_144 = wp::load(var_142);
        var_143 = wp::sub(var_144, var_141);
        var_145 = wp::address(var_rotation, var_1);
        var_147 = wp::load(var_145);
        var_146 = wp::quat_rotate_inv(var_147, var_143);
        var_149 = wp::extract(var_146, var_148);
        var_150 = wp::neg(var_149);
        var_152 = wp::max(var_150, var_151);
        var_155 = wp::extract(var_146, var_154);
        var_156 = wp::abs(var_155);
        var_157 = wp::mul(var_153, var_156);
        var_158 = wp::add(var_152, var_157);
        var_159 = wp::length(var_143);
        var_161 = wp::address(var_area, var_2);
        var_163 = wp::load(var_161);
        var_162 = wp::mul(var_160, var_163);
        var_164 = wp::address(var_paid, var_0);
        var_166 = wp::load(var_164);
        var_165 = wp::sub(var_162, var_166);
        var_168 = wp::max(var_165, var_167);
        // if advance<=0. or speed<=1e-8 or remaining<=0.:return                                  <L 44>
        var_171 = (var_158 <= var_170);
        var_169 = var_171;
        if (!var_169) {
            var_173 = (var_159 <= var_172);
            var_169 = var_169 || var_173;
        }
        if (!var_169) {
            var_175 = (var_168 <= var_174);
            var_169 = var_169 || var_175;
        }
        if (var_169) {
            continue;
        }
        // dwork=wp.min(remaining,budget/h*advance*dt);resistance=dwork/(speed*dt)*rel/speed       <L 47>
        var_176 = wp::div(var_162, var_h);
        var_177 = wp::mul(var_176, var_158);
        var_178 = wp::mul(var_177, var_dt);
        var_179 = wp::min(var_168, var_178);
        var_180 = wp::mul(var_159, var_dt);
        var_181 = wp::div(var_179, var_180);
        var_182 = wp::mul(var_181, var_143);
        var_183 = wp::div(var_182, var_159);
        // wp.atomic_add(force,i,(1.-t)*resistance);wp.atomic_add(force,j,t*resistance);wp.atomic_sub(reaction,e,resistance);wp.atomic_add(load,e,wp.length(resistance));wp.atomic_add(ledger,e,1,dwork);wp.atomic_add(ledger,e,2,wp.dot(resistance,velocity[e])*dt);paid[idx]+=dwork       <L 48>
        var_185 = wp::sub(var_184, var_115);
        var_186 = wp::mul(var_185, var_183);
        var_187 = wp::atomic_add(var_force, var_18, var_186);
        var_188 = wp::mul(var_115, var_183);
        var_189 = wp::atomic_add(var_force, var_22, var_188);
        var_190 = wp::atomic_sub(var_reaction, var_1, var_183);
        var_191 = wp::length(var_183);
        var_192 = wp::atomic_add(var_load, var_1, var_191);
        var_194 = wp::atomic_add(var_ledger, var_1, var_193, var_179);
        var_196 = wp::address(var_velocity, var_1);
        var_198 = wp::load(var_196);
        var_197 = wp::dot(var_183, var_198);
        var_199 = wp::mul(var_197, var_dt);
        var_200 = wp::atomic_add(var_ledger, var_1, var_195, var_199);
        var_201 = wp::atomic_add(var_paid, var_0, var_179);
        // if paid[idx]>=budget*(1.-1e-5):                                                        <L 49>
        var_202 = wp::address(var_paid, var_0);
        var_205 = wp::sub(var_203, var_204);
        var_206 = wp::mul(var_162, var_205);
        var_208 = wp::load(var_202);
        var_207 = (var_208 >= var_206);
        if (var_207) {
            // alive[idx]=0;wp.atomic_add(ledger,e,3,.5*stiffness[b]*strain*strain)               <L 50>
            wp::array_store(var_alive, var_0, var_209);
            var_212 = wp::address(var_stiffness, var_2);
            var_214 = wp::load(var_212);
            var_213 = wp::mul(var_211, var_214);
            var_215 = wp::mul(var_213, var_35);
            var_216 = wp::mul(var_215, var_35);
            var_217 = wp::atomic_add(var_ledger, var_1, var_210, var_216);
        }
    }
}



extern "C" __global__ void clear_step_1c989fed_cuda_kernel_forward(
    wp::launch_bounds_t<1> dim,
    wp::array_t<wp::vec_t<3, wp::float32>> var_x,
    wp::array_t<wp::vec_t<3, wp::float32>> var_force,
    wp::array_t<wp::float32> var_mass,
    wp::array_t<wp::vec_t<3, wp::float32>> var_reaction,
    wp::array_t<wp::float32> var_normal_load,
    wp::array_t<wp::vec_t<3, wp::float32>> var_drive,
    wp::array_t<wp::vec_t<3, wp::float32>> var_tool,
    wp::array_t<wp::vec_t<3, wp::float32>> var_action,
    wp::array_t<wp::int32> var_bad,
    wp::float32 var_dt,
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
        wp::int32 var_1;
        const wp::float32 var_2 = 0.0;
        const wp::float32 var_3 = -9.81;
        wp::int32 var_4;
        wp::float32* var_5;
        wp::float32 var_6;
        wp::float32 var_7;
        const wp::float32 var_8 = 0.0;
        wp::vec_t<3, wp::float32> var_9;
        wp::int32 var_10;
        const wp::int32 var_11 = 0;
        bool var_12;
        const wp::float32 var_13 = 0.0;
        wp::vec_t<3, wp::float32> var_14;
        const wp::float32 var_15 = 0.0;
        wp::vec_t<3, wp::float32>* var_16;
        wp::vec_t<3, wp::float32> var_17;
        wp::int32* var_18;
        const wp::int32 var_19 = 0;
        bool var_20;
        wp::int32 var_21;
        wp::vec_t<3, wp::float32>* var_22;
        wp::vec_t<3, wp::float32> var_23;
        wp::vec_t<3, wp::float32> var_24;
        wp::vec_t<3, wp::float32> var_25;
        //---------
        // forward
        // def clear_step(x:wp.array(dtype=wp.vec3),force:wp.array(dtype=wp.vec3),mass:wp.array(dtype=float),reaction:wp.array(dtype=wp.vec3),normal_load:wp.array(dtype=float),drive:wp.array(dtype=wp.vec3),tool:wp.array(dtype=wp.vec3),action:wp.array(dtype=wp.vec3),bad:wp.array(dtype=int),dt:float,n:int):       <L 24>
        // i=wp.tid();e=i//n;force[i]=wp.vec3(0.,-9.81*mass[i%n],0.)                              <L 25>
        var_0 = builtin_tid1d();
        var_1 = wp::floordiv(var_0, var_n);
        var_4 = wp::mod(var_0, var_n);
        var_5 = wp::address(var_mass, var_4);
        var_7 = wp::load(var_5);
        var_6 = wp::mul(var_3, var_7);
        var_9 = wp::vec_t<3, wp::float32>(var_2, var_6, var_8);
        wp::array_store(var_force, var_0, var_9);
        // if i%n==0:                                                                             <L 26>
        var_10 = wp::mod(var_0, var_n);
        var_12 = (var_10 == var_11);
        if (var_12) {
            // reaction[e]=wp.vec3(0.);normal_load[e]=0.;drive[e]=action[e]                       <L 27>
            var_14 = wp::vec_t<3, wp::float32>(var_13);
            wp::array_store(var_reaction, var_1, var_14);
            wp::array_store(var_normal_load, var_1, var_15);
            var_16 = wp::address(var_action, var_1);
            var_17 = wp::load(var_16);
            wp::array_store(var_drive, var_1, var_17);
            // if bad[e]==0:tool[e]+=dt*action[e]                                                 <L 28>
            var_18 = wp::address(var_bad, var_1);
            var_21 = wp::load(var_18);
            var_20 = (var_21 == var_19);
            if (var_20) {
                var_22 = wp::address(var_action, var_1);
                var_24 = wp::load(var_22);
                var_23 = wp::mul(var_dt, var_24);
                var_25 = wp::atomic_add(var_tool, var_1, var_23);
            }
        }
    }
}



extern "C" __global__ void finish_step_29b9af99_cuda_kernel_forward(
    wp::launch_bounds_t<1> dim,
    wp::array_t<wp::vec_t<3, wp::float32>> var_reaction,
    wp::array_t<wp::float32> var_load,
    wp::array_t<wp::float32> var_peak,
    wp::array_t<wp::int32> var_bad,
    wp::float32 var_stop_force)
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
        wp::float32* var_1;
        wp::float32* var_2;
        wp::float32 var_3;
        wp::float32 var_4;
        wp::float32 var_5;
        bool var_6;
        wp::float32* var_7;
        bool var_8;
        wp::float32 var_9;
        wp::float32* var_10;
        bool var_11;
        wp::float32 var_12;
        bool var_13;
        const wp::int32 var_14 = 3;
        wp::int32 var_15;
        //---------
        // forward
        // def finish_step(reaction:wp.array(dtype=wp.vec3),load:wp.array(dtype=float),peak:wp.array(dtype=float),bad:wp.array(dtype=int),stop_force:float):       <L 118>
        // e=wp.tid();peak[e]=wp.max(peak[e],load[e])                                             <L 119>
        var_0 = builtin_tid1d();
        var_1 = wp::address(var_peak, var_0);
        var_2 = wp::address(var_load, var_0);
        var_4 = wp::load(var_1);
        var_5 = wp::load(var_2);
        var_3 = wp::max(var_4, var_5);
        wp::array_store(var_peak, var_0, var_3);
        // if load[e]>stop_force or not wp.isfinite(load[e]):wp.atomic_max(bad,e,3)               <L 120>
        var_7 = wp::address(var_load, var_0);
        var_9 = wp::load(var_7);
        var_8 = (var_9 > var_stop_force);
        var_6 = var_8;
        if (!var_6) {
            var_10 = wp::address(var_load, var_0);
            var_12 = wp::load(var_10);
            var_11 = wp::isfinite(var_12);
            var_13 = wp::unot(var_11);
            var_6 = var_6 || var_13;
        }
        if (var_6) {
            var_15 = wp::atomic_max(var_bad, var_0, var_14);
        }
    }
}



extern "C" __global__ void integrate_52a15767_cuda_kernel_forward(
    wp::launch_bounds_t<1> dim,
    wp::array_t<wp::vec_t<3, wp::float32>> var_x,
    wp::array_t<wp::int32> var_fixed,
    wp::array_t<wp::vec_t<3, wp::float32>> var_v,
    wp::array_t<wp::vec_t<3, wp::float32>> var_force,
    wp::array_t<wp::float32> var_mass,
    wp::array_t<wp::vec_t<3, wp::float32>> var_tool,
    wp::array_t<wp::vec_t<3, wp::float32>> var_velocity,
    wp::array_t<wp::quat_t<wp::float32>> var_rotation,
    wp::array_t<wp::vec_t<3, wp::float32>> var_reaction,
    wp::array_t<wp::float32> var_load,
    wp::array_t<wp::float32> var_ledger,
    wp::array_t<wp::float32> var_penetration_peak,
    wp::array_t<wp::int32> var_bad,
    wp::float32 var_dt,
    wp::float32 var_radius,
    wp::int32 var_n,
    wp::float32 var_half_length,
    wp::int32 var_knife_enabled)
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
        wp::int32* var_2;
        const wp::int32 var_3 = 0;
        bool var_4;
        wp::int32 var_5;
        wp::int32* var_6;
        const wp::int32 var_7 = 0;
        bool var_8;
        wp::int32 var_9;
        const wp::int32 var_10 = 0;
        bool var_11;
        wp::quat_t<wp::float32>* var_12;
        wp::vec_t<3, wp::float32>* var_13;
        wp::vec_t<3, wp::float32>* var_14;
        wp::vec_t<3, wp::float32> var_15;
        wp::vec_t<3, wp::float32> var_16;
        wp::vec_t<3, wp::float32> var_17;
        wp::vec_t<3, wp::float32> var_18;
        wp::quat_t<wp::float32> var_19;
        wp::vec_t<3, wp::float32> var_20;
        wp::float32 var_21;
        wp::float32 var_22;
        const wp::float32 var_23 = 0.0;
        wp::float32 var_24;
        wp::float32 var_25;
        const wp::float32 var_26 = 0.0001;
        bool var_27;
        const wp::int32 var_28 = 4;
        wp::int32 var_29;
        wp::int32 var_30;
        wp::float32* var_31;
        wp::float32 var_32;
        wp::float32 var_33;
        wp::vec_t<3, wp::float32>* var_34;
        wp::vec_t<3, wp::float32>* var_35;
        wp::vec_t<3, wp::float32> var_36;
        wp::vec_t<3, wp::float32> var_37;
        wp::vec_t<3, wp::float32> var_38;
        wp::vec_t<3, wp::float32> var_39;
        wp::vec_t<3, wp::float32> var_40;
        wp::vec_t<3, wp::float32>* var_41;
        wp::vec_t<3, wp::float32> var_42;
        wp::vec_t<3, wp::float32> var_43;
        wp::vec_t<3, wp::float32> var_44;
        const wp::int32 var_45 = 0;
        bool var_46;
        wp::quat_t<wp::float32>* var_47;
        wp::vec_t<3, wp::float32>* var_48;
        wp::vec_t<3, wp::float32> var_49;
        wp::vec_t<3, wp::float32> var_50;
        wp::vec_t<3, wp::float32> var_51;
        wp::quat_t<wp::float32> var_52;
        wp::vec_t<3, wp::float32> var_53;
        wp::float32 var_54;
        wp::float32 var_55;
        const wp::float32 var_56 = 0.0;
        wp::float32 var_57;
        wp::float32 var_58;
        const wp::float32 var_59 = 0.0001;
        bool var_60;
        const wp::int32 var_61 = 4;
        wp::int32 var_62;
        const wp::float32 var_63 = 0.0;
        bool var_64;
        wp::quat_t<wp::float32>* var_65;
        wp::vec_t<3, wp::float32> var_66;
        wp::quat_t<wp::float32> var_67;
        wp::vec_t<3, wp::float32> var_68;
        wp::float32 var_69;
        wp::vec_t<3, wp::float32> var_70;
        wp::vec_t<3, wp::float32> var_71;
        wp::vec_t<3, wp::float32> var_72;
        wp::vec_t<3, wp::float32> var_73;
        wp::vec_t<3, wp::float32>* var_74;
        wp::vec_t<3, wp::float32> var_75;
        wp::vec_t<3, wp::float32> var_76;
        wp::float32 var_77;
        wp::vec_t<3, wp::float32> var_78;
        wp::vec_t<3, wp::float32> var_79;
        wp::float32 var_80;
        const wp::float32 var_81 = 0.0;
        wp::vec_t<3, wp::float32> var_82;
        const wp::float32 var_83 = 1e-12;
        bool var_84;
        const wp::float32 var_85 = 0.2;
        wp::float32 var_86;
        wp::float32 var_87;
        wp::float32 var_88;
        wp::float32 var_89;
        wp::float32 var_90;
        wp::vec_t<3, wp::float32> var_91;
        wp::vec_t<3, wp::float32> var_92;
        wp::vec_t<3, wp::float32> var_93;
        wp::vec_t<3, wp::float32> var_94;
        wp::vec_t<3, wp::float32> var_95;
        wp::vec_t<3, wp::float32> var_96;
        wp::vec_t<3, wp::float32> var_97;
        wp::vec_t<3, wp::float32> var_98;
        wp::vec_t<3, wp::float32> var_99;
        wp::float32 var_100;
        wp::float32 var_101;
        wp::float32 var_102;
        const wp::int32 var_103 = 2;
        wp::vec_t<3, wp::float32>* var_104;
        wp::float32 var_105;
        wp::vec_t<3, wp::float32> var_106;
        wp::float32 var_107;
        const wp::int32 var_108 = 4;
        wp::float32 var_109;
        wp::float32 var_110;
        wp::float32 var_111;
        wp::vec_t<3, wp::float32> var_112;
        wp::vec_t<3, wp::float32> var_113;
        wp::vec_t<3, wp::float32> var_114;
        wp::vec_t<3, wp::float32> var_115;
        wp::vec_t<3, wp::float32> var_116;
        wp::float32 var_117;
        wp::float32 var_118;
        wp::vec_t<3, wp::float32> var_119;
        wp::vec_t<3, wp::float32> var_120;
        const wp::int32 var_121 = 1;
        wp::float32 var_122;
        bool var_123;
        const wp::float32 var_124 = 0.5;
        wp::float32 var_125;
        wp::float32 var_126;
        wp::float32 var_127;
        const wp::int32 var_128 = 1;
        const wp::int32 var_129 = 1;
        wp::float32 var_130;
        const wp::float32 var_131 = 0.0;
        bool var_132;
        const wp::int32 var_133 = 1;
        wp::float32 var_134;
        wp::float32 var_135;
        const wp::float32 var_136 = 0.0;
        const wp::int32 var_137 = 1;
        const wp::int32 var_138 = 0;
        wp::float32 var_139;
        const wp::float32 var_140 = 0.0;
        const wp::int32 var_141 = 2;
        wp::float32 var_142;
        wp::vec_t<3, wp::float32> var_143;
        wp::float32 var_144;
        const wp::float32 var_145 = 1e-12;
        bool var_146;
        const wp::float32 var_147 = 0.4;
        wp::float32 var_148;
        wp::float32 var_149;
        wp::vec_t<3, wp::float32> var_150;
        wp::vec_t<3, wp::float32> var_151;
        wp::vec_t<3, wp::float32> var_152;
        wp::vec_t<3, wp::float32> var_153;
        wp::vec_t<3, wp::float32> var_154;
        const wp::int32 var_155 = 6;
        const wp::float32 var_156 = 0.5;
        wp::float32 var_157;
        wp::float32 var_158;
        wp::float32 var_159;
        wp::float32 var_160;
        const wp::float32 var_161 = 0.0;
        wp::float32 var_162;
        wp::float32 var_163;
        wp::vec_t<3, wp::float32> var_164;
        const wp::int32 var_165 = 0;
        bool var_166;
        wp::quat_t<wp::float32>* var_167;
        wp::vec_t<3, wp::float32>* var_168;
        wp::vec_t<3, wp::float32> var_169;
        wp::vec_t<3, wp::float32> var_170;
        wp::vec_t<3, wp::float32> var_171;
        wp::quat_t<wp::float32> var_172;
        wp::vec_t<3, wp::float32> var_173;
        wp::float32 var_174;
        wp::float32 var_175;
        const wp::float32 var_176 = 0.0001;
        bool var_177;
        const wp::int32 var_178 = 4;
        wp::int32 var_179;
        wp::vec_t<3, wp::float32> var_180;
        wp::vec_t<3, wp::float32> var_181;
        wp::float32 var_182;
        bool var_183;
        const wp::int32 var_184 = 0;
        wp::float32 var_185;
        bool var_186;
        bool var_187;
        const wp::int32 var_188 = 1;
        wp::float32 var_189;
        bool var_190;
        bool var_191;
        const wp::int32 var_192 = 2;
        wp::float32 var_193;
        bool var_194;
        bool var_195;
        wp::float32 var_196;
        const wp::float32 var_197 = 10.0;
        bool var_198;
        const wp::int32 var_199 = 2;
        wp::int32 var_200;
        //---------
        // forward
        // def integrate(x:wp.array(dtype=wp.vec3),fixed:wp.array(dtype=int),v:wp.array(dtype=wp.vec3),force:wp.array(dtype=wp.vec3),mass:wp.array(dtype=float),tool:wp.array(dtype=wp.vec3),velocity:wp.array(dtype=wp.vec3),rotation:wp.array(dtype=wp.quat),reaction:wp.array(dtype=wp.vec3),load:wp.array(dtype=float),ledger:wp.array2d(dtype=float),penetration_peak:wp.array(dtype=float),bad:wp.array(dtype=int),dt:float,radius:float,n:int,half_length:float,knife_enabled:int):       <L 85>
        // i=wp.tid();e=i//n                                                                      <L 86>
        var_0 = builtin_tid1d();
        var_1 = wp::floordiv(var_0, var_n);
        // if bad[e]!=0:return                                                                    <L 87>
        var_2 = wp::address(var_bad, var_1);
        var_5 = wp::load(var_2);
        var_4 = (var_5 != var_3);
        if (var_4) {
            continue;
        }
        // if fixed[i]!=0:                                                                        <L 88>
        var_6 = wp::address(var_fixed, var_0);
        var_9 = wp::load(var_6);
        var_8 = (var_9 != var_7);
        if (var_8) {
            // if knife_enabled!=0:                                                               <L 89>
            var_11 = (var_knife_enabled != var_10);
            if (var_11) {
                // p=wp.quat_rotate_inv(rotation[e],x[i]-tool[e]);normal,distance=knife_normal(p,half_length);penetration=radius-distance       <L 90>
                var_12 = wp::address(var_rotation, var_1);
                var_13 = wp::address(var_x, var_0);
                var_14 = wp::address(var_tool, var_1);
                var_16 = wp::load(var_13);
                var_17 = wp::load(var_14);
                var_15 = wp::sub(var_16, var_17);
                var_19 = wp::load(var_12);
                var_18 = wp::quat_rotate_inv(var_19, var_15);
                knife_normal_0(var_18, var_half_length, var_20, var_21);
                var_22 = wp::sub(var_radius, var_21);
                // wp.atomic_max(penetration_peak,e,wp.max(penetration,0.))                       <L 91>
                var_24 = wp::max(var_22, var_23);
                var_25 = wp::atomic_max(var_penetration_peak, var_1, var_24);
                // if penetration>.0001:wp.atomic_max(bad,e,4)                                    <L 92>
                var_27 = (var_22 > var_26);
                if (var_27) {
                    var_29 = wp::atomic_max(var_bad, var_1, var_28);
                }
            }
            // return                                                                             <L 93>
            continue;
        }
        // m=mass[i%n];newv=v[i]+dt*force[i]/m;newx=x[i]+dt*newv                                  <L 94>
        var_30 = wp::mod(var_0, var_n);
        var_31 = wp::address(var_mass, var_30);
        var_33 = wp::load(var_31);
        var_32 = wp::copy(var_33);
        var_34 = wp::address(var_v, var_0);
        var_35 = wp::address(var_force, var_0);
        var_37 = wp::load(var_35);
        var_36 = wp::mul(var_dt, var_37);
        var_38 = wp::div(var_36, var_32);
        var_40 = wp::load(var_34);
        var_39 = wp::add(var_40, var_38);
        var_41 = wp::address(var_x, var_0);
        var_42 = wp::mul(var_dt, var_39);
        var_44 = wp::load(var_41);
        var_43 = wp::add(var_44, var_42);
        // if knife_enabled!=0:                                                                   <L 95>
        var_46 = (var_knife_enabled != var_45);
        if (var_46) {
            // p=wp.quat_rotate_inv(rotation[e],newx-tool[e]);normal,distance=knife_normal(p,half_length);penetration=radius-distance       <L 96>
            var_47 = wp::address(var_rotation, var_1);
            var_48 = wp::address(var_tool, var_1);
            var_50 = wp::load(var_48);
            var_49 = wp::sub(var_43, var_50);
            var_52 = wp::load(var_47);
            var_51 = wp::quat_rotate_inv(var_52, var_49);
            knife_normal_0(var_51, var_half_length, var_53, var_54);
            var_55 = wp::sub(var_radius, var_54);
            // wp.atomic_max(penetration_peak,e,wp.max(penetration,0.))                           <L 97>
            var_57 = wp::max(var_55, var_56);
            var_58 = wp::atomic_max(var_penetration_peak, var_1, var_57);
            // if penetration>.0001:wp.atomic_max(bad,e,4);return                                 <L 98>
            var_60 = (var_55 > var_59);
            if (var_60) {
                var_62 = wp::atomic_max(var_bad, var_1, var_61);
                continue;
            }
            // if penetration>0.:                                                                 <L 99>
            var_64 = (var_55 > var_63);
            if (var_64) {
                // normal=wp.quat_rotate(rotation[e],normal);correction=penetration*normal;impulse=m/dt*correction;newx+=correction;newv+=impulse/m       <L 100>
                var_65 = wp::address(var_rotation, var_1);
                var_67 = wp::load(var_65);
                var_66 = wp::quat_rotate(var_67, var_53);
                var_68 = wp::mul(var_55, var_66);
                var_69 = wp::div(var_32, var_dt);
                var_70 = wp::mul(var_69, var_68);
                var_71 = wp::add(var_43, var_68);
                var_72 = wp::div(var_70, var_32);
                var_73 = wp::add(var_39, var_72);
                // rel=newv-velocity[e];tangent=rel-wp.dot(rel,normal)*normal;length=wp.length(tangent);friction=wp.vec3(0.)       <L 101>
                var_74 = wp::address(var_velocity, var_1);
                var_76 = wp::load(var_74);
                var_75 = wp::sub(var_73, var_76);
                var_77 = wp::dot(var_75, var_66);
                var_78 = wp::mul(var_77, var_66);
                var_79 = wp::sub(var_75, var_78);
                var_80 = wp::length(var_79);
                var_82 = wp::vec_t<3, wp::float32>(var_81);
                // if length>1e-12:friction=-wp.min(.2*wp.length(impulse),m*length)*tangent/length;newv+=friction/m       <L 102>
                var_84 = (var_80 > var_83);
                if (var_84) {
                    var_86 = wp::length(var_70);
                    var_87 = wp::mul(var_85, var_86);
                    var_88 = wp::mul(var_32, var_80);
                    var_89 = wp::min(var_87, var_88);
                    var_90 = wp::neg(var_89);
                    var_91 = wp::mul(var_90, var_79);
                    var_92 = wp::div(var_91, var_80);
                    var_93 = wp::div(var_92, var_32);
                    var_94 = wp::add(var_73, var_93);
                }
                var_95 = wp::where(var_84, var_94, var_73);
                var_96 = wp::where(var_84, var_92, var_82);
                // total=impulse+friction;wp.atomic_sub(reaction,e,total/dt);wp.atomic_add(load,e,wp.length(total)/dt);wp.atomic_add(ledger,e,2,wp.dot(total,velocity[e]));wp.atomic_add(ledger,e,4,-wp.dot(friction,rel))       <L 103>
                var_97 = wp::add(var_70, var_96);
                var_98 = wp::div(var_97, var_dt);
                var_99 = wp::atomic_sub(var_reaction, var_1, var_98);
                var_100 = wp::length(var_97);
                var_101 = wp::div(var_100, var_dt);
                var_102 = wp::atomic_add(var_load, var_1, var_101);
                var_104 = wp::address(var_velocity, var_1);
                var_106 = wp::load(var_104);
                var_105 = wp::dot(var_97, var_106);
                var_107 = wp::atomic_add(var_ledger, var_1, var_103, var_105);
                var_109 = wp::dot(var_96, var_75);
                var_110 = wp::neg(var_109);
                var_111 = wp::atomic_add(var_ledger, var_1, var_108, var_110);
            }
            var_112 = wp::where(var_64, var_66, var_53);
            var_113 = wp::where(var_64, var_95, var_39);
            var_114 = wp::where(var_64, var_71, var_43);
        }
        var_115 = wp::where(var_46, var_51, var_18);
        var_116 = wp::where(var_46, var_112, var_20);
        var_117 = wp::where(var_46, var_54, var_21);
        var_118 = wp::where(var_46, var_55, var_22);
        var_119 = wp::where(var_46, var_113, var_39);
        var_120 = wp::where(var_46, var_114, var_43);
        // if newx[1]<radius:                                                                     <L 104>
        var_122 = wp::extract(var_120, var_121);
        var_123 = (var_122 < var_radius);
        if (var_123) {
            // old_ke=.5*m*wp.dot(newv,newv)                                                      <L 105>
            var_125 = wp::mul(var_124, var_32);
            var_126 = wp::dot(var_119, var_119);
            var_127 = wp::mul(var_125, var_126);
            // newx[1]=radius                                                                     <L 106>
            wp::assign_inplace(var_120, var_128, var_radius);
            // if newv[1]<0.:                                                                     <L 107>
            var_130 = wp::extract(var_119, var_129);
            var_132 = (var_130 < var_131);
            if (var_132) {
                // normal_speed=-newv[1];newv[1]=0.;horizontal=wp.vec3(newv[0],0.,newv[2]);speed=wp.length(horizontal)       <L 108>
                var_134 = wp::extract(var_119, var_133);
                var_135 = wp::neg(var_134);
                wp::assign_inplace(var_119, var_137, var_136);
                var_139 = wp::extract(var_119, var_138);
                var_142 = wp::extract(var_119, var_141);
                var_143 = wp::vec_t<3, wp::float32>(var_139, var_140, var_142);
                var_144 = wp::length(var_143);
                // if speed>1e-12:newv-=wp.min(.4*normal_speed,speed)*horizontal/speed            <L 109>
                var_146 = (var_144 > var_145);
                if (var_146) {
                    var_148 = wp::mul(var_147, var_135);
                    var_149 = wp::min(var_148, var_144);
                    var_150 = wp::mul(var_149, var_143);
                    var_151 = wp::div(var_150, var_144);
                    var_152 = wp::sub(var_119, var_151);
                }
                var_153 = wp::where(var_146, var_152, var_119);
            }
            var_154 = wp::where(var_132, var_153, var_119);
            // wp.atomic_add(ledger,e,6,wp.max(old_ke-.5*m*wp.dot(newv,newv),0.))                 <L 110>
            var_157 = wp::mul(var_156, var_32);
            var_158 = wp::dot(var_154, var_154);
            var_159 = wp::mul(var_157, var_158);
            var_160 = wp::sub(var_127, var_159);
            var_162 = wp::max(var_160, var_161);
            var_163 = wp::atomic_add(var_ledger, var_1, var_155, var_162);
        }
        var_164 = wp::where(var_123, var_154, var_119);
        // if knife_enabled!=0:                                                                   <L 111>
        var_166 = (var_knife_enabled != var_165);
        if (var_166) {
            // p=wp.quat_rotate_inv(rotation[e],newx-tool[e]);normal,distance=knife_normal(p,half_length)       <L 112>
            var_167 = wp::address(var_rotation, var_1);
            var_168 = wp::address(var_tool, var_1);
            var_170 = wp::load(var_168);
            var_169 = wp::sub(var_120, var_170);
            var_172 = wp::load(var_167);
            var_171 = wp::quat_rotate_inv(var_172, var_169);
            knife_normal_0(var_171, var_half_length, var_173, var_174);
            // if radius-distance>.0001:wp.atomic_max(bad,e,4)                                    <L 113>
            var_175 = wp::sub(var_radius, var_174);
            var_177 = (var_175 > var_176);
            if (var_177) {
                var_179 = wp::atomic_max(var_bad, var_1, var_178);
            }
        }
        var_180 = wp::where(var_166, var_171, var_115);
        var_181 = wp::where(var_166, var_173, var_116);
        var_182 = wp::where(var_166, var_174, var_117);
        // if not wp.isfinite(newx[0]) or not wp.isfinite(newx[1]) or not wp.isfinite(newx[2]) or wp.length(newv)>10.:wp.atomic_max(bad,e,2)       <L 114>
        var_185 = wp::extract(var_120, var_184);
        var_186 = wp::isfinite(var_185);
        var_187 = wp::unot(var_186);
        var_183 = var_187;
        if (!var_183) {
            var_189 = wp::extract(var_120, var_188);
            var_190 = wp::isfinite(var_189);
            var_191 = wp::unot(var_190);
            var_183 = var_183 || var_191;
        }
        if (!var_183) {
            var_193 = wp::extract(var_120, var_192);
            var_194 = wp::isfinite(var_193);
            var_195 = wp::unot(var_194);
            var_183 = var_183 || var_195;
        }
        if (!var_183) {
            var_196 = wp::length(var_164);
            var_198 = (var_196 > var_197);
            var_183 = var_183 || var_198;
        }
        if (var_183) {
            var_200 = wp::atomic_max(var_bad, var_1, var_199);
        }
        // x[i]=newx;v[i]=newv                                                                    <L 115>
        wp::array_store(var_x, var_0, var_120);
        wp::array_store(var_v, var_0, var_164);
    }
}



extern "C" __global__ void particle_contacts_d18fc9fc_cuda_kernel_forward(
    wp::launch_bounds_t<1> dim,
    wp::uint64 var_grid,
    wp::array_t<wp::vec_t<3, wp::float32>> var_x,
    wp::array_t<wp::vec_t<3, wp::float32>> var_v,
    wp::array_t<wp::vec_t<3, wp::float32>> var_force,
    wp::array_t<wp::float32> var_mass,
    wp::array_t<wp::float32> var_ledger,
    wp::array_t<wp::int32> var_bad,
    wp::float32 var_radius,
    wp::float32 var_dt,
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
        wp::int32 var_1;
        wp::int32* var_2;
        const wp::int32 var_3 = 0;
        bool var_4;
        wp::int32 var_5;
        wp::vec_t<3, wp::float32>* var_6;
        const wp::float32 var_7 = 2.0;
        wp::float32 var_8;
        wp::hash_grid_query_f var_9;
        wp::vec_t<3, wp::float32> var_10;
        wp::int32 var_11;
        bool var_12;
        bool var_13;
        wp::int32 var_14;
        bool var_15;
        wp::vec_t<3, wp::float32>* var_16;
        wp::vec_t<3, wp::float32>* var_17;
        wp::vec_t<3, wp::float32> var_18;
        wp::vec_t<3, wp::float32> var_19;
        wp::vec_t<3, wp::float32> var_20;
        wp::float32 var_21;
        bool var_22;
        const wp::float32 var_23 = 2.0;
        wp::float32 var_24;
        bool var_25;
        const wp::float32 var_26 = 1e-08;
        bool var_27;
        wp::vec_t<3, wp::float32> var_28;
        wp::vec_t<3, wp::float32>* var_29;
        wp::vec_t<3, wp::float32>* var_30;
        wp::vec_t<3, wp::float32> var_31;
        wp::vec_t<3, wp::float32> var_32;
        wp::vec_t<3, wp::float32> var_33;
        wp::float32 var_34;
        wp::int32 var_35;
        wp::float32* var_36;
        wp::int32 var_37;
        wp::float32* var_38;
        wp::float32 var_39;
        wp::float32 var_40;
        wp::float32 var_41;
        wp::int32 var_42;
        wp::float32* var_43;
        wp::int32 var_44;
        wp::float32* var_45;
        wp::float32 var_46;
        wp::float32 var_47;
        wp::float32 var_48;
        wp::float32 var_49;
        const wp::float32 var_50 = 0.4;
        const wp::float32 var_51 = 1000.0;
        wp::float32 var_52;
        wp::float32 var_53;
        wp::float32 var_54;
        const wp::float32 var_55 = 1000.0;
        const wp::float32 var_56 = 2.0;
        wp::float32 var_57;
        wp::float32 var_58;
        wp::float32 var_59;
        wp::float32 var_60;
        wp::float32 var_61;
        const wp::float32 var_62 = 0.0;
        wp::float32 var_63;
        wp::vec_t<3, wp::float32> var_64;
        wp::vec_t<3, wp::float32> var_65;
        wp::float32 var_66;
        const wp::float32 var_67 = 0.0;
        wp::vec_t<3, wp::float32> var_68;
        const wp::float32 var_69 = 1e-10;
        bool var_70;
        const wp::float32 var_71 = 0.2;
        wp::float32 var_72;
        wp::float32 var_73;
        wp::float32 var_74;
        wp::float32 var_75;
        wp::float32 var_76;
        wp::vec_t<3, wp::float32> var_77;
        wp::vec_t<3, wp::float32> var_78;
        wp::vec_t<3, wp::float32> var_79;
        wp::vec_t<3, wp::float32> var_80;
        wp::vec_t<3, wp::float32> var_81;
        wp::vec_t<3, wp::float32> var_82;
        wp::vec_t<3, wp::float32> var_83;
        const wp::int32 var_84 = 5;
        wp::float32 var_85;
        wp::float32 var_86;
        wp::float32 var_87;
        wp::float32 var_88;
        const wp::float32 var_89 = 0.0;
        wp::float32 var_90;
        wp::float32 var_91;
        wp::float32 var_92;
        //---------
        // forward
        // def particle_contacts(grid:wp.uint64,x:wp.array(dtype=wp.vec3),v:wp.array(dtype=wp.vec3),force:wp.array(dtype=wp.vec3),mass:wp.array(dtype=float),ledger:wp.array2d(dtype=float),bad:wp.array(dtype=int),radius:float,dt:float,n:int):       <L 10>
        // i=wp.tid();e=i//n                                                                      <L 11>
        var_0 = builtin_tid1d();
        var_1 = wp::floordiv(var_0, var_n);
        // if bad[e]!=0:return                                                                    <L 12>
        var_2 = wp::address(var_bad, var_1);
        var_5 = wp::load(var_2);
        var_4 = (var_5 != var_3);
        if (var_4) {
            continue;
        }
        // neighbors=wp.hash_grid_query(grid,x[i],2.*radius)                                      <L 13>
        var_6 = wp::address(var_x, var_0);
        var_8 = wp::mul(var_7, var_radius);
        var_10 = wp::load(var_6);
        var_9 = wp::hash_grid_query(var_grid, var_10, var_8);
        // for j in neighbors:                                                                    <L 14>
        start_for_1:;
            if (iter_cmp(var_9) == 0) goto end_for_1;
            var_11 = wp::iter_next(var_9);
            // if j>i and j//n==e:                                                                <L 15>
            var_13 = (var_11 > var_0);
            var_12 = var_13;
            if (var_12) {
                var_14 = wp::floordiv(var_11, var_n);
                var_15 = (var_14 == var_1);
                var_12 = var_12 && var_15;
            }
            if (var_12) {
                // delta=x[j]-x[i];distance=wp.length(delta)                                      <L 16>
                var_16 = wp::address(var_x, var_11);
                var_17 = wp::address(var_x, var_0);
                var_19 = wp::load(var_16);
                var_20 = wp::load(var_17);
                var_18 = wp::sub(var_19, var_20);
                var_21 = wp::length(var_18);
                // if distance<2.*radius and distance>1e-8:                                       <L 17>
                var_24 = wp::mul(var_23, var_radius);
                var_25 = (var_21 < var_24);
                var_22 = var_25;
                if (var_22) {
                    var_27 = (var_21 > var_26);
                    var_22 = var_22 && var_27;
                }
                if (var_22) {
                    // normal=delta/distance;rel=v[j]-v[i];speed=wp.dot(rel,normal);reduced=mass[i%n]*mass[j%n]/(mass[i%n]+mass[j%n]);damping=.4*wp.sqrt(1000.*reduced)       <L 18>
                    var_28 = wp::div(var_18, var_21);
                    var_29 = wp::address(var_v, var_11);
                    var_30 = wp::address(var_v, var_0);
                    var_32 = wp::load(var_29);
                    var_33 = wp::load(var_30);
                    var_31 = wp::sub(var_32, var_33);
                    var_34 = wp::dot(var_31, var_28);
                    var_35 = wp::mod(var_0, var_n);
                    var_36 = wp::address(var_mass, var_35);
                    var_37 = wp::mod(var_11, var_n);
                    var_38 = wp::address(var_mass, var_37);
                    var_40 = wp::load(var_36);
                    var_41 = wp::load(var_38);
                    var_39 = wp::mul(var_40, var_41);
                    var_42 = wp::mod(var_0, var_n);
                    var_43 = wp::address(var_mass, var_42);
                    var_44 = wp::mod(var_11, var_n);
                    var_45 = wp::address(var_mass, var_44);
                    var_47 = wp::load(var_43);
                    var_48 = wp::load(var_45);
                    var_46 = wp::add(var_47, var_48);
                    var_49 = wp::div(var_39, var_46);
                    var_52 = wp::mul(var_51, var_49);
                    var_53 = wp::sqrt(var_52);
                    var_54 = wp::mul(var_50, var_53);
                    // magnitude=wp.max(1000.*(2.*radius-distance)-damping*speed,0.);tangent=rel-speed*normal;slip=wp.length(tangent);friction=wp.vec3(0.)       <L 19>
                    var_57 = wp::mul(var_56, var_radius);
                    var_58 = wp::sub(var_57, var_21);
                    var_59 = wp::mul(var_55, var_58);
                    var_60 = wp::mul(var_54, var_34);
                    var_61 = wp::sub(var_59, var_60);
                    var_63 = wp::max(var_61, var_62);
                    var_64 = wp::mul(var_34, var_28);
                    var_65 = wp::sub(var_31, var_64);
                    var_66 = wp::length(var_65);
                    var_68 = wp::vec_t<3, wp::float32>(var_67);
                    // if slip>1e-10:friction=-wp.min(.2*magnitude,reduced*slip/dt)*tangent/slip       <L 20>
                    var_70 = (var_66 > var_69);
                    if (var_70) {
                        var_72 = wp::mul(var_71, var_63);
                        var_73 = wp::mul(var_49, var_66);
                        var_74 = wp::div(var_73, var_dt);
                        var_75 = wp::min(var_72, var_74);
                        var_76 = wp::neg(var_75);
                        var_77 = wp::mul(var_76, var_65);
                        var_78 = wp::div(var_77, var_66);
                    }
                    var_79 = wp::where(var_70, var_78, var_68);
                    // f=magnitude*normal+friction;wp.atomic_sub(force,i,f);wp.atomic_add(force,j,f);wp.atomic_add(ledger,e,5,wp.max(damping*speed*speed-wp.dot(friction,rel),0.)*dt)       <L 21>
                    var_80 = wp::mul(var_63, var_28);
                    var_81 = wp::add(var_80, var_79);
                    var_82 = wp::atomic_sub(var_force, var_0, var_81);
                    var_83 = wp::atomic_add(var_force, var_11, var_81);
                    var_85 = wp::mul(var_54, var_34);
                    var_86 = wp::mul(var_85, var_34);
                    var_87 = wp::dot(var_79, var_31);
                    var_88 = wp::sub(var_86, var_87);
                    var_90 = wp::max(var_88, var_89);
                    var_91 = wp::mul(var_90, var_dt);
                    var_92 = wp::atomic_add(var_ledger, var_1, var_84, var_91);
                }
            }
            goto start_for_1;
        end_for_1:;
    }
}


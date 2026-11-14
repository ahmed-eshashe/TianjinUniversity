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


// /home/omen/Documents/Codex/experiments/tomato_approx_rl_20261113_v28/src/solver.py:72
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
    // def knife_normal(p:wp.vec3,half_length:float):                                         <L 73>
    // q=wp.vec2(p[0],p[1]);best=float(1e9);near=wp.vec2(0.)                                  <L 75>
    var_1 = wp::extract(var_p, var_0);
    var_3 = wp::extract(var_p, var_2);
    var_4 = wp::vec_t<2, wp::float32>(var_1, var_3);
    var_6 = wp::float(var_5);
    var_8 = wp::vec_t<2, wp::float32>(var_7);
    // for k in range(3):                                                                     <L 76>
    // a=wp.vec2(0.,0.);b=wp.vec2(.0005,.03)                                                  <L 77>
    var_12 = wp::vec_t<2, wp::float32>(var_10, var_11);
    var_15 = wp::vec_t<2, wp::float32>(var_13, var_14);
    // if k==1:a=wp.vec2(.0005,.03);b=wp.vec2(-.0005,.03)                                     <L 78>
    var_17 = (var_9 == var_16);
    if (var_17) {
        var_20 = wp::vec_t<2, wp::float32>(var_18, var_19);
        var_23 = wp::vec_t<2, wp::float32>(var_21, var_22);
    }
    var_24 = wp::where(var_17, var_20, var_12);
    var_25 = wp::where(var_17, var_23, var_15);
    // if k==2:a=wp.vec2(-.0005,.03);b=wp.vec2(0.,0.)                                         <L 79>
    var_27 = (var_9 == var_26);
    if (var_27) {
        var_30 = wp::vec_t<2, wp::float32>(var_28, var_29);
        var_33 = wp::vec_t<2, wp::float32>(var_31, var_32);
    }
    var_34 = wp::where(var_27, var_30, var_24);
    var_35 = wp::where(var_27, var_33, var_25);
    // ab=b-a;t=wp.clamp(wp.dot(q-a,ab)/wp.dot(ab,ab),0.,1.);point=a+t*ab;d=wp.length(q-point)       <L 80>
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
    // if d<best:best=d;near=point                                                            <L 81>
    var_48 = (var_47 < var_6);
    if (var_48) {
        var_49 = wp::copy(var_47);
        var_50 = wp::copy(var_45);
    }
    var_51 = wp::where(var_48, var_49, var_6);
    var_52 = wp::where(var_48, var_50, var_8);
    // a=wp.vec2(0.,0.);b=wp.vec2(.0005,.03)                                                  <L 77>
    var_56 = wp::vec_t<2, wp::float32>(var_54, var_55);
    var_59 = wp::vec_t<2, wp::float32>(var_57, var_58);
    // if k==1:a=wp.vec2(.0005,.03);b=wp.vec2(-.0005,.03)                                     <L 78>
    var_61 = (var_53 == var_60);
    if (var_61) {
        var_64 = wp::vec_t<2, wp::float32>(var_62, var_63);
        var_67 = wp::vec_t<2, wp::float32>(var_65, var_66);
    }
    var_68 = wp::where(var_61, var_64, var_56);
    var_69 = wp::where(var_61, var_67, var_59);
    // if k==2:a=wp.vec2(-.0005,.03);b=wp.vec2(0.,0.)                                         <L 79>
    var_71 = (var_53 == var_70);
    if (var_71) {
        var_74 = wp::vec_t<2, wp::float32>(var_72, var_73);
        var_77 = wp::vec_t<2, wp::float32>(var_75, var_76);
    }
    var_78 = wp::where(var_71, var_74, var_68);
    var_79 = wp::where(var_71, var_77, var_69);
    // ab=b-a;t=wp.clamp(wp.dot(q-a,ab)/wp.dot(ab,ab),0.,1.);point=a+t*ab;d=wp.length(q-point)       <L 80>
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
    // if d<best:best=d;near=point                                                            <L 81>
    var_92 = (var_91 < var_51);
    if (var_92) {
        var_93 = wp::copy(var_91);
        var_94 = wp::copy(var_89);
    }
    var_95 = wp::where(var_92, var_93, var_51);
    var_96 = wp::where(var_92, var_94, var_52);
    // a=wp.vec2(0.,0.);b=wp.vec2(.0005,.03)                                                  <L 77>
    var_100 = wp::vec_t<2, wp::float32>(var_98, var_99);
    var_103 = wp::vec_t<2, wp::float32>(var_101, var_102);
    // if k==1:a=wp.vec2(.0005,.03);b=wp.vec2(-.0005,.03)                                     <L 78>
    var_105 = (var_97 == var_104);
    if (var_105) {
        var_108 = wp::vec_t<2, wp::float32>(var_106, var_107);
        var_111 = wp::vec_t<2, wp::float32>(var_109, var_110);
    }
    var_112 = wp::where(var_105, var_108, var_100);
    var_113 = wp::where(var_105, var_111, var_103);
    // if k==2:a=wp.vec2(-.0005,.03);b=wp.vec2(0.,0.)                                         <L 79>
    var_115 = (var_97 == var_114);
    if (var_115) {
        var_118 = wp::vec_t<2, wp::float32>(var_116, var_117);
        var_121 = wp::vec_t<2, wp::float32>(var_119, var_120);
    }
    var_122 = wp::where(var_115, var_118, var_112);
    var_123 = wp::where(var_115, var_121, var_113);
    // ab=b-a;t=wp.clamp(wp.dot(q-a,ab)/wp.dot(ab,ab),0.,1.);point=a+t*ab;d=wp.length(q-point)       <L 80>
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
    // if d<best:best=d;near=point                                                            <L 81>
    var_136 = (var_135 < var_95);
    if (var_136) {
        var_137 = wp::copy(var_135);
        var_138 = wp::copy(var_133);
    }
    var_139 = wp::where(var_136, var_137, var_95);
    var_140 = wp::where(var_136, var_138, var_96);
    // inside=p[1]>=0. and p[1]<=.03 and wp.abs(p[0])<=p[1]/60.                               <L 82>
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
    // normal2=wp.vec2(1.,0.);distance2=best                                                  <L 83>
    var_160 = wp::vec_t<2, wp::float32>(var_158, var_159);
    var_161 = wp::copy(var_139);
    // if best>1e-12:normal2=(q-near)/best                                                    <L 84>
    var_163 = (var_139 > var_162);
    if (var_163) {
        var_164 = wp::sub(var_4, var_140);
        var_165 = wp::div(var_164, var_139);
    }
    var_166 = wp::where(var_163, var_165, var_160);
    // if inside:distance2=-best;normal2=-normal2                                             <L 85>
    if (var_141) {
        var_167 = wp::neg(var_139);
        var_168 = wp::neg(var_166);
    }
    var_169 = wp::where(var_141, var_168, var_166);
    var_170 = wp::where(var_141, var_167, var_161);
    // dz=wp.abs(p[2])-half_length;az=wp.max(dz,0.);axy=wp.max(distance2,0.);distance=wp.sqrt(az*az+axy*axy)+wp.min(wp.max(distance2,dz),0.);normal=wp.vec3(normal2[0],normal2[1],0.)       <L 86>
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
    // if dz>distance2 and distance2<=0.:normal=wp.vec3(0.,0.,wp.sign(p[2]))                  <L 87>
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
        // elif az>0.:                                                                        <L 88>
        var_204 = (var_176 > var_203);
        if (var_204) {
            // norm=wp.sqrt(az*az+axy*axy);normal=wp.vec3(axy*normal2[0],axy*normal2[1],az*wp.sign(p[2]))/norm       <L 89>
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
    // return normal,distance                                                                 <L 90>
    ret_0 = var_222;
    ret_1 = var_186;
    return;
}


// /home/omen/Documents/Codex/experiments/tomato_approx_rl_20261113_v28/src/solver.py:72
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



extern "C" __global__ void grid_motion_guard_07e5a7a1_cuda_kernel_forward(
    wp::launch_bounds_t<1> dim,
    wp::array_t<wp::vec_t<3, wp::float32>> var_x,
    wp::array_t<wp::vec_t<3, wp::float32>> var_reference,
    wp::array_t<wp::int32> var_bad,
    wp::float32 var_skin,
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
        wp::vec_t<3, wp::float32>* var_1;
        wp::vec_t<3, wp::float32>* var_2;
        wp::vec_t<3, wp::float32> var_3;
        wp::vec_t<3, wp::float32> var_4;
        wp::vec_t<3, wp::float32> var_5;
        wp::float32 var_6;
        bool var_7;
        wp::int32 var_8;
        const wp::int32 var_9 = 5;
        wp::int32 var_10;
        //---------
        // forward
        // def grid_motion_guard(x:wp.array(dtype=wp.vec3),reference:wp.array(dtype=wp.vec3),bad:wp.array(dtype=int),skin:float,n:int):       <L 10>
        // i=wp.tid()                                                                             <L 11>
        var_0 = builtin_tid1d();
        // if wp.length(x[i]-reference[i])>skin:wp.atomic_max(bad,i//n,5)                         <L 12>
        var_1 = wp::address(var_x, var_0);
        var_2 = wp::address(var_reference, var_0);
        var_4 = wp::load(var_1);
        var_5 = wp::load(var_2);
        var_3 = wp::sub(var_4, var_5);
        var_6 = wp::length(var_3);
        var_7 = (var_6 > var_skin);
        if (var_7) {
            var_8 = wp::floordiv(var_0, var_n);
            var_10 = wp::atomic_max(var_bad, var_8, var_9);
        }
    }
}



extern "C" __global__ void integrate_0d602b63_cuda_kernel_forward(
    wp::launch_bounds_t<1> dim,
    wp::array_t<wp::vec_t<3, wp::float32>> var_x,
    wp::array_t<wp::int32> var_fixed,
    wp::array_t<wp::vec_t<3, wp::float32>> var_v,
    wp::array_t<wp::vec_t<3, wp::float32>> var_force,
    wp::array_t<wp::float32> var_mass,
    wp::array_t<wp::vec_t<3, wp::float32>> var_tool,
    wp::array_t<wp::vec_t<3, wp::float32>> var_velocity,
    wp::array_t<wp::vec_t<3, wp::float32>> var_angular_velocity,
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
        wp::vec_t<3, wp::float32>* var_75;
        wp::vec_t<3, wp::float32>* var_76;
        wp::vec_t<3, wp::float32> var_77;
        wp::vec_t<3, wp::float32> var_78;
        wp::vec_t<3, wp::float32> var_79;
        wp::vec_t<3, wp::float32> var_80;
        wp::vec_t<3, wp::float32> var_81;
        wp::vec_t<3, wp::float32> var_82;
        wp::vec_t<3, wp::float32> var_83;
        wp::float32 var_84;
        wp::vec_t<3, wp::float32> var_85;
        wp::vec_t<3, wp::float32> var_86;
        wp::float32 var_87;
        const wp::float32 var_88 = 0.0;
        wp::vec_t<3, wp::float32> var_89;
        const wp::float32 var_90 = 1e-12;
        bool var_91;
        const wp::float32 var_92 = 0.2;
        wp::float32 var_93;
        wp::float32 var_94;
        wp::float32 var_95;
        wp::float32 var_96;
        wp::float32 var_97;
        wp::vec_t<3, wp::float32> var_98;
        wp::vec_t<3, wp::float32> var_99;
        wp::vec_t<3, wp::float32> var_100;
        wp::vec_t<3, wp::float32> var_101;
        wp::vec_t<3, wp::float32> var_102;
        wp::vec_t<3, wp::float32> var_103;
        wp::vec_t<3, wp::float32> var_104;
        wp::vec_t<3, wp::float32> var_105;
        wp::vec_t<3, wp::float32> var_106;
        wp::float32 var_107;
        wp::float32 var_108;
        wp::float32 var_109;
        const wp::int32 var_110 = 2;
        wp::float32 var_111;
        wp::float32 var_112;
        const wp::int32 var_113 = 4;
        wp::float32 var_114;
        wp::float32 var_115;
        wp::float32 var_116;
        wp::vec_t<3, wp::float32> var_117;
        wp::vec_t<3, wp::float32> var_118;
        wp::vec_t<3, wp::float32> var_119;
        wp::vec_t<3, wp::float32> var_120;
        wp::vec_t<3, wp::float32> var_121;
        wp::float32 var_122;
        wp::float32 var_123;
        wp::vec_t<3, wp::float32> var_124;
        wp::vec_t<3, wp::float32> var_125;
        const wp::int32 var_126 = 1;
        wp::float32 var_127;
        bool var_128;
        const wp::float32 var_129 = 0.5;
        wp::float32 var_130;
        wp::float32 var_131;
        wp::float32 var_132;
        const wp::int32 var_133 = 1;
        const wp::int32 var_134 = 1;
        wp::float32 var_135;
        const wp::float32 var_136 = 0.0;
        bool var_137;
        const wp::int32 var_138 = 1;
        wp::float32 var_139;
        wp::float32 var_140;
        const wp::float32 var_141 = 0.0;
        const wp::int32 var_142 = 1;
        const wp::int32 var_143 = 0;
        wp::float32 var_144;
        const wp::float32 var_145 = 0.0;
        const wp::int32 var_146 = 2;
        wp::float32 var_147;
        wp::vec_t<3, wp::float32> var_148;
        wp::float32 var_149;
        const wp::float32 var_150 = 1e-12;
        bool var_151;
        const wp::float32 var_152 = 0.4;
        wp::float32 var_153;
        wp::float32 var_154;
        wp::vec_t<3, wp::float32> var_155;
        wp::vec_t<3, wp::float32> var_156;
        wp::vec_t<3, wp::float32> var_157;
        wp::vec_t<3, wp::float32> var_158;
        wp::vec_t<3, wp::float32> var_159;
        const wp::int32 var_160 = 6;
        const wp::float32 var_161 = 0.5;
        wp::float32 var_162;
        wp::float32 var_163;
        wp::float32 var_164;
        wp::float32 var_165;
        const wp::float32 var_166 = 0.0;
        wp::float32 var_167;
        wp::float32 var_168;
        wp::vec_t<3, wp::float32> var_169;
        const wp::int32 var_170 = 0;
        bool var_171;
        wp::quat_t<wp::float32>* var_172;
        wp::vec_t<3, wp::float32>* var_173;
        wp::vec_t<3, wp::float32> var_174;
        wp::vec_t<3, wp::float32> var_175;
        wp::vec_t<3, wp::float32> var_176;
        wp::quat_t<wp::float32> var_177;
        wp::vec_t<3, wp::float32> var_178;
        wp::float32 var_179;
        wp::float32 var_180;
        const wp::float32 var_181 = 0.0001;
        bool var_182;
        const wp::int32 var_183 = 4;
        wp::int32 var_184;
        wp::vec_t<3, wp::float32> var_185;
        wp::vec_t<3, wp::float32> var_186;
        wp::float32 var_187;
        bool var_188;
        const wp::int32 var_189 = 0;
        wp::float32 var_190;
        bool var_191;
        bool var_192;
        const wp::int32 var_193 = 1;
        wp::float32 var_194;
        bool var_195;
        bool var_196;
        const wp::int32 var_197 = 2;
        wp::float32 var_198;
        bool var_199;
        bool var_200;
        wp::float32 var_201;
        const wp::float32 var_202 = 10.0;
        bool var_203;
        const wp::int32 var_204 = 2;
        wp::int32 var_205;
        //---------
        // forward
        // def integrate(x:wp.array(dtype=wp.vec3),fixed:wp.array(dtype=int),v:wp.array(dtype=wp.vec3),force:wp.array(dtype=wp.vec3),mass:wp.array(dtype=float),tool:wp.array(dtype=wp.vec3),velocity:wp.array(dtype=wp.vec3),angular_velocity:wp.array(dtype=wp.vec3),rotation:wp.array(dtype=wp.quat),reaction:wp.array(dtype=wp.vec3),load:wp.array(dtype=float),ledger:wp.array2d(dtype=float),penetration_peak:wp.array(dtype=float),bad:wp.array(dtype=int),dt:float,radius:float,n:int,half_length:float,knife_enabled:int):       <L 93>
        // i=wp.tid();e=i//n                                                                      <L 94>
        var_0 = builtin_tid1d();
        var_1 = wp::floordiv(var_0, var_n);
        // if bad[e]!=0:return                                                                    <L 95>
        var_2 = wp::address(var_bad, var_1);
        var_5 = wp::load(var_2);
        var_4 = (var_5 != var_3);
        if (var_4) {
            continue;
        }
        // if fixed[i]!=0:                                                                        <L 96>
        var_6 = wp::address(var_fixed, var_0);
        var_9 = wp::load(var_6);
        var_8 = (var_9 != var_7);
        if (var_8) {
            // if knife_enabled!=0:                                                               <L 97>
            var_11 = (var_knife_enabled != var_10);
            if (var_11) {
                // p=wp.quat_rotate_inv(rotation[e],x[i]-tool[e]);normal,distance=knife_normal(p,half_length);penetration=radius-distance       <L 98>
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
                // wp.atomic_max(penetration_peak,e,wp.max(penetration,0.))                       <L 99>
                var_24 = wp::max(var_22, var_23);
                var_25 = wp::atomic_max(var_penetration_peak, var_1, var_24);
                // if penetration>.0001:wp.atomic_max(bad,e,4)                                    <L 100>
                var_27 = (var_22 > var_26);
                if (var_27) {
                    var_29 = wp::atomic_max(var_bad, var_1, var_28);
                }
            }
            // return                                                                             <L 101>
            continue;
        }
        // m=mass[i%n];newv=v[i]+dt*force[i]/m;newx=x[i]+dt*newv                                  <L 102>
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
        // if knife_enabled!=0:                                                                   <L 103>
        var_46 = (var_knife_enabled != var_45);
        if (var_46) {
            // p=wp.quat_rotate_inv(rotation[e],newx-tool[e]);normal,distance=knife_normal(p,half_length);penetration=radius-distance       <L 104>
            var_47 = wp::address(var_rotation, var_1);
            var_48 = wp::address(var_tool, var_1);
            var_50 = wp::load(var_48);
            var_49 = wp::sub(var_43, var_50);
            var_52 = wp::load(var_47);
            var_51 = wp::quat_rotate_inv(var_52, var_49);
            knife_normal_0(var_51, var_half_length, var_53, var_54);
            var_55 = wp::sub(var_radius, var_54);
            // wp.atomic_max(penetration_peak,e,wp.max(penetration,0.))                           <L 105>
            var_57 = wp::max(var_55, var_56);
            var_58 = wp::atomic_max(var_penetration_peak, var_1, var_57);
            // if penetration>.0001:wp.atomic_max(bad,e,4);return                                 <L 106>
            var_60 = (var_55 > var_59);
            if (var_60) {
                var_62 = wp::atomic_max(var_bad, var_1, var_61);
                continue;
            }
            // if penetration>0.:                                                                 <L 107>
            var_64 = (var_55 > var_63);
            if (var_64) {
                // normal=wp.quat_rotate(rotation[e],normal);correction=penetration*normal;impulse=m/dt*correction;newx+=correction;newv+=impulse/m       <L 108>
                var_65 = wp::address(var_rotation, var_1);
                var_67 = wp::load(var_65);
                var_66 = wp::quat_rotate(var_67, var_53);
                var_68 = wp::mul(var_55, var_66);
                var_69 = wp::div(var_32, var_dt);
                var_70 = wp::mul(var_69, var_68);
                var_71 = wp::add(var_43, var_68);
                var_72 = wp::div(var_70, var_32);
                var_73 = wp::add(var_39, var_72);
                // blade_velocity=velocity[e]+wp.cross(angular_velocity[e],newx-tool[e]);rel=newv-blade_velocity;tangent=rel-wp.dot(rel,normal)*normal;length=wp.length(tangent);friction=wp.vec3(0.)       <L 109>
                var_74 = wp::address(var_velocity, var_1);
                var_75 = wp::address(var_angular_velocity, var_1);
                var_76 = wp::address(var_tool, var_1);
                var_78 = wp::load(var_76);
                var_77 = wp::sub(var_71, var_78);
                var_80 = wp::load(var_75);
                var_79 = wp::cross(var_80, var_77);
                var_82 = wp::load(var_74);
                var_81 = wp::add(var_82, var_79);
                var_83 = wp::sub(var_73, var_81);
                var_84 = wp::dot(var_83, var_66);
                var_85 = wp::mul(var_84, var_66);
                var_86 = wp::sub(var_83, var_85);
                var_87 = wp::length(var_86);
                var_89 = wp::vec_t<3, wp::float32>(var_88);
                // if length>1e-12:friction=-wp.min(.2*wp.length(impulse),m*length)*tangent/length;newv+=friction/m       <L 110>
                var_91 = (var_87 > var_90);
                if (var_91) {
                    var_93 = wp::length(var_70);
                    var_94 = wp::mul(var_92, var_93);
                    var_95 = wp::mul(var_32, var_87);
                    var_96 = wp::min(var_94, var_95);
                    var_97 = wp::neg(var_96);
                    var_98 = wp::mul(var_97, var_86);
                    var_99 = wp::div(var_98, var_87);
                    var_100 = wp::div(var_99, var_32);
                    var_101 = wp::add(var_73, var_100);
                }
                var_102 = wp::where(var_91, var_101, var_73);
                var_103 = wp::where(var_91, var_99, var_89);
                // total=impulse+friction;wp.atomic_sub(reaction,e,total/dt);wp.atomic_add(load,e,wp.length(total)/dt);wp.atomic_add(ledger,e,2,wp.dot(total,blade_velocity));wp.atomic_add(ledger,e,4,-wp.dot(friction,rel))       <L 111>
                var_104 = wp::add(var_70, var_103);
                var_105 = wp::div(var_104, var_dt);
                var_106 = wp::atomic_sub(var_reaction, var_1, var_105);
                var_107 = wp::length(var_104);
                var_108 = wp::div(var_107, var_dt);
                var_109 = wp::atomic_add(var_load, var_1, var_108);
                var_111 = wp::dot(var_104, var_81);
                var_112 = wp::atomic_add(var_ledger, var_1, var_110, var_111);
                var_114 = wp::dot(var_103, var_83);
                var_115 = wp::neg(var_114);
                var_116 = wp::atomic_add(var_ledger, var_1, var_113, var_115);
            }
            var_117 = wp::where(var_64, var_66, var_53);
            var_118 = wp::where(var_64, var_102, var_39);
            var_119 = wp::where(var_64, var_71, var_43);
        }
        var_120 = wp::where(var_46, var_51, var_18);
        var_121 = wp::where(var_46, var_117, var_20);
        var_122 = wp::where(var_46, var_54, var_21);
        var_123 = wp::where(var_46, var_55, var_22);
        var_124 = wp::where(var_46, var_118, var_39);
        var_125 = wp::where(var_46, var_119, var_43);
        // if newx[1]<radius:                                                                     <L 112>
        var_127 = wp::extract(var_125, var_126);
        var_128 = (var_127 < var_radius);
        if (var_128) {
            // old_ke=.5*m*wp.dot(newv,newv)                                                      <L 113>
            var_130 = wp::mul(var_129, var_32);
            var_131 = wp::dot(var_124, var_124);
            var_132 = wp::mul(var_130, var_131);
            // newx[1]=radius                                                                     <L 114>
            wp::assign_inplace(var_125, var_133, var_radius);
            // if newv[1]<0.:                                                                     <L 115>
            var_135 = wp::extract(var_124, var_134);
            var_137 = (var_135 < var_136);
            if (var_137) {
                // normal_speed=-newv[1];newv[1]=0.;horizontal=wp.vec3(newv[0],0.,newv[2]);speed=wp.length(horizontal)       <L 116>
                var_139 = wp::extract(var_124, var_138);
                var_140 = wp::neg(var_139);
                wp::assign_inplace(var_124, var_142, var_141);
                var_144 = wp::extract(var_124, var_143);
                var_147 = wp::extract(var_124, var_146);
                var_148 = wp::vec_t<3, wp::float32>(var_144, var_145, var_147);
                var_149 = wp::length(var_148);
                // if speed>1e-12:newv-=wp.min(.4*normal_speed,speed)*horizontal/speed            <L 117>
                var_151 = (var_149 > var_150);
                if (var_151) {
                    var_153 = wp::mul(var_152, var_140);
                    var_154 = wp::min(var_153, var_149);
                    var_155 = wp::mul(var_154, var_148);
                    var_156 = wp::div(var_155, var_149);
                    var_157 = wp::sub(var_124, var_156);
                }
                var_158 = wp::where(var_151, var_157, var_124);
            }
            var_159 = wp::where(var_137, var_158, var_124);
            // wp.atomic_add(ledger,e,6,wp.max(old_ke-.5*m*wp.dot(newv,newv),0.))                 <L 118>
            var_162 = wp::mul(var_161, var_32);
            var_163 = wp::dot(var_159, var_159);
            var_164 = wp::mul(var_162, var_163);
            var_165 = wp::sub(var_132, var_164);
            var_167 = wp::max(var_165, var_166);
            var_168 = wp::atomic_add(var_ledger, var_1, var_160, var_167);
        }
        var_169 = wp::where(var_128, var_159, var_124);
        // if knife_enabled!=0:                                                                   <L 119>
        var_171 = (var_knife_enabled != var_170);
        if (var_171) {
            // p=wp.quat_rotate_inv(rotation[e],newx-tool[e]);normal,distance=knife_normal(p,half_length)       <L 120>
            var_172 = wp::address(var_rotation, var_1);
            var_173 = wp::address(var_tool, var_1);
            var_175 = wp::load(var_173);
            var_174 = wp::sub(var_125, var_175);
            var_177 = wp::load(var_172);
            var_176 = wp::quat_rotate_inv(var_177, var_174);
            knife_normal_0(var_176, var_half_length, var_178, var_179);
            // if radius-distance>.0001:wp.atomic_max(bad,e,4)                                    <L 121>
            var_180 = wp::sub(var_radius, var_179);
            var_182 = (var_180 > var_181);
            if (var_182) {
                var_184 = wp::atomic_max(var_bad, var_1, var_183);
            }
        }
        var_185 = wp::where(var_171, var_176, var_120);
        var_186 = wp::where(var_171, var_178, var_121);
        var_187 = wp::where(var_171, var_179, var_122);
        // if not wp.isfinite(newx[0]) or not wp.isfinite(newx[1]) or not wp.isfinite(newx[2]) or wp.length(newv)>10.:wp.atomic_max(bad,e,2)       <L 122>
        var_190 = wp::extract(var_125, var_189);
        var_191 = wp::isfinite(var_190);
        var_192 = wp::unot(var_191);
        var_188 = var_192;
        if (!var_188) {
            var_194 = wp::extract(var_125, var_193);
            var_195 = wp::isfinite(var_194);
            var_196 = wp::unot(var_195);
            var_188 = var_188 || var_196;
        }
        if (!var_188) {
            var_198 = wp::extract(var_125, var_197);
            var_199 = wp::isfinite(var_198);
            var_200 = wp::unot(var_199);
            var_188 = var_188 || var_200;
        }
        if (!var_188) {
            var_201 = wp::length(var_169);
            var_203 = (var_201 > var_202);
            var_188 = var_188 || var_203;
        }
        if (var_188) {
            var_205 = wp::atomic_max(var_bad, var_1, var_204);
        }
        // x[i]=newx;v[i]=newv                                                                    <L 123>
        wp::array_store(var_x, var_0, var_125);
        wp::array_store(var_v, var_0, var_169);
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
        // def finish_step(reaction:wp.array(dtype=wp.vec3),load:wp.array(dtype=float),peak:wp.array(dtype=float),bad:wp.array(dtype=int),stop_force:float):       <L 126>
        // e=wp.tid();peak[e]=wp.max(peak[e],load[e])                                             <L 127>
        var_0 = builtin_tid1d();
        var_1 = wp::address(var_peak, var_0);
        var_2 = wp::address(var_load, var_0);
        var_4 = wp::load(var_1);
        var_5 = wp::load(var_2);
        var_3 = wp::max(var_4, var_5);
        wp::array_store(var_peak, var_0, var_3);
        // if load[e]>stop_force or not wp.isfinite(load[e]):wp.atomic_max(bad,e,3)               <L 128>
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



extern "C" __global__ void particle_contacts_751ffca2_cuda_kernel_forward(
    wp::launch_bounds_t<1> dim,
    wp::uint64 var_grid,
    wp::array_t<wp::vec_t<3, wp::float32>> var_x,
    wp::array_t<wp::vec_t<3, wp::float32>> var_v,
    wp::array_t<wp::vec_t<3, wp::float32>> var_force,
    wp::array_t<wp::float32> var_mass,
    wp::array_t<wp::float32> var_ledger,
    wp::array_t<wp::int32> var_bad,
    wp::float32 var_radius,
    wp::float32 var_skin,
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
        wp::float32 var_9;
        wp::hash_grid_query_f var_10;
        wp::vec_t<3, wp::float32> var_11;
        wp::int32 var_12;
        bool var_13;
        bool var_14;
        wp::int32 var_15;
        bool var_16;
        wp::vec_t<3, wp::float32>* var_17;
        wp::vec_t<3, wp::float32>* var_18;
        wp::vec_t<3, wp::float32> var_19;
        wp::vec_t<3, wp::float32> var_20;
        wp::vec_t<3, wp::float32> var_21;
        wp::float32 var_22;
        bool var_23;
        const wp::float32 var_24 = 2.0;
        wp::float32 var_25;
        bool var_26;
        const wp::float32 var_27 = 1e-08;
        bool var_28;
        wp::vec_t<3, wp::float32> var_29;
        wp::vec_t<3, wp::float32>* var_30;
        wp::vec_t<3, wp::float32>* var_31;
        wp::vec_t<3, wp::float32> var_32;
        wp::vec_t<3, wp::float32> var_33;
        wp::vec_t<3, wp::float32> var_34;
        wp::float32 var_35;
        wp::int32 var_36;
        wp::float32* var_37;
        wp::int32 var_38;
        wp::float32* var_39;
        wp::float32 var_40;
        wp::float32 var_41;
        wp::float32 var_42;
        wp::int32 var_43;
        wp::float32* var_44;
        wp::int32 var_45;
        wp::float32* var_46;
        wp::float32 var_47;
        wp::float32 var_48;
        wp::float32 var_49;
        wp::float32 var_50;
        const wp::float32 var_51 = 0.4;
        const wp::float32 var_52 = 1000.0;
        wp::float32 var_53;
        wp::float32 var_54;
        wp::float32 var_55;
        const wp::float32 var_56 = 1000.0;
        const wp::float32 var_57 = 2.0;
        wp::float32 var_58;
        wp::float32 var_59;
        wp::float32 var_60;
        wp::float32 var_61;
        wp::float32 var_62;
        const wp::float32 var_63 = 0.0;
        wp::float32 var_64;
        wp::vec_t<3, wp::float32> var_65;
        wp::vec_t<3, wp::float32> var_66;
        wp::float32 var_67;
        const wp::float32 var_68 = 0.0;
        wp::vec_t<3, wp::float32> var_69;
        const wp::float32 var_70 = 1e-10;
        bool var_71;
        const wp::float32 var_72 = 0.2;
        wp::float32 var_73;
        wp::float32 var_74;
        wp::float32 var_75;
        wp::float32 var_76;
        wp::float32 var_77;
        wp::vec_t<3, wp::float32> var_78;
        wp::vec_t<3, wp::float32> var_79;
        wp::vec_t<3, wp::float32> var_80;
        wp::vec_t<3, wp::float32> var_81;
        wp::vec_t<3, wp::float32> var_82;
        wp::vec_t<3, wp::float32> var_83;
        wp::vec_t<3, wp::float32> var_84;
        const wp::int32 var_85 = 5;
        wp::float32 var_86;
        wp::float32 var_87;
        wp::float32 var_88;
        wp::float32 var_89;
        const wp::float32 var_90 = 0.0;
        wp::float32 var_91;
        wp::float32 var_92;
        wp::float32 var_93;
        //---------
        // forward
        // def particle_contacts(grid:wp.uint64,x:wp.array(dtype=wp.vec3),v:wp.array(dtype=wp.vec3),force:wp.array(dtype=wp.vec3),mass:wp.array(dtype=float),ledger:wp.array2d(dtype=float),bad:wp.array(dtype=int),radius:float,skin:float,dt:float,n:int):       <L 15>
        // i=wp.tid();e=i//n                                                                      <L 16>
        var_0 = builtin_tid1d();
        var_1 = wp::floordiv(var_0, var_n);
        // if bad[e]!=0:return                                                                    <L 17>
        var_2 = wp::address(var_bad, var_1);
        var_5 = wp::load(var_2);
        var_4 = (var_5 != var_3);
        if (var_4) {
            continue;
        }
        // neighbors=wp.hash_grid_query(grid,x[i],2.*radius+skin)                                 <L 18>
        var_6 = wp::address(var_x, var_0);
        var_8 = wp::mul(var_7, var_radius);
        var_9 = wp::add(var_8, var_skin);
        var_11 = wp::load(var_6);
        var_10 = wp::hash_grid_query(var_grid, var_11, var_9);
        // for j in neighbors:                                                                    <L 19>
        start_for_1:;
            if (iter_cmp(var_10) == 0) goto end_for_1;
            var_12 = wp::iter_next(var_10);
            // if j>i and j//n==e:                                                                <L 20>
            var_14 = (var_12 > var_0);
            var_13 = var_14;
            if (var_13) {
                var_15 = wp::floordiv(var_12, var_n);
                var_16 = (var_15 == var_1);
                var_13 = var_13 && var_16;
            }
            if (var_13) {
                // delta=x[j]-x[i];distance=wp.length(delta)                                      <L 21>
                var_17 = wp::address(var_x, var_12);
                var_18 = wp::address(var_x, var_0);
                var_20 = wp::load(var_17);
                var_21 = wp::load(var_18);
                var_19 = wp::sub(var_20, var_21);
                var_22 = wp::length(var_19);
                // if distance<2.*radius and distance>1e-8:                                       <L 22>
                var_25 = wp::mul(var_24, var_radius);
                var_26 = (var_22 < var_25);
                var_23 = var_26;
                if (var_23) {
                    var_28 = (var_22 > var_27);
                    var_23 = var_23 && var_28;
                }
                if (var_23) {
                    // normal=delta/distance;rel=v[j]-v[i];speed=wp.dot(rel,normal);reduced=mass[i%n]*mass[j%n]/(mass[i%n]+mass[j%n]);damping=.4*wp.sqrt(1000.*reduced)       <L 23>
                    var_29 = wp::div(var_19, var_22);
                    var_30 = wp::address(var_v, var_12);
                    var_31 = wp::address(var_v, var_0);
                    var_33 = wp::load(var_30);
                    var_34 = wp::load(var_31);
                    var_32 = wp::sub(var_33, var_34);
                    var_35 = wp::dot(var_32, var_29);
                    var_36 = wp::mod(var_0, var_n);
                    var_37 = wp::address(var_mass, var_36);
                    var_38 = wp::mod(var_12, var_n);
                    var_39 = wp::address(var_mass, var_38);
                    var_41 = wp::load(var_37);
                    var_42 = wp::load(var_39);
                    var_40 = wp::mul(var_41, var_42);
                    var_43 = wp::mod(var_0, var_n);
                    var_44 = wp::address(var_mass, var_43);
                    var_45 = wp::mod(var_12, var_n);
                    var_46 = wp::address(var_mass, var_45);
                    var_48 = wp::load(var_44);
                    var_49 = wp::load(var_46);
                    var_47 = wp::add(var_48, var_49);
                    var_50 = wp::div(var_40, var_47);
                    var_53 = wp::mul(var_52, var_50);
                    var_54 = wp::sqrt(var_53);
                    var_55 = wp::mul(var_51, var_54);
                    // magnitude=wp.max(1000.*(2.*radius-distance)-damping*speed,0.);tangent=rel-speed*normal;slip=wp.length(tangent);friction=wp.vec3(0.)       <L 24>
                    var_58 = wp::mul(var_57, var_radius);
                    var_59 = wp::sub(var_58, var_22);
                    var_60 = wp::mul(var_56, var_59);
                    var_61 = wp::mul(var_55, var_35);
                    var_62 = wp::sub(var_60, var_61);
                    var_64 = wp::max(var_62, var_63);
                    var_65 = wp::mul(var_35, var_29);
                    var_66 = wp::sub(var_32, var_65);
                    var_67 = wp::length(var_66);
                    var_69 = wp::vec_t<3, wp::float32>(var_68);
                    // if slip>1e-10:friction=-wp.min(.2*magnitude,reduced*slip/dt)*tangent/slip       <L 25>
                    var_71 = (var_67 > var_70);
                    if (var_71) {
                        var_73 = wp::mul(var_72, var_64);
                        var_74 = wp::mul(var_50, var_67);
                        var_75 = wp::div(var_74, var_dt);
                        var_76 = wp::min(var_73, var_75);
                        var_77 = wp::neg(var_76);
                        var_78 = wp::mul(var_77, var_66);
                        var_79 = wp::div(var_78, var_67);
                    }
                    var_80 = wp::where(var_71, var_79, var_69);
                    // f=magnitude*normal+friction;wp.atomic_sub(force,i,f);wp.atomic_add(force,j,f);wp.atomic_add(ledger,e,5,wp.max(damping*speed*speed-wp.dot(friction,rel),0.)*dt)       <L 26>
                    var_81 = wp::mul(var_64, var_29);
                    var_82 = wp::add(var_81, var_80);
                    var_83 = wp::atomic_sub(var_force, var_0, var_82);
                    var_84 = wp::atomic_add(var_force, var_12, var_82);
                    var_86 = wp::mul(var_55, var_35);
                    var_87 = wp::mul(var_86, var_35);
                    var_88 = wp::dot(var_80, var_32);
                    var_89 = wp::sub(var_87, var_88);
                    var_91 = wp::max(var_89, var_90);
                    var_92 = wp::mul(var_91, var_dt);
                    var_93 = wp::atomic_add(var_ledger, var_1, var_85, var_92);
                }
            }
            goto start_for_1;
        end_for_1:;
    }
}



extern "C" __global__ void clear_step_752727a1_cuda_kernel_forward(
    wp::launch_bounds_t<1> dim,
    wp::array_t<wp::vec_t<3, wp::float32>> var_x,
    wp::array_t<wp::vec_t<3, wp::float32>> var_force,
    wp::array_t<wp::float32> var_mass,
    wp::array_t<wp::vec_t<3, wp::float32>> var_reaction,
    wp::array_t<wp::float32> var_normal_load,
    wp::array_t<wp::vec_t<3, wp::float32>> var_drive,
    wp::array_t<wp::vec_t<3, wp::float32>> var_tool,
    wp::array_t<wp::vec_t<3, wp::float32>> var_action,
    wp::array_t<wp::vec_t<3, wp::float32>> var_angular_action,
    wp::array_t<wp::vec_t<3, wp::float32>> var_angular_velocity,
    wp::array_t<wp::quat_t<wp::float32>> var_rotation,
    wp::array_t<wp::float32> var_clock,
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
        wp::vec_t<3, wp::float32>* var_26;
        wp::vec_t<3, wp::float32> var_27;
        wp::vec_t<3, wp::float32>* var_28;
        wp::float32 var_29;
        wp::vec_t<3, wp::float32> var_30;
        const wp::float32 var_31 = 1e-10;
        bool var_32;
        wp::vec_t<3, wp::float32>* var_33;
        wp::vec_t<3, wp::float32> var_34;
        wp::vec_t<3, wp::float32> var_35;
        wp::float32 var_36;
        wp::quat_t<wp::float32> var_37;
        wp::quat_t<wp::float32>* var_38;
        wp::quat_t<wp::float32> var_39;
        wp::quat_t<wp::float32> var_40;
        wp::quat_t<wp::float32> var_41;
        const wp::float32 var_42 = 1.0;
        wp::float32 var_43;
        //---------
        // forward
        // def clear_step(x:wp.array(dtype=wp.vec3),force:wp.array(dtype=wp.vec3),mass:wp.array(dtype=float),reaction:wp.array(dtype=wp.vec3),normal_load:wp.array(dtype=float),drive:wp.array(dtype=wp.vec3),tool:wp.array(dtype=wp.vec3),action:wp.array(dtype=wp.vec3),angular_action:wp.array(dtype=wp.vec3),angular_velocity:wp.array(dtype=wp.vec3),rotation:wp.array(dtype=wp.quat),clock:wp.array(dtype=float),bad:wp.array(dtype=int),dt:float,n:int):       <L 29>
        // i=wp.tid();e=i//n;force[i]=wp.vec3(0.,-9.81*mass[i%n],0.)                              <L 30>
        var_0 = builtin_tid1d();
        var_1 = wp::floordiv(var_0, var_n);
        var_4 = wp::mod(var_0, var_n);
        var_5 = wp::address(var_mass, var_4);
        var_7 = wp::load(var_5);
        var_6 = wp::mul(var_3, var_7);
        var_9 = wp::vec_t<3, wp::float32>(var_2, var_6, var_8);
        wp::array_store(var_force, var_0, var_9);
        // if i%n==0:                                                                             <L 31>
        var_10 = wp::mod(var_0, var_n);
        var_12 = (var_10 == var_11);
        if (var_12) {
            // reaction[e]=wp.vec3(0.);normal_load[e]=0.;drive[e]=action[e]                       <L 32>
            var_14 = wp::vec_t<3, wp::float32>(var_13);
            wp::array_store(var_reaction, var_1, var_14);
            wp::array_store(var_normal_load, var_1, var_15);
            var_16 = wp::address(var_action, var_1);
            var_17 = wp::load(var_16);
            wp::array_store(var_drive, var_1, var_17);
            // if bad[e]==0:                                                                      <L 33>
            var_18 = wp::address(var_bad, var_1);
            var_21 = wp::load(var_18);
            var_20 = (var_21 == var_19);
            if (var_20) {
                // tool[e]+=dt*action[e];angular_velocity[e]=angular_action[e];omega=wp.length(angular_action[e])       <L 34>
                var_22 = wp::address(var_action, var_1);
                var_24 = wp::load(var_22);
                var_23 = wp::mul(var_dt, var_24);
                var_25 = wp::atomic_add(var_tool, var_1, var_23);
                var_26 = wp::address(var_angular_action, var_1);
                var_27 = wp::load(var_26);
                wp::array_store(var_angular_velocity, var_1, var_27);
                var_28 = wp::address(var_angular_action, var_1);
                var_30 = wp::load(var_28);
                var_29 = wp::length(var_30);
                // if omega>1e-10:rotation[e]=wp.normalize(wp.quat_from_axis_angle(angular_action[e]/omega,omega*dt)*rotation[e])       <L 35>
                var_32 = (var_29 > var_31);
                if (var_32) {
                    var_33 = wp::address(var_angular_action, var_1);
                    var_35 = wp::load(var_33);
                    var_34 = wp::div(var_35, var_29);
                    var_36 = wp::mul(var_29, var_dt);
                    var_37 = wp::quat_from_axis_angle(var_34, var_36);
                    var_38 = wp::address(var_rotation, var_1);
                    var_40 = wp::load(var_38);
                    var_39 = wp::mul(var_37, var_40);
                    var_41 = wp::normalize(var_39);
                    wp::array_store(var_rotation, var_1, var_41);
                }
                // clock[e]+=1.                                                                   <L 36>
                var_43 = wp::atomic_add(var_clock, var_1, var_42);
            }
        }
    }
}



extern "C" __global__ void bonds_891d59ed_cuda_kernel_forward(
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
    wp::array_t<wp::vec_t<3, wp::float32>> var_angular_velocity,
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
        wp::vec_t<3, wp::float32>* var_143;
        const wp::float32 var_144 = 1.0;
        wp::float32 var_145;
        wp::vec_t<3, wp::float32>* var_146;
        wp::vec_t<3, wp::float32> var_147;
        wp::vec_t<3, wp::float32> var_148;
        wp::vec_t<3, wp::float32>* var_149;
        wp::vec_t<3, wp::float32> var_150;
        wp::vec_t<3, wp::float32> var_151;
        wp::vec_t<3, wp::float32> var_152;
        wp::vec_t<3, wp::float32>* var_153;
        wp::vec_t<3, wp::float32> var_154;
        wp::vec_t<3, wp::float32> var_155;
        wp::vec_t<3, wp::float32> var_156;
        wp::vec_t<3, wp::float32> var_157;
        wp::vec_t<3, wp::float32> var_158;
        wp::vec_t<3, wp::float32> var_159;
        wp::vec_t<3, wp::float32> var_160;
        wp::quat_t<wp::float32>* var_161;
        wp::vec_t<3, wp::float32> var_162;
        wp::quat_t<wp::float32> var_163;
        const wp::int32 var_164 = 1;
        wp::float32 var_165;
        wp::float32 var_166;
        const wp::float32 var_167 = 0.0;
        wp::float32 var_168;
        const wp::float32 var_169 = 0.25;
        const wp::int32 var_170 = 2;
        wp::float32 var_171;
        wp::float32 var_172;
        wp::float32 var_173;
        wp::float32 var_174;
        wp::float32 var_175;
        const wp::float32 var_176 = 80.0;
        wp::float32* var_177;
        wp::float32 var_178;
        wp::float32 var_179;
        wp::float32* var_180;
        wp::float32 var_181;
        wp::float32 var_182;
        const wp::float32 var_183 = 0.0;
        wp::float32 var_184;
        bool var_185;
        const wp::float32 var_186 = 0.0;
        bool var_187;
        const wp::float32 var_188 = 1e-08;
        bool var_189;
        const wp::float32 var_190 = 0.0;
        bool var_191;
        wp::float32 var_192;
        wp::float32 var_193;
        wp::float32 var_194;
        wp::float32 var_195;
        wp::float32 var_196;
        wp::float32 var_197;
        wp::vec_t<3, wp::float32> var_198;
        wp::vec_t<3, wp::float32> var_199;
        const wp::float32 var_200 = 1.0;
        wp::float32 var_201;
        wp::vec_t<3, wp::float32> var_202;
        wp::vec_t<3, wp::float32> var_203;
        wp::vec_t<3, wp::float32> var_204;
        wp::vec_t<3, wp::float32> var_205;
        wp::vec_t<3, wp::float32> var_206;
        wp::float32 var_207;
        wp::float32 var_208;
        const wp::int32 var_209 = 1;
        wp::float32 var_210;
        const wp::int32 var_211 = 2;
        wp::float32 var_212;
        wp::float32 var_213;
        wp::float32 var_214;
        wp::float32 var_215;
        wp::float32* var_216;
        const wp::float32 var_217 = 1.0;
        const wp::float32 var_218 = 1e-05;
        wp::float32 var_219;
        wp::float32 var_220;
        bool var_221;
        wp::float32 var_222;
        const wp::int32 var_223 = 0;
        const wp::int32 var_224 = 3;
        const wp::float32 var_225 = 0.5;
        wp::float32* var_226;
        wp::float32 var_227;
        wp::float32 var_228;
        wp::float32 var_229;
        wp::float32 var_230;
        wp::float32 var_231;
        //---------
        // forward
        // def bonds(x:wp.array(dtype=wp.vec3),v:wp.array(dtype=wp.vec3),force:wp.array(dtype=wp.vec3),edge:wp.array(dtype=wp.vec2i),rest:wp.array(dtype=float),stiffness:wp.array(dtype=float),mass:wp.array(dtype=float),area:wp.array(dtype=float),alive:wp.array(dtype=int),paid:wp.array(dtype=float),tool:wp.array(dtype=wp.vec3),velocity:wp.array(dtype=wp.vec3),angular_velocity:wp.array(dtype=wp.vec3),rotation:wp.array(dtype=wp.quat),reaction:wp.array(dtype=wp.vec3),load:wp.array(dtype=float),ledger:wp.array2d(dtype=float),bad:wp.array(dtype=int),h:float,dt:float,n:int,nb:int,half_length:float,cut_enabled:int):       <L 39>
        // idx=wp.tid();e=idx//nb;b=idx%nb                                                        <L 40>
        var_0 = builtin_tid1d();
        var_1 = wp::floordiv(var_0, var_nb);
        var_2 = wp::mod(var_0, var_nb);
        // if bad[e]!=0 or alive[idx]==0:return                                                   <L 41>
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
        // ends=edge[b];i=e*n+ends[0];j=e*n+ends[1];delta=x[j]-x[i];length=wp.length(delta)       <L 42>
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
        // if length<1e-8:wp.atomic_max(bad,e,2);return                                           <L 43>
        var_30 = (var_28 < var_29);
        if (var_30) {
            var_32 = wp::atomic_max(var_bad, var_1, var_31);
            continue;
        }
        // direction=delta/length;strain=length-rest[b];relative=wp.dot(v[j]-v[i],direction);reduced=mass[ends[0]]*mass[ends[1]]/(mass[ends[0]]+mass[ends[1]]);damping=2.*.02*wp.sqrt(stiffness[b]*reduced);f=(stiffness[b]*strain+damping*relative)*direction       <L 44>
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
        // wp.atomic_add(force,i,f);wp.atomic_sub(force,j,f);wp.atomic_add(ledger,e,0,damping*relative*relative*dt)       <L 45>
        var_76 = wp::atomic_add(var_force, var_18, var_75);
        var_77 = wp::atomic_sub(var_force, var_22, var_75);
        var_79 = wp::mul(var_69, var_42);
        var_80 = wp::mul(var_79, var_42);
        var_81 = wp::mul(var_80, var_dt);
        var_82 = wp::atomic_add(var_ledger, var_1, var_78, var_81);
        // if cut_enabled==0:return                                                               <L 46>
        var_84 = (var_cut_enabled == var_83);
        if (var_84) {
            continue;
        }
        // a=wp.quat_rotate_inv(rotation[e],x[i]-tool[e]);c=wp.quat_rotate_inv(rotation[e],x[j]-tool[e])       <L 47>
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
        // if a[0]*c[0]>=0.:return                                                                <L 48>
        var_102 = wp::extract(var_91, var_101);
        var_104 = wp::extract(var_99, var_103);
        var_105 = wp::mul(var_102, var_104);
        var_107 = (var_105 >= var_106);
        if (var_107) {
            continue;
        }
        // t=a[0]/(a[0]-c[0]);p=a+t*(c-a)                                                         <L 49>
        var_109 = wp::extract(var_91, var_108);
        var_111 = wp::extract(var_91, var_110);
        var_113 = wp::extract(var_99, var_112);
        var_114 = wp::sub(var_111, var_113);
        var_115 = wp::div(var_109, var_114);
        var_116 = wp::sub(var_99, var_91);
        var_117 = wp::mul(var_115, var_116);
        var_118 = wp::add(var_91, var_117);
        // if wp.abs(p[2])>half_length or p[1]<-.5*h or p[1]>.03:return                           <L 50>
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
        // midpoint_v=(1.-t)*v[i]+t*v[j];blade_velocity=velocity[e]+wp.cross(angular_velocity[e],(1.-t)*x[i]+t*x[j]-tool[e]);rel=blade_velocity-midpoint_v;local=wp.quat_rotate_inv(rotation[e],rel);advance=wp.max(-local[1],0.)+.25*wp.abs(local[2]);speed=wp.length(rel);budget=80.*area[b];remaining=wp.max(budget-paid[idx],0.)       <L 51>
        var_134 = wp::sub(var_133, var_115);
        var_135 = wp::address(var_v, var_18);
        var_137 = wp::load(var_135);
        var_136 = wp::mul(var_134, var_137);
        var_138 = wp::address(var_v, var_22);
        var_140 = wp::load(var_138);
        var_139 = wp::mul(var_115, var_140);
        var_141 = wp::add(var_136, var_139);
        var_142 = wp::address(var_velocity, var_1);
        var_143 = wp::address(var_angular_velocity, var_1);
        var_145 = wp::sub(var_144, var_115);
        var_146 = wp::address(var_x, var_18);
        var_148 = wp::load(var_146);
        var_147 = wp::mul(var_145, var_148);
        var_149 = wp::address(var_x, var_22);
        var_151 = wp::load(var_149);
        var_150 = wp::mul(var_115, var_151);
        var_152 = wp::add(var_147, var_150);
        var_153 = wp::address(var_tool, var_1);
        var_155 = wp::load(var_153);
        var_154 = wp::sub(var_152, var_155);
        var_157 = wp::load(var_143);
        var_156 = wp::cross(var_157, var_154);
        var_159 = wp::load(var_142);
        var_158 = wp::add(var_159, var_156);
        var_160 = wp::sub(var_158, var_141);
        var_161 = wp::address(var_rotation, var_1);
        var_163 = wp::load(var_161);
        var_162 = wp::quat_rotate_inv(var_163, var_160);
        var_165 = wp::extract(var_162, var_164);
        var_166 = wp::neg(var_165);
        var_168 = wp::max(var_166, var_167);
        var_171 = wp::extract(var_162, var_170);
        var_172 = wp::abs(var_171);
        var_173 = wp::mul(var_169, var_172);
        var_174 = wp::add(var_168, var_173);
        var_175 = wp::length(var_160);
        var_177 = wp::address(var_area, var_2);
        var_179 = wp::load(var_177);
        var_178 = wp::mul(var_176, var_179);
        var_180 = wp::address(var_paid, var_0);
        var_182 = wp::load(var_180);
        var_181 = wp::sub(var_178, var_182);
        var_184 = wp::max(var_181, var_183);
        // if advance<=0. or speed<=1e-8 or remaining<=0.:return                                  <L 52>
        var_187 = (var_174 <= var_186);
        var_185 = var_187;
        if (!var_185) {
            var_189 = (var_175 <= var_188);
            var_185 = var_185 || var_189;
        }
        if (!var_185) {
            var_191 = (var_184 <= var_190);
            var_185 = var_185 || var_191;
        }
        if (var_185) {
            continue;
        }
        // dwork=wp.min(remaining,budget/h*advance*dt);resistance=dwork/(speed*dt)*rel/speed       <L 55>
        var_192 = wp::div(var_178, var_h);
        var_193 = wp::mul(var_192, var_174);
        var_194 = wp::mul(var_193, var_dt);
        var_195 = wp::min(var_184, var_194);
        var_196 = wp::mul(var_175, var_dt);
        var_197 = wp::div(var_195, var_196);
        var_198 = wp::mul(var_197, var_160);
        var_199 = wp::div(var_198, var_175);
        // wp.atomic_add(force,i,(1.-t)*resistance);wp.atomic_add(force,j,t*resistance);wp.atomic_sub(reaction,e,resistance);wp.atomic_add(load,e,wp.length(resistance));wp.atomic_add(ledger,e,1,dwork);wp.atomic_add(ledger,e,2,wp.dot(resistance,blade_velocity)*dt);paid[idx]+=dwork       <L 56>
        var_201 = wp::sub(var_200, var_115);
        var_202 = wp::mul(var_201, var_199);
        var_203 = wp::atomic_add(var_force, var_18, var_202);
        var_204 = wp::mul(var_115, var_199);
        var_205 = wp::atomic_add(var_force, var_22, var_204);
        var_206 = wp::atomic_sub(var_reaction, var_1, var_199);
        var_207 = wp::length(var_199);
        var_208 = wp::atomic_add(var_load, var_1, var_207);
        var_210 = wp::atomic_add(var_ledger, var_1, var_209, var_195);
        var_212 = wp::dot(var_199, var_158);
        var_213 = wp::mul(var_212, var_dt);
        var_214 = wp::atomic_add(var_ledger, var_1, var_211, var_213);
        var_215 = wp::atomic_add(var_paid, var_0, var_195);
        // if paid[idx]>=budget*(1.-1e-5):                                                        <L 57>
        var_216 = wp::address(var_paid, var_0);
        var_219 = wp::sub(var_217, var_218);
        var_220 = wp::mul(var_178, var_219);
        var_222 = wp::load(var_216);
        var_221 = (var_222 >= var_220);
        if (var_221) {
            // alive[idx]=0;wp.atomic_add(ledger,e,3,.5*stiffness[b]*strain*strain)               <L 58>
            wp::array_store(var_alive, var_0, var_223);
            var_226 = wp::address(var_stiffness, var_2);
            var_228 = wp::load(var_226);
            var_227 = wp::mul(var_225, var_228);
            var_229 = wp::mul(var_227, var_35);
            var_230 = wp::mul(var_229, var_35);
            var_231 = wp::atomic_add(var_ledger, var_1, var_224, var_230);
        }
    }
}


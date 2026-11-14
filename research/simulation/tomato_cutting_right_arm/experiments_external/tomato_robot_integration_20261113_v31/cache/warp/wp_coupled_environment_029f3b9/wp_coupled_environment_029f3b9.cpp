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


// /home/omen/Documents/Codex/experiments/tomato_robot_integration_20261113_v31/src/instrumented_solver.py:72
static void knife_normal_0(
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


// /home/omen/Documents/Codex/experiments/tomato_robot_integration_20261113_v31/src/instrumented_solver.py:72
static void adj_knife_normal_0(
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

struct wp_args_clearance_9a3df28e {
    wp::array_t<wp::vec_t<3, wp::float32>> x;
    wp::array_t<wp::vec_t<3, wp::float32>> tool;
    wp::array_t<wp::quat_t<wp::float32>> rotation;
    wp::array_t<wp::float32> out;
    wp::float32 radius;
    wp::int32 n;
};


void clearance_9a3df28e_cpu_kernel_forward(
    wp::launch_bounds_t<1> dim,
    size_t task_index,
    wp_args_clearance_9a3df28e *_wp_args)
{
    //---------
    // argument vars
    wp::array_t<wp::vec_t<3, wp::float32>> var_x = _wp_args->x;
    wp::array_t<wp::vec_t<3, wp::float32>> var_tool = _wp_args->tool;
    wp::array_t<wp::quat_t<wp::float32>> var_rotation = _wp_args->rotation;
    wp::array_t<wp::float32> var_out = _wp_args->out;
    wp::float32 var_radius = _wp_args->radius;
    wp::int32 var_n = _wp_args->n;
    //---------
    // primal vars
    wp::int32 var_0;
    wp::int32 var_1;
    wp::quat_t<wp::float32>* var_2;
    wp::vec_t<3, wp::float32>* var_3;
    wp::vec_t<3, wp::float32>* var_4;
    wp::vec_t<3, wp::float32> var_5;
    wp::vec_t<3, wp::float32> var_6;
    wp::vec_t<3, wp::float32> var_7;
    wp::vec_t<3, wp::float32> var_8;
    wp::quat_t<wp::float32> var_9;
    const wp::float32 var_10 = 0.06;
    wp::vec_t<3, wp::float32> var_11;
    wp::float32 var_12;
    wp::float32 var_13;
    //---------
    // forward
    // def clearance(x:wp.array(dtype=wp.vec3),tool:wp.array(dtype=wp.vec3),rotation:wp.array(dtype=wp.quat),out:wp.array(dtype=float),radius:float,n:int):       <L 16>
    // i=wp.tid();e=i//n;p=wp.quat_rotate_inv(rotation[e],x[i]-tool[e]);normal,d=knife_normal(p,.06);out[i]=d-radius       <L 17>
    var_0 = builtin_tid1d();
    var_1 = wp::floordiv(var_0, var_n);
    var_2 = wp::address(var_rotation, var_1);
    var_3 = wp::address(var_x, var_0);
    var_4 = wp::address(var_tool, var_1);
    var_6 = wp::load(var_3);
    var_7 = wp::load(var_4);
    var_5 = wp::sub(var_6, var_7);
    var_9 = wp::load(var_2);
    var_8 = wp::quat_rotate_inv(var_9, var_5);
    knife_normal_0(var_8, var_10, var_11, var_12);
    var_13 = wp::sub(var_12, var_radius);
    wp::array_store(var_out, var_0, var_13);
}



extern "C" {

// Python CPU entry points
WP_API void clearance_9a3df28e_cpu_forward(
    wp::launch_bounds_t<1> *dim,
    wp_args_clearance_9a3df28e *_wp_args)
{
    wp::tile_shared_storage_t tile_mem;
#if defined(WP_ENABLE_TILES_IN_STACK_MEMORY)
    wp::shared_tile_storage = &tile_mem;
#endif

    for (size_t task_index = 0; task_index < dim->size; ++task_index)
    {
        clearance_9a3df28e_cpu_kernel_forward(*dim, task_index, _wp_args);
    }
}

} // extern C


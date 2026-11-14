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

struct wp_args_grid_motion_guard_07e5a7a1 {
    wp::array_t<wp::vec_t<3, wp::float32>> x;
    wp::array_t<wp::vec_t<3, wp::float32>> reference;
    wp::array_t<wp::int32> bad;
    wp::float32 skin;
    wp::int32 n;
};


void grid_motion_guard_07e5a7a1_cpu_kernel_forward(
    wp::launch_bounds_t<1> dim,
    size_t task_index,
    wp_args_grid_motion_guard_07e5a7a1 *_wp_args)
{
    //---------
    // argument vars
    wp::array_t<wp::vec_t<3, wp::float32>> var_x = _wp_args->x;
    wp::array_t<wp::vec_t<3, wp::float32>> var_reference = _wp_args->reference;
    wp::array_t<wp::int32> var_bad = _wp_args->bad;
    wp::float32 var_skin = _wp_args->skin;
    wp::int32 var_n = _wp_args->n;
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



extern "C" {

// Python CPU entry points
WP_API void grid_motion_guard_07e5a7a1_cpu_forward(
    wp::launch_bounds_t<1> *dim,
    wp_args_grid_motion_guard_07e5a7a1 *_wp_args)
{
    wp::tile_shared_storage_t tile_mem;
#if defined(WP_ENABLE_TILES_IN_STACK_MEMORY)
    wp::shared_tile_storage = &tile_mem;
#endif

    for (size_t task_index = 0; task_index < dim->size; ++task_index)
    {
        grid_motion_guard_07e5a7a1_cpu_kernel_forward(*dim, task_index, _wp_args);
    }
}

} // extern C

struct wp_args_clear_step_40dbecea {
    wp::array_t<wp::vec_t<3, wp::float32>> x;
    wp::array_t<wp::vec_t<3, wp::float32>> force;
    wp::array_t<wp::float32> mass;
    wp::array_t<wp::vec_t<3, wp::float32>> reaction;
    wp::array_t<wp::vec_t<3, wp::float32>> moment;
    wp::array_t<wp::float32> normal_load;
    wp::array_t<wp::vec_t<3, wp::float32>> drive;
    wp::array_t<wp::vec_t<3, wp::float32>> tool;
    wp::array_t<wp::vec_t<3, wp::float32>> action;
    wp::array_t<wp::vec_t<3, wp::float32>> angular_action;
    wp::array_t<wp::vec_t<3, wp::float32>> angular_velocity;
    wp::array_t<wp::quat_t<wp::float32>> rotation;
    wp::array_t<wp::float32> clock;
    wp::array_t<wp::int32> bad;
    wp::float32 dt;
    wp::int32 n;
};


void clear_step_40dbecea_cpu_kernel_forward(
    wp::launch_bounds_t<1> dim,
    size_t task_index,
    wp_args_clear_step_40dbecea *_wp_args)
{
    //---------
    // argument vars
    wp::array_t<wp::vec_t<3, wp::float32>> var_x = _wp_args->x;
    wp::array_t<wp::vec_t<3, wp::float32>> var_force = _wp_args->force;
    wp::array_t<wp::float32> var_mass = _wp_args->mass;
    wp::array_t<wp::vec_t<3, wp::float32>> var_reaction = _wp_args->reaction;
    wp::array_t<wp::vec_t<3, wp::float32>> var_moment = _wp_args->moment;
    wp::array_t<wp::float32> var_normal_load = _wp_args->normal_load;
    wp::array_t<wp::vec_t<3, wp::float32>> var_drive = _wp_args->drive;
    wp::array_t<wp::vec_t<3, wp::float32>> var_tool = _wp_args->tool;
    wp::array_t<wp::vec_t<3, wp::float32>> var_action = _wp_args->action;
    wp::array_t<wp::vec_t<3, wp::float32>> var_angular_action = _wp_args->angular_action;
    wp::array_t<wp::vec_t<3, wp::float32>> var_angular_velocity = _wp_args->angular_velocity;
    wp::array_t<wp::quat_t<wp::float32>> var_rotation = _wp_args->rotation;
    wp::array_t<wp::float32> var_clock = _wp_args->clock;
    wp::array_t<wp::int32> var_bad = _wp_args->bad;
    wp::float32 var_dt = _wp_args->dt;
    wp::int32 var_n = _wp_args->n;
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
    wp::vec_t<3, wp::float32> var_16;
    const wp::float32 var_17 = 0.0;
    wp::vec_t<3, wp::float32>* var_18;
    wp::vec_t<3, wp::float32> var_19;
    wp::int32* var_20;
    const wp::int32 var_21 = 0;
    bool var_22;
    wp::int32 var_23;
    wp::vec_t<3, wp::float32>* var_24;
    wp::vec_t<3, wp::float32> var_25;
    wp::vec_t<3, wp::float32> var_26;
    wp::vec_t<3, wp::float32> var_27;
    wp::vec_t<3, wp::float32>* var_28;
    wp::vec_t<3, wp::float32> var_29;
    wp::vec_t<3, wp::float32>* var_30;
    wp::float32 var_31;
    wp::vec_t<3, wp::float32> var_32;
    const wp::float32 var_33 = 1e-10;
    bool var_34;
    wp::vec_t<3, wp::float32>* var_35;
    wp::vec_t<3, wp::float32> var_36;
    wp::vec_t<3, wp::float32> var_37;
    wp::float32 var_38;
    wp::quat_t<wp::float32> var_39;
    wp::quat_t<wp::float32>* var_40;
    wp::quat_t<wp::float32> var_41;
    wp::quat_t<wp::float32> var_42;
    wp::quat_t<wp::float32> var_43;
    const wp::float32 var_44 = 20000.0;
    wp::float32 var_45;
    wp::float32 var_46;
    //---------
    // forward
    // def clear_step(x:wp.array(dtype=wp.vec3),force:wp.array(dtype=wp.vec3),mass:wp.array(dtype=float),reaction:wp.array(dtype=wp.vec3),moment:wp.array(dtype=wp.vec3),normal_load:wp.array(dtype=float),drive:wp.array(dtype=wp.vec3),tool:wp.array(dtype=wp.vec3),action:wp.array(dtype=wp.vec3),angular_action:wp.array(dtype=wp.vec3),angular_velocity:wp.array(dtype=wp.vec3),rotation:wp.array(dtype=wp.quat),clock:wp.array(dtype=float),bad:wp.array(dtype=int),dt:float,n:int):       <L 29>
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
        // reaction[e]=wp.vec3(0.);moment[e]=wp.vec3(0.);normal_load[e]=0.;drive[e]=action[e]       <L 32>
        var_14 = wp::vec_t<3, wp::float32>(var_13);
        wp::array_store(var_reaction, var_1, var_14);
        var_16 = wp::vec_t<3, wp::float32>(var_15);
        wp::array_store(var_moment, var_1, var_16);
        wp::array_store(var_normal_load, var_1, var_17);
        var_18 = wp::address(var_action, var_1);
        var_19 = wp::load(var_18);
        wp::array_store(var_drive, var_1, var_19);
        // if bad[e]==0:                                                                      <L 33>
        var_20 = wp::address(var_bad, var_1);
        var_23 = wp::load(var_20);
        var_22 = (var_23 == var_21);
        if (var_22) {
            // tool[e]+=dt*action[e];angular_velocity[e]=angular_action[e];omega=wp.length(angular_action[e])       <L 34>
            var_24 = wp::address(var_action, var_1);
            var_26 = wp::load(var_24);
            var_25 = wp::mul(var_dt, var_26);
            var_27 = wp::atomic_add(var_tool, var_1, var_25);
            var_28 = wp::address(var_angular_action, var_1);
            var_29 = wp::load(var_28);
            wp::array_store(var_angular_velocity, var_1, var_29);
            var_30 = wp::address(var_angular_action, var_1);
            var_32 = wp::load(var_30);
            var_31 = wp::length(var_32);
            // if omega>1e-10:rotation[e]=wp.normalize(wp.quat_from_axis_angle(angular_action[e]/omega,omega*dt)*rotation[e])       <L 35>
            var_34 = (var_31 > var_33);
            if (var_34) {
                var_35 = wp::address(var_angular_action, var_1);
                var_37 = wp::load(var_35);
                var_36 = wp::div(var_37, var_31);
                var_38 = wp::mul(var_31, var_dt);
                var_39 = wp::quat_from_axis_angle(var_36, var_38);
                var_40 = wp::address(var_rotation, var_1);
                var_42 = wp::load(var_40);
                var_41 = wp::mul(var_39, var_42);
                var_43 = wp::normalize(var_41);
                wp::array_store(var_rotation, var_1, var_43);
            }
            // clock[e]+=dt*20000.                                                            <L 36>
            var_45 = wp::mul(var_dt, var_44);
            var_46 = wp::atomic_add(var_clock, var_1, var_45);
        }
    }
}



extern "C" {

// Python CPU entry points
WP_API void clear_step_40dbecea_cpu_forward(
    wp::launch_bounds_t<1> *dim,
    wp_args_clear_step_40dbecea *_wp_args)
{
    wp::tile_shared_storage_t tile_mem;
#if defined(WP_ENABLE_TILES_IN_STACK_MEMORY)
    wp::shared_tile_storage = &tile_mem;
#endif

    for (size_t task_index = 0; task_index < dim->size; ++task_index)
    {
        clear_step_40dbecea_cpu_kernel_forward(*dim, task_index, _wp_args);
    }
}

} // extern C

struct wp_args_bonds_4ee2522a {
    wp::array_t<wp::vec_t<3, wp::float32>> x;
    wp::array_t<wp::vec_t<3, wp::float32>> v;
    wp::array_t<wp::vec_t<3, wp::float32>> force;
    wp::array_t<wp::vec_t<2, wp::int32>> edge;
    wp::array_t<wp::float32> rest;
    wp::array_t<wp::float32> stiffness;
    wp::array_t<wp::float32> mass;
    wp::array_t<wp::float32> area;
    wp::array_t<wp::int32> alive;
    wp::array_t<wp::float32> paid;
    wp::array_t<wp::vec_t<3, wp::float32>> tool;
    wp::array_t<wp::vec_t<3, wp::float32>> velocity;
    wp::array_t<wp::vec_t<3, wp::float32>> angular_velocity;
    wp::array_t<wp::quat_t<wp::float32>> rotation;
    wp::array_t<wp::vec_t<3, wp::float32>> reaction;
    wp::array_t<wp::vec_t<3, wp::float32>> moment;
    wp::array_t<wp::float32> load;
    wp::array_t<wp::float32> ledger;
    wp::array_t<wp::int32> bad;
    wp::float32 h;
    wp::float32 dt;
    wp::int32 n;
    wp::int32 nb;
    wp::float32 half_length;
    wp::int32 cut_enabled;
};


void bonds_4ee2522a_cpu_kernel_forward(
    wp::launch_bounds_t<1> dim,
    size_t task_index,
    wp_args_bonds_4ee2522a *_wp_args)
{
    //---------
    // argument vars
    wp::array_t<wp::vec_t<3, wp::float32>> var_x = _wp_args->x;
    wp::array_t<wp::vec_t<3, wp::float32>> var_v = _wp_args->v;
    wp::array_t<wp::vec_t<3, wp::float32>> var_force = _wp_args->force;
    wp::array_t<wp::vec_t<2, wp::int32>> var_edge = _wp_args->edge;
    wp::array_t<wp::float32> var_rest = _wp_args->rest;
    wp::array_t<wp::float32> var_stiffness = _wp_args->stiffness;
    wp::array_t<wp::float32> var_mass = _wp_args->mass;
    wp::array_t<wp::float32> var_area = _wp_args->area;
    wp::array_t<wp::int32> var_alive = _wp_args->alive;
    wp::array_t<wp::float32> var_paid = _wp_args->paid;
    wp::array_t<wp::vec_t<3, wp::float32>> var_tool = _wp_args->tool;
    wp::array_t<wp::vec_t<3, wp::float32>> var_velocity = _wp_args->velocity;
    wp::array_t<wp::vec_t<3, wp::float32>> var_angular_velocity = _wp_args->angular_velocity;
    wp::array_t<wp::quat_t<wp::float32>> var_rotation = _wp_args->rotation;
    wp::array_t<wp::vec_t<3, wp::float32>> var_reaction = _wp_args->reaction;
    wp::array_t<wp::vec_t<3, wp::float32>> var_moment = _wp_args->moment;
    wp::array_t<wp::float32> var_load = _wp_args->load;
    wp::array_t<wp::float32> var_ledger = _wp_args->ledger;
    wp::array_t<wp::int32> var_bad = _wp_args->bad;
    wp::float32 var_h = _wp_args->h;
    wp::float32 var_dt = _wp_args->dt;
    wp::int32 var_n = _wp_args->n;
    wp::int32 var_nb = _wp_args->nb;
    wp::float32 var_half_length = _wp_args->half_length;
    wp::int32 var_cut_enabled = _wp_args->cut_enabled;
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
    const wp::float32 var_207 = 1.0;
    wp::float32 var_208;
    wp::vec_t<3, wp::float32>* var_209;
    wp::vec_t<3, wp::float32> var_210;
    wp::vec_t<3, wp::float32> var_211;
    wp::vec_t<3, wp::float32>* var_212;
    wp::vec_t<3, wp::float32> var_213;
    wp::vec_t<3, wp::float32> var_214;
    wp::vec_t<3, wp::float32> var_215;
    wp::vec_t<3, wp::float32> var_216;
    wp::vec_t<3, wp::float32> var_217;
    wp::float32 var_218;
    wp::float32 var_219;
    const wp::int32 var_220 = 1;
    wp::float32 var_221;
    const wp::int32 var_222 = 2;
    wp::float32 var_223;
    wp::float32 var_224;
    wp::float32 var_225;
    wp::float32 var_226;
    wp::float32* var_227;
    const wp::float32 var_228 = 1.0;
    const wp::float32 var_229 = 1e-05;
    wp::float32 var_230;
    wp::float32 var_231;
    bool var_232;
    wp::float32 var_233;
    const wp::int32 var_234 = 0;
    const wp::int32 var_235 = 3;
    const wp::float32 var_236 = 0.5;
    wp::float32* var_237;
    wp::float32 var_238;
    wp::float32 var_239;
    wp::float32 var_240;
    wp::float32 var_241;
    wp::float32 var_242;
    //---------
    // forward
    // def bonds(x:wp.array(dtype=wp.vec3),v:wp.array(dtype=wp.vec3),force:wp.array(dtype=wp.vec3),edge:wp.array(dtype=wp.vec2i),rest:wp.array(dtype=float),stiffness:wp.array(dtype=float),mass:wp.array(dtype=float),area:wp.array(dtype=float),alive:wp.array(dtype=int),paid:wp.array(dtype=float),tool:wp.array(dtype=wp.vec3),velocity:wp.array(dtype=wp.vec3),angular_velocity:wp.array(dtype=wp.vec3),rotation:wp.array(dtype=wp.quat),reaction:wp.array(dtype=wp.vec3),moment:wp.array(dtype=wp.vec3),load:wp.array(dtype=float),ledger:wp.array2d(dtype=float),bad:wp.array(dtype=int),h:float,dt:float,n:int,nb:int,half_length:float,cut_enabled:int):       <L 39>
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
        return;
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
        return;
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
        return;
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
        return;
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
        return;
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
        return;
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
    // wp.atomic_add(force,i,(1.-t)*resistance);wp.atomic_add(force,j,t*resistance);wp.atomic_sub(reaction,e,resistance);wp.atomic_sub(moment,e,wp.cross((1.-t)*x[i]+t*x[j],resistance));wp.atomic_add(load,e,wp.length(resistance));wp.atomic_add(ledger,e,1,dwork);wp.atomic_add(ledger,e,2,wp.dot(resistance,blade_velocity)*dt);paid[idx]+=dwork       <L 56>
    var_201 = wp::sub(var_200, var_115);
    var_202 = wp::mul(var_201, var_199);
    var_203 = wp::atomic_add(var_force, var_18, var_202);
    var_204 = wp::mul(var_115, var_199);
    var_205 = wp::atomic_add(var_force, var_22, var_204);
    var_206 = wp::atomic_sub(var_reaction, var_1, var_199);
    var_208 = wp::sub(var_207, var_115);
    var_209 = wp::address(var_x, var_18);
    var_211 = wp::load(var_209);
    var_210 = wp::mul(var_208, var_211);
    var_212 = wp::address(var_x, var_22);
    var_214 = wp::load(var_212);
    var_213 = wp::mul(var_115, var_214);
    var_215 = wp::add(var_210, var_213);
    var_216 = wp::cross(var_215, var_199);
    var_217 = wp::atomic_sub(var_moment, var_1, var_216);
    var_218 = wp::length(var_199);
    var_219 = wp::atomic_add(var_load, var_1, var_218);
    var_221 = wp::atomic_add(var_ledger, var_1, var_220, var_195);
    var_223 = wp::dot(var_199, var_158);
    var_224 = wp::mul(var_223, var_dt);
    var_225 = wp::atomic_add(var_ledger, var_1, var_222, var_224);
    var_226 = wp::atomic_add(var_paid, var_0, var_195);
    // if paid[idx]>=budget*(1.-1e-5):                                                        <L 57>
    var_227 = wp::address(var_paid, var_0);
    var_230 = wp::sub(var_228, var_229);
    var_231 = wp::mul(var_178, var_230);
    var_233 = wp::load(var_227);
    var_232 = (var_233 >= var_231);
    if (var_232) {
        // alive[idx]=0;wp.atomic_add(ledger,e,3,.5*stiffness[b]*strain*strain)               <L 58>
        wp::array_store(var_alive, var_0, var_234);
        var_237 = wp::address(var_stiffness, var_2);
        var_239 = wp::load(var_237);
        var_238 = wp::mul(var_236, var_239);
        var_240 = wp::mul(var_238, var_35);
        var_241 = wp::mul(var_240, var_35);
        var_242 = wp::atomic_add(var_ledger, var_1, var_235, var_241);
    }
}



extern "C" {

// Python CPU entry points
WP_API void bonds_4ee2522a_cpu_forward(
    wp::launch_bounds_t<1> *dim,
    wp_args_bonds_4ee2522a *_wp_args)
{
    wp::tile_shared_storage_t tile_mem;
#if defined(WP_ENABLE_TILES_IN_STACK_MEMORY)
    wp::shared_tile_storage = &tile_mem;
#endif

    for (size_t task_index = 0; task_index < dim->size; ++task_index)
    {
        bonds_4ee2522a_cpu_kernel_forward(*dim, task_index, _wp_args);
    }
}

} // extern C

struct wp_args_accumulate_impulse_5b3db279 {
    wp::array_t<wp::vec_t<3, wp::float32>> reaction;
    wp::array_t<wp::vec_t<3, wp::float32>> moment;
    wp::array_t<wp::vec_t<3, wp::float32>> linear_impulse;
    wp::array_t<wp::vec_t<3, wp::float32>> angular_impulse;
    wp::float32 dt;
};


void accumulate_impulse_5b3db279_cpu_kernel_forward(
    wp::launch_bounds_t<1> dim,
    size_t task_index,
    wp_args_accumulate_impulse_5b3db279 *_wp_args)
{
    //---------
    // argument vars
    wp::array_t<wp::vec_t<3, wp::float32>> var_reaction = _wp_args->reaction;
    wp::array_t<wp::vec_t<3, wp::float32>> var_moment = _wp_args->moment;
    wp::array_t<wp::vec_t<3, wp::float32>> var_linear_impulse = _wp_args->linear_impulse;
    wp::array_t<wp::vec_t<3, wp::float32>> var_angular_impulse = _wp_args->angular_impulse;
    wp::float32 var_dt = _wp_args->dt;
    //---------
    // primal vars
    wp::int32 var_0;
    wp::vec_t<3, wp::float32>* var_1;
    wp::vec_t<3, wp::float32> var_2;
    wp::vec_t<3, wp::float32> var_3;
    wp::vec_t<3, wp::float32> var_4;
    wp::vec_t<3, wp::float32>* var_5;
    wp::vec_t<3, wp::float32> var_6;
    wp::vec_t<3, wp::float32> var_7;
    wp::vec_t<3, wp::float32> var_8;
    //---------
    // forward
    // def accumulate_impulse(reaction:wp.array(dtype=wp.vec3),moment:wp.array(dtype=wp.vec3),linear_impulse:wp.array(dtype=wp.vec3),angular_impulse:wp.array(dtype=wp.vec3),dt:float):       <L 139>
    // e=wp.tid();linear_impulse[e]+=reaction[e]*dt;angular_impulse[e]+=moment[e]*dt          <L 140>
    var_0 = builtin_tid1d();
    var_1 = wp::address(var_reaction, var_0);
    var_3 = wp::load(var_1);
    var_2 = wp::mul(var_3, var_dt);
    var_4 = wp::atomic_add(var_linear_impulse, var_0, var_2);
    var_5 = wp::address(var_moment, var_0);
    var_7 = wp::load(var_5);
    var_6 = wp::mul(var_7, var_dt);
    var_8 = wp::atomic_add(var_angular_impulse, var_0, var_6);
}



extern "C" {

// Python CPU entry points
WP_API void accumulate_impulse_5b3db279_cpu_forward(
    wp::launch_bounds_t<1> *dim,
    wp_args_accumulate_impulse_5b3db279 *_wp_args)
{
    wp::tile_shared_storage_t tile_mem;
#if defined(WP_ENABLE_TILES_IN_STACK_MEMORY)
    wp::shared_tile_storage = &tile_mem;
#endif

    for (size_t task_index = 0; task_index < dim->size; ++task_index)
    {
        accumulate_impulse_5b3db279_cpu_kernel_forward(*dim, task_index, _wp_args);
    }
}

} // extern C

struct wp_args_integrate_66f88683 {
    wp::array_t<wp::vec_t<3, wp::float32>> x;
    wp::array_t<wp::int32> fixed;
    wp::array_t<wp::vec_t<3, wp::float32>> v;
    wp::array_t<wp::vec_t<3, wp::float32>> force;
    wp::array_t<wp::float32> mass;
    wp::array_t<wp::vec_t<3, wp::float32>> tool;
    wp::array_t<wp::vec_t<3, wp::float32>> velocity;
    wp::array_t<wp::vec_t<3, wp::float32>> angular_velocity;
    wp::array_t<wp::quat_t<wp::float32>> rotation;
    wp::array_t<wp::vec_t<3, wp::float32>> reaction;
    wp::array_t<wp::vec_t<3, wp::float32>> moment;
    wp::array_t<wp::float32> load;
    wp::array_t<wp::float32> ledger;
    wp::array_t<wp::float32> penetration_peak;
    wp::array_t<wp::int32> bad;
    wp::float32 dt;
    wp::float32 radius;
    wp::int32 n;
    wp::float32 half_length;
    wp::int32 knife_enabled;
};


void integrate_66f88683_cpu_kernel_forward(
    wp::launch_bounds_t<1> dim,
    size_t task_index,
    wp_args_integrate_66f88683 *_wp_args)
{
    //---------
    // argument vars
    wp::array_t<wp::vec_t<3, wp::float32>> var_x = _wp_args->x;
    wp::array_t<wp::int32> var_fixed = _wp_args->fixed;
    wp::array_t<wp::vec_t<3, wp::float32>> var_v = _wp_args->v;
    wp::array_t<wp::vec_t<3, wp::float32>> var_force = _wp_args->force;
    wp::array_t<wp::float32> var_mass = _wp_args->mass;
    wp::array_t<wp::vec_t<3, wp::float32>> var_tool = _wp_args->tool;
    wp::array_t<wp::vec_t<3, wp::float32>> var_velocity = _wp_args->velocity;
    wp::array_t<wp::vec_t<3, wp::float32>> var_angular_velocity = _wp_args->angular_velocity;
    wp::array_t<wp::quat_t<wp::float32>> var_rotation = _wp_args->rotation;
    wp::array_t<wp::vec_t<3, wp::float32>> var_reaction = _wp_args->reaction;
    wp::array_t<wp::vec_t<3, wp::float32>> var_moment = _wp_args->moment;
    wp::array_t<wp::float32> var_load = _wp_args->load;
    wp::array_t<wp::float32> var_ledger = _wp_args->ledger;
    wp::array_t<wp::float32> var_penetration_peak = _wp_args->penetration_peak;
    wp::array_t<wp::int32> var_bad = _wp_args->bad;
    wp::float32 var_dt = _wp_args->dt;
    wp::float32 var_radius = _wp_args->radius;
    wp::int32 var_n = _wp_args->n;
    wp::float32 var_half_length = _wp_args->half_length;
    wp::int32 var_knife_enabled = _wp_args->knife_enabled;
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
    wp::vec_t<3, wp::float32> var_107;
    wp::vec_t<3, wp::float32> var_108;
    wp::vec_t<3, wp::float32> var_109;
    wp::float32 var_110;
    wp::float32 var_111;
    wp::float32 var_112;
    const wp::int32 var_113 = 2;
    wp::float32 var_114;
    wp::float32 var_115;
    const wp::int32 var_116 = 4;
    wp::float32 var_117;
    wp::float32 var_118;
    wp::float32 var_119;
    wp::vec_t<3, wp::float32> var_120;
    wp::vec_t<3, wp::float32> var_121;
    wp::vec_t<3, wp::float32> var_122;
    wp::vec_t<3, wp::float32> var_123;
    wp::vec_t<3, wp::float32> var_124;
    wp::float32 var_125;
    wp::float32 var_126;
    wp::vec_t<3, wp::float32> var_127;
    wp::vec_t<3, wp::float32> var_128;
    const wp::int32 var_129 = 1;
    wp::float32 var_130;
    bool var_131;
    const wp::float32 var_132 = 0.5;
    wp::float32 var_133;
    wp::float32 var_134;
    wp::float32 var_135;
    const wp::int32 var_136 = 1;
    const wp::int32 var_137 = 1;
    wp::float32 var_138;
    const wp::float32 var_139 = 0.0;
    bool var_140;
    const wp::int32 var_141 = 1;
    wp::float32 var_142;
    wp::float32 var_143;
    const wp::float32 var_144 = 0.0;
    const wp::int32 var_145 = 1;
    const wp::int32 var_146 = 0;
    wp::float32 var_147;
    const wp::float32 var_148 = 0.0;
    const wp::int32 var_149 = 2;
    wp::float32 var_150;
    wp::vec_t<3, wp::float32> var_151;
    wp::float32 var_152;
    const wp::float32 var_153 = 1e-12;
    bool var_154;
    const wp::float32 var_155 = 0.4;
    wp::float32 var_156;
    wp::float32 var_157;
    wp::vec_t<3, wp::float32> var_158;
    wp::vec_t<3, wp::float32> var_159;
    wp::vec_t<3, wp::float32> var_160;
    wp::vec_t<3, wp::float32> var_161;
    wp::vec_t<3, wp::float32> var_162;
    const wp::int32 var_163 = 6;
    const wp::float32 var_164 = 0.5;
    wp::float32 var_165;
    wp::float32 var_166;
    wp::float32 var_167;
    wp::float32 var_168;
    const wp::float32 var_169 = 0.0;
    wp::float32 var_170;
    wp::float32 var_171;
    wp::vec_t<3, wp::float32> var_172;
    const wp::int32 var_173 = 0;
    bool var_174;
    wp::quat_t<wp::float32>* var_175;
    wp::vec_t<3, wp::float32>* var_176;
    wp::vec_t<3, wp::float32> var_177;
    wp::vec_t<3, wp::float32> var_178;
    wp::vec_t<3, wp::float32> var_179;
    wp::quat_t<wp::float32> var_180;
    wp::vec_t<3, wp::float32> var_181;
    wp::float32 var_182;
    wp::float32 var_183;
    const wp::float32 var_184 = 0.0001;
    bool var_185;
    const wp::int32 var_186 = 4;
    wp::int32 var_187;
    wp::vec_t<3, wp::float32> var_188;
    wp::vec_t<3, wp::float32> var_189;
    wp::float32 var_190;
    bool var_191;
    const wp::int32 var_192 = 0;
    wp::float32 var_193;
    bool var_194;
    bool var_195;
    const wp::int32 var_196 = 1;
    wp::float32 var_197;
    bool var_198;
    bool var_199;
    const wp::int32 var_200 = 2;
    wp::float32 var_201;
    bool var_202;
    bool var_203;
    wp::float32 var_204;
    const wp::float32 var_205 = 10.0;
    bool var_206;
    const wp::int32 var_207 = 2;
    wp::int32 var_208;
    //---------
    // forward
    // def integrate(x:wp.array(dtype=wp.vec3),fixed:wp.array(dtype=int),v:wp.array(dtype=wp.vec3),force:wp.array(dtype=wp.vec3),mass:wp.array(dtype=float),tool:wp.array(dtype=wp.vec3),velocity:wp.array(dtype=wp.vec3),angular_velocity:wp.array(dtype=wp.vec3),rotation:wp.array(dtype=wp.quat),reaction:wp.array(dtype=wp.vec3),moment:wp.array(dtype=wp.vec3),load:wp.array(dtype=float),ledger:wp.array2d(dtype=float),penetration_peak:wp.array(dtype=float),bad:wp.array(dtype=int),dt:float,radius:float,n:int,half_length:float,knife_enabled:int):       <L 93>
    // i=wp.tid();e=i//n                                                                      <L 94>
    var_0 = builtin_tid1d();
    var_1 = wp::floordiv(var_0, var_n);
    // if bad[e]!=0:return                                                                    <L 95>
    var_2 = wp::address(var_bad, var_1);
    var_5 = wp::load(var_2);
    var_4 = (var_5 != var_3);
    if (var_4) {
        return;
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
        return;
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
            return;
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
            // total=impulse+friction;wp.atomic_sub(reaction,e,total/dt);wp.atomic_sub(moment,e,wp.cross(newx,total/dt));wp.atomic_add(load,e,wp.length(total)/dt);wp.atomic_add(ledger,e,2,wp.dot(total,blade_velocity));wp.atomic_add(ledger,e,4,-wp.dot(friction,rel))       <L 111>
            var_104 = wp::add(var_70, var_103);
            var_105 = wp::div(var_104, var_dt);
            var_106 = wp::atomic_sub(var_reaction, var_1, var_105);
            var_107 = wp::div(var_104, var_dt);
            var_108 = wp::cross(var_71, var_107);
            var_109 = wp::atomic_sub(var_moment, var_1, var_108);
            var_110 = wp::length(var_104);
            var_111 = wp::div(var_110, var_dt);
            var_112 = wp::atomic_add(var_load, var_1, var_111);
            var_114 = wp::dot(var_104, var_81);
            var_115 = wp::atomic_add(var_ledger, var_1, var_113, var_114);
            var_117 = wp::dot(var_103, var_83);
            var_118 = wp::neg(var_117);
            var_119 = wp::atomic_add(var_ledger, var_1, var_116, var_118);
        }
        var_120 = wp::where(var_64, var_66, var_53);
        var_121 = wp::where(var_64, var_102, var_39);
        var_122 = wp::where(var_64, var_71, var_43);
    }
    var_123 = wp::where(var_46, var_51, var_18);
    var_124 = wp::where(var_46, var_120, var_20);
    var_125 = wp::where(var_46, var_54, var_21);
    var_126 = wp::where(var_46, var_55, var_22);
    var_127 = wp::where(var_46, var_121, var_39);
    var_128 = wp::where(var_46, var_122, var_43);
    // if newx[1]<radius:                                                                     <L 112>
    var_130 = wp::extract(var_128, var_129);
    var_131 = (var_130 < var_radius);
    if (var_131) {
        // old_ke=.5*m*wp.dot(newv,newv)                                                      <L 113>
        var_133 = wp::mul(var_132, var_32);
        var_134 = wp::dot(var_127, var_127);
        var_135 = wp::mul(var_133, var_134);
        // newx[1]=radius                                                                     <L 114>
        wp::assign_inplace(var_128, var_136, var_radius);
        // if newv[1]<0.:                                                                     <L 115>
        var_138 = wp::extract(var_127, var_137);
        var_140 = (var_138 < var_139);
        if (var_140) {
            // normal_speed=-newv[1];newv[1]=0.;horizontal=wp.vec3(newv[0],0.,newv[2]);speed=wp.length(horizontal)       <L 116>
            var_142 = wp::extract(var_127, var_141);
            var_143 = wp::neg(var_142);
            wp::assign_inplace(var_127, var_145, var_144);
            var_147 = wp::extract(var_127, var_146);
            var_150 = wp::extract(var_127, var_149);
            var_151 = wp::vec_t<3, wp::float32>(var_147, var_148, var_150);
            var_152 = wp::length(var_151);
            // if speed>1e-12:newv-=wp.min(.4*normal_speed,speed)*horizontal/speed            <L 117>
            var_154 = (var_152 > var_153);
            if (var_154) {
                var_156 = wp::mul(var_155, var_143);
                var_157 = wp::min(var_156, var_152);
                var_158 = wp::mul(var_157, var_151);
                var_159 = wp::div(var_158, var_152);
                var_160 = wp::sub(var_127, var_159);
            }
            var_161 = wp::where(var_154, var_160, var_127);
        }
        var_162 = wp::where(var_140, var_161, var_127);
        // wp.atomic_add(ledger,e,6,wp.max(old_ke-.5*m*wp.dot(newv,newv),0.))                 <L 118>
        var_165 = wp::mul(var_164, var_32);
        var_166 = wp::dot(var_162, var_162);
        var_167 = wp::mul(var_165, var_166);
        var_168 = wp::sub(var_135, var_167);
        var_170 = wp::max(var_168, var_169);
        var_171 = wp::atomic_add(var_ledger, var_1, var_163, var_170);
    }
    var_172 = wp::where(var_131, var_162, var_127);
    // if knife_enabled!=0:                                                                   <L 119>
    var_174 = (var_knife_enabled != var_173);
    if (var_174) {
        // p=wp.quat_rotate_inv(rotation[e],newx-tool[e]);normal,distance=knife_normal(p,half_length)       <L 120>
        var_175 = wp::address(var_rotation, var_1);
        var_176 = wp::address(var_tool, var_1);
        var_178 = wp::load(var_176);
        var_177 = wp::sub(var_128, var_178);
        var_180 = wp::load(var_175);
        var_179 = wp::quat_rotate_inv(var_180, var_177);
        knife_normal_0(var_179, var_half_length, var_181, var_182);
        // if radius-distance>.0001:wp.atomic_max(bad,e,4)                                    <L 121>
        var_183 = wp::sub(var_radius, var_182);
        var_185 = (var_183 > var_184);
        if (var_185) {
            var_187 = wp::atomic_max(var_bad, var_1, var_186);
        }
    }
    var_188 = wp::where(var_174, var_179, var_123);
    var_189 = wp::where(var_174, var_181, var_124);
    var_190 = wp::where(var_174, var_182, var_125);
    // if not wp.isfinite(newx[0]) or not wp.isfinite(newx[1]) or not wp.isfinite(newx[2]) or wp.length(newv)>10.:wp.atomic_max(bad,e,2)       <L 122>
    var_193 = wp::extract(var_128, var_192);
    var_194 = wp::isfinite(var_193);
    var_195 = wp::unot(var_194);
    var_191 = var_195;
    if (!var_191) {
        var_197 = wp::extract(var_128, var_196);
        var_198 = wp::isfinite(var_197);
        var_199 = wp::unot(var_198);
        var_191 = var_191 || var_199;
    }
    if (!var_191) {
        var_201 = wp::extract(var_128, var_200);
        var_202 = wp::isfinite(var_201);
        var_203 = wp::unot(var_202);
        var_191 = var_191 || var_203;
    }
    if (!var_191) {
        var_204 = wp::length(var_172);
        var_206 = (var_204 > var_205);
        var_191 = var_191 || var_206;
    }
    if (var_191) {
        var_208 = wp::atomic_max(var_bad, var_1, var_207);
    }
    // x[i]=newx;v[i]=newv                                                                    <L 123>
    wp::array_store(var_x, var_0, var_128);
    wp::array_store(var_v, var_0, var_172);
}



extern "C" {

// Python CPU entry points
WP_API void integrate_66f88683_cpu_forward(
    wp::launch_bounds_t<1> *dim,
    wp_args_integrate_66f88683 *_wp_args)
{
    wp::tile_shared_storage_t tile_mem;
#if defined(WP_ENABLE_TILES_IN_STACK_MEMORY)
    wp::shared_tile_storage = &tile_mem;
#endif

    for (size_t task_index = 0; task_index < dim->size; ++task_index)
    {
        integrate_66f88683_cpu_kernel_forward(*dim, task_index, _wp_args);
    }
}

} // extern C

struct wp_args_finish_step_6749bff9 {
    wp::array_t<wp::vec_t<3, wp::float32>> reaction;
    wp::array_t<wp::vec_t<3, wp::float32>> moment;
    wp::array_t<wp::float32> load;
    wp::array_t<wp::float32> peak;
    wp::array_t<wp::int32> bad;
    wp::array_t<wp::vec_t<3, wp::float32>> tool;
    wp::array_t<wp::quat_t<wp::float32>> rotation;
    wp::int32 knife_enabled;
    wp::float32 stop_force;
};


void finish_step_6749bff9_cpu_kernel_forward(
    wp::launch_bounds_t<1> dim,
    size_t task_index,
    wp_args_finish_step_6749bff9 *_wp_args)
{
    //---------
    // argument vars
    wp::array_t<wp::vec_t<3, wp::float32>> var_reaction = _wp_args->reaction;
    wp::array_t<wp::vec_t<3, wp::float32>> var_moment = _wp_args->moment;
    wp::array_t<wp::float32> var_load = _wp_args->load;
    wp::array_t<wp::float32> var_peak = _wp_args->peak;
    wp::array_t<wp::int32> var_bad = _wp_args->bad;
    wp::array_t<wp::vec_t<3, wp::float32>> var_tool = _wp_args->tool;
    wp::array_t<wp::quat_t<wp::float32>> var_rotation = _wp_args->rotation;
    wp::int32 var_knife_enabled = _wp_args->knife_enabled;
    wp::float32 var_stop_force = _wp_args->stop_force;
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
    const wp::int32 var_16 = 0;
    bool var_17;
    const wp::float32 var_18 = 1000000000.0;
    wp::float32 var_19;
    const wp::int32 var_20 = 0;
    const wp::float32 var_21 = 0.0;
    const wp::float32 var_22 = 0.0;
    const wp::int32 var_23 = 3;
    bool var_24;
    const wp::float32 var_25 = -0.06;
    const wp::float32 var_26 = 0.06;
    wp::float32 var_27;
    wp::vec_t<3, wp::float32> var_28;
    const wp::int32 var_29 = 3;
    wp::int32 var_30;
    const wp::int32 var_31 = 1;
    bool var_32;
    const wp::float32 var_33 = 0.0005;
    const wp::int32 var_34 = 0;
    const wp::float32 var_35 = 0.03;
    const wp::int32 var_36 = 1;
    const wp::int32 var_37 = 3;
    wp::int32 var_38;
    const wp::int32 var_39 = 2;
    bool var_40;
    const wp::float32 var_41 = -0.0005;
    const wp::int32 var_42 = 0;
    const wp::float32 var_43 = 0.03;
    const wp::int32 var_44 = 1;
    wp::vec_t<3, wp::float32>* var_45;
    wp::quat_t<wp::float32>* var_46;
    wp::vec_t<3, wp::float32> var_47;
    wp::quat_t<wp::float32> var_48;
    wp::vec_t<3, wp::float32> var_49;
    wp::vec_t<3, wp::float32> var_50;
    const wp::int32 var_51 = 1;
    wp::float32 var_52;
    wp::float32 var_53;
    const wp::int32 var_54 = 1;
    const wp::float32 var_55 = 0.0;
    const wp::float32 var_56 = 0.0;
    const wp::int32 var_57 = 3;
    bool var_58;
    const wp::float32 var_59 = -0.06;
    const wp::float32 var_60 = 0.06;
    wp::float32 var_61;
    wp::vec_t<3, wp::float32> var_62;
    const wp::int32 var_63 = 3;
    wp::int32 var_64;
    const wp::int32 var_65 = 1;
    bool var_66;
    const wp::float32 var_67 = 0.0005;
    const wp::int32 var_68 = 0;
    const wp::float32 var_69 = 0.03;
    const wp::int32 var_70 = 1;
    const wp::int32 var_71 = 3;
    wp::int32 var_72;
    const wp::int32 var_73 = 2;
    bool var_74;
    const wp::float32 var_75 = -0.0005;
    const wp::int32 var_76 = 0;
    const wp::float32 var_77 = 0.03;
    const wp::int32 var_78 = 1;
    wp::vec_t<3, wp::float32>* var_79;
    wp::quat_t<wp::float32>* var_80;
    wp::vec_t<3, wp::float32> var_81;
    wp::quat_t<wp::float32> var_82;
    wp::vec_t<3, wp::float32> var_83;
    wp::vec_t<3, wp::float32> var_84;
    const wp::int32 var_85 = 1;
    wp::float32 var_86;
    wp::float32 var_87;
    const wp::int32 var_88 = 2;
    const wp::float32 var_89 = 0.0;
    const wp::float32 var_90 = 0.0;
    const wp::int32 var_91 = 3;
    bool var_92;
    const wp::float32 var_93 = -0.06;
    const wp::float32 var_94 = 0.06;
    wp::float32 var_95;
    wp::vec_t<3, wp::float32> var_96;
    const wp::int32 var_97 = 3;
    wp::int32 var_98;
    const wp::int32 var_99 = 1;
    bool var_100;
    const wp::float32 var_101 = 0.0005;
    const wp::int32 var_102 = 0;
    const wp::float32 var_103 = 0.03;
    const wp::int32 var_104 = 1;
    const wp::int32 var_105 = 3;
    wp::int32 var_106;
    const wp::int32 var_107 = 2;
    bool var_108;
    const wp::float32 var_109 = -0.0005;
    const wp::int32 var_110 = 0;
    const wp::float32 var_111 = 0.03;
    const wp::int32 var_112 = 1;
    wp::vec_t<3, wp::float32>* var_113;
    wp::quat_t<wp::float32>* var_114;
    wp::vec_t<3, wp::float32> var_115;
    wp::quat_t<wp::float32> var_116;
    wp::vec_t<3, wp::float32> var_117;
    wp::vec_t<3, wp::float32> var_118;
    const wp::int32 var_119 = 1;
    wp::float32 var_120;
    wp::float32 var_121;
    const wp::int32 var_122 = 3;
    const wp::float32 var_123 = 0.0;
    const wp::float32 var_124 = 0.0;
    const wp::int32 var_125 = 3;
    bool var_126;
    const wp::float32 var_127 = -0.06;
    const wp::float32 var_128 = 0.06;
    wp::float32 var_129;
    wp::vec_t<3, wp::float32> var_130;
    const wp::int32 var_131 = 3;
    wp::int32 var_132;
    const wp::int32 var_133 = 1;
    bool var_134;
    const wp::float32 var_135 = 0.0005;
    const wp::int32 var_136 = 0;
    const wp::float32 var_137 = 0.03;
    const wp::int32 var_138 = 1;
    const wp::int32 var_139 = 3;
    wp::int32 var_140;
    const wp::int32 var_141 = 2;
    bool var_142;
    const wp::float32 var_143 = -0.0005;
    const wp::int32 var_144 = 0;
    const wp::float32 var_145 = 0.03;
    const wp::int32 var_146 = 1;
    wp::vec_t<3, wp::float32>* var_147;
    wp::quat_t<wp::float32>* var_148;
    wp::vec_t<3, wp::float32> var_149;
    wp::quat_t<wp::float32> var_150;
    wp::vec_t<3, wp::float32> var_151;
    wp::vec_t<3, wp::float32> var_152;
    const wp::int32 var_153 = 1;
    wp::float32 var_154;
    wp::float32 var_155;
    const wp::int32 var_156 = 4;
    const wp::float32 var_157 = 0.0;
    const wp::float32 var_158 = 0.0;
    const wp::int32 var_159 = 3;
    bool var_160;
    const wp::float32 var_161 = -0.06;
    const wp::float32 var_162 = 0.06;
    wp::float32 var_163;
    wp::vec_t<3, wp::float32> var_164;
    const wp::int32 var_165 = 3;
    wp::int32 var_166;
    const wp::int32 var_167 = 1;
    bool var_168;
    const wp::float32 var_169 = 0.0005;
    const wp::int32 var_170 = 0;
    const wp::float32 var_171 = 0.03;
    const wp::int32 var_172 = 1;
    const wp::int32 var_173 = 3;
    wp::int32 var_174;
    const wp::int32 var_175 = 2;
    bool var_176;
    const wp::float32 var_177 = -0.0005;
    const wp::int32 var_178 = 0;
    const wp::float32 var_179 = 0.03;
    const wp::int32 var_180 = 1;
    wp::vec_t<3, wp::float32>* var_181;
    wp::quat_t<wp::float32>* var_182;
    wp::vec_t<3, wp::float32> var_183;
    wp::quat_t<wp::float32> var_184;
    wp::vec_t<3, wp::float32> var_185;
    wp::vec_t<3, wp::float32> var_186;
    const wp::int32 var_187 = 1;
    wp::float32 var_188;
    wp::float32 var_189;
    const wp::int32 var_190 = 5;
    const wp::float32 var_191 = 0.0;
    const wp::float32 var_192 = 0.0;
    const wp::int32 var_193 = 3;
    bool var_194;
    const wp::float32 var_195 = -0.06;
    const wp::float32 var_196 = 0.06;
    wp::float32 var_197;
    wp::vec_t<3, wp::float32> var_198;
    const wp::int32 var_199 = 3;
    wp::int32 var_200;
    const wp::int32 var_201 = 1;
    bool var_202;
    const wp::float32 var_203 = 0.0005;
    const wp::int32 var_204 = 0;
    const wp::float32 var_205 = 0.03;
    const wp::int32 var_206 = 1;
    const wp::int32 var_207 = 3;
    wp::int32 var_208;
    const wp::int32 var_209 = 2;
    bool var_210;
    const wp::float32 var_211 = -0.0005;
    const wp::int32 var_212 = 0;
    const wp::float32 var_213 = 0.03;
    const wp::int32 var_214 = 1;
    wp::vec_t<3, wp::float32>* var_215;
    wp::quat_t<wp::float32>* var_216;
    wp::vec_t<3, wp::float32> var_217;
    wp::quat_t<wp::float32> var_218;
    wp::vec_t<3, wp::float32> var_219;
    wp::vec_t<3, wp::float32> var_220;
    const wp::int32 var_221 = 1;
    wp::float32 var_222;
    wp::float32 var_223;
    const wp::float32 var_224 = 0.0;
    bool var_225;
    const wp::int32 var_226 = 6;
    wp::int32 var_227;
    //---------
    // forward
    // def finish_step(reaction:wp.array(dtype=wp.vec3),moment:wp.array(dtype=wp.vec3),load:wp.array(dtype=float),peak:wp.array(dtype=float),bad:wp.array(dtype=int),tool:wp.array(dtype=wp.vec3),rotation:wp.array(dtype=wp.quat),knife_enabled:int,stop_force:float):       <L 126>
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
    // if knife_enabled!=0:                                                                   <L 129>
    var_17 = (var_knife_enabled != var_16);
    if (var_17) {
        // minimum=float(1e9)                                                                 <L 130>
        var_19 = wp::float(var_18);
        // for k in range(6):                                                                 <L 131>
        // p=wp.vec3(0.,0.,-.06 if k<3 else .06)                                              <L 132>
        var_24 = (var_20 < var_23);
        if (var_24) {
        }
        if (!var_24) {
        }
        var_27 = wp::where(var_24, var_25, var_26);
        var_28 = wp::vec_t<3, wp::float32>(var_21, var_22, var_27);
        // if k%3==1:p[0]=.0005;p[1]=.03                                                      <L 133>
        var_30 = wp::mod(var_20, var_29);
        var_32 = (var_30 == var_31);
        if (var_32) {
            wp::assign_inplace(var_28, var_34, var_33);
            wp::assign_inplace(var_28, var_36, var_35);
        }
        // if k%3==2:p[0]=-.0005;p[1]=.03                                                     <L 134>
        var_38 = wp::mod(var_20, var_37);
        var_40 = (var_38 == var_39);
        if (var_40) {
            wp::assign_inplace(var_28, var_42, var_41);
            wp::assign_inplace(var_28, var_44, var_43);
        }
        // world=tool[e]+wp.quat_rotate(rotation[e],p);minimum=wp.min(minimum,world[1])       <L 135>
        var_45 = wp::address(var_tool, var_0);
        var_46 = wp::address(var_rotation, var_0);
        var_48 = wp::load(var_46);
        var_47 = wp::quat_rotate(var_48, var_28);
        var_50 = wp::load(var_45);
        var_49 = wp::add(var_50, var_47);
        var_52 = wp::extract(var_49, var_51);
        var_53 = wp::min(var_19, var_52);
        // p=wp.vec3(0.,0.,-.06 if k<3 else .06)                                              <L 132>
        var_58 = (var_54 < var_57);
        if (var_58) {
        }
        if (!var_58) {
        }
        var_61 = wp::where(var_58, var_59, var_60);
        var_62 = wp::vec_t<3, wp::float32>(var_55, var_56, var_61);
        // if k%3==1:p[0]=.0005;p[1]=.03                                                      <L 133>
        var_64 = wp::mod(var_54, var_63);
        var_66 = (var_64 == var_65);
        if (var_66) {
            wp::assign_inplace(var_62, var_68, var_67);
            wp::assign_inplace(var_62, var_70, var_69);
        }
        // if k%3==2:p[0]=-.0005;p[1]=.03                                                     <L 134>
        var_72 = wp::mod(var_54, var_71);
        var_74 = (var_72 == var_73);
        if (var_74) {
            wp::assign_inplace(var_62, var_76, var_75);
            wp::assign_inplace(var_62, var_78, var_77);
        }
        // world=tool[e]+wp.quat_rotate(rotation[e],p);minimum=wp.min(minimum,world[1])       <L 135>
        var_79 = wp::address(var_tool, var_0);
        var_80 = wp::address(var_rotation, var_0);
        var_82 = wp::load(var_80);
        var_81 = wp::quat_rotate(var_82, var_62);
        var_84 = wp::load(var_79);
        var_83 = wp::add(var_84, var_81);
        var_86 = wp::extract(var_83, var_85);
        var_87 = wp::min(var_53, var_86);
        // p=wp.vec3(0.,0.,-.06 if k<3 else .06)                                              <L 132>
        var_92 = (var_88 < var_91);
        if (var_92) {
        }
        if (!var_92) {
        }
        var_95 = wp::where(var_92, var_93, var_94);
        var_96 = wp::vec_t<3, wp::float32>(var_89, var_90, var_95);
        // if k%3==1:p[0]=.0005;p[1]=.03                                                      <L 133>
        var_98 = wp::mod(var_88, var_97);
        var_100 = (var_98 == var_99);
        if (var_100) {
            wp::assign_inplace(var_96, var_102, var_101);
            wp::assign_inplace(var_96, var_104, var_103);
        }
        // if k%3==2:p[0]=-.0005;p[1]=.03                                                     <L 134>
        var_106 = wp::mod(var_88, var_105);
        var_108 = (var_106 == var_107);
        if (var_108) {
            wp::assign_inplace(var_96, var_110, var_109);
            wp::assign_inplace(var_96, var_112, var_111);
        }
        // world=tool[e]+wp.quat_rotate(rotation[e],p);minimum=wp.min(minimum,world[1])       <L 135>
        var_113 = wp::address(var_tool, var_0);
        var_114 = wp::address(var_rotation, var_0);
        var_116 = wp::load(var_114);
        var_115 = wp::quat_rotate(var_116, var_96);
        var_118 = wp::load(var_113);
        var_117 = wp::add(var_118, var_115);
        var_120 = wp::extract(var_117, var_119);
        var_121 = wp::min(var_87, var_120);
        // p=wp.vec3(0.,0.,-.06 if k<3 else .06)                                              <L 132>
        var_126 = (var_122 < var_125);
        if (var_126) {
        }
        if (!var_126) {
        }
        var_129 = wp::where(var_126, var_127, var_128);
        var_130 = wp::vec_t<3, wp::float32>(var_123, var_124, var_129);
        // if k%3==1:p[0]=.0005;p[1]=.03                                                      <L 133>
        var_132 = wp::mod(var_122, var_131);
        var_134 = (var_132 == var_133);
        if (var_134) {
            wp::assign_inplace(var_130, var_136, var_135);
            wp::assign_inplace(var_130, var_138, var_137);
        }
        // if k%3==2:p[0]=-.0005;p[1]=.03                                                     <L 134>
        var_140 = wp::mod(var_122, var_139);
        var_142 = (var_140 == var_141);
        if (var_142) {
            wp::assign_inplace(var_130, var_144, var_143);
            wp::assign_inplace(var_130, var_146, var_145);
        }
        // world=tool[e]+wp.quat_rotate(rotation[e],p);minimum=wp.min(minimum,world[1])       <L 135>
        var_147 = wp::address(var_tool, var_0);
        var_148 = wp::address(var_rotation, var_0);
        var_150 = wp::load(var_148);
        var_149 = wp::quat_rotate(var_150, var_130);
        var_152 = wp::load(var_147);
        var_151 = wp::add(var_152, var_149);
        var_154 = wp::extract(var_151, var_153);
        var_155 = wp::min(var_121, var_154);
        // p=wp.vec3(0.,0.,-.06 if k<3 else .06)                                              <L 132>
        var_160 = (var_156 < var_159);
        if (var_160) {
        }
        if (!var_160) {
        }
        var_163 = wp::where(var_160, var_161, var_162);
        var_164 = wp::vec_t<3, wp::float32>(var_157, var_158, var_163);
        // if k%3==1:p[0]=.0005;p[1]=.03                                                      <L 133>
        var_166 = wp::mod(var_156, var_165);
        var_168 = (var_166 == var_167);
        if (var_168) {
            wp::assign_inplace(var_164, var_170, var_169);
            wp::assign_inplace(var_164, var_172, var_171);
        }
        // if k%3==2:p[0]=-.0005;p[1]=.03                                                     <L 134>
        var_174 = wp::mod(var_156, var_173);
        var_176 = (var_174 == var_175);
        if (var_176) {
            wp::assign_inplace(var_164, var_178, var_177);
            wp::assign_inplace(var_164, var_180, var_179);
        }
        // world=tool[e]+wp.quat_rotate(rotation[e],p);minimum=wp.min(minimum,world[1])       <L 135>
        var_181 = wp::address(var_tool, var_0);
        var_182 = wp::address(var_rotation, var_0);
        var_184 = wp::load(var_182);
        var_183 = wp::quat_rotate(var_184, var_164);
        var_186 = wp::load(var_181);
        var_185 = wp::add(var_186, var_183);
        var_188 = wp::extract(var_185, var_187);
        var_189 = wp::min(var_155, var_188);
        // p=wp.vec3(0.,0.,-.06 if k<3 else .06)                                              <L 132>
        var_194 = (var_190 < var_193);
        if (var_194) {
        }
        if (!var_194) {
        }
        var_197 = wp::where(var_194, var_195, var_196);
        var_198 = wp::vec_t<3, wp::float32>(var_191, var_192, var_197);
        // if k%3==1:p[0]=.0005;p[1]=.03                                                      <L 133>
        var_200 = wp::mod(var_190, var_199);
        var_202 = (var_200 == var_201);
        if (var_202) {
            wp::assign_inplace(var_198, var_204, var_203);
            wp::assign_inplace(var_198, var_206, var_205);
        }
        // if k%3==2:p[0]=-.0005;p[1]=.03                                                     <L 134>
        var_208 = wp::mod(var_190, var_207);
        var_210 = (var_208 == var_209);
        if (var_210) {
            wp::assign_inplace(var_198, var_212, var_211);
            wp::assign_inplace(var_198, var_214, var_213);
        }
        // world=tool[e]+wp.quat_rotate(rotation[e],p);minimum=wp.min(minimum,world[1])       <L 135>
        var_215 = wp::address(var_tool, var_0);
        var_216 = wp::address(var_rotation, var_0);
        var_218 = wp::load(var_216);
        var_217 = wp::quat_rotate(var_218, var_198);
        var_220 = wp::load(var_215);
        var_219 = wp::add(var_220, var_217);
        var_222 = wp::extract(var_219, var_221);
        var_223 = wp::min(var_189, var_222);
        // if minimum<0.:wp.atomic_max(bad,e,6)                                               <L 136>
        var_225 = (var_223 < var_224);
        if (var_225) {
            var_227 = wp::atomic_max(var_bad, var_0, var_226);
        }
    }
}



extern "C" {

// Python CPU entry points
WP_API void finish_step_6749bff9_cpu_forward(
    wp::launch_bounds_t<1> *dim,
    wp_args_finish_step_6749bff9 *_wp_args)
{
    wp::tile_shared_storage_t tile_mem;
#if defined(WP_ENABLE_TILES_IN_STACK_MEMORY)
    wp::shared_tile_storage = &tile_mem;
#endif

    for (size_t task_index = 0; task_index < dim->size; ++task_index)
    {
        finish_step_6749bff9_cpu_kernel_forward(*dim, task_index, _wp_args);
    }
}

} // extern C

struct wp_args_particle_contacts_751ffca2 {
    wp::uint64 grid;
    wp::array_t<wp::vec_t<3, wp::float32>> x;
    wp::array_t<wp::vec_t<3, wp::float32>> v;
    wp::array_t<wp::vec_t<3, wp::float32>> force;
    wp::array_t<wp::float32> mass;
    wp::array_t<wp::float32> ledger;
    wp::array_t<wp::int32> bad;
    wp::float32 radius;
    wp::float32 skin;
    wp::float32 dt;
    wp::int32 n;
};


void particle_contacts_751ffca2_cpu_kernel_forward(
    wp::launch_bounds_t<1> dim,
    size_t task_index,
    wp_args_particle_contacts_751ffca2 *_wp_args)
{
    //---------
    // argument vars
    wp::uint64 var_grid = _wp_args->grid;
    wp::array_t<wp::vec_t<3, wp::float32>> var_x = _wp_args->x;
    wp::array_t<wp::vec_t<3, wp::float32>> var_v = _wp_args->v;
    wp::array_t<wp::vec_t<3, wp::float32>> var_force = _wp_args->force;
    wp::array_t<wp::float32> var_mass = _wp_args->mass;
    wp::array_t<wp::float32> var_ledger = _wp_args->ledger;
    wp::array_t<wp::int32> var_bad = _wp_args->bad;
    wp::float32 var_radius = _wp_args->radius;
    wp::float32 var_skin = _wp_args->skin;
    wp::float32 var_dt = _wp_args->dt;
    wp::int32 var_n = _wp_args->n;
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
        return;
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



extern "C" {

// Python CPU entry points
WP_API void particle_contacts_751ffca2_cpu_forward(
    wp::launch_bounds_t<1> *dim,
    wp_args_particle_contacts_751ffca2 *_wp_args)
{
    wp::tile_shared_storage_t tile_mem;
#if defined(WP_ENABLE_TILES_IN_STACK_MEMORY)
    wp::shared_tile_storage = &tile_mem;
#endif

    for (size_t task_index = 0; task_index < dim->size; ++task_index)
    {
        particle_contacts_751ffca2_cpu_kernel_forward(*dim, task_index, _wp_args);
    }
}

} // extern C


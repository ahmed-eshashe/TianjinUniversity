from pathlib import Path
W=Path(__file__).resolve().parent;E=W.parent/'cressim_20261110'
s=(E/'feasibility.cpp').read_text()
s=s.replace('bool stock=mode=="stock"','double angle=(argc>6?std::stod(argv[6]):0)*3.141592653589793/180; double ca=std::cos(angle),sa=std::sin(angle);bool stock=mode=="stock"')
s=s.replace('std::vector<int> labels;', '''if(!stock&&!cuts){auto&p=s->getParticleData();for(unsigned i=0;i<s->getNumAllocatedParticles();++i){auto a=p.positionMass[i];p.positionMass[i]=make_float4(ca*a.x-sa*a.y,sa*a.x+ca*a.y,a.z,a.w);}s->markDirty(SceneDataDirtyFlags::eParticlePositionMass);}
 std::vector<int> labels;''')
s=s.replace('(p.x>=0));','(i>=4000));')
s=s.replace('sd.transform=pose;', 'if(!stock&&!cuts){auto a=pose.position;pose.position=Vec3f(ca*a.x()-sa*a.y(),sa*a.x()+ca*a.y(),a.z());pose.rotation=Quat(0,0,std::sin((angle+1.5707963267948966)/2),std::cos((angle+1.5707963267948966)/2));}sd.transform=pose;')
(W/'src/cressim_control.cpp').write_text(s)

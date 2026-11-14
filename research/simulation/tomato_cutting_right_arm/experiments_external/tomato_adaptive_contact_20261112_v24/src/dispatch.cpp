#include <cuda.h>
#include <vector>
#include <string>
#include <stdexcept>
static thread_local std::string error;
static void check(CUresult r){if(r!=CUDA_SUCCESS){const char* s=nullptr;cuGetErrorString(r,&s);throw std::runtime_error(s?s:"CUDA graph error");}}
struct Node { CUgraphNode handle; CUDA_KERNEL_NODE_PARAMS params; int kind; };
struct Dispatch { CUgraphExec executable; std::vector<Node> nodes; };
extern "C" {
const char* dispatch_error(){return error.c_str();}
void* dispatch_prepare(void* graph,void* executable){
 auto d=new Dispatch;d->executable=(CUgraphExec)executable;
 try{
  if(!d->executable)check(cuGraphInstantiateWithFlags(&d->executable,(CUgraph)graph,0));
  size_t n=0;check(cuGraphGetNodes((CUgraph)graph,nullptr,&n));std::vector<CUgraphNode> nodes(n);check(cuGraphGetNodes((CUgraph)graph,nodes.data(),&n));
  for(auto h:nodes){CUgraphNodeType type;check(cuGraphNodeGetType(h,&type));if(type!=CU_GRAPH_NODE_TYPE_KERNEL)throw std::runtime_error("unexpected non-kernel graph node");
   Node row;row.handle=h;check(cuGraphKernelNodeGetParams(h,&row.params));const char* text;check(cuFuncGetName(&text,row.params.func));std::string name(text);
   if(name.find("stress")!=std::string::npos)row.kind=0;else if(name.find("gather")!=std::string::npos)row.kind=1;else if(name.find("advance")!=std::string::npos)row.kind=2;else throw std::runtime_error("unrecognized kernel "+name);
   if(row.params.gridDimY!=1||row.params.gridDimZ!=1)throw std::runtime_error("unexpected multidimensional launch");d->nodes.push_back(row);
  }return d;
 }catch(const std::exception& e){error=e.what();delete d;return nullptr;}
}
int dispatch_update(void* handle,int nodes,int regions){
 auto d=(Dispatch*)handle;try{
  if(nodes<=0||regions<=0)throw std::runtime_error("empty active geometry");
  for(auto& row:d->nodes){auto p=row.params;size_t threads=row.kind==0?regions:(row.kind==1?((nodes+3)/4)*128:nodes);p.gridDimX=(threads+p.blockDimX-1)/p.blockDimX;check(cuGraphExecKernelNodeSetParams(d->executable,row.handle,&p));}return 0;
 }catch(const std::exception& e){error=e.what();return 1;}
}
void dispatch_free(void* h){delete (Dispatch*)h;}
void* dispatch_executable(void* h){return ((Dispatch*)h)->executable;}
void* dispatch_stream_create(){CUstream s;try{check(cuStreamCreate(&s,CU_STREAM_NON_BLOCKING));return s;}catch(const std::exception& e){error=e.what();return nullptr;}}
void dispatch_stream_free(void* s){cuStreamSynchronize((CUstream)s);cuStreamDestroy((CUstream)s);}
}

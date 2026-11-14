#include <torch/extension.h>
using torch::Tensor;
void geom(Tensor,Tensor,Tensor,Tensor,Tensor,Tensor,Tensor,Tensor,Tensor,Tensor,Tensor);
void damp(Tensor,Tensor,Tensor,Tensor,Tensor,Tensor);
void ground(Tensor,Tensor,Tensor,Tensor);
void step(Tensor,Tensor,Tensor,Tensor,Tensor,double);
void gathered_damp(Tensor,Tensor,Tensor,Tensor,Tensor,Tensor,Tensor,Tensor,Tensor,Tensor,Tensor);
void pcg_op(Tensor,Tensor,Tensor,Tensor,Tensor,Tensor,Tensor,Tensor,Tensor,Tensor,Tensor,Tensor,double);
void pcg_iteration(Tensor,Tensor,Tensor,Tensor,Tensor,Tensor,Tensor);
PYBIND11_MODULE(TORCH_EXTENSION_NAME,m){m.def("geom",&geom);m.def("damp",&damp);m.def("ground",&ground);m.def("step",&step);m.def("gathered_damp",&gathered_damp);m.def("pcg_op",&pcg_op);m.def("pcg_iteration",&pcg_iteration);}

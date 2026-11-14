# Install script for directory: /home/omen/teamwork_projects/tomato_cutting_right_arm/work/native_instrumentation_20261102/PhysX/physx/source/compiler/cmakegpu

# Set the install prefix
if(NOT DEFINED CMAKE_INSTALL_PREFIX)
  set(CMAKE_INSTALL_PREFIX "/home/omen/teamwork_projects/tomato_cutting_right_arm/work/native_instrumentation_20261102/PhysX/omni/ovexts/_install")
endif()
string(REGEX REPLACE "/$" "" CMAKE_INSTALL_PREFIX "${CMAKE_INSTALL_PREFIX}")

# Set the install configuration name.
if(NOT DEFINED CMAKE_INSTALL_CONFIG_NAME)
  if(BUILD_TYPE)
    string(REGEX REPLACE "^[^A-Za-z0-9_]+" ""
           CMAKE_INSTALL_CONFIG_NAME "${BUILD_TYPE}")
  else()
    set(CMAKE_INSTALL_CONFIG_NAME "Release")
  endif()
  message(STATUS "Install configuration: \"${CMAKE_INSTALL_CONFIG_NAME}\"")
endif()

# Set the component getting installed.
if(NOT CMAKE_INSTALL_COMPONENT)
  if(COMPONENT)
    message(STATUS "Install component: \"${COMPONENT}\"")
    set(CMAKE_INSTALL_COMPONENT "${COMPONENT}")
  else()
    set(CMAKE_INSTALL_COMPONENT)
  endif()
endif()

# Install shared libraries without execute permission?
if(NOT DEFINED CMAKE_INSTALL_SO_NO_EXE)
  set(CMAKE_INSTALL_SO_NO_EXE "1")
endif()

# Is this installation the result of a crosscompile?
if(NOT DEFINED CMAKE_CROSSCOMPILING)
  set(CMAKE_CROSSCOMPILING "FALSE")
endif()

# Set default install directory permissions.
if(NOT DEFINED CMAKE_OBJDUMP)
  set(CMAKE_OBJDUMP "/usr/bin/objdump")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/cudamanager" TYPE FILE FILES
    "/home/omen/teamwork_projects/tomato_cutting_right_arm/work/native_instrumentation_20261102/PhysX/physx/include/cudamanager/PxCudaContextManager.h"
    "/home/omen/teamwork_projects/tomato_cutting_right_arm/work/native_instrumentation_20261102/PhysX/physx/include/cudamanager/PxCudaContext.h"
    "/home/omen/teamwork_projects/tomato_cutting_right_arm/work/native_instrumentation_20261102/PhysX/physx/include/cudamanager/PxCudaTypes.h"
    )
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  if(EXISTS "$ENV{DESTDIR}/release/libPhysXGpu_64.so" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}/release/libPhysXGpu_64.so")
    file(RPATH_CHECK
         FILE "$ENV{DESTDIR}/release/libPhysXGpu_64.so"
         RPATH "")
  endif()
  list(APPEND CMAKE_ABSOLUTE_DESTINATION_FILES
   "/release/libPhysXGpu_64.so")
  if(CMAKE_WARN_ON_ABSOLUTE_INSTALL_DESTINATION)
    message(WARNING "ABSOLUTE path INSTALL DESTINATION : ${CMAKE_ABSOLUTE_DESTINATION_FILES}")
  endif()
  if(CMAKE_ERROR_ON_ABSOLUTE_INSTALL_DESTINATION)
    message(FATAL_ERROR "ABSOLUTE path INSTALL DESTINATION forbidden (by caller): ${CMAKE_ABSOLUTE_DESTINATION_FILES}")
  endif()
  file(INSTALL DESTINATION "/release" TYPE SHARED_LIBRARY FILES "/home/omen/teamwork_projects/tomato_cutting_right_arm/work/native_instrumentation_20261102/PhysX/omni/ovexts/_compiler/gcc-linux-x86_64/build-release/physx_sdk/sdk_gpu_source_bin/libPhysXGpu_64.so")
  if(EXISTS "$ENV{DESTDIR}/release/libPhysXGpu_64.so" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}/release/libPhysXGpu_64.so")
    if(CMAKE_INSTALL_DO_STRIP)
      execute_process(COMMAND "/usr/bin/strip" "$ENV{DESTDIR}/release/libPhysXGpu_64.so")
    endif()
  endif()
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  include("/home/omen/teamwork_projects/tomato_cutting_right_arm/work/native_instrumentation_20261102/PhysX/omni/ovexts/_compiler/gcc-linux-x86_64/build-release/physx_sdk/sdk_gpu_source_bin/CMakeFiles/PhysXGpu.dir/install-cxx-module-bmi-Release.cmake" OPTIONAL)
endif()


# Install script for directory: /home/omen/teamwork_projects/tomato_cutting_right_arm/work/native_instrumentation_20261102/PhysX/omni/ovruntime/source/omni.physx.gpu

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
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/bin" TYPE FILE RENAME "libPhysXGpu_64.so" FILES "/home/omen/teamwork_projects/tomato_cutting_right_arm/work/native_instrumentation_20261102/PhysX/omni/ovexts/_compiler/gcc-linux-x86_64/build-release/physx_sdk/sdk_gpu_source_bin/libPhysXGpu_64.so")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/bin" TYPE FILE RENAME "libPhysXGpu_64.so" FILES "/home/omen/teamwork_projects/tomato_cutting_right_arm/work/native_instrumentation_20261102/PhysX/omni/ovexts/_compiler/gcc-linux-x86_64/build-release/physx_sdk/sdk_gpu_source_bin/libPhysXGpu_64.so")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/bin" TYPE FILE RENAME "libPVDRuntime_64.so" FILES "/home/omen/teamwork_projects/tomato_cutting_right_arm/work/native_instrumentation_20261102/PhysX/omni/ovexts/_compiler/gcc-linux-x86_64/build-release/physx_sdk/pvdruntime_bin/libPVDRuntime_64.so")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  if(EXISTS "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/bin/libomni.physx.gpu.plugin.so" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/bin/libomni.physx.gpu.plugin.so")
    file(RPATH_CHECK
         FILE "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/bin/libomni.physx.gpu.plugin.so"
         RPATH "\$ORIGIN")
  endif()
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/bin" TYPE SHARED_LIBRARY FILES "/home/omen/teamwork_projects/tomato_cutting_right_arm/work/native_instrumentation_20261102/PhysX/omni/ovexts/_build/linux-x86_64/release/extsPhysics/omni.physx.gpu/bin/libomni.physx.gpu.plugin.so")
  if(EXISTS "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/bin/libomni.physx.gpu.plugin.so" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/bin/libomni.physx.gpu.plugin.so")
    file(RPATH_CHANGE
         FILE "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/bin/libomni.physx.gpu.plugin.so"
         OLD_RPATH "\$ORIGIN:/home/omen/teamwork_projects/tomato_cutting_right_arm/work/native_instrumentation_20261102/PhysX/omni/ovexts/_build/target-deps/python/lib:/home/omen/teamwork_projects/tomato_cutting_right_arm/work/native_instrumentation_20261102/PhysX/omni/ovexts/_build/target-deps/carb_sdk_plugins/_build/linux-x86_64/release:"
         NEW_RPATH "\$ORIGIN")
    if(CMAKE_INSTALL_DO_STRIP)
      execute_process(COMMAND "/usr/bin/strip" "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/bin/libomni.physx.gpu.plugin.so")
    endif()
  endif()
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
endif()


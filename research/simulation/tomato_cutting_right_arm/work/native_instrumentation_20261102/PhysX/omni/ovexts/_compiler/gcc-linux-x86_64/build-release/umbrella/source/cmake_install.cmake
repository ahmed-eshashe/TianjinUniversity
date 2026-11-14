# Install script for directory: /home/omen/teamwork_projects/tomato_cutting_right_arm/work/native_instrumentation_20261102/PhysX/omni/umbrella/source

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
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/omni/physics/simulation" TYPE FILE FILES
    "/home/omen/teamwork_projects/tomato_cutting_right_arm/work/native_instrumentation_20261102/PhysX/omni/umbrella/include/omni/physics/simulation/IPhysics.h"
    "/home/omen/teamwork_projects/tomato_cutting_right_arm/work/native_instrumentation_20261102/PhysX/omni/umbrella/include/omni/physics/simulation/IPhysicsBenchmark.h"
    "/home/omen/teamwork_projects/tomato_cutting_right_arm/work/native_instrumentation_20261102/PhysX/omni/umbrella/include/omni/physics/simulation/IPhysicsInteraction.h"
    "/home/omen/teamwork_projects/tomato_cutting_right_arm/work/native_instrumentation_20261102/PhysX/omni/umbrella/include/omni/physics/simulation/IPhysicsSceneQuery.h"
    "/home/omen/teamwork_projects/tomato_cutting_right_arm/work/native_instrumentation_20261102/PhysX/omni/umbrella/include/omni/physics/simulation/IPhysicsSimulation.h"
    "/home/omen/teamwork_projects/tomato_cutting_right_arm/work/native_instrumentation_20261102/PhysX/omni/umbrella/include/omni/physics/simulation/IPhysicsStageUpdate.h"
    )
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/omni/physics/simulation/simulator" TYPE FILE FILES
    "/home/omen/teamwork_projects/tomato_cutting_right_arm/work/native_instrumentation_20261102/PhysX/omni/umbrella/include/omni/physics/simulation/simulator/Simulator.h"
    "/home/omen/teamwork_projects/tomato_cutting_right_arm/work/native_instrumentation_20261102/PhysX/omni/umbrella/include/omni/physics/simulation/simulator/Simulation.h"
    "/home/omen/teamwork_projects/tomato_cutting_right_arm/work/native_instrumentation_20261102/PhysX/omni/umbrella/include/omni/physics/simulation/simulator/Benchmark.h"
    "/home/omen/teamwork_projects/tomato_cutting_right_arm/work/native_instrumentation_20261102/PhysX/omni/umbrella/include/omni/physics/simulation/simulator/Interaction.h"
    "/home/omen/teamwork_projects/tomato_cutting_right_arm/work/native_instrumentation_20261102/PhysX/omni/umbrella/include/omni/physics/simulation/simulator/InteractionTools.h"
    "/home/omen/teamwork_projects/tomato_cutting_right_arm/work/native_instrumentation_20261102/PhysX/omni/umbrella/include/omni/physics/simulation/simulator/SceneQuery.h"
    "/home/omen/teamwork_projects/tomato_cutting_right_arm/work/native_instrumentation_20261102/PhysX/omni/umbrella/include/omni/physics/simulation/simulator/StageUpdate.h"
    "/home/omen/teamwork_projects/tomato_cutting_right_arm/work/native_instrumentation_20261102/PhysX/omni/umbrella/include/omni/physics/simulation/simulator/ContactEvent.h"
    )
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  if(EXISTS "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/bin/libPhysicsUmbrella.so" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/bin/libPhysicsUmbrella.so")
    file(RPATH_CHECK
         FILE "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/bin/libPhysicsUmbrella.so"
         RPATH "\$ORIGIN")
  endif()
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/bin" TYPE SHARED_LIBRARY FILES "/home/omen/teamwork_projects/tomato_cutting_right_arm/work/native_instrumentation_20261102/PhysX/omni/ovexts/_build/linux-x86_64/release/libPhysicsUmbrella.so")
  if(EXISTS "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/bin/libPhysicsUmbrella.so" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/bin/libPhysicsUmbrella.so")
    file(RPATH_CHANGE
         FILE "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/bin/libPhysicsUmbrella.so"
         OLD_RPATH "/home/omen/teamwork_projects/tomato_cutting_right_arm/work/native_instrumentation_20261102/PhysX/omni/ovexts/_build/target-deps/carb_sdk_plugins/_build/linux-x86_64/release:"
         NEW_RPATH "\$ORIGIN")
    if(CMAKE_INSTALL_DO_STRIP)
      execute_process(COMMAND "/usr/bin/strip" "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/bin/libPhysicsUmbrella.so")
    endif()
  endif()
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
endif()


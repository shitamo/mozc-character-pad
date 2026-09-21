cmake_minimum_required(VERSION 3.16)
project(mozc_standalone_character_pad CXX)

# Qt6 requires C++17.
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_AUTOMOC OFF)
set(CMAKE_AUTOUIC OFF)
set(CMAKE_AUTORCC OFF)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE Release)
endif()

# ---------------------------------------------------------------------------
# Platform macro required by mozc's base/port.h.
# ---------------------------------------------------------------------------
if(UNIX AND NOT APPLE)
  add_compile_definitions(OS_LINUX)
elseif(APPLE)
  add_compile_definitions(OS_MACOSX)
elseif(WIN32)
  add_compile_definitions(OS_WIN)
endif()

# ---------------------------------------------------------------------------
# Dependencies: Qt6 and zinnia.
# ---------------------------------------------------------------------------
find_package(Qt6 REQUIRED COMPONENTS Widgets Gui Core)

find_package(PkgConfig QUIET)
if(PKG_CONFIG_FOUND)
  pkg_check_modules(ZINNIA QUIET zinnia)
endif()

if(NOT ZINNIA_FOUND)
  find_path(ZINNIA_INCLUDE_DIR NAMES zinnia.h)
  find_library(ZINNIA_LIBRARY NAMES zinnia)
  if(ZINNIA_INCLUDE_DIR AND ZINNIA_LIBRARY)
    set(ZINNIA_INCLUDE_DIRS ${ZINNIA_INCLUDE_DIR})
    set(ZINNIA_LIBRARIES ${ZINNIA_LIBRARY})
  else()
    message(FATAL_ERROR
      "zinnia (libzinnia-dev) not found. Install it, e.g. "
      "'apt-get install libzinnia-dev', or point ZINNIA_INCLUDE_DIR / "
      "ZINNIA_LIBRARY at your zinnia installation.")
  endif()
endif()

find_package(Python3 COMPONENTS Interpreter REQUIRED)

set(SRC_ROOT ${CMAKE_CURRENT_SOURCE_DIR}/src)
set(GEN_DIR ${CMAKE_CURRENT_BINARY_DIR}/gen)

# ---------------------------------------------------------------------------
# base/ library: mozc's platform-independent utility layer.
# ---------------------------------------------------------------------------
file(GLOB BASE_SOURCES ${SRC_ROOT}/base/*.cc)

add_library(mozc_base STATIC ${BASE_SOURCES})
target_include_directories(mozc_base PUBLIC ${SRC_ROOT})
target_link_libraries(mozc_base PUBLIC pthread)

# ---------------------------------------------------------------------------
# handwriting/ library: HandwritingManager + Zinnia-backed recognizer.
# Cloud handwriting recognition (handwriting/cloud_handwriting.*) is
# intentionally NOT built: this standalone tool only performs local
# recognition via zinnia (see README.md).
# ---------------------------------------------------------------------------
add_library(mozc_handwriting STATIC
  ${SRC_ROOT}/handwriting/handwriting_manager.cc
  ${SRC_ROOT}/handwriting/zinnia_handwriting.cc
)
target_include_directories(mozc_handwriting PUBLIC ${SRC_ROOT} ${ZINNIA_INCLUDE_DIRS})
target_link_libraries(mozc_handwriting PUBLIC mozc_base ${ZINNIA_LIBRARIES})

# ---------------------------------------------------------------------------
# Generated Unicode/JIS/CP932/Unihan data headers.
# These headers are produced from the raw Unicode Consortium / JIS mapping
# data under src/data/unicode by the (Python 3-ported) generator scripts
# under src/gui/character_pad/data, exactly as the original gyp targets
# 'gen_character_pad_cp932_data' and 'gen_character_pad_data' did.
# ---------------------------------------------------------------------------
set(CP_DATA_DIR ${SRC_ROOT}/gui/character_pad/data)
set(UNICODE_DATA_DIR ${SRC_ROOT}/data/unicode)
set(GEN_CP_DATA_DIR ${GEN_DIR}/gui/character_pad/data)
file(MAKE_DIRECTORY ${GEN_CP_DATA_DIR})

add_custom_command(
  OUTPUT ${GEN_CP_DATA_DIR}/cp932_map.h
  COMMAND ${Python3_EXECUTABLE} ${CP_DATA_DIR}/gen_cp932_map.py
          ${UNICODE_DATA_DIR}/CP932.TXT > ${GEN_CP_DATA_DIR}/cp932_map.h
  DEPENDS ${CP_DATA_DIR}/gen_cp932_map.py ${UNICODE_DATA_DIR}/CP932.TXT
  VERBATIM
)

add_custom_command(
  OUTPUT ${GEN_CP_DATA_DIR}/unihan_data.h
  COMMAND ${Python3_EXECUTABLE} ${CP_DATA_DIR}/gen_unihan_data.py
          ${UNICODE_DATA_DIR}/RadicalIndex.txt ${UNICODE_DATA_DIR}/Unihan.txt
          > ${GEN_CP_DATA_DIR}/unihan_data.h
  DEPENDS ${CP_DATA_DIR}/gen_unihan_data.py
          ${UNICODE_DATA_DIR}/RadicalIndex.txt ${UNICODE_DATA_DIR}/Unihan.txt
  VERBATIM
)

add_custom_command(
  OUTPUT ${GEN_CP_DATA_DIR}/unicode_blocks.h
  COMMAND ${Python3_EXECUTABLE} ${CP_DATA_DIR}/gen_unicode_blocks.py
          ${UNICODE_DATA_DIR}/Blocks.txt > ${GEN_CP_DATA_DIR}/unicode_blocks.h
  DEPENDS ${CP_DATA_DIR}/gen_unicode_blocks.py ${UNICODE_DATA_DIR}/Blocks.txt
  VERBATIM
)

add_custom_command(
  OUTPUT ${GEN_CP_DATA_DIR}/unicode_data.h
  COMMAND ${Python3_EXECUTABLE} ${CP_DATA_DIR}/gen_unicode_data.py
          ${UNICODE_DATA_DIR}/UnicodeData.txt > ${GEN_CP_DATA_DIR}/unicode_data.h
  DEPENDS ${CP_DATA_DIR}/gen_unicode_data.py ${UNICODE_DATA_DIR}/UnicodeData.txt
  VERBATIM
)

add_custom_command(
  OUTPUT ${GEN_CP_DATA_DIR}/local_character_map.h
  COMMAND ${Python3_EXECUTABLE} ${CP_DATA_DIR}/gen_local_character_map.py
          ${UNICODE_DATA_DIR}/JIS0201.TXT ${UNICODE_DATA_DIR}/JIS0208.TXT
          ${UNICODE_DATA_DIR}/JIS0212.TXT ${UNICODE_DATA_DIR}/CP932.TXT
          > ${GEN_CP_DATA_DIR}/local_character_map.h
  DEPENDS ${CP_DATA_DIR}/gen_local_character_map.py
          ${UNICODE_DATA_DIR}/JIS0201.TXT ${UNICODE_DATA_DIR}/JIS0208.TXT
          ${UNICODE_DATA_DIR}/JIS0212.TXT ${UNICODE_DATA_DIR}/CP932.TXT
  VERBATIM
)

add_custom_target(gen_character_pad_data DEPENDS
  ${GEN_CP_DATA_DIR}/cp932_map.h
  ${GEN_CP_DATA_DIR}/unihan_data.h
  ${GEN_CP_DATA_DIR}/unicode_blocks.h
  ${GEN_CP_DATA_DIR}/unicode_data.h
  ${GEN_CP_DATA_DIR}/local_character_map.h
)

# ---------------------------------------------------------------------------
# Qt UI / MOC / resource generation.
# ---------------------------------------------------------------------------
set(CP_DIR ${SRC_ROOT}/gui/character_pad)
set(DICT_DIR ${SRC_ROOT}/gui/dictionary_tool)
set(GEN_CP_DIR ${GEN_DIR}/gui/character_pad)
file(MAKE_DIRECTORY ${GEN_CP_DIR})

# character_palette.h / hand_writing.h include their generated UI headers as
# "gui/character_pad/ui_<name>.h" (matching the source tree layout), so the
# .ui files are compiled with Qt6::uic directly into that path rather than
# via qt6_wrap_ui(), which always flattens output into the current binary
# directory.
set(UI_HEADERS
  ${GEN_CP_DIR}/ui_character_palette.h
  ${GEN_CP_DIR}/ui_hand_writing.h
)
add_custom_command(
  OUTPUT ${GEN_CP_DIR}/ui_character_palette.h
  COMMAND Qt6::uic ${CP_DIR}/character_palette.ui -o ${GEN_CP_DIR}/ui_character_palette.h
  DEPENDS ${CP_DIR}/character_palette.ui
  VERBATIM
)
add_custom_command(
  OUTPUT ${GEN_CP_DIR}/ui_hand_writing.h
  COMMAND Qt6::uic ${CP_DIR}/hand_writing.ui -o ${GEN_CP_DIR}/ui_hand_writing.h
  DEPENDS ${CP_DIR}/hand_writing.ui
  VERBATIM
)

qt6_wrap_cpp(MOC_SOURCES
  ${CP_DIR}/character_palette.h
  ${CP_DIR}/character_palette_table_widget.h
  ${CP_DIR}/hand_writing.h
  ${CP_DIR}/hand_writing_canvas.h
  ${CP_DIR}/hand_writing_thread.h
  ${CP_DIR}/result_list.h
  ${DICT_DIR}/zero_width_splitter.h
)

# The source calls Q_INIT_RESOURCE(qrc_character_pad), which expects the
# generated resource-init function to be named qInitResources_qrc_character_pad.
# Qt's rcc derives that name from its "-name" argument, and the original gyp
# build (gui/qt_rcc.gypi) explicitly passed "-name qrc_<qrc_base_name>", not
# the bare qrc file's basename.
#
# qt6_add_resources()'s CMake macro always appends its own "-name
# <qrc-basename>" *after* whatever is passed via OPTIONS, so passing --name
# there does not actually override the generated symbol name (rcc keeps the
# later, macro-appended one). So, exactly like the .ui handling above, invoke
# Qt6::rcc directly instead of going through qt6_add_resources().
set(QRC_SOURCES ${GEN_CP_DIR}/qrc_character_pad.cc)
add_custom_command(
  OUTPUT ${QRC_SOURCES}
  COMMAND Qt6::rcc -name qrc_character_pad
          -o ${QRC_SOURCES} ${CP_DIR}/character_pad.qrc
  DEPENDS ${CP_DIR}/character_pad.qrc
          ${CP_DIR}/character_pad_en.qm ${CP_DIR}/character_pad_ja.qm
  VERBATIM
)

# ---------------------------------------------------------------------------
# character_pad_lib: shared code between the two GUI executables.
# This mirrors gui/gui.gyp's 'character_pad_lib' target, minus the
# mozc_server IPC client, config/protocol proto dependencies, cloud
# handwriting, and the Windows-only selection handler (see README.md for the
# behavioral differences from upstream mozc).
# ---------------------------------------------------------------------------
add_library(character_pad_lib STATIC
  ${CP_DIR}/character_pad_libmain.cc
  ${CP_DIR}/character_palette_table_widget.cc
  ${CP_DIR}/character_palette.cc
  ${CP_DIR}/hand_writing_canvas.cc
  ${CP_DIR}/hand_writing_thread.cc
  ${CP_DIR}/hand_writing.cc
  ${CP_DIR}/result_list.cc
  ${CP_DIR}/selection_handler.cc
  ${CP_DIR}/unicode_util.cc
  ${DICT_DIR}/zero_width_splitter.cc
  ${SRC_ROOT}/gui/base/locale_util.cc
  ${UI_HEADERS}
  ${MOC_SOURCES}
  ${QRC_SOURCES}
)
add_dependencies(character_pad_lib gen_character_pad_data)

target_include_directories(character_pad_lib PUBLIC
  ${SRC_ROOT}
  ${GEN_DIR}
  ${CMAKE_CURRENT_BINARY_DIR}
)
target_link_libraries(character_pad_lib PUBLIC
  mozc_base
  mozc_handwriting
  Qt6::Widgets
  Qt6::Gui
  Qt6::Core
)

# ---------------------------------------------------------------------------
# Executables.
# ---------------------------------------------------------------------------
add_executable(character_palette ${CP_DIR}/character_palette_main.cc)
target_link_libraries(character_palette PRIVATE character_pad_lib)

add_executable(hand_writing ${CP_DIR}/hand_writing_main.cc)
target_link_libraries(hand_writing PRIVATE character_pad_lib)

install(TARGETS character_palette hand_writing RUNTIME DESTINATION bin)

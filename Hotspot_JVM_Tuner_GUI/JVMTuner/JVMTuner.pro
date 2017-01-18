#-------------------------------------------------
#
# Project created by QtCreator 2015-01-02T10:42:42
#
#-------------------------------------------------
#INCLUDEPATH += /usr/local/qwt-6.1.2/include
#LIBS += /usr/local/qwt-6.1.2/lib/libqwt.so.6.1.2
QT       += core gui
QT += printsupport
greaterThan(QT_MAJOR_VERSION, 4): QT += widgets

TARGET = JVMTuner
TEMPLATE = app

QMAKE_CXXFLAGS += -std=c++0x -pthread
LIBS += -pthread
SOURCES += main.cpp\
        mainwindow.cpp \
    results.cpp \
    appthread.cpp \
    qcustomplot.cpp \
    jstat_profiler_data_visualizer.cpp \
    scrollbar.cpp

HEADERS  += mainwindow.h \
    results.h \
    appthread.h \
    qcustomplot.h \
    jstat_profiler_data_visualizer.h \
    scrollbar.h

FORMS    += mainwindow.ui \
    results.ui \
    jstat_profiler_data_visualizer.ui \
    scrollbar.ui

#include "mainwindow.h"
#include "jstat_profiler_data_visualizer.h"
#include <QApplication>
//#include <qwt.h>
//#include <qwt_plot.h>
//#include <qwt_plot_curve.h>
//#include <qwt_text.h>
int main(int argc, char *argv[])
{

    QApplication a(argc, argv);
    a.setStyleSheet("QGroupBox {  border: 0px solid gray;}");
    MainWindow w;
    w.showMaximized();
    return a.exec();

}

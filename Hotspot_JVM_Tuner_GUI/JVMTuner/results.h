#ifndef RESULTS_H
#define RESULTS_H

#include "appthread.h"
#include <QDialog>
#include "timeperformanceplot.h"
#include "jstat_profiler_data_visualizer.h"
#include <limits.h>
#include <fstream>
#include <sstream>
#include <algorithm>
#include <iterator>
#include <boost/algorithm/string/split.hpp>
#include <boost/algorithm/string/classification.hpp>
#include <iostream>
#include <vector>
#include "appthread.h"
#include <qdatetime.h>
#include <QDateTime>
namespace Ui {
class Results;
}

class Results : public QDialog
{
    Q_OBJECT

    void setup();


public:
     const QString DEFAULT_CONFIG_TAG = "Default Configuration Metric :";
     const QString IMPROVEMENT_TAG = "Improvement:";
     const double INFINITY_DEF = std::numeric_limits<double>::max();
     AppThread *appthread;
     jstat_profiler_data_visualizer *profiler;
     bool first;
     bool is_default_read_from_file;
     double bestPerformance;
     double defaultRuntime;
     QString command;
     QString class_folder_path;
     QString program_name;
     QString config_file_name;
     QTimer* timer;
     QDateTime tunerStartedDateTime;
     //QTime tunerStartedTime;

     explicit Results(QWidget *parent = 0);
     ~Results();
     void drawGraph(double,double);
     void startprocess(QString command);
     void stopProcess();
     QString GenerateExecutionCode(QString run_command,QString program_name,QString run_type);
     QString GetBestFlagConfiguration();

private:
    Ui::Results *ui;




public slots:
    void onTextChanged(QString);
    void showTime();

private slots:
    void on_cmd_jstat_clicked();
    void on_cmd_stopTuner_clicked();
    void on_cmd_showConfigFile_clicked();
};

#endif // RESULTS_H

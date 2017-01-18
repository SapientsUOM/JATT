#ifndef JSTAT_PROFILER_DATA_VISUALIZER_H
#define JSTAT_PROFILER_DATA_VISUALIZER_H

#include <QDialog>

#include <fstream>
#include <sstream>
#include <algorithm>
#include <iterator>
#include <boost/algorithm/string/split.hpp>
#include <boost/algorithm/string/classification.hpp>
#include <iostream>
#include <vector>
#include "appthread.h"
#include "scrollbar.h"
using namespace std;
namespace Ui {
class jstat_profiler_data_visualizer;
}

class jstat_profiler_data_visualizer : public QDialog
{
    Q_OBJECT

public:
    explicit jstat_profiler_data_visualizer(QWidget *parent = 0,string default_command="",string tuned_command="",string program_name="");
    ~jstat_profiler_data_visualizer();
    void GenerateJstatGraphs();
    string GenerateJstatFileName(string benchmark,string option,string run_type);
    void ProfileProgram();
    void GenerateJstatData(vector< vector<float> >& data, string &type);
    void DrawGCGraph(vector<float> gc_default_list,vector<float> gc_tuned_list);
    void DrawCompilerGraph(vector<float> compiler_default_list,vector<float> compiler_tuned_list);
    void DrawClassGraph(vector<float> class_default_list, vector<float> class_tuned_list);
private:
    Ui::jstat_profiler_data_visualizer *ui;
    string jstat_data_folder;
    string default_setting_command;
    string tuned_setting_command;
    bool default_config_graph;
    bool tuned_config_graph;
    vector<string> option_list;
    string benchmark_name;
    AppThread *appthread;
    scrollbar* progress_bar;




};

#endif // JSTAT_PROFILER_DATA_VISUALIZER_H

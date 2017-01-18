#include "jstat_profiler_data_visualizer.h"
#include "ui_jstat_profiler_data_visualizer.h"
#include <fstream>
#include <sstream>
#include <algorithm>
#include <iterator>
#include <boost/algorithm/string/split.hpp>
#include <boost/algorithm/string/classification.hpp>
#include <jstat_profiler_data_visualizer.h>
#include <vector>
using namespace std;
using namespace boost::algorithm;

jstat_profiler_data_visualizer::jstat_profiler_data_visualizer(QWidget *parent,string default_command,string tuned_command,string program_name) :
    QDialog(parent),
    ui(new Ui::jstat_profiler_data_visualizer)
{
    ui->setupUi(this);

    this->progress_bar=new scrollbar(this);
    this->progress_bar->show();
    this->progress_bar->UpdateProgressBar(10);

    this->default_setting_command = default_command;
    this->tuned_setting_command = tuned_command;
    default_config_graph=false;
    tuned_config_graph=true;
    jstat_data_folder="jstat_temp_files/";
    option_list.push_back("gc");
    option_list.push_back("compiler");
    option_list.push_back("class");

    this->benchmark_name=program_name;
    this->appthread = new AppThread(this);

    ProfileProgram();
    GenerateJstatGraphs();
    this->progress_bar->hide();
}

jstat_profiler_data_visualizer::~jstat_profiler_data_visualizer()
{
    delete ui;
}


string jstat_profiler_data_visualizer::GenerateJstatFileName(string benchmark,string option,string run_type)
{
    string temp="jstat_"+benchmark+"_"+option+""+run_type+".csv";
    return temp;
}

void jstat_profiler_data_visualizer::ProfileProgram(){
    this->progress_bar->UpdateProgressBar(20);
    this->appthread->command= QString::fromStdString(this->default_setting_command);
    this->appthread->start();
    while(!(this->appthread->isAppThreadStopped)){};
    this->progress_bar->UpdateProgressBar(40);
    this->appthread->isAppThreadStopped = false;
    this->appthread->command = QString::fromStdString(this->tuned_setting_command);
    this->appthread->start();
    while(!(this->appthread->isAppThreadStopped)){};
    this->progress_bar->UpdateProgressBar(60);
}

void jstat_profiler_data_visualizer::GenerateJstatData(vector< vector<float> >& data,string& type){


    string temp;
    ifstream jstat_file;
    string line="";

    vector<string> tokens;
    for(int i=0;i<option_list.size();i++)
    {
        temp=GenerateJstatFileName(this->benchmark_name,option_list[i],type);
        temp=jstat_data_folder+temp;
        jstat_file.open(temp,ios::out);
        if(jstat_file.is_open()){
            getline(jstat_file,line);
            while ( getline (jstat_file,line) )
            {
                split(tokens, line, is_any_of(","));
                data[i].push_back(stof(tokens[tokens.size()-1]));
                tokens.clear();

            }
            jstat_file.close();
        }
    }


}

void jstat_profiler_data_visualizer::GenerateJstatGraphs()
{

    vector<float> HU_default;
    vector<float> CR_default;
    vector<float> CLR_default;
    vector< vector<float> > graph_data_default;
    graph_data_default.push_back(HU_default);
    graph_data_default.push_back(CR_default);
    graph_data_default.push_back(CLR_default);

    string temp="default";

    this->GenerateJstatData(graph_data_default,temp);
    this->progress_bar->UpdateProgressBar(70);

    //Generating tuned graphs
    vector<float> HU_tuned;
    vector<float> CR_tuned;
    vector<float> CLR_tuned;
    vector< vector<float> > graph_data_tuned;
    graph_data_tuned.push_back(HU_tuned);
    graph_data_tuned.push_back(CR_tuned);
    graph_data_tuned.push_back(CLR_tuned);
    temp="tuned";

    this->GenerateJstatData(graph_data_tuned,temp);
    this->progress_bar->UpdateProgressBar(80);
    this->DrawGCGraph(graph_data_default[0],graph_data_tuned[0]);
    this->DrawCompilerGraph(graph_data_default[1],graph_data_tuned[1]);
    this->DrawClassGraph(graph_data_default[2],graph_data_tuned[2]);
    this->progress_bar->UpdateProgressBar(100);





}

void jstat_profiler_data_visualizer::DrawClassGraph(vector<float> class_default_list, vector<float> class_tuned_list){

    ui->graph_class->addGraph();
    ui->graph_class->xAxis->setLabel("Time (ms)");
    ui->graph_class->yAxis->setLabel("Overall Class Loading Rate (per ms)");

    if(class_default_list.size()<class_tuned_list.size()){
        ui->graph_class->xAxis->setRange(0, class_tuned_list.size()+10);
    }
    else{
        ui->graph_class->xAxis->setRange(0, class_default_list.size()+10);
    }

    ui->graph_class->yAxis->setRange(0, 0);

    float y;
    float ymax = 0;

    if (class_default_list.size()>0){
        ymax = class_default_list[0];
        ui->graph_class->yAxis->setRange(0, ymax);
    }


    for (int i=0;i<class_default_list.size();i++) {
        y = class_default_list[i];
        if(ymax< y){
            ui->graph_class->yAxis->setRange(0, 1.5*y);
            ymax=y;
        }
        ui->graph_class->graph(0)->addData(i,y);
    }

    //@Drawing : Tuned Graph
    //draw tuned graph
    ui->graph_class->addGraph();
    ui->graph_class->graph(1)->setPen(QPen(Qt::red));
    if (class_tuned_list.size()>0 && ymax == 0){
        ymax = class_default_list[0];
        ui->graph_class->yAxis->setRange(0, ymax);
    }


    for (int i=0;i<class_tuned_list.size();i++) {
        y = class_tuned_list[i];
        if(ymax< y){
            ui->graph_class->yAxis->setRange(0, 1.5*y);
            ymax=y;
        }
        ui->graph_class->graph(1)->addData(i,y);
    }
    ui->graph_class->replot();
}

void jstat_profiler_data_visualizer::DrawCompilerGraph(vector<float> compiler_default_list, vector<float> compiler_tuned_list){

    ui->graph_compiler->addGraph();
    ui->graph_compiler->xAxis->setLabel("Time (ms)");
    ui->graph_compiler->yAxis->setLabel("Overall Compilation Rate (per ms)");

    if(compiler_default_list.size()<compiler_tuned_list.size()){
        ui->graph_compiler->xAxis->setRange(0, compiler_tuned_list.size()+10);
    }
    else{
        ui->graph_compiler->xAxis->setRange(0, compiler_default_list.size()+10);
    }

    ui->graph_compiler->yAxis->setRange(0, 0);
    float y;
    float ymax = 0;
    if (compiler_default_list.size()>0){
        ymax = compiler_default_list[0];
        ui->graph_compiler->yAxis->setRange(0, ymax);
    }
    for (int i=0;i<compiler_default_list.size();i++) {
        y = compiler_default_list[i];
        if(ymax < y){
            ui->graph_compiler->yAxis->setRange(0, 1.5*y);
            ymax = y;
        }
        ui->graph_compiler->graph(0)->addData(i,y);
    }

    //@Drawing : Tuned Graph
    //draw tuned graph
    ui->graph_compiler->addGraph();
    ui->graph_compiler->graph(1)->setPen(QPen(Qt::red));
    if (compiler_tuned_list.size()>0 && ymax == 0){
        ymax = compiler_default_list[0];
        ui->graph_compiler->yAxis->setRange(0, ymax);
    }


    for (int i=0;i<compiler_tuned_list.size();i++) {
        y = compiler_tuned_list[i];
        if(ymax< y){
            ui->graph_compiler->yAxis->setRange(0, 1.5*y);
            ymax=y;
        }
        ui->graph_compiler->graph(1)->addData(i,y);

    }
    ui->graph_compiler->replot();
}

void jstat_profiler_data_visualizer::DrawGCGraph(vector<float> gc_default_list, vector<float> gc_tuned_list){

    ui->graph_gc->addGraph();
    ui->graph_gc->xAxis->setLabel("Time (ms)");
    ui->graph_gc->yAxis->setLabel("Overall Heap Usage (%)");
    if(gc_default_list.size()<gc_tuned_list.size()){
        ui->graph_gc->xAxis->setRange(0, gc_tuned_list.size()+10);
    }
    else{
        ui->graph_gc->xAxis->setRange(0, gc_default_list.size()+10);
    }
    ui->graph_gc->yAxis->setRange(0, 2);

    float y;
    float ymax = 0;

    if (gc_default_list.size()>0){
        ymax = gc_default_list[0];
        ui->graph_gc->yAxis->setRange(0, ymax);
    }

    for (int i=0;i<gc_default_list.size();i++) {
        y = gc_default_list[i];
        if(ymax < y){
            ui->graph_gc->yAxis->setRange(0, 1.5*y);
            ymax = y;
        }
        ui->graph_gc->graph(0)->addData(i,y);
    }

    //@Drawing : Tuned Graph
    //draw tuned graph
    ui->graph_gc->addGraph();
    ui->graph_gc->graph(1)->setPen(QPen(Qt::red));
    if (gc_tuned_list.size()>0 && ymax == 0){
        ymax = gc_default_list[0];
        ui->graph_gc->yAxis->setRange(0, ymax);
    }


    for (int i=0;i<gc_tuned_list.size();i++) {
        y = gc_tuned_list[i];
        if(ymax< y){
            ui->graph_gc->yAxis->setRange(0, 1.5*y);
            ymax=y;
        }
        ui->graph_gc->graph(1)->addData(i,y);
    }
    ui->graph_gc->replot();
}

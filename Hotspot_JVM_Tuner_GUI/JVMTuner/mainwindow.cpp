#include "mainwindow.h"
#include "ui_mainwindow.h"
#include "results.h"
#include "ui_results.h"
#include <sstream>
#include <thread>
using namespace std;
MainWindow::MainWindow(QWidget *parent) :
    QMainWindow(parent),
    ui(new Ui::MainWindow)
{
    ui->setupUi(this);
    ui->chk_gc->setChecked(true);
    ui->chk_jit->setChecked(true);
}

MainWindow::~MainWindow()
{
    delete ui;
}

void MainWindow:: initializeCheckBoxes(bool isChecked){
     ui->chk_bytecode->setChecked(isChecked);
     ui->chk_codecache->setChecked(isChecked);
     ui->chk_deoptimization->setChecked(isChecked);
     ui->chk_gc->setChecked(isChecked);
     ui->chk_interpreter->setChecked(isChecked);
     ui->chk_jit->setChecked(isChecked);
     ui->chk_memory->setChecked(isChecked);
     ui->chk_properties->setChecked(isChecked);
     ui->chk_temporary->setChecked(isChecked);
}

QString MainWindow::getTuningCommand(){
    QStringList flagslist = getOptions();
    QString source = ui->txt_source->text();
    string str=source.toUtf8().constData();
    QString source_folder_path=QString::fromStdString(str.substr(0, str.find_last_of('/')+1));
    QString source_file_name=QString::fromStdString(str.substr(str.find_last_of('/')+1,str.length()));
    QString configfile = ui->txt_configfile->text();
    QString runtime_raction = ui->txt_runtime_fraction->text();





    QString tunning_command = "python src/javaProgramTuner.py";
    if(source_folder_path!=NULL){
       this->class_folder_path=source_folder_path;
       tunning_command = tunning_command + " --class_path="+source_folder_path;
    }
    if(source_file_name!=NULL){
        source_file_name.remove(".java");
        this->program_name=source_file_name;
        tunning_command = tunning_command + " --source="+source_file_name;
    }
    if(configfile!=NULL){
        this->config_file_name=configfile;
        tunning_command = tunning_command+" --configfile="+configfile;
    }
    if(runtime_raction!=NULL){
        tunning_command = tunning_command + " --runtimefraction="+runtime_raction;
    }
    QString flags;
    if(flagslist.length()>0){
        foreach(QString str,flagslist ){
            if (flags==NULL){

                flags = str;
            }
            else{
                flags = flags+","+str;
            }
        }
        
    }
    if (flags!=NULL){
        tunning_command = tunning_command + " --flags="+flags;
    }
    return tunning_command;
}

QStringList MainWindow::getOptions(){
    QStringList optionlist;
    if(ui->chk_bytecode->isChecked()){
        optionlist.append("bytecode");
    }
    if(ui->chk_codecache->isChecked()){
        optionlist.append("codecache");
    }
    if(ui->chk_deoptimization->isChecked()){
        optionlist.append("deoptimization");
    }
    if(ui->chk_gc->isChecked()){
        optionlist.append("gc");
    }

    if(ui->chk_interpreter->isChecked()){
        optionlist.append("interpreter");
    }
    if(ui->chk_jit->isChecked()){
        optionlist.append("jit");
    }
    if(ui->chk_memory->isChecked()){
        optionlist.append("memory");
    }
    if(ui->chk_properties->isChecked()){
        optionlist.append("properties");
    }
    if(ui->chk_temporary->isChecked()){
        optionlist.append("temporary");
    }

    return optionlist;
}

bool MainWindow::validateFields(){
    QString error_message = "";
    bool error_found = false;
    if (ui->txt_tuningcommand->text()==NULL){
        error_message = "* Give the command to run the program. \n  This should be the command you give on the terminal\n";
        error_found = true;
    }

    if (ui->txt_runtime_fraction->text()==NULL){
        error_message = error_message +"\n* Runtime fraction is needed to decide wait for a result.";
        error_found = true;
    }
    if (!isNumeric(ui->txt_runtime_fraction->text())){
        error_message = error_message +"\n* Runtime fraction is needed to be a number.";
        error_found = true;
    }
    if(ui->txt_source->text()==NULL){
        error_message = error_message +"\n* Select a java program to tune.";
        error_found = true;
    }

    else{
        QStringList source_dot_seperated_list = ui->txt_source->text().split(".");
        QString extension = source_dot_seperated_list[source_dot_seperated_list.length()-1];
        if (extension!="java" && extension!="jar"){
            error_message = error_message +"\n* Invalid file type as source.\n* Select a .java  or .jar file to tune.";
            error_found = true;
        }

    }
    if(ui->txt_configfile->text()==NULL){
        error_message = error_message +"\n* Select a text file to write the best configurtions.";
        error_found = true;
    }
    else{
        QStringList config_dot_seperated_list = ui->txt_configfile->text().split(".");
        QString extension = config_dot_seperated_list[config_dot_seperated_list.length()-1];
        if (extension!="txt"){
            error_message = error_message +"\n* Invalid file type as configuration file.\n* Select a .txt file as configuration file.";
            error_found = true;
        }

    }
    if(error_found){
         QMessageBox::critical(this,tr("Tuner initialization failed"),error_message);
    }
    return error_found;
}

bool MainWindow::isNumeric( QString  iterations)
{
    QByteArray bytestring = iterations.toLocal8Bit();
    const char *numberstring= bytestring.data();
    istringstream iss( numberstring );

    double dTestSink;
    iss >> dTestSink;

    // was any input successfully consumed/converted?
    if ( ! iss )
        return false;

    // was all the input successfully consumed/converted?
    return ( iss.rdbuf()->in_avail() == 0 );
}


/**
 * Signals
 *
**/
void MainWindow::on_cmd_test_clicked()
{
    bool error_found = validateFields();

    if(!error_found){
        this->results = new Results(this);
        results->program_name  = this->program_name;
        results->class_folder_path = this->class_folder_path;
        results->config_file_name = this->config_file_name;
        results->showMaximized();
        results->startprocess(ui->txt_tuningcommand->text());
    }

}



void MainWindow::on_cmd_browse_2_clicked()
{
    QString fileName = QFileDialog::getOpenFileName(this, tr("Open File"),"",tr("Files (*.*)"));
    ui -> txt_configfile ->setText(fileName);
}

void MainWindow::on_cmd_browse_3_clicked()
{
    QString fileName = QFileDialog::getOpenFileName(this, tr("Open File"),"",tr("Files (*.*)"));
    ui -> txt_source ->setText(fileName);
}

void MainWindow::on_txt_source_textChanged(const QString &arg1)
{
    ui->txt_tuningcommand->setText(getTuningCommand());
}

void MainWindow::on_txt_configfile_textChanged(const QString &arg1)
{
    ui->txt_tuningcommand->setText(getTuningCommand());
}

void MainWindow::on_txt_runtime_fraction_textChanged(const QString &arg1)
{
    ui->txt_tuningcommand->setText(getTuningCommand());
}

void MainWindow::on_chk_bytecode_stateChanged(int arg1)
{
    ui->txt_tuningcommand->setText(getTuningCommand());
}

void MainWindow::on_chk_codecache_stateChanged(int arg1)
{
    ui->txt_tuningcommand->setText(getTuningCommand());
}

void MainWindow::on_chk_interpreter_stateChanged(int arg1)
{
    ui->txt_tuningcommand->setText(getTuningCommand());
}

void MainWindow::on_chk_jit_stateChanged(int arg1)
{
    ui->txt_tuningcommand->setText(getTuningCommand());
}

void MainWindow::on_chk_memory_stateChanged(int arg1)
{
    ui->txt_tuningcommand->setText(getTuningCommand());
}

void MainWindow::on_chk_deoptimization_stateChanged(int arg1)
{
    ui->txt_tuningcommand->setText(getTuningCommand());
}

void MainWindow::on_chk_gc_stateChanged(int arg1)
{
    ui->txt_tuningcommand->setText(getTuningCommand());
}

void MainWindow::on_chk_temporary_stateChanged(int arg1)
{
    ui->txt_tuningcommand->setText(getTuningCommand());
}

void MainWindow::on_chk_properties_stateChanged(int arg1)
{
    ui->txt_tuningcommand->setText(getTuningCommand());
}

void MainWindow::on_cmd_stop_clicked()
{
    this->results->stopProcess();
}

void MainWindow::on_chk_all_stateChanged(int arg1)
{
        if(ui->chk_all->isChecked()){
            initializeCheckBoxes(true);
        }
        else{
            initializeCheckBoxes(false);
        }
        ui->txt_tuningcommand->setText(getTuningCommand());
}

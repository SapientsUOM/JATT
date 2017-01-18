#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QMainWindow>
#include <QMessageBox>
#include <QFileDialog>
#include "results.h"
#include "ui_results.h"
#include "appthread.h"
namespace Ui {
class MainWindow;
}

class MainWindow : public QMainWindow
{
    Q_OBJECT

public:

    explicit MainWindow(QWidget *parent = 0);
    ~MainWindow();
    QString class_folder_path;
    QString program_name;
    QString config_file_name;

private slots:

    void initializeCheckBoxes(bool);

    bool validateFields();

    QStringList getOptions();

    QString getTuningCommand();

    void on_cmd_stop_clicked();

    void on_cmd_test_clicked();

    void on_cmd_browse_2_clicked();

    void on_cmd_browse_3_clicked();

    void on_txt_source_textChanged(const QString &arg1);

    void on_txt_configfile_textChanged(const QString &arg1);

    void on_txt_runtime_fraction_textChanged(const QString &arg1);

    bool isNumeric( QString);

    void on_chk_bytecode_stateChanged(int arg1);

    void on_chk_codecache_stateChanged(int arg1);

    void on_chk_interpreter_stateChanged(int arg1);

    void on_chk_jit_stateChanged(int arg1);

    void on_chk_memory_stateChanged(int arg1);

    void on_chk_deoptimization_stateChanged(int arg1);

    void on_chk_ignore_stateChanged(int arg1);

    void on_chk_gc_stateChanged(int arg1);

    void on_chk_temporary_stateChanged(int arg1);

    void on_chk_properties_stateChanged(int arg1);



    void on_chk_all_clicked();

    void on_chk_all_clicked(bool checked);

    void on_chk_all_stateChanged(int arg1);

private:
    Ui::MainWindow *ui;
    Results *results;
    AppThread* thread;



};

#endif // MAINWINDOW_H

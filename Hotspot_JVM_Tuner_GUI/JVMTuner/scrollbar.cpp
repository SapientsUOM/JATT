#include "scrollbar.h"
#include "ui_scrollbar.h"

scrollbar::scrollbar(QWidget *parent) :
    QDialog(parent),
    ui(new Ui::scrollbar)
{
    ui->setupUi(this);
    ui->progressBar->setRange(0,100);
}

scrollbar::~scrollbar()
{
    delete ui;
}

void scrollbar::UpdateProgressBar(int value){

    ui->progressBar->setValue(value);
    this->update();

}

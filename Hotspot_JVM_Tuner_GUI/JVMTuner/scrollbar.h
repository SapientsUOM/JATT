#ifndef SCROLLBAR_H
#define SCROLLBAR_H

#include <QDialog>

namespace Ui {
class scrollbar;
}

class scrollbar : public QDialog
{
    Q_OBJECT

public:
    explicit scrollbar(QWidget *parent = 0);
    void UpdateProgressBar(int value);
    ~scrollbar();

private:
    Ui::scrollbar *ui;
};

#endif // SCROLLBAR_H

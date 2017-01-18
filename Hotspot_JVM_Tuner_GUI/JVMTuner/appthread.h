#ifndef APPTHREAD_H
#define APPTHREAD_H

#include <QThread>
#include <string>
#include<QString>
using namespace std;
class AppThread : public QThread
{
    Q_OBJECT
public:
    bool isAppThreadStopped;
    QString command;
    FILE *in;
    FILE *fp;
    int pid;

    explicit AppThread(QObject *parent = 0);
    void run();
    int pclose2(FILE * fp, pid_t pid);
    FILE * popen2(string command, string type, int & pid);
    void closeProcess();

signals:
    void textChanged(QString);

public slots:

};

#endif // APPTHREAD_H

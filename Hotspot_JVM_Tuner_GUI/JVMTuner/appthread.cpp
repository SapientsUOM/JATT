#include "appthread.h"
#include <QtCore>
#include <unistd.h>
#include <stdlib.h>
#include <stdio.h>
#include <signal.h>
#include <string.h>
#include <sys/wait.h>
#include <errno.h>
#include <string>
#include <sstream>
#include <sys/types.h>

using namespace std;

#define READ   0
#define WRITE  1

AppThread::AppThread(QObject *parent) :
    QThread(parent)
{
    isAppThreadStopped = false;
}

void AppThread::run(){
    isAppThreadStopped = false;
    command = command + " 2>&1";
    string command_temp = command.toStdString();//"ping 8.8.8.8";
    qDebug()<<"Command"<<command;
    fp = popen2(command_temp, "r", pid);
    char command_out[100] = {0};
    stringstream output;

    //Using read() so that I have the option of using select() if I want non-blocking flow
    while (read(fileno(fp), command_out, sizeof(command_out)-1) != 0 && !isAppThreadStopped)
    {
        //qDebug()<<"The output at appthread is : "<< QString::fromStdString(string(command_out));
        emit textChanged(QString::fromStdString(string(command_out)));
        kill(pid, 9);
        memset(&command_out, 0, sizeof(command_out));
    }

    string token;
    while (getline(output, token, '\n'))
    {
        qDebug()<<"The Process Was killed while recieving"<<token.c_str();
    }

    pclose2(fp, pid);
    closeProcess();
}

void AppThread::closeProcess(){

    if(!isAppThreadStopped){
        qDebug()<<"PID"<<pid;
        emit textChanged(QString::fromStdString("Terminating tunning process..."));
        kill(pid+1, 9);
        emit textChanged(QString::fromStdString("The tunning process is stopped. \nYou can see the profiler graphs for the program now.\nTuning process terminated."));
        //pclose2(fp, pid);
    }
    isAppThreadStopped = true;
}

FILE * AppThread::popen2(string command, string type, int & pid)
{
    pid_t child_pid;
    int fd[2];
    pipe(fd);

    if((child_pid = fork()) == -1)
    {
        perror("fork");
        exit(1);
    }

    /* child process */
    if (child_pid == 0)
    {
        if (type == "r")
        {
            close(fd[READ]);    //Close the READ end of the pipe since the child's fd is write-only
            dup2(fd[WRITE], 1); //Redirect stdout to pipe
        }
        else
        {
            close(fd[WRITE]);    //Close the WRITE end of the pipe since the child's fd is read-only
            dup2(fd[READ], 0);   //Redirect stdin to pipe
        }

        execl("/bin/sh", "/bin/sh", "-c", command.c_str(), NULL);
        exit(0);
    }
    else
    {
        if (type == "r")
        {
            close(fd[WRITE]); //Close the WRITE end of the pipe since parent's fd is read-only
        }
        else
        {
            close(fd[READ]); //Close the READ end of the pipe since parent's fd is write-only
        }
    }

    pid = child_pid;

    if (type == "r")
    {
        return fdopen(fd[READ], "r");
    }

    return fdopen(fd[WRITE], "w");
}

int AppThread::pclose2(FILE * fp, pid_t pid)
{
    int stat;

    fclose(fp);
    while (waitpid(pid, &stat, 0) == -1)
    {
        if (errno != EINTR)
        {
            stat = -1;
            break;
        }
    }

    return stat;
}

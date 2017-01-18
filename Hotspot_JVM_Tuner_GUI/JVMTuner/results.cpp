#include "results.h"
#include "ui_results.h"
#include "appthread.h"
#include<stdlib.h>
#include <stdio.h>
#include <math.h>
#include <iostream>
#include <unistd.h>
#include <boost/regex.hpp>
#include <QMessageBox>
#include "string"
#include <QTimer>
#include<qdatetime.h>
using namespace std;
using namespace boost::algorithm;

Results::Results(QWidget *parent) :
    QDialog(parent),
    ui(new Ui::Results)
{
   ui->setupUi(this);
   this->appthread = new AppThread(this);
   this->timer = new QTimer(this);
   this->tunerStartedDateTime = QDateTime::currentDateTime();
   qDebug()<<"tuner Started time"<<tunerStartedDateTime.toString();
   connect(timer, SIGNAL(timeout()), this, SLOT(showTime()));
   timer->start(1000);
   QObject::connect(appthread,SIGNAL(textChanged(QString)),this,SLOT(onTextChanged(QString)));
   setup();
   first = true;
   is_default_read_from_file = false;
   bestPerformance = INFINITY_DEF;
   defaultRuntime = INFINITY_DEF;

}

Results::~Results()
{
    stopProcess();
    delete ui;
}

void Results::startprocess(QString command){
  this->command = command;
  this->appthread->command = command;
  this->appthread->start();
}

void Results::stopProcess(){
  this->appthread->closeProcess();
}

/**
*  Result window ui initialization.
*  This method initialize styles for ui elements
**/

void Results::setup(){
    QPalette p = ui->txt_console ->palette();
    p.setColor(QPalette::Base, QColor(48, 10, 36));
    QPalette bestconfig_text = ui->txt_bestconfig->palette();
    bestconfig_text.setColor(QPalette::Base,QColor(48,10,36/*189,189,189*/));
    ui->txt_bestconfig->setPalette(bestconfig_text);
    //ui->txt_bestconfig->setText("-XX:+UseParallelGC -XX:-ParallelGCVerbose -XX:ParallelGCThreads=3 -XX:ParallelGCBufferWastePct=15 -XX:+AlwaysTenure -XX:-NeverTenure -XX:+ScavengeBeforeFullGC -XX:-UseParallelOldGC -XX:-ResizePLAB -XX:-ResizeOldPLAB -XX:+AlwaysPreTouch -XX:-ParallelRefProcEnabled -XX:-ParallelRefProcBalancingEnabled -XX:-UseTLAB -XX:-ResizeTLAB -XX:+ZeroTLAB -XX:+FastTLABRefill -XX:-NeverActAsServerClassMachine -XX:+AlwaysActAsServerClassMachine -XX:-UseAutoGCSelectPolicy -XX:+UseAdaptiveSizePolicy -XX:-UsePSAdaptiveSurvivorSizePolicy -XX:-UseAdaptiveGenerationSizePolicyAtMinorCollection -XX:+UseAdaptiveGenerationSizePolicyAtMajorCollection -XX:+UseAdaptiveSizePolicyWithSystemGC -XX:-UseAdaptiveGCBoundary -XX:+UseAdaptiveSizePolicyFootprintGoal -XX:+UseAdaptiveSizeDecayMajorGCCost -XX:+UseGCOverheadLimit -XX:-DisableExplicitGC -XX:+CollectGen0First -XX:+BindGCTaskThreadsToCPUs -XX:+UseGCTaskAffinity -XX:YoungPLABSize=6108 -XX:OldPLABSize=1361 -XX:GCTaskTimeStampEntries=263 -XX:TargetPLABWastePct=10 -XX:PLABWeight=75 -XX:OldPLABWeight=27 -XX:MarkStackSize=5141127 -XX:MarkStackSizeMax=499791324 -XX:RefDiscoveryPolicy=0 -XX:InitiatingHeapOccupancyPercent=29 -XX:MaxRAM=102494187795 -XX:ErgoHeapSizeLimit=0 -XX:MaxRAMFraction=3 -XX:DefaultMaxRAMFraction=4 -XX:MinRAMFraction=2 -XX:InitialRAMFraction=92 -XX:AutoGCSelectPauseMillis=6268 -XX:AdaptiveSizeThroughPutPolicy=0 -XX:AdaptiveSizePausePolicy=0 -XX:AdaptiveSizePolicyInitializingSteps=21 -XX:AdaptiveSizePolicyOutputInterval=0 -XX:AdaptiveSizePolicyWeight=15 -XX:AdaptiveTimeWeight=26 -XX:PausePadding=1 -XX:PromotedPadding=1 -XX:SurvivorPadding=1 -XX:AdaptivePermSizeWeight=15 -XX:PermGenPadding=1 -XX:ThresholdTolerance=5 -XX:AdaptiveSizePolicyCollectionCostMargin=38 -XX:YoungGenerationSizeIncrement=17 -XX:YoungGenerationSizeSupplement=51 -XX:YoungGenerationSizeSupplementDecay=12 -XX:TenuredGenerationSizeIncrement=25 -XX:TenuredGenerationSizeSupplement=57 -XX:TenuredGenerationSizeSupplementDecay=2 -XX:MaxGCPauseMillis=18561604466259967612 -XX:GCPauseIntervalMillis=0 -XX:MaxGCMinorPauseMillis=10778540132918410573 -XX:GCTimeRatio=119 -XX:AdaptiveSizeDecrementScaleFactor=3 -XX:AdaptiveSizeMajorGCDecayTimeScale=10 -XX:MinSurvivorRatio=3 -XX:InitialSurvivorRatio=6 -XX:BaseFootPrintEstimate=384559451 -XX:GCHeapFreeLimit=2 -XX:PrefetchCopyIntervalInBytes=600 -XX:PrefetchScanIntervalInBytes=784 -XX:PrefetchFieldsAhead=1 -XX:ProcessDistributionStride=4 -XX:+UseCompiler -XX:+UseCounterDecay -XX:+AlwaysCompileLoopMethods -XX:+DontCompileHugeMethods -XX:+TieredCompilation -XX:Tier0InvokeNotifyFreqLog=10 -XX:Tier2InvokeNotifyFreqLog=5 -XX:Tier3InvokeNotifyFreqLog=8 -XX:Tier0BackedgeNotifyFreqLog=10 -XX:Tier2BackedgeNotifyFreqLog=12 -XX:Tier3BackedgeNotifyFreqLog=13 -XX:Tier2CompileThreshold=0 -XX:Tier2BackEdgeThreshold=0 -XX:Tier3InvocationThreshold=169 -XX:Tier3MinInvocationThreshold=71 -XX:Tier3CompileThreshold=2430 -XX:Tier3BackEdgeThreshold=64112 -XX:Tier4InvocationThreshold=4814 -XX:Tier4MinInvocationThreshold=612 -XX:Tier4CompileThreshold=7906 -XX:Tier4BackEdgeThreshold=45614 -XX:Tier3DelayOn=5 -XX:Tier3DelayOff=1 -XX:Tier3LoadFeedback=6 -XX:Tier4LoadFeedback=2 -XX:TieredCompileTaskTimeout=68 -XX:TieredStopAtLevel=4 -XX:Tier0ProfilingStartPercentage=242 -XX:TieredRateUpdateMinTime=0 -XX:TieredRateUpdateMaxTime=25 -XX:+TimeLinearScan -XX:-LIRFillDelaySlots -XX:+C1ProfileCalls -XX:+C1ProfileVirtualCalls -XX:+C1ProfileInlinedCalls -XX:+C1ProfileBranches -XX:+C1ProfileCheckcasts -XX:+C1OptimizeVirtualCallProfiling -XX:-C1UpdateMethodData -XX:ValueMapInitialSize=12 -XX:ValueMapMaxLoopSize=7 -XX:CompilationRepeat=0 -XX:SafepointPollOffset=358 -XX:CompileThreshold=11034 -XX:BackEdgeThreshold=68306 -XX:OnStackReplacePercentage=189 -XX:InterpreterProfilePercentage=39 -XX:-Inline -XX:+ClipInlining -XX:+UseTypeProfile -XX:+UseCountLeadingZerosInstruction -XX:-UsePopCountInstruction -XX:+IgnoreUnrecognizedVMOptions -XX:+DisplayVMOutputToStderr -XX:+DisplayVMOutputToStdout -XX:+UseHeavyMonitors -XX:+RangeCheckElimination -XX:-SplitIfBlocks -XX:-AggressiveOpts -XX:+UseStringCache -XX:CICompilerCount=1 -XX:CompilationPolicyChoice=0 -XX:TypeProfileMajorReceiverPercent=49 -XX:-UseLoopPredicate -XX:+OptimizeFill -XX:-ReduceFieldZeroing -XX:+ReduceInitialCardMarks -XX:-ReduceBulkZeroing -XX:+UseFPUForSpilling -XX:+PartialPeelLoop -XX:-PartialPeelAtUnsignedTests -XX:-ReassociateInvariants -XX:-LoopUnswitching -XX:+UseSuperWord -XX:+BranchOnRegister -XX:-UseRDPCForConstantTableBase -XX:+UseOldInlining -XX:-UseBimorphicInlining -XX:-UseOnlyInlinedBimorphic -XX:-InsertMemBarAfterArraycopy -XX:-OptoScheduling -XX:+OptoBundling -XX:-UseJumpTables -XX:-UseDivMod -XX:-EliminateLocks -XX:+DoEscapeAnalysis -XX:+EliminateAllocations -XX:+UseOptoBiasInlining -XX:-OptimizeStringConcat -XX:-BlockLayoutByFrequency -XX:+BlockLayoutRotateLoops -XX:MaxLoopPad=13 -XX:NumberOfLoopInstrToAlign=5 -XX:LoopUnrollMin=5 -XX:MultiArrayExpandLimit=9 -XX:TrackedInitializationLimit=36 -XX:PartialPeelNewPhiDelta=0 -XX:InteriorEntryAlignment=14 -XX:LoopUnrollLimit=33 -XX:ConditionalMoveLimit=4 -XX:MaxNodeLimit=68776 -XX:NodeLimitFudgeFactor=1209 -XX:MinJumpTableSize=12 -XX:MaxJumpTableSize=77870 -XX:MaxJumpTableSparseness=6 -XX:AutoBoxCacheMax=142 -XX:EliminateAllocationArraySizeLimit=64 -XX:ValueSearchLimit=853 -XX:MaxLabelRootDepth=1182 -XX:BlockLayoutMinDiamondPercentage=26 -XX:LoopOptsCount=41 -XX:-EstimateArgEscape -XX:MaxBCEAEstimateLevel=5 -XX:MaxBCEAEstimateSize=166 -XX:AllocatePrefetchStyle=0 -XX:AllocatePrefetchDistance=150 -XX:AllocatePrefetchLines=2 -XX:AllocatePrefetchStepSize=45 -XX:AllocatePrefetchInstr=0 -XX:ReadPrefetchInstr=0 -XX:SelfDestructTimer=0 -XX:SafepointTimeoutDelay=13215 -XX:NmethodSweepFraction=18 -XX:NmethodSweepCheckInterval=2 -XX:MaxInlineLevel=12 -XX:MaxRecursiveInlineLevel=1 -XX:MaxInlineSize=22 -XX:MaxTrivialSize=4 -XX:MinInliningThreshold=183 -XX:ProfileIntervalsTicks=69 -XX:TypeProfileWidth=1 -XX:PerMethodRecompilationCutoff=470 -XX:PerBytecodeRecompilationCutoff=140 -XX:PerMethodTrapLimit=77 -XX:PerBytecodeTrapLimit=4 -XX:AliasLevel=3 -XX:InlineSmallCode=1133 -XX:FreqInlineSize=379 -XX:PreInflateSpin=8 -XX:-UseCodeCacheFlushing -XX:CodeCacheMinimumFreeSpace=722043 -XX:MinCodeCacheFlushingInterval=23 -XX:CodeCacheFlushingMinimumFreeSpace=873565 -XX:OptoLoopAlignment=19 -XX:InitialCodeCacheSize=3720926 -XX:ReservedCodeCacheSize=32645359 -XX:CodeCacheExpansionSize=65275 -XX:SelfDestructTimer=0 -XX:MaxJavaStackTraceDepth=762 -XX:SafepointTimeoutDelay=13215 -XX:NmethodSweepFraction=18 -XX:NmethodSweepCheckInterval=2 -XX:MaxInlineLevel=12 -XX:MaxRecursiveInlineLevel=1");
    ui->txt_console->setPalette(p);
    ui->txt_console->setStyleSheet("QTextEdit"
                                   "{"
                                   "color: yellow;"
                                   "}");
    ui->txt_bestconfig->setStyleSheet("QTextEdit"
                                   "{"
                                   "color: yellow;"
                                   "}");
    ui->graph->addGraph();
    ui->graph->xAxis->setLabel("x : Time (s)");
    ui->graph->yAxis->setLabel("y : Execution Time (s)");
    ui->graph->xAxis->setRange(0, 1);
    ui->graph->yAxis->setRange(0, 1);


    ui->performancegraph->addGraph();
    ui->performancegraph->xAxis->setLabel("x : Time (s)");
    ui->performancegraph->yAxis->setLabel("x : Performance Improvement (%)");
    ui->performancegraph->xAxis->setRange(0, 1);
    ui->performancegraph->yAxis->setRange(0, 100);
}


void Results::onTextChanged(QString text){

    if(!(this->is_default_read_from_file)){

        if (text.contains(DEFAULT_CONFIG_TAG)){
            QStringList textlist = text.split(":");
            string double_string = textlist[1].toStdString();
            qDebug()<<"default run time"<<textlist[1];
            std::istringstream i(double_string);
            double x;
            if (!(i >> x)){
                defaultRuntime = INFINITY_DEF;
            }
            else{
                defaultRuntime = x;
            }
            this->ui->num_default_time->display(defaultRuntime);
            this->is_default_read_from_file = true;
            qDebug()<<"The default time found"<<defaultRuntime;
        }

    }

   qDebug()<<"Txt is "<< text;
   QString time_str,perfor_str;
   double time,performance;
   ui->txt_console->append(text);
   if (text.contains("cost time=")){
       text=text.replace(" *"," ");
       text=text.replace("[ ","[");
       QStringList textlist = text.split(" ");
       for(int i = 0 ; i<textlist.count();i++){
           if (textlist[i].contains("s]")){
                time_str = textlist[i].replace("s]","");
                time = time_str.toDouble();
           }
           else if (textlist[i].contains("time=")){
                perfor_str = textlist[i].replace("time=","");
                performance = atof( perfor_str.toStdString().c_str() );
                drawGraph(time,performance);
                break;
           }
       }

   }

   QString best_config=this->GetBestFlagConfiguration();
   string best_config_str=best_config.toStdString();
   if(best_config_str!=""){
    this->ui->txt_bestconfig->setText(best_config);
   }


}

void Results::showTime(){

    if(!this->appthread->isAppThreadStopped){
        QDateTime currentDateTime = QDateTime::currentDateTime();
        int days = tunerStartedDateTime.daysTo(currentDateTime);
        int secs = tunerStartedDateTime.time().secsTo(currentDateTime.time());
        int hours = floor(secs /(60*60));
        int mins = floor((secs - hours * 60*60)/60);
        secs = secs - hours * 60*60 - mins * 60;
        QString tuningTime = QString::number(days)+":"+QString::number(hours)+":"+QString::number(mins)+":"+QString::number(secs);
        this->ui->num_tuning->display(tuningTime);
    }

}
void Results::drawGraph(double time, double performance){
      if (bestPerformance == 0 || bestPerformance > performance){
          if (bestPerformance==0){
              ui->performancegraph->graph(0)->addData(0,0);
              ui->performancegraph->replot();
          }
          bestPerformance = performance;

      }



      ui->graph->xAxis->setRange(0, 1.1*time);
      ui->performancegraph->xAxis->setRange(0,1.1*time);

      if (ui->graph->yAxis->range().maxRange<performance || first){
          ui->graph->yAxis->setRange(0, 1.1*performance);
          first = false;
      }
      double performanceImprovement = 100*(defaultRuntime - performance) / defaultRuntime;
      double bestPerformanceImprovement =  100*(defaultRuntime - bestPerformance) / defaultRuntime;

      if(ui->performancegraph->yAxis->range().maxRange<performanceImprovement){
          ui->performancegraph->yAxis->setRange(0,1.1*performanceImprovement);

      }

      ui->performancegraph->graph(0)->addData(time,performanceImprovement);
      ui->performancegraph->replot();

      ui->graph->graph(0)->addData(time, performance);
      ui->graph->replot();

      ui->num_performance->display(bestPerformance);
      //ui->num_tuning->display(time);
      ui->num_best_improvement->display(bestPerformanceImprovement);
}



QString Results::GenerateExecutionCode(QString run_command, QString program_name, QString run_type){

    QString execute="python src/JVM_Profile_Extractor.py";
    execute=execute+" --RunCommand="+run_command;
    execute=execute+" --ProgramName="+program_name;
    execute=execute+" --RunType="+run_type;

    return execute;

}

QString Results::GetBestFlagConfiguration(){

    ifstream jstat_file;
    string line="";
    vector<string> tokens;
    int line_counter=0;
    int last_improvement_tag_line=0;
    try{
        jstat_file.open(config_file_name.toStdString(),ios::out);
        if(jstat_file.is_open()){
            getline(jstat_file,line);
            while ( getline (jstat_file,line) )
            {
                line_counter++;
                tokens.push_back(line);
                if(QString::fromStdString(line).contains(IMPROVEMENT_TAG)){
                    last_improvement_tag_line = line_counter;
                }
                //qDebug()<<"ConfigFile text = "<<QString::fromStdString(line);
            }
            jstat_file.close();
        }

        //qDebug()<<"line counter "<<line_counter;
        //qDebug()<<"last_improvement_tag_line"<<last_improvement_tag_line;
        if((!tokens.empty()) && (last_improvement_tag_line-2)>=0){
            return QString::fromStdString(tokens[last_improvement_tag_line-2]);
        }else
        {
          return QString::fromStdString("");
        }
    }catch(int e){
        qDebug()<<"file config file open failed.";
        return QString::fromStdString("");
    }

}

/**
* Event Listeners
*
*/
void Results::on_cmd_jstat_clicked()
{
    if(appthread->isAppThreadStopped){

        QString default_run_command;
        QString tuned_run_command;


        default_run_command="\"java -classpath "+ class_folder_path +" "+program_name+"\" ";

        QString default_execute;
        QString tuned_execute;

        QString best_configuration_flags="";
        //Assiign best configuration flags
        best_configuration_flags=GetBestFlagConfiguration();
        qDebug()<<"THE BEST CONFIGURATION IS"<<best_configuration_flags;


        tuned_run_command="\"java "+best_configuration_flags+" -classpath "+class_folder_path +" "+program_name+"\" ";

        default_execute=this->GenerateExecutionCode(default_run_command,program_name,"default");

        tuned_execute=GenerateExecutionCode(tuned_run_command,program_name,"tuned");

        this->profiler = new jstat_profiler_data_visualizer(this,default_execute.toStdString(),tuned_execute.toStdString(),program_name.toStdString());
        profiler->showMaximized();


    }
    else{
         QMessageBox::critical(this,tr(""),"Stop the tunning process first!");
    }
}

void Results::on_cmd_stopTuner_clicked()
{
    stopProcess();
}

void Results::on_cmd_showConfigFile_clicked()
{

}

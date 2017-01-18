#include "timeperformanceplot.h"


class TimePerformancePlot : public QwtPlot
{
public:
  TimePerformancePlot( QWidget *parent=0, char *name=0 ) : QwtPlot( parent, name )
  {
    // Show a title
    setTitle( "This is an Example" );

    // Show a legend at the bottom
    setAutoLegend( true );
    setLegendPos( Qwt::Bottom );

    // Show the axes
    setAxisTitle( xBottom, "x" );
    setAxisTitle( yLeft, "y" );

    // Insert two curves and get IDs for them
    long cSin = insertCurve( "y = sin(x)" );
    long cSign = insertCurve( "y = sign(sin(x))" );

    // Calculate the data, 500 points each
    const int points = 500;
    double x[ points ];
    double sn[ points ];
    double sg[ points ];

    for( int i=0; i<points; i++ )
    {
      x[i] = (3.0*3.14/double(points))*double(i);

      sn[i] = 2.0*sin( x[i] );
      sg[i] = (sn[i]>0)?1:((sn[i]<0)?-1:0);
    }

    // Copy the data to the plot
    setCurveData( cSin, x, sn, points );
    setCurveData( cSign, x, sg, points );

    // Set the style of the curves
    setCurvePen( cSin, QPen( blue ) );
    setCurvePen( cSign, QPen( green, 3 ) );

    // Show the plots
    replot();
  }
};

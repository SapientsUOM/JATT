

//This class measures the time elapse between antobjects creation and threadexcution.
//This measure the time to create objects + time to execute threads.
//Ant Colony Shared Resource example with SYCHRONIZTION.
public class AntColonyMain {
	
	public static void main(String[] args) {
		
		long startThreadTime =0 , endThreadTime=0, startTime = 0 , endTime = 0, antCreationTime = 0, threadRunningTime = 0 ;
		double avgantCreationTime=0, avgthreadRunningTime = 0;
		int programIterations=5;
		long[] antCreationTimeArray = new long[programIterations];
		long[] threadRunTimeArray = new long[programIterations];
		int NoofAnts = Integer.parseInt(args[0]);
		// Above variable should be changes for every test.
		
		for (int colonyNum = 0 ;colonyNum<programIterations; colonyNum++ )
		{
			System.out.println("Starting" +colonyNum);
			AntColony colony  = new AntColony(NoofAnts);
			
			if (colony.ants != null){
				if (colony.ants[0] == null){
					startTime = System.currentTimeMillis();
					colony.createAnts();
				}
			}
			
			if (colony.ants != null){
				if (colony.ants[0] != null){
					endTime = System.currentTimeMillis();
				}
				
			}
			
			antCreationTime = endTime - startTime ;
			antCreationTimeArray[colonyNum]=antCreationTime;
			System.out.println("*******************************\nProgram Iteration "+colonyNum+
					"\nTime Ant Creation Started =" + startTime+
					"\nTime Ant Creation Ended =" + endTime+
					"\nTime to Create Ants = " + antCreationTime+
					"\n*******************************\n");
			
		
			if(colony.getAntsInHole()==0){
				startThreadTime = System.currentTimeMillis();
				colony.startEntering();
			}
			
			while(colony.getAntsInHole()!=NoofAnts){
				System.out.print("");
			}
			
			if(colony.getAntsInHole()== NoofAnts){
				endThreadTime = System.currentTimeMillis();
			}
			
			threadRunningTime = endThreadTime-startThreadTime;
			threadRunTimeArray[colonyNum]=threadRunningTime;
			System.out.println("*******************************\nProgram Iteration "+colonyNum+
					"\nTime Thread.Start call Started =" + startThreadTime+
					"\nTime Thread Execution Ended =" + endThreadTime+
					"\nTime to Create and Run Threads = " + threadRunningTime+
					"\n*******************************\n");
			colony.clearColony(colonyNum);
			colony = null;
		}
		
		long sum = 0;
		for (long tempval : antCreationTimeArray) sum+= tempval;
		avgantCreationTime = 1.0d* sum/antCreationTimeArray.length;
		System.out.println ("Average AntSet Creation Time "+ avgantCreationTime);
		
		sum = 0;
		for (long tempval : threadRunTimeArray) sum+= tempval;
		avgthreadRunningTime = 1.0d* sum/threadRunTimeArray.length;
		System.out.println ("Average Run time of Thread creating an Execution "+ avgthreadRunningTime);
		
	
	}

}


public class AntColony {
	
	  public int noOfAnts;
	  public Ant[] ants;
	  public AntHole hole;
	  
    public AntColony(int noOfAnts){
  	  this.noOfAnts=noOfAnts;
  	  this.ants = new Ant[noOfAnts];
  	  this.hole = new AntHole();
    }
    public void createAnts(){
  	  for (int i=0 ; i< noOfAnts ; i++){
  		  ants[i] = new Ant("Ant "+i , hole); 
  	  }
    }
    public void startEntering(){
  	  for (int i=0 ; i< noOfAnts ; i++){
  		  ants[i].start();
  	  }
    }
    public int getAntsInHole(){
  	  return this.hole.numberOfAntsGotIn;
    }
    public void clearColony(int colonyNum){
    	for (int i=0 ; i< noOfAnts ; i++){
    		  ants[i].stopThread();
    		  ants[i] = null; 
    	  }
    	hole = null;
    	System.out.println("Cleared Colony" +colonyNum);
    }
}

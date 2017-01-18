public class AntHole {

	public int numberOfAntsGotIn;
	
	public AntHole(){
		 numberOfAntsGotIn = 0;
	}
	
	public void OpenDoor() throws Exception{
		    try{
		    	numberOfAntsGotIn++;
		    	int i=0;
		    	while(i<100){
					i++;
				}	
		    }
		    catch(Exception e){
		    	throw e;
		    }
	}
}

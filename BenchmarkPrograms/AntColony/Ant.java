
public class Ant extends Thread {
    private	Thread thread;
    public String name;
	public AntHole hole;
	
	 public Ant(String name,AntHole hole ){
		 this.name = name;
		 this.hole = hole;
	 }
	public  void run() {
		synchronized(hole){
			try{
			hole.OpenDoor();
			}
			catch(Exception e){
				System.out.println("Thread "+ this.name+ " was interrupted.");
			}
		}
		//System.out.println("Thread "+this.name+" is exiting.");
		
	}

	public synchronized void start() {
		
		//System.out.println("Thread "+ this.name + "Starting");
		if(thread==null){
			thread = new Thread(this,this.name);
			thread.start();
		}
		
	}
	
	public void stopThread(){
		if(thread!=null){
			thread.stop();
			thread = null;
		}
		
	}

}

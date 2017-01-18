package IOhandling;

public class MainClass {

	
	public static void main(String[] args) {
		long readStartTime = 0, readEndTime = 0, readingTime = 0;
		
		FileReaderDemo readerdemo = new FileReaderDemo("src\\IOhandling\\readingEx.txt");
		
		if (readerdemo.readingStarted==false){
			readStartTime = System.currentTimeMillis();
		}
		readerdemo.Read();
		if(readerdemo.readingStopped == true){
			readEndTime = System.currentTimeMillis();
		}
		
		readingTime = readEndTime - readStartTime;
		System.out.println("\n\nThe time to read the file and write the steme is " + readingTime);
	}

}

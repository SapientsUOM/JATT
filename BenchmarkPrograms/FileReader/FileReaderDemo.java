package IOhandling;

import java.io.*;
import java.lang.ProcessBuilder.Redirect;

public class FileReaderDemo {

	    private FileReader filereader;
	    private BufferedReader bufferreader;
	    private String filePath;
	    public boolean readingStarted, readingStopped;
	    
	    public FileReaderDemo(String filePath){
	    	this.filePath = filePath;
			try{
				this.filereader = new FileReader(this.filePath);
				this.bufferreader = new BufferedReader(filereader);				
			}
			catch (Exception ex){
				System.out.println("An error occured while ceating the File Reader.\nCheck the path.\n"+ex.toString());
			}
			readingStarted =false;
			readingStopped = false;
	    }
	    
		public void Read(){
			
			String s;
			try{
				readingStarted = true;
				
				while((s = bufferreader.readLine()) != null) {
					System.out.println(s);
				}
				filereader.close();
				readingStopped = true;
			}
			catch(Exception ex){
				System.out.println("An error occured while reading the File.\nTry Again.\n"+ex.toString());
		    }
			
		}
}


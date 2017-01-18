import java.util.Random;
import java.util.Scanner;

public class MatrixMultiplyMain {
	
	private volatile int [][] Mat_A;
	private volatile int [][] Mat_B;
	private volatile int [][] Mat_C;
	
	public MatrixMultiplyMain(){
		
		// Sizes of the Matrices are hard coded for ease of the use.
	    int rowsInA = 1000;
	    int columnsInA =1000;
	    int columnsInB = 1000;
		
	    Mat_A = new int[rowsInA][columnsInA];
	    Mat_B = new int[columnsInA][columnsInB];
	    int minimum=0;
	    int maximum=1000;
	    System.out.println("Random matrix A Generated");
	    for (int i = 0; i < Mat_A.length; i++) {
	         for (int j = 0; j < Mat_A[0].length; j++) {
	             Mat_A[i][j] = minimum + (int)(Math.random()*maximum); 
	         }
	     }
	     System.out.println("Random matrix B Generated");
	     for (int i = 0; i < Mat_B.length; i++) {
	         for (int j = 0; j < Mat_B[0].length; j++) {
	             Mat_B[i][j] = minimum + (int)(Math.random()*maximum);
	         }
	     }
	     
	     
	     
	    
	}
	
	
	public void Multiplication(){
		
      int rowsInA = Mat_A.length;
	  int columnsInA = Mat_A[0].length; // same as rows in B
	  int columnsInB = Mat_B[0].length;
	  Mat_C = new int[rowsInA][columnsInB];
	  for (int i = 0; i < rowsInA; i++) {
	      for (int j = 0; j < columnsInB; j++) {
	          for (int k = 0; k < columnsInA; k++) {
	        	   Mat_C[i][j] = Mat_C[i][j] + Mat_A[i][k] * Mat_B[k][j];
	           }	              
	      }
	   }
		
	}
	

   public static void main(String[] args) {
	   
	   MatrixMultiplyMain Test=new MatrixMultiplyMain();
	   // Warming up the compiler.
	   Test.Multiplication();
	   Test.Multiplication();
	   
	   
	   long start=System.currentTimeMillis();
	   Test.Multiplication();
	   long end=System.currentTimeMillis();
	   long execution_time=end-start;
	   
	   System.out.println("Execution Time:"+execution_time);
  
   }

   
}

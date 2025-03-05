import java.util.Scanner;

public class entradadedados {
    public static void main(String[] args) {


        System.out.println("");
//
//        Scanner sc = new Scanner(System.in);
//
//        String x;
//        x = sc.next();
//
//        System.out.println("Você digitou: " + x);
//
//        sc.close();



//
//        Scanner sc2 = new Scanner(System.in);
//
//        int x2
//        x2 = sc2.nextInt();
//
//        System.out.println("Você digitou o número: " + x2);
//
//        sc2.close();



//
//        Scanner sc2 = new Scanner(System.in);
//
//        double x2;
//        x2 = sc2.nextDouble();
//
//        System.out.printf("Você digitou o número: %.1f %n ", x2);
//
//        sc2.close();



        Scanner sc2 = new Scanner(System.in);

        char x2;
        x2 = sc2.next().charAt(0);

        System.out.printf("Você digitou a letra:  " +  x2);

        sc2.close();



    }
}

//TIP To <b>Run</b> code, press <shortcut actionId="Run"/> or
// click the <icon src="AllIcons.Actions.Execute"/> icon in the gutter.
import java.util.Scanner;

public class Main {
    public static void main(String[] args) {

        Scanner sc = new Scanner(System.in);

        int x = sc.nextInt();


        int soma = 0;
        while (x != 0) {
            soma += x;
            x = sc.nextInt();
        }

        sc.close();

        System.out.println(soma);

    }
}
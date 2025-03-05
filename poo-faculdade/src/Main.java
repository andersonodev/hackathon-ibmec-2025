import java.sql.SQLOutput;
import java.util.Scanner;

public class Main {
    public static void main(String[] args) {

        int idade;

        float peso;

        Scanner teclado = new Scanner(System.in);
        System.out.println("Qual sua idade");
        idade = teclado.nextInt();

        System.out.println("Qual o seu peso?");
        peso = teclado.nextFloat();

        System.out.printf("Idade: " + idade + "\n" + "Peso: " + peso);




        }
    }

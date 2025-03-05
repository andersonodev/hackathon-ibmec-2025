class Coffee {
    private boolean empty = true;

    public boolean isEmpty() {
        return empty;
    }

    public void refill() {
        System.out.println("Refilling coffee...");
        empty = false;
    }

    public void drink() {
        System.out.println("Drinking coffee...");
        empty = true; // Assume que foi bebido tudo
    }
}

public class Main {
    public static void main(String[] args) {
        Coffee myCoffee = new Coffee();
        boolean awake = true;
        while (awake) {
            if (myCoffee.isEmpty()) {
                myCoffee.refill();
            } else {
                myCoffee.drink();
            }

            try {
                Thread.sleep(2000); //
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }
    }
}

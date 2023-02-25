public class Test {

    static class InnerClass {
        int d = 0;
    }

    List<String> myList = null;

    int a;
    String b;
    InnerClass c = new InnerClass();

    String func1() {
        int c = 2;
        return "" + c;
    }

}

class MyClass {
}

class FooClass {
    class func myStaticFunc() -> Int {
        return 0
    }
}

protocol MyProtocol {
    
}

struct MyStruct {

}

enum MyEnum {
    
}

class MyChildClass:  MyClass, MyProtocol {

    var a = FooClass.myStaticFunc()

    var b = MyStruct()

    func myfunc() {
    }   
}

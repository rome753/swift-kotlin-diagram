
class MyClass {
    
}

protocol MyProtocol {
    
}

struct MyStruct {

}

enum MyEnum {
    
}

class MyChildClass: MyClass, MyProtocol {
    var a: MyClass = MyClass()

    var b = MyStruct()

    func myfunc() -> MyProtocol {
        return Foo()
    }   
}

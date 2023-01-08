
class MyClass {

    static func staticFunc1() {

    }

    class func classFunc1() -> Int {
        
    }

    static var a = 2
    class var b: FooClass = nil

    func func1() {

    }

    func func2() -> String {
        return String()
    }

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
    case success
    case fail
}

class MyChildClass:  MyClass, MyProtocol {

    var a = FooClass.myStaticFunc()

    var b = MyStruct()

    func myfunc() {
    }   
}

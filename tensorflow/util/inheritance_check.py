class Base:
    def fun1(self):
        print("baseFun1")
        self.fun2()
    def fun2(self):
        print("baseFun2")

class Child(Base):
    def fun2(self):
        print("childFun2")
    def run(self):
        self.fun1()

Child().run()
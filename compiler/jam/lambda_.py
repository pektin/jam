from .. import lekvar

class Lambda(lekvar.Function):
    def verify(self):
        lekvar.State.scope.local_context.fakeChild(self)
        lekvar.Function.verify(self)

    #def resolveIdentifier(self, name:str):
    #    return lekvar.State.scope.resolveIdentifier(self.name)

lekvar.Lambda = Lambda

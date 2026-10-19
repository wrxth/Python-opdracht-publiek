from functools import wraps 


def OnceDeco(func):
        @wraps(func)
        def wrapper(self,*args, **kwargs):

            if getattr(self, "SpcUseable",True):
                result = func(self,*args, **kwargs)
                self.SpcUseable = False
                return result
            else:
                print(f"{self.__class__.__name__} special used")
        return wrapper
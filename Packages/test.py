import sys
from PyQt4.QtGui import QApplication
from PyQt4.QtCore import QUrl
from PyQt4.QtWebKit import QWebView
import timeit

class Browser(QWebView):

    def __init__(self):
        QWebView.__init__(self)
        self.loadFinished.connect(self._result_available)

    def _result_available(self, ok):
        frame = self.page().mainFrame()
        print unicode(frame.toHtml()).encode('utf-8')

def decorator_with_args(decor_decorator):
    def decorator_maker(*args, **kwargs):
        def wrapper1(func):
            return decor_decorator(func, args,kwargs)
        return wrapper1
    return decorator_maker

@decorator_with_args
def decor_decor(func, *args, **kwargs):
    def wrapper(f_arg1, f_arg2):
        print u'get args:', args, kwargs
        return func(f_arg1, f_arg2)
    return wrapper

@decor_decor(1,2,3, t = 'dsf')
def fu(a1,a2):
    print u'Hello!', a1, a2

def timing(f):
    import time
    def wrap(*args):
        time1 = time.time()
        ret = f(*args)
        time2 = time.time()
        print '%s function took %0.3f ms' % (f.func_name, (time2-time1))
        return ret
    return wrap
@timing
def a():
    a = 0
    for i in [1,2,3,4,5,6,7]*5:
        a +=i
if __name__ == u'__main__':
    a()
    # setup = '''sum(xrange(10))**10'''
    # print timeit.Timer(setup=setup).repeat(7)
    # app = QApplication(sys.argv)
    # view = Browser()
    # view.load(QUrl(u'http://www.google.com'))
    # app.exec_()


__author__ = 'Aliaksandr'


import cPickle as pickle

a = [1,2,3]
with open(u'D:/workspace/GitProject/testDB.pkl','wb') as output:
    pickle.dump(a, output, 2)


with open(u'D:/workspace/GitProject/testDB.pkl', u'rb') as inp:
    q = pickle.load(inp)
    print q

import os
import pickle


full_path = os.path.realpath(__file__)
file_directory = os.path.dirname(full_path)

with open(file_directory + '/pickled/model.pickle') as f:  # Python 3: open(..., 'rb')
    nb = pickle.load(f)

with open(file_directory + '/pickled/count_vec.pickle') as f:  # Python 3: open(..., 'rb')
    count_vec = pickle.load(f)

with open(file_directory + '/pickled/fselect.pickle') as f:  # Python 3: open(..., 'rb')
    fselect = pickle.load(f)


def calculate1(myReview):
    global nb
    testList = []
    testVec = []
    testList.append(clean_review(myReview))
    print testList
    testVec = count_vec.transform(testList)
    print testVec
    testVec = fselect.transform(testVec)
    print '\n'
    print testVec
    print '\n'
    mood = nb.predict(testVec)
    print 'Prediction: ' + str(mood)
    return mood * 1.0, 1.0
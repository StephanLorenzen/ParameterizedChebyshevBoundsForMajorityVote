#!/bin/sh

mkdir data
cd data

# Get letter
mkdir letter
wget -O letter/letter-recognition.data https://archive.ics.uci.edu/ml/machine-learning-databases/letter-recognition/letter-recognition.data

# Get ilpd
mkdir ilpd
wget -O ilpd/ilpd.csv 'https://archive.ics.uci.edu/ml/machine-learning-databases/00225/Indian%20Liver%20Patient%20Dataset%20(ILPD).csv'

# Get mushroom
mkdir mushroom
wget -O mushroom/mushroom.data https://archive.ics.uci.edu/ml/machine-learning-databases/mushroom/agaricus-lepiota.data

# Get tic-tac-toe
mkdir tic-tac-toe
wget -O tic-tac-toe/tic-tac-toe.data https://archive.ics.uci.edu/ml/machine-learning-databases/tic-tac-toe/tic-tac-toe.data

# Get sonar
mkdir sonar
wget -O sonar/sonar.data https://archive.ics.uci.edu/ml/machine-learning-databases/undocumented/connectionist-bench/sonar/sonar.all-data

# Get usvotes 
mkdir usvotes
wget -O usvotes/house-votes-84.data https://archive.ics.uci.edu/ml/machine-learning-databases/voting-records/house-votes-84.data

# Get wdbc
mkdir wdbc
wget -O wdbc/wdbc.data https://archive.ics.uci.edu/ml/machine-learning-databases/breast-cancer-wisconsin/wdbc.data

# Get heart
mkdir heart
wget -O heart/cleveland.data https://archive.ics.uci.edu/ml/machine-learning-databases/heart-disease/processed.cleveland.data

# Get haberman
mkdir haberman
wget -O haberman/haberman.data https://archive.ics.uci.edu/ml/machine-learning-databases/haberman/haberman.data

# Get ionosphere
mkdir ionosphere
wget -O ionosphere/ionosphere.data https://archive.ics.uci.edu/ml/machine-learning-databases/ionosphere/ionosphere.data

# Get credit-a
mkdir credit-a
wget -O credit-a/crx.data https://archive.ics.uci.edu/ml/machine-learning-databases/credit-screening/crx.data

# Get madelon
mkdir madelon
wget -O madelon/madelon.data https://www.csie.ntu.edu.tw/~cjlin/libsvmtools/datasets/binary/madelon
wget -O tmp https://www.csie.ntu.edu.tw/~cjlin/libsvmtools/datasets/binary/madelon.t
cat tmp >> madelon/madelon.data
rm tmp

# Get phishing
mkdir phishing
wget -O phishing/phishing.data https://www.csie.ntu.edu.tw/~cjlin/libsvmtools/datasets/binary/phishing

# Get svmguide1
mkdir svmguide1
wget -O svmguide1/svmguide1.data https://www.csie.ntu.edu.tw/~cjlin/libsvmtools/datasets/binary/svmguide1
wget -O tmp https://www.csie.ntu.edu.tw/~cjlin/libsvmtools/datasets/binary/svmguide1.t
cat tmp >> svmguide1/svmguide1.data
rm tmp

# Get splice
mkdir splice
wget -O splice/splice.data https://www.csie.ntu.edu.tw/~cjlin/libsvmtools/datasets/binary/splice
wget -O tmp https://www.csie.ntu.edu.tw/~cjlin/libsvmtools/datasets/binary/splice.t
cat tmp >> splice/splice.data
rm tmp

# Get Adult
mkdir adult
wget -O adult/adult.data https://www.csie.ntu.edu.tw/~cjlin/libsvmtools/datasets/binary/a1a
wget -O tmp https://www.csie.ntu.edu.tw/~cjlin/libsvmtools/datasets/binary/a1a.t
cat tmp >> adult/adult.data
rm tmp

# Get german.numer
mkdir numer
wget -O numer/numer.data https://www.csie.ntu.edu.tw/~cjlin/libsvmtools/datasets/binary/german.numer

# Get w1a
mkdir w1a
wget -O w1a/w1a.data https://www.csie.ntu.edu.tw/~cjlin/libsvmtools/datasets/binary/w1a
wget -O tmp https://www.csie.ntu.edu.tw/~cjlin/libsvmtools/datasets/binary/w1a.t
cat tmp >> w1a/w1a.data
rm tmp


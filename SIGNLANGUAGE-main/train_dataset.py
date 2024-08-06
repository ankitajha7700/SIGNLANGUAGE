import pickle
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import numpy as np
data_dict = pickle.load(open('./data.pickle', 'rb'))

data = data_dict['data']
labels = data_dict['labels']

lengths = [len(seq) for seq in data]
target_length = max(lengths)

normalized_data = []
for seq in data:
    if len(seq) < target_length:
       
        seq.extend([0] * (target_length - len(seq)))
    elif len(seq) > target_length:
      
        seq = seq[:target_length]
    normalized_data.append(seq)


data_array = np.array(normalized_data)
labels_array = np.array(labels)


x_train, x_test, y_train, y_test = train_test_split(data_array, labels_array, test_size=0.2, shuffle=True, stratify=labels)


model = RandomForestClassifier()
model.fit(x_train, y_train)

y_predict = model.predict(x_test)

score = accuracy_score(y_predict, y_test)
print('{}% of samples were classified correctly'.format(score * 100))

with open('model.p', 'wb') as f:
    pickle.dump({'model': model}, f)

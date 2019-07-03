import pickle
import joblib
from sklearn.naive_bayes import GaussianNB
from sklearn.ensemble import GradientBoostingClassifier
from src.AI.DocEmbedding import DocEmbedding
from sklearn.linear_model import LogisticRegression
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix, classification_report
from gensim.models.doc2vec import Doc2Vec
from sklearn.metrics import accuracy_score
from src.Database.MyDatabase import MyDatabase
import numpy as np
psqlConnection = MyDatabase()
doc2vec_obj = DocEmbedding()
X_train, y_train, X_test, y_test = doc2vec_obj.inference_vector_from_model()


class MachineLearning:

    def __init__(self):
        self.psqlConnection = None

        self.loaded_doc2vecmodel = None
        self.file_path = "/home/jyri/bear/proje2/data/ml_models/"
        # print(self.X_train, self.y_train, self.X_test, self.y_test)

    def dump_models(self, type_name, model):
        pickle.dump(model, open(self.file_path + type_name, "wb"))

    def heatconmat(self, y_true, y_pred):
        sns.set_context('poster')
        plt.figure(figsize=(9, 6))
        sns.heatmap(confusion_matrix(y_true, y_pred),
                    annot=True,
                    fmt='d',
                    cbar=False,
                    cmap='gist_earth_r',
                    yticklabels=sorted(y_test.unique()))
        plt.show()
        print(classification_report(y_true, y_pred))

    def train_logistic_regression(self):
        logistic_regression = LogisticRegression(C=5, multi_class='multinomial', solver='saga', max_iter=1000)
        logistic_regression.fit(X_train, y_train)

        # y_pred == predict class labels for samples in X.

        y_pred = logistic_regression.predict(X_test)
        # y_proba == The returned estimates for all classes are ordered by the label of classes.
        y_proba = logistic_regression.predict_log_proba(X_test)

        # dump
        self.dump_models("logreg.model", logistic_regression)

        print("***************")
        print(y_pred)
        print(y_proba)

        self.heatconmat(y_test, y_pred)

    def train_naive_bayes(self):
        gnb = GaussianNB()
        gnb.fit(X_train, y_train)

        y_pred = gnb.predict(X_test)
        y_proba = gnb.predict_proba(X_test)

        # print information about prediction class and probability
        print("*" * 20)
        print(y_pred)
        print(y_proba)

        self.heatconmat(y_test, y_pred)
        self.dump_models("naivebayes.model", gnb)

    def train_gbm(self):
        gbm = GradientBoostingClassifier()
        gbm.fit(X_train, y_train)

        y_pred = gbm.predict(X_test)
        y_proba = gbm.predict_proba(X_test)
        print(X_test[0].shape)
        # print(gbm.score(self.X_train, self.y_train))
        print(accuracy_score(y_test, y_pred))

        # print information about prediction class and probability
        print("*" * 20)
        print(y_pred)
        print(y_proba)

        self.dump_models("gradient_boost.model", gbm)
        self.heatconmat(y_test, y_pred)

    #Paketin vektor haline cevrilmesi
    def inference_vector_from_packet(self, packet):
        self.loaded_doc2vecmodel = Doc2Vec.load("/home/jyri/bear/proje2/data/doc2vec/doc2vecmodel")
        list_packet = packet.split(",")
        vector = self.loaded_doc2vecmodel.infer_vector(list_packet)
        # print(vector)
        return vector

    # Paketlerin tahminlenmesi
    def predict_packets(self, packet):
        vector = self.inference_vector_from_packet(packet)
        vector = vector.reshape(1, -1)

        file_path = "/home/jyri/bear/proje2/data/ml_models/"
        gbm_model = joblib.load(file_path + "gradient_boost.model")
        log_model = joblib.load(file_path + "logreg.model")
        nbm_model = joblib.load(file_path + "naivebayes.model")

        print(gbm_model.predict(vector))
        # print(log_model.predict(vector))
        # print(nbm_model.predict(vector))

        proba_gbm = gbm_model.predict_proba(vector)
        proba_log = log_model.predict_proba(vector)
        proba_nbm = nbm_model.predict_proba(vector)

        #print(proba_gbm, proba_log, proba_nbm)
        return proba_gbm

    def sql_query(self, packets, epoch):
        label = ""
        probabilty = self.predict_packets(packets)
        print(probabilty)
        print("probality {}".format(probabilty))
        splitted_packet = packets.split(",")
        splitted_packet.pop(0)

        if np.argmax(probabilty) == 0:
            label = "attack"
        elif np.argmax(probabilty) == 1:
            label = "normal"

        # query fo r packet infos to PostgreSQL columns
        query = "insert into packet ( packet_epoch  , packet_info , packet_label) VALUES ("
        query2 = "'" + str(epoch) + "','" + ",".join(splitted_packet) + "','" + label + "')"
        query = query + query2
        print(query)
        # Send ack to Rabbitmq Queue
        response = psqlConnection.query(query)  # for test purpose True
        print(response)

        return response

import pandas as pd
import numpy as np
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from sklearn.model_selection import train_test_split


class DocEmbedding:

    def __init__(self):

        #csv path.
        self.csv_file = pd.read_csv("/home/jyri/bear/proje2/data/csv/flowtest.csv", low_memory=False)

        self.train, self.test, self.tagged_train, self.tagged_test = self.process_data()

        #initialize model variable
        self.loaded_doc2vecmodel = None

    def process_data(self):
        # split packets as train and test with %70 for train_data and %30 for test data.
        train, test = train_test_split(self.csv_file, test_size=.30, random_state=43, shuffle=True)

        #split and tag the  data for doc2vec

        tagged_train = [TaggedDocument(words=_d.split(","), tags=[str(i)])
                        for i, _d in enumerate(train.packet)]

        tagged_test = [TaggedDocument(words=_d.split(","), tags=[str(i)])
                       for i, _d in enumerate(test.packet)]

        return train, test, tagged_train, tagged_test

    # train doc2vec model.
    def train_doc2vec_model(self):
        epochs = range(100)

        #model initialization
        doc2vec_model = Doc2Vec(vector_size=100,
                                window=5,
                                alpha=.025,
                                min_alpha=0.00025,
                                min_count=2,
                                dm=1,
                                workers=8
                                )
        #Build vocabulary from a self.tagged_train.
        doc2vec_model.build_vocab(self.tagged_train)


        #training part
        for epoch in epochs:
            print(f'Epoch {epoch + 1}')
            doc2vec_model.train(
                self.tagged_train,
                total_examples=doc2vec_model.corpus_count,
                epochs=doc2vec_model.epochs
            )

            doc2vec_model.alpha -= 0.00025
            doc2vec_model.min_alpha = doc2vec_model.alpha
            doc2vec_model.save("/home/jyri/bear/proje2/data/doc2vec/doc2vecmodel")

    def inference_vector_from_model(self):
        """# train_doc2vec_model
        load model that have created by train_doc2vec_model definition.
        """
        self.loaded_doc2vecmodel = Doc2Vec.load("/home/jyri/bear/proje2/data/doc2vec/doc2vecmodel")


        X_train = np.array(
            [self.loaded_doc2vecmodel.infer_vector(self.tagged_train[i][0]) for i in range(len(self.tagged_train))])
        y_train = self.train["label"]
        #same as X_train
        X_test = np.array(
            [self.loaded_doc2vecmodel.infer_vector(self.tagged_test[i][0]) for i in range(len(self.tagged_test))])
        y_test = self.test['label']

        # print("Sample Vector : ", X_train[6])
        # print("Vector label : ", y_train)

        return X_train, y_train, X_test, y_test

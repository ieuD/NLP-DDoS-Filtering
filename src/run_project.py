import sys
from src.AI.MachineLearning import MachineLearning
from src.rabbitmq.Rabbit import Rabbit
from src.sniffing.Sniffing import Sniffing
from src.AI.DocEmbedding import DocEmbedding
import warnings

warnings.filterwarnings("ignore")



rabbitmq_connection = None
jsonizePacket = None
utility_obj = None
obj_doc2vec = None

if __name__ == "__main__":

    argv = sys.argv[1]

    if argv == "scapy":
        rabbitmq_connection = Rabbit()
        Sniffing(rabbitmq_connection.send2_first_queue)

    elif argv == "create_csv":
        rabbitmq_connection = Rabbit()
        rabbitmq_connection.consume4csv(rabbitmq_connection.callback_csv)
    elif argv == "w2v_train":

        obj_doc2vec = DocEmbedding()
        obj_doc2vec.train_doc2vec_model()
        obj_doc2vec.inference_vector_from_model()

    elif argv == "machinelearning":
        ml_obj = MachineLearning()
        ml_obj.train_naive_bayes()
        ml_obj.train_logistic_regression()
        ml_obj.train_gbm()

    elif argv == "label_new_data":
        rabbitmq_connection = Rabbit()
        rabbitmq_connection.consume4ml(rabbitmq_connection.callback_ml)

    else:
        pass

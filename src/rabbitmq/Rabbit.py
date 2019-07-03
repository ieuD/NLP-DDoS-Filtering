from subprocess import PIPE, run
import datetime
from src.AI.MachineLearning import MachineLearning
import pika
import traceback
import json
from src.sniffing.Sniffing import JsonPacket


class Rabbit:

    def __init__(self):
        self.ml_obj = None
        self.csv_file_path = "/home/jyri/bear/proje2/data/csv/flowtest.csv"
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        self.channel = connection.channel()
        self.json_class = JsonPacket()
        self.command = ['wc', '-l', self.csv_file_path]

    def produce4_firstqueue(self, content):
        # print(content)
        self.channel.basic_publish(exchange='amq.direct',
                                   routing_key='black',
                                   body=content)

    def produce4_secondqueue(self, content):
        self.channel.basic_publish(exchange='amq.direct',
                                   routing_key='black',
                                   body=content)

    def send2_first_queue(self, packets):
        packet_info = self.json_class.build_done(packets)
        self.produce4_firstqueue(packet_info)

    def send2_second_queue(self, packets):
        pass

    def consume4csv(self, callback):
        try:
            self.channel.basic_consume(queue="first_queue", on_message_callback=callback, auto_ack=True)
            print('[*] Waiting for messages for ml. To Exit press CTRL+C')
            self.channel.start_consuming()
        except Exception as e:
            print("Consume Error on ML queue :", e)
            print(traceback.print_exc())

    def consume4ml(self, callback):
        try:
            self.channel.basic_consume(queue="second_queue", on_message_callback=callback)
            print('[*] Waiting for messages for ml. To Exit press CTRL+C')
            self.channel.start_consuming()
        except Exception as e:
            print("Consume Error on ML queue :", e)
            print(traceback.print_exc())

    def callback_csv(self, unused_channel, basic_deliver, properties, body):
        self.create_csv(body)

    def callback_ml(self, unused_channel, basic_deliver, properties, body):
        self.parse_input(body,basic_deliver)

    def parse_json(self, json_val):
        header_list = list()
        field_list = list()
        value_list = list()
        my_json = json_val.decode('utf-8')
        data = json.loads(my_json)
        # print(data)
        print("*" * 20)
        for index in range(len(data)):
            for element in data[index].items():
                header_list.append(element[0])
                for proper in element[1].items():
                    field_list.append(proper[0])
                    value_list.append(proper[1])

        str_val_list = [str(i) for i in value_list]

        for index in range(len(str_val_list)):
            if "{}" == str_val_list[index]:
                str_val_list[index] = "empty"

        # print(",".join(header_list))
        # print(",".join(field_list))
        # print(",".join(str_val_list))
        return header_list, field_list, str_val_list

    def parse_input(self, body,basic_deliver):
        # print(body)
        parsed_package = self.parse_json(body)
        self.ml_obj = MachineLearning()
        conc = list()
        headers = ",".join(parsed_package[0])
        field_list = parsed_package[1]
        str_val_list = parsed_package[2]
        # for i in range(len(str_val_list)):
        for i in range(len(field_list)):
            conc.append(field_list[i] + ":")
            conc.append(str_val_list[i] + ",")
        conc[-1] = conc[-1].replace(",", "")

        if "IP,UDP" == headers or "IP,UDP,RAW" == headers or "IP,TCP" == headers or "IP,TCP,RAW" == headers:
            result = run(self.command, stdout=PIPE, stderr=PIPE, universal_newlines=True)

            count = result.stdout.replace(" " + self.csv_file_path, "").replace("\n", "")
            epoch = int(datetime.datetime.timestamp(datetime.datetime.now()) * 1000000)
            sample_line = "epoch:" + str(epoch) + ','
            # print(sample_line)
            conc = [sample_line] + conc
            print("".join(conc))
            response = self.ml_obj.sql_query(str("".join(conc)), epoch)

            if response:
                self.acknowledge_message(basic_deliver.delivery_tag)



    def acknowledge_message(self, delivery_tag):
        self.channel.basic_ack(delivery_tag)

    def create_csv(self, body):
        parsed_package = self.parse_json(body)
        #
        conc = list()
        headers = ",".join(parsed_package[0])
        field_list = parsed_package[1]
        str_val_list = parsed_package[2]
        # for i in range(len(str_val_list)):
        for i in range(len(field_list)):
            conc.append(field_list[i] + ":")
            conc.append(str_val_list[i] + ",")
        conc[-1] = conc[-1].replace(",", "")
        if "IP,UDP" == headers or "IP,UDP,RAW" == headers or "IP,TCP" == headers or "IP,TCP,RAW" == headers:
            result = run(self.command, stdout=PIPE, stderr=PIPE, universal_newlines=True)
            with open(self.csv_file_path, "a+") as csv_writer:
                count = result.stdout.replace(" " + self.csv_file_path, "").replace("\n", "")
                epoch = int(datetime.datetime.timestamp(datetime.datetime.now()) * 1000000)
                sample_line = count + "," + count + ',"' + "epoch:" + str(epoch) + ','
                print(sample_line)
                conc = [sample_line] + conc + ['"']
                csv_writer.writelines(conc)
                csv_writer.write("\n")
                print(headers)
                print("".join(conc))

import json
from scapy.all import *
from scapy.layers.dns import dnstypes, dnsclasses


class Sniffing:
    def __init__(self, callback):
        """

        :param callback:
        """
        sniff(prn=callback, count=0 , iface="wlo1")


class JsonPacket:
    fields_desc = []
    json_valid_types = (dict, list, str, int, float, bool, None)

    # Override
    def build_done(self, pkt):
        jsonized = self._jsonize_packet(pkt)
        # jsonized.append({"Ethernet": {"dst": pkt.fields["dst"], "src": pkt.fields["src"], "type": pkt.fields["type"]}})
        return json.dumps(jsonized, ensure_ascii=False, indent=4)

    def _jsonize_packet(self, pkt):
        out = []
        for layer in self._walk_layers(pkt):
            layer_name = layer.name if layer.name else layer.__name__
            out.append({layer_name: self._serialize_fields(layer, {})})
        return out

    def _walk_layers(self, pkt):
        i = 1
        layer = pkt.getlayer(i)
        while layer:
            yield layer
            i += 1
            layer = pkt.getlayer(i)

    def _serialize_fields(self, layer, serialized_fields={}):
        if hasattr(layer, "fields_desc"):
            for field in layer.fields_desc:
                self._extract_fields(layer, field, serialized_fields)
        return serialized_fields

    def _extract_fields(self, layer, field, extracted={}):
        value = layer.__getattr__(field.name)
        layer_name = layer.name if layer.name else layer.__name__

        # print(layer.name, "->", type(value).__name__)

        # DNSQR used for test purpose.
        if type(value).__name__ == "DNSQR" and extracted['qdcount'] > 0:
            qd = layer.__getattr__("qd")

            if len(dnstypes) > qd.qtype:
                qtype = dnstypes[qd.qtype]
            else:
                qtype = int(qd.qtype)

            if len(dnsclasses) > qd.qclass:
                qclass = dnsclasses[qd.qclass]
            else:
                qclass = qd.qclass
            local_serialized = {'qname': str(qd.qname), 'qtype': str(qtype), 'qclass': str(qclass)}
            extracted[field.name] = local_serialized
        elif type(value) in self.json_valid_types and \
                not hasattr(value, "fields_desc") and \
                not type(value) == list:
            extracted.update({field.name: value})

        

            if field.name == "flags":
                tcp_flags = layer.__getattr__("flags")
                extracted[field.name] = str(tcp_flags)
        elif layer_name == "IP":
            #extracted["packet_length"] = str(len(layer))

            if field.name == "flags":
                ip_flag = layer.__getattr__("flags")  # -> DF, MF
                extracted[field.name] = str(ip_flag)
        else:
            local_serialized = {}
            extracted.update({field.name: local_serialized})
            self._serialize_fields(field, local_serialized)


import paho.mqtt.client as mqtt
import json
import time
import sys

broker_ip = "localhost"
broker_port = 1883

class node_base:
    def __init__(self, name, delay):
        print("Node %s" % (name))

        if(len(sys.argv) == 1):
            print("Expected ID for node %s" % (name))
            quit(1)
    
        self.ID = name + ":" + sys.argv[1]
        self.delay = delay
        self.name = name
        self.params = {}

        self.client = mqtt.Client(self.ID)
        self.client.connect(broker_ip, broker_port)
        print("%s Connected to %s:%d" % (self.ID, broker_ip, broker_port))

        self.client.on_message = self.__handle_message
        self.client.subscribe("nodes/" + name)
        print("Subscribed to nodes/" + name)

        self.client.loop_start()
        while(True):
            # If parameters are in place, call check()
            if(len(self.params) == len(self.get_params_format())):
                preset = {
                    "trigger" : False,
                }

                result = self.check()
                if(result):
                    preset.update(result)

                self.__respond(preset)
                time.sleep(delay)

            # Minimize CPU usage
            time.sleep(0.01)

    def __respond(self, response):
        self.client.publish("noderesult", json.dumps(response))

    def __patched_format(self):
        format_preset = {
            "default" : "",
            "type" : "string",
            "strict" : False,
            "hint": {}
        }

        fmt = self.get_params_format()
        result = {}

        for i in fmt:
            result[i] = format_preset
            result[i].update(fmt[i])

        for i in result:
            print(i)
            # FIXME "time" has hints when it shouldn't
            print(result[i])

        print("patched")
        print(result)
        return result

    def __handle_message(self, client, userdata, message):
        p = message.payload.decode("utf-8").split()

        # Only handle messages meant for this node
        if(p[0] != self.ID):
            return

        # Delete the ID from the incoming parameters
        del p[0]

        params_format = self.get_params_format()
        result = { "valid" : True, "reason" : "" }

        # Is the server asking for the parameters format
        if(p[0] == "paramsformat"):
            result["format"] = self.__patched_format()

        # Does the the parameter count match
        elif(len(p) != len(params_format)):
            result["reason"] = "Number of parameters should be %d" % (len(params_format))
            result["valid"] = False

        else:
            # What keys are in params_format
            params_keys = list(params_format)

            # Loop through each incoming parameter
            for i in range(len(p)):
                typename = params_format[params_keys[i]]
                value = None

                # Attempt to convert the parameter to it's real type
                try:
                    if(typename == "int"): value = int(p[i])
                    elif(typename == "float"): value = float(p[i])

                    if(value == None):
                        value = p[i]

                    self.params[params_keys[i]] = value
                    print("parameter %s = {}" % (params_keys[i]), value)

                    print(params_format[params_keys[i]])
                    #if(params_format[params_keys[i]]["strict"]):
                    #    print("strict" + params_keys[i])

                # The type of the parameter is invalid
                except ValueError:
                    result["reason"] = "Parameter '%s' should be of type '%s'" % (params_keys[i], typename)
                    result["valid"] = False

                    break

            if(result["valid"]):
                result["value"] = {
                    "valid": True,
                    "reason": ""
                }

                res = self.validate_params()
                if(res): result["value"].update(res)

        self.__respond(result)

    def check(self, params):
        raise NotImplementedError()

    def validate_params(self, params):
        raise NotImplementedError()

    def get_params_format(self, params):
        raise NotImplementedError()

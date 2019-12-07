# phenome_001_tools_test.py, Copyright (c) 2019, Phenome Project - Nicholas Saparoff <nick.saparoff@gmail.com>

import socket, time

from phenome.test import BaseTest
from phenome.tools.phenome_builder import PhenomeBuilder
from phenome_core.core.database.model.api import get_objects_by_model_id

builder = None


class TestPhenomeBuilder(BaseTest):

    builder = None

    def setUp(self):

        super(TestPhenomeBuilder, self).setUp()

        # let's reuse the BUILDER object between tests
        # since methods are static and single-OPs anyway

        global builder
        if builder is None:
            builder = PhenomeBuilder()

        self.builder = builder

    def test_phenome_builder_001_get_classtypes(self):

        builder = self.builder
        response = builder.get_classtypes()

        self.assertEqual(response['OBJECT'].value, 0)

    def test_phenome_builder_002_get_subclasstypes(self):

        builder = self.builder
        response = builder.get_subclasstypes()

        self.assertEqual(response['NONE'].value, 0)

    def test_phenome_builder_003_get_models(self):

        builder = self.builder
        models = builder.get_models()
        for model in models:
            # just make sure it is returning real objects and they all have a classtype
            self.assertTrue(model.model_classtype >= 0)

    def test_phenome_builder_004_create_objects(self):
        model_name = 'ROOT_PDU'

        builder = self.builder

        # get a model
        model = builder.get_model(model_name)

        self.assertTrue(model.model == model_name)

        # delete them just in case they are there
        builder.delete_object('test_builder_object1')
        builder.delete_object('test_builder_object2')

        # create object with a fictious IP
        obj1 = builder.create_object(name='test_builder_object1', model=model, ip='129.0.0.101')
        self.assertTrue(obj1 is not None and obj1.id > 0)

        obj1_1 = builder.get_object('test_builder_object1')
        self.assertEqual(obj1.id, obj1_1.id)

        # create another object with a fictious IP, but pass in model ID
        obj2 = builder.create_object(name='test_builder_object2', model=model.id, ip='129.0.0.102')
        self.assertTrue(obj2 is not None and obj2.id > 0)

        obj2_1 = builder.get_object('test_builder_object2')
        self.assertEqual(obj2.id, obj2_1.id)

    def test_phenome_builder_005_get_objects(self):

        builder = self.builder
        response = builder.get_objects()
        self.assertTrue(response is not None and len(response)>0)

    def test_phenome_builder_006_delete_objects(self):

        builder = self.builder

        # delete them - SHOULD BE THERE FROM PREVIOUS TEST
        deleted1 = builder.delete_object('test_builder_object1')
        deleted2 = builder.delete_object('test_builder_object2')

        self.assertTrue(deleted1)
        self.assertTrue(deleted2)

    def test_phenome_builder_007_create_simple_model(self):

        builder = self.builder
        model1 = builder.create_model('Thing1')
        self.assertTrue(model1.id > 0)

    def test_phenome_builder_008_create_complex_model(self):

        builder = self.builder
        model2 = builder.create_model(name='Thing2', classtype=1, subclasstype=0, description='This is Thing2 Model')
        self.assertTrue(model2.id > 0 and model2.model_classtype == 1 and model2.model == 'Thing2')

    def test_phenome_builder_009_delete_simple_model(self):

        builder = self.builder
        model3 = builder.create_model('Thing1')

        if model3:
            builder.delete_model(model3, True)

        model3_1 = builder.get_model('Thing3')
        self.assertTrue(model3_1 is None)

    def test_phenome_builder_010_delete_model_with_objects(self):

        builder = self.builder
        builder.delete_object('test_builder_object1')
        builder.delete_object('test_builder_object2')

        # get the model we created in test 8
        model1 = builder.get_model('Thing2')

        if model1:

            model_id = model1.id

            # use the ID instead of the model itself
            obj1 = builder.create_object(name='test_builder_object1', model=model_id, ip='129.0.0.101')
            # use the NAME instead of the model itself
            obj2 = builder.create_object(name='test_builder_object2', model='Thing2', ip='129.0.0.102')

            objs = get_objects_by_model_id(model_id)
            self.assertTrue(objs is not None and len(objs)==2)

            # now delete, and see if the model is still there and if the objects are still there
            # FORCE DELETE so no prompt for us during the Unit Tests
            success = builder.delete_model(model1, True)
            self.assertTrue(success)

            # see if the objects were removed (from the model and the system)
            objs = get_objects_by_model_id(model_id)
            self.assertTrue(objs is None or len(objs)==0)

            # now just make sure the object doesn't still exist
            obj1  = builder.get_object('test_builder_object1')
            self.assertTrue(obj1 is None)

        else:
            # FAIL
            self.assertTrue(False==True)


class TestSimulator(BaseTest):

    def setUp(self):
        super(TestSimulator, self).setUp()

    def test_simulator_001_HTTP(self):

        api_port = str(self.CONST_SIMULATOR_API_TARGET_PORT)

        # get path to data file
        simulator_data_path = self.absolute_path_of_test_directory + "/supporting/resources/simulator_route_test.py"

        # start the simulator
        simulator = self.startSimulator(simulator_data_path, "HTTP", api_port)

        text_hello_world = None
        json_hello_world = None

        try:

            from phenome_core.util.rest_api import RestAPI

            # create an API object
            api = RestAPI(url="http://127.0.0.1:" + api_port + "/")

            # create an API object for call2
            api2 = RestAPI(url="http://127.0.0.1:" + api_port + "/jsontest")

            # do the API call and ...
            text_hello_world = api.get_raw()
            json_hello_world = api2.get_json()

        except Exception as ex:
            print(ex)
        finally:
            # MAKE SURE TO PUT A FINALLY AND STOP otherwise there could be hanging threads
            simulator.stop()

        # compare the data from the responses
        self.assertEqual('Hello World', text_hello_world)
        self.assertEqual('Hello World', json_hello_world['response'])

    def test_simulator_002_UDP(self):

        self.CONST_SIMULATOR_API_TARGET_PORT += 1

        api_port = self.CONST_SIMULATOR_API_TARGET_PORT

        response = None

        message = "Hello World"
        message_bytes = str.encode(message)
        server_address_and_port = ("127.0.0.1", api_port)

        # start the simulator
        simulator = self.startSimulator(None, "UDP_SERVER", api_port)

        try:

            # create socket and send the message a couple times
            socket_udp = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
            socket_udp.sendto(message_bytes, server_address_and_port)
            socket_udp.sendto(message_bytes, server_address_and_port)
            socket_udp.sendto(message_bytes, server_address_and_port)
            time.sleep(1)

            # did the UDP server get a Hello World?
            response = simulator.get_last_query().decode()

        except Exception as ex:
            print(ex)
        finally:
            # MAKE SURE TO PUT A FINALLY AND STOP otherwise there could be hanging threads
            simulator.stop()

        # compare the response
        self.assertEqual('Hello World', response)



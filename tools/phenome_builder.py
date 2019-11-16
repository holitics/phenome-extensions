from phenome_core.core.database.model import api
from phenome_core.core.database.model.object import Object
from phenome_core.core.database.model.object_model import ObjectModel

from phenome_core.core.globals import global_enums
from phenome_core.core.helpers.numeric_helpers import is_number
from phenome_core.core.helpers.model_helpers import get_model_classtype_id_by_name, delete_model, add_object_model as add_object_model_helper
from phenome_core.core.database.create import CreateDB

class PhenomeBuilder():

    def __init__(self):

        import sys, os

        self.absolute_path_of_util_dir = os.path.dirname(os.path.realpath(__file__))
        self.metadirectory = self.absolute_path_of_util_dir + "/../config/meta/"

        self.force_api_enum_loading = False

        # set the interactive shell so that apps configured to load API ENUMs will not do so
        sys._interactive_shell = True

        self.__load_database_and_metadata()

    def set_force_api_enum_loading(self, enabled):

        self.force_api_enum_loading = enabled

    def reload_metadata(self):

        self.__load_database_and_metadata()

    def load_json_file(self, file_json):
        self.__load_metadata(file_json)

    def __load_database_and_metadata(self):

        # create a META/DB object
        meta = CreateDB()

        if self.force_api_enum_loading:
            import sys
            sys._interactive_shell = False

        # create does both system data and app data loading
        meta.create()

    def __load_metadata(self, file):

        meta = CreateDB()
        meta.load_specific_metadata_file(file)

    def delete_model(self, model):

        success = delete_model(model)

        if success:
            print("Model {} deleted.".format(model))
        else:
            print("Model {} could not be deleted.".format(model))

    def add_model(self, model):
        print("TODO")

    def __print_list(self, response):

        # one line at the top for readability
        print('')
        print(''.join(response))
        # add one more line for readability
        print('')

    def __print_ENUM_data(self, enum, filter):

        d1 = {}

        for data in enum:
            d1[data.value] = data.name

        for key in sorted(d1.keys()):
            value = d1[key]
            if filter is None or filter.lower() in value.lower():
                print('{:15} = {}'.format(key, d1[key]))

    def __print_OBJECT_data(self, objects, key, value, filter):

        d1 = {}

        # one line at the top for readability
        print('')

        if filter is not None:
            if isinstance(filter, int):
                filter = str(filter)
            filter = filter.lower()

        if value == 'unique_id':

            # this is for a real phenome object
            for obj in objects:
                d1[getattr(obj,key)] = obj

            for key in sorted(d1.keys()):
                value = d1[key]
                if filter is None or filter == str(value.id) or \
                        (filter in value.unique_id.lower()) or \
                        (value.ip is not None and filter in value.ip) or \
                        (value.mac is not None and filter in value.mac) or \
                        (filter in value.model.model.lower()):

                    print('{:15} = {}'.format(key, value))

        else:

            # for another type of 'object' in the system

            for obj in objects:
                d1[getattr(obj,key)] = getattr(obj,value)

            for key in sorted(d1.keys()):
                value = d1[key]
                if filter is None or filter in value:
                    print('{:15} = {}'.format(key, value))

        # add one more line for readability
        print('')


    def list_classtypes(self, filter = None):
        return self.__print_ENUM_data(self.get_classtypes(), filter)

    def list_subclasstypes(self, filter = None):
        return self.__print_ENUM_data(self.get_subclasstypes(), filter)

    def list_models(self, filter=None):
        models = api.get_objectmodels()
        self.__print_OBJECT_data(models, 'id', 'model', filter)

    def list_objects(self, filter=None):
        objects = api.get_all_objects()
        self.__print_OBJECT_data(objects, 'id', 'unique_id', filter)

    def get_objects(self, filter=None):

        objects = api.get_all_objects()
        if filter is None:
            return objects
        else:
            objs = []
            filter = str(filter).lower()
            for obj in objects:
                if filter is None or filter == str(obj.id) or \
                        (filter in obj.unique_id.lower()) or \
                        (obj.ip is not None and filter in obj.ip) or \
                        (obj.mac is not None and filter in obj.mac) or \
                        (filter in obj.model.model.lower()):

                    objs.append(obj)

            return objs

    def get_classtypes(self):
        # TODO - add filter
        return global_enums.get_enum('_MODEL_CLASSTYPES_')

    def get_subclasstypes(self):
        # TODO - add filter
        return global_enums.get_enum('_MODEL_SUBCLASSTYPES_')

    def get_models(self):
        # TODO - add filter
        return api.get_objectmodels()

    def get_model(self, model):

        if isinstance(model, ObjectModel):
            # seems redundant but that's OK
            return api.get_objectmodel_by_id(model.id)
        elif is_number(model):
            return api.get_objectmodel_by_id(int(model))
        else:
            return api.get_objectmodel_by_name(model)

    def _create_object(self, model, name, ip, mac):

        # use the ROOT OBJECT as default
        model_id = 1

        if model is not None:
            model_id = self.__get_model_id(model)

        obj = None

        try:
            obj = api.create_object(model_id, ip, mac, name)
        except Exception as e:
            print(e)

        if obj is not None:
            print ("Created object '{}' ID={}".format(obj.unique_id, obj.id))
        else:
            print ("Could not create object '{}'".format(name))

        return obj

    def get_object(self, obj):

        object = self.__get_object(obj)
        if object:
            print("Found object '{}' ID={}".format(object.unique_id, object.id))
            return object
        else:
            print("Could not find object with property '{}'".format(obj))


    def delete_object(self, obj):

        object = self.__get_object(obj)
        if object:
            obj_id = object.id
            obj_name = object.unique_id
            success = api.delete_object(object, False, True)
            if success:
                print ("Deleted object '{}' ID={}".format(obj_name, obj_id))
                return True
        else:
            print("Could not find object with property '{}'".format(obj))

        return False

    def __get_model_id(self, model_repr):

        model_id = None

        try:
            if isinstance(model_repr, ObjectModel):
                model_id = model_repr.id
            elif is_number(model_repr):
                model_id = int(model_repr)
            elif isinstance(model_repr, str):
                model = api.get_objectmodel_by_name(model_repr)
                if model is not None:
                    model_id = model.id
        except Exception as ex:
            print(ex)

        return model_id

    def __get_object(self, obj_repr):

        object = None

        if isinstance(obj_repr, Object):
            object = obj_repr
        elif is_number(obj_repr):
            object = api.get_object_by_id(obj_repr)
        elif isinstance(obj_repr, str):
            object = api.get_object_by_unique_id(obj_repr)
            if object is None:
                object = api.get_object_by_ip(obj_repr)
            if object is None:
                object = api.get_object_by_mac(obj_repr)

        return object

    def create_model(self, *pargs, **kwargs):

        # set some defaults

        model_classtype = 0
        model_subclasstype = 0

        # assume powered object will use this model, since this is what 99.999% of objects created will be
        # otherwise, to create a model that is NOT based on PoweredObject, specify it directly using 'classname'
        model_classname = 'phenome.extensions.classtypes.OBJECT.powered_object.PoweredObject'

        if pargs is not None and len(pargs)==1 and len(kwargs) == 0:

            # create unique model named PARGS
            model_name = pargs[0]
            model_description = model_name

        else:

            model_name = kwargs.get("name")

            if kwargs.get("classname") is not None:
                model_classname = int(kwargs.get("classname"))

            if kwargs.get("classtype") is not None:
                model_classtype = int(kwargs.get("classtype"))

            if kwargs.get("subclasstype") is not None:
                model_subclasstype = int(kwargs.get("subclasstype"))

            if kwargs.get("description") is not None:
                model_description = kwargs.get("description")
            else:
                model_description = model_name

        obj_model = add_object_model_helper(0, model_name, model_classtype,
                        model_description, model_classname, model_subclasstype)

        if obj_model:
            response = "Created object model {}(ID={}) for model_classtype {}:{} and model_classname {}".format(
                obj_model.model, obj_model.id, model_classtype, model_subclasstype, model_classname)

            print(response)
            return obj_model

        else:

            print ("Could not create object model {}".format(model_name))
            return None


    def delete_model(self, model, force = False):

        model_id = 0

        # FIRST get the model_id
        if model:
            model_id = self.__get_model_id(model)

        if model_id is None or model_id<=0:
            print("Could not find a model that matches passed value.")
            return False

        # assume we will delete the model
        delete_model = True

        # Next, are there any objects using this model?
        obj_count = Object.query.filter_by(model_id=model_id).count()

        if not force and (obj_count is not None and obj_count>0):
            print ('Deleting this model will also delete the following objects:')
            confirm = input("CANNOT BE UNDONE: Are you sure you wish to delete this model? (Y/N)")
            if not confirm == 'Y':
                delete_model = False
                print ("Not deleting model ID={}".format(model_id))

        if delete_model:
            api.delete_model_by_id(model_id)
            print ("Deleted Model with ID={}".format(model_id))
            return True
        else:
            return False

    def create_object(self, *pargs, **kwargs):

        if pargs is not None and len(pargs)==1 and len(kwargs) == 0:
            # create unique object named PARGS
            object_name = pargs[0]
            object_model = 0
            object_ip = None
            object_mac = None
        else:

            # Get the object name
            object_name = kwargs.get("name")

            if object_name is None:
                object_name = kwargs.get("id")

            if object_name is None and pargs is not None:
                # use pargs for the name?
                object_name = pargs[0]

            object_model = kwargs.get("model")

            # get OBJECT IP, if provided
            object_ip = kwargs.get("ip")

            if object_ip is None:
                object_ip = kwargs.get("ip_address")
            if object_ip is None:
                object_ip = kwargs.get("ipaddress")


            object_mac = kwargs.get("mac")
            if object_mac is None:
                object_mac = kwargs.get("mac_address")
            if object_mac is None:
                object_mac = kwargs.get("macaddress")

        return self._create_object(object_model, object_name, object_ip, object_mac)

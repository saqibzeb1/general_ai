# -----------------------------------------------
# Importing required dependencies
# -----------------------------------------------
import weaviate
from weaviate.classes.query import Filter
import config as cfg

# Importing api_entities
import app.api.api_entities as api_entities

# -----------------------------------------------
# Weaviate Connection Manager 
# -----------------------------------------------
class WeaviateConnectionManager:
    """
    Context manager for handling the connection to Weaviate.

    This class establishes a connection to the Weaviate instance using the provided 
    configuration parameters and ensures that the connection is properly closed after use.

    Attributes:
        cluster_url (str): The URL of the Weaviate instance.
        api_key (str): The API key for authenticating with Weaviate.
        llm_key_header (str): The LLM key name for integration e.g. 'X-OpenAI-Api-Key' or 'X-Palm-Api-Key'
        llm_key_value (str): The LLM key value (hash code) for integration.
        client (weaviate.Client): The Weaviate client object.

    Usage:
        weaviate_configs = {
            "api_url": "your_cluster_url",
            "api_key": "your_api_key",
            "llm_key_header": "your_llm_key_header",
            "llm_key_value": "your_llm_key_value"
        }
        
        with WeaviateConnectionManager(weaviate_configs) as client:
            # Perform operations with the client
    """
    
    def __init__(self, weaviate_configs):
        self.cluster_url = weaviate_configs["api_url"]
        self.api_key = weaviate_configs["api_key"].replace('Bearer ', '')
        self.llm_key_header = weaviate_configs["llm_key_header"]
        self.llm_key_value = weaviate_configs["llm_key_value"]
        self.client = None

    def __enter__(self):
        self.client = weaviate.connect_to_weaviate_cloud(
            cluster_url=self.cluster_url,
            auth_credentials=weaviate.auth.AuthApiKey(self.api_key),
            headers={self.llm_key_header: self.llm_key_value}
        )
        
        return self.client

    def __exit__(self, exc_type, exc_value, traceback):
        if self.client:
            self.client.close()

# ------------------------------------------------------------------------------------
# Weaviate methods
# - We will be using context manager as it will close the connection itself
# ------------------------------------------------------------------------------------
# Get All objects from Class or Collection
def getObjectsOfCollection(weaviate_configs, class_name):
    """
    Retrieve all objects from a specified class or collection in Weaviate.

    Args:
        weaviate_configs (dict): Configuration dictionary containing Weaviate connection parameters.
        class_name (str): The name of the class or collection.

    Returns:
        tuple: A message indicating the status and a list of objects in the specified class.

    Example:
        message, objects = getObjectsOfCollection(weaviate_configs, "MyClass")
    """

    objects_in_collection = []
    try:
        # Using Content manager to initiate the client as it will close the connection automatically
        with WeaviateConnectionManager(weaviate_configs) as client:
            
            collection = client.collections.get(class_name)
            
            objects_in_collection = [{'item': object.properties, 
                                    'vector': object.vector} for object in collection.iterator(include_vector=False )]
            
            message = api_entities.CLASS_FOUND.format(class_name)
            
            return message, objects_in_collection

    except Exception as ex:
        raise
# Create data object in Class or Collection
def createObject(weaviate_configs, class_name, object_data):
    """
    Create a data object in a specified class or collection in Weaviate.

    Args:
        weaviate_configs (dict): Configuration dictionary containing Weaviate connection parameters.
        class_name (str): The name of the class or collection.
        object_data (dict): The data to be inserted as an object.

    Returns:
        tuple: A message indicating the status and the UUID of the created object.

    Example:
        message, uuid = createObject(weaviate_configs, "MyClass", {"brief_id": "1"})
    """
    
    try:
        # Using Content manager to initiate the client as it will close the connection automatically
        with WeaviateConnectionManager(weaviate_configs) as client:
         
            collection = client.collections.get(class_name)
            uuid = collection.data.insert( properties=object_data )
            
            message = api_entities.DATA_SAVED_MESSAGE.format(class_name)
            
            return message, uuid

    except Exception as ex:
        raise
    
# Update data object in Class or Collection
def updateObject(weaviate_configs, class_name, object_uuid, object_data):
    """
    Update a data object in a specified class or collection in Weaviate.

    Args:
        weaviate_configs (dict): Configuration dictionary containing Weaviate connection parameters.
        class_name (str): The name of the class or collection.
        object_uuid (str): The UUID of the object to be updated.
        object_data (dict): The new data to update the object with.

    Returns:
        tuple: A message indicating the status and the UUID of the updated object.

    Example:
        message, uuid = updateObject(weaviate_configs, "MyClass", "uuid-string", {"brief_id": "1"})
    """
    
    try:
        # Using Content manager to initiate the client as it will close the connection automatically
        with WeaviateConnectionManager(weaviate_configs) as client:
            
            collection = client.collections.get(class_name)
            # uuid=object_uuid,
            collection.data.update(
                    uuid=object_uuid,
                    properties=object_data,
                )
            
            message = api_entities.DATA_UPDATED_MESSAGE.format(class_name)
            
            return message

    except Exception as ex:
        raise

# Delete data object in Class or Collection
def deleteObject(weaviate_configs, class_name, object_uuid):
    """
    Delete a data object in a specified class or collection in Weaviate.

    Args:
        weaviate_configs (dict): Configuration dictionary containing Weaviate connection parameters.
        class_name (str): The name of the class or collection.
        object_uuid (str): The UUID of the object to be deleted.

    Returns:
        tuple: A message indicating the status and the UUID of the deleted object.

    Example:
        message, uuid = deleteObject(weaviate_configs, "MyClass", "uuid-string")
    """
        
    try:
        # Using Content manager to initiate the client as it will close the connection automatically
        with WeaviateConnectionManager(weaviate_configs) as client:
            
            collection = client.collections.get(class_name)
            collection.data.delete_by_id(
                    object_uuid
                )
            
            message = api_entities.DATA_DELETED_MESSAGE.format(class_name)
            
            return message

    except Exception as ex:
        raise
    
# Get data object UUID in Class or Collection
def getObjectUUID(weaviate_configs, class_name, field_name, field_value):
    """
    Retrieve the UUID of a data object in a specified class or collection in Weaviate,
    based on a specified field and its value.

    Args:
        weaviate_configs (dict): Configuration dictionary containing Weaviate connection parameters.
        class_name (str): The name of the class or collection.
        field_name (str): The name of the field to search for.
        field_value (str): The value of the field to search for.

    Returns:
        str: The UUID of the matching object, or an empty string if no match is found.

    Example:
        uuid = getObjectUUID(weaviate_configs, "MyClass", "brief_id", "1")
    """
        
    try:
        # Using Content manager to initiate the client as it will close the connection automatically
        with WeaviateConnectionManager(weaviate_configs) as client:
            object_uuid = ""

            collection = client.collections.get(class_name)
            response = collection.query.near_text(
                query=field_value,
                filters=Filter.by_property(field_name).equal(field_value),
                limit=1,
            )

            if response.objects:
                 object_uuid = response.objects[0].uuid.urn.removeprefix('urn:uuid:')

            
            return object_uuid

    except Exception as ex:
        raise
    
# Create Batch Objects in Class or Collection
def createBatchObjects (weaviate_configs, class_name, data_rows):
    """
    Create multiple data objects in a specified class or collection in Weaviate using batch processing.

    Args:
        weaviate_configs (dict): Configuration dictionary containing Weaviate connection parameters.
        class_name (str): The name of the class or collection.
        data_rows (list): A list of dictionaries, where each dictionary represents data for one object.

    Returns:
        str: A message indicating the status of the operation.

    Example:
        message = createBatchObjects(weaviate_configs, "MyClass", [{"brief_id": "1"}, {"brief_id": "2"}])
    """
        
    try:
        # Using Content manager to initiate the client as it will close the connection automatically
        with WeaviateConnectionManager(weaviate_configs) as client:
            
            collection = client.collections.get(class_name)
            with collection.batch.dynamic() as batch:
                for data_row in data_rows:
                    batch.add_object(
                        properties=data_row,
                    )
            
            message = api_entities.ALL_DATA_SAVED_MESSAGE.format(class_name)
            
            return message

    except Exception as ex:
        raise

# Validate JSON against specified keys   
def validate_json(data, keys, is_update=False):
    """
    Validate JSON data against specified keys for creating or updating an object.

    Args:
        data (dict): JSON data to validate.
        keys (list): List of keys that are required in the JSON data.
        is_update (bool, optional): Flag indicating if the validation is for an update operation. Defaults to False.

    Returns:
        bool: True if the JSON data is valid against specified keys, False otherwise.

    Notes:
        - For creation (is_update=False), all specified keys must be present as non-empty strings.
        - For update (is_update=True), at least one of the specified keys must be present.

    Example:
        data = {
            "brief_id": "123",
            "brief_type": "type",
            "brief_name": "name",
            "brief_content": "content",
            "brief_status": "active"
        }
        required_keys = ["brief_id", "brief_type", "brief_name", "brief_content", "brief_status"]
        is_valid = validate_json(data, required_keys)  # Returns True
    """    
    
    if is_update:
        if not any(key in data for key in keys):
            return False
    else:
        if not all(key in data and isinstance(data[key], str) and data[key].strip() for key in keys):
            return False
    
    return True 

# Search data with given text in Class or Collection
def searchWithText(weaviate_configs, class_name, search_question, limit, return_fields, filter_property, auto_limit):
    """
    Searches data within a specified class or collection using the given search text.

    Args:
        weaviate_configs (dict): Configuration dictionary containing Weaviate connection parameters.
        class_name (str): The name of the class or collection to search within.
        search_question (str): The text to search for within the class or collection.
        limit (int): The maximum number of results to return.
        return_fields (str): A comma-separated string of fields to include in the returned results.
        "filter_property" e-g "brief_id" (For applying filters to inlclude or exclude particular results).
        auto_limit (int): For allowing the number of closely related groups.
    Returns:
        list: A list of dictionaries containing the properties of the matched objects. If `return_fields` is specified, 
              only those fields will be included; otherwise, all properties are included.
        str: An error message if an exception occurs.

    Example:
        weaviate_configs = {
            "api_url": "your_cluster_url",
            "api_key": "your_api_key",
            "openai_api_key": "your_openai_api_key"
        }
        class_name = "Article"
        search_question = "machine learning"
        limit = 5
        return_fields = "title,summary,author"
        filter_property = "brief_id"
        results = searchWithText(weaviate_configs, class_name, search_question, limit, return_fields, filter_property)
        # Returns a list of dictionaries with the specified fields for each matched object.
    """
        
    try:
        # Using Content manager to initiate the client as it will close the connection automatically
        with WeaviateConnectionManager(weaviate_configs) as client:
            
            collection = client.collections.get(class_name)
            filters = Filter.by_property(filter_property).not_equal("OBJ_TEMP") if filter_property else None #filter temporary objects from search results
            response = collection.query.near_text(
                query=search_question,
                limit=limit,
                auto_limit=auto_limit,
                filters=filters
            )
            return getResponseData(response.objects, return_fields)

    except Exception as ex:
        raise
    
# Search near/similar objects with given uuid in Class or Collection
def searchWithNearObject(weaviate_configs, class_name, uuid, limit, return_fields, filter_property):
    """
    Searches for objects similar to a specified object within a given class or collection using the object's UUID.

    Args:
        weaviate_configs (dict): Configuration dictionary containing Weaviate connection parameters.
        class_name (str): The name of the class or collection to search within.
        uuid (str): The UUID of the object to find similar objects.
        limit (int): The maximum number of similar results to return.
        return_fields (str): A comma-separated string of fields to include in the returned results.
        "filter_property" e-g "brief_id" (For applying filters to inlclude or exclude particular results).

    Returns:
        tuple: A list of dictionaries containing the properties of the matched objects. If `return_fields` is specified, 
               only those fields will be included; otherwise, all properties are included.
        str: An error message if an exception occurs.

    Example:
        weaviate_configs = {
            "api_url": "your_cluster_url",
            "api_key": "your_api_key",
            "openai_api_key": "your_openai_api_key"
        }
        class_name = "Article"
        uuid = "123e4567-e89b-12d3-a456-426614174000"
        limit = 5
        return_fields = "title,summary,author"
        filter_property = "brief_id"
        results = searchWithNearObject(weaviate_configs, class_name, uuid, limit, return_fields, filter_property)
        # Returns a list of dictionaries with the specified fields for each matched object.
    """
        
    try:
        # Using Content manager to initiate the client as it will close the connection automatically
        with WeaviateConnectionManager(weaviate_configs) as client:
            filters = Filter.by_property(filter_property).not_equal("OBJ_TEMP") if filter_property else None #filter temporary objects from similar objects results
            collection = client.collections.get(class_name)
            response = collection.query.near_object(
                near_object=uuid,
                limit=limit,
                filters=filters
            )
            return getResponseData(response.objects, return_fields)

    except Exception as ex:
        raise
    
# Search objects with given graphQL raw query in Class or Collection
def getResponseFromRawQuery(weaviate_configs, class_name, query):
    """
    Executes a raw GraphQL query to retrieve data from a specified class or collection in Weaviate.

    Args:
        weaviate_configs (dict): Configuration dictionary containing Weaviate connection parameters.
        class_name (str): The name of the class or collection to query.
        query (str): The raw GraphQL query string to execute.

    Returns:
        tuple: A list of dictionaries containing the query results, and a string with an error message if an exception occurs.

    Example:
        query = '''
            {
                Get {
                    BriefsIndex_100_test(
                        limit: 2
                        nearObject: { id: "c7803f66-9c76-4081-bba0-77c679c4fa61" }
                        where: { operator: NotEqual, valueText: "20", path: "brief_id" }
                    ) {
                        brief_id, brief_name, brief_type
                    }
                }
            }
        '''
        results, error = getResponseFromRawQuery(weaviate_configs, "BriefsIndex_100_test", query)
        # Returns a list of dictionaries with the specified fields for each matched object, and an error message if any.
    """
        
    try:
        # Using Content manager to initiate the client as it will close the connection automatically
        with WeaviateConnectionManager(weaviate_configs) as client:
            return_data = []
     
            query = """{}""".format(query)
            response = client.graphql_raw_query(query)
            
            # Check for GraphQL internal errors in the response and handle exception for them
            if response.errors:
                raise Exception(f"GraphQL Error: {response.errors}")
            
            if len(response.get[class_name]) > 0:
                return_data = response.get[class_name]
                
            return return_data 

    except Exception as ex:
        raise
    
def getResponseData (data_objects, return_fields):
    """
    Processes a list of data objects and filters their properties based on specified return fields.

    Args:
        data_objects (list): A list of objects, each containing a 'properties' attribute which is a dictionary of key-value pairs.
        return_fields (str): A comma-separated string of fields to include in the returned results.

    Returns:
        list: A list of dictionaries containing the filtered properties of each object. If `return_fields` is specified,
        only those fields are included; otherwise, all properties are included.

    Example:
        data_objects = [
            {"properties": {"field1": "value1", "field2": "value2", "field3": "value3"}},
            {"properties": {"field1": "value4", "field2": "value5", "field3": "value6"}}
        ]
        return_fields = "field1,field3"
        results = getResponseData(data_objects, return_fields)
        # Returns:
        # [
        #     {"field1": "value1", "field3": "value3"},
        #     {"field1": "value4", "field3": "value6"}
        # ]

    """
    
    return_data = []
    if data_objects:
        if return_fields:
            selected_columns = [field.strip() for field in return_fields.split(',')]
            for obj in data_objects:
                filtered_properties = {key: obj.properties[key] for key in selected_columns if key in obj.properties}
                return_data.append(filtered_properties)
        else:    
            return_data = [object.properties for object in  data_objects]
    
    return return_data

def validateWeaviateConfigs (weaviate_configs):
    """
    Validates the Weaviate configuration dictionary to ensure it contains all required keys with non-empty values.

    Args:
        weaviate_configs (dict): Configuration dictionary containing Weaviate connection parameters.

    Returns:
        bool: True if all required configuration keys are present and non-empty; False otherwise.
    """    
    return (weaviate_configs and weaviate_configs["api_url"] and weaviate_configs["api_key"] and weaviate_configs["llm_key_header"]  and weaviate_configs["llm_key_value"])

# Create a child object in Class or Collection and update it's cross-reference property
def addUpdateChildObject(weaviate_configs, class_name_parent, class_name_child, uuid_parent, parent_id, parent_id_field, cross_reference_field, object_data, child_uuid):
	"""
	Endpoint to add / update a child object 

	JSON Payload:
		{
			"class_name_parent": "collection A",  # The name of the class or collection of parent object
			"class_name_child": "collection B",   # The name of the class or collection of child object
			"uuid_parent" : "4a242d70-2f67-4983-8860-3c64cf8b33b0" # The uuid of parent object
			"parent_id" : 123 # OMG ID of parent object
			"parent_id_field" : 'brief_id' # ID field of parent object for finding parent object on weaviate if required
			"cross_reference_field" 'brief_parent' # Name of cross-reference field in child object
			"data": {		# child object data
				"field1": "value1",
				"field2": "value2",
				...
			},
			"weaviate_configs": Config object for connection
		}

	Returns:
		tuple: A JSON response with:
			- status (str): Indicates the success or failure of the operation.
			- message (str): A message about the result of the creation process.
	"""

	try:
		# Using Content manager to initiate the client as it will close the connection automatically
		with WeaviateConnectionManager(weaviate_configs) as client:
			collection = client.collections.get(class_name_child)
			uuid = child_uuid
			if child_uuid:
				collection.data.update(
					uuid=child_uuid,
					properties=object_data,
				)
			else:
				uuid = collection.data.insert( properties=object_data)

				# Update cross reference for newly created object
				if uuid:
					UpdateObjectCrossReference(weaviate_configs, class_name_child, uuid, class_name_parent, uuid_parent, parent_id_field, parent_id, cross_reference_field) 
			message = api_entities.DATA_SAVED_MESSAGE.format(class_name_child)
			return message, uuid

	except Exception as ex:
		raise

from enum import Enum
import os
from dotenv import load_dotenv
load_dotenv()

class GroupID(Enum):
    TESTING = os.getenv("SOME_TEST_GROUP")
   
    
    @staticmethod
    def nameValuePairMap():
        return {group.name.replace('_', ' ').title(): group.value for group in GroupID}
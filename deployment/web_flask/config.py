import os

class Config:
    RUN_ID = os.environ.get('RUN_ID', 'default_run_id_value')
    MODEL_URI = os.environ.get('MODEL_URI')
    PORT = int(os.environ.get('PORT', 9696))

    
    @classmethod
    def get_run_id(cls):
        return cls.RUN_ID



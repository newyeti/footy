import os
from app.core.tools.hydra import load_app_config
from app.entrypoints.cmd.main import get_message_service
from app.entrypoints.cmd.client.switch import Switch
import os.path

def test_main():
    current_directory =  os.path.abspath(os.path.dirname(__file__))
    data_directory = os.path.abspath(os.path.join(current_directory, "../../../data/2022"))
    app_config = load_app_config(f"{current_directory}/config", "app")
    message_service = get_message_service(app_config=app_config)
    switch = Switch(message_service=message_service, service_config=app_config.service)
    switch.execute("teams", 2022, data_directory)
    
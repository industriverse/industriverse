import pytest
from src.scf.integrations.industrial.modbus_bridge import ModbusBridge
from src.scf.integrations.industrial.mqtt_client import MQTTClient

def test_modbus_mock():
    bridge = ModbusBridge(host="localhost", mock_mode=True)
    assert bridge.connect() == True
    
    # Write
    bridge.write_register(40001, 123)
    
    # Read
    values = bridge.read_holding_registers(40001, 1)
    assert values[0] == 123
    
    bridge.close()

def test_mqtt_mock():
    client = MQTTClient(broker="localhost")
    client.connect()
    assert client.connected == True
    
    # Publish (Should print to stdout, no error)
    client.publish("telemetry/energy", {"kwh": 10.5})
    
    client.disconnect()
    assert client.connected == False

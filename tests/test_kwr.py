from korad import kwr
import pytest
import time


host_ip = "192.168.1.1"
device_ip = "192.168.1.198"
port = 18190

@pytest.fixture
def device():
    """Fixture to create and return a connected device, and clean up after test"""
    dev = kwr.kwr(host_ip, device_ip, port)
    yield dev
    dev.endComm()

# Basic device information
def test_device_info(device):
    """Test getting device information"""
    info = device.deviceInfo()
    assert info is not None
    assert isinstance(info, str)
    assert len(info) > 0

def test_check_device(device):
    """Test device check function"""
    result = device.checkDevice()
    assert result is True

def test_mac_address(device):
    """Test getting MAC address"""
    mac = device.macAddress()
    assert mac is not None
    assert isinstance(mac, str)
    assert len(mac) > 0
    # Verify MAC format (XX:XX:XX:XX:XX:XX)
    assert len(mac.split(':')) == 6 or len(mac.replace('-', ':').split(':')) == 6

# Network settings tests
def test_network_settings_getters(device):
    """Test getting network settings (read-only test)"""
    ip = device.ipAddress()
    assert isinstance(ip, str)
    assert len(ip.split('.')) == 4
    
    netmask = device.netmask()
    assert isinstance(netmask, str)
    assert len(netmask.split('.')) == 4
    
    gateway = device.gateway()
    assert isinstance(gateway, str)
    assert len(gateway.split('.')) == 4
    
    port_num = device.port()
    assert isinstance(port_num, int)

# WARNING: The following tests modify network settings and are commented out
# because they can disconnect the device and require manual reconnection.
# Uncomment only if you're prepared to manually reconfigure the device.
"""
def test_dhcp(device):
    # Save original state
    original_state = device.dhcp()
    
    # Test setting to opposite state
    device.setDhcp(not original_state)
    assert device.dhcp() == (not original_state)
    
    # Restore original state
    device.setDhcp(original_state)
    assert device.dhcp() == original_state

def test_set_ip_address(device):
    # Save original IP
    original_ip = device.ipAddress()
    # Test by setting to the same IP (no change but tests the command)
    device.setIpAddress(original_ip)
    
def test_set_netmask(device):
    original_netmask = device.netmask()
    device.setNetmask(original_netmask)
    
def test_set_gateway(device):
    original_gateway = device.gateway()
    device.setGateway(original_gateway)
    
def test_set_port(device):
    original_port = device.port()
    # Don't actually change to avoid disconnection
    # device.setPort(original_port)
"""

# Baud rate tests
def test_baud_rate(device):
    """Test getting and setting baud rate"""
    # Save original value
    original_baud = device.baudRate()
    assert isinstance(original_baud, int)
    
    # Test setting to same value (no change but tests the command)
    device.setBaudRate(original_baud)
    assert device.baudRate() == original_baud
    
    # Test setting to different value if desired (commented out)
    new_baud = 115200 if original_baud != 115200 else 9600
    device.setBaudRate(new_baud)
    assert device.baudRate() == new_baud

    # Restore original
    device.setBaudRate(original_baud)
    assert device.baudRate() == original_baud

# Voltage control tests
def test_voltage_measurement(device):
    """Test measuring voltage"""
    voltage = device.measureVoltage()
    assert isinstance(voltage, float)
    assert voltage >= 0

def test_set_voltage(device):
    """Test setting voltage"""
    # Save original value
    original_voltage = device.getSetVoltage()
    
    # Test setting to new value
    test_voltage = 1.234  # Safe low test value
    device.setVoltage(test_voltage)
    assert device.getSetVoltage() == test_voltage
    
    # Restore original
    device.setVoltage(original_voltage)
    assert device.getSetVoltage() == original_voltage

# Current control tests
def test_current_measurement(device):
    """Test measuring current"""
    current = device.measureCurrent()
    assert isinstance(current, float)
    assert current >= 0

def test_set_current(device):
    """Test setting current"""
    # Save original value
    original_current = device.getSetCurrent()
    
    # Test setting to new value
    test_current = 0.123  # Safe low test value
    device.setCurrent(test_current)
    assert device.getSetCurrent() == test_current
    
    # Restore original
    device.setCurrent(original_current)
    assert device.getSetCurrent() == original_current

# OCP tests
def test_ocp_status(device):
    """Test OCP status"""
    # Note that it is not possible to set OCP status on the KWR103, only read it
    status = device.ocpEnabled()
    assert isinstance(status, bool)

def test_ocp_current(device):
    """Test getting and setting OCP current"""
    
    # Test setting OCP current
    original_current = device.ocpCurrent()
    
    # Choose a test value
    test_current = 0.5 if original_current != 0.5 else 1.0
    device.setOcpCurrent(test_current)
    assert device.ocpCurrent() == test_current
    
    # Restore original
    device.setOcpCurrent(original_current)
    assert device.ocpCurrent() == original_current

# OVP tests
def test_ovp_status(device):
    """Test OVP status"""
    # Note that it is not possible to set OVP status on the KWR103, only read it
    status = device.ovpEnabled()
    assert isinstance(status, bool)

def test_ovp_voltage(device):
    """Test getting and setting OVP voltage"""
    
    # Test setting OVP voltage
    original_voltage = device.ovpVoltage()
    assert isinstance(original_voltage, float)
    
    # Choose a test value
    test_voltage = 12.0 if original_voltage != 12.0 else 15.0
    device.setOvpVoltage(test_voltage)
    assert device.ovpVoltage() == test_voltage
    
    # Restore original
    device.setOvpVoltage(original_voltage)
    assert device.ovpVoltage() == original_voltage

# Output control tests
def test_output_control(device):
    """Test getting and setting output state"""
    # Get original state
    original_state = device.outputEnabled()
    
    # Set and verify OFF
    device.setOutputEnable(False)
    assert device.outputEnabled() == False
    
    # Set and verify ON
    device.setOutputEnable(True)
    assert device.outputEnabled() == True
    
    # Restore original
    device.setOutputEnable(original_state)
    assert device.outputEnabled() == original_state

# Beep control tests
def test_beep_control(device):
    """Test getting and setting beep state"""
    # Get original state
    original_state = device.beepEnable()
    
    # Set to opposite state
    device.setBeepEnabled(not original_state)
    # Wait a moment for setting to apply
    time.sleep(0.1)
    assert device.beepEnable() == (not original_state)
    
    # Restore original
    device.setBeepEnabled(original_state)
    # Wait a moment for setting to apply
    time.sleep(0.1)
    assert device.beepEnable() == original_state

# Button lock tests
def test_button_lock(device):
    """Test getting and setting button lock state"""
    # Get original state
    original_state = device.lockButtons()
    
    # Set to opposite state
    device.setLockButtons(not original_state)
    # Wait a moment for setting to apply
    time.sleep(0.1)
    assert device.lockButtons() == (not original_state)
    
    # Restore original
    device.setLockButtons(original_state)
    # Wait a moment for setting to apply
    time.sleep(0.1)
    assert device.lockButtons() == original_state

# Slope tests
def test_voltage_slope(device):
    """Test getting and setting voltage slope"""
    # Get original slope
    original_slope = device.vSlope()
    
    # Set to a test value
    test_slope = 10
    device.setVSlope(test_slope)
    assert device.vSlope() == test_slope
    
    # Restore original
    device.setVSlope(original_slope)

def test_current_slope(device):
    """Test getting and setting current slope"""
    # Get original slope
    original_slope = device.iSlope()
    
    # Set to a test value
    test_slope = 20
    device.setISlope(test_slope)
    assert device.iSlope() == test_slope
    
    # Restore original
    device.setISlope(original_slope)
    assert device.iSlope() == original_slope

# Remote compensation tests
def test_remote_compensation(device):
    """Test getting and setting remote compensation"""
    # Get original state
    original_state = device.remoteCompensationEnabled()
    
    # Set to opposite state
    device.setRemoteCompensationEnabled(not original_state)
    assert device.remoteCompensationEnabled() == (not original_state)
    
    # Restore original
    device.setRemoteCompensationEnabled(original_state)
    assert device.remoteCompensationEnabled() == original_state

# Priority tests
def test_priority(device):
    """Test getting and setting priority mode"""
    # Get original state
    original_priority = device.priority()
    
    # Set to opposite priority
    new_priority = "v" if original_priority == "c" else "c"
    device.setPriority(new_priority)
    assert device.priority() == new_priority
    
    # Restore original
    device.setPriority(original_priority)
    assert device.priority() == original_priority

# Memory tests
def test_memory_save_recall(device):
    """Test saving and recalling from memory"""
    # Let's use memory slot 5 for testing
    memory_slot = 5
    
    # Save current settings
    original_voltage = device.getSetVoltage()
    original_current = device.getSetCurrent()
    
    # Change settings
    new_voltage = 1.5 if original_voltage != 1.5 else 2.0
    new_current = 0.1 if original_current != 0.1 else 0.2
    
    device.setVoltage(new_voltage)
    device.setCurrent(new_current)
    
    # Save to memory
    device.saveMemory(memory_slot)
    
    # Restore original settings
    device.setVoltage(original_voltage)
    device.setCurrent(original_current)
    
    # Make sure settings are back to original
    assert device.getSetVoltage() == original_voltage
    assert device.getSetCurrent() == original_current
    
    # Recall from memory
    device.recallMemory(memory_slot)
    
    # Verify recalled settings
    assert device.getSetVoltage() == new_voltage
    assert device.getSetCurrent() == new_current
    
    # Restore original settings
    device.setVoltage(original_voltage)
    device.setCurrent(original_current)

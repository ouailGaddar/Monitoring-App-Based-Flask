from pysnmp.hlapi import *

community = 'public'
memory_size = '.1.3.6.1.2.1.25.2.3.1.5.1'
memory_used = '.1.3.6.1.2.1.25.2.3.1.6.1'
cpu_load_oid_base = '.1.3.6.1.2.1.25.3.3.1.2'

def get(host, oid):
    error_indication, error_status, error_index, var_bind = next(
        getCmd(SnmpEngine(),
               CommunityData(community),
               UdpTransportTarget((host, 161)),
               ContextData(),
               ObjectType(ObjectIdentity(oid))
               )
    )
    if error_indication:
        return f'Error indication: {error_indication}'
    elif error_status:
        return f'Error status: {error_status}'
    elif error_index:
        return f'Error index: {error_index}'
    return f'{var_bind[0][1]}'

def get_cpu_load(host):
    cpu_load_values = []

    for (errorIndication, errorStatus, errorIndex, varBinds) in nextCmd(
            SnmpEngine(),
            CommunityData(community),
            UdpTransportTarget((host, 161)),
            ContextData(),
            ObjectType(ObjectIdentity(cpu_load_oid_base)),
            lexicographicMode=False,
    ):
        if errorIndication:
            return f'Error indication: {errorIndication}'
        elif errorStatus:
            return f'Error status: {errorStatus} at {errorIndex}'

        for varBind in varBinds:
            oid, value = varBind
            # Convert OID to string and then split
            process_number = str(oid).split('.')[-1]
            cpu_load_values.append({'Process Number': process_number, 'CPU Load': value.prettyPrint()})

    return cpu_load_values

def getSystemInfo(host):
    return (
        get(host, memory_size),
        get(host, memory_used),
        get_cpu_load(host)
    )

if __name__ == '__main__':
    host_ip = '127.0.0.1'  # Replace with your desired SNMP host IP
    print(getSystemInfo(host_ip))


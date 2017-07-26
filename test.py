import serial
import time
from time import localtime, strftime

class Commands(object):
    def TERMINATOR(self):
        return b'\x0A'

    def PING(self):
        return b'ping' + self.TERMINATOR()

    def EPS_ENABLE_LCL(self, lcl_id):
        return b'eps enable_lcl ' + str(lcl_id) + self.TERMINATOR()
        
    def EPS_DISABLE_LCL(self, lcl_id):
        return b'eps disable_lcl ' + str(lcl_id) + self.TERMINATOR()

    def PAYLOAD_WHO(self):
        return b'payload who' + self.TERMINATOR()
        
    def GYRO_INIT(self):
        return b'gyro init' + self.TERMINATOR()
    
    def GYRO_READ(self):
        return b'gyro read' + self.TERMINATOR()
        
    def RTC_DURATION(self):
        return b'rtc duration' + self.TERMINATOR()
        
class Communication(object):
    def connect(self, port, baud):
        self.ser = serial.Serial(port, baud)
        
    def disconnect(self):
        self.ser.close()
    
    def send_command(self, command):
        self.clear_buffers()
        self.ser.write(command)
        
    def read_buffer(self):
        return self.ser.readline()
        
    def received_bytes(self):
        return self.ser.in_waiting
    
    def clear_buffers(self):
        self.ser.reset_input_buffer()
        self.ser.reset_output_buffer()

class PLD(object):
    def __init__(self, port, baud):
        self.communication = Communication()
        self.communication.connect(port, baud)
        
    def log_clear_buffer(self):
        self.communication.clear_buffers()
    
    def log_get_buffer(self):
        log_list = []
        while self.communication.received_bytes()>1:
            log_list.append(self.communication.read_buffer())
        
        log_record = " | ".join(log_list)
        log_record = log_record.replace("\n", "")
        log_record = log_record.replace("\r", "")
        
        self.log_clear_buffer()
        
        return log_record

class OBC(object):
    def __init__(self, port, baud, log):
        self.commands = Commands()
        self.communication = Communication()
        self.log = log
        self.communication.connect(port, baud)
    
    def COMMAND_SLEEP(self):
        return 0.1
    
    def disconnect(self):
        self.communication.disconnect()
        
    def ping(self):
        self.communication.send_command(self.commands.PING())
        time.sleep(self.COMMAND_SLEEP())
        if self.communication.read_buffer()=="pong\n":
            return True
        return False
        
    def eps_enable_lcl(self, lcl_id):
        self.communication.send_command(self.commands.EPS_ENABLE_LCL(lcl_id))
        time.sleep(self.COMMAND_SLEEP())
        if self.communication.read_buffer()=="0\n":
            return True
        return False
        
    def eps_disable_lcl(self, lcl_id):
        self.communication.send_command(self.commands.EPS_DISABLE_LCL(lcl_id))
        time.sleep(self.COMMAND_SLEEP())
        if self.communication.read_buffer()=="0\n":
            return True
        return False

    def payload_who(self, delays):
        self.communication.send_command(self.commands.PAYLOAD_WHO())
        time.sleep(delays)
        
        log_buffer = self.log_get_buffer()
        if not log_buffer=="Starting Whoami Test! | Who Am I: 83 (0x53) | Success!":
            print self.log.error("pld_log\",\"payload_who,\"" + log_buffer + "\"")
            return False
        return True
        
    def gyro_init(self):
        self.communication.send_command(self.commands.GYRO_INIT())
        time.sleep(self.COMMAND_SLEEP())
    
    def gyro_read(self):
        self.communication.send_command(self.commands.GYRO_READ())
        time.sleep(0.5)
        return self.communication.read_buffer()
        
    def rtc_duration(self):
        self.communication.send_command(self.commands.RTC_DURATION())
        time.sleep(0.5)
        return self.communication.read_buffer()
        
    def log_get_buffer(self):
        log_list = []
        while self.communication.received_bytes()>1:
            log_list.append(self.communication.read_buffer())
        
        log_record = " | ".join(log_list)
        log_record = log_record.replace("\n", "")
        log_record = log_record.replace("\r", "")
        
        self.communication.clear_buffers()
        
        return log_record
    
class Tests(object):
    def __init__(self, log):
        self.obc = OBC("COM8", 115200, log)
        self.pld = PLD("COM22", 38400)
        self.eps = PLD("COM20", 38400)
        self.log = log
        
        self.eps.log_clear_buffer()
        self.pld.log_clear_buffer()

    def lcls_enable_all(self):
        for lcl_id in range(1, 6):
            if not self.obc.eps_enable_lcl(lcl_id):
                print self.log.error("Enable LCL: failed, id: " + str(lcl_id))
                
        time.sleep(0.05)
        eps_log = self.eps.log_get_buffer()
        if not eps_log=="[INFO]  Enable LCL: TKmain | [INFO]  Enable LCL: SunS | [INFO]  Enable LCL: CAMnadir | [INFO]  Enable LCL: CAMwing | [INFO]  Enable LCL: SENS":
            print self.log.error("eps_log\",\"lcls_enable_all,\"" + eps_log)

    def lcls_disable_all(self):
        for lcl_id in range(1, 6):
            if not self.obc.eps_disable_lcl(lcl_id):
                print self.log.error("Disable LCL: failed, id: " + str(lcl_id))
        
        time.sleep(0.05)
        eps_log = self.eps.log_get_buffer()
        if not eps_log=="[INFO]  Disable LCL: TKmain | [INFO]  Disable LCL: SunS | [INFO]  Disable LCL: CAMnadir | [INFO]  Disable LCL: CAMwing | [INFO]  Disable LCL: SENS":
            print self.log.error("eps_log\",\"lcls_disable_all,\"" + eps_log)

    def lcls_enable_and_disable_one_by_one(self):
        for lcl_id in range(1, 6):
            if not self.obc.eps_enable_lcl(lcl_id):
                print self.log.error("Enable LCL: failed, id: " + str(lcl_id))
            if not self.obc.eps_disable_lcl(lcl_id):
                print self.log.error("Disable LCL: failed, id: " + str(lcl_id))
        
        time.sleep(0.05)
        eps_log = self.eps.log_get_buffer()
        if not eps_log=="[INFO]  Enable LCL: TKmain | [INFO]  Disable LCL: TKmain | [INFO]  Enable LCL: SunS | [INFO]  Disable LCL: SunS | [INFO]  Enable LCL: CAMnadir | [INFO]  Disable LCL: CAMnadir | [INFO]  Enable LCL: CAMwing | [INFO]  Disable LCL: CAMwing | [INFO]  Enable LCL: SENS | [INFO]  Disable LCL: SENS":
            print self.log.error("eps_log\",\"lcls_enable_and_disable_one_by_one,\"" + eps_log)

    def lcls_enable_wait_disable_one_by_one(self):
        for lcl_id in range(1, 6):
            if not self.obc.eps_enable_lcl(lcl_id):
                print self.log.error("Enable LCL: failed, id: " + str(lcl_id))
            time.sleep(2)
            if not self.obc.eps_disable_lcl(lcl_id):
                print self.log.error("Disable LCL: failed, id: " + str(lcl_id))
                
        time.sleep(0.05)
        eps_log = self.eps.log_get_buffer()
        if not eps_log=="[INFO]  Enable LCL: TKmain | [INFO]  Disable LCL: TKmain | [INFO]  Enable LCL: SunS | [INFO]  Disable LCL: SunS | [INFO]  Enable LCL: CAMnadir | [INFO]  Disable LCL: CAMnadir | [INFO]  Enable LCL: CAMwing | [INFO]  Disable LCL: CAMwing | [INFO]  Enable LCL: SENS | [INFO]  Disable LCL: SENS":
            print self.log.error("eps_log\",\"lcls_enable_wait_disable_one_by_one,\"" + eps_log)

    def payload_enable_who_disable(self, delays):
        self.pld.log_get_buffer()
        self.obc.eps_enable_lcl(5)
        time.sleep(delays)
        
        pld_log = self.pld.log_get_buffer()
        if not pld_log=="[INFO]  Setting memory to 0x8c1 | [INFO]  Enable TWI | [INFO]  PLD Initialised.":
            print self.log.error("pld_log\",payload_enable_who_disable,\"" + pld_log)
        
        output = ""
        
        if not self.obc.payload_who(delays):
            output = "1"
        else:
            output = "0"

        if not self.obc.payload_who(delays):
            output = output + ",1"
        else:
            output = output + ",0"
        
        self.obc.eps_disable_lcl(5)

        eps_log = self.eps.log_get_buffer()
        if not eps_log=="[INFO]  Enable LCL: SENS | [INFO]  Disable LCL: SENS":
            print self.log.error("eps_log\",payload_enable_who_disable,\"" + eps_log)

        return output

    def obc_ping(self):
        if not self.obc.ping():
            print self.log.error("OBC ping failed")
        
    def gyro_init(self):
        self.obc.gyro_init()
        time.sleep(1)
        return "gyro_init"
        
    def gyro_read(self):
        gyro_readout = self.obc.gyro_read().replace("\n","")
        gyro_readout = gyro_readout.replace(" ",",")
        return str(gyro_readout)
        
    def rtc_duration(self):
        duration = self.obc.rtc_duration().replace("\n","")
        duration = duration.replace("\r","")
        return str(duration)

class Log(object):
    def __init__(self):
        self.file_name = self.generate_file_name()
        self.append_record(self.HEADER())

    def append_record(self, record):
        with open(self.file_name, 'a') as f:
            f.write(record)
        f.close()
        return record
        
    def get_timestamp(self):
        timestamp = []
        timestamp.append(strftime("%Y-%m-%d", localtime()))
        timestamp.append(strftime("%H:%M:%S", localtime()))
        return timestamp

    def generate_file_name(self):
        timestamp = []
        timestamp = self.get_timestamp()

        file_name = "TestsLog_"
        file_name += timestamp[0]
        file_name += "_"
        file_name += timestamp[1].replace(":", "-")
        file_name += self.EXPANSION()

        return file_name

    def EXPANSION(self):
        return ".txt"

    def HEADER(self):
        return ""

    def prefix_INFO(self):
        return "[INFO]"

    def prefix_DATA(self):
        return "[DATA]"

    def prefix_ERROR(self):
        return "[ERROR]"
    
    def NEW_LINE(self):
        return "\n"

    def SEPARATOR(self):
        return ","

    def join(self, list):
        return ",".join(list)

    def info(self, info_list):
        info_record = self.prefix_INFO() + self.SEPARATOR()
        info_record += self.join(self.get_timestamp())
        info_record += self.SEPARATOR()
        info_record += self.join(info_list)

        self.append_record(info_record + self.NEW_LINE())

        return info_record

    def data(self, data_list):
        data_record = self.prefix_DATA() + self.SEPARATOR()
        data_record += self.join(self.get_timestamp())
        data_record += self.SEPARATOR()
        data_record += self.join(data_list)

        self.append_record(data_record + self.NEW_LINE())

        return data_record

    def error(self, error_message):
        error_record = self.prefix_ERROR() + self.SEPARATOR()
        error_record += self.join(self.get_timestamp())
        error_record += self.SEPARATOR()
        error_record += "\""+error_message+"\""
        
        self.append_record(error_record + self.NEW_LINE())
        
        return error_record
    
log = Log()
tests = Tests(log)

print "Log file name: " + log.file_name
print log.info(["\""+tests.gyro_init()+"\""])

while True:
    print log.info(["\"tests_started\""])
    tests.lcls_enable_all()
    tests.lcls_disable_all()
    tests.lcls_enable_and_disable_one_by_one()
    tests.lcls_enable_wait_disable_one_by_one()

    time.sleep(1)
    tests.lcls_enable_all()
    time.sleep(10)
    tests.lcls_disable_all()
    time.sleep(1)

    time.sleep(1)
    print log.data(["\"pld_enable_who_disable_results\"",
    "1000",str(tests.payload_enable_who_disable(1)),
    "200",str(tests.payload_enable_who_disable(0.2)),
    "50",str(tests.payload_enable_who_disable(0.05))])
    time.sleep(1)

    print log.data(["\"gyro_read\"",tests.gyro_read()])
    print log.data(["\"rtc_duration\"",tests.rtc_duration()])

    tests.obc_ping()

    time.sleep(1)

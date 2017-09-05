import math
import resistance_sensors as sensor

class ControllerBFormulas:
    @staticmethod
    def lmt87_ref3V0_temperature(adc_readout):
        if adc_readout>1023 or adc_readout<0:
            adc_readout = 1023
        calculated_mv_adc = ((adc_readout/1024.0)*3.0)*1000.0
        return round((((13.582-math.sqrt((-13.582*(-13.582))+4*0.00433*(2230.8-(calculated_mv_adc)))))/(2*(-0.00433)))+30.0, 1)

    @staticmethod
    def batc_voltage(adc_readout):
        if adc_readout>1023 or adc_readout<0:
            adc_readout = 1023
        calculated_v_adc = (adc_readout/1024.0)*3.0
        return round(calculated_v_adc*((470.0+150.0)/(150.0)), 2)
    
    @staticmethod
    def local_3v3d_voltage(adc_readout):
        if adc_readout>1023 or adc_readout<0:
            adc_readout = 1023
        calculated_v_adc = (adc_readout/1024.0)*3.0
        return round(calculated_v_adc*2.0, 2)

    @staticmethod
    def pt1000_temperature(adc_readout):
        if adc_readout>1023 or adc_readout<0:
            adc_readout = 1023
        calculated_v_adc = (adc_readout/1024.0)*3.0
        pt1000_resistance = calculated_v_adc/((3.0-calculated_v_adc)/3320.68)
        print pt1000_resistance
        return round(sensor.pt1000_res_to_temp(pt1000_resistance), 1)
        
    @staticmethod
    def batc_state(readout):
        return readout

    @staticmethod
    def uptime(readout):
        return readout
        
    @staticmethod
    def safety_counter(readout):
        return readout
        
    @staticmethod
    def power_cycle_counter(readout):
        return readout


controller_b_formulas = {'1180: BP.Temperature': ControllerBFormulas.pt1000_temperature,
                      '1190: BATC.VOLT_B': ControllerBFormulas.batc_voltage,
                      '1200: Safety Counter': ControllerBFormulas.safety_counter,
                      '1208: Power Cycle Count': ControllerBFormulas.power_cycle_counter,
                      '1224: Uptime': ControllerBFormulas.uptime,
                      '1256: Temperature': ControllerBFormulas.lmt87_ref3V0_temperature,
                      '1266: SUPP_TEMP': ControllerBFormulas.lmt87_ref3V0_temperature,
                      '1276: Other.Temperature': ControllerBFormulas.local_3v3d_voltage}

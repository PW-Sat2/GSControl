import math

class ControllerAFormulas:
    @staticmethod
    def lmt87_ref3V0_temperature(adc_readout):
        if adc_readout>1023 or adc_readout<0:
            adc_readout = 1023
        calculated_mv_adc = ((adc_readout/1024.0)*3.0)*1000.0
        return round((((13.582-math.sqrt((-13.582*(-13.582))+4*0.00433*(2230.8-(calculated_mv_adc)))))/(2*(-0.00433)))+30.0, 1)

    @staticmethod
    def mppt_lmt87_temperature(adc_readout):
        if adc_readout>4095 or adc_readout<0:
            adc_readout = 4095
        calculated_mv_adc = ((adc_readout/4096.0)*3.3)*1000.0
        return round((((13.582-math.sqrt((-13.582*(-13.582))+4*0.00433*(2230.8-(calculated_mv_adc)))))/(2*(-0.00433)))+30.0, 1)

    @staticmethod
    def mppt_voltage(adc_readout):
        if adc_readout>4095 or adc_readout<0:
            adc_readout = 4095
        calculated_v_adc = (adc_readout/4096.0)*3.3
        return round(calculated_v_adc*((4.7+1.0)/(1.0)), 2)
    
    @staticmethod
    def mppt_current(adc_readout):
        if adc_readout>4095 or adc_readout<0:
            adc_readout = 4095
        calculated_v_adc = (adc_readout/4096.0)*3.3
        return round(calculated_v_adc*(1.0/(0.068*50.0)), 3)
    
    @staticmethod
    def mppt_state(readout):
        return readout
    
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
    def distribution_voltage(adc_readout):
        if adc_readout>1023 or adc_readout<0:
            adc_readout = 1023
        calculated_v_adc = (adc_readout/1024.0)*3.0
        return round(calculated_v_adc*((4.7+2.2)/2.2), 2)
    
    @staticmethod
    def distribution_current(adc_readout):
        if adc_readout>1023 or adc_readout<0:
            adc_readout = 1023
        calculated_v_adc = (adc_readout/1024.0)*3.0
        return round(calculated_v_adc*(1.0/(0.025*50.0)), 3)
 
    @staticmethod
    def batc_state(readout):
        return readout

    @staticmethod
    def lcl_flagb(readout):
        return readout
    
    @staticmethod
    def lcl_state(readout):
        return readout
    
    @staticmethod
    def tmp121_temperature(readout):
        sign = (-1)**(readout >> 12)
        return sign*(readout & 0b111111111111)*2*0.0625
        
    @staticmethod
    def uptime(readout):
        return readout
        
    @staticmethod
    def safety_counter(readout):
        return readout
        
    @staticmethod
    def power_cycle_counter(readout):
        return readout

controller_a_formulas = {'0762: MPPT_X.SOL_VOLT': ControllerAFormulas.mppt_voltage,
                      '0774: MPPT_X.SOL_CURR': ControllerAFormulas.mppt_current,
                      '0786: MPPT_X.SOL_OUT_VOLT': ControllerAFormulas.mppt_voltage,
                      '0798: MPPT_X.Temperature': ControllerAFormulas.mppt_lmt87_temperature,
                      '0810: MPPT_X.State': ControllerAFormulas.mppt_state,
                      '0816: MPPT_Y+.SOL_VOLT': ControllerAFormulas.mppt_voltage,
                      '0828: MPPT_Y+.SOL_CURR': ControllerAFormulas.mppt_current,
                      '0840: MPPT_Y+.SOL_OUT_VOLT': ControllerAFormulas.mppt_voltage,
                      '0852: MPPT_Y+.Temperature': ControllerAFormulas.mppt_lmt87_temperature,
                      '0864: MPPT_Y+.State': ControllerAFormulas.mppt_state,
                      '0870: MPPT_Y-.SOL_VOLT': ControllerAFormulas.mppt_voltage,
                      '0882: MPPT_Y-.SOL_CURR': ControllerAFormulas.mppt_current,
                      '0894: MPPT_Y-.SOL_OUT_VOLT': ControllerAFormulas.mppt_voltage,
                      '0906: MPPT_Y-.Temperature': ControllerAFormulas.mppt_lmt87_temperature,
                      '0918: MPPT_Y-.State': ControllerAFormulas.mppt_state,
                      '0924: DISTR.VOLT_3V3': ControllerAFormulas.distribution_voltage,
                      '0934: DISTR.CURR_3V3': ControllerAFormulas.distribution_current,
                      '0944: DISTR.VOLT_5V': ControllerAFormulas.distribution_voltage,
                      '0954: DISTR.CURR_5V': ControllerAFormulas.distribution_current,
                      '0964: DISTR.VOLT_VBAT': ControllerAFormulas.distribution_voltage,
                      '0974: DISTR.CURR_VBAT': ControllerAFormulas.distribution_current,
                      '0984: DISTR.LCL_STATE': ControllerAFormulas.lcl_state,
                      '0992: DISTR.LCL_FLAGS': ControllerAFormulas.lcl_flagb,
                      '1000: BATC.VOLT_A': ControllerAFormulas.batc_voltage,
                      '1010: BATC.CHRG_CURR': ControllerAFormulas.distribution_current,
                      '1020: BATC.DCHRG_CURR': ControllerAFormulas.distribution_current,
                      '1030: BATC.Temperature': ControllerAFormulas.lmt87_ref3V0_temperature,
                      '1040: BATC.State': ControllerAFormulas.batc_state,
                      '1048: BP.Temperature A': ControllerAFormulas.tmp121_temperature,
                      '1061: BP.Temperature B': ControllerAFormulas.tmp121_temperature,
                      '1074: Safety Counter': ControllerAFormulas.safety_counter,
                      '1082: Power Cycle Count': ControllerAFormulas.power_cycle_counter,
                      '1098: Uptime': ControllerAFormulas.uptime,
                      '1130: Temperature': ControllerAFormulas.lmt87_ref3V0_temperature,
                      '1140: SUPP_TEMP': ControllerAFormulas.lmt87_ref3V0_temperature,
                      '1150: Other.Temperature': ControllerAFormulas.local_3v3d_voltage,
                      '1160: DCDC3V3.Temperature': ControllerAFormulas.lmt87_ref3V0_temperature,
                      '1170: DCDC5V.Temperature': ControllerAFormulas.lmt87_ref3V0_temperature}

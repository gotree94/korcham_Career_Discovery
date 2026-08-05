class omniwheel_database:
    def __init__(self):
        # Odometry data
        self.data_wheel_1_encoder_count = 0
        self.data_wheel_2_encoder_count = 0
        self.data_wheel_3_encoder_count = 0

        # Sensor data
        self.data_Ultrasonic_Sensors = [0,0,0,0,0,0]
        self.data_PSD_Sensor = [0, 0, 0]

        self.data_Switch = [0,0]

        self.data_Flame_Sensor = 0

        self.data_Lux_Sensor = 0
        self.data_Attitude_X = 0
        self.data_Attitude_Y = 0
        self.data_Attitude_Z = 0
        self.data_Pressure   = 0
        self.data_Geomagnetism = 0

        self.data_PIR_Sensor = 0

        self.data_CO2_Gas_Sensor = 0

        self.data_Dust_Sensor = 0

        self.data_Temperature_Sensor = 0

        self.data_Microwave_Motion_Sensor = 0

        self.data_Sound_1_Sensor = 0
        self.data_Sound_2_Sensor = 0
        self.data_Sound_3_Sensor = 0
        self.data_Sound_4_Sensor = 0

        # Drive control data
        self.data_X_Linear_velocity = 0
        self.data_Y_Linear_velocity = 0
        self.data_W_Angular_velocity = 0

        # Module control data
        self.data_LED_output = 0
        self.data_Buzzer_output = 0

        # Battery data
        self.data_Battery = 0

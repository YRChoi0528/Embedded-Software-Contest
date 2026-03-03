import serial

import time



class Robot():



    def __init__(self, serial = None):

        self.serial = serial



    def TX_data(self, one_byte):

        self.serial.write(serial.to_bytes([one_byte]))

        

    '''********************************************'''

    def go_left(self,T = 1.45):

        self.TX_data(1)

        time.sleep(T)

    

    def go_right(self, T =1.45):

        self.TX_data(2)

        time.sleep(T)

    

    def left_walk(self, T =0.3):

        self.TX_data(3)

        time.sleep(T)

    

    def right_walk(self, T =0.3):

        self.TX_data(4)

        time.sleep(T)

        
#
    def walk12(self, T =1.8):

        for i in range(6):

            self.TX_data(1)

            time.sleep(T)

            self.TX_data(2)

            time.sleep(T)

    

    def left_turn(self, T =0.53):

        self.TX_data(5)

        time.sleep(T)



    def right_turn(self, T =0.55):

        self.TX_data(6)

        time.sleep(T)

        

    def left_turn90(self, T =0.7):

        for i in range(0,3):

            self.TX_data(7)

            time.sleep(T)

        self.TX_data(5)

        time.sleep(T)

        self.TX_data(4)

        time.sleep(T)

        #self.TX_data(1)

        #time.sleep(2)

    

    def right_turn90(self, T =0.8):

        for i in range(0,4):

            self.TX_data(8)

            time.sleep(T)

        self.TX_data(6)

        time.sleep(T)

        #self.TX_data(1)

        #time.sleep(2)

        

    def left_turn180(self, T =1):

        for i in range(0,6):

            self.TX_data(7)

            time.sleep(1)

        self.TX_data(5)

        time.sleep(T)

    

    def right_turn180(self, T =1):

        for i in range(0,8):

            self.TX_data(8)

            time.sleep(1)

        self.TX_data(6)

        time.sleep(T)

        

    def stand(self, T =1.3):

        self.TX_data(9)

        time.sleep(T)

        

    def swalk(self, T =0.1):

        self.TX_data(10)

        time.sleep(T)

        

    def head_100(self, T =0.1):

        self.TX_data(11)

        time.sleep(T)

        

    def head_110(self, T =0.1):

        self.TX_data(12)

        time.sleep(T)

    

    def head_120(self, T =0.1):

        self.TX_data(13)

        time.sleep(T)

        

    def head_130(self, T =0.1):

        self.TX_data(14)

        time.sleep(T)

        

    def head_140(self, T =0.1):

        self.TX_data(15)

        time.sleep(T)

        

    def head_150(self, T =0.1):

        self.TX_data(17)

        time.sleep(T)

    

    def head_160(self, T =0.1):

        self.TX_data(18)

        time.sleep(T)

        

    def head_170(self, T =0.1):

        self.TX_data(19)

        time.sleep(T)

        

    def head_180(self, T =0.1):

        self.TX_data(20)

        time.sleep(T)

        

    '''******************mission*******************'''

    

    def up_stair(self, T =1):

        for i in range(3):

            self.TX_data(21)

            time.sleep(7)

            self.TX_data(6)

            time.sleep(T)

            self.TX_data(5)

            time.sleep(T)

        

    def down_stair(self, T =8.3):

        for i in range(3):

            self.TX_data(22)

            time.sleep(T)

        

    def hit_bell(self, T =5.2):

        self.TX_data(23)

        time.sleep(T)

    

    def pick_up(self, T =3.5):

        self.TX_data(24)

        time.sleep(T)

        

    def pick_up_left_walk(self, T =1.6):

        self.TX_data(25)

        time.sleep(T)

    

    def pick_up_right_walk(self, T =1.6):

        self.TX_data(26)

        time.sleep(T)

        

    def pick_up_left_turn(self, T =0.7):

        self.TX_data(27)

        time.sleep(T)

    

    def pick_up_right_turn(self, T =0.7):

        self.TX_data(28)

        time.sleep(T)    

    

    def throw_away(self, T =1):

        self.TX_data(29)

        time.sleep(T)

    

    '''*******************sound********************'''



    def east(self, T =2.5):

        self.TX_data(41)

        time.sleep(T)

        

    def west(self, T =2.5):

        self.TX_data(42)

        time.sleep(T)

        

    def south(self, T =1.7):

        self.TX_data(43)

        time.sleep(T)

        

    def north(self, T =1.6):

        self.TX_data(44)

        time.sleep(T)

        

    def safe_area(self, T =1):

        self.TX_data(45)

        time.sleep(T)

    

    def covid_area(self, T =1):

        self.TX_data(46)

        time.sleep(T)

        

    def danger_area(self, T =1):

        self.TX_data(47)

        time.sleep(T)

        

    def help(self, T =1):

        self.TX_data(48)

        time.sleep(T)

        

    def A_area(self, T =1):

        self.TX_data(49)

        time.sleep(T)

        

    def B_area(self, T =1):

        self.TX_data(50)

        time.sleep(T)

        

    def C_area(self, T =1):

        self.TX_data(51)

        time.sleep(T)

    

    def D_area(self, T =1):

        self.TX_data(52)

        time.sleep(T)

    

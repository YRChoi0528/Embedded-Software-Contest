import serial
import time

class Robot():
    def __init__(self, port='/dev/ttyS0', bps=4800):
        self.ser = serial.Serial(port, bps, timeout=0.01)

    def TX_data(self, command, delay):
        """
        제어 보드에 1byte 명령어를 전송하고 동작 수행을 위한 대기 시간을 가진다.
        """
        self.ser.write(serial.to_bytes([command]))
        time.sleep(delay)


    def loop_command(self, command, count, delay):
        for _ in range(count):
            self.TX_data(command, delay)

    # --- 기본 이동 및 보행 제어 ---
    def go_left(self): self.TX_data(1, 1.45)
    def go_right(self): self.TX_data(2, 1.45)
    def left_walk(self): self.TX_data(3, 0.3)
    def right_walk(self): self.TX_data(4, 0.3)
    def left_turn(self): self.TX_data(5, 0.53)
    def right_turn(self): self.TX_data(6, 0.55)
    def stand(self): self.TX_data(9, 1.3)
    def swalk(self): self.TX_data(10, 0.1)
    
    def walk12(self):
        for i in range(6):
            self.TX_data(1, 1.8)
            self.TX_data(2, 1.8)

    # --- 회전 제어 (복합 동작) ---
    def left_turn90(self):
        self.loop_command(7, 3, 0.7)
        self.TX_data(5, 0.53)
        self.TX_data(4, 0.3)
    

    def right_turn90(self):
        self.loop_command(8, 4, 0.8)
        self.TX_data(6, 0.55)


    def left_turn180(self):
        self.loop_command(7, 6, 1)
        self.TX_data(5, 1)


    def right_turn180(self, T =1):
        self.loop_command(8, 8, 1)
        self.TX_data(6, 1)

    # --- 카메라 헤드 각도 제어 ---
    def head_100(self): self.TX_data(11, 0.1)
    def head_110(self): self.TX_data(12, 0.1)
    def head_120(self): self.TX_data(13, 0.1)
    def head_130(self): self.TX_data(14, 0.1)
    def head_140(self): self.TX_data(15, 0.1)
    def head_150(self): self.TX_data(17, 0.1)
    def head_160(self): self.TX_data(18, 0.1)
    def head_170(self): self.TX_data(19, 0.1)
    def head_180(self): self.TX_data(20, 0.1)

    # --- 미션 수행 기능 ---
    def up_stair(self):
        for i in range(3):
            self.TX_data(21, 7)
            self.TX_data(6, 1)
            self.TX_data(5, 1)
    
    def down_stair(self): self.loop_command(22, 3, 8.3)
    def hit_bell(self): self.TX_data(23, 5.2)
    def pick_up(self): self.TX_data(24, 3.5)
    def pick_up_left_walk(self): self.TX_data(25, 1.6)
    def pick_up_right_walk(self): self.TX_data(26, 1.6)
    def pick_up_left_turn(self): self.TX_data(27, 0.7)
    def pick_up_right_turn(self): self.TX_data(28, 0.7)
    def throw_away(self): self.TX_data(29, 1)

    # --- 음성 및 지역 안내 (방위 포함)
    def east(self): self.TX_data(41, 2.5)
    def west(self): self.TX_data(42, 2.5)
    def south(self): self.TX_data(43, 1.7)
    def north(self): self.TX_data(44, 1.6)
    def safe_area(self): self.TX_data(45, 1)
    def covid_area(self): self.TX_data(46, 1)
    def danger_area(self): self.TX_data(47, 1)
    def help(self): self.TX_data(48, 1)
    def A_area(self): self.TX_data(49, 1)
    def B_area(self): self.TX_data(50, 1)
    def C_area(self): self.TX_data(51, 1)
    def D_area(self): self.TX_data(52, 1)
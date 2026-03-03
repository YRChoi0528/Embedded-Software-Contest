import serial
import time
import numpy as np
from motion import Robot
from alpha import Vision
from threading import Thread



class HumanoidController:
    def __init__(self):
        # 통신 설정
        self.BPS = 4800
        self.port = '/dev/ttyS0'
        self.serial_port = serial.Serial(self.port, self.BPS, timeout=0.01)
        self.serial_port.flush()

        # 모듈 초기화
        self.yr = Robot(self.serial_port)
        self.vision = Vision()

        # 상태 변수
        self.step = 0
        self.leg = 0                # 0: left, 1: right
        self.direction = 1          # 화살표 방향: 우(+1), 좌(-1)
        self.cardinal_dir_start = 1 # 현재 방위: (S=1, E=2, N=3, W=4)
        self.cardinal_dir_finish = 0
        self.corner_type = None
        self.is_running = True

        # 방향 비교를 위한 변수 
        self.prev_heading = None

        # 데이터 수신 스레드 시작
        self.rx_thread = Thread(target=self._receiving_loop)
        self.rx_thread.daemon = True
        self.rx_thread.start()

    

    def _receiving_loop(self):
        """
        제어 보드로부터의 피드백 수신 (Threaded)
        """
        while self.is_running:
            while self.serial_port.inWaiting() > 0:
                rx = ord(self.serial_port.read(1))
                print(f"[RX] Control Board: {rx}")
            time.sleep(0.01)

    

    def walk_cycle(self, trace=None):
        """
        실시간 라인 트레이싱 피드백 제어를 포함한 보행 사이클
        """
        # 궤적 이탈 시 방향 보정
        if trace and trace.get('up'):
            up_points = trace['up']
            if len(up_points) > 0:
                mid_x = np.median(up_points)
                # 라인이 화면 중심(160)을 벗어날 경우 해당 방향으로 미세 회전
                if mid_x < 140:
                    self.yr.left_turn()
                elif mid_x > 180:
                    self.yr.right_turn()

        self.leg = 1 if self.leg == 0 else 0
        if self.leg == 1:
            self.yr.go_left()
        else:
            self.yr.go_right()



    def update_cardinal_pos(self):
        """
        직각 코스를 지날 때마다 현재 방위 값을 갱신한다.
        """
        self.cardinal_dir_start += self.direction
        # 방위 값 범위 보정 (1~4 순환)
        if self.cardinal_dir_start == 0:
            self.cardinal_dir_start = 4
        elif self.cardinal_dir_start == 5:
            self.cardinal_dir_start = 1
        print(f"Current Cardinal Direction Position: {self.cardinal_dir_start}")



    def perform_stair_mission(self):
        """
        계단 오르기/내리기 미션 통합 로직
        """
        self.yr.head_180()

        while True:
            clr = self.vision.detect_side_color('green')
            # 수평 정렬 로직
            if clr[0] - clr[1] > 40:
                self.yr.left_walk() if clr[1] == 0 else self.yr.left_turn()
            elif clr[1] - clr[0] > 40:
                self.yr.right_walk() if clr[0] == 0 else self.yr.right_turn()
            else:
                if clr[0] > 160 and clr[1] > 160:
                    self.yr.up_stair()
                    break
                else:
                    self.walk_cycle()
        
        self.yr.hit_bell()
        self.yr.covid_area()

        # 회전 후 하강
        self.yr.left_turn180()
        self.yr.down_stair()



    def perform_rescue_mission(self):
        """
        위험 지역 시민 구출 미션
        """
        flag = 0
        self.yr.head_120()
        while True:
            mid = self.vision.track_object()
            if mid[0] < 120: 
                self.yr.left_walk()
            elif mid[0] > 200: 
                self.yr.right_walk()
            else:
                if mid[1] < 180:
                    self.walk_cycle()
                else:
                    if flag == 0:
                        self.yr.head_140()
                        flag = 1
                    elif flag == 1:
                        self.yr.head_160()
                        flag = 2
                    elif flag == 2:
                        self.yr.pick_up()
                        break
        self.yr.left_turn180()
        for _ in range(6):
            self.yr.pick_up_left_walk()
            self.yr.pick_up_right_walk()
        self.yr.throw_away()
        self.yr.head_180()



    def run(self):
        """
        메인 실행 루프
        """
        self.yr.head_180()
        print("Robot Mission Started")
        
        while self.is_running:
            try:
                # 영상 데이터 획득
                trace = self.vision.line_trace()

                # --- Step 0 : 입장 단계 ---
                if self.step == 0:
                    if trace:
                        print("Line Detected.")
                        self.step = 1

                # --- Step 1 : 첫 T자 분기점에서 목적지 방위 및 주행 방향 인식 ---
                elif self.step == 1:
                    if trace['up'] and (trace['left'] or trace['right']):
                        self.yr.head_140()
                        # 1. 방위 표지판 인식 (목적지 결정)
                        news_char = self.vision.detect_news()
                        news_map = {'S':1, 'E':2, 'N':3, 'W':4}
                        
                        if news_char in news_map:
                            self.cardinal_dir_finish = news_map[news_char]
                            print(f"Destination Set: {news_char} ({self.cardinal_dir_finish})")

                        self.yr.head_100()
                        # 2. 화살표 방향 인식 (주행 방향 결정)
                        dir_str = self.vision.detected_direction()
                        if dir_str == 'right':
                            self.direction = 1
                        else:
                            self.direction = -1
                        print(f"Arrow Direction: {dir_str} ({self.direction})")

                        # 3. 화살표 방향대로 회전 후 이동 시작
                        if self.direction == 1: 
                            self.yr.right_turn90()
                        else:
                            self.yr.left_turn90()
                        
                        self.yr.head_180()
                        self.step = 2
                    self.walk_cycle(trace)

                # --- Step 2 : 코너 감지 후 미션 진입 준비 ---
                elif self.step == 2:
                    # 90도 코너 감지 (직진 라인이 없고 사이드 라인만 존재할 때)
                    if not trace['up'] and (trace['left'] or trace['right']):
                        self.corner_type = 'left' if trace['left'] else 'right'
                        print(f"{self.corner_type} corner detected.")

                        # 미션 수행 지역까지 충분히 직진
                        self.yr.walk12()

                        # 미션 수행 지역으로 회전 (코너 방향과 반대로 회전)
                        if self.corner_type == 'left':
                            self.yr.right_turn90()
                        else:
                            self.yr.left_turn90()

                        # 회전 후 미션 판별 및 수행 단계로 전이
                        self.step = 3
                    self.walk_cycle(trace)


                # --- Step 3 : 미션 판별 및 수행 ---
                elif self.step == 3:
                    print("Detecting mission")
                    self.yr.head_140() # 미션 판별을 위해 고개 숙임
                    mission_type = self.vision.detect_mission()
                    
                    if mission_type == 'stair':
                        self.perform_stair_mission()
                    else:
                        self.perform_rescue_mission()
                    
                    if self.corner_type == 'left':
                        self.yr.right_turn90()
                    else:
                        self.yr.left_turn90()

                    self.step = 4

                # --- Step 4 : 미션 이후 라인 위치 및 방향 비교/보행 ---
                elif self.step == 4:
                    if trace and trace.get('up'):
                        up_p = trace['up']

                        # 배열의 길이가 충분할 때만 선 두께 기반 처리 진행
                        if len(up_p) >= 2 and (up_p[-1] - up_p[0] > 60):
                            self.walk_cycle(trace)
                        else:
                            # 라인 위치 보상 알고리즘
                            if len(up_p) > 0:
                                if up_p[-1] < 100:
                                    self.yr.left_walk()
                                    continue
                                elif up_p[0] > 160:
                                    self.yr.right_walk()
                                    continue
                            
                            h_threshold = trace['height'] * 0.5
                            
                            # 진행 방향에 따른 사이드 라인 중앙값 활용하여 코너 판단
                            if self.direction == 1:
                                if trace.get('right') and len(trace['right']) > 0:
                                    if np.median(trace['right']) > h_threshold:
                                        self.yr.right_turn90()
                                        self.step = 5
                            else:
                                if trace.get('left') and len(trace['left']) > 0:
                                    if np.median(trace['left']) > h_threshold:
                                        self.yr.left_turn90()
                                        self.step = 5
                    else:
                        self.walk_cycle(trace)

                # --- Step 5 : T자에서 현재지점 업데이트 및 탈출 판단 ---
                elif self.step == 5:
                    if trace['up'] and (trace['left'] or trace['right']):
                        # 현재 지점 업데이트 (순환 구조)
                        self.update_cardinal_pos()

                        # 도착 지점 비교
                        if self.cardinal_dir_start == self.cardinal_dir_finish:
                            self.step = 6
                            print("Final exit turn.")
                            if self.direction == 1:
                                self.yr.right_turn90()
                            else:
                                self.yr.left_turn90()
                            break
                        else:
                            # T자 중복 인식 방지를 위한 장거리 직진 후 다시 코너 탐색
                            print("Continue navigation.")
                            self.yr.walk12()
                            self.step = 2

                elif self.step == 6:
                    if trace:
                        self.walk_cycle(trace)
                    else:
                        print("Clear!!")

            except Exception as e:
                print(f"[Error] {e}")
                self.walk_cycle(trace)

if __name__ == "__main__":
    controller = HumanoidController()
    try:
        controller.run()
    except KeyboardInterrupt:
        controller.is_running = False
        print("Terminated by User.")

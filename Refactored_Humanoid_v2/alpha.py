import cv2
import numpy as np

class Vision:
	def __init__(self):
		# 카메라 초기화 및 설정
		self.cap = cv2.VideoCapture(0)
		self.cap.set(cv2.CAP_PROP_FRAME_WIDTH , 320)
		self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
		self.cap.set(cv2.CAP_PROP_FPS, 90)

		# 색상 임계값 정의
		self.L_YELLOW = np.array([20, 70, 70])
		self.U_YELLOW = np.array([45, 255, 255])
		self.L_BLACK = 30 # V_value 기준
	


	def get_frame(self, roi=None):
		"""
		프레임을 읽고 ROI(관심 영역)가 지정된 경우 크롭한다..
		"""
		ret, frame = self.cap.read()
		if not ret:
			return None
		if roi:
			# roi = (y0, y1, x0, x1)
			return frame[roi[0]:roi[1], roi[2]:roi[3]].copy()
		return frame
	


	def line_trace(self):
		"""
		라인 트레이싱을 위한 노란색 라인 경계 검출
		"""
		frame = self.get_frame(roi=(0, 200, 0, 320))
		if frame is None: 
			return None
		
		blur = cv2.GaussianBlur(frame, (3, 3), 0)
		hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)
		mask = cv2.inRange(hsv, self.L_YELLOW, self.U_YELLOW)
		contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

		if not contours: 
			return None
		
		c = max(contours, key=cv2.contourArea)
		points = np.squeeze(c, axis=1)

		# 경계 포인트 추출 로직 최적화
		h, w = frame.shape[:2]
		res = {
			'right': sorted([p[1] for p in points if p[0] == w-1]),
			'left': sorted([p[1] for p in points if p[0] == 0]),
			'up': sorted([p[0] for p in points if p[1] == 0]),
			'down': sorted([p[0] for p in points if p[1] == h-1]),
			'y_min': np.min(points, axis=0)[1],
			'y_max': np.max(points, axis=0)[1],
			'x_min': np.min(points, axis=0)[0],
			'x_max': np.max(points, axis=0)[0],
			'height': h, 'width': w
		}
		return res
	


	def detected_direction(self, WC=False):
		"""
		이동 방향(화살표 인식)
		"""
		frame = self.get_frame(roi=(0, 200, 0, 320))
		hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
		v_channel = hsv[:, :, 2]

		# 검은색 라인 추출 (Thresholding)
		_, binary = cv2.threshold(v_channel, self.L_BLACK, 255, cv2.THRESH_BINARY_INV)

		# 각 수직 열에서의 검은색 픽셀 높이 계산
		col_counts = [cv2.countNonZero(binary[:, x]) for x in range(0, 320, 10)]
		active_cols = [i for i, count in enumerate(col_counts) if count > 0]

		if not active_cols:
			return None

		vs, ve = active_cols[0], active_cols[-1]
		max_idx = col_counts.index(max(col_counts))

		result = 'right' if (max_idx - vs) > (ve - vs) / 2 else 'left'

		if WC:
			cv2.imshow('Cam', binary)
			cv2.waitKey(1)
		return result



	def detect_news(self, WC=False):
		"""
		동서남북(E, W, S, N) 방위 표지판 인식
		"""
		frame = self.get_frame(roi=(90, 220, 0, 320))
		hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
		h, w = frame.shape[:2]

		wid = [] # 가로 방향 검은색 선분 개수
		for y in range(0, h, 5):
			count, cnt = 0, 0
			for x in range(w):
				if hsv[y, x][2] < 65: # V_value < 65
					cnt = 1
				else:
					if cnt == 1: 
						count += 1
						cnt = 0
			wid.append(count)

		vrc = [] # 세로 방향 검은색 선분 개수
		for x in range(0, w, 10):
			count, cnt = 0, 0	
			for y in range(h):
				if hsv[y, x][2] < 65: # V_value < 65
					cnt = 1
				else:
					if cnt == 1:
						count += 1
						cnt = 0
			vrc.append(count)
		
		# 시작/끝 인덱스 검출
		ws = next((i for i, v in enumerate(wid) if v != 0), 0)
		ve = next((i for i in range(len(vrc)-1, -1, -1) if vrc[i] != 0), 0)

		res = None
		if wid[ws] >= 3 or (ws < len(wid)-1 and wid[ws+1] == 3): res = 'W'
		elif wid[ws] == 2: res = 'N'
		elif wid[ws] == 1:
			if vrc[ve] == 3: res = 'E'
			elif vrc[ve] == 2: res = 'S'

		if WC:
			cv2.imshow('Cam', frame)
			cv2.waitKey(1)
		return res



	def detect_abcd(self, WC=False):
		"""
		재난 지역 알파벳(A, B, C, D) 인식
		"""
		frame = self.get_frame()
		hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
		h, w = frame.shape[:2]

		wid, vrc = [], []
		# 채도 기반 분석
		for y in range(0, h, 5):
			count, cnt = 0, 0
			for x in range(w):
				if hsv[y, x][1] > 120: # S_value >120
					cnt = 1
				else:
					if cnt == 1:
						count += 1
						cnt = 0
			wid.append(count)

		for x in range(0, w, 10):
			count, cnt = 0, 0
			for y in range(h):
				if hsv[y, x][1] > 120: # S_value >120
					cnt = 1
				else:
					if cnt == 1:
						count += 1
						cnt = 0
			vrc.append(count)

		ws = next((i for i, v in enumerate(wid) if v != 0), 0)
		vs = next((i for i, v in enumerate(vrc) if v != 0), 0)
		we = next((i for i in range(len(wid)-1, -1, -1) if wid[i] != 0), 0)
		ve = next((i for i in range(len(vrc)-1, -1, -1) if vrc[i] != 0), 0)

		res = None
		mid_vrc = vrc[int((vs+ve)/2)]
		if mid_vrc == 3: res = 'B'
		elif vrc[ve] == 2 or (ve > 0 and vrc[ve-1] == 2): res = 'C'
		elif wid[we] == 2: res = 'A'
		elif wid[we] == 1: res = 'D'

		if WC:
			cv2.imshow('Cam', frame)
			cv2.waitKey(1)
		return res



	def detect_side_color(self, color_type='green', WC=False):
		"""
		계단 정렬 등을 위해 좌우 끝안의 색상 픽셀 수를 카운트 한다.
		"""
		frame = self.get_frame(roi=(0, 200, 0, 320))
		hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

		if color_type == 'green':
			mask = cv2.inRange(hsv, np.array([45, 100, 140]), np.array([60, 160, 255]))
		elif color_type == 'blue':
			mask = cv2.inRange(hsv, np.array([45, 100, 170]), np.array([255, 255, 255]))
		else: # red
			mask = cv2.inRange(hsv, np.array([160, 110, 70]), np.array([255, 255, 255]))
		
		# 좌측 끝(x=1)과 우측 끝(x=319)의 흰색 픽셀(255) 개수 합산
		left_cnt = cv2.countNonZero(mask[:, 1])
		right_cnt = cv2.countNonZero(mask[:, 319])

		if WC:
			cv2.imshow('Cam', frame)
			cv2.waitKey(1)
		return [left_cnt, right_cnt]
	


	def track_object(self, WC=False):
		"""
		위험 지역 내 물체(시민)의 중앙 좌표를 반환한다.
		"""
		frame = self.get_frame()
		hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

		# 검정색/무채색을 제외한 유색 영역 마스킹
		mask = cv2.inRange(hsv, np.array([0, 75, 65]), np.array([180, 255, 255]))
		contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

		middle = [160, 200] # 기본값 (화면 하단 중앙 부근)
		if contours:
			c = max(contours, key=cv2.contourArea)
			x, y, w, h = cv2.boundingRect(c)
			middle[0] = int(x + w/2) # 객체의 가로 중앙
			middle[1] = int(y + h/2) # 객체의 세로 중앙
			
			if WC:
				cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
				cv2.circle(frame, (middle[0], middle[1]), 5, (0, 0, 255), -1)
				cv2.imshow('Cam', frame)
				cv2.waitKey(1)
		return middle
	


	def detect_mission(self):
		"""
		위험 지역(dan) vs 계단 지역(stair) 판별
		"""
		frame = self.get_frame()
		hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

		# 모서리 픽셀의 채도를 확인하여 위험 지역 여부 판단
		corners = [(0, 0), (0, 319), (239, 0), (239, 319)]
		is_dangerous = all(hsv[y, x][1] < 30 for y, x in corners)

		return 'dan' if is_dangerous else 'stair'



	def cap_img(self, name='cap'):
		"""
		현재 화면 캡처 저장
		"""
		frame = self.get_frame()
		cv2.imwrite(f'cap/{name}.jpg', frame)



	def __del__(self):
		"""
		객체 소멸 시 카메라 리소스를 해체합니다.
		"""
		if self.cap.isOpened():
			self.cap.release()
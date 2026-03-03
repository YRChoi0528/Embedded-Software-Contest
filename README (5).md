# 제 20회 임베디드 경진대회 (지능형 휴머노이드 부분)

## 경진대회 소개
제 20회 임베디드 경진대회로 지능형 휴머노이드를 활용하여 재난상황 속 여러 미션을 진행하며 문제를 해결해 나가는 대회이다.<br>
강원대학교 전자공학과에 속한 NPE라는 동아리 소속으로 대회에 참가하였으며 단순히 코딩을 통해 문제를 해결하는 것이 아닌 <br>
휴머노이드를 통해 직접 로봇을 활용하여 로봇의 모터값을 조정, 로션의 무게중심을 맞추는 등 로봇의 하드위어적 부분과 휴머노이드를 <br>
동작시키는 라즈베리파이를 활용한 프로그래밍을 통해 미션을 수행할 수 있는 기능을 구현해 나가게 된다.

## 경진대회 팀 소개 및 역할
> 최영락(팀장) : 라인트레이스 기능 구현 및 로봇 모션 기능 보조<br>
> 송우석(팀원) : 컬러 트래킹 기능 구현 및 알파벳 인식 기능 구현<br>
> 강선규(팀원) : 로봇의 통신 기능 및 알파벳에 따른 로봇 모션 변화 기능 구현<br>
> 김선영(팀원) : 로봇베이직을 통해 로봇의 모션 구현<br>
> 곽수정(팀원) : 로봇 모션 기능 보조 및 컬러 트래킹 기능 구현 보조<br>


## Stacks 🐈

### Environment
 <img src="https://img.shields.io/badge/PyCharm-007396?style=for-the-badge&logo=PyCharm&logoColor=white"> <img src="https://img.shields.io/badge/RoboBasic-green?style=for-the-badge&logo=RoboBasic&logoColor=white"> 
 
### Development
![Python](https://img.shields.io/badge/-Python-blue?logo=python&logoColor=white)


##  Explain Code 📦

### ⭐️ alpha.py
- OpenCV contour기능을 활용한 Line trace 기능 구현
- 재난지역(a,b,c,d) 판별 기능 및 동서남북, 이동방향(화살표) 인식 기능 구현

### ⭐️ motion.py
- 로봇의 통신을 통한 로봇 동작 실행 함수 구현

### ⭐️ robobasicMotion
- 로보베이직을 통한 로봇의 모터값을 비롯한 세팅값 조정

### ⭐️ finish.py
- main 코드로 로봇의 프로그램을 실행시 자동으로 로봇의 카메라를 통해 영상을 처리해 상황 별 로봇 동작 수행

def detection(pose, dist):
	# 로봇을 지정된 pose로 이동
	movel(pose, v=100, a=100, ref=DR_BASE)
	wait(0.5)
	# 디지털 출력 1번을 ON (예: 집게 작동)
	set_digital_output(1, ON)
	wait(1)
	# 디지털 출력 1번을 OFF (예: 집게 해제)
	set_digital_output(1, OFF)
	wait(0.5)

	# 힘 제어 수행 (Base 좌표계 기준 -z 방향 힘 인가)
	k_d = [3000.0, 3000.0, 3000.0, 200.0, 200.0, 200.0]
	task_compliance_ctrl(k_d)
	force_desired = 20.0
	f_d = [0.0, 0.0, -force_desired, 0.0, 0.0, 0.0]
	f_dir = [0, 0, 1, 0, 0, 0]
	set_desired_force(f_d, f_dir)

	flag = 0
	# 외력 감지 후 힘-강성 제어 수행
	force_check = 20.0
	force_condition = check_force_condition(DR_AXIS_Z, max=force_check)
	while force_condition:
		# 계속해서 외력 감지 여부 확인
		force_condition = check_force_condition(DR_AXIS_Z, max=force_check)
		if force_condition == 0:
			# 감지된 힘이 없는 경우
			if get_current_posx()[0][2] < 44.0:
				flag = 0  # 아무것도 없을 때
			else:
				flag = 1  # 물체가 있을 때
			break

	release_force()
	wait(0.5)
	release_compliance_ctrl()

	if flag == 1:
		# 물체가 감지되었을 경우
		x1 = trans(get_current_posx()[0], [0, 0, -15, 0, 0, 0], DR_BASE, DR_BASE)
		set_digital_output(2, ON)  # 그리퍼 닫기
		set_digital_output(2, OFF)
		movel(x1, v=100, a=100, ref=DR_BASE)
		wait(0.5)
		set_digital_output(1, ON)  # 물체를 잡기
		wait(1)
		set_digital_output(1, OFF)
		wait(0.5)
		movel(pose, v=100, a=100, ref=DR_BASE)
		x2 = trans(pose, [dist, 0, 0, 0, 0, 0], DR_BASE, DR_BASE)
		movel(x2, v=100, a=100, ref=DR_BASE)
		fall(x2)  # 물체 놓기 수행
	else:
		movel(pose, v=100, a=100, ref=DR_BASE)

# 물체 내려놓는 함수
def fall(pose):
	# 물체를 아래로 이동시킴
	x1 = trans(pose, [0, 0, -60, 0, 0, 0], DR_BASE, DR_BASE)
	movel(x1, v=100, a=100, ref=DR_BASE)

	# 힘 제어 수행 (Base 좌표계 기준 -z 방향 힘 인가)
	k_d = [3000.0, 3000.0, 3000.0, 200.0, 200.0, 200.0]
	task_compliance_ctrl(k_d)
	force_desired = 20.0
	f_d = [0.0, 0.0, -force_desired, 0.0, 0.0, 0.0]
	f_dir = [0, 0, 1, 0, 0, 0]
	set_desired_force(f_d, f_dir)

	# 외력 감지 후 힘-강성 제어 수행
	force_check = 20.0
	force_condition = check_force_condition(DR_AXIS_Z, max=force_check)
	while force_condition:
		force_condition = check_force_condition(DR_AXIS_Z, max=force_check)
		if force_condition == 0:
			# 물체를 내려놓기 위해 그리퍼 열기
			set_digital_output(2, ON)
			wait(1)
			set_digital_output(2, OFF)
			break

	release_force()
	wait(0.5)
	release_compliance_ctrl()
	wait(1)

	# 원래 위치로 복귀
	x2 = trans(pose, [0, 0, 0, 0, 0, 0], DR_BASE, DR_BASE)
	movel(x2, v=100, a=100, ref=DR_BASE)

# -----쓰레드
def stoping():
	# 특정 힘이 y축 방향으로 감지되었을 경우 작동
	if get_tool_force()[1] > 10:
		set_digital_output(2, ON)
		set_digital_output(2, OFF)

# 메인 코드 실행
# 포인트들의 배열 정의
points = [Global_point1, Global_point2, Global_point3, Global_point4,
	   Global_point5, Global_point6, Global_point7, Global_point8, Global_point9]

# 쓰레드 시작
th_id = thread_run(stoping, loop=True)

# 모든 포인트에서 감지 실행
for i in range(len(points)):
	detection(points[i], -150)

# 새로운 포인트 배열 생성 후 위치 조정
new_points = [Global_point1, Global_point2, Global_point3, Global_point4,
		  Global_point5, Global_point6, Global_point7, Global_point8, Global_point9]

for i in range(len(new_points)):
	new_points[i][0] -= 150.0

# 새로운 위치에서 감지 실행
for i in range(len(new_points)):
	detection(new_points[i], 150)

# 쓰레드 종료
thread_stop(th_id)

def detection(pose1, pose2):
    movel(pose1, v = 200, a = 100, ref = DR_BASE)
    wait(0.5)
    set_digital_output(1,ON)
    wait(1)
    set_digital_output(1,OFF)    
    wait(0.5)

    # 3. 힘 제어 수행 (Base 좌표계 기준 -z 방향 힘 인가)
    k_d = [3000.0, 3000.0, 3000.0, 200.0, 200.0, 200.0]
    task_compliance_ctrl(k_d)
    force_desired = 20.0
    f_d = [0.0, 0.0, -force_desired, 0.0, 0.0, 0.0]
    f_dir = [0, 0, 1, 0, 0, 0]
    set_desired_force(f_d, f_dir)

    flag = 0
    # 4. 외력 감지 후 힘-강성 제어 수행
    force_check = 20.0
    force_condition = check_force_condition(DR_AXIS_Z, max=force_check)
    while (force_condition):
        force_condition = check_force_condition(DR_AXIS_Z, max=force_check)
        if force_condition == 0:
            # 아무것도 없을 때
            if get_current_posx()[0][2] < 44.0:
                flag = 0
            # 물체가 있을 때
            else:
                flag = 1
            break
    release_force()
    wait(0.5)
    release_compliance_ctrl()

    if flag == 1:
        x1 = trans(get_current_posx()[0], [0, 0, -15, 0, 0, 0],DR_BASE,DR_BASE)
        set_digital_output(2,ON)
        set_digital_output(2,OFF)
        movel(x1, v = 200, a = 100, ref = DR_BASE)
        wait(0.5)
        set_digital_output(1,ON)
        wait(1)
        set_digital_output(1,OFF)    
        wait(0.5)
        current_z = get_current_posx()[0][2]
        movel(pose1, v = 200, a = 100, ref = DR_BASE)
        movel(pose2, v = 200, a = 100, ref = DR_BASE)
        fall(pose2, current_z)
    else :
        movel(pose1, v = 100, a = 100, ref = DR_BASE)

# 내려놓는 함수
def fall(pose, current_z):
    # 내려가는거
    #x1 = trans(pose,[0, 0, -60, 0, 0, 0],DR_BASE,DR_BASE)
    movel(pose, v =200, a = 100, ref = DR_BASE)

    # 3. 힘 제어 수행 (Base 좌표계 기준 -z 방향 힘 인가)
    k_d = [3000.0, 3000.0, 3000.0, 200.0, 200.0, 200.0]
    task_compliance_ctrl(k_d)
    force_desired = 20.0
    f_d = [0.0, 0.0, -force_desired, 0.0, 0.0, 0.0]
    f_dir = [0, 0, 1, 0, 0, 0]
   

    # 4. 외력 감지 후 힘-강성 제어 수행
    force_check = 20.0
    force_condition = check_force_condition(DR_AXIS_Z, max=force_check)
    while (force_condition):
        set_desired_force(f_d, f_dir)
        force_condition = check_force_condition(DR_AXIS_Z, max=force_check)
        if force_condition == 0:    
            if (get_current_posx()[0][2] - current_z)*(get_current_posx()[0][2] - current_z) < 4:
                # 그리퍼 풀고
                set_digital_output(2,ON)
                wait(1)
                set_digital_output(2,OFF)
                break
            else:
                release_force()
                wait(0.5)
                release_compliance_ctrl()
                movel(pose, v = 200, a = 100, ref = DR_BASE)
                wait(0.5)
                tp_popup('there is something',DR_PM_MESSAGE)
               
                exit()
               
    release_force()
    wait(0.5)
    release_compliance_ctrl()

    wait(1)
    # 위로 올라감
    movel(pose, v = 200, a = 100, ref = DR_BASE)


# -----쓰레드
def stoping():
    #a = check_robot_mastering()
    a = get_tool_digital_input(1)
   
    tp_log('{}'.format(a))
# -------메인
# ---------------좌표
# 1 plate
pose_11 = posx(498.0, 99.2, 130.0, 0, 180, 0)
pose_12 = posx(498.5, -0.5, 130.0, 0, 180, 0)
pose_13 = posx(600.3, 98.8, 130.0, 0, 180, 0)
pose_14 = posx(600.0, -1.9, 130.0, 0, 180, 0)

direction_1 = 0
row_1 = 3
column_1 = 3
thickness_1 = 0
point_offset_1 = [0, 0, 0]
stack_1 = 1

if direction_1 < 2:
    total_count_1 = row_1*column_1*stack_1
else:
    total_count_1 = (row_1*cloumn_1-int(row_1/2))*stack_1
   
# 2 plate
pose_21 = posx(348.1, 99.5, 130.0, 0, 180, 0)
pose_22 = posx(348.8, -2.8, 130.0, 0, 180, 0)
pose_23 = posx(449.5, 99.5, 130.0, 0, 180, 0)
pose_24 = posx(449.8, -2.7, 130.0, 0, 180, 0)

direction_2 = 0
row_2 = 3
column_2 = 3
thickness_2 = 0
point_offset_2 = [0, 0, 0]
stack_2 = 1

if direction_1 < 2:
    total_count_2 = row_2*column_2*stack_2
else:
    total_count_2 = (row_2*cloumn_2-int(row_2/2))*stack_2



# ------------------------실제 행동
# thread on
th_id = thread_run(stoping, loop=True)

while True:
    user_in = tp_get_user_input('start point (1-9 : 시작할 위치, 0 - 이전 위치부터 시작)', input_type = DR_VAR_INT)-1

    if user_in == -1:
        break
    elif (user_in >=0) and (user_in <=8):
        check_current = user_in
        break
    else:
        tp_popup('wrong point input',DR_PM_MESSAGE)

while True:
    dir =  tp_get_user_input('direction (1 - 안쪽으로, 2 - 바깥쪽으로)', input_type = DR_VAR_INT)
   
    if dir != 1 and dir != 2:
        tp_popup('wrong direction input',DR_PM_MESSAGE)
    else:
        break
   
for i in range(check_current, total_count_1):
    p1 = get_pattern_point(pose_11, pose_12, pose_13, pose_14, i, direction_1, row_1, column_1, stack_1, thickness_1, point_offset_1)
    p2 = get_pattern_point(pose_21, pose_22, pose_23, pose_24, i, direction_2, row_2, column_2, stack_2, thickness_2, point_offset_2)
   
    if dir == 1:
        detection(p1,p2)
    elif dir == 2:
        detection(p2,p1)
    check_current = i+1

check_current = 0


thread_stop(th_id)

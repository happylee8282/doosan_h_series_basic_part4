x2 = trans(Global_goal, [0, 0, -30, 0, 0, 0], DR_BASE, DR_BASE)

movel(Global_init, v=100, a=100, ref=DR_BASE)
wait(0.5)

x1 = trans(Global_init, [0, 0, -50, 0, 0, 0], DR_BASE, DR_BASE)
movel(x1, v=100, a=100, ref=DR_BASE)
wait(0.5)

set_digital_output(1, ON)
wait(1)
set_digital_output(1, OFF)
wait(0.5)

movel(Global_init, v=130, a=130, ref=DR_BASE)
wait(0.5)

movel(Global_goal, v=150, a=150, ref=DR_BASE)
movel(x2, v=100, a=100, ref=DR_BASE)

# 내려놓는 함수
movel(x2, v=100, a=100, ref=DR_BASE)
wait(0.5)

force_check = 15.0
force_condition = check_force_condition(DR_AXIS_Z, max=force_check)
flag = 0

while True:
    # 4. 외력 감지 후 힘-강성 제어 수행
    force_condition = check_force_condition(DR_AXIS_Z, max=force_check)
    
    k_d = [3000.0, 3000.0, 3000.0, 200.0, 200.0, 200.0]
    task_compliance_ctrl(k_d)

    force_desired = 15.0
    f_d = [0.0, 0.0, -force_desired, 0.0, 0.0, 0.0]
    f_dir = [0, 0, 1, 0, 0, 0]
    set_desired_force(f_d, f_dir)

    if force_condition == 0:
        # move_spiral(rev=10, rmax=10.0, lmax=0.0, time=20.0, axis=DR_AXIS_Z, ref=DR_TOOL)
        move_periodic(amp=[0, 0, 0, 0, 0, 30], period=1.0, atime=0.2, repeat=1, ref=DR_TOOL)
        wait(1)

        if get_current_posx()[0][2] < 65:
            wait(1)
            break
    else:
        flag += 1
        if flag >= 5:
            break

release_force()
wait(0.5)
release_compliance_ctrl()
wait(0.5)

if flag >= 5:
    movel(Global_goal, v=150, a=150, ref=DR_BASE)
    tp_popup('clean up please', DR_PM_MESSAGE)
else:
    set_digital_output(2, ON)
    wait(1)
    set_digital_output(2, OFF)
    wait(0.5)

movel(Global_goal, v=150, a=150, ref=DR_BASE)

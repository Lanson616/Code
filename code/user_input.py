# ==================== 用户输入模块 ====================
# 两种输墙的格式按需取用：input1 逐个输坐标，input2 一行一行输整张地图
import constants


def read_size_and_delta():
    # 读入地图大小和转头角度，写入 constants 的共享状态
    constants.width = int(input("width: "))
    constants.height = int(input("height: "))
    if constants.width <= 0 or constants.height <= 0:
        print("地图大小必须大于0")
        exit(1)
    # 创建空地图，左上角是(0,0)
    constants.map1 = [[0 for _ in range(constants.height)] for _ in range(constants.width)]

    # 角度用整数标记，delta 只取 1 和 2，分别对应 30 度和 60 度
    temp = int(input('请输入每次转头的角度delta，只能是30或60：'))
    while temp not in [30, 60]:
        print('错误！当前版本只支持取delta为30或60！')
        temp = int(input('请输入每次转头的角度delta，只能是30或60：'))
    constants.delta = temp / 30


def input1():
    # 输入所有有墙格子的坐标，输入（-1, -1）表示结束
    while True:
        try:
            x, y = (int(i.strip()) for i in input("请输入墙的坐标（x, y），输入（-1， -1）结束输入").split(","))
            if (x, y) == (-1, -1):
                break
            if constants.in_bounds(x, y):
                constants.map1[x][y] = 1
            else:
                print("坐标超出范围，请重新输入")
        except ValueError:
            print("输入格式错误，请输入两个整数，用逗号分隔")


def input2():
    # 按行输入整张地图，一行内格子之间不分隔，0=空，1=墙
    print(f'请按行输入地图，共 {constants.height} 行，每行 {constants.width} 个字符（0=空，1=墙）')
    for i in range(constants.height):
        while True:
            temp = input(f"第 {i + 1} 行: ").strip()
            if len(temp) != constants.width:
                print("输入的格子数与列数不符，请重新输入")
                continue
            for j in range(constants.width):
                constants.map1[j][i] = int(temp[j])
            break


def input_start():
    # 输入起始格子坐标，必须在地图内且不为墙格
    start_x, start_y = (int(i.strip()) for i in input("请输入起始格子的坐标（x, y）: ").split(","))
    while not (constants.in_bounds(start_x, start_y) and constants.map1[start_x][start_y] == 0):
        print('错误！起始格子必须在地图内且不为墙格！')
        start_x, start_y = (int(i.strip()) for i in input("请输入起始格子的坐标（x, y）: ").split(","))
    return start_x, start_y

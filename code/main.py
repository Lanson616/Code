# ==================== main：串联并运行所有模块 ====================
# 模块结构：
#   constants       常数与共享状态
#   user_input      用户输入
#   simulation      视觉（遮挡/可见性）+ 模拟运行规则（安全性检查、动作系统）
#   BFS_search 等   搜索算法（统一提供 search_single / search_double 接口）
#   search_registry 搜索算法注册表，main 启动时从这里选算法
#   visualization   重放与动画
import constants
import user_input
import search_registry
from simulation import visible_mask_at, find_all_empty_mask
from visualization import replay_single, replay_double, quick_anim

UPPER_INIT = 9999999  # 剪枝上界的初始值


def solve_single(algo, start):
    # 用指定算法做单人搜索：对 12 个初始面向都试一遍，
    # 用当前已知最优步数做剪枝上界，越搜越快
    # 返回 (是否有解, 最优路径, 最优步数, 最优初始面向)
    solution = False
    final_path = None
    final_step = -1
    best_face = -1
    best = UPPER_INIT
    for face in range(12):
        initial = (start, face, visible_mask_at(start, face))
        result, path, step = algo.search_single(initial, best)
        if result:
            final_path, final_step, best_face = path, step, face
            best = step
            solution = True
    return solution, final_path, final_step, best_face


def solve_double(algo, start):
    # 用指定算法做双人搜索（单人无解时调用）
    # 返回 (是否有解, 最优路径, 最优步数, 最优初始面向组合)
    solution = False
    final_path = None
    final_step = -1
    best_faces = (-1, -1)
    best = UPPER_INIT
    for face1 in range(12):
        # face2 从 face1 开始：两个初始面向对称，省一半
        for face2 in range(face1, 12):
            cleared = visible_mask_at(start, face1) | visible_mask_at(start, face2)
            initial = (start, face1, start, face2, cleared)
            result, path, step = algo.search_double(initial, best)
            if result:
                final_path, final_step, best_faces = path, step, (face1, face2)
                best = step
                solution = True
    return solution, final_path, final_step, best_faces


def choose_algorithm():
    # 启动时选择搜索算法，直接回车用默认（第一个注册的）
    # 返回 (算法模块, 算法名)
    all_names = search_registry.names()
    print('可用搜索算法：', '、'.join(all_names))
    name = input(f'请选择算法（直接回车默认 {all_names[0]}）：').strip()
    if not name:
        name = all_names[0]
    while name not in all_names:
        print('没有注册这个算法，请重新输入')
        name = input(f'请选择算法（直接回车默认 {all_names[0]}）：').strip() or all_names[0]
    return search_registry.get(name), name


def main():
    # ---------- 输入 ----------
    user_input.read_size_and_delta()
    user_input.input2()   # 逐坐标输墙可改用 user_input.input1()
    start = user_input.input_start()
    find_all_empty_mask()

    # ---------- 选择搜索算法 ----------
    algo, algo_name = choose_algorithm()
    print(f'已选择算法：{algo_name}')

    # ---------- 单人搜索 ----------
    solution, final_path, final_step, best_face = solve_single(algo, start)
    if solution:
        print(f'本地图可以单人完成搜索，最小步数为{final_step}，可以在初始面向取{best_face * 30}度时取得，一个最优路径为{final_path}。')
        states = replay_single(start, best_face, final_path)
        quick_anim(states, mode='single', interval=400, save=constants.output_path('single.gif'))
        return

    # ---------- 双人搜索 ----------
    solution, final_path, final_step, best_faces = solve_double(algo, start)
    if solution:
        print(f'本地图至少需要两人才可安全搜索，最小步数为{final_step}，可以在两个守卫分别面向{best_faces[0] * 30}度和{best_faces[1] * 30}度时取得，与之对应的一个最优路径为{final_path}')
        states = replay_double(start, best_faces[0], best_faces[1], final_path)
        quick_anim(states, mode='double', interval=500, save=constants.output_path('double.gif'))
    else:
        print('本地图需要至少三人才可安全搜索。没有非平凡的安全路径。')


if __name__ == '__main__':
    main()

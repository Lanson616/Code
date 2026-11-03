# ==================== 重放与可视化 ====================
# replay_*：按搜索得到的 path 重放，重建每一步的完整状态序列
# quick_anim：用 matplotlib 播放动画，可另存为 gif
import numpy as np
import matplotlib
matplotlib.use('TkAgg')          # 强制有界面后端；若报错改 'QtAgg'
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import matplotlib.patches as mpatches

import constants
from simulation import visible_mask_at, can_see, apply_one

_ani_keepalive = None


def replay_single(start, face0, path):
    states = []
    pos, face = start, face0
    cleared = visible_mask_at(pos, face)
    states.append((pos, face, cleared))
    for act in path:
        if act is None:
            continue
        pos, face = apply_one(pos, face, act)
        cleared |= visible_mask_at(pos, face)
        states.append((pos, face, cleared))
    return states


def replay_double(start, face1_0, face2_0, path):
    states = []
    g1, f1, g2, f2 = start, face1_0, start, face2_0
    cleared = visible_mask_at(g1, f1) | visible_mask_at(g2, f2)
    states.append((g1, f1, g2, f2, cleared))
    for item in path:
        if item is None:
            continue
        a1, a2 = item
        g1, f1 = apply_one(g1, f1, a1)
        g2, f2 = apply_one(g2, f2, a2)
        cleared |= visible_mask_at(g1, f1) | visible_mask_at(g2, f2)
        states.append((g1, f1, g2, f2, cleared))
    return states


def quick_anim(states, mode='single', interval=400, save=None):
    # 播放动画；save 传文件名可同时保存为 gif
    global _ani_keepalive
    assert states, "states 为空，检查 replay_* 的输入"
    print(f"开始动画，共 {len(states)} 帧，后端 = {matplotlib.get_backend()}")

    fig, ax = plt.subplots(figsize=(7, 7))
    base = np.array(constants.map1).T  # 转置成 [y][x] 方便 imshow
    width, height = constants.width, constants.height

    def update(i):
        ax.clear()
        ax.imshow(base, cmap='gray_r', origin='upper',
                  extent=(-0.5, width - 0.5, height - 0.5, -0.5))
        ax.set_xticks(range(width)); ax.set_yticks(range(height))
        ax.grid(color='lightgray', lw=0.4)
        ax.set_aspect('equal')

        st = states[i]
        if mode == 'single':
            g1, f1, cleared = st
            guards = [(g1, f1, 'red')]
        else:
            g1, f1, g2, f2, cleared = st
            guards = [(g1, f1, 'red'), (g2, f2, 'blue')]

        # 已清除的格子涂绿
        for x in range(width):
            for y in range(height):
                if (cleared >> constants.idx(x, y)) & 1 and constants.map1[x][y] == 0:
                    ax.add_patch(mpatches.Rectangle((x - 0.5, y - 0.5), 1, 1,
                                                    facecolor='lime', alpha=0.3))
        # 守卫本体 + 当前视野范围内的格子
        for gpos, gface, c in guards:
            for x in range(width):
                for y in range(height):
                    if constants.map1[x][y] == 0 and can_see((x, y), gpos, gface):
                        ax.add_patch(mpatches.Rectangle((x - 0.5, y - 0.5), 1, 1,
                                                        facecolor=c, alpha=0.12))
            ax.add_patch(mpatches.Circle(gpos, 0.3, color=c, zorder=5))
            th = gface * np.pi / 6
            ax.annotate('', xy=(gpos[0] + 0.45 * np.cos(th), gpos[1] + 0.45 * np.sin(th)),
                        xytext=gpos, arrowprops=dict(arrowstyle='-|>', color=c, lw=2))
        ax.set_title(f'step {i}/{len(states) - 1}')

    ani = FuncAnimation(fig, update, frames=len(states),
                        interval=interval, repeat=False)
    _ani_keepalive = ani
    if save:
        ani.save(save, writer='pillow', fps=max(1, 1000 // interval))
        print(f"动画已保存到 {save}")
    plt.show(block=True)
    return ani

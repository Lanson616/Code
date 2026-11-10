# ==================== 地图绘制器 ====================
# 点击式地图编辑：先点格子画墙（黑白切换），确认后点击白色格子选守卫起点（红色）
# 两种使用方式：
#   独立启动  python3 map_editor.py   —— 画完默认保存到 maps/
#   被 user_input.choose_map 引用（地图来源选项 4）—— 画完询问是否保存
import tkinter as tk
from tkinter import messagebox

import map_loader

MAX_SIZE = 50  # 地图长宽上限


class MapEditor:
    # 编辑器状态机：draw（画墙） -> start（选起点） -> done（完成）
    def __init__(self, width, height):
        self.width, self.height = width, height
        self.walls = set()      # 墙格子坐标集合
        self.start = None       # 守卫起点坐标
        self.phase = 'draw'

        # 格子像素大小：大地图自动缩小，画布不超过约 700px
        self.cell = self._calc_cell(width, height)

        self.root = tk.Tk()
        self.root.title('地图绘制器')
        self.info = tk.Label(self.root, text='阶段 1：点击格子切换 墙（黑）/ 空地（白），画好后点【确认】')
        self.info.pack(padx=8, pady=6)
        self.canvas = tk.Canvas(self.root, width=width * self.cell, height=height * self.cell, bg='white')
        self.canvas.pack(padx=8, pady=4)
        self.canvas.bind('<Button-1>', self.on_click)

        # 按钮栏：加/减行、加/减列（只作用于最后一行/列），以及确认键
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=6)
        self.size_btns = []
        for text, cmd in (('＋ 行', self._add_row), ('－ 行', self._remove_row),
                          ('＋ 列', self._add_col), ('－ 列', self._remove_col)):
            b = tk.Button(btn_frame, text=text, width=5, command=cmd)
            b.pack(side='left', padx=3)
            self.size_btns.append(b)
        self.confirm_btn = tk.Button(btn_frame, text='确认', width=10, command=self.on_confirm)
        self.confirm_btn.pack(side='left', padx=12)

        self.rects = {}
        self._draw_grid()

    def _calc_cell(self, width, height):
        # 格子像素大小：大地图自动缩小，画布不超过约 700px
        return max(10, min(18, 700 // max(width, height)))

    def _resize(self, width, height):
        # 行列尺寸变化（新行/列加在最后一行/列之后）：
        # 丢弃超出新范围的墙，重算格子大小并重画整张网格
        # 仅画墙阶段可用：选起点阶段改尺寸会让起点坐标失效
        if self.phase != 'draw':
            return
        if not (1 <= width <= MAX_SIZE and 1 <= height <= MAX_SIZE):
            return
        self.walls = {(x, y) for (x, y) in self.walls if x < width and y < height}
        self.width, self.height = width, height
        self.cell = self._calc_cell(width, height)
        self.canvas.config(width=width * self.cell, height=height * self.cell)
        self.canvas.delete('all')
        self.rects = {}
        self._draw_grid()

    def _add_row(self):
        self._resize(self.width, self.height + 1)

    def _remove_row(self):
        self._resize(self.width, self.height - 1)

    def _add_col(self):
        self._resize(self.width + 1, self.height)

    def _remove_col(self):
        self._resize(self.width - 1, self.height)

    def _draw_grid(self):
        # 画出全部格子，记录每个格子的矩形 id，方便之后重涂颜色
        for x in range(self.width):
            for y in range(self.height):
                r = self.canvas.create_rectangle(
                    x * self.cell, y * self.cell,
                    (x + 1) * self.cell, (y + 1) * self.cell,
                    fill='white', outline='gray')
                self.rects[(x, y)] = r

    def _repaint(self, x, y):
        # 依据当前状态重涂一个格子：起点红 > 墙黑 > 空地白
        if self.start == (x, y):
            color = 'red'
        elif (x, y) in self.walls:
            color = 'black'
        else:
            color = 'white'
        self.canvas.itemconfig(self.rects[(x, y)], fill=color)

    def _cell_at(self, event):
        # 把鼠标事件换算成格子坐标，超出画布返回 None
        x, y = event.x // self.cell, event.y // self.cell
        if 0 <= x < self.width and 0 <= y < self.height:
            return x, y
        return None

    def on_click(self, event):
        pos = self._cell_at(event)
        if pos is None:
            return
        if self.phase == 'draw':
            # 画墙阶段：点击切换 墙 <-> 空地
            if pos in self.walls:
                self.walls.remove(pos)
            else:
                self.walls.add(pos)
            self._repaint(*pos)
        elif self.phase == 'start':
            # 选起点阶段：只能点白格，点墙没反应；新起点出现后旧起点恢复白色
            if pos in self.walls:
                return
            old = self.start
            self.start = pos
            if old is not None:
                self._repaint(*old)
            self._repaint(*pos)
            # 已选择起点，确认键由灰变可用
            self.confirm_btn.config(state='normal')

    def on_confirm(self):
        if self.phase == 'draw':
            if len(self.walls) >= self.width * self.height:
                messagebox.showwarning('提示', '至少要留一个空地作为守卫的活动空间')
                return
            self.phase = 'start'
            # 进入选起点阶段后，行列增减会破坏已画布局，禁用
            for b in self.size_btns:
                b.config(state='disabled')
            self.confirm_btn.config(state='disabled')  # 未选起点前确认键置灰
            self.info.config(text='阶段 2：点击白色格子设置守卫起点（红色），设置后点【确认】完成')
        elif self.phase == 'start':
            self.phase = 'done'
            self.root.destroy()

    def run(self):
        # 进入主循环，窗口关闭后返回 (map1, start)；未完成就关闭窗口返回 None
        # on_confirm 完成时窗口已销毁（phase=done），此时不再进入 mainloop
        if self.phase != 'done':
            self.root.mainloop()
        if self.phase != 'done':
            return None
        map1 = [[1 if (x, y) in self.walls else 0 for y in range(self.height)]
                for x in range(self.width)]
        return map1, self.start


def edit_map(width, height):
    # 打开编辑窗口，返回 (map1, start) 或 None（用户中途关闭窗口）
    return MapEditor(width, height).run()


def ask_size():
    # 询问地图长宽，上限 50x50
    while True:
        try:
            w = int(input(f'width（1-{MAX_SIZE}）: ').strip())
            h = int(input(f'height（1-{MAX_SIZE}）: ').strip())
        except ValueError:
            print('请输入整数')
            continue
        if 1 <= w <= MAX_SIZE and 1 <= h <= MAX_SIZE:
            return w, h
        print(f'长宽必须在 1 到 {MAX_SIZE} 之间，请重新输入')


def _ask_name_and_save(map1, start):
    # 询问地图名称并保存，重名时询问是否覆盖
    presets = map_loader.list_presets()
    while True:
        name = input('请输入地图名称（保存到 maps/）：').strip()
        if not name:
            print('名称不能为空')
            continue
        if name in presets:
            if input(f'{name} 已存在，覆盖？（y/n）：').strip().lower() != 'y':
                continue
        break
    path = map_loader.save_map(name, map1, start)
    print(f'已保存到 {path}')


def run_embedded():
    # 被 user_input.choose_map 引用的入口
    # 返回守卫起点 start；返回 None 表示用户中途取消
    w, h = ask_size()
    result = edit_map(w, h)
    if result is None:
        return None
    map1, start = result
    if input('是否保存该地图到 maps/？（y/n，直接回车默认 n）：').strip().lower() == 'y':
        _ask_name_and_save(map1, start)
    return start


def run_standalone():
    # 独立启动的入口：画完默认保存
    w, h = ask_size()
    result = edit_map(w, h)
    if result is None:
        print('未完成绘制，已退出')
        return
    map1, start = result
    print('绘制完成，开始保存。')
    _ask_name_and_save(map1, start)


if __name__ == '__main__':
    run_standalone()

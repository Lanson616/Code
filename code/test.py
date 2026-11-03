# ==================== test：多种搜索算法对比 ====================
# 像 main 一样输入地图，然后对所有注册的搜索算法跑同样的搜索任务，
# 每个算法开始前清空所有记忆化缓存，保证计时公平。
# 最后打印对比表格，并生成耗时 / 步数对比条形图（保存为 comparison.png）。
import time

import matplotlib
matplotlib.use('TkAgg')          # 强制有界面后端；若报错改 'QtAgg'
import matplotlib.pyplot as plt

import constants
import user_input
import search_registry
from simulation import (visible_mask_at, find_all_empty_mask,
                        block_cache, can_see_cache, visible_mask_at_cache, check_cache)
from main import solve_single, solve_double


def clear_caches():
    # 清空 simulation 的全部记忆化缓存，让每个算法都从冷启动开始计时
    block_cache.clear()
    can_see_cache.clear()
    visible_mask_at_cache.clear()
    check_cache.clear()


def benchmark_one(name, algo, start, test_double=False):
    # 测一个算法，返回结果字典
    clear_caches()
    row = {'algo': name}
    print(f'\n--- 正在测试 {name}（单人搜索，12 个初始面向）---')
    t0 = time.perf_counter()
    ok, path, step, face = solve_single(algo, start)
    t1 = time.perf_counter()
    row.update(single_ok=ok, single_time=t1 - t0,
               single_steps=step if ok else None, single_face=face)
    if ok:
        print(f'{name} 单人：{step} 步，耗时 {t1 - t0:.3f} 秒')
    else:
        print(f'{name} 单人无解，耗时 {t1 - t0:.3f} 秒')

    # 双人搜索非常慢，只有明确要求（且单人无解）时才测
    if test_double and not ok:
        print(f'--- 正在测试 {name}（双人搜索，可能很慢）---')
        t0 = time.perf_counter()
        ok2, path2, step2, faces = solve_double(algo, start)
        t1 = time.perf_counter()
        row.update(double_ok=ok2, double_time=t1 - t0,
                   double_steps=step2 if ok2 else None, double_faces=faces)
        print(f'{name} 双人：{step2 if ok2 else "无解"}，耗时 {t1 - t0:.3f} 秒')
    return row


def print_table(rows):
    # 打印对比表格
    print('\n==================== 对比结果 ====================')
    print(f'{"算法":<8}{"单人有解":<8}{"单人步数":<8}{"单人耗时(s)":<12}'
          f'{"双人有解":<8}{"双人步数":<8}{"双人耗时(s)":<12}')
    for r in rows:
        s_ok = '是' if r['single_ok'] else '否'
        s_steps = r['single_steps'] if r['single_ok'] else '-'
        d_ok = '是' if r.get('double_ok') else ('否' if r.get('double_ok') is not None else '-')
        d_steps = r['double_steps'] if r.get('double_ok') else '-'
        d_time = f"{r['double_time']:.3f}" if r.get('double_time') is not None else '-'
        print(f"{r['algo']:<8}{s_ok:<8}{s_steps:<8}{r['single_time']:<12.3f}{d_ok:<8}{d_steps:<8}{d_time:<12}")


def plot_comparison(rows, has_double):
    # 画对比条形图：单一人手一份（耗时、步数）；若测了双人再补两幅
    names = [r['algo'] for r in rows]
    ncols = 4 if has_double else 2
    fig, axes = plt.subplots(1, ncols, figsize=(6 * ncols, 5))

    def bar(ax, values, title, unit, labels=None, colors=None):
        bars = ax.bar(names, values, color=colors)
        ax.set_title(title)
        ax.set_ylabel(unit)
        ax.grid(axis='y', alpha=0.4)
        for i, (bar, v) in enumerate(zip(bars, values)):
            text = labels[i] if labels else f'{v:.3f}'
            ax.annotate(text, xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
                        ha='center', va='bottom')

    single_times = [r['single_time'] for r in rows]
    single_steps = [r['single_steps'] if r['single_ok'] else 0 for r in rows]
    single_labels = [str(r['single_steps']) if r['single_ok'] else 'no solution' for r in rows]
    single_colors = ['#4C9BE8' if r['single_ok'] else '#D9534F' for r in rows]

    bar(axes[0], single_times, 'Single-guard total time (12 initial facings)', 'seconds')
    bar(axes[1], single_steps, 'Single-guard optimal steps (lower is better)', 'steps',
        labels=single_labels, colors=single_colors)

    if has_double:
        double_times = [r.get('double_time') or 0 for r in rows]
        double_steps = [r['double_steps'] if r.get('double_ok') else 0 for r in rows]
        double_labels = [str(r['double_steps']) if r.get('double_ok') else
                         ('no solution' if r.get('double_ok') is not None else 'not tested') for r in rows]
        double_colors = ['#5CB85C' if r.get('double_ok') else
                         ('#D9534F' if r.get('double_ok') is not None else '#B0B0B0') for r in rows]
        bar(axes[2], double_times, 'Double-guard total time', 'seconds')
        bar(axes[3], double_steps, 'Double-guard optimal steps (lower is better)', 'steps',
            labels=double_labels, colors=double_colors)

    fig.suptitle('Search Algorithm Comparison')
    fig.tight_layout()
    save_path = constants.output_path('comparison.png')
    fig.savefig(save_path, dpi=150)
    print(f'\n对比图已保存为 {save_path}')
    plt.show(block=True)


def main():
    # ---------- 输入（和 main 一样） ----------
    user_input.read_size_and_delta()
    user_input.input2()
    start = user_input.input_start()
    find_all_empty_mask()

    # ---------- 是否测双人 ----------
    print('\n注意：双人搜索非常慢。单人无解的地图才会涉及双人搜索。')
    ans = input('单人无解时是否继续测双人搜索？（y/n，直接回车默认 n）：').strip().lower()
    test_double = (ans == 'y')

    # ---------- 逐个算法计时 ----------
    all_names = search_registry.names()
    print(f'\n共注册 {len(all_names)} 个算法：{"、".join(all_names)}')
    rows = [benchmark_one(name, search_registry.get(name), start, test_double)
            for name in all_names]

    # ---------- 输出对比 ----------
    print_table(rows)
    has_double = any(r.get('double_time') is not None for r in rows)
    plot_comparison(rows, has_double)


if __name__ == '__main__':
    main()

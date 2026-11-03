## 项目结构 ##

项目根目录包含本 README、更新日志（CHANGELOG.md）、运行产物 output/；
所有源代码在 code/ 子目录中，已拆分为多个模块，入口是 code/main.py：

| 文件（均在 code/ 内） | 职责 |
|---|---|
| main.py | 主流程：选地图 → 选算法 → 单人搜索 → 双人搜索 → 动画输出。solve_single / solve_double 返回带计时的结果 dict，供 test 复用；print_solution / print_time_table / export_solution 是共享的输出与导出函数 |
| constants.py | 常数与共享状态（width / height / map1 / delta 等）+ output_path 输出路径工具（自动创建 output/） |
| user_input.py | 用户输入。choose_map() 是地图入口（预设 / 文件 / 随机 / 手动四种来源）；另有 read_delta、manual_map（手动逐行输图，大小自动识别）、input_start |
| map_loader.py | 地图解析与生成：parse_map_text 解析地图文本 / load_file 文件读取 / load_preset 预设加载（maps/ 文件夹）/ generate_random 随机生成（保证全空地与起点连通）；地图大小一律从内容自动读取；换图时自动清空 simulation 缓存 |
| maps/ | 预设示例地图库（code/maps/，.txt 文件，见下方格式说明） |
| simulation.py | 视觉（block 遮挡 / can_see 可见性 / visible_mask_at 视野位掩码，均带缓存）+ 运行规则（check 安全性检查 / apply_one 动作系统 / next_step_generator）+ find_all_empty_mask + clear_caches |
| search_registry.py | 搜索算法注册表。接入新算法：写一个模块提供 search_single / search_double（返回 (是否有解, 路径, 步数)），import 并加进 ALGORITHMS 即可 |
| BFS_search.py | BFS 搜索（search1 单人 / search2 双人，带步数上界剪枝）；search_single / search_double 是接口别名 |
| visualization.py | 重放（replay_single / replay_double）与动画（quick_anim，可存 gif）：渐变手电筒视野锥 + 金色边界线，坐标轴固定为地图范围、网格画在格子边界 |
| test.py | 算法对比基准：像 main 一样输入，对所有注册算法计时跑同样的任务；输出对比表格（最少人数 / 步数 / 守卫面向 / 单双人耗时），每个有解算法导出 output/solution_<算法名>.txt，并生成 output/comparison.png 对比图（图表为英文） |
| output/ | 运行产物：single.gif / double.gif（动画）、solution.txt 或 solution_<算法名>.txt（最优路径）、comparison.png（对比图）。位置固定在项目根目录（代码文件夹的上一级），与启动命令所在目录无关；已加入 .gitignore |

## 地图文件格式 ##

code/maps/ 里的预设和任意自定义地图都用同一格式（.txt）：

```
# 以 # 开头是注释，空行跳过
S....
.###.
.###.
.###.
.....
```

- `.` 或 `0` = 空地，`#` 或 `1` = 墙，`S` = 守卫起点（省略 S 则运行时手动输入起点坐标）
- 每行字符数 = 地图宽度，行数 = 高度；左上角是 (0,0)，x 向右，y 向下
- 地图大小一律从内容自动读取，任何来源都不需要手动输入长宽

预设说明：tiny（带中心柱，单人 4 步）/ ring（回字形，单人 10 步）单人可解，演示快；hall / plus / rooms 单人无解，运行会进入较慢的双人搜索。

## 运行方式 ##

```
cd code
python3 main.py    # 选地图、选算法，求解并播放动画，结果导出到 output/
python3 test.py    # 对所有注册算法做性能对比，输出表格和对比图
```

## 备注 ##
更新日志：
- 将main文件拆分成不同模块
- 添加算法对比模块（待测试）
- 优化用户输入，添加预设地图、随机地图（待测试）
- 修复并优化了视觉化模块中角度转换的问题
- 添加了算法性能输出
- 新增CHANGELOG（伪造）

待完成：
- 添加更多算法：深度优先、暴力求解、其他搜索算法
- 优化单双多人算法切换
- 测试算法对比功能，随机地图功能
- 添加地图制作器模块
- 制作更多复杂仿真地图（房间、博物馆、学校、迷宫）
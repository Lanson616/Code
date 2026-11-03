## 项目结构 ##

代码已拆分为多个模块，入口是 main.py：

| 文件 | 职责 |
|---|---|
| main.py | 主流程：串联所有模块（输入 → 单人搜索 → 双人搜索 → 动画输出） |
| constants.py | 常数与共享状态（width / height / map1 / delta 等），其他模块用 constants.xxx 读写 |
| user_input.py | 用户输入（read_size_and_delta / input1 坐标输墙 / input2 按行输图 / input_start） |
| vision.py | 视觉模块（block 遮挡 / can_see 可见性 / visible_mask_at 视野位掩码，均带缓存） |
| rules.py | 模拟运行规则（check 安全性检查 / apply_one 动作系统 / next_step_generator） |
| search.py | 搜索算法（search1 单人 / search2 双人，BFS + 步数上界剪枝） |
| visualization.py | 重放（replay_single / replay_double）与动画（quick_anim，可存 gif） |

## 说明 ##
原计划虽然没有打算求最短步数，但是我写的时候发现很容易实现所以就顺手写掉了
最后返回来的东西直接到主函数里面扣出来就行，path，best_face, step_min都可以直接扣
双人搜索的速度很慢，但是我懒得优化了
代码想review的话注释应该挺清楚

test1.py 已删除，它的功能（简洁的动作系统、修好的 input2 重输逻辑）已并入 rules.py 和 user_input.py
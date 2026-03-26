# 符塔夜行

一个基于 `Python + pygame` 开发的轻量级东方奇幻肉鸽原型项目。  
当前版本为 `v1`，已经具备可玩的多关卡成长、双模式菜单、20 技能池、自动战斗与本地排行榜等核心功能。

## 当前玩法

- 模式
  - `闯关模式`：共 4 关，完成第 4 关后通关结算
  - `无限模式`：按关卡循环推进，记录本地排行榜
- 关卡成长
  - 每关从 20 个技能中分配 5 个本关可升级技能
  - 每个技能最高 `Lv.3`
  - 当本关 5 个技能全部升满后，进入下一关
- 战斗节奏
  - 玩家自动释放已解锁技能
  - 击败敌人会掉落经验，靠近后会自动吸取
  - 进入下一关时回复 20 点生命，并重置本关经验等级

## v1 已有功能

- 菜单支持：
  - `闯关模式`
  - `无限模式`
  - `说明`
  - `窗口 / 全屏` 运行期切换
- 说明界面支持：
  - 操作说明
  - 20 技能图鉴
  - 技能详情滚轮查看
- 战斗系统支持：
  - 多关卡成长制
  - 20 技能池与 4 组技能分配
  - 技能三级成长
  - 自动吸取掉落物
  - 脚本波次 + 无限导演刷怪
- UI 支持：
  - 关卡说明弹窗
  - 起始技能选择
  - 三选一卡片升级面板
  - 战斗内技能栏
  - 无限模式本地排行榜

## 技术栈

- Python 3.12
- pygame 2.6
- unittest
- PyInstaller

## 运行方式

### 1. 安装依赖

```powershell
pip install -r requirements.txt
```

### 2. 启动游戏

```powershell
python main.py
```

## 测试与校验

运行单元测试：

```powershell
python -m unittest discover -s tests
```

运行编译检查：

```powershell
python -m compileall game tests main.py
```

## 打包

项目已经包含打包产物和 `.spec` 文件。  
如果需要重新打包，推荐先使用 `onedir` 模式：

```powershell
pyinstaller --noconfirm --clean --windowed --name 符塔夜行 --add-data "assets;assets" main.py
```

打包完成后可执行文件位于：

```text
dist/符塔夜行/符塔夜行.exe
```

## 目录结构

```text
game/
├─ main.py
├─ assets/
│  ├─ data/
│  └─ images/
├─ game/
│  ├─ content/
│  ├─ core/
│  ├─ entities/
│  ├─ models/
│  ├─ scenes/
│  ├─ systems/
│  └─ ui/
├─ save_data/
├─ tests/
└─ requirements.txt
```

## 代码结构说明

- `game/app.py`
  管理 pygame 初始化、主循环、场景切换、窗口/全屏切换
- `game/scenes/`
  管理菜单、战斗、结算等流程
- `game/systems/`
  管理战斗、刷怪、成长和移动规则
- `game/ui/`
  管理 HUD、升级面板、技能图鉴等显示层
- `assets/data/`
  管理敌人、技能、波次等 JSON 数据
- `save_data/`
  管理无限模式排行榜

## 当前状态

这是一个偏“工程化原型”的 v1：

- 已有完整的基础玩法循环
- 已有数据驱动的技能和波次系统
- 已有本地排行榜和打包能力
- 美术资源仍以程序绘制和占位资源为主

## 后续可继续扩展的方向

- 接入正式 PNG 角色、敌人、技能图标和背景
- 增加更多敌人类型和关卡机制
- 增加音效与背景音乐
- 增加更完整的结算页和数值统计
- 增加 Boss、精英怪和特殊事件房

## License

当前仓库默认未附带正式开源许可证。  
如果准备公开到 GitHub，建议在发布前补充 `LICENSE` 文件并明确资源授权范围。

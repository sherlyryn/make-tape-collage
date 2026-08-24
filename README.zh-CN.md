# Make Tape Collage

**简体中文** | [English](README.md)

将照片或简短描述转化为干净、具有触感的和纸胶带拼贴作品。该 skill 也支持忠实保留原始照片，并在同一张连续的暖白手账纸上搭配一幅紧凑的胶带重构图案。

![柔和结构胶带拼贴参考](assets/style-references/reference-10-soft-structural-collage.png)

## 主要特点

- 可将食物、宠物、物件、植物、人物、旅行场景、建筑或情绪提炼为结构完整的胶带平面。
- 主要使用宽型和中型胶带、纯色或常见基础纹样，并保留半透明叠压、纤维边缘与浅层接触阴影。
- 强调留白与编辑设计感，避免把纸面填满无关的手账装饰。
- 支持忠实保留照片：保留区域内的照片像素不会被重绘、调色、修饰、拉伸或生成式替换。
- 生成一张连续、干净的暖白手账纸，具有可辨识的不规则细纤维、轻微纸浆起伏和少量断续扫描痕迹。
- 使用确定性的本地合成处理排版、纸张、照片安装效果、阴影和文字，避免生成纸张出现接缝或背景色差。
- 除非用户明确要求，否则不会加入票据、标签、印章、封条、无意义小字、可见工具或无关复古素材。

## 作例

| 保留原照片 · SWEET PAIR | 保留原照片 · CROSSED FORMS |
| --- | --- |
| ![保留原照片作例：甜点组合 SWEET PAIR](assets/examples/example-01-sweet-pair.png) | ![保留原照片作例：雕塑 CROSSED FORMS](assets/examples/example-02-crossed-forms.png) |
| **文字描述生成 · 雨天窗景** | **照片转换 · 猫与花盆** |
| ![描述生成作例：雨天窗边的咖啡桌](assets/examples/example-03-rainy-window.png) | ![照片转换作例：猫与花盆](assets/examples/example-04-cat-and-pot.png) |

前两张为"保留原照片"模式：左侧（或上方）忠实保留原照片，右侧（或下方）的暖白纸面上放置紧凑的胶带重构图案与褪色打字机标题。后两张为纯胶带拼贴：原照片不进入成品，主体完全由胶带重建。

## 使用方法

可以使用 `$make-tape-collage` 显式调用，也可以直接描述明确的和纸胶带、胶带画或拼贴手账需求。

### 将照片转成胶带拼贴

```text
使用 $make-tape-collage，把这张猫咪照片做成和纸胶带拼贴手账。
```

```text
使用 $make-tape-collage，把这张建筑照片做成安静的胶带拼贴海报，不要文字。
```

这种模式会用胶带重新构成主体；除非明确要求保留原图，否则原照片不会出现在最终作品中。

### 保留原始照片

```text
使用 $make-tape-collage，把这张照片做成胶带拼贴手账，并保留原图。
```

```text
使用 $make-tape-collage，保留这张照片，并在胶带图案旁写上“TOKYO”。
```

这种模式会把照片和胶带重构放在互相独立的版面区域。系统只生成透明背景的胶带主体，再在本地完成最终合成，以控制原图像素和纸张纹理。

### 根据描述生成

```text
使用 $make-tape-collage，生成一张关于雨天独处的蓝灰色胶带拼贴海报。
```

```text
使用 $make-tape-collage，生成一张关于咖啡厅独处的暖色胶带拼贴海报。
```

纯描述生成默认不包含文字。

### 精确修改已有结果

```text
保持已经确认的胶带拼贴不变，只把标题放大并把图案移到左下角。
```

```text
保持照片像素和排版不变，只加强纸张纤维的可见程度。
```

## 默认行为

| 项目 | 默认设置 |
| --- | --- |
| 最终画幅 | 图片类作品默认使用竖版 `3:4`（宽:高） |
| 照片转胶带拼贴 | 用约 10–18 块连贯胶带构成一个可辨认主体；必要时加入最多两个来自原图环境的克制呼应元素 |
| 保留竖版照片 | 照片在左，纸张区在右 |
| 保留横版或方形照片 | 照片在上，纸张区在下 |
| 保留原图的版面占比 | 照片约 50%，纸张约 50% |
| 照片完整性 | 保留像素不变，不重绘、不调色、不修图、不拉伸、不叠加纹理滤镜 |
| 照片裁切 | 仅在必要时裁切，最多移除原图面积的 20%；主体完整性更重要时不裁切 |
| 照片安装效果 | 无白色相框，外露边缘带自然手撕纤维，并使用克制的环境阴影与接触阴影 |
| 保留原图模式的胶带图案 | 图案与标题组成紧凑文字组，放在平衡构图的角落，约占纸张区 20% |
| 背景纸 | 干净暖白、可见纤维、低对比、无重复纹理，不使用污渍或过度做旧 |
| 图片类默认文字 | 一至三个英文单词的客观标题；用户指定文字或明确不要文字时除外 |
| 纯描述默认文字 | 无文字 |
| 生成次数 | 默认只生成一次胶带主体；仅当主体识别或胶带材质失败时，最多进行一次针对性重试 |

用户的明确指令始终优先于这些默认值。

## 视觉系统

默认采用 **柔和结构场景提炼（Soft structural scene distillation）**：

- 保留一至三个最重要的识别锚点。
- 使用相邻的明、中、暗胶带面表达透视或体积，不使用绘制轮廓线。
- 胶带拼贴保持平面、正面和浅层叠压，不做成立体纸雕。
- 从原图提取约四至六种低饱和颜色，最多保留一个克制的暖色强调。
- 优先使用纯色胶带和条纹、格子、方格、波点等基础纹样。
- 明显褶皱面积控制在拼贴图案区域的约 25% 以下。
- 保持充足留白，并让图案与文字远离纸张边缘。

随 skill 提供的参考图只用于约束材质、抽象程度和构图，禁止复制其中的具体主体。

## 保留原图模式的工作流程

1. 先运行 `compose_direct_split.py --plan`，确定最终比例、版面方向、裁切上限与像素坐标。
2. 图像生成仅创建一个独立、无文字、透明 RGBA 背景的胶带主体。
3. 合成器为整张画布生成唯一且连续的手账纸表面。
4. 原始照片像素在不使用像素级滤镜的情况下被安装到纸面。
5. 手撕边缘、克制阴影、胶带位置和精确文字通过确定性方法添加。
6. 最终检查画幅比例、裁切比例、原图像素完整性、透明通道、纸纹连续性和安全边距。

这一分离流程可以避免生成图中的白色矩形、透明棋盘、污渍或颜色偏差进入最终纸张区域。

## 手动使用合成器

合成器主要由 skill 自动调用，也可以在安装 Python 和 Pillow 后单独运行。

预览计算后的排版：

```bash
python scripts/compose_direct_split.py \
  --photo path/to/photo.png \
  --crop-mode none \
  --plan
```

使用透明胶带主体合成保留原图的作品：

```bash
python scripts/compose_direct_split.py \
  --photo path/to/photo.png \
  --motif path/to/motif-rgba.png \
  --output path/to/final.png \
  --crop-mode none \
  --caption "QUIET MORNING"
```

运行 `python scripts/compose_direct_split.py --help` 可以查看排版、画幅、裁切、图案、纸张、阴影与文字选项。`--paper-panel` 仅用于兼容旧素材；新作品应使用 `--motif`。

## 安装

```bash
git clone https://github.com/<你的用户名>/make-tape-collage.git
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
cp -R make-tape-collage \
  "${CODEX_HOME:-$HOME/.codex}/skills/make-tape-collage"
```

也可以手动下载本仓库，将完整文件夹放在 `$CODEX_HOME/skills/make-tape-collage/`。Windows 默认安装中通常为：

```text
%USERPROFILE%\.codex\skills\make-tape-collage\
```

如果 skill 没有立即出现，请重启 Codex，使 skill 目录被发现；随后可使用 `$make-tape-collage` 或匹配的自然语言请求调用。

默认使用内置图像生成功能。手动运行合成器需要 Python 和 Pillow。

## 文件结构

```text
make-tape-collage/
|-- SKILL.md
|-- README.md
|-- README.zh-CN.md
|-- LICENSE
|-- agents/
|   `-- openai.yaml
|-- assets/
|   |-- style-references/
|   `-- examples/
|-- references/
|   |-- prompt-recipes.md
|   `-- style-system.md
`-- scripts/
    `-- compose_direct_split.py
```

## 定制与维护

- 修改 [`references/style-system.md`](references/style-system.md)，可调整视觉语言、比例、色彩、纸张、排除项和保留原图规则。
- 修改 [`references/prompt-recipes.md`](references/prompt-recipes.md)，可调整生成提示模板和示例。
- 修改 [`scripts/compose_direct_split.py`](scripts/compose_direct_split.py)，可调整确定性的版面几何、照片安装方式、纸张合成、阴影与文字。
- 可将经过筛选的图片加入 [`assets/style-references/`](assets/style-references/)，并在视觉系统中明确它们各自的参考作用。参考图只能作为风格证据，不能作为可复用的主体模板。
- 让 [`SKILL.md`](SKILL.md) 专注于调用路由、核心流程和不可破坏的约束。

修改 skill 后，可使用 Skill Creator 附带的验证器检查：

```bash
python path/to/skill-creator/scripts/quick_validate.py path/to/make-tape-collage
```

## 已知边界

- 纯胶带转换不保证保留人物面部身份。
- 复杂场景会主动简化为少量识别锚点和环境呼应。
- 保留原图模式中的精确文字通过确定性排版添加，避免依赖生成模型绘制自由文字。
- 只有用户明确要求“保留原图”“显示原照片”等内容时，才会启用原图保留模式。

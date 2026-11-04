# When Restoration Gains Reverse in Camera Attribution

论文《When Restoration Gains Reverse in Camera Attribution》的代码与保存数据包。

## 论文研究什么

源相机归因通过图像中的微弱设备痕迹识别拍摄相机。图像恢复可能降低重建误差，却减少正确归因。本文研究给定恢复操作后，这些变化出现在哪个阶段：评分与候选排名、候选接受，还是最终输出答案。配对幅度和分量交换进一步检验局部评分响应能够解释哪些真实排名损失。

包内保存数据对应的主要发现包括：

- **评分组成改变恢复响应。** CSAFE原始D+L正确排名为215→203，固定同一残差、删除学习logit后的D控制为218→221；两个ForensiCam队列的室内子集呈相反交互。
- **候选集合与首位输出可能方向相反。** 在所报告的20%任错集合校准预算、状态分别校准条件下，CSAFE正确单元素集合为152→160，正确winner为211→176。集合增量的配对范围为[-9, 25]；更严格预算和共享截止会改变比较。
- **机制解释按真实损失核算。** 双向幅度交换在同一父图上同时复现并挽回BM3D的2/13、Restormer的5/13实际损失。

## 如何运行

使用Python 3.10或更新版本。先检查文件完整性：

```sh
python scripts/check_package.py
```

仅用Python标准库复现核心排名、交叉答案、附加队列分量状态、Gaussian幅度覆盖和22项条件范围：

```sh
python scripts/reproduce.py --core-only
```

安装依赖后，完整入口另计算raw ROC/DET、AUC及配对范围：

```sh
python -m pip install -r requirements.txt
python scripts/reproduce.py
```

核对4758行既有raw接受路径、8916个固定权重合并配置和81204个精确有理候选分数：

```sh
python scripts/reproduce_paths_precision.py
```

程序将结果与`expected/`核对，生成文件写入`results/`，成功后打印`PASS_...`。raw路径原本已存在；精度检查针对相同保存D/L和相同表示权重的合并算术。

可选绘图：

```sh
python scripts/plot_raw_paths.py
python scripts/plot_verification.py
```

验证曲线绘图需先运行完整复现。raw路径绘图读取保存参考结果，图件统一写入`results/figures/`。

## 文件与论文的对应关系

|论文分析|主要数据（位于data/）|参考结果（位于expected/）|
|---|---|---|
|固定残差评分与排名|core_scores.json、native_components.json|core_ranks.csv、native_rank_summary.csv|
|接受与输出|core_scores.json、raw_path_inputs.json|CSAFE_crossed_answers.csv、raw_paths.csv|
|实际损失的幅度覆盖|amplitude_scores.json|amplitude_counts.csv、amplitude_coverage.csv|
|配对条件范围|paired_contrasts.csv|conditional_ranges.csv|
|raw验证及同型号中心化|raw_verification_scores.json、resampling_weights.npz、classical_centering_scores.json|raw_ROC_DET.csv、raw_verification_AUC.csv、classical_centering_answers.csv|
|固定权重合并精度|merge_components.json|merge_precision_rows.csv|

`src/camera_attribution/`保存评分、决定、统计和验证实现；`scripts/`提供运行与绘图入口；`docs/`解释协议和第三方来源。`data/PROVENANCE.json`记录来源身份与哈希，父图、设备、候选顺序和处理状态配对均保留。

## 数据与结论范围

CSAFE与核心ForensiCam共有394个评价父项；附加十台原生JPEG队列的160个评价父项单独报告，每台F50参考设置保持。不同状态和JPEG质量复用父项。

详细说明见[协议](docs/PROTOCOL.md)、[第三方来源](docs/THIRD_PARTY_NOTICES.md)。第三方图像及权重按原来源条款获取。 


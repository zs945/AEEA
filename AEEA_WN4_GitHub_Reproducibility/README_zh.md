# AEEA–DeepSeek 超大规模 Set D–WN4 复现说明

本项目包含超大规模 Set D–WN4 实例、完整AEEA代码以及DeepSeek调用审计记录。

运行后，每次API尝试都会保存：请求时间、代数、重试次数、请求模型、API返回模型、系统指纹、完整提示词、原始最终输出、JSON解析结果、可行性检查结果、请求/接受候选数、token用量、缓存命中情况、延迟和费用估计。总配置保存在`run_manifest.json`，汇总保存在`run_summary.json`。

## temperature和top-p怎么处理

原代码调用的是`deepseek-reasoner`思考模型。DeepSeek官方说明思考模式下`temperature`和`top_p`不生效。因此本项目不向API传递这两个参数，并在日志中记为`null`和“not applicable in thinking mode”。原`LLMAgent`类中虽然写过`temperature=0.1`，但该值没有传入API，不能在论文中声称原实验使用了0.1。

DeepSeek Chat Completions也没有可用的LLM随机种子参数，因此只记录进化算法和NumPy随机种子；LLM seed如实写为不可用。

## 运行前

1. 建议立即撤销并更换曾经硬编码在原项目中的API密钥。
2. 安装依赖：`python -m pip install -r requirements.txt`。
3. 在系统环境变量中设置`DEEPSEEK_API_KEY`，不要写入代码。
4. 根据实验实际运行日期填写`pricing.json`。价格未经确认时，程序不会伪造费用。

PowerShell设置密钥：

```powershell
$env:DEEPSEEK_API_KEY="your-key"
```

正式运行：

```powershell
python run_experiment.py --seed 4 --population-size 50 --generations 100 --crossover-rate 0.8 --mutation-rate 0.1 --llm-guided-ratio 0.3 --run-id setD_wn4_seed4
```

两代连通测试：

```powershell
python run_experiment.py --seed 4 --population-size 6 --generations 2 --run-id smoke_test
```

所有结果保存在`artifacts/<run-id>/`。上传GitHub前检查完整提示词和原始输出，确认其中没有不应公开的信息。

## 选择与Agent个体数量处理

正式AEEA在精英保留、提示上下文提取和三元父代锦标赛中统一采用非支配等级与归一化拥挤距离：优先选择非支配等级较低的个体，同等级时优先选择拥挤距离较大的个体，仍相同时按原位置确定。上述决策不对三个目标值直接求和。

当LLM生成比例大于零时，每个进化代调用一次Agent。若通过验证和修复的个体多于目标数量，则按上述Pareto规则筛减；若少于目标数量，则用遗传操作生成的子代补齐，保证下一代种群规模不变。

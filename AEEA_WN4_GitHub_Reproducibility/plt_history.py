import matplotlib.pyplot as plt
import numpy as np

def plot_pareto_trend_subplots(history_pareto, save_path=None, show=False):
    """
    绘制三个目标指标在迭代过程中的演化趋势（分子图）
    :param history_pareto: List of [individuals, objective_values] per generation
    :param save_path: Optional path to save the figure
    """
    generations = len(history_pareto)
    obj1_min, obj2_min, obj3_min = [], [], []
    obj1_mean, obj2_mean, obj3_mean = [], [], []

    for _, vals in history_pareto:
        vals = np.array(vals)
        obj1_min.append(np.min(vals[:, 0]))   # caigou_cost
        obj2_min.append(np.min(vals[:, 1]))   # total_delay
        obj3_min.append(np.min(vals[:, 2]))   # total_warehousing

        obj1_mean.append(np.mean(vals[:, 0]))
        obj2_mean.append(np.mean(vals[:, 1]))
        obj3_mean.append(np.mean(vals[:, 2]))

    x = np.arange(1, generations + 1)

    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    titles = ['Caigou Cost', 'Total Delay', 'Total Warehousing']
    colors = ['tab:blue', 'tab:orange', 'tab:green']
    mins = [obj1_min, obj2_min, obj3_min]
    means = [obj1_mean, obj2_mean, obj3_mean]

    for i in range(3):
        ax = axes[i]
        ax.plot(x, means[i], label='Average', color=colors[i], linewidth=2)
        ax.plot(x, mins[i], label='Best', color=colors[i], linestyle='--')
        ax.set_title(titles[i], fontsize=13)
        ax.set_xlabel('Generation')
        ax.set_ylabel('Value')
        ax.grid(True)
        ax.legend()

    plt.suptitle('Evolution of Objectives Across Generations', fontsize=15)
    plt.tight_layout(rect=[0, 0, 1, 0.95])

    if save_path:
        plt.savefig(save_path)
    if show:
        plt.show()
    plt.close(fig)

import os
import matplotlib.pyplot as plt


PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

output_file = os.path.join(
    PROJECT_ROOT,
    "results",
    "figures",
    "adaptive_mean_comparison.png"
)


methods = [
    "Original GA",
    "Adaptive GA"
]

mean_fitness = [
    4665.32,
    4524.94
]

std_deviation = [
    1569.04,
    813.32
]


os.makedirs(
    os.path.dirname(output_file),
    exist_ok=True
)


plt.figure(figsize=(8, 5))

plt.bar(
    methods,
    mean_fitness,
    yerr=std_deviation,
    capsize=6
)

plt.ylabel("Mean Fitness")

plt.title(
    "Mean Fitness Comparison"
)

plt.grid(
    axis="y"
)

plt.tight_layout()

plt.savefig(output_file)

plt.show()

print(
    "Graph saved to: "
    "results/figures/adaptive_mean_comparison.png"
)
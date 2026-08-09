import os
import csv

import matplotlib.pyplot as plt


PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

input_file = os.path.join(
    PROJECT_ROOT,
    "results",
    "data",
    "generation_comparison.csv"
)

output_file = os.path.join(
    PROJECT_ROOT,
    "results",
    "figures",
    "generation_comparison.png"
)


generations = []
fitness_values = []


with open(
    input_file,
    "r"
) as file:

    reader = csv.DictReader(file)

    for row in reader:

        generations.append(
            int(row["Generations"])
        )

        fitness_values.append(
            float(row["Best Fitness"])
        )


os.makedirs(
    os.path.dirname(output_file),
    exist_ok=True
)


plt.figure(
    figsize=(8, 5)
)

plt.plot(
    generations,
    fitness_values,
    marker="o"
)

plt.xlabel(
    "Number of Generations"
)

plt.ylabel(
    "Best Fitness"
)

plt.title(
    "Effect of Number of Generations on GA Performance"
)

plt.xticks(
    generations
)

plt.grid(True)

plt.tight_layout()

plt.savefig(
    output_file,
    dpi=300
)

plt.show()

print(
    "Graph saved to: "
    "results/figures/generation_comparison.png"
)
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
    "baseline_comparison.csv"
)

output_file = os.path.join(
    PROJECT_ROOT,
    "results",
    "figures",
    "baseline_comparison.png"
)


methods = []
fitness_values = []


with open(
    input_file,
    "r"
) as file:

    reader = csv.DictReader(file)

    for row in reader:

        methods.append(
            row["Method"]
        )

        fitness_values.append(
            float(row["Fitness"])
        )


os.makedirs(
    os.path.dirname(output_file),
    exist_ok=True
)


plt.figure(
    figsize=(8, 5)
)

plt.bar(
    methods,
    fitness_values
)

plt.ylabel(
    "Fitness"
)

plt.title(
    "Genetic Algorithm vs Random Baseline"
)

plt.grid(
    axis="y"
)

plt.tight_layout()

plt.savefig(
    output_file,
    dpi=300
)

plt.show()

print(
    "Graph saved to: "
    "results/figures/baseline_comparison.png"
)
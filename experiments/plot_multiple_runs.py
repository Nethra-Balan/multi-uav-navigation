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
    "multiple_runs.csv"
)

output_file = os.path.join(
    PROJECT_ROOT,
    "results",
    "figures",
    "multiple_runs_fitness.png"
)


seeds = []
fitness_values = []


with open(
    input_file,
    "r"
) as file:

    reader = csv.DictReader(file)

    for row in reader:

        seeds.append(
            int(row["Seed"])
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

plt.plot(
    seeds,
    fitness_values,
    marker="o"
)

plt.axhline(
    sum(fitness_values) / len(fitness_values),
    linestyle="--",
    label="Mean Fitness"
)

plt.xlabel("Random Seed")
plt.ylabel("Best Fitness")

plt.title(
    "GA Performance Across Independent Runs"
)

plt.xticks(
    seeds
)

plt.grid(True)

plt.legend()

plt.tight_layout()

plt.savefig(
    output_file,
    dpi=300
)

plt.show()

print(
    "Graph saved to: "
    "results/figures/multiple_runs_fitness.png"
)
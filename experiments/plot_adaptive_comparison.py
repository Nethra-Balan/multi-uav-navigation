import csv
import os

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
    "adaptive_comparison.csv"
)

output_file = os.path.join(
    PROJECT_ROOT,
    "results",
    "figures",
    "adaptive_comparison.png"
)


runs = []
original_fitness = []
adaptive_fitness = []


with open(input_file, "r") as file:

    reader = csv.DictReader(file)

    for row in reader:

        runs.append(
            int(row["Run"])
        )

        original_fitness.append(
            float(row["Original GA"])
        )

        adaptive_fitness.append(
            float(row["Adaptive GA"])
        )


os.makedirs(
    os.path.dirname(output_file),
    exist_ok=True
)


plt.figure(figsize=(8, 5))

plt.plot(
    runs,
    original_fitness,
    marker="o",
    label="Original GA"
)

plt.plot(
    runs,
    adaptive_fitness,
    marker="o",
    label="Adaptive GA"
)

plt.xlabel("Run")
plt.ylabel("Best Fitness")

plt.title(
    "Original GA vs Adaptive Mutation GA"
)

plt.legend()

plt.grid(True)

plt.tight_layout()

plt.savefig(output_file)

plt.show()

print(
    "Graph saved to: "
    "results/figures/adaptive_comparison.png"
)
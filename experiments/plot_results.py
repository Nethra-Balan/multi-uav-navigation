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
    "fitness_history.csv"
)

output_file = os.path.join(
    PROJECT_ROOT,
    "results",
    "figures",
    "fitness_convergence.png"
)


generations = []
fitness_values = []

with open(input_file, "r") as file:

    reader = csv.DictReader(file)

    for row in reader:
        generations.append(
            int(row["Generation"])
        )

        fitness_values.append(
            float(row["Best Fitness"])
        )


os.makedirs(
    os.path.dirname(output_file),
    exist_ok=True
)

plt.figure(figsize=(8, 5))

plt.plot(
    generations,
    fitness_values,
    marker="o"
)

plt.xlabel("Generation")
plt.ylabel("Best Fitness")

plt.title(
    "Genetic Algorithm Convergence"
)

plt.grid(True)

plt.tight_layout()

plt.savefig(output_file)

plt.show()

print(
    f"Graph saved to: "
    f"results/figures/fitness_convergence.png"
)
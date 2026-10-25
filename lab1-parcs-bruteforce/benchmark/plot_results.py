import csv
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

src = sys.argv[1] if len(sys.argv) > 1 else "results.csv"
out = sys.argv[2] if len(sys.argv) > 2 else "results.png"

workers, times, speedups = [], [], []
with open(src) as f:
    for row in csv.DictReader(f):
        workers.append(int(row["workers"]))
        times.append(float(row["time_sec"]))
        speedups.append(float(row["speedup"]))

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.5))

ax1.plot(workers, times, "o-", color="#1f77b4", linewidth=2, markersize=8)
for x, y in zip(workers, times):
    ax1.annotate("%.2f s" % y, (x, y), textcoords="offset points", xytext=(0, 8))
ax1.set_title("Час виконання vs кількість воркерів")
ax1.set_xlabel("Кількість воркерів N")
ax1.set_ylabel("Час, с")
ax1.set_xticks(workers)
ax1.grid(True, alpha=0.3)

ax2.plot(workers, speedups, "o-", color="#2ca02c", linewidth=2, markersize=8, label="фактичне")
ax2.plot(workers, workers, "--", color="gray", alpha=0.7, label="ідеальне (лінійне)")
for x, y in zip(workers, speedups):
    ax2.annotate("%.2f×" % y, (x, y), textcoords="offset points", xytext=(0, 8))
ax2.set_title("Прискорення (speedup) vs кількість воркерів")
ax2.set_xlabel("Кількість воркерів N")
ax2.set_ylabel("Прискорення S(N)")
ax2.set_xticks(workers)
ax2.grid(True, alpha=0.3)
ax2.legend()

fig.suptitle("PARCS brute-force: простір ключів 1 727 604 кандидатів (lower+digits, len≤4)",
             fontsize=11)
fig.tight_layout(rect=[0, 0, 1, 0.96])
fig.savefig(out, dpi=130)
print("saved %s" % out)

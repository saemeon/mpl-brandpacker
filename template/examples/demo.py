"""my_brand demo — shows what the template brand looks like.

Run::

    python examples/demo.py
"""

import my_brand.pyplot as plt
import numpy as np
from my_brand import Colors, Sizes

# --- Simple line chart ---

fig, ax = plt.subplots(2, 2, figsize=Sizes.full)

x = np.linspace(0, 4 * np.pi, 200)
ax.plot(x, np.sin(x), color=Colors.primary, label="sin(x)")
ax.plot(x, np.cos(x), color=Colors.accent, label="cos(x)")
ax.set_xlabel("Radians")
ax.set_ylabel("Amplitude")
ax.legend()

plt.title("Trigonometric Functions")
plt.subtitle("A simple example")
plt.sources("Generated data")

plt.savefig("demo_line.png", dpi=150, bbox_inches="tight")
print("Saved demo_line.png")
plt.close()

# --- Bar chart ---

fig, ax = plt.subplots(figsize=Sizes.half)

categories = ["Q1", "Q2", "Q3", "Q4"]
values = [12, 19, 8, 15]
bars = ax.bar(
    categories,
    values,
    color=[Colors.primary, Colors.secondary, Colors.accent, Colors.success],
)
ax.set_xlabel("Quarter")
ax.set_ylabel("Revenue (M)")

plt.title("Quarterly Revenue")
plt.sources("Internal data")

plt.savefig("demo_bar.png", dpi=150, bbox_inches="tight")
print("Saved demo_bar.png")
plt.close()

# --- Multi-panel ---

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=Sizes.full)

ax1.plot(np.cumsum(np.random.randn(100)), color=Colors.primary)
ax1.set_xlabel("Day")
ax1.set_ylabel("Price")

ax2.hist(np.random.randn(500), bins=30, color=Colors.secondary, edgecolor="white")
ax2.set_xlabel("Return")
ax2.set_ylabel("Count")

fig.set_title("Market Analysis")
fig.set_sources("Simulated data")

plt.savefig("demo_multi.png", dpi=150, bbox_inches="tight")
print("Saved demo_multi.png")
plt.close()

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

# Define data for the infographic
steps = [
    "Data Collection",
    "Preprocessing",
    "Model Training",
    "Integration with Django"
]
descriptions = [
    "Gather extensive IP data",
    "Clean and prepare data for training",
    "Train ML models on the data",
    "Integrate ML models into Django framework"
]

# Create a figure and axis
fig, ax = plt.subplots(figsize=(10, 6))
ax.axis('off')  # Turn off the axis

# Create a box for each step
bbox_props = dict(boxstyle="round,pad=0.3", edgecolor="black", facecolor="lightblue")
for i, (step, desc) in enumerate(zip(steps, descriptions)):
    # Create a text box for each step
    ax.text(
        0.5, 1 - i * 0.25, f"{step}\n{desc}",
        ha='center', va='center',
        fontsize=12, bbox=bbox_props,
        transform=ax.transAxes
    )

# Add arrows between boxes
for i in range(len(steps) - 1):
    ax.annotate(
        '', xy=(0.5, 1 - (i + 1) * 0.25), xytext=(0.5, 1 - i * 0.25),
        arrowprops=dict(facecolor='black', shrink=0.05)
    )

# Set title
plt.title('Feasibility Steps for Implementing ML in IPR Management Software', fontsize=16)

# Show the infographic
plt.show()

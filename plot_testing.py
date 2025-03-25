import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Sample data
n_months = 120
n_runs = 100
data = np.cumsum(np.random.normal(0.5, 1, (n_months, n_runs)), axis=0)
df = pd.DataFrame(data)

# Compute bounds and mean
lower = df.quantile(0.10, axis=1)
upper = df.quantile(0.90, axis=1)
mean = df.mean(axis=1)
baseline = np.cumsum(np.full(n_months, 0.5))

# Plot
fig, ax = plt.subplots()
ax.fill_between(df.index, lower, upper, color='lightblue', alpha=0.5, label='10–90% Range')
ax.plot(df.index, mean, color='darkblue', label='Mean')
ax.plot(df.index, baseline, color='gray', linestyle='--', label='Baseline')
ax.legend()
ax.set_title("Simulation Outcomes")

# Show in Streamlit
st.pyplot(fig)


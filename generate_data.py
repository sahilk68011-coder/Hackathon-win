import numpy as np
import pandas as pd

np.random.seed(42)

N = 10000

visitor_types = np.random.choice(
    ["New_Visitor", "Returning_Visitor"], size=N, p=[0.55, 0.45]
)

traffic_sources = np.random.choice(
    ["Organic", "Direct", "Referral", "Social", "Paid"],
    size=N,
    p=[0.30, 0.25, 0.15, 0.15, 0.15],
)

regions = np.random.choice(
    ["North America", "Europe", "Asia", "South America", "Africa", "Oceania"],
    size=N,
    p=[0.30, 0.25, 0.20, 0.10, 0.08, 0.07],
)

devices = np.random.choice(
    ["Desktop", "Mobile", "Tablet"], size=N, p=[0.45, 0.40, 0.15]
)

days = np.random.choice(
    ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
    size=N,
    p=[0.15, 0.14, 0.14, 0.14, 0.15, 0.14, 0.14],
)

hour_probs = np.array([
    0.01, 0.008, 0.005, 0.005, 0.005, 0.008,
    0.015, 0.03, 0.05, 0.06, 0.07, 0.07,
    0.065, 0.06, 0.06, 0.055, 0.055, 0.05,
    0.05, 0.05, 0.045, 0.04, 0.03, 0.02,
])
hour_probs = hour_probs / hour_probs.sum()
hours = np.random.choice(range(24), size=N, p=hour_probs)

months = np.random.choice(
    ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
     "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
    size=N,
    p=[0.07, 0.07, 0.08, 0.08, 0.08, 0.08,
       0.08, 0.08, 0.08, 0.09, 0.10, 0.11],
)

is_special_day = np.random.choice([True, False], size=N, p=[0.08, 0.92])

page_views = np.clip(np.random.exponential(scale=3, size=N).astype(int) + 1, 1, 30)

session_duration = np.clip(
    np.random.exponential(scale=180, size=N) * (page_views / 3), 0, 1800
)
session_duration = np.round(session_duration, 1)

bounce = page_views == 1

product_pages_viewed = np.zeros(N, dtype=int)
for i in range(N):
    if page_views[i] > 1:
        max_pp = min(page_views[i] - 1, 15)
        product_pages_viewed[i] = np.random.binomial(max_pp, 0.4)

cart_additions = np.zeros(N, dtype=int)
for i in range(N):
    if product_pages_viewed[i] > 0:
        max_cart = min(product_pages_viewed[i], 8)
        cart_additions[i] = np.random.binomial(max_cart, 0.25)

# --- Conversion logic with realistic patterns ---
base_prob = np.full(N, 0.02)

# Returning visitors convert better
base_prob[visitor_types == "Returning_Visitor"] += 0.015

# Traffic source effects
source_boost = {"Organic": 0.01, "Direct": 0.015, "Paid": 0.02, "Referral": 0.005, "Social": -0.005}
for src, boost in source_boost.items():
    base_prob[traffic_sources == src] += boost

# More cart additions = much higher conversion
base_prob += cart_additions * 0.08

# Product pages viewed boost
base_prob += product_pages_viewed * 0.005

# Longer sessions slightly boost
base_prob += np.clip(session_duration / 1800, 0, 1) * 0.02

# Desktop converts slightly better
base_prob[devices == "Desktop"] += 0.005

# Special day boost
base_prob[is_special_day] += 0.01

# Bounce = no conversion
base_prob[bounce] = 0.0

# Clamp
base_prob = np.clip(base_prob, 0, 0.95)

is_converted = np.random.random(N) < base_prob

revenue = np.zeros(N)
revenue[is_converted] = np.round(
    np.random.lognormal(mean=3.5, sigma=0.8, size=is_converted.sum()), 2
)

# --- Introduce ~1.5% missing values in some columns for realism ---
def add_nulls(series, frac=0.015):
    idx = np.random.choice(len(series), size=int(len(series) * frac), replace=False)
    series = series.copy()
    if isinstance(series, np.ndarray):
        series = pd.array(series)
    result = pd.Series(series)
    result.iloc[idx] = np.nan
    return result

df = pd.DataFrame({
    "session_id": [f"S{str(i).zfill(5)}" for i in range(1, N + 1)],
    "visitor_type": visitor_types,
    "traffic_source": traffic_sources,
    "region": regions,
    "device_type": devices,
    "page_views": page_views,
    "session_duration": session_duration,
    "bounce": bounce,
    "product_pages_viewed": product_pages_viewed,
    "cart_additions": cart_additions,
    "day_of_week": days,
    "hour": hours,
    "month": months,
    "is_special_day": is_special_day,
    "revenue": revenue,
})

df["session_duration"] = add_nulls(df["session_duration"].values)
df["page_views"] = add_nulls(df["page_views"].values)

out_path = "data/ecommerce_sessions.csv"
df.to_csv(out_path, index=False)
print(f"Generated {len(df)} sessions -> {out_path}")
print(f"Conversion rate: {is_converted.mean():.2%}")
print(f"Missing values:\n{df.isnull().sum()[df.isnull().sum() > 0]}")

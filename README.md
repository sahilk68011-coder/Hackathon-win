# E-Commerce Session Conversion Analysis

An end-to-end data analysis project that examines e-commerce browsing sessions to understand what distinguishes converting and non-converting sessions and how visitor behaviour changes across the purchase funnel.

## Project Structure

```
├── data/
│   └── ecommerce_sessions.csv   # 10,000 synthetic e-commerce sessions
├── generate_data.py             # Script to regenerate the dataset
├── analysis.ipynb               # Jupyter notebook — cleaning, EDA, funnel analysis
├── app.py                       # Streamlit interactive dashboard
├── requirements.txt
└── README.md
```

## Dataset

10,000 simulated e-commerce browsing sessions with fields including:
- **Session attributes:** session_id, visitor_type, traffic_source, region, device_type
- **Behaviour metrics:** page_views, session_duration, bounce, product_pages_viewed, cart_additions
- **Temporal:** day_of_week, hour, month, is_special_day
- **Outcome:** revenue (0 = no purchase)

Conversion rate is approximately 5%.

## Setup

```bash
pip install -r requirements.txt
```

## Usage

### 1. Generate / Regenerate Dataset

```bash
python generate_data.py
```

### 2. Run the Jupyter Notebook

```bash
jupyter notebook analysis.ipynb
```

The notebook covers:
- Data loading, cleaning and validation
- Missing value handling and derived features
- Visitor behaviour analysis (page views, session duration, engagement)
- Conversion rates by visitor type, traffic source, device, region
- Temporal heatmaps (hour x day-of-week)
- Full funnel analysis with drop-off rates
- Key findings and recommendations

### 3. Launch the Streamlit Dashboard

```bash
streamlit run app.py
```

The dashboard includes:
- Interactive sidebar filters (visitor type, traffic source, device, region, day)
- KPI cards (sessions, conversion rate, avg revenue, avg duration)
- Visual conversion funnel with drop-off table
- Conversion breakdown tabs (by traffic source, visitor type, device, region)
- Temporal analysis (heatmap + monthly trend)
- Behavioural box plots (converted vs not converted)
- Auto-generated key insights

## Key Findings

1. Returning visitors convert at higher rates than new visitors
2. Paid and Direct traffic channels produce the best conversion rates
3. The largest funnel drop-off occurs between product view and cart addition
4. Cart additions are the strongest single predictor of purchase
5. Desktop users convert slightly more than mobile/tablet
6. Engagement score effectively separates converting from non-converting sessions

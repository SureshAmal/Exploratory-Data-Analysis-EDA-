# Data Alchemy Lab

> **An intelligent exploratory data analysis (EDA) platform powered by multi-agent AI architecture**

Transform raw data into actionable insights through automated profiling, intelligent cleaning, and AI-driven analysis. Built for data scientists, analysts, and business users who need rapid, reliable data understanding.

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.20%2B-FF4B4B)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

---

## 🎯 Overview

Data Alchemy Lab is a production-ready EDA platform that combines traditional statistical methods with modern AI capabilities. The system employs a **multi-agent architecture** where specialized AI agents collaborate to automate data quality assessment, cleaning, and insight generation.

### Key Differentiators

- **Multi-Agent Intelligence**: Supervisor agent orchestrates specialized cleaning and analysis agents
- **Verified Accuracy**: All analysis uses proven statistical algorithms (IQR, Z-score, Pearson correlation) - no random data
- **Memory & Observability**: Session-based memory tracks agent decisions with full action logging
- **Intelligent Automation**: CleaningAgent auto-imputes missing values using statistical methods
- **Context-Aware AI**: Gemini-powered insights receive complete dataset context (schema, statistics, sample data)
- **Enterprise-Ready UI**: Modular CSS design system with light/dark themes and accessibility features

---

## ✨ Features

### 📊 Automated Data Profiling
- **Comprehensive Statistics**: Row/column counts, data types, missing values, memory usage
- **Column-Level Metrics**: Non-null counts, missing percentages, unique values, sample data
- **Distribution Analysis**: Histograms with box plots for all numeric columns
- **Correlation Matrix**: Pearson correlation heatmaps for multi-variate relationships

### 🔍 Advanced Outlier Detection
- **IQR Method**: Interquartile range with configurable sensitivity (Q1 - factor×IQR, Q3 + factor×IQR)
- **Z-Score Method**: Standard deviation-based detection with customizable thresholds
- **Visual Feedback**: Per-column outlier counts and percentages
- **Interactive Tuning**: Real-time parameter adjustment with immediate results

### 🧹 Intelligent Data Cleaning
- **Multi-Agent Architecture**: SupervisorAgent delegates to CleaningAgent for automated quality improvement
- **Auto-Imputation**: Median imputation for numeric columns, row removal for categorical missing values
- **Manual Controls**: Per-column cleaning actions (drop, cap, impute with mean/median/mode)
- **Before/After Comparison**: Side-by-side comparison of original vs cleaned data
- **Export Capability**: Download cleaned datasets as CSV

### 🤖 AI-Powered Insights (Google Gemini)
- **Automatic Analysis**: Comprehensive dataset overview with patterns, trends, and recommendations
- **Custom Queries**: Ask specific questions and receive targeted visualizations
- **Context-Rich Prompts**: AI receives dataset schema, statistics, and sample rows
- **Intelligent Charting**: Generate customer/product/time/distribution analysis based on question keywords
- **Token Optimization**: Targeted visual generation reduces API costs

### 📈 Sales Analytics Dashboard
- **Auto-Detection**: Automatically activates for datasets with Date, Customer, Total_Amount columns
- **Time Series Analysis**: Daily/monthly/yearly trends with cumulative growth tracking
- **Customer Intelligence**: Top customers by revenue, transaction counts, average transaction value
- **Product Performance**: Sales by product, revenue share, trend analysis
- **KPI Metrics**: Total revenue, transaction count, customer count, daily averages

### 🎨 Professional UI/UX
- **Design Token System**: Centralized color, spacing, typography, and motion tokens
- **Theme Support**: Light (pure white), Dark (deep naval), System preference detection
- **Narrative Journey**: Sidebar progress tracking (Upload → Profile → Clean → Insights)
- **Responsive Layout**: Optimized for desktop analysis workflows
- **Accessible Design**: WCAG AA contrast, keyboard navigation, reduced motion support

---

## 🏗️ Architecture

### Multi-Agent System

The platform implements a **supervisor pattern** where specialized agents handle distinct responsibilities:

```
SupervisorAgent (Orchestrator)
    ├── CleaningAgent (Data Quality)
    │   ├── Inspects missing values per column
    │   ├── Auto-imputes numeric columns (median)
    │   ├── Drops rows for categorical missing values
    │   └── Logs all decisions to SessionMemory
    │
    └── AnalysisAgent (Insights Generation)
        ├── Delegates to AgentTools.generate_insights()
        ├── Sends dataset context to Gemini API
        ├── Generates targeted visualizations
        └── Returns insights + charts to user
```

**Key Components:**

- **BaseAgent**: Parent class providing logging infrastructure (`log_thought`, `log_action`)
- **SessionMemory**: Tracks agent actions with timestamps for debugging and auditing
- **AgentTools**: Static wrapper abstracting EDA operations and AI integration
- **Dual Observability**: Actions logged to both Python logger and SessionMemory (visible in sidebar)

### Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | Streamlit 1.20+ | Interactive web interface |
| **Data Processing** | pandas, numpy | DataFrame operations, statistics |
| **Visualization** | Plotly 5.0+ | Interactive charts with brand template |
| **AI Engine** | Google Gemini API | Natural language insights, pattern detection |
| **Statistical Analysis** | scipy | Outlier detection (Z-score), correlation |
| **Agent Framework** | Custom Python classes | Multi-agent orchestration, memory |
| **Styling** | Modular CSS | Token-based design system |

### Data Flow

```
1. Upload CSV/Excel → read_dataset()
2. SupervisorAgent.process_upload(df)
    ↓
3. CleaningAgent.run(df)
    - Detect missing values
    - Apply auto-cleaning rules
    - Log actions to memory
    ↓
4. Display Profile + Statistics
    - basic_profile(), column_profile()
    - summary_stats(), correlation matrix
    ↓
5. User Query → SupervisorAgent.handle_query()
    ↓
6. AnalysisAgent.run(df, query, api_key)
    - Build context (schema + stats + samples)
    - Call Gemini API
    - Generate targeted charts
    ↓
7. Display Insights + Visualizations
```

---

## 📦 Installation

### Prerequisites

- **Python**: 3.8 or higher
- **pip**: Latest version recommended
- **Google Gemini API Key**: Required for AI insights ([Get API Key](https://makersuite.google.com/app/apikey))

### Quick Start

1. **Clone the repository**
```bash
git clone <repository-url>
cd eda_agent
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment variables**

Create a `.env` file in the project root:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```

4. **Launch the application**
```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

### Alternative Launch (Shell Script)

```bash
chmod +x run.sh
./run.sh
```

Select option 4 to launch the Streamlit app.

---

## 🚀 Usage Guide

### 1. Upload Your Dataset

**Supported Formats:**
- CSV (`.csv`)
- Excel (`.xls`, `.xlsx`)

**Best Practices:**
- First row should contain column headers
- Use UTF-8 encoding for CSV files
- Ensure dates are in recognizable formats (YYYY-MM-DD, MM/DD/YYYY)
- Numeric columns should use standard number formatting

### 2. Review Data Profile

**Automated Metrics:**
- Total rows and columns
- Missing value counts (global and per-column)
- Memory usage estimation
- Data types for each column

**Column Profile Table:**
- Non-null counts and missing percentages
- Unique value counts
- Sample values (up to 3 examples)
- Statistical measures (min, max, mean, median) for numeric columns

### 3. Explore Distributions & Correlations

**Distribution Analysis:**
- Select any numeric column
- View histogram with 50 bins
- Box plot overlay shows quartiles and outliers

**Correlation Matrix:**
- Pearson correlation coefficients for all numeric columns
- Color-coded heatmap (red = positive, blue = negative)
- Identify multicollinearity and relationships

### 4. Detect Outliers

**IQR Method** (Default: factor = 1.5)
- Best for: Normally distributed data
- Adjustable sensitivity: 1.0 (strict) to 3.0 (lenient)
- Formula: Lower = Q1 - factor×IQR, Upper = Q3 + factor×IQR

**Z-Score Method** (Default: threshold = 3.0)
- Best for: Data with known Gaussian distribution
- Adjustable threshold: 2.0 (strict) to 5.0 (lenient)
- Formula: Outlier if |Z| > threshold

**Output:**
- Per-column outlier counts
- Percentage of rows affected
- Real-time updates as parameters change

### 5. Clean Your Data

**Automated Cleaning** (via CleaningAgent):
- Upload triggers `SupervisorAgent.process_upload()`
- `CleaningAgent` inspects missing values
- Auto-imputes numeric columns with median
- Drops rows with categorical missing values
- All actions logged to SessionMemory

**Manual Cleaning:**
- Select columns for custom actions
- Choose action per column:
  - **Drop**: Remove rows with outliers/missing values
  - **Cap**: Set min/max bounds (e.g., cap_lower=0, cap_upper=1000)
  - **Impute**: Fill missing with mean, median, or mode
- Preview changes in comparison table
- Download cleaned dataset as CSV

### 6. Generate AI Insights

**Automatic Analysis:**
- Comprehensive dataset overview
- Key patterns and trends identification
- Anomaly detection
- Business recommendations
- Multiple visualization types (distributions, trends, comparisons)

**Custom Query Examples:**
```
"Which customers generate the most revenue?"
"Show sales trends over time"
"What products have declining sales?"
"Analyze regional performance"
"Distribution of transaction amounts"
```

**AI Response Includes:**
- Natural language analysis
- Targeted visualizations (only relevant charts)
- Specific answers to your question
- Actionable insights

### 7. Sales Analytics (Auto-Activated)

**Required Columns:**
- `Date`: Transaction timestamp
- `Customer`: Customer identifier
- `Total_Amount`: Transaction value

**Dashboard Tabs:**

1. **Sales Over Time**
   - Daily sales trend line
   - Monthly sales bar chart
   - Cumulative sales growth
   - Year-over-year comparison

2. **Sales by Customer**
   - Top N customers (configurable slider)
   - Revenue distribution pie chart
   - Transaction count analysis
   - Customer comparison table

3. **Product Analysis** (if `Product` column exists)
   - Sales by product bar chart
   - Product revenue share
   - Top 5 products trend over time

4. **Key Metrics**
   - Total revenue, transactions, customers
   - Average transaction value
   - Revenue per customer
   - Best sales day, top customer, top product

---

## 📁 Project Structure

```
eda_agent/
│
├── app.py                          # Main Streamlit application (UI + workflows)
├── agents.py                       # Multi-agent system (Supervisor, Cleaner, Analyst)
├── memory.py                       # SessionMemory for agent action tracking
├── tools.py                        # AgentTools static wrapper methods
├── eda.py                          # Core statistical analysis functions
├── gemini_client.py                # Google Gemini API client
├── ai_visual_generator.py          # Targeted chart generation logic
├── plotly_theme.py                 # BRAND_TEMPLATE for visual consistency
│
├── styles/                         # Modular CSS design system
│   ├── theme_tokens.css            # Design tokens (colors, spacing, typography)
│   ├── base.css                    # Global styles, resets, scrollbar
│   ├── components.css              # Component-specific styles
│   ├── dark.css                    # Dark theme overrides
│   └── motion.css                  # Animations + reduced-motion support
│
├── data/                           # Sample datasets
│   └── sales_data.csv              # Example sales data for testing
│
├── utils/                          # Utility scripts
│   ├── generate_sales_data.py      # Synthetic sales data generator
│   └── sales_visualizations.py     # Standalone sales visualization script
│
├── tests/                          # Unit tests
│   └── test_agents.py              # Agent system tests
│
├── requirements.txt                # Python dependencies
├── .env                            # Environment variables (create this - not in repo)
├── .gitignore                      # Git exclusions
├── run.sh                          # Interactive launch script
├── README.md                       # This file
└── ANALYSIS_VALIDATION.md          # Algorithm verification documentation
```

### Key Files Explained

| File | Responsibility |
|------|---------------|
| `app.py` | Streamlit UI, file upload, tab organization, chart rendering, agent integration |
| `agents.py` | BaseAgent, CleaningAgent, AnalysisAgent, SupervisorAgent classes |
| `memory.py` | SessionMemory class for tracking agent actions with timestamps |
| `tools.py` | AgentTools static methods (get_dataset_profile, clean_dataset, generate_insights) |
| `eda.py` | Statistical functions (basic_profile, summary_stats, outlier_detection, cleaning) |
| `gemini_client.py` | API client for Google Gemini with error handling |
| `ai_visual_generator.py` | Intelligent chart generation based on query keywords |
| `plotly_theme.py` | Custom Plotly template (colorway, fonts, transparent backgrounds) |

---

## 🎨 Design System

### Philosophy

The UI is built on a **token-based design system** that separates semantic meaning from visual values. This enables consistent theming, easy maintenance, and rapid iteration.

### Token Categories

**Colors**
- `--color-bg`: Background (pure white in light, naval in dark)
- `--color-accent`: Primary accent (gold #d4a64e)
- `--color-accent-alt`: Secondary accent (teal #2e6f85)
- `--color-text`: Body text color
- `--color-text-muted`: Secondary text

**Spacing Scale** (1rem = 16px)
- `--space-1` to `--space-7`: Consistent vertical rhythm

**Typography**
- `--font-sans`: IBM Plex Sans (body text)
- `--font-serif`: Fraunces (headings)
- `--fs-xs` to `--fs-xxl`: Font size scale

**Other Tokens**
- Radii: `--radius-xs` to `--radius-lg`
- Shadows: `--shadow-sm`, `--shadow-md`, `--shadow-lg`
- Motion: `--dur-fast`, `--dur-base`, `--ease-standard`

### Theme Support

**Light Theme** (Default)
- Pure white background (#ffffff)
- High contrast text
- Gradient accents (gold → teal)

**Dark Theme**
- Deep naval backgrounds
- Reduced contrast for comfort
- Adjusted shadow depths

**System Theme**
- Detects OS preference via `prefers-color-scheme`
- Automatically applies appropriate theme

### Accessibility

- **WCAG AA Compliance**: 4.5:1 minimum contrast ratio
- **Keyboard Navigation**: All interactive elements accessible via Tab
- **Focus Indicators**: Visible 2px accent outline on focus
- **Reduced Motion**: Respects `prefers-reduced-motion` media query
- **Semantic HTML**: Proper heading hierarchy, ARIA labels where needed

---

## 🔬 Statistical Methods & Algorithms

All analysis uses **verified, industry-standard algorithms**. See `ANALYSIS_VALIDATION.md` for test results.

### Profiling

**Basic Statistics**
- Count: `df.shape[0]`
- Column count: `df.shape[1]`
- Missing values: `df.isna().sum()`
- Data types: `df.dtypes`
- Memory: `df.memory_usage(deep=True).sum()`

**Descriptive Statistics**
- Mean, median, std deviation: `df.describe()`
- Min, max, quartiles: pandas built-in methods

### Outlier Detection

**IQR (Interquartile Range) Method**
```python
Q1 = series.quantile(0.25)
Q3 = series.quantile(0.75)
IQR = Q3 - Q1
lower_bound = Q1 - factor * IQR
upper_bound = Q3 + factor * IQR
outliers = (series < lower_bound) | (series > upper_bound)
```

**Z-Score Method**
```python
from scipy import stats
z_scores = np.abs(stats.zscore(series.dropna()))
outliers = z_scores > threshold
```

### Correlation

**Pearson Correlation Coefficient**
```python
r = Σ[(x - x̄)(y - ȳ)] / [√Σ(x - x̄)² × √Σ(y - ȳ)²]
# Implemented as: df[numeric_cols].corr()
```

### Data Cleaning

**Imputation Methods**
- Mean: `series.fillna(series.mean())`
- Median: `series.fillna(series.median())`
- Mode: `series.fillna(series.mode()[0])`

**Auto-Cleaning Rules** (CleaningAgent)
- Numeric missing → Median imputation
- Categorical missing → Drop row
- Rationale: Median robust to outliers, categorical imputation unreliable

---

## 🤖 AI Integration

### Google Gemini API

**Model**: gemini-1.5-flash (fast, cost-effective)

**Context Provided to AI:**
```python
Dataset Information:
- Rows: {len(df)}
- Columns: {len(df.columns)}
- Column Names: {list}
- Data Types: {df.dtypes}
- Sample Data: {df.head(5)}
- Statistical Summary: {df.describe()}
```

**Token Optimization:**
- Automatic analysis: Up to 8192 output tokens
- Custom queries: 4096 tokens max
- Targeted visuals: Only generate charts matching query keywords

**Safety:**
- Error handling for API failures
- Graceful degradation if API key missing
- Rate limit awareness (exponential backoff recommended for production)

### Chart Generation Logic

**Keyword Detection:**
```python
if 'customer' in query.lower() and 'sales' in query.lower():
    # Generate: Bar chart (customer vs sales), Pie chart (top 10)
elif 'time' in query.lower() or 'trend' in query.lower():
    # Generate: Line chart (time series), Monthly aggregation
elif 'product' in query.lower():
    # Generate: Product sales bar chart, Revenue share pie
```

**Fallback:**
- If no keywords match, generate generic charts:
  - First categorical vs first numeric (bar chart)
  - First two numeric columns (scatter plot)

---

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Required for AI insights
GEMINI_API_KEY=your_google_gemini_api_key

# Optional: Configure Streamlit server
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=localhost
```

### Streamlit Configuration

Create `.streamlit/config.toml` for advanced settings:

```toml
[server]
port = 8501
enableCORS = false
enableXsrfProtection = true

[browser]
gatherUsageStats = false

[theme]
base = "light"
primaryColor = "#d4a64e"
```

### Customization Options

**Modify Analysis Parameters:**
- `eda.py`: Change outlier detection formulas, imputation logic
- `ai_visual_generator.py`: Add new chart types, adjust keyword detection

**UI Customization:**
- `styles/theme_tokens.css`: Change colors, spacing, fonts
- `plotly_theme.py`: Modify chart colorway, fonts, grid styling
- `app.py`: Reorder tabs, add new sections, adjust layout

**Agent Behavior:**
- `agents.py`: Modify CleaningAgent auto-cleaning rules
- `memory.py`: Add new memory features (e.g., long-term storage)

---

## 🐛 Troubleshooting

### Installation Issues

**"No module named 'dotenv'"**
```bash
pip install python-dotenv
```

**"No module named 'streamlit'"**
```bash
pip install streamlit
```

**"No module named 'google.generativeai'"**
```bash
pip install google-generativeai
```

**General dependency issues**
```bash
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

### API & Configuration

**"Error: GEMINI_API_KEY not found"**
1. Verify `.env` file exists in project root (same directory as `app.py`)
2. Check file contents: `GEMINI_API_KEY=your_actual_key` (no quotes needed)
3. Restart Streamlit after creating/modifying `.env`
4. Ensure no extra spaces or line breaks in `.env`

**"API error: 401 Unauthorized"**
- API key is invalid or expired
- Get a new key at [Google AI Studio](https://makersuite.google.com/app/apikey)
- Ensure key has Gemini API access enabled

**"API error: 429 Rate Limit"**
- You've exceeded free tier quota
- Wait for quota reset or upgrade to paid plan
- Reduce custom query frequency

### Data Upload Issues

**File upload fails silently**
- Check file format: Only CSV, XLS, XLSX supported
- Try opening file in Excel/text editor to verify it's not corrupted
- For CSV: Save with UTF-8 encoding
- For Excel: Ensure it's not password-protected

**"UnicodeDecodeError" on CSV**
```bash
# Re-save CSV with UTF-8 encoding in Excel:
# File → Save As → CSV UTF-8 (Comma delimited)
```

**Large files cause timeout**
- Streamlit has ~200MB default upload limit
- For larger files, increase in `.streamlit/config.toml`:
```toml
[server]
maxUploadSize = 500
```

### Analysis Errors

**"ValueError: Unsupported method" in outlier detection**
- Ensure method parameter is either `'iqr'` or `'zscore'`
- This error indicates corrupted session state (refresh page)

**Charts not displaying**
- Check browser console for JavaScript errors
- Try different browser (Chrome/Edge recommended)
- Disable browser extensions that block scripts
- Clear Streamlit cache: `streamlit cache clear`

**"KeyError" on sales dashboard**
- Sales dashboard requires exact column names: `Date`, `Customer`, `Total_Amount`
- Check for trailing spaces in column headers
- Use Data Preview section to verify column names

### Performance Issues

**App loads slowly**
- Large datasets (>100K rows) may take time to profile
- Consider sampling: `df.sample(n=10000)` for exploration
- Close unused browser tabs
- Check system RAM usage

**Charts freeze/stutter**
- Reduce number of data points in time series charts
- Use monthly/yearly aggregation instead of daily for long time periods
- Disable dark theme (light theme renders faster)

### Agent & Memory Issues

**Agent logs not showing in sidebar**
- Verify SessionMemory initialized: Check `st.session_state['agent_memory']`
- Refresh page to reset session state
- Check browser console for JavaScript errors

**Cleaning actions not applied**
- Ensure you clicked "Apply Cleaning" button (not just "Preview")
- Check that columns are selected in multiselect
- Verify cleaning actions dictionary is not empty

---

## 📚 Dependencies

### Core Libraries

```
streamlit >= 1.20.0          # Web framework
pandas >= 2.0.0              # Data manipulation
numpy >= 1.24.0              # Numerical computing
plotly >= 5.0.0              # Interactive visualizations
scipy >= 1.10.0              # Statistical functions
scikit-learn >= 1.2.0        # Machine learning utilities
```

### AI & API

```
google-generativeai >= 0.3.0 # Gemini API client
python-dotenv >= 1.0.0       # Environment variable management
requests >= 2.28.0           # HTTP requests
```

### Data I/O

```
openpyxl >= 3.1.0            # Excel file support (.xlsx)
xlrd == 1.2.0                # Legacy Excel support (.xls)
```

### Full Requirements

See `requirements.txt` for complete dependency list with pinned versions.

---

## 🧪 Testing

### Run Unit Tests

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_agents.py

# Run with coverage
pytest --cov=. tests/
```

### Manual Testing Checklist

**Data Upload**
- [ ] CSV file uploads successfully
- [ ] Excel file uploads successfully
- [ ] Large files (>10MB) handled properly
- [ ] Invalid files show error message

**Analysis**
- [ ] Basic profile shows correct row/column counts
- [ ] Column profile displays all metrics
- [ ] Outlier detection runs without errors
- [ ] Correlation matrix generated for numeric columns

**Cleaning**
- [ ] Auto-cleaning triggers on upload
- [ ] Manual cleaning actions apply correctly
- [ ] Download cleaned dataset works
- [ ] Before/after comparison accurate

**AI Insights**
- [ ] Automatic analysis generates insights
- [ ] Custom queries return relevant charts
- [ ] API errors handled gracefully
- [ ] Charts match query intent

**UI/UX**
- [ ] Theme toggle works (Light/Dark/System)
- [ ] Sidebar journey updates correctly
- [ ] Agent logs display in sidebar
- [ ] All tabs accessible
- [ ] Charts interactive (zoom, pan, hover)

---

## 🚀 Deployment

### Streamlit Cloud (Recommended)

1. **Push to GitHub**
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin <your-repo-url>
git push -u origin main
```

2. **Deploy on Streamlit Cloud**
- Visit [share.streamlit.io](https://share.streamlit.io)
- Connect GitHub account
- Select repository and branch
- Set `app.py` as main file
- Add secrets in Streamlit Cloud dashboard:
  - `GEMINI_API_KEY=your_key`
- Click Deploy

### Docker Deployment

Create `Dockerfile`:
```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

Build and run:
```bash
docker build -t data-alchemy-lab .
docker run -p 8501:8501 --env-file .env data-alchemy-lab
```

### AWS EC2 / VPS

```bash
# SSH into server
ssh user@your-server-ip

# Install Python and dependencies
sudo apt update
sudo apt install python3-pip
pip3 install -r requirements.txt

# Run with nohup (persistent)
nohup streamlit run app.py --server.port=8501 &

# Or use systemd service (recommended)
# Create /etc/systemd/system/streamlit-eda.service
```

---

## 📖 API Reference

### Core Functions (eda.py)

```python
from eda import basic_profile, summary_stats, column_profile, outlier_summary, apply_cleaning

# Get basic dataset info
profile = basic_profile(df)
# Returns: {'rows': int, 'columns': int, 'dtypes': dict, 'missing': dict}

# Get descriptive statistics
stats = summary_stats(df)
# Returns: DataFrame with count, mean, std, min, quartiles, max

# Get detailed column profile
col_prof = column_profile(df)
# Returns: DataFrame with dtype, non_null, missing, missing_pct, unique, 
#          sample_values, min, max, mean, median, memory_bytes

# Detect outliers
outliers = outlier_summary(df, method='iqr', factor=1.5)
# Returns: DataFrame with column, outlier_count, outlier_pct

# Apply cleaning actions
cleaned_df = apply_cleaning(df, actions={
    'column_name': {
        'method': 'impute',  # or 'drop', 'cap'
        'impute': 'median',  # or 'mean', 'mode'
        'lower': 0,          # for 'cap' method
        'upper': 100         # for 'cap' method
    }
})
```

### Agent Classes (agents.py)

```python
from agents import SupervisorAgent, CleaningAgent, AnalysisAgent
from memory import SessionMemory

# Initialize memory and supervisor
memory = SessionMemory()
supervisor = SupervisorAgent(memory)

# Process upload (triggers auto-cleaning)
cleaned_df = supervisor.process_upload(df)

# Handle user query (generates insights)
figures, text, error = supervisor.handle_query(df, query="Show sales trends", api_key="...")
```

### AI Insights (ai_visual_generator.py)

```python
from ai_visual_generator import generate_insights_with_visuals

# Generate automatic insights
figures, text, error = generate_insights_with_visuals(
    df=dataframe,
    custom_prompt=None,  # or specific question string
    api_key="your_gemini_key"
)

# Returns:
# - figures: List of plotly Figure objects
# - text: String with AI-generated analysis
# - error: None or error message string
```

---

## 🤝 Contributing

### Development Setup

1. **Fork and clone**
```bash
git clone <your-fork-url>
cd eda_agent
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dev dependencies**
```bash
pip install -r requirements.txt
pip install pytest pytest-cov black flake8
```

4. **Create feature branch**
```bash
git checkout -b feature/your-feature-name
```

### Code Style

- **Formatting**: Use `black` for Python formatting
- **Linting**: Follow `flake8` guidelines
- **Docstrings**: Use Google-style docstrings
- **Type Hints**: Add type hints for function signatures

```python
def example_function(param: str, data: pd.DataFrame) -> Dict[str, Any]:
    """Brief description of function.

    Args:
        param: Description of param
        data: Description of data

    Returns:
        Dictionary containing results
    """
    pass
```

### Pull Request Process

1. Update README.md with new features
2. Add tests for new functionality
3. Ensure all tests pass: `pytest tests/`
4. Update `ANALYSIS_VALIDATION.md` if algorithms changed
5. Submit PR with clear description

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

**Built With:**
- [Streamlit](https://streamlit.io/) - Web framework for data applications
- [Plotly](https://plotly.com/) - Interactive visualization library
- [pandas](https://pandas.pydata.org/) - Data manipulation and analysis
- [Google Gemini](https://ai.google.dev/) - AI-powered insights
- [scikit-learn](https://scikit-learn.org/) - Machine learning utilities
- [scipy](https://scipy.org/) - Scientific computing

**Design Inspiration:**
- [IBM Design Language](https://www.ibm.com/design/language/) - Design tokens approach
- [Material Design](https://material.io/) - Accessibility guidelines
- [Tailwind CSS](https://tailwindcss.com/) - Utility-first CSS philosophy

---

## 📞 Support & Contact

**Documentation:**
- [ANALYSIS_VALIDATION.md](ANALYSIS_VALIDATION.md) - Algorithm verification
- [requirements.txt](requirements.txt) - Full dependency list

**Issues:**
- Report bugs via GitHub Issues
- Include error messages, browser console logs, and steps to reproduce

**Questions:**
- Check Troubleshooting section first
- Review Streamlit documentation for framework-specific questions
- Consult Google Gemini API docs for AI-related queries

---

## 🗺️ Roadmap

**Planned Features:**
- [ ] PostgreSQL/MySQL database connection support
- [ ] Advanced time series forecasting (ARIMA, Prophet)
- [ ] Automated feature engineering suggestions
- [ ] Export reports as PDF/PowerPoint
- [ ] Collaborative analysis (multi-user sessions)
- [ ] Custom agent creation interface
- [ ] Integration with dbt for data transformation
- [ ] Real-time data streaming support

**Completed:**
- [x] Multi-agent architecture
- [x] Session memory and observability
- [x] Automated data cleaning
- [x] AI-powered insights with Gemini
- [x] Sales analytics dashboard
- [x] Dark theme support
- [x] Column-level profiling

---

<div align="center">

**Data Alchemy Lab** - Transforming raw data into golden insights

Made with ❤️ for data professionals

[⭐ Star on GitHub](https://github.com) | [📖 Documentation](README.md) | [🐛 Report Bug](https://github.com)

</div>

# 📊 Risk Management Software - Trading Strategy Analysis Platform

A professional PyQt5 application for analyzing trading strategies using advanced financial metrics including Omega Ratio, Sharpe Ratio, and overfitting detection.

## ✨ Features

- **Portfolio Analysis**: Calculate key performance metrics (Omega, Sharpe, Sortino, Calmar ratios)
- **Risk Management**: Custom allocation formulas with real-time evaluation
- **Overfitting Detection**: Advanced algorithms to detect strategy overfitting
- **Monte Carlo Simulations**: Stress test your strategies
- **Professional Charts**: Interactive visualizations with matplotlib
- **Dark Theme UI**: Modern, professional trading interface

## 🚀 Installation

1. Clone the repository:
```bash
git clone https://github.com/SachaProject/risk-management-software.git
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python app.py
```

## 📋 Requirements

- Python 3.8+
- PyQt5
- pandas
- numpy
- matplotlib
- scipy

## 🎯 Usage

1. **Import Data**: Load your trading data (CSV format)
2. **Configure Portfolio**: Set initial capital and risk parameters
3. **Create Formulas**: Design custom allocation strategies using metrics
4. **Analyze Results**: View detailed performance analytics
5. **Detect Overfitting**: Check if your strategy is overfitted to historical data

## 📂 Project Structure

```
omega-ratio/
├── app.py              # Main application entry point
├── controllers/        # Business logic controllers
├── models/             # Data models and calculations
├── views/              # PyQt5 UI components
└── requirements.txt    # Python dependencies
```

## 🔧 Key Components

- **Portfolio Management**: Dynamic allocation based on custom formulas
- **Strategy Analysis**: Comprehensive metrics calculation
- **Overfitting Detection**: 5 different analysis methods
- **Risk Assessment**: Monte Carlo & stress testing
- **Real-time Updates**: Live formula evaluation

## 📈 Metrics Supported

- Omega Ratio
- Sharpe Ratio
- Sortino Ratio
- Calmar Ratio
- Maximum Drawdown
- Win Rate
- Profit Factor
- And many more...

## 🛡️ Risk Management

The platform includes sophisticated risk management tools:
- Custom allocation formulas
- Position sizing optimization
- Drawdown protection
- Volatility-based adjustments

## 📝 License

MIT License

## 👤 Author

Sacha Pédenon

---


Built with ❤️ for quantitative traders

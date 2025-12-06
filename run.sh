#!/bin/bash
# Quick launcher script for the Sales Analysis Project

echo "========================================================================"
echo "  📊 SALES ANALYSIS PROJECT - QUICK LAUNCHER"
echo "========================================================================"
echo ""
echo "What would you like to do?"
echo ""
echo "  1) Test project setup (verify files and dependencies)"
echo "  2) Generate new sample sales data"
echo "  3) Run standalone sales analysis (creates HTML reports)"
echo "  4) Launch Streamlit web app"
echo "  5) View quick start guide"
echo "  6) Exit"
echo ""
read -p "Enter your choice (1-6): " choice

case $choice in
1)
  echo ""
  echo "Running project verification..."
  python3 test_project.py
  ;;
2)
  echo ""
  echo "Generating new sample sales data..."
  python3 generate_sales_data.py
  ;;
3)
  echo ""
  echo "Running comprehensive sales analysis..."
  echo "This will create interactive HTML reports in the current directory."
  python3 sales_visualizations.py
  echo ""
  echo "✅ Analysis complete!"
  echo "Open these files in your browser:"
  echo "  • sales_over_time_comprehensive.html"
  echo "  • sales_by_customer_comprehensive.html"
  ;;
4)
  echo ""
  echo "Launching Streamlit app..."
  echo "The app will open in your default browser."
  echo ""
  streamlit run app.py
  ;;
5)
  echo ""
  echo "========================================================================"
  cat SALES_ANALYSIS_GUIDE.md
  echo "========================================================================"
  ;;
6)
  echo ""
  echo "Goodbye! 👋"
  exit 0
  ;;
*)
  echo ""
  echo "Invalid choice. Please run the script again and select 1-6."
  exit 1
  ;;
esac

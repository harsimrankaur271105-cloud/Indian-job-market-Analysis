# 💼 Indian Job Market Analysis

An interactive **Streamlit-based web application** for exploring, analyzing, and understanding the Indian job market using job listing data.

The application provides insights into **job roles, companies, locations, salaries, experience levels, skills, work modes, and career opportunities** through an interactive and professional dashboard.

---

## 🚀 Project Overview

The **Indian Job Market Analysis** project is designed to help students, job seekers, and career planners understand current job-market trends through data analysis and visualization.

The application uses a cleaned Indian job-market dataset and provides multiple interactive modules for exploring job opportunities and generating career insights.

The project includes a modern **dark/glass-style user interface** with interactive charts, filters, tables, metrics, and career-oriented tools.

---

## ✨ Main Features

### 🏠 1. Home

The Home page provides an overview of the Indian job market.

It includes:

- Total number of jobs
- Number of companies
- Number of cities
- Median salary
- Top hiring city
- Top skill
- Remote/Hybrid job percentage
- Best-paid experience level
- Overview of all major application modules

---

### 📊 2. Job Market Dashboard

The Dashboard provides interactive analysis of the job-market dataset.

It includes analysis of:

- Job distribution
- Companies
- Locations
- Salary trends
- Experience levels
- Skills
- Work modes
- Company ratings

The dashboard also provides KPI cards and interactive filters to make the analysis easier.

---

### 🔎 3. Job Explorer

The Job Explorer allows users to search and explore individual job opportunities.

Users can:

- Search for job roles
- Filter job listings
- Sort job results
- View company information
- View salary information
- View experience requirements
- View location
- View company ratings
- View required skills
- Read complete job descriptions
- Download filtered job results as CSV

---

### 🎯 4. Career Insights

Career Insights helps users understand the salary and skill requirements associated with a particular career profile.

Users can enter:

- Job role
- Skill
- City
- Years of experience

The application then provides:

- Lower salary range
- Typical/median salary
- Upper salary range
- Number of matching jobs
- Salary distribution
- Companies hiring for the selected profile
- Skills commonly requested for similar jobs
- Top matching job opportunities

---

### 🤖 5. Smart Career Tools

The Smart Career Tools module provides three career-oriented tools.

#### 🎯 Job Recommendation

Users can enter their skills or profile and receive job recommendations based on similarity with job-market data.

Features include:

- Skill/profile matching
- Match score
- Recommended jobs
- Company details
- Salary information
- Downloadable recommendations

#### 🧩 Skill Gap Analyzer

The Skill Gap Analyzer compares a user's current skills with skills commonly requested for a selected target role.

It identifies:

- Skills already possessed
- Frequently requested skills
- Skill gaps
- Recommended skills to learn

#### 💰 Salary Estimator

The Salary Estimator provides an estimated salary range based on comparable jobs in the dataset.

Users can select:

- Job role
- City
- Experience
- Work mode

The tool provides:

- Estimated/median salary
- Lower salary range
- Upper salary range
- Number of comparable jobs

The estimate is calculated from salary information available in the project's dataset.

---

## 🛠️ Technologies Used

- **Python**
- **Streamlit**
- **Pandas**
- **NumPy**
- **Altair**
- **HTML**
- **CSS**

---

## 📂 Project Structure

```text
Indian-job-market-Analysis/
│
├── app.py
├── cleaned_indian_job_market.csv
├── README.md
└── app_backup.py
```

### `app.py`

Main Streamlit application containing the complete dashboard, data processing, visualizations, filters, job exploration, career insights, and smart career tools.

### `cleaned_indian_job_market.csv`

Cleaned job-market dataset used by the application.

### `README.md`

Project documentation and setup instructions.

---

## 📊 Data Analysis

The project analyzes job-market information such as:

- Job titles
- Companies
- Locations
- Salaries
- Experience
- Skills
- Work modes
- Company ratings
- Job descriptions
- Posting information

The application performs data processing and filtering before displaying the information through interactive components.

---

## 🎨 User Interface

The application uses a modern dashboard-style interface with:

- Dark background
- Glass-style cards
- Modern KPI cards
- Interactive charts
- Sidebar navigation
- Responsive layout
- Professional color accents
- Interactive tables
- Download options

---

## ⚙️ How to Run the Project Locally

### 1. Clone the repository

```bash
git clone https://github.com/harsimrankaur271105-cloud/Indian-job-market-Analysis.git
```

### 2. Open the project folder

```bash
cd Indian-job-market-Analysis
```

### 3. Install required packages

```bash
pip install streamlit pandas numpy altair
```

### 4. Run the application

```bash
streamlit run app.py
```

The application will open in your browser.

---

## 🌐 Live Application

The project can be deployed using **Streamlit Community Cloud**.

Once deployed, the application can be accessed through a public `streamlit.app` URL.

---

## 🎯 Project Objectives

The main objectives of this project are:

1. Analyze the Indian job market using real job-listing data.
2. Understand salary patterns across different roles and experience levels.
3. Identify highly demanded skills.
4. Explore companies and locations offering job opportunities.
5. Help users discover suitable job opportunities.
6. Identify skill gaps for target career roles.
7. Provide data-driven salary estimates.
8. Present complex job-market information through an easy-to-use dashboard.

---

## 🔮 Future Enhancements

The project can be further improved by adding:

- Machine-learning based salary prediction
- Advanced job recommendation models
- Resume analysis
- Resume-to-job matching
- More advanced NLP-based job-description analysis
- Real-time job APIs
- Job alerts
- Personalized career roadmaps
- Additional interactive visualizations
- More datasets from different job platforms

---

## 👩‍💻 Project

**Project Title:** Indian Job Market Analysis

**Application Type:** Interactive Data Analytics & Career Intelligence Dashboard

**Framework:** Streamlit

**Language:** Python

---

## 📌 Conclusion

The **Indian Job Market Analysis** application combines data analysis, visualization, and career-oriented tools into a single interactive platform.

It allows users to explore job opportunities, understand salary trends, identify important skills, analyze career paths, receive job recommendations, evaluate skill gaps, and estimate salaries using job-market data.

The project demonstrates the practical application of **Python, Pandas, NumPy, Streamlit, data visualization, and data-driven decision making** in the field of career and job-market analytics.

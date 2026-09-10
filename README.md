# A VISUAL STUDY OF E-COMMERCE ORDERS, DELIVERY & CUSTOMER SATISFACTION

**DATA VISUALIZATION DESIGN (BSCS4001)**

**Team:** Team 2

**Team members:**

Sahib Randhawa — `21F1006116`
Yash Arabhavi — `22F3001882`
Anushka — `21F1003889`
Ashwanth V — `22F3001662`
Kannan S — `21F3000990`

This project analyzes a Brazilian e-commerce dataset to understand delivery performance, seller performance, regional logistics, product pricing, and customer satisfaction.

## Project Resources

- Presentation: [PRESENTATION.pdf](https://github.com/DSAshv/DVDProject/blob/master/PRESENTATION.pdf)
- Project management page: [dvd-project.streamlit.app](https://dvd-project.streamlit.app/)
- Interactive dashboard: [Open dashboard](https://dvd-project.streamlit.app/?page=dashboard)
- Repository: [github.com/DSAshv/DVDProject](https://github.com/DSAshv/DVDProject)

## Reproducibility

From the repository root:

```bash
python3 -m pip install -r requirements.txt
python preprocess.py
streamlit run app.py
```

Run preprocessing before analysis so that the files in `processed_data/` are regenerated from the raw dataset. The Streamlit portal provides access to the raw-data overview, cleaned-data overview, EDA, business questions, analyses, and deliverables. Individual notebooks can be opened and rerun from the `analysis/` directory.
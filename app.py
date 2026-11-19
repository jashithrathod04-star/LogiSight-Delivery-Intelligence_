
        view = df[txt]

    st.caption(f"Showing {len(view):,} of {len(df):,} filtered records (click a column header to sort).")

    st.dataframe(view, width="stretch", hide_index=True, height=420)

    summ = pd.DataFrame({"Metric": list(S.keys()), "Value": [round(v, 4) if isinstance(v, float) else v for v in S.values()]})

    report_txt = (
        "LogiSight analytical summary\\n"
        + "\\n".join(f"{k}: {fmt(v, 2)}" for k, v in S.items())
        + "\\n\\nOperational insights\\n"
        + "\\n".join("- " + l.replace("**", "") for l in ins.generate(df))
    )

    c = st.columns(5)

    c[0].download_button("Cleaned dataset", csv_bytes(clean), "cleaned_dataset.csv", "text/csv", width="stretch")

    c[1].download_button("Filtered dataset", csv_bytes(df), "filtered_dataset.csv", "text/csv", width="stretch")

    c[2].download_button("Statistical summary", csv_bytes(summ), "statistical_summary.csv", "text/csv", width="stretch")

    c[3].download_button("Late deliveries", csv_bytes(df[df["Is_Late"]]), "late_deliveries.csv", "text/csv", width="stretch")

    c[4].download_button("Insights report", report_txt.encode("utf-8"), "analytical_summary.txt", "text/plain", width="stretch")

    st.markdown("### Statistical summary (filtered data)")

    table(summ)



else:

    r = report

    c = st.columns(5)

    kpi(c[0], "Raw records", f"{r['raw_rows']:,}", "", "Rows in the source")

    kpi(c[1], "Duplicates removed", f"{r['duplicates']:,}", "", "Repeated Order_ID")

    kpi(c[2], "Invalid time excluded", f"{r['invalid_time_dropped']:,}", "", "Missing/invalid Delivery_Time")

    kpi(c[3], "Cleaned records", f"{r['final_rows']:,}", "", "Used in all analysis")

    kpi(c[4], "Invalid values", f"{sum(r['invalid_counts'].values()):,}", "", "Text or out-of-range numbers")

    st.markdown("### Cleaning actions")

    if r["log"].empty:

        st.success("No cleaning actions were needed.")

    else:

        table(r["log"])

    a, b = st.columns(2)

    with a:

        st.markdown("### Missing values (before → after)")

        table(pd.DataFrame({"Column": r["missing_before"].index, "Before": r["missing_before"].values, "After": r["missing_after"].values}))

    with b:

        st.markdown("### Column data types")

        table(pd.DataFrame({"Column": clean.columns, "Type": clean.dtypes.astype(str).values}))

    st.markdown("### Records before and after cleaning")

    a, b = st.columns(2)

    a.caption("Original (unchanged)"); a.dataframe(raw.head(8), width="stretch", hide_index=True)

    b.caption("Cleaned working copy"); b.dataframe(clean.head(8), width="stretch", hide_index=True)

    st.markdown("### Statistical methodology")

    st.latex(r"\mu=\frac{1}{n}\sum_{i=1}^{n}t_i \qquad \sigma=\sqrt{\frac{1}{n-1}\sum_{i=1}^{n}(t_i-\mu)^2} \qquad T_{late}=\mu+\sigma")

    st.latex(r"\text{Late \%}=\frac{**\#\\{**&#x74;_i>T_{late}\}}{n_{valid}}\times 100 \qquad IQR=Q_3-Q_1")

    st.markdown(f"""

- **Convention:** the *sample* standard deviation (divide by n − 1) is used everywhere. For this data μ = {fmt(mu_all, 2)} min, σ = {fmt(sd_all, 2)} min, T_late = {fmt(T, 2)} min.

- **Late threshold:** an order is late when Delivery_Time > μ + σ. This is a statistical threshold defined for this project, **not an official company SLA**. It is computed once on the full cleaned dataset so the definition of "late" stays constant while filters change; KPIs, percentages and charts respond to filters.

- **Why μ + σ:** if times were roughly normal, about 16% of orders would exceed it, so it flags unusually slow deliveries relative to this dataset.

- **Age groups:** Below 25 (age < 25), 25–40 (25 ≤ age ≤ 40), Above 40 (age > 40); missing ages are median-imputed first.

- **Cleaning choices:** median for numeric gaps (robust to outliers), mode for categorical gaps. Delivery_Time is the outcome variable, so rows without a valid value are excluded rather than imputed. Valid ranges: time > 0, rating 0–5, age 1–100.

- **Interpretation:** all findings are descriptive associations. They do not show that weather, traffic, vehicle or agent characteristics *cause* delays.

- **Limitations:** imputation can understate variability; groups with few orders give unstable averages (insights need ≥ {ins.MIN_GROUP} orders per group and ≥ {ins.MIN_TOTAL} overall); scatter plots sample 1,500 points for display only; no time or distance variables are available to control for confounding.

""")

    st.markdown("### FA-1 plan → FA-2 implementation")

    table(pd.DataFrame({"FA-1 planned feature": ["Delay Analyzer", "Vehicle Comparison", "Agent Performance Insights", "Regional Bottleneck Finder", "Category Visualizer", "Sidebar filters", "Data logic flow"],

                        "Implemented as": [PAGES[1], PAGES[2], PAGES[3], PAGES[4], PAGES[5], "Global sidebar filters (7 filters + reset)", "utils/preprocessing.py → calculations.py → charts.py"]}))

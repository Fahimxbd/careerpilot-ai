from __future__ import annotations

from datetime import date, datetime
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from src.analytics import applications_over_time, source_performance, status_counts, summary_metrics
from src.db import (
    PRIORITIES,
    STATUSES,
    add_application,
    clear_all,
    delete_application,
    get_application,
    init_db,
    list_applications,
    seed_demo_data,
    update_application,
)
from src.matcher import analyze_match
from src.utils import is_valid_email, is_valid_url, iso_date

APP_DIR = Path(__file__).resolve().parent
DB_PATH = APP_DIR / "data" / "careerpilot.db"

st.set_page_config(
    page_title="CareerPilot AI",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)


def inject_css() -> None:
    st.markdown(
        """
        <style>
        .block-container {padding-top: 1.4rem; padding-bottom: 3rem; max-width: 1450px;}
        [data-testid="stSidebar"] {border-right: 1px solid rgba(128,128,128,.2);}
        .hero {
            padding: 1.35rem 1.5rem; border: 1px solid rgba(128,128,128,.22);
            border-radius: 18px; margin-bottom: 1.2rem;
            background: linear-gradient(135deg, rgba(69,110,255,.13), rgba(100,210,190,.06));
        }
        .hero h1 {margin: 0; font-size: clamp(2rem, 4vw, 3.2rem); letter-spacing: -0.04em;}
        .hero p {margin: .4rem 0 0; opacity: .78; font-size: 1.03rem;}
        .metric-note {font-size:.82rem; opacity:.66; margin-top:-.4rem;}
        .score-pill {display:inline-block; padding:.35rem .75rem; border-radius:999px;
            border:1px solid rgba(128,128,128,.28); font-weight:700; margin:.15rem .25rem .15rem 0;}
        .footer {opacity:.62; font-size:.84rem; text-align:center; padding-top:2rem;}
        div[data-testid="stMetric"] {border: 1px solid rgba(128,128,128,.2); padding: .85rem;
            border-radius: 14px; background: rgba(128,128,128,.025);}
        </style>
        """,
        unsafe_allow_html=True,
    )


def page_header(title: str, subtitle: str) -> None:
    st.markdown(f'<div class="hero"><h1>{title}</h1><p>{subtitle}</p></div>', unsafe_allow_html=True)


def show_sidebar() -> str:
    with st.sidebar:
        st.title("🎯 CareerPilot AI")
        st.caption("Track smarter. Tailor better. Apply consistently.")
        page = st.radio(
            "Navigation",
            ["Overview", "Applications", "Match Lab", "Analytics", "About"],
            label_visibility="collapsed",
        )
        st.divider()
        st.subheader("Demo controls")
        if st.button("Load sample data", use_container_width=True):
            added = seed_demo_data(DB_PATH)
            st.success(f"Added {added} sample applications." if added else "Database already has data.")
        with st.expander("Danger zone"):
            confirm = st.checkbox("I understand this deletes all local records")
            if st.button("Reset database", type="secondary", use_container_width=True, disabled=not confirm):
                clear_all(DB_PATH)
                st.success("All records deleted.")
        st.divider()
        st.caption("No external AI API • Local SQLite • Explainable matching")
    return page


def overview_page() -> None:
    page_header("Job search, under control.", "A practical command center for applications, follow-ups, and CV-to-role matching.")
    df = list_applications(DB_PATH)
    metrics = summary_metrics(df)
    cols = st.columns(6)
    labels = [
        ("Applications", metrics["total"]), ("Active", metrics["active"]),
        ("Interviews", metrics["interviews"]), ("Offers", metrics["offers"]),
        ("Avg. match", f"{metrics['avg_match']:.0f}%"), ("Response rate", f"{metrics['response_rate']:.0f}%"),
    ]
    for col, (label, value) in zip(cols, labels, strict=True):
        col.metric(label, value)

    if df.empty:
        st.info("No applications yet. Load sample data or add your first role from the Applications page.")
        return

    left, right = st.columns([1.15, 1])
    with left:
        st.subheader("Pipeline")
        counts = status_counts(df)
        fig = px.bar(counts, x="status", y="count", text_auto=True)
        fig.update_layout(height=360, margin=dict(l=10, r=10, t=20, b=10), xaxis_title=None, yaxis_title=None)
        st.plotly_chart(fig, use_container_width=True)
    with right:
        st.subheader("Weekly application activity")
        weekly = applications_over_time(df)
        if weekly.empty:
            st.info("Add applied dates to see activity over time.")
        else:
            fig = px.line(weekly, x="date", y="applications", markers=True)
            fig.update_layout(height=360, margin=dict(l=10, r=10, t=20, b=10), xaxis_title=None, yaxis_title=None)
            st.plotly_chart(fig, use_container_width=True)

    st.subheader("Priority queue")
    queue = df[df["status"].isin(["Saved", "Applied", "Screening", "Interview"])].copy()
    priority_rank = {"High": 0, "Medium": 1, "Low": 2}
    queue["priority_rank"] = queue["priority"].map(priority_rank).fillna(3)
    queue = queue.sort_values(["priority_rank", "deadline", "updated_at"]).head(8)
    if queue.empty:
        st.success("No active follow-ups. Keep prospecting.")
    else:
        st.dataframe(
            queue[["company", "role", "status", "priority", "deadline", "match_score", "source"]],
            use_container_width=True,
            hide_index=True,
            column_config={
                "match_score": st.column_config.ProgressColumn("Match", min_value=0, max_value=100, format="%d%%"),
                "job_url": st.column_config.LinkColumn("Job link"),
            },
        )


def application_form(existing: dict | None = None, form_key: str = "application_form") -> tuple[bool, dict]:
    existing = existing or {}
    with st.form(form_key, clear_on_submit=existing == {}):
        a, b = st.columns(2)
        company = a.text_input("Company *", value=existing.get("company", ""))
        role = b.text_input("Role *", value=existing.get("role", ""))
        a, b, c = st.columns(3)
        location = a.text_input("Location", value=existing.get("location", ""))
        job_type_options = ["Remote", "Hybrid", "On-site", "Part-time", "Internship", "Contract"]
        current_type = existing.get("job_type", "Remote")
        job_type = b.selectbox("Work type", job_type_options, index=job_type_options.index(current_type) if current_type in job_type_options else 0)
        source = c.text_input("Source", value=existing.get("source", ""), placeholder="LinkedIn, referral, company site")

        a, b = st.columns(2)
        job_url = a.text_input("Job URL", value=existing.get("job_url", ""))
        salary_range = b.text_input("Salary range", value=existing.get("salary_range", ""), placeholder="€15–18/hour")

        a, b, c, d = st.columns(4)
        current_status = existing.get("status", "Saved")
        status = a.selectbox("Status", STATUSES, index=STATUSES.index(current_status) if current_status in STATUSES else 0)
        current_priority = existing.get("priority", "Medium")
        priority = b.selectbox("Priority", PRIORITIES, index=PRIORITIES.index(current_priority) if current_priority in PRIORITIES else 1)

        def parse_date(value: str):
            try:
                return datetime.strptime(value, "%Y-%m-%d").date() if value else None
            except ValueError:
                return None

        applied_date = c.date_input("Applied date", value=parse_date(existing.get("applied_date", "")), format="YYYY-MM-DD")
        deadline = d.date_input("Deadline", value=parse_date(existing.get("deadline", "")), format="YYYY-MM-DD")

        a, b = st.columns(2)
        contact_person = a.text_input("Contact person", value=existing.get("contact_person", ""))
        contact_email = b.text_input("Contact email", value=existing.get("contact_email", ""))

        a, b = st.columns(2)
        cv_version = a.text_input("CV version", value=existing.get("cv_version", ""), placeholder="CV-Python-v2")
        match_score_default = int(existing.get("match_score") or 0)
        match_score = b.slider("Match score", 0, 100, match_score_default)
        notes = st.text_area("Notes / next action", value=existing.get("notes", ""), height=110)
        submitted = st.form_submit_button("Save application", type="primary", use_container_width=True)

    data = {
        "company": company.strip(), "role": role.strip(), "location": location.strip(),
        "job_type": job_type, "source": source.strip(), "job_url": job_url.strip(),
        "salary_range": salary_range.strip(), "status": status, "priority": priority,
        "applied_date": iso_date(applied_date), "deadline": iso_date(deadline),
        "contact_person": contact_person.strip(), "contact_email": contact_email.strip(),
        "cv_version": cv_version.strip(), "match_score": match_score, "notes": notes.strip(),
    }
    return submitted, data


def applications_page() -> None:
    page_header("Application pipeline", "Capture every role, keep follow-ups visible, and stop losing opportunities in scattered notes.")
    add_tab, manage_tab, export_tab = st.tabs(["➕ Add", "🗂 Manage", "⬇ Export"])

    with add_tab:
        submitted, data = application_form(form_key="add_application_form")
        if submitted:
            errors = []
            if not data["company"] or not data["role"]:
                errors.append("Company and role are required.")
            if not is_valid_url(data["job_url"]):
                errors.append("Job URL must start with http:// or https://.")
            if not is_valid_email(data["contact_email"]):
                errors.append("Contact email is invalid.")
            if errors:
                for error in errors:
                    st.error(error)
            else:
                add_application(DB_PATH, data)
                st.success("Application saved.")
                st.rerun()

    with manage_tab:
        top_a, top_b = st.columns([1, 2])
        selected_statuses = top_a.multiselect("Filter status", STATUSES)
        search = top_b.text_input("Search company, role, or location")
        df = list_applications(DB_PATH, selected_statuses or None, search)
        if df.empty:
            st.info("No matching applications.")
        else:
            display = df[["id", "company", "role", "location", "status", "priority", "applied_date", "deadline", "match_score", "source"]]
            st.dataframe(
                display,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "id": st.column_config.NumberColumn("ID", width="small"),
                    "match_score": st.column_config.ProgressColumn("Match", min_value=0, max_value=100, format="%d%%"),
                },
            )
            choices = {f"#{row.id} — {row.company} / {row.role}": int(row.id) for row in df.itertuples()}
            selected_label = st.selectbox("Select a record to edit", list(choices))
            selected_id = choices[selected_label]
            selected = get_application(DB_PATH, selected_id)
            if selected:
                st.divider()
                submitted, updates = application_form(selected, form_key=f"edit_application_form_{selected_id}")
                if submitted:
                    if not updates["company"] or not updates["role"]:
                        st.error("Company and role are required.")
                    elif not is_valid_url(updates["job_url"]):
                        st.error("Job URL must start with http:// or https://.")
                    elif not is_valid_email(updates["contact_email"]):
                        st.error("Contact email is invalid.")
                    else:
                        update_application(DB_PATH, selected_id, updates)
                        st.success("Application updated.")
                        st.rerun()
                with st.expander("Delete this record"):
                    if st.button("Delete permanently", key=f"delete_{selected_id}"):
                        delete_application(DB_PATH, selected_id)
                        st.success("Application deleted.")
                        st.rerun()

    with export_tab:
        df = list_applications(DB_PATH)
        st.write("Download a portable CSV backup of the current database.")
        st.download_button(
            "Download applications.csv",
            data=df.to_csv(index=False).encode("utf-8"),
            file_name=f"careerpilot-applications-{date.today().isoformat()}.csv",
            mime="text/csv",
            disabled=df.empty,
            use_container_width=True,
        )
        if not df.empty:
            st.dataframe(df, use_container_width=True, hide_index=True)


def match_lab_page() -> None:
    page_header("CV Match Lab", "Compare a CV with a job description using local TF-IDF similarity and transparent skill-gap analysis.")
    st.caption("This is a decision-support tool, not an ATS guarantee. Keep every claim truthful.")

    default_cv = """Aspiring software and AI engineer with Python, Streamlit, JavaScript, SQL, HTML, CSS, Git and WordPress experience. Built an AI web app, a pharmaceutical inventory website, and data analysis projects using pandas and scikit-learn. Familiar with REST APIs, Firebase, SEO and Linux."""
    default_job = """We are hiring a Junior Python Developer. You will build REST APIs, write automated tests, work with SQL databases, Git and Docker, and collaborate in an Agile team. Experience with FastAPI, CI/CD and AWS is an advantage."""

    left, right = st.columns(2)
    cv_text = left.text_area("CV text", value=default_cv, height=340)
    job_text = right.text_area("Job description", value=default_job, height=340)
    analyze = st.button("Analyze match", type="primary", use_container_width=True)

    if analyze:
        if not cv_text.strip() or not job_text.strip():
            st.error("Paste both CV text and a job description.")
            return
        result = analyze_match(cv_text, job_text)
        a, b, c = st.columns(3)
        a.metric("Overall match", f"{result.overall_score}%")
        b.metric("Text similarity", f"{result.text_similarity}%")
        c.metric("Skill coverage", f"{result.skill_score}%")

        left, right = st.columns(2)
        with left:
            st.subheader("Matched skills")
            if result.matched_skills:
                st.markdown(" ".join(f'<span class="score-pill">✓ {s}</span>' for s in result.matched_skills), unsafe_allow_html=True)
            else:
                st.warning("No catalog skills matched.")
        with right:
            st.subheader("Missing job skills")
            if result.missing_skills:
                st.markdown(" ".join(f'<span class="score-pill">△ {s}</span>' for s in result.missing_skills), unsafe_allow_html=True)
            else:
                st.success("No recognized job skills are missing.")

        st.subheader("Action plan")
        for i, recommendation in enumerate(result.recommendations, 1):
            st.write(f"**{i}.** {recommendation}")

        with st.expander("Detected skill sets"):
            st.write("**CV:**", ", ".join(result.cv_skills) or "None")
            st.write("**Job:**", ", ".join(result.job_skills) or "None")


def analytics_page() -> None:
    page_header("Search analytics", "Measure effort, channel quality, and pipeline movement instead of guessing.")
    df = list_applications(DB_PATH)
    if df.empty:
        st.info("Add applications or load sample data to unlock analytics.")
        return

    metrics = summary_metrics(df)
    a, b, c, d = st.columns(4)
    a.metric("Response rate", f"{metrics['response_rate']}%")
    b.metric("Average match", f"{metrics['avg_match']}%")
    c.metric("Interview count", metrics["interviews"])
    d.metric("Offer count", metrics["offers"])

    left, right = st.columns(2)
    with left:
        st.subheader("Status distribution")
        counts = status_counts(df)
        fig = px.pie(counts, names="status", values="count", hole=.55)
        fig.update_layout(height=380, margin=dict(l=10, r=10, t=20, b=10), legend_title=None)
        st.plotly_chart(fig, use_container_width=True)
    with right:
        st.subheader("Match score by status")
        plot_df = df.copy()
        plot_df["match_score"] = pd.to_numeric(plot_df["match_score"], errors="coerce")
        plot_df = plot_df.dropna(subset=["match_score"])
        if plot_df.empty:
            st.info("Add match scores to compare quality by status.")
        else:
            fig = px.box(plot_df, x="status", y="match_score", points="all")
            fig.update_layout(height=380, margin=dict(l=10, r=10, t=20, b=10), xaxis_title=None, yaxis_title="Match score")
            st.plotly_chart(fig, use_container_width=True)

    st.subheader("Source performance")
    sources = source_performance(df)
    st.dataframe(
        sources,
        use_container_width=True,
        hide_index=True,
        column_config={"response_rate": st.column_config.ProgressColumn("Response rate", min_value=0, max_value=100, format="%.1f%%")},
    )
    st.caption("Use this table to cut low-yield channels and double down on referrals, direct outreach, or job boards that actually respond.")


def about_page() -> None:
    page_header("About the project", "A portfolio-grade Streamlit application built to demonstrate product thinking, Python engineering, data handling, testing, and deployment discipline.")
    st.markdown(
        """
        ### What this repository demonstrates
        - Modular Python architecture rather than one giant script
        - SQLite CRUD operations with parameterized queries
        - Explainable NLP using TF-IDF, cosine similarity, and skill extraction
        - Interactive analytics with pandas and Plotly
        - Input validation, CSV export, automated tests, Docker, and GitHub Actions

        ### Honest limitations
        The matcher is deterministic and local. It does not reproduce a proprietary applicant-tracking system, infer recruiter intent, or guarantee interviews. Its purpose is to help users tailor applications consistently and identify obvious skill gaps.

        ### Suggested portfolio pitch
        > I built CareerPilot AI to solve a problem I face personally: managing a high-volume job search without losing follow-ups or sending generic CVs. The app combines a normalized SQLite data layer, explainable NLP scoring, and actionable analytics in a deployable Streamlit interface.
        """
    )


init_db(DB_PATH)
inject_css()
page = show_sidebar()

if page == "Overview":
    overview_page()
elif page == "Applications":
    applications_page()
elif page == "Match Lab":
    match_lab_page()
elif page == "Analytics":
    analytics_page()
else:
    about_page()

st.markdown('<div class="footer">CareerPilot AI • Built with Python, Streamlit, SQLite and scikit-learn</div>', unsafe_allow_html=True)

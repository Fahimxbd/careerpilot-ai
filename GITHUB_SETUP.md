# Publish this project on GitHub

Recommended repository name: `careerpilot-ai`

Recommended description:

> Local-first job application tracker and explainable CV match analyzer built with Python, Streamlit, SQLite, pandas, Plotly, and scikit-learn.

Recommended topics:

`python` `streamlit` `sqlite` `job-tracker` `nlp` `scikit-learn` `data-visualization` `portfolio-project` `docker` `github-actions`

## Terminal method

```bash
cd careerpilot-ai
git init
git add .
git commit -m "feat: launch CareerPilot AI v1.0"
git branch -M main
git remote add origin https://github.com/Fahimxbd/careerpilot-ai.git
git push -u origin main
```

Create the empty GitHub repository before running the final two commands. Do not add another README, license, or `.gitignore` on GitHub because this project already contains them.

## After pushing

1. Open the repository **Settings → General** and add the description and topics above.
2. Under **Social preview**, upload `assets/social-preview.svg` after converting it to PNG if GitHub requests a raster image.
3. Open the **Actions** tab and confirm the CI workflow passes.
4. Deploy `app.py` on Streamlit Community Cloud.
5. Take real screenshots of the deployed Overview, Match Lab, and Analytics pages.
6. Put them in `docs/images/` and add them to the README.
7. Pin the repository on your GitHub profile.

## First release

Create a GitHub release tagged `v1.0.0` with this title:

> CareerPilot AI v1.0.0 — Application tracking, CV matching, and search analytics

Do not claim that the matcher duplicates a commercial ATS. Describe it accurately as an explainable decision-support tool.

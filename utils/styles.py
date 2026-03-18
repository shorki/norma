import streamlit as st


def apply_global_styles():
    st.markdown(
        """
        <style>
        .stApp {
            background: #f4f6f8;
        }

        [data-testid="stSidebar"] {
            background: #111827;
            border-right: 1px solid #1f2937;
        }

        [data-testid="stSidebar"] * {
            color: #f9fafb !important;
        }

        .hero-card {
            padding: 34px;
            border-radius: 18px;
            color: white;
            margin-bottom: 24px;
        }

        .formal-hero {
            background: linear-gradient(135deg, #111827 0%, #1f2937 55%, #374151 100%);
            box-shadow: 0 10px 30px rgba(17, 24, 39, 0.18);
            border: 1px solid rgba(255,255,255,0.06);
        }

        .hero-badge {
            display: inline-block;
            background: rgba(255,255,255,0.10);
            color: #e5e7eb;
            padding: 6px 12px;
            border-radius: 999px;
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 0.7px;
            margin-bottom: 12px;
            text-transform: uppercase;
        }

        .hero-title {
            font-size: 42px;
            margin-bottom: 8px;
            font-weight: 800;
            letter-spacing: -0.5px;
        }

        .hero-subtitle {
            font-size: 17px;
            color: #e5e7eb;
            margin-bottom: 0;
            max-width: 760px;
            line-height: 1.6;
        }

        .info-card,
        .result-card,
        .metric-box,
        .doc-card,
        .fragment-card,
        .legal-output-card,
        .module-card {
            background: #ffffff;
            border: 1px solid #dde3ea;
            border-radius: 16px;
            box-shadow: 0 6px 18px rgba(15, 23, 42, 0.05);
        }

        .formal-card {
            min-height: 160px;
        }

        .info-card {
            padding: 20px;
            margin-bottom: 14px;
        }

        .info-card h4 {
            margin-top: 0;
            margin-bottom: 10px;
            color: #111827;
            font-size: 18px;
            font-weight: 700;
        }

        .info-card p {
            color: #4b5563;
            line-height: 1.6;
            margin-bottom: 0;
        }

        .module-grid {
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 14px;
            margin-top: 10px;
            margin-bottom: 22px;
        }

        .module-card {
            padding: 18px;
        }

        .module-title {
            font-size: 17px;
            font-weight: 700;
            color: #111827;
            margin-bottom: 8px;
        }

        .module-text {
            color: #4b5563;
            line-height: 1.55;
            font-size: 14px;
        }

        .result-card {
            padding: 22px;
            margin-bottom: 14px;
        }

        .fragment-card {
            background: #fbfcfd;
            border-left: 4px solid #374151;
            padding: 16px;
            margin-bottom: 12px;
        }

        .section-title {
            font-size: 30px;
            font-weight: 800;
            color: #111827;
            margin-bottom: 6px;
            letter-spacing: -0.3px;
        }

        .section-subtitle {
            color: #6b7280;
            margin-bottom: 24px;
            font-size: 15px;
        }

        .metric-box {
            padding: 18px;
            text-align: center;
        }

        .small-muted {
            color: #6b7280;
            font-size: 13px;
        }

        .success-pill {
            display: inline-block;
            background: #eef2f7;
            color: #1f2937;
            padding: 6px 10px;
            border-radius: 999px;
            font-size: 12px;
            font-weight: 700;
            border: 1px solid #d1d5db;
        }

        .warning-pill {
            display: inline-block;
            background: #fef3c7;
            color: #92400e;
            padding: 6px 10px;
            border-radius: 999px;
            font-size: 12px;
            font-weight: 700;
        }

        .danger-pill {
            display: inline-block;
            background: #fee2e2;
            color: #991b1b;
            padding: 6px 10px;
            border-radius: 999px;
            font-size: 12px;
            font-weight: 700;
        }

        .doc-card {
            padding: 16px;
            margin-bottom: 12px;
        }

        .legal-output-card {
            padding: 24px;
            margin-bottom: 18px;
            background: #ffffff;
        }

        .legal-header-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 18px;
        }

        .legal-badge {
            display: inline-block;
            background: #eef2f7;
            color: #374151;
            padding: 7px 12px;
            border-radius: 999px;
            font-size: 11px;
            font-weight: 800;
            letter-spacing: 0.6px;
            border: 1px solid #d1d5db;
        }

        .legal-section {
            border-top: 1px solid #e5e7eb;
            padding-top: 16px;
            margin-top: 16px;
        }

        .legal-section:first-of-type {
            border-top: none;
            padding-top: 0;
            margin-top: 0;
        }

        .legal-section-title {
            font-size: 13px;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.8px;
            color: #4b5563;
            margin-bottom: 10px;
        }

        .legal-list {
            margin: 0;
            padding-left: 18px;
        }

        .legal-list li {
            margin-bottom: 6px;
        }

        .stButton > button {
            background: #111827;
            color: white;
            border-radius: 10px;
            border: 1px solid #111827;
            font-weight: 600;
            padding: 0.6rem 1rem;
        }

        .stButton > button:hover {
            background: #1f2937;
            border-color: #1f2937;
            color: white;
        }

        .stDownloadButton > button {
            border-radius: 10px;
            font-weight: 600;
        }

        @media (max-width: 900px) {
            .module-grid {
                grid-template-columns: 1fr;
            }

            .hero-title {
                font-size: 32px;
            }
        }
        </style>
        """,
        unsafe_allow_html=True
    )
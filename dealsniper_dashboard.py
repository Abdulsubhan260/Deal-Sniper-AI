import os
import requests
import streamlit as st

st.set_page_config(
    page_title="DealSniper AI",
    page_icon="🎯",
    layout="wide"
)

# Point to your decoupled FastAPI backend!
BACKEND_URL = "http://127.0.0.1:7860/snipe-deal"

st.title("🎯 DealSniper AI")
st.markdown("#### Autonomous Freelance Job Intelligence & Proposal Machine")
st.caption("Decoupled Architecture: Streamlit Frontend ──► FastAPI Microservice ──► Swarm & GraphRAG")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("1. Job Posting Screenshot")
    uploaded_file = st.file_uploader("Upload Upwork Screenshot", type=["png", "jpg", "jpeg"])
    if uploaded_file:
        st.image(uploaded_file, caption="Target Job", use_container_width=True)

with col2:
    st.subheader("2. Your Custom Pitch Strategy")
    notes = st.text_area(
        "Custom instructions or demo links (Optional):",
        placeholder="e.g. Offer 2-week delivery at $75/hr and include link to our live Hugging Face demo.",
        height=140
    )
    submit_btn = st.button("🎯 Snipe This Job", type="primary", use_container_width=True)

if submit_btn:
    if not uploaded_file:
        st.error("Please upload a job screenshot first!")
    else:
        with st.spinner("🚀 Contacting FastAPI Backend & Swarm Agents..."):
            try:
                # Prepare multipart form data payload
                files = {"screenshot": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                data = {"custom_notes": notes}
                
                # Shoot HTTP POST request to your backend!
                response = requests.post(BACKEND_URL, files=files, data=data)
                
                if response.status_code == 200:
                    result = response.json()
                    st.success("✅ Deal Successfully Sniped & Proposal Verified!")
                    
                    st.markdown("---")
                    res_col1, res_col2 = st.columns([1.2, 0.8])
                    
                    with res_col1:
                        st.subheader("🏆 Winning Cover Letter")
                        st.text_area("Ready to paste into Upwork:", value=result["proposal"], height=250)
                        
                        with st.expander("🔍 Extracted Job Metadata (Vision)"):
                            st.markdown(result["job_metadata"])
                            
                        with st.expander("📊 Market Benchmarks (Neo4j GraphRAG)"):
                            st.markdown(result["market_intel"])
                            
                    with res_col2:
                        st.subheader("🎧 Interview Coaching Brief")
                        st.markdown(result["coaching_notes"])
                        
                        # Check for generated audio file on local server
                        if os.path.exists("interview_prep.mp3"):
                            st.audio("interview_prep.mp3", format="audio/mp3")
                            
                else:
                    st.error(f"Backend Server Error: {response.status_code}")
                    st.write(response.text)
                    
            except Exception as e:
                st.error(f"Failed to connect to FastAPI backend: {e}")
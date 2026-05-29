import streamlit as st
import hashlib
import requests
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.exceptions import InvalidSignature

st.set_page_config(page_title="Bank APK Verifier", page_icon="🔐")

st.sidebar.title("Workflow")
st.sidebar.write("1. Upload APK")
st.sidebar.write("2. Generate SHA-256 hash (I')")
st.sidebar.write("3. Send I' to bank server")
st.sidebar.write("4. Server compares I' with I")
st.sidebar.write("5. Server generates KEY and SIGN")
st.sidebar.write("6. Client verifies SIGN")
st.sidebar.write("7. Allow or reject installation")

st.title("🔐 Banking APK Verification System")
st.write("Upload APK to verify whether it is original or fake.")

def verify_signature(apk_hash, signature_hex):
    with open("keys/public_key.pem", "rb") as f:
        public_key = serialization.load_pem_public_key(f.read())

    try:
        public_key.verify(
            bytes.fromhex(signature_hex),
            apk_hash.encode(),
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        return True
    except InvalidSignature:
        return False

uploaded_file = st.file_uploader("Upload APK File", type=["apk"])

if uploaded_file is not None:
    file_bytes = uploaded_file.read()
    client_hash = hashlib.sha256(file_bytes).hexdigest()

    st.subheader("Generated APK Hash (I')")
    st.code(client_hash)

    if st.button("Verify APK"):
        try:
            response = requests.post(
                "http://127.0.0.1:5000/verify",
                json={"hash": client_hash}
            )

            result = response.json()

            if result["status"] == "approved":
                is_valid = verify_signature(client_hash, result["signature"])

                st.subheader("Server Response")
                st.write("Generated KEY:")
                st.code(result["key"])

                if is_valid:
                    st.success("Installation Allowed: APK is authentic")
                    st.download_button(
                        label="Download Verified APK",
                        data=file_bytes,
                        file_name=uploaded_file.name,
                        mime="application/vnd.android.package-archive"
                    )
                else:
                    st.error("Installation Failed: Signature invalid")
            else:
                st.error(result["message"])

        except Exception as e:
            st.error(f"Error: {str(e)}")
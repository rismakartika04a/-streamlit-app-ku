import streamlit as st
import re
import os
import tempfile
import zipfile

st.title("Split Dokumen TXT")

uploaded_file = st.file_uploader("Upload file teks (.txt)", type=[])

split_header = st.selectbox("Pilih header pemisah halaman:", ["GAJI KARYAWAN TETAP", "GAJI KARYAWAN KONTRAK"])

if uploaded_file is not None:
    try:
        # Gunakan UTF-8 kalau bisa
        try:
            text = uploaded_file.read().decode("utf-8")
        except UnicodeDecodeError:
            uploaded_file.seek(0)
            text = uploaded_file.read().decode("latin-1")
    except Exception as e:
        st.error(f"Gagal membaca file: {e}")
        st.stop()

    pattern = rf'({split_header}.*?)(?={split_header}|\Z)'
    sections = re.findall(pattern, text, flags=re.DOTALL)
    st.success(f"Ditemukan {len(sections)} bagian berdasarkan header '{split_header}'.")

    with tempfile.TemporaryDirectory() as tmpdirname:
        zip_path = os.path.join(tmpdirname, "split_files.zip")
        zipf = zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED)
        filepaths = []

        for i, section in enumerate(sections, start=1):
            filename = f'gaji_karyawan_page_{i}.txt'
            filepath = os.path.join(tmpdirname, filename)
            # Simpan pakai UTF-8 agar bisa dibaca di mana saja
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(section)
            zipf.write(filepath, arcname=filename)
            filepaths.append((filename, filepath, section))  # Simpan konten juga untuk preview

        zipf.close()

        with open(zip_path, "rb") as f:
            st.download_button(
                label="📦 Download Semua File (.zip)",
                data=f,
                file_name="hasil_split_gaji_karyawan.zip",
                mime="application/zip"
            )

        st.markdown("---")

        for filename, filepath, content in filepaths:
            with st.expander(f"📄 Preview {filename}"):
                preview = "\n".join(content.splitlines()[:20])
                st.text(preview)

                with open(filepath, "rb") as f:
                    st.download_button(
                        label=f"⬇️ Download {filename}",
                        data=f,
                        file_name=filename,
                        mime="text/plain"
                    )

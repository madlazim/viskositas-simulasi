import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import streamlit as st
from datetime import datetime
from matplotlib.animation import PillowWriter

# **STREAMLIT DASHBOARD**
st.title("🔬 Simulasi Gerak Bola dalam Cairan dengan Kontrol Animasi")

# **Inisialisasi session state untuk kontrol animasi**
if "play" not in st.session_state:
    st.session_state.play = False
if "stop" not in st.session_state:
    st.session_state.stop = False
if "reset" not in st.session_state:
    st.session_state.reset = False
if "bola_di_dasar" not in st.session_state:
    st.session_state.bola_di_dasar = False

# **Pengaturan Parameter**
rho_cairan = st.slider("Densitas Cairan (kg/m³)", min_value=500, max_value=2000, value=1000, step=50)  
suhu = st.slider("Suhu Cairan (°C)", min_value=0, max_value=100, value=25, step=5)  
tekanan = st.slider("Tekanan (atm)", min_value=0.5, max_value=2.0, value=1.0, step=0.1)  
rho_bola = st.slider("Densitas Bola (kg/m³)", min_value=1000, max_value=5000, value=2500, step=100)  
radius_bola = st.slider("Jejari Bola (m)", min_value=0.001, max_value=0.02, value=0.005, step=0.001)  

# **Tombol Kontrol Animasi**
if st.button("▶ Play"):
    st.session_state.play = True
    st.session_state.stop = False
    st.session_state.bola_di_dasar = False

if st.button("⏸ Pause"):
    st.session_state.play = False

if st.button("⏹ Stop"):
    st.session_state.play = False
    st.session_state.stop = True

if st.button("🔄 Reset (Bola Kembali ke Permukaan)"):
    st.session_state.play = False
    st.session_state.stop = False
    st.session_state.reset = True
    st.session_state.bola_di_dasar = False
    st.rerun()

# **Fungsi untuk menghitung viskositas berdasarkan suhu, tekanan, dan densitas**
def hitung_viskositas(suhu, tekanan, rho_cairan):
    A = 2.414e-5  # Konstanta
    B = 247.8  
    C = 140  
    viskositas_dasar = A * 10 ** (B / (suhu + C))  
    faktor_densitas = (rho_cairan / 1000) ** 0.5  # Faktor koreksi empiris
    return (viskositas_dasar * faktor_densitas) / tekanan  

mu_cairan = hitung_viskositas(suhu, tekanan, rho_cairan)  

# **Konstanta Fisik**
g = 9.81  

# **Hitung volume dan massa bola**
volume_bola = (4/3) * np.pi * radius_bola**3
massa_bola = rho_bola * volume_bola

# **Hitung percepatan efektif bola akibat gravitasi dan gaya apung**
g_eff = g * (1 - (rho_cairan / rho_bola))

# **Hitung kecepatan terminal berdasarkan hukum Stokes**
v_terminal = (2/9) * ((radius_bola**2) * g_eff * (rho_bola - rho_cairan)) / mu_cairan

# **Waktu simulasi diperpanjang**
t_max = 30  
dt = 0.1  
t_values = np.arange(0, t_max, dt)

# **Inisialisasi posisi bola (mulai dari atas tabung 2 meter)**
y_values = np.zeros_like(t_values)
y_values[0] = 2.0  

# **Simulasi jatuhnya bola dalam cairan**
for i in range(1, len(t_values)):
    if y_values[i-1] > 0:
        dy = v_terminal * (1 - np.exp(-g_eff * t_values[i] / v_terminal)) * dt
        y_values[i] = max(y_values[i-1] - dy, 0)  
    else:
        y_values[i] = 0  

# **MULAI ANIMASI**
fig, ax = plt.subplots(figsize=(5, 12))  

# **Atur batas tampilan tabung**
ax.set_xlim(-0.05, 0.05)
ax.set_ylim(0, 2.2)
ax.set_xticks([])
ax.set_yticks(np.linspace(0, 2, 5))
ax.set_ylabel("Ketinggian (m)")
ax.set_title("Simulasi Gerak Bola dalam Tabung Berisi Cairan (2 Meter)")

# **Gambar tabung**
tabung = plt.Rectangle((-0.02, 0), 0.04, 2, color='lightblue', alpha=0.6)
ax.add_patch(tabung)

# **Inisialisasi bola**
bola, = ax.plot([0], [2], 'ro', markersize=10)

# **Tambahkan teks alat ukur waktu & lintasan**
text_waktu = ax.text(-0.045, 2.1, "", fontsize=12, color="black")
text_jarak = ax.text(-0.045, 2.05, "", fontsize=12, color="black")

# **Fungsi update animasi**
def update(frame):
    if st.session_state.stop:
        return bola, text_waktu, text_jarak

    if not st.session_state.play:
        return bola, text_waktu, text_jarak
    
    # **Hentikan animasi ketika bola mencapai dasar tabung**
    if y_values[frame] <= 0:
        st.session_state.play = False
        st.session_state.bola_di_dasar = True
        return bola, text_waktu, text_jarak

    bola.set_data([0], [y_values[frame]])  
    text_waktu.set_text(f"Waktu: {t_values[frame]:.2f} s")
    text_jarak.set_text(f"Lintasan: {2.0 - y_values[frame]:.2f} m")
    return bola, text_waktu, text_jarak

# **Jalankan animasi**
ani = animation.FuncAnimation(fig, update, frames=len(t_values), interval=100, blit=False)  

# **Simpan animasi sebagai GIF untuk Streamlit**
ani.save("ball_falling_controlled.gif", writer=PillowWriter(fps=5))  

# **Tampilkan animasi di Streamlit**
st.image("ball_falling_controlled.gif", caption="Simulasi Gerak Bola dengan Kontrol Animasi")

# **Tampilkan hasil perhitungan**
st.markdown(f"""
- **Densitas cairan:** {rho_cairan} kg/m³
- **Densitas bola:** {rho_bola} kg/m³
- **Jejari bola:** {radius_bola:.3f} m
- **Viskositas cairan:** {mu_cairan:.6f} Pa.s
- **Kecepatan terminal bola:** {v_terminal:.4f} m/s
- **Percepatan efektif bola:** {g_eff:.4f} m/s²
""")

import streamlit as st
from fpdf import FPDF

class InvoicePDF(FPDF):
    def header(self):
        pass

def create_invoice_pdf(lasku_nro, asiakas_nimi, asiakas_ytunnus, tuotteet, erapaiva, viesti):
    pdf = InvoicePDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Используем стандартный шрифт Helvetica
    pdf.set_font("Helvetica", size=10)
    
    # 1. ЗАГОЛОВОК
    pdf.set_text_color(41, 128, 185) # Синий цвет
    pdf.set_font("Helvetica", style="B", size=18)
    pdf.cell(0, 8, "LASKU", ln=True)
    
    # 2. ДАННЫЕ ПРОДАВЦА
    pdf.set_font("Helvetica", style="B", size=10)
    pdf.cell(0, 5, "Nihtisillan autohuolto ja korjaus", ln=True)
    
    pdf.set_text_color(80, 80, 80)
    pdf.set_font("Helvetica", size=9)
    pdf.cell(0, 4, "Y-tunnus: 3488305-9", ln=True)
    pdf.cell(0, 4, "Nihtisillantie 1", ln=True)
    pdf.cell(0, 4, "ESPOO 02630", ln=True)
    pdf.cell(0, 4, "(+358) 45 2526 125", ln=True)
    pdf.cell(0, 4, "nihtisillanautohuolto@gmail.com", ln=True)
    pdf.ln(5)
    
    # 3. ДАННЫЕ СЧЕТА И КЛИЕНТА
    pdf.set_text_color(41, 128, 185)
    pdf.set_font("Helvetica", style="B", size=10)
    pdf.cell(0, 5, f"Lasku Nro. {lasku_nro}", ln=True)
    
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", style="B", size=9)
    pdf.cell(0, 4, "Asiakas:", ln=True)
    
    pdf.set_text_color(102, 0, 102) # Фиолетовый
    pdf.cell(0, 4, str(asiakas_nimi), ln=True)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 4, str(asiakas_ytunnus), ln=True)
    pdf.ln(8)
    
    # 4. ШАПКА ТАБЛИЦЫ
    pdf.set_font("Helvetica", style="B", size=9)
    pdf.cell(100, 5, "Tuote/palvelu", ln=0)
    pdf.cell(40, 5, "Kpl/tunti", ln=0)
    pdf.cell(30, 5, "Hinta", ln=1)
    
    # 5. ТОВАРЫИ УСЛУГИ (Вместо € используем EUR)
    pdf.set_font("Helvetica", size=9)
    yht_summa = 0.0
    for item in tuotteet:
        nimi = str(item["nimi"])
        maara = str(item["maara"])
        hinta = float(item["hinta"])
        yht_summa += hinta
        pdf.cell(100, 4, nimi, ln=0)
        pdf.cell(40, 4, maara, ln=0)
        pdf.cell(30, 4, f"{hinta:.2f} EUR", ln=1)
        
    pdf.set_draw_color(180, 180, 180)
    pdf.line(10, pdf.get_y() + 2, 180, pdf.get_y() + 2)
    pdf.ln(4)
    
    # 6. ИТОГИ И НАЛОГИ (ALV 25.5%)
    veroton = yht_summa / 1.255
    alv_osuus = yht_summa - veroton
    
    pdf.set_font("Helvetica", style="B", size=9)
    pdf.cell(140, 4, "YHT.", ln=0)
    pdf.cell(30, 4, f"{yht_summa:.2f} EUR", ln=1)
    pdf.cell(140, 4, "Veroton", ln=0)
    pdf.cell(30, 4, f"{veroton:.2f} EUR", ln=1)
    pdf.cell(140, 4, "ALV. Osuus", ln=0)
    pdf.cell(30, 4, f"{alv_osuus:.2f} EUR", ln=1)
    pdf.ln(8)
    
    # 7. РЕКВИЗИТЫ ОПЛАТЫ
    pdf.cell(0, 5, "Maksutapa: Tilisiiro", ln=True)
    pdf.cell(0, 5, "Saaja: Nihtisillan autohuolto ja korjaamo Oy", ln=True)
    pdf.cell(0, 5, "IBAN: FI6979977992229018", ln=True)
    pdf.cell(0, 5, f"Maksettava summa: {yht_summa:.2f} EUR", ln=True)
    pdf.cell(0, 5, f"Erapaiva: {erapaiva}", ln=True)
    pdf.cell(0, 5, f"Viesti: {viesti}", ln=True)
    
    filename = "generated_lasku.pdf"
    pdf.output(filename)
    return filename

# --- ИНТЕРФЕЙС STREAMLIT ---
st.title("Система счетов Nihtisillan Autohuolto")

lasku_nro = st.text_input("Номер счета (Lasku Nro)", "00077")
asiakas_nimi = st.text_input("Имя клиента (Asiakas)", "BEOR PALVELUT OY")
asiakas_ytunnus = st.text_input("Y-tunnus клиента", "3410949-3")

st.subheader("Товары / Услуги")
t1_nimi = st.text_input("Товар 1", "ARS-anuri")
t1_maara = st.text_input("Кол-во 1", "1 kpl")
t1_hinta = st.number_input("Цена 1 (EUR)", value=30.0)

t2_nimi = st.text_input("Товар 2", "Asennustyot")
t2_maara = st.text_input("Кол-во 2", "0.5 h")
t2_hinta = st.number_input("Цена 2 (EUR)", value=50.0)

erapaiva = st.text_input("Срок оплаты (Erapaiva)", "18.9.2026")
viesti = st.text_input("Сообщение (Viesti)", "Jumper77")

if st.button("Сформировать PDF"):
    tuotteet = [
        {"nimi": t1_nimi, "maara": t1_maara, "hinta": t1_hinta},
        {"nimi": t2_nimi, "maara": t2_maara, "hinta": t2_hinta}
    ]
    pdf_file = create_invoice_pdf(lasku_nro, asiakas_nimi, asiakas_ytunnus, tuotteet, erapaiva, viesti)
    
    with open(pdf_file, "rb") as f:
        st.download_button(
            label="📥 Скачать готовый счет (PDF)",
            data=f,
            file_name=f"Lasku_{lasku_nro}.pdf",
            mime="application/pdf"
        )

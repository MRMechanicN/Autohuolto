from fpdf import FPDF

class InvoicePDF(FPDF):
    def header(self):
        # Если есть логотип, раскомментируйте строчку ниже:
        # self.image('logo.png', x=140, y=10, w=55)
        pass

def create_invoice(filename="invoice.pdf"):
    pdf = InvoicePDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Поддержка стандартных шрифтов (для финского языка используйте шрифт с UTF-8, например DejaVu)
    pdf.set_font("Helvetica", size=10)
    
    # 1. ЗАГОЛОВОК СЧЁТА
    pdf.set_text_color(41, 128, 185) # Синий цвет
    pdf.set_font("Helvetica", style="B", size=18)
    pdf.cell(0, 8, "LASKU", ln=True)
    
    # 2. РЕКВИЗИТЫ КОМПАНИИ (Исполнитель)
    pdf.set_text_color(41, 128, 185)
    pdf.set_font("Helvetica", style="B", size=10)
    pdf.cell(0, 5, "Nihtisillan autohuolto ja korjaus", ln=True)
    
    pdf.set_text_color(80, 80, 80)
    pdf.set_font("Helvetica", size=9)
    pdf.cell(35, 4, "Y-tunnus:", ln=0)
    pdf.cell(0, 4, "3488305-9", ln=True)
    pdf.cell(0, 4, "Nihtisillantie 1", ln=True)
    pdf.cell(0, 4, "ESPOO 02630", ln=True)
    pdf.cell(0, 4, "(+358) 45 2526 125", ln=True)
    pdf.cell(0, 4, "nihtisillanautohuolto@gmail.com", ln=True)
    
    pdf.ln(5)
    
    # 3. НОМЕР СЧЁТА И ДАННЫЕ КЛИЕНТА
    pdf.set_text_color(41, 128, 185)
    pdf.set_font("Helvetica", style="B", size=10)
    pdf.cell(0, 5, "Lasku Nro. 00077", ln=True)
    
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", style="B", size=9)
    pdf.cell(0, 4, "Asiakas:", ln=True)
    
    pdf.set_text_color(102, 0, 102) # Фиолетовый цвет для клиента
    pdf.cell(0, 4, "BEOR PALVELUT OY", ln=True)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 4, "3410949-3", ln=True)
    
    pdf.ln(8)
    
    # 4. ТАБЛИЦА С УСЛУГАМИ / ТОВАРАМИ
    pdf.set_font("Helvetica", style="B", size=9)
    pdf.cell(100, 5, "Tuote/palvelu", ln=0)
    pdf.cell(40, 5, "Kpl/tunti", ln=0)
    pdf.cell(30, 5, "Hinta", ln=1)
    
    pdf.set_font("Helvetica", size=9)
    # Позиция 1
    pdf.cell(100, 4, "ARS-anuri", ln=0)
    pdf.cell(40, 4, "1 kpl", ln=0)
    pdf.cell(30, 4, "30    €", ln=1)
    # Позиция 2
    pdf.cell(100, 4, "Asennustyöt", ln=0)
    pdf.cell(40, 4, "0.5 h", ln=0)
    pdf.cell(30, 4, "50    €", ln=1)
    
    # Линия-разделитель
    pdf.set_draw_color(180, 180, 180)
    pdf.line(10, pdf.get_y() + 2, 180, pdf.get_y() + 2)
    pdf.ln(4)
    
    # 5. ИТОГИ (YHT, Veroton, ALV)
    pdf.set_font("Helvetica", style="B", size=9)
    pdf.cell(140, 4, "YHT.", ln=0)
    pdf.cell(30, 4, "80    €", ln=1)
    
    pdf.cell(140, 4, "Veroton", ln=0)
    pdf.cell(30, 4, "63.75  €", ln=1)
    
    pdf.cell(140, 4, "ALV. Osuus", ln=0)
    pdf.cell(30, 4, "16.25  €", ln=1)
    
    pdf.ln(8)
    
    # 6. БЛОК ОПЛАТЫ (Maksutapa)
    pdf.set_font("Helvetica", style="B", size=9)
    pdf.cell(0, 5, "Maksutapa: Tilisiiro", ln=True)
    pdf.cell(0, 5, "Saaja: Nihtisillan autohuolto ja korjaamo Oy", ln=True)
    pdf.cell(0, 5, "IBAN: FI6979977992229018", ln=True)
    pdf.cell(0, 5, "Maksettava summa: 80 €", ln=True)
    pdf.cell(0, 5, "Eräpäivä: 18.9.2026", ln=True)
    pdf.cell(0, 5, "Viesti: Jumper77", ln=True)
    
    # Сохранение файла
    pdf.output(filename)

if __name__ == "__main__":
    create_invoice()

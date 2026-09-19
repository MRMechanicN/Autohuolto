import json
import os
from datetime import date, datetime
from fpdf import FPDF
import pandas as pd
import streamlit as st

# --- НАСТРОЙКА СТРАНИЦЫ ---
st.set_page_config(page_title="Nihtisillan Autohuolto System", layout="wide")

DB_FILE = "database.json"

# --- РАБОТА С БАЗОЙ ДАННЫХ ---
def load_data():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"clients": {}, "records": []}
    return {"clients": {}, "records": []}

def save_data(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

db = load_data()

# --- ГЕНЕРАЦИЯ PDF С ПОДДЕРЖКОЙ UTF-8 ---
class UnicodePDF(FPDF):
    def __init__(self):
        super().__init__()
        try:
            self.add_font("DejaVu", "", "DejaVuSans.ttf", uni=True)
            self.add_font("DejaVu", "B", "DejaVuSans-Bold.ttf", uni=True)
            self.font_family = "DejaVu"
        except Exception:
            self.font_family = "Helvetica"

def generate_pdf(doc_type, doc_num, client_name, client_ytunnus, items, date_str, iban="FI6979977992229018"):
    pdf = UnicodePDF()
    pdf.add_page()
    font_name = pdf.font_family

    def safe_str(val):
        val_str = str(val)
        if font_name == "Helvetica":
            return val_str.encode("latin-1", "replace").decode("latin-1")
        return val_str

    # Шапка компании
    pdf.set_font(font_name, "B", 16)
    pdf.cell(0, 8, safe_str("Nihtisillan autohuolto ja korjaamo"), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font(font_name, "", 10)
    pdf.cell(0, 5, safe_str("Y-tunnus: 3488305-9 | Tel: (+358) 45 2526 125"), new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 5, safe_str("nihtisillanautohuolto@gmail.com"), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)

    # Детали документа
    pdf.set_font(font_name, "B", 14)
    pdf.cell(0, 8, safe_str(f"{doc_type.upper()} Nro. {doc_num}"), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font(font_name, "", 11)
    pdf.cell(0, 6, safe_str(f"Päivämäärä: {date_str}"), new_x="LMARGIN", new_y="NEXT")

    if client_name:
        pdf.ln(2)
        pdf.set_font(font_name, "B", 11)
        pdf.cell(0, 6, safe_str(f"Asiakas: {client_name}"), new_x="LMARGIN", new_y="NEXT")
        if client_ytunnus:
            pdf.set_font(font_name, "", 10)
            pdf.cell(0, 5, safe_str(f"Y-tunnus: {client_ytunnus}"), new_x="LMARGIN", new_y="NEXT")

    pdf.ln(5)

    # Таблица позиций
    pdf.set_font(font_name, "B", 10)
    pdf.cell(90, 7, safe_str("Tuote / palvelu"), 1)
    pdf.cell(30, 7, safe_str("Kpl / h"), 1)
    pdf.cell(30, 7, safe_str("Hinta (€)"), 1)
    pdf.cell(30, 7, safe_str("Yht (€)"), 1, new_x="LMARGIN", new_y="NEXT")

    pdf.set_font(font_name, "", 10)
    total_sum = 0.0
    for item in items:
        qty = float(item["qty"])
        price = float(item["price"])
        total = qty * price
        total_sum += total

        pdf.cell(90, 6, safe_str(item["name"]), 1)
        pdf.cell(30, 6, safe_str(f"{qty:.2f}"), 1)
        pdf.cell(30, 6, safe_str(f"{price:.2f}"), 1)
        pdf.cell(30, 6, safe_str(f"{total:.2f}"), 1, new_x="LMARGIN", new_y="NEXT")

    # Расчет ALV (25.5%)
    alv_rate = 0.255
    veroton = total_sum / (1 + alv_rate)
    alv_amount = total_sum - veroton

    pdf.ln(5)
    pdf.set_font(font_name, "B", 11)
    pdf.cell(0, 6, safe_str(f"YHTEENSA: {total_sum:.2f} EUR"), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font(font_name, "", 10)
    pdf.cell(0, 5, safe_str(f"Veroton: {veroton:.2f} EUR"), new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 5, safe_str(f"ALV (25.5%): {alv_amount:.2f} EUR"), new_x="LMARGIN", new_y="NEXT")

    if doc_type == "Lasku":
        pdf.ln(5)
        pdf.cell(0, 6, safe_str(f"Maksutapa: Tilisiirto | IBAN: {iban}"), new_x="LMARGIN", new_y="NEXT")

    return bytes(pdf.output())

# --- ИНТЕРФЕЙС ---
st.title("🚗 Nihtisillan Autohuolto System")

menu = st.sidebar.selectbox("Навигация", ["Выписать документ (Lasku/Kuitti)", "База клиентов", "Таблица учета", "Календарь"])

if menu == "Выписать документ (Lasku/Kuitti)":
    st.header("📄 Создание документа")

    if "item_list" not in st.session_state:
        st.session_state.item_list = [{"name": "Työ", "qty": 1.0, "price": 50.0}]

    st.subheader("1. Данные клиента")
    clients_list = ["-- Новый клиент --"] + list(db["clients"].keys())
    selected_client = st.selectbox("Выберите сохраненного клиента:", clients_list)

    if selected_client != "-- Новый клиент --":
        client_name = selected_client
        client_ytunnus = db["clients"][selected_client].get("ytunnus", "")
        st.info(f"Клиент: **{client_name}** | Y-tunnus: **{client_ytunnus}**")
    else:
        c_col1, c_col2 = st.columns(2)
        client_name = c_col1.text_input("Название фирмы / Имя клиента")
        client_ytunnus = c_col2.text_input("Y-tunnus (если есть)")

    st.subheader("2. Параметры документа")
    col1, col2, col3 = st.columns(3)
    doc_type = col1.selectbox("Тип документа", ["Lasku", "Kuitti"])
    
    next_id = len(db["records"]) + 1
    doc_num = col2.text_input("Номер документа", value=f"000{next_id:02d}")
    doc_date = col3.date_input("Дата", value=date.today())
    hours_spent = st.number_input("Отработано часов (h)", min_value=0.0, value=1.0, step=0.5)

    st.subheader("3. Услуги и запчасти")

    def add_item():
        st.session_state.item_list.append({"name": "", "qty": 1.0, "price": 0.0})

    def remove_item(idx):
        if len(st.session_state.item_list) > 1:
            st.session_state.item_list.pop(idx)

    for idx, item in enumerate(st.session_state.item_list):
        c1, c2, c3, c4 = st.columns([4, 1.5, 1.5, 0.8])
        
        st.session_state.item_list[idx]["name"] = c1.text_input(
            f"Наименование #{idx+1}", value=item["name"], key=f"item_name_{idx}"
        )
        st.session_state.item_list[idx]["qty"] = c2.number_input(
            f"Кол-во #{idx+1}", value=float(item["qty"]), key=f"item_qty_{idx}", min_value=0.0, step=0.5
        )
        st.session_state.item_list[idx]["price"] = c3.number_input(
            f"Цена (€) #{idx+1}", value=float(item["price"]), key=f"item_price_{idx}", min_value=0.0, step=5.0
        )
        
        c4.write(" ")
        c4.write(" ")
        if c4.button("❌", key=f"del_{idx}"):
            remove_item(idx)
            st.rerun()

    st.button("➕ Добавить строку", on_click=add_item)

    total_val = sum(float(i["qty"]) * float(i["price"]) for i in st.session_state.item_list)
    alv_rate = 0.255
    veroton_val = total_val / (1 + alv_rate)
    alv_val = total_val - veroton_val

    st.markdown("---")
    st.markdown(f"### **Итого к оплате: {total_val:.2f} €**")
    st.caption(f"В том числе ALV (25.5%): {alv_val:.2f} € | Без налога: {veroton_val:.2f} €")

    if st.button("💾 Сохранить и сформировать PDF", type="primary"):
        if client_name.strip():
            db["clients"][client_name] = {"ytunnus": client_ytunnus}

            new_record = {
                "Дата": str(doc_date),
                "Тип": doc_type,
                "Номер Документа": doc_num,
                "Клиент": client_name,
                "Сумма (€)": round(total_val, 2),
                "ALV (€)": round(alv_val, 2),
                "Часы": hours_spent
            }
            db["records"].append(new_record)
            save_data(db)

            pdf_bytes = generate_pdf(
                doc_type=doc_type,
                doc_num=doc_num,
                client_name=client_name,
                client_ytunnus=client_ytunnus,
                items=st.session_state.item_list,
                date_str=str(doc_date)
            )

            st.success("Данные успешно сохранены в базе!")
            st.download_button(
                label="⬇️ Скачать PDF документ",
                data=pdf_bytes,
                file_name=f"{doc_type}_{doc_num}.pdf",
                mime="application/pdf"
            )
        else:
            st.error("Ошибка: Укажите имя или компанию клиента перед сохранением!")

elif menu == "База клиентов":
    st.header("👥 База сохраненных клиентов")
    if db["clients"]:
        clients_df = pd.DataFrame([
            {"Клиент / Компания": name, "Y-tunnus": info.get("ytunnus", "")}
            for name, info in db["clients"].items()
        ])
        st.dataframe(clients_df, use_container_width=True)
    else:
        st.info("База клиентов пока пуста.")

elif menu == "Таблица учета":
    st.header("📊 Финансовая история")
    if db["records"]:
        df = pd.DataFrame(db["records"])
        st.dataframe(df, use_container_width=True)

        c1, c2, c3 = st.columns(3)
        c1.metric("Общий доход (€)", f"{df['Сумма (€)'].sum():.2f}")
        c2.metric("ALV к уплате (€)", f"{df['ALV (€)'].sum():.2f}")
        c3.metric("Часов отработано", f"{df['Часы'].sum():.1f} h")
    else:
        st.info("Записей пока нет.")

elif menu == "Календарь":
    st.header("📅 Календарь")
    selected_date = str(st.date_input("Выберите дату:", date.today()))

    if db["records"]:
        df = pd.DataFrame(db["records"])
        day_records = df[df["Дата"] == selected_date]
        if not day_records.empty:
            st.subheader(f"Записи за {selected_date}")
            st.dataframe(day_records, use_container_width=True)
        else:
            st.info("На эту дату нет сохраненных документов.")
    else:
        st.info("История пуста.")

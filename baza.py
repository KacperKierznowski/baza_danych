import streamlit as st
from supabase import create_client, Client

# Konfiguracja połączenia z Supabase
# Najlepiej przechowywać te dane w .streamlit/secrets.toml

supabase = init_connection()

st.title("📦 System Zarządzania Produktami")

# --- ZAKŁADKI ---
tab1, tab2, tab3 = st.tabs(["Dodaj Produkt", "Dodaj Kategorię", "Podgląd Bazy"])

# --- DODAWANIE KATEGORII ---
with tab2:
    st.header("Nowa Kategoria")
    with st.form("category_form", clear_on_submit=True):
        kat_nazwa = st.text_input("Nazwa kategorii")
        kat_opis = st.text_area("Opis")
        submit_kat = st.form_submit_button("Zapisz kategorię")

        if submit_kat:
            if kat_nazwa:
                data = {"nazwa": kat_nazwa, "opis": kat_opis}
                response = supabase.table("Kategorie").insert(data).execute()
                st.success(f"Dodano kategorię: {kat_nazwa}")
            else:
                st.error("Nazwa kategorii jest wymagana!")

# --- DODAWANIE PRODUKTU ---
with tab1:
    st.header("Nowy Produkt")
    
    # Pobranie kategorii do listy rozwijanej
    categories_res = supabase.table("Kategorie").select("id, nazwa").execute()
    categories_data = categories_res.data
    
    if not categories_data:
        st.warning("Najpierw dodaj przynajmniej jedną kategorię!")
    else:
        # Tworzymy słownik do mapowania nazwy na ID
        cat_options = {item['nazwa']: item['id'] for item in categories_data}
        
        with st.form("product_form", clear_on_submit=True):
            prod_nazwa = st.text_input("Nazwa produktu")
            prod_liczba = st.number_input("Liczba (sztuki)", min_value=0, step=1)
            prod_cena = st.number_input("Cena", min_value=0.0, format="%.2f")
            prod_kat_nazwa = st.selectbox("Kategoria", options=list(cat_options.keys()))
            
            submit_prod = st.form_submit_button("Dodaj produkt")
            
            if submit_prod:
                if prod_nazwa:
                    product_data = {
                        "nazwa": prod_nazwa,
                        "liczba": prod_liczba,
                        "cena": prod_cena,
                        "kategorie_id": cat_options[prod_kat_nazwa]
                    }
                    supabase.table("Produkty").insert(product_data).execute()
                    st.success(f"Produkt '{prod_nazwa}' został dodany.")
                else:
                    st.error("Nazwa produktu jest wymagana!")

# --- PODGLĄD DANYCH ---
with tab3:
    st.header("Aktualny stan bazy")
    
    st.subheader("Kategorie")
    kat_view = supabase.table("Kategorie").select("*").execute()
    st.table(kat_view.data)
    
    st.subheader("Produkty")
    prod_view = supabase.table("Produkty").select("id, nazwa, liczba, cena, kategorie_id").execute()
    st.table(prod_view.data)

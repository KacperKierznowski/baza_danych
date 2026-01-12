import streamlit as st
from supabase import create_client, Client

# --- KONFIGURACJA POŁĄCZENIA ---
# Wklej tutaj swoje dane z panelu Supabase (Settings -> API)
URL = "https://detydvxlwkuxdqirojtx.supabase.co"
KEY = "sb_publishable_M6BTQ-6fjxkjkeQijkmIrg_FAKVKOZV"

@st.cache_resource
def init_connection():
    """Inicjalizacja połączenia z Supabase."""
    return create_client(URL, KEY)

supabase = init_connection()

# Ustawienia strony
st.set_page_config(page_title="Zarządzanie Produktami", layout="centered")
st.title("📦 System Zarządzania Baza Danych")

# --- ZAKŁADKI ---
tab1, tab2, tab3 = st.tabs(["➕ Dodaj Produkt", "📂 Dodaj Kategorię", "📋 Podgląd Danych"])

# --- ZAKŁADKA: DODAWANIE KATEGORII ---
with tab2:
    st.header("Nowa Kategoria")
    with st.form("category_form", clear_on_submit=True):
        kat_nazwa = st.text_input("Nazwa kategorii")
        kat_opis = st.text_area("Opis")
        submit_kat = st.form_submit_button("Zapisz kategorię")

        if submit_kat:
            if kat_nazwa:
                data = {"nazwa": kat_nazwa, "opis": kat_opis}
                try:
                    supabase.table("kategorie").insert(data).execute()
                    st.success(f"Dodano kategorię: {kat_nazwa}")
                except Exception as e:
                    st.error(f"Błąd zapisu: {e}")
            else:
                st.error("Nazwa kategorii jest wymagana!")

# --- ZAKŁADKA: DODAWANIE PRODUKTU ---
with tab1:
    st.header("Nowy Produkt")
    
    # Pobranie aktualnych kategorii, aby powiązać produkt (klucz obcy kategorie_id)
    categories_res = supabase.table("kategorie").select("id, nazwa").execute()
    categories_data = categories_res.data
    
    if not categories_data:
        st.warning("Najpierw dodaj przynajmniej jedną kategorię w zakładce obok!")
    else:
        # Mapowanie nazwy kategorii na ID dla użytkownika
        cat_options = {item['nazwa']: item['id'] for item in categories_data}
        
        with st.form("product_form", clear_on_submit=True):
            prod_nazwa = st.text_input("Nazwa produktu")
            prod_liczba = st.number_input("Liczba (sztuki)", min_value=0, step=1)
            # Cena odpowiada typowi numeric w bazie
            prod_cena = st.number_input("Cena", min_value=0.0, step=0.01, format="%.2f")
            prod_kat_nazwa = st.selectbox("Wybierz kategorię", options=list(cat_options.keys()))
            
            submit_prod = st.form_submit_button("Dodaj produkt")
            
            if submit_prod:
                if prod_nazwa:
                    product_data = {
                        "nazwa": prod_nazwa,
                        "liczba": prod_liczba,
                        "cena": prod_cena,
                        "kategorie_id": cat_options[prod_kat_nazwa]
                    }
                    try:
                        supabase.table("Produkty").insert(product_data).execute()
                        st.success(f"Produkt '{prod_nazwa}' został dodany do bazy.")
                    except Exception as e:
                        st.error(f"Wystąpił błąd: {e}")
                else:
                    st.error("Nazwa produktu jest wymagana!")

# --- ZAKŁADKA: PODGLĄD BAZY ---
with tab3:
    st.header("Aktualny stan magazynowy")
    
    st.subheader("Tabela: Produkty")
    prod_view = supabase.table("Produkty").select("*").execute()
    if prod_view.data:
        st.dataframe(prod_view.data, use_container_width=True)
    else:
        st.info("Brak danych w tabeli Produkty.")

    st.subheader("Tabela: Kategorie")
    kat_view = supabase.table("kategorie").select("*").execute()
    if kat_view.data:
        st.dataframe(kat_view.data, use_container_width=True)
    else:
        st.info("Brak danych w tabeli Kategorie.")

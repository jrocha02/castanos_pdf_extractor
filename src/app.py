import streamlit as st 
import pandas as pd 
import pdfplumber as p 


def extract_raw_pdf_data(pdf_path):
    all_rows = []
    bbox_table = [113, 358, 322, 760]
    
    with p.open(pdf_path) as pdf:
        for page in pdf.pages:
            table_area = page.within_bbox(bbox_table)
            v_lines = [114, 263, 321]
            h_lines = [u for u in range(358, 760, 12)]
            
            table_settings = {
                "vertical_strategy": "explicit",
                "explicit_vertical_lines": v_lines,
                "horizontal_strategy": "explicit", 
                "explicit_horizontal_lines": h_lines,
                "snap_tolerance": 5,
                "join_tolerance": 3
            }
            
            table_page = table_area.extract_table(table_settings)
            
            if table_page:

                filtered_rows = [row for row in table_page if any(cell and cell.strip() for cell in row)]
                all_rows.extend(filtered_rows)

    df = pd.DataFrame(all_rows, columns=["Descripcion", "Cantidad"])
    
    return df

def _making_one_df_simple(df: pd.DataFrame) -> pd.DataFrame:

    even_rows = df.iloc[::2].reset_index(drop=True) 
    odd_rows = df.iloc[1::2].reset_index(drop=True) 
    
    df_new = pd.concat([even_rows, odd_rows], axis=1)
    
    # Rename columns (adjust indexes based on your v_lines)
    df_new.columns = ['Description', 'Cant', 'Barcode_Registry', 'Misc']
    return df_new

def _clean_df(df:pd) -> pd.DataFrame:
    df = df.copy()
    n = len(df)


    for u in range(n):
        strings_cant= df["Cant"].iloc[u].split()
        strings_des = df["Description"].iloc[u].split()

    
        if len(strings_cant) >= 2:
            df["Cant"].loc[u] = strings_cant[-1]
            df["Description"].iloc[u] = df["Description"].iloc[u]+ "".join(strings_cant[:len(strings_cant)-1])
        if len(strings_des) >= 2:
            df["Description"].loc[u] = "".join(strings_des[1:])
    return df 



def main():
    st.title("Página de Extracción de tabla de pdf's Casa Ley")
    title = st.text_input("Escribe el nombre que tendrá el archivo: ")
    pdf = st.file_uploader("Sube tu archivo .pdf ", type="pdf")
    if pdf is not None: 
        df = extract_raw_pdf_data(pdf)
        df = _making_one_df_simple(df)
        df = _clean_df(df)
        
        csv_data = df.to_csv(index=False, encoding='utf-8-sig')
        csv_bytes = csv_data.encode('utf-8-sig')

        st.download_button(label="Descarga el resultado"
                           ,data=csv_bytes,
                            file_name=f"{title}.csv",
                            mime="text/csv")



if __name__ == "__main__":
    main()


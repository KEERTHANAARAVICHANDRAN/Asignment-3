import easyocr
import streamlit as st 
from streamlit_option_menu import option_menu
from PIL import Image
import mysql.connector
import pandas as pd
import numpy as np
import re 
import io


def image_to_text(path):
    
    i=Image.open(path)

    img_arr=np.array(i)

    reader=easyocr.Reader(['en'])
    text=reader.readtext(img_arr,detail=0)
    return text,i



def extracted_text(texts):
    
    text_dict = {"NAME":[],"DESIGNATION":[],"COMPANY":[],"CONTACT":[],"WEBSITE":[],"E-MAIL":[],"ADDRESS":[],"PINCODE":[]}

    text_dict["NAME"].append(texts[0])
    text_dict["DESIGNATION"].append(texts[1])
    

    for j in range (2,len(texts)):
        
        if texts[j].startswith("+") or (texts[j].replace("-"," ").isdigit()and '-'in texts[j]):
            text_dict["CONTACT"].append(texts[j])

        elif   "@" in texts[j] and ".com" in texts[j]:
            text_dict["E-MAIL"].append(texts[j])

        elif "WWW" in texts[j] or "www" in texts[j] or "Www" in texts[j] or "wWw" in texts[j] or "wwW" in texts[j]:
               small =texts[j].lower()
               text_dict["WEBSITE"].append(small)

        elif "Tamil Nadu" in texts[j] or "TamilNadu" in texts[j] or texts[j].isdigit():
               text_dict["PINCODE"].append(texts[j])
               
        elif re.match(r'^[A-Za-z]',texts[j]):
             text_dict["COMPANY"].append(texts[j])

        else:
             colon = re. sub(r'[,;]','',texts[j])                
             text_dict["ADDRESS"].append(colon)  
    for key,value in text_dict.items():
        if len(value)>0:
                c=" ".join(value)
                text_dict[key]=[c]
        else:
             value = "NaN"
             text_dict[key] = [value]         
    
    return text_dict


# streamlit
# SETTING PAGE CONFIGURATIONS

st.set_page_config(page_title= "BizCardX: Extracting Business Card Data with OCR ",
                   layout= "wide",
                   initial_sidebar_state= "expanded")


# CREATING OPTION MENU
with st.sidebar:
    select = option_menu(None, ["Home","Upload & Extract","Modify"])

if select == "Home":
    col1,col2 = st.columns(2)
    with col1:
        st.markdown("## :green[**Technologies Used :**] Python,easy OCR, Streamlit, SQL, Pandas")
        st.markdown("## :green[**Overview :**] In this streamlit web app you can upload an image of a business card and extract relevant information from it using easyOCR. You can view, modify or delete the extracted data in this app. This app would also allow users to save the extracted information into a database along with the uploaded business card image. The database would be able to store multiple entries, each with its own business card image and extracted information.")
    with col2:
        
        pass

elif select == "Upload & Extract":         
    card = st.file_uploader("upload here",label_visibility="collapsed",type=["png","jpeg","jpg"])

    if card is not None:
        st.image(card,width=200)

        text_img,i_img=image_to_text(card)

        extra_dict=extracted_text(text_img) 

        if extra_dict:
             st.success("Extracted successfully") 

        df=pd.DataFrame(extra_dict) 

        # bytes of image:
        img_bytes=io.BytesIO()
        i_img.save(img_bytes,format = "PNG")

        data=img_bytes.getvalue()

        # dictionary:
        image_data ={"IMAGE":[data]}
        df_1 = pd.DataFrame(image_data)

        concat_df=pd.concat([df],axis=1)     
        
        st.dataframe(concat_df)

        button_1= st.button("save")

        if button_1:
            
            
            mydb = mysql.connector.connect(host="localhost",
                                            user="root",
                                            password="Keerthanaa9799",
                                            database= "bizcardx",
                                            port="3306")
            mycursor = mydb.cursor()
        
            query=('''CREATE TABLE IF NOT EXISTS bizcardx_data( Name  varchar(200),
                                                            Designation varchar(200),
                                                            COMPANY varchar(200),
                                                            CONTACT varchar(200) ,
                                                            WEBSITE text,
                                                            EMAIL varchar(200),
                                                            Address  text,
                                                            PINCODE varchar(200))''')
                                                            

            mycursor.execute(query)
            mydb.commit()

            # insert:
            insert_query='''INSERT INTO  bizcardx_data(Name,Designation,COMPANY,CONTACT,WEBSITE,EMAIL,Address,PINCODE) 
                                       VALUES (%s,%s,%s,%s,%s,%s,%s,%s)'''
            
            d1=concat_df.values.tolist()[0]
            
            mycursor.execute(insert_query,d1)
            mydb.commit()

            st.success("inserted successfully")
        method=st.radio("select the method",["preview"])

        if method=="preview":
                
                mydb = mysql.connector.connect(host="localhost",
                                            user="root",
                                            password="Keerthanaa9799",
                                            database= "bizcardx",
                                            port="3306")
                mycursor = mydb.cursor()
            
                query=('''CREATE TABLE IF NOT EXISTS bizcardx_data( Name  varchar(200),
                                                                Designation varchar(200),
                                                                COMPANY varchar(200),
                                                                CONTACT varchar(200) ,
                                                                WEBSITE text,
                                                                EMAIL varchar(200),
                                                                Address  text,
                                                                PINCODE varchar(200))''')

                mycursor.execute(query)
                mydb.commit()


             # select query:
                select_query="SELECT * FROM bizcardx_data"
                mycursor.execute(select_query)
                tab=mycursor.fetchall()
                mydb.commit()

                tab_df=pd.DataFrame(tab,columns=('Name','Designation','COMPANY','CONTACT','WEBSITE','EMAIL','Address','PINCODE'))
                st.dataframe(tab_df)


elif select == "Modify":

    if select =="Modify":
        mydb = mysql.connector.connect(host="localhost",
                                            user="root",
                                            password="Keerthanaa9799",
                                            database= "bizcardx",
                                            port="3306")
        mycursor = mydb.cursor()
    
        query=('''CREATE TABLE IF NOT EXISTS bizcardx_data( Name  varchar(200),
                                                        Designation varchar(200),
                                                        COMPANY varchar(200),
                                                        CONTACT varchar(200) ,
                                                        WEBSITE text,
                                                        EMAIL varchar(200),
                                                        Address  text,
                                                        PINCODE varchar(200))''')

        mycursor.execute(query)
        mydb.commit()


        # select query:
        select_query="SELECT * FROM bizcardx_data"
        mycursor.execute(select_query)
        tab=mycursor.fetchall()
        mydb.commit()

        tab_df=pd.DataFrame(tab,columns=('Name','Designation','COMPANY','CONTACT','WEBSITE','EMAIL','Address','PINCODE'))
        st.dataframe(tab_df)

        col1,col2,col3=st.columns(3)
        with col1:
             
            given_name = st.selectbox("select name",tab_df["Name"])

        df1=tab_df[tab_df["Name"] == given_name ]

        

        df_2=df1.copy()
        

        col1,col2= st.columns(2)
        with col1:
             ch_name=st.text_input("Name",df1["Name"].unique()[0])
             ch_d=st.text_input("Designation",df1["Designation"].unique()[0])
             ch_c=st.text_input("COMPANY",df1["COMPANY"].unique()[0])
             ch_con=st.text_input("CONTACT",df1["CONTACT"].unique()[0])
             
             df_2["Name"] =ch_name
             df_2["Designation"] =ch_d
             df_2["COMPANY"] =ch_c
             df_2["CONTACT"] =ch_con
             
             
        with col2:     
             ch_we=st.text_input("WEBSITE",df1["WEBSITE"].unique()[0])
             ch_em=st.text_input("EMAIL",df1["EMAIL"].unique()[0])
             ch_ad=st.text_input("Address",df1["Address"].unique()[0])
             ch_pi=st.text_input("PINCODE",df1["PINCODE"].unique()[0])

             df_2["WEBSITE"] =ch_we
             df_2["EMAIL"] =ch_em
             df_2["Address"] =ch_ad
             df_2["PINCODE"] =ch_pi
        st.dataframe(df_2)

        col1,col2,col3= st.columns(3)  
        with col1:
           button_2 = st.button("Modify")

        if button_2:
            

            mydb = mysql.connector.connect(host="localhost",
                                user="root",
                                password="Keerthanaa9799",
                                database= "bizcardx",
                                port="3306")
            mycursor = mydb.cursor()

            query=('''CREATE TABLE IF NOT EXISTS bizcardx_data( Name  varchar(200),
                                                        Designation varchar(200),
                                                        COMPANY varchar(200),
                                                        CONTACT varchar(200) ,
                                                        WEBSITE text,
                                                        EMAIL varchar(200),
                                                        Address  text,
                                                        PINCODE varchar(200))''')

            mycursor.execute(query)
            mydb.commit()


            mycursor.execute(f"DELETE  FROM bizcardx_data WHERE Name ='{given_name}'")
            mydb.commit()

            # insert:
            insert_query='''INSERT INTO  bizcardx_data(Name,Designation,COMPANY,CONTACT,WEBSITE,EMAIL,Address,PINCODE) 
                                       VALUES (%s,%s,%s,%s,%s,%s,%s,%s)'''
            
            data1 = df_2.values.tolist()[0]
            
            mycursor.execute(insert_query,data1)
            mydb.commit()

            st.success("entered successfully")

            
            
            with col2:
                select_query="SELECT Name FROM bizcardx_data"
                mycursor.execute(select_query)
                tab=mycursor.fetchall()
                mydb.commit()
                
                names=[]

                for i in tab:
                    names.append(i[0])

                select_names = st.selectbox("select the Name",names)

            
            
            with col3:
                select_query=f"SELECT Designation FROM bizcardx_data WHERE Name ='{select_names}'"
                mycursor.execute(select_query)
                tab1=mycursor.fetchall()
                mydb.commit()
            
                Designation=[]

                for k in tab1:
                 Designation.append(k[0])

                select_des = st.selectbox("select the Designation",Designation)

            
            
            if  select_names and  select_des:
                 
                 col1,col2,col3 = st.columns(3)

                 with col1:
                      st.write(f"selected Name : {select_names}")  
                      st.write("")
                      st.write("")
                      st.write("")
                      st.write(f"selected Designation : {select_des}")

                 with col2:
                      st.write("")
                      st.write("")
                      st.write("")
                      st.write("")
                      remove = st.button("Delete")

                      if remove:
                            mycursor.execute(f"DELETE FROM bizcardx_data WHERE Name ='{select_names}' AND Designation = '{select_des}'")
                            mydb.commit()

                            st.warning ("DELETED")

 
                  
               
                
            



         
            

          



#İŞ PROBLEMİ E-TİCARET SİTESİ MÜŞTERİ SEGMANTASYONU
import datetime as dt
import pandas as pd
pd.set_option("display.max_columns",None)
pd.set_option("display.max_rows",None)
pd.set_option("display.float_format",lambda x:"%.3f"%x)

df_= pd.read_excel("online_retail_II.xlsx",sheet_name="Year 2009-2010")
df = df_.copy()

#----------------------------#
df.head()
df.shape
df.isnull().sum()

df["Description"].nunique()
df["Description"].value_counts().head() #Kaç faturada bu isim geçiyor.
df.groupby("Description").agg({"Quantity":"sum"}).head() #Bu isimli üründen toplam kaç adet sipariş verildi.

df["Invoice"].nunique()
df["TotalPrice"]=df["Quantity"]*df["Price"] #Toplam fiyat sütunu oluşturuyoruz.
df.groupby("Invoice").agg({"TotalPrice":"sum"}).head() #Bir faturadaki ürünlerin toplam fiyatı

#----------------------------#
df.shape
df.dropna(inplace=True) #eksik değerleri droplamak
df.describe().T

df = df[~df["Invoice"].str.contains("C",na=False)] #C barındıranların (iptal olan faturalar) dışındakileri getir

#-----RFM METRİKLERİ BULMA-------#
df.head()
df["InvoiceDate"].max()

today_date=dt.datetime(2010,12,11) #zaman fotmatında güncel gün atadık (yıl,ay,gün formatında)
type(today_date)

rfm=df.groupby("Customer ID").agg({"InvoiceDate": lambda InvoiceDate:(today_date-InvoiceDate.max()).days, #müşterinin son fatura tarihini gün şeklinde aldık ve today_date'den çıkardık -> rec.
                                   "Invoice":lambda Invoice:Invoice.nunique(), # her bir müşterinin faturalarının eşsiz değerini aldık -> freq.
                                   "TotalPrice":lambda TotalPrice:TotalPrice.sum()}) #müşterilere ait faturalardaki toplam fiyat mone.
rfm.head()

rfm.columns=["rec","fre","mon"]
rfm.describe().T
rfm = rfm[rfm["mon"]>0] #0 lira olanları sildik çünkü değerlendirme için önemsiz

rfm.shape

#-----RFM METRİKLERİ HESAPLAMA-------#
rfm["recency_score"]=pd.qcut(rfm["rec"],5,labels=[5,4,3,2,1]) #aralıklara göre kaça böleceğimizi verip o değer kadar böler, çıkan değerleri labellarla eşler, küçük olanı büyük labella atadık
#rec. değeri ters olduğu için labellara dikkat yani iyi olan küçük değerdir

rfm["monetary_score"]=pd.qcut(rfm["mon"],5,labels=[1,2,3,4,5])
#monetary değeri düzdür labellara dikkat yani iyi olan büyük değerdir

rfm["frequency_score"]=pd.qcut(rfm["fre"].rank(method="first"),5,labels=[1,2,3,4,5]) #BU KISMI ANLAMADIM
#frequency değeri düzdür labellara dikkat yani iyi olan büyük değerdir

rfm["rfm_score"]= (rfm["recency_score"].astype(str)+
                   rfm["frequency_score"].astype(str)) #string değerlere çevirip topladık

rfm.describe().T

rfm[rfm["rfm_score"]=="55"].head() #champion müşterileri en değerli kişiler (55'in string değer olduğuna dikkat et)
rfm[rfm["rfm_score"]=="11"].head() #en değersiz kişiler

#-----REGEX-------#
segment_map={
    #   R    F
    r'[1-2][1-2]':'hibernating',
    r'[1-2][3-4]':'at_risk',
    r'[1-2]5':'cant_loose',
    r'3[1-2]':'about_to_sleep',
    r'33':'need_attention',
    r'[3-4][4-5]':'loyal_customers',
    r'41':'promosing',
    r'51':'new_customers',
    r'[4-5][2-3]':'potential_customers',
    r'5[4-5]':'champions'
}

rfm["segment"]=rfm["rfm_score"].replace(segment_map,regex=True) #skorları birleştiren regex.

rfm[["segment","rec","fre","mon"]].groupby("segment").agg(["mean","count"]) #segmentler hakkında betimleme, analiz yaptık.

rfm[rfm["segment"]=="need_attention"].head()
rfm[rfm["segment"]=="at_risk"].index #index bilgileri liste halinde gelir.

new_df=pd.DataFrame()
new_df["customers_id"]=rfm[rfm["segment"]=="new_customers"].index
new_df=new_df["customers_id"].astype(int) # id'leri ondalıklı durumdan kurtardık.
new_df.to_csv("new_customers.csv") #new_df dataframe'ni csv dosyası olarak dışarı çıkardık.

rfm.to_csv("rfm.csv")

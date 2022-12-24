"""İş Problemi
Aşağıda 3 farklı kullanıcının sepet bilgileri verilmiştir. Bu sepet bilgilerine en
uygun ürün önerisini birliktelik kuralı kullanarak yapınız. Ürün önerileri 1 tane
ya da 1'den fazla olabilir. Karar kurallarını 2010-2011 Germany müşterileri
üzerinden türetiniz.
Kullanıcı 1’in sepetinde bulunan ürünün id'si: 21987
Kullanıcı 2’in sepetinde bulunan ürünün id'si : 23235
Kullanıcı 3’in sepetinde bulunan ürünün id'si : 22747
"""

#Veri Seti Hikayesi

"""Online Retail II isimli veri seti İngiltere merkezli bir perakende şirketinin 01/12/2009 - 09/12/2011 tarihleri arasındaki online satış
işlemlerini içeriyor. Şirketin ürün kataloğunda hediyelik eşyalar yer almaktadır ve çoğu müşterisinin toptancı olduğu bilgisi
mevcuttur."""


import pandas as pd
pd.set_option('display.max_columns', None)
# pd.set_option('display.max_rows', None)
pd.set_option('display.width', 500)
# çıktının tek bir satırda olmasını sağlar.
pd.set_option('display.expand_frame_repr', False)
pd.set_option('display.max_columns', 500)
###################################
#Görev 1: Veriyi Hazırlama
##################################

#Adım 1: Online Retail II veri setinden 2010-2011 sheet’ini okutuyoruz.

df_ = pd.read_excel('C:/Users/Enes Fevzi/Desktop/recommender_systems-221002-142621/BONUS PROJECT/online_retail_II-220908-163413/online_retail_II.xlsx',sheet_name="Year 2010-2011")
df = df_.copy()
df.head()
df.shape

#Adım 2: StockCode’u POST olan gözlem birimlerini drop ediniz. (POST her faturaya eklenen bedel, ürünü ifade etmemektedir.)
#Adım 3: Boş değer içeren gözlem birimlerini drop ediniz.
#Adım 4: Invoice içerisinde C bulunan değerleri veri setinden çıkarınız. (C faturanın iptalini ifade etmektedir.)
#Adım 5: Price değeri sıfırdan küçük olan gözlem birimlerini filtreleyiniz.


def retail_data_prep(df):
    df.dropna(inplace=True)
    df = df[~df["Invoice"].str.contains("C", na=False)]
    df = df[df["Quantity"] > 0]
    df = df[df["Price"] > 0]
    replace_with_thresholds(df, "Quantity")
    replace_with_thresholds(df, "Price")
    return df

#Adım 6: Price ve Quantity değişkenlerinin aykırı değerlerini inceleyip, gerekirse baskılayalım.
def outlier_thresholds(dataframe, variable):
    quartile1 = dataframe[variable].quantile(0.01)
    quartile3 = dataframe[variable].quantile(0.99)
    interquantile_range = quartile3 - quartile1
    up_limit = quartile3 + 1.5 * interquantile_range
    low_limit = quartile1 - 1.5 * interquantile_range
    return low_limit, up_limit

def replace_with_thresholds(dataframe, variable):
    low_limit, up_limit = outlier_thresholds(dataframe, variable)
    dataframe.loc[(dataframe[variable] < low_limit), variable] = low_limit
    dataframe.loc[(dataframe[variable] > up_limit), variable] = up_limit





#################################################################
#Görev 2: Alman Müşteriler Üzerinden Birliktelik Kuralları Üretme
#################################################################




#Adım 1: Fatura ürün pivot table’i oluşturacak create_invoice_product_df fonksiyonunu tanımlayalım.

create_invoice_product_df = df.groupby(['Description', 'Invoice'])['Quantity'].sum().unstack().fillna(0).applymap(lambda x: 1 if x > 0 else 0)

# Kuralları oluşturacak create_rules fonksiyonunu tanımlayınız ve alman müşteriler için kurallarını bulalım.

df_germany = df[df['Country'] == "Germany"]


def create_invoice_product_df(dataframe, id=True, country="Germany"):
    dataframe = dataframe[dataframe['Country'] == country]
    dataframe = create_invoice_product_df(dataframe, id)
    frequent_itemsets = apriori(dataframe, min_support=0.01, use_colnames=True)
    rules = association_rules(frequent_itemsets, metric="support", min_threshold=0.01)
    return rules


rules = create_invoice_product_df(df_germany)

#Adım 1: check_id fonksiyonunu kullanarak verilen ürünlerin isimlerini buluyoruz.

def check_id(dataframe, stock_code):
    product_name = dataframe[dataframe["StockCode"] == stock_code][["Description"]].values[0].tolist()  #id yazdığımda bu id nin descriptionı gelir
    print(product_name)

check_id(df_germany, 10120)


#arl_recommender fonksiyonunu kullanarak 3 kullanıcı için ürün önerisinde bulunuyoruz.

def arl_recommender(rules_df, product_id, rec_count=1):
    sorted_rules = rules_df.sort_values("lift", ascending=False)
    recommendation_list = []
    for i, product in enumerate(sorted_rules["antecedents"]):
        for j in list(product):
            if j == product_id:
                recommendation_list.append(list(sorted_rules.iloc[i]["consequents"])[0])

    return recommendation_list[0:rec_count]

#Adım 3: Önerilecek ürünlerin isimlerine bakınız.
arl_recommender(rules, 22492, 1)
arl_recommender(rules, 22492, 2)
arl_recommender(rules, 22492, 3)







from tkinter import Tk,Frame,Label,Button,Listbox,END,BooleanVar,Checkbutton,Entry
from tkinter.ttk import Treeview
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from pandas import DataFrame,Series,isna,read_csv
from numpy import zeros
from re import sub
from seaborn import heatmap
from matplotlib.pyplot import subplots
from os.path import dirname, abspath, join

class Chess_tk():

    def __init__(self, df, column_hamle ,title="Chess_"):
        self.df = df# df i tanımlıyoruz
        self.root = Tk()# tk inter ana ekranı oluşturuyoruz                            
        self.root.title(title)#ekranın üstünde yazan etiket
        self.root.resizable(False, False)# Hem yatay hem dikey yeniden boyutlandırmayı kapatır
        self.column_hamle = column_hamle # veri setindeki hamleleri tutan kolon
        self.hamle_temizleme() # veri setinde olan hamleleri temizliyoruz
        self.df_ = DataFrame() # Seçim yaptığımız veri setimizi buraya atacağız (ör sadece beyaz oyuncuların maçı)
        self.selected_filters = {}  # kolon bazlı seçilen filtreleri tutacak sözlük yapısı
   
    def hamle_temizleme(self):# veri setimizdeki hamlelerin olduğu kolonu seçip temizleteceğiz
        hamleler = self.df[self.column_hamle].str.split()#Hamleleri bölüyoruz hamleler pd.Series oalrka dönecek
        hamleler_df = hamleler.apply(Series)# Hamlelerin herbir satırında liste var (0 : [a4,f4,e3]) bunların
        # Her birini dataframe yapıyoruz 0. indisler ilk hamleler haliyle beyazların hamleleri hamle sırasına göre kolon oluşturuyoruz bu sayede

        for c in hamleler_df:#hamleler_df deki kolonları c değerine atıyoruz
            temp = hamleler_df[c]#c kolonlarını temp e atıyoruz
            for i,v in temp.items():# temp bir pandas serisi .items ile indeks ve value değerlerini tuple dönüştürüyor i : indeks / v : value
                if not isna(v):# Eğer value null değil ise gir
                    v = sub(r"[RBNQ+#=xKO-]","",v)# sub: value de [RBNQ+#=xKO-] bu değerler var ise "" buna çevir
                    hamleler_df.iat[i,c] = v[-2:]# hamlelerin i. indeksi ve c. kolonuna valueninsondan 2 sini alıp hamleler_df ye at 
                    # programın yavaş başlamasının sebebi burada blok şeklinde kolon*sütun kere hamleler_df ye erişiyoruz 2 tane de for döngüsü var çok fazla işlem var
        self.hamleler_df = hamleler_df

    #Filtreleme işlemleri //////(Düzenlene bilir eksikler var)
    def filtrele(self):# Burada seçim yaptığımız veri setini kuracağız (ör : sadece kazananların verisini al)
        df_filtered = self.df.copy()# df'yi df_filtered'e kopyalıyoruz
        for col, values in self.selected_filters.items():# selected_filters deki col: sözlüğün keyleri / values: sözlüğün valueları
            if values:# Eğer values boş değil ise.
                df_filtered = df_filtered[df_filtered[col].isin(values)] # df_filtered'e selected_filters deki değerlerin keyleri yani kolonların içinde values ler var mı
                #(ör: selected_filters={"Zafer_Durumu" : ["resign"]}    df nin Zafer_Durumu kolonunda resign leri al )

        self.df_ = df_filtered
        self.hamleler_df_ = self.hamleler_df.loc[self.df_.index]# Burada hamlelerin olduğu veride ve filtrelenen df_ de ki indeksler aynı seçtiğimiz df deki hamleleri alıyoruz
        
        self.hamleler_df_column_count = self.hamleler_df_.shape[1]# Bu hamlelerin yoğunluğu örnek "Zafer_Durumu" : ["resign"] kaçtane resigh olan veri var
        print("filtrele",len(self.df_))

    def hamle_tahta(self,stop = -1):
            # stop işlemi verideki hamlelere eişmek için ilk 3 hamle gibi
            
            # hamle sıramızı giricez 0. kolon beyaz taşın başlangıç hamlesi
            self.hamleler_df_secim = self.hamleler_df_.iloc[:,stop-1:stop]
            #stop-1 i silersek toplam hamle dağılımını verir
            #silmezsek sıralı hamle dağılımını verir

            # tahta oluşturuyoruz
            tahta = zeros((8,8),dtype=int)   

            # beyaz ve siyah diye 2 tahta oluştrup kordinatlarını ayarlıyoruz
            tahta_beyaz = DataFrame(         
                tahta,columns=["a","b","c","d","e","f","g","h"],
                index=[8,7,6,5,4,3,2,1])
            tahta_siyah = tahta_beyaz.copy()

            for c in self.hamleler_df_secim:# Hamleler in sütunlarına giriyoruz (Sütunlar hamle sırası 0.sütun 1.hamle) 
                temp = self.hamleler_df_secim[c].value_counts()# sütunlardaki değerlerin toplamını temp e atıyoruz (temp kullanmamın sebebi hızı arttırma ama hafıza kullanımı artıyor)
                for i in temp.index:# sütunların index değerlerini i ye atıyoruz (ör d5)
                    if (i != "") and (len(i) == 2) and (i[0] in ["a","b","c","d","e","f","g","h"]) and (i[1] in ["1","2","3","4","5","6","7","8"]):# i[0]=a,b,c,d,e,f,g,h/i[1]=1,2,3,4,5,6,7,8/i= "a1"....                            
                        x,y = i# index değerlerini x ve y diye ayırıyoruz (x : f , y: 3 gibi)
                        if (c % 2 == 0):# çift beyaz taşlar
                            tahta_beyaz[x][int(y)] += temp[i]# tahtanın kordinatlarına temp in i. indisindeki değeri atıyoruz #(toplam yapılan hamle sayısı e4 kaç defa yapılmış gibi sonra ısı haritasında kullanılacak)
                        if (c % 2 == 1):# tek siyah taşlar
                            tahta_siyah[x][int(y)] += temp[i]# aynı işlem  
            self.tahta_beyaz = tahta_beyaz
            self.tahta_siyah = tahta_siyah
            print("hamle_tahta")

    def heatmap(self,frame):# ısı haritasını yükleme bölümü. Frame ile nerede konumlanacağını belirtiyoruz
        
        # Önce varsa eski canvas'ı temizleme
        if hasattr(self, "canvas"):
            self.canvas.get_tk_widget().destroy()

        # Yeni figür oluşturma
        fig, axes = subplots(1, 2,figsize = (9,3))

        ax1, ax2= axes # siyah ve beyaz tahta 

        # Her bir heatmap
        # data seti self.tahta_beyaz , ax = ax1 e entegre et, linewidths=0.5 çizgilerin kalınlığı
        #square=True heatmap kare olsun
        heatmap(self.tahta_beyaz, ax=ax1, cmap="Reds", linewidths=0.5, square=True, annot=True, fmt="d", cbar=False, annot_kws={"size": 6})
        ax1.set_title("Beyaz Oyuncu Tahta")

        heatmap(self.tahta_siyah, ax=ax2, cmap="Reds", linewidths=0.5, square=True, annot=True, fmt="d", cbar=False, annot_kws={"size": 6})
        ax2.set_title("Siyah Oyuncu Tahta")

        # Matplotlib figürünü Tkinter arayüzüne gömme
        self.canvas = FigureCanvasTkAgg(fig, master=frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side="left", fill="y", expand=True)
        print("heatmap")

    # Df i güncelleme
    def df_yukle(self):
        c = 0 # c bizim hamle sayımızı tutacak değişken

        # haetmapin duracağı frame
        frame = Frame(self.root, bg="#FFFFFF", highlightthickness=5)
        frame.pack(side="top",fill="x")

        #hamlenin yükleneceği ileri geri gideceği ve filtreleme işleminin yapılacağı butonların duracağı frame
        frame_ = Frame(frame, bg="#FFFFFF", highlightthickness=5)
        frame_.pack(side="bottom")

        # nonlocal c dışarıdaki c ye erişmeyi sağlıyor
        # heatmapin yükleneceği fonksiyon
        def heatmap_yukle():
            self.filtrele()
            self.hamle_tahta()
            self.heatmap(frame)
            nonlocal c
            c = self.hamleler_df_column_count 
            label.config(text=str(c))
            
        # ilk hamlemiz
        # Buradan sonraya yorum sayırı ekleeeeeee!!!!!!!!!!!
        def ilk_hamle():
            nonlocal c
            c = 1
            label.config(text=str(c))
            self.hamle_tahta(stop=c)
            self.heatmap(frame)

        def ileri():
            nonlocal c
            if c < self.hamleler_df_column_count:
                c += 1
                label.config(text=str(c))
                self.hamle_tahta(stop=c)
                self.heatmap(frame)

        def geri():
            nonlocal c
            if c > 0:
                c -= 1
                label.config(text=str(c))
                self.hamle_tahta(stop=c)
                self.heatmap(frame)

        label = Label(frame)
        label.pack(side="top", padx=5)     

        buton_ileri = Button(frame_, text="ileri", command=ileri)
        buton_ileri.pack(side="right", padx=5)  

        buton_geri = Button(frame_, text="geri", command=geri)
        buton_geri.pack(side="left", padx=5)   

        buton_heatmap_yukle = Button(frame_, text="Filtrele ve Uygula", command=heatmap_yukle)
        buton_heatmap_yukle.pack(side="top", padx=5)            

        buton_ilk_hamle = Button(frame_, text="ilk_hamle", command=ilk_hamle)
        buton_ilk_hamle.pack(side="top", padx=5)   
        heatmap_yukle()
    
    
    def listbox(self, columns_name):

        frame = Frame(self.root, bg="#8D4141", highlightthickness=5)
        frame.pack(side="left",fill="both")     
        column_value_list = self.df.groupby(columns_name).size().sort_values(ascending=False).index
        width = (len(str(column_value_list[0])) + 3) 
        width_ = 10
        pady = 2
        padx = 2

        def ara():
            arama = ara_entry.get().lower()
            filtrelenmiş = [val for val in column_value_list if (isinstance(val, str) and arama in val.lower()) or (isinstance(val, int) and arama in str(val))]
            listbox.delete(0, END)
            for eleman in filtrelenmiş:
                listbox.insert(END, eleman)

        def ara_tümünü_seç():
            if all_select_var.get():
                listbox.select_set(0, END)
            else:
                listbox.select_clear(0, END)
            df_ekle()
        
        def df_ekle():
            selection = listbox.curselection()
            values = [listbox.get(i) for i in selection]
            self.selected_filters[columns_name] = values
        

        label = Label(frame, text=columns_name, bg="#8D4141", fg="white",width=width_)
        label.pack(side="top", pady=pady)

        all_select_var = BooleanVar()
        cb = Checkbutton(frame, text="Tümünü Seç", variable=all_select_var, command=ara_tümünü_seç,width=width_)
        cb.pack(side="top", pady=pady)

        listbox = Listbox(frame, selectmode="extended",width=width)
        for v in column_value_list:
            listbox.insert(END, v)
        listbox.pack(side="top", expand=True,fill="y")

        ara_entry = Entry(frame,width=width_)
        ara_entry.pack(side="top", pady=pady,padx=padx)

        btn_frame = Frame(frame)
        btn_frame.pack(side="bottom", fill="x")

        ara_buton = Button(frame, text="Ara!", command=ara,width=width_)
        ara_buton.pack(side="top", pady=pady, padx=padx, ipadx=10)

        ekle = Button(frame, text="Ekle", command=df_ekle,width=width_)
        ekle.pack(side="top", pady=pady, padx=padx, ipadx=10)
          
    
    def treeview(self, columns_name):
        frame = Frame(self.root, bg="#8D4141", highlightthickness=5)
        frame.pack(side="left",fill="both")        
        column_value_list = self.df.groupby(columns_name).size().sort_values(ascending=False)
        iwidth = (len(str(column_value_list.index[0])) * 6) + 30
        vwidth = (len(str(column_value_list.values[0])) * 6) + 10
        width_ = 10
        pady = 2
        padx = 2
        def ara():
            arama = ara_entry.get().lower()
            
                
            for v in tree.get_children():
                tree.delete(v)

            for v,s in column_value_list.items():
                if arama in str(v).lower():
                    tree.insert("", "end", values=(v, s))

        def ara_tümünü_seç():
            if all_select_var.get():
                tree.selection_set(tree.get_children())
            else:
                tree.selection_clear()

            df_ekle()
            

        def df_ekle():
            selection = tree.selection()
            values = [tree.item(v,"values")[0] for v in tree.selection()]
            self.selected_filters[columns_name] = values     

        label = Label(frame, text=columns_name, bg="#8D4141", fg="white",width=width_)
        label.pack(side="top", pady=pady)      

        all_select_var = BooleanVar()

        cb = Checkbutton(frame, text="Tümünü Seç", variable=all_select_var, command=ara_tümünü_seç,width=width_)
        cb.pack(side="top", pady=pady)

        # Treeview'i ve özellikleri yüklüyoruz
        tree = Treeview(frame, columns=("Değer","size"), show="headings")
        tree.heading("Değer", text="Değer")
        tree.heading("size", text="size")
        tree.column("Değer", width=iwidth)
        tree.column("size", width=vwidth)

        # Değerlerimizi ekliyoruz
        for i,v in column_value_list.items():
            tree.insert("", "end", values=(i, v))
        tree.pack(side="top", expand=True,fill="y")

        ara_entry = Entry(frame,width=width_)
        ara_entry.pack(side="top",pady=pady, padx=padx)

        btn_frame = Frame(frame)
        btn_frame.pack(side="bottom", fill="x")

        ara_buton = Button(frame, text="Ara!", command=ara,width=width_)
        ara_buton.pack(side="top", pady=pady, padx=padx, ipadx=10)

        ekle = Button(frame, text="Ekle", command=df_ekle,width=width_)
        ekle.pack(side="top", pady=pady, padx=padx, ipadx=10)

BASE_DIR = dirname(abspath(__file__))
path = join(BASE_DIR, "games.csv")

df = read_csv(path)

df = df.rename(columns={
    'id': 'Oyun_ID',
    'rated': 'Dereceli_Oyun',
    'created_at': 'Oluşturulma_Tarihi',
    'last_move_at': 'Son_Hamle_Tarihi',
    'turns': 'Hamle_Sayısı',
    'victory_status': 'Zafer_Durumu',
    'winner': 'Kazanan',
    'increment_code': 'Süre_Kodu',
    'white_id': 'Beyaz_Oyuncu_ID',
    'white_rating': 'Beyaz_Puanı',
    'black_id': 'Siyah_Oyuncu_ID',
    'black_rating': 'Siyah_Puanı',
    'moves': 'Hamleler',
    'opening_eco': 'Açılış_Kodu',
    'opening_name': 'Açılış_Adı',
    'opening_ply': 'Açılış_Hamlesi_Sayısı'
})

chess = Chess_tk(column_hamle="Hamleler" ,df=df)
chess.df_yukle()
chess.listbox("Dereceli_Oyun")
chess.listbox("Hamle_Sayısı")
chess.treeview("Zafer_Durumu")
chess.treeview("Kazanan")
chess.treeview("Süre_Kodu")
chess.treeview("Beyaz_Oyuncu_ID")
chess.listbox("Beyaz_Puanı")
chess.treeview("Siyah_Oyuncu_ID")
chess.listbox("Siyah_Puanı")
chess.treeview("Açılış_Kodu")
chess.treeview("Açılış_Adı")
chess.listbox("Açılış_Hamlesi_Sayısı")
chess.root.mainloop()

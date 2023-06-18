from random import randint

from kivy.app import App
from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.properties import ListProperty, ObjectProperty, StringProperty, BooleanProperty, NumericProperty
from kivy.uix.screenmanager import ScreenManager, Screen, FallOutTransition
import os
import json
from kivy.storage.jsonstore import JsonStore
from kivy.core.window import Window
from kivy.utils import platform
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.datatables import MDDataTable
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.uix.widget import Widget

screen_manager = ScreenManager()
kv = '''
<LoginScreen>:
    name: "Login"
    id:"screen1"
    MDCard:
        size_hint: None, None
        size: 300,340
        pos_hint: {"center_x": 0.5, "center_y": 0.5}
        elevation: 7
        padding: 15
        spacing: 25
        orientation: "vertical"

        MDLabel:
            id: giris_yazisi
            text: "Portfolium'a Hoşgeldiniz"
            font_size: 30
            halign: "center"
            size_hint_y: None
            height: self.texture_size[1]
            padding_y: 15

        MDTextField:
            id: kullanici
            hint_text: "Email"
            #icon_right:""
            size_hint_x: None
            width: 200
            font_size: 15
            pos_hint: {"center_x": 0.5}

        MDTextField:
            id: sifre
            hint_text: "Sifre"
            #icon_right:""
            size_hint_x: None
            width: 200
            font_size: 15
            pos_hint: {"center_x": 0.5}
            password: True
            multiline: False

        MDTextField:
            id: sifreiki
            hint_text: "Şifre Kontrol"
            #icon_right:""
            size_hint_x: None
            width: 200
            font_size: 15
            pos_hint: {"center_x": 0.5}
            password: True
            multiline: False

        MDFillRoundFlatButton:
            text: "Kayıt Ol"  #kullanıcı kayıtlı is bu butonun tekstini degiştirip login yaz
            font_size: 15
            pos_hint: {"center_x": 0.5}
            text_color: "white"
            md_bg_color: "#990000"
            on_press: app.userRegister()
            #on_release: app.root.current = "Main"

<MainScreen>
    name: "Main"

    MDBoxLayout:
        orientation: "vertical"

        MDTopAppBar:
            md_bg_color: 153, 0, 0, .3
            title:"Portfolium"
            right_action_items:
            MDLabel:
                text: str(app.userInfo())
                halign: "right"
        Button:
            size_hint: None, None
            size: 60,25
            pos_hint: {"x": .93, "y": 0}
            text: "Çıkış"
            background_color: "#FFFFFF"
            text_color: "red"
            # on_release: app.root.current = "Login"
            on_release: root.screen_manager.current ="login_screen"
            #login ekranına password reset de eklemek lazım
            # on_release: app.close()
            
            #root.manager.transition.direction = "left"
        MDBottomNavigation:
            panel_color: 153, 0, 0, .3
            #renk ıvır zıvır
            text_color_active: 40, 40, 40, 1

            MDBottomNavigationItem:
                id: portfoyum
                name: "Portföy"
                text: "Portföyüm"
                icon: "pix\star.png"

                MDLabel:
                    text: "Kişinin portföyü burda olcak"
                    halign: "center"

            MDBottomNavigationItem:
                id: bist100
                name: "BIST"
                text: "BIST 100"
                icon: "pix\statistics.png"
                on_tab_press: app.data_inkb100()

            MDBottomNavigationItem:
                name: "Coin Ekranı"
                text: "Diğer Menkul Kıymetler"
                icon: "pix\gold.png"

                MDLabel:
                    text: ""
                    halign: "center"                   
'''

class LoginScreen(Screen):
    screen_manager = ObjectProperty(screen_manager)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_enter(self):
        try:
            app = App.get_running_app()
            path = app.initilize_global_store_path()
            self.store_id = JsonStore(os.path.join(path, 'userdata.json'))
            if self.store_id.exists('userinfo'):
                if ('username' in self.store_id['userinfo']) and ('password' in self.store_id['userinfo']):
                    screen_manager.get_screen("login_screen").ids.kullanici.text = str(self.store_id['userinfo']['username'])
                    screen_manager.get_screen("login_screen").ids.sifre.text = str(self.store_id['userinfo']['password'])
            else:
                pass
        except Exception as e:
            print("LoginScreen on_enter hata aldı sebebi : ", e)
            pass
class CukurClockAnimasyon(Widget):
    a = NumericProperty(0)  # seconds


    def start(self):
        # app = App.get_running_app()
        # app.cukur_bes_saniye = False
        Animation.cancel_all(self)  # stop any current animations
        # self.anim = Animation(a=0, duration=self.a)
        self.anim = Animation(a=0, duration=3)

        def finish_callback(animation, *args):
            app = App.get_running_app()
            if app.cukur_clock_animasyon_takip == True:
                app.cukur_bes_saniye = True
            else:
                self.start()
        self.anim.bind(on_complete=finish_callback)
        self.anim.start(self)
class MainScreen(Screen):
    screen_manager = ObjectProperty(screen_manager)
    pass

class PortfolioApp(MDApp):
    screen_manager = ObjectProperty(screen_manager)
    user_ids = ObjectProperty()
    pass_ids = ObjectProperty()
    row_data = ListProperty()
    row_data2 = ListProperty()
    column_data = ListProperty()
    # portfoy_icin_secimler = []

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        path = self.initilize_global_store_path()
        self.store_id = JsonStore(os.path.join(path, 'userdata.json'))
        # self.data_updata = Clock.schedule_interval (self.updata_imkb100, 1)
        # Clock.create_trigger(self.data_updata, 0.2)
        # Clock.unschedule(self.data_updata)
        self.data_table = None
        self.data_table2 = None
        self.data_updata = Clock.schedule_interval(self.update_data, 1)
       #aşağıdaki portföy datasını güncellemek için
        self.data_updata = Clock.schedule_interval(self.update_data2, 1)
        self.portfoy_icin_secimler = []
        self.secime_uygun_data_duzenlemesi = []

    def update_data(self, *args):
        # you would call this method with the on_pre_enter screen event

        # load you data from the database, replace or extend the row_data list
        # self.row_data = [(str(i), randint(10, 100), 'Updated Data ' + str(randint(75, 150))) for i in range(5)]
        self.hello = self.mydata()
        dandomize_data = randint(0,4)
        # self.row_data = [(int(i), self.hello[i]) for i in range(1,5)]
        # self.hello = self.mydata()
        # self.row_data = [(self.hello[i]) for i in range(5)]
        self.row_data = self.hello[dandomize_data]
        self.data_table.update_row_data(self.data_table, self.row_data)

    def update_data2(self,*args):
        #bu fonksiyonda da secim_datasi fonksiyonunda düzenledigim arraydaki datayı
        # potföy içinde ki hisselerden rasgele  seçilen data ile güncelliyorum
        if len(self.secime_uygun_data_duzenlemesi) == 0:
            dandomize_data = 0
        else:
            dandomize_data = randint(0, len(self.secime_uygun_data_duzenlemesi[0]))
            self.row_data2=self.secime_uygun_data_duzenlemesi[dandomize_data]
            self.data_table2.update_row_data(self.data_table2, self.row_data2)

    def secim_datasi(self, *args):
        #burada tüm datayı çekip seçilen hisse senetleri dışındakileri datadan silerek
        # secime_uygun_data_duzenlemesi arrayında datayı oluşturuyorum
        self.secime_uygun_data_duzenlemesi = self.mydata() # initde çağrıldı
        # for i in self.secime_uygun_data_duzenlemesi:
        for datasayisi in range(0,4): # toplam tata kayıt sayımız 5 tane olduğu için o dan 4 e kadar
            for i in self.secime_uygun_data_duzenlemesi:
                print("bu i",i)
                for j in i:
                    print("bu j", j)
                    if j[0] not in  self.portfoy_icin_secimler:
                        # sil = self.secime_uygun_data_duzenlemesi.index(i)
                        i.remove(j) # bu tek bir data data içindeki seçim dışında kalanları siliyor

                        print("güncell self.secime_uygun_data_duzenlemesi",self.secime_uygun_data_duzenlemesi)

        print("son  self.secime_uygun_data_duzenlemesi", self.secime_uygun_data_duzenlemesi)



    def portfoy_data(self, instance_row,*args):
        #byrada seçtigi hisse senetlerini  portfoy_icin_secimler arrayına atıyorum ve  secim_datasi fonksiyonunu çağırıyorum
        if instance_row[0] not in self.portfoy_icin_secimler:
            self.portfoy_icin_secimler.append(instance_row[0])
        print("self.portfoy_icin_secimler",self.portfoy_icin_secimler)
        self.secim_datasi()
    def portfoy_data_sil(self, instance_row,*args):
        if instance_row[0] in self.portfoy_icin_secimler:
            self.portfoy_icin_secimler.remove(instance_row[0])
        # print("self.portfoy_icin_secimler",self.portfoy_icin_secimler)
        self.secim_datasi()

    def updata_imkb100(self, *args):
        hello = self.mydata()
        for i in range(1, 5):
            return hello[i]

    def initilize_global_store_path(self):
        return str(self.user_data_dir)

    def on_start(self):
        self.my_portfoy()
        self.data_inkb100()
        if self.store_id.exists('userinfo'):
            self.root.current = 'main_screen'
        else:
            self.root.current = 'login_screen'
    def userInfo(self, *args):
        if self.store_id.exists('userinfo'):
            return str(self.store_id['userinfo']['username'])
        else:
            return 'Welcome'

    def close(self, *args):
        if platform == "android":
            App.get_running_app().stop()
            Window.close()
            exit()
        elif platform == "ios":
            App.get_running_app().stop()
            # removing window
            Window.close()
            exit()
        else:
            App.get_running_app().stop()
            # removing window
            Window.close()
            exit()

    def build(self):
        self.initilize_global_store_path()
        Builder.load_string(kv)
        self.title = 'Portfolium'
        self.theme_cls.theme_style = 'Dark'
        # return Builder.load_file('birlesim.kv')

        self.screen_manager = screen_manager

        login_scrn = LoginScreen(name="login_screen")
        main_scrn = MainScreen(name="main_screen")

        self.screen_manager.add_widget(login_scrn)
        self.screen_manager.add_widget(main_scrn)

        return self.screen_manager

    def userRegister(self, *args):
        try:
            user  = screen_manager.get_screen("login_screen").ids.kullanici.text
            paswd = screen_manager.get_screen("login_screen").ids.sifre.text
            paswd2 = screen_manager.get_screen("login_screen").ids.sifreiki.text

            # user = self.root.children[0].ids.kullanici.text
            # paswd = self.root.children[0].ids.sifre.text

            if (not self.store_id.exists('userinfo')):
                if user != '' and paswd != '' and paswd == paswd2:
                    data_set = {"username": user, "password": paswd}
                    self.store_id['userinfo']=data_set
                    self.root.current = 'main_screen'
                elif user == '' :
                    # self.root.children[0].ids.kullanici.hint_text = 'isim neydi?'
                    screen_manager.get_screen("login_screen").ids.kullanici.hint_text = 'Bir kullanıcı adı belirleyiniz.'
                elif paswd == '' or paswd2 == '' or (paswd != paswd2):
                    # self.root.children[0].ids.sifre.hint_text = 'Bide şifremiz olsun!'
                    screen_manager.get_screen("login_screen").ids.sifre.hint_text = 'Şifreler aynı degil'
                    screen_manager.get_screen("login_screen").ids.sifreiki.hint_text = 'Şifreler aynı degil'

                else:
                    self.userRegister()

            else:
                print("Elseteyiz")

                self.root.current = 'main_screen'
        except Exception as e:
            print("userRegister hata aldı sebebi : ", e)
            pass
    def mydata(self, * args):

        data1=[
                (
                    "TUPRS",
                    "79,31",
                    "3,60 %",
                ),
                (
                    "AKSA",
                    "62,34",
                    "-2,21%",
                ),
                (
                    "EREGL",
                    "41,68",
                    "5,48%",
                ),
                (
                    "ISCTRE",
                    "11,25",
                    "-1,19%",
                ),
                (
                    "GSARAY",
                    "13,11",
                    "7,93% "
                ),
                (
                    "SAHOL",
                    "40,11",
                    "8,93% "
                )
            ]
        data2 = [
            (
                "TUPRS",
                "81.27",
                "5,01 %",
            ),
            (
                "AKSA",
                "57.18",
                "-7,75%",
            ),
            (
                "EREGL",
                "45.31",
                "6,17 %",
            ),
            (
                "ISCTRE",
                "7.62",
                "-10,01%",
            ),
            (
                "GSARAY",
                "15.33",
                "10,03% "
            ),
            (
                "SAHOL",
                "48,11",
                "4,93% "
            ),

        ]
        data3 = [
            (
                "TUPRS",
                "83.72",
                "4,10%",
            ),
            (
                "AKSA",
                "59.69",
                "-4,55%",
            ),
            (
                "EREGL",
                "47.68",
                "7,10%",
            ),
            (
                "ISCTRE",
                "9.04",
                "-7,74%",
            ),
            (
                "GSARAY",
                "14.03",
                "9,12% "
            ),
            (
                "SAHOL",
                "50,71",
                "10,00% "
            ),
        ]
        data4 = [
            (
                "TUPRS",
                "85.07",
                "4,60%",
            ),
            (
                "AKSA",
                "60,05",
                "-3,42%",
            ),
            (
                "EREGL",
                "48,01",
                "7,28%",
            ),
            (
                "ISCTRE",
                "10,16",
                "-6,21%",
            ),
            (
                "GSARAY",
                "13,87",
                "8,19% "
            ),
            (
                "SAHOL",
                "47,41",
                "9,00% "
            ),
        ]
        data5 = [
            (
                "TUPRS",
                "82,411",
                "5,60%",
            ),
            (
                "AKSA",
                "62,34",
                "-2,21%",
            ),
            (
                "EREGL",
                "61,18",
                "-4,26%",
            ),
            (
                "ISCTRE",
                "11,25",
                "-1,19%",
            ),
            (
                "GSARAY",
                "14,54",
                "-9,47% "
            ),
            (
                "SAHOL",
                "43,60",
                "3,06% "
            ),
        ]
        liste= [data1,data2,data3,data4,data5]
        # for i in range(1,5):
        #     return liste[i]
        return liste


    def sort_on_signal(self, data):
        return zip(*sorted(enumerate(data), key=lambda l: l[1][2]))

    def sort_on_schedule(self, data):
        return zip(
            *sorted(
                enumerate(data),
                key=lambda l: sum(
                    [
                        int(l[1][-2].split(":")[0]) * 60,
                        int(l[1][-2].split(":")[1]),
                    ]
                ),
            )
        )


    def sort_on_team(self, data):
        return zip(*sorted(enumerate(data), key=lambda l: l[1][-1]))


    def on_row_press(self, instance_table, instance_row):
        '''Called when a table row is clicked.'''

        # print("satira tıklandı",instance_table, instance_row,instance_row.text)
        #
        # print(instance_table, instance_row)
        # print(instance_row.children)
        # print(instance_row.children[1].children[0].children)
        # print(f'Signal Name: {instance_row.children[1].children[0].children[0].text}')
        # print(f'Signal Name: {instance_row.children[1].children[0].children[1].text}')
        # print("self.data_tables.row_data[1]", self.data_table.row_data[1])
        # print("self.data_tables.row_data[]", self.data_table.row_data)

        row_num = int(instance_row.index / len(instance_table.column_data))
        row_data = instance_table.row_data[row_num]
        print(row_data)
        # self.update_data2(row_data)
        self.portfoy_data(row_data) # imkb 100 den rova tıklayınca çağrılan on_row_press den portfoy_data fonksiyonunu çağırıyorum
        # self.add_row(row_data)


    def update_row(self, instance_button: MDRaisedButton) -> None:
        self.data_tables.update_row(
            self.data_tables.row_data[1],  # old row data
            ["2", "A", "B", "C"],  # new row data
        )
    def on_row_press2(self, instance_table, instance_row):
        '''Called when a table row is clicked.'''

        print("satira tıklandı on_row_press2",instance_table, instance_row)
        # self.add_row()

        row_num = int(instance_row.index / len(instance_table.column_data))
        row_data = instance_table.row_data[row_num]
        print(row_data)
        # self.update_data2(row_data)
        self.portfoy_data_sil(row_data)


    def on_check_press(self, instance_table, current_row):
        '''Called when the check box in the table row is checked.'''

        print(instance_table, current_row)
        pass
    def on_check_press2(self, instance_table, current_row):
        '''Called when the check box in the table row is checked.'''

        print("burda loo on_check_press2",instance_table, current_row)
        pass


    def add_row(self, instance_row) -> None:

        last_num_row = int(self.data_table2.row_data[-1][0])
        # self.data_table2.add_row((str(last_num_row + 1), "1", "2", "3"))
        # self.data_table2.add_row((str(last_num_row + 1), "1", "2"))
        # datam = json.dumps(instance_row)
        # print("datam",type(instance_row),datam[0],datam[1],datam[2])
        print("datam",type(instance_row),instance_row[0],instance_row[1])
        self.data_table2.add_row((str(last_num_row + 1),str(instance_row[0]),str(instance_row[1]),str(instance_row[2])))
        # self.data_table2.add_row(str(instance_row[0]),instance_row)

    def remove_row(self) -> None:
        if len(self.data_table2.row_data) > 1:
            self.data_table2.remove_row(self.data_table2.row_data[-1])

    def data_inkb100(self, *args):

        self.column_data = [("Hisse Senedi", dp(40)), ("Fiyat", dp(30)), ("Yuzdesi(Artis/Azalis) ", dp(40))]
        # self.data_table = MDDataTable(use_pagination=True, column_data=self.column_data, row_data=self.row_data, check = True, pos_hint = {'center_x': 0.5, 'center_y': 0.5},)
        self.data_table = MDDataTable(use_pagination=True, column_data=self.column_data, row_data=self.row_data, check = False, pos_hint = {'center_x': 0.5, 'center_y': 0.5},)
        self.data_table.bind(on_row_press=self.on_row_press) # row a tıklayınca portföye eklemek için bu fonsiyon kullanılıyor
        self.data_table.bind(on_check_press=self.on_check_press)
        table_area = screen_manager.get_screen("main_screen").ids.bist100.add_widget(self.data_table)
        return
    def my_portfoy(self, *args):
        # self.row_data2 = [(1,'','','')]
        # self.column_data = [("id", dp(10)),("Hisse Senedi", dp(40)), ("Fiyat", dp(30)), ("Yuzdesi(Artis/Azalis) ", dp(40))]

        #burayı data_inkb100 deki data yapısı ile aynı hale getirdim
        self.column_data = [("Hisse Senedi", dp(40)), ("Fiyat", dp(30)), ("Yuzdesi(Artis/Azalis) ", dp(40))]
        # self.data_table2 = MDDataTable(use_pagination=True, column_data=self.column_data, row_data=self.row_data2, check = True, pos_hint = {'center_x': 0.5, 'center_y': 0.5},)
        self.data_table2 = MDDataTable(use_pagination=True, column_data=self.column_data, row_data=self.row_data2, check = False, pos_hint = {'center_x': 0.5, 'center_y': 0.5},)
        self.data_table2.bind(on_row_press=self.on_row_press2) #row a tıklayınca portföy den silmek için bu fonsiyon kullanılıyor
        self.data_table2.bind(on_check_press=self.on_check_press2)
        table_area = screen_manager.get_screen("main_screen").ids.portfoyum.add_widget(self.data_table2)
        return
if __name__=='__main__':
    PortfolioApp().run()
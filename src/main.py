#!/usr/bin/env python3

import gi
gi.require_version("Gtk", "3.0")
gi.require_version('Handy', '1')

import sys
import datetime
import torrent_parser as tp
import humanize
from gi.repository import GObject, GLib, Gtk, Gio , Handy


class Application(Gtk.Application):

    def __init__(self):
        super().__init__(application_id='mlv.knrf.TRiver')
        GLib.set_application_name('TRiver')
        GLib.set_prgname('mlv.knrf.TRiver')
        self.triver_backend = TRiver_Backend()

    def do_activate(self):
        window = Gtk.ApplicationWindow(application=self)
        window.set_icon_name('mlv.knrf.TRiver')
        
        window.set_titlebar(self.mk_title_bar())
        window.add(self.mk_main_ui())
        window.set_default_size(720, 1300)
        window.show_all()

    def mk_title_bar(self):
        title_bar = Handy.TitleBar()
        
        header = Gtk.HeaderBar(
            title='TRiver',
            show_close_button=True)

        self.popover = Gtk.Popover()
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        
        open_btn = Gtk.ModelButton(label="Open")
        open_btn.connect("clicked", self.on_open)

        about_btn = Gtk.ModelButton(label="About")
        about_btn.connect("clicked", self.on_about)


        vbox.pack_start(open_btn, False, True, 5)
        vbox.pack_start(about_btn, False, True, 5)

        vbox.show_all()
        self.popover.add(vbox)
        self.popover.set_position(Gtk.PositionType.BOTTOM)

        btn = Gtk.MenuButton(popover=self.popover)
        icon = Gio.ThemedIcon(name="preferences-system-symbolic")
        image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        btn.add(image)
        header.add(btn)
       
        title_bar.add(header)
        return title_bar

    def mk_main_ui(self):
        scroll_win = Gtk.ScrolledWindow()
        self.text_edit = Gtk.TextView()
        self.text_edit.set_left_margin(20)
        self.text_edit.set_wrap_mode(Gtk.WrapMode(2))
        self.text_edit.set_editable(False)
        self.text_edit.set_cursor_visible(False)
        self.text_buffer = self.text_edit.get_buffer()
        self.text_buffer.set_text("Ready to load torrent file")

        scroll_win.add(self.text_edit)
        return scroll_win

    # event handlers
    def on_open(self, model_button):
        open_dialog = Gtk.FileChooserDialog(title="Open file",  action=Gtk.FileChooserAction.OPEN)
        open_dialog.add_buttons(
            Gtk.STOCK_CANCEL,
            Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN,
            Gtk.ResponseType.OK,)

        open_dialog.resize(200, 200)    
        response = open_dialog.run()
        if response == Gtk.ResponseType.OK:
            try:
                text = self.triver_backend.get_torrent_data(open_dialog.get_filename())
                self.text_buffer.set_text(text)
            except Exception as e:
                print(str(e))
                open_dialog.destroy()
        elif response == Gtk.ResponseType.CANCEL:
            pass
        else:
            pass
        open_dialog.destroy()
    
    def on_about(self, model_button):
        #icon = GdkPixbuf.Pixbuf.new_from_file()
        about = Gtk.AboutDialog()
        about.resize(200,200)
        about.set_version("1.0.0")
        about.set_website("https://github.com/Frankmau5/TRiver")
        about.set_license("GPLv3 Read more here : https://github.com/Frankmau5/TRiver/blob/main/LICENSE")
        about.set_comments("A Torrent file viewer - by knrf")
        about.show_all()


class TRiver_Backend():
    def __init__(self):
        self.data = None

    def get_torrent_data(self, filepath):
        self.data = tp.parse_torrent_file(filepath)
        text = ""

        for key in self.data:
            if key == "creation date":
                try:
                    dt = datetime.date.fromtimestamp(self.data[key])
                    text = text + str(key) + " = " + str(dt) + "\n\n"
                    continue
                except OverflowError as of:
                    print(str(of))
                except OSError as ose:
                    print(str(ose))
            
            if key == "announce-list":
                d = self.data[key]
                text = text + str(key) + " = "
                for da in d:
                    for dat in da:
                        text = text + str(dat) + " , \n" 

                text = text + "\n\n"
                continue
            
            if key == "info":
                for ckey in self.data[key]:
                    if ckey == "files" :
                        text = text + "Files = "
                        for d in self.data[key][ckey]:
                            text = text + "Size" + " : " + str(self.human_readable_size(d["length"]))   + " , "
                            text = text + "Filename" + " : " + str(d["path"])   + " \n"
                    if "Files =" not in text:
                        if ckey == "name":
                            text = text + " File = " + self.data[key]["name"]
                        if ckey == "length":
                            text = text + "Size : " + str(self.human_readable_size(self.data[key]["length"]))
                            
                text = text + "\n\n"
                continue

            if key == "nodes":
                d = self.data[key]
                text = text + str(key) + " = "
                for da in d:
                    text = text + str(da[0]) + ":" + str(da[1])   + " , "
                text = text + "\n\n"
                continue

            text = text + str(key) + " = " + str(self.data[key]) + "\n\n"

        return text

    def human_readable_size(self, byte_size):
        return humanize.naturalsize(byte_size, gnu=True)
    
def main():
    Handy.init()
    app = Application()
    rvalue = app.run(sys.argv)

#main() # debug

#!/usr/bin/env python3

import gi
gi.require_version("Gtk", "3.0")
gi.require_version('Handy', '1')

import sys

from gi.repository import GObject, GLib, Gtk, Gio , Handy


# https://github.com/7sDream/torrent_parser

class Application(Gtk.Application):

    def __init__(self):
        super().__init__(application_id='mlv.knrf.TRiver')
        GLib.set_application_name('TRiver')
        GLib.set_prgname('mlv.knrf.TRiver')

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

        save_btn = Gtk.ModelButton(label="Save")
        save_btn.connect("clicked", self.on_save)

        edit_btn = Gtk.ToggleButton(label="Editable")
        edit_btn.connect("clicked", self.on_edit)


        vbox.pack_start(open_btn, False, True, 5)
        vbox.pack_start(save_btn, False, True, 5)
        vbox.pack_start(edit_btn, False, True, 5)
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
            print("Open clicked")
            print("File selected: " + open_dialog.get_filename())
        elif response == Gtk.ResponseType.CANCEL:
            pass
        else:
            pass
        open_dialog.destroy()

    def on_save(self, model_button):
        save_dialog = Gtk.FileChooserDialog(title="Save File",  action=Gtk.FileChooserAction.SAVE)
        save_dialog.add_buttons(
            Gtk.STOCK_CANCEL,
            Gtk.ResponseType.CANCEL,
            Gtk.STOCK_SAVE,
            Gtk.ResponseType.OK,)

        save_dialog.resize(200, 200)    
        response = save_dialog.run()
        if response == Gtk.ResponseType.OK:
            print("Open clicked")
            print("File selected: " + save_dialog.get_filename())
        elif response == Gtk.ResponseType.CANCEL:
            pass
        else:
            pass
        save_dialog.destroy()

    def on_edit(self, model_button):
        if model_button.get_active():
            self.text_edit.set_editable(True)
            self.text_edit.set_cursor_visible(True)
        else:
            self.text_edit.set_editable(False)
            self.text_edit.set_cursor_visible(False)


class TRiver_Backend():
    def __init__(self):
        pass

def main():
    Handy.init()
    app = Application()
    rvalue = app.run(sys.argv)

main() # debug

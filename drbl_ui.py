#!/usr/bin/python
import os
import string
import re

try:
	import gtk
except:
	print >> sys.stderr, "Can't import python gtk"
	sys.exit(1)

try:
	import vte
except:
	print >> sys.stderr, "Can't import python vte"
	sys.exit(1)

class DRBL_GUI_Template():
	srv_options = "-t n -a n -n n -m n -c n -g n -k 0 -o 1 "

	def __init__(self):
		DRBL_menu = gtk.MenuBar()

		# File Menu
		DRBL_menu_file_quit = gtk.MenuItem("Quit")
		DRBL_menu_file_srv  = gtk.MenuItem("drblsrv")
		DRBL_menu_file_push = gtk.MenuItem("drblpush")

		DRBL_menu_file_quit.connect("activate", gtk.main_quit)
		DRBL_menu_file_srv.connect("activate", self.drblsrv)
		DRBL_menu_file_push.connect("activate", self.drblpush)

		DRBL_menu_file = gtk.Menu()
		DRBL_menu_file.append(gtk.SeparatorMenuItem())
		DRBL_menu_file.append(DRBL_menu_file_srv)
		DRBL_menu_file.append(DRBL_menu_file_push)
		DRBL_menu_file.append(DRBL_menu_file_quit)

		DRBL_menu_root_file = gtk.MenuItem("DRBL")
		DRBL_menu_root_file.set_submenu(DRBL_menu_file)
		DRBL_menu.append(DRBL_menu_root_file)


		# View Menu
		DRBL_menu_view_verbose = gtk.CheckMenuItem("Verbose")
		DRBL_menu_view_verbose.set_active(True)

		DRBL_menu_view = gtk.Menu()
		DRBL_menu_view.append(gtk.SeparatorMenuItem())
		DRBL_menu_view.append(DRBL_menu_view_verbose)
		
		DRBL_menu_root_view = gtk.MenuItem("View")
		DRBL_menu_root_view.set_submenu(DRBL_menu_view)
		DRBL_menu.append(DRBL_menu_root_view)

		# Remote Menu
		DRBL_menu_remote_gra      = gtk.MenuItem("Linux-gra")
		DRBL_menu_remote_txt      = gtk.MenuItem("Linux-txt")
		DRBL_menu_remote_local    = gtk.MenuItem("local")
		DRBL_menu_remote_memtest  = gtk.MenuItem("memtest")
		DRBL_menu_remote_terminal = gtk.MenuItem("Terminal")

		DRBL_menu_remote_gra.connect("activate", self.drbl_remote_gra)
		DRBL_menu_remote_gra.connect("activate", self.drbl_remote_txt)
		DRBL_menu_remote_gra.connect("activate", self.drbl_remote_memtest)
		DRBL_menu_remote_gra.connect("activate", self.drbl_remote_local)
		DRBL_menu_remote_gra.connect("activate", self.drbl_remote_terminal)

		DRBL_menu_remote = gtk.Menu()
		DRBL_menu_remote.append(gtk.SeparatorMenuItem())
		DRBL_menu_remote.append(DRBL_menu_remote_gra)
		DRBL_menu_remote.append(DRBL_menu_remote_txt)
		DRBL_menu_remote.append(DRBL_menu_remote_memtest)
		DRBL_menu_remote.append(DRBL_menu_remote_local)
		DRBL_menu_remote.append(DRBL_menu_remote_terminal)

		DRBL_menu_root_remote = gtk.MenuItem("Remote")
	        DRBL_menu_root_remote.set_submenu(DRBL_menu_remote)
		DRBL_menu.append(DRBL_menu_root_remote)

		# Boot Menu
		DRBL_menu_boot_shutdown           = gtk.MenuItem("Shutdown")
		DRBL_menu_boot_wakeonlan          = gtk.MenuItem("Wake On Lan")
		DRBL_menu_boot_reboot             = gtk.MenuItem("Reboot")
		DRBL_menu_boot_switch_pxe_menu    = gtk.MenuItem("PXE MENU")
		DRBL_menu_boot_switch_pxe_bg_mode = gtk.MenuItem("PXE BG MODE")

		DRBL_menu_boot_shutdown.connect("activate", self.drbl_boot_shutdown)
		DRBL_menu_boot_reboot.connect("activate", self.drbl_boot_reboot)
		DRBL_menu_boot_wakeonlan.connect("activate", self.drbl_boot_wakeonlan)
		DRBL_menu_boot_switch_pxe_menu.connect("activate", self.drbl_boot_switch_pxe_menu)
		DRBL_menu_boot_switch_pxe_bg_mode.connect("activate", self.drbl_boot_switch_pxe_bg_mode)

		DRBL_menu_boot = gtk.Menu()
		DRBL_menu_boot.append(DRBL_menu_boot_shutdown)
		DRBL_menu_boot.append(DRBL_menu_boot_reboot)
		DRBL_menu_boot.append(DRBL_menu_boot_wakeonlan)
		DRBL_menu_boot.append(DRBL_menu_boot_switch_pxe_menu)
		DRBL_menu_boot.append(DRBL_menu_boot_switch_pxe_bg_mode)

		DRBL_menu_root_boot = gtk.MenuItem("Boot")
		DRBL_menu_root_boot.set_submenu(DRBL_menu_boot)
		DRBL_menu.append(DRBL_menu_root_boot)

		# User Menu
		
		DRBL_menu_user_useradd = gtk.MenuItem("Add User")
		DRBL_menu_user_userdel = gtk.MenuItem("Del User")

		DRBL_menu_user_useradd.connect("activate", self.drbl_user_useradd)
		DRBL_menu_user_userdel.connect("activate", self.drbl_user_userdel)

		DRBL_menu_user = gtk.Menu()
		DRBL_menu_user.append(DRBL_menu_user_useradd)
		DRBL_menu_user.append(DRBL_menu_user_userdel)

		DRBL_menu_root_user = gtk.MenuItem("User")
		DRBL_menu_root_user.set_submenu(DRBL_menu_user)
		DRBL_menu.append(DRBL_menu_root_user)

		# Help Menu

		DRBL_menu_help_about = gtk.MenuItem("About")
		DRBL_menu_help_about.connect("activate", self.drbl_about)
		DRBL_menu_help = gtk.Menu()
		DRBL_menu_help.append(DRBL_menu_help_about);
		DRBL_menu_root_help = gtk.MenuItem("Help")
		DRBL_menu_root_help.set_submenu(DRBL_menu_help)
		DRBL_menu.append(DRBL_menu_root_help)

		# Window
		DRBL_BG_image = gtk.Image()
		DRBL_BG_image.set_from_file("drblwp.png")

		menu_box = gtk.VBox(False, 0)
		menu_box.pack_start(DRBL_menu, False, False, 0)

		bg_box = gtk.VBox(False, 0)
		bg_box.pack_start(DRBL_BG_image, False, False, 0)

		main_box = gtk.VBox(False, 0)
		self.main_box = main_box
		main_box.pack_start(bg_box, False, False, 0)

		box = gtk.VBox(False,0)
		self.box = box
		box.pack_start(menu_box, False, False, 0)
		box.pack_end(main_box, False, False, 0)

		window = gtk.Window()
		self.window = window
		window.set_title("DRBL")
		window.set_size_request(640,500)
		window.set_position(gtk.WIN_POS_CENTER)
		try:
		    self.icon = window.set_icon_from_file("drbl.png")
		except Exception, e:
		    print e.message
		    sys.exit(1)

		window.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#FFFFFF"))
		window.add(box)
		window.connect('delete-event', lambda window, event: gtk.main_quit())
		window.show_all()
		
	def drbl_about(self, widget):
	    _about = gtk.AboutDialog()
	    _about.set_name('DRBL')
	    _about.set_logo(gtk.gdk.pixbuf_new_from_file("drbl.png"))		
	    _about.set_authors([
		'Steven  <steven@nchc.org.tw>',
		'Thomas  <thomas@nchc.org.tw>',
		'Ceasar  <ceasar@nchc.org.tw>',
		'Jazz    <jazz@nchc.org.tw>'
		])
	    _about.set_copyright('Copyright (C) 2010 by DRBL/Clonezilla project')
	    _about.set_license('GNU General Public License V2')
	    _about.set_comments('Diskless Remote Boot in Linux')
	    _about.run()
	    _about.destroy()

	def drblsrv(self, widget):
	    
	    self.main_box.hide()
	    self.main_box = gtk.VBox(False,0)
	    label = gtk.Label("srblsrv options")
	    label.set_alignment(0, 0)
	    self.main_box.pack_start(label, False, False, 0)
	    label.show()

	    box = gtk.VBox()
	    testing_button = gtk.CheckButton("testing")
	    testing_button.set_active(False)
	    testing_button.unset_flags(gtk.CAN_FOCUS)
	    testing_button.connect("clicked", self.set_option, "testing")
	    

	    unstable_button = gtk.CheckButton("unstable")
	    unstable_button.set_active(False)
	    unstable_button.unset_flags(gtk.CAN_FOCUS)
	    unstable_button.connect("clicked", self.set_option, "unstable")

	    netinstall_button = gtk.CheckButton("netinstall")
	    netinstall_button.set_active(False)
	    netinstall_button.unset_flags(gtk.CAN_FOCUS)
	    netinstall_button.connect("clicked", self.set_option, "netinstall")

	    smp_client_button = gtk.CheckButton("smp client")
	    smp_client_button.set_active(False)
	    smp_client_button.unset_flags(gtk.CAN_FOCUS)
	    smp_client_button.connect("clicked", self.set_option, "smp")

	    console_output_button = gtk.CheckButton("console output")
	    console_output_button.set_active(False)
	    console_output_button.unset_flags(gtk.CAN_FOCUS)
	    console_output_button.connect("clicked", self.set_option, "console")

	    upgrade_system_button = gtk.CheckButton("upgrade_system")
	    upgrade_system_button.set_active(False)
	    upgrade_system_button.unset_flags(gtk.CAN_FOCUS)
	    upgrade_system_button.connect("clicked", self.set_option, "upgrade")

	    archi_button = gtk.combo_box_new_text()
	    archi_button.connect("changed", self.set_option, "arch")
	    archi_button.append_text('i386')
	    archi_button.append_text('i586')
	    archi_button.append_text('DRBL')
	    archi_button.set_active(0)
	    
	    kernel_button = gtk.combo_box_new_text()
	    kernel_button.connect("changed", self.set_option, "kernel")
	    kernel_button.append_text('ayo')
	    kernel_button.append_text('DRBL')
	    kernel_button.set_active(1)
	    
	    box.pack_start(testing_button, False, False, 0)
	    box.pack_start(unstable_button, False, False, 0)
	    box.pack_start(netinstall_button, False, False, 0)
	    box.pack_start(smp_client_button, False, False, 0)
	    box.pack_start(console_output_button, False, False, 0)
	    box.pack_start(upgrade_system_button, False, False, 0)
	    box.pack_start(archi_button, False, False, 0)
	    box.pack_start(kernel_button, False, False, 0)
	    testing_button.show()
	    unstable_button.show()
	    netinstall_button.show()
	    smp_client_button.show()
	    console_output_button.show()
	    upgrade_system_button.show()
	    archi_button.show()
	    kernel_button.show()
	    
	    apply_button = gtk.Button("Apply")
	    apply_button.set_size_request(80, 35)
	    id = apply_button.connect("clicked", self.do_apply)
	    box.pack_start(apply_button, False, False, 0)
	    apply_button.show()

	    self.main_box.pack_start(box, False, False, 0)
	    box.show()
	    
	    self.box.pack_start(self.main_box, False, False, 0)
	    self.main_box.show()
	    self.box.show()
	    
    
	def drblpush(self, widget):
	    os.system("ls /")

	def drbl_boot_shutdown(self, widget):
	    cmd = "shutdown"
	    print cmd

	def drbl_boot_wakeonlan(self, widget):
	    cmd = "WOL"
	    print cmd

	def drbl_boot_reboot(self, widget):
	    cmd = "reboot"
	    print cmd

	def drbl_boot_switch_pxe_menu(self, widget):
	    cmd = "switch pxe menu"
	    print cmd

	def drbl_boot_switch_pxe_bg_mode(self, widget):
	    cmd = "switch pxe bg mode"
	    print cmd

	def drbl_remote_gra(self, widget):
	    cmd = "remote_gra"
	    print cmd

	def drbl_remote_txt(self, widget):
	    cmd = "remote_txt"
	    print cmd

	def drbl_remote_memtest(self, widget):
	    cmd = "remote_memtest"
	    print cmd

	def drbl_remote_terminal(self, widget):
	    cmd = "remote_terminal"
	    print cmd

	def drbl_remote_local(self, widget):
	    cmd = "remote_local"
	    print cmd

	def drbl_user_useradd(self, widget):
	    cmd = "useradd"
	    print cmd

	def drbl_user_userdel(self, widget):
	    cmd = "userdel"
	    print cmd

	def set_chk_option(self, widget, option_str):
	    if widget.get_active():
		self.srv_options += option_str
	    else:
		self.srv_options = string.replace(self.srv_options, option_str, "")

	def set_option(self, widget, option_srt):
	    #fixme
	    if option_srt == "arch":
		new_option = "-k %d " % widget.get_active()
		self.srv_options = re.sub('-k\s\d\s', new_option, self.srv_options)
	    elif option_srt == "kernel":
		new_option = "-o %d " % widget.get_active()
		self.srv_options = re.sub('-o\s\d\s', new_option, self.srv_options)
	    elif option_srt == "testing":
		if widget.get_active():
		    new_option = "-t y "
		else:
		    new_option = "-t n "
		self.srv_options = re.sub('-t\s\w\s', new_option, self.srv_options)
	    elif option_srt == "unstable":
		if widget.get_active():
		    new_option = "-a y "
		else:
		    new_option = "-a n "
		self.srv_options = re.sub('-a\s\w\s', new_option, self.srv_options)
	    elif option_srt == "netinstall":
		if widget.get_active():
		    new_option = "-n y "
		else:
		    new_option = "-n n "
		self.srv_options = re.sub('-n\s\w\s', new_option, self.srv_options)
	    elif option_srt == "smp":
		if widget.get_active():
		    new_option = "-m y "
		else:
		    new_option = "-m n "
		self.srv_options = re.sub('-m\s\w\s', new_option, self.srv_options)
	    elif option_srt == "console":
		if widget.get_active():
		    new_option = "-c y "
		else:
		    new_option = "-c n "
		self.srv_options = re.sub('-c\s\w\s', new_option, self.srv_options)
	    elif option_srt == "upgrade":
		if widget.get_active():
		    new_option = "-g y "
		else:
		    new_option = "-g n "
		self.srv_options = re.sub('-g\s\w\s', new_option, self.srv_options)

	def do_apply(self, widget):
	    #print self.srv_options
	    srv_cmd = "/opt/drbl/sbin/drblsrv -i %s" % self.srv_options
	    close_cmd = "sleep 5; exit\n"
	    print srv_cmd
	    ## Terminal
	    srv_term = vte.Terminal()
	    srv_term.fork_command()
	    srv_term.feed_child(srv_cmd+'\n')
	    srv_term.feed_child(close_cmd+'\n')

	    self.main_box.hide()
	    self.main_box = gtk.VBox(False,0)
	    self.main_box.pack_start(srv_term,False,False,0)
	    srv_term.show()
	    self.box.pack_start(self.main_box,False,False,0)
	    self.main_box.show()
	    self.box.show()
	

if __name__ == '__main__':
	DRBL_GUI_Template()
 	gtk.main()

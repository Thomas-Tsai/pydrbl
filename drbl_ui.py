#!/usr/bin/python
import os
import string
import re
import gobject

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


options = {}
opt_value = {}
opt_value_def = {}

options["drblsrv"] = {
#"i", "install", "install DRBL.", "", "check"),
#"u", "uninstall", "uninstall DRBL.", "", "check"),
"g":("upgrade_system", "upgrade system or not.", "yn", "check"),
"t":("testing", "use packages in testing branch or not.", "yn", "check"),
"a":("unstable", "use packages in unstable branch or not.", "yn", "check"),
"s":("skip-select-repository", "skip the question for selecting repository.", "", "check"),
"n":("netinstall", "install the network installation program or not.", "yn", "check"),
"m":("smp-client", "use SMP kernel for DRBL clients or not.", "yn", "check"),
"f":("force-yes", "force yes, only for Debian-like distribution. It  should  not  be used except in very special situations. Using force-yes can potentially destroy your system!", "", "check"),
"v":("verbose", "verbose mode.", "", "check"),
"x":("set-proxy", "set proxy or not.", "yn", "check"),
"c":("console-output", "set console output for client or not.", "yn", "check"),
"k":("client_archi", "set the client's CPU arch.", {0:"i386",1:"i586",2:"DRBL"}, "combo"),
"o":("client_kernel_from", "choose client's kernel image from ", {0:"",1:"DRBL server",2:"ayo repository"}, "combo"),
"l":("language", "Set the language to be shown.", {0:"English",1:"Traditional Chinese (Big5) - Taiwan",2:"Traditional Chinese (UTF-8, Unicode) - Taiwan"}, "combo")
}

options["drblpush"] = {
#("h", "help", "Show this help message", "", ""),
"b":("not-add-start-drbl-srvi", "Do NOT add and start DRBL related services after the configuration is done", "", "check"),
"c":("config", "The DRBL config file, text format", "args", "file"),
"d":("debug", "Turn on debug mode when run shell script", "", "check"),
"e":("accept-one-nic", "Accept to run DRBL service in only one network card. ///NOTE/// This might mess up your network environment especially if there is an existing DHCP service in your network environment.", "", "check"),
"i":("interactive", "Interactive mode, setup step by step.", "", "check"),
"k":("keep_clients", "Keep previously saved files for clients.", "yn", "check"),
"m":("client_startup_mode", "Assign client mode", {"0":"","1":"graphic mode","2":"text mode"}, "combo"),
"n":("no_deploy", "Just create files, do NOT deploy the files into system", "", "check"),
"o":("clonezilla_home",  "Use DIR as the clonezilla image directory", "args", "folder"),
"p":("port_client_no", "The client no. in each NIC port.", "args", "text"),
"q":("quiet", "Be less verbose", "", "check"),
"r":("drbl_mode", "Assign DRBL mode", {"0":"Full DRBL mode", "1":"DRBL SSI mode", "2":"Do NOT provide diskless Linux service to clients"}, "combo"),
"s":("swap_create", "Switch to create and use local swap in clients", "yn", "check"),
"u":("live_client_cpu_mode", "Assign the CPU mode for client when doing Clonezilla job with Clonezilla live", {"0":"i486", "1":"i686", "2":"amd64"}, "combo"),
"v":("verbose", "Be more verbose", "", "check"),
"z":("clonezilla_mode", "Assign Clonezilla mode", {"0":"Full DRBL mode", "1":"Clonezilla box mode", "2":"Do NOT provide clonezilla service to clients", "3":"Use Clonezilla live as the OS of clients"}, "combo"),
"l":("language", "Set the language to be shown.", {0:"English",1:"Traditional Chinese (Big5) - Taiwan",2:"Traditional Chinese (UTF-8, Unicode) - Taiwan"}, "combo")
}

opt_value_def["drblsrv"] = {
    "f":"",
#    "i":"",
#    "u":"",
    "v":"",
    "t":"y",
    "a":"n",
    "n":"n",
    "m":"n",
    "x":"n",
    "c":"n",
    "g":"n",
    "k":"2",
    "o":"1",
    "s":"",
    "l":"0"
}

opt_value_def["drblpush"] = {
    "b":"",
    "c":"",
    "d":"",
    "e":"",
    "i":"y",
    "k":"y",
    "m":"1",
    "n":"",
    "o":"/home/partimag",
    "p":"12",
    "q":"",
    "r":"0",
    "s":"y",
    "u":"1",
    "v":"",
    "z":"0",
    "l":"0"
}

drbl_hosts = []
drbl_pxe_menu = []
dcs_mode_1 = ("shutdown", "Wake-on-LAN", "reboot", "boot_switch_pxe_menu", "boot_switch_pxe_bg_mode", "remote-linux-gra", "remote-linux-txt", "remote-memtest", "terminal", "local")


drblsrv_cmd = "/opt/drbl/sbin/drblsrv"
drblpush_cmd = "/opt/drbl/sbin/drblpush"
dcs_cmd = "/opt/drbl/sbin/dcs"

class DRBL_GUI_Template():
	vterm = vte.Terminal()

	def __init__(self):
		DRBL_menu = gtk.MenuBar()

		# File Menu
		DRBL_menu_file_quit = gtk.MenuItem("Quit")
		DRBL_menu_file_srv_i  = gtk.MenuItem("drblsrv install")
		DRBL_menu_file_srv_u  = gtk.MenuItem("drblsrv uninstall")
		DRBL_menu_file_push = gtk.MenuItem("drblpush")

		DRBL_menu_file_quit.connect("activate", gtk.main_quit)
		DRBL_menu_file_srv_i.connect("activate", self.drblsrv_i)
		DRBL_menu_file_srv_u.connect("activate", self.drblsrv_u)
		DRBL_menu_file_push.connect("activate", self.drblpush)

		DRBL_menu_file = gtk.Menu()
		DRBL_menu_file.append(gtk.SeparatorMenuItem())
		DRBL_menu_file.append(DRBL_menu_file_srv_i)
		DRBL_menu_file.append(DRBL_menu_file_srv_u)
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
		DRBL_menu_remote_txt.connect("activate", self.drbl_remote_txt)
		DRBL_menu_remote_local.connect("activate", self.drbl_remote_local)
		DRBL_menu_remote_memtest.connect("activate", self.drbl_remote_memtest)
		DRBL_menu_remote_terminal.connect("activate", self.drbl_remote_terminal)

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
		box.pack_start(main_box, False, False, 0)

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
		

	def collect_drbl_hosts(self):
	    drbl_cmd = "/opt/drbl/bin/get-client-ip-list"
	    del drbl_hosts[0:]
	    drbl_hosts.append([True, "ALL", ""])
	    for ip in os.popen(drbl_cmd).readlines():
		ip = ip[:-1]
		client=[True, ip, ""]
		drbl_hosts.append(client)

	def get_host(self):
	    client = []
	    for c in drbl_hosts:
		if c[0] == True:
		    client.append(c[1])
	    return client

	def list_hosts(self, box):

	    liststore = gtk.ListStore(gobject.TYPE_BOOLEAN, gobject.TYPE_STRING, gobject.TYPE_STRING)
	    treeview = gtk.TreeView(liststore)
	    treeview.set_rules_hint(True)
	    treeview.get_selection().set_mode(gtk.SELECTION_NONE)

	    render = gtk.CellRendererToggle()
	    render.set_property('activatable', True)
	    render.set_property('width', 20)
	    render.connect ('toggled', self.on_toggled_host, liststore)
	    col = gtk.TreeViewColumn()
	    col.pack_start(render)
	    col.set_attributes(render, active=0)
	    treeview.append_column(col)

	    column_ip = gtk.TreeViewColumn('IP')
	    column_mac = gtk.TreeViewColumn('MAC')
	    treeview.append_column(column_ip)	
	    treeview.append_column(column_mac)	
	    cell_ip = gtk.CellRendererText()
	    cell_mac = gtk.CellRendererText()

	    column_ip.pack_start(cell_ip, True)
	    column_mac.pack_start(cell_mac, True)

	    column_ip.set_attributes(cell_ip, text=1)
	    column_mac.set_attributes(cell_mac, text=2)

	    self.collect_drbl_hosts()

	    for host in drbl_hosts:
		liststore.append(host)

	    treeview.set_search_column(0)
	    column_ip.set_sort_column_id(0)
	    treeview.set_reorderable(True)

	    box.pack_start(treeview, False, False, 0)
	    treeview.show()
	
	def on_toggled_host(self, render, path, list):
	    it = list.get_iter_from_string(path)
	    value, ip = list.get(it, 0, 1)
	    value = not value
	    i = 0
	    if ip == 'ALL':
		for all_toggle, all_ip, all_mac in drbl_hosts:
		    drbl_hosts[i][0] = value
		    list.set(it, 0, value)
		    i = i+1
		    it = list.iter_next(it)
	    else:
		list.set(it, 0, value)
		for all_toggle, all_ip, all_mac in drbl_hosts:
		    if ip == all_ip:
			drbl_hosts[i][0] = value
		    i = i+1

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

	def drblsrv_i(self, widget):
	    action = "drblsrv_i"
	    opt_value["drblsrv"] = opt_value_def["drblsrv"].copy()
	    self.main_box.hide()
	    self.main_box = gtk.VBox(False,0)
	    self.main_box.show()
	    label = gtk.Label("srblsrv options")
	    label.set_alignment(0, 0)
	    self.main_box.pack_start(label, False, False, 0)
	    label.show()

	    box = gtk.VBox()
	    for sopt in options["drblsrv"].keys():
		lopt, desc_opt, value_opt, type = options["drblsrv"][sopt]
		#print  sopt, lopt, desc_opt, value_opt, type

		if type == "check":
		    sopt_button = gtk.CheckButton(desc_opt)
		    if opt_value["drblsrv"][sopt] == "y":
			sopt_button.set_active(True)
		    else:
			sopt_button.set_active(False)
		    sopt_button.unset_flags(gtk.CAN_FOCUS)
		    sopt_button.connect("clicked", self.set_option, sopt, action)
		    box.pack_start(sopt_button, False, False, 0)
		    sopt_button.show()
		elif type == "combo":
		    sopt_box = gtk.HBox()
		    sopt_label = gtk.Label(desc_opt)
		    sopt_label.set_max_width_chars(50)
		    sopt_button = gtk.combo_box_new_text()
		    sopt_button.connect("changed", self.set_option, sopt, action)
		    for ko in value_opt.keys():
			sopt_button.append_text(value_opt[ko])
			try:
			    def_opt = string.atoi(opt_value["drblsrv"][sopt], 10)
			except:
			    def_opt = opt_value["drblsrv"][sopt]
		    sopt_button.set_active(def_opt)
		    sopt_box.pack_start(sopt_label, False, False, 0)
		    sopt_box.pack_end(sopt_button, False, False, 0)
		    sopt_label.show()
		    sopt_button.show()
		    box.pack_start(sopt_box, False, False, 0)
		    sopt_box.show()

	    action_box = gtk.HBox()
	    apply_button = gtk.Button("Apply")
	    apply_button.set_size_request(80, 35)
	    id = apply_button.connect("clicked", self.do_apply, action)

	    cancel_button = gtk.Button("Cancel")
	    cancel_button.set_size_request(80, 35)
	    id = cancel_button.connect("clicked", self.do_cancel)
	    
	    reset_button = gtk.Button("Reset")
	    reset_button.set_size_request(80, 35)
	    id = reset_button.connect("clicked", self.drblsrv_i)

	    action_box.pack_end(apply_button, False, False, 0)
	    action_box.pack_end(cancel_button, False, False, 0)
	    action_box.pack_end(reset_button, False, False, 0)
	    cancel_button.show()
	    apply_button.show()
	    reset_button.show()
	    box.pack_end(action_box, True, False, 0)
	    action_box.show()

	    self.main_box.pack_start(box, True, True, 0)
	    box.show()
	    
	    self.box.pack_start(self.main_box, True, True, 0)
	    self.main_box.show()
	    self.box.show()
	    
	def drblsrv_u(self, widget):
	    action = "drblsrv_u"
	    self.main_box.hide()
	    self.main_box = gtk.VBox(False,0)
	    self.main_box.show()

	    label = gtk.Label("will run drblsrv -u")
	    label.set_alignment(0, 0)
	    self.main_box.pack_start(label, False, False, 0)
	    label.show()


	    action_box = gtk.HBox()
	    apply_button = gtk.Button("Apply")
	    apply_button.set_size_request(80, 35)
	    id = apply_button.connect("clicked", self.do_apply, action)

	    cancel_button = gtk.Button("Cancel")
	    cancel_button.set_size_request(80, 35)
	    id = cancel_button.connect("clicked", self.do_cancel)
	    
	    action_box.pack_end(apply_button, False, False, 0)
	    action_box.pack_end(cancel_button, False, False, 0)
	    cancel_button.show()
	    apply_button.show()

	    self.main_box.pack_start(action_box, False, False, 0)
	    action_box.show()
	    
	    self.box.pack_start(self.main_box, False, False, 0)
	    self.main_box.show()
	    self.box.show()
	
    
	def drblpush(self, widget):
	    action = "drblpush"
	    opt_value["drblpush"] = opt_value_def["drblpush"].copy()
	    self.main_box.hide()
	    self.main_box = gtk.VBox(False,0)
	    self.main_box.show()
	    label = gtk.Label("srblpush options")
	    label.set_alignment(0, 0)
	    self.main_box.pack_start(label, False, False, 0)
	    label.show()

	    box = gtk.VBox()
	    for sopt in options["drblpush"].keys():
		lopt, desc_opt, value_opt, type = options["drblpush"][sopt]
		#print  sopt, lopt, desc_opt, value_opt, type
		if type == "check":
		    sopt_button = gtk.CheckButton(desc_opt)
		    if opt_value["drblpush"][sopt] == "y":
			sopt_button.set_active(True)
		    else:
			sopt_button.set_active(False)
		    sopt_button.unset_flags(gtk.CAN_FOCUS)
		    sopt_button.connect("clicked", self.set_option, sopt, action)
		    box.pack_start(sopt_button, False, False, 0)
		    sopt_button.show()
		elif type == "combo":
		    sopt_box = gtk.HBox()
		    sopt_label = gtk.Label(desc_opt)
		    sopt_label.set_max_width_chars(50)
		    sopt_button = gtk.combo_box_new_text()
		    sopt_button.connect("changed", self.set_option, sopt, action)
		    combo_args = value_opt.keys()
		    combo_args.sort()
		    for ko in combo_args:
			sopt_button.append_text(value_opt[ko])
			try:
			    def_opt = string.atoi(opt_value["drblpush"][sopt], 10)
			except:
			    def_opt = opt_value["drblpush"][sopt]
		    sopt_button.set_active(def_opt)
		    sopt_box.pack_start(sopt_label, False, False, 0)
		    sopt_box.pack_end(sopt_button, False, False, 0)
		    sopt_label.show()
		    sopt_button.show()
		    box.pack_start(sopt_box, False, False, 0)
		    sopt_box.show()

	    action_box = gtk.HBox()
	    apply_button = gtk.Button("Apply")
	    apply_button.set_size_request(80, 35)
	    id = apply_button.connect("clicked", self.do_apply, action)

	    lazy_button = gtk.Button("Lazy Apply")
	    lazy_button.set_size_request(80, 35)
	    id = lazy_button.connect("clicked", self.do_apply, "lazypush")

	    cancel_button = gtk.Button("Cancel")
	    cancel_button.set_size_request(80, 35)
	    id = cancel_button.connect("clicked", self.do_cancel)
	    
	    reset_button = gtk.Button("Reset")
	    reset_button.set_size_request(80, 35)
	    id = reset_button.connect("clicked", self.drblpush)

	    action_box.pack_end(apply_button, False, False, 0)
	    action_box.pack_end(lazy_button, False, False, 0)
	    action_box.pack_end(cancel_button, False, False, 0)
	    action_box.pack_end(reset_button, False, False, 0)
	    cancel_button.show()
	    apply_button.show()
	    lazy_button.show()
	    reset_button.show()
	    box.pack_end(action_box, True, False, 0)
	    action_box.show()

	    self.main_box.pack_start(box, True, True, 0)
	    box.show()
	    
	    self.box.pack_start(self.main_box, True, True, 0)
	    self.main_box.show()
	    self.box.show()

	def action_for_host_mode(self, widget, action):
	    self.main_box.hide()
	    self.main_box = gtk.VBox(False,0)
	    self.main_box.show()

	    box = gtk.VBox()
	    self.list_hosts(box)

	    action_box = gtk.HBox()
	    apply_button = gtk.Button("Apply")
	    apply_button.set_size_request(80, 35)
	    id = apply_button.connect("clicked", self.do_apply, action)

	    cancel_button = gtk.Button("Cancel")
	    cancel_button.set_size_request(80, 35)
	    id = cancel_button.connect("clicked", self.do_cancel)
	    
	    reset_button = gtk.Button("Reset")
	    reset_button.set_size_request(80, 35)
	    id = reset_button.connect("clicked", self.action_for_host_mode, action)

	    action_box.pack_end(apply_button, False, False, 0)
	    action_box.pack_end(cancel_button, False, False, 0)
	    action_box.pack_end(reset_button, False, False, 0)
	    cancel_button.show()
	    apply_button.show()
	    reset_button.show()
	    box.pack_end(action_box, True, False, 0)
	    action_box.show()

	    self.main_box.pack_start(box, True, True, 0)
	    box.show()

	    self.box.pack_start(self.main_box, True, True, 0)
	    self.main_box.show()
	    self.box.show()

	def drbl_boot_shutdown(self, widget):
	    action = "shutdown"
	    self.action_for_host_mode(self, action)

	def drbl_boot_wakeonlan(self, widget):
	    action = "Wake-on-LAN"
	    self.action_for_host_mode(self, action)
	   
	def drbl_boot_reboot(self, widget):
	    action = "reboot"
	    self.action_for_host_mode(self, action)
	    
	def drbl_remote_gra(self, widget):
	    action = "remote-linux-gra"
	    self.action_for_host_mode(self, action)

	def drbl_remote_txt(self, widget):
	    action = "remote-linux-txt"
	    self.action_for_host_mode(self, action)

	def drbl_remote_memtest(self, widget):
	    action = "remote-memtest"
	    self.action_for_host_mode(self, action)

	def drbl_remote_terminal(self, widget):
	    action = "terminal"
	    self.action_for_host_mode(self, action)

	def drbl_remote_local(self, widget):
	    action = "local"
	    self.action_for_host_mode(self, action)

	def drbl_boot_switch_pxe_menu(self, widget):
	    action = "boot_switch_pxe_menu"
	    self.action_for_pxe_menu(self, action)

	def drbl_boot_switch_pxe_bg_mode(self, widget):
	    action = "boot_switch_pxe_bg_mode"
	    self.action_for_pxe_bg_mode(self, action)

	def drbl_user_useradd(self, widget):
	    cmd = "useradd"
	    print cmd

	def drbl_user_userdel(self, widget):
	    cmd = "userdel"
	    print cmd

	def set_option(self, widget, short_option, action):
	    #print short_option
	    if action == "drblsrv_i":
		for sopt in options["drblsrv"].keys():
		    lopt, desc_opt, value_opt, type = options["drblsrv"][sopt]
		    if sopt == short_option:
			if type == "check":
			    if widget.get_active() == True:
				opt_value["drblsrv"][short_option] = "y"
			    elif widget.get_active() == False:
				opt_value["drblsrv"][short_option] = "n"
			elif type == "combo":
				opt_value["drblsrv"][short_option] = widget.get_active()
	    elif action == "drblpush":
		for sopt in options["drblpush"].keys():
		    lopt, desc_opt, value_opt, type = options["drblpush"][sopt]
		    if sopt == short_option:
			if type == "check":
			    if widget.get_active() == True:
				opt_value["drblpush"][short_option] = "y"
			    elif widget.get_active() == False:
				opt_value["drblpush"][short_option] = "n"
			elif type == "combo":
				opt_value["drblpush"][short_option] = widget.get_active()

	def do_apply(self, widget, action):

	    option_str = " "
	    if action == "drblsrv_i":
		for opt_s in opt_value["drblsrv"].keys():
		    if opt_value["drblsrv"][opt_s] != "":
			if options["drblsrv"][opt_s][2] == "":
			    tmp_opt = "-%s " % opt_s
			else:
			    tmp_opt = "-%s %s " % (opt_s, opt_value["drblsrv"][opt_s])
			option_str = option_str + tmp_opt
		run_cmd = "%s -i %s" % (drblsrv_cmd, option_str)
	    elif action == "drblsrv_u":
		run_cmd = "%s -u %s" % (drblsrv_cmd, option_str)
	    elif action == "drblpush":
		for opt_s in opt_value["drblpush"].keys():
		    if opt_value["drblpush"][opt_s] != "":
			if options["drblpush"][opt_s][2] == "":
			    tmp_opt = "-%s " % opt_s
			else:
			   tmp_opt = "-%s %s " % (opt_s, opt_value["drblpush"][opt_s])
			option_str = option_str + tmp_opt
		run_cmd = "%s %s" % (drblpush_cmd, option_str)
	    elif action == "lazypush":
		for opt_s in opt_value["drblpush"].keys():
		    if opt_value["drblpush"][opt_s] != "":
			if options["drblpush"][opt_s][2] == "":
			    tmp_opt = "-%s " % opt_s
			else:
			   tmp_opt = "-%s %s " % (opt_s, opt_value["drblpush"][opt_s])
			option_str = option_str + tmp_opt
		run_cmd = "yes \'\' | %s %s" % (drblpush_cmd, option_str)
	    elif action in dcs_mode_1:
		cmd_options = "-nl"
		clients = []
		clients = self.get_host()
		action_host = ""
		for h in clients:
		    if h == "ALL":
			break
		    else:
			action_host = action_host + " " + h
		
		if action_host == "":
		    cmd_options = "-nl"
		else:
		    cmd_options = "-h \" %s \"" % action_host
		
		run_cmd = "%s %s %s" % (dcs_cmd, cmd_options, action)
	    #elif action = "boot_switch_pxe_menu":
	#	run_cmd = "%s %s %s" % (switch_pxe_cmd, cmd_options, label)

	    else:
		run_cmd = "exit\n"
		print "not impliement."

	    close_cmd = "exit\n"
	    print run_cmd

	    self.main_box.hide()
	    self.main_box = gtk.VBox(False,0)
	    self.main_box.show()

	    apply_box = gtk.VBox()
	    label = gtk.Label("apply...")
	    label.set_alignment(0, 0)
	    apply_box.pack_start(label, False, False, 0)
	    label.show()

	    ## Terminal
	    self.vterm = vte.Terminal()
	    self.vterm.fork_command()
	    self.vterm.feed_child(run_cmd+'\n')
	    self.vterm.feed_child(close_cmd+'\n')
	    self.vterm.connect('child-exited', self.do_complete)
	    apply_box.pack_start(self.vterm,False,False,0)
	    self.vterm.show()
	    
	    action_box = gtk.HBox()
	    abort_button = gtk.Button("Abort")
	    finish_button = gtk.Button("Finish")
	    id = abort_button.connect("clicked", self.do_cancel)
	    id = finish_button.connect("clicked", self.do_cancel)
	    action_box.pack_end(finish_button, False, False, 0)
	    action_box.pack_end(abort_button, False, False, 0)
	    abort_button.show()
	    finish_button.show()
	    apply_box.pack_end(action_box, False, False, 0)
	    action_box.show()

	    self.main_box.pack_start(apply_box, False, False, 0)
	    apply_box.show()

	    self.box.pack_start(self.main_box,False,False,0)
	    self.main_box.show()
	    self.box.show()
	
	def do_cancel(self, widget):
	    self.box.hide()
	    self.main_box.hide()
	    self.main_box = gtk.VBox(False,0)
	    self.main_box.show()
	    # Window
	    DRBL_BG_image = gtk.Image()
	    DRBL_BG_image.set_from_file("drblwp.png")

	    bg_box = gtk.VBox(False, 0)
	    bg_box.pack_start(DRBL_BG_image, False, False, 0)
	    DRBL_BG_image.show()
	    self.main_box.pack_start(bg_box, False, False, 0)
	    bg_box.show()

	    self.box.pack_start(self.main_box, True, True, 0)
	    self.main_box.show()
	    self.box.show()

	def do_complete(self, widget):
	    self.vterm.feed("\nFinish!\n")
	    
if __name__ == '__main__':
	DRBL_GUI_Template()
 	gtk.main()

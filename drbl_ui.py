import os
import sys
import string
import re
import gobject
import gettext
import locale
import drbl_assistant
import pango

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
APP_NAME="drbl_ui"
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
drblsrv_u_options = {"Dist":"n", "DRBL":"n"}
drblsrv_u_option_desc = {"Dist":"Do you want to remove the small GNU/Linux Distributions", "DRBL":"Do you want to remove the drbl package"}
drbl_hosts = []
pxe_menu = []
user_list = []
update_pxe_menu = []
pxe_bg_mode = "graphic"
dcs_mode_1 = ("shutdown", "Wake-on-LAN", "reboot", "remote-linux-gra", "remote-linux-txt", "remote-memtest", "terminal", "local")

drblsrv_cmd = "/opt/drbl/sbin/drblsrv"
drblpush_cmd = "/opt/drbl/sbin/drblpush"
dcs_cmd = "/opt/drbl/sbin/dcs"
pxe_cmd = "switch-pxe-menu"
pxe_bg_cmd = "switch-pxe-bg-mode"
user_add_cmd = "/opt/drbl/sbin/drbl-useradd"
user_del_cmd = "/opt/drbl/sbin/drbl-userdel"

## i18n
## Copy from "blog learning python" http://www.learningpython.com/2006/12/03/translating-your-pythonpygtk-application/
#Translation stuff

#Get the local directory since we are not installing anything
local_path = os.path.realpath(os.path.dirname(sys.argv[0]))
local_path = os.path.join (local_path, 'locale')

# Init the list of languages to support
langs = []
#Check the default locale
lc, encoding = locale.getdefaultlocale()
if (lc):
	#If we have a default, it's the first in the list
	langs = [lc]
# Now lets get all of the supported languages on the system
language = os.environ.get('LANGUAGE', None)
if (language):
	"""langage comes back something like en_CA:en_US:en_GB:en
	on linuxy systems, on Win32 it's nothing, so we need to
	split it up into a list"""
	langs += language.split(":")
"""Now add on to the back of the list the translations that we
know that we have, our defaults"""
langs += ["en_CA", "en_US"]

"""Now langs is a list of all of the languages that we are going
to try to use.  First we check the default, then what the system
told us, and finally the 'known' list"""

gettext.bindtextdomain(APP_NAME, local_path)
gettext.textdomain(APP_NAME)
# Get the language to use
lang = gettext.translation(APP_NAME, local_path
	, languages=langs, fallback = True)
"""Install the language, map _() (which we marked our
strings to translate with) to lang.gettext() which will
translate them."""
_ = lang.gettext

desc_shutdown = _("Shutdown DRBL clients now")
desc_Wake_on_LAN = _("Turn on DRBL clients by Wake-on-LAN now")
desc_reboot = _("Reboot DRBL clients now")
desc_remote_linux_gra = _("Client machine will boot from DRBL server, and enter graphic mode, for powerful client.")
desc_remote_linux_txt = _("Client machine will boot from DRBL server, and enter text mode, for powerful client.")
desc_remote_memtest = _("Remote boot to run memtest86")
desc_terminal = _("Remote display Linux, terminal mode")
desc_local = _("Client machine will boot from local (now PXE only)")

desc_of_dcs_mode1 = {  
    "shutdown": desc_shutdown, 
    "Wake-on-LAN": desc_Wake_on_LAN,
    "reboot" : desc_reboot, 
    "remote-linux-gra" : desc_remote_linux_gra, 
    "remote-linux-txt" : desc_remote_linux_txt, 
    "remote-memtest": desc_remote_memtest, 
    "terminal": desc_terminal, 
    "local": desc_local
    }

class DRBL_GUI_Template():
	vterm = vte.Terminal()

	def __init__(self):

	    DRBL_menu = gtk.MenuBar()

	    # File Menu
	    DRBL_menu_file_quit = gtk.MenuItem(_("Quit"))
	    DRBL_menu_file_srv_i  = gtk.MenuItem(_("drblsrv install"))
	    DRBL_menu_file_srv_u  = gtk.MenuItem(_("drblsrv uninstall"))
	    DRBL_menu_file_push = gtk.MenuItem(_("drblpush"))
	    DRBL_menu_file_ass = gtk.MenuItem(_("drbl-assistant"))

	    DRBL_menu_file_quit.connect("activate", gtk.main_quit)
	    DRBL_menu_file_srv_i.connect("activate", self.drblsrv_i)
	    DRBL_menu_file_srv_u.connect("activate", self.drblsrv_u)
	    DRBL_menu_file_push.connect("activate", self.drblpush)
	    DRBL_menu_file_ass.connect("activate", self.drblassistant)

	    DRBL_menu_file = gtk.Menu()
	    DRBL_menu_file.append(DRBL_menu_file_ass)
	    DRBL_menu_file.append(DRBL_menu_file_srv_i)
	    DRBL_menu_file.append(DRBL_menu_file_srv_u)
	    DRBL_menu_file.append(DRBL_menu_file_push)
	    DRBL_menu_file.append(DRBL_menu_file_quit)

	    DRBL_menu_root_file = gtk.MenuItem(_("DRBL"))
	    DRBL_menu_root_file.set_submenu(DRBL_menu_file)
	    DRBL_menu.append(DRBL_menu_root_file)


	    # View Menu
	    #DRBL_menu_view_verbose = gtk.CheckMenuItem("Verbose")
	    #DRBL_menu_view_verbose.set_active(True)

	    #DRBL_menu_view = gtk.Menu()
	    #DRBL_menu_view.append(DRBL_menu_view_verbose)
	    
	    #DRBL_menu_root_view = gtk.MenuItem("View")
	    #DRBL_menu_root_view.set_submenu(DRBL_menu_view)
	    #DRBL_menu.append(DRBL_menu_root_view)

	    # Remote Menu
	    DRBL_menu_remote_gra      = gtk.MenuItem(_("Linux-gra"))
	    DRBL_menu_remote_txt      = gtk.MenuItem(_("Linux-txt"))
	    DRBL_menu_remote_local    = gtk.MenuItem(_("local"))
	    DRBL_menu_remote_memtest  = gtk.MenuItem(_("memtest"))
	    DRBL_menu_remote_terminal = gtk.MenuItem(_("Terminal"))

	    DRBL_menu_remote_gra.connect("activate", self.drbl_remote_gra)
	    DRBL_menu_remote_txt.connect("activate", self.drbl_remote_txt)
	    DRBL_menu_remote_local.connect("activate", self.drbl_remote_local)
	    DRBL_menu_remote_memtest.connect("activate", self.drbl_remote_memtest)
	    DRBL_menu_remote_terminal.connect("activate", self.drbl_remote_terminal)

	    DRBL_menu_remote = gtk.Menu()
	    DRBL_menu_remote.append(DRBL_menu_remote_gra)
	    DRBL_menu_remote.append(DRBL_menu_remote_txt)
	    DRBL_menu_remote.append(DRBL_menu_remote_memtest)
	    DRBL_menu_remote.append(DRBL_menu_remote_local)
	    DRBL_menu_remote.append(DRBL_menu_remote_terminal)

	    DRBL_menu_root_remote = gtk.MenuItem(_("Remote"))
	    DRBL_menu_root_remote.set_submenu(DRBL_menu_remote)
	    DRBL_menu.append(DRBL_menu_root_remote)

	    # Boot Menu
	    DRBL_menu_boot_shutdown           = gtk.MenuItem(_("Shutdown"))
	    DRBL_menu_boot_wakeonlan          = gtk.MenuItem(_("Wake On Lan"))
	    DRBL_menu_boot_reboot             = gtk.MenuItem(_("Reboot"))
	    DRBL_menu_boot_switch_pxe_menu    = gtk.MenuItem(_("PXE MENU"))
	    DRBL_menu_boot_switch_pxe_bg_mode = gtk.MenuItem(_("PXE BG MODE"))

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

	    DRBL_menu_root_boot = gtk.MenuItem(_("Boot"))
	    DRBL_menu_root_boot.set_submenu(DRBL_menu_boot)
	    DRBL_menu.append(DRBL_menu_root_boot)

	    # User Menu
	    
	    DRBL_menu_user_userlist = gtk.MenuItem(_("List User"))
	    DRBL_menu_user_useradd = gtk.MenuItem(_("Add User"))
	    DRBL_menu_user_userdel = gtk.MenuItem(_("Del User"))

	    DRBL_menu_user_userlist.connect("activate", self.drbl_user_userlist)
	    DRBL_menu_user_useradd.connect("activate", self.drbl_user_useradd)
	    DRBL_menu_user_userdel.connect("activate", self.drbl_user_userdel)

	    DRBL_menu_user = gtk.Menu()
	    DRBL_menu_user.append(DRBL_menu_user_userlist)
	    DRBL_menu_user.append(DRBL_menu_user_useradd)
	    DRBL_menu_user.append(DRBL_menu_user_userdel)

	    DRBL_menu_root_user = gtk.MenuItem(_("User"))
	    DRBL_menu_root_user.set_submenu(DRBL_menu_user)
	    DRBL_menu.append(DRBL_menu_root_user)

	    # Help Menu

	    DRBL_menu_help_about = gtk.MenuItem(_("About"))
	    DRBL_menu_help_about.connect("activate", self.drbl_about)
	    DRBL_menu_help = gtk.Menu()
	    DRBL_menu_help.append(DRBL_menu_help_about);
	    DRBL_menu_root_help = gtk.MenuItem(_("Help"))
	    DRBL_menu_root_help.set_submenu(DRBL_menu_help)
	    DRBL_menu.append(DRBL_menu_root_help)

	    # Window
	    DRBL_BG_image = gtk.Image()
	    DRBL_BG_image.set_from_file("drblwp.png")

	    menu_box = gtk.VBox(False, 0)
	    menu_box.pack_start(DRBL_menu, False, False, 0)

	    bg_box = gtk.VBox(False, 0)
	    bg_box.pack_start(DRBL_BG_image, False, False, 0)

	    welcome_msg = _("Enjoy DRBL right now!")
	    label = gtk.Label(welcome_msg)
	    fontdesc = pango.FontDescription("Purisa 16")
	    label.modify_font(fontdesc)

	    main_box = gtk.VBox(False, 0)
	    self.main_box = main_box
	    main_box.pack_start(label, False, False, 20)
	    main_box.pack_end(bg_box, False, False, 0)

	    box = gtk.VBox(False,0)
	    self.box = box
	    box.pack_start(menu_box, False, False, 0)
	    box.pack_end(main_box, True, True, 0)


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

	    window.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#E6E6E6"))
	    window.add(box)
	    window.connect('delete-event', lambda window, event: gtk.main_quit())
	    window.show_all()
		
	def collect_user_list(self):
	    nis_group = {}
	    del user_list[0:]
	    for group_line in os.popen("ypcat group.byname").readlines():
		group_line = group_line[:-1]
		(g_name, x, gid, something) = group_line.split(":")
		nis_group[gid] = g_name
	    for user_line in os.popen("ypcat passwd.byname").readlines():
		user_line = user_line[:-1]
		(user, x, uid, gid, full_name, home_path, shell) = user_line.split(":")
		user_data = [False, user, uid, gid, nis_group[gid], full_name, home_path, shell]
		user_list.append(user_data)


	def collect_pxe_menu(self):
	    pxe_list_menu = "./get-pxe-menu"
	    del pxe_menu[0:]
	    for menu_line in os.popen(pxe_list_menu).readlines():
		menu = menu_line[:-1].split(" ")
		if menu[2] == "True":
		    pmenu = [True, menu[0], menu[1]]
		else:
		    pmenu = [False, menu[0], menu[1]]

		pxe_menu.append(pmenu)
		update_pxe_menu.append(pmenu)

	def ipFormatChk(self, ip_str):
	    # copy from http://bytes.com/topic/python/answers/569207-how-validate-ip-address-python
	    #pattern = r"\b(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b"

	    pattern = re.compile(r"""
	    \b                                           # matches the beginning of the string
	    (25[0-5]|                                    # matches the integer range 250-255 OR
	    2[0-4][0-9]|                                 # matches the integer range 200-249 OR
	    [01]?[0-9][0-9]?)                            # matches any other combination of 1-3 digits below 200
	    \.                                           # matches '.'
	    (25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)       # repeat
	    \.                                           # matches '.'
	    (25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)       # repeat
	    \.                                           # matches '.'
	    (25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)       # repeat
	    \b                                           # matches the end of the string
	    """, re.VERBOSE)

	    if re.match(pattern, ip_str):
		return True
	    else:
		return False

	def collect_drbl_hosts(self):
	    drbl_cmd = "/opt/drbl/bin/get-client-ip-list"
	    del drbl_hosts[0:]
	    drbl_hosts.append([True, "ALL", ""])
	    for ip in os.popen(drbl_cmd).readlines():
		ip = ip[:-1]
		if self.ipFormatChk(ip) == True:
		    client=[True, ip, ""]
		    drbl_hosts.append(client)

	def get_host(self):
	    client = []
	    for c in drbl_hosts:
		if c[0] == True:
		    client.append(c[1])
	    return client

	def get_host_option(self):
	    host_options = ""
	    clients = self.get_host()
	    action_host = ""
	    for h in clients:
		if h == "ALL":
			break
		else:
		    action_host = action_host + " " + h
		
	    if action_host == "":
		host_options = "-nl"
	    else:
		host_options = "-h \" %s \"" % action_host
	    return host_options

	def list_user(self, box):
	    self.collect_user_list()
	    #liststore = gtk.ListStore(gobject.TYPE_BOOLEAN, gobject.TYPE_STRING, gobject.TYPE_STRING)
	    liststore = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_STRING)
	    treeview = gtk.TreeView(liststore)
	    treeview.set_rules_hint(True)
	    treeview.get_selection().set_mode(gtk.SELECTION_NONE)

	    scroll = gtk.ScrolledWindow()
	    scroll.add(treeview)
	    scroll.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
	    scroll.set_shadow_type(gtk.SHADOW_IN)

	    #render = gtk.CellRendererToggle()
	    #render.set_property('activatable', True)
	    #render.set_property('width', 20)
	    #render.connect ('toggled', self.on_toggled_pxe_menu, liststore)
	    #col = gtk.TreeViewColumn()
	    #col.pack_start(render)
	    #col.set_attributes(render, active=0)
	    #treeview.append_column(col)

	    column_name = gtk.TreeViewColumn('Name')
	    column_group = gtk.TreeViewColumn('Group')
	    treeview.append_column(column_name)	
	    treeview.append_column(column_group)	
	    cell_name = gtk.CellRendererText()
	    cell_group = gtk.CellRendererText()

	    column_name.pack_start(cell_name, True)
	    column_group.pack_start(cell_group, True)

	    column_name.set_attributes(cell_name, text=0)
	    column_group.set_attributes(cell_group, text=1)

	    for userx in user_list:
		view_user_data = [userx[1], userx[4]]
		liststore.append(view_user_data)

	    treeview.set_search_column(0)
	    column_name.set_sort_column_id(0)
	    column_group.set_sort_column_id(1)
	    #treeview.set_reorderable(True)

	    #box.pack_start(treeview, False, False, 0)
	    treeview.show()
	    box.pack_start(scroll, True, True, 0)
	    scroll.show()
    
	def list_pxe_menu(self, box):

	    liststore = gtk.ListStore(gobject.TYPE_BOOLEAN, gobject.TYPE_STRING, gobject.TYPE_STRING)
	    treeview = gtk.TreeView(liststore)
	    treeview.set_rules_hint(True)
	    treeview.get_selection().set_mode(gtk.SELECTION_NONE)

	    scroll = gtk.ScrolledWindow()
	    scroll.add(treeview)
	    scroll.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
	    scroll.set_shadow_type(gtk.SHADOW_IN)

	    render = gtk.CellRendererToggle()
	    render.set_property('activatable', True)
	    render.set_property('width', 20)
	    render.connect ('toggled', self.on_toggled_pxe_menu, liststore)
	    col = gtk.TreeViewColumn()
	    col.pack_start(render)
	    col.set_attributes(render, active=0)
	    treeview.append_column(col)

	    column_menu = gtk.TreeViewColumn('MENU')
	    column_status = gtk.TreeViewColumn('STATUS')
	    treeview.append_column(column_menu)	
	    treeview.append_column(column_status)	
	    cell_menu = gtk.CellRendererText()
	    cell_status = gtk.CellRendererText()

	    column_menu.pack_start(cell_menu, True)
	    column_status.pack_start(cell_status, True)

	    column_menu.set_attributes(cell_menu, text=1)
	    column_status.set_attributes(cell_status, text=2)

	    self.collect_pxe_menu()

	    for menu in pxe_menu:
		liststore.append(menu)

	    treeview.set_search_column(0)
	    column_menu.set_sort_column_id(0)
	    treeview.set_reorderable(True)

	    #box.pack_start(treeview, False, False, 0)
	    treeview.show()
	    box.pack_start(scroll, True, True, 0)
	    scroll.show()
	
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
	
	def on_toggled_bg_mode(self, render, mode):
	    pxe_bg_mode = mode

	def on_toggled_pxe_menu(self, render, path, list):
	    it = list.get_iter_from_string(path)
	    value, menu = list.get(it, 0, 1)
	    value = not value
	    i = 0
	    list.set(it, 0, value)
	    for all_toggle, all_menu, all_desc in update_pxe_menu:
		if menu == all_menu:
		    update_pxe_menu[i][0] = value
		    print "update %s" % update_pxe_menu[i][1]
		i = i+1

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
	    name = _(_("Diskless Remote Boot in Linux (DRBL)"))
	    _about.set_name(name)
	    _about.set_logo(gtk.gdk.pixbuf_new_from_file("drbl.png"))		
	    _about.set_authors([
		'Steven  <steven@nchc.org.tw>',
		'Thomas  <thomas@nchc.org.tw>',
		'Ceasar  <ceasar@nchc.org.tw>',
		'Jazz    <jazz@nchc.org.tw>'
		])
	    _about.set_copyright('Copyright (C) 2010 by DRBL/Clonezilla project')
	    _about.set_license('GNU General Public License V2')
	    _about.set_comments(_("Thanks for donate from Hualien county government"))
	    _about.set_website("http://drbl.name")
	    _about.run()
	    _about.destroy()

	def drblsrv_i(self, widget):
	    ## Install DRBL and related packages by drblsrv -i bla bla
	    todo_desc = _("""
	    Start to install DRBL and related packages by drblsrv
	    Please check all option here:
	    """)
	    action = "drblsrv_i"
	    opt_value["drblsrv"] = opt_value_def["drblsrv"].copy()
	    self.main_box.hide()
	    self.main_box = gtk.VBox(False,0)
	    self.main_box.show()
	    label = gtk.Label(todo_desc)
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
	    apply_button = gtk.Button(_("Apply"))
	    apply_button.set_size_request(80, 35)
	    id = apply_button.connect("clicked", self.do_apply, action)

	    cancel_button = gtk.Button(_("Cancel"))
	    cancel_button.set_size_request(80, 35)
	    id = cancel_button.connect("clicked", self.do_cancel)
	    
	    reset_button = gtk.Button(_("Reset"))
	    reset_button.set_size_request(80, 35)
	    id = reset_button.connect("clicked", self.drblsrv_i)

	    action_box.pack_end(apply_button, False, False, 0)
	    action_box.pack_end(cancel_button, False, False, 0)
	    action_box.pack_end(reset_button, False, False, 0)
	    cancel_button.show()
	    apply_button.show()
	    reset_button.show()
	    box.pack_end(action_box, False, False, 2)
	    action_box.show()

	    self.main_box.pack_start(box, True, True, 0)
	    box.show()
	    
	    self.box.pack_start(self.main_box, True, True, 0)
	    self.main_box.show()
	    self.box.show()
	    
	def drblassistant(self, widget):
	    ## The assistant for drbl user
	    drbl_assistant.assistant()

	def drblsrv_u(self, widget):
	    ## Uninstall DRBL
	    todo_desc = _("""
	    Uninstall DRBL and data by drblsrv -u
	    Please check all option here:
	    """)
	    action = "drblsrv_u"
	    self.main_box.hide()
	    self.main_box = gtk.VBox(False,0)
	    self.main_box.show()

	    label = gtk.Label(todo_desc)
	    label.set_alignment(0, 0)
	    self.main_box.pack_start(label, False, False, 0)
	    label.show()

	    option_box = gtk.VBox()
	    for option in drblsrv_u_options:
		_button = gtk.CheckButton(drblsrv_u_option_desc[option])
		if drblsrv_u_options[option] == "y":
		    _button.set_active(True)
		else:
		    _button.set_active(False)
		_button.connect("clicked", self.set_option, option, action)
		option_box.pack_start(_button, False, False, 0)
	    self.main_box.pack_start(option_box, False, False, 0)
	    option_box.show_all()

	    action_box = gtk.HBox()
	    apply_button = gtk.Button(_("Apply"))
	    apply_button.set_size_request(80, 35)
	    id = apply_button.connect(_("clicked"), self.do_apply, action)

	    cancel_button = gtk.Button(_("Cancel"))
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
	    ## Setup and Confige DRBL environment with drblpush bla bla...
	    todo_desc = _("""
	    Start to config drbl environment with drblpush
	    Please check all option here:
	    """)
	    action = "drblpush"
	    opt_value["drblpush"] = opt_value_def["drblpush"].copy()
	    self.main_box.hide()
	    self.main_box = gtk.VBox(False,0)
	    self.main_box.show()
	    label = gtk.Label(todo_desc)
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
	    apply_button = gtk.Button(_("Apply"))
	    apply_button.set_size_request(80, 35)
	    id = apply_button.connect("clicked", self.do_apply, action)

	    lazy_button = gtk.Button("Lazy Apply")
	    lazy_button.set_size_request(80, 35)
	    id = lazy_button.connect("clicked", self.do_apply, "lazypush")

	    cancel_button = gtk.Button(_("Cancel"))
	    cancel_button.set_size_request(80, 35)
	    id = cancel_button.connect("clicked", self.do_cancel)
	    
	    reset_button = gtk.Button(_("Reset"))
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
	    box.pack_end(action_box, False, False, 2)
	    action_box.show()

	    self.main_box.pack_start(box, True, True, 0)
	    box.show()
	    
	    self.box.pack_start(self.main_box, True, True, 0)
	    self.main_box.show()
	    self.box.show()

	def action_for_user(self, widget, action):
	    if action == "userlist":
		## list nis user
		todo_desc = "\n            DRBL User List:\n"
	    elif action == "useradd":
		## add user
		todo_desc = "\n            DRBL User add:\n"
		desc_of_single = _("""
    generate a single user <username> with group <groupname>
		""")
		desc_of_range = _("""
    generate a range of users from <prefix><start> to <prefix><end> with group <groupname>,
    passwd_opt:
    If one digit, it's the length of randomly created password.
    If blank, it will be randomly generated with some (say:8) characters.
    Other setting is the password itself.
    """)

	    elif action == "userdel":
		## del user
		todo_desc = "\n            DRBL User Delete:\n"
		desc_of_single = _("""
    delete a single user <username> with group <groupname>
		""")
		desc_of_range = _("""
    delete a range of users from <prefix><start> to <prefix><end> with group <groupname>,
    """)


	    self.main_box.hide()
	    self.main_box = gtk.VBox(False,0)
	    self.main_box.show()
	    label = gtk.Label(todo_desc)
	    label.set_alignment(0, 0)
	    self.main_box.pack_start(label, False, False, 0)
	    label.show()

	    box = gtk.VBox()
	    if action == "userlist":
		self.list_user(box)
	    else:
		mode_box = gtk.VBox()
		## add single user
		su_box = gtk.HBox()
		single_label = gtk.Label(desc_of_single)
		single_label.set_alignment(0, 0)
		mode_box.pack_start(single_label, False, False, 0)
		single_label.show()
		
		tlabel = gtk.Label("    ")
		ulabel = gtk.Label("Name: ")
		glabel = gtk.Label("Group: ")
		self.uentry = uname_entry = gtk.Entry()
		self.gentry = gname_entry = gtk.Entry()
		su_box.pack_start(tlabel, False, False, 0)
		su_box.pack_start(ulabel, False, False, 0)
		su_box.pack_start(uname_entry, False, False, 0)
		su_box.pack_start(glabel, False, False, 0)
		su_box.pack_start(gname_entry, False, False, 0)
		tlabel.show()
		ulabel.show()
		uname_entry.show()
		glabel.show()
		gname_entry.show()
		mode_box.pack_start(su_box, False, False, 2)
		su_box.show()

		## add range user
		su_box = gtk.VBox()
		range_label = gtk.Label(desc_of_range)
		mode_box.pack_start(range_label, False, False, 0)
		range_label.show()

		entry_box = gtk.HBox()
		tlabel = gtk.Label("    ")
		prefix_label = gtk.Label("prefix: ")
		self.prefix = gtk.Entry()
		entry_box.pack_start(tlabel, False, False, 0)
		entry_box.pack_start(prefix_label, False, False, 0)
		entry_box.pack_start(self.prefix, False, False, 0)
		tlabel.show()
		prefix_label.show()
		self.prefix.show()
		su_box.pack_start(entry_box, False, False, 0)
		entry_box.show()

		entry_box = gtk.HBox()
		tlabel = gtk.Label("    ")
		start_label = gtk.Label("start: ")
		self.start = gtk.Entry()
		entry_box.pack_start(tlabel, False, False, 0)
		entry_box.pack_start(start_label, False, False, 0)
		entry_box.pack_start(self.start, False, False, 0)
		tlabel.show()
		start_label.show()
		self.start.show()
		su_box.pack_start(entry_box, False, False, 0)
		entry_box.show()

		entry_box = gtk.HBox()
		tlabel = gtk.Label("    ")
		end_label = gtk.Label("end: ")
		self.end = gtk.Entry()
		entry_box.pack_start(tlabel, False, False, 0)
		entry_box.pack_start(end_label, False, False, 0)
		entry_box.pack_start(self.end, False, False, 0)
		tlabel.show()
		end_label.show()
		self.end.show()
		su_box.pack_start(entry_box, False, False, 0)
		entry_box.show()

		entry_box = gtk.HBox()
		tlabel = gtk.Label("    ")
		group_label = gtk.Label("group: ")
		self.group = gtk.Entry()
		entry_box.pack_start(tlabel, False, False, 0)
		entry_box.pack_start(group_label, False, False, 0)
		entry_box.pack_start(self.group, False, False, 0)
		tlabel.show()
		group_label.show()
		self.group.show()
		su_box.pack_start(entry_box, False, False, 0)
		entry_box.show()

		self.password = gtk.Entry()
		if action == "useradd":
		    entry_box = gtk.HBox()
		    tlabel = gtk.Label("    ")
		    password_label = gtk.Label("password: ")
		    entry_box.pack_start(tlabel, False, False, 0)
		    entry_box.pack_start(password_label, False, False, 0)
		    entry_box.pack_start(self.password, False, False, 0)
		    tlabel.show()
		    password_label.show()
		    self.password.show()
		    su_box.pack_start(entry_box, False, False, 0)
		    entry_box.show()

		mode_box.pack_start(su_box, False, False, 2)
		su_box.show()
		
		box.pack_start(mode_box, False, False, 2)
		mode_box.show()


	    if action != "userlist":
		action_box = gtk.HBox()
		apply_button = gtk.Button(_("Apply"))
		apply_button.set_size_request(80, 35)
		id = apply_button.connect("clicked", self.do_apply, action)

		cancel_button = gtk.Button(_("Cancel"))
		cancel_button.set_size_request(80, 35)
		id = cancel_button.connect("clicked", self.do_cancel)
		
		reset_button = gtk.Button(_("Reset"))
		reset_button.set_size_request(80, 35)
		id = reset_button.connect("clicked", self.action_for_user, action)

		action_box.pack_end(apply_button, False, False, 0)
		action_box.pack_end(cancel_button, False, False, 0)
		action_box.pack_end(reset_button, False, False, 0)
		apply_button.show()
		cancel_button.show()
		reset_button.show()
		box.pack_end(action_box, False, False, 2)
		action_box.show()

	    self.main_box.pack_start(box, True, True, 0)
	    box.show()

	    self.box.pack_start(self.main_box, True, True, 0)
	    self.main_box.show()
	    self.box.show()

	def action_for_pxe_bg_mode(self, widget, action):
	    ## change pxe menu to text or graphic mode
	    todo_desc = _("""
	    To set the default PXE client menu:
	    Please check all option here:
	    """)
	    self.main_box.hide()
	    self.main_box = gtk.VBox(False,0)
	    self.main_box.show()
	    label = gtk.Label(todo_desc)
	    label.set_alignment(0, 0)
	    self.main_box.pack_start(label, False, False, 0)
	    label.show()

	    mode_box = gtk.HBox()
	    label = gtk.Label("Select menu mode: ")
	    text_button = gtk.RadioButton(None, "text")
   	    text_button.connect("toggled", self.on_toggled_bg_mode, "text")
	    gra_button = gtk.RadioButton(text_button, "graphic")
   	    gra_button.connect("toggled", self.on_toggled_bg_mode, "graphic")
            gra_button.set_active(True)
	    mode_box.pack_start(label, False, False, 0)
	    mode_box.pack_start(text_button, False, False, 0)
	    mode_box.pack_start(gra_button, False, False, 0)
	    self.main_box.pack_start(mode_box, False, False, 4)
	    mode_box.show_all()

	    box = gtk.VBox()
	    self.list_hosts(box)

	    action_box = gtk.HBox()
	    apply_button = gtk.Button(_("Apply"))
	    apply_button.set_size_request(80, 35)
	    id = apply_button.connect("clicked", self.do_apply, action)

	    cancel_button = gtk.Button(_("Cancel"))
	    cancel_button.set_size_request(80, 35)
	    id = cancel_button.connect("clicked", self.do_cancel)
	    
	    reset_button = gtk.Button(_("Reset"))
	    reset_button.set_size_request(80, 35)
	    id = reset_button.connect("clicked", self.action_for_host_mode, action)

	    action_box.pack_end(apply_button, False, False, 0)
	    action_box.pack_end(cancel_button, False, False, 0)
	    action_box.pack_end(reset_button, False, False, 0)
	    apply_button.show()
	    cancel_button.show()
	    reset_button.show()
	    box.pack_end(action_box, False, False, 2)
	    action_box.show()

	    self.main_box.pack_start(box, True, True, 0)
	    box.show()

	    self.box.pack_start(self.main_box, True, True, 0)
	    self.main_box.show()
	    self.box.show()

	def action_for_pxe_menu(self, widget, action, next):
	    ## To hide, reveal or set default PXE client menu:
	    todo_desc = _("""
	    To hide, reveal or set default PXE client menu:
	    Please check all option here:
	    """)
	    self.main_box.hide()
	    self.main_box = gtk.VBox(False,0)
	    self.main_box.show()
	    label = gtk.Label(todo_desc)
	    label.set_alignment(0, 0)
	    self.main_box.pack_start(label, False, False, 0)
	    label.show()

	    box = gtk.VBox()
	    if next == 0:
		self.list_hosts(box)
	    else:
		self.list_pxe_menu(box)

	    action_box = gtk.HBox()
	    next_button = gtk.Button(_("Next"))
	    next_button.set_size_request(80, 35)
	    id = next_button.connect("clicked", self.action_for_pxe_menu, action, 1)

	    apply_button = gtk.Button(_("Apply"))
	    apply_button.set_size_request(80, 35)
	    id = apply_button.connect("clicked", self.do_apply, action)

	    cancel_button = gtk.Button(_("Cancel"))
	    cancel_button.set_size_request(80, 35)
	    id = cancel_button.connect("clicked", self.do_cancel)
	    
	    reset_button = gtk.Button(_("Reset"))
	    reset_button.set_size_request(80, 35)
	    id = reset_button.connect("clicked", self.action_for_host_mode, action)

	    if next == 0:
		action_box.pack_end(next_button, False, False, 0)
		next_button.show()
	    else:
		action_box.pack_end(apply_button, False, False, 0)
		apply_button.show()
	    action_box.pack_end(cancel_button, False, False, 0)
	    action_box.pack_end(reset_button, False, False, 0)
	    cancel_button.show()
	    reset_button.show()
	    box.pack_end(action_box, False, False, 2)
	    action_box.show()

	    self.main_box.pack_start(box, True, True, 0)
	    box.show()

	    self.box.pack_start(self.main_box, True, True, 0)
	    self.main_box.show()
	    self.box.show()

	def action_for_host_mode(self, widget, action):
	    ## Install DRBL and related packages by drblsrv -i bla bla
	    todo_desc = "\n            %s\n" % desc_of_dcs_mode1[action]
	    self.main_box.hide()
	    self.main_box = gtk.VBox(False,0)
	    self.main_box.show()
	    label = gtk.Label(todo_desc)
	    label.set_alignment(0, 0)
	    self.main_box.pack_start(label, False, False, 0)
	    label.show()

	    box = gtk.VBox()
	    self.list_hosts(box)

	    action_box = gtk.HBox()
	    apply_button = gtk.Button(_("Apply"))
	    apply_button.set_size_request(80, 35)
	    id = apply_button.connect("clicked", self.do_apply, action)

	    cancel_button = gtk.Button(_("Cancel"))
	    cancel_button.set_size_request(80, 35)
	    id = cancel_button.connect("clicked", self.do_cancel)
	    
	    reset_button = gtk.Button(_("Reset"))
	    reset_button.set_size_request(80, 35)
	    id = reset_button.connect("clicked", self.action_for_host_mode, action)

	    action_box.pack_end(apply_button, False, False, 0)
	    action_box.pack_end(cancel_button, False, False, 0)
	    action_box.pack_end(reset_button, False, False, 0)
	    cancel_button.show()
	    apply_button.show()
	    reset_button.show()
	    box.pack_end(action_box, False, False, 2)
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
	    self.action_for_pxe_menu(self, action, 0)

	def drbl_boot_switch_pxe_bg_mode(self, widget):
	    action = "boot_switch_pxe_bg_mode"
	    self.action_for_pxe_bg_mode(self, action)

	def drbl_user_useradd(self, widget):
	    action = "useradd"
	    self.action_for_user(self, action)

	def drbl_user_userdel(self, widget):
	    action = "userdel"
	    self.action_for_user(self, action)

	def drbl_user_userlist(self, widget):
	    action = "userlist"
	    self.action_for_user(self, action)

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

	    elif action == "drblsrv_u":
		if widget.get_active() == True:
		    drblsrv_u_options[short_option] = "y\ny"
		elif widget.get_active() == False:
		    drblsrv_u_options[short_option] = "n"

	def do_apply(self, widget, action):
	    print action

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
		run_cmd = "%s -u %s << 'EOF'\n%s\n%s\nEOF" % (drblsrv_cmd, option_str, drblsrv_u_options["Dist"], drblsrv_u_options["DRBL"])
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
		dcs_options = ""
		dcs_options = "%s %s" % (dcs_options, self.get_host_option())
	
		run_cmd = "%s %s %s" % (dcs_cmd, dcs_options, action)
	    elif action == "boot_switch_pxe_menu":

		reveal_img = []
		hide_img = []
		clients = []
		hide_options = ""
		reveal_options = ""
		run_cmd_reveal = ""
		run_cmd_hide = ""
		dcs_options = ""
		dcs_options = "%s %s" % (dcs_options, self.get_host_option())
		for st, menu, desc in update_pxe_menu:
		    if st == True:
			reveal_img.append(menu)
		    else:
			hide_img.append(menu)
		
		if len(reveal_img) > 0:
		    reveal_options = " -i ".join(reveal_img)
		    reveal_options = "%s reveal" % reveal_options
		    reveal_options = "' -i " + reveal_options + "'"
		    run_cmd_reveal = "%s %s more %s %s " % (dcs_cmd, dcs_options, pxe_cmd, reveal_options)
		if len(hide_img) > 0:
		    hide_options = " -i ".join(hide_img)
		    hide_options = "%s hide" % hide_options
		    hide_options = "'-i " + hide_options + "'"
		    run_cmd_hide = "%s %s more %s %s " % (dcs_cmd, dcs_options, pxe_cmd, hide_options)

		#dcs -nl more switch-pxe-menu '-i drbl reveal'
		run_cmd = "%s; %s" % (run_cmd_reveal, run_cmd_hide)

	    elif action == "boot_switch_pxe_bg_mode":
		dcs_options = ""
		dcs_options = "%s %s" % (dcs_options, self.get_host_option())
		run_cmd = "%s %s more %s %s " % (dcs_cmd, dcs_options, pxe_bg_cmd, pxe_bg_mode)

	    elif action == "useradd" or action == "userdel":
		name = self.uentry.get_text()
		group = self.gentry.get_text()
		prefix = self.prefix.get_text()
		start = self.start.get_text()
		end = self.end.get_text()
		rgroup = self.group.get_text()
		password = self.password.get_text()
		hash_password = ""
		remove_home = "y"
		remove_all_group = "y"
		set_continue = "y"
		if name != "":
		    print (name, group)
		    if group == "":
			group = name
		    if action == "useradd":
			run_cmd = "%s -s %s %s <<\'EOF\'\n%s\nEOF\n" % (user_add_cmd, name, group, hash_password)
		    elif action == "userdel":
			run_cmd = "%s -s %s %s <<\'EOF\'\n%s\nEOF\n" % (user_del_cmd, name, group, remove_home)

		elif prefix != "" and start !="" and end != "":
		    if password == "":
			password = 8
		    print (prefix, start, end, rgroup, password)
		    if action == "useradd":
			run_cmd = "%s -r %s %s %s %s %s" % (user_add_cmd, prefix, start, end, rgroup, password)
		    elif action == "userdel":
			run_cmd = "%s -r %s %s %s %s <<\'EOF\'\n%s\n%s\nEOF\n" % (user_del_cmd, prefix, start, end, rgroup, remove_home, remove_all_group)
		elif prefix == "" and start == "" and  end == "" and rgroup != "" and action == "userdel":
			run_cmd = "%s -g %s <<\'EOF\'\n%s\n%s\n%s\nEOF\n" % (user_del_cmd, rgroup, set_continue, remove_home, remove_all_group)
		else:
		    run_cmd = "exit\n"
		    print "not impliement."
	    else:
		run_cmd = "exit\n"
		print "not impliement."

	    close_cmd = "exit\n"
	    print run_cmd

	    self.main_box.hide()
	    self.main_box = gtk.VBox(False,0)
	    self.main_box.show()

	    apply_box = gtk.VBox()
	    try:
		display_cmd,other = run_cmd.split("\n", 1)
	    except:
		display_cmd = run_cmd
	    desc = "\nStart appling your action:\n%s \nPlease Wait...\n" % display_cmd
	    label = gtk.Label(desc)
	    label.set_alignment(0, 0)
	    apply_box.pack_start(label, False, False, 0)
	    label.show()

	    run_in_terminal = True
	    if run_in_terminal == True:
		## Terminal
		self.vterm = vte.Terminal()
		self.vterm.set_size(10,20)
		self.vterm.fork_command()
		self.vterm.feed_child(run_cmd+'\n')
		self.vterm.feed_child(close_cmd+'\n')
		self.vterm.connect('child-exited', self.do_complete)
		apply_box.pack_start(self.vterm,False,False,0)
		self.vterm.show()
	    
	    action_box = gtk.HBox()
	    abort_button = gtk.Button(_("Abort"))
	    finish_button = gtk.Button(_("Finish"))
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

	    ## branch for hualien
	    hualien_msg = _("Thanks donate from Hualien county government")
	    label = gtk.Label(hualien_msg)
	    fontdesc = pango.FontDescription("Purisa 16")
	    label.modify_font(fontdesc)

	    bg_box = gtk.VBox(False, 0)
	    bg_box.pack_start(DRBL_BG_image, False, False, 0)
	    DRBL_BG_image.show()
	    self.main_box.pack_start(label, False, False, 20)
	    label.show()
	    self.main_box.pack_end(bg_box, False, False, 0)
	    bg_box.show()

	    self.box.pack_end(self.main_box, True, True, 0)
	    self.main_box.show()
	    self.box.show()

	def do_complete(self, widget):
	    self.vterm.feed("\nFinish!\n")
	    
if __name__ == '__main__':
	DRBL_GUI_Template()
 	gtk.main()

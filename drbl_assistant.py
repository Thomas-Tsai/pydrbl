import gettext
import locale
import gobject
import string
import gtk
import os
import time
import re
import sys
from threading import Thread
import subprocess
try:
    import apt
    import aptsources
    from aptsources.sourceslist import SourcesList
    import aptsources.distro
except:
    print >> sys.stderr, "Can't import python apt"
gtk.gdk.threads_init()
collected_mac = []

drbl_etc_path = "/etc/drbl/"
template_push_conf = {
    "domain" : "drbl.name",
    "nisdomain" : "penguinzilla",
    "localswapfile" : "yes",
    "client_init" : "graphic",
    "login_gdm_opt" : "login",
    "timed_login_time" : "",
    "maxswapsize" : "128",
    "ocs_img_repo_dir" : "/home/partimag",
    "create_account" : "",
    "account_passwd_length" : "8",
    "hostname" : "ubuntu",
    "purge_client" : "no",
    "client_autologin_passwd" : "",
    "client_root_passwd" : "",
    "client_pxelinux_passwd" : "",
    "set_client_system_select" : "yes",
    "use_graphic_pxelinux_menu" : "yes",
    "set_DBN_client_audio_plugdev" : "yes",
    "open_thin_client_option" : "no",
    "client_system_boot_timeout" : "70",
    "language" : "en_US.UTF-8",
    "set_client_public_ip_opt" : "no",
    "config_file" : "drblpush.conf",
    "live_client_cpu_mode" : "i686",
    "drbl_server_as_NAT_server" : "yes",
    "add_start_drbl_services_after_cfg" : "yes",
    "continue_with_one_port" : "",
    #"clonezilla_mode" : "full_clonezilla_mode", "clonezilla_box_mode", "clonezilla_live_mode" or "none
    #"drbl_mode" : "full_drbl_mode",  "drbl_ssi_mode" or "none"

    #"collect_mac" : "no",
    #"total_client_no" : "12"
}
APP_NAME="drbl_ui"

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



## Class for DRBL Setup Assistant

class collect(Thread):

    def __init__(self, dev, mac_list):
	Thread.__init__(self)
	self.dev = dev
	self.stop = 0
	self.mac_list = mac_list

    def run(self):
	cmd = "/usr/sbin/tcpdump -tel -c 1 -i %s broadcast and port bootpc" % self.dev
	while True:
	    if self.stop == 1:
		break;
	    self.p = subprocess.Popen(cmd, executable="/bin/bash", shell=True, stdout=subprocess.PIPE)
	    data = self.p.communicate()[0]
	    if data != "":
		(mac, other) = data.split(" ", 1)
		gobject.idle_add(self.update_mac, mac)

    def update_mac(self, mac_addr):

	if mac_addr in collected_mac:
	    return
	else:
	    collected_mac.append(mac_addr)
	    self.mac_list.append([mac_addr])


    def kill(self):
	self.stop = 1
	self.p.kill()
	time.sleep(1)

class collectmac():
    def __init__(self, dev):
	self.dev = dev
	self.go = 1
	self.p = 0
	# window
	window = gtk.Window(gtk.WINDOW_TOPLEVEL)
	self.window = window
	window.set_title("DRBL - Collect MAC Address")
	window.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#FFFFFF"))
	window.set_size_request(500, 400)
	window.connect('delete-event', self.exit_collectmac)
	vbox = gtk.VBox(False, 2)
	window.add(vbox)
	
	tree = gtk.TreeView()
	scroll = gtk.ScrolledWindow()
	scroll.add(tree)
	scroll.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
	scroll.set_shadow_type(gtk.SHADOW_IN)
	col = gtk.TreeViewColumn()
	render = gtk.CellRendererText()
	col.pack_start(render)
	col.set_attributes(render, text=0)
	tree.append_column(col)
	self.mac_list = mac_list = gtk.ListStore(gobject.TYPE_STRING)
        # make treeview searchable
	tree.set_search_column(0)

	# Allow drag and drop reordering of rows
	tree.set_reorderable(True)

	# thread for collect mac address
	self.thr=collect(self.dev, self.mac_list)
	self.thr.start()

	tree.set_model(self.mac_list)
	vbox.pack_start(scroll, True, True, 2)

	# buttons
	bbox = gtk.HBox()
	_button = gtk.Button(_("Start"))
	_button.set_size_request(80, 35)
	id = _button.connect("clicked", self.go_start)
	bbox.pack_start(_button, False, False, 0)

	_button = gtk.Button(_("Stop"))
	_button.set_size_request(80, 35)
	id = _button.connect("clicked", self.go_stop)
	bbox.pack_start(_button, False, False, 0)

	_button = gtk.Button(_("Reset"))
	_button.set_size_request(80, 35)
	id = _button.connect("clicked", self.go_reset)
	bbox.pack_start(_button, False, False, 0)

	_button = gtk.Button(_("Load"))
	_button.set_size_request(80, 35)
	id = _button.connect("clicked", self.go_load)
	bbox.pack_start(_button, False, False, 0)

	_button = gtk.Button(_("Save"))
	_button.set_size_request(80, 35)
	id = _button.connect("clicked", self.go_save)
	bbox.pack_start(_button, False, False, 0)

	_button = gtk.Button(_("Finish"))
	_button.set_size_request(80, 35)
	id = _button.connect("clicked", self.go_finish)
	bbox.pack_start(_button, False, False, 0)

	vbox.pack_start(bbox, False, False, 0)
	bbox.show_all()
	vbox.show_all()
	window.show_all()

    def go_start(self, widget):
	# thread for collect mac address
	self.thr=collect(self.dev, self.mac_list)
	self.thr.start()

    def go_stop(self, widget):
	self.thr.kill()
	self.thr.join()

    def go_save(self, widget):
	current_time = time.strftime("%Y_%m_%d_%H%M", time.gmtime())
	mac_fname = "mac-"+self.dev+"-"+current_time+".txt"
	# get fname
	dialog = gtk.FileChooserDialog("Open..",
	       			None,
	       			gtk.FILE_CHOOSER_ACTION_SAVE,
	       			(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
	       			 gtk.STOCK_OPEN, gtk.RESPONSE_OK))
	dialog.set_default_response(gtk.RESPONSE_OK)
	dialog.set_current_name(mac_fname)

	response = dialog.run()
	if response == gtk.RESPONSE_OK:
	    mac_fname = dialog.get_filename()

	    FILE = open(mac_fname,"w")
	    for mac_addr in collected_mac:
		FILE.write(mac_addr+'\n')
	    FILE.close()

	dialog.destroy()

    def go_reset(self, widget):
	gtk.ListStore.clear(self.mac_list)
	del collected_mac[0:]

    def go_load(self, widget):
	# Remove old
	gtk.ListStore.clear(self.mac_list)
	del collected_mac[0:]
	# get fname
	dialog = gtk.FileChooserDialog("Open..",
	       			None,
	       			gtk.FILE_CHOOSER_ACTION_OPEN,
	       			(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
	       			 gtk.STOCK_OPEN, gtk.RESPONSE_OK))
	dialog.set_default_response(gtk.RESPONSE_OK)

	response = dialog.run()
	if response == gtk.RESPONSE_OK:
	    mac_fname = dialog.get_filename()
	    FILE = open(mac_fname, "r")
	    is_addr = '([a-fA-F0-9]{2}[:|\-]?){6}'
	    for mac_addr in FILE.readlines():
		mac_addr = mac_addr[:-1]
		pattern = re.compile(is_addr)
		if re.match(pattern, mac_addr):
		    collected_mac.append(mac_addr)
		    self.mac_list.append([mac_addr])
	    FILE.close()

	dialog.destroy()

    def go_finish(self, widget):
	if self.thr.isAlive() == True:
	    self.go_stop(widget)
	#all selected mac saved on collected_mac, and autosave as file mac-ethx.txt
	path = drbl_etc_path
	fname = path+"mac-"+self.dev+".txt"
	current_time = time.strftime("%Y_%m_%d_%H%M", time.gmtime())

	if os.path.isdir(path):
	    if os.path.isfile(fname):
		backupfilename = path+"mac-"+self.dev+"-saved-"+current_time+".txt"
		os.system("/bin/cp %s %s" % (fname, backupfilename))
	    FILE = open(fname,"w")
	    for mac_addr in collected_mac:
		FILE.write(mac_addr+'\n')
	    FILE.close()
	else:
	    print "can't find path %s, try to mkdir %s to save mac file" % (path, path)
	    os.system("mkdir %s" % path)
	    FILE = open(fname,"w")
	    for mac_addr in collected_mac:
		FILE.write(mac_addr+'\n')
	    FILE.close()

	
	self.exit_collectmac(self.window, 'delete-event')

    def exit_collectmac(self, window, event):
	widget=0
	if self.thr.isAlive() == True:
	    self.go_stop(widget)
	window.destroy()

class assistant():
    ## initial step summary page
    def __init__(self):
	self.nettypebox = {}
	self.netdevbox = {}
	self.netdev = []
	self.collect_mac = "no"
	self.total_client_no = "12"
	self.r_start = {}
	self.r_total = {}
	## network[netdev] = [ip, [mac|range|uplink], start, end, file]
	self.network = {}
	self.linux_dist = ""
	self.netinst = "n"
	# window
	window = gtk.Window(gtk.WINDOW_TOPLEVEL)
	self.window = window
	window.set_title("DRBL - Setup Assistant")
	window.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#FFFFFF"))
	window.set_size_request(500, 400)
	window.connect('delete-event', self.exit_assistant)
	vbox = gtk.VBox(False, 2)
	window.add(vbox)

	hbox = gtk.HBox(False, 2)
	# Left panel
	ltree = gtk.TreeView()
	lscroll = gtk.ScrolledWindow()
	lscroll.add(ltree)
	lscroll.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
	lscroll.set_shadow_type(gtk.SHADOW_IN)
	hbox.pack_start(lscroll, False, True, 2)

	col = gtk.TreeViewColumn()
	render = gtk.CellRendererText()
	col.pack_start(render)
	col.set_attributes(render, text=0)
	ltree.append_column(col)
	steps_list = gtk.ListStore(gobject.TYPE_STRING)
	steps_list.append(['Step 0'])
	steps_list.append(['Step 1'])
	steps_list.append(['Step 2'])
	steps_list.append(['Step 3'])
	steps_list.append(['Step 4'])
	ltree.set_model(steps_list)
	self.ltree = ltree
	step = ltree.get_selection()
	step.connect('changed', self.go_stepX)

	# right panel
	self.rscroll = rscroll = gtk.ScrolledWindow()
	rscroll.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
	rscroll.set_shadow_type(gtk.SHADOW_IN)
	self.rbox = rbox = gtk.VBox()
	welcome_box = gtk.VBox()
	welcome_desc = _("""

	Welcome to Diskless Remote Boot in Linux (DRBL)
	
	Please follow the steps for DRBL Environment

	Step1: Setup the Linux Server
	
	Step2: Setup the clients
	
	Step3: Set up the file system for the client in the Server
	
	Step4: Setting up clients to use the DRBL environment
	""")
	wlabel= gtk.Label(welcome_desc)
	welcome_box.pack_start(wlabel, False, False, 0)

	start_button = gtk.Button(_("Start"))
	start_button.set_size_request(80, 35)
	id = start_button.connect("clicked", self.go_step1)
	welcome_box.pack_start(start_button, False, False, 0)
	rbox.pack_start(welcome_box, False, False, 0)
	rscroll.add_with_viewport(rbox)
	hbox.pack_start(rscroll, True, True, 2)

	vbox.pack_start(hbox, True, True, 2)
	hbox.show_all()
	window.show_all()

    def go_stepX(self, widget):
	list, it = widget.get_selected()
	stepX = list.get(it, 0)
	if stepX[0] == "Step 1":
	    self.go_step1(widget)
	elif stepX[0] == "Step 2":
	    self.go_step2(widget)
	elif stepX[0] == "Step 3":
	    self.go_step3(widget)
	elif stepX[0] == "Step 4":
	    self.go_step4(widget)

    def go_step1(self, widget):
	self.rbox = rbox = gtk.VBox()
	_desc = _("""
	Step 1: Setup the Linux Server
	""")
	label= gtk.Label(_desc)
	rbox.pack_start(label, False, False, 0)
	
	_desc = _("""
	Step 1a: Setup linux
	""")
	label= gtk.Label(_desc)
	rbox.pack_start(label, False, False, 0)
	self.show_linux_dist()
	if self.linux_dist == "Fedora":
	    if self.check_selinux() == False:
		label= gtk.Label("manual disable selinux first")
	    else:
		label= gtk.Label("selinux disabled")
	    rbox.pack_start(label, False, False, 0)

	_desc = _("""
	Step 1b: Setup Network
	""")
	label= gtk.Label(_desc)
	rbox.pack_start(label, False, False, 0)
	self.show_network()

	_button = gtk.Button(_("Config Network"))
	_button.set_size_request(80, 35)
	id = _button.connect("clicked", self.go_config_net)
	rbox.pack_start(_button, False, False, 0)
	_button = gtk.Button(_("Next"))
	_button.set_size_request(80, 35)
	id = _button.connect("clicked", self.go_step2)
	rbox.pack_start(_button, False, False, 0)
	scroll = self.rscroll
	old=scroll.get_child()
	if old != None:
	    scroll.remove(old)
	    scroll.add_with_viewport(rbox)
	rbox.show_all()


    def go_step2(self, widget):
	self.rbox = rbox = gtk.VBox()
	_desc = _("""
	Step 2: Setup the clients
	""")
	label= gtk.Label(_desc)
	rbox.pack_start(label, False, False, 0)
	
	_desc = _("""
	Step 2a: Install program "drbl"
	""")
	label= gtk.Label(_desc)
	rbox.pack_start(label, False, False, 0)
	branch = gtk.combo_box_new_text()
	branch.connect("changed", self.go_config_branch)
	rbox.pack_start(branch, False, False, 0)

	branch.append_text('stable')
	branch.append_text('testing')
	branch.append_text('unstable')

	branch.set_active(0)
	_button = gtk.Button(_("Install"))
	_button.set_size_request(80, 35)
	id = _button.connect("clicked", self.go_install_drbl)
	rbox.pack_start(_button, False, False, 0)

	_desc = _("""
	Step 2b: do drblsrv -i
	""")
	label= gtk.Label(_desc)
	rbox.pack_start(label, False, False, 0)
	label = gtk.Label("Select ARCH ")
	rbox.pack_start(label, False, False, 0)
	arch = gtk.combo_box_new_text()
	arch.connect("changed", self.go_config_arch)
	rbox.pack_start(arch, False, False, 0)

	arch.append_text('i386')
	arch.append_text('i586')
	arch.append_text('DRBL')

	arch.set_active(2)
	sopt_button = gtk.CheckButton(_("Netinstall"))
	sopt_button.connect("clicked", self.go_config_netinst)
	rbox.pack_start(sopt_button, False, False, 0)

	_button = gtk.Button(_("drblsrv -i"))
	_button.set_size_request(80, 35)
	id = _button.connect("clicked", self.go_drblsrv_i)
	rbox.pack_start(_button, False, False, 0)

	_button = gtk.Button(_("Next"))
	_button.set_size_request(80, 35)
	id = _button.connect("clicked", self.go_step3)
	rbox.pack_start(_button, False, False, 0)
	scroll = self.rscroll
	old=scroll.get_child()
	if old != None:
	    scroll.remove(old)
	    scroll.add_with_viewport(rbox)
	rbox.show_all()


    def go_step3(self, widget):
	get_uplink = "/opt/drbl/bin/get-all-nic-ip -u"
	self.rbox = rbox = gtk.VBox()
	_desc = _("""
	Step 3: Set up the file system for the client in the Server
	""")
	label= gtk.Label(_desc)
	rbox.pack_start(label, False, False, 0)
	
	label = gtk.Label(_("Select mode for DRBL "))
	rbox.pack_start(label, False, False, 0)
	dmode = gtk.combo_box_new_text()
	dmode.connect("changed", self.go_config_mode, "DRBL")
	rbox.pack_start(dmode, False, False, 0)

	dmode.append_text('FULL')
	dmode.append_text('SSI')
	dmode.append_text('Disable')
	dmode.set_active(0)
	self.drbl_mode = "full_drbl_mode"

	label = gtk.Label(_("Select mode for Clonezilla"))
	rbox.pack_start(label, False, False, 0)
	cmode = gtk.combo_box_new_text()
	cmode.connect("changed", self.go_config_mode, "Clonezilla")
	rbox.pack_start(cmode, False, False, 0)

	cmode.append_text('FULL')
	cmode.append_text('SSI')
	cmode.append_text('Live')
	cmode.append_text('Disable')
	cmode.set_active(0)
	self.clonezilla_mode = "full_clonezilla_mode"

	nbox = gtk.VBox()
	#collect dev and uplink
	netdev = self.netdev
	if len(netdev) == 0:
	    get_network = './get-nic-devs'
	    for dev in os.popen(get_network).readlines():
		dev = dev[:-1]
		netdev.append(dev)
		## self.network[netdev] = [ip, [mac|range], start, end, file]
		get_ip = "ifconfig %s | grep -A1 %s | grep -v %s | grep \"inet addr\" | sed -e \'s/^.*inet addr:\([0-9\.]\+\).*$/\\1/\'" % (dev, dev, dev)
		ip = os.popen(get_ip).readlines()
		if len(ip) == 1:
		    ip = ip[0][:-1]
		else:
		    ip = "NONE"
		self.network[dev] = [ip, "", "", "", ""]
	    
	get_uplink = "LC_ALL=C route -n | awk '/^0.0.0.0/ {print $8}' | sort | head -n 1"
	uplink_dev = os.popen(get_uplink).readlines()[0][:-1]
	for dev in netdev:
	    self.netdevbox[dev] = devbox = gtk.HBox()
	    typebox = gtk.HBox()
	    self.nettypebox[dev] = typebox
	    label = gtk.Label(dev)
	    devbox.pack_start(label, False, False, 0)
	    
	    devtype = gtk.combo_box_new_text()
	    devtype.connect("changed", self.go_config_devtype, dev)
	    devbox.pack_start(devtype, False, False, 0)
	    devtype.append_text('mac')
	    devtype.append_text('range')
	    devtype.append_text('uplink')
	    if dev == uplink_dev:
		devtype.set_active(2)
		self.network[dev][1] = "uplink"
	    devbox.pack_start(typebox, False, False, 0)
	    nbox.pack_start(devbox, False, False, 0)


	rbox.pack_start(nbox, False, False, 0)

	sopt_button = gtk.Button(_("drblpush"))
	id = sopt_button.connect("clicked", self.go_drblpush)
	rbox.pack_start(sopt_button, False, False, 0)

	_button = gtk.Button(_("Next"))
	_button.set_size_request(80, 35)
	id = _button.connect("clicked", self.go_step4)
	rbox.pack_start(_button, False, False, 0)
	scroll = self.rscroll
	old=scroll.get_child()
	if old != None:
	    scroll.remove(old)
	    scroll.add_with_viewport(rbox)
	rbox.show_all()

    def go_step4(self, widget):
	self.rbox = rbox = gtk.VBox()
	_desc = _("""
	Step 4: Setting up clients to use the DRBL""")
	label= gtk.Label(_desc)
	rbox.pack_start(label, False, False, 0)

	step4_desc = _("""
	The client has a PXE network interface card

	  * Set the client's BIOS to boot from "LAN" or "network".

	  * Take one of the Asus motherboards for example,

	      1. You will see OnBoard LAN, there is a subfuncton 
		 "OnBoard LAN BOOT ROM", normally it's disabled, 
		 you have to enable it.
	      2. Usually you have to reboot it now, make the 
		 function re-read by BIOS.
	      3. After rebooting, enter BIOS setting again, this time, 
		 you have to make LAN boot as the 1st boot device.

	The client do not support PXE network interface card
	Please check http://drbl.sourceforge.net

	That's it. Let client boot and enjoy DRBL!!!""")
	
	label= gtk.Label(step4_desc)
	rbox.pack_start(label, False, False, 0)
	_button = gtk.Button("Finish")
	_button.set_size_request(80, 35)
	id = _button.connect("clicked", self.exit_assistant, self.window)
	rbox.pack_start(_button, False, False, 0)
	scroll = self.rscroll
	old=scroll.get_child()
	if old != None:
	    scroll.remove(old)
	    scroll.add_with_viewport(rbox)
	rbox.show_all()

    def get_linux_dist(self):
	lsb = os.popen("lsb_release -is").readlines()
	issue = os.popen("cat /etc/issue").readlines()
	if len(lsb) > 0:
	    self.linux_dist = lsb[0][:-1]
	elif len(issue) > 0:
	    linux_dist_str = issue[0][:-1]
	    self.linux_dist, other = linux_dist_str.split(" ", 1)
	else:
	    self.linux_dist = "not support"
	return self.linux_dist

    def show_linux_dist(self):
	self.linux_dist = self.get_linux_dist()
	_desc = "Linux Distribution: %s" % self.linux_dist
	label= gtk.Label(_desc)
	self.rbox.pack_start(label, False, False, 0)

    def show_network(self):
	get_network = './get-nic-devs'
	for netdev in os.popen(get_network).readlines():
	    netdev = netdev[:-1]
	    has_dev = "no"
	    for already_dev in self.netdev:
		if already_dev == netdev:
		    has_dev = "yes"
	    if has_dev == "no":
		self.netdev.append(netdev)
	    get_ip = "ifconfig %s | grep -A1 %s | grep -v %s | grep \"inet addr\" | sed -e \'s/^.*inet addr:\([0-9\.]\+\).*$/\\1/\'" % (netdev, netdev, netdev)
	    ip = os.popen(get_ip).readlines()
	    if len(ip) == 1:
		ip = ip[0][:-1]
	    else:
		ip = "NONE"
	    _desc = "net %s: %s " % (netdev, ip)
	    label= gtk.Label(_desc)
	    self.rbox.pack_start(label, False, False, 0)
	    
	    ## self.network[netdev] = [ip, [mac|range], start, end, file]
	    self.network[netdev] = [ip, "", "", "", ""]


    def go_config_net(self, widget):
	nm = os.popen("ps ax | grep nm-applet | wc -l").readlines()[0][:-1]
	nm = string.atoi(nm)
	if nm >= 2:
	    remove_nm_msg = _("Remove NetworkManager and Install gnome-network-admin")
	    dlg = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_QUESTION, gtk.BUTTONS_YES_NO, remove_nm_msg)
	    ret = dlg.run ()
	    dlg.destroy ()
	    if ret == gtk.RESPONSE_YES:
		if self.linux_dist == "Fedora":
		    os.system('chkconfig --del NetworkManager')
		    os.system('chkconfig --del NetworkManagerDispatcher')
		    os.system('chkconfig network on')
		    os.system('yum install gnome-network-admin')
		else:
		    os.system('apt-get --purge -y remove network-manager')
		    os.system('apt-get install -y gnome-network-admin')
		os.system('network-admin')
	self.go_step1(widget)

    def go_config_branch(self, widget):
	branch = widget.get_active_text()
	if branch == "stable":
	    self.comps = ["stable"]
	elif branch == "testing":
	    self.comps = ["stable testing"]
	elif branch == "unstable":
	    self.comps = ["stable testing unstable"]

    def go_install_drbl(self, widget):
	if self.linux_dist == "":
	    self.linux_dist = self.get_linux_dist()

	if self.linux_dist == "not support":
	    return -1
	
	if self.linux_dist == "Fedora":
	    os.system('yum -y install perl-Digest-SHA1')
	    os.system('yum -y install wget')
	    os.system('rm -f GPG-KEY-DRBL')
	    os.system('wget http://drbl.nchc.org.tw/GPG-KEY-DRBL')
	    os.system('rpm --import GPG-KEY-DRBL')
	    os.system('wget http://drbl.nchc.org.tw/one4all/desktop/download/stable/RPMS/drbl-current.i386.rpm')
	    os.system('yum -y install drbl-current.i386.rpm')

	elif self.linux_dist == "Ubuntu":
	    sourceslist = SourcesList ()
	    distro = aptsources.distro.get_distro ()
	    try:
		distro.get_sources (sourceslist)
	    except:
		print "your distribution is remix release!"
		return -1
	    has_drbl_repo = 0
	    has_drbl_comps = 0
	    for source in sourceslist:
		if source.disabled == False:
		    if source.uri == "http://free.nchc.org.tw/drbl-core":
			has_drbl_repo = 1
			if source.comps == self.comps:
			    has_drbl_comps = 1
			else:
			    print "remove drbl repo"
			    sourceslist.remove(source)

	    if has_drbl_repo == 0 or has_drbl_comps == 0:
		drbl_uri = "http://free.nchc.org.tw/drbl-core"
		drbl_dist = "drbl"
		drbl_comps = self.comps
		distro.add_source (type="deb", uri=drbl_uri, dist=drbl_dist, comps=drbl_comps, comment="DRBL Repository (Add by drbl_assistant)")
		sourceslist.backup ()
		sourceslist.save ()

	    add_key_st = os.popen("wget -q http://drbl.nchc.org.tw/GPG-KEY-DRBL -O- | apt-key add -").readlines()[0][:-1]

	    try:
		cache = apt.Cache()
		pkg = cache['drbl'] # Access the Package object for python-apt
		pkg.mark_install()
		# Now, really install it
		cache.commit()
	    except:
		print "apt-get install drbl"
		os.system("apt-get update")
		os.system("apt-get install drbl")
	else:
	    print "Unknown linux"
	print "install finish"

    def check_selinux(self):
	is_selinux = os.popen("grep -v ^# /etc/sysconfig/selinux| grep disable").readlines()
	if len (is_selinux) < 1:
	    return False
	else:
	    return True
    
    def go_config_arch(self, widget):
	arch = widget.get_active()
	self.arch = arch

    def go_config_netinst(self, widget):
	if widget.get_active() == True:
	    self.netinst = "y"
	elif widget.get_active() == False:
	    self.netinst = "n"

    def go_drblsrv_i(self, widget):

	srvopt_i = "-i -x n -c n -a n -m n -t n -s -f -g n -l 0 -o 1 -k %s -n %s " % (self.arch, self.netinst)
	cmd = "yes \"\" |/opt/drbl/sbin/drblsrv %s" % srvopt_i
	os.system(cmd)

    def go_drblpush(self, widget):
	fname = "/etc/drbl/drblpush_ui.conf"
	self.generate_pushconf(fname)

	cmd = "yes \'\' | /opt/drbl/sbin/drblpush -c %s" % fname
	os.system(cmd)

    def go_config_mode(self, widget, target):
	mode = widget.get_active_text()
	if target == "DRBL":
	    if mode == "FULL":
		self.drbl_mode = "full_drbl_mode"
	    elif mode == "SSI":
		self.drbl_mode = "drbl_ssi_mode"
	    elif mode == "Disable":
		self.drbl_mode = "nonoe"
	    else:
		self.drbl_mode = "full_drbl_mode"
	elif target == "Clonezilla":
	    if mode == "FULL":
		self.clonezilla_mode = "full_clonezilla_mode"
	    elif mode == "SSI":
		self.clonezilla_mode = "clonezilla_box_mode"
	    elif mode == "LIVE":
		self.clonezilla_mode = "clonezilla_live_mode"
	    elif mode == "Disable":
		self.clonezilla_mode = "none"
	    else:
		self.clonezilla_mode = "full_clonezilla_mode"

    def go_config_devtype(self, widget, dev):
	devbox = self.netdevbox[dev]
	self.nettypebox[dev].hide()
	self.nettypebox[dev] = gtk.HBox()
	#self.nettypebox[dev].show()
	if widget.get_active_text() == "range":
	    self.collect_mac = "no"
	    self.network[dev][1] = "range"
	    label = gtk.Label("start")
	    self.nettypebox[dev].pack_start(label, False, False ,0)
	    label.show()
	    def_r_start_cmd = "/opt/drbl/bin/drbl-ipcalc %s | grep HostMin | awk {'print $2'}" % dev
	    def_r_start = os.popen(def_r_start_cmd).readlines()
	    if len(def_r_start) >= 0:
		def_r_start_ip = def_r_start[0][:-1]
	    self.r_start[dev] = start = gtk.Entry()
	    start.set_width_chars(15)
	    start.set_text(def_r_start_ip)
	    self.nettypebox[dev].pack_start(start, False, False ,0)
	    start.show()
	    label = gtk.Label("%s clients:" % dev)
	    self.nettypebox[dev].pack_start(label, False, False ,0)
	    label.show()
	    self.r_total[dev] = total = gtk.Entry()
	    total.set_width_chars(3)
	    total.set_text("12")

	    self.nettypebox[dev].pack_start(total, False, False ,0)
	    total.show()
	elif widget.get_active_text() == "mac":
	    self.collect_mac = "yes"
	    fname = drbl_etc_path+"mac-"+dev+".txt"
	    self.network[dev][4] = fname
	    self.network[dev][1] = "mac"
	    _button = gtk.Button("Collect MAC Address")
	    _button.set_size_request(80, 35)
	    id = _button.connect("clicked", self.go_CollectMacAddress, dev)
	    self.nettypebox[dev].pack_start(_button, False, False ,0)
	    _button.show()
	    label = gtk.Label("start")
	    self.nettypebox[dev].pack_start(label, False, False ,0)
	    label.show()
	    self.r_start[dev] = start = gtk.Entry()
	    start.set_width_chars(15)
	    self.nettypebox[dev].pack_start(start, False, False ,0)
	    start.show()

	elif widget.get_active_text() == "uplink":
	    self.collect_mac = "no"
	    self.network[dev][1] = "uplink"
	    label = gtk.Label("uplink")
	    self.nettypebox[dev].pack_start(label, False, False ,0)
	    label.show()
	devbox.pack_start(self.nettypebox[dev], False, False, 0)
	self.nettypebox[dev].show()
	devbox.show()

    def go_CollectMacAddress(self, widget, dev):
	collectmac(dev)

    def calculate_client_no(self):
	network = self.network
	total = 0
	for dev in network.keys():
	    dev_client_count = 0
	    if network[dev][1] == "mac":
		dev_client_count = len(collected_mac)
		network[dev][2] = self.r_start[dev].get_text()
		saddr1, saddr2, saddr3, saddr4 = network[dev][2].split(".")
		network[dev][2] = saddr4
		eaddr4 = string.atoi(saddr4) + dev_client_count -1
		network[dev][3] = "%s" % eaddr4
	    elif network[dev][1] == "range":
		network[dev][2] = self.r_start[dev].get_text()
		saddr1, saddr2, saddr3, saddr4 = network[dev][2].split(".")
		dev_client_count = string.atoi(self.r_total[dev].get_text())
		network[dev][2] = saddr4
		eaddr4 = string.atoi(saddr4) + dev_client_count -1
		network[dev][3] = "%s" % eaddr4
	    else:
		dev_client_count = 0
	    
	    total = total + dev_client_count
	    self.total_client_no = total

    def	generate_pushconf(self, fname):
	if os.path.isdir(drbl_etc_path) == False:
	    os.system("mkdir %s" % drbl_etc_path)
	FILE = open(fname, "w")
	FILE.write("#setup by ui"+'\n')
	FILE.write("[general]"+'\n')
	for data in template_push_conf.keys():
	    conf = data+'='+template_push_conf[data]
	    FILE.write(conf+'\n')
	FILE.write('clonezilla_mode='+self.clonezilla_mode+'\n')
	FILE.write('drbl_mode='+self.drbl_mode+'\n')
	FILE.write('collect_mac='+self.collect_mac+'\n')
	self.calculate_client_no()
	total_client_str = "total_client_no=%i" % self.total_client_no
	FILE.write(total_client_str+'\n')

	for dev in self.network.keys():
	    if self.network[dev][1] == "mac":
		FILE.write('\n'+'#setup for '+dev+'\n')
		FILE.write('['+dev+']'+'\n')
		FILE.write('interface='+dev+'\n')
		FILE.write('mac='+self.network[dev][4]+'\n')
		FILE.write('ip_start='+self.network[dev][2]+'\n')
	    elif self.network[dev][1] == "range":
		FILE.write('\n'+'#setup for '+dev+'\n')
		FILE.write('['+dev+']'+'\n')
		FILE.write('interface='+dev+'\n')
		FILE.write('range='+self.network[dev][2]+'-'+self.network[dev][3]+'\n')


    def exit_assistant(self, window, event):
	self.window.destroy()
	if __name__ == '__main__':
	    gtk.main_quit()
if __name__ == '__main__':
    assistant()
    gtk.main()

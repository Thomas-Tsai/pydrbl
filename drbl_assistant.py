import gettext
import locale
import gobject
import string
import gtk
import os
import apt
import aptsources
import time
import re
from aptsources.sourceslist import SourcesList
import aptsources.distro
from threading import Thread
import subprocess
gtk.gdk.threads_init()
collected_mac = []
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

## Class for DRBL Setup Assistant

class collect(Thread):

    def __init__(self, dev, mac_list):
	Thread.__init__(self)
	self.dev = dev
	self.stop = 0
	self.mac_list = mac_list
	print "thread"+dev

    def run(self):
	print "thread"
	cmd = "/usr/sbin/tcpdump -tel -c 1 -i %s broadcast and port bootpc" % self.dev
	while True:
	    if self.stop == 1:
		break;
	    self.p = subprocess.Popen(cmd, executable="/bin/bash", shell=True, stdout=subprocess.PIPE)
	    data = self.p.communicate()[0]
	    if data != "":
		(mac, other) = data.split(" ", 1)
		print (self.dev, mac)
		gobject.idle_add(self.update_mac, mac)

    def update_mac(self, mac_addr):

	if mac_addr in collected_mac:
	    print "duplicate"
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
	_button = gtk.Button("start")
	_button.set_size_request(80, 35)
	id = _button.connect("clicked", self.go_start)
	bbox.pack_start(_button, False, False, 0)

	_button = gtk.Button("stop")
	_button.set_size_request(80, 35)
	id = _button.connect("clicked", self.go_stop)
	bbox.pack_start(_button, False, False, 0)

	_button = gtk.Button("reset")
	_button.set_size_request(80, 35)
	id = _button.connect("clicked", self.go_reset)
	bbox.pack_start(_button, False, False, 0)

	_button = gtk.Button("load")
	_button.set_size_request(80, 35)
	id = _button.connect("clicked", self.go_load)
	bbox.pack_start(_button, False, False, 0)

	_button = gtk.Button("save")
	_button.set_size_request(80, 35)
	id = _button.connect("clicked", self.go_save)
	bbox.pack_start(_button, False, False, 0)

	_button = gtk.Button("finish")
	_button.set_size_request(80, 35)
	id = _button.connect("clicked", self.go_finish)
	bbox.pack_start(_button, False, False, 0)

	vbox.pack_start(bbox, False, False, 0)
	bbox.show_all()
	vbox.show_all()
	window.show_all()

    def go_start(self, widget):
	print "start"
	# thread for collect mac address
	self.thr=collect(self.dev, self.mac_list)
	self.thr.start()

    def go_stop(self, widget):
	print "stop"
	self.thr.kill()
	self.thr.join()

    def go_save(self, widget):
	print "save"
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
	    print dialog.get_filename(), 'selected'
	    mac_fname = dialog.get_filename()

	    FILE = open(mac_fname,"w")
	    for mac_addr in collected_mac:
		FILE.write(mac_addr+'\n')
	    FILE.close()


	elif response == gtk.RESPONSE_CANCEL:
	    print 'Closed, no files selected'
	dialog.destroy()

    def go_reset(self, widget):
	print "reset"
	gtk.ListStore.clear(self.mac_list)
	del collected_mac[0:]

    def go_load(self, widget):
	print "load"
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
	    print dialog.get_filename(), 'selected'
	    mac_fname = dialog.get_filename()
	    FILE = open(mac_fname, "r")
	    is_addr = '([a-fA-F0-9]{2}[:|\-]?){6}'
	    for mac_addr in FILE.readlines():
		mac_addr = mac_addr[:-1]
		print mac_addr
		pattern = re.compile(is_addr)
		if re.match(pattern, mac_addr):
		    collected_mac.append(mac_addr)
		    self.mac_list.append([mac_addr])
		else:
		    print "not match"
	    FILE.close()

	elif response == gtk.RESPONSE_CANCEL:
	    print 'Closed, no files selected'
	dialog.destroy()

    def go_finish(self, widget):
	print "finish"
	print self.thr.isAlive()
	if self.thr.isAlive() == True:
	    self.go_stop(widget)
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
	self.r_end = {}
	## network[netdev] = [ip, [mac|range|uplink], start, end, file]
	self.network = {}
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
	welcome_desc = """

	Welcome to Diskless Remote Boot in Linux (DRBL)
	
	Please follow the steps for DRBL Environment

	Step1: Setup the Linux Server
	
	Step2: Setup the clients
	
	Step3: Set up the file system for the client in the Server
	
	Step4: Setting up clients to use the DRBL environment
	"""
	wlabel= gtk.Label(welcome_desc)
	welcome_box.pack_start(wlabel, False, False, 0)

	start_button = gtk.Button("Start")
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
	print stepX[0]
	if stepX[0] == "Step 1":
	    self.go_step1(widget)
	elif stepX[0] == "Step 2":
	    self.go_step2(widget)
	elif stepX[0] == "Step 3":
	    self.go_step3(widget)
	elif stepX[0] == "Step 4":
	    self.go_step4(widget)

    def go_step1(self, widget):
	print "Step1"
	self.rbox = rbox = gtk.VBox()
	_desc = """
	Step 1: Setup the Linux Server
	"""
	label= gtk.Label(_desc)
	rbox.pack_start(label, False, False, 0)
	
	_desc = """
	Step 1a: Setup linux
	"""
	label= gtk.Label(_desc)
	rbox.pack_start(label, False, False, 0)
	self.show_linux_dist()

	_desc = """
	Step 1b: Setup Network
	"""
	label= gtk.Label(_desc)
	rbox.pack_start(label, False, False, 0)
	self.show_network()

	_button = gtk.Button("Config Network")
	_button.set_size_request(80, 35)
	id = _button.connect("clicked", self.go_config_net)
	rbox.pack_start(_button, False, False, 0)
	_button = gtk.Button("Next")
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
	print "Step2"
	self.rbox = rbox = gtk.VBox()
	_desc = """
	Step 2: Setup the clients
	"""
	label= gtk.Label(_desc)
	rbox.pack_start(label, False, False, 0)
	
	_desc = """
	Step 2a: Install program "drbl"
	"""
	label= gtk.Label(_desc)
	rbox.pack_start(label, False, False, 0)
	branch = gtk.combo_box_new_text()
	branch.connect("changed", self.go_config_branch)
	rbox.pack_start(branch, False, False, 0)

	branch.append_text('stable')
	branch.append_text('testing')
	branch.append_text('unstable')

	branch.set_active(0)
	_button = gtk.Button("Install")
	_button.set_size_request(80, 35)
	id = _button.connect("clicked", self.go_install_drbl)
	rbox.pack_start(_button, False, False, 0)

	_desc = """
	Step 2b: do drblsrv -i
	"""
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
	sopt_button = gtk.CheckButton("Netinstall")
	sopt_button.connect("clicked", self.go_config_netinst)
	rbox.pack_start(sopt_button, False, False, 0)

	_button = gtk.Button("drblsrv -i")
	_button.set_size_request(80, 35)
	id = _button.connect("clicked", self.go_drblsrv_i)
	rbox.pack_start(_button, False, False, 0)

	_button = gtk.Button("Next")
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
	get_uplink = "/opt/drbl/bin/get-all-nic-ip -u-all-nic-ip -u"
	print "Step3"
	self.rbox = rbox = gtk.VBox()
	_desc = """
	Step 3: Set up the file system for the client in the Server
	"""
	label= gtk.Label(_desc)
	rbox.pack_start(label, False, False, 0)
	
	label = gtk.Label("Select mode for DRBL ")
	rbox.pack_start(label, False, False, 0)
	dmode = gtk.combo_box_new_text()
	dmode.connect("changed", self.go_config_mode, "DRBL")
	rbox.pack_start(dmode, False, False, 0)

	dmode.append_text('FULL')
	dmode.append_text('SSI')
	dmode.append_text('Disable')
	dmode.set_active(0)
	self.drbl_mode = "full_drbl_mode"

	label = gtk.Label("Select mode for Clonezilla ")
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

	sopt_button = gtk.Button("drblpush")
	id = sopt_button.connect("clicked", self.go_drblpush)
	rbox.pack_start(sopt_button, False, False, 0)

	_button = gtk.Button("Next")
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
	print "Step4"
	self.rbox = rbox = gtk.VBox()
	_desc = """
	Step 4: 
	"""
	label= gtk.Label(_desc)
	rbox.pack_start(label, False, False, 0)
	
	_button = gtk.Button("Finish")
	_button.set_size_request(80, 35)
	id = _button.connect("clicked", self.go_step4)
	rbox.pack_start(_button, False, False, 0)
	scroll = self.rscroll
	old=scroll.get_child()
	if old != None:
	    scroll.remove(old)
	    scroll.add_with_viewport(rbox)
	rbox.show_all()

    def show_linux_dist(self):
	check_linux_dist = "lsb_release -is"
	linux_dist = os.popen(check_linux_dist).readlines()[0][:-1]
	_desc = "Linux Distribution: %s" % linux_dist
	label= gtk.Label(_desc)
	self.rbox.pack_start(label, False, False, 0)

    def show_network(self):
	get_network = './get-nic-devs'

	for netdev in os.popen(get_network).readlines():
	    netdev = netdev[:-1]
	    self.netdev.append(netdev)
	    get_ip = "ifconfig %s | grep -A1 %s | grep -v %s | grep \"inet addr\" | sed -e \'s/^.*inet addr:\([0-9\.]\+\).*$/\\1/\'" % (netdev, netdev, netdev)
	    print get_ip
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
	    os.system('apt-get install -y gnome-network-admin')
	    os.system('apt-get --purge -y remove network-manager')
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
	print "install" ,self.comps
	sourceslist = SourcesList ()
	distro = aptsources.distro.get_distro ()
	try:
            distro.get_sources (sourceslist)
	except:
	    print "your distribution is remix release!"
	    return -1
	has_drbl_repo = 0
	for source in sourceslist:
	    print source.uri
	    if source.disabled == False:
		if source.uri == "http://free.nchc.org.tw/drbl-core":
		    print "drbl source added"
		    has_drbl_repo = 1
	if has_drbl_repo == 0:
	    drbl_uri = "http://free.nchc.org.tw/drbl-core"
	    drbl_dist = "drbl"
	    drbl_comps = self.comps
	    distro.add_source (type="deb", uri=drbl_uri, dist=drbl_dist, comps=drbl_comps, comment="DRBL Repository (Add by drbl_assistant)")
	    sourceslist.backup ()
	    sourceslist.save ()

	add_key_st = os.popen("wget -q http://drbl.nchc.org.tw/GPG-KEY-DRBL -O- | apt-key add -").readlines()[0][:-1]
	print add_key_st
	try:
	    cache = apt.Cache()
	    pkg = cache['drbl'] # Access the Package object for python-apt
	    print 'drbl is trusted:', pkg.candidate.origins[0].trusted
	    pkg.mark_install()
	    print 'drbl is marked for install:', pkg.marked_install
	    print 'drbl is (summary):', pkg.candidate.summary
	    # Now, really install it
	    cache.commit()
	except:
	    print "apt-get install drbl"
	    os.system("apt-get update")
	    os.system("apt-get install drbl")
	print "install finish"

    def go_config_arch(self, widget):
	arch = widget.get_active()
	self.arch = arch

    def go_config_netinst(self, widget):
	if widget.get_active() == True:
	    self.netinst = "y"
	elif widget.get_active() == False:
	    self.netinst = "n"

    def go_drblsrv_i(self, widget):

	srvopt_i = "-i -c n -a n -g n -l 0 -o 1 -k %s -n %s " % (self.arch, self.netinst)
	print srvopt_i
	cmd = "/opt/drbl/sbin/drblsrv %s" % srvopt_i
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
	    self.r_start[dev] = start = gtk.Entry()
	    start.set_width_chars(15)
	    self.nettypebox[dev].pack_start(start, False, False ,0)
	    start.show()
	    label = gtk.Label("end")
	    self.nettypebox[dev].pack_start(label, False, False ,0)
	    label.show()
	    self.r_end[dev] = end = gtk.Entry()
	    end.set_width_chars(15)
	    self.nettypebox[dev].pack_start(end, False, False ,0)
	    end.show()
	elif widget.get_active_text() == "mac":
	    self.collect_mac = "yes"
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
	print dev
	collectmac(dev)
	#all selected mac saved on collected_mac, and autosave as file mac-ethx.txt
	path = "/etc/drbl/"
	fname = path+"mac-"+dev+".txt"

	if os.path.isdir(path):
	    if os.path.isfile(fname) and os.path.isabs(fname):
		backupfilename = "mac-"+dev+"-saved-"+current_time+".txt"
		os.system("copy %s %s" % (fname, backupfilename))
	    else:

		FILE = open(fname,"w")
		for mac_addr in collected_mac:
		    FILE.write(mac_addr+'\n')
		FILE.close()
	
    def calculate_client_no(self):
	network = self.network
	total = 0
	for dev in network.keys():
	    dev_client_count = 0
	    if network[dev][1] == "mac":
		dev_client_count = len(self.collected_mac)
		network[dev][2] = self.r_start[dev].get_text()
	    elif network[dev][1] == "range":
		network[dev][2] = self.r_start[dev].get_text()
		network[dev][3] = self.r_end[dev].get_text()
		saddr1, saddr2, saddr3, saddr4 = network[dev][2].split(".")
		eaddr1, eaddr2, eaddr3, eaddr4 = network[dev][3].split(".")
		network[dev][2] = saddr4
		network[dev][3] = eaddr4
		dev_client_count = string.atoi(eaddr4) - string.atoi(saddr4) + 1
	    else:
		dev_client_count = 0
	    
	    print dev,dev_client_count
	    total = total + dev_client_count
	    self.total_client_no = total

    def	generate_pushconf(self, fname):
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


    def exit_assistant(iself, window, event):
	window.destroy()
	if __name__ == '__main__':
	    gtk.main_quit()
if __name__ == '__main__':
    assistant()
    gtk.main()

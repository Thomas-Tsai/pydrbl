import gettext
import locale
import gobject
import string
import gtk
import os
import apt
import aptsources
from aptsources.sourceslist import SourcesList
import aptsources.distro


## Class for DRBL Setup Assistant
class collectmac():
    def __init__(self):
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
	self.collect()

	tree.set_model(mac_list)
	vbox.pack_start(scroll, True, True, 2)

	# buttons
	bbox = gtk.HBox()
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

    def collect(self, widget):
	print "collect"


    def go_save(self, widget):
	print "save"

    def go_reset(self, widget):
	print "reset"

    def go_load(self, widget):
	print "load"

    def go_finish(self, widget):
	print "finish"

    def exit_collectmac(iself, window, event):
	window.destroy()

class assistant():
    ## initial step summary page
    def __init__(self):
	self.nettypebox = {}
	self.netdevbox = {}
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


    def show_linux_dist(self):
	check_linux_dist = "lsb_release -is"
	linux_dist = os.popen(check_linux_dist).readlines()[0][:-1]
	_desc = "Linux Distribution: %s" % linux_dist
	label= gtk.Label(_desc)
	self.rbox.pack_start(label, False, False, 0)

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

	label = gtk.Label("Select mode for Clonezilla ")
	rbox.pack_start(label, False, False, 0)
	cmode = gtk.combo_box_new_text()
	cmode.connect("changed", self.go_config_mode, "Clonezilla")
	rbox.pack_start(cmode, False, False, 0)

	cmode.append_text('FULL')
	cmode.append_text('SSI')
	cmode.append_text('Disable')

	nbox = gtk.VBox()
	#collect dev and uplink
	self.netdev = netdev = ["eth0", "eth1"]
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

    def show_network(self):
	network = []
	get_network = './get-nic-devs'
	#uplink = "LC_ALL=C route -n | awk '/^0.0.0.0/ {print $8}' | sort | head -n 1"

	for netdev in os.popen(get_network).readlines():
	    netdev = netdev[:-1]
	    get_ip = "ifconfig %s | grep -A1 %s | grep -v %s | grep \"inet addr\" | sed -e \'s/^.*inet addr:\([0-9\.]\+\).*$/\\1/\'" % (netdev, netdev, netdev)
	    print get_ip
	    ip = os.popen(get_ip).readlines()
	    if len(ip) == 1:
		ip = ip[0][:-1]
	    else:
		ip = "NONE"
	    network.append([netdev, ip])
	    _desc = "net %s: %s " % (netdev, ip)
	    label= gtk.Label(_desc)
	    self.rbox.pack_start(label, False, False, 0)


    def go_config_net(self, widget):
	os.system('/usr/bin/nm-connection-editor')
	self.go_step1(widget)

    def go_config_branch(self, widget):
	branch = widget.get_active_text()
	if branch == "testing":
	    branch = "stable testing"
	elif branch == "unstable":
	    branch = "stable testing unstable"
	self.branch = branch

    def go_install_drbl(self, widget):
	print "install" ,self.branch
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
	    drbl_comps = "drbl %s" % self.branch
	    distro.add_source (type="deb", uri=drbl_uri, comps=drbl_comps, comment="DRBL Repository (Add by drbl_assistant)")
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
	cmd = "yes \'\' | /opt/drbl/sbin/drblpush -c drbluipush.conf"
	os.system(cmd)

    def go_config_mode(self, widget, target):
	if target == "DRBL":
	    self.drblmode = widget.get_active_text()
	elif target == "Clonezilla":
	    self.clonezillamode = widget.get_active_text()

    def go_config_devtype(self, widget, dev):
	devbox = self.netdevbox[dev]
	self.nettypebox[dev].hide()
	self.nettypebox[dev] = gtk.HBox()
	#self.nettypebox[dev].show()
	if widget.get_active_text() == "range":
	    print "range"
	    label = gtk.Label("start")
	    self.nettypebox[dev].pack_start(label, False, False ,0)
	    label.show()
	    self.r_start = start = gtk.Entry()
	    start.set_width_chars(3)
	    self.nettypebox[dev].pack_start(start, False, False ,0)
	    start.show()
	    label = gtk.Label("end")
	    self.nettypebox[dev].pack_start(label, False, False ,0)
	    label.show()
	    self.r_end = end = gtk.Entry()
	    end.set_width_chars(3)
	    self.nettypebox[dev].pack_start(end, False, False ,0)
	    end.show()
	elif widget.get_active_text() == "mac":
	    print "mac"
	    _button = gtk.Button("Collect MAC Address")
	    _button.set_size_request(80, 35)
	    id = _button.connect("clicked", self.go_CollectMacAddress, dev)
	    self.nettypebox[dev].pack_start(_button, False, False ,0)
	    _button.show()

	elif widget.get_active_text() == "uplink":
	    print "uplink"
	    label = gtk.Label("uplink")
	    self.nettypebox[dev].pack_start(label, False, False ,0)
	    label.show()
	devbox.pack_start(self.nettypebox[dev], False, False, 0)
	self.nettypebox[dev].show()
	devbox.show()

    def go_CollectMacAddress(self, widget, dev):
	print dev
	collectmac()
	

    def exit_assistant(iself, window, event):
	window.destroy()
	if __name__ == '__main__':
	    gtk.main_quit()
if __name__ == '__main__':
    assistant()
    gtk.main()

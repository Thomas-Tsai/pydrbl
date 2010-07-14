import gettext
import locale
import gobject
import string
import gtk
import os

## Class for DRBL Setup Assistant

class assistant():
    ## initial step summary page
    def __init__(self):
	# window
	window = gtk.Window(gtk.WINDOW_TOPLEVEL)
	self.window = window
	window.set_title("DRBL - Setup Assistant")
	window.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#FFFFFF"))
	window.set_size_request(500, 400)
	window.connect('delete-event', lambda window, event: gtk.main_quit())
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
	#step = ltree.get_selection()
	#step.connect('changed', self.on_changed)

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
	hbox.pack_start(rscroll, False, True, 2)

	vbox.pack_start(hbox, True, True, 2)
	hbox.show_all()
	window.show_all()

    def go_step1(self, widget):
	print "Step1"
	self.rbox = rbox = gtk.VBox()
	_desc = """
	Step 1:
	"""
	label= gtk.Label(_desc)
	rbox.pack_start(label, False, False, 0)
	self.rscroll.add_with_viewport(rbox)
	self.rscroll.show_all()

if __name__ == '__main__':
    assistant()
    gtk.main()

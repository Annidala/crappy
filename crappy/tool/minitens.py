# coding: utf-8
import Tkinter as tk
import ttk
from collections import OrderedDict


class MinitensFrameObjects(tk.Frame):
  def __init__(self):
    pass

  def add_button(self, **kwargs):

    widgets_dict = kwargs.pop('widgets_dict', None)
    frame = kwargs.pop('frame', None)
    name = kwargs.pop('name', 'Button')
    text = kwargs.pop('text', 'Button')
    bg = kwargs.pop('bg', 'white')
    height = kwargs.pop('height', 2)
    width = kwargs.pop('width', 10)
    command = kwargs.pop('command', None)
    command_type = kwargs.pop('command_type', 'to_serial')

    assert not kwargs, 'Error: unknown arg(s) in button definition:' + str(
      kwargs)

    if command_type is not 'to_serial':
      widgets_dict[name] = tk.Button(frame,
                                     text=text,
                                     bg=bg,
                                     relief="raised",
                                     height=height, width=width,
                                     command=command,
                                     font=("Courier bold", 11))
    else:
      widgets_dict[name] = tk.Button(frame,
                                     text=text,
                                     bg=bg,
                                     relief="raised",
                                     height=height, width=width,
                                     command=lambda: self.submit_command(
                                       command),
                                     font=("Courier bold", 11))

  def add_label(self, **kwargs):

    widgets_dict = kwargs.pop('widgets_dict', None)
    frame = kwargs.pop('frame', None)
    text = kwargs.pop('text', 'label')
    name = kwargs.pop('name', text)
    relief = kwargs.pop('relief', 'flat')
    font = kwargs.pop('font', ('Courier bold', 11))

    widgets_dict[name] = (tk.Label(frame,
                                   text=text,
                                   relief=relief,
                                   font=font))

  def add_entry(self, **kwargs):

    widgets_dict = kwargs.pop('widgets_dict', None)
    frame = kwargs.pop('frame', None)
    entry_name = kwargs.pop('entry_name', 'entry_name')
    width = kwargs.pop('width', 10)
    vartype = kwargs.pop('vartype', tk.DoubleVar())
    variable = kwargs.pop("variable", None)

    # Affect the variable associated with the entry to the self object.
    if not variable:
      setattr(self, entry_name + '_var', vartype)
      widgets_dict[entry_name] = tk.Entry(frame,
                                          textvariable=getattr(self, entry_name
                                                               + '_var'),
                                          width=width)
    else:
      widgets_dict[entry_name] = tk.Entry(frame,
                                          textvariable=variable,
                                          width=width)

  def add_checkbutton(self, **kwargs):
    widgets_dict = kwargs.pop('widgets_dict', None)
    frame = kwargs.pop('frame', None)
    name = kwargs.pop('name', 'checkbutton')
    variable_name = kwargs.pop('variable', name + '_var')

    var = tk.BooleanVar()
    setattr(self, variable_name, var)
    widgets_dict[name] = tk.Checkbutton(frame,
                                        text=None,
                                        variable=var)

  def add_combobox(self, **kwargs):

    widgets_dict = kwargs.pop("widgets_dict", None)
    frame = kwargs.pop("frame", None)
    entries = kwargs.pop("entries", None)
    name = kwargs.pop("name", "combobox")
    variable_name = kwargs.pop("variable", name + "_var")
    var = tk.StringVar()
    var.set(entries[0])
    setattr(self, variable_name, var)

    combo_box = ttk.Combobox(frame,
                             textvariable=var,
                             values=entries,
                             state='readonly')

    widgets_dict[name] = combo_box

  def add_scale(self, **kwargs):
    widgets_dict = kwargs.pop('widgets_dict', None)
    frame = kwargs.pop('frame', None)
    name = kwargs.pop('name', 'Button')
    boundaries = kwargs.pop("boundaries", (0, 1))

    widgets_dict[name] = tk.Scale(frame,
                                  from_=boundaries[0],
                                  to_=boundaries[1],
                                  orient=tk.HORIZONTAL,
                                  )


class MinitensFrame(MinitensFrameObjects):
  def __init__(self, parent, **kwargs):
    """
    Frame to use with minitens in crappy.
    """
    tk.Frame.__init__(self, parent)
    self.grid()

    self.frames = ["displayer",
                   "action",
                   "cycles"]
    for frame in self.frames:
      setattr(self, "frame_" + frame, tk.Frame(self,
                                               relief=tk.SUNKEN,
                                               borderwidth=1))
      setattr(self, frame + "_widgets", OrderedDict())

    self.variables = [("Position(mm)", "position"),
                      ("Position(%)", "position_prct"),
                      ("Effort(N)", "effort"),
                      ("Contrainte(MPa)", "contrainte")]
    self.create_widgets(**kwargs)
    self.queue = kwargs.get("queue")

    for name, default in [('speed', 0.8),
                          ('ep_length', 0),
                          ('ep_width', 0),
                          ('ep_depth', 0)]:
      setattr(self, name, tk.DoubleVar())
      getattr(self, name).set(default)
    self.submit_command({"vts": self.speed})

    self.position = 0.0
    self.position_rel = 0.0
    self.position_prct = 0.0

  def create_widgets(self, **kwargs):
    """
    Frames organization
      Frame_displayer: to display effort and displacement values.
      Frame_position: to start and stop the motor, according to pre-defined
      values.
      Frame_cycle: cycle generator.
    """

    self.create_menubar()
    self.create_frame_display()
    self.create_frame_action()
    # self.create_menu_limits()
    self.create_frame_cycles()
    # self.create_popup_limits()

    self.frame_displayer.grid(row=0, column=0)
    self.frame_action.grid(row=1, column=0)
    self.frame_cycles.grid(row=2, column=0)

  def create_menubar(self):
    self.menubar = tk.Menu(self)
    self.menubar.add_command(label='Limites',
                             command=self.create_popup_limits)
    self.menubar.add_command(label='Vitesse',
                             command=self.create_popup_speed)
    self.menubar.add_command(label='Paramètres échantillon',
                             command=self.create_popup_sample_parameters)
    self.menubar.add_command(label='Consigne...',
                             command=self.create_popup_command)

  def create_popup_limits(self):

    if hasattr(self, 'popup_limits'):
      self.popup_limits.deiconify()
      return

    self.popup_limits = tk.Toplevel()
    self.popup_limits.resizable(False, False)
    self.popup_limits.protocol("WM_DELETE_WINDOW",
                               self.popup_limits.withdraw)

    self.popup_limits.title("Limites")
    self.create_menu_limits(self.popup_limits)

  def create_frame_display(self):

    for i, (variable, abrg) in enumerate(self.variables):
      self.add_label(widgets_dict=self.displayer_widgets,
                     frame=self.frame_displayer,
                     text=variable,
                     name=abrg + '_label',
                     font=("Courier bold", 11, "bold"))

      self.add_label(widgets_dict=self.displayer_widgets,
                     frame=self.frame_displayer,
                     text='0.0',
                     font=("Courier bold", 48),
                     name=abrg + '_display')

      self.add_button(widgets_dict=self.displayer_widgets,
                      frame=self.frame_displayer,
                      name=abrg + "_tare",
                      text='Zéro',
                      command=abrg + "_tare")

      self.displayer_widgets[abrg + '_label'].grid(row=2 * i,
                                                   column=0,
                                                   columnspan=3,
                                                   sticky=tk.W)
      self.displayer_widgets[abrg + '_tare'].grid(row=2 * i + 1,
                                                  column=0,
                                                  sticky=tk.W)
      self.displayer_widgets[abrg + '_display'].grid(row=2 * i + 1,
                                                     column=1,
                                                     columnspan=2)

  def create_frame_action(self):

    self.add_button(widgets_dict=self.action_widgets,
                    frame=self.frame_action,
                    text="Traction",
                    bg="white",
                    command="TRACTION",
                    name="TRACTION",
                    width=10, height=4)

    self.add_button(widgets_dict=self.action_widgets,
                    frame=self.frame_action,
                    text="STOP!",
                    bg="red",
                    command="STOP",
                    name="STOP",
                    width=10, height=4)

    self.add_button(widgets_dict=self.action_widgets,
                    frame=self.frame_action,
                    text="Compression",
                    bg="white",
                    command="COMPRESSION",
                    name="COMPRESSION",
                    width=10, height=4)

    for id, widget in enumerate(self.action_widgets):
      self.action_widgets[widget].grid(row=0 + 1, column=id)

  def create_menu_limits(self, frame):

    self.limits_widgets = OrderedDict()
    self.frame_limits = frame

    self.add_label(widgets_dict=self.limits_widgets,
                   frame=self.frame_limits,
                   text="Limites",
                   name="limites_title",
                   font=("Courier bold", 14, "bold"))

    self.limits_widgets['limites_title'].grid(row=0, columnspan=4)

    for i, (label, name) in enumerate([("MAXIMUM", "Haute"),
                                       ("MINIMUM", "Basse"),
                                       ("Actif?", "Actif")]):
      self.add_label(widgets_dict=self.limits_widgets,
                     frame=self.frame_limits,
                     text=label,
                     name=name)
      self.limits_widgets[name].grid(row=1, column=1 + i)

    for i, (variable, abrg) in enumerate(self.variables):
      self.add_label(widgets_dict=self.limits_widgets,
                     frame=self.frame_limits,
                     text=variable,
                     name=abrg)
      self.limits_widgets[abrg].grid(row=2 + i, column=0, sticky=tk.W)

    for i, (variable, abrg) in enumerate(self.variables):
      self.add_entry(widgets_dict=self.limits_widgets,
                     frame=self.frame_limits,
                     entry_name=abrg + '_haute')
      self.add_entry(widgets_dict=self.limits_widgets,
                     frame=self.frame_limits,
                     entry_name=abrg + '_basse')

      # setattr(self, abrg + '_enabled', tk.BooleanVar())
      # getattr(self, abrg + '_enabled').set(False)

      self.add_checkbutton(widgets_dict=self.limits_widgets,
                           frame=self.frame_limits,
                           name=abrg + '_chck')

      self.limits_widgets[abrg + '_haute'].grid(row=2 + i, column=1)
      self.limits_widgets[abrg + '_basse'].grid(row=2 + i, column=2)
      self.limits_widgets[abrg + '_chck'].grid(row=2 + i, column=3)

    self.add_button(widgets_dict=self.limits_widgets,
                    frame=self.frame_limits,
                    name="quit_window",
                    text="Fini",
                    command_type="custom",
                    command=self.popup_limits.withdraw)

    self.limits_widgets["quit_window"].grid(row=10, column=1, columnspan=2)

  def create_frame_cycles(self):

    # self.frame_cycles = tk.Frame(self,
    #                              relief=tk.SUNKEN,
    #                              borderwidth=1)
    #
    # self.cycles_widgets = OrderedDict()
    self.add_label(widgets_dict=self.cycles_widgets,
                   frame=self.frame_cycles,
                   text="GENERATEUR DE CYCLES",
                   name="CYCLES",
                   font=("Courier bold", 14, "bold"))

    self.cycles_widgets["cycles_type"] = tk.StringVar()
    self.cycles_widgets["cycles_type"].set("position")
    self.cycles = []
    self.nb_cycles = 0.
    self.cycles_started = False
    self.rising = True

    self.add_button(widgets_dict=self.cycles_widgets,
                    frame=self.frame_cycles,
                    name="submit_cycle",
                    text="Soumettre \n nouveaux cycles...",
                    bg="white",
                    command_type="custom",
                    command=self.create_popup_new_cycle,
                    width=15, height=5)

    self.add_button(widgets_dict=self.cycles_widgets,
                    frame=self.frame_cycles,
                    name="start_cycle",
                    text="Démarrer",
                    bg="green",
                    command_type="custom",
                    command=self.start_cycle,
                    width=15, height=5)

    columns = ("Type de limite haute",
               "Limite haute",
               "Type de limite basse",
               "Limite basse")

    self.cycles_table = ttk.Treeview(self.frame_cycles)
    self.cycles_table["columns"] = columns

    self.cycles_table.heading('#0', text="#")
    self.cycles_table.column('#0', width=50)

    for column in columns:
      self.cycles_table.column(column, width=10 * len(column))
      self.cycles_table.heading(column, text=column)

    self.cycles_widgets["CYCLES"].grid(row=0, columnspan=4)
    self.cycles_widgets["submit_cycle"].grid(row=1, column=0,
                                             columnspan=2)

    self.cycles_widgets["start_cycle"].grid(row=1, column=2,
                                            columnspan=2)
    self.cycles_table.grid(row=5, column=0, columnspan=4, rowspan=1)

  def create_popup_new_cycle(self):

    if hasattr(self, 'cycles_popup'):
      self.cycles_popup.deiconify()
      print(self.cycles_popup.winfo_geometry())
      return

    self.cycles_popup = tk.Toplevel()
    self.cycles_popup.title("Nouveau cycle")
    self.cycles_popup.protocol("WM_DELETE_WINDOW",
                               self.cycles_popup.withdraw)
    self.cycles_popup.resizable(False, False)
    # entries_combobox = ('Position(%)',
    #                     'Position(mm)',
    #                     'Effort(N)',
    #                     'Effort('
    #                                                                 'MPa)')
    entries_combobox = [name[0] for name in self.variables]

    labels_cycles = (("max_type_label", "Type de valeur max"),
                     ("max_label", "Valeur max"),
                     ("min_type_label", "Type de valeur min"),
                     ("min_label", "Valeur min"),
                     ("nb_label", "Nombre"))

    for name, label in labels_cycles:
      self.add_label(widgets_dict=self.cycles_widgets,
                     frame=self.cycles_popup,
                     name=name,
                     text=label)
    for name in ['maximum', 'minimum']:
      self.add_entry(widgets_dict=self.cycles_widgets,
                     frame=self.cycles_popup,
                     entry_name=name + "_entry")

      self.add_combobox(widgets_dict=self.cycles_widgets,
                        frame=self.cycles_popup,
                        name=name + "_type",
                        entries=entries_combobox)

    self.add_entry(widgets_dict=self.cycles_widgets,
                   frame=self.cycles_popup,
                   entry_name="nombre_entry",
                   vartype=tk.IntVar())

    self.add_button(widgets_dict=self.cycles_widgets,
                    frame=self.cycles_popup,
                    name="submit",
                    text="Ajouter",
                    command=lambda: self.submit_cycle(),
                    command_type='custom')

    self.add_button(widgets_dict=self.cycles_widgets,
                    frame=self.cycles_popup,
                    text="Terminer",
                    name="quit",
                    command=self.cycles_popup.withdraw,
                    command_type='custom')

    for index, (name, _) in enumerate(labels_cycles):
      self.cycles_widgets[name].grid(row=0, column=index)

    self.cycles_widgets["maximum_type"].grid(row=1, column=0)
    self.cycles_widgets["maximum_entry"].grid(row=1, column=1)
    self.cycles_widgets["minimum_type"].grid(row=1, column=2)
    self.cycles_widgets["minimum_entry"].grid(row=1, column=3)
    self.cycles_widgets["nombre_entry"].grid(row=1, column=4)
    self.cycles_widgets["submit"].grid(row=2, column=1, columnspan=2)
    self.cycles_widgets["quit"].grid(row=2, column=3, columnspan=2)

    # def close_cycles_popup(self):
    # self.cycles_popup.destroy()
    # del self.cycles_popup

    # for limit in ["maximum", "minimum"]:
    #   self.add_label(widgets_dict=self.cycles_widgets,
    #                  frame=self.frame_cycles,
    #                  name=limit,
    #                  text=limit)
    #   self.add_entry(widgets_dict=self.cycles_widgets,
    #                  frame=self.frame_cycles,
    #                  entry_name=limit + '_entry')
    # self.add_label(widgets_dict=self.cycles_widgets,
    #                frame=self.frame_cycles,
    #                name="nombre",
    #                text="nombre")
    # self.add_entry(widgets_dict=self.cycles_widgets,
    #                frame=self.frame_cycles,
    #                entry_name="nombre_entry",
    #                vartype=tk.IntVar())

  def create_popup_sample_parameters(self):
    if hasattr(self, 'sample_parameters'):
      self.sample_parameters.deiconify()
      return

    self.sample_parameters = tk.Toplevel()
    self.sample_parameters.title("en mm")
    self.sample_parameters.resizable(False, False)
    self.sample_parameters.protocol("WM_DELETE_WINDOW",
                                    self.sample_parameters.withdraw)
    self.sample_parameters_widgets = OrderedDict()

    parameters = [('Longueur', self.ep_length),
                  ('Largeur', self.ep_width),
                  ('Epaisseur', self.ep_depth)]

    for i, (parameter, variable) in enumerate(parameters):
      self.add_label(frame=self.sample_parameters,
                     widgets_dict=self.sample_parameters_widgets,
                     text=parameter,
                     name=parameter + '_label')
      self.sample_parameters_widgets[parameter + '_label'].grid(row=i, column=0)

      self.add_entry(frame=self.sample_parameters,
                     widgets_dict=self.sample_parameters_widgets,
                     entry_name=parameter,
                     variable=variable)
      self.sample_parameters_widgets[parameter].grid(row=i, column=1)

    self.add_button(frame=self.sample_parameters,
                    widgets_dict=self.sample_parameters_widgets,
                    name="ok_button",
                    text="Fini",
                    command_type='custom',
                    command=self.sample_parameters.withdraw)
    self.sample_parameters_widgets["ok_button"].grid(row=3, column=0,
                                                     columnspan=2)

  def create_popup_command(self):

    if hasattr(self, 'popup_command'):
      self.popup_command.deiconify()
      return
    self.check_goto_bool = False
    self.popup_command = tk.Toplevel()
    self.popup_command.title("Aller à")
    self.popup_command.protocol("WM_DELETE_WINDOW",
                                self.popup_command.withdraw)
    self.popup_command.resizable(False, False)
    self.popup_command_widgets = OrderedDict()

    combobox_entries = [variable[0] for variable in self.variables]

    self.add_label(frame=self.popup_command,
                   widgets_dict=self.popup_command_widgets,
                   name="command_type_label",
                   text="Type de commande")

    self.add_combobox(frame=self.popup_command,
                      widgets_dict=self.popup_command_widgets,
                      entries=combobox_entries,
                      name='command_type')

    self.add_label(frame=self.popup_command,
                   widgets_dict=self.popup_command_widgets,
                   name="command_value_label",
                   text="Valeur")

    self.add_entry(frame=self.popup_command,
                   widgets_dict=self.popup_command_widgets,
                   entry_name='command_value',
                   vartype=tk.DoubleVar())

    self.add_button(frame=self.popup_command,
                    widgets_dict=self.popup_command_widgets,
                    name="submit_command_button",
                    text="Go!",
                    command_type="custom",
                    command=lambda: self.init_command())

    self.add_button(frame=self.popup_command,
                    widgets_dict=self.popup_command_widgets,
                    name="quit_popup_command",
                    text='Fini',
                    command=self.popup_command.withdraw,
                    command_type="custom")

    # to_show = ['command_type_label',
    #            'command_type',
    #            'command_value_label',
    #            'command_value',
    #            'submit_command_button',
    #            'quit_popup_command']

    for i, widg in enumerate(self.popup_command_widgets.values()):
      widg.grid(row=0, column=i)

    self.popup_command_widgets["quit_popup_command"].grid(row=0, column=6)

  def create_popup_speed(self):

    if hasattr(self, 'popup_speed'):
      self.popup_speed.deiconify()
      return

    self.popup_speed = tk.Toplevel()
    self.popup_speed.title("Vitesse du moteur")
    self.popup_speed.protocol("WM_DELETE_WINDOW",
                              self.popup_speed.withdraw)

    self.popup_speed.resizable(False, False)

    self.popup_speed_widgets = OrderedDict()

    self.add_label(frame=self.popup_speed,
                   widgets_dict=self.popup_speed_widgets,
                   text="Vitesse du moteur (mm/min)",
                   name="vit_mot_label")

    self.add_entry(frame=self.popup_speed,
                   widgets_dict=self.popup_speed_widgets,
                   entry_name="vit_mot",
                   variable=self.speed)

    # self.add_scale(frame=self.popup_speed,
    #                widgets_dict=self.popup_speed_widgets,
    #                name="vit_mot_scale",
    #                boundaries=(0, 255))

    self.add_button(frame=self.popup_speed,
                    widgets_dict=self.popup_speed_widgets,
                    name="vit_mot_submit",
                    command="VITESSE",
                    text='Soumettre')
    self.add_button(frame=self.popup_speed,
                    widgets_dict=self.popup_speed_widgets,
                    name="vit_mot_quit",
                    text="Fini",
                    command_type="custom",
                    command=self.popup_speed.withdraw)

    for value in self.popup_speed_widgets.values():
      value.pack()

  def check_limits(self, **kwargs):
    sens = kwargs.pop("sens")
    for variable, abrg in self.variables:
      try:
        if getattr(self, abrg + '_chck_var').get():
          var = kwargs.pop(abrg)
          if var <= getattr(self, abrg + '_basse_var').get() and sens == -1:
            self.submit_command("STOP")
          if var >= getattr(self, abrg + '_haute_var').get() and sens == 1:
            self.submit_command("STOP")
      except ValueError:
        pass

  def submit_cycle(self):
    try:
      nb_cycles = self.nombre_entry_var.get()

      for i in xrange(nb_cycles):
        new_cycle = [len(self.cycles) + 1,
                     self.maximum_type_var.get(),
                     self.maximum_entry_var.get(),
                     self.minimum_type_var.get(),
                     self.minimum_entry_var.get()]
        self.cycles.append(new_cycle)
        self.cycles_table.insert("", "end",
                                 text=new_cycle[0],
                                 values=new_cycle[1:])

    except ValueError:
      pass
    for widg in ['nombre_entry_var', 'minimum_entry_var', 'nombre_entry_var']:
      getattr(self, widg).set(0.0)

  def init_command(self):
    try:
      self.command_value_var.get()
    except ValueError:
      return

    self.command_bool = True
    self.check_goto_bool = True

  def check_go_to(self, **kwargs):
    sens = kwargs.pop("sens")
    var_type = self.command_type_var.get()
    for name, variable in self.variables:
      if name == var_type:
        var = kwargs.pop(variable)
    if self.command_bool:
      if var < self.command_value_var.get():
        self.submit_command("TRACTION")
        self.command_bool = False
      elif var > self.command_value_var.get():
        self.submit_command("COMPRESSION")
        self.command_bool = False
    else:
      if var >= self.command_value_var.get() and sens == 1:
        self.submit_command("STOP")
        self.check_goto_bool = False

      elif var <= self.command_value_var.get() and sens == -1:
        self.submit_command("STOP")
        self.check_goto_bool = False

  def start_cycle(self):
    if self.cycles:
      self.cycles_started = True
      self.submit_command("TRACTION")

  def check_cycle(self, **kwargs):

    sens = kwargs.pop("sens")
    mode_max, maximum, mode_min, minimum = self.cycles[0][1:]

    for name, variable in self.variables:
      if name == mode_max:
        mode_max = variable
      if name == mode_min:
        mode_min = variable

    if self.rising:
      var = kwargs.pop(mode_max)
    else:
      var = kwargs.pop(mode_min)

    if var >= maximum and sens == 1 and self.rising:
      self.nb_cycles += 0.5
      self.rising = False
      self.submit_command("COMPRESSION")

    elif var <= minimum and sens == -1 and not self.rising:
      self.nb_cycles += 0.5
      self.rising = True

      del self.cycles[0]
      self.cycles_table.delete(self.cycles_table.get_children()[0])

      if self.cycles:
        self.submit_command("TRACTION")
      else:
        self.cycles_started = False
        self.submit_command("STOP")

  def calc_speed(self):
    return int(255 * (-self.speed.get() / 208. + 1))

  def tare(self):
    pass

  def submit_command(self, arg):
    if arg == "STOP":
      dico = {"s": 0}
    elif arg == "TRACTION":
      dico = {"s": 1}
    elif arg == "COMPRESSION":
      dico = {"s": -1}
    # elif arg == "position_tare":
    #   dico = {"t": 1}
    elif arg == "effort_tare":
      dico = {"t": 2}
    elif arg == "VITESSE":
      dico = {"v": (self.calc_speed())}
    else:
      dico = arg
    message = str(dico)
    self.queue.put(message)

  def update_data(self, new_data):

    try:
      # Retrieved from arduino
      effort = new_data.get('e')
      sens = new_data.get('s')
      millis = new_data.get('m')
      position_abs = new_data.get('p')
      # delta = position_abs * self.calc_speed() / (1000 * 60.) - self.position_rel
      # self.position_rel += delta
      # self.position = self.position_rel + self.position

      # Computed
      if 0 in (self.ep_depth.get(), self.ep_width.get()):
        contrainte = 0.0
      else:
        contrainte = effort / (self.ep_depth.get() * self.ep_width.get())
      if self.ep_length.get() == 0:
        position_prct = 0.0
      else:
        position_prct = (position_abs - self.ep_length.get()) / \
                        self.ep_length.get()

    except (TypeError, AttributeError):  # If errors, at the beginning in
      # general.
      position_abs = 0.0
      effort = 0.0
      sens = 0.0
      millis = 0.0

      position_prct = 0.0
      contrainte = 0.0

    if hasattr(self, 'limits_widgets'):
      self.check_limits(effort=effort,
                        position=position,
                        sens=sens,
                        position_prct=position_prct,
                        contrainte=contrainte)

    if self.cycles_started:
      self.check_cycle(effort=effort,
                       sens=sens,
                       position=position,
                       position_prct=position_prct,
                       contrainte=contrainte)

    if hasattr(self, 'popup_command'):
      if self.check_goto_bool:
        self.check_go_to(position=position_abs,
                         position_prct=position_prct,
                         contrainte=contrainte,
                         effort=effort,
                         sens=sens)

    to_send = {"position": position_abs,
               "effort": effort,
               "sens": sens,
               "position_prct": position_prct,
               "contrainte": contrainte}

    self.update_widgets(to_send)

  def update_widgets(self, new_data):

    formating_parameters = [("position", ('.3f', 'mm')),
                            ("effort", ('.2f', 'N')),
                            ('position_prct', ('.2f', '%')),
                            ('contrainte', ('.3f', 'MPa'))]

    for parameters, formats in formating_parameters:
      mot = format(new_data[parameters], formats[0]) + ' ' + formats[1]
      self.displayer_widgets[parameters + "_display"].configure(text=mot)

    if new_data["sens"] == 1:
      self.action_widgets["TRACTION"].configure(bg="blue")
      self.action_widgets["COMPRESSION"].configure(bg="white")
    elif new_data["sens"] == -1:
      self.action_widgets["COMPRESSION"].configure(bg="blue")
      self.action_widgets["TRACTION"].configure(bg="white")
    else:
      self.action_widgets["COMPRESSION"].configure(bg="white")
      self.action_widgets["TRACTION"].configure(bg="white")

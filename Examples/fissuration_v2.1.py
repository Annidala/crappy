import time
import crappy
import numpy as np

crappy.blocks.MasterBlock.instances = []  # Init masterblock instances


# try:
# import sys
# sys.path.insert(0, '/home/essais-2015-3/Bureau/')
# import alerte_jerome
# except:
# pass
# for tracking memory leaks:
# from pympler import tracker
# tr = tracker.SummaryTracker()
# from pympler import summary
# from pympler import muppy
# sum1 = summary.summarize(all_objects)
# summary.print_(sum1)
# sum2 = summary.summarize(muppy.get_objects())
# diff = summary.get_diff(sum1, sum2)
# summary.print_(diff)

class ConditionCoeff(crappy.links.MetaCondition):
    def __init__(self):
        initial_coeff = 0
        self.last_cycle = -1
        self.coeff = initial_coeff
        self.last_coeff = initial_coeff
        self.delay = 10
        self.blocking = False
        self.last_new_coeff = initial_coeff
        self.new_coeff = 0

    # print "condition coeff"

    def evaluate(self, value):
        # print "1"
        recv = self.external_trigger.recv(blocking=self.blocking)  # first run is blocking, others are not
        # print "2"
        self.blocking = False
        try:
            self.new_coeff = recv['coeff']
        except TypeError:  # if no new coeff
            # print "no new coeff"
            pass
        # print recv
        if self.new_coeff != self.coeff:  # if coeff is changing
            if self.new_coeff != self.last_new_coeff:  # if first change
                self.t_init = time.time()
                self.t1 = self.t_init
                self.last_new_coeff = self.new_coeff
                self.last_coeff = self.coeff
            self.t2 = time.time()
            if (self.t2 - self.t_init) < self.delay:
                self.coeff += (self.new_coeff - self.last_coeff) * ((self.t2 - self.t1) / (self.delay))
            else:  # if delay is passed
                self.coeff = self.new_coeff
                self.last_coeff = self.coeff
            self.t1 = self.t2
        val = value.pop('signal')
        value['signal'] = val * self.coeff
        return value


class ConditionCycleBool(crappy.links.MetaCondition):
    def __init__(self, n=1, n_per_cycle=2):
        self.last_cycle = -1
        self.n = n
        self.n_per_cycle = n_per_cycle

    def evaluate(self, value):
        cycle = value['cycle']
        if cycle != self.last_cycle:
            # print "here"
            self.last_cycle = cycle
            if (cycle % self.n == 0 or (cycle - 0.5) % self.n == 0) and self.n_per_cycle == 2:
                return value
            elif ((cycle - 0.5) % self.n == 0) and self.n_per_cycle == 1:
                return value
            else:
                return None
        else:
            return None


class ConditionK(crappy.links.MetaCondition):
    def __init__(self):
        self.K = 0
        self.W = 18. * 10 ** (-3)  # largeur eprouvette
        self.y = 3. * 10 ** (-3)  # distance de prise potentielle depuis centre eprouvette
        # self.a0_elec= 3.4*10**(-3) #longueur prefissure
        self.e = 3.8 * 10 ** (-3)  # epaisseur eprouvette
        self.K1 = 6 * 10 ** 6
        self.F0 = 10000.
        self.K0 = self.F0 / (2500.)  # 2000 Newtons/Volt on the instron computer
        self.FIFO = []
        self.size = 120  # 120 cycles = 1 minute
        if self.K0 > 4:
            print "WARNING, K0 is too high for the USB-DUX D, please stop and modify your script"
        self.first = True
        self.finish = False

    # self.V0=0#2.348060601499999723e-04  Add here the v0 value if you restart the script
    def evaluate(self, value):
        # print "sending tension value"
        self.FIFO.insert(0, value['tension(V)'])
        if len(self.FIFO) > self.size:
            self.FIFO.pop()
        median_value = np.median(self.FIFO)
        if value['t_agilent(s)'] > 30:  # delay before starting
            if self.first:
                self.first = False
                self.V0 = median_value  # *0.727
                np.savetxt('/home/essais-2015-3/Bureau/test_fissurationv2.1/V0.txt', [self.V0])
                self.K = self.K0
            # self.V0= 2.138003450000000236e-04 #jusqu au cycle 508200
            # a = (2. * self.W / np.pi) * np.arccos(
            #     np.cosh(np.pi * self.y / (2. * self.W)) / np.cosh(median_value / self.V0 * np.arccosh(
            #         np.cosh(np.pi * self.y / (2. * self.W)) / np.cos(
            #             np.pi * self.a0_elec * 10 ** (-3) / (2. * self.W)))))  # johnson law

            a = (-(median_value/self.V0)**4*0.00036203+(median_value/self.V0)**3*0.00329946-(median_value/self.V0)**2*0.0116056+(median_value/self.V0)*0.02238681-0.009609) # FEM law1
            a = (-(median_value / self.V0) ** 4 * 0.00086926 + (median_value / self.V0) ** 3 * 0.00631791 - (
                median_value / self.V0) ** 2 * 0.01777262 + (
                     median_value / self.V0) * 0.02732055 - 0.01139102)  # FEM law2 VG cast iron
            alpha = a / self.W  # rapport longueur fissure sur largeur
            # V2 ep sacrificielle
            # Y = alpha**4*13.569+alpha**3*7.850-alpha**2*10.150+alpha*4.820-0.247
            # FEM law1
            # Y = alpha**4*196.89980597-alpha**3*281.49618641+alpha**2*157.05615266-alpha*36.9122841+3.54991714
            Y = alpha ** 4 * 88.68154823 - alpha ** 3 * 103.98805267 + alpha ** 2 * 51.65245584 - alpha * 10.17983283 + 1.11828637  # FEM law2 VG cast iron
            Fmax = self.K1 / (Y * np.sqrt(3.1416 * a)) * self.e * self.W
            if not (np.isnan(Fmax)):
                self.K = (Fmax / self.F0) * self.K0
            # if a > (4.4*10**(-3)):
            # comment this loop if you don't want to stop the test
            # self.K=0
            # self.finish=True
            print "a, Fmax, K ,median value : ", a, Fmax, self.K, median_value
        if self.K > self.K0:
            print "WARNING, evaluation of K is wrong!"
            self.K = self.K0
        if self.finish:  # if the notch is long enough, stop the test
            self.K = 0
        # self.K=4
        # value['coeff'] = pd.Series((self.K), index=value.index)
        value['coeff'] = self.K
        # print "value coeff :" ,value
        return value


try:
    # Creating objects

    instronSensor = crappy.sensor.ComediSensor(device='/dev/comedi0', channels=[0, 1], gain=[10, 15000], offset=[0, 0])
    agilentSensor = crappy.sensor.Agilent34420ASensor(device='/dev/ttyUSB1', baudrate=9600, timeout=1)
    # agilentSensor=crappy.sensor.DummySensor()
    comedi_actuator = crappy.actuator.ComediActuator(device='/dev/comedi1', subdevice=1, channel=1, range_num=0, gain=1,
                                                      offset=0)

    comedi_actuator.set_cmd(0)
    time.sleep(0.5)
    comedi_actuator.set_cmd(0)
    # Creating blocks
    comedi_output = crappy.blocks.CommandComedi([comedi_actuator])
    tension = crappy.blocks.MeasureAgilent34420A(agilentSensor, labels=['t_agilent(s)', 'tension(V)'])
    camera = crappy.blocks.StreamerCamera("Ximea", freq=None, save=True,
                                           save_directory="/home/essais-2015-3/Bureau/test_fissurationv2.1/images_fissuration_18-02-16/")

    compacter_tension = crappy.blocks.Compacter(5)
    graph_tension = crappy.blocks.Grapher(('t_agilent(s)', 'tension(V)'))  # ,('t(s)','tension(V)')
    save_tension = crappy.blocks.Saver("/home/essais-2015-3/Bureau/test_fissurationv2.1/tension_coeff.txt")

    effort = crappy.blocks.MeasureComediByStep(instronSensor, labels=['t(s)', 'dep(mm)', 'F(N)'], freq=200)
    compacter_effort = crappy.blocks.Compacter(100)
    graph_effort = crappy.blocks.Grapher(('t(s)', 'F(N)'))
    save_effort = crappy.blocks.Saver("/home/essais-2015-3/Bureau/test_fissurationv2.1/t_dep_F.txt")

    signalGenerator = crappy.blocks.SignalGenerator(
        path=[{"waveform": "sinus", "time": 1000000, "phase": 0, "amplitude": 0.45, "offset": 0.55, "freq": 4}],
        send_freq=600, repeat=True, labels=['t(s)', 'signal', 'cycle'])

    # Creating links

    link1 = crappy.links.Link(condition=ConditionCycleBool(n=100))
    link2 = crappy.links.Link(condition=ConditionCycleBool(n=1, n_per_cycle=1))
    link3 = crappy.links.Link(condition=ConditionK())
    link4 = crappy.links.Link()
    link5 = crappy.links.Link()
    link6 = crappy.links.Link(condition=ConditionK())
    link7 = crappy.links.Link(condition=ConditionCoeff())
    link7.add_external_trigger(link6)
    # link8=crappy.links.Link(condition=ConditionCoeff(test=True))
    # link14=crappy.links.Link()
    # link8.add_external_trigger(link14)
    link9 = crappy.links.Link()
    link10 = crappy.links.Link()
    link11 = crappy.links.Link()
    # link12=crappy.links.Link()
    # link13=crappy.links.Link()

    # link15=crappy.links.Link()
    # link16=crappy.links.Link()

    # link_alert=crappy.links.Link(condition=alerte_jerome.Alert())
    # Linking objects

    camera.add_input(link1)
    # camera.add_output(link_alert)

    tension.add_input(link2)
    tension.add_output(link3)
    tension.add_output(link6)
    # tension.add_output(link14)

    compacter_tension.add_input(link3)
    compacter_tension.add_output(link5)
    compacter_tension.add_output(link4)

    graph_tension.add_input(link5)
    save_tension.add_input(link4)

    effort.add_output(link9)
    compacter_effort.add_input(link9)
    compacter_effort.add_output(link10)
    compacter_effort.add_output(link11)

    graph_effort.add_input(link10)
    save_effort.add_input(link11)

    signalGenerator.add_output(link1)
    signalGenerator.add_output(link2)
    signalGenerator.add_output(link7)
    # signalGenerator.add_output(link8)

    # adapter.add_input(link6)
    # adapter.add_input(link7)
    # adapter.add_output(link8)
    # adapter.add_output(link15)

    ##compacter_signal.add_input(link8)
    ##compacter_signal.add_output(link12)
    ##compacter_signal.add_output(link13)
    ##save_signal.add_input(link13)
    ##graph_signal.add_input(link12)

    # coeffGenerator.add_output(link1)
    # coeffGenerator.add_output(link2)
    # compacter_coeff.add_input(link2)
    # compacter_coeff.add_output(link3)
    # graph_coeff.add_input(link3)

    # adapter.add_input(link1)
    # adapter.add_input(link4)
    # adapter.add_output(link5)
    comedi_output.add_input(link7)
    # compacter_adapter.add_input(link15)
    # compacter_adapter.add_output(link12)
    # compacter_adapter.add_output(link16)
    # save_adapter.add_input(link16)
    # graph_adapter.add_input(link12)

    # Starting objects

    t0 = time.time()  # 1.445448736241215944e+09 # modify t0 here if you restart your script
    np.savetxt('/home/essais-2015-3/Bureau/test_fissurationv2.1/t0.txt', [t0])
    for instance in crappy.blocks.MasterBlock.instances:
        instance.t0 = t0

    for instance in crappy.blocks.MasterBlock.instances:
        instance.start()

        # Waiting for execution
        # time.sleep(10)
        # sum1 = summary.summarize(muppy.get_objects())
        # summary.print_(sum1)
        # while True:
        # time.sleep(10)
        # sum2 = summary.summarize(muppy.get_objects())
        # diff = summary.get_diff(sum1, sum2)
        # summary.print_(diff)

# Stopping objects

except (Exception, KeyboardInterrupt) as e:
    print "Exception in main :", e
    # for instance in crappy.blocks._meta.MasterBlock.instances:
    # instance.join()
    for instance in crappy.blocks.MasterBlock.instances:
        try:
            instance.stop()
            print "instance stopped : ", instance
        except Exception as e:
            print e

import crappy

lbj = crappy.technical.LabJack(actuator={'channel': 'TDAC0'},
                               verbose=True)

cc = crappy.blocks.ControlCommand(lbj,
                                  compacter=1000,
                                  verbose=True)

wave = crappy.blocks.WaveGenerator(waveform='pwm',
                                   duty_cycle=0.2,
                                   wave_frequency=1,
                                   nb_points=100,
                                   gain=1)
# dash = crappy.blocks.Dashboard()
# graph = crappy.blocks.Grapher(('time(sec)', 'signal'), length=10)

crappy.link(wave, cc)
# crappy.link(cc, graph)
# crappy.link(cc, dash)
crappy.start()

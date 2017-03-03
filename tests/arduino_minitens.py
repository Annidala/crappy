import crappy
# labels = ['temps_python(s)', 'temps_arduino(ms)', 'mode', 'vitesse', 'random']
if __name__ == '__main__':
  labels = ["current_millis", "effort"]
  arduino = crappy.technical.Arduino(port='/dev/ttyACM0',
                                     baudrate=250000,
                                     labels=labels)
  measurebystep = crappy.blocks.MeasureByStep(arduino)

  graph = crappy.blocks.Grapher(('current_millis', 'effort'), length=10)
  dash = crappy.blocks.Dashboard()

  crappy.link(measurebystep, graph)
  crappy.link(measurebystep, dash, name='dash')
  crappy.start()

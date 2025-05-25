class TSVPath():
    def __init__(self):
        self.tsvPitch = 1.7e-6
        self.tsvRes = 0.3
        self.tsvCap = 20e-15

    def CalculateArea(self):
        self.area = (pow(self.tsvPitch, 2))
        return self.area

    def CalculateLatency(self):
        self.latency = 3 * self.tsvRes * self.tsvCap # 3~5 tau
        return self.latency

    def CalculatePower(self):
        self.freq = 1e9
        self.vdd = 1
        self.delta = 0.15 # switching activity of adder, delta = 0.15 by default
        self.i_leak = 1e-9 # [need change] e-9~e-6?
        self.leakPower = self.i_leak * self.vdd
        self.dynamicPower = self.tsvCap * self.vdd * self.vdd * self.delta * self.freq
        return self.dynamicPower
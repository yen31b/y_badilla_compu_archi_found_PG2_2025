class branch_predictor_2_bit:
    def __init__(self):
        self.counters = {}  # pc -> 2-bit counter (0-3)

    def predict(self, pc):
        """Predict whether the branch will be taken based on the 2-bit counter."""
        state = self.counters.get(pc, 1)  # Default: weakly not taken
        return state >= 2  # 2 or 3 means predict taken

    def update(self, pc, taken):
        """Update the 2-bit counter based on the actual branch outcome."""
        state = self.counters.get(pc, 1)
        if taken:
            if state < 3:
                state += 1
        else:
            if state > 0:
                state -= 1
        self.counters[pc] = state
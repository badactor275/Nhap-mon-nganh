self.start_x, self.start_y = x, y
        self.rect.x, self.rect.y = x, y
        # Wave movement parameters (slow/choreographed, upper-half only)
        self.amplitude = random.uniform(12, 18)
        # slower, calmer movement suitable for upper-half choreography
        self.frequency = random.uniform(0.00004, 0.00008)
        self.time_offset = random.uniform(0, 2 * math.pi)
        # very slow downward drift; will be clamped to upper half
        self.downward_speed = random.uniform(0.01, 0.06)
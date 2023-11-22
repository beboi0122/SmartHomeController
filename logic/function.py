
class Function:
    def status_changed(self, status):
        raise NotImplementedError("Update class is not implemented")

    def load_state(self):
        raise NotImplementedError("Load state class is not implemented")
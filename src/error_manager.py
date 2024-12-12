class ErrorManagementSystem:
    def __init__(self, config):
        self.config = config
        self.running = False

    def start(self):
        # Add logging to capture start attempts
        print("Attempting to start the Error Management System...")
        try:
            # Initialize resources, connections, etc.
            self.running = True
            print("Error Management System started successfully.")
        except Exception as e:
            print(f"Failed to start Error Management System: {e}")
            self.running = False

    def is_running(self):
        return self.running

import time
import threading

class RedLightGreenLight:
    def __init__(self):
        self.distance = 0
        self.target_distance = 10
        self.light = "green"
        self.game_over = False
        self.lock = threading.Lock()

    def light_changer(self):
        while not self.game_over:
            time.sleep(3)  
            with self.lock:
                self.light = "red" if self.light == "green" else "green"
                print(f"\n[LIGHT] The light is now {self.light.upper()}!")

    def play(self):
        print("Welcome to Red Light, Green Light!")
        print("Type 'move' to move forward. Reach the goal without moving on RED.\n")
        time.sleep(1)

        light_thread = threading.Thread(target=self.light_changer)
        light_thread.start()

        while not self.game_over:
            user_input = input(">> ").strip().lower()

            with self.lock:
                if user_input == "move":
                    if self.light == "red":
                        print("You moved on RED! You lose!")
                        self.game_over = True
                    else:
                        self.distance += 1
                        print(f"You moved forward! Current distance: {self.distance}/{self.target_distance}")
                        if self.distance >= self.target_distance:
                            print("Congratulations! You reached the goal and survived!")
                            self.game_over = True
                else:
                    print("You stayed still.")

        light_thread.join()

if __name__ == "__main__":
    game = RedLightGreenLightGame()
    game.play()

import threading
import timing
import time
import serial
import json

class enc():
    def __init__(self, sample_wait):
        self.running = True
        self.sample_wait = sample_wait
        self.ser = serial.Serial('/dev/ttyTHS1', 19200, timeout=0.8)
        self.ser.flush()
        print("encoder initialized")
        self.enc_thread1 = threading.Thread(target=self.encoder)
        self.test_threads = []
        self.t = time.time()
        self.last_times = []
        for test_thread in range(2):
            self.test_threads.append(threading.Thread(target=self.test))
        try:
            self.enc_thread1.start()
            for test_thread in self.test_threads:
                test_thread.start()
            print(f"Active threads: {threading.active_count()}")
            while True:
                continue
        except KeyboardInterrupt:
            self.running = False
        except Exception as e:
            print(e)

    def test(self):

        while self.running:
            #print("testing")
            for i in range(100):
                t = time.time()
                self.t = t
            time.sleep(0.01)

    def encoder(self):
        if True:
            while self.running:
                try:
                    start = time.time()
                    self.ser.flush()
                    data = self.ser.readline().decode()
                    print(data)
                    next_t = time.time()
                    #print(data)
                except serial.SerialTimeoutException:
                    print("Serial Timeout")
                except serial.SerialException as e:
                    print(e)
                except Exception as e:
                    print(e)
                    raise e
                try:
                    j_data = json.loads(data)
                    tally = j_data["tally"]
                    delta_ms = j_data["delta_time"]
                    now = time.time()
                    print(f"Time taken to get data: {next_t - start}")
                    print(f"TIme taken after: {now - next_t}")
                    self.statistics(next_t - start)
                except Exception as e:
                    print(e)

    def statistics(self,this_time):
        self.last_times.append(this_time)
        last_times = self.last_times
        mean_sum = 0
        for t in last_times:
            mean_sum = mean_sum + t

        mean = mean_sum/len(last_times)

        var_sum = 0
        for t in last_times:
            var_sum = var_sum + (t - mean)**2

        std_dev = (var_sum/(len(last_times)))**0.5
        print(f"Mean: {mean}\n Std Dev: {std_dev}")

if __name__ == "__main__":
    e = enc(1)

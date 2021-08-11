from pebble import ProcessPool
from concurrent.futures import TimeoutError
import os, time
from functools import partial


def function(number):

    os.mkdir(str(number))

    time.sleep(5)


def task_done(future, folder = None):
    
    try:
        result = future.result() # blocks until results are ready
    except TimeoutError as error:
        print("Function took longer than %d seconds" % error.args[1])
    except Exception as error:
        print(" -> Function raised %s" % error)  # error raised
        with open("error_backlog.txt", "a") as file:
            file.write(error.traceback + "\n")
    
    print("clean up on file", folder)
    os.rmdir(str(folder))



if __name__ == '__main__':

    start = time.perf_counter()

    
    with open("error_backlog.txt" ,"w") as file:
        file.write("ERROR BACKLOG\n\n")
    
    with ProcessPool(max_workers=os.cpu_count()) as pool:
        for i in range(0, 10):
            future = pool.schedule(function, args=[i], timeout=3)
            future.add_done_callback(partial(task_done, folder = i))
            
    
    print(f"finished in: {round(time.perf_counter() - start, 2)} second(s)")
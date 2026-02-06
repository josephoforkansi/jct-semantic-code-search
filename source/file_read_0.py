def log_message(msg):
    with open("log.txt", "a") as log:
        log.write(msg + "\n")

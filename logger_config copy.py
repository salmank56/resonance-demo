import logging

def setup_logging(debug=False):
    if debug:
        logging.basicConfig(
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            level=logging.DEBUG,
            datefmt="%d-%b-%y %H:%M:%S",
            handlers=[logging.StreamHandler()]  # Ensure logs are written to stdout
        )
    else:
        logging.basicConfig(
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            level=logging.INFO,
            datefmt="%d-%b-%y %H:%M:%S",
            handlers=[logging.StreamHandler()]  # Ensure logs are written to stdout
        )
        
if __name__ == "__main__":
    setup_logging()
    logging.info("Hello, info Loggings!")
    logging.warning("Hello, debug Loggings!")
    logging.error("Hello, error Loggings!")
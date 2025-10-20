from debate.app import run_app


if __name__ == "__main__":
    # Run app in console mode for environments without GUI
    run_app(gui=False, rounds=3)

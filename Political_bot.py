from debate.app import run_app


def main():
    # Thin entrypoint: compose and run the refactored application.
    run_app(gui=True, rounds=10)


if __name__ == "__main__":
    main()
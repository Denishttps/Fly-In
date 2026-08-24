from gui.pygame_render import PyGameRenderer
from dispatcher import Dispatcher


def main():
    dp = Dispatcher("maps/challenger/01_the_impossible_dream.txt")
    history = dp.print_simulation()
    renderer = PyGameRenderer(
        dp.graph,
        history,
        offset=(100, 200),
        scale=100,
        tick_duration=0.8,
        width=1200,
        height=800
    )
    renderer.run()


if __name__ == "__main__":
    main()
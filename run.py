import sys

from model import Model


def main():
    args = [i.split('=') for i in sys.argv[1:]]
    start = None
    x = None
    y = None
    num_iter = None
    write_files = False
    eval_dates = False
    show_prog = False
    plot_model = False
    params = {}

    arg_int = {
        '--k': 'k',
        '--fiss': 'fission_threshold',
        '--perm': 'permanence',
        '--catch': 'catchment',
        '--leap': 'leap_distance'
    }

    for arg in args:
        if arg[0] == '--start':
            start = int(arg[1])
        elif arg[0] == '--show-bar':
            show_prog = True
        elif arg[0] == '--plot':
            plot_model = True
        elif arg[0] == '--iter':
            num_iter = int(arg[1])
        elif arg[0] == '--write':
            write_files = True
        elif arg[0] == '--eval':
            eval_dates = True
        elif arg[0] == '--x':
            x = float(arg[1])
        elif arg[0] == '--y':
            y = float(arg[1])
        elif arg[0] == '--tol':
            params['tolerance'] = float(arg[1])
        else:
            params[arg_int[arg[0]]] = int(arg[1])

    params['coords'] = (x,y)
    model = Model(start, params)
    model.run(num_iter, show_prog, plot_model)

    if write_files:
        model.write()

    if eval_dates:
        print('score:', model.eval())


if __name__ == "__main__":
    main()

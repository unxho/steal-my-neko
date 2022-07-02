if __package__ != 'smn':
    print('Do not run it as a script!')
else:
    from .main import main
    try:
        import uvloop
        uvloop.install()
    except (ImportError, ModuleNotFoundError):
        pass
    main()

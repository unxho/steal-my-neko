if __package__ != "smn":
    print("Do not run it as a script!")
else:
    from contextlib import suppress

    from .main import main

    with suppress(ImportError):
        import uvloop

        uvloop.install()

    main()

def get_image_class(backend):
    """
    Returns the Image class for the specified backend

    Handy in cases where you wish to make this configurable at runtime

    Callers must be prepared to handle ImportErrors when a given backend
    cannot be loaded and KeyError when an unknown backend is requested
    """

    if backend == "aware":
        from backends.aware import AwareImage
        return AwareImage
    if backend == "aware_cext":
        from backends.aware_cext import AwareImage
        return AwareImage
    elif backend.lower() == "graphicsmagick":
        from backends.GraphicsMagick import GraphicsMagickImage
        return GraphicsMagickImage
    elif backend.lower() == "java":
        from backends.java import JavaImage
        return JavaImage
    elif backend.lower() == "pil":
        # Useful only for benchmarking:
        from PIL import Image
        return Image
    else:
        raise KeyError("Unknown backend %s" % backend)
